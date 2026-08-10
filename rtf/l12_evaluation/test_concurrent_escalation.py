"""Unit tests for the concurrent-investigation path added to
`run_pipeline_e2e` (`max_concurrent_investigations` > 1,
`_run_escalations_concurrent`). No live Codex/API calls -- every test
mocks `run_arm_g_bundle` the same way `test_agentic_architecture.py` and
`test_mock_codex_routing.py` already do. Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_concurrent_escalation
"""
from __future__ import annotations

import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import ArmGResult
from rtf.l12_evaluation import pipeline_e2e
from rtf.l12_evaluation.registry import AGENT_REQUIRED_REQ_IDS, DETERMINISTIC_COMPLETE_REQ_IDS
from rtf.standards.generator import generated_requirement_id
from rtf.standards.test_discovery import IERC4626_INTERFACE, _ERC20_METHOD_BODIES, _ERC4626_METHOD_BODIES

PASSES: list[str] = []
FAILURES: list[str] = []

VAULT_SOL = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "multi_contract" / "Vault.sol"


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


def _fake_codex_result(req_id: str, decision: str = "PASS", cost_usd: float = 0.001) -> ArmGResult:
    final_decision = {"decision": decision, "reasoning_summary": "test"}
    if decision == "PASS":
        # A PASS mock must include a well-formed counterexample_search or
        # codex_bridge.resolve_conformance_from_arm_g's Phase 5 rigor
        # check downgrades it to INCONCLUSIVE, same as a real under-
        # rigorous PASS would be -- see test_codex_bridge.py for that
        # behavior's own dedicated tests; these fixtures exist to test
        # concurrency/attribution, not rigor enforcement, so they opt in
        # to a well-formed search by default.
        final_decision["counterexample_search"] = _FAKE_COUNTEREXAMPLE_SEARCH
    return ArmGResult(
        case_id=f"test__{req_id}", final_decision=final_decision,
        reasoning_text="test", actual_shell_commands=1, actual_shell_files_touched=[],
        revealed_files=[], graph_tool_calls=0, graph_unresolved_events=[], max_hop_depth_seen=None,
        divergent_files=[], input_tokens=10, cached_input_tokens=0, output_tokens=10,
        cost_usd=cost_usd, wall_clock_s=1.0, timed_out=False, session_log_path="", trace_log_path="",
    )


def _run_scoped(only_req_ids: set[str], mock_run_arm_g_bundle, max_concurrent_investigations: int = 1,
                 cost_ceiling_usd: float | None = None, entry_sol_file: Path = VAULT_SOL, project_root: Path | None = None):
    with patch.object(pipeline_e2e, "run_arm_g_bundle", mock_run_arm_g_bundle):
        return pipeline_e2e.run_pipeline_e2e(
            audit_id="test-audit", entry_sol_file=entry_sol_file, project_root=project_root or entry_sol_file.parent,
            solc_version="0.8.20", judgment_layer=object(),
            codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
            mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
            solc_path_dir="/nonexistent", scratch_root=Path(tempfile.mkdtemp()),
            escalation_enabled=True, codex_timeout_s=5, cost_ceiling_usd=cost_ceiling_usd,
            only_req_ids=only_req_ids, max_concurrent_investigations=max_concurrent_investigations,
        )


def _make_vault_repo(tmp: Path, contract_name: str = "ConcVault") -> Path:
    (tmp / "interfaces").mkdir(parents=True, exist_ok=True)
    (tmp / "interfaces" / "IERC4626.sol").write_text(IERC4626_INTERFACE, encoding="utf-8")
    source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

contract {contract_name} is IERC4626 {{
{_ERC20_METHOD_BODIES}
{_ERC4626_METHOD_BODIES}
}}
"""
    (tmp / f"{contract_name}.sol").write_text(source, encoding="utf-8")
    return tmp / f"{contract_name}.sol"


# --- default (max_concurrent_investigations=1) is untouched ---------------

def test_default_still_serial_and_unchanged():
    """Sanity: omitting the new parameter entirely still exercises the
    original serial code path (not just 'a concurrency-1 pool')."""
    calls = []

    def _record_and_return(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    req_id = "req-2-external-calls"
    artifacts = _run_scoped({req_id}, _record_and_return)  # max_concurrent_investigations defaults to 1
    check("default: single call still happens", len(calls) == 1, calls)
    check("default: result correct", artifacts.run.routed[req_id].conformance_state is not None)


# --- concurrency actually overlaps in time ---------------------------------

def test_investigations_actually_run_concurrently():
    """Proves overlap, not just 'still works': each mock call blocks on a
    shared Event until N=3 calls are simultaneously in flight, then all
    release together. If the pipeline were still serial, this would
    deadlock (call #1 would block forever waiting for #2 and #3, which
    would never start until #1 returns) -- so a completion within the
    test's timeout is itself the proof of real concurrency, not just a
    faster wall-clock measurement.
    """
    N = 3
    barrier = threading.Barrier(N, timeout=10)
    max_in_flight = [0]
    current_in_flight = [0]
    lock = threading.Lock()

    def _blocking_call(**kwargs):
        with lock:
            current_in_flight[0] += 1
            max_in_flight[0] = max(max_in_flight[0], current_in_flight[0])
        barrier.wait()  # deadlocks unless all N calls are concurrently in flight
        with lock:
            current_in_flight[0] -= 1
        return _fake_codex_result(kwargs["case_id"])

    with tempfile.TemporaryDirectory() as tmp:
        entry = _make_vault_repo(Path(tmp))
        req_ids = {
            generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees"),
            generated_requirement_id("ERC-4626", "erc4626-totalassets-should-include-yield"),
            generated_requirement_id("ERC-4626", "erc4626-converttoshares-must-round-down"),
        }
        try:
            artifacts = _run_scoped(
                req_ids, _blocking_call, max_concurrent_investigations=N,
                entry_sol_file=entry, project_root=Path(tmp),
            )
            check("concurrency: run completed without deadlocking (proves real overlap, N calls were simultaneously in flight)", True)
            check("concurrency: peak simultaneous in-flight calls reached N", max_in_flight[0] == N, max_in_flight[0])
            for rid in req_ids:
                check(f"concurrency: {rid} resolved correctly", artifacts.run.routed[rid].conformance_state is not None)
        except Exception as e:  # noqa: BLE001 -- a barrier timeout manifests as a raised exception, i.e. NOT concurrent
            check("concurrency: run completed without deadlocking (proves real overlap, N calls were simultaneously in flight)", False, f"{type(e).__name__}: {e}")


# --- results attributed correctly, no cross-talk ---------------------------

def test_results_attributed_to_correct_req_id_under_concurrency():
    """Each concurrent call returns a DIFFERENT decision keyed by its own
    case_id -- verifies no mixup/race in how futures map back to req_ids."""
    def _decision_from_case_id(**kwargs):
        case_id = kwargs["case_id"]
        if "totalassets-must-include-fees" in case_id:
            decision = "FAIL"
        elif "totalassets-should-include-yield" in case_id:
            decision = "PASS"
        else:
            decision = "INCONCLUSIVE"
        return _fake_codex_result(case_id, decision=decision)

    with tempfile.TemporaryDirectory() as tmp:
        entry = _make_vault_repo(Path(tmp))
        fee_id = generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees")
        yield_id = generated_requirement_id("ERC-4626", "erc4626-totalassets-should-include-yield")
        artifacts = _run_scoped(
            {fee_id, yield_id}, _decision_from_case_id, max_concurrent_investigations=4,
            entry_sol_file=entry, project_root=Path(tmp),
        )
        check("attribution: fee clause got its OWN decision (FAIL), not the other's", artifacts.run.routed[fee_id].conformance_state.value == "FAIL", artifacts.run.routed[fee_id])
        check("attribution: yield clause got its OWN decision (PASS), not the other's", artifacts.run.routed[yield_id].conformance_state.value == "PASS", artifacts.run.routed[yield_id])


# --- negative properties preserved under concurrency ------------------------

def test_deterministic_complete_never_invokes_agent_under_concurrency():
    def _raise_if_called(**kwargs):
        raise AssertionError("run_arm_g_bundle must NOT be called for a DETERMINISTIC_COMPLETE_REQ_IDS requirement")

    req_id = "req-3-event-on-state-change"
    check("precondition: req_id is DETERMINISTIC_COMPLETE", req_id in DETERMINISTIC_COMPLETE_REQ_IDS)
    artifacts = _run_scoped({req_id}, _raise_if_called, max_concurrent_investigations=5)
    check("concurrency: deterministic-complete requirement still never invokes the agent", artifacts.run.routed[req_id].conformance_state is not None)
    check("concurrency: bundles_escalated_to_codex stayed 0", artifacts.stage_metrics.bundles_escalated_to_codex == 0, artifacts.stage_metrics.bundles_escalated_to_codex)


def test_agent_required_still_invokes_under_concurrency():
    calls = []

    def _record_and_return(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    req_id = "req-2-external-calls"
    check("precondition: req_id is AGENT_REQUIRED", req_id in AGENT_REQUIRED_REQ_IDS)
    artifacts = _run_scoped({req_id}, _record_and_return, max_concurrent_investigations=5)
    check("concurrency: agent-required requirement still invokes exactly once", len(calls) == 1, calls)


def test_a_crashing_investigation_does_not_kill_the_batch():
    def _maybe_crash(**kwargs):
        if "totalassets-must-include-fees" in kwargs["case_id"]:
            raise RuntimeError("simulated crash")
        return _fake_codex_result(kwargs["case_id"])

    with tempfile.TemporaryDirectory() as tmp:
        entry = _make_vault_repo(Path(tmp))
        fee_id = generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees")
        yield_id = generated_requirement_id("ERC-4626", "erc4626-totalassets-should-include-yield")
        artifacts = _run_scoped(
            {fee_id, yield_id}, _maybe_crash, max_concurrent_investigations=4,
            entry_sol_file=entry, project_root=Path(tmp),
        )
        check(
            "resilience: the crashing investigation resolves to INCONCLUSIVE with a recorded reason, not an unhandled exception",
            artifacts.run.routed[fee_id].conformance_state.value == "INCONCLUSIVE" and "codex_invocation_crashed" in artifacts.escalation_skip_reasons.get(fee_id, ""),
            (artifacts.run.routed[fee_id], artifacts.escalation_skip_reasons.get(fee_id)),
        )
        check(
            "resilience: the OTHER investigation in the same batch still completed normally",
            artifacts.run.routed[yield_id].conformance_state.value == "PASS",
            artifacts.run.routed[yield_id],
        )


# --- batch-granularity cost ceiling -----------------------------------------

def test_cost_ceiling_enforced_at_batch_granularity():
    """4 requirements, batch size 2, each costing $2 -- ceiling $3 should
    allow the FIRST batch (2 calls, $4 total -- ceiling exceeded mid-batch,
    an accepted, documented, bounded overrun) but block the second batch
    entirely (checked BEFORE it's submitted, using only completed cost)."""
    def _costly(**kwargs):
        return _fake_codex_result(kwargs["case_id"], cost_usd=2.0)

    with tempfile.TemporaryDirectory() as tmp:
        entry = _make_vault_repo(Path(tmp))
        req_ids = {
            generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees"),
            generated_requirement_id("ERC-4626", "erc4626-totalassets-should-include-yield"),
            generated_requirement_id("ERC-4626", "erc4626-converttoshares-must-round-down"),
            generated_requirement_id("ERC-4626", "erc4626-converttoassets-must-round-down"),
        }
        artifacts = _run_scoped(
            req_ids, _costly, max_concurrent_investigations=2, cost_ceiling_usd=3.0,
            entry_sol_file=entry, project_root=Path(tmp),
        )
        completed = [r for r in req_ids if artifacts.run.routed[r].conformance_state is not None
                     and artifacts.escalation_skip_reasons.get(r) != "cost_ceiling_reached"]
        skipped = [r for r in req_ids if artifacts.escalation_skip_reasons.get(r) == "cost_ceiling_reached"]
        check("batch-ceiling: first batch (2 calls) completed despite exceeding the ceiling mid-batch (documented, bounded overrun)", len(completed) == 2, completed)
        check("batch-ceiling: second batch (2 calls) was skipped entirely, never invoked", len(skipped) == 2, skipped)
        check("batch-ceiling: skipped requirements resolve to INCONCLUSIVE, not silently dropped", all(artifacts.run.routed[r].conformance_state.value == "INCONCLUSIVE" for r in skipped), skipped)


def main() -> int:
    tests = [
        test_default_still_serial_and_unchanged,
        test_investigations_actually_run_concurrently,
        test_results_attributed_to_correct_req_id_under_concurrency,
        test_deterministic_complete_never_invokes_agent_under_concurrency,
        test_agent_required_still_invokes_under_concurrency,
        test_a_crashing_investigation_does_not_kill_the_batch,
        test_cost_ceiling_enforced_at_batch_granularity,
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
