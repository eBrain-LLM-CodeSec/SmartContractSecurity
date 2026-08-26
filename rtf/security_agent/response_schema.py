"""Builds an OpenAI/OpenRouter Responses-API strict JSON schema for the
kernel's action union (`rtf.security_agent.kernel.RESPONSE_MODELS`), so
the provider constrains output at generation time instead of the kernel
only discovering a malformed shape after the fact.

Real, live-verified finding (2026-08-25 canto run): this project's own
earlier history recording "GLM-5.2 ignores structured output" was
specific to Codex CLI's own `--output-schema` mechanism, not the raw
Responses API `text.format: {type: "json_schema"}` parameter this
kernel's own `ResponsesChatClient` actually calls -- a direct test
against that parameter with `z-ai/glm-5.2` returned a clean, schema-
conformant JSON object with no markdown fencing at all, confirming the
model DOES honor it when asked the way this client actually asks.
"""
from __future__ import annotations

from typing import Union, get_args

from pydantic import BaseModel, TypeAdapter

# Value-level constraints (length/pattern/format) the Responses API's
# strict structured-output mode does not reliably support across
# providers -- stripped from the PROVIDER-facing schema only. Pydantic's
# own post-hoc validation (kernel.py's `model_client.decide()` still
# calls `model.model_validate(...)` on every parsed response regardless)
# continues to enforce these; the provider schema only needs to get the
# STRUCTURAL SHAPE right -- field names, types, and the discriminating
# `action` literal -- which is the actual class of error observed live
# (e.g. the model naming a tool directly as the top-level "action").
_UNSUPPORTED_KEYWORDS = ("minLength", "maxLength", "minItems", "maxItems", "pattern", "format")


def _strip_unsupported_keywords(node: object) -> None:
    if isinstance(node, dict):
        for key in _UNSUPPORTED_KEYWORDS:
            node.pop(key, None)
        for value in node.values():
            _strip_unsupported_keywords(value)
    elif isinstance(node, list):
        for item in node:
            _strip_unsupported_keywords(item)


def _enforce_strict_object_rules(node: object) -> None:
    """The two structural rules strict mode actually requires: every
    object schema sets `additionalProperties: false`, and every one of
    its properties is listed in `required`. A field that already allows
    None in its Pydantic type (e.g. `str | None = None`) is already
    representable as null in its generated schema; a field with a non-
    None default (e.g. `args: dict = Field(default_factory=dict)`)
    simply becomes a property the model must always supply a concrete
    value for, never omit -- not a change to what values are valid,
    only to whether the key itself may be absent."""
    if isinstance(node, dict):
        if node.get("type") == "object" and "properties" in node:
            node["additionalProperties"] = False
            node["required"] = list(node["properties"].keys())
        for value in node.values():
            _enforce_strict_object_rules(value)
    elif isinstance(node, list):
        for item in node:
            _enforce_strict_object_rules(item)


def build_strict_schema(models: tuple[type[BaseModel], ...], name: str) -> dict:
    """One `text.format` payload (Responses API shape) accepting any of
    `models`, discriminated by each model's own `action` Literal field."""
    adapter = TypeAdapter(Union[tuple(models)])
    schema = adapter.json_schema()
    _strip_unsupported_keywords(schema)
    _enforce_strict_object_rules(schema)
    return {
        "type": "json_schema",
        "name": name,
        "strict": True,
        "schema": schema,
    }


def build_action_tool_schemas(models: tuple[type[BaseModel], ...]) -> list[dict]:
    """One native `tools=[...]` entry (same OpenAI/OpenRouter Responses-API
    function-calling shape `tools.build_tool_schemas()` already produces
    for the 13 read-only investigation tools) per action model in
    `models` -- promotes `update_investigation`/`conclude` from free-text
    fenced-JSON conventions to real native tools the model can reach for
    with the same affordance as every other tool (root cause #1,
    RTF_SECURITY_AGENT_NATURAL_CONCLUSION_INVESTIGATION_20260826.md: the
    model almost never called `update_investigation` when it was a
    text-mode-switch away from the tool-calling machinery it was already
    using for everything else).

    The tool `name` is derived from each model's own `action:
    Literal[...]` field -- never a hand-maintained parallel string, same
    discipline as `build_tool_schemas`. `description` is the first line
    of the model's own docstring: the natural place to state a hard
    mechanical requirement (e.g. conclude's PASS-completion-gate rule),
    since it sits right next to the tool the model actually calls,
    rather than buried once in a large system prompt it may not
    re-attend to every turn.

    Reuses `_strip_unsupported_keywords`/`_enforce_strict_object_rules`
    unchanged -- they already recurse into nested dicts/lists, exactly
    what `ConcludeAction`'s nested EvidenceInput/HypothesisInput/
    PropertyVerdictInput/CounterexampleAttemptInput lists need. Cross-
    field validators (`evidence_references_are_complete`,
    `contains_an_update`) are not representable in JSON schema and don't
    need to be -- they still run post-hoc via `model.model_validate(...)`
    in the kernel dispatch, the same "structural shape at generation
    time, full validation post-hoc" split this module already uses for
    the legacy text-mode schema above."""
    schemas = []
    for model in models:
        action_value = get_args(model.model_fields["action"].annotation)[0]
        schema = model.model_json_schema()
        schema.pop("title", None)
        schema["properties"].pop("action", None)
        # `_enforce_strict_object_rules` recomputes `required` from
        # `properties` below -- popping "action" first means it will not
        # be re-added.
        _strip_unsupported_keywords(schema)
        _enforce_strict_object_rules(schema)
        doc = (model.__doc__ or "").strip().splitlines()[0] if model.__doc__ else ""
        schemas.append({
            "type": "function",
            "name": action_value,
            "description": doc,
            "parameters": schema,
            "strict": True,
        })
    return schemas
