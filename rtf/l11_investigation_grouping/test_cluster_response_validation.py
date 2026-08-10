"""Unit tests for rtf.l11_investigation_grouping.cluster_response_validation.
Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_cluster_response_validation
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.cluster_response_validation import (
    property_counterexample_is_sufficient, resolve_property_verdicts, validate_cluster_response,
)
from rtf.l12_evaluation.metrics import ConformanceState

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


_GOOD_PASS_ENTRY = {
    "property_id": "P001", "verdict": "PASS",
    "counterexample_attempt": "Considered whether amount=0 or amount>balance could bypass the check.",
    "counterexample_result": "Confirmed require(amount<=balance) blocks both cases.",
    "reasoning": "Traced amount through withdraw() and confirmed the bound.",
}


def _entry(pid: str, verdict: str = "PASS", **overrides) -> dict:
    e = {**_GOOD_PASS_ENTRY, "property_id": pid, "verdict": verdict}
    e.update(overrides)
    return e


# --- validate_cluster_response: completeness --------------------------------

def test_exact_match_is_complete():
    response = {"properties": [_entry("P001"), _entry("P002")]}
    result = validate_cluster_response(["P001", "P002"], response)
    check("exact match: complete", result.complete, result)
    check("exact match: no issues", result.issues == (), result.issues)


def test_missing_property_detected():
    response = {"properties": [_entry("P001")]}
    result = validate_cluster_response(["P001", "P002"], response)
    check("missing property: not complete", not result.complete)
    check("missing property: P002 named", result.missing_property_ids == ("P002",), result.missing_property_ids)


def test_duplicate_property_detected():
    response = {"properties": [_entry("P001"), _entry("P001")]}
    result = validate_cluster_response(["P001"], response)
    check("duplicate property: not complete", not result.complete)
    check("duplicate property: P001 named", result.duplicate_property_ids == ("P001",), result.duplicate_property_ids)


def test_unrecognized_property_detected():
    response = {"properties": [_entry("P001"), _entry("P999")]}
    result = validate_cluster_response(["P001"], response)
    check("unrecognized property: not complete", not result.complete)
    check("unrecognized property: P999 named", result.unrecognized_property_ids == ("P999",), result.unrecognized_property_ids)


def test_entry_missing_property_id_field_detected():
    response = {"properties": [_entry("P001"), {"verdict": "PASS"}]}
    result = validate_cluster_response(["P001"], response)
    check("entry with no property_id field: not complete", not result.complete)
    check("entry with no property_id field: counted", result.entries_missing_property_id_field == 1, result)


def test_malformed_response_missing_properties_key():
    result = validate_cluster_response(["P001", "P002"], {"something_else": []})
    check("malformed response: not complete", not result.complete)
    check("malformed response: all expected ids reported missing", set(result.missing_property_ids) == {"P001", "P002"}, result)


def test_none_response_handled_without_crash():
    result = validate_cluster_response(["P001"], None)
    check("None response: not complete, no crash", not result.complete)


def test_empty_expected_list_with_empty_response_is_complete():
    result = validate_cluster_response([], {"properties": []})
    check("empty expected + empty response: complete", result.complete)


# --- duplicated-reasoning detection (implicit verdict inheritance) ---------

def test_identical_reasoning_across_properties_flagged():
    response = {"properties": [
        _entry("P001", reasoning="Everything looks fine here."),
        _entry("P002", reasoning="Everything looks fine here."),
        _entry("P003", reasoning="A genuinely distinct analysis for P003."),
    ]}
    result = validate_cluster_response(["P001", "P002", "P003"], response)
    check("identical reasoning group detected", ("P001", "P002") in result.duplicated_reasoning_groups, result.duplicated_reasoning_groups)
    check("distinct reasoning NOT flagged", not any("P003" in g for g in result.duplicated_reasoning_groups), result.duplicated_reasoning_groups)
    check("duplicated reasoning does not, by itself, make the response incomplete", result.complete, result)


def test_no_duplicated_reasoning_when_all_distinct():
    response = {"properties": [
        _entry("P001", reasoning="Analysis A."),
        _entry("P002", reasoning="Analysis B."),
    ]}
    result = validate_cluster_response(["P001", "P002"], response)
    check("no duplicated reasoning groups", result.duplicated_reasoning_groups == (), result.duplicated_reasoning_groups)


# --- property_counterexample_is_sufficient ----------------------------------

def test_well_formed_pass_is_sufficient():
    sufficient, reason = property_counterexample_is_sufficient(_entry("P001"))
    check("well-formed PASS: sufficient", sufficient, reason)


def test_pass_without_counterexample_attempt_is_insufficient():
    entry = _entry("P001", counterexample_attempt="")
    sufficient, reason = property_counterexample_is_sufficient(entry)
    check("empty counterexample_attempt: insufficient", not sufficient)
    check("reason names the specific gap", reason == "counterexample_attempt_too_thin", reason)


def test_pass_with_thin_counterexample_result_is_insufficient():
    entry = _entry("P001", counterexample_result="ok")
    sufficient, reason = property_counterexample_is_sufficient(entry)
    check("thin counterexample_result: insufficient", not sufficient)
    check("reason names the specific gap", reason == "counterexample_result_too_thin", reason)


def test_fail_does_not_require_counterexample_fields():
    entry = {"property_id": "P001", "verdict": "FAIL"}
    sufficient, reason = property_counterexample_is_sufficient(entry)
    check("FAIL: no counterexample requirement", sufficient, reason)


def test_inconclusive_does_not_require_counterexample_fields():
    entry = {"property_id": "P001", "verdict": "INCONCLUSIVE"}
    sufficient, reason = property_counterexample_is_sufficient(entry)
    check("INCONCLUSIVE: no counterexample requirement", sufficient, reason)


# --- resolve_property_verdicts: independence + counterexample gating -------

def test_each_property_resolved_independently():
    response = {"properties": [
        _entry("P001", verdict="FAIL"),
        _entry("P002", verdict="PASS"),  # well-formed, from _GOOD_PASS_ENTRY defaults
    ]}
    resolved = resolve_property_verdicts(response)
    check("P001 resolves to FAIL", resolved["P001"].conformance_state == ConformanceState.FAIL, resolved["P001"])
    check("P002 resolves to PASS (independently, not inheriting P001's FAIL)",
          resolved["P002"].conformance_state == ConformanceState.PASS, resolved["P002"])


def test_pass_without_sufficient_counterexample_downgraded_per_property():
    response = {"properties": [
        _entry("P001", verdict="PASS"),  # well-formed
        _entry("P002", verdict="PASS", counterexample_attempt="none"),  # thin
    ]}
    resolved = resolve_property_verdicts(response)
    check("P001 (well-formed PASS) stays PASS", resolved["P001"].conformance_state == ConformanceState.PASS)
    check("P002 (thin counterexample) downgraded to INCONCLUSIVE", resolved["P002"].conformance_state == ConformanceState.INCONCLUSIVE)
    check("P002's downgrade reason is specific", "insufficient_reasoning_rigor" in resolved["P002"].reason, resolved["P002"].reason)
    check("P001's downgrade did NOT affect P002's independent verdict resolution or vice versa (both computed)",
          "P001" in resolved and "P002" in resolved)


def test_unknown_verdict_value_resolves_to_inconclusive_with_reason():
    entry = {"property_id": "P001", "verdict": "MAYBE"}
    resolved = resolve_property_verdicts({"properties": [entry]})
    check("unknown verdict value: INCONCLUSIVE", resolved["P001"].conformance_state == ConformanceState.INCONCLUSIVE)
    check("unknown verdict value: reason names it", resolved["P001"].reason == "unknown_verdict:MAYBE", resolved["P001"].reason)


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
