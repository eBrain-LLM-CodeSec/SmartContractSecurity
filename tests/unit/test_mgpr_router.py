from pathlib import Path

import pytest

from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.mgpr import predicates as P
from a4v.mgpr.router import (
    INVESTIGATION_DEFERRED_BY_BUDGET,
    INVESTIGATION_FILTERED_NOT_ENTRYPOINT,
    INVESTIGATION_SELECTED,
    KNOWN_PREDICATES,
    Route,
    fired_routes,
    route_all,
    unresolved_investigation_units,
)
from a4v.mgpr.spec import load_routing_spec

REPO_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")
VULNERABLE_BANK = REPO_ROOT / "ploit/examples/reentrancy/contracts/VulnerableBank.sol"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
CASTS_SOL = FIXTURES / "features" / "Casts.sol"
RESTRICTED_SOL = FIXTURES / "modifier_source" / "Restricted.sol"
ROUTING_SPEC = Path(__file__).resolve().parents[2] / "routing_spec.yaml"


@pytest.fixture(scope="module")
def spec():
    return load_routing_spec(ROUTING_SPEC, known_predicates=KNOWN_PREDICATES)


@pytest.fixture(scope="module")
def vault_graph():
    return ProgramGraph.build(VAULT_SOL)


@pytest.fixture(scope="module")
def vault_features(vault_graph):
    return FeatureExtractor.compute(vault_graph)


@pytest.fixture(scope="module")
def bank_graph():
    return ProgramGraph.build(VULNERABLE_BANK)


@pytest.fixture(scope="module")
def casts_graph():
    return ProgramGraph.build(CASTS_SOL)


def _route(routes, node_id, family, gate):
    matches = [r for r in routes if r.routing_unit == node_id and r.family == family and r.gate == gate]
    assert len(matches) == 1, f"expected exactly one route for {node_id}/{family}/{gate}, got {len(matches)}"
    return matches[0]


def test_routing_spec_loads_against_router_predicate_registry(spec):
    # this is the load-time cross-check itself: load_routing_spec raises if
    # any gate references a predicate name router.py doesn't know about.
    assert spec.specified_families()


def test_p2_fires_on_reentrant_withdraw_vault(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    r = _route(routes, "fn::Vault.withdraw(uint256)", "P2_REENTRANCY", "P2_CALL_BEFORE_WRITE")
    assert r.route_would_fire is True
    assert r.reason == "all 'all:' predicates SATISFIED"
    assert r.unresolved_or_missing == []


def test_p2_does_not_fire_on_safe_deposit_vault(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    r = _route(routes, "fn::Vault.deposit()", "P2_REENTRANCY", "P2_CALL_BEFORE_WRITE")
    assert r.route_would_fire is False
    assert "external_call_exists" in r.reason


def test_p2_fires_on_vulnerable_bank_withdraw(bank_graph, spec):
    features = FeatureExtractor.compute(bank_graph)
    routes = route_all(bank_graph, features, spec)
    r = _route(routes, "fn::VulnerableBank.withdraw(uint256)", "P2_REENTRANCY", "P2_CALL_BEFORE_WRITE")
    assert r.route_would_fire is True


def test_p5_fires_on_unsafe_cast(casts_graph, spec):
    features = FeatureExtractor.compute(casts_graph)
    routes = route_all(casts_graph, features, spec)
    r = _route(routes, "fn::Casts.unsafeCast(uint256)", "P5_ARITHMETIC_PRECISION", "P5_NARROWING_CAST")
    assert r.route_would_fire is True


def test_p5_does_not_fire_on_safe_cast(casts_graph, spec):
    features = FeatureExtractor.compute(casts_graph)
    routes = route_all(casts_graph, features, spec)
    r = _route(routes, "fn::Casts.safeCast(uint8)", "P5_ARITHMETIC_PRECISION", "P5_NARROWING_CAST")
    assert r.route_would_fire is False


def test_p1_fires_on_unprotected_state_writers(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    for node in ("fn::Vault.withdraw(uint256)", "fn::Vault.deposit()"):
        r = _route(routes, node, "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR")
        assert r.route_would_fire is True, f"{node}: {r.reason}"


def test_p1_does_not_fire_on_protected_set_oracle(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    r = _route(routes, "fn::Vault.setOracle(address)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR")
    assert r.route_would_fire is False
    assert "authorization_control_state" in r.reason


def test_p1_does_not_fire_on_constructor(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    r = _route(routes, "fn::Vault.constructor(address)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR")
    assert r.route_would_fire is False
    assert "not_constructor" in r.reason


def test_p1_does_not_fire_on_view_function_no_state_write(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    r = _route(routes, "fn::Vault.callHelper()", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR")
    assert r.route_would_fire is False
    assert "state_write_exists" in r.reason


def test_p1_does_not_fire_on_internal_function(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    r = _route(routes, "fn::Vault._internalHelper()", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR")
    assert r.route_would_fire is False
    assert "visibility_is_public_or_external" in r.reason


def test_multi_label_withdraw_fires_both_p1_and_p2(vault_graph, vault_features, spec):
    """A single routing unit can produce multiple fired routes -- no
    unit-level 'winner' (plan section 6.1). withdraw() also legitimately
    fires P5_ARITHMETIC_PRECISION under Gap B's broadened accounting/
    arithmetic gates (it has accounting-vocabulary identifiers -- "price",
    "amount", "shares", "totalShares", plus its own name -- direct
    multiplication, an external call, and a numeric parameter) -- multi-
    label routing across three families, not just two."""
    routes = route_all(vault_graph, vault_features, spec)
    fired = fired_routes(routes)
    withdraw_families = {r.family for r in fired if r.routing_unit == "fn::Vault.withdraw(uint256)"}
    assert withdraw_families == {"P1_AUTHORIZATION", "P2_REENTRANCY", "P5_ARITHMETIC_PRECISION"}


def test_external_stub_nodes_are_never_routing_units(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    stub_routes = [r for r in routes if r.routing_unit.startswith("ext::")]
    assert stub_routes == []


def test_route_all_is_deterministic(vault_graph, vault_features, spec):
    routes_1 = route_all(vault_graph, vault_features, spec)
    routes_2 = route_all(vault_graph, vault_features, spec)
    key = lambda r: (r.routing_unit, r.family, r.gate, r.route_would_fire, r.reason)
    assert sorted(map(key, routes_1)) == sorted(map(key, routes_2))


def test_route_all_returns_both_fired_and_not_fired(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    assert any(r.route_would_fire for r in routes)
    assert any(not r.route_would_fire for r in routes)


# --- Gap C, Workstream 2: decision_blocking_unresolved ----------------------


@pytest.fixture(scope="module")
def restricted_graph():
    return ProgramGraph.build(RESTRICTED_SOL)


def test_decision_blocking_unresolved_true_when_unresolved_is_the_only_blocker(restricted_graph, spec):
    """setValue is public/external, writes state, not a constructor -- every
    OTHER P1 predicate already resolves SATISFIED. Forcing the modifier
    scan UNRESOLVED (by stripping the modifier node's `file` attribute, the
    exact pre-fix bug) makes `authorization_control_state` the ONLY thing
    standing between this route and firing."""
    from a4v.mgpr.router import evaluate_gate
    pg = restricted_graph
    pg.graph.nodes["mod::Restricted.restricted()"]["file"] = None
    features = FeatureExtractor.compute(pg)
    p1 = spec.families["P1_AUTHORIZATION"]
    node = "fn::Restricted.setValue(uint256)"
    route = evaluate_gate(pg, node, features.get(node), p1, p1.gates[0])
    assert route.route_would_fire is False
    assert any(s.status == "UNRESOLVED" for s in route.predicates)
    assert route.decision_blocking_unresolved is True
    # restore for other tests sharing the module-scoped fixture
    pg.graph.nodes["mod::Restricted.restricted()"]["file"] = str(RESTRICTED_SOL)


def test_decision_blocking_unresolved_false_when_another_predicate_already_missing(restricted_graph, spec):
    """viewOnly has NO state write -- state_write_exists is definitively
    MISSING regardless of what the (separately forced UNRESOLVED) auth scan
    finds. The gate was already going to fail on MISSING -- this is noise,
    not "we lost information here", and must NOT be decision-blocking."""
    from a4v.mgpr.router import evaluate_gate
    pg = restricted_graph
    pg.graph.nodes["mod::Restricted.restricted()"]["file"] = None
    features = FeatureExtractor.compute(pg)
    p1 = spec.families["P1_AUTHORIZATION"]
    node = "fn::Restricted.viewOnly()"
    route = evaluate_gate(pg, node, features.get(node), p1, p1.gates[0])
    assert route.route_would_fire is False
    assert any(s.status == "UNRESOLVED" for s in route.predicates)
    assert any(s.status == "MISSING" for s in route.predicates)
    assert route.decision_blocking_unresolved is False
    pg.graph.nodes["mod::Restricted.restricted()"]["file"] = str(RESTRICTED_SOL)


def test_decision_blocking_unresolved_false_when_gate_fires_cleanly(vault_graph, vault_features, spec):
    routes = route_all(vault_graph, vault_features, spec)
    r = _route(routes, "fn::Vault.withdraw(uint256)", "P2_REENTRANCY", "P2_CALL_BEFORE_WRITE")
    assert r.route_would_fire is True
    assert r.decision_blocking_unresolved is False


def test_spec_dsl_is_all_only_today():
    """Documents the constraint decision_blocking_unresolved's formula
    depends on: routing_spec.yaml's gate DSL supports only flat `all:`
    (conjunction), no `any`/`not`. Load-bearing, not incidental -- if this
    ever changes, the formula in router.py needs to change with it."""
    from a4v.mgpr.spec import SpecError, _parse_predicate
    with pytest.raises(SpecError):
        _parse_predicate({"any": ["external_call_exists"]}, "FAKE_FAMILY", "FAKE_GATE")


# --- Gap C, Workstream 2: unresolved_investigation_units --------------------


def _fake_status(predicate: str, status: str, evidence=None) -> P.PredicateStatus:
    return P.PredicateStatus(predicate=predicate, status=status, evidence=evidence or [])


def _fake_route(routing_unit, family, gate, predicates, fires, decision_blocking) -> Route:
    return Route(
        routing_unit=routing_unit, unit_type="function", family=family, gate=gate,
        predicates=predicates, route_would_fire=fires, reason="test", prompt_id=f"{family}_v1",
        decision_blocking_unresolved=decision_blocking,
    )


def test_unresolved_investigation_units_creates_entry_for_decision_blocking_route(vault_graph):
    routes = [
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
            [_fake_status("authorization_control_state", "UNRESOLVED", ["mod::X: modifier source unavailable"])],
            fires=False, decision_blocking=True,
        ),
    ]
    units = unresolved_investigation_units(vault_graph, routes)
    assert len(units) == 1
    unit = units[0]
    assert unit.routing_unit == "fn::Vault.withdraw(uint256)"
    assert unit.families_blocked == ["P1_AUTHORIZATION"]
    assert unit.blocked_predicates == ["authorization_control_state"]
    assert unit.status == INVESTIGATION_SELECTED


def test_unresolved_investigation_units_not_decision_blocking_produces_no_entry(vault_graph):
    routes = [
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
            [_fake_status("authorization_control_state", "UNRESOLVED"),
             _fake_status("state_write_exists", "MISSING")],
            fires=False, decision_blocking=False,
        ),
    ]
    assert unresolved_investigation_units(vault_graph, routes) == []


def test_unresolved_investigation_units_same_family_two_gates_collapse_into_one_entry(vault_graph):
    """Two decision-blocking-unresolved gates within the SAME family for the
    same unit must collapse into ONE investigation entry, not two."""
    routes = [
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "GATE_A",
            [_fake_status("pred_a", "UNRESOLVED", ["note a"])], fires=False, decision_blocking=True,
        ),
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "GATE_B",
            [_fake_status("pred_b", "UNRESOLVED", ["note b"])], fires=False, decision_blocking=True,
        ),
    ]
    units = unresolved_investigation_units(vault_graph, routes)
    assert len(units) == 1
    assert units[0].families_blocked == ["P1_AUTHORIZATION"]
    assert set(units[0].blocked_predicates) == {"pred_a", "pred_b"}


def test_unresolved_investigation_units_different_family_gets_its_own_entry(vault_graph):
    """A decision-blocking-unresolved gate in a family with NO fired route
    still gets its own entry even when a DIFFERENT family has one -- this is
    NOT the same-family redundancy skip."""
    routes = [
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P2_REENTRANCY", "P2_CALL_BEFORE_WRITE",
            [_fake_status("external_call_exists", "SATISFIED"),
             _fake_status("write_after_external_call_exists", "SATISFIED")],
            fires=True, decision_blocking=False,
        ),
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
            [_fake_status("authorization_control_state", "UNRESOLVED")], fires=False, decision_blocking=True,
        ),
    ]
    units = unresolved_investigation_units(vault_graph, routes)
    assert len(units) == 1
    assert units[0].families_blocked == ["P1_AUTHORIZATION"]


def test_unresolved_investigation_units_same_family_redundancy_skip_when_already_fired(vault_graph):
    """A decision-blocking-unresolved gate in the SAME family as a normal
    fired route for the same unit must be SKIPPED entirely -- the fired
    route's context already carries the unresolved evidence alongside it
    (RouteContextGroup.unresolved_routes), so a second investigation call
    would just duplicate that analysis."""
    routes = [
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "GATE_A",
            [_fake_status("pred_a", "SATISFIED")], fires=True, decision_blocking=False,
        ),
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "GATE_B",
            [_fake_status("pred_b", "UNRESOLVED")], fires=False, decision_blocking=True,
        ),
    ]
    assert unresolved_investigation_units(vault_graph, routes) == []


def test_unresolved_investigation_units_filters_non_entrypoint(vault_graph):
    """An internal function fails the visibility pre-filter ->
    INVESTIGATION_FILTERED_NOT_ENTRYPOINT, not silently dropped and not
    selected for a Commentator call."""
    routes = [
        _fake_route(
            "fn::Vault._internalHelper()", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
            [_fake_status("authorization_control_state", "UNRESOLVED")], fires=False, decision_blocking=True,
        ),
    ]
    units = unresolved_investigation_units(vault_graph, routes)
    assert len(units) == 1
    assert units[0].status == INVESTIGATION_FILTERED_NOT_ENTRYPOINT


def test_unresolved_investigation_units_cap_selects_by_composite_priority_deterministically(vault_graph):
    """Over-budget eligible units -> exactly `max_per_audit` are
    INVESTIGATION_SELECTED, the rest INVESTIGATION_DEFERRED_BY_BUDGET --
    never silently dropped, and selection is deterministic. withdraw() has
    a state write + external call + accounting-vocabulary identifiers (all
    three composite-priority signals) so it must win the cap over deposit()
    (state write + accounting vocabulary, no external call)."""
    routes = [
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
            [_fake_status("authorization_control_state", "UNRESOLVED")], fires=False, decision_blocking=True,
        ),
        _fake_route(
            "fn::Vault.deposit()", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
            [_fake_status("authorization_control_state", "UNRESOLVED")], fires=False, decision_blocking=True,
        ),
    ]
    units = unresolved_investigation_units(vault_graph, routes, max_per_audit=1)
    selected = [u for u in units if u.status == INVESTIGATION_SELECTED]
    deferred = [u for u in units if u.status == INVESTIGATION_DEFERRED_BY_BUDGET]
    assert len(units) == 2  # both still present, never dropped
    assert len(selected) == 1
    assert len(deferred) == 1
    assert selected[0].routing_unit == "fn::Vault.withdraw(uint256)"
    assert deferred[0].routing_unit == "fn::Vault.deposit()"
    assert deferred[0].evidence  # not silently emptied


def test_unresolved_investigation_units_deterministic_across_runs(vault_graph):
    routes = [
        _fake_route(
            "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
            [_fake_status("authorization_control_state", "UNRESOLVED")], fires=False, decision_blocking=True,
        ),
        _fake_route(
            "fn::Vault.deposit()", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
            [_fake_status("authorization_control_state", "UNRESOLVED")], fires=False, decision_blocking=True,
        ),
    ]
    units_1 = unresolved_investigation_units(vault_graph, routes)
    units_2 = unresolved_investigation_units(vault_graph, routes)
    key = lambda units: [(u.routing_unit, u.status) for u in units]
    assert key(units_1) == key(units_2)
