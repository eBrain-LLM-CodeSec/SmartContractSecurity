"""Reconstructs the real, timestamped per-turn timeline for the
PoolTogether Arm G run, from the full .codex/sessions/*.jsonl file (which
carries real timestamps -- unlike arm_g_codex.py's own parsed --json
event stream, which does not). Written to verify AR-022's originally-
reported root cause for PoolTogether's non-completion (a relation-choice
mistake) against the actual evidence, after being asked to find the root
cause rather than accept the first plausible explanation -- see AR-023
and AGENT_DRIVEN_GRAPH_NAVIGATION_EXPERIMENT.md SS15/SS18 for the
findings this script produced.

The full .codex/sessions/*.jsonl this script depends on lives in
ephemeral job-scratch and is not committed (large, session-specific) --
regenerate by rerunning the PoolTogether Arm G bundle and pointing
SESSION_PATH at the new rollout-*.jsonl this produces.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

SESSION_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/scratch/md5344/.claude/jobs/318205ae/tmp/arm_g_scratch/pooltogether_vault_burn_ghome/"
    ".codex/sessions/2026/08/08/rollout-2026-08-08T01-00-32-019fde07-0e7d-7473-888d-168e65b3a5ab.jsonl"
)


def ts(e: dict) -> datetime | None:
    t = e.get("timestamp")
    return datetime.fromisoformat(t.replace("Z", "+00:00")) if t else None


def main() -> None:
    events = [json.loads(line) for line in SESSION_PATH.read_text().splitlines() if line.strip()]
    t0 = ts(events[0])

    calls = []
    for e in events:
        t = ts(e)
        if t is None:
            continue
        payload = e.get("payload", {})
        if e.get("type") == "response_item" and payload.get("type") == "function_call":
            calls.append({
                "t": (t - t0).total_seconds(),
                "name": payload.get("name", ""),
                "arguments": payload.get("arguments", ""),
            })

    print(f"{'t(s)':>7}  call")
    for c in calls:
        print(f"{c['t']:7.1f}  {c['name']}  {c['arguments'][:120]}")

    deltas = [calls[i]["t"] - calls[i - 1]["t"] for i in range(1, len(calls))]
    print()
    print(f"total calls: {len(calls)}")
    print(f"mean gap: {sum(deltas) / len(deltas):.2f}s  min: {min(deltas):.2f}s  max: {max(deltas):.2f}s")
    print(f"last call at: {calls[-1]['t']:.1f}s")
    print(f"sum(mean_gap * n_calls) approx {sum(deltas):.1f}s  (compare to observed session length)")


if __name__ == "__main__":
    main()
