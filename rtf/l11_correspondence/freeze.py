"""L11: validate and freeze a correspondence mapping produced by a
SEPARATED reviewer (see EXPOSURE_DECLARATION.json / CORRESPONDENCE_SCHEMA.md
for why this script does not itself contain or generate any judgments).

Usage:
    python3 -m rtf.l11_correspondence.freeze <path-to-correspondence.json>

Input: a JSON list of records matching the schema in
CORRESPONDENCE_SCHEMA.md. Output: <input>.sha256 next to it, refusing to
write a hash for a file that fails validation.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RELATIONSHIPS = {"DIRECT", "PARTIAL", "CONTEXTUAL", "NONE"}
REQUIRED_FIELDS = {
    "finding_id",
    "req_id",
    "relationship",
    "justification",
    "supporting_evidence",
    "review_status",
}


def validate_records(records: list[dict]) -> list[str]:
    errors = []
    for i, r in enumerate(records):
        missing = REQUIRED_FIELDS - r.keys()
        if missing:
            errors.append(f"record {i}: missing fields {sorted(missing)}")
            continue
        if r["relationship"] not in RELATIONSHIPS:
            errors.append(f"record {i}: relationship {r['relationship']!r} not in {sorted(RELATIONSHIPS)}")
        if not isinstance(r["supporting_evidence"], list):
            errors.append(f"record {i}: supporting_evidence must be a list")
        if r["relationship"] != "NONE" and not r.get("justification", "").strip():
            errors.append(f"record {i}: relationship {r['relationship']!r} requires a non-empty justification")
    return errors


def freeze(path: Path, framework_version: str) -> None:
    records = json.loads(path.read_text())
    if not isinstance(records, list):
        raise SystemExit("input must be a JSON list of correspondence records")

    errors = validate_records(records)
    if errors:
        print(f"REFUSING TO FREEZE -- {len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)

    for r in records:
        r["frozen_at_framework_version"] = framework_version

    path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    hash_path = path.with_suffix(path.suffix + ".sha256")
    frozen_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hash_path.write_text(f"{digest}  {path.name}\nframework_version: {framework_version}\nfrozen_at: {frozen_at}\n")

    n_direct = sum(1 for r in records if r["relationship"] == "DIRECT")
    n_partial = sum(1 for r in records if r["relationship"] == "PARTIAL")
    n_contextual = sum(1 for r in records if r["relationship"] == "CONTEXTUAL")
    n_none = sum(1 for r in records if r["relationship"] == "NONE")
    print(f"Validated {len(records)} record(s): DIRECT={n_direct} PARTIAL={n_partial} CONTEXTUAL={n_contextual} NONE={n_none}")
    print(f"Frozen -> {hash_path} ({digest})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python3 -m rtf.l11_correspondence.freeze <path.json> [framework_version]")
    freeze(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "0.1.0-track-a")
