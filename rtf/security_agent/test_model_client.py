"""Unit tests for rtf.security_agent.model_client. NO real LLM calls.
Run with:
    .venv/bin/python3 -m rtf.security_agent.test_model_client
"""
from __future__ import annotations

import json
import sys

from rtf.security_agent.kernel import RESPONSE_MODELS, ToolCallAction
from rtf.security_agent.model_client import (
    DEFAULT_MAX_COMPLETION_TOKENS, MalformedModelResponse, ModelClient,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


class RaisesJSONDecodeError:
    """Stands in for a4v.llm.ChatClient in the exact failure mode a real
    genuinely-malformed model response produces: complete_json's own
    extract_last_fenced_json re-raises json.JSONDecodeError for content
    that still isn't valid JSON after the tolerant "extra trailing data"
    recovery -- confirmed by reading a4v/llm.py, not assumed."""

    def complete_json(self, messages, temperature: float = 0.0, **kwargs):
        raise json.JSONDecodeError("Expecting value", "not json at all {{{", 0)


class SpyChatClient:
    """Records the kwargs it was called with; returns a fixed valid
    tool_call response."""

    def __init__(self):
        self.calls: list[dict] = []

    def complete_json(self, messages, temperature: float = 0.0, **kwargs):
        self.calls.append({"temperature": temperature, **kwargs})
        return ({"action": "call_tool", "tool": "read_file", "args": {"path": "x.sol"}, "reasoning": "r"}, None)


# --- root cause 1: JSONDecodeError must not propagate uncaught -------------

def test_json_decode_error_is_converted_to_malformed_model_response():
    """Before the fix: this raised a raw json.JSONDecodeError, uncaught
    anywhere in kernel.py, propagating all the way to live_runner.py's
    generic except Exception as cluster_invocation_crashed:JSONDecodeError
    -- confirmed live, 32/147 properties in the 2026-08-17 forte run."""
    client = ModelClient(RaisesJSONDecodeError(), RESPONSE_MODELS)
    try:
        client.decide([{"role": "user", "content": "x"}])
        check("raises MalformedModelResponse, not JSONDecodeError", False, "did not raise")
    except MalformedModelResponse as e:
        check("raises MalformedModelResponse, not JSONDecodeError", True)
        check("error message references the JSON problem", "not valid JSON" in e.errors, e.errors)
    except json.JSONDecodeError:
        check("raises MalformedModelResponse, not JSONDecodeError", False,
              "raw JSONDecodeError escaped uncaught -- this is the exact live crash")


# --- root cause 3 (mitigation): max_tokens must be sent on every call ------

def test_max_tokens_is_forwarded_with_a_sane_default():
    """Real live incident (2026-08-17 forte run): no max_tokens was ever
    sent, and the model repeatedly generated runaway completions hitting
    an apparent ~65,536-token provider ceiling (cluster_006: 29209,
    33813, 23069, 29414, then 65536 completion tokens across successive
    turns, the last costing $0.067 alone) -- truncated/anomalous output
    that crashed downstream parsing (all 3 AttributeError-crashed
    clusters showed this exact signature)."""
    spy = SpyChatClient()
    client = ModelClient(spy, RESPONSE_MODELS)
    client.decide([{"role": "user", "content": "x"}])
    check("max_tokens was sent", spy.calls[0].get("max_tokens") is not None, spy.calls)
    check("default is the documented DEFAULT_MAX_COMPLETION_TOKENS",
          spy.calls[0].get("max_tokens") == DEFAULT_MAX_COMPLETION_TOKENS, spy.calls)


def test_max_tokens_is_configurable():
    spy = SpyChatClient()
    client = ModelClient(spy, RESPONSE_MODELS, max_tokens=1234)
    client.decide([{"role": "user", "content": "x"}])
    check("configured max_tokens forwarded", spy.calls[0].get("max_tokens") == 1234, spy.calls)


def test_decide_still_returns_parsed_action_normally():
    spy = SpyChatClient()
    client = ModelClient(spy, RESPONSE_MODELS)
    turn = client.decide([{"role": "user", "content": "x"}])
    check("still parses a valid response normally", isinstance(turn.parsed, ToolCallAction), turn.parsed)


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
