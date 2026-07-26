"""A5 orchestrator: dispatch, outer backstop timeout, and resume (see plan
A5/A7). **Compute node only** -- refuses to run on a login host / without a
SLURM allocation, since this compiles arbitrary sampled Solidity via Slither
under real timeouts.

`python -m scripts.etl.run_sample <corpus_root> <sample_json> <full_index_jsonl>
    <candidates_json> --out-dir data/gnn/processed
    --attempts data/gnn/manifests/attempts.jsonl
    [--outer-timeout-seconds 600] [--candidate-timeout-seconds 180]`

Every launch **first refreshes derived state** (merges `attempts.jsonl` into
an in-memory latest-status table) so a relaunch after a crash never
consults a stale `manifest.jsonl` on disk. Before dispatching a contract, it
checks that fresh state for a terminal `OK` row **and** validates the
output at Part-A's cheap tier (file exists, size>0, npz header loads without
decompressing arrays) -- full array load only if that cheap check disagrees
with the manifest. A hit skips the contract and logs a `SKIPPED_RESUME`
event (a log event, not a status -- never overwrites `OK`, never itself
creates a manifest row).

Each contract is compiled in its own `python -m a4v.gnn.etl.compile_one`
subprocess, bounded by an **outer backstop timeout**
(`subprocess.run(timeout=...)`) that contains genuine hangs/segfaults of the
whole compile_one process -- separate from (and looser than) compile_one's
own internal per-candidate timeout.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

from solc_select import solc_select as ss

from a4v.gnn.etl.manifest import (
    Attempt,
    append_attempt,
    current_array_task_id,
    current_run_id,
    merge_manifest,
    read_attempts,
)

DEFAULT_OUTER_TIMEOUT_SECONDS = 600
DEFAULT_CANDIDATE_TIMEOUT_SECONDS = 180
# Resource 2's own 4 vuln classes -- see data/gnn/raw/MANIFEST.md.
MESSIQ_CLASS_NAMES = ["reentrancy", "timestamp", "Integeroverflow", "delegatecall"]


def _label_record_for_row(row: dict) -> dict:
    """Real Resource 2 labels are file-granularity (see MANIFEST.md finding
    2): `merged_classes` from A3's index is already the per-contract positive
    label set. Shape matches what `compile_one.run_job` expects to rebuild a
    `labels.LabelRecord` (native_id here is just the row's own contract_id --
    map_labels.py never reads it, it only needs a value to carry through).
    """
    return {
        "native_id": row["contract_id"],
        "granularity": "file",
        "annotations": [
            {"vuln_class": c, "file": None, "lines": [], "contract": None,
             "function_name": None, "signature": None}
            for c in row.get("merged_classes", [])
        ],
    }


def _refuse_unless_compute_node() -> None:
    if not os.environ.get("SLURM_JOB_ID"):
        print("FATAL: $SLURM_JOB_ID is unset -- refusing to run outside a SLURM allocation "
              "(this must never run on a login node).")
        raise SystemExit(2)


def _cheap_output_valid(out_dir: Path, contract_id: str) -> bool:
    json_path = out_dir / f"{contract_id}.json"
    npz_path = out_dir / f"{contract_id}.npz"
    if not json_path.exists() or not npz_path.exists():
        return False
    if json_path.stat().st_size == 0 or npz_path.stat().st_size == 0:
        return False
    try:
        with zipfile.ZipFile(npz_path) as zf:
            if not zf.namelist():
                return False
    except zipfile.BadZipFile:
        return False
    return True


def dispatch_one(
    row: dict,
    candidate_info: dict,
    class_names: list[str],
    label_record_raw: dict | None,
    out_dir: Path,
    candidate_timeout_seconds: int,
    outer_timeout_seconds: int,
    corpus_root: Path,
) -> dict:
    candidates_to_try = candidate_info.get("candidates_to_try") or (
        [candidate_info["resolved_version"]] if candidate_info.get("resolved_version") else []
    )
    if candidate_info.get("unresolved") or not candidates_to_try:
        return {"status": "UNRESOLVED_DEPS", "solc_attempts": []}

    candidates = [
        {"solc_version": v, "solc_path": str(ss.artifact_path(v))} for v in candidates_to_try
    ]

    job = {
        "target": str(corpus_root / row["source_relpath"]),
        "candidates": candidates,
        "candidate_timeout_seconds": candidate_timeout_seconds,
        "class_names": class_names,
        "label_record": label_record_raw,
        "contract_id": row["contract_id"],
        "native_ids": row["native_ids"],
        "source_relpath": row["source_relpath"],
        "content_sha256": row["content_sha256"],
        "out_dir": str(out_dir),
        "pragma_raw": [row.get("pragma_major_minor")] if row.get("pragma_major_minor") else [],
    }

    with __import__("tempfile").TemporaryDirectory() as td:
        job_path = Path(td) / "job.json"
        result_path = Path(td) / "result.json"
        job_path.write_text(json.dumps(job))
        try:
            subprocess.run(
                [sys.executable, "-m", "a4v.gnn.etl.compile_one", str(job_path), str(result_path)],
                timeout=outer_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"status": "CRASHED", "solc_attempts": [], "error": "outer backstop timeout exceeded"}

        if not result_path.exists():
            return {"status": "CRASHED", "solc_attempts": [], "error": "compile_one produced no result file"}
        return json.loads(result_path.read_text())


def main(argv: list[str] | None = None) -> int:
    _refuse_unless_compute_node()

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("corpus_root", type=Path)
    ap.add_argument("sample_json", type=Path)
    ap.add_argument("full_index_jsonl", type=Path)
    ap.add_argument("candidates_json", type=Path)
    ap.add_argument("--out-dir", type=Path, default=Path("data/gnn/processed"))
    ap.add_argument("--attempts", type=Path, default=Path("data/gnn/manifests/attempts.jsonl"))
    ap.add_argument("--outer-timeout-seconds", type=int, default=DEFAULT_OUTER_TIMEOUT_SECONDS)
    ap.add_argument("--candidate-timeout-seconds", type=int, default=DEFAULT_CANDIDATE_TIMEOUT_SECONDS)
    ap.add_argument("--class-names", nargs="*", default=MESSIQ_CLASS_NAMES)
    args = ap.parse_args(argv)

    sample = json.loads(args.sample_json.read_text())
    candidates_doc = json.loads(args.candidates_json.read_text())
    rows_by_id = {}
    for line in args.full_index_jsonl.read_text().splitlines():
        row = json.loads(line)
        rows_by_id[row["contract_id"]] = row

    run_id = current_run_id()
    array_task_id = current_array_task_id()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for contract_id in sample["contract_ids"]:
        # Refresh derived state fresh before EVERY dispatch decision -- never
        # trust an on-disk manifest.jsonl that could be stale after a crash.
        latest = merge_manifest(read_attempts(args.attempts))
        prior = latest.get(contract_id)

        if prior and prior["status"] == "OK" and _cheap_output_valid(args.out_dir, contract_id):
            append_attempt(args.attempts, Attempt(
                contract_id=contract_id, status="SKIPPED_RESUME", run_id=run_id,
                array_task_id=array_task_id, detail={"prior_run_id": prior["run_id"]},
            ))
            continue

        row = rows_by_id.get(contract_id)
        if row is None:
            print(f"WARNING: {contract_id} in sample but not in full index -- skipping")
            continue

        candidate_info = candidates_doc["resolutions"].get(contract_id, {"unresolved": True})
        result = dispatch_one(
            row, candidate_info, args.class_names, _label_record_for_row(row), args.out_dir,
            args.candidate_timeout_seconds, args.outer_timeout_seconds, args.corpus_root,
        )
        append_attempt(args.attempts, Attempt(
            contract_id=contract_id, status=result.get("status", "CRASHED"),
            run_id=run_id, array_task_id=array_task_id,
            detail={"solc_attempts": result.get("solc_attempts", []), "error": result.get("error")},
        ))
        print(f"{contract_id[:12]}...: {result.get('status')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
