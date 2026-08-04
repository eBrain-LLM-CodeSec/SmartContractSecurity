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

# name -> callable(pg, node_id, features, params) -> PredicateStatus. Every
# boolean predicate takes `params` (the owning family's routing_spec.yaml
# params dict) uniformly, even predicates that ignore it -- so a predicate
# like `precision_sensitive_arithmetic_exists` can read its own
# routing_spec.yaml-level param (bounded-search depth) the same way the
# enum predicate `authorization_control_state` already does, without a
# special-cased dispatch path. `params` defaults to None on every predicate
# function so direct unit-test calls (3 positional args) keep working.
BOOLEAN_PREDICATES = {
    "external_call_exists": P.external_call_exists,
    "write_after_external_call_exists": P.write_after_external_call_exists,
    "unsafe_cast_count_gt_zero": P.unsafe_cast_count_gt_zero,
    "visibility_is_public_or_external": P.visibility_is_public_or_external,
    "not_constructor": P.not_constructor,
    "state_write_exists": P.state_write_exists,
    "callback_interface_signature_match": P.callback_interface_signature_match,
    "accounting_identifier_signal": P.accounting_identifier_signal,
    "accounting_action_identifier_signal": P.accounting_action_identifier_signal,
    "precision_sensitive_arithmetic_exists": P.precision_sensitive_arithmetic_exists,
    "external_call_and_state_write_exists": P.external_call_and_state_write_exists,
    "numeric_user_input_exists": P.numeric_user_input_exists,
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
    # True only when every OTHER predicate in this gate's `all:` list already
    # resolved SATISFIED and the sole reason the gate didn't fire is one
    # UNRESOLVED predicate -- i.e. that predicate is the only thing standing
    # between this route and firing (Gap C, Workstream 2). A gate that was
    # already going to fail on a definitively MISSING predicate is NOT
    # decision-blocking, regardless of any UNRESOLVED predicate elsewhere in
    # the same gate -- that's noise, not "we lost information here."
    decision_blocking_unresolved: bool = False


def evaluate_gate(pg: ProgramGraph, node_id: str, features: NodeFeatures | None,
                   family: FamilySpec, gate: Gate) -> Route:
    statuses: list[P.PredicateStatus] = []
    for item in gate.predicate["all"]:
        if isinstance(item, str):
            fn = BOOLEAN_PREDICATES[item]
            statuses.append(fn(pg, node_id, features, family.params))
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

    # This formula is correct specifically because routing_spec.yaml's gate
    # DSL supports only flat `all:` (conjunction) today -- spec.py's
    # _parse_predicate requires set(raw.keys()) == {"all"}, no any/not
    # support. The general version of this check ("would replacing the
    # unresolved predicate's value change the gate's outcome?") is what a
    # future any/not/nested DSL would need instead of this all:-specific
    # shortcut (see test_spec_dsl_is_all_only_today).
    decision_blocking_unresolved = bool(unresolved) and all(
        s.status == "SATISFIED" for s in statuses if s.status != "UNRESOLVED"
    )

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
        decision_blocking_unresolved=decision_blocking_unresolved,
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


# --- Gap C, Workstream 2: decision-blocking-unresolved investigation fallback

INVESTIGATION_FILTERED_NOT_ENTRYPOINT = "INVESTIGATION_FILTERED_NOT_ENTRYPOINT"
INVESTIGATION_SELECTED = "INVESTIGATION_SELECTED"
INVESTIGATION_DEFERRED_BY_BUDGET = "INVESTIGATION_DEFERRED_BY_BUDGET"

DEFAULT_UNRESOLVED_INVESTIGATION_MAX_PER_AUDIT = 15


@dataclass
class UnresolvedInvestigationUnit:
    routing_unit: str
    unit_type: str
    families_blocked: list[str]
    blocked_predicates: list[str]
    evidence: list[str]  # deduped "predicate: note" pairs
    status: str  # INVESTIGATION_FILTERED_NOT_ENTRYPOINT | INVESTIGATION_SELECTED | INVESTIGATION_DEFERRED_BY_BUDGET


def _unresolved_evidence_strings(routes: list[Route]) -> list[str]:
    items: set[str] = set()
    for r in routes:
        for s in r.predicates:
            if s.status != "UNRESOLVED":
                continue
            for note in (s.evidence or ["no evidence"]):
                items.add(f"{s.predicate}: {note}")
    return sorted(items)


def unresolved_investigation_units(
    pg: ProgramGraph, routes: list[Route],
    max_per_audit: int = DEFAULT_UNRESOLVED_INVESTIGATION_MAX_PER_AUDIT,
) -> list[UnresolvedInvestigationUnit]:
    """One entry per routing unit that has at least one genuinely
    decision-blocking-unresolved gate, in a family not already covered by a
    normal fired route for that SAME family (the fired route's context
    already carries the unresolved evidence alongside it via
    `RouteContextGroup.unresolved_routes` -- a second, separate investigation
    call would just duplicate that analysis). A decision-blocking-unresolved
    gate in a DIFFERENT family from a unit's fired route still gets its own
    entry here -- different families are genuinely different information.

    Two decision-blocking-unresolved gates within the same family for the
    same unit collapse into ONE entry (not two), with `families_blocked`
    listing every qualifying family and `evidence`/`blocked_predicates`
    merged and deduped across all of them.

    `status` is never a silent drop: every candidate unit gets exactly one
    of INVESTIGATION_FILTERED_NOT_ENTRYPOINT (didn't pass the
    visibility/constructor entry-point pre-filter -- reuses
    `visibility_is_public_or_external` + `not_constructor`, the same
    entry-point class P1 already targets), INVESTIGATION_SELECTED (eligible,
    within `max_per_audit`), or INVESTIGATION_DEFERRED_BY_BUDGET (eligible,
    over budget -- still returned with full evidence, never dropped).
    Selection among eligible units uses a composite priority --
    (families_blocked_count, has_state_write, has_external_call,
    accounting_identifier_signal_matched, is_payable), compared as a tuple
    descending -- tie-broken by routing_unit for determinism.
    """
    fired_unit_families = {(r.routing_unit, r.family) for r in routes if r.route_would_fire}

    by_unit: dict[str, dict[str, list[Route]]] = {}
    for r in routes:
        if not r.decision_blocking_unresolved:
            continue
        if (r.routing_unit, r.family) in fired_unit_families:
            continue
        by_unit.setdefault(r.routing_unit, {}).setdefault(r.family, []).append(r)

    units: list[UnresolvedInvestigationUnit] = []
    priority_by_unit: dict[str, tuple] = {}

    for routing_unit in sorted(by_unit):
        family_routes = by_unit[routing_unit]
        families_blocked = sorted(family_routes)
        all_routes_for_unit = [r for group in family_routes.values() for r in group]
        blocked_predicates = sorted({
            s.predicate for r in all_routes_for_unit for s in r.predicates if s.status == "UNRESOLVED"
        })
        evidence = _unresolved_evidence_strings(all_routes_for_unit)
        unit_type = all_routes_for_unit[0].unit_type

        vis = P.visibility_is_public_or_external(pg, routing_unit, None)
        ctor = P.not_constructor(pg, routing_unit, None)
        if not (vis.status == "SATISFIED" and ctor.status == "SATISFIED"):
            units.append(UnresolvedInvestigationUnit(
                routing_unit=routing_unit, unit_type=unit_type, families_blocked=families_blocked,
                blocked_predicates=blocked_predicates, evidence=evidence,
                status=INVESTIGATION_FILTERED_NOT_ENTRYPOINT,
            ))
            continue

        has_state_write = P.state_write_exists(pg, routing_unit, None).status == "SATISFIED"
        has_external_call = P.external_call_exists(pg, routing_unit, None).status == "SATISFIED"
        accounting_signal = P.accounting_identifier_signal(pg, routing_unit, None).status == "SATISFIED"
        function = P._function_by_node_id(pg, routing_unit)
        is_payable = bool(getattr(function, "payable", False))

        priority_by_unit[routing_unit] = (
            len(families_blocked), has_state_write, has_external_call, accounting_signal, is_payable,
        )
        units.append(UnresolvedInvestigationUnit(
            routing_unit=routing_unit, unit_type=unit_type, families_blocked=families_blocked,
            blocked_predicates=blocked_predicates, evidence=evidence,
            status=INVESTIGATION_SELECTED,  # provisional -- capped below
        ))

    eligible = [u for u in units if u.status == INVESTIGATION_SELECTED]
    eligible.sort(key=lambda u: (tuple(-int(x) for x in priority_by_unit[u.routing_unit]), u.routing_unit))
    for i, u in enumerate(eligible):
        if i >= max_per_audit:
            u.status = INVESTIGATION_DEFERRED_BY_BUDGET

    return units
