"""RTF v2 Phase 5: semantic property generation.

The one genuinely new stage this redesign adds -- see RTF_V2_ARCHITECTURE.md
section A.5/C. Every property in RTF today traces to a pre-existing
`requirement_id` (the static 81-item EthTrust corpus, or an `rtf.standards`
generated ERC/EIP clause) AND requires a structural predicate to have
already produced evidence for it. This module proposes candidate
properties that are NOT anchored to any pre-existing requirement_id --
derived instead from the protocol's own documented/structural semantics
(the enriched `protocol_context.md`, applicable-standard obligations, and
a concrete contract/function/state-variable manifest).

**Critical discipline (task brief Section 15, non-negotiable)**: this
module asks ONLY "what must remain true" -- never "does the code violate
this" / "find vulnerabilities". No verdict-shaped field (PASS/FAIL/
vulnerable/exploit/...) is ever accepted from the LLM; any entry carrying
one is rejected outright as a discipline violation, not silently stripped
and kept. Grounding (rejecting ungrounded/generic properties) is a
SEPARATE, deterministic, non-LLM stage -- `property_grounding.py` -- by
design: this module's only job is proposal, not validation.

Reuses `a4v.llm.ChatClient` directly for caching (hash-keyed on the exact
messages/temperature/model, same mechanism the L8 judgment layer already
relies on) -- no parallel cache. `chat_client` is duck-typed to anything
exposing `.complete_json(messages, temperature=...) -> (dict, ChatResult)`,
so tests inject a fake with zero real network/API-key dependency (same
"mock-tested only, no live calls yet" convention `live_runner.py` already
established for `run_arm_g_bundle_fn`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from rtf.l11_investigation_grouping.semantic_taxonomy import PROPERTY_TYPE_VOCABULARY

# Any of these keys anywhere in a proposed property entry is a hard signal
# the model tried to render a verdict/finding instead of a property --
# reject the entry outright (never coerce/strip and keep it), per the
# module's own stated discipline.
_VERDICT_SHAPED_KEYS = frozenset({
    "verdict", "vulnerable", "vulnerability", "finding", "pass", "fail",
    "passed", "failed", "exploit", "severity", "is_vulnerable", "confirmed",
})

_REQUIRED_KEYS = frozenset({"statement", "property_type", "rationale"})

_SYSTEM_PROMPT = """You are a security-property analyst for a smart-contract audit framework (RTF).

Your ONLY task: given facts about a protocol (its documented purpose, the external \
standards it implements, its contracts/functions/state variables), propose SECURITY \
PROPERTIES that must remain true for the protocol to behave correctly.

You are NOT auditing this code. You must NEVER:
- state whether the implementation satisfies or violates a property
- use words like "vulnerable", "PASS", "FAIL", "exploit", "bug", "violates", "confirmed"
- report a finding, a severity, or a verdict of any kind

A separate system will investigate each property you propose. Your job ends at proposing \
WHAT MUST HOLD, not whether it currently does.

Every property must be FALSIFIABLE and CONCRETE -- it must name at least one real \
contract, function, or state variable from the facts you were given, and/or cite a real \
standard clause you were given. Do NOT propose generic statements such as:
- "The protocol should not lose money."
- "The code should be secure."
- "Accounting should be correct."
These are not properties; they name no concrete target and cannot be investigated.

Each property must declare a property_type from EXACTLY this list: """ + ", ".join(sorted(PROPERTY_TYPE_VOCABULARY)) + """

Respond with ONLY a JSON object, no prose, in a fenced code block:
```json
{"properties": [
  {
    "statement": "...",
    "property_type": "one of the allowed types above",
    "rationale": "why this must hold, grounded in the facts you were given",
    "affected_contracts": ["ContractName", ...],
    "affected_functions": ["ContractName.functionName", ...],
    "affected_state_variables": ["ContractName.varName", ...],
    "source_refs": ["a standard clause id, doc citation, or other concrete reference you were given"],
    "confidence": 0.0
  }
]}
```
Propose at most {max_properties} properties. Every affected_contracts/affected_functions/\
affected_state_variables entry MUST be copied verbatim from the facts you were given -- \
never invent a name that wasn't in the manifest."""


@dataclass(frozen=True)
class ProjectManifest:
    """The concrete, real names the generator is allowed to reference --
    grounding (`property_grounding.py`) later checks every proposed
    affected_contracts/affected_functions/affected_state_variables entry
    against this exact manifest, so an LLM that ignores the prompt's
    "copy verbatim" instruction is still caught deterministically, not
    just discouraged."""
    contracts: tuple[str, ...]
    functions: tuple[str, ...]
    """"Contract.function" strings."""
    state_variables: tuple[str, ...]
    """"Contract.variable" strings."""

    @classmethod
    def from_slither(cls, slither) -> "ProjectManifest":
        """Known limitation (found live against a real EVMbench target,
        `2025-01-liquid-ron`, not just reasoned about): uses `functions_
        declared`/`state_variables_declared`, which are a contract's OWN
        directly-declared members only -- an inherited-but-never-
        overridden function (e.g. a vault that never overrides OZ
        ERC4626's own `convertToShares`) is invisible here under the
        derived contract's name. Confirmed this does NOT cause incorrect
        grounding in practice (the generator/grounder still succeed via a
        different, real concrete reference the property also names -- see
        RTF_V2_LIVE_VALIDATION_REAL_TARGET_PARTIAL.md), but it does mean
        the generator cannot itself PROPOSE a property naming only an
        inherited-only method. A future fix would use `functions`/
        `state_variables` (the full, inherited-inclusive sets) instead --
        deliberately not changed here without live-run evidence it's
        actually needed, per this module's own anti-speculative-change
        discipline.
        """
        contracts: list[str] = []
        functions: list[str] = []
        state_vars: list[str] = []
        for c in getattr(slither, "contracts_derived", []):
            if getattr(c, "is_interface", False):
                continue
            contracts.append(c.name)
            for f in getattr(c, "functions_declared", []):
                if not f.is_constructor:
                    functions.append(f"{c.name}.{f.name}")
            for v in getattr(c, "state_variables_declared", []):
                state_vars.append(f"{c.name}.{v.name}")
        return cls(contracts=tuple(sorted(set(contracts))), functions=tuple(sorted(set(functions))),
                    state_variables=tuple(sorted(set(state_vars))))


@dataclass(frozen=True)
class RawSemanticProperty:
    statement: str
    property_type: str
    rationale: str
    affected_contracts: tuple[str, ...]
    affected_functions: tuple[str, ...]
    affected_state_variables: tuple[str, ...]
    source_refs: tuple[str, ...]
    confidence: float


@dataclass(frozen=True)
class GenerationRejection:
    """A raw LLM-proposed entry that failed BASIC SHAPE validation (missing
    required keys, verdict-shaped keys present, wrong types) -- distinct
    from `property_grounding.RejectedProperty`, which rejects
    shape-valid-but-ungrounded properties. Both are recorded, never
    silently dropped (Section 19's observability requirement)."""
    raw_entry: dict
    reason: str


def build_prompt_messages(protocol_context_md: str, manifest: ProjectManifest, max_properties: int = 12) -> list[dict]:
    system = _SYSTEM_PROMPT.replace("{max_properties}", str(max_properties))
    user = (
        "## Protocol context\n\n" + protocol_context_md + "\n\n"
        "## Manifest of real names you may reference\n\n"
        f"Contracts: {', '.join(manifest.contracts) or '(none)'}\n\n"
        f"Functions: {', '.join(manifest.functions) or '(none)'}\n\n"
        f"State variables: {', '.join(manifest.state_variables) or '(none)'}\n"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _validate_entry(entry: object) -> RawSemanticProperty | GenerationRejection:
    if not isinstance(entry, dict):
        return GenerationRejection(raw_entry={"_raw": repr(entry)}, reason="entry_not_an_object")

    verdict_keys = _VERDICT_SHAPED_KEYS & set(entry.keys())
    if verdict_keys:
        return GenerationRejection(
            raw_entry=entry, reason=f"verdict_shaped_response_rejected:{sorted(verdict_keys)}",
        )

    missing = _REQUIRED_KEYS - set(entry.keys())
    if missing:
        return GenerationRejection(raw_entry=entry, reason=f"missing_required_keys:{sorted(missing)}")

    statement = entry.get("statement")
    property_type = entry.get("property_type")
    rationale = entry.get("rationale")
    if not isinstance(statement, str) or not statement.strip():
        return GenerationRejection(raw_entry=entry, reason="statement_not_a_nonempty_string")
    if not isinstance(property_type, str) or property_type not in PROPERTY_TYPE_VOCABULARY:
        return GenerationRejection(raw_entry=entry, reason=f"invalid_property_type:{property_type!r}")
    if not isinstance(rationale, str):
        return GenerationRejection(raw_entry=entry, reason="rationale_not_a_string")

    def _str_tuple(key: str) -> tuple[str, ...] | None:
        val = entry.get(key, [])
        if not isinstance(val, list) or not all(isinstance(x, str) for x in val):
            return None
        return tuple(val)

    affected_contracts = _str_tuple("affected_contracts")
    affected_functions = _str_tuple("affected_functions")
    affected_state_variables = _str_tuple("affected_state_variables")
    source_refs = _str_tuple("source_refs")
    if None in (affected_contracts, affected_functions, affected_state_variables, source_refs):
        return GenerationRejection(raw_entry=entry, reason="affected_or_source_refs_not_a_string_list")

    confidence = entry.get("confidence", 0.0)
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        return GenerationRejection(raw_entry=entry, reason="confidence_not_numeric")
    confidence = max(0.0, min(1.0, float(confidence)))

    return RawSemanticProperty(
        statement=statement.strip(), property_type=property_type, rationale=rationale.strip(),
        affected_contracts=affected_contracts, affected_functions=affected_functions,
        affected_state_variables=affected_state_variables, source_refs=source_refs, confidence=confidence,
    )


def generate_semantic_properties(
    protocol_context_md: str, manifest: ProjectManifest, chat_client, max_properties: int = 12, temperature: float = 0.0,
) -> tuple[list[RawSemanticProperty], list[GenerationRejection]]:
    """One bounded LLM call (cached via `chat_client`'s own cache) proposing
    candidate semantic properties. Returns (accepted, rejected) --
    `rejected` entries are basic-shape/discipline failures (see
    `_validate_entry`), always recorded, never silently dropped.

    Deliberately does NOT catch/report the underlying LLM call failing --
    a real API error should surface to the caller exactly like every other
    `chat_client.complete_json` use in this codebase, not be swallowed
    into an empty result that looks identical to "the model proposed
    nothing"."""
    messages = build_prompt_messages(protocol_context_md, manifest, max_properties=max_properties)
    response, _chat_result = chat_client.complete_json(messages, temperature=temperature)

    if not isinstance(response, dict) or not isinstance(response.get("properties"), list):
        return [], [GenerationRejection(raw_entry=response if isinstance(response, dict) else {"_raw": repr(response)},
                                         reason="response_missing_properties_list")]

    accepted: list[RawSemanticProperty] = []
    rejected: list[GenerationRejection] = []
    for entry in response["properties"][:max_properties]:
        result = _validate_entry(entry)
        if isinstance(result, RawSemanticProperty):
            accepted.append(result)
        else:
            rejected.append(result)
    return accepted, rejected


def raw_property_to_dict(raw: RawSemanticProperty) -> dict:
    return {
        "statement": raw.statement, "property_type": raw.property_type, "rationale": raw.rationale,
        "affected_contracts": list(raw.affected_contracts), "affected_functions": list(raw.affected_functions),
        "affected_state_variables": list(raw.affected_state_variables), "source_refs": list(raw.source_refs),
        "confidence": raw.confidence,
    }


def rejection_to_dict(rejection: GenerationRejection) -> dict:
    try:
        json.dumps(rejection.raw_entry)
        raw = rejection.raw_entry
    except TypeError:
        raw = {"_unserializable_repr": repr(rejection.raw_entry)}
    return {"raw_entry": raw, "reason": rejection.reason}
