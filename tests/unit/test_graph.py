"""Phase 1: assert the program graph has the expected typed nodes/edges on
two fixtures -- VulnerableBank.sol (single-file reentrancy) and Vault.sol
(multi-contract: inheritance, modifier, external interface call).
"""
from pathlib import Path

import pytest

from a4v.graph import (
    ProgramGraph,
    CONTRACT, FUNCTION, MODIFIER, STATEVAR,
    CALLS, DECLARES, INHERITS, USES_MODIFIER, STATE_READ, STATE_WRITE, STATE_WRITE_TRANSITIVE,
    EXTERNAL_CALL, WRITE_AFTER_EXTERNAL_CALL,
)

REPO_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")
VULNERABLE_BANK = REPO_ROOT / "ploit/examples/reentrancy/contracts/VulnerableBank.sol"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
LIB_DELEGATE_SOL = FIXTURES / "state_write_transitive" / "LibDelegate.sol"
RESTRICTED_SOL = FIXTURES / "modifier_source" / "Restricted.sol"
AUTH_ADMIN_SOL = FIXTURES / "inherited_function" / "AuthAdmin.sol"


@pytest.fixture(scope="module")
def bank_graph() -> ProgramGraph:
    return ProgramGraph.build(VULNERABLE_BANK)


@pytest.fixture(scope="module")
def vault_graph() -> ProgramGraph:
    return ProgramGraph.build(VAULT_SOL)


def test_vulnerable_bank_has_external_call_and_write_after_call(bank_graph):
    withdraw = "fn::VulnerableBank.withdraw(uint256)"
    assert withdraw in bank_graph.graph.nodes
    external_targets = bank_graph.neighbors_by_kind(withdraw, EXTERNAL_CALL)
    assert external_targets, "expected withdraw() to have an external-call edge (the low-level .call)"

    write_after = bank_graph.neighbors_by_kind(withdraw, WRITE_AFTER_EXTERNAL_CALL)
    written_names = {bank_graph.graph.nodes[n]["name"] for n in write_after}
    assert "balances" in written_names
    assert "totalDeposits" in written_names


def test_vault_inheritance_edge(vault_graph):
    assert ("contract::Vault", "contract::Ownable") in vault_graph.edges_of_kind(INHERITS)


def test_vault_modifier_usage_edge(vault_graph):
    set_oracle = "fn::Vault.setOracle(address)"
    modifiers = vault_graph.neighbors_by_kind(set_oracle, USES_MODIFIER)
    assert any("onlyOwner" in m for m in modifiers)


def test_vault_external_call_edge_to_oracle(vault_graph):
    withdraw = "fn::Vault.withdraw(uint256)"
    external_targets = vault_graph.neighbors_by_kind(withdraw, EXTERNAL_CALL)
    assert any("getPrice" in t for t in external_targets)
    assert any(t == "ext::<low-level-call>" for t in external_targets)


def test_vault_write_after_external_call(vault_graph):
    withdraw = "fn::Vault.withdraw(uint256)"
    write_after = vault_graph.neighbors_by_kind(withdraw, WRITE_AFTER_EXTERNAL_CALL)
    names = {vault_graph.graph.nodes[n]["name"] for n in write_after}
    assert {"shares", "totalShares"} <= names


def test_vault_internal_call_edge_not_modifier(vault_graph):
    call_helper = "fn::Vault.callHelper()"
    callees = vault_graph.neighbors_by_kind(call_helper, CALLS)
    assert any("_internalHelper" in c for c in callees)
    # the modifier internal-call must not leak into CALLS (covered by USES_MODIFIER instead)
    set_oracle_callees = vault_graph.neighbors_by_kind("fn::Vault.setOracle(address)", CALLS)
    assert not any(vault_graph.graph.nodes[c].get("kind") == MODIFIER for c in set_oracle_callees)


def test_seed_one_hop_bundle_contains_callee_and_touched_state(vault_graph):
    """A seed's 1-hop bundle must contain its callee + touched state vars
    (plan Phase-1 pass criterion)."""
    withdraw = "fn::Vault.withdraw(uint256)"
    bundle = vault_graph.expand(withdraw, hops=1)
    assert any("getPrice" in n for n in bundle)  # callee (external)
    assert "var::Vault.shares" in bundle
    assert "var::Vault.totalShares" in bundle
    assert "var::Vault.oracle" in bundle


@pytest.fixture(scope="module")
def lib_delegate_graph() -> ProgramGraph:
    return ProgramGraph.build(LIB_DELEGATE_SOL)


@pytest.fixture(scope="module")
def restricted_graph() -> ProgramGraph:
    return ProgramGraph.build(RESTRICTED_SOL)


# --- Gap A: STATE_WRITE_TRANSITIVE -----------------------------------------


def test_state_write_transitive_edge_for_internal_call_delegated_write(lib_delegate_graph):
    """`deposit` never directly writes `balances` -- the write happens
    entirely inside `_setBalance`, one internal call away. STATE_WRITE_TRANSITIVE
    must carry it; STATE_WRITE (direct) must NOT."""
    deposit = "fn::Delegator.deposit(address,uint256)"
    assert lib_delegate_graph.neighbors_by_kind(deposit, STATE_WRITE) == []
    transitive = lib_delegate_graph.neighbors_by_kind(deposit, STATE_WRITE_TRANSITIVE)
    assert transitive == ["var::Delegator.balances"]


def test_state_write_transitive_disjoint_from_state_write(lib_delegate_graph):
    """`_setBalance` writes `balances` DIRECTLY -- it must appear under
    STATE_WRITE, never duplicated under STATE_WRITE_TRANSITIVE for the same
    function/var pair (the two edge kinds are disjoint by construction)."""
    set_balance = "fn::Delegator._setBalance(address,uint256)"
    assert lib_delegate_graph.neighbors_by_kind(set_balance, STATE_WRITE) == ["var::Delegator.balances"]
    assert lib_delegate_graph.neighbors_by_kind(set_balance, STATE_WRITE_TRANSITIVE) == []


def test_state_write_transitive_empty_for_direct_only_writer(lib_delegate_graph):
    """`bumpDirect` writes `directCounter` directly -- STATE_WRITE_TRANSITIVE
    must be empty for it (nothing written only-transitively)."""
    bump = "fn::Delegator.bumpDirect()"
    assert lib_delegate_graph.neighbors_by_kind(bump, STATE_WRITE) == ["var::Delegator.directCounter"]
    assert lib_delegate_graph.neighbors_by_kind(bump, STATE_WRITE_TRANSITIVE) == []


def test_state_write_transitive_empty_for_pure_reader(lib_delegate_graph):
    read = "fn::Delegator.pureRead(address)"
    assert lib_delegate_graph.neighbors_by_kind(read, STATE_WRITE) == []
    assert lib_delegate_graph.neighbors_by_kind(read, STATE_WRITE_TRANSITIVE) == []


# --- Gap C, Workstream 1: MODIFIER node `file` attribute -------------------


def test_modifier_nodes_carry_file_attribute(vault_graph):
    """Every MODIFIER node built by graph.py must carry a `file` attribute,
    exactly like FUNCTION nodes already do -- the bug this regresses:
    MODIFIER nodes were built with no `file` at either construction site
    (contract.modifiers_declared and function.modifiers), making every
    applied-modifier source-text lookup unconditionally unreadable."""
    modifier_nodes = vault_graph.nodes_of_kind(MODIFIER)
    assert modifier_nodes
    for mid in modifier_nodes:
        data = vault_graph.graph.nodes[mid]
        assert data.get("file"), f"{mid} has no 'file' attribute"


def test_modifier_declared_via_contract_and_via_function_both_get_file(restricted_graph):
    """`restricted` is both contract-declared (contract.modifiers_declared
    loop) and function-applied (function.modifiers loop) -- both
    construction sites must populate `file` (regression covers both, not
    just whichever one happens to run first)."""
    mid = "mod::Restricted.restricted()"
    assert mid in restricted_graph.graph.nodes
    assert restricted_graph.graph.nodes[mid]["file"]


# --- Gap D: inherited-but-not-overridden function node corruption ----------


@pytest.fixture(scope="module")
def auth_admin_graph() -> ProgramGraph:
    return ProgramGraph.build(AUTH_ADMIN_SOL)


def test_inherited_function_keeps_declaring_contract_attribute(auth_admin_graph):
    """AuthAdmin inherits Auth.verify() without overriding it. The node's
    `contract` attribute must still read the true declarer "Auth", not the
    derived contract "AuthAdmin" -- the bug this regresses: the function loop
    had no `if fid in g` guard, so re-encountering the inherited function
    while iterating AuthAdmin's own `contract.functions` silently overwrote
    `contract` to the last-processed (most-derived) contract's name, even
    though the node id itself ("fn::Auth.verify(...)") already correctly
    encodes the true declarer via canonical_name."""
    verify = "fn::Auth.verify(bytes32,uint8,bytes32,bytes32)"
    assert verify in auth_admin_graph.graph.nodes
    assert auth_admin_graph.graph.nodes[verify]["contract"] == "Auth"


def test_inherited_function_gets_exactly_one_declares_edge(auth_admin_graph):
    """Only Auth (the true declarer) may have a DECLARES edge to verify() --
    AuthAdmin inheriting it without overriding must not add a second,
    spurious DECLARES edge from AuthAdmin."""
    verify = "fn::Auth.verify(bytes32,uint8,bytes32,bytes32)"
    declarers = [u for u, v, d in auth_admin_graph.graph.edges(data=True)
                 if d.get("kind") == DECLARES and v == verify]
    assert declarers == ["contract::Auth"]


def test_derived_contracts_own_function_unaffected(auth_admin_graph):
    """AuthAdmin's own, non-inherited function (setAuthorizedSigner) must
    still be built normally -- the `if fid in g` guard must only skip
    re-processing of an already-seen fid, never suppress genuinely new
    functions declared directly by a derived contract."""
    set_signer = "fn::AuthAdmin.setAuthorizedSigner(address)"
    assert set_signer in auth_admin_graph.graph.nodes
    assert auth_admin_graph.graph.nodes[set_signer]["contract"] == "AuthAdmin"
    declarers = [u for u, v, d in auth_admin_graph.graph.edges(data=True)
                 if d.get("kind") == DECLARES and v == set_signer]
    assert declarers == ["contract::AuthAdmin"]


def test_no_partial_graph_on_build_failure(tmp_path):
    from a4v.graph import BuildFailed

    bad_file = tmp_path / "Broken.sol"
    bad_file.write_text("pragma solidity ^0.8.20; contract Broken { this is not valid solidity )")
    with pytest.raises(BuildFailed):
        ProgramGraph.build(bad_file)
