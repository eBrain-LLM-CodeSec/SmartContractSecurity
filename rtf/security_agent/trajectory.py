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

    def __call__(self, event_type: str, payload: dict) -> None:
        self.sequence += 1
        event = {"sequence": self.sequence, "timestamp": time.time(),
                 "event_type": event_type, "payload": payload}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
