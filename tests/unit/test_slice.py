from pathlib import Path

from a4v.graph import ProgramGraph
from a4v.slice import BundleBuilder

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"


def test_bundle_contains_expected_context():
    pg = ProgramGraph.build(VAULT_SOL)
    builder = BundleBuilder(pg)
    bundle = builder.expand("fn::Vault.withdraw(uint256)", hops=1)

    assert bundle.contract == "Vault"
    assert "Ownable" in bundle.inherited_defs
    assert set(bundle.state_vars) >= {"oracle", "shares", "totalShares"}
    assert any("getPrice" in e for e in bundle.external_interactions)
    assert any(e == "ext::<low-level-call>" for e in bundle.external_interactions)
    assert set(bundle.write_after_external_call_vars) >= {"shares", "totalShares"}
    # source excerpt for the seed itself must be present and contain the vulnerable call
    seed_excerpt = bundle.source_excerpts.get("fn::Vault.withdraw(uint256)", "")
    assert "msg.sender.call" in seed_excerpt


def test_bundle_includes_caller_and_callee():
    pg = ProgramGraph.build(VAULT_SOL)
    builder = BundleBuilder(pg)
    bundle = builder.expand("fn::Vault._internalHelper()", hops=1)
    assert any("callHelper" in c for c in bundle.callers)


def test_bundle_rejects_non_function_seed():
    import pytest
    pg = ProgramGraph.build(VAULT_SOL)
    builder = BundleBuilder(pg)
    with pytest.raises(ValueError):
        builder.expand("contract::Vault", hops=1)
