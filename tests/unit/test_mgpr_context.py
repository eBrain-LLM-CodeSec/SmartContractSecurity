from pathlib import Path

import pytest

from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.mgpr.context import build_context
from a4v.mgpr.router import route_all
from a4v.mgpr.spec import load_routing_spec

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
CASTS_SOL = FIXTURES / "features" / "Casts.sol"
ROUTING_SPEC = Path(__file__).resolve().parents[2] / "routing_spec.yaml"


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

    bundle, record = build_context(vault_graph, route)
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
    bundle, record = build_context(vault_graph, route)
    assert bundle.seed == "fn::Vault.withdraw(uint256)"
    assert "fn::Vault.withdraw(uint256)" in bundle.source_excerpts
    assert "fn::Vault.deposit()" in bundle.source_excerpts


def test_p5_context_includes_cast_site_and_stops_at_function_scope(casts_graph):
    features = FeatureExtractor.compute(casts_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(casts_graph, features, spec)
    route = _find_route(routes, "fn::Casts.unsafeCast(uint256)", "P5_ARITHMETIC_PRECISION", "P5_NARROWING_CAST")
    assert route.route_would_fire

    bundle, record = build_context(casts_graph, route)
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

    bundle, record = build_context(vault_graph, route)
    assert any("applied_modifier" in item and "onlyOwner" in item for item in record.included)
    assert bundle.modifiers  # onlyOwner shows up in the bundle's typed modifiers field too


def test_p1_context_on_fired_withdraw(vault_graph):
    features = FeatureExtractor.compute(vault_graph)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(vault_graph, features, spec)
    route = _find_route(routes, "fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION", "P1_STATE_CHANGE_NO_AUTH_DOMINATOR")
    assert route.route_would_fire is True

    bundle, record = build_context(vault_graph, route)
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
        build_context(vault_graph, fake_route)
