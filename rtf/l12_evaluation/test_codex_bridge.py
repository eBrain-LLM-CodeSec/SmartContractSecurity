"""Unit tests for codex_bridge.resolve_conformance_from_arm_g, focused on
the Phase 5 reasoning-rigor downgrade added on top of its pre-existing
timeout/no-decision/unknown-decision handling. Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_codex_bridge
"""
from __future__ import annotations

import sys

from rtf.l12_evaluation.codex_bridge import build_codex_prompt_inputs, resolve_conformance_from_arm_g
from rtf.l12_evaluation.metrics import ApplicabilityState, RoutedRequirementResult
from rtf.l12_evaluation.metrics import ConformanceState

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


# --- RTF_V3_REDESIGN_PLAN.md Phase 3, finding 2: legacy single-property path
# used to forward ONLY bare normative_text, dropping explanatory_text/
# exceptions/overrides even though the corpus carries them. Verify the fix
# without needing an on-disk L2 bundle file (same in-memory bundle_record
# seam standards/routing.py already uses for generated requirements). ------

def test_build_codex_prompt_inputs_carries_exception_text_for_real_requirement():
    """req-1-no-tx.origin's real corpus record has a real, non-empty
    `overriding_requirements`/`exceptions_referenced` entry
    (req-3-verify-tx.origin) -- this must now reach `requirement_text`,
    not just the bare normative sentence."""
    result = RoutedRequirementResult(
        req_id="req-1-no-tx.origin",
        applicability_state=ApplicabilityState.APPLICABLE,
        evidence=(),
    )
    inputs = build_codex_prompt_inputs(
        req_id="req-1-no-tx.origin",
        candidate_location="Foo.sol:bar",
        result=result,
        repo_root=None,
        bundle_record={"bundle": {"self": "No tx.origin fallback bundle text"}},
    )
    check(
        "requirement_text includes the bare normative text",
        "tx.origin" in inputs.requirement_text,
        inputs.requirement_text,
    )
    check(
        "requirement_text now carries the exception cross-reference (was previously dropped)",
        "req-3-verify-tx.origin" in inputs.requirement_text,
        inputs.requirement_text,
    )
    check(
        "requirement_text explanatory text (SWC-115) now included",
        "SWC-115" in inputs.requirement_text,
        inputs.requirement_text,
    )


def test_build_codex_prompt_inputs_falls_back_when_req_id_not_in_corpus():
    result = RoutedRequirementResult(
        req_id="req-not-a-real-requirement",
        applicability_state=ApplicabilityState.APPLICABLE,
        evidence=(),
    )
    inputs = build_codex_prompt_inputs(
        req_id="req-not-a-real-requirement",
        candidate_location="Foo.sol:bar",
        result=result,
        repo_root=None,
        bundle_record={"bundle": {"self": "fallback bundle self text"}},
    )
    check(
        "unknown req_id falls back to bundle['self'] rather than crashing",
        inputs.requirement_text == "fallback bundle self text",
        inputs.requirement_text,
    )


_GOOD_SEARCH = {
    "attempted": True,
    "violation_scenario_considered": "A caller supplies a malformed signature whose ecrecover result is address(0).",
    "checks_performed": "Confirmed the require(signer != address(0)) check runs immediately after ecrecover.",
    "found_violation": False,
}


# --- pre-existing behavior, unaffected by the Phase 5 change ---------------

def test_timeout_still_inconclusive_with_codex_timeout_reason():
    outcome = resolve_conformance_from_arm_g({"decision": "PASS"}, timed_out=True)
    check("timeout: INCONCLUSIVE", outcome.conformance_state == ConformanceState.INCONCLUSIVE)
    check("timeout: reason is codex_timeout", outcome.reason == "codex_timeout", outcome.reason)


def test_missing_decision_still_inconclusive():
    outcome = resolve_conformance_from_arm_g(None, timed_out=False)
    check("no final_decision: INCONCLUSIVE", outcome.conformance_state == ConformanceState.INCONCLUSIVE)
    check("no final_decision: reason is codex_no_decision", outcome.reason == "codex_no_decision", outcome.reason)


def test_fail_decision_unaffected_by_rigor_check():
    outcome = resolve_conformance_from_arm_g({"decision": "FAIL", "reasoning_summary": "found it"}, timed_out=False)
    check("FAIL: passes through unchanged, no rigor check applied", outcome.conformance_state == ConformanceState.FAIL)
    check("FAIL: no reason code (genuine decision)", outcome.reason is None, outcome.reason)


def test_inconclusive_decision_unaffected_by_rigor_check():
    outcome = resolve_conformance_from_arm_g({"decision": "INCONCLUSIVE"}, timed_out=False)
    check("INCONCLUSIVE: passes through unchanged", outcome.conformance_state == ConformanceState.INCONCLUSIVE)
    check("INCONCLUSIVE: no reason code", outcome.reason is None, outcome.reason)


# --- new Phase 5 rigor-gated PASS behavior ----------------------------------

def test_pass_with_good_counterexample_search_stays_pass():
    outcome = resolve_conformance_from_arm_g(
        {"decision": "PASS", "counterexample_search": _GOOD_SEARCH, "reasoning_summary": "ok"}, timed_out=False,
    )
    check("PASS with real search: stays PASS", outcome.conformance_state == ConformanceState.PASS)
    check("PASS with real search: no reason code", outcome.reason is None, outcome.reason)


def test_pass_without_counterexample_search_is_downgraded():
    outcome = resolve_conformance_from_arm_g({"decision": "PASS", "reasoning_summary": "looked fine"}, timed_out=False)
    check("PASS without search: downgraded to INCONCLUSIVE", outcome.conformance_state == ConformanceState.INCONCLUSIVE)
    check("PASS without search: reason names the rigor gap",
          outcome.reason == "insufficient_reasoning_rigor:counterexample_search_missing", outcome.reason)
    check("PASS without search: reasoning_summary still preserved for observability",
          outcome.reasoning_summary == "looked fine", outcome.reasoning_summary)


def test_pass_with_thin_counterexample_search_is_downgraded():
    thin = {**_GOOD_SEARCH, "checks_performed": "checked"}
    outcome = resolve_conformance_from_arm_g({"decision": "PASS", "counterexample_search": thin}, timed_out=False)
    check("PASS with thin search: downgraded to INCONCLUSIVE", outcome.conformance_state == ConformanceState.INCONCLUSIVE)
    check("PASS with thin search: reason names the specific gap",
          outcome.reason == "insufficient_reasoning_rigor:counterexample_search_checks_too_thin", outcome.reason)


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
