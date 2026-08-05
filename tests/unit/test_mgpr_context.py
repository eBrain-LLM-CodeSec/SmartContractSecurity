from pathlib import Path

import pytest

from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.mgpr.context import RouteContextGroup, build_context, build_investigation_context
from a4v.mgpr.predicates import PredicateStatus
from a4v.mgpr.router import Route, UnresolvedInvestigationUnit, fired_routes, route_all
from a4v.mgpr.spec import load_routing_spec

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
CASTS_SOL = FIXTURES / "features" / "Casts.sol"
RESTRICTED_SOL = FIXTURES / "modifier_source" / "Restricted.sol"
ACCOUNTING_SOL = FIXTURES / "accounting_signals" / "Accounting.sol"
ROUTING_SPEC = Path(__file__).resolve().parents[2] / "routing_spec.yaml"


@pytest.fixture(scope="module")
def accounting_graph():
    return ProgramGraph.build(ACCOUNTING_SOL)


@pytest.fixture(scope="module")
def restricted_graph():
    return ProgramGraph.build(RESTRICTED_SOL)


@pytest.fixture(scope="module")
def spec():
    return load_routing_spec(ROUTING_SPEC)


@pytest.fixture(scope="module")
def vault_graph():
    return ProgramGraph.build(VAULT_SOL)


@pytest.fixture(scope="module")
def casts_graph():
    return ProgramGraph.build(CASTS_SOL)


def _find_route(routes, node_id, family, gate):
    for r in routes:
        if r.routing_unit == node_id and r.family == family and r.gate == gate:
            return r
    raise AssertionError(f"no route for {node_id}/{family}/{gate}")


def test_p2_context_includes_cross_function_shared_state(vault_graph):
    features = FeatureExtractor.compute(vault_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(vault_graph, features, spec)
    route = _find_route(routes, "fn::Vault.withdraw(uint256)", "P2_REENTRANCY", "P2_CALL_BEFORE_WRITE")
    assert route.route_would_fire

    bundle, record = build_context(vault_graph, RouteContextGroup(fired_routes=[route]))
    assert record.family == "P2_REENTRANCY"
    assert record.routing_unit == "fn::Vault.withdraw(uint256)"
    included_text = " ".join(record.included)
    assert "external_call_site" in included_text
    assert "writes_before_and_after_call" in included_text
    # deposit() also writes shares/totalShares -- the fixed-point closure
    # over STATE_READ/STATE_WRITE must find it as a function touching the
    # same affected state, without any shared-state-cluster construction.
    assert any("Vault.deposit()" in item and "functions_touching_affected_state" in item
               for item in record.included)
    assert any("callback_reachable_entrypoints" in u for u in record.unresolved)


def test_p2_context_bundle_has_source_for_included_functions(vault_graph):
    features = FeatureExtractor.compute(vault_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(vault_graph, features, spec)
    route = _find_route(routes, "fn::Vault.withdraw(uint256)", "P2_REENTRANCY", "P2_CALL_BEFORE_WRITE")
    bundle, record = build_context(vault_graph, RouteContextGroup(fired_routes=[route]))
    assert bundle.seed == "fn::Vault.withdraw(uint256)"
    assert "fn::Vault.withdraw(uint256)" in bundle.source_excerpts
    assert "fn::Vault.deposit()" in bundle.source_excerpts


def test_p5_context_includes_cast_site_and_stops_at_function_scope(casts_graph):
    features = FeatureExtractor.compute(casts_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(casts_graph, features, spec)
    route = _find_route(routes, "fn::Casts.unsafeCast(uint256)", "P5_ARITHMETIC_PRECISION", "P5_NARROWING_CAST")
    assert route.route_would_fire

    bundle, record = build_context(casts_graph, RouteContextGroup(fired_routes=[route]))
    assert any("cast_site" in item and "uint96" in item for item in record.included)
    assert any("single_function_scope" in item for item in record.excluded)
    assert record.unresolved == []
    assert set(bundle.source_excerpts) == {"fn::Casts.unsafeCast(uint256)"}


def test_p1_context_includes_applied_and_base_contract_modifiers(vault_graph):
    features = FeatureExtractor.compute(vault_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(vault_graph, features, spec)
    route = _find_route(routes, "fn::Vault.setOracle(address)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR")
    # setOracle is protected, so this gate does not fire -- context
    # construction should still work for a not-fired route (context.py
    # doesn't require route_would_fire to build context).
    assert route.route_would_fire is False

    bundle, record = build_context(vault_graph, RouteContextGroup(fired_routes=[route]))
    assert any("applied_modifier" in item and "onlyOwner" in item for item in record.included)
    assert bundle.modifiers  # onlyOwner shows up in the bundle's typed modifiers field too


def test_p1_context_on_fired_withdraw(vault_graph):
    features = FeatureExtractor.compute(vault_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(vault_graph, features, spec)
    route = _find_route(routes, "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR")
    assert route.route_would_fire is True

    bundle, record = build_context(vault_graph, RouteContextGroup(fired_routes=[route]))
    assert record.family == "P1_AUTHORIZATION"
    # withdraw has no applied modifiers -- context is just the seed plus
    # whatever base-contract modifiers exist (Ownable's onlyOwner, declared
    # but not applied to withdraw).
    assert any("base_contract_modifier_def" in item for item in record.included)


def test_build_context_raises_for_unregistered_family(vault_graph):
    from a4v.mgpr.router import Route
    fake_route = Route(
        routing_unit="fn::Vault.withdraw(uint256)", unit_type="function",
        family="P6_ACCOUNTING_SOLVENCY", gate="fake", predicates=[],
        route_would_fire=True, reason="test", prompt_id="P6_ACCOUNTING_SOLVENCY_v1",
    )
    with pytest.raises(ValueError, match="no context builder"):
        build_context(vault_graph, RouteContextGroup(fired_routes=[fake_route]))


def test_route_context_group_requires_at_least_one_fired_route(vault_graph):
    with pytest.raises(ValueError, match="at least one fired route"):
        build_context(vault_graph, RouteContextGroup(fired_routes=[]))


# --- Cross-cutting fix: merge, don't pick, when a unit fires multiple gates
# in one family -----------------------------------------------------------


def test_build_context_merges_multiple_p5_gates_fired_by_one_unit(vault_graph):
    """withdraw() fires THREE separate P5_ARITHMETIC_PRECISION gates
    (P5_ACCOUNTING_ARITHMETIC, P5_ACCOUNTING_ENTRYPOINT,
    P5_EXTERNAL_CALL_ACCOUNTING_WRITE) -- build_context must MERGE all
    three gates' evidence into one ContextRecord, not pick one and silently
    drop the others."""
    features = FeatureExtractor.compute(vault_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(vault_graph, features, spec)
    p5_routes = [
        r for r in fired_routes(routes)
        if r.routing_unit == "fn::Vault.withdraw(uint256)" and r.family == "P5_ARITHMETIC_PRECISION"
    ]
    assert len(p5_routes) == 3
    gates_fired = {r.gate for r in p5_routes}
    assert gates_fired == {"P5_ACCOUNTING_ARITHMETIC", "P5_ACCOUNTING_ENTRYPOINT", "P5_EXTERNAL_CALL_ACCOUNTING_WRITE"}

    bundle, record = build_context(vault_graph, RouteContextGroup(fired_routes=p5_routes))
    included_text = " ".join(record.included)
    # each gate's own evidence section is present -- none silently won over another
    assert "arithmetic_op_site" in included_text
    assert "external_call_site" in included_text or "written_state_var" in included_text
    assert "accounting_action_term" in included_text
    assert "numeric_parameter" in included_text


def test_build_context_merges_unresolved_evidence_alongside_fired(vault_graph):
    """No real compiled predicate can produce "one gate fired, a different
    gate in the same family decision-blocking-unresolved" today (P1 has
    exactly one gate, and no Gap B/D predicate can ever return UNRESOLVED)
    -- directly construct a synthetic unresolved Route by hand for the SAME
    (unit, family) as a real fired route, and assert the merged
    ContextRecord carries both: the unresolved route's evidence in
    `.unresolved`, alongside the fired route's normal `.included` evidence,
    not one replacing the other."""
    features = FeatureExtractor.compute(vault_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(vault_graph, features, spec)
    fired_route = _find_route(
        routes, "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
    )
    assert fired_route.route_would_fire

    unresolved_route = Route(
        routing_unit=fired_route.routing_unit, unit_type="function", family="P1_AUTHORIZATION",
        gate="SYNTHETIC_GATE",
        predicates=[PredicateStatus(
            predicate="synthetic_predicate", status="UNRESOLVED",
            evidence=["mod::Synthetic.helper(): modifier source unavailable"],
        )],
        route_would_fire=False, reason="synthetic test route", prompt_id="P1_AUTHORIZATION_v1",
        decision_blocking_unresolved=True,
    )
    group = RouteContextGroup(fired_routes=[fired_route], unresolved_routes=[unresolved_route])
    bundle, record = build_context(vault_graph, group)

    assert any(
        "synthetic_predicate" in u and "modifier source unavailable" in u for u in record.unresolved
    )
    # the fired route's normal included evidence is still there too, not
    # replaced by the unresolved evidence
    assert any("base_contract_modifier_def" in item for item in record.included)


def test_p5_context_surfaces_transitive_arithmetic_evidence_not_just_assembly(accounting_graph):
    """Regression for a gap found live during the 27-audit corpus
    validation: `quoteShares` fires P5_ACCOUNTING_ARITHMETIC via the
    TRANSITIVE branch (arithmetic lives in `_computeShareQuote`, one
    internal call away, depth > 0) -- `arithmetic_op_sites` (seed-only,
    depth 0) finds nothing, and the pre-fix code only ever surfaced
    assembly-branch evidence into `included`, so a transitively-triggered,
    non-assembly fire got NO arithmetic evidence at all in its context
    (confirmed live: ~28% of P5_ACCOUNTING_ARITHMETIC's corpus-wide fires
    during the Gap B validation run had neither `arithmetic_op_site` nor
    `assembly_arithmetic_note` in `included`)."""
    features = FeatureExtractor.compute(accounting_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(accounting_graph, features, spec)
    route = _find_route(
        routes, "fn::Accounting.quoteShares(uint256)", "P5_ARITHMETIC_PRECISION", "P5_ACCOUNTING_ARITHMETIC",
    )
    assert route.route_would_fire

    bundle, record = build_context(accounting_graph, RouteContextGroup(fired_routes=[route]))
    assert any("arithmetic_op_site" in item for item in record.included) is False  # seed itself has no direct op
    assert any(
        "transitive_arithmetic_note" in item and "_computeShareQuote" in item for item in record.included
    )


# --- build_investigation_context --------------------------------------------


def test_build_investigation_context_includes_cited_unreadable_node(restricted_graph):
    unit = UnresolvedInvestigationUnit(
        routing_unit="fn::Restricted.setValue(uint256)", unit_type="function",
        families_blocked=["P1_AUTHORIZATION"], blocked_predicates=["authorization_control_state"],
        evidence=["authorization_control_state: mod::Restricted.restricted(): modifier source unavailable"],
        status="INVESTIGATION_SELECTED",
    )
    bundle, record = build_investigation_context(restricted_graph, unit)
    assert record.family == "UNRESOLVED_INVESTIGATION"
    assert record.routing_unit == "fn::Restricted.setValue(uint256)"
    assert any("mod::Restricted.restricted()" in item for item in record.included)
    assert bundle.seed == "fn::Restricted.setValue(uint256)"
    assert "fn::Restricted.setValue(uint256)" in bundle.source_excerpts
    assert record.unresolved == unit.evidence


def test_build_investigation_context_bounded_no_expansion_beyond_cited_nodes(vault_graph):
    """A unit with NO node references in its evidence gets only its own
    source -- bounded by design, no further expansion."""
    unit = UnresolvedInvestigationUnit(
        routing_unit="fn::Vault.withdraw(uint256)", unit_type="function",
        families_blocked=["P1_AUTHORIZATION"], blocked_predicates=["authorization_control_state"],
        evidence=["authorization_control_state: resolved_state=UNRESOLVED_BY_EXTRACTION"],
        status="INVESTIGATION_SELECTED",
    )
    bundle, record = build_investigation_context(vault_graph, unit)
    assert set(bundle.source_excerpts) == {"fn::Vault.withdraw(uint256)"}
    assert any("bounded_by_design" in item for item in record.excluded)
