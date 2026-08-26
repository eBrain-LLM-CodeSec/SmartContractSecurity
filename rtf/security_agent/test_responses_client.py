"""Unit tests for rtf.security_agent.responses_client. NO real network
calls -- httpx.Client.post is monkeypatched on the instance. Run with:
    .venv/bin/python3 -m rtf.security_agent.test_responses_client
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from rtf.security_agent.responses_client import NativeToolCall, ResponsesChatClient, _build_input, _extract_output

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


# --- _extract_output ---------------------------------------------------

def test_extract_output_finds_message_item_after_reasoning_items():
    text, tool_calls = _extract_output(_MESSAGE_RESPONSE_BODY["output"])
    check("extracts the message's output_text", text == '```json\n{"action": "call_tool"}\n```', text)
    check("no tool_calls for a plain message response", tool_calls == [], tool_calls)


def test_extract_output_returns_none_for_reasoning_only_output():
    """The actual root-cause scenario this client exists to handle
    correctly: an output array with ONLY reasoning items (the model spent
    its whole budget reasoning, never reached an answer) -- must return
    None cleanly, not raise, so the SAME MalformedModelResponse path
    model_client.py already has for content=None handles it."""
    text, tool_calls = _extract_output(_REASONING_ONLY_BODY["output"])
    check("returns None text for reasoning-only output", text is None, text)
    check("returns no tool_calls for reasoning-only output", tool_calls == [], tool_calls)


def test_extract_output_handles_empty_output():
    check("empty list returns (None, [])", _extract_output([]) == (None, []))
    check("None output returns (None, [])", _extract_output(None) == (None, []))


_PARALLEL_FUNCTION_CALL_BODY_OUTPUT = [
    {"type": "reasoning", "encrypted_content": "...", "summary": []},
    {"type": "function_call", "call_id": "call_1", "name": "get_function_source",
     "arguments": '{"contract": "Vault", "function": "mint"}'},
    {"type": "function_call", "call_id": "call_2", "name": "get_callers",
     "arguments": '{"contract": "Vault", "function": "mint"}'},
]


def test_extract_output_collects_multiple_sibling_function_calls():
    """Live-verified (Part 0, native tool-calling migration): a single
    response can contain several sibling `function_call` items -- the
    whole point of the migration is exploiting this."""
    text, tool_calls = _extract_output(_PARALLEL_FUNCTION_CALL_BODY_OUTPUT)
    check("no message text on a tool-calling-only response", text is None, text)
    check("both function_call items collected", len(tool_calls) == 2, tool_calls)
    check("first call decoded correctly",
          tool_calls[0] == NativeToolCall(call_id="call_1", tool="get_function_source",
                                           args={"contract": "Vault", "function": "mint"}),
          tool_calls[0])
    check("second call decoded correctly",
          tool_calls[1] == NativeToolCall(call_id="call_2", tool="get_callers",
                                           args={"contract": "Vault", "function": "mint"}),
          tool_calls[1])


def test_extract_output_drops_a_function_call_with_unparseable_arguments():
    """Degrades cleanly (drops the one bad call) rather than raising --
    this module has no dependency on model_client.py's error types, and
    an empty tool_calls list already degrades correctly through
    ModelClient.decide()'s existing no-content guard."""
    bad_output = [{"type": "function_call", "call_id": "call_1", "name": "get_callers",
                   "arguments": "{not valid json"}]
    text, tool_calls = _extract_output(bad_output)
    check("no crash; call silently dropped", tool_calls == [], tool_calls)
    check("no text either", text is None, text)


# --- _build_input (message -> Responses API `input` projection) --------------

def test_build_input_passes_plain_entries_through_unchanged():
    messages = [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}]
    check("plain entries pass through unchanged", _build_input(messages) == messages, _build_input(messages))


def test_build_input_expands_a_tool_call_request_entry():
    messages = [{"role": "assistant", "tool_calls": [
        {"call_id": "call_1", "tool": "get_callers", "args": {"contract": "Vault", "function": "mint"}},
        {"call_id": "call_2", "tool": "get_callees", "args": {"contract": "Vault", "function": "mint"}},
    ]}]
    result = _build_input(messages)
    check("one function_call item per tool_calls entry", len(result) == 2, result)
    check("call_id/name/arguments correctly projected",
          result[0] == {"type": "function_call", "call_id": "call_1", "name": "get_callers",
                        "arguments": json.dumps({"contract": "Vault", "function": "mint"})},
          result[0])


def test_build_input_projects_a_tool_result_entry():
    messages = [{"role": "tool", "call_id": "call_1", "tool": "get_callers", "content": "Tool result: ..."}]
    result = _build_input(messages)
    check("becomes a function_call_output item",
          result == [{"type": "function_call_output", "call_id": "call_1", "output": "Tool result: ..."}], result)


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


# --- native tool-calling (tools/tool_choice/parallel_tool_calls) wiring ------

_TOOLS_PAYLOAD = [{"type": "function", "name": "get_callers", "description": "...",
                   "parameters": {"type": "object", "properties": {}, "required": [],
                                  "additionalProperties": False}, "strict": True}]


def test_tools_tool_choice_parallel_tool_calls_sent_when_configured():
    client, fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY), tools=_TOOLS_PAYLOAD,
                                 tool_choice="auto", parallel_tool_calls=True)
    client.complete([{"role": "user", "content": "x"}])
    body = fake_post.last_call["json"]
    check("tools carried in the request body", body.get("tools") == _TOOLS_PAYLOAD, body.get("tools"))
    check("tool_choice carried", body.get("tool_choice") == "auto", body.get("tool_choice"))
    check("parallel_tool_calls carried", body.get("parallel_tool_calls") is True, body.get("parallel_tool_calls"))


def test_no_native_tool_keys_sent_when_not_configured():
    """Backward compatibility: a client built without tools/tool_choice/
    parallel_tool_calls (every pre-migration construction site) sends
    none of these keys at all -- unchanged prior wire behavior."""
    client, fake_post = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY))
    client.complete([{"role": "user", "content": "x"}])
    body = fake_post.last_call["json"]
    check("no tools key present", "tools" not in body, body)
    check("no tool_choice key present", "tool_choice" not in body, body)
    check("no parallel_tool_calls key present", "parallel_tool_calls" not in body, body)


def test_tools_changes_the_cache_key():
    client_a, _ = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY))
    client_b, _ = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY), tools=_TOOLS_PAYLOAD)
    key_a = client_a._cache_key([{"role": "user", "content": "x"}], 0.0, None)
    key_b = client_b._cache_key([{"role": "user", "content": "x"}], 0.0, None)
    check("cache keys differ when tools differs", key_a != key_b, (key_a, key_b))


_FUNCTION_CALL_RESPONSE_BODY = {
    "output": _PARALLEL_FUNCTION_CALL_BODY_OUTPUT,
    "usage": {"input_tokens": 400, "output_tokens": 60, "cost": 0.0015},
}


def test_complete_returns_tool_calls_for_a_native_tool_calling_response():
    client, _ = _client(FakeResponse(200, _FUNCTION_CALL_RESPONSE_BODY))
    result = client.complete([{"role": "user", "content": "x"}])
    check("content is None (tool calls, no text)", result.content is None, result.content)
    check("tool_calls populated", result.tool_calls is not None and len(result.tool_calls) == 2, result.tool_calls)


def test_complete_returns_none_tool_calls_for_a_plain_text_response():
    client, _ = _client(FakeResponse(200, _MESSAGE_RESPONSE_BODY))
    result = client.complete([{"role": "user", "content": "x"}])
    check("tool_calls is None for a plain-text response", result.tool_calls is None, result.tool_calls)


def test_second_identical_call_with_tool_calls_hits_cache_with_tool_calls_intact():
    """The local disk cache must round-trip tool_calls too, not just
    content/tokens -- easy to miss since the cache never needed to store
    more than that before this migration."""
    client, fake_post = _client(FakeResponse(200, _FUNCTION_CALL_RESPONSE_BODY))
    client.complete([{"role": "user", "content": "x"}])
    fake_post.last_call = None
    result2 = client.complete([{"role": "user", "content": "x"}])
    check("second call did not hit the network", fake_post.last_call is None)
    check("cached result still has tool_calls",
          result2.tool_calls == [
              NativeToolCall(call_id="call_1", tool="get_function_source",
                              args={"contract": "Vault", "function": "mint"}),
              NativeToolCall(call_id="call_2", tool="get_callers",
                              args={"contract": "Vault", "function": "mint"}),
          ], result2.tool_calls)
    check("cached result marked cached=True", result2.cached is True)


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
