"""Unit tests for rtf.security_agent.model_client. NO real LLM calls.
Run with:
    .venv/bin/python3 -m rtf.security_agent.test_model_client
"""
from __future__ import annotations

import sys

from a4v.llm import ChatResult
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


_VALID_TOOL_CALL_CONTENT = (
    '```json\n{"action": "call_tool", "tool": "read_file", '
    '"args": {"path": "x.sol"}, "reasoning": "r"}\n```'
)


class FakeChatClient:
    """Stands in for a4v.llm.ChatClient. ModelClient.decide() calls
    .complete() directly (not .complete_json()) so it can inspect
    content=None before extract_last_fenced_json ever sees it -- this
    fake matches that real interface."""

    def __init__(self, content, prompt_tokens: int = 100, completion_tokens: int = 50):
        self.content = content
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.calls: list[dict] = []

    def complete(self, messages, temperature: float = 0.0, top_p=None, max_tokens=None) -> ChatResult:
        self.calls.append({"temperature": temperature, "top_p": top_p, "max_tokens": max_tokens})
        return ChatResult(content=self.content, prompt_tokens=self.prompt_tokens,
                          completion_tokens=self.completion_tokens, cached=False, cost_usd=0.001)


# --- root cause: genuinely malformed (non-JSON) content ---------------------

def test_malformed_json_content_is_converted_to_malformed_model_response():
    """Before the fix: extract_last_fenced_json's own json.JSONDecodeError
    propagated uncaught, all the way to live_runner.py's generic except
    Exception as cluster_invocation_crashed:JSONDecodeError -- confirmed
    live, 32/147 properties in the 2026-08-17 forte run."""
    client = ModelClient(FakeChatClient("not json at all {{{"), RESPONSE_MODELS)
    try:
        client.decide([{"role": "user", "content": "x"}])
        check("raises MalformedModelResponse, not JSONDecodeError", False, "did not raise")
    except MalformedModelResponse as e:
        check("raises MalformedModelResponse, not JSONDecodeError", True)
        check("error message references the JSON problem", "not valid JSON" in e.errors, e.errors)
    except Exception as e:  # noqa: BLE001
        check("raises MalformedModelResponse, not JSONDecodeError", False,
              f"a different exception escaped uncaught: {type(e).__name__}: {e}")


# --- root cause 2: content=None (reasoning-budget exhaustion) --------------

def test_none_content_is_converted_to_malformed_model_response_not_attributeerror():
    """Real, previously-uncaught live crash (2026-08-17 forte RERUN, after
    the max_tokens cap fix): z-ai/glm-5.2 returned content=null with
    completion_tokens exactly at the configured cap on 2 separate large
    clusters (confirmed by reading the raw cached API responses) -- it
    exhausted its entire completion budget on internal reasoning tokens
    without ever emitting a visible answer. extract_last_fenced_json(None)
    crashes with AttributeError ('NoneType' object has no attribute
    'find'); this must never reach that call uncaught."""
    client = ModelClient(FakeChatClient(None, completion_tokens=16000), RESPONSE_MODELS)
    try:
        client.decide([{"role": "user", "content": "x"}])
        check("raises MalformedModelResponse for content=None", False, "did not raise")
    except MalformedModelResponse as e:
        check("raises MalformedModelResponse for content=None", True)
        check("error message explains the likely cause", "reasoning budget" in e.errors, e.errors)
    except AttributeError as e:
        check("raises MalformedModelResponse for content=None", False,
              f"raw AttributeError escaped uncaught -- this is the exact live crash: {e}")


def test_empty_string_content_also_treated_as_malformed():
    """Defense in depth: an empty (not None, but falsy) content string
    should be treated the same way, not passed to extract_last_fenced_json
    only to fail there with a less clear error."""
    client = ModelClient(FakeChatClient(""), RESPONSE_MODELS)
    try:
        client.decide([{"role": "user", "content": "x"}])
        check("empty content treated as malformed", False, "did not raise")
    except MalformedModelResponse:
        check("empty content treated as malformed", True)


# --- max_tokens is forwarded with a sane, now-higher default --------------

def test_max_tokens_is_forwarded_with_a_sane_default():
    """Real live incident (2026-08-17 forte run #1): no max_tokens was
    ever sent, and the model repeatedly generated runaway completions
    hitting an apparent ~65,536-token provider ceiling. Real live
    incident #2 (forte run #2, WITH the first fix's 8000 cap in place):
    z-ai/glm-5.2 exhausted that whole budget on reasoning alone for large
    clusters -- cap raised to 16000 as a result (see model_client.py's
    own DEFAULT_MAX_COMPLETION_TOKENS docstring for both incidents)."""
    fake = FakeChatClient(_VALID_TOOL_CALL_CONTENT)
    client = ModelClient(fake, RESPONSE_MODELS)
    client.decide([{"role": "user", "content": "x"}])
    check("max_tokens was sent", fake.calls[0].get("max_tokens") is not None, fake.calls)
    check("default is the documented DEFAULT_MAX_COMPLETION_TOKENS",
          fake.calls[0].get("max_tokens") == DEFAULT_MAX_COMPLETION_TOKENS, fake.calls)
    check("default reflects the raised (not original 8000) value",
          DEFAULT_MAX_COMPLETION_TOKENS == 16000, DEFAULT_MAX_COMPLETION_TOKENS)


def test_max_tokens_is_configurable():
    fake = FakeChatClient(_VALID_TOOL_CALL_CONTENT)
    client = ModelClient(fake, RESPONSE_MODELS, max_tokens=1234)
    client.decide([{"role": "user", "content": "x"}])
    check("configured max_tokens forwarded", fake.calls[0].get("max_tokens") == 1234, fake.calls)


def test_decide_still_returns_parsed_action_normally():
    fake = FakeChatClient(_VALID_TOOL_CALL_CONTENT)
    client = ModelClient(fake, RESPONSE_MODELS)
    turn = client.decide([{"role": "user", "content": "x"}])
    check("still parses a valid response normally", isinstance(turn.parsed, ToolCallAction), turn.parsed)
    check("chat_result carries real token/cost accounting",
          turn.chat_result.cost_usd == 0.001, turn.chat_result)


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
