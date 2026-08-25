"""Thin wrapper around `a4v.llm.ChatClient` for the kernel's decide/
execute/update loop.

Deliberately does NOT use native OpenAI-style *tool-calling*
(`tools`/`tool_choice`/`tool_calls`) -- `a4v.llm.ChatClient`'s request
body never sends those fields, and extending it to would be a real,
cross-cutting change to shared code every other part of this project
also depends on. So this kernel's PROMPT contract is still "respond with
exactly one JSON object" (rtf.security_agent.prompts).

The PARSING side, however, uses `extract_last_fenced_json` for a reason
independent of structured output: it already handles both a fenced
```json block AND bare (unfenced) JSON with no fence markers at all
(`a4v/llm.py`: `first_open == -1` falls back to parsing the whole text)
-- exactly what `ResponsesChatClient` returns when its own optional
`response_schema` is set (see `response_schema.py` and that client's
own docstring for the live-verified correction to this project's
earlier "structured output doesn't work for this model" finding, which
was scoped to a different mechanism, Codex CLI's `--output-schema`).
This module needed no changes to support that -- the same parsing path
already worked for both cases.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError

from a4v.llm import ChatClient, ChatResult, extract_last_fenced_json

DEFAULT_MAX_COMPLETION_TOKENS = 16000
"""Real incident #1 (2026-08-17, first forte run): no cap set anywhere
produced repeated runaway completions hitting an apparent ~65,536-token
provider ceiling on verbose clusters (cluster_006: 29209, 33813, 23069,
29414, then 65536 completion tokens on successive turns, the last one
costing $0.067 alone) -- truncated/anomalous output that crashed
downstream parsing. An 8000 cap was applied to fix this.

Real incident #2 (2026-08-17, rerun with that 8000 cap): z-ai/glm-5.2 is
a reasoning model -- on large/complex clusters (8 properties) it can
spend its ENTIRE completion budget on internal reasoning tokens without
ever emitting a visible answer (`content: null`, `completion_tokens`
exactly at the 8000 cap, confirmed live in two separate clusters' cached
raw responses). Raised to 16000 to give real reasoning headroom while
staying well below the original 65,536-token pathological ceiling; see
ModelClient.decide's own None-content guard for what happens when even
this isn't enough."""


class MalformedModelResponse(Exception):
    """The model's JSON response matched none of the accepted action
    schemas. Callers decide what to do (retry with a corrective message,
    or give up and record it) -- this class only carries the diagnostic
    information needed to do either."""

    def __init__(self, raw: dict, errors: str):
        self.raw = raw
        self.errors = errors
        super().__init__(f"model response matched no accepted action schema: {errors}\nraw: {raw}")


@dataclass
class ModelTurn:
    parsed: BaseModel
    """Whichever of `response_models` successfully validated, in order."""
    chat_result: ChatResult | None
    """None only under a test double that doesn't model real token/cost
    accounting (matches this codebase's existing FakeChatClient
    convention, e.g. rtf.l11_investigation_grouping.test_semantic_only_
    driver.FakeChatClient) -- real ChatClient calls always return one."""
    raw: dict


class ModelClient:
    def __init__(self, chat_client: ChatClient, response_models: tuple[type[BaseModel], ...],
                 temperature: float = 0.0, max_tokens: int | None = DEFAULT_MAX_COMPLETION_TOKENS):
        self.chat_client = chat_client
        self.response_models = response_models
        self.temperature = temperature
        self.max_tokens = max_tokens

    def decide(self, messages: list[dict]) -> ModelTurn:
        # Calls ChatClient.complete() directly (not complete_json) so
        # content=None can be caught BEFORE it ever reaches
        # extract_last_fenced_json -- see incident #2 in
        # DEFAULT_MAX_COMPLETION_TOKENS's docstring: a real, previously-
        # uncaught crash (extract_last_fenced_json(None) -> AttributeError,
        # 'NoneType' object has no attribute 'find') confirmed live in two
        # separate clusters' cached raw responses on 2026-08-17.
        chat_result = self.chat_client.complete(
            messages, temperature=self.temperature, max_tokens=self.max_tokens)
        if not chat_result.content:
            raise MalformedModelResponse(
                {}, "response had no content -- the model likely exhausted its reasoning "
                    "budget without producing an answer; respond more concisely, one action per turn")
        try:
            raw = extract_last_fenced_json(chat_result.content)
        except json.JSONDecodeError as e:
            # A real, previously-uncaught crash path (2026-08-17 live run,
            # cluster_invocation_crashed:JSONDecodeError): genuinely
            # malformed model output -- not just "extra trailing data",
            # which extract_last_fenced_json's tolerant fallback already
            # recovers from. Philosophically the SAME failure mode as
            # "matched no accepted action schema" (MalformedModelResponse
            # already covers that), just caught one parsing stage earlier;
            # folded into the same retry-then-give-up path rather than
            # left to crash the whole cluster invocation.
            raise MalformedModelResponse({}, f"response was not valid JSON: {e}") from e
        errors = []
        for model_cls in self.response_models:
            try:
                parsed = model_cls.model_validate(raw)
            except ValidationError as e:
                errors.append(f"{model_cls.__name__}: {e}")
                continue
            return ModelTurn(parsed=parsed, chat_result=chat_result, raw=raw)
        raise MalformedModelResponse(raw, "; ".join(errors))
