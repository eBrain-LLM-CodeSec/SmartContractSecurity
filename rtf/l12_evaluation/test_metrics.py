"""Unit tests for L12's stage-separated metrics and failure taxonomy.
Pure synthetic data -- no compilation, no network, no live LLM calls.
Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_metrics
"""
from __future__ import annotations

import sys

from .failure_taxonomy import (
    OperationalStatus,
    classify_bucket,
    is_eligible_for_routing_metrics,
)
from .metrics import (
    ApplicabilityState,
    ConformanceState,
    EvidenceItem,
    GroundTruthFinding,
    RoutedRequirementResult,
    TargetRunResult,
    applicability_recall_on_known_applicable,
    evidence_collection_recall,
    false_alert_rate,
    final_finding_recall,
    inconclusive_rate,
    insufficient_evidence_rate,
    requirement_routing_precision,
    requirement_routing_recall,
    target_localization_accuracy,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def test_failure_taxonomy_classification():
    check("taxonomy: OK is eligible for routing metrics", is_eligible_for_routing_metrics(OperationalStatus.OK), "")
    check("taxonomy: COMPILATION_FAILURE is NOT eligible", not is_eligible_for_routing_metrics(OperationalStatus.COMPILATION_FAILURE), "")
    check("taxonomy: OK classifies to its own bucket", classify_bucket(OperationalStatus.OK) == "OK", classify_bucket(OperationalStatus.OK))
    check("taxonomy: COMPILATION_FAILURE classifies as INFRASTRUCTURE", classify_bucket(OperationalStatus.COMPILATION_FAILURE) == "INFRASTRUCTURE", classify_bucket(OperationalStatus.COMPILATION_FAILURE))
    check("taxonomy: ROUTING_FAILURE classifies as FRAMEWORK_DECISION_FAILURE", classify_bucket(OperationalStatus.ROUTING_FAILURE) == "FRAMEWORK_DECISION_FAILURE", classify_bucket(OperationalStatus.ROUTING_FAILURE))
    check("taxonomy: MISSING_EXTERNAL_EVIDENCE classifies as EXPECTED_LIMITATION", classify_bucket(OperationalStatus.MISSING_EXTERNAL_EVIDENCE) == "EXPECTED_LIMITATION", classify_bucket(OperationalStatus.MISSING_EXTERNAL_EVIDENCE))
    all_classified = all(classify_bucket(s) for s in OperationalStatus)
    check("taxonomy: every OperationalStatus member classifies without raising", all_classified, "")


def _finding(fid, reqs_and_rel, locs=()):
    return GroundTruthFinding(finding_id=fid, audit_id="test-audit", correspondences=tuple(reqs_and_rel), ground_truth_locations=tuple(locs))


def _result(req_id, applicability, conformance=None, evidence=(), op_status=OperationalStatus.OK):
    return RoutedRequirementResult(req_id=req_id, applicability_state=applicability, conformance_state=conformance, evidence=tuple(evidence), operational_status=op_status)


def test_routing_recall_and_precision():
    findings = [
        _finding("H-01", [("req-A", "DIRECT")]),
        _finding("H-02", [("req-B", "DIRECT")]),
    ]
    run = TargetRunResult(audit_id="test-audit", routed={
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE),
        "req-B": _result("req-B", ApplicabilityState.NOT_APPLICABLE),  # missed
        "req-C": _result("req-C", ApplicabilityState.APPLICABLE),  # unjustified fire
    })
    recall = requirement_routing_recall(run, findings)
    precision = requirement_routing_precision(run, findings)
    check("routing_recall: 1 of 2 DIRECT requirements correctly routed", recall == (1, 2), recall)
    check("routing_precision: 1 of 2 routed requirements justified (req-A, req-C fired; only req-A justified)", precision == (1, 2), precision)


def test_routing_metrics_exclude_operational_failures():
    findings = [_finding("H-01", [("req-A", "DIRECT")])]
    run = TargetRunResult(audit_id="test-audit", routed={
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, op_status=OperationalStatus.COMPILATION_FAILURE),
    })
    recall = requirement_routing_recall(run, findings)
    check("routing_recall: an operationally-failed result does not count as a routing hit (excluded, not penalized)", recall == (0, 1), recall)


def test_evidence_collection_recall_vs_final_finding_recall():
    findings = [
        _finding("H-01", [("req-A", "DIRECT")]),
        _finding("H-02", [("req-B", "DIRECT")]),
    ]
    run = TargetRunResult(audit_id="test-audit", routed={
        # req-A: evidence collected but L8 judged it PASS (a semantic-judgment miss, not an evidence-collection miss)
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, ConformanceState.PASS, evidence=[EvidenceItem("pred", "C.f")]),
        # req-B: routed correctly but NO evidence at all (an evidence-collection miss)
        "req-B": _result("req-B", ApplicabilityState.APPLICABLE, ConformanceState.INSUFFICIENT_EVIDENCE, evidence=[]),
    })
    ev_recall = evidence_collection_recall(run, findings)
    final_recall = final_finding_recall(run, findings)
    check("evidence_collection_recall: req-A counts (evidence exists) even though judgment was wrong", ev_recall == (1, 2), ev_recall)
    check("final_finding_recall: NEITHER counts (req-A judged PASS not FAIL, req-B has no evidence)", final_recall == (0, 2), final_recall)


def test_target_localization_accuracy():
    findings = [
        _finding("H-01", [("req-A", "DIRECT")], locs=["Vault.sol", "Vault._burn"]),
    ]
    run_correct = TargetRunResult(audit_id="a", routed={
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, evidence=[EvidenceItem("pred", "Vault._burn")]),
    })
    run_wrong = TargetRunResult(audit_id="a", routed={
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, evidence=[EvidenceItem("pred", "PrizePool.claim")]),
    })
    run_no_evidence = TargetRunResult(audit_id="a", routed={
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, evidence=[]),
    })
    # Regression case for a REAL bug this project's own first evaluation run
    # caught: evidence in the SAME contract but a DIFFERENT function must be
    # a MISS, not a hit -- an earlier version of this metric compared only
    # the contract-name prefix and would have wrongly scored this as a match.
    run_same_contract_wrong_function = TargetRunResult(audit_id="a", routed={
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, evidence=[EvidenceItem("pred", "Vault.withdraw")]),
    })
    check("localization: matching contract/function location counts as a hit", target_localization_accuracy(run_correct, findings) == (1, 1), target_localization_accuracy(run_correct, findings))
    check("localization: non-matching location counts as a miss", target_localization_accuracy(run_wrong, findings) == (0, 1), target_localization_accuracy(run_wrong, findings))
    check("localization: SAME contract but a DIFFERENT function is a miss, not a hit", target_localization_accuracy(run_same_contract_wrong_function, findings) == (0, 1), target_localization_accuracy(run_same_contract_wrong_function, findings))
    check("localization: no evidence at all is EXCLUDED from the denominator, not a miss", target_localization_accuracy(run_no_evidence, findings) == (0, 0), target_localization_accuracy(run_no_evidence, findings))


def test_false_alert_rate():
    findings = [
        _finding("H-01", [("req-A", "DIRECT")]),
        _finding("H-02", [("req-B", "PARTIAL")]),
    ]
    run = TargetRunResult(audit_id="a", routed={
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, ConformanceState.FAIL),  # justified (DIRECT)
        "req-B": _result("req-B", ApplicabilityState.APPLICABLE, ConformanceState.FAIL),  # justified (PARTIAL still counts here)
        "req-C": _result("req-C", ApplicabilityState.APPLICABLE, ConformanceState.FAIL),  # unjustified -- no correspondence at all
    })
    rate = false_alert_rate(run, findings)
    check("false_alert_rate: 1 of 3 FAILs is unjustified (req-C has no correspondence record at all)", rate == (1, 3), rate)


def test_inconclusive_and_insufficient_evidence_rate():
    run = TargetRunResult(audit_id="a", routed={
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, ConformanceState.INCONCLUSIVE),
        "req-B": _result("req-B", ApplicabilityState.APPLICABLE, ConformanceState.INSUFFICIENT_EVIDENCE),
        "req-C": _result("req-C", ApplicabilityState.APPLICABLE, ConformanceState.PASS),
        "req-D": _result("req-D", ApplicabilityState.NOT_APPLICABLE),  # excluded -- not applicable at all
    })
    check("inconclusive_rate: 1 of 3 applicable results is INCONCLUSIVE", inconclusive_rate(run) == (1, 3), inconclusive_rate(run))
    check("insufficient_evidence_rate: 1 of 3 applicable results is INSUFFICIENT_EVIDENCE", insufficient_evidence_rate(run) == (1, 3), insufficient_evidence_rate(run))


def test_applicability_recall_alias_matches_routing_recall():
    findings = [_finding("H-01", [("req-A", "DIRECT")])]
    run = TargetRunResult(audit_id="a", routed={"req-A": _result("req-A", ApplicabilityState.APPLICABLE)})
    check("applicability_recall_on_known_applicable: matches requirement_routing_recall (documented as recall-only, not full accuracy)", applicability_recall_on_known_applicable(run, findings) == requirement_routing_recall(run, findings), "")


def test_empty_ground_truth_returns_zero_over_zero_not_a_crash():
    run = TargetRunResult(audit_id="a", routed={"req-A": _result("req-A", ApplicabilityState.APPLICABLE)})
    check("empty findings: routing_recall returns (0, 0), does not raise", requirement_routing_recall(run, []) == (0, 0), requirement_routing_recall(run, []))
    check("empty findings: evidence_collection_recall returns (0, 0), does not raise", evidence_collection_recall(run, []) == (0, 0), evidence_collection_recall(run, []))


def main() -> int:
    tests = [
        test_failure_taxonomy_classification,
        test_routing_recall_and_precision,
        test_routing_metrics_exclude_operational_failures,
        test_evidence_collection_recall_vs_final_finding_recall,
        test_target_localization_accuracy,
        test_false_alert_rate,
        test_inconclusive_and_insufficient_evidence_rate,
        test_applicability_recall_alias_matches_routing_recall,
        test_empty_ground_truth_returns_zero_over_zero_not_a_crash,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
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
