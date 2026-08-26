"""Client for OpenAI's Responses API (`POST {base_url}/responses`), routed
through OpenRouter -- the SAME wire format the existing Codex investigator
already uses successfully against z-ai/glm-5.2 (`arm_c_codex.py`'s
`DEFAULT_WIRE_API = "responses"`, confirmed live: the real Codex baseline
run against forte never hit a reasoning-budget-exhaustion failure).

Why this exists as a SEPARATE client from `a4v.llm.ChatClient`, not a
change to it: `ChatClient` posts to `/chat/completions` (the older Chat
Completions format) and is shared, general-purpose infrastructure other
parts of this codebase depend on (Commentator, embedding ranking, etc.).
The Responses API has a genuinely different request/response shape (an
`input` array instead of `messages`, an `output` array of typed items
instead of `choices[0].message.content`, a separate `reasoning.effort`
control) -- retrofitting that in place would be a real cross-cutting
change to shared code. This client is isolated to `rtf/security_agent/`.

The actual root-cause fix this closes (found live, 2026-08-17, during the
second forte rerun): `max_output_tokens` in the Responses API is STILL a
combined cap on reasoning + visible output (confirmed via OpenAI's own
docs), so simply switching wire formats does not alone prevent a model
from exhausting its budget on reasoning. The real lever is
`reasoning.effort` (minimal/low/medium/high) -- explicitly telling the
model how much to reason, rather than gambling that a flat token count
works out. Defaults to "low": our CEIV schema's own structure already
does much of the "thinking out loud" work the schema demands (hypotheses,
hypothesis status, hypothesis/evidence citations are all EXPLICIT
structured fields the model fills in, not something it needs extensive
freeform reasoning to arrive at first).

Structured-output correction (found live, 2026-08-25, canto run):
`rtf.security_agent.model_client`'s own docstring previously claimed
"provider tool-calling/structured-output support is UNRELIABLE... some
models ignore response_format" and concluded native structured output
wasn't worth pursuing for this kernel. That finding was real but scoped
to a DIFFERENT mechanism -- Codex CLI's own `--output-schema` flag
(`pipeline_lite` validation, 2026-08-xx) -- not the raw Responses API
`text.format: {type: "json_schema", strict: true}` parameter THIS
client actually posts. A direct test against that parameter with
z-ai/glm-5.2 returned clean, schema-conformant bare JSON (no markdown
fencing) for both the simplest (call_tool) and most complex (conclude,
with nested evidence/hypotheses/properties arrays) action shapes. See
`response_schema.py` for the schema builder this client's optional
`response_schema` constructor param expects.

Prompt-caching via `session_id` (found live, 2026-08-26, prompted by a
user tip after the canto cost gap was traced to this client resending
the ENTIRE conversation, uncached, on every single turn -- $3.045 vs.
Codex's $1.84 for the same target): OpenRouter's `/responses` proxy
REJECTS the OpenAI-native `previous_response_id` stateful-chaining
mechanism outright (`"expected null, received string"` -- confirmed via
a direct live test; that mechanism requires provider-side conversation
storage OpenRouter's proxy does not offer). It DOES support a different,
simpler mechanism: an opaque `session_id` string in the request body.
Verified via 3 separate live tests against z-ai/glm-5.2: with NO
`session_id`, `usage.input_tokens_details.cached_tokens` is always 0
(full price every call, matching this client's pre-fix behavior
exactly); WITH a `session_id` present, a repeated/overlapping prefix
across calls gets `cached_tokens` covering nearly the entire shared
prefix, at roughly 1/9th the cost for that portion. This is a "sticky
routing" hint (keeps requests landing on the same backend so ITS OWN KV
cache stays warm), NOT guaranteed provider-side storage like
`previous_response_id` -- a 5-turn live test hit the cache on 4 of 5
non-baseline calls, not all of them (one miss, likely routing/TTL
variance) -- still a large net win (~2x cheaper across that sequence,
up to ~9x on an actual hit), but never assume a specific call will hit.
Unlike `previous_response_id`, this needs NO change to what `messages`/
`input` this client sends -- the full conversation is still transmitted
every call, exactly as before; `session_id` only affects routing/
caching on the provider side. One `ResponsesChatClient` instance = one
cluster investigation (confirmed in `investigator.py`), so the
`session_id` is set once at construction and reused for every call the
instance makes.

Native tool-calling (found live, 2026-08-26, Part 0 of the native-tool-
calling migration): `model_client.py`'s docstring previously claimed
native OpenAI-style tool-calling (`tools`/`tool_choice`/`tool_calls`)
was deliberately unused because `a4v.llm.ChatClient` has no support for
it and extending shared infra was too risky. That constraint never
applied to THIS client -- it already posts directly to `/responses`
with its own request body, independent of `a4v.llm.ChatClient`. A live
test against z-ai/glm-5.2 (3 real tools, real JSON-schema `parameters`)
confirmed: (1) `tools=[...]`/`tool_choice: "auto"` is accepted and
produces a correct `function_call` output item; (2) with
`parallel_tool_calls: true` and a prompt asking for several independent
facts at once, the model returned 3 sibling `function_call` items in
ONE response, each with correctly-typed args (including a boolean
default field); (3) feeding the `function_call` items back verbatim
plus one `function_call_output` per `call_id` is accepted and produces
a coherent next response; (4) `tools` and `text.format` (structured
output) coexist cleanly -- the model correctly picks the schema-
conformant JSON path when told not to call a tool; (5) `session_id`
caching survives a mixed tool-call history (a second call built on a
`function_call`/`function_call_output` history from the first still hit
`cached_tokens` on ~99% of its input). No blockers found; see
`kernel.py`'s dispatch loop and `context_manager.py` for how the kernel
side of this is wired.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from a4v.llm import (
    LLMError, RETRY_MAX_ATTEMPTS, RETRY_WAIT_MAX, RETRY_WAIT_MIN,
    RETRY_WAIT_MULTIPLIER,
)

DEFAULT_TIMEOUT_SECONDS = 120.0


@dataclass(frozen=True)
class NativeToolCall:
    """One `type: "function_call"` item from the Responses API's `output`
    array, decoded. `call_id` MUST be echoed back verbatim on the
    matching `function_call_output` entry -- the API correlates request
    and result by this id, not by position (live-verified, Part 0)."""
    call_id: str
    tool: str
    args: dict


@dataclass
class ResponsesResult:
    """Same fields as `a4v.llm.ChatResult` (drop-in for every existing
    reader: `kernel.py`'s `_record_token_usage`, `model_client.py`'s
    `decide()`) plus `tool_calls` -- non-empty only for a native
    tool-calling turn, in which case `content` is typically None (the
    model called tools instead of answering in text)."""
    content: str | None
    prompt_tokens: int
    completion_tokens: int
    cached: bool
    cost_usd: float | None = None
    tool_calls: list[NativeToolCall] | None = None


def _extract_output(output: list[dict]) -> tuple[str | None, list[NativeToolCall]]:
    """Walks the Responses API's `output` array once, collecting both a
    `type: "message"` item's `output_text` (as before) AND any
    `type: "function_call"` items (new). Returns `(text, tool_calls)` --
    exactly one of these is typically populated for a real turn, but
    both are extracted independently so a mixed response degrades
    gracefully rather than silently dropping one side. A
    `type: "reasoning"` item (or anything else) is skipped, same as
    before. An unparseable `arguments` string drops that one call
    silently (contributes nothing) rather than raising here -- this
    module has no dependency on `model_client.py`'s error types, and an
    empty `tool_calls` list already degrades correctly through
    `ModelClient.decide()`'s existing no-content guard."""
    text: str | None = None
    tool_calls: list[NativeToolCall] = []
    for item in output or []:
        item_type = item.get("type")
        if item_type == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    text = part.get("text")
        elif item_type == "function_call":
            try:
                args = json.loads(item.get("arguments") or "{}")
            except json.JSONDecodeError:
                continue
            tool_calls.append(NativeToolCall(call_id=item["call_id"], tool=item["name"], args=args))
    return text, tool_calls


def _build_input(messages: list[dict]) -> list[dict]:
    """Projects this kernel's `messages` entries into the Responses API's
    `input` array. Three entry shapes (see `context_manager.py`/
    `kernel.py`'s grouped-append helper for how these are produced):

    - plain (`{"role", "content"}`, any role): passes through unchanged,
      exactly as before this migration.
    - a tool-call REQUEST (`{"role": "assistant", "tool_calls": [...]}`,
      no `content` key): expands to one `type: "function_call"` item per
      entry in `tool_calls`, `arguments` re-serialized to a JSON string
      (the wire format the API returned it as originally).
    - a tool-call RESULT (`{"role": "tool", "call_id", "tool", "content"}`):
      becomes one `type: "function_call_output"` item, `call_id` echoed
      verbatim -- this is what correlates a result back to its request;
      getting it wrong produces an invalid next request (Part 0, live-
      verified)."""
    input_items: list[dict] = []
    for m in messages:
        if m.get("role") == "assistant" and "tool_calls" in m:
            for call in m["tool_calls"]:
                input_items.append({
                    "type": "function_call", "call_id": call["call_id"],
                    "name": call["tool"], "arguments": json.dumps(call["args"]),
                })
        elif m.get("role") == "tool":
            input_items.append({
                "type": "function_call_output", "call_id": m["call_id"], "output": m["content"],
            })
        else:
            input_items.append({"role": m["role"], "content": m["content"]})
    return input_items


class ResponsesChatClient:
    """Same public interface as `a4v.llm.ChatClient`
    (`.complete(messages, temperature, top_p, max_tokens) -> <result>`)
    -- a drop-in replacement wherever a chat_client is duck-typed against
    that method, e.g. `rtf.security_agent.model_client.ModelClient`.
    Returns `ResponsesResult`, not `a4v.llm.ChatResult` itself -- every
    reader duck-types on the shared fields (`content`/`prompt_tokens`/
    `completion_tokens`/`cached`/`cost_usd`), plus the new `tool_calls`
    field a plain `ChatResult` never has (`ModelClient.decide()` checks
    for it via `getattr(..., "tool_calls", None)`, not `isinstance`)."""

    def __init__(self, base_url: str, api_key: str, model: str,
                 cache_dir: Path, token_log_path: Path | None = None,
                 timeout: float = DEFAULT_TIMEOUT_SECONDS, reasoning_effort: str = "low",
                 response_schema: dict | None = None, session_id: str | None = None,
                 tools: list[dict] | None = None, tool_choice: str | dict | None = None,
                 parallel_tool_calls: bool | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.token_log_path = token_log_path
        self.timeout = timeout
        self.reasoning_effort = reasoning_effort
        self.response_schema = response_schema
        """Optional `text.format` payload (see `rtf.security_agent.
        response_schema.build_strict_schema`) -- when set, the Responses
        API constrains generation to the schema's shape directly, rather
        than the kernel only discovering a malformed shape after the
        fact via fenced-JSON parsing. Live-verified (2026-08-25 canto
        run) that z-ai/glm-5.2 honors this correctly for the kernel's
        full 3-action discriminated union, including the most complex
        (conclude) branch. None preserves the prior prompt-only
        behavior -- kept opt-in so existing tests/callers that construct
        a client without one see no behavior change."""
        self.session_id = session_id
        """Opaque OpenRouter prompt-caching hint (see module docstring for
        the live-verified cost mechanics). None preserves the pre-fix
        behavior (no session_id sent, no caching) -- kept opt-in so
        existing tests/callers that construct a client without one see
        no behavior change. A real live run should always set this, one
        stable value per cluster investigation (e.g. the case_id)."""
        self.tools = tools
        self.tool_choice = tool_choice
        self.parallel_tool_calls = parallel_tool_calls
        """Native tool-calling controls (see module docstring's Part 0
        finding). All three None preserves the pre-native behavior
        exactly (no `tools` key sent at all) -- kept opt-in so existing
        tests/callers that construct a client without them see no
        behavior change."""
        self._client = httpx.Client(timeout=timeout)

    def _cache_key(self, messages: list[dict], temperature: float, max_tokens: int | None) -> str:
        payload = {"model": self.model, "messages": messages, "temperature": temperature,
                   "reasoning_effort": self.reasoning_effort}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if self.response_schema is not None:
            payload["response_schema"] = self.response_schema
        if self.tools is not None:
            payload["tools"] = self.tools
        if self.tool_choice is not None:
            payload["tool_choice"] = self.tool_choice
        if self.parallel_tool_calls is not None:
            payload["parallel_tool_calls"] = self.parallel_tool_calls
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _log_tokens(self, prompt_tokens: int, completion_tokens: int, cached: bool,
                     cost_usd: float | None = None, provider_cached_tokens: int | None = None) -> None:
        if not self.token_log_path:
            return
        self.token_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.token_log_path.open("a") as f:
            f.write(json.dumps({
                "model": self.model, "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens, "cached": cached, "cost_usd": cost_usd,
                # Distinct from `cached` above (a LOCAL disk-cache hit,
                # meaning this call never touched the network at all):
                # this is OpenRouter's own reported prompt-cache hit count
                # for a real network call (usage.input_tokens_details.
                # cached_tokens) -- see the module docstring's session_id
                # finding. None on a local cache hit (no real usage data
                # to report) or if the provider didn't include the field.
                "provider_cached_tokens": provider_cached_tokens,
                "ts": time.time(), "wire_api": "responses",
            }) + "\n")

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=RETRY_WAIT_MULTIPLIER, min=RETRY_WAIT_MIN, max=RETRY_WAIT_MAX),
        reraise=True,
    )
    def _post(self, messages: list[dict], temperature: float, max_tokens: int | None) -> dict:
        body = {
            "model": self.model,
            "input": _build_input(messages),
            "temperature": temperature,
            "reasoning": {"effort": self.reasoning_effort},
        }
        if max_tokens is not None:
            body["max_output_tokens"] = max_tokens
        if self.response_schema is not None:
            body["text"] = {"format": self.response_schema}
        if self.session_id is not None:
            body["session_id"] = self.session_id
        if self.tools is not None:
            body["tools"] = self.tools
        if self.tool_choice is not None:
            body["tool_choice"] = self.tool_choice
        if self.parallel_tool_calls is not None:
            body["parallel_tool_calls"] = self.parallel_tool_calls
        resp = self._client.post(
            f"{self.base_url}/responses",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=body,
        )
        if resp.status_code == 429 or resp.status_code >= 500:
            resp.raise_for_status()
        if resp.status_code >= 400:
            raise LLMError(f"OpenRouter /responses error {resp.status_code}: {resp.text[:1000]}")
        return resp.json()

    def complete(self, messages: list[dict], temperature: float = 0.0,
                 top_p: float | None = None, max_tokens: int | None = None) -> ResponsesResult:
        # top_p accepted for interface compatibility with a4v.llm.ChatClient
        # (ModelClient.decide never actually passes it), not forwarded --
        # the Responses API's reasoning-effort control is the lever this
        # client uses instead.
        del top_p
        key = self._cache_key(messages, temperature, max_tokens)
        cache_path = self._cache_path(key)
        if cache_path.exists():
            data = json.loads(cache_path.read_text())
            self._log_tokens(data["prompt_tokens"], data["completion_tokens"], cached=True)
            cached_tool_calls = [NativeToolCall(**tc) for tc in data.get("tool_calls") or []] or None
            return ResponsesResult(content=data["content"], prompt_tokens=data["prompt_tokens"],
                                    completion_tokens=data["completion_tokens"], cached=True,
                                    tool_calls=cached_tool_calls)

        data = self._post(messages, temperature, max_tokens)
        content, tool_calls = _extract_output(data.get("output", []))
        usage = data.get("usage", {}) or {}
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)
        cost_usd = usage.get("cost")  # OpenRouter-specific; None if absent, matching a4v.llm.ChatClient
        provider_cached_tokens = (usage.get("input_tokens_details") or {}).get("cached_tokens")

        cache_path.write_text(json.dumps({
            "content": content, "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
            "tool_calls": [{"call_id": tc.call_id, "tool": tc.tool, "args": tc.args} for tc in tool_calls],
        }))
        self._log_tokens(prompt_tokens, completion_tokens, cached=False, cost_usd=cost_usd,
                         provider_cached_tokens=provider_cached_tokens)
        return ResponsesResult(content=content, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                                cached=False, cost_usd=cost_usd, tool_calls=tool_calls or None)
