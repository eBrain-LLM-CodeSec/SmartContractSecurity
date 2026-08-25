"""Unit tests for rtf.security_agent.responses_client. NO real network
calls -- httpx.Client.post is monkeypatched on the instance. Run with:
    .venv/bin/python3 -m rtf.security_agent.test_responses_client
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from rtf.security_agent.responses_client import ResponsesChatClient, _extract_output_text

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


class FakeResponse:
    def __init__(self, status_code: int, body: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._body = body or {}
        self.text = text or json.dumps(body or {})

    def json(self):
        return self._body

    def raise_for_status(self):
        raise RuntimeError(f"HTTP {self.status_code}")


class FakePost:
    """Records the last call's kwargs; returns a scripted FakeResponse."""

    def __init__(self, response: FakeResponse):
        self.response = response
        self.last_call: dict | None = None

    def __call__(self, url, headers=None, json=None):
        self.last_call = {"url": url, "headers": headers, "json": json}
        return self.response


def _client(response: FakeResponse, **kwargs) -> tuple[ResponsesChatClient, FakePost]:
    tmp = Path(tempfile.mkdtemp(prefix="responses_client_test_"))
    client = ResponsesChatClient(
        base_url="https://openrouter.ai/api/v1", api_key="unused", model="z-ai/glm-5.2",
        cache_dir=tmp / "cache", token_log_path=tmp / "tokens.jsonl", **kwargs,
    )
    fake_post = FakePost(response)
    client._client.post = fake_post
    return client, fake_post


_MESSAGE_RESPONSE_BODY = {
    "output": [
        {"type": "reasoning", "encrypted_content": "...", "summary": []},
        {"type": "message", "role": "assistant", "content": [
            {"type": "output_text", "text": '```json\n{"action": "call_tool"}\n```'},
        ]},
    ],
    "usage": {"input_tokens": 500, "output_tokens": 80, "output_tokens_details": {"reasoning_tokens": 40}, "cost": 0.002},
}

_REASONING_ONLY_BODY = {
    "output": [
        {"type": "reasoning", "encrypted_content": "...", "summary": ["thinking a lot"]},
    ],
    "usage": {"input_tokens": 500, "output_tokens": 16000, "output_tokens_details": {"reasoning_tokens": 16000}},
}


# --- _extract_output_text ---------------------------------------------------

def test_extract_output_text_finds_message_item_after_reasoning_items():
    text = _extract_output_text(_MESSAGE_RESPONSE_BODY["output"])
    check("extracts the message's output_text", text == '```json\n{"action": "call_tool"}\n```', text)


def test_extract_output_text_returns_none_for_reasoning_only_output():
    """The actual root-cause scenario this client exists to handle
    correctly: an output array with ONLY reasoning items (the model spent
    its whole budget reasoning, never reached an answer) -- must return
    None cleanly, not raise, so the SAME MalformedModelResponse path
    model_client.py already has for content=None handles it."""
    text = _extract_output_text(_REASONING_ONLY_BODY["output"])
    check("returns None for reasoning-only output", text is None, text)


def test_extract_output_text_handles_empty_output():
    check("empty list returns None", _extract_output_text([]) is None)
    check("None output returns None", _extract_output_text(None) is None)


# --- request shape -----------------------------------------------------------

def test_request_uses_responses_endpoint_and_includes_reasoning_effort():
    client, fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY), reasoning_effort="low")
    client.complete([{"role": "user", "content": "hello"}], temperature=0.0, max_tokens=8000)
    check("posted to /responses", fake_post.last_call["url"].endswith("/responses"), fake_post.last_call["url"])
    body = fake_post.last_call["json"]
    check("input array built from messages", body["input"] == [{"role": "user", "content": "hello"}], body)
    check("reasoning.effort set", body["reasoning"] == {"effort": "low"}, body)
    check("max_output_tokens set (not max_tokens)", body.get("max_output_tokens") == 8000, body)
    check("max_tokens key NOT used (that's the Chat Completions field name)", "max_tokens" not in body, body)


def test_reasoning_effort_is_configurable():
    client, fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY), reasoning_effort="high")
    client.complete([{"role": "user", "content": "x"}])
    check("configured effort forwarded", fake_post.last_call["json"]["reasoning"] == {"effort": "high"})


# --- session_id (OpenRouter prompt-caching hint) wiring ----------------------

def test_session_id_is_sent_in_body_when_configured():
    client, fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY), session_id="case-abc-123")
    client.complete([{"role": "user", "content": "x"}])
    body = fake_post.last_call["json"]
    check("session_id carried in the request body", body.get("session_id") == "case-abc-123", body)


def test_no_session_id_sent_when_not_configured():
    """Backward compatibility: a client built without session_id (the
    pre-fix construction pattern) sends no session_id key at all --
    unchanged prior wire behavior, matching pre-fix (uncached) cost."""
    client, fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY))
    client.complete([{"role": "user", "content": "x"}])
    body = fake_post.last_call["json"]
    check("no session_id key present", "session_id" not in body, body)


_CACHED_MESSAGE_RESPONSE_BODY = {
    "output": [
        {"type": "message", "role": "assistant", "content": [
            {"type": "output_text", "text": '{"action": "call_tool"}'},
        ]},
    ],
    "usage": {"input_tokens": 6164, "output_tokens": 3,
              "input_tokens_details": {"cached_tokens": 6144}, "cost": 0.0009},
}


def test_provider_cached_tokens_logged_to_token_log():
    """Real, live-verified finding (2026-08-26): session_id enables
    OpenRouter prompt caching for z-ai/glm-5.2, reported via
    usage.input_tokens_details.cached_tokens. Logged distinctly from the
    (unrelated) local disk-cache `cached` flag so a real run's savings
    can be verified after the fact from tokens.jsonl alone."""
    tmp = Path(tempfile.mkdtemp(prefix="responses_client_test_"))
    client = ResponsesChatClient(
        base_url="https://openrouter.ai/api/v1", api_key="unused", model="z-ai/glm-5.2",
        cache_dir=tmp / "cache", token_log_path=tmp / "tokens.jsonl", session_id="case-1",
    )
    client._client.post = FakePost(FakeResponse(200, _CACHED_MESSAGE_RESPONSE_BODY))
    client.complete([{"role": "user", "content": "x"}])
    lines = (tmp / "tokens.jsonl").read_text().strip().splitlines()
    logged = json.loads(lines[-1])
    check("provider_cached_tokens logged from usage.input_tokens_details.cached_tokens",
          logged.get("provider_cached_tokens") == 6144, logged)
    check("local disk-cache flag still False for a real network call",
          logged.get("cached") is False, logged)


def test_provider_cached_tokens_none_when_absent_from_usage():
    client, _fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY), session_id="case-1")
    client.complete([{"role": "user", "content": "x"}])
    lines = client.token_log_path.read_text().strip().splitlines()
    logged = json.loads(lines[-1])
    check("provider_cached_tokens is None when usage has no input_tokens_details",
          logged.get("provider_cached_tokens") is None, logged)


# --- response_schema (structured output) wiring ------------------------------

_SCHEMA_PAYLOAD = {"type": "json_schema", "name": "kernel_action", "strict": True,
                   "schema": {"type": "object", "properties": {}, "additionalProperties": False}}


def test_response_schema_is_sent_as_text_format_when_configured():
    client, fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY), response_schema=_SCHEMA_PAYLOAD)
    client.complete([{"role": "user", "content": "x"}])
    body = fake_post.last_call["json"]
    check("text.format carries the configured schema payload",
          body.get("text") == {"format": _SCHEMA_PAYLOAD}, body.get("text"))


def test_no_text_field_sent_when_response_schema_not_configured():
    """Backward compatibility: a client built without response_schema
    (the pre-fix construction pattern, still used by tests/other
    callers) must send no `text` key at all -- unchanged prior wire
    behavior."""
    client, fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY))
    client.complete([{"role": "user", "content": "x"}])
    body = fake_post.last_call["json"]
    check("no text key present", "text" not in body, body)


def test_response_schema_changes_the_cache_key():
    """Two otherwise-identical calls, one with a schema configured and
    one without, must not collide in the cache -- a schema-conditioned
    generation is a genuinely different request."""
    client_a, _ = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY))
    client_b, _ = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY), response_schema=_SCHEMA_PAYLOAD)
    key_a = client_a._cache_key([{"role": "user", "content": "x"}], 0.0, None)
    key_b = client_b._cache_key([{"role": "user", "content": "x"}], 0.0, None)
    check("cache keys differ when response_schema differs", key_a != key_b, (key_a, key_b))


# --- response parsing / ChatResult mapping -----------------------------------

def test_complete_returns_chat_result_with_real_usage_mapped():
    client, _ = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY))
    result = client.complete([{"role": "user", "content": "x"}])
    check("content extracted", result.content == '```json\n{"action": "call_tool"}\n```', result.content)
    check("prompt_tokens from usage.input_tokens", result.prompt_tokens == 500, result.prompt_tokens)
    check("completion_tokens from usage.output_tokens", result.completion_tokens == 80, result.completion_tokens)
    check("cost_usd from usage.cost", result.cost_usd == 0.002, result.cost_usd)
    check("cached is False on a fresh call", result.cached is False)


def test_reasoning_only_response_yields_none_content_not_a_crash():
    client, _ = _client(FakeResponse(200, _REASONING_ONLY_BODY))
    result = client.complete([{"role": "user", "content": "x"}], max_tokens=16000)
    check("content is None, no exception raised", result.content is None, result.content)
    check("completion_tokens still recorded (16000, the exhausted budget)", result.completion_tokens == 16000)


def test_missing_cost_field_defaults_to_none():
    body = {"output": _MESSAGE_RESPONSE_BODY["output"], "usage": {"input_tokens": 10, "output_tokens": 5}}
    client, _ = _client(FakeResponse(200, body))
    result = client.complete([{"role": "user", "content": "x"}])
    check("cost_usd defaults to None when absent", result.cost_usd is None, result.cost_usd)


# --- caching -------------------------------------------------------------

def test_second_identical_call_hits_cache_not_network():
    client, fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY))
    client.complete([{"role": "user", "content": "x"}], max_tokens=8000)
    call_count_after_first = 1 if fake_post.last_call else 0
    fake_post.last_call = None
    result2 = client.complete([{"role": "user", "content": "x"}], max_tokens=8000)
    check("first call hit the network", call_count_after_first == 1)
    check("second identical call did NOT hit the network", fake_post.last_call is None)
    check("cached result still has correct content", result2.content == _MESSAGE_RESPONSE_BODY["output"][1]["content"][0]["text"])
    check("cached result marked cached=True", result2.cached is True)


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
