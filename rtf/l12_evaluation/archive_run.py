"""Archive a completed L12 evaluation run into a permanent, versioned
record under `rtf/l12_evaluation/runs/`.

The "live" top-level files (`FROZEN_MANIFEST.json`,
`FIRST_EVALUATION_RESULT.json`, etc.) are working state for the most
recent run and get overwritten by the next one. This module copies a
completed run's outputs into an immutable, uniquely-named directory and
appends a record to `runs/RUNS_REGISTRY.json` -- the durable answer to
"what did RTF version X, run Y actually produce," independent of
whatever the top-level files currently hold.

This is the first real piece of L10 (Maturity & Versioning) this project
has built -- previously every requirement record carried a `maturity`
field but nothing tracked evaluation-run identity/history at all (see
`rtf/AUDIT_L0_L12.md`'s L10 row).
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO_ROOT / "rtf" / "l12_evaluation" / "runs"
REGISTRY_PATH = RUNS_DIR / "RUNS_REGISTRY.json"

# Maps the durable archive filenames to the current "live" filenames they
# capture a snapshot of.
ARCHIVE_FILES = {
    "MANIFEST.json": "FROZEN_MANIFEST.json",
    "RESULT.json": "FIRST_EVALUATION_RESULT.json",
    "DETECTGRADER_RESULT.json": "FIRST_EVALUATION_DETECTGRADER_RESULT.json",
    "RENDERED_REPORT.md": "FIRST_EVALUATION_RENDERED_REPORT.md",
    "FAILURE_ATTRIBUTION.md": "FAILURE_ATTRIBUTION_REPORT.md",
}


def archive_run(rtf_version: str, run_number: int, audit_ids: list[str], notes: str = "") -> Path:
    """Copy the current live run outputs into a new, permanent
    `runs/v{rtf_version}_run{run_number}_{slug}/` directory and register
    it. Refuses to overwrite an existing archive for the same
    (version, run_number) -- archiving is a one-time action per run,
    same discipline as `freeze_gate.freeze()`.
    """
    slug = "-".join(a.split("/")[0] for a in audit_ids)[:80]
    run_dir_name = f"v{rtf_version}_run{run_number}_{slug}"
    run_dir = RUNS_DIR / run_dir_name

    if run_dir.exists():
        raise SystemExit(
            f"REFUSING TO ARCHIVE: {run_dir} already exists. Archiving is one-time "
            f"per (version, run_number). Use a new run_number for a new run."
        )

    live_dir = REPO_ROOT / "rtf" / "l12_evaluation"
    missing = [live for live in ARCHIVE_FILES.values() if not (live_dir / live).exists()]
    if missing:
        raise SystemExit(f"REFUSING TO ARCHIVE: missing live output file(s): {missing}")

    run_dir.mkdir(parents=True)
    for archive_name, live_name in ARCHIVE_FILES.items():
        shutil.copy2(live_dir / live_name, run_dir / archive_name)

    manifest = json.loads((run_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    result = json.loads((run_dir / "RESULT.json").read_text(encoding="utf-8"))
    grade = json.loads((run_dir / "DETECTGRADER_RESULT.json").read_text(encoding="utf-8"))

    record = {
        "rtf_version": rtf_version,
        "run_number": run_number,
        "run_id": run_dir_name,
        "audit_ids": audit_ids,
        "git_commit_at_freeze": manifest.get("git_commit"),
        "framework_version_internal": manifest.get("framework_version"),
        "frozen_manifest_timestamp": manifest.get("timestamp"),
        "archived_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "detectgrader_summary": {
            "score": grade.get("score"),
            "max_score": grade.get("max_score"),
            "vulnerability_results": grade.get("vulnerability_results"),
        },
        "metrics_summary": result.get("metrics"),
        "notes": notes,
        "status": "ARCHIVED",
    }

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")) if REGISTRY_PATH.exists() else []
    registry.append(record)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    return run_dir


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        raise SystemExit("usage: python3 -m rtf.l12_evaluation.archive_run <rtf_version> <run_number> <audit_id> [audit_id...]")
    rtf_version = sys.argv[1]
    run_number = int(sys.argv[2])
    audit_ids = sys.argv[3:]
    run_dir = archive_run(rtf_version, run_number, audit_ids)
    print(f"Archived -> {run_dir}")
    print(f"Registry -> {REGISTRY_PATH}")
