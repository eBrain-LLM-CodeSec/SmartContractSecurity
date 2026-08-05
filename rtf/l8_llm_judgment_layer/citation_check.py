"""L8: verification that cited files/symbols/locations in a judgment's
`evidence` list actually exist in the audited repository.

A judgment can pass schema validation (schema.py) and still cite a file
that doesn't exist or a line number past EOF -- this is a distinct check,
run against a real repo checkout, not against the judgment JSON alone.
"""
from __future__ import annotations

import re
from pathlib import Path

# Accepted `location` shapes: "path/to/file.sol", "path/to/file.sol:42",
# "path/to/file.sol:10-25", "path/to/file.sol#FunctionName".
LOCATION_RE = re.compile(r"^(?P<path>[^:#]+)(?::(?P<lines>\d+(-\d+)?))?(?:#(?P<symbol>\w+))?$")


def verify_evidence_citations(evidence: list[dict], repo_root: Path) -> dict:
    """Returns {"valid": int, "invalid": int, "details": [...]} -- always
    reports the raw numerator/denominator (plan finalization-patch rule),
    never just a bare percentage."""
    details = []
    valid = 0
    for i, ev in enumerate(evidence):
        location = ev.get("location", "")
        m = LOCATION_RE.match(location)
        if not m:
            details.append({"index": i, "location": location, "ok": False, "reason": "unparseable location format"})
            continue

        path = repo_root / m.group("path")
        if not path.exists():
            details.append({"index": i, "location": location, "ok": False, "reason": f"file not found: {path}"})
            continue

        lines_spec = m.group("lines")
        if lines_spec:
            file_line_count = sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
            end_line = int(lines_spec.split("-")[-1])
            if end_line > file_line_count:
                details.append(
                    {
                        "index": i,
                        "location": location,
                        "ok": False,
                        "reason": f"line {end_line} exceeds file length {file_line_count}",
                    }
                )
                continue

        symbol = m.group("symbol")
        if symbol:
            text = path.read_text(encoding="utf-8", errors="replace")
            if symbol not in text:
                details.append(
                    {"index": i, "location": location, "ok": False, "reason": f"symbol {symbol!r} not found in file text"}
                )
                continue

        details.append({"index": i, "location": location, "ok": True, "reason": None})
        valid += 1

    return {
        "valid": valid,
        "invalid": len(evidence) - valid,
        "total": len(evidence),
        "validity_fraction": (valid / len(evidence)) if evidence else None,
        "details": details,
    }
