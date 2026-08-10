"""Unit tests for rtf.l11_investigation_grouping.live_runner -- the ONLY
module in this package that can spend real money. Every test here mocks
`run_arm_g_bundle_fn`; NO live Codex/API calls happen anywhere in this
file. This is the safety net that must be fully green before any real
paid run uses this module. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_live_runner
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l11_investigation_grouping.cluster_response_validation import PropertyVerdict
from rtf.l11_investigation_grouping.complexity import ClusterBudget
from rtf.l11_investigation_grouping.live_runner import (
    aggregate_properties_to_requirements, build_property_pool,
    prepare_cluster_investigations, run_cluster_investigations_live,
)
from rtf.l11_investigation_grouping.run_metadata import GROUPING_POLICY_G0_UNGROUPED, GROUPING_POLICY_G2_CONTEXT_AWARE
from rtf.l12_evaluation.metrics import ConformanceState
from rtf.l12_evaluation.pipeline_e2e import CORPUS_PATH
from rtf.l12_evaluation.run_rtf import build_context_for_evmbench_target, load_unconditioned_map, run_rtf

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


class _FakeArmGResult:
    def __init__(self, case_id: str, final_decision: dict | None, cost_usd: float = 0.01):
        self.case_id = case_id
        self.final_decision = final_decision
        self.cost_usd = cost_usd
        self.timed_out = False


_SOURCE = """// SPDX-License-Identifier: MIT
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


def _real_routed_and_ctx(tmp: Path):
    entry = tmp / "BlockDataUser.sol"
    entry.write_text(_SOURCE, encoding="utf-8")
    ctx, compile_error = build_context_for_evmbench_target(entry, tmp, "0.8.20")
    assert ctx.slither is not None, f"fixture failed to compile: {compile_error}"
    unconditioned_map = load_unconditioned_map(CORPUS_PATH)
    run, _raw = run_rtf(ctx, "test-audit", unconditioned_map)
    return run.routed, ctx, entry


# --- build_property_pool (real compile, real predicates, no Codex) ---------

def test_build_property_pool_derives_real_properties_from_real_evidence():
    with tempfile.TemporaryDirectory() as tmp:
        routed, ctx, entry = _real_routed_and_ctx(Path(tmp))
        props = build_property_pool(routed, Path(tmp), pg=None, slither=ctx.slither)
        check("at least one property derived from real evidence", len(props) > 0, len(props))
        req_ids = {p.requirement_id for p in props}
        check("req-2-block-data-misuse is among the derived properties (real predicate fires on this fixture)",
              "req-2-block-data-misuse" in req_ids, req_ids)


def test_build_property_pool_multi_location_requirement_expands_into_multiple_properties():
    with tempfile.TemporaryDirectory() as tmp:
        routed, ctx, entry = _real_routed_and_ctx(Path(tmp))
        props = build_property_pool(routed, Path(tmp), pg=None, slither=ctx.slither, max_total_instances=6)
        block_data_props = [p for p in props if p.requirement_id == "req-2-block-data-misuse"]
        check("req-2-block-data-misuse expands into >=2 properties (touchA and touchB both read block.timestamp)",
              len(block_data_props) >= 2, block_data_props)
        targets = {p.target_function for p in block_data_props}
        check("both touchA and touchB represented", {"touchA", "touchB"}.issubset(targets), targets)


def test_build_property_pool_assigns_reasoning_category():
    with tempfile.TemporaryDirectory() as tmp:
        routed, ctx, entry = _real_routed_and_ctx(Path(tmp))
        props = build_property_pool(routed, Path(tmp), pg=None, slither=ctx.slither)
        block_data_props = [p for p in props if p.requirement_id == "req-2-block-data-misuse"]
        check("reasoning_category assigned (not left None) for a known static requirement",
              all(p.reasoning_category is not None for p in block_data_props), block_data_props)


def test_build_property_pool_skips_not_applicable_and_deterministic_complete():
    with tempfile.TemporaryDirectory() as tmp:
        routed, ctx, entry = _real_routed_and_ctx(Path(tmp))
        props = build_property_pool(routed, Path(tmp), pg=None, slither=ctx.slither)
        # req-3-annotate is DETERMINISTIC_COMPLETE -- must never appear (already resolved, conformance_state is not None)
        check("DETERMINISTIC_COMPLETE requirement (req-3-annotate) not in the property pool",
              not any(p.requirement_id == "req-3-annotate" for p in props))


# --- prepare_cluster_investigations (grouping + context generation, no Codex) --

def test_prepare_cluster_investigations_produces_real_context():
    with tempfile.TemporaryDirectory() as tmp:
        routed, ctx, entry = _real_routed_and_ctx(Path(tmp))
        props = build_property_pool(routed, Path(tmp), pg=None, slither=ctx.slither)
        clusters, by_id, protocol_md, req_ctx = prepare_cluster_investigations(
            props, GROUPING_POLICY_G2_CONTEXT_AWARE, "test-audit", ctx.slither, ["BlockDataUser.sol"],
        )
        check("clusters cover every property exactly once",
              sorted(pid for c in clusters for pid in c.property_ids) == sorted(by_id.keys()))
        check("protocol context mentions the real contract", "BlockDataUser" in protocol_md, protocol_md[:300])
        check("requirement context generated for every distinct requirement in the pool",
              set(req_ctx.keys()) == {p.requirement_id for p in props}, req_ctx.keys())


# --- run_cluster_investigations_live (MOCKED run_arm_g_bundle_fn only) -----

def _minimal_pool():
    from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata

    def prop(pid, req_id="req-x", **overrides):
        base = dict(property_id=pid, requirement_id=req_id, requirement_level="Q",
                    requirement_semantic_intent="Test", property_text="Tested code MUST do X.",
                    target_contract="Vault", target_function=pid, candidate_locations=(f"Vault.{pid}",))
        base.update(overrides)
        return PropertyMetadata(**base)
    return prop


def test_run_live_writes_expected_extra_files_and_calls_mock_once_per_cluster():
    prop = _minimal_pool()
    p1, p2 = prop("f1"), prop("f2")
    by_id = {"f1": p1, "f2": p2}
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    cluster = Cluster(cluster_id="cluster_000", property_ids=("f1", "f2"), grouping_reason=("same_requirement",),
                       shared_context={}, estimated_context_size=2)

    calls = []

    def mock_run_arm_g(**kwargs):
        calls.append(kwargs)
        return _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": "f1", "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r1"},
            {"property_id": "f2", "verdict": "FAIL", "reasoning": "r2", "evidence": "found it"},
        ]})

    with tempfile.TemporaryDirectory() as tmp:
        verdicts, results, cost = run_cluster_investigations_live(
            [cluster], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g,
        )
        check("mock called exactly once for one cluster", len(calls) == 1, calls)
        extra_files = calls[0]["extra_files"]
        check("protocol context in extra_files", extra_files.get(".rtf/context/protocol_context.md") == "# protocol\n", extra_files)
        check("requirement context in extra_files", extra_files.get(".rtf/context/requirements/req-x.md") == "# req-x\n", extra_files)
        check("cluster plan in extra_files, mentions both property ids",
              "f1" in extra_files.get(".rtf/plans/cluster_000.md", "") and "f2" in extra_files.get(".rtf/plans/cluster_000.md", ""),
              extra_files.get(".rtf/plans/cluster_000.md"))
        check("f1 resolves PASS", verdicts["f1"].conformance_state == ConformanceState.PASS, verdicts["f1"])
        check("f2 resolves FAIL", verdicts["f2"].conformance_state == ConformanceState.FAIL, verdicts["f2"])
        check("cost accumulated", cost == 0.01, cost)


def test_run_live_incomplete_response_triggers_split_and_both_halves_investigated():
    prop = _minimal_pool()
    by_id = {f"f{i}": prop(f"f{i}") for i in range(1, 5)}
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    cluster = Cluster(cluster_id="cluster_001", property_ids=tuple(by_id.keys()), grouping_reason=("same_requirement",),
                       shared_context={}, estimated_context_size=4)

    calls = []

    # Deterministic mock: the first call (the full 4-property cluster)
    # deliberately returns an INCOMPLETE response (missing f3, f4) to
    # trigger a split; every subsequent call (a split half) answers
    # exactly the property ids actually referenced in ITS OWN prompt
    # (extracted from the prompt text, not guessed) -- so this mock is
    # correct regardless of how split_cluster's bisection assigns ids.
    def mock_run_arm_g_v2(**kwargs):
        calls.append(kwargs["case_id"])
        if len(calls) == 1:
            return _FakeArmGResult(kwargs["case_id"], {"properties": [
                {"property_id": "f1", "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
                {"property_id": "f2", "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
            ]})  # missing f3, f4 -> incomplete -> triggers split
        # For split halves we don't know exactly which ids landed where without
        # inspecting the plan text -- extract property ids referenced in the prompt.
        import re
        ids_in_prompt = set(re.findall(r"\bf[1-4]\b", kwargs["prompt"]))
        return _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": pid, "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": f"r-{pid}"}
            for pid in sorted(ids_in_prompt)
        ]})

    with tempfile.TemporaryDirectory() as tmp:
        verdicts, results, cost = run_cluster_investigations_live(
            [cluster], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g_v2, max_split_depth=2,
        )
        check("more than 1 call made (split occurred)", len(calls) > 1, calls)
        check("every original property has a verdict (none lost)", set(verdicts.keys()) == set(by_id.keys()), verdicts.keys())


def test_run_live_cost_ceiling_stops_further_clusters():
    prop = _minimal_pool()
    p1, p2 = prop("f1"), prop("f2")
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    c1 = Cluster(cluster_id="c1", property_ids=("f1",), grouping_reason=(), shared_context={}, estimated_context_size=1)
    c2 = Cluster(cluster_id="c2", property_ids=("f2",), grouping_reason=(), shared_context={}, estimated_context_size=1)
    by_id = {"f1": p1, "f2": p2}

    calls = []

    def mock_run_arm_g(**kwargs):
        calls.append(kwargs["case_id"])
        pid = "f1" if "c1" in kwargs["case_id"] else "f2"
        return _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": pid, "verdict": "PASS",
             "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
        ]}, cost_usd=100.0)

    with tempfile.TemporaryDirectory() as tmp:
        verdicts, results, cost = run_cluster_investigations_live(
            [c1, c2], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g, cost_ceiling_usd=50.0,
        )
        check("only 1 cluster actually invoked (ceiling hit after)", len(calls) == 1, calls)
        check("second cluster's property resolves INCONCLUSIVE with cost_ceiling_reached",
              verdicts["f2"].conformance_state == ConformanceState.INCONCLUSIVE and verdicts["f2"].reason == "cost_ceiling_reached",
              verdicts["f2"])


def test_run_live_crashing_cluster_does_not_kill_the_run():
    prop = _minimal_pool()
    p1, p2 = prop("f1"), prop("f2")
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    c1 = Cluster(cluster_id="c1", property_ids=("f1",), grouping_reason=(), shared_context={}, estimated_context_size=1)
    c2 = Cluster(cluster_id="c2", property_ids=("f2",), grouping_reason=(), shared_context={}, estimated_context_size=1)
    by_id = {"f1": p1, "f2": p2}

    def mock_run_arm_g(**kwargs):
        if "c1" in kwargs["case_id"]:
            raise RuntimeError("simulated crash")
        return _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": "f2", "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
        ]})

    with tempfile.TemporaryDirectory() as tmp:
        verdicts, results, cost = run_cluster_investigations_live(
            [c1, c2], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g,
        )
        check("crashed cluster's property resolves INCONCLUSIVE with a recorded reason",
              verdicts["f1"].conformance_state == ConformanceState.INCONCLUSIVE and "crashed" in verdicts["f1"].reason,
              verdicts["f1"])
        check("the OTHER cluster still completed normally", verdicts["f2"].conformance_state == ConformanceState.PASS, verdicts["f2"])


# --- aggregate_properties_to_requirements ------------------------------

def test_aggregate_fail_wins_across_properties_of_same_requirement():
    prop = _minimal_pool()
    by_id = {"f1": prop("f1", req_id="req-shared"), "f2": prop("f2", req_id="req-shared")}
    verdicts = {
        "f1": PropertyVerdict(ConformanceState.PASS, None),
        "f2": PropertyVerdict(ConformanceState.FAIL, None),
    }
    aggregated = aggregate_properties_to_requirements(verdicts, by_id)
    check("FAIL wins across 2 properties of the same requirement", aggregated["req-shared"] == ConformanceState.FAIL, aggregated)


def test_aggregate_separate_requirements_resolved_independently():
    prop = _minimal_pool()
    by_id = {"f1": prop("f1", req_id="req-a"), "f2": prop("f2", req_id="req-b")}
    verdicts = {
        "f1": PropertyVerdict(ConformanceState.PASS, None),
        "f2": PropertyVerdict(ConformanceState.FAIL, None),
    }
    aggregated = aggregate_properties_to_requirements(verdicts, by_id)
    check("req-a resolves PASS independently", aggregated["req-a"] == ConformanceState.PASS, aggregated)
    check("req-b resolves FAIL independently", aggregated["req-b"] == ConformanceState.FAIL, aggregated)


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
