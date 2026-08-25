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
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from a4v.llm import (
    ChatResult, LLMError, RETRY_MAX_ATTEMPTS, RETRY_WAIT_MAX, RETRY_WAIT_MIN,
    RETRY_WAIT_MULTIPLIER,
)

DEFAULT_TIMEOUT_SECONDS = 120.0


def _extract_output_text(output: list[dict]) -> str | None:
    """Finds the first `type: "message"` item in the Responses API's
    `output` array and returns its `output_text` content, or None if no
    message item is present (a real, expected outcome -- a response that
    is ENTIRELY `type: "reasoning"` items means the model spent its whole
    budget on reasoning and never got to the answer; treated as no-content
    the same way a4v.llm-based content=None is, not a crash)."""
    for item in output or []:
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                return part.get("text")
    return None


class ResponsesChatClient:
    """Same public interface as `a4v.llm.ChatClient` (`.complete(messages,
    temperature, top_p, max_tokens) -> ChatResult`) -- a drop-in
    replacement wherever a chat_client is duck-typed against that method,
    e.g. `rtf.security_agent.model_client.ModelClient`."""

    def __init__(self, base_url: str, api_key: str, model: str,
                 cache_dir: Path, token_log_path: Path | None = None,
                 timeout: float = DEFAULT_TIMEOUT_SECONDS, reasoning_effort: str = "low",
                 response_schema: dict | None = None, session_id: str | None = None):
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
        self._client = httpx.Client(timeout=timeout)

    def _cache_key(self, messages: list[dict], temperature: float, max_tokens: int | None) -> str:
        payload = {"model": self.model, "messages": messages, "temperature": temperature,
                   "reasoning_effort": self.reasoning_effort}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if self.response_schema is not None:
            payload["response_schema"] = self.response_schema
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
            "input": [{"role": m["role"], "content": m["content"]} for m in messages],
            "temperature": temperature,
            "reasoning": {"effort": self.reasoning_effort},
        }
        if max_tokens is not None:
            body["max_output_tokens"] = max_tokens
        if self.response_schema is not None:
            body["text"] = {"format": self.response_schema}
        if self.session_id is not None:
            body["session_id"] = self.session_id
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
                 top_p: float | None = None, max_tokens: int | None = None) -> ChatResult:
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
            return ChatResult(content=data["content"], prompt_tokens=data["prompt_tokens"],
                              completion_tokens=data["completion_tokens"], cached=True)

        data = self._post(messages, temperature, max_tokens)
        content = _extract_output_text(data.get("output", []))
        usage = data.get("usage", {}) or {}
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)
        cost_usd = usage.get("cost")  # OpenRouter-specific; None if absent, matching a4v.llm.ChatClient
        provider_cached_tokens = (usage.get("input_tokens_details") or {}).get("cached_tokens")

        cache_path.write_text(json.dumps({
            "content": content, "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
        }))
        self._log_tokens(prompt_tokens, completion_tokens, cached=False, cost_usd=cost_usd,
                         provider_cached_tokens=provider_cached_tokens)
        return ChatResult(content=content, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                          cached=False, cost_usd=cost_usd)
