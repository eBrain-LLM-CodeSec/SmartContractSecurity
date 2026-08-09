"""§16 (mock-Codex routing) + §17 (negative routing) tests for the
standards-driven GP requirement generator, run against the REAL
`pipeline_e2e.run_pipeline_e2e` orchestrator with a spy/mock at the actual
Codex invocation boundary (`run_arm_g_bundle`), per the implementation
plan's explicit instruction not to simulate routing independently. No live
Codex/API calls anywhere in this file. Run with:
    python3 -m rtf.standards.test_mock_codex_routing
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import ArmGResult
from rtf.l12_evaluation import pipeline_e2e
from rtf.l12_evaluation.registry import DETERMINISTIC_COMPLETE_REQ_IDS

from .generator import generated_requirement_id
from .test_discovery import IERC4626_INTERFACE, _ERC20_METHOD_BODIES, _ERC4626_METHOD_BODIES

PASSES: list[str] = []
FAILURES: list[str] = []

VAULT_SOL = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "multi_contract" / "Vault.sol"


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _fake_codex_result(req_id: str, decision: str = "INCONCLUSIVE") -> ArmGResult:
    """Deterministic INCONCLUSIVE per the plan's §16 instruction ('Return
    deterministic INCONCLUSIVE from the mock')."""
    return ArmGResult(
        case_id=f"test__{req_id}", final_decision={"decision": decision, "reasoning_summary": "mock"},
        reasoning_text="mock", actual_shell_commands=1, actual_shell_files_touched=[],
        revealed_files=[], graph_tool_calls=0, graph_unresolved_events=[], max_hop_depth_seen=None,
        divergent_files=[], input_tokens=10, cached_input_tokens=0, output_tokens=10,
        cost_usd=0.001, wall_clock_s=1.0, timed_out=False, session_log_path="", trace_log_path="",
    )


def _make_vault_repo(tmp: Path, contract_name: str = "MockVault") -> Path:
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


def _run_scoped(entry_sol_file: Path, project_root: Path, only_req_ids: set[str], mock_run_arm_g_bundle):
    with patch.object(pipeline_e2e, "run_arm_g_bundle", mock_run_arm_g_bundle):
        return pipeline_e2e.run_pipeline_e2e(
            audit_id="mock-routing-test", entry_sol_file=entry_sol_file, project_root=project_root,
            solc_version="0.8.20", judgment_layer=object(),
            codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
            mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
            solc_path_dir="/nonexistent", scratch_root=Path(tempfile.mkdtemp()),
            escalation_enabled=True, codex_timeout_s=5, cost_ceiling_usd=None,
            only_req_ids=only_req_ids,
        )


# Sample of generated req_ids spanning both registered standards and all
# three normative strengths actually present -- not exhaustive (91 total
# generated requirements against this fixture), but broad enough to prove
# the routing property generically rather than for one cherry-picked clause.
_SAMPLE_CLAUSES = [
    ("ERC-4626", "erc4626-totalassets-must-include-fees"),       # MUST
    ("ERC-4626", "erc4626-totalassets-should-include-yield"),    # SHOULD
    ("ERC-4626", "erc4626-nontransferable-may-revert-transfer"), # MAY, conditional (UNKNOWN applicability)
    ("ERC-4626", "erc4626-converttoshares-must-round-down"),
    ("ERC-20", "erc20-transfer-must-fire-transfer-event"),
    ("ERC-20", "erc20-transfer-should-throw-on-insufficient-balance"),
]


def _sample_req_ids() -> set[str]:
    return {generated_requirement_id(std, clause) for std, clause in _SAMPLE_CLAUSES}


# --- §16: every agent-required generated requirement invokes the mock -----

def test_every_sampled_generated_requirement_invokes_mock_codex():
    calls: list[str] = []

    def _record_and_return(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    with tempfile.TemporaryDirectory() as tmp:
        entry = _make_vault_repo(Path(tmp))
        req_ids = _sample_req_ids()
        artifacts = _run_scoped(entry, Path(tmp), req_ids, _record_and_return)

        check(
            "mock-routing: mock Codex invocation count exactly equals the number of sampled agent-required requirements",
            len(calls) == len(req_ids),
            (len(calls), len(req_ids), calls),
        )
        for std, clause in _SAMPLE_CLAUSES:
            rid = generated_requirement_id(std, clause)
            check(f"mock-routing: {rid} is in codex_results (real agent-invocation record)", rid in artifacts.codex_results, list(artifacts.codex_results)[:5])
            check(f"mock-routing: {rid}'s conformance came from the mock's INCONCLUSIVE decision", artifacts.run.routed[rid].conformance_state is not None and artifacts.run.routed[rid].conformance_state.value == "INCONCLUSIVE")
            check(f"mock-routing: {rid} has a rendered bundle with real requirement text", rid in artifacts.generated_bundles, list(artifacts.generated_bundles)[:5])


def test_agent_input_carries_required_metadata():
    """§16: 'Record: requirement ID, requirement text, standard, source
    clause, repository, routing reason, agent input.' Verifies this is
    ACTUALLY present in what gets built for the agent, not merely claimed."""
    with tempfile.TemporaryDirectory() as tmp:
        entry = _make_vault_repo(Path(tmp))
        rid = generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees")
        artifacts = _run_scoped(entry, Path(tmp), {rid}, lambda **kw: _fake_codex_result(kw["case_id"]))

        bundle = artifacts.generated_bundles[rid]["bundle"]
        check("agent-input: requirement text (obligation) present in bundle", "inclusive of any fees" in bundle["self"], bundle["self"])
        check("agent-input: standard identity present in bundle", "ERC-4626" in bundle["self"], bundle["self"])
        check("agent-input: source section present in bundle", "totalAssets" in bundle["self"], bundle["self"])
        check("agent-input: WHY the standard is applicable (routing reason) present", "APPLICABLE" in bundle["parent_section_context"], bundle["parent_section_context"])

        evidence = artifacts.run.routed[rid].evidence
        check("agent-input: evidence references the real repository location (contract name)", evidence[0].location == "MockVault", evidence)
        check("agent-input: evidence detail cites the standard and clause_id", "ERC-4626" in evidence[0].detail and "erc4626-totalassets-must-include-fees" in evidence[0].detail, evidence[0].detail)


# --- §17: negative routing tests -----------------------------------------

def test_not_applicable_generated_requirement_does_not_invoke_codex():
    def _raise_if_called(**kwargs):
        raise AssertionError("run_arm_g_bundle must NOT be called for a NOT_APPLICABLE generated requirement")

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        entry = repo / "Unrelated.sol"
        entry.write_text("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\ncontract Unrelated { uint256 public x; }\n", encoding="utf-8")
        rid = generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees")
        artifacts = _run_scoped(entry, repo, {rid}, _raise_if_called)
        check("negative: NOT_APPLICABLE generated requirement resolves without ever invoking Codex", rid in artifacts.run.routed)
        check("negative: its applicability_state is NOT_APPLICABLE", artifacts.run.routed[rid].applicability_state.value == "NOT_APPLICABLE", artifacts.run.routed[rid])


def test_deterministic_81_corpus_requirement_still_never_invokes_codex_alongside_standards_generation():
    """Regression-safety: adding standards-driven generation to the
    pipeline must not perturb the EXISTING deterministic-complete routing
    for the frozen 81-requirement corpus (two logically separate code
    paths merged into the same `routed` dict -- confirm no cross-talk)."""
    def _raise_if_called(**kwargs):
        raise AssertionError("run_arm_g_bundle must NOT be called for a DETERMINISTIC_COMPLETE_REQ_IDS requirement")

    req_id = "req-3-event-on-state-change"
    check("precondition: req_id is DETERMINISTIC_COMPLETE", req_id in DETERMINISTIC_COMPLETE_REQ_IDS)
    artifacts = _run_scoped(VAULT_SOL, VAULT_SOL.parent, {req_id}, _raise_if_called)
    check(
        "negative: the 81-corpus deterministic requirement still resolves with zero Codex invocations, standards generation running alongside it",
        artifacts.run.routed[req_id].conformance_state is not None and artifacts.stage_metrics.bundles_escalated_to_codex == 0,
        artifacts.stage_metrics.bundles_escalated_to_codex,
    )


def test_unrelated_repo_produces_zero_agent_invocations_from_generated_requirements():
    """'unrelated standards produce no requirements' (§17), interpreted
    precisely: clauses are still uniformly generated for every registered
    standard (so nothing is silently skipped at generation time -- see
    routing.py's own silently_missing invariant), but NONE of them reach
    Codex for a repository that doesn't use ERC-4626/ERC-20 at all."""
    calls: list[str] = []

    def _record_and_return(**kwargs):
        calls.append(kwargs["case_id"])
        return _fake_codex_result(kwargs["case_id"])

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        entry = repo / "Unrelated.sol"
        entry.write_text(
            "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\n"
            "contract Unrelated { function doThing() external pure returns (uint256) { return 1; } }\n",
            encoding="utf-8",
        )
        req_ids = _sample_req_ids()
        artifacts = _run_scoped(entry, repo, req_ids, _record_and_return)
        check(
            "negative: zero mock Codex invocations for a repository unrelated to any registered standard",
            len(calls) == 0,
            calls,
        )
        check(
            "negative: every sampled generated requirement still reached an explicit NOT_APPLICABLE terminal state (not silently missing)",
            all(artifacts.run.routed[r].applicability_state.value == "NOT_APPLICABLE" for r in req_ids),
            {r: artifacts.run.routed[r].applicability_state.value for r in req_ids},
        )


def test_unresolvable_graph_seed_does_not_block_generated_requirement_agent_invocation():
    """Mirrors test_agentic_architecture.py's own #4/#7 property, for a
    GENERATED requirement specifically: evidence location = a bare
    contract name (e.g. "MockVault"), which resolve_seed_node may or may
    not resolve on the program graph -- either way, the agent MUST still
    be invoked (no candidate_location precondition anywhere in this new
    code path either)."""
    calls: list[tuple] = []

    def _record_and_return(**kwargs):
        calls.append((kwargs["case_id"], kwargs["candidate_location"]))
        return _fake_codex_result(kwargs["case_id"])

    def _raise_ambiguous(pg, location):
        raise ValueError("simulated: graph seed cannot be resolved for this location")

    with tempfile.TemporaryDirectory() as tmp:
        entry = _make_vault_repo(Path(tmp))
        rid = generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees")
        with patch.object(pipeline_e2e, "resolve_seed_node", _raise_ambiguous):
            artifacts = _run_scoped(entry, Path(tmp), {rid}, _record_and_return)
        check("negative: agent WAS still invoked despite a graph-seed resolution failure", len(calls) == 1, calls)
        check("negative: run completed without raising", artifacts.run.routed[rid].conformance_state is not None)


def test_insufficient_evidence_never_returned_without_real_investigation():
    """§17: 'INSUFFICIENT_EVIDENCE cannot be returned before an agent-
    required requirement has actually received its investigation.'
    Verifies directly: for every generated requirement that ends up with
    a non-None conformance_state, a real (mocked) Codex investigation
    record MUST exist in codex_results -- conformance is never pre-judged."""
    def _record_and_return(**kwargs):
        return _fake_codex_result(kwargs["case_id"], decision="INSUFFICIENT_EVIDENCE")

    with tempfile.TemporaryDirectory() as tmp:
        entry = _make_vault_repo(Path(tmp))
        req_ids = _sample_req_ids()
        artifacts = _run_scoped(entry, Path(tmp), req_ids, _record_and_return)
        for rid in req_ids:
            result = artifacts.run.routed[rid]
            if result.conformance_state is not None and result.applicability_state.value == "APPLICABLE":
                check(
                    f"negative: {rid}'s non-None conformance_state ({result.conformance_state.value}) has a real backing investigation in codex_results",
                    rid in artifacts.codex_results,
                    rid,
                )


def main() -> int:
    tests = [
        test_every_sampled_generated_requirement_invokes_mock_codex,
        test_agent_input_carries_required_metadata,
        test_not_applicable_generated_requirement_does_not_invoke_codex,
        test_deterministic_81_corpus_requirement_still_never_invokes_codex_alongside_standards_generation,
        test_unrelated_repo_produces_zero_agent_invocations_from_generated_requirements,
        test_unresolvable_graph_seed_does_not_block_generated_requirement_agent_invocation,
        test_insufficient_evidence_never_returned_without_real_investigation,
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
