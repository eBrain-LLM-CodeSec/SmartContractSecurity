"""Full 15-cluster canto (2024-01-canto) rerun with GPT-5.6 Sol as the
investigator model, through the CURRENT security-agent kernel (this
worktree's HEAD -- includes the anti-anchoring PASS gate, 73bf68c, and the
rank_evidence scope-filter fix, 881eeb3 -- unlike the model-eval harness's
frozen a61d547 checkout, which was deliberately pinned for comparability
with the earlier GLM-5.3/Sol single-property results).

Directly adapted from canto_full_rerun_grading_launch.py (the script that
produced the graded 0/2 GLM-5.2 full-cluster result,
rtf_canto_rootcause_fix_full_rerun_20260827/) -- SAME audit_id (so the
property pool/clustering is byte-identical, isolating model as the only
variable), SAME generation_client model (z-ai/glm-5.2, unrelated to
investigation quality, matching precedent), SAME per-cluster cost scaling
and step/cost ceilings. The ONLY changed line is `codex_model` (the
generic "actual investigator model string" parameter, despite the name).

Sol needed one real infra fix to run against this kernel at all:
build_tool_schemas() previously excluded 2 keyword-only-with-default
params from each tool's `required` list, which GLM tolerates but OpenAI's
own strict-mode validator rejects outright. That fix is now applied
permanently to this worktree's tools.py (not just a throwaway checkout) --
see that commit's message for the full incident writeup.

This file lives inside the worktree only because the Write tool refuses
paths outside it under worktree isolation -- every path it touches points
outside the worktree, at the real scratch run directory. Not meant to be
committed.
"""
import json
import sys
import time
from pathlib import Path

WORKTREE = Path("/scratch/md5344/evmbench/agent4vul/.claude/worktrees/security-agent-kernel")
sys.path.insert(0, str(WORKTREE))

from a4v.llm import ChatClient
from rtf.l11_investigation_grouping.semantic_only_driver import (
    build_ethtrust_structural_properties,
    run_semantic_investigation,
)
from rtf.security_agent.investigator import _PROPERTY_HEADING, run_security_agent_bundle

REPO_ROOT = Path("/scratch/md5344/.claude/jobs/a22997fe/tmp/checkouts/2024-01-canto")
RUN_DIR = Path("/scratch/md5344/evmbench/rtf_canto_full_rerun_sol_20260828")
PRIOR_RUN = Path("/scratch/md5344/evmbench/rtf_canto_live_foundry_combined_20260815")
SCRATCH_ROOT = RUN_DIR / "scratch"
CHECKPOINT_PATH = RUN_DIR / "checkpoint.jsonl"
OBSERVABILITY_ROOT = RUN_DIR / "observability"
API_KEY = Path("/scratch/md5344/evmbench/run/task5_secrets/openrouter.key").read_text().strip()
SCOPE_FILES = ["src/LendingLedger.sol"]

INVESTIGATOR_MODEL = "openai/gpt-5.6-sol"  # the ONLY changed parameter vs. the GLM-5.2 full rerun

MAX_STEPS = 60
COST_PER_PROPERTY_USD = 0.15
COST_FLOOR_USD = 0.30
TOTAL_COST_CEILING_USD = 5.00


def _max_cost_for_cluster(extra_files: dict[str, str]) -> float:
    plan = next((v for k, v in extra_files.items() if k.startswith(".rtf/plans/")), "")
    num_properties = len(_PROPERTY_HEADING.findall(plan)) or 1
    return max(COST_FLOOR_USD, COST_PER_PROPERTY_USD * num_properties)


def scaled_run_bundle(**kwargs):
    max_cost = _max_cost_for_cluster(kwargs["extra_files"])
    return run_security_agent_bundle(max_steps=MAX_STEPS, max_cost_usd=max_cost, **kwargs)


if __name__ == "__main__":
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    print("Building deterministic EthTrust structural properties...", flush=True)
    structural_started = time.time()
    structural_properties, compile_error = build_ethtrust_structural_properties(
        audit_id="2024-01-canto-rootcause-fix-full-rerun",  # SAME audit_id as the GLM-5.2 run --
        repo_root=REPO_ROOT,                                 # keeps property pool/clustering byte-identical
        entry_sol_file=REPO_ROOT / "src" / "LendingLedger.sol",
        solc_version="0.8.17",
        scope_files=SCOPE_FILES,
        compile_via_foundry=True,
    )
    structural_elapsed = time.time() - structural_started
    print(f"Structural build: {len(structural_properties)} properties, "
          f"compile_error={compile_error}, took {structural_elapsed:.1f}s", flush=True)

    generation_client = ChatClient(
        base_url="https://openrouter.ai/api/v1", api_key=API_KEY, model="z-ai/glm-5.2",
        cache_dir=PRIOR_RUN / "llm_cache", token_log_path=RUN_DIR / "generation_tokens.jsonl",
    )

    started = time.time()
    result = run_semantic_investigation(
        audit_id="2024-01-canto-rootcause-fix-full-rerun",
        repo_root=REPO_ROOT,
        entry_sol_file=REPO_ROOT / "src" / "LendingLedger.sol",
        solc_version="0.8.17",
        chat_client=generation_client,
        codex_bin=Path("/home/md5344/.local/bin/codex"),
        python_bin=Path("/scratch/md5344/evmbench/agent4vul/.claude/worktrees/rtf-v2-redesign/.venv/bin/python3"),
        mcp_server_script=WORKTREE / "rtf/l8_llm_judgment_layer/bundle_agent_experiment/graph_mcp_server.py",
        api_key=API_KEY,
        codex_model=INVESTIGATOR_MODEL,
        scratch_root=SCRATCH_ROOT,
        scope_files=SCOPE_FILES,
        compile_via_foundry=True,
        max_semantic_properties=78,
        structural_properties=structural_properties,
        max_concurrent_investigations=2,
        codex_timeout_s=900,
        cost_ceiling_usd=TOTAL_COST_CEILING_USD,
        estimated_cost_per_call_usd=0.02,
        checkpoint_path=CHECKPOINT_PATH,
        observability_root=OBSERVABILITY_ROOT,
        run_arm_g_bundle_fn=scaled_run_bundle,
    )

    summary = {
        "purpose": "full 15-cluster canto rerun with GPT-5.6 Sol as the investigator model, "
                   "through the current security-agent kernel (anti-anchoring gate + rank_evidence "
                   "fix applied) -- same audit_id/property-pool/clustering as the GLM-5.2 full rerun, "
                   "model swapped as the only variable, to check whether Sol's known single-property "
                   "success (rtf_canto_gpt56sol_capability_test_20260827, 1/1) generalizes to a real, "
                   "full-audit DetectGrader score",
        "comparison_baselines": {
            "codex_investigator_sol": {
                "run_dir": "rtf_canto_live_foundry_combined_20260815",
                "detected": 1, "ground_truth": 2, "cost_usd": 1.8376003750000003,
                "note": "GPT-5.6 Sol via Codex CLI, not this kernel",
            },
            "custom_kernel_glm52_full_rerun": {
                "run_dir": "rtf_canto_rootcause_fix_full_rerun_20260827",
                "note": "same audit_id/clustering, GLM-5.2 investigator, graded 0/2",
            },
            "custom_kernel_sol_single_property": {
                "run_dir": "rtf_canto_gpt56sol_capability_test_20260827",
                "note": "single trimmed property (req-3-implement-as-documented::loc0), 1/1, "
                        "on the FROZEN a61d547 checkout (no anti-anchoring gate) -- this run is "
                        "the first full-audit, current-kernel test of the same model",
            },
        },
        "investigator": "custom security agent, current worktree HEAD (anti-anchoring gate + "
                        "rank_evidence fix + OpenAI-strict-schema tools.py fix applied)",
        "model": INVESTIGATOR_MODEL,
        "cost_ceiling_usd_total_run": TOTAL_COST_CEILING_USD,
        "max_steps_per_cluster": MAX_STEPS,
        "max_cost_usd_per_cluster": f"scaled: max({COST_FLOOR_USD}, {COST_PER_PROPERTY_USD} * num_properties)",
        "structural_property_count": len(structural_properties),
        "structural_build_time_s": structural_elapsed,
        "wall_clock_s": time.time() - started,
        "total_cost_usd": result["total_cost_usd"],
        "in_scope_count": result["in_scope_count"],
        "out_of_scope_count": result["out_of_scope_count"],
        "scope_boundary_violations": result["scope_boundary_violations"],
        "num_clusters": len(result["clusters"]),
        "verdicts": {
            pid: {
                "conformance_state": verdict.conformance_state.value,
                "reason": verdict.reason,
                "target_contract": result["properties_by_id"][pid].target_contract,
                "statement": result["properties_by_id"][pid].property_text,
                "source_kind": result["properties_by_id"][pid].source_kind,
                "requirement_id": result["properties_by_id"][pid].requirement_id,
            }
            for pid, verdict in result["property_verdicts"].items()
        },
    }
    (RUN_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("DONE", flush=True)
    print(json.dumps({k: v for k, v in summary.items() if k != "verdicts"}, indent=2), flush=True)
