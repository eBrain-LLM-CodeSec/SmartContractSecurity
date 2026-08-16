"""Unit tests for the 3 live-compatibility fixes found and fixed during
Increment 9/10's live validation (see RTF_SECURITY_AGENT_INCREMENT10_AB_
REPORT.md's "Live compatibility defects found and fixed"): the Codex
rollout-fallback recovery path, the last-fenced-JSON extractor, and the
option-shaped-argument file-extraction guard.

Written in this project's own established `check()`/`PASSES`/`FAILURES`/
`main()` convention (matching every other file in this suite), NOT bare
pytest -- a bare-pytest version of this file previously existed and was
silently never executed by `.venv/bin/python3 -m rtf.security_agent.
test_codex_rollout_fallback` (that invocation just imports the module
and does nothing when there's no runner block), even though all 4
assertions do pass under `pytest` directly. Run with:
    .venv/bin/python3 -m rtf.security_agent.test_codex_rollout_fallback
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import recover_codex_rollout
from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_c_codex import (
    _extract_last_fenced_json, _extract_touched_files,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def test_recovers_final_message_and_usage_from_latest_rollout():
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp_path = Path(tmp_str)
        rollout = tmp_path / ".codex/sessions/2026/08/16/rollout-test.jsonl"
        rollout.parent.mkdir(parents=True)
        events = [
            {"type": "event_msg", "payload": {"type": "token_count", "info": {
                "total_token_usage": {"input_tokens": 12, "cached_input_tokens": 4, "output_tokens": 3}
            }}},
            {"type": "event_msg", "payload": {"type": "task_complete", "last_agent_message": "```json\n{\"ok\": true}\n```"}},
        ]
        rollout.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")

        result = recover_codex_rollout(tmp_path)
        check(
            "recovers final message + usage from the newest rollout when Codex CLI's own -o/stdout flush is unreliable",
            result == ("```json\n{\"ok\": true}\n```", 12, 4, 3),
            result,
        )


def test_missing_rollout_is_empty():
    with tempfile.TemporaryDirectory() as tmp_str:
        result = recover_codex_rollout(Path(tmp_str))
        check("missing rollout directory returns the empty sentinel, not a crash", result == ("", 0, 0, 0), result)


def test_extracts_final_json_after_explanatory_code_fence():
    text = 'Evidence:\n```solidity\nrequire(value > 0);\n```\nFinal:\n```json\n{"properties": []}\n```'
    result = _extract_last_fenced_json(text)
    check(
        "walks fences BACKWARD to find the final JSON block, not the first-to-last naive span "
        "(an explanatory Solidity fence before it used to yield a false None decision)",
        result == {"properties": []},
        result,
    )


def test_head_limit_is_not_reported_as_a_file():
    result = _extract_touched_files("find . -type f | head -80")
    check("a piped `head -80` numeric option is not misparsed as a touched filename", result == [], result)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
