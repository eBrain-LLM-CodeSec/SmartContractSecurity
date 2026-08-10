"""Unit tests for rtf.l11_investigation_grouping.complexity. Synthetic
fixtures only. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_complexity
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.complexity import (
    ClusterBudget, budget_violations, compute_complexity, within_budget, with_complexity,
)
from rtf.l11_investigation_grouping.grouping_engine import Cluster
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.l11_investigation_grouping.taxonomy import ReasoningCategory

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _prop(pid: str, **overrides) -> PropertyMetadata:
    base = dict(
        property_id=pid, requirement_id=f"req-{pid}", requirement_level="Q",
        requirement_semantic_intent="Test Requirement", property_text="test",
        target_contract=None, target_function=None, candidate_locations=(),
    )
    base.update(overrides)
    return PropertyMetadata(**base)


def _cluster(property_ids: tuple[str, ...], estimated_context_size: int = 0) -> Cluster:
    return Cluster(
        cluster_id="c0", property_ids=property_ids, grouping_reason=(),
        shared_context={}, estimated_context_size=estimated_context_size,
    )


# --- compute_complexity -------------------------------------------------

def test_more_properties_increases_score():
    p1 = _prop("p1", target_contract="A")
    p2 = _prop("p2", target_contract="A")
    p3 = _prop("p3", target_contract="A")
    by_id = {p.property_id: p for p in (p1, p2, p3)}
    small = compute_complexity(_cluster(("p1",)), by_id)
    large = compute_complexity(_cluster(("p1", "p2", "p3")), by_id)
    check("more properties -> higher score", large.score > small.score, (small.score, large.score))
    check("num_properties counted correctly", large.num_properties == 3, large.num_properties)


def test_more_contracts_increases_score_more_than_more_functions_same_contract():
    """Contracts are weighted heaviest of the count-based factors --
    verify that empirically, not just assert the weight constant."""
    a = _prop("p1", target_contract="Vault", target_function="f1")
    b_same_contract = _prop("p2", target_contract="Vault", target_function="f2")
    b_diff_contract = _prop("p2", target_contract="Other", target_function="f2")

    same_contract_complexity = compute_complexity(
        _cluster(("p1", "p2")), {"p1": a, "p2": b_same_contract})
    diff_contract_complexity = compute_complexity(
        _cluster(("p1", "p2")), {"p1": a, "p2": b_diff_contract})
    check("2 contracts scores higher than 1 contract, same function count",
          diff_contract_complexity.score > same_contract_complexity.score,
          (same_contract_complexity.score, diff_contract_complexity.score))


def test_cross_contract_callgraph_dependency_detected():
    a = _prop("p1", target_contract="Vault", callgraph_neighbors=("fn::Other.helper(uint256)",))
    by_id = {"p1": a}
    breakdown = compute_complexity(_cluster(("p1",)), by_id)
    check("cross-contract callgraph neighbor detected", breakdown.num_cross_contract_dependencies == 1, breakdown)


def test_same_contract_callgraph_neighbor_not_counted_as_cross_contract():
    a = _prop("p1", target_contract="Vault", callgraph_neighbors=("fn::Vault.helper(uint256)",))
    by_id = {"p1": a}
    breakdown = compute_complexity(_cluster(("p1",)), by_id)
    check("same-contract callgraph neighbor NOT counted as cross-contract", breakdown.num_cross_contract_dependencies == 0, breakdown)


def test_temporal_reasoning_flag_from_category():
    a = _prop("p1", target_contract="Vault", reasoning_category=ReasoningCategory.TIME_BLOCK_MEV_ORDERING)
    breakdown = compute_complexity(_cluster(("p1",)), {"p1": a})
    check("temporal reasoning flag set for TIME_BLOCK_MEV_ORDERING", breakdown.requires_temporal_reasoning)
    check("arithmetic reasoning flag NOT set", not breakdown.requires_arithmetic_reasoning)


def test_arithmetic_reasoning_flag_from_category():
    a = _prop("p1", target_contract="Vault", reasoning_category=ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS)
    breakdown = compute_complexity(_cluster(("p1",)), {"p1": a})
    check("arithmetic reasoning flag set for ARITHMETIC_VALUE_CORRECTNESS", breakdown.requires_arithmetic_reasoning)
    check("temporal reasoning flag NOT set", not breakdown.requires_temporal_reasoning)


def test_source_context_size_reused_from_cluster_not_recomputed():
    a = _prop("p1", target_contract="Vault")
    breakdown = compute_complexity(_cluster(("p1",), estimated_context_size=42), {"p1": a})
    check("source_context_size matches the cluster's own estimated_context_size", breakdown.source_context_size == 42, breakdown)


def test_with_complexity_populates_the_cluster_field():
    a = _prop("p1", target_contract="Vault")
    cluster = _cluster(("p1",))
    check("before with_complexity: estimated_complexity is None", cluster.estimated_complexity is None)
    updated = with_complexity(cluster, {"p1": a})
    check("after with_complexity: estimated_complexity is a real number", isinstance(updated.estimated_complexity, float))
    check("with_complexity does not mutate the original cluster (frozen dataclass)", cluster.estimated_complexity is None)


# --- budgets --------------------------------------------------------------

def test_default_budget_has_no_limits():
    from rtf.l11_investigation_grouping.complexity import DEFAULT_BUDGET
    a = _prop("p1", target_contract="Vault")
    huge_cluster = _cluster(tuple(f"p{i}" for i in range(1000)), estimated_context_size=100000)
    by_id = {f"p{i}": _prop(f"p{i}", target_contract="Vault") for i in range(1000)}
    check("default budget: nothing violates it, even a huge cluster",
          within_budget(huge_cluster, by_id, DEFAULT_BUDGET))


def test_max_properties_per_cluster_enforced():
    by_id = {f"p{i}": _prop(f"p{i}", target_contract="Vault") for i in range(5)}
    cluster = _cluster(tuple(by_id.keys()))
    budget = ClusterBudget(max_properties_per_cluster=3)
    violations = budget_violations(cluster, by_id, budget)
    check("max_properties_per_cluster violated when exceeded", "max_properties_per_cluster" in violations, violations)


def test_max_properties_per_cluster_not_violated_when_under_limit():
    by_id = {f"p{i}": _prop(f"p{i}", target_contract="Vault") for i in range(2)}
    cluster = _cluster(tuple(by_id.keys()))
    budget = ClusterBudget(max_properties_per_cluster=3)
    check("under the limit: no violation", within_budget(cluster, by_id, budget))


def test_max_files_per_cluster_enforced():
    a = _prop("p1", relevant_files=("A.sol", "B.sol", "C.sol"))
    cluster = _cluster(("p1",))
    budget = ClusterBudget(max_files_per_cluster=2)
    violations = budget_violations(cluster, {"p1": a}, budget)
    check("max_files_per_cluster violated when exceeded", "max_files_per_cluster" in violations, violations)


def test_max_context_tokens_uses_estimated_context_size_as_proxy():
    a = _prop("p1")
    cluster = _cluster(("p1",), estimated_context_size=500)
    budget = ClusterBudget(max_context_tokens=100)
    violations = budget_violations(cluster, {"p1": a}, budget)
    check("max_context_tokens violated when estimated_context_size exceeds it", "max_context_tokens" in violations, violations)


def test_max_complexity_score_enforced():
    by_id = {f"p{i}": _prop(f"p{i}", target_contract=f"C{i}") for i in range(5)}
    cluster = _cluster(tuple(by_id.keys()))
    unconstrained = compute_complexity(cluster, by_id)
    budget = ClusterBudget(max_complexity_score=unconstrained.score - 1.0)
    violations = budget_violations(cluster, by_id, budget)
    check("max_complexity_score violated when the real score exceeds it", "max_complexity_score" in violations, violations)


def test_multiple_violations_all_reported():
    by_id = {f"p{i}": _prop(f"p{i}", target_contract="Vault", relevant_files=(f"F{i}.sol",)) for i in range(10)}
    cluster = _cluster(tuple(by_id.keys()), estimated_context_size=1000)
    budget = ClusterBudget(max_properties_per_cluster=3, max_files_per_cluster=3, max_context_tokens=10)
    violations = budget_violations(cluster, by_id, budget)
    check("all 3 violated limits reported, not just the first",
          set(violations) == {"max_properties_per_cluster", "max_files_per_cluster", "max_context_tokens"}, violations)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
