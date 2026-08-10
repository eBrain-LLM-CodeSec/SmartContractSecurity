"""Unit tests for rtf.l12_evaluation.coverage_telemetry's 6-state
applicability/coverage classification. All fixtures are synthetic dicts
matching the exact shapes PipelineArtifacts's fields already use -- no
live Codex/API calls, no EVMbench data. Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_coverage_telemetry
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l12_evaluation.coverage_telemetry import CoverageState, classify_all, classify_coverage
from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState, EvidenceItem, RoutedRequirementResult

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _result(applicability=ApplicabilityState.APPLICABLE, conformance=ConformanceState.PASS,
            evidence: tuple = ()) -> RoutedRequirementResult:
    return RoutedRequirementResult(
        req_id="req-x", applicability_state=applicability, conformance_state=conformance, evidence=evidence,
    )


def test_not_in_routed_is_never_considered():
    state = classify_coverage("req-x", {}, {}, {}, {})
    check("missing from routed -> NEVER_CONSIDERED", state == CoverageState.NEVER_CONSIDERED, state)


def test_not_applicable_state():
    routed = {"req-x": _result(applicability=ApplicabilityState.NOT_APPLICABLE, conformance=None)}
    state = classify_coverage("req-x", routed, {}, {}, {})
    check("NOT_APPLICABLE applicability -> NOT_APPLICABLE", state == CoverageState.NOT_APPLICABLE, state)


def test_applicable_but_never_escalated_is_never_considered():
    """conformance_state is None despite being applicable -- no evidence,
    or an operational failure blocked evaluation before the agent step."""
    routed = {"req-x": _result(applicability=ApplicabilityState.APPLICABLE, conformance=None)}
    state = classify_coverage("req-x", routed, {}, {}, {})
    check("applicable, conformance_state=None -> NEVER_CONSIDERED (never reached the agent)",
          state == CoverageState.NEVER_CONSIDERED, state)


def test_crashed_investigation_is_exploration_failed():
    routed = {"req-x": _result(conformance=ConformanceState.INCONCLUSIVE)}
    skip_reasons = {"req-x": "codex_invocation_crashed: RuntimeError: boom"}
    state = classify_coverage("req-x", routed, skip_reasons, {}, {})
    check("crashed -> EXPLORATION_FAILED", state == CoverageState.EXPLORATION_FAILED, state)


def test_timeout_is_exploration_failed():
    routed = {"req-x": _result(conformance=ConformanceState.INCONCLUSIVE)}
    outcome_reasons = {"req-x": "codex_timeout"}
    state = classify_coverage("req-x", routed, {}, outcome_reasons, {})
    check("timeout -> EXPLORATION_FAILED", state == CoverageState.EXPLORATION_FAILED, state)


def test_no_decision_is_exploration_failed():
    routed = {"req-x": _result(conformance=ConformanceState.INCONCLUSIVE)}
    outcome_reasons = {"req-x": "codex_no_decision"}
    state = classify_coverage("req-x", routed, {}, outcome_reasons, {})
    check("no parseable decision -> EXPLORATION_FAILED", state == CoverageState.EXPLORATION_FAILED, state)


def test_unresolved_graph_seed_is_applied_to_wrong_functions():
    routed = {"req-x": _result(conformance=ConformanceState.PASS)}
    skip_reasons = {"req-x": "graph_seed_not_resolved (agent still investigates): ValueError: no such node"}
    graph_seed_resolved = {"req-x": False}
    state = classify_coverage("req-x", routed, skip_reasons, {}, graph_seed_resolved)
    check("graph seed never resolved -> APPLIED_TO_WRONG_FUNCTIONS",
          state == CoverageState.APPLIED_TO_WRONG_FUNCTIONS, state)


def test_exploration_failure_takes_precedence_over_wrong_functions():
    """A crash is a MORE specific explanation than an unresolved graph
    seed -- if both signals are present (a crash after a bad seed
    resolution attempt), EXPLORATION_FAILED wins."""
    routed = {"req-x": _result(conformance=ConformanceState.INCONCLUSIVE)}
    skip_reasons = {"req-x": "graph_seed_not_resolved (agent still investigates): ValueError: no such node"}
    outcome_reasons = {"req-x": "codex_timeout"}
    graph_seed_resolved = {"req-x": False}
    state = classify_coverage("req-x", routed, skip_reasons, outcome_reasons, graph_seed_resolved)
    check("crash/timeout wins over unresolved-seed", state == CoverageState.EXPLORATION_FAILED, state)


def test_multi_location_evidence_investigated_only_once_is_applied_once_globally():
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp)
        evidence = (
            EvidenceItem(predicate="p", location="Contract.funcA"),
            EvidenceItem(predicate="p", location="Contract.funcB"),
        )
        routed = {"req-x": _result(conformance=ConformanceState.PASS, evidence=evidence)}
        state = classify_coverage("req-x", routed, {}, {}, {"req-x": True},
                                   instance_results={}, project_root=project_root)
        check("multi-location evidence, only 1 investigation -> APPLIED_ONCE_GLOBALLY",
              state == CoverageState.APPLIED_ONCE_GLOBALLY, state)


def test_single_location_evidence_investigated_once_is_reasoning_failed_not_flagged():
    """A requirement whose evidence only ever had ONE relevant site is
    NOT under-covered by investigating it once -- must fall through to
    REASONING_FAILED, not be mislabeled APPLIED_ONCE_GLOBALLY."""
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp)
        evidence = (EvidenceItem(predicate="p", location="Contract.onlyFunc"),)
        routed = {"req-x": _result(conformance=ConformanceState.PASS, evidence=evidence)}
        state = classify_coverage("req-x", routed, {}, {}, {"req-x": True},
                                   instance_results={}, project_root=project_root)
        check("single-location evidence investigated once -> REASONING_FAILED (not flagged as under-covered)",
              state == CoverageState.REASONING_FAILED, state)


def test_multi_location_evidence_with_multiple_instances_is_reasoning_failed():
    """Expansion WAS used and covered multiple locations -- no longer
    under-covered, falls through to REASONING_FAILED."""
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp)
        evidence = (
            EvidenceItem(predicate="p", location="Contract.funcA"),
            EvidenceItem(predicate="p", location="Contract.funcB"),
        )
        routed = {"req-x": _result(conformance=ConformanceState.PASS, evidence=evidence)}
        instance_results = {"req-x": [object(), object()]}  # 2 real investigations happened
        state = classify_coverage("req-x", routed, {}, {}, {"req-x": True},
                                   instance_results=instance_results, project_root=project_root)
        check("multi-location evidence, 2 investigations actually happened -> REASONING_FAILED",
              state == CoverageState.REASONING_FAILED, state)


def test_clean_outcome_with_no_evidence_data_available_is_reasoning_failed():
    """project_root omitted -- caller doesn't have enough data to compute
    the APPLIED_ONCE_GLOBALLY distinction; must degrade safely to
    REASONING_FAILED, not crash."""
    routed = {"req-x": _result(conformance=ConformanceState.PASS)}
    state = classify_coverage("req-x", routed, {}, {}, {"req-x": True})
    check("no project_root given -> degrades to REASONING_FAILED, no crash",
          state == CoverageState.REASONING_FAILED, state)


def test_classify_all_covers_every_req_id_in_routed():
    routed = {
        "req-a": _result(applicability=ApplicabilityState.NOT_APPLICABLE, conformance=None),
        "req-b": _result(conformance=ConformanceState.PASS),
    }
    result = classify_all(routed, {}, {}, {})
    check("classify_all: every req_id present", set(result.keys()) == {"req-a", "req-b"}, result)
    check("classify_all: req-a is NOT_APPLICABLE", result["req-a"] == CoverageState.NOT_APPLICABLE)
    check("classify_all: req-b falls through to REASONING_FAILED", result["req-b"] == CoverageState.REASONING_FAILED)


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
