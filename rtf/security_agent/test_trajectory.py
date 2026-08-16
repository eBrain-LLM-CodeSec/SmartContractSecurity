"""Deterministic tests for append-only trajectory JSONL."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from rtf.security_agent.trajectory import TrajectoryWriter


def main() -> int:
    path = Path(tempfile.mkdtemp(prefix="trajectory_test_")) / "trace.jsonl"
    writer = TrajectoryWriter(path)
    writer("first", {"value": 1})
    writer("second", {"value": 2})
    events = [json.loads(line) for line in path.read_text().splitlines()]
    checks = [
        ("two events persisted", len(events) == 2),
        ("sequence monotonic", [event["sequence"] for event in events] == [1, 2]),
        ("event types preserved", [event["event_type"] for event in events] == ["first", "second"]),
        ("payloads preserved", events[1]["payload"] == {"value": 2}),
    ]
    failed = [name for name, passed in checks if not passed]
    print(f"PASSED: {len(checks) - len(failed)}")
    for name, passed in checks:
        if passed:
            print(f"  ok - {name}")
    if failed:
        print(f"FAILED: {len(failed)}")
        for name in failed:
            print(f"  FAIL - {name}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
