"""Thin wrapper around `a4v.llm.ChatClient` for the kernel's decide/
execute/update loop.

Deliberately does NOT use native OpenAI-style tool-calling.
`a4v.llm.ChatClient`'s request body only ever sends `{model, messages,
temperature, top_p, max_tokens}` (confirmed by reading `a4v/llm.py` in
full) -- no `tools`/`tool_choice` field, and nothing parses a `tool_calls`
response field. Extending it to speak native tool-calling would be a
real, cross-cutting change to code every other part of this project also
depends on -- and this project's own documented history is that
provider tool-calling/structured-output support is UNRELIABLE across
models routed through OpenRouter anyway (`a4v/llm.py`'s own docstring:
some models ignore `response_format`; `evmbench` CLAUDE.md: codex CLI's
`wire_api="chat"` fallback was removed outright in 0.104.0). So this
kernel uses the SAME proven pattern every other LLM call in this
codebase already uses: a strict "respond with exactly one fenced JSON
object" prompt contract (rtf.security_agent.prompts), parsed via
`ChatClient.complete_json`'s existing `extract_last_fenced_json`
(first-fence-open/last-fence-close, survives a nested ```solidity block,
same fix already applied everywhere else in this codebase).
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError

from a4v.llm import ChatClient, ChatResult

DEFAULT_MAX_COMPLETION_TOKENS = 8000
"""Real incident, not a guess: a live 2026-08-17 run against 2025-04-forte
(z-ai/glm-5.2, no cap set anywhere -- confirmed by grep, `complete_json`
was never called with `max_tokens`) produced repeated runaway completions
hitting an apparent ~65,536-token provider ceiling on verbose clusters
(cluster_006 alone: 29209, 33813, 23069, 29414, then 65536 completion
tokens on successive turns, the last one costing $0.067 alone) --
truncated/anomalous output that crashed downstream parsing. 8000 is
comfortably above what a legitimate single turn needs (the CEIV schema's
own conclude payload for an 8-property cluster measured ~3000-5000
completion tokens in an earlier, non-runaway live sample) while firmly
capping the pathological case."""


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
        try:
            raw, chat_result = self.chat_client.complete_json(
                messages, temperature=self.temperature, max_tokens=self.max_tokens)
        except json.JSONDecodeError as e:
            # A real, previously-uncaught crash path (2026-08-17 live run,
            # cluster_invocation_crashed:JSONDecodeError): genuinely
            # malformed model output -- not just "extra trailing data",
            # which a4v.llm.extract_last_fenced_json's tolerant fallback
            # already recovers from -- re-raises through ChatClient.
            # Philosophically the SAME failure mode as "matched no
            # accepted action schema" (MalformedModelResponse already
            # covers that), just caught one parsing stage earlier; folded
            # into the same retry-then-give-up path rather than left to
            # crash the whole cluster invocation.
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
