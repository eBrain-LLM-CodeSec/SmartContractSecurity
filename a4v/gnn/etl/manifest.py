"""A7 -- immutable attempt log + derived manifest state (see plan A7).

Two pieces:
- `append_attempt`: writes one line to the **immutable, append-only**
  attempt log (`data/gnn/manifests/attempts.jsonl`). Each line carries a
  monotonic `run_id` + `ts`.
- `merge_manifest`: derives the canonical latest-state table (one row per
  `contract_id`) from the full attempt log.

`run_id` is `$SLURM_ARRAY_JOB_ID` if set, else `$SLURM_JOB_ID` -- **not**
plain `$SLURM_JOB_ID` unconditionally. This is load-bearing: in an array job
every task gets its own `SLURM_JOB_ID` but shares `SLURM_ARRAY_JOB_ID`, so
keying on `SLURM_JOB_ID` would give two same-launch tasks different run_ids
and misclassify a double-claim (the dispatch-slicing bug) as a legitimate
cross-run retry -- defeating this module's whole purpose.
`$SLURM_ARRAY_TASK_ID` is recorded as a **separate** provenance field, never
folded into `run_id`.

Because SLURM job ids are cluster-unique and monotonically increasing,
**zero locking code is needed** here (Lustre `flock` is unreliable under
some mount options) -- ordering cross-run retries by `(run_id, ts)` with
`run_id` dominating is immune to cross-node clock skew. A locked counter file
is a documented fallback only for a future non-SLURM path, not implemented
here.

Merge semantics:
- Rows with `status == "SKIPPED_RESUME"` are **log events, not real
  attempts** -- they never participate in merge (can't create, retry, or
  downgrade a contract's state).
- Two or more real-attempt rows sharing `(contract_id, run_id)` mean the
  *same launch* claimed the same contract twice -- the dispatch-slicing bug
  -- and `merge_manifest` raises `SameRunDuplicateClaim` rather than picking
  one silently.
- Otherwise, rows for a `contract_id` across *different* run_ids are
  legitimate cross-run retries: ordered by `(int(run_id), ts)`, last wins.
- **`OK` is sticky**: once any row for a `contract_id` is `OK`, that
  `contract_id`'s merged state is the latest `OK` row, even if a
  later-run_id row for the same contract records a worse status (e.g. a
  buggy resume re-attempting an already-`OK` contract and failing this
  time). The derived table never downgrades `OK`.
- `read_attempts` tolerates a truncated trailing line (a preemption can cut
  a write mid-line) by dropping only that final malformed line; a malformed
  line anywhere else in the file is a real corruption and raises.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path

SKIPPED_RESUME = "SKIPPED_RESUME"
OK = "OK"


class SameRunDuplicateClaim(Exception):
    pass


class CorruptAttemptLog(Exception):
    pass


def current_run_id() -> str:
    return os.environ.get("SLURM_ARRAY_JOB_ID") or os.environ.get("SLURM_JOB_ID") or ""


def current_array_task_id() -> str | None:
    return os.environ.get("SLURM_ARRAY_TASK_ID")


@dataclass
class Attempt:
    contract_id: str
    status: str
    run_id: str
    array_task_id: str | None = None
    ts: float | None = None
    detail: dict | None = None

    def __post_init__(self):
        if self.ts is None:
            self.ts = time.time()


def append_attempt(log_path: Path, attempt: Attempt) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(json.dumps(asdict(attempt), sort_keys=True) + "\n")


def read_attempts(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    lines = log_path.read_text().splitlines()
    attempts: list[dict] = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            attempts.append(json.loads(line))
        except json.JSONDecodeError:
            if i == len(lines) - 1:
                continue  # tolerated: preemption-truncated trailing line
            raise CorruptAttemptLog(f"malformed line {i} in {log_path} (not the trailing line)")
    return attempts


def _run_id_sort_key(run_id: str) -> tuple[int, str]:
    try:
        return (0, "%020d" % int(run_id))
    except (ValueError, TypeError):
        return (1, str(run_id))  # non-numeric run_id sorts after all numeric ones, defensively


def merge_manifest(attempts: list[dict]) -> dict[str, dict]:
    real_attempts = [a for a in attempts if a.get("status") != SKIPPED_RESUME]

    by_contract: dict[str, list[dict]] = {}
    for a in real_attempts:
        by_contract.setdefault(a["contract_id"], []).append(a)

    result: dict[str, dict] = {}
    for contract_id, rows in by_contract.items():
        by_run: dict[str, list[dict]] = {}
        for r in rows:
            by_run.setdefault(r["run_id"], []).append(r)
        for run_id, same_run_rows in by_run.items():
            if len(same_run_rows) > 1:
                raise SameRunDuplicateClaim(
                    f"contract_id={contract_id} claimed {len(same_run_rows)}x "
                    f"within run_id={run_id} -- likely a dispatch-slicing bug"
                )

        def sort_key(r: dict) -> tuple:
            return (_run_id_sort_key(r["run_id"]), r.get("ts") or 0.0)

        ok_rows = [r for r in rows if r["status"] == OK]
        latest = max(ok_rows, key=sort_key) if ok_rows else max(rows, key=sort_key)
        result[contract_id] = latest

    return result


def write_manifest(manifest_path: Path, merged: dict[str, dict]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w") as f:
        for contract_id in sorted(merged):
            f.write(json.dumps(merged[contract_id], sort_keys=True) + "\n")


def merge_and_write(attempts_log_path: Path, manifest_path: Path) -> dict[str, dict]:
    merged = merge_manifest(read_attempts(attempts_log_path))
    write_manifest(manifest_path, merged)
    return merged
