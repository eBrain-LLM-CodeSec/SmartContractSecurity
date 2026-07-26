"""Thin CLI over `a4v.gnn.etl.manifest.merge_and_write` (see plan A7).

`python -m scripts.etl.merge_manifests [--attempts PATH] [--manifest PATH]`

Every `run_sample.py` launch already refreshes derived state itself before
dispatching (never trusts a stale `manifest.jsonl`); this script exists so
the merge can also be run standalone -- after a crash, for inspection, or as
a cron-style periodic refresh separate from a live run.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from a4v.gnn.etl.manifest import SameRunDuplicateClaim, merge_and_write


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--attempts", type=Path, default=Path("data/gnn/manifests/attempts.jsonl"))
    ap.add_argument("--manifest", type=Path, default=Path("data/gnn/manifests/manifest.jsonl"))
    args = ap.parse_args(argv)

    try:
        merged = merge_and_write(args.attempts, args.manifest)
    except SameRunDuplicateClaim as e:
        print(f"FATAL: {e}")
        return 1

    statuses: dict[str, int] = {}
    for row in merged.values():
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    print(f"merged {len(merged)} contract(s) -> {args.manifest}")
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
