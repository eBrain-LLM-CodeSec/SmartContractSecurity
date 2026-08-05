"""OpenRouter chat client: on-disk cache, retries, token accounting, and
last-fence JSON extraction (some models, e.g. GLM, ignore response_format
and return ordinary markdown-fenced JSON -- see evmbench CLAUDE.md Run 4).

Uses the *last* ``` fence as the closing delimiter, not the first: a
finding's own rationale/fix text can embed a nested ```solidity fence, which
truncates mid-string if you close on the first one (a real bug hit and fixed
in orchestrate_pipeline.py; mirrored here).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class LLMError(Exception):
    pass


@dataclass
class ChatResult:
    content: str
    prompt_tokens: int
    completion_tokens: int
    cached: bool


def _parse_json_tolerant(s: str) -> dict:
    """`json.loads`, falling back to decoding just the first complete JSON
    value in `s` if there's trailing garbage after it. Hit live (RTF L8
    validation, 2026-08-06): openai/gpt-5.1-codex-max occasionally emits one
    extra stray closing brace after an otherwise complete, valid object --
    e.g. `{"decision": "PASS", ...}}` with an extra `}` tacked on. Plain
    `json.loads` raises "Extra data" on this even though the actual object
    is well-formed; `raw_decode` parses the first valid value and reports
    where it ended, ignoring whatever comes after.
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        if e.msg != "Extra data":
            raise
        obj, _end = json.JSONDecoder().raw_decode(s)
        return obj


def _strip_fence_language_tag(body: str) -> str:
    first_newline = body.find("\n")
    if first_newline != -1 and body[:first_newline].strip().isalpha():
        return body[first_newline + 1:]
    return body


def extract_last_fenced_json(text: str) -> dict:
    """Parse the outermost fenced code block in `text` as JSON: the *first*
    ``` in the text is the opening delimiter, the *last* ``` is the closing
    one. A finding's rationale/fix text can embed its own nested ```solidity
    fence, which breaks a naive "nearest previous fence" search (it finds the
    inner block's closing fence, not the outer opening one) -- first/last is
    the version of this fix that survives that case. Falls back to parsing
    the whole text if there are no fences at all.

    Three cases, not two: hit live (RTF L8 validation, 2026-08-06) --
    openai/gpt-5.1-codex-max sometimes opens a ```json fence and never closes
    it (the body itself is complete, well-formed JSON; only the closing
    marker is missing). The original two-way branch conflated "no fence at
    all" with "exactly one fence, unclosed", parsing the WHOLE text
    (including the leading ```json prefix) in both cases -- wrong for the
    unclosed-fence case, which needs the prefix stripped like the normal
    case, just reading to the end of the string instead of to a closing
    fence.
    """
    fence = "```"
    first_open = text.find(fence)
    last_close = text.rfind(fence)

    if first_open == -1:
        return _parse_json_tolerant(text)
    if first_open == last_close:
        # Exactly one fence marker -- opened but never closed.
        body = text[first_open + len(fence):]
        return _parse_json_tolerant(_strip_fence_language_tag(body).strip())

    body = text[first_open + len(fence):last_close]
    return _parse_json_tolerant(_strip_fence_language_tag(body).strip())


class ChatClient:
    def __init__(self, base_url: str, api_key: str, model: str,
                 cache_dir: Path, token_log_path: Path | None = None,
                 timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.token_log_path = token_log_path
        self._client = httpx.Client(timeout=timeout)

    def _cache_key(self, messages: list[dict], temperature: float) -> str:
        payload = json.dumps({"model": self.model, "messages": messages, "temperature": temperature}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _log_tokens(self, prompt_tokens: int, completion_tokens: int, cached: bool) -> None:
        if not self.token_log_path:
            return
        self.token_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.token_log_path.open("a") as f:
            f.write(json.dumps({
                "model": self.model, "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens, "cached": cached, "ts": time.time(),
            }) + "\n")

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    def _post(self, messages: list[dict], temperature: float) -> dict:
        resp = self._client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "messages": messages, "temperature": temperature},
        )
        if resp.status_code == 429 or resp.status_code >= 500:
            resp.raise_for_status()
        if resp.status_code >= 400:
            raise LLMError(f"OpenRouter error {resp.status_code}: {resp.text[:1000]}")
        return resp.json()

    def complete(self, messages: list[dict], temperature: float = 0.0) -> ChatResult:
        key = self._cache_key(messages, temperature)
        cache_path = self._cache_path(key)
        if cache_path.exists():
            data = json.loads(cache_path.read_text())
            self._log_tokens(data["prompt_tokens"], data["completion_tokens"], cached=True)
            return ChatResult(content=data["content"], prompt_tokens=data["prompt_tokens"],
                               completion_tokens=data["completion_tokens"], cached=True)

        data = self._post(messages, temperature)
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        cache_path.write_text(json.dumps({
            "content": content, "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
        }))
        self._log_tokens(prompt_tokens, completion_tokens, cached=False)
        return ChatResult(content=content, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, cached=False)

    def complete_json(self, messages: list[dict], temperature: float = 0.0) -> tuple[dict, ChatResult]:
        result = self.complete(messages, temperature=temperature)
        return extract_last_fenced_json(result.content), result

    @classmethod
    def from_config(cls, cfg: dict, model: str, cache_dir: Path, token_log_path: Path | None = None) -> "ChatClient":
        api_key = Path(cfg["api_key_file"]).read_text().strip()
        return cls(base_url=cfg["base_url"], api_key=api_key, model=model,
                   cache_dir=cache_dir, token_log_path=token_log_path)
