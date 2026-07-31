"""MGPR deterministic router: evaluates routing_spec.yaml gates against a
ProgramGraph + per-function structural features, producing full-traceability
Route records (plan section 6.3) -- never a bare boolean. Multi-label by
construction: one routing unit can produce multiple fired Routes, one per
family whose gates fire; there is no unit-level "winner."
"""
from __future__ import annotations

from dataclasses import dataclass, field

from a4v.features import NodeFeatures
from a4v.graph import ProgramGraph, FUNCTION
from a4v.mgpr import predicates as P
from a4v.mgpr.spec import FamilySpec, Gate, RoutingSpec

# name -> callable(pg, node_id, features) -> PredicateStatus
BOOLEAN_PREDICATES = {
    "external_call_exists": P.external_call_exists,
    "write_after_external_call_exists": P.write_after_external_call_exists,
    "unsafe_cast_count_gt_zero": P.unsafe_cast_count_gt_zero,
    "visibility_is_public_or_external": P.visibility_is_public_or_external,
    "not_constructor": P.not_constructor,
    "state_write_exists": P.state_write_exists,
}

# name -> callable(pg, node_id, features, params, expected) -> PredicateStatus
ENUM_PREDICATES = {
    "authorization_control_state": P.authorization_control_state_predicate,
}

KNOWN_PREDICATES = set(BOOLEAN_PREDICATES) | set(ENUM_PREDICATES)


@dataclass
class Route:
    routing_unit: str
    unit_type: str
    family: str
    gate: str
    predicates: list[P.PredicateStatus]
    route_would_fire: bool
    reason: str
    prompt_id: str
    unresolved_or_missing: list[str] = field(default_factory=list)


def evaluate_gate(pg: ProgramGraph, node_id: str, features: NodeFeatures | None,
                   family: FamilySpec, gate: Gate) -> Route:
    statuses: list[P.PredicateStatus] = []
    for item in gate.predicate["all"]:
        if isinstance(item, str):
            fn = BOOLEAN_PREDICATES[item]
            statuses.append(fn(pg, node_id, features))
        else:
            (name, expected), = item["equals"].items()
            fn = ENUM_PREDICATES[name]
            statuses.append(fn(pg, node_id, features, family.params, expected))

    unresolved = [s for s in statuses if s.status == "UNRESOLVED"]
    missing = [s for s in statuses if s.status == "MISSING"]
    not_applicable = [s for s in statuses if s.status == "NOT_APPLICABLE"]

    if unresolved:
        # An unresolved predicate blocks firing on its own, independent of
        # whatever the other predicates found -- an unresolved search is
        # never treated as evidence one way or the other (plan section 5).
        blocker = unresolved[0]
        fires = False
        reason = f"{blocker.predicate}: UNRESOLVED -- {'; '.join(blocker.evidence) or 'no evidence'}"
    elif missing or not_applicable:
        blocker = (missing + not_applicable)[0]
        fires = False
        reason = f"{blocker.predicate}: {blocker.status}"
    else:
        fires = True
        reason = "all 'all:' predicates SATISFIED"

    return Route(
        routing_unit=node_id,
        unit_type="function",
        family=family.name,
        gate=gate.id,
        predicates=statuses,
        route_would_fire=fires,
        reason=reason,
        prompt_id=family.prompt_id,
        unresolved_or_missing=[s.predicate for s in (unresolved + missing + not_applicable)],
    )


def route_all(pg: ProgramGraph, features: dict[str, NodeFeatures], spec: RoutingSpec) -> list[Route]:
    """Evaluate every SPECIFIED family's gates against every function
    routing unit (plan section 6.1: external stub nodes are never routing
    units). Returns every evaluated record, fired and not-fired alike --
    filtering to only-fired routes is the caller's choice, not this
    function's, so the full evidence trail is always available.
    """
    routes: list[Route] = []
    function_ids = [
        n for n in pg.nodes_of_kind(FUNCTION)
        if not pg.graph.nodes[n].get("external") and not n.startswith("ext::")
    ]
    for family in spec.specified_families():
        if "function" not in family.seed_types:
            continue
        for node_id in function_ids:
            node_features = features.get(node_id)
            for gate in family.gates:
                routes.append(evaluate_gate(pg, node_id, node_features, family, gate))
    return routes


def fired_routes(routes: list[Route]) -> list[Route]:
    return [r for r in routes if r.route_would_fire]
