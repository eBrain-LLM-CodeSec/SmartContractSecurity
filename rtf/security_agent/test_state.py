"""Unit tests for rtf.security_agent.state. Synthetic data only. Run with:
    .venv/bin/python3 -m rtf.security_agent.test_state
"""
from __future__ import annotations

import sys

from rtf.security_agent.state import (
    ClusterInvestigationState, DuplicateIdError, Evidence, Hypothesis,
    HypothesisStatus, RequirementResolution, UnknownEvidenceIdError,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _evidence(eid: str, **overrides) -> Evidence:
    base = dict(id=eid, claim="test claim", source_file="Foo.sol",
                source_contract="Foo", source_function="bar")
    base.update(overrides)
    return Evidence(**base)


# --- initial state / requirement resolution -----------------------------------

def test_initial_state_has_one_unresolved_requirement_per_property():
    state = ClusterInvestigationState.initial("c1", ["p1", "p2", "p3"])
    check("3 requirement_states created", len(state.requirement_states) == 3, state.requirement_states)
    check("all UNRESOLVED", all(rs.status == RequirementResolution.UNRESOLVED
                                 for rs in state.requirement_states.values()))
    check("not all_resolved()", state.all_resolved() is False)


def test_transition_unresolved_to_pass():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.resolve_requirement("p1", RequirementResolution.PASS, reason="no violation found")
    check("status is PASS", state.requirement_states["p1"].status == RequirementResolution.PASS)
    check("reason recorded", state.requirement_states["p1"].resolution_reason == "no violation found")
    check("all_resolved() true", state.all_resolved() is True)


def test_transition_unresolved_to_fail():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.resolve_requirement("p1", RequirementResolution.FAIL, reason="counterexample found")
    check("status is FAIL", state.requirement_states["p1"].status == RequirementResolution.FAIL)


def test_resolve_unknown_property_id_raises():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    try:
        state.resolve_requirement("does-not-exist", RequirementResolution.PASS)
        check("raises KeyError", False, "did not raise")
    except KeyError:
        check("raises KeyError", True)


# --- shared evidence across requirements in one cluster -----------------------

def test_evidence_shared_across_two_requirements_in_same_cluster():
    """The core "shared evidence" invariant: one Evidence object, added
    once, referenced by id from TWO different RequirementStates -- not
    duplicated, and mutating the shared object once is visible from both
    property_ids' evidence lists."""
    state = ClusterInvestigationState.initial("c1", ["p1", "p2"])
    ev = _evidence("ev1", claim="GaugeController reads block.number where caller passes a timestamp")
    state.add_evidence(ev)
    state.link_evidence_to_requirement("p1", "ev1", supports=False)
    state.link_evidence_to_requirement("p2", "ev1", supports=False)

    p1_evidence = state.evidence_against("p1")
    p2_evidence = state.evidence_against("p2")
    check("evidence reachable from p1", len(p1_evidence) == 1 and p1_evidence[0].id == "ev1")
    check("SAME evidence reachable from p2", len(p2_evidence) == 1 and p2_evidence[0].id == "ev1")
    check("only one Evidence object stored (not duplicated)", len(state.evidence) == 1)
    check("is the exact same object identity via id lookup",
          p1_evidence[0] is p2_evidence[0])


def test_link_to_unknown_evidence_id_raises():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    try:
        state.link_evidence_to_requirement("p1", "does-not-exist", supports=True)
        check("raises UnknownEvidenceIdError", False, "did not raise")
    except UnknownEvidenceIdError:
        check("raises UnknownEvidenceIdError", True)


def test_duplicate_evidence_id_raises():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.add_evidence(_evidence("ev1"))
    try:
        state.add_evidence(_evidence("ev1", claim="a different claim"))
        check("raises DuplicateIdError", False, "did not raise")
    except DuplicateIdError:
        check("raises DuplicateIdError", True)


def test_add_evidence_updates_inspected_sets():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.add_evidence(_evidence("ev1", source_file="Vault.sol", source_contract="Vault", source_function="withdraw"))
    check("file tracked", "Vault.sol" in state.inspected_files)
    check("contract tracked", "Vault" in state.inspected_contracts)
    check("function tracked", "Vault.withdraw" in state.inspected_functions)


# --- hypotheses -----------------------------------------------------------

def test_hypothesis_spans_multiple_originating_properties():
    state = ClusterInvestigationState.initial("c1", ["p1", "p2"])
    state.add_evidence(_evidence("ev1"))
    hyp = Hypothesis(id="h1", claim="cross-boundary unit mismatch", originating_property_ids=["p1", "p2"],
                      supporting_evidence_ids=["ev1"])
    state.add_hypothesis(hyp)
    check("hypothesis linked to p1", "h1" in state.requirement_states["p1"].hypothesis_ids)
    check("hypothesis linked to p2", "h1" in state.requirement_states["p2"].hypothesis_ids)
    check("status defaults to OPEN", state.hypotheses["h1"].status == HypothesisStatus.OPEN)


def test_hypothesis_with_unknown_evidence_id_raises():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    hyp = Hypothesis(id="h1", claim="x", supporting_evidence_ids=["missing"])
    try:
        state.add_hypothesis(hyp)
        check("raises UnknownEvidenceIdError", False, "did not raise")
    except UnknownEvidenceIdError:
        check("raises UnknownEvidenceIdError", True)


def test_duplicate_hypothesis_id_raises():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.add_hypothesis(Hypothesis(id="h1", claim="x"))
    try:
        state.add_hypothesis(Hypothesis(id="h1", claim="y"))
        check("raises DuplicateIdError", False, "did not raise")
    except DuplicateIdError:
        check("raises DuplicateIdError", True)


# --- tool bookkeeping -----------------------------------------------------

def test_record_tool_call_appends_history_and_increments_step_count():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.record_tool_call("get_function_source", {"contract": "Foo", "function": "bar"}, "returned 12 lines")
    state.record_tool_call("get_callers", {"contract": "Foo", "function": "bar"}, "2 callers found")
    check("2 tool calls recorded", len(state.tool_history) == 2)
    check("step_count incremented", state.step_count == 2)
    check("first call's tool name recorded", state.tool_history[0].tool == "get_function_source")
    check("tool calls receive stable sequential ids",
          [call.id for call in state.tool_history] == ["tool-1", "tool-2"])


def test_successful_source_tool_result_tracks_inspection():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.record_tool_call(
        "get_function_source", {"contract": "Vault", "function": "withdraw"}, "OK (source)",
        {"status": "OK", "file": "Vault.sol", "contract": "Vault", "name": "withdraw"},
    )
    check("tool result tracks inspected file", state.inspected_files == {"Vault.sol"})
    check("tool result tracks inspected contract", state.inspected_contracts == {"Vault"})
    check("tool result tracks inspected function", state.inspected_functions == {"Vault.withdraw"})


# --- find_duplicate_tool_call (kernel-controlled cached-result replay) -------

def test_find_duplicate_tool_call_exact_match():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    record = state.record_tool_call("get_contract_source", {"contract": "Vault"}, "OK (source)",
                                    {"status": "OK", "contract": "Vault"})
    found = state.find_duplicate_tool_call("get_contract_source", {"contract": "Vault"})
    check("exact match found", found is not None and found.id == record.id, found)


def test_find_duplicate_tool_call_different_args_no_match():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.record_tool_call("get_contract_source", {"contract": "Vault"}, "OK (source)", {"status": "OK"})
    found = state.find_duplicate_tool_call("get_contract_source", {"contract": "Other"})
    check("different args -- no match", found is None, found)


def test_find_duplicate_tool_call_different_tool_no_match():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.record_tool_call("get_contract_source", {"contract": "Vault"}, "OK (source)", {"status": "OK"})
    found = state.find_duplicate_tool_call("get_function_source", {"contract": "Vault"})
    check("different tool, same args -- no match", found is None, found)


def test_find_duplicate_tool_call_ignores_args_key_order():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.record_tool_call("get_function_source", {"contract": "Vault", "function": "withdraw"},
                           "OK (source)", {"status": "OK"})
    found = state.find_duplicate_tool_call("get_function_source", {"function": "withdraw", "contract": "Vault"})
    check("dict key ordering does not defeat the match", found is not None, found)


def test_find_duplicate_tool_call_third_request_maps_back_to_the_original():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    original = state.record_tool_call("get_contract_source", {"contract": "Vault"}, "OK (source)", {"status": "OK"})
    found_1 = state.find_duplicate_tool_call("get_contract_source", {"contract": "Vault"})
    found_2 = state.find_duplicate_tool_call("get_contract_source", {"contract": "Vault"})
    check("first duplicate lookup maps to the original record", found_1 is not None and found_1.id == original.id)
    check("a later, third identical request still maps to the SAME original record, not a new one",
          found_2 is not None and found_2.id == original.id, found_2)


def test_record_verdict_persists_ceiv_and_links_shared_evidence():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.add_evidence(_evidence("ev1", claim="call precedes state update"))
    state.add_hypothesis(Hypothesis(id="h1", claim="unsafe ordering",
                                    originating_property_ids=["p1"]))
    state.record_verdict(
        "p1", claim="withdraw uses safe ordering", evidence_ids=["ev1"],
        hypothesis_ids=["h1"],
        interpretation="the cited ordering refutes the claim",
        verdict=RequirementResolution.FAIL,
    )
    assessment = state.requirement_states["p1"].final_assessment
    check("assessment stored", assessment is not None)
    check("CEIV claim stored separately", assessment.claim == "withdraw uses safe ordering")
    check("CEIV evidence linked by id", assessment.evidence_ids == ["ev1"])
    check("CEIV interpretation stored separately",
          assessment.interpretation == "the cited ordering refutes the claim")
    check("CEIV verdict resolves requirement", assessment.verdict == RequirementResolution.FAIL)
    check("shared evidence linked to property", state.requirement_states["p1"].evidence_for_ids == ["ev1"])


# --- result mapping (cluster -> per-property verdicts) --------------------

def test_to_property_verdict_entries_covers_exact_property_id_set():
    """Mirrors cluster_response_validation.validate_cluster_response's own
    completeness check on the Codex path -- no missing, no duplicate,
    no unrecognized property_id."""
    state = ClusterInvestigationState.initial("c1", ["p1", "p2", "p3"])
    state.resolve_requirement("p1", RequirementResolution.PASS)
    state.resolve_requirement("p2", RequirementResolution.FAIL, reason="counterexample found")
    state.resolve_requirement("p3", RequirementResolution.NOT_APPLICABLE)

    entries = state.to_property_verdict_entries()
    ids_seen = [e["property_id"] for e in entries]
    check("exactly 3 entries", len(entries) == 3, entries)
    check("no duplicates", len(set(ids_seen)) == len(ids_seen))
    check("exact set matches cluster property_ids", set(ids_seen) == {"p1", "p2", "p3"})
    verdict_by_id = {e["property_id"]: e["verdict"] for e in entries}
    check("p1 verdict PASS", verdict_by_id["p1"] == "PASS")
    check("p2 verdict FAIL", verdict_by_id["p2"] == "FAIL")
    check("p3 verdict NOT_APPLICABLE", verdict_by_id["p3"] == "NOT_APPLICABLE")


def test_to_property_verdict_entries_includes_shared_evidence_per_property():
    state = ClusterInvestigationState.initial("c1", ["p1", "p2"])
    state.add_evidence(_evidence("ev1", claim="shared fact"))
    state.link_evidence_to_requirement("p1", "ev1", supports=True)
    state.link_evidence_to_requirement("p2", "ev1", supports=True)
    entries = {e["property_id"]: e for e in state.to_property_verdict_entries()}
    check("p1 entry carries evidence", entries["p1"]["evidence_for"][0]["id"] == "ev1")
    check("p2 entry carries the SAME evidence, not a copy with a different id",
          entries["p2"]["evidence_for"][0]["id"] == "ev1")


def test_one_cluster_multiple_requirements_is_one_shared_state_object():
    """Verifies clustering behavior at the state layer: a cluster with
    multiple requirements produces ONE ClusterInvestigationState (one
    trajectory/tool_history/evidence pool), never independent per-property
    state objects -- the architectural invariant the task brief requires
    ("one cluster does NOT create independent agent sessions")."""
    state = ClusterInvestigationState.initial("c1", ["p1", "p2", "p3"])
    state.record_tool_call("read_file", {"path": "Foo.sol"}, "read 40 lines")
    check("single shared tool_history serves all properties", len(state.tool_history) == 1)
    check("single cluster_id", state.cluster_id == "c1")
    check("3 distinct RequirementStates inside the ONE state object",
          len(state.requirement_states) == 3 and len({id(rs) for rs in state.requirement_states.values()}) == 3)


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
