"""Part A execution-ladder rung 1 (10-20 contracts): a lightweight,
compute-node-only smoke test of real Resource 2 samples, run ahead of the
full A2-A5 pipeline (labels.py doesn't have a real parser for the
name.txt/label.txt pair format yet -- see data/gnn/raw/MANIFEST.md finding
2). This script only answers "does compilation work at all, and with which
solc version" -- it does NOT do label mapping, indexing, or write
RawGraphRecords; it directly drives `a4v.gnn.etl.compile_one.run_job` per
sample so the real per-candidate-timeout/status-enum machinery gets
exercised against real data, not just fixtures.

`python -m scripts.etl.smoke_real_sample [--n-per-class 5]`
Refuses to run outside a SLURM allocation, same guardrail as run_sample.py.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from a4v.gnn.etl.compile_one import run_job  # noqa: E402

RAW_ROOT = REPO_ROOT / "data/gnn/raw/dataset_preprocessing_for_vulnerabilities"
CLASSES = ["reentrancy", "timestamp", "Integeroverflow", "delegatecall"]

# Available locally (no internet needed) -- oldest first, matching the
# pre-0.5.0 syntax cues (bare `throw`, `.call.value()`) found in the corpus.
SOLC_CANDIDATES = [
    {"solc_version": "0.4.24", "solc_path": str(REPO_ROOT / ".venv/.solc-select/artifacts/solc-0.4.24/solc-0.4.24")},
    {"solc_version": "0.8.17", "solc_path": str(REPO_ROOT / ".venv/.solc-select/artifacts/solc-0.8.17/solc-0.8.17")},
    {"solc_version": "0.8.20", "solc_path": str(REPO_ROOT / ".venv/.solc-select/artifacts/solc-0.8.20/solc-0.8.20")},
]


def _refuse_unless_compute_node() -> None:
    if not os.environ.get("SLURM_JOB_ID"):
        print("FATAL: $SLURM_JOB_ID unset -- refusing to run outside a SLURM allocation.")
        raise SystemExit(2)


def pick_sample(n_per_class: int) -> list[dict]:
    picked = []
    for cls in CLASSES:
        name_file = RAW_ROOT / cls / f"final_{cls.lower()}_name.txt"
        label_file = RAW_ROOT / cls / f"final_{cls.lower()}_label.txt"
        names = name_file.read_text().splitlines()
        labels = label_file.read_text().splitlines()
        count = 0
        for name, label in zip(names, labels):
            sol_path = RAW_ROOT / cls / "sourcecode" / name
            if not sol_path.exists():
                continue  # moved to error_data/ -- counted separately, not this smoke test's job
            picked.append({"cls": cls, "name": name, "label": label, "path": sol_path})
            count += 1
            if count >= n_per_class:
                break
    return picked


def main(argv: list[str] | None = None) -> int:
    _refuse_unless_compute_node()

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-per-class", type=int, default=5)
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "data/gnn/reports/smoke_real_sample.json")
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "data/gnn/processed_smoke")
    args = ap.parse_args(argv)

    sample = pick_sample(args.n_per_class)
    results = []
    for item in sample:
        contract_id = f"{item['cls']}-{item['name']}"
        job = {
            "target": str(item["path"]),
            "candidates": SOLC_CANDIDATES,
            "candidate_timeout_seconds": 60,
            "class_names": [item["cls"]],
            "label_record": None,
            "contract_id": contract_id.replace("/", "_"),
            "native_ids": [contract_id],
            "source_relpath": str(item["path"].relative_to(RAW_ROOT)),
            "content_sha256": contract_id,
            "out_dir": str(args.out_dir),
            "pragma_raw": [],
        }
        result = run_job(job)
        results.append({
            "cls": item["cls"], "name": item["name"], "ground_truth_label": item["label"],
            "status": result.get("status"),
            "solc_attempts": result.get("solc_attempts", []),
        })
        print(f"{item['cls']}/{item['name']}: {result.get('status')}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2))

    ok = sum(1 for r in results if r["status"] == "OK")
    print(f"\n{ok}/{len(results)} compiled OK")
    by_status: dict[str, int] = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
