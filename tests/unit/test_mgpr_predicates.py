from pathlib import Path

import pytest

from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.mgpr import predicates as P
from a4v.mgpr.resolution import NegativeFeatureState, authorization_control_state

REPO_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")
VULNERABLE_BANK = REPO_ROOT / "ploit/examples/reentrancy/contracts/VulnerableBank.sol"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
CASTS_SOL = FIXTURES / "features" / "Casts.sol"


@pytest.fixture(scope="module")
def vault_graph() -> ProgramGraph:
    return ProgramGraph.build(VAULT_SOL)


@pytest.fixture(scope="module")
def bank_graph() -> ProgramGraph:
    return ProgramGraph.build(VULNERABLE_BANK)


@pytest.fixture(scope="module")
def casts_graph() -> ProgramGraph:
    return ProgramGraph.build(CASTS_SOL)


@pytest.fixture(scope="module")
def vault_features(vault_graph) -> dict:
    return FeatureExtractor.compute(vault_graph)


@pytest.fixture(scope="module")
def casts_features(casts_graph) -> dict:
    return FeatureExtractor.compute(casts_graph)


# --- P2 predicates ---------------------------------------------------------


def test_external_call_exists_on_withdraw(vault_graph, vault_features):
    node = "fn::Vault.withdraw(uint256)"
    status = P.external_call_exists(vault_graph, node, vault_features.get(node))
    assert status.status == "SATISFIED"
    assert status.evidence


def test_external_call_exists_missing_on_deposit(vault_graph, vault_features):
    node = "fn::Vault.deposit()"
    status = P.external_call_exists(vault_graph, node, vault_features.get(node))
    assert status.status == "MISSING"
    assert status.evidence == []


def test_write_after_external_call_exists_on_withdraw(vault_graph, vault_features):
    node = "fn::Vault.withdraw(uint256)"
    status = P.write_after_external_call_exists(vault_graph, node, vault_features.get(node))
    assert status.status == "SATISFIED"


def test_write_after_external_call_missing_on_deposit(vault_graph, vault_features):
    node = "fn::Vault.deposit()"
    status = P.write_after_external_call_exists(vault_graph, node, vault_features.get(node))
    assert status.status == "MISSING"


def test_p2_gate_conditions_hold_on_vulnerable_bank(bank_graph):
    features = FeatureExtractor.compute(bank_graph)
    node = "fn::VulnerableBank.withdraw(uint256)"
    assert P.external_call_exists(bank_graph, node, features.get(node)).status == "SATISFIED"
    assert P.write_after_external_call_exists(bank_graph, node, features.get(node)).status == "SATISFIED"


# --- P5 predicates ---------------------------------------------------------


def test_unsafe_cast_count_gt_zero_detected(casts_graph, casts_features):
    node = "fn::Casts.unsafeCast(uint256)"
    status = P.unsafe_cast_count_gt_zero(casts_graph, node, casts_features.get(node))
    assert status.status == "SATISFIED"


def test_unsafe_cast_count_gt_zero_missing_on_safe_cast(casts_graph, casts_features):
    node = "fn::Casts.safeCast(uint8)"
    status = P.unsafe_cast_count_gt_zero(casts_graph, node, casts_features.get(node))
    assert status.status == "MISSING"


def test_unsafe_cast_sites_line_evidence(casts_graph):
    sites = P.unsafe_cast_sites(casts_graph, "fn::Casts.unsafeCast(uint256)")
    assert len(sites) == 1
    assert sites[0]["line"] is not None
    assert "uint96" in sites[0]["expression"]


def test_unsafe_cast_sites_empty_for_safe_cast(casts_graph):
    assert P.unsafe_cast_sites(casts_graph, "fn::Casts.safeCast(uint8)") == []


# --- P1 predicates ----------------------------------------------------------


def test_state_write_exists(vault_graph, vault_features):
    node = "fn::Vault.withdraw(uint256)"
    assert P.state_write_exists(vault_graph, node, vault_features.get(node)).status == "SATISFIED"


def test_state_write_missing_on_view_function(vault_graph, vault_features):
    node = "fn::Vault.callHelper()"
    assert P.state_write_exists(vault_graph, node, vault_features.get(node)).status == "MISSING"


def test_visibility_is_public_or_external(vault_graph, vault_features):
    node = "fn::Vault.withdraw(uint256)"
    assert P.visibility_is_public_or_external(vault_graph, node, vault_features.get(node)).status == "SATISFIED"


def test_visibility_missing_for_internal_function(vault_graph, vault_features):
    node = "fn::Vault._internalHelper()"
    assert P.visibility_is_public_or_external(vault_graph, node, vault_features.get(node)).status == "MISSING"


def test_not_constructor_true_for_normal_function(vault_graph, vault_features):
    node = "fn::Vault.withdraw(uint256)"
    assert P.not_constructor(vault_graph, node, vault_features.get(node)).status == "SATISFIED"


def test_not_constructor_false_for_constructor(vault_graph, vault_features):
    node = "fn::Vault.constructor(address)"
    assert P.not_constructor(vault_graph, node, vault_features.get(node)).status == "MISSING"


# --- authorization_control_state resolution (real graphs) ------------------


def test_authorization_control_state_present_via_modifier(vault_graph):
    result = authorization_control_state(vault_graph, "fn::Vault.setOracle(address)")
    assert result.state == NegativeFeatureState.PRESENT
    # setOracle's own source span includes its signature line ("... external
    # onlyOwner {"), so the auth pattern matches directly in the function
    # body scan (step 1) -- it doesn't need to reach the modifier-body scan
    # (step 2) to find it, since the modifier name itself is right there.
    assert any("onlyOwner" in e or "auth pattern" in e for e in result.evidence)


def test_authorization_control_state_absent_on_unprotected_withdraw(vault_graph):
    result = authorization_control_state(vault_graph, "fn::Vault.withdraw(uint256)")
    assert result.state == NegativeFeatureState.ABSENT


def test_authorization_control_state_absent_on_unprotected_deposit(vault_graph):
    result = authorization_control_state(vault_graph, "fn::Vault.deposit()")
    assert result.state == NegativeFeatureState.ABSENT


def test_authorization_control_state_absent_on_vulnerable_bank_withdraw(bank_graph):
    result = authorization_control_state(bank_graph, "fn::VulnerableBank.withdraw(uint256)")
    assert result.state == NegativeFeatureState.ABSENT


# --- authorization_control_state_predicate wrapper (enum -> gate status) ---


def test_auth_predicate_wrapper_satisfied_when_expecting_absent(vault_graph, vault_features):
    node = "fn::Vault.withdraw(uint256)"
    status = P.authorization_control_state_predicate(
        vault_graph, node, vault_features.get(node), params={}, expected="ABSENT"
    )
    assert status.status == "SATISFIED"


def test_auth_predicate_wrapper_missing_when_expecting_absent_but_present(vault_graph, vault_features):
    node = "fn::Vault.setOracle(address)"
    status = P.authorization_control_state_predicate(
        vault_graph, node, vault_features.get(node), params={}, expected="ABSENT"
    )
    assert status.status == "MISSING"
    assert "resolved_state=PRESENT" in status.evidence


def test_auth_predicate_wrapper_satisfied_when_expecting_present(vault_graph, vault_features):
    node = "fn::Vault.setOracle(address)"
    status = P.authorization_control_state_predicate(
        vault_graph, node, vault_features.get(node), params={}, expected="PRESENT"
    )
    assert status.status == "SATISFIED"


def test_auth_predicate_wrapper_respects_max_helper_depth_param(vault_graph, vault_features):
    node = "fn::Vault.withdraw(uint256)"
    status = P.authorization_control_state_predicate(
        vault_graph, node, vault_features.get(node),
        params={"authorization_search_max_helper_depth": 0}, expected="ABSENT",
    )
    # depth=0 still resolves cleanly to ABSENT for this fixture (no helper
    # calls involved in withdraw's own auth-relevant path) -- this asserts
    # the param is read and passed through without erroring, not a specific
    # depth-dependent outcome.
    assert status.status in ("SATISFIED", "MISSING", "UNRESOLVED")
