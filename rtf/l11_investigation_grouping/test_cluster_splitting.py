"""Unit tests for rtf.l11_investigation_grouping.cluster_splitting.
Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_cluster_splitting
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.cluster_response_validation import (
    ClusterValidationResult, PropertyVerdict, validate_cluster_response,
)
from rtf.l11_investigation_grouping.cluster_splitting import detect_split_reason, split_cluster
from rtf.l11_investigation_grouping.complexity import ClusterBudget
from rtf.l11_investigation_grouping.grouping_engine import Cluster
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.l12_evaluation.metrics import ConformanceState

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
        target_contract="Vault", target_function="f", candidate_locations=(f"Vault.{pid}",),
    )
    base.update(overrides)
    return PropertyMetadata(**base)


def _cluster(pids: tuple[str, ...], **overrides) -> Cluster:
    base = dict(cluster_id="cluster_017", property_ids=pids, grouping_reason=(),
                shared_context={}, estimated_context_size=len(pids))
    base.update(overrides)
    return Cluster(**base)


# --- detect_split_reason -----------------------------------------------

def test_no_signals_means_no_split():
    cluster = _cluster(("P1", "P2"))
    result = detect_split_reason(cluster, {})
    check("no signals given: should_split is False", not result.should_split)
    check("no signals given: reason_code is None", result.reason_code is None)


def test_budget_violation_triggers_split():
    by_id = {f"P{i}": _prop(f"P{i}") for i in range(1, 6)}
    cluster = _cluster(tuple(by_id.keys()))
    budget = ClusterBudget(max_properties_per_cluster=3)
    result = detect_split_reason(cluster, by_id, budget=budget)
    check("budget violation: should_split True", result.should_split)
    check("budget violation: correct reason code", result.reason_code == "exceeds_context_budget", result.reason_code)


def test_incomplete_response_triggers_split():
    cluster = _cluster(("P1", "P2"))
    validation = validate_cluster_response(["P1", "P2"], {"properties": [{"property_id": "P1", "verdict": "PASS"}]})
    result = detect_split_reason(cluster, {}, validation_result=validation)
    check("incomplete response: should_split True", result.should_split)
    check("incomplete response: correct reason code", result.reason_code == "incomplete_response", result.reason_code)


def test_insufficient_counterexample_rigor_triggers_split():
    cluster = _cluster(("P1",))
    resolved = {"P1": PropertyVerdict(ConformanceState.INCONCLUSIVE, "insufficient_reasoning_rigor:counterexample_attempt_too_thin")}
    result = detect_split_reason(cluster, {}, resolved_verdicts=resolved)
    check("insufficient rigor: should_split True", result.should_split)
    check("insufficient rigor: correct reason code", result.reason_code == "insufficient_counterexample_rigor", result.reason_code)


def test_conflated_obligations_triggers_split():
    cluster = _cluster(("P1", "P2"))
    validation = validate_cluster_response(["P1", "P2"], {
        "properties": [
            {"property_id": "P1", "verdict": "PASS", "reasoning": "Same text.",
             "counterexample_attempt": "x" * 20, "counterexample_result": "x" * 20},
            {"property_id": "P2", "verdict": "PASS", "reasoning": "Same text.",
             "counterexample_attempt": "x" * 20, "counterexample_result": "x" * 20},
        ]
    })
    result = detect_split_reason(cluster, {}, validation_result=validation)
    check("conflated obligations: should_split True", result.should_split)
    check("conflated obligations: correct reason code", result.reason_code == "conflated_obligations", result.reason_code)


def test_precedence_budget_checked_before_completeness():
    by_id = {f"P{i}": _prop(f"P{i}") for i in range(1, 6)}
    cluster = _cluster(tuple(by_id.keys()))
    budget = ClusterBudget(max_properties_per_cluster=3)
    validation = validate_cluster_response(list(by_id.keys()), {"properties": [{"property_id": "P1", "verdict": "PASS"}]})
    result = detect_split_reason(cluster, by_id, budget=budget, validation_result=validation)
    check("budget checked before completeness (both apply, budget wins)", result.reason_code == "exceeds_context_budget", result.reason_code)


# --- split_cluster --------------------------------------------------------

def test_split_produces_two_halves_no_property_lost():
    by_id = {f"P{i}": _prop(f"P{i}") for i in range(1, 7)}
    cluster = _cluster(tuple(by_id.keys()))
    a, b = split_cluster(cluster, by_id)
    all_ids = sorted(a.property_ids + b.property_ids)
    check("split: no property lost", all_ids == sorted(by_id.keys()), all_ids)
    check("split: no property duplicated across halves", len(set(a.property_ids) & set(b.property_ids)) == 0)


def test_split_example_matches_plan_p1_p6_becomes_p1_p3_and_p4_p6():
    by_id = {pid: _prop(pid) for pid in ("P1", "P2", "P3", "P4", "P5", "P6")}
    cluster = _cluster(tuple(by_id.keys()))
    a, b = split_cluster(cluster, by_id)
    check("first half is P1,P2,P3", a.property_ids == ("P1", "P2", "P3"), a.property_ids)
    check("second half is P4,P5,P6", b.property_ids == ("P4", "P5", "P6"), b.property_ids)


def test_split_odd_count_gives_extra_to_first_half():
    by_id = {pid: _prop(pid) for pid in ("P1", "P2", "P3", "P4", "P5")}
    cluster = _cluster(tuple(by_id.keys()))
    a, b = split_cluster(cluster, by_id)
    check("odd count: first half has the extra member", len(a.property_ids) == 3 and len(b.property_ids) == 2,
          (a.property_ids, b.property_ids))


def test_split_records_why_via_cluster_ids_and_grouping_reason():
    by_id = {pid: _prop(pid) for pid in ("P1", "P2", "P3", "P4")}
    cluster = _cluster(tuple(by_id.keys()), cluster_id="cluster_017")
    a, b = split_cluster(cluster, by_id)
    check("split halves reference the original cluster_id", "cluster_017" in a.cluster_id and "cluster_017" in b.cluster_id, (a.cluster_id, b.cluster_id))
    check("split halves record the split origin in grouping_reason",
          "split_from:cluster_017" in a.grouping_reason and "split_from:cluster_017" in b.grouping_reason,
          (a.grouping_reason, b.grouping_reason))


def test_split_recomputes_shared_context_not_stale_copy():
    a_prop = _prop("P1", target_contract="Alpha", relevant_files=("Alpha.sol",))
    b_prop = _prop("P2", target_contract="Beta", relevant_files=("Beta.sol",))
    by_id = {"P1": a_prop, "P2": b_prop}
    cluster = _cluster(("P1", "P2"), shared_context={"contracts": ["Alpha", "Beta"]})
    a, b = split_cluster(cluster, by_id)
    check("first half's shared_context reflects ONLY its own member",
          a.shared_context["contracts"] == ["Alpha"], a.shared_context)
    check("second half's shared_context reflects ONLY its own member",
          b.shared_context["contracts"] == ["Beta"], b.shared_context)


def test_split_single_property_cluster_raises():
    by_id = {"P1": _prop("P1")}
    cluster = _cluster(("P1",))
    try:
        split_cluster(cluster, by_id)
        check("splitting a singleton raises", False, "did not raise")
    except ValueError:
        check("splitting a singleton raises", True)


def test_split_singleton_halves_have_empty_grouping_reason():
    by_id = {"P1": _prop("P1"), "P2": _prop("P2")}
    cluster = _cluster(("P1", "P2"))
    a, b = split_cluster(cluster, by_id)
    check("size-1 halves have empty grouping_reason (matches engine's own singleton convention)",
          a.grouping_reason == () and b.grouping_reason == (), (a.grouping_reason, b.grouping_reason))


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
