"""Unit tests for the pure, non-network parts of judge_with_l8.py
(question rendering, decision mapping). judge_result()/judge_run()
themselves require a real LLM call and are exercised live instead (see
rtf/l8_llm_judgment_layer/live_validation/03_*), not here.
Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_judge_with_l8
"""
from __future__ import annotations

import sys

from .judge_with_l8 import _DECISION_TO_CONFORMANCE, build_judgment_question
from .metrics import ConformanceState, EvidenceItem

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def test_plain_detail_evidence_renders_as_before():
    ev = [EvidenceItem(predicate="p", location="C.f", detail="some plain finding")]
    q = build_judgment_question(ev)
    check("question: plain-detail evidence (no structured field) renders the old one-line form", "- C.f: some plain finding" in q, q)


def test_structured_evidence_renders_all_fields():
    ev = [EvidenceItem(
        predicate="find_unsafe_narrowing_cast",
        location="Ledger.record",
        detail="unchecked narrowing cast",
        structured={
            "operation": "narrowing type conversion uint256 -> uint96",
            "input": {"name": "_amount", "type": "uint256"},
            "source_type": "uint256",
            "destination_type": "uint96",
            "validation_found": "none",
            "missing_safety_condition": "_amount <= type(uint96).max",
            "risk": "values above uint96's max are truncated",
            "affected_functions": ["Ledger.record"],
        },
    )]
    q = build_judgment_question(ev)
    check("question: structured evidence includes the operation", "narrowing type conversion uint256 -> uint96" in q, q)
    check("question: structured evidence includes the input", "_amount, type uint256" in q, q)
    check("question: structured evidence includes validation_found", "Validation found: none" in q, q)
    check("question: structured evidence includes missing_safety_condition", "_amount <= type(uint96).max" in q, q)
    check("question: structured evidence includes risk", "truncated" in q, q)
    check("question: structured evidence includes affected_functions", "Ledger.record" in q, q)
    check("question: structured evidence does NOT also print the bare 'detail' redundantly", "unchecked narrowing cast" not in q, q)


def test_structured_evidence_handles_missing_optional_fields_gracefully():
    ev = [EvidenceItem(
        predicate="find_unchecked_ecrecover_result",
        location="Auth._recoverSigner",
        detail="ecrecover result used without an intermediate named variable",
        structured={
            "operation": "ecrecover(...)",
            "possible_result": "address(0) for an invalid/malformed signature",
            "validation_found": "UNKNOWN -- result not assigned to a traceable named variable",
            "risk": "cannot be determined by this predicate; requires manual/semantic review",
        },
    )]
    q = build_judgment_question(ev)
    check("question: partial structured evidence (no input/missing_safety_condition/affected_functions) does not crash", "ecrecover(...)" in q, q)
    check("question: partial structured evidence still shows validation_found", "UNKNOWN" in q, q)


def test_evidence_cap_still_applies_to_structured_evidence():
    ev = [EvidenceItem(predicate="p", location=f"C.f{i}", detail=f"finding {i}") for i in range(35)]
    q = build_judgment_question(ev, max_items=30)
    check("question: caps at max_items even with a large evidence list", "C.f29" in q and "C.f30" not in q, q)
    check("question: states how many items were omitted", "5 more" in q, q)


def test_decision_to_conformance_covers_all_four_canonical_states():
    expected = {"PASS": ConformanceState.PASS, "FAIL": ConformanceState.FAIL, "INCONCLUSIVE": ConformanceState.INCONCLUSIVE, "INSUFFICIENT_EVIDENCE": ConformanceState.INSUFFICIENT_EVIDENCE}
    check("decision_mapping: all 4 canonical L8 decisions map to the correct ConformanceState", _DECISION_TO_CONFORMANCE == expected, _DECISION_TO_CONFORMANCE)


def main() -> int:
    tests = [
        test_plain_detail_evidence_renders_as_before,
        test_structured_evidence_renders_all_fields,
        test_structured_evidence_handles_missing_optional_fields_gracefully,
        test_evidence_cap_still_applies_to_structured_evidence,
        test_decision_to_conformance_covers_all_four_canonical_states,
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
