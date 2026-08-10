"""Unit tests for rtf.l11_investigation_grouping.grouping_engine.
Synthetic PropertyMetadata fixtures only -- no EVMbench data. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_grouping_engine
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.grouping_engine import (
    STRONG_POSITIVE_WEIGHT, cluster_properties, compatibility_score,
)
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


# --- compatibility_score -----------------------------------------------------

def test_same_property_id_is_hard_veto():
    a = _prop("p1")
    result = compatibility_score(a, a)
    check("same property_id: hard veto", result.hard_veto, result)


def test_same_requirement_is_strong_positive():
    a = _prop("p1", requirement_id="req-x", candidate_locations=("A.f",))
    b = _prop("p2", requirement_id="req-x", candidate_locations=("A.f",))
    result = compatibility_score(a, b)
    check("same requirement_id: positive score", result.score > 0, result)
    check("same requirement_id: reason present", "same_requirement" in result.reasons, result.reasons)


def test_same_reasoning_category_is_strong_positive():
    a = _prop("p1", requirement_id="req-a", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    b = _prop("p2", requirement_id="req-b", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    result = compatibility_score(a, b)
    check("same reasoning_category: reason present", "same_reasoning_category" in result.reasons, result.reasons)


def test_unsafe_category_combination_is_hard_veto_regardless_of_other_overlap():
    a = _prop("p1", requirement_id="req-a", target_contract="Vault", reasoning_category=ReasoningCategory.AGGREGATION_META)
    b = _prop("p2", requirement_id="req-b", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    result = compatibility_score(a, b)
    check("unsafe category combo: hard veto even with same contract", result.hard_veto, result)


def test_shared_state_variables_is_strong_positive():
    a = _prop("p1", target_contract="Vault", relevant_state_variables=("totalShares",))
    b = _prop("p2", target_contract="Vault2", relevant_state_variables=("totalShares", "owner"))
    result = compatibility_score(a, b)
    check("shared state variables: reason present", "shared_state_variables" in result.reasons, result.reasons)


def test_unrelated_contracts_no_shared_context_is_negative():
    a = _prop("p1", target_contract="Alpha", relevant_state_variables=("x",), relevant_files=("Alpha.sol",))
    b = _prop("p2", target_contract="Beta", relevant_state_variables=("y",), relevant_files=("Beta.sol",))
    result = compatibility_score(a, b)
    check("unrelated contracts, no overlap anywhere: negative score", result.score < 0, result)
    check("unrelated contracts: reason present", "unrelated_contracts_no_shared_context" in result.reasons, result.reasons)


def test_unrelated_contracts_but_shared_file_not_penalized():
    """Two different contracts declared in the SAME file (a common
    Solidity pattern) should not be penalized as 'no shared context'."""
    a = _prop("p1", target_contract="Alpha", relevant_files=("Multi.sol",))
    b = _prop("p2", target_contract="Beta", relevant_files=("Multi.sol",))
    result = compatibility_score(a, b)
    check("different contracts, same file: NOT penalized", "unrelated_contracts_no_shared_context" not in result.reasons, result.reasons)


def test_same_contract_no_veto_no_penalty():
    a = _prop("p1", target_contract="Vault", target_function="withdraw")
    b = _prop("p2", target_contract="Vault", target_function="deposit")
    result = compatibility_score(a, b)
    check("same contract: positive, not vetoed", result.score > 0 and not result.hard_veto, result)


def test_score_is_symmetric():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", relevant_state_variables=("s",))
    b = _prop("p2", requirement_id="req-x", target_contract="Vault", relevant_state_variables=("s",))
    r1 = compatibility_score(a, b)
    r2 = compatibility_score(b, a)
    check("symmetric score", r1.score == r2.score, (r1.score, r2.score))
    check("symmetric reasons", set(r1.reasons) == set(r2.reasons), (r1.reasons, r2.reasons))


# --- cluster_properties -------------------------------------------------------

def test_two_highly_compatible_properties_merge():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", candidate_locations=("Vault.f",))
    b = _prop("p2", requirement_id="req-x", target_contract="Vault", candidate_locations=("Vault.f",))
    clusters = cluster_properties([a, b])
    check("2 highly compatible props: 1 cluster", len(clusters) == 1, clusters)
    check("cluster has both property_ids", set(clusters[0].property_ids) == {"p1", "p2"}, clusters[0].property_ids)
    check("grouping_reason non-empty", len(clusters[0].grouping_reason) > 0, clusters[0].grouping_reason)


def test_two_unrelated_properties_stay_separate():
    a = _prop("p1", target_contract="Alpha", relevant_files=("Alpha.sol",), relevant_state_variables=("x",))
    b = _prop("p2", target_contract="Beta", relevant_files=("Beta.sol",), relevant_state_variables=("y",))
    clusters = cluster_properties([a, b])
    check("2 unrelated props: 2 singleton clusters", len(clusters) == 2, clusters)


def test_no_property_is_dropped_or_duplicated():
    props = [_prop(f"p{i}", target_contract=f"C{i % 3}") for i in range(10)]
    clusters = cluster_properties(props)
    all_ids = [pid for c in clusters for pid in c.property_ids]
    check("every input property appears exactly once", sorted(all_ids) == sorted(p.property_id for p in props), all_ids)


def test_unsafe_combination_never_merges_even_with_high_similarity():
    a = _prop("p1", target_contract="Vault", candidate_locations=("Vault.f",), reasoning_category=ReasoningCategory.AGGREGATION_META)
    b = _prop("p2", target_contract="Vault", candidate_locations=("Vault.f",), reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    clusters = cluster_properties([a, b])
    check("unsafe combo: never merged despite same contract/location", len(clusters) == 2, clusters)


def test_max_cluster_size_is_respected():
    props = [_prop(f"p{i}", requirement_id="req-x", target_contract="Vault", candidate_locations=("Vault.f",))
             for i in range(6)]
    clusters = cluster_properties(props, max_cluster_size=3)
    check("max_cluster_size=3: no cluster exceeds 3", all(len(c.property_ids) <= 3 for c in clusters), clusters)
    check("max_cluster_size=3: at least 2 clusters formed (6 props, cap 3)", len(clusters) >= 2, clusters)


def test_deterministic_across_repeated_calls():
    props = [_prop(f"p{i}", target_contract=f"C{i % 4}", requirement_id=f"req-{i % 4}") for i in range(12)]
    r1 = cluster_properties(props)
    r2 = cluster_properties(props)
    check("deterministic: same clusters both times",
          [c.property_ids for c in r1] == [c.property_ids for c in r2], (r1, r2))


def test_shared_context_reflects_real_union_of_member_data():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", relevant_files=("Vault.sol",),
              relevant_state_variables=("totalShares",))
    b = _prop("p2", requirement_id="req-x", target_contract="Vault", relevant_files=("Vault.sol",),
              relevant_state_variables=("owner",))
    clusters = cluster_properties([a, b])
    check("shared_context: union of files", clusters[0].shared_context["files"] == ["Vault.sol"], clusters[0].shared_context)
    check("shared_context: union of state variables",
          sorted(clusters[0].shared_context["state_variables"]) == ["owner", "totalShares"], clusters[0].shared_context)
    check("shared_context: contracts listed", clusters[0].shared_context["contracts"] == ["Vault"], clusters[0].shared_context)


def test_singleton_cluster_has_empty_grouping_reason():
    a = _prop("p1", target_contract="Alpha")
    clusters = cluster_properties([a])
    check("singleton: empty grouping_reason", clusters[0].grouping_reason == (), clusters[0].grouping_reason)
    check("singleton: contains its own property", clusters[0].property_ids == ("p1",))


def test_min_score_threshold_prevents_weak_only_merges():
    """Two properties sharing ONLY a weak positive signal (source
    proximity) must not merge under the default threshold (1 strong
    positive signal's worth)."""
    a = _prop("p1", target_contract="Alpha", relevant_files=("Shared.sol",))
    b = _prop("p2", target_contract="Beta", relevant_files=("Shared.sol",))
    clusters = cluster_properties([a, b])
    check("weak-only overlap: does not merge under default threshold", len(clusters) == 2, clusters)


def test_lower_threshold_allows_weak_only_merge():
    a = _prop("p1", target_contract="Alpha", relevant_files=("Shared.sol",))
    b = _prop("p2", target_contract="Beta", relevant_files=("Shared.sol",))
    clusters = cluster_properties([a, b], min_score_to_group=0.5)
    check("weak-only overlap merges when threshold is lowered below the weak weight", len(clusters) == 1, clusters)


def test_chain_transitivity_uses_conservative_minimum():
    """A-B share a requirement (strong positive); B-C share a requirement
    too, but A-C share NOTHING and are on unrelated contracts (negative).
    The conservative min-score rule means the A-B-C merge must NOT
    complete once C would drag the cluster's compatibility with A below
    threshold -- verifies the algorithm doesn't just chain-merge blindly.
    """
    a = _prop("p1", requirement_id="req-shared-ab", target_contract="Alpha", relevant_files=("Alpha.sol",))
    b = _prop("p2", requirement_id="req-shared-ab", target_contract="Alpha", relevant_files=("Alpha.sol",))
    c = _prop("p3", requirement_id="req-shared-bc-not-real", target_contract="Gamma", relevant_files=("Gamma.sol",))
    # a & b are highly compatible (same requirement, same contract, same file).
    # c is unrelated to both a and b (different contract, different file, different requirement).
    clusters = cluster_properties([a, b, c])
    check("a,b merge together", any(set(cl.property_ids) == {"p1", "p2"} for cl in clusters), clusters)
    check("c stays separate (no path connects it)", any(cl.property_ids == ("p3",) for cl in clusters), clusters)


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
