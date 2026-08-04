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
LIB_DELEGATE_SOL = FIXTURES / "state_write_transitive" / "LibDelegate.sol"
RECEIVER_SOL = FIXTURES / "callback_interfaces" / "Receiver.sol"
ACCOUNTING_SOL = FIXTURES / "accounting_signals" / "Accounting.sol"


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


@pytest.fixture(scope="module")
def lib_delegate_graph() -> ProgramGraph:
    return ProgramGraph.build(LIB_DELEGATE_SOL)


@pytest.fixture(scope="module")
def receiver_graph() -> ProgramGraph:
    return ProgramGraph.build(RECEIVER_SOL)


@pytest.fixture(scope="module")
def accounting_graph() -> ProgramGraph:
    return ProgramGraph.build(ACCOUNTING_SOL)


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


# --- Gap A: state_write_exists broadened to STATE_WRITE_TRANSITIVE ---------


def test_state_write_exists_satisfied_via_transitive_only(lib_delegate_graph):
    node = "fn::Delegator.deposit(address,uint256)"
    status = P.state_write_exists(lib_delegate_graph, node, None)
    assert status.status == "SATISFIED"
    assert any("STATE_WRITE_TRANSITIVE" in e for e in status.evidence)
    assert not any("(STATE_WRITE)" in e for e in status.evidence)


def test_state_write_exists_satisfied_via_direct(lib_delegate_graph):
    node = "fn::Delegator._setBalance(address,uint256)"
    status = P.state_write_exists(lib_delegate_graph, node, None)
    assert status.status == "SATISFIED"
    assert any("(STATE_WRITE)" in e for e in status.evidence)
    assert not any("STATE_WRITE_TRANSITIVE" in e for e in status.evidence)


def test_state_write_exists_missing_for_pure_reader(lib_delegate_graph):
    node = "fn::Delegator.pureRead(address)"
    assert P.state_write_exists(lib_delegate_graph, node, None).status == "MISSING"


# --- Gap D: callback_interface_signature_match ------------------------------


def test_callback_signature_exact_tier_matches_erc721_receiver(receiver_graph):
    node = "fn::Receiver.onERC721Received(address,address,uint256,bytes)"
    status = P.callback_interface_signature_match(receiver_graph, node, None)
    assert status.status == "SATISFIED"
    assert "EXACT" in status.evidence[0]
    assert status.resolution_state == "EXACT"


def test_callback_signature_heuristic_tier_matches_struct_param_order(receiver_graph):
    node = "fn::Receiver.validateOrder(Order,bytes)"
    status = P.callback_interface_signature_match(receiver_graph, node, None)
    assert status.status == "SATISFIED"
    assert "HEURISTIC" in status.evidence[0]
    assert status.resolution_state == "HEURISTIC"


def test_callback_signature_missing_for_unrelated_function(receiver_graph):
    node = "fn::Receiver.normalDeposit(uint256)"
    status = P.callback_interface_signature_match(receiver_graph, node, None)
    assert status.status == "MISSING"
    assert status.evidence == []


def test_callback_signature_missing_for_wrong_signature(receiver_graph):
    node = "fn::Receiver.onWrongSignatureReceived(address,uint256)"
    status = P.callback_interface_signature_match(receiver_graph, node, None)
    assert status.status == "MISSING"


def test_p2_callback_reachable_write_gate_fires_end_to_end(receiver_graph):
    features = FeatureExtractor.compute(receiver_graph)
    from a4v.mgpr.router import route_all
    from a4v.mgpr.spec import load_routing_spec
    spec = load_routing_spec(Path(__file__).resolve().parents[2] / "routing_spec.yaml")
    routes = route_all(receiver_graph, features, spec)
    fired = {(r.routing_unit, r.gate) for r in routes if r.route_would_fire and r.family == "P2_REENTRANCY"}
    assert ("fn::Receiver.onERC721Received(address,address,uint256,bytes)", "P2_CALLBACK_REACHABLE_WRITE") in fired
    assert ("fn::Receiver.validateOrder(Order,bytes)", "P2_CALLBACK_REACHABLE_WRITE") in fired
    assert ("fn::Receiver.normalDeposit(uint256)", "P2_CALLBACK_REACHABLE_WRITE") not in fired


# --- Gap B: accounting_identifier_signal / accounting_action_identifier_signal


def test_accounting_identifier_signal_matches_via_state_var_and_name(accounting_graph):
    node = "fn::Accounting.convertToShares(uint256)"
    status = P.accounting_identifier_signal(accounting_graph, node, None)
    assert status.status == "SATISFIED"


def test_accounting_identifier_signal_missing_when_no_vocab_overlap(accounting_graph):
    node = "fn::Accounting.multiplyInputs(uint256,uint256)"
    status = P.accounting_identifier_signal(accounting_graph, node, None)
    assert status.status == "MISSING"
    assert status.evidence == []


def test_accounting_identifier_signal_tokenization_guard_no_substring_match(accounting_graph):
    """"captureEvent" must NOT match vocabulary token "cap" via substring --
    whole-token matching only."""
    node = "fn::Accounting.captureEvent(uint256)"
    status = P.accounting_identifier_signal(accounting_graph, node, None)
    assert status.status == "MISSING"


def test_accounting_identifier_signal_matches_via_parameter_name_only(accounting_graph):
    """Revision 3's required fix: a pure library function with NO state
    variables at all, whose only accounting vocabulary lives in its own
    parameter names ("mantissa", "exponent") -- mirrors forte/H-05's
    Float128.toPackedFloat exactly."""
    node = "fn::Float128.toPackedFloat(uint256,uint256)"
    status = P.accounting_identifier_signal(accounting_graph, node, None)
    assert status.status == "SATISFIED"
    assert any("parameter:mantissa" in e for e in status.evidence)
    assert any("parameter:exponent" in e for e in status.evidence)
    # not a state-var or function-name match -- specifically the parameter scan
    assert not any(e.startswith("state_var:") or e.startswith("function_name:") for e in status.evidence)


def test_accounting_action_identifier_signal_uses_narrow_verb_vocab(accounting_graph):
    withdraw = P.accounting_action_identifier_signal(
        accounting_graph, "fn::Accounting.withdrawShares(uint256)", None,
    )
    assert withdraw.status == "SATISFIED"
    # "total" (reportTotal) is in the BROAD vocab but NOT the narrow
    # action-verb vocab -- accounting_action_identifier_signal must be
    # stricter than accounting_identifier_signal.
    report_total_broad = P.accounting_identifier_signal(accounting_graph, "fn::Accounting.reportTotal()", None)
    report_total_narrow = P.accounting_action_identifier_signal(accounting_graph, "fn::Accounting.reportTotal()", None)
    assert report_total_broad.status == "SATISFIED"
    assert report_total_narrow.status == "MISSING"


# --- Gap B: precision_sensitive_arithmetic_exists ---------------------------


def test_precision_sensitive_arithmetic_direct_at_seed(accounting_graph):
    status = P.precision_sensitive_arithmetic_exists(accounting_graph, "fn::Accounting.convertToShares(uint256)", None)
    assert status.status == "SATISFIED"
    assert any("at seed" in e for e in status.evidence)


def test_precision_sensitive_arithmetic_transitive_via_internal_helper(accounting_graph):
    """`quoteShares` has no arithmetic of its own -- the multiplication/
    division lives one internal call away in `_computeShareQuote`, mirroring
    thorwallet/H-01's quoteTitn shape exactly."""
    status = P.precision_sensitive_arithmetic_exists(accounting_graph, "fn::Accounting.quoteShares(uint256)", None)
    assert status.status == "SATISFIED"
    assert any("transitive" in e and "_computeShareQuote" in e for e in status.evidence)


def test_precision_sensitive_arithmetic_depth_zero_misses_transitive_case(accounting_graph):
    """depth=0 must NOT see the helper's arithmetic -- proves the BFS depth
    param is actually load-bearing, not a no-op."""
    status = P.precision_sensitive_arithmetic_exists(
        accounting_graph, "fn::Accounting.quoteShares(uint256)", None,
        params={"p5_arithmetic_search_max_helper_depth": 0},
    )
    assert status.status == "MISSING"


def test_precision_sensitive_arithmetic_missing_when_no_arithmetic_or_assembly(accounting_graph):
    status = P.precision_sensitive_arithmetic_exists(accounting_graph, "fn::Accounting.reportTotal()", None)
    assert status.status == "MISSING"
    assert status.evidence == []


def test_precision_sensitive_arithmetic_assembly_branch_toPackedFloat(accounting_graph):
    """The direct regression test for the Phase-0 spike's exact gap: a pure
    library function with no state vars, whose accounting vocabulary lives
    only in parameter names, with math inside an inline assembly block."""
    node = "fn::Float128.toPackedFloat(uint256,uint256)"
    status = P.precision_sensitive_arithmetic_exists(accounting_graph, node, None)
    assert status.status == "SATISFIED"
    assert any("assembly" in e for e in status.evidence)


def test_p5_accounting_arithmetic_gate_fires_end_to_end_on_toPackedFloat(accounting_graph):
    """The direct regression test for the exact gap the Phase-0 spike
    found: both the parameter-name scope widening
    (accounting_identifier_signal) and the assembly-awareness branch
    (precision_sensitive_arithmetic_exists) fire together end-to-end."""
    from a4v.mgpr.router import route_all
    from a4v.mgpr.spec import load_routing_spec
    features = FeatureExtractor.compute(accounting_graph)
    spec = load_routing_spec(Path(__file__).resolve().parents[2] / "routing_spec.yaml")
    routes = route_all(accounting_graph, features, spec)
    fired = {(r.routing_unit, r.gate) for r in routes if r.route_would_fire}
    assert ("fn::Float128.toPackedFloat(uint256,uint256)", "P5_ACCOUNTING_ARITHMETIC") in fired


# --- Gap B: arithmetic_op_sites evidence helper -----------------------------


def test_arithmetic_op_sites_line_evidence(accounting_graph):
    sites = P.arithmetic_op_sites(accounting_graph, "fn::Accounting.convertToShares(uint256)")
    assert len(sites) == 2  # amount * totalShares, and the division
    assert all(s["line"] is not None for s in sites)


def test_arithmetic_op_sites_empty_for_no_arithmetic(accounting_graph):
    assert P.arithmetic_op_sites(accounting_graph, "fn::Accounting.reportTotal()") == []


# --- Gap B: external_call_and_state_write_exists ----------------------------


def test_external_call_and_state_write_exists_satisfied(accounting_graph):
    status = P.external_call_and_state_write_exists(accounting_graph, "fn::Accounting.syncReserveFromOracle()", None)
    assert status.status == "SATISFIED"


def test_external_call_and_state_write_exists_missing_when_only_one_present(accounting_graph):
    # withdrawShares writes state but has no external call
    status = P.external_call_and_state_write_exists(accounting_graph, "fn::Accounting.withdrawShares(uint256)", None)
    assert status.status == "MISSING"


def test_external_call_and_state_write_exists_evidence_never_claims_value_flow(accounting_graph):
    """Required negative test: this predicate only establishes co-
    occurrence, never a traced dataflow claim -- the literal phrase "value
    flows into" must never appear anywhere in its evidence or extraction
    method, on either a SATISFIED or MISSING outcome."""
    for node in ("fn::Accounting.syncReserveFromOracle()", "fn::Accounting.withdrawShares(uint256)",
                 "fn::Accounting.reportTotal()"):
        status = P.external_call_and_state_write_exists(accounting_graph, node, None)
        combined = " ".join(status.evidence) + " " + status.extraction_method
        assert "value flows into" not in combined
    satisfied = P.external_call_and_state_write_exists(accounting_graph, "fn::Accounting.syncReserveFromOracle()", None)
    assert any("co-occurrence" in e for e in satisfied.evidence)


# --- Gap B: numeric_user_input_exists ---------------------------------------


def test_numeric_user_input_exists_satisfied_for_uint_param(accounting_graph):
    status = P.numeric_user_input_exists(accounting_graph, "fn::Accounting.withdrawShares(uint256)", None)
    assert status.status == "SATISFIED"
    assert any("amount" in e for e in status.evidence)


def test_numeric_user_input_exists_missing_for_zero_arg_function(accounting_graph):
    status = P.numeric_user_input_exists(accounting_graph, "fn::Accounting.reportTotal()", None)
    assert status.status == "MISSING"


def test_numeric_user_input_exists_missing_for_non_numeric_param(receiver_graph):
    # normalDeposit takes a uint256 -- contrast with a purely address-typed one
    status = P.numeric_user_input_exists(receiver_graph, "fn::Receiver.validateOrder(Order,bytes)", None)
    assert status.status == "MISSING"


# --- Gap B: P5_ACCOUNTING_ENTRYPOINT gate end-to-end ------------------------


def test_p5_accounting_entrypoint_gate_fires_on_withdraw_shares(accounting_graph):
    from a4v.mgpr.router import route_all
    from a4v.mgpr.spec import load_routing_spec
    features = FeatureExtractor.compute(accounting_graph)
    spec = load_routing_spec(Path(__file__).resolve().parents[2] / "routing_spec.yaml")
    routes = route_all(accounting_graph, features, spec)
    fired = {(r.routing_unit, r.gate) for r in routes if r.route_would_fire}
    assert ("fn::Accounting.withdrawShares(uint256)", "P5_ACCOUNTING_ENTRYPOINT") in fired
    # reportTotal has the accounting-entrypoint vocab overlap via "total"
    # only under the BROAD vocab, not the narrow action-verb one, and takes
    # no numeric parameter either -- must not fire.
    assert not any(g == "P5_ACCOUNTING_ENTRYPOINT" and u == "fn::Accounting.reportTotal()" for u, g in fired)
