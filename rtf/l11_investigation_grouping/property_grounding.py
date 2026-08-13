"""RTF v2 Phase 6/7: deterministic grounding/validation of semantic
properties, and consolidation of near-duplicate ones.

No LLM here, deliberately (see task brief Section 9: grounding is a
SEPARATE step from proposal, and must not itself be another opportunity
for hallucination). Every `RawSemanticProperty`
(`semantic_property_generation.py`) is checked against real facts --
does every named contract/function/state variable actually exist in the
compiled project's `ProjectManifest`? does the statement concretely name
at least one of them (or a real cited source_ref), rather than reading as
generic boilerplate? A property that fails is REJECTED with a recorded
reason (`RejectedProperty`), never silently dropped and never kept
"downgraded" -- Section 9's own instruction is to reject or downgrade;
this module rejects outright, since a property missing its concrete
target has nothing left to investigate.

An accepted property becomes a full `PropertyMetadata`
(`source_kind="code_semantics"`, `generation_method="semantic_derivation"`)
-- the SAME object type structural/requirement-derived properties use, so
it flows through the unchanged grouping engine / cluster-plan generator /
live_runner with zero special-casing downstream. This is the concrete
mechanism behind Section 10's "predicates become one high-confidence
source of candidate properties alongside semantic generation" -- both
kinds are `PropertyMetadata`, merged into one pool before scope filtering
(`merge_property_pools`).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace

from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata, _slither_enrichment
from rtf.l11_investigation_grouping.semantic_property_generation import ProjectManifest, RawSemanticProperty
from rtf.l11_investigation_grouping.semantic_taxonomy import map_property_type_to_reasoning_category

# Defense-in-depth against the task brief's own literal banned examples and
# close variants -- checked in ADDITION to (not instead of) the real
# concrete-reference requirement below, since a statement could technically
# name a real contract while still being substantively this generic
# ("Vault should not lose money.").
_BANNED_GENERIC_PATTERNS = (
    re.compile(r"should\s+not\s+lose\s+money", re.IGNORECASE),
    re.compile(r"code\s+should\s+be\s+secure", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+secure\b", re.IGNORECASE),
    re.compile(r"accounting\s+should\s+be\s+correct", re.IGNORECASE),
    re.compile(r"\bshould\s+work\s+correctly\b", re.IGNORECASE),
    re.compile(r"\bmust\s+be\s+secure\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class RejectedProperty:
    raw: RawSemanticProperty
    reason: str


def _requirement_id_for(raw: RawSemanticProperty) -> str:
    digest = hashlib.sha256(raw.statement.encode("utf-8")).hexdigest()[:12]
    return f"semantic__{raw.property_type}__{digest}"


def _unknown_references(names: tuple[str, ...], known: tuple[str, ...]) -> list[str]:
    known_set = set(known)
    return [n for n in names if n not in known_set]


def _statement_names_a_concrete_reference(statement: str, concrete_names: list[str]) -> bool:
    lowered = statement.lower()
    for name in concrete_names:
        # For "Contract.function"/"Contract.variable" refs, a mention of
        # either the qualified form OR the bare trailing component (a
        # function/variable name alone, e.g. "totalAssets") counts --
        # natural statement prose says "totalAssets()" far more often than
        # "Vault.totalAssets".
        bare = name.rsplit(".", 1)[-1]
        if name.lower() in lowered or (bare and bare.lower() in lowered):
            return True
    return False


def ground_semantic_property(
    raw: RawSemanticProperty, manifest: ProjectManifest, slither=None,
) -> PropertyMetadata | RejectedProperty:
    """Deterministic grounding for one raw semantic property. See module
    docstring for the full rule set; every rejection reason is a distinct,
    greppable string (never a bare "rejected")."""
    bad_contracts = _unknown_references(raw.affected_contracts, manifest.contracts)
    bad_functions = _unknown_references(raw.affected_functions, manifest.functions)
    bad_state_vars = _unknown_references(raw.affected_state_variables, manifest.state_variables)
    if bad_contracts or bad_functions or bad_state_vars:
        return RejectedProperty(
            raw=raw,
            reason=(
                "ungrounded_reference:"
                f"contracts={bad_contracts},functions={bad_functions},state_variables={bad_state_vars}"
            ),
        )

    concrete_names = list(raw.affected_contracts) + list(raw.affected_functions) + list(raw.affected_state_variables)
    if not concrete_names:
        return RejectedProperty(raw=raw, reason="no_concrete_target_named")

    for pattern in _BANNED_GENERIC_PATTERNS:
        if pattern.search(raw.statement):
            return RejectedProperty(raw=raw, reason=f"generic_banned_statement:{pattern.pattern}")

    if not _statement_names_a_concrete_reference(raw.statement, concrete_names):
        return RejectedProperty(raw=raw, reason="statement_not_concretely_grounded")

    if not raw.rationale.strip() and not raw.source_refs:
        return RejectedProperty(raw=raw, reason="insufficient_grounding_evidence")

    requirement_id = _requirement_id_for(raw)

    if raw.affected_functions:
        target_contract, target_function = raw.affected_functions[0].split(".", 1)
        location = raw.affected_functions[0]
    elif raw.affected_contracts:
        target_contract, target_function = raw.affected_contracts[0], None
        location = raw.affected_contracts[0]
    else:  # unreachable given the no_concrete_target_named check above, kept for type-safety
        target_contract, target_function, location = None, None, ""

    files, inheritance, constants = _slither_enrichment(target_contract, slither)

    relevant_state_variables = tuple(dict.fromkeys(
        v.split(".", 1)[-1] for v in raw.affected_state_variables
    ))

    grounding_evidence = tuple(dict.fromkeys([
        *raw.source_refs,
        *(f"affected_function:{f}" for f in raw.affected_functions),
        *(f"affected_state_variable:{v}" for v in raw.affected_state_variables),
        *(f"affected_contract:{c}" for c in raw.affected_contracts if not raw.affected_functions),
    ]))

    return PropertyMetadata(
        property_id=f"{requirement_id}::loc0",
        requirement_id=requirement_id,
        requirement_level="SEMANTIC",
        requirement_semantic_intent=raw.property_type,
        property_text=raw.statement,
        target_contract=target_contract,
        target_function=target_function,
        location=location,
        candidate_locations=tuple(raw.affected_functions or raw.affected_contracts),
        relevant_files=files,
        relevant_symbols=(),
        relevant_state_variables=relevant_state_variables,
        relevant_types=(),
        relevant_constants=constants,
        callgraph_neighbors=(),
        inheritance_context=inheritance,
        reasoning_category=map_property_type_to_reasoning_category(raw.property_type, raw.statement),
        estimated_complexity=None,
        source_provenance=f"semantic_derivation; property_type={raw.property_type}; source_refs={list(raw.source_refs)}",
        requirement_explanatory_text=raw.rationale,
        related_out_of_scope_context=(),
        source_kind="code_semantics",
        generation_method="semantic_derivation",
        confidence=raw.confidence,
        rationale=raw.rationale,
        grounding_evidence=grounding_evidence,
    )


def ground_semantic_properties(
    raws: list[RawSemanticProperty], manifest: ProjectManifest, slither=None,
) -> tuple[list[PropertyMetadata], list[RejectedProperty]]:
    accepted: list[PropertyMetadata] = []
    rejected: list[RejectedProperty] = []
    for raw in raws:
        result = ground_semantic_property(raw, manifest, slither=slither)
        if isinstance(result, PropertyMetadata):
            accepted.append(result)
        else:
            rejected.append(result)
    return accepted, rejected


def rejected_property_to_dict(rejection: RejectedProperty) -> dict:
    from rtf.l11_investigation_grouping.semantic_property_generation import raw_property_to_dict
    return {"raw": raw_property_to_dict(rejection.raw), "reason": rejection.reason}


# --- Phase 7: merge structural + semantic pools, consolidate duplicates --

def _word_set(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


_DEDUP_JACCARD_THRESHOLD = 0.3
"""Calibrated against realistic paraphrases of the same underlying
concern (the task brief's own P1/P2/P3 "totalAssets vs. fee accounting"
example): three genuinely-independent rephrasings of one accounting
relationship typically land around 0.33-0.45 word-Jaccard, not >=0.5 --
natural language reuses connective/domain words ("must", "Vault",
"totalAssets") but varies its own phrasing structure heavily. This
threshold is a THIRD, additional gate on top of two already-strict
requirements (same `reasoning_category` AND at least one shared affected
state variable) -- not the sole discriminator -- so 0.3 stays safe from
over-merging unrelated properties that only coincidentally share a few
common words."""


def deduplicate_semantic_properties(properties: list[PropertyMetadata]) -> list[PropertyMetadata]:
    """Consolidates near-duplicate GROUNDED semantic properties (only
    `source_kind="code_semantics"` -- structural/requirement-derived
    properties are left untouched, they're already 1:1 with a distinct
    requirement clause and never need this) into one canonical property
    per group, rather than one Codex sub-call worth of redundant
    near-identical text per cluster. Two properties are merged when they
    share `reasoning_category` AND at least one affected state variable
    AND their statement text's word-Jaccard similarity is >=
    `_DEDUP_JACCARD_THRESHOLD` -- the concrete P1/P2/P3 "totalAssets vs.
    fee accounting" example from the task brief satisfies all three.

    The FIRST property in each group (by property_id, for determinism) is
    kept as canonical; the others' statements are folded into its
    `requirement_explanatory_text` (prefixed, clearly attributed) so the
    distinct phrasings aren't lost, and their `grounding_evidence`/
    `source_refs`-derived entries are unioned in. This does NOT touch
    non-semantic properties, and never merges across different
    `reasoning_category` values (an unsafe/meaningless merge)."""
    semantic = [p for p in properties if p.source_kind == "code_semantics"]
    other = [p for p in properties if p.source_kind != "code_semantics"]
    if not semantic:
        return properties

    semantic_sorted = sorted(semantic, key=lambda p: p.property_id)
    used: set[str] = set()
    result: list[PropertyMetadata] = []

    for p in semantic_sorted:
        if p.property_id in used:
            continue
        group = [p]
        used.add(p.property_id)
        p_words = _word_set(p.property_text)
        p_state_vars = set(p.relevant_state_variables)
        for q in semantic_sorted:
            if q.property_id in used:
                continue
            if q.reasoning_category != p.reasoning_category or q.reasoning_category is None:
                continue
            if not (p_state_vars & set(q.relevant_state_variables)):
                continue
            if _jaccard(p_words, _word_set(q.property_text)) < _DEDUP_JACCARD_THRESHOLD:
                continue
            group.append(q)
            used.add(q.property_id)

        if len(group) == 1:
            result.append(p)
            continue

        others_text = "\n".join(
            f"[Consolidated duplicate {g.property_id}]: {g.property_text}" for g in group[1:]
        )
        merged_explanatory = p.requirement_explanatory_text
        merged_explanatory = (merged_explanatory + "\n" + others_text) if merged_explanatory else others_text
        merged_grounding = tuple(dict.fromkeys(
            [*p.grounding_evidence, *(e for g in group[1:] for e in g.grounding_evidence)]
        ))
        result.append(replace(
            p, requirement_explanatory_text=merged_explanatory, grounding_evidence=merged_grounding,
        ))

    return other + result


def merge_property_pools(
    structural_properties: list[PropertyMetadata], semantic_properties: list[PropertyMetadata],
) -> list[PropertyMetadata]:
    """Combines the existing structural/requirement-derived property pool
    with the newly-grounded semantic pool into ONE pool -- structurally
    identical objects, so every downstream stage (scope filtering,
    grouping, cluster planning, live_runner) needs zero special-casing to
    handle "semantic" properties. Consolidates near-duplicate semantic
    properties first (Phase 7) so the merged pool doesn't carry redundant
    near-identical entries into clustering."""
    return structural_properties + deduplicate_semantic_properties(semantic_properties)
