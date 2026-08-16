"""Append-only JSONL observability for security-agent investigations."""
from __future__ import annotations

import json
import time
from pathlib import Path


class TrajectoryWriter:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.sequence = 0
        if self.path.exists():
            for line in reversed(self.path.read_text(encoding="utf-8").splitlines()):
                try:
                    self.sequence = int(json.loads(line)["sequence"])
                    break
                except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                    continue

    def __call__(self, event_type: str, payload: dict) -> None:
        self.sequence += 1
        event = {"sequence": self.sequence, "timestamp": time.time(),
                 "event_type": event_type, "payload": payload}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
