"""Phase 2 of the grouped-investigation architecture: explicit,
structured metadata for every atomic derived property.

An `InvestigationInstance` (`rtf.l10_property_derivation.derive_
investigations`) already names WHICH (requirement-clause, location) pair
one investigation covers -- this module adds the STRUCTURED metadata the
grouping engine (Phase 4) needs to decide which properties can safely
share one Codex call: what contract/function it targets, what it shares
with other properties (files, symbols, state, types, callgraph
neighborhood, inheritance), and how it was derived.

Every field's source is one of: the EthTrust corpus record itself
(`requirement_id`/`requirement_level`/`requirement_semantic_intent`/
`source_provenance`), RTF's own requirement interpretation
(`property_text`, from `InvestigationInstance.focused_clause` or the
full normative text), or repository/code static evidence (everything
else -- parsed from the predicate's own evidence, or, when a compiled
Slither object / ProgramGraph is available, real state/inheritance/
callgraph facts). **Never EVMbench.** `reasoning_category` (Phase 3's
taxonomy) and `estimated_complexity` (Phase 6's scorer) are left `None`
here by design -- those phases don't exist yet, and a placeholder value
would misrepresent a real classification.
"""
from __future__ import annotations

from dataclasses import dataclass

from rtf.l10_property_derivation.derive_investigations import InvestigationInstance
from rtf.l12_evaluation.metrics import EvidenceItem


def parse_contract_function(candidate_location: str) -> tuple[str | None, str | None]:
    """Splits RTF's bare "Contract.function" location string (see
    `rtf.l8_llm_judgment_layer.graph_navigation`'s own docstring for this
    format) into (contract, function). "Contract" alone (no dot) ->
    (contract, None) -- a real, common shape for contract-level (not
    function-level) evidence, e.g. `req-2-compiler-060`'s location is
    just the contract name. Empty/falsy input -> (None, None).
    """
    if not candidate_location:
        return None, None
    if "." not in candidate_location:
        return candidate_location, None
    contract, _, function = candidate_location.partition(".")
    return contract or None, function or None


@dataclass(frozen=True)
class PropertyMetadata:
    property_id: str
    requirement_id: str
    requirement_level: str | None
    requirement_semantic_intent: str | None
    """The requirement's own spec title (e.g. "Process All Inputs") --
    directly spec-derived, not invented; EthTrust names each requirement
    with a short intent-bearing title already."""
    property_text: str
    """The specific obligation THIS property checks -- the derived
    clause text if the parent requirement was multi-clause, else the
    full normative text (mirrors `InvestigationInstance.focused_clause`
    semantics exactly)."""
    target_contract: str | None
    target_function: str | None
    candidate_locations: tuple[str, ...]
    """Every distinct location the PARENT requirement's evidence pool
    named (not just this one property's own single location) -- real
    signal for the grouping engine: two properties whose parent
    requirements share candidate locations plausibly share investigation
    context, even if each property's own instance targets a different
    one."""
    relevant_files: tuple[str, ...] = ()
    relevant_symbols: tuple[str, ...] = ()
    relevant_state_variables: tuple[str, ...] = ()
    relevant_types: tuple[str, ...] = ()
    relevant_constants: tuple[str, ...] = ()
    callgraph_neighbors: tuple[str, ...] = ()
    """Node ids one CALLER/CALLEE hop from the target function, when a
    live `ProgramGraph` was available at derivation time -- empty (not
    fabricated) otherwise."""
    inheritance_context: tuple[str, ...] = ()
    """Immediate parent contracts, when a live Slither object was
    available -- empty otherwise."""
    reasoning_category: str | None = None
    """Phase 3's semantic grouping taxonomy tag -- always None from this
    module; assigned by a later, separate categorization pass once that
    taxonomy exists, not invented here."""
    estimated_complexity: float | None = None
    """Phase 6's investigation-complexity score -- always None from this
    module, for the same reason."""
    source_provenance: str = ""


def _structured_symbols_and_types(evidence: EvidenceItem | None) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Pulls symbol/type names out of a predicate's own `structured`
    evidence dict, when present (see e.g.
    `predicates.find_unsafe_narrowing_cast`'s `{"input": {"name": ...,
    "type": ...}}` shape) -- the ONLY structured evidence shape
    consistently used across predicates today. Returns ([], []) for any
    evidence item without a recognizable `input` sub-dict, rather than
    guessing at other shapes.
    """
    if evidence is None or not evidence.structured:
        return (), ()
    inp = evidence.structured.get("input")
    if not isinstance(inp, dict):
        return (), ()
    symbols = (inp["name"],) if inp.get("name") else ()
    types = (inp["type"],) if inp.get("type") else ()
    return symbols, types


def _graph_enrichment(candidate_location: str, pg) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Best-effort: resolves `candidate_location` on the given
    ProgramGraph and returns (callgraph_neighbors, relevant_state_variables).
    Never raises -- an unresolvable location (ambiguous overload, non-
    function-shaped candidate, or no graph at all) simply yields empty
    tuples, exactly matching every other graph-hint consumer in this
    codebase's own "best-effort HINT, never a precondition" convention.
    """
    if pg is None or not candidate_location:
        return (), ()
    try:
        from a4v.graph import CALLS, EXTERNAL_CALL, STATE_READ, STATE_WRITE
        from rtf.l8_llm_judgment_layer.graph_navigation import resolve_seed_node

        node = resolve_seed_node(pg, candidate_location)
        callers = pg.neighbors_by_kind(node, CALLS, direction="in")
        callees = pg.neighbors_by_kind(node, CALLS, direction="out")
        externals = pg.neighbors_by_kind(node, EXTERNAL_CALL, direction="out")
        neighbors = tuple(dict.fromkeys([*callers, *callees, *externals]))  # dedupe, preserve order

        reads = pg.neighbors_by_kind(node, STATE_READ, direction="out")
        writes = pg.neighbors_by_kind(node, STATE_WRITE, direction="out")
        state_vars = tuple(dict.fromkeys([*reads, *writes]))
        return neighbors, state_vars
    except Exception:  # noqa: BLE001 -- graph enrichment is best-effort, never blocks metadata derivation
        return (), ()


def _slither_enrichment(target_contract: str | None, slither) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Best-effort: given a compiled Slither object and a target contract
    name, returns (relevant_files, inheritance_context, relevant_constants).
    Never raises.
    """
    if slither is None or not target_contract:
        return (), (), ()
    try:
        matches = [c for c in slither.contracts if c.name == target_contract]
        if not matches:
            return (), (), ()
        contract = matches[0]
        files = ()
        source_mapping = getattr(contract, "source_mapping", None)
        if source_mapping is not None and getattr(source_mapping, "filename", None) is not None:
            rel = getattr(source_mapping.filename, "relative", None) or getattr(source_mapping.filename, "used", None)
            if rel:
                files = (rel,)
        inheritance = tuple(c.name for c in getattr(contract, "inheritance", []) or [])
        constants = tuple(v.name for v in getattr(contract, "state_variables", []) or []
                           if getattr(v, "is_constant", False) or getattr(v, "is_immutable", False))
        return files, inheritance, constants
    except Exception:  # noqa: BLE001 -- best-effort, never blocks metadata derivation
        return (), (), ()


def derive_property_metadata(
    instance: InvestigationInstance,
    requirement_record: dict,
    parent_candidate_locations: list[str],
    evidence: EvidenceItem | None = None,
    pg=None,
    slither=None,
) -> PropertyMetadata:
    """Builds the full structured metadata for one derived property
    (one `InvestigationInstance`).

    `requirement_record` is the requirement's own corpus record (a dict
    from `rtf/l1_corpus/requirement_corpus.json`, or a generated-
    requirement's equivalent shape -- both already carry `req_id`/
    `level`/`title`/`normative_text`/`section`). `parent_candidate_locations`
    is the full ranked-evidence location list for the PARENT requirement
    (not just this instance's own one location) -- see
    `candidate_locations`'s own docstring for why. `evidence`, `pg`,
    `slither` are all optional, best-effort enrichment sources; every
    field they'd populate degrades to an empty tuple, never a crash or a
    guess, when omitted or when resolution fails.
    """
    target_contract, target_function = parse_contract_function(instance.candidate_location)
    symbols, types_from_evidence = _structured_symbols_and_types(evidence)
    neighbors, state_vars = _graph_enrichment(instance.candidate_location, pg)
    files, inheritance, constants = _slither_enrichment(target_contract, slither)

    section = requirement_record.get("section") or {}
    secno = section.get("secno")
    provenance_parts = [f"req_id={instance.req_id}"]
    if secno:
        provenance_parts.append(f"spec_section={secno}")
    if instance.focused_clause is not None:
        provenance_parts.append(f"clause_index={instance.clause_index}")
    provenance = "; ".join(provenance_parts)

    return PropertyMetadata(
        property_id=instance.instance_id,
        requirement_id=instance.req_id,
        requirement_level=requirement_record.get("level"),
        requirement_semantic_intent=requirement_record.get("title"),
        property_text=instance.focused_clause or requirement_record.get("normative_text", ""),
        target_contract=target_contract,
        target_function=target_function,
        candidate_locations=tuple(dict.fromkeys(loc for loc in parent_candidate_locations if loc)),
        relevant_files=files,
        relevant_symbols=symbols,
        relevant_state_variables=state_vars,
        relevant_types=types_from_evidence,
        relevant_constants=constants,
        callgraph_neighbors=neighbors,
        inheritance_context=inheritance,
        reasoning_category=None,
        estimated_complexity=None,
        source_provenance=provenance,
    )
