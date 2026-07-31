from pathlib import Path

import pytest

from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.mgpr.router import KNOWN_PREDICATES, fired_routes, route_all
from a4v.mgpr.spec import load_routing_spec

REPO_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")
VULNERABLE_BANK = REPO_ROOT / "ploit/examples/reentrancy/contracts/VulnerableBank.sol"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
CASTS_SOL = FIXTURES / "features" / "Casts.sol"
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
    unit-level 'winner' (plan section 6.1)."""
    routes = route_all(vault_graph, vault_features, spec)
    fired = fired_routes(routes)
    withdraw_families = {r.family for r in fired if r.routing_unit == "fn::Vault.withdraw(uint256)"}
    assert withdraw_families == {"P1_AUTHORIZATION", "P2_REENTRANCY"}


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
