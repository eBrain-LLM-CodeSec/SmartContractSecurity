"""Unit tests for reasoning_rigor.counterexample_search_is_sufficient.
Run with:
    .venv/bin/python3 -m rtf.l8_llm_judgment_layer.bundle_agent_experiment.test_reasoning_rigor
"""
from __future__ import annotations

import sys

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.reasoning_rigor import counterexample_search_is_sufficient

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


_GOOD_SEARCH = {
    "attempted": True,
    "violation_scenario_considered": "A caller supplies amount=0 or amount > totalSupply to trigger an underflow.",
    "checks_performed": "Traced amount through _burn and confirmed require(amount <= balance) bounds it before use.",
    "found_violation": False,
}


def test_well_formed_search_is_sufficient():
    decision = {"decision": "PASS", "counterexample_search": _GOOD_SEARCH}
    sufficient, reason = counterexample_search_is_sufficient(decision)
    check("well-formed search: sufficient", sufficient, reason)
    check("well-formed search: no failure reason", reason is None, reason)


def test_missing_field_entirely_is_insufficient():
    decision = {"decision": "PASS"}
    sufficient, reason = counterexample_search_is_sufficient(decision)
    check("missing field: insufficient", not sufficient)
    check("missing field: correct reason code", reason == "counterexample_search_missing", reason)


def test_not_a_dict_is_insufficient():
    decision = {"decision": "PASS", "counterexample_search": "I checked it"}
    sufficient, reason = counterexample_search_is_sufficient(decision)
    check("string instead of dict: insufficient", not sufficient)
    check("string instead of dict: correct reason code", reason == "counterexample_search_missing", reason)


def test_attempted_false_is_insufficient():
    decision = {"decision": "PASS", "counterexample_search": {**_GOOD_SEARCH, "attempted": False}}
    sufficient, reason = counterexample_search_is_sufficient(decision)
    check("attempted=False: insufficient", not sufficient)
    check("attempted=False: correct reason code", reason == "counterexample_search_not_attempted", reason)


def test_attempted_missing_is_insufficient():
    search = {k: v for k, v in _GOOD_SEARCH.items() if k != "attempted"}
    decision = {"decision": "PASS", "counterexample_search": search}
    sufficient, reason = counterexample_search_is_sufficient(decision)
    check("attempted key absent: insufficient", not sufficient)
    check("attempted key absent: correct reason code", reason == "counterexample_search_not_attempted", reason)


def test_thin_scenario_description_is_insufficient():
    decision = {"decision": "PASS", "counterexample_search": {**_GOOD_SEARCH, "violation_scenario_considered": "none"}}
    sufficient, reason = counterexample_search_is_sufficient(decision)
    check("thin scenario text: insufficient", not sufficient)
    check("thin scenario text: correct reason code", reason == "counterexample_search_scenario_too_thin", reason)


def test_thin_checks_description_is_insufficient():
    decision = {"decision": "PASS", "counterexample_search": {**_GOOD_SEARCH, "checks_performed": "n/a"}}
    sufficient, reason = counterexample_search_is_sufficient(decision)
    check("thin checks text: insufficient", not sufficient)
    check("thin checks text: correct reason code", reason == "counterexample_search_checks_too_thin", reason)


def test_missing_scenario_key_is_insufficient():
    search = {k: v for k, v in _GOOD_SEARCH.items() if k != "violation_scenario_considered"}
    decision = {"decision": "PASS", "counterexample_search": search}
    sufficient, reason = counterexample_search_is_sufficient(decision)
    check("scenario key absent: insufficient", not sufficient)
    check("scenario key absent: correct reason code", reason == "counterexample_search_scenario_too_thin", reason)


def test_found_violation_true_with_pass_decision_is_flagged_as_inconsistent():
    decision = {"decision": "PASS", "counterexample_search": {**_GOOD_SEARCH, "found_violation": True}}
    sufficient, reason = counterexample_search_is_sufficient(decision)
    check("found_violation=True but decision=PASS: insufficient (internal inconsistency)", not sufficient)
    check("inconsistency: correct reason code",
          reason == "counterexample_search_found_violation_but_decision_was_pass", reason)


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
