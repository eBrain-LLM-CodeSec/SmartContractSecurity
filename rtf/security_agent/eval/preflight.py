"""Cheap, mandatory compatibility check run before any paid RTF
investigation for a candidate model (Phase 4 of the model-eval harness
spec).

This exists because the GPT-5.6 Sol controlled test discovered a real,
live-blocking incompatibility only once money was already being spent: a
`strict: true` tool schema that omitted an optional parameter from
`required` was silently tolerated by z-ai/glm-5.2/5.3 but flatly rejected
by OpenAI/Azure's own function-calling validator. That specific gap is now
closed for good (`tools.build_tool_schemas()` always lists every
parameter in `required`), but the underlying risk -- SOME wire-format or
capability assumption breaking for a NEW provider -- is not something this
registry can predict in advance. `run_preflight` makes exactly two live
calls, both tiny, both using the REAL schemas/tools the actual
investigation will send (not a simplified stand-in), so a rejection here
is the same rejection a real run would hit, just before any real
investigation spend happens.

Deliberately reuses `ResponsesChatClient` rather than a new HTTP client --
"reuse the existing API/client abstraction," per the task spec.

Schema source (IMPORTANT): callers running against the frozen baseline
checkout (`run_model_eval.py` always does) MUST pass the exact schema
list that checkout's `_frozen_worker.py --emit-tool-schemas` produced, via
the `tool_schemas` parameter -- this module's own worktree copy of
`rtf.security_agent.kernel`/`tools`/`response_schema` may not be
byte-identical to the frozen checkout (e.g. the current worktree HEAD's
`ConcludeAction` may carry newer fields, like the anti-anchoring gate's
`preconditions_satisfied`, that a61d547 predates). Only when `tool_schemas`
is omitted does this module fall back to building schemas from ITS OWN
import of the worktree's kernel/tools -- fine for a standalone
connectivity smoke test, wrong for anything meant to gate a real run
against a pinned checkout.
"""
from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from a4v.llm import LLMError
from rtf.security_agent.eval.model_registry import ModelConfig
from rtf.security_agent.responses_client import ResponsesChatClient

_PREFLIGHT_CONCLUDE_PROMPT = (
    "This is a compatibility preflight check, not a real investigation. "
    "Call the `conclude` tool exactly once, with action=\"conclude\", and "
    "these exact arguments: "
    'evidence=[{"id": "ev-1", "claim": "preflight placeholder", "raw_excerpt": "n/a", '
    '"source_tool": "get_contract_source", "source_file": "n/a"}], '
    'hypotheses=[{"id": "hyp-1", "statement": "preflight placeholder", "status": "unresolved", '
    '"supporting_evidence_ids": [], "contradicting_evidence_ids": []}], '
    'properties=[{"property_id": "preflight-check", "decision": "NOT_APPLICABLE", '
    '"evidence_ids": [], "hypothesis_ids": [], "rationale": "preflight compatibility check"}], '
    "counterexample_attempts=[]. "
    "Do not call any other tool, and do not explain -- just call conclude."
)

_REQUIRED_FIELD_ERROR_MARKERS = ("invalid_function_parameters", "'required' is required")
_REASONING_FIELD_ERROR_MARKERS = ("reasoning",)


@dataclass
class PreflightResult:
    model_key: str
    openrouter_model_id: str
    api_reachable: bool = False
    model_responded: bool = False
    ping_content: str | None = None
    tool_schema_accepted: bool | None = None
    """None = never got far enough to test (e.g. connectivity failed).
    False = the provider rejected the exact tool schema list the real
    investigation sends (the Sol/`required`-fields failure mode)."""
    tool_call_emitted: bool | None = None
    """Whether the model actually returned a `conclude` tool call (vs.
    answering in plain text) once the schema itself was accepted. A
    schema-accepted-but-no-tool-call outcome is model BEHAVIOR, not a
    wire incompatibility -- recorded separately, never conflated with
    `tool_schema_accepted`."""
    conclude_args_parse_ok: bool | None = None
    """Soft signal only (not a pass/fail gate) -- whether the emitted
    tool call's own arguments happen to validate against the real
    `ConcludeAction` pydantic model. A model choosing different
    (still-valid-shape) field values is normal preflight-prompt behavior,
    not a compatibility problem."""
    reasoning_field_rejected: bool | None = None
    """True only if the provider explicitly rejected the `reasoning.effort`
    request field. None if untested (e.g. connectivity failed first)."""
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """The three hard gates Phase 4 requires before any paid run:
        reachable, real tool schema accepted, reasoning field not
        rejected outright. `tool_call_emitted`/`conclude_args_parse_ok`
        are diagnostic, not gating -- a model that answers the preflight
        prompt in prose instead of calling the tool is still wire-
        compatible; that is exactly the kind of REAL model-behavior
        signal the harness should surface, not paper over by gating on
        it."""
        return bool(
            self.api_reachable and self.model_responded
            and self.tool_schema_accepted and not self.reasoning_field_rejected
        )


def _worktree_tool_schemas() -> list[dict]:
    """Fallback only -- see module docstring's Schema source note. NOT
    used by run_model_eval.py's real gated path."""
    from rtf.security_agent.response_schema import build_action_tool_schemas
    from rtf.security_agent.tools import build_tool_schemas
    from rtf.security_agent.kernel import NATIVE_RESPONSE_MODELS
    return build_tool_schemas() + build_action_tool_schemas(NATIVE_RESPONSE_MODELS)


def run_preflight(config: ModelConfig, api_key: str, base_url: str = "https://openrouter.ai/api/v1",
                   timeout: float = 60.0, tool_schemas: list[dict] | None = None) -> PreflightResult:
    result = PreflightResult(model_key=config.key, openrouter_model_id=config.openrouter_model_id)
    with tempfile.TemporaryDirectory(prefix="preflight_cache_") as cache_dir:
        # Call 1: bare connectivity + reasoning-field acceptance. No
        # tools, smallest possible completion budget.
        client = ResponsesChatClient(
            base_url=base_url, api_key=api_key, model=config.openrouter_model_id,
            cache_dir=Path(cache_dir), timeout=timeout, reasoning_effort=config.reasoning_effort,
        )
        try:
            ping = client.complete(
                [{"role": "user", "content": "Reply with exactly the single word: OK"}],
                temperature=0.0, max_tokens=64,
            )
            result.api_reachable = True
            result.reasoning_field_rejected = False
            result.model_responded = bool(ping.content)
            result.ping_content = ping.content
        except LLMError as e:
            result.errors.append(f"connectivity/reasoning-field call failed: {e}")
            if any(marker in str(e).lower() for marker in _REASONING_FIELD_ERROR_MARKERS):
                result.reasoning_field_rejected = True
            return result  # nothing further is testable without connectivity

        # Call 2: the REAL tool schema list (13 read tools + 2 native
        # action tools), exactly as run_security_agent_bundle sends it --
        # this is the call that would have caught the Sol `required`-
        # fields incompatibility before any real investigation spend.
        schemas = tool_schemas if tool_schemas is not None else _worktree_tool_schemas()
        tool_client = ResponsesChatClient(
            base_url=base_url, api_key=api_key, model=config.openrouter_model_id,
            cache_dir=Path(cache_dir), timeout=timeout, reasoning_effort=config.reasoning_effort,
            tools=schemas, tool_choice="auto", parallel_tool_calls=True,
        )
        try:
            turn = tool_client.complete(
                [{"role": "user", "content": _PREFLIGHT_CONCLUDE_PROMPT}],
                temperature=0.0, max_tokens=2000,
            )
            result.tool_schema_accepted = True
        except LLMError as e:
            result.errors.append(f"real tool-schema call failed: {e}")
            if any(marker in str(e) for marker in _REQUIRED_FIELD_ERROR_MARKERS):
                result.tool_schema_accepted = False
            else:
                result.tool_schema_accepted = False
                result.errors.append("rejection did not match the known required-fields "
                                      "signature -- inspect manually before assuming this is the same class of bug")
            return result

        calls = turn.tool_calls or []
        conclude_calls = [c for c in calls if c.tool == "conclude"]
        result.tool_call_emitted = bool(conclude_calls)
        if conclude_calls:
            try:
                # Best-effort only, against THIS worktree's ConcludeAction --
                # may not be byte-identical to the frozen checkout's shape
                # (see module docstring). Never gates `passed`.
                from rtf.security_agent.kernel import ConcludeAction
                ConcludeAction.model_validate({"action": "conclude", **conclude_calls[0].args})
                result.conclude_args_parse_ok = True
            except Exception as e:  # noqa: BLE001 -- diagnostic only, never re-raised
                result.conclude_args_parse_ok = False
                result.errors.append(f"conclude args did not validate against worktree ConcludeAction "
                                      f"(non-gating, may reflect a frozen-checkout schema difference "
                                      f"rather than a real problem): {e}")
    return result
