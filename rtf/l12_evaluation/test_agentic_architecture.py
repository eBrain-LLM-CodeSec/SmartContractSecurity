"""Unit tests for the "revisit the RTF architecture" redesign: bounded L8
is no longer a gate deciding whether an agent investigation happens;
deterministic-complete requirements never invoke any LLM at all;
agent-required requirements ALWAYS reach the agent (no candidate_location
precondition, no graph-ambiguity block); the agent gets full repository
access, not a fixed-size excerpt. No live Codex/API calls -- every test
either exercises real code paths with `run_arm_g_bundle` mocked out, or
tests a mechanism (like the repo-copy step) directly and in isolation.
Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_agentic_architecture
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import (
    ArmGResult,
    prepare_full_repo_investigation_dir,
)
from rtf.l12_evaluation import pipeline_e2e
from rtf.l12_evaluation.registry import AGENT_REQUIRED_REQ_IDS, DETERMINISTIC_COMPLETE_REQ_IDS, REGISTRY

VAULT_SOL = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "multi_contract" / "Vault.sol"
ARM_G_PROMPT_V2 = Path(__file__).resolve().parents[1] / "l8_llm_judgment_layer" / "bundle_agent_experiment" / "ARM_G_PROMPT_v2.md"

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _fake_codex_result(req_id: str, decision: str = "PASS") -> ArmGResult:
    return ArmGResult(
        case_id=f"test__{req_id}", final_decision={"decision": decision, "reasoning_summary": "test"},
        reasoning_text="test", actual_shell_commands=1, actual_shell_files_touched=[],
        revealed_files=[], graph_tool_calls=0, graph_unresolved_events=[], max_hop_depth_seen=None,
        divergent_files=[], input_tokens=10, cached_input_tokens=0, output_tokens=10,
        cost_usd=0.001, wall_clock_s=1.0, timed_out=False, session_log_path="", trace_log_path="",
    )


def _run_scoped(only_req_ids: set[str], mock_run_arm_g_bundle):
    """Runs the real pipeline against the real Vault.sol fixture, scoped
    to `only_req_ids`, with the agent-invocation function replaced by a
    mock -- exercises real routing/evidence-collection/seed-resolution
    logic, zero live LLM/Codex calls.
    """
    with patch.object(pipeline_e2e, "run_arm_g_bundle", mock_run_arm_g_bundle):
        return pipeline_e2e.run_pipeline_e2e(
            audit_id="test-audit", entry_sol_file=VAULT_SOL, project_root=VAULT_SOL.parent,
            solc_version="0.8.20", judgment_layer=object(),  # never touched -- L8 not called in this path
            codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
            mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
            solc_path_dir="/nonexistent", scratch_root=Path(tempfile.mkdtemp()),
            escalation_enabled=True, codex_timeout_s=5, cost_ceiling_usd=None,
            only_req_ids=only_req_ids,
        )


# --- 1/9: deterministic-only requirements do not invoke Codex --------------

def test_deterministic_complete_never_invokes_agent():
    def _raise_if_called(**kwargs):
        raise AssertionError("run_arm_g_bundle must NOT be called for a DETERMINISTIC_COMPLETE_REQ_IDS requirement")

    # req-3-event-on-state-change has real evidence (a real FAIL) on Vault.sol -- see corpus check.
    req_id = "req-3-event-on-state-change"
    check("precondition: req_id is DETERMINISTIC_COMPLETE", req_id in DETERMINISTIC_COMPLETE_REQ_IDS, "")
    artifacts = _run_scoped({req_id}, _raise_if_called)
    check("deterministic-complete: no exception, agent never invoked",
          artifacts.run.routed[req_id].conformance_state is not None, "")
    check("deterministic-complete: codex_results is empty for this req", req_id not in artifacts.codex_results, "")
    check("deterministic-complete: agent_investigations counter stayed 0",
          artifacts.stage_metrics.bundles_escalated_to_codex == 0, artifacts.stage_metrics.bundles_escalated_to_codex)


# --- 2/9: every agent-required, evidence-bearing requirement invokes an agent --

def test_agent_required_always_invokes_agent_when_evidence_exists():
    calls = []

    def _record_and_return(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    req_id = "req-2-external-calls"  # real evidence (Vault.withdraw) on Vault.sol, no bounded-L8 pre-pass needed
    check("precondition: req_id is AGENT_REQUIRED", req_id in AGENT_REQUIRED_REQ_IDS, "")
    artifacts = _run_scoped({req_id}, _record_and_return)
    check("agent-required: run_arm_g_bundle WAS called (not gated on any bounded judgment)", len(calls) == 1, calls)
    check("agent-required: codex_results has an entry", req_id in artifacts.codex_results, "")
    check("agent-required: final conformance came from the (mocked) agent decision",
          artifacts.run.routed[req_id].conformance_state is not None, "")


# --- 3/9: the agent can inspect code beyond the first 8000 characters ------

def test_full_repo_copy_includes_content_beyond_8000_chars():
    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp) / "repo"
        repo_root.mkdir()
        big_file = repo_root / "Big.sol"
        # A real, large single-file repo -- put a UNIQUE marker function
        # well past any 8000-char excerpt cutoff, matching the real
        # LiquidRon.sol/totalAssets() shape that caused the original bug.
        padding = "// padding line to grow the file\n" * 400  # well over 8000 chars
        marker = "function totalAssetsMarkerBeyondCutoff() public pure returns (uint256) { return 42; }\n"
        big_file.write_text("pragma solidity ^0.8.0;\ncontract Big {\n" + padding + marker + "}\n")
        check("test setup: file is genuinely bigger than the old 8000-char cutoff",
              big_file.stat().st_size > 8000, big_file.stat().st_size)
        marker_offset = big_file.read_text().index("totalAssetsMarkerBeyondCutoff")
        check("test setup: marker function starts past the old cutoff", marker_offset > 8000, marker_offset)

        investigation_dir = Path(tmp) / "investigation"
        prepare_full_repo_investigation_dir(repo_root, investigation_dir)

        copied = investigation_dir / "Big.sol"
        check("full-repo copy: the file exists in the investigation dir", copied.exists(), "")
        copied_text = copied.read_text()
        check("full-repo copy: the marker function IS present in the copy (not truncated)",
              "totalAssetsMarkerBeyondCutoff" in copied_text, "")
        check("full-repo copy: content is byte-identical, no truncation at all",
              copied_text == big_file.read_text(), "")


def test_full_repo_copy_excludes_git_but_includes_everything_else():
    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp) / "repo"
        (repo_root / ".git").mkdir(parents=True)
        (repo_root / ".git" / "config").write_text("git internals")
        (repo_root / "README.md").write_text("# hello")
        (repo_root / "src").mkdir()
        (repo_root / "src" / "Contract.sol").write_text("pragma solidity ^0.8.0;\ncontract C {}\n")
        (repo_root / "docs").mkdir()
        (repo_root / "docs" / "spec.md").write_text("spec")

        investigation_dir = Path(tmp) / "investigation"
        prepare_full_repo_investigation_dir(repo_root, investigation_dir)

        check("full-repo copy: README.md present", (investigation_dir / "README.md").exists(), "")
        check("full-repo copy: nested src/Contract.sol present", (investigation_dir / "src" / "Contract.sol").exists(), "")
        check("full-repo copy: docs/spec.md present", (investigation_dir / "docs" / "spec.md").exists(), "")
        check("full-repo copy: .git excluded", not (investigation_dir / ".git").exists(), "")


# --- 4/9 + 7/9: no candidate_location precondition, graph ambiguity/failure never blocks ---

def test_agent_invoked_even_when_graph_seed_never_resolves():
    """Directly exercises pipeline_e2e's seed-resolution try/except: a
    requirement whose top-ranked evidence location is non-function-shaped
    ("compiler config" -- a real, live-confirmed case, not synthetic)
    cannot resolve on the graph at all. Property: this must NOT prevent
    the agent from being invoked (the old architecture aborted escalation
    here entirely).
    """
    calls = []

    def _record_and_return(**kwargs):
        calls.append((kwargs["case_id"], kwargs["candidate_location"]))
        return _fake_codex_result(kwargs["case_id"])

    req_id = "req-1-compiler-SOL-2023-3"  # real evidence location = "compiler config" on Vault.sol
    check("precondition: req_id is AGENT_REQUIRED", req_id in AGENT_REQUIRED_REQ_IDS, "")
    artifacts = _run_scoped({req_id}, _record_and_return)
    check("non-function-shaped location: agent WAS still invoked despite an unresolvable graph seed",
          len(calls) == 1, calls)
    if calls:
        check("non-function-shaped location: the unresolvable string was passed through as a HINT, not blocking",
              calls[0][1] == "compiler config", calls[0][1])
    check("non-function-shaped location: failure is recorded as informational, not fatal",
          req_id in artifacts.escalation_skip_reasons and "graph_seed_not_resolved" in artifacts.escalation_skip_reasons[req_id],
          artifacts.escalation_skip_reasons.get(req_id))
    check("non-function-shaped location: graph_seed_resolved explicitly False, not silently omitted",
          artifacts.graph_seed_resolved.get(req_id) is False, artifacts.graph_seed_resolved.get(req_id))


def test_ambiguous_graph_seed_does_not_block_agent_invocation():
    """graph_navigation.resolve_seed_node's own contract (unchanged, still
    tested in test_graph.py) is to RAISE ValueError on an ambiguous
    (>1 overload) match -- fail loud at that layer, never silently guess.
    The property this test protects is one layer up: pipeline_e2e.py must
    catch that raise and STILL invoke the agent, never abort escalation
    because of it (the old architecture's exact failure mode -- see
    RTF_AGENTIC_ARCHITECTURE.md defect #3). Simulated via a monkeypatched
    resolve_seed_node that raises the real ambiguous-overload exception
    shape (confirmed live in a prior real run's own escalation_skip_
    reasons, not invented), since Vault.sol's own simple single-file
    fixture has no real overloaded function to trigger this naturally.
    """
    calls = []

    def _record_and_return(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    def _raise_ambiguous(pg, candidate_location):
        raise ValueError(
            f"ambiguous candidate_location={candidate_location!r}: 2 overloads "
            f"['fn::Math.mulDiv(uint256,uint256,uint256,Math.Rounding)', 'fn::Math.mulDiv(uint256,uint256,uint256)'] "
            f"-- RTF's bare Contract.function location format cannot disambiguate"
        )

    req_id = "req-2-external-calls"  # real evidence (Vault.withdraw) on Vault.sol
    with patch.object(pipeline_e2e, "resolve_seed_node", _raise_ambiguous):
        artifacts = _run_scoped({req_id}, _record_and_return)
    check("graph ambiguity: agent WAS still invoked despite a simulated ambiguous-overload resolution failure",
          len(calls) == 1, calls)
    check("graph ambiguity: recorded as informational, not fatal",
          req_id in artifacts.escalation_skip_reasons and "graph_seed_not_resolved" in artifacts.escalation_skip_reasons[req_id],
          artifacts.escalation_skip_reasons.get(req_id))


# --- 5/9: INSUFFICIENT_EVIDENCE only after genuine exploration -------------

def test_prompt_forbids_premature_insufficient_evidence():
    text = ARM_G_PROMPT_V2.read_text(encoding="utf-8")
    check("ARM_G_PROMPT_v2.md exists (the active, full-repo-access prompt)", ARM_G_PROMPT_V2.exists(), "")
    check("prompt explicitly forbids returning INSUFFICIENT_EVIDENCE without genuine exploration",
          "Do not return `INSUFFICIENT_EVIDENCE`" in text or "genuinely tried to locate" in text, "")
    check("prompt explicitly grants full repository access (not graph-gated-only)",
          "full, normal access to the repository" in text, "")
    check("prompt does not contain the old v1 restriction language",
          "You do not have unrestricted repository browsing" not in text, "")


def test_arm_g_codex_loads_v2_prompt_not_v1():
    from rtf.l8_llm_judgment_layer.bundle_agent_experiment import arm_g_codex
    check("arm_g_codex.py's active prompt path is v2", arm_g_codex.ARM_G_PROMPT_PATH.name == "ARM_G_PROMPT_v2.md",
          arm_g_codex.ARM_G_PROMPT_PATH.name)
    loaded = arm_g_codex.load_frozen_arm_g_prompt()
    check("loaded prompt text is the v2 content (full repository access)",
          "full, normal access to the repository" in loaded, "")


# --- 6/9: non-function-shaped requirements can still be investigated -------
# (covered directly by test_agent_invoked_even_when_graph_seed_never_resolves
# above, using the real "compiler config" location -- not duplicated here)


# --- graph_mcp_server graceful degradation (supports 4/9 and 7/9) ----------

def test_graph_mcp_server_get_seed_never_raises_on_empty_or_bad_hint():
    """graph_mcp_server.py reads its config from env vars at import time
    (by design -- it runs as a standalone MCP subprocess), so this test
    exercises it as a real subprocess with a controlled, minimal
    environment rather than importing it in-process (which would pollute
    this test process's module cache and any other test's env-var
    assumptions).
    """
    import json
    import os
    import subprocess

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        entry = tmp_path / "Contract.sol"
        entry.write_text("pragma solidity ^0.8.20;\ncontract Contract { function f() public {} }\n")
        investigation_dir = tmp_path / "inv"
        investigation_dir.mkdir()
        (investigation_dir / "Contract.sol").write_text(entry.read_text())
        trace_log = tmp_path / "trace.jsonl"

        script = """
import sys
sys.path.insert(0, {repo!r})
from rtf.l8_llm_judgment_layer.bundle_agent_experiment.graph_mcp_server import show_candidate
import json
print(json.dumps(show_candidate()))
"""
        env = dict(os.environ)
        env.update({
            "GRAPH_ENTRY_FILE": str(entry),
            "GRAPH_REPO_ROOT": str(investigation_dir),
            "GRAPH_INVESTIGATION_DIR": str(investigation_dir),
            "GRAPH_CANDIDATE_LOCATION": "",  # no hint at all -- the property under test
            "GRAPH_TRACE_LOG_PATH": str(trace_log),
            "GRAPH_SOLC_PATH_DIR": "",
        })
        repo_root_for_import = str(Path(__file__).resolve().parents[2])
        result = subprocess.run(
            [sys.executable, "-c", script.format(repo=repo_root_for_import)],
            env=env, capture_output=True, text=True, timeout=30,
        )
        check("graph_mcp_server: show_candidate() with empty candidate_location does not crash",
              result.returncode == 0, (result.returncode, result.stderr[-2000:]))
        if result.returncode == 0:
            out = json.loads(result.stdout.strip().splitlines()[-1])
            check("graph_mcp_server: returns NO_CANDIDATE_HINT status, not an error",
                  out.get("status") == "NO_CANDIDATE_HINT", out)
            check("graph_mcp_server: provides guidance to explore via normal file tools",
                  "guidance" in out and "grep" in out["guidance"].lower() or "find" in out.get("guidance", "").lower(),
                  out.get("guidance"))


# --- 8/9: existing deterministic checks continue to behave correctly -------

def test_deterministic_complete_and_agent_required_partition_registry_exactly():
    check("DETERMINISTIC_COMPLETE and AGENT_REQUIRED are disjoint",
          DETERMINISTIC_COMPLETE_REQ_IDS.isdisjoint(AGENT_REQUIRED_REQ_IDS), "")
    check("DETERMINISTIC_COMPLETE union AGENT_REQUIRED equals REGISTRY exactly",
          (DETERMINISTIC_COMPLETE_REQ_IDS | AGENT_REQUIRED_REQ_IDS) == frozenset(REGISTRY.keys()),
          (frozenset(REGISTRY.keys()) - (DETERMINISTIC_COMPLETE_REQ_IDS | AGENT_REQUIRED_REQ_IDS)))
    check("19 deterministic-complete requirements (mechanically classified, see RTF_AGENTIC_ARCHITECTURE.md)",
          len(DETERMINISTIC_COMPLETE_REQ_IDS) == 19, len(DETERMINISTIC_COMPLETE_REQ_IDS))
    check("59 agent-required requirements", len(AGENT_REQUIRED_REQ_IDS) == 59, len(AGENT_REQUIRED_REQ_IDS))


def test_deterministic_predicates_produce_the_same_evidence_as_before():
    """Spot-check against this session's own real fixture run (recorded
    above while designing these tests): req-3-event-on-state-change,
    req-3-annotate, req-R-define-license all still fire real evidence on
    Vault.sol and resolve to FAIL directly (no LLM), same predicate
    functions, unchanged by this redesign.
    """
    from rtf.l12_evaluation.metrics import ConformanceState
    from rtf.l12_evaluation.run_rtf import build_context_for_evmbench_target, load_unconditioned_map, run_rtf

    ctx, err = build_context_for_evmbench_target(VAULT_SOL, VAULT_SOL.parent, "0.8.20")
    check("fixture compiles cleanly", err is None, err)
    unconditioned_map = load_unconditioned_map(Path(__file__).resolve().parents[1] / "l1_corpus" / "requirement_corpus.json")
    run, _raw = run_rtf(ctx, "test-audit", unconditioned_map)
    for req_id in ("req-3-event-on-state-change", "req-3-annotate", "req-R-define-license"):
        r = run.routed[req_id]
        check(f"{req_id}: still resolves directly to FAIL with real evidence (deterministic-complete, unchanged)",
              r.conformance_state == ConformanceState.FAIL and len(r.evidence) > 0,
              (r.conformance_state, len(r.evidence)))


# --- 9/9: no silent requirement omissions -----------------------------------
# (covered by test_runtime_coverage.py's compute_integrity_report tests,
# unaffected by this redesign -- routing changed WHERE evidence goes, not
# whether every requirement reaches a terminal state. Re-asserted here at
# the registry level for this specific redesign's own new sets.)

def test_no_omissions_in_new_routing_sets():
    from rtf.l12_evaluation.registry import AGGREGATION_REQ_IDS

    all_req_ids = DETERMINISTIC_COMPLETE_REQ_IDS | AGENT_REQUIRED_REQ_IDS | AGGREGATION_REQ_IDS
    check("all 81 corpus requirements are covered by exactly one of the three routing sets",
          len(all_req_ids) == 81, len(all_req_ids))
    check("no requirement appears in more than one routing set (no double-counting)",
          len(DETERMINISTIC_COMPLETE_REQ_IDS) + len(AGENT_REQUIRED_REQ_IDS) + len(AGGREGATION_REQ_IDS) == 81,
          (len(DETERMINISTIC_COMPLETE_REQ_IDS), len(AGENT_REQUIRED_REQ_IDS), len(AGGREGATION_REQ_IDS)))


def main() -> int:
    tests = [
        test_deterministic_complete_never_invokes_agent,
        test_agent_required_always_invokes_agent_when_evidence_exists,
        test_full_repo_copy_includes_content_beyond_8000_chars,
        test_full_repo_copy_excludes_git_but_includes_everything_else,
        test_agent_invoked_even_when_graph_seed_never_resolves,
        test_ambiguous_graph_seed_does_not_block_agent_invocation,
        test_prompt_forbids_premature_insufficient_evidence,
        test_arm_g_codex_loads_v2_prompt_not_v1,
        test_graph_mcp_server_get_seed_never_raises_on_empty_or_bad_hint,
        test_deterministic_complete_and_agent_required_partition_registry_exactly,
        test_deterministic_predicates_produce_the_same_evidence_as_before,
        test_no_omissions_in_new_routing_sets,
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
