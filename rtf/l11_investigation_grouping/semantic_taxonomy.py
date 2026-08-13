"""RTF v2: the controlled `property_type` vocabulary a semantic property
must declare (see RTF_V2_ARCHITECTURE.md / the task brief's Section 5), and
its mapping onto the EXISTING `taxonomy.ReasoningCategory` grouping key --
so a semantic property flows through the unchanged grouping engine (which
keys off `PropertyMetadata.reasoning_category`) without a second, parallel
grouping dimension.

Deliberately a small, explicit dict, not NLP -- every mapping choice is
documented below. `property_type` itself is still preserved verbatim on
the generated `PropertyMetadata` object (folded into `source_provenance`/
`grounding_evidence`, since `PropertyMetadata` doesn't carry a second
category-shaped field by design -- see property_metadata.py's own
docstring on not introducing a redundant parallel schema).
"""
from __future__ import annotations

from rtf.l11_investigation_grouping.taxonomy import ReasoningCategory, categorize_generated_clause

# The exact vocabulary the task brief's Section 5 lists for `property_type`.
# A semantic property whose declared type isn't in this set is rejected at
# grounding time (property_grounding.py) -- an LLM inventing its own
# category name is a real grounding failure mode, not a harmless variation.
PROPERTY_TYPE_VOCABULARY: frozenset[str] = frozenset({
    "structural", "semantic", "standard_conformance", "accounting",
    "authorization", "state_consistency", "numerical", "external_interaction",
    "lifecycle", "oracle", "governance", "token_semantics",
})

# Property types with a clear, direct match onto an EXISTING reasoning
# category -- reused rather than duplicated (accounting/numerical both
# concern value-correctness the same way ARITHMETIC_VALUE_CORRECTNESS's
# own EthTrust members do; governance is treated as an on-chain privilege
# question here, distinct from PROCESS_GOVERNANCE_PRACTICE's org-level
# documentation-practice sense).
_DIRECT_MAP: dict[str, ReasoningCategory] = {
    "accounting": ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS,
    "numerical": ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS,
    "authorization": ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
    "governance": ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
    "external_interaction": ReasoningCategory.EXTERNAL_CALL_INTERACTION,
    "oracle": ReasoningCategory.ORACLE_EXTERNAL_DEPENDENCY,
    "state_consistency": ReasoningCategory.STATE_CONSISTENCY,
    "lifecycle": ReasoningCategory.LIFECYCLE_INITIALIZATION,
    "token_semantics": ReasoningCategory.TOKEN_SEMANTICS_CONFORMANCE,
}


def map_property_type_to_reasoning_category(property_type: str, statement: str) -> ReasoningCategory | None:
    """Direct lookup for the 9 unambiguous types above. For the 3
    deliberately under-specified types ("structural", "semantic",
    "standard_conformance" -- the property brief itself concedes these
    don't name a single reasoning shape), falls back to the EXISTING
    best-effort keyword categorizer (`categorize_generated_clause`)
    applied to the property's own statement text -- the same mechanism
    already used for generated ERC/GP clauses, not a new heuristic.
    Returns None (an honest gap, never a guessed default) if neither
    resolves."""
    direct = _DIRECT_MAP.get(property_type)
    if direct is not None:
        return direct
    return categorize_generated_clause(statement)
