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
        verdicts, results, cost, raw_entries = run_cluster_investigations_live(
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
        check("raw_entries has the real evidence text for f2's FAIL",
              raw_entries.get("f2", {}).get("evidence") == "found it", raw_entries.get("f2"))
        check("raw_entries has both property ids", set(raw_entries.keys()) == {"f1", "f2"}, raw_entries.keys())


def test_compile_via_foundry_propagates_to_every_run_arm_g_bundle_fn_call():
    """RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md SS13: proves the plumbing
    reaches the real call site (`_invoke`'s `run_arm_g_bundle_fn(...,
    compile_via_foundry=...)`), without needing a real Codex binary --
    `arm_g_codex.run_arm_g_bundle`'s own env-var wiring is separately
    tested in `test_arm_g_codex_foundry_wiring.py`.
    """
    prop = _minimal_pool()
    p1 = prop("f1")
    by_id = {"f1": p1}
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    cluster = Cluster(cluster_id="cluster_000", property_ids=("f1",), grouping_reason=("same_requirement",),
                       shared_context={}, estimated_context_size=1)

    calls = []

    def mock_run_arm_g(**kwargs):
        calls.append(kwargs)
        return _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": "f1", "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r1"},
        ]})

    with tempfile.TemporaryDirectory() as tmp:
        run_cluster_investigations_live(
            [cluster], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g, compile_via_foundry=True,
        )
        check("compile_via_foundry=True reached the mocked run_arm_g_bundle_fn",
              calls[0].get("compile_via_foundry") is True, calls)

    calls.clear()
    with tempfile.TemporaryDirectory() as tmp:
        run_cluster_investigations_live(
            [cluster], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g,
        )
        check("compile_via_foundry defaults to False when omitted (unchanged prior behavior)",
              calls[0].get("compile_via_foundry") is False, calls)


def test_prepare_cluster_context_filters_vendor_when_repo_root_is_given():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "src").mkdir()
        (repo / "lib").mkdir()
        (repo / "lib" / "Vendor.sol").write_text(
            "pragma solidity ^0.8.20; contract Vendor { function vendored() external {} }",
            encoding="utf-8",
        )
        (repo / "src" / "Entry.sol").write_text(
            'pragma solidity ^0.8.20; import "../lib/Vendor.sol"; contract Entry { function run() external {} }',
            encoding="utf-8",
        )
        from rtf.l5_predicates.compile_helper import compile_evmbench_target
        slither = compile_evmbench_target(repo / "src" / "Entry.sol", repo, solc_version="0.8.20")
        _clusters, _by_id, context, _reqs = prepare_cluster_investigations(
            [], GROUPING_POLICY_G2_CONTEXT_AWARE, "vendor-context", slither,
            ["src/Entry.sol"], repo_root=repo,
        )
        check("prepare context: first-party Entry remains", "**Entry**" in context, context)
        check("prepare context: vendored Vendor excluded", "**Vendor**" not in context, context)


def test_prepare_cluster_context_uses_explicit_enriched_override():
    enriched = "# Enriched protocol context\n\nA vetted narrative and structural view.\n"
    clusters, by_id, context, reqs = prepare_cluster_investigations(
        [], GROUPING_POLICY_G2_CONTEXT_AWARE, "override", object(), [],
        protocol_context_override=enriched,
    )
    check("prepare context: explicit enriched context is preserved byte-for-byte",
          context == enriched, context)


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
        verdicts, results, cost, raw_entries = run_cluster_investigations_live(
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
        verdicts, results, cost, raw_entries = run_cluster_investigations_live(
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
        verdicts, results, cost, raw_entries = run_cluster_investigations_live(
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


# --- max_concurrent_investigations: genuine overlap + correctness ----------

def test_default_max_concurrent_investigations_is_serial():
    """Omitting the parameter must exercise EXACTLY the same code path
    as before it existed -- calls happen one at a time, not just
    'eventually all complete'."""
    prop = _minimal_pool()
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    clusters = [Cluster(cluster_id=f"c{i}", property_ids=(f"f{i}",), grouping_reason=(),
                         shared_context={}, estimated_context_size=1) for i in range(3)]
    by_id = {f"f{i}": prop(f"f{i}") for i in range(3)}

    import threading
    max_in_flight = [0]
    current_in_flight = [0]
    lock = threading.Lock()

    def mock_run_arm_g(**kwargs):
        with lock:
            current_in_flight[0] += 1
            max_in_flight[0] = max(max_in_flight[0], current_in_flight[0])
        pid = kwargs["case_id"].split("__")[-1].replace("c", "f")
        result = _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": pid, "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
        ]})
        with lock:
            current_in_flight[0] -= 1
        return result

    with tempfile.TemporaryDirectory() as tmp:
        run_cluster_investigations_live(
            clusters, by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g,
        )
        check("default: never more than 1 call in flight at once (serial)", max_in_flight[0] == 1, max_in_flight[0])


def test_concurrent_investigations_actually_overlap_in_time():
    """Barrier-based genuine-overlap proof, same rigor as
    test_concurrent_escalation.py's own proof for pipeline_e2e.py: each
    mock call blocks on a shared Barrier until N=3 calls are
    simultaneously in flight. If still serial, this deadlocks --
    completion within the timeout IS the proof."""
    import threading

    prop = _minimal_pool()
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    N = 3
    clusters = [Cluster(cluster_id=f"c{i}", property_ids=(f"f{i}",), grouping_reason=(),
                         shared_context={}, estimated_context_size=1) for i in range(N)]
    by_id = {f"f{i}": prop(f"f{i}") for i in range(N)}

    barrier = threading.Barrier(N, timeout=10)
    max_in_flight = [0]
    current_in_flight = [0]
    lock = threading.Lock()

    def mock_run_arm_g(**kwargs):
        with lock:
            current_in_flight[0] += 1
            max_in_flight[0] = max(max_in_flight[0], current_in_flight[0])
        barrier.wait()  # deadlocks unless all N calls are concurrently in flight
        with lock:
            current_in_flight[0] -= 1
        pid = kwargs["case_id"].split("__")[-1].replace("c", "f")
        return _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": pid, "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
        ]})

    with tempfile.TemporaryDirectory() as tmp:
        try:
            verdicts, results, cost, raw = run_cluster_investigations_live(
                clusters, by_id, "# protocol\n", {"req-x": "# req-x\n"},
                audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
                codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
                api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
                scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g, max_concurrent_investigations=N,
            )
            check("concurrent: completed without deadlocking (proves real overlap)", True)
            check("concurrent: peak simultaneous in-flight calls reached N", max_in_flight[0] == N, max_in_flight[0])
            check("concurrent: all 3 properties still correctly resolved", all(
                verdicts[f"f{i}"].conformance_state == ConformanceState.PASS for i in range(N)
            ), verdicts)
        except Exception as e:  # noqa: BLE001 -- a barrier timeout manifests as an exception, i.e. NOT concurrent
            check("concurrent: completed without deadlocking (proves real overlap)", False, f"{type(e).__name__}: {e}")


def test_cost_ceiling_reservation_limits_batch_size_under_concurrency():
    """Real-incident-motivated fix (2026-08-14, an interrupted real
    2024-08-phi investigation reported the cost ceiling was "checked
    between concurrent batches, not reserved per in-flight call").
    max_concurrent_investigations=4 but a ceiling that can only afford 1
    call at the estimated per-call cost: peak in-flight concurrency must
    stay at 1 across the whole run, never jump to 4 and overspend once
    all 4 completed calls are counted.
    """
    import threading
    import time as _time

    prop = _minimal_pool()
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    N = 4
    clusters = [Cluster(cluster_id=f"c{i}", property_ids=(f"f{i}",), grouping_reason=(),
                         shared_context={}, estimated_context_size=1) for i in range(N)]
    by_id = {f"f{i}": prop(f"f{i}") for i in range(N)}

    max_in_flight = [0]
    current_in_flight = [0]
    lock = threading.Lock()

    def mock_run_arm_g(**kwargs):
        with lock:
            current_in_flight[0] += 1
            max_in_flight[0] = max(max_in_flight[0], current_in_flight[0])
        _time.sleep(0.1)
        with lock:
            current_in_flight[0] -= 1
        pid = kwargs["case_id"].split("__")[-1].replace("c", "f")
        return _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": pid, "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
        ]}, cost_usd=0.30)

    with tempfile.TemporaryDirectory() as tmp:
        verdicts, results, cost, raw = run_cluster_investigations_live(
            clusters, by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g, max_concurrent_investigations=N,
            cost_ceiling_usd=0.50, estimated_cost_per_call_usd=0.30,
        )
        check("cost reservation: peak in-flight concurrency capped below max_concurrent_investigations",
              max_in_flight[0] < N, max_in_flight[0])
        check("cost reservation: total cost stayed well under what unrestricted concurrency would have spent",
              cost < 0.30 * N, cost)


def test_checkpoint_round_trip_and_resume_skips_completed_clusters():
    """Real-incident-motivated fix: proves a checkpoint file written
    during one call to `run_cluster_investigations_live` lets a SECOND
    call (simulating a resumed run after an interruption) skip
    re-dispatching a cluster whose property already has a checkpointed
    verdict, and correctly restores total_cost from what was already
    spent.
    """
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
            {"property_id": pid, "verdict": "FAIL", "evidence": f"real evidence for {pid}",
             "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
        ]}, cost_usd=0.05)

    with tempfile.TemporaryDirectory() as tmp:
        checkpoint_path = Path(tmp) / "checkpoint.jsonl"

        # First "run": only c1 gets to complete (simulates c2 never finishing
        # before an interruption -- we simply never dispatch it here).
        verdicts1, _results1, cost1, raw1 = run_cluster_investigations_live(
            [c1], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g, checkpoint_path=checkpoint_path,
        )
        check("checkpoint: c1 resolved FAIL on the first run", verdicts1["f1"].conformance_state == ConformanceState.FAIL, verdicts1)
        check("checkpoint: file was actually written", checkpoint_path.exists(), checkpoint_path)

        calls.clear()
        # "Resumed" run: pass BOTH clusters again (as a real resumed run
        # would, re-deriving the full pool) -- c1 must be skipped entirely.
        verdicts2, _results2, cost2, raw2 = run_cluster_investigations_live(
            [c1, c2], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g, checkpoint_path=checkpoint_path,
        )
        check("checkpoint: resumed run never re-dispatched c1 (only c2's case_id was invoked)",
              calls == ["test-audit__Vault__c2"], calls)
        check("checkpoint: resumed run's verdicts include f1 (restored from checkpoint) and f2 (freshly resolved)",
              verdicts2["f1"].conformance_state == ConformanceState.FAIL and verdicts2["f2"].conformance_state == ConformanceState.FAIL,
              verdicts2)
        check("checkpoint: resumed run's raw_entries restored f1's real evidence text from the checkpoint",
              raw2.get("f1", {}).get("evidence") == "real evidence for f1", raw2)
        check("checkpoint: resumed run's total_cost includes the FIRST run's already-spent cost",
              cost2 == cost1 + 0.05, (cost1, cost2))


def test_checkpoint_resume_skip_is_keyed_on_property_ids_not_cluster_id():
    """RTF_SECURITY_AGENT_CONTEXT_MANAGEMENT_DESIGN.md section 9: resume
    must key on property_ids (or a stable cluster fingerprint), never a
    transient cluster-name label -- because clustering itself can
    legitimately (or, before the grouping_engine.py tie-break fix,
    non-deterministically) assign a different cluster_id to the exact
    same grouping of properties across two process launches (e.g.
    "cluster_003" vs "cluster_005" for an identical {f1} singleton,
    since cluster_id is only a post-hoc sorted-enumeration index --
    grouping_engine.py's own `for idx, member_ids in enumerate(sorted(
    clusters, key=...))`). Checkpoints f1 under cluster_id "c1", then
    presents the SAME property (f1 alone, already fully resolved) under
    an entirely different, never-before-seen cluster_id "c_renamed" on
    the "resumed" call. It must still be skipped (never re-dispatched),
    proving the skip check (`set(cluster.property_ids) <=
    resolved_property_ids`, live_runner.py) is content-keyed on
    property_ids, not on cluster_id matching a prior run's label.

    A cluster that only PARTIALLY overlaps the checkpoint (mixes an
    already-resolved property with a brand-new one) is a separate,
    already-covered scenario (`test_run_live_incomplete_response_
    triggers_split_and_both_halves_investigated`'s split-on-incomplete-
    response path applies there since the whole cluster is dispatched
    and must be answered in full) -- deliberately not re-tested here to
    keep this test isolated to the specific property_ids-vs-cluster_id
    identity question.
    """
    prop = _minimal_pool()
    p1 = prop("f1")
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    c1 = Cluster(cluster_id="c1", property_ids=("f1",), grouping_reason=(), shared_context={}, estimated_context_size=1)
    by_id = {"f1": p1}

    def mock_run_arm_g_first(**kwargs):
        return _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": "f1", "verdict": "FAIL", "evidence": "real evidence for f1",
             "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
        ]}, cost_usd=0.05)

    with tempfile.TemporaryDirectory() as tmp:
        checkpoint_path = Path(tmp) / "checkpoint.jsonl"
        run_cluster_investigations_live(
            [c1], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g_first, checkpoint_path=checkpoint_path,
        )

        # Same single property, same content, but a DIFFERENT, never-
        # before-seen cluster_id -- as a re-clustering pass would produce.
        c1_renamed = Cluster(cluster_id="c_renamed_by_reclustering", property_ids=("f1",),
                             grouping_reason=(), shared_context={}, estimated_context_size=1)
        calls = []

        def mock_run_arm_g_second(**kwargs):
            calls.append(kwargs["case_id"])
            raise AssertionError("must not be dispatched: f1 was already fully resolved in the checkpoint")

        verdicts2, _results2, cost2, raw2 = run_cluster_investigations_live(
            [c1_renamed], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g_second, checkpoint_path=checkpoint_path,
        )
        check("a fully-resolved property under a brand-new cluster_id is never re-dispatched",
              calls == [], calls)
        check("f1's checkpointed verdict is restored regardless of the new cluster_id",
              verdicts2["f1"].conformance_state == ConformanceState.FAIL and
              raw2.get("f1", {}).get("evidence") == "real evidence for f1", (verdicts2, raw2))
        check("resumed total_cost still reflects only the first run's spend (nothing re-dispatched)",
              cost2 == 0.05, cost2)


def test_split_halves_processed_in_a_later_batch_under_concurrency():
    """A split cluster's halves must still be investigated (not dropped)
    when concurrency > 1 -- the pending-queue design (not immediate
    recursion) must correctly re-enqueue them for the next batch."""
    prop = _minimal_pool()
    by_id = {f"f{i}": prop(f"f{i}") for i in range(1, 5)}
    from rtf.l11_investigation_grouping.grouping_engine import Cluster
    cluster = Cluster(cluster_id="c1", property_ids=tuple(by_id.keys()), grouping_reason=("same_requirement",),
                       shared_context={}, estimated_context_size=4)

    call_count = [0]

    def mock_run_arm_g(**kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # First call: incomplete (missing f3, f4) -> triggers a split.
            return _FakeArmGResult(kwargs["case_id"], {"properties": [
                {"property_id": "f1", "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
                {"property_id": "f2", "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": "r"},
            ]})
        import re
        plan_content = "".join(v for k, v in kwargs.get("extra_files", {}).items() if k.startswith(".rtf/plans/"))
        ids_in_plan = sorted(set(re.findall(r"`(f[1-4])`", plan_content)))
        return _FakeArmGResult(kwargs["case_id"], {"properties": [
            {"property_id": pid, "verdict": "PASS", "counterexample_attempt": "x" * 20, "counterexample_result": "y" * 20, "reasoning": f"r-{pid}"}
            for pid in ids_in_plan
        ]})

    with tempfile.TemporaryDirectory() as tmp:
        verdicts, results, cost, raw = run_cluster_investigations_live(
            [cluster], by_id, "# protocol\n", {"req-x": "# req-x\n"},
            audit_id="test-audit", entry_sol_file=Path(tmp) / "Vault.sol", project_root=Path(tmp),
            codex_bin=Path("/nonexistent"), python_bin=Path("/nonexistent"), mcp_server_script=Path("/nonexistent"),
            api_key="unused", codex_model="unused", solc_path_dir="/nonexistent", solc_remaps=None,
            scratch_root=Path(tmp), run_arm_g_bundle_fn=mock_run_arm_g, max_concurrent_investigations=2,
        )
        check("split halves eventually investigated under concurrency (none lost)",
              set(verdicts.keys()) == set(by_id.keys()), verdicts.keys())
        check("all resolve PASS (split halves correctly answered)",
              all(v.conformance_state == ConformanceState.PASS for v in verdicts.values()), verdicts)


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
