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

from dataclasses import dataclass, replace

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
    location: str = ""
    """This property's own single raw candidate_location string (before
    `parse_contract_function` splits it), preserved verbatim -- e.g.
    "README.md" or "compiler config", cases `target_contract`/
    `target_function` alone can't reconstruct losslessly. Used by
    `filter_properties_to_scope` to resolve a file path when Slither
    never compiled the target (so `relevant_files` is empty)."""
    candidate_locations: tuple[str, ...] = ()
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
    requirement_explanatory_text: str = ""
    """This property's PARENT requirement's `explanatory_text` (the
    spec's own informative prose following the normative sentence --
    see rtf/l1_corpus's "Explanatory/informative content extraction"),
    captured verbatim at derivation time regardless of whether this
    property ends up in-scope or not. Read by `forward_out_of_scope_
    context` when this property is later dropped for being out-of-
    scope but is call-graph-adjacent to a property that IS kept --
    empty string when the corpus has no explanatory text for this
    requirement."""
    related_out_of_scope_context: tuple[str, ...] = ()
    """Populated post-hoc by `forward_out_of_scope_context`, never at
    derivation time: background guidance forwarded from OTHER,
    out-of-scope properties this one is call-graph-adjacent to. Always
    empty on a freshly `derive_property_metadata`'d instance."""
    source_kind: str = "ethtrust"
    """Where this property's AUTHORITY comes from: `"ethtrust"` (static
    81-requirement corpus), `"erc_gp"` (a `rtf.standards` generated ERC/EIP
    clause requirement), or `"code_semantics"` (RTF v2's semantic property
    generator -- a property with no pre-existing requirement_id at all,
    proposed from protocol_context/interfaces/code and then grounded; see
    `rtf.l11_investigation_grouping.semantic_property_generation` and
    `property_grounding`). `derive_property_metadata` infers `"ethtrust"`
    or `"erc_gp"` automatically from `requirement_id`'s shape -- never
    `"code_semantics"`, which only `property_grounding.to_property_metadata`
    assigns."""
    generation_method: str = "structural_predicate"
    """HOW this specific property instance was mechanically produced:
    `"structural_predicate"` (a deterministic L5 predicate supplied the
    evidence/location), `"standard_clause"` (a `rtf.standards` generated
    ERC/EIP clause, translated 1:1 from spec text), or
    `"semantic_derivation"` (RTF v2's semantic generator). Distinct from
    `source_kind`: an `"ethtrust"` requirement is always
    `"structural_predicate"`-derived today (EthTrust's static corpus has no
    other evidence path yet), but the two are independent axes by design
    so a future non-predicate EthTrust evidence path wouldn't need a schema
    change."""
    confidence: float | None = None
    """Property-level confidence, when the generation method produces one
    (currently only `semantic_derivation` does -- see `RawSemanticProperty.
    confidence`). `None`, not a fabricated default, for every
    deterministically-derived property: a structural-predicate match or a
    verbatim standard-clause translation doesn't have a meaningful
    "confidence" separate from the evidence itself."""
    rationale: str = ""
    """WHY this property must hold, in the generator's own words. Empty
    for `"ethtrust"`/`"erc_gp"` properties -- their rationale IS
    `property_text` (the spec's own normative sentence), not a separate
    field; populated only for `"code_semantics"` properties, where the
    obligation text and the justification for it are genuinely distinct
    (see Section 9's grounding requirement: WHY should this property
    exist)."""
    grounding_evidence: tuple[str, ...] = ()
    """Concrete WHERE-grounded-from citations for a `"code_semantics"`
    property (standard clause ids, doc file/section citations, specific
    code facts) -- distinct from `source_provenance` (which already serves
    this role for `"ethtrust"`/`"erc_gp"` properties via `req_id`/
    `spec_section`). Always empty for non-semantic properties; see
    `property_grounding.ground_semantic_property` for how this gets
    populated and why an ungrounded property is rejected rather than kept
    with an empty tuple here."""


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

    is_generated_erc = instance.req_id.startswith("gp-accepted-standard__")
    source_kind = "erc_gp" if is_generated_erc else "ethtrust"
    generation_method = "standard_clause" if is_generated_erc else "structural_predicate"

    return PropertyMetadata(
        property_id=instance.instance_id,
        requirement_id=instance.req_id,
        requirement_level=requirement_record.get("level"),
        requirement_semantic_intent=requirement_record.get("title"),
        property_text=instance.focused_clause or requirement_record.get("normative_text", ""),
        target_contract=target_contract,
        target_function=target_function,
        location=instance.candidate_location or "",
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
        requirement_explanatory_text=requirement_record.get("explanatory_text", ""),
        source_kind=source_kind,
        generation_method=generation_method,
    )


_FILE_LIKE_SUFFIXES = (".sol", ".md", ".json", ".yml", ".yaml", ".txt")


def _property_target_files(prop: PropertyMetadata) -> tuple[str, ...]:
    """Best-effort file path(s) this property targets, for scope
    filtering. Prefers `relevant_files` (Slither-verified, from real
    compiled `source_mapping`); falls back to `location` itself when it
    already looks like a file path (e.g. "README.md") that Slither never
    compiled so never enriched via `relevant_files`. Empty when the
    property targets something inherently non-file-scoped (e.g.
    "compiler config", a bare project/repo name) -- `filter_properties_
    to_scope` never treats these as out-of-scope.
    """
    if prop.relevant_files:
        return prop.relevant_files
    head = (prop.location or "").split(" ", 1)[0]
    if head.endswith(_FILE_LIKE_SUFFIXES):
        return (head,)
    return ()


def _paths_match(candidate: str, scope_file: str) -> bool:
    """True when `candidate` and `scope_file` name the same file,
    tolerating differing relative-path prefixes (e.g. Slither's
    project-root-relative "2024-01-canto/src/X.sol" vs. a bare
    "src/X.sol" scope.txt entry) via suffix comparison on path
    components, not raw string prefix/substring matching.
    """
    c = candidate.replace("\\", "/").lstrip("./")
    s = scope_file.replace("\\", "/").lstrip("./")
    return c == s or c.endswith("/" + s) or s.endswith("/" + c)


def split_properties_by_scope(
    properties: list[PropertyMetadata], scope_files: list[str],
) -> tuple[list[PropertyMetadata], list[PropertyMetadata]]:
    """Same in-scope test `filter_properties_to_scope` uses, but returns
    BOTH halves (kept, dropped) instead of discarding the dropped one --
    needed so `forward_out_of_scope_context` can still see what was
    filtered out. See `filter_properties_to_scope`'s docstring for the
    actual scoping rule; this is a strict superset of that function's
    behavior, not a separate rule.
    """
    if not scope_files:
        return list(properties), []
    kept: list[PropertyMetadata] = []
    dropped: list[PropertyMetadata] = []
    for prop in properties:
        candidates = _property_target_files(prop)
        if not candidates or any(_paths_match(c, s) for c in candidates for s in scope_files):
            kept.append(prop)
        else:
            dropped.append(prop)
    return kept, dropped


def filter_properties_to_scope(
    properties: list[PropertyMetadata], scope_files: list[str],
) -> list[PropertyMetadata]:
    """Drops properties whose only resolvable file target(s) fall
    outside the audit's declared `scope_files` -- e.g. vendored third-
    party libraries (OpenZeppelin's Address.sol/Math.sol), sibling
    contracts never listed in scope.txt, or a stray documentation file
    (README.md) a candidate-location heuristic mis-targeted. Properties
    with no resolvable file target at all (compiler-config-level checks,
    bare project-name pseudo-locations) are never considered out-of-
    scope by this filter and are always kept, since they're inherently
    about the whole compiled unit rather than one specific (possibly
    wrong) file. A no-op when `scope_files` is empty.

    Dropping a property here means it is never independently
    investigated/gradeable -- correct per the audit's own declared
    scope. It does NOT mean the property's requirement is necessarily
    irrelevant background for something that IS in scope; see
    `forward_out_of_scope_context` for that separate concern.
    """
    kept, _dropped = split_properties_by_scope(properties, scope_files)
    return kept


def shares_callgraph_region(a: PropertyMetadata, b: PropertyMetadata) -> bool:
    """True if two properties' one-hop callgraph neighborhoods overlap,
    or either directly names the other's own target function as a
    neighbor. The same real, structural "these two functions are one
    call apart" signal is meaningful for two different purposes: the
    grouping engine's own compatibility scoring
    (`rtf.l11_investigation_grouping.grouping_engine.compatibility_
    score`, which reuses this exact function rather than reimplementing
    it) and `forward_out_of_scope_context` below.
    """
    if set(a.callgraph_neighbors) & set(b.callgraph_neighbors):
        return True
    if a.target_function and b.target_function:
        if f"fn::{b.target_contract}.{b.target_function}" in a.callgraph_neighbors:
            return True
        if f"fn::{a.target_contract}.{a.target_function}" in b.callgraph_neighbors:
            return True
    return False


def forward_out_of_scope_context(
    kept: list[PropertyMetadata], dropped: list[PropertyMetadata],
) -> list[PropertyMetadata]:
    """For each KEPT (in-scope) property, finds every DROPPED (out-of-
    scope) property it shares a real callgraph edge with (see
    `shares_callgraph_region`) and, when that dropped property's parent
    requirement carries spec explanatory text, forwards that text into
    the kept property's `related_out_of_scope_context` -- clearly
    attributed to its source requirement and explicitly caveated as
    coming from an out-of-scope target, never presented as if it were
    itself an in-scope finding.

    This does NOT re-admit the dropped property as its own
    investigatable check -- only its background guidance travels, one
    hop, to a property that IS in scope and genuinely call-graph-
    adjacent to it. Root-cased by a real case: canto's H-01
    (LendingLedger.update_market passing a block-number-scale `epoch`
    to GaugeController.gauge_relative_weight_write, which internally
    treats it as a timestamp) -- GaugeController is out of scope per
    canto's own scope.txt, so `req-2-block-data-misuse`'s properties
    (which name this exact failure pattern, "block.number / 14 as a
    proxy for elapsed seconds") get dropped, but `update_market`'s own
    in-scope properties are one callgraph hop away from them and should
    still see that guidance.

    Deduplicated per (kept property, source requirement_id): multiple
    dropped instances of the same requirement (one per candidate
    location) would otherwise repeat identical guidance.
    """
    result: list[PropertyMetadata] = []
    for k in kept:
        seen_req_ids: set[str] = set()
        forwarded: list[str] = []
        for d in dropped:
            if not d.requirement_explanatory_text or d.requirement_id in seen_req_ids:
                continue
            if not shares_callgraph_region(k, d):
                continue
            seen_req_ids.add(d.requirement_id)
            # `requirement_explanatory_text` carries the spec's own paragraph
            # breaks (render_explanatory_text joins chunks with "\n\n"). This
            # note is rendered as ONE Markdown bullet line by
            # `generate_cluster_plan_md` -- embedding those raw blank lines
            # would split the bullet, so everything past the first paragraph
            # (concretely: the SWC-116 example itself, for the req-2-block-
            # data-misuse case this whole mechanism was built for) renders as
            # bare, unattributed text floating outside the bullet, no longer
            # visibly tied to this property. Collapse to one line instead.
            single_line_text = " ".join(d.requirement_explanatory_text.split())
            forwarded.append(
                f"[Background from out-of-scope requirement {d.requirement_id} "
                f"(target `{d.target_contract}.{d.target_function}` is outside this "
                f"audit's declared scope, so it is not itself an investigatable finding "
                f"here) -- forwarded because it is call-graph-adjacent to this property's "
                f"own target: {single_line_text}"
            )
        result.append(replace(k, related_out_of_scope_context=tuple(forwarded)) if forwarded else k)
    return result
