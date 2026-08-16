"""Unit tests for rtf.l11_investigation_grouping.cluster_response_validation.
Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_cluster_response_validation
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.cluster_response_validation import (
    parent_obligation_check_is_sufficient, property_counterexample_is_sufficient,
    resolve_property_verdicts, validate_cluster_response,
)
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
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


# --- RTF_V3_REDESIGN_PLAN.md Phase 4: parent_obligation_check gate ----------

def _prop(pid: str, parent_requirement_id: str | None) -> PropertyMetadata:
    return PropertyMetadata(
        property_id=pid, requirement_id=f"semantic__accounting__{pid}", requirement_level="SEMANTIC",
        requirement_semantic_intent="test", property_text="Vault.totalAssets must be correct.",
        target_contract="Vault", target_function="totalAssets",
        source_provenance="semantic_derivation", parent_requirement_id=parent_requirement_id,
    )


def test_parent_obligation_check_not_required_when_no_parent_linked():
    ok, reason = parent_obligation_check_is_sufficient(_entry("P001"), has_parent_requirement=False)
    check("no parent linked: always sufficient regardless of the field", ok, reason)


def test_parent_obligation_check_not_required_for_non_pass_verdicts():
    ok, reason = parent_obligation_check_is_sufficient(_entry("P001", verdict="FAIL"), has_parent_requirement=True)
    check("FAIL with parent linked: not required (only PASS is dual-checked)", ok, reason)


def test_parent_obligation_check_missing_downgrades_a_pass_with_linked_parent():
    entry = _entry("P001")  # no parent_obligation_check field at all
    ok, reason = parent_obligation_check_is_sufficient(entry, has_parent_requirement=True)
    check("PASS with parent linked but field missing: insufficient", not ok, reason)
    check("reason names the gap", reason == "parent_obligation_check_missing_or_too_thin", reason)


def test_parent_obligation_check_trivial_na_downgrades_when_parent_actually_linked():
    # Long enough to clear the bare-length check on its own -- this is
    # specifically the schema's OWN legitimate "no parent" escape-hatch
    # phrase, reused here despite a real parent being linked -- distinct
    # from a merely-too-short answer like bare "N/A".
    entry = _entry("P001", parent_obligation_check="N/A - no parent requirement linked")
    ok, reason = parent_obligation_check_is_sufficient(entry, has_parent_requirement=True)
    check("PASS falsely claiming N/A despite a real linked parent: insufficient", not ok, reason)
    check("reason distinguishes this from a bare missing/thin field", reason == "parent_obligation_check_falsely_claims_no_parent", reason)


def test_parent_obligation_check_bare_short_na_caught_by_length_check_first():
    """A too-short placeholder ("N/A" alone, 3 chars) is caught by the
    ordinary length floor before ever reaching the trivial-value check --
    both are real rejections, just via the more fundamental reason."""
    entry = _entry("P001", parent_obligation_check="N/A")
    ok, reason = parent_obligation_check_is_sufficient(entry, has_parent_requirement=True)
    check("bare short N/A still rejected", not ok, reason)
    check("rejected via the length check, not the trivial-phrase check", reason == "parent_obligation_check_missing_or_too_thin", reason)


def test_parent_obligation_check_genuine_na_accepted_when_no_parent_linked():
    entry = _entry("P001", parent_obligation_check="N/A - no parent requirement linked")
    ok, reason = parent_obligation_check_is_sufficient(entry, has_parent_requirement=False)
    check("genuine N/A accepted when there really is no parent", ok, reason)


def test_parent_obligation_check_real_engagement_accepted():
    entry = _entry(
        "P001",
        parent_obligation_check=(
            "Parent req-2-check-rounding also requires no biased rounding; "
            "confirmed totalAssets rounds down consistently, so the parent "
            "obligation is also satisfied, not just this property's own statement."
        ),
    )
    ok, reason = parent_obligation_check_is_sufficient(entry, has_parent_requirement=True)
    check("real engagement with the parent obligation is accepted", ok, reason)


def test_resolve_property_verdicts_downgrades_pass_missing_parent_obligation_check():
    properties_by_id = {"P001": _prop("P001", parent_requirement_id="req-2-check-rounding")}
    response = {"properties": [_entry("P001")]}  # no parent_obligation_check field
    resolved = resolve_property_verdicts(response, properties_by_id)
    check(
        "PASS on a parent-linked property with no parent_obligation_check downgrades to INCONCLUSIVE",
        resolved["P001"].conformance_state == ConformanceState.INCONCLUSIVE, resolved["P001"],
    )
    check(
        "downgrade reason is the parent-obligation-specific one",
        "parent_obligation_check" in (resolved["P001"].reason or ""), resolved["P001"].reason,
    )


def test_resolve_property_verdicts_stays_pass_when_no_parent_linked():
    properties_by_id = {"P001": _prop("P001", parent_requirement_id=None)}
    response = {"properties": [_entry("P001")]}
    resolved = resolve_property_verdicts(response, properties_by_id)
    check("no parent linked: PASS is not downgraded by the new gate", resolved["P001"].conformance_state == ConformanceState.PASS, resolved["P001"])


def test_resolve_property_verdicts_without_properties_by_id_arg_is_unaffected():
    """Omitting `properties_by_id` entirely (every pre-existing caller,
    and any future caller that doesn't have it) must behave EXACTLY as
    before this Phase 4 change -- no parent-obligation gate applied at
    all, since there's nothing to know a parent even exists."""
    response = {"properties": [_entry("P001")]}
    resolved = resolve_property_verdicts(response)
    check("no properties_by_id given: PASS stays PASS, prior behavior preserved", resolved["P001"].conformance_state == ConformanceState.PASS, resolved["P001"])


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
