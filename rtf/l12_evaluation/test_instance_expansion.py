"""Unit tests for the opt-in `instance_expansion_enabled` path added to
`run_pipeline_e2e` (rtf.l10_property_derivation.derive_investigations
wired into `_run_escalations_concurrent`). No live Codex/API calls --
mocks `run_arm_g_bundle` the same way `test_concurrent_escalation.py`
does. Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_instance_expansion
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import ArmGResult
from rtf.l12_evaluation import pipeline_e2e

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


_FAKE_COUNTEREXAMPLE_SEARCH = {
    "attempted": True,
    "violation_scenario_considered": "test-fixture violation scenario, long enough to pass the rigor check",
    "checks_performed": "test-fixture checks performed, long enough to pass the rigor check",
    "found_violation": False,
}


def _fake_codex_result(case_id: str, decision: str = "PASS", cost_usd: float = 0.001) -> ArmGResult:
    final_decision = {"decision": decision, "reasoning_summary": "test"}
    if decision == "PASS":
        # See test_concurrent_escalation.py's identical fixture note --
        # codex_bridge's Phase 5 rigor check downgrades a PASS with no
        # counterexample_search, so these mocks opt in to a well-formed
        # one by default (rigor enforcement has its own dedicated tests
        # in test_codex_bridge.py; this file tests instance expansion).
        final_decision["counterexample_search"] = _FAKE_COUNTEREXAMPLE_SEARCH
    return ArmGResult(
        case_id=case_id, final_decision=final_decision,
        reasoning_text="test", actual_shell_commands=1, actual_shell_files_touched=[],
        revealed_files=[], graph_tool_calls=0, graph_unresolved_events=[], max_hop_depth_seen=None,
        divergent_files=[], input_tokens=10, cached_input_tokens=0, output_tokens=10,
        cost_usd=cost_usd, wall_clock_s=1.0, timed_out=False, session_log_path="", trace_log_path="",
    )


def _run_scoped(only_req_ids: set[str], mock_run_arm_g_bundle, entry_sol_file: Path, project_root: Path,
                 max_concurrent_investigations: int = 1, instance_expansion_enabled: bool = False,
                 max_instances_per_requirement: int = 6):
    with patch.object(pipeline_e2e, "run_arm_g_bundle", mock_run_arm_g_bundle):
        return pipeline_e2e.run_pipeline_e2e(
            audit_id="test-audit", entry_sol_file=entry_sol_file, project_root=project_root,
            solc_version="0.8.20", judgment_layer=object(),
            codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
            mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
            solc_path_dir="/nonexistent", scratch_root=Path(tempfile.mkdtemp()),
            escalation_enabled=True, codex_timeout_s=5,
            only_req_ids=only_req_ids, max_concurrent_investigations=max_concurrent_investigations,
            instance_expansion_enabled=instance_expansion_enabled,
            max_instances_per_requirement=max_instances_per_requirement,
        )


_MULTI_LOCATION_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BlockDataUser {
    uint256 public lastSeen1;
    uint256 public lastSeen2;

    function touchA() public {
        lastSeen1 = block.timestamp;
    }

    function touchB() public {
        lastSeen2 = block.timestamp;
    }
}
"""

_MULTI_CLAUSE_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Rounder {
    function share(uint256 amount, uint256 total, uint256 supply) public pure returns (uint256) {
        return amount * supply / total;
    }
}
"""


def _write(tmp: Path, name: str, source: str) -> Path:
    path = tmp / f"{name}.sol"
    path.write_text(source, encoding="utf-8")
    return path


# --- default (instance_expansion_enabled=False) is byte-behavior-identical --

def test_default_disabled_produces_exactly_one_call_even_with_multi_location_evidence():
    calls = []

    def _record(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    with tempfile.TemporaryDirectory() as tmp:
        entry = _write(Path(tmp), "BlockDataUser", _MULTI_LOCATION_SOURCE)
        req_id = "req-2-block-data-misuse"
        artifacts = _run_scoped({req_id}, _record, entry, Path(tmp))  # instance_expansion_enabled defaults False
        check("disabled: exactly one call even though the predicate has 2 distinct locations",
              len(calls) == 1, calls)
        check("disabled: instance_results stays empty (only populated when enabled)",
              artifacts.instance_results == {}, artifacts.instance_results)


# --- multi-location single-clause requirement expands ----------------------

def test_enabled_multi_location_requirement_expands_into_multiple_calls():
    calls = []

    def _record(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    with tempfile.TemporaryDirectory() as tmp:
        entry = _write(Path(tmp), "BlockDataUser", _MULTI_LOCATION_SOURCE)
        req_id = "req-2-block-data-misuse"
        artifacts = _run_scoped(
            {req_id}, _record, entry, Path(tmp),
            max_concurrent_investigations=1, instance_expansion_enabled=True,
        )
        check("enabled: more than one call for a requirement with 2 distinct evidence locations",
              len(calls) >= 2, calls)
        check("enabled: all case_ids are distinct (no collision)", len(calls) == len(set(calls)), calls)
        check("enabled: instance_results has an entry for this req_id",
              req_id in artifacts.instance_results, artifacts.instance_results)
        check("enabled: instance_results has one ArmGResult per call made",
              len(artifacts.instance_results.get(req_id, [])) == len(calls))
        check("enabled: final conformance_state is set (aggregation completed)",
              artifacts.run.routed[req_id].conformance_state is not None)
        check("enabled: codex_results still has exactly one representative result",
              req_id in artifacts.codex_results)


def test_enabled_all_instances_pass_aggregates_to_pass():
    def _all_pass(**kwargs):
        return _fake_codex_result(kwargs["case_id"], decision="PASS")

    with tempfile.TemporaryDirectory() as tmp:
        entry = _write(Path(tmp), "BlockDataUser", _MULTI_LOCATION_SOURCE)
        req_id = "req-2-block-data-misuse"
        artifacts = _run_scoped(
            {req_id}, _all_pass, entry, Path(tmp),
            max_concurrent_investigations=2, instance_expansion_enabled=True,
        )
        check("all-PASS instances aggregate to PASS",
              artifacts.run.routed[req_id].conformance_state.value == "PASS",
              artifacts.run.routed[req_id])
        check("representative codex_results result is a PASS (no FAIL exists)",
              artifacts.codex_results[req_id].final_decision["decision"] == "PASS")


def test_enabled_any_instance_fail_aggregates_to_fail():
    calls = {"n": 0}

    def _first_fails_rest_pass(**kwargs):
        calls["n"] += 1
        decision = "FAIL" if calls["n"] == 1 else "PASS"
        return _fake_codex_result(kwargs["case_id"], decision=decision)

    with tempfile.TemporaryDirectory() as tmp:
        entry = _write(Path(tmp), "BlockDataUser", _MULTI_LOCATION_SOURCE)
        req_id = "req-2-block-data-misuse"
        # Serialize (max_concurrent_investigations=1 with expansion still
        # routes through the concurrent path per design, but batches of 1
        # keep call order deterministic for this test).
        artifacts = _run_scoped(
            {req_id}, _first_fails_rest_pass, entry, Path(tmp),
            max_concurrent_investigations=1, instance_expansion_enabled=True,
        )
        check("any-FAIL instance aggregates the whole requirement to FAIL",
              artifacts.run.routed[req_id].conformance_state.value == "FAIL",
              artifacts.run.routed[req_id])
        check("representative codex_results result IS the FAIL (never displaced by a later PASS)",
              artifacts.codex_results[req_id].final_decision["decision"] == "FAIL")


# --- multi-clause requirement expands even with only one location -----------

def test_enabled_multi_clause_requirement_expands_even_with_one_location():
    calls = []

    def _record(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    with tempfile.TemporaryDirectory() as tmp:
        entry = _write(Path(tmp), "Rounder", _MULTI_CLAUSE_SOURCE)
        req_id = "req-2-check-rounding"
        artifacts = _run_scoped(
            {req_id}, _record, entry, Path(tmp),
            max_concurrent_investigations=1, instance_expansion_enabled=True,
        )
        check("multi-clause: at least 2 calls for a requirement with a multi-sentence normative text",
              len(calls) >= 2, calls)
        check("multi-clause: final conformance_state resolved", artifacts.run.routed[req_id].conformance_state is not None)


# --- combinatorial cap honored end-to-end -----------------------------------

def test_max_instances_per_requirement_cap_is_honored_end_to_end():
    calls = []

    def _record(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    with tempfile.TemporaryDirectory() as tmp:
        entry = _write(Path(tmp), "BlockDataUser", _MULTI_LOCATION_SOURCE)
        req_id = "req-2-block-data-misuse"
        artifacts = _run_scoped(
            {req_id}, _record, entry, Path(tmp),
            max_concurrent_investigations=1, instance_expansion_enabled=True,
            max_instances_per_requirement=1,
        )
        check("cap=1: exactly one call even though evidence has multiple locations",
              len(calls) == 1, calls)


def main() -> int:
    tests = [
        test_default_disabled_produces_exactly_one_call_even_with_multi_location_evidence,
        test_enabled_multi_location_requirement_expands_into_multiple_calls,
        test_enabled_all_instances_pass_aggregates_to_pass,
        test_enabled_any_instance_fail_aggregates_to_fail,
        test_enabled_multi_clause_requirement_expands_even_with_one_location,
        test_max_instances_per_requirement_cap_is_honored_end_to_end,
    ]
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
