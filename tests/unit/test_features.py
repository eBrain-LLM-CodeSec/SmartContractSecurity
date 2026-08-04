from pathlib import Path

from a4v.features import FeatureExtractor, arithmetic_op_count
from a4v.graph import ProgramGraph

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
CASTS_SOL = FIXTURES / "features" / "Casts.sol"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
ACCOUNTING_SOL = FIXTURES / "accounting_signals" / "Accounting.sol"


def test_unsafe_cast_detected():
    pg = ProgramGraph.build(CASTS_SOL)
    raw = FeatureExtractor.compute(pg)
    assert raw["fn::Casts.unsafeCast(uint256)"].unsafe_cast_count == 1
    assert raw["fn::Casts.safeCast(uint8)"].unsafe_cast_count == 0


def test_cyclomatic_complexity_higher_for_branchy_function():
    pg = ProgramGraph.build(CASTS_SOL)
    raw = FeatureExtractor.compute(pg)
    branchy = raw["fn::Casts.branchy(uint256)"].cyclomatic_complexity
    unsafe_cast = raw["fn::Casts.unsafeCast(uint256)"].cyclomatic_complexity
    assert branchy > unsafe_cast


def test_external_call_and_write_after_call_counts_on_vault():
    pg = ProgramGraph.build(VAULT_SOL)
    raw = FeatureExtractor.compute(pg)
    withdraw = raw["fn::Vault.withdraw(uint256)"]
    assert withdraw.external_call_count >= 2  # oracle.getPrice() + low-level .call
    assert withdraw.write_after_external_call_count >= 2  # shares, totalShares

    deposit = raw["fn::Vault.deposit()"]
    assert deposit.external_call_count == 0
    assert deposit.write_after_external_call_count == 0


def test_arithmetic_op_count_multiplication_and_division():
    pg = ProgramGraph.build(CASTS_SOL)
    raw = FeatureExtractor.compute(pg)
    assert raw["fn::Casts.scaleAndDivide(uint256,uint256,uint256)"].arithmetic_op_count == 2


def test_arithmetic_op_count_modulo_only_does_not_count():
    pg = ProgramGraph.build(CASTS_SOL)
    raw = FeatureExtractor.compute(pg)
    assert raw["fn::Casts.modOnly(uint256,uint256)"].arithmetic_op_count == 0


def test_arithmetic_op_count_power_counts():
    pg = ProgramGraph.build(CASTS_SOL)
    raw = FeatureExtractor.compute(pg)
    assert raw["fn::Casts.powerOnly(uint256,uint256)"].arithmetic_op_count == 1


def test_arithmetic_op_count_zero_when_no_arithmetic():
    pg = ProgramGraph.build(CASTS_SOL)
    raw = FeatureExtractor.compute(pg)
    assert raw["fn::Casts.safeCast(uint8)"].arithmetic_op_count == 0


def test_arithmetic_op_count_callable_directly_on_function_object():
    """`arithmetic_op_count` is public (not `_`-prefixed) specifically so
    `a4v/mgpr/predicates.py` can call it on any Function object -- including
    internal-call callees discovered by a bounded-depth search, not just
    nodes with a precomputed NodeFeatures entry."""
    pg = ProgramGraph.build(ACCOUNTING_SOL)
    by_canonical = {f.canonical_name: f for c in pg.slither.contracts for f in c.functions}
    fn = by_canonical["Accounting._computeShareQuote(uint256)"]
    assert arithmetic_op_count(fn) == 2  # (tgtAmount * totalShares) / (reserve + 1)


def test_zscore_is_centered_and_scaled():
    pg = ProgramGraph.build(VAULT_SOL)
    raw = FeatureExtractor.compute(pg)
    z = FeatureExtractor.zscore(raw)
    withdraw_z = z["fn::Vault.withdraw(uint256)"]["write_after_external_call_count"]
    deposit_z = z["fn::Vault.deposit()"]["write_after_external_call_count"]
    assert withdraw_z > deposit_z
