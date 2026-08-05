"""MGPR context constructor: builds bounded, family-specific context for a
fired Route (plan sections 3 & 6.4). Replaces
`BundleBuilder.expand(seed, hops=1)` as the source of Commentator context
for MGPR-routed units -- each family gets its own include/stop rules, not
one fixed hop radius.

`build_context` returns two things: a `ContextBundle` (slice.py's existing
dataclass, reused unmodified so `Commentator.comment_bundle`'s signature
needs no change) for the Commentator call itself, and a `ContextRecord`
(this module) -- the descriptive included/excluded/unresolved list the
feasibility study reports verbatim (plan section 6.4). Neither ever states
whether the resulting context is "enough."
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from a4v.graph import (
    ProgramGraph, FUNCTION, CONTRACT, MODIFIER,
    STATE_READ, STATE_WRITE, STATE_WRITE_TRANSITIVE, EXTERNAL_CALL, WRITE_AFTER_EXTERNAL_CALL,
    USES_MODIFIER, INHERITS, DECLARES,
)
from a4v.mgpr import predicates as P
from a4v.mgpr.router import Route, UnresolvedInvestigationUnit
from a4v.slice import ContextBundle, BundleBuilder

_NODE_REF_RE = re.compile(r"(?:mod|fn|var|contract|ext)::[^\s:]+")

_source_cache: dict[str, list[str]] = {}


def _read_lines(path: str) -> list[str] | None:
    if path not in _source_cache:
        try:
            _source_cache[path] = Path(path).read_text(errors="ignore").splitlines()
        except OSError:
            return None
    return _source_cache[path]


def _excerpt(node_data: dict) -> str | None:
    path = node_data.get("file")
    lines = node_data.get("lines")
    if not path or not lines:
        return None
    all_lines = _read_lines(path)
    if all_lines is None:
        return None
    start, end = min(lines), max(lines)
    return "\n".join(all_lines[start - 1 : end])


@dataclass
class ContextRecord:
    routing_unit: str
    family: str
    included: list[str] = field(default_factory=list)
    excluded: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)


def _bundle_for(pg: ProgramGraph, seed: str, included_node_ids: list[str]) -> ContextBundle:
    """Builds a slice.py-compatible ContextBundle whose source_excerpts
    cover exactly the family-selected `included_node_ids` (plus the seed),
    not a fixed-hop neighborhood. Typed fields (modifiers/state_vars/etc.)
    are pulled directly off the seed, matching BundleBuilder's own
    convention, since those are informational summary fields, not the
    context-selection mechanism itself.
    """
    seed_data = pg.graph.nodes[seed]
    contract_name = seed_data.get("contract")
    contract_node = f"contract::{contract_name}" if contract_name else None

    modifiers = [pg.graph.nodes[m]["name"] for m in pg.neighbors_by_kind(seed, USES_MODIFIER)]
    state_read = [pg.graph.nodes[v]["name"] for v in pg.neighbors_by_kind(seed, STATE_READ)]
    state_written = [pg.graph.nodes[v]["name"] for v in pg.neighbors_by_kind(seed, STATE_WRITE)]
    state_vars = sorted(set(state_read) | set(state_written))
    callers = [n for n in pg.graph.predecessors(seed) if pg.graph.nodes[n].get("kind") == FUNCTION]
    callees = pg.neighbors_by_kind(seed, "calls")
    external = pg.neighbors_by_kind(seed, EXTERNAL_CALL)
    write_after = [pg.graph.nodes[v]["name"] for v in pg.neighbors_by_kind(seed, WRITE_AFTER_EXTERNAL_CALL)]

    inherited = []
    if contract_node and contract_node in pg.graph:
        for base in pg.neighbors_by_kind(contract_node, INHERITS):
            inherited.append(pg.graph.nodes[base]["name"])

    source_excerpts, source_start_lines, source_files = {}, {}, {}
    for node in set(included_node_ids) | {seed}:
        if node not in pg.graph:
            continue
        data = pg.graph.nodes[node]
        if data.get("kind") in (FUNCTION, CONTRACT, MODIFIER):
            excerpt = _excerpt(data)
            if excerpt:
                source_excerpts[node] = excerpt
                lines = data.get("lines") or []
                if lines:
                    source_start_lines[node] = min(lines)
                if data.get("file"):
                    source_files[node] = data["file"]

    contract_summary = ""
    if contract_node and contract_node in pg.graph:
        cdata = pg.graph.nodes[contract_node]
        fn_names = [pg.graph.nodes[f]["name"] for f in pg.neighbors_by_kind(contract_node, DECLARES)
                    if pg.graph.nodes[f].get("kind") == FUNCTION]
        parts = [f"contract {cdata.get('name')}"]
        if inherited:
            parts.append(f"inherits {', '.join(inherited)}")
        if fn_names:
            parts.append(f"functions: {', '.join(fn_names)}")
        contract_summary = "; ".join(parts)

    return ContextBundle(
        seed=seed,
        contract=contract_name or "",
        contract_summary=contract_summary,
        inherited_defs=inherited,
        modifiers=modifiers,
        state_vars=state_vars,
        callers=callers,
        callees=callees,
        external_interactions=external,
        write_after_external_call_vars=write_after,
        neighborhood=set(included_node_ids),
        source_excerpts=source_excerpts,
        source_excerpt_start_lines=source_start_lines,
        source_files=source_files,
    )


def _p2_context(pg: ProgramGraph, seed: str, gates_fired: list[str], unresolved_evidence: list[str]) -> ContextRecord:
    included = [seed]
    included_ids = [seed]
    unresolved: list[str] = list(unresolved_evidence)

    if "P2_CALL_BEFORE_WRITE" in gates_fired:
        write_after = pg.neighbors_by_kind(seed, WRITE_AFTER_EXTERNAL_CALL)
        ext_calls = pg.neighbors_by_kind(seed, EXTERNAL_CALL)
        # sorted, not raw iteration order -- Slither's own high_level_calls/
        # low_level_calls iteration order is not guaranteed stable across
        # processes (confirmed live: identical membership, differing order,
        # across two runs with the sorted-frontier fix already applied below).
        # Membership is unaffected; this only fixes output-list determinism.
        for v in sorted(ext_calls):
            included.append(f"{v} (external_call_site)")
            included_ids.append(v)
        for v in sorted(write_after):
            included.append(f"{v} (writes_before_and_after_call)")
            included_ids.append(v)

        state_written = set(pg.neighbors_by_kind(seed, STATE_WRITE))
        state_read = set(pg.neighbors_by_kind(seed, STATE_READ))
        affected = state_written | state_read | set(write_after)

        seen_statevars = set(affected)
        seen_functions = {seed}
        frontier = set(affected)
        while frontier:
            next_frontier: set[str] = set()
            # Iterate in sorted order, not raw set order -- Python's per-process
            # string hash randomization otherwise makes the traversal (and
            # therefore this record's `included` list order) non-deterministic
            # across runs, even though the resulting MEMBERSHIP is unaffected.
            # Confirmed live: two independent runs of the same study produced
            # byte-identical gate_evaluation.jsonl/route_manifest.jsonl but
            # differing entry order in context_manifest.jsonl's P2 records.
            for var_id in sorted(frontier):
                readers = pg.neighbors_by_kind(var_id, STATE_READ, direction="in")
                writers = pg.neighbors_by_kind(var_id, STATE_WRITE, direction="in")
                for fn_id in sorted(set(readers) | set(writers)):
                    if fn_id in seen_functions:
                        continue
                    seen_functions.add(fn_id)
                    included.append(f"{fn_id} (functions_touching_affected_state)")
                    included_ids.append(fn_id)
                    for v in pg.neighbors_by_kind(fn_id, STATE_WRITE) + pg.neighbors_by_kind(fn_id, STATE_READ):
                        if v not in seen_statevars:
                            seen_statevars.add(v)
                            next_frontier.add(v)
            frontier = next_frontier

        unresolved.append(
            "callback_reachable_entrypoints: deferred, requires callback_potential "
            "extraction not built in this slice"
        )

    if "P2_CALLBACK_REACHABLE_WRITE" in gates_fired:
        match = P.callback_interface_signature_match(pg, seed, None)
        for ev in match.evidence:
            included.append(f"{seed} (callback_interface_signature: {ev})")
        write_targets = sorted(set(pg.neighbors_by_kind(seed, STATE_WRITE))
                                | set(pg.neighbors_by_kind(seed, STATE_WRITE_TRANSITIVE)))
        for v in write_targets:
            included.append(f"{v} (state_write_from_callback)")
            if v not in included_ids:
                included_ids.append(v)

    record = ContextRecord(routing_unit=seed, family="P2_REENTRANCY", included=included,
                            excluded=[], unresolved=unresolved)
    return record, included_ids


def _p5_context(pg: ProgramGraph, seed: str, gates_fired: list[str], unresolved_evidence: list[str]) -> ContextRecord:
    included = [seed]
    included_ids = [seed]
    unresolved: list[str] = list(unresolved_evidence)

    if "P5_NARROWING_CAST" in gates_fired:
        for s in P.unsafe_cast_sites(pg, seed):
            included.append(f"{seed}:{s['line']} (cast_site: {s['expression']})")

    if "P5_ACCOUNTING_ARITHMETIC" in gates_fired:
        for s in P.arithmetic_op_sites(pg, seed):
            included.append(f"{seed}:{s['line']} (arithmetic_op_site: {s['expression']})")
        precision = P.precision_sensitive_arithmetic_exists(pg, seed, None)
        for ev in precision.evidence:
            if "assembly" in ev:
                included.append(f"{seed} (assembly_arithmetic_note: {ev})")
            elif "transitive" in ev:
                # Found in an internal-call BFS at depth > 0, not the seed's
                # own body -- arithmetic_op_sites (seed-only, depth 0) never
                # surfaces this, so without this branch a transitively-
                # triggered fire got NO arithmetic evidence at all in its
                # context (confirmed live: ~28% of P5_ACCOUNTING_ARITHMETIC's
                # corpus-wide fires during the Gap B validation run).
                included.append(f"{seed} (transitive_arithmetic_note: {ev})")

    if "P5_EXTERNAL_CALL_ACCOUNTING_WRITE" in gates_fired:
        for t in sorted(pg.neighbors_by_kind(seed, EXTERNAL_CALL)):
            included.append(f"{seed} -> {t} (external_call_site)")
        write_targets = sorted(set(pg.neighbors_by_kind(seed, STATE_WRITE))
                                | set(pg.neighbors_by_kind(seed, STATE_WRITE_TRANSITIVE)))
        for v in write_targets:
            included.append(f"{v} (written_state_var)")
            if v not in included_ids:
                included_ids.append(v)

    if "P5_ACCOUNTING_ENTRYPOINT" in gates_fired:
        action = P.accounting_action_identifier_signal(pg, seed, None)
        for ev in action.evidence:
            included.append(f"{seed} (accounting_action_term: {ev})")
        numeric = P.numeric_user_input_exists(pg, seed, None)
        for ev in numeric.evidence:
            included.append(f"{seed} (numeric_parameter: {ev})")

    # No P5 gate expands into other functions/contracts (only the seed's own
    # source plus its own state-var neighbors, which never get a source
    # excerpt -- see _bundle_for's FUNCTION/CONTRACT/MODIFIER-only filter) --
    # true for every P5 gate combination, not just P5_NARROWING_CAST alone.
    excluded = ["(single_function_scope: no neighbor functions/contracts included)"]
    record = ContextRecord(routing_unit=seed, family="P5_ARITHMETIC_PRECISION", included=included,
                            excluded=excluded, unresolved=unresolved)
    return record, included_ids


def _p1_context(pg: ProgramGraph, seed: str, gates_fired: list[str], unresolved_evidence: list[str]) -> ContextRecord:
    # P1 has exactly one gate today, so gates_fired is ignored here -- but
    # unresolved_evidence (from a decision-blocking-unresolved route in the
    # same family, per the cross-cutting fix) is still consumed.
    included = [seed]
    included_ids = [seed]
    excluded: list[str] = []
    unresolved: list[str] = list(unresolved_evidence)

    for m in pg.neighbors_by_kind(seed, USES_MODIFIER):
        included.append(f"{m} (applied_modifier)")
        included_ids.append(m)

    contract_name = pg.graph.nodes[seed].get("contract")
    contract_id = f"contract::{contract_name}" if contract_name else None
    if contract_id and contract_id in pg.graph:
        base_chain = list(pg.neighbors_by_kind(contract_id, INHERITS))
        visited = {contract_id}
        i = 0
        while i < len(base_chain):
            base_id = base_chain[i]
            i += 1
            if base_id in visited:
                continue
            visited.add(base_id)
            if not pg.graph.nodes[base_id].get("kind"):
                unresolved.append(f"{base_id}: base contract not present in compile unit")
                continue
            base_chain.extend(pg.neighbors_by_kind(base_id, INHERITS))
            for decl_id in pg.neighbors_by_kind(base_id, DECLARES):
                if pg.graph.nodes[decl_id].get("kind") == MODIFIER:
                    included.append(f"{decl_id} (base_contract_modifier_def)")
                    included_ids.append(decl_id)
    else:
        excluded.append("(no contract node resolvable for base_contract_modifier_defs)")

    record = ContextRecord(routing_unit=seed, family="P1_AUTHORIZATION", included=included,
                            excluded=excluded, unresolved=unresolved)
    return record, included_ids


_BUILDERS = {
    "P1_AUTHORIZATION": _p1_context,
    "P2_REENTRANCY": _p2_context,
    "P5_ARITHMETIC_PRECISION": _p5_context,
}


@dataclass
class RouteContextGroup:
    """All routes for one (routing_unit, family) pair that should feed a
    SINGLE Commentator call: `fired_routes` (every gate in this family that
    actually fired for this unit -- merged, not picked-one, since more than
    one gate firing on the same unit/family is now possible with Gap D/B's
    additional gates) plus `unresolved_routes` (any decision-blocking-
    unresolved route for the SAME (unit, family) pair, so that evidence
    rides along in the same call instead of triggering a separate,
    duplicative investigation call -- see Gap C, Workstream 2's redundancy
    reduction).
    """
    fired_routes: list[Route]
    unresolved_routes: list[Route] = field(default_factory=list)


def _dedup_unresolved_evidence(unresolved_routes: list[Route]) -> list[str]:
    """Same dedup logic `unresolved_investigation_units` uses -- kept as a
    separate copy (not imported) since the two call sites operate on
    different route groupings (this one is always scoped to a single
    (unit, family) pair already; router.py's version spans multiple
    families for one unit)."""
    items: set[str] = set()
    for r in unresolved_routes:
        for s in r.predicates:
            if s.status != "UNRESOLVED":
                continue
            for note in (s.evidence or ["no evidence"]):
                items.add(f"{s.predicate}: {note}")
    return sorted(items)


def build_context(pg: ProgramGraph, group: RouteContextGroup) -> tuple[ContextBundle, ContextRecord]:
    """Merges EVERY fired route in `group` into one context (never "pick a
    representative route" -- if a unit fires two gates in the same family,
    both gates' evidence sections are included, not one silently winning),
    and carries along any decision-blocking-unresolved evidence for the
    same (unit, family) pair via `ContextRecord.unresolved`.
    """
    if not group.fired_routes:
        raise ValueError("RouteContextGroup requires at least one fired route")
    family = group.fired_routes[0].family
    seed = group.fired_routes[0].routing_unit
    gates_fired = sorted({r.gate for r in group.fired_routes})
    unresolved_evidence = _dedup_unresolved_evidence(group.unresolved_routes)

    builder = _BUILDERS.get(family)
    if builder is None:
        raise ValueError(f"no context builder registered for family {family!r}")
    record, included_ids = builder(pg, seed, gates_fired, unresolved_evidence)
    bundle = _bundle_for(pg, seed, included_ids)
    return bundle, record


def build_investigation_context(
    pg: ProgramGraph, unit: UnresolvedInvestigationUnit,
) -> tuple[ContextBundle, ContextRecord]:
    """Bounded by design: the unit's own source, plus whichever specific
    modifier/callee node its unresolved evidence itself names as unreadable
    (parsed out of the evidence strings via a node-id pattern -- the same
    "<node_id>: <reason>" shape `resolution.py`'s SearchResult.notes already
    uses) -- nothing expanded further than that. Family is the synthetic
    "UNRESOLVED_INVESTIGATION" tag, not one of P1/P2/P5, since this context
    isn't scoped to any one family's evidence -- it may cover several
    (`unit.families_blocked`).
    """
    seed = unit.routing_unit
    included = [seed]
    included_ids = [seed]

    cited_nodes: set[str] = set()
    for ev in unit.evidence:
        cited_nodes.update(_NODE_REF_RE.findall(ev))
    for node_ref in sorted(cited_nodes):
        if node_ref == seed or node_ref not in pg.graph:
            continue
        included.append(f"{node_ref} (cited_in_unresolved_evidence)")
        included_ids.append(node_ref)

    excluded = [
        "(bounded_by_design: only the seed's own source plus evidence-cited "
        "unreadable modifier/callee nodes are included, no further expansion)"
    ]
    record = ContextRecord(
        routing_unit=seed, family="UNRESOLVED_INVESTIGATION",
        included=included, excluded=excluded, unresolved=list(unit.evidence),
    )
    bundle = _bundle_for(pg, seed, included_ids)
    return bundle, record
