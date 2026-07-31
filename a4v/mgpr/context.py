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

from dataclasses import dataclass, field
from pathlib import Path

from a4v.graph import (
    ProgramGraph, FUNCTION, CONTRACT, MODIFIER,
    STATE_READ, STATE_WRITE, EXTERNAL_CALL, WRITE_AFTER_EXTERNAL_CALL,
    USES_MODIFIER, INHERITS, DECLARES,
)
from a4v.mgpr import predicates as P
from a4v.mgpr.router import Route
from a4v.slice import ContextBundle, BundleBuilder

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


def _p2_context(pg: ProgramGraph, seed: str) -> ContextRecord:
    included = [seed]
    included_ids = [seed]

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

    unresolved = [
        "callback_reachable_entrypoints: deferred, requires callback_potential "
        "extraction not built in this slice"
    ]
    record = ContextRecord(routing_unit=seed, family="P2_REENTRANCY", included=included,
                            excluded=[], unresolved=unresolved)
    return record, included_ids


def _p5_context(pg: ProgramGraph, seed: str) -> ContextRecord:
    included = [seed]
    included_ids = [seed]
    sites = P.unsafe_cast_sites(pg, seed)
    for s in sites:
        included.append(f"{seed}:{s['line']} (cast_site: {s['expression']})")
    excluded = ["(single_function_scope: no neighbor functions/contracts included)"]
    record = ContextRecord(routing_unit=seed, family="P5_ARITHMETIC_PRECISION", included=included,
                            excluded=excluded, unresolved=[])
    return record, included_ids


def _p1_context(pg: ProgramGraph, seed: str) -> ContextRecord:
    included = [seed]
    included_ids = [seed]
    excluded: list[str] = []
    unresolved: list[str] = []

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


def build_context(pg: ProgramGraph, route: Route) -> tuple[ContextBundle, ContextRecord]:
    builder = _BUILDERS.get(route.family)
    if builder is None:
        raise ValueError(f"no context builder registered for family {route.family!r}")
    record, included_ids = builder(pg, route.routing_unit)
    bundle = _bundle_for(pg, route.routing_unit, included_ids)
    return bundle, record
