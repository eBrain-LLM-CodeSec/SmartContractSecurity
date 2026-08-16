"""Deterministic tests for Increment 5's completion gate."""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.taxonomy import ReasoningCategory
from rtf.security_agent.completion import check_property_completion, cluster_can_conclude
from rtf.security_agent.state import (
    ClusterInvestigationState, Evidence, Hypothesis, HypothesisStatus,
    RequirementResolution,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail=""):
    (PASSES if condition else FAILURES).append(name if condition else f"{name}: {detail}")


def _pass_state(attempt: str = "unauthorized caller invokes the owner-only function"):
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.record_tool_call("get_function_source", {"contract": "Vault", "function": "setOracle"},
                           "OK (source)", {"status": "OK", "file": "Vault.sol",
                                           "contract": "Vault", "name": "setOracle"})
    state.add_evidence(Evidence(id="ev1", claim="onlyOwner is applied",
                                source_file="Vault.sol", tool_call_id="tool-1"))
    state.add_hypothesis(Hypothesis(
        id="h1", claim="an unprivileged caller can set the oracle",
        originating_property_ids=["p1"], status=HypothesisStatus.REFUTED,
        contradicting_evidence_ids=["ev1"],
    ))
    state.record_counterexample_attempt("p1", "h1", attempt, "onlyOwner rejects the call")
    state.record_verdict(
        "p1", claim="oracle changes are access controlled", evidence_ids=["ev1"],
        hypothesis_ids=["h1"], interpretation="modifier refutes unauthorized access",
        verdict=RequirementResolution.PASS,
    )
    return state


def test_pass_requires_counterexample_attempt():
    state = _pass_state()
    state.requirement_states["p1"].counterexample_attempts.clear()
    result = check_property_completion(state, "p1")
    check("PASS without attempt blocked", not result.ready and
          "pass_without_counterexample_attempt" in result.blocking_reasons, result)


def test_pass_rejects_evidence_not_grounded_in_a_tool_call():
    state = _pass_state()
    state.evidence["ev1"].tool_call_id = None
    result = check_property_completion(state, "p1")
    check("ungrounded PASS evidence blocked", not result.ready and
          any("pass_evidence_not_from_recorded_tool" in r for r in result.blocking_reasons), result)


def test_pass_requires_resolved_hypothesis():
    state = _pass_state()
    state.hypotheses["h1"].status = HypothesisStatus.OPEN
    result = check_property_completion(state, "p1")
    check("PASS with OPEN hypothesis blocked", not result.ready and
          any("pass_with_unresolved_hypothesis" in r for r in result.blocking_reasons), result)


def test_access_control_requires_unprivileged_scenario():
    state = _pass_state("owner calls the owner-only function")
    result = check_property_completion(state, "p1", ReasoningCategory.ACCESS_PRIVILEGE_CONTROL)
    check("owner-only happy path is not a sufficient access-control counterexample", not result.ready, result)


def test_complete_access_control_pass_is_ready():
    state = _pass_state()
    result = cluster_can_conclude(state, {"p1": ReasoningCategory.ACCESS_PRIVILEGE_CONTROL})
    check("complete access-control PASS accepted", result.ready, result)


def test_fail_needs_ceiv_but_not_pass_counterexample_gate():
    state = _pass_state()
    state.requirement_states["p1"].counterexample_attempts.clear()
    state.requirement_states["p1"].status = RequirementResolution.FAIL
    state.requirement_states["p1"].final_assessment.verdict = RequirementResolution.FAIL
    result = check_property_completion(state, "p1", ReasoningCategory.ACCESS_PRIVILEGE_CONTROL)
    check("evidence-backed FAIL does not use PASS gate", result.ready, result)


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as exc:
                FAILURES.append(f"{name}: CRASHED -- {type(exc).__name__}: {exc}")
    print(f"PASSED: {len(PASSES)}")
    for item in PASSES:
        print(f"  ok - {item}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for item in FAILURES:
            print(f"  FAIL - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
