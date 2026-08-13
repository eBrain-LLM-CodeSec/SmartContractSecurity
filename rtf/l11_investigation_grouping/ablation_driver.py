"""Driver for the B-vs-D ablation of the grouped-investigation
architecture (Phase 14/15 of the plan, user-authorized scope: "skip
straight to the 3 reruns + B-vs-D ablation only").

Configuration B: properties are NOT grouped (G0_UNGROUPED -- 1 property
= 1 investigation, same call count as the pre-grouping architecture),
but EVERY investigation uses the new Markdown context/plan artifacts
(Phase 7) and the new cluster-aware prompt (Phase 8, ARM_G_CLUSTER_PROMPT_v1.md)
instead of the old inline `ARM_G_PROMPT_v3.md`-built prompt. This
isolates the value of PLANNING/context-reuse alone, independent of
grouping.

Configuration D: properties ARE grouped (a real grouping policy, default
G2_CONTEXT_AWARE) with the same context/plan artifacts and prompt. This
is the full proposed architecture.

Both configurations reuse the exact same deterministic layer (`run_rtf`,
`build_standards_routed_requirements`) the pre-existing pipeline uses --
only the AGENT_REQUIRED escalation path differs (`live_runner` instead
of `pipeline_e2e`'s own escalation loop). Real spend: real Codex calls,
same model/pricing as every other run this session made.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from dataclasses import asdict, replace
from pathlib import Path

from a4v.graph import ProgramGraph
from rtf.l11_investigation_grouping.live_runner import (
    aggregate_properties_to_requirements, build_property_pool,
    prepare_cluster_investigations, run_cluster_investigations_live,
)
from rtf.l11_investigation_grouping.property_metadata import forward_out_of_scope_context, split_properties_by_scope
from rtf.l11_investigation_grouping.run_metadata import (
    GROUPING_POLICY_G0_UNGROUPED, GROUPING_POLICY_G2_CONTEXT_AWARE, RunMetadata,
)
from rtf.l12_evaluation.metrics import ConformanceState, RoutedRequirementResult, TargetRunResult
from rtf.l12_evaluation.pilot5_driver import (
    API_KEY, CODEX_BIN, CODEX_MODEL, MCP_SERVER, PYTHON_BIN, _solc_bin_dir_for, _solc_version_for,
)
from rtf.l12_evaluation.pipeline_e2e import CORPUS_PATH, compute_aggregation_requirements
from rtf.l12_evaluation.run_grader import run_grader
from rtf.l12_evaluation.run_rtf import build_context_for_evmbench_target, load_requirement_levels, load_unconditioned_map, run_rtf
from rtf.l5_predicates.compile_helper import _collect_remappings
from rtf.standards.routing import build_standards_routed_requirements

CONFIG_TO_POLICY = {"B": GROUPING_POLICY_G0_UNGROUPED, "D": GROUPING_POLICY_G2_CONTEXT_AWARE}


def run_config_entry(
    *,
    audit_id: str,
    rel_path: str,
    repo_root: Path,
    config: str,
    scope_files: list[str],
    scratch_root: Path,
    cost_ceiling_usd: float,
    default_solc_version: str,
    path_prefix_overrides: dict[str, str],
    run_arm_g_bundle_fn=None,
    extra_solc_args: list[str] | None = None,
    max_concurrent_investigations: int = 1,
    investigation_model: str | None = None,
    cluster_limit: int | None = None,
    run_variant: str | None = None,
    target_functions: list[str] | None = None,
) -> dict:
    """Runs ONE (entry, configuration) pair. Returns a summary dict
    (saved to disk by the caller) -- never raises for a real per-entry
    failure (compile error, crashed investigation); those are recorded
    in the returned dict's "error" field instead, matching
    `pilot5_driver.py`'s own "one entry's crash must not kill the whole
    audit" convention.

    `run_arm_g_bundle_fn`, when given, is passed straight through to
    `run_cluster_investigations_live` -- the ONLY way to dry-run this
    entire function (real compile, real property derivation, real
    grouping/context generation, everything except the actual Codex
    call) with zero spend. Defaults to None, which resolves to the real
    `run_arm_g_bundle` -- a live, paid call.

    `target_functions`, when given, restricts the run to clusters whose
    property pool includes at least one property targeting one of these
    function names (case-insensitive substring match against
    `PropertyMetadata.target_function`). Applied after `cluster_limit`
    truncation, so pass `cluster_limit=None` when using this.
    """
    assert config in CONFIG_TO_POLICY, f"unknown config {config!r}, must be 'B' or 'D'"
    policy_name = CONFIG_TO_POLICY[config]
    model = investigation_model or CODEX_MODEL

    entry_file = repo_root / rel_path.lstrip("./")
    solc_version = _solc_version_for(rel_path, default_solc_version, path_prefix_overrides)
    solc_path_dir = _solc_bin_dir_for(solc_version, scratch_root)

    t0 = time.time()
    try:
        ctx, compile_error = build_context_for_evmbench_target(
            entry_file, repo_root, solc_version, extra_solc_args=extra_solc_args,
        )
        if ctx.slither is None:
            return {"entry": rel_path, "config": config, "error": f"compile_failed: {compile_error}"}

        unconditioned_map = load_unconditioned_map(CORPUS_PATH)
        requirement_levels = load_requirement_levels(CORPUS_PATH)
        run, _raw = run_rtf(ctx, audit_id, unconditioned_map)

        generated_bundles: dict = {}
        if ctx.repo_root is not None:
            generated_routed, _standards_report, generated_bundles = build_standards_routed_requirements(
                repo_root=ctx.repo_root, entry_sol_file=entry_file, slither=ctx.slither,
            )
            run = TargetRunResult(audit_id=run.audit_id, routed={**run.routed, **generated_routed})

        pg = None
        try:
            pg = ProgramGraph.from_slither(ctx.slither)
        except Exception:  # noqa: BLE001 -- graph enrichment is best-effort, never blocks the run
            pg = None

        properties = build_property_pool(run.routed, repo_root, generated_bundles, pg=pg, slither=ctx.slither, scope_files=scope_files)
        in_scope_properties, out_of_scope_properties = split_properties_by_scope(properties, scope_files)
        properties = forward_out_of_scope_context(in_scope_properties, out_of_scope_properties)

        if not properties:
            new_routed = compute_aggregation_requirements(dict(run.routed), requirement_levels)
            return {
                "entry": rel_path, "config": config, "wall_s": time.time() - t0, "codex_cost": 0.0,
                "num_properties": 0, "num_investigation_instances": 0,
                "conformance_by_req": {k: (v.conformance_state.value if v.conformance_state else None) for k, v in new_routed.items()},
                "fail_count": sum(1 for v in new_routed.values() if v.conformance_state == ConformanceState.FAIL),
                "raw_property_entries": {},
            }

        clusters, properties_by_id, protocol_md, req_ctx_md = prepare_cluster_investigations(
            properties, policy_name, audit_id, ctx.slither, scope_files,
        )
        if cluster_limit is not None:
            clusters = clusters[:max(0, cluster_limit)]
        if target_functions:
            wanted = [t.lower() for t in target_functions]
            clusters = [
                c for c in clusters
                if any(
                    properties_by_id[pid].target_function
                    and any(w in properties_by_id[pid].target_function.lower() for w in wanted)
                    for pid in c.property_ids
                )
            ]
        remaps = _collect_remappings(repo_root)

        verdicts, arm_g_results, cost, raw_entries = run_cluster_investigations_live(
            clusters, properties_by_id, protocol_md, req_ctx_md,
            audit_id=audit_id, entry_sol_file=entry_file, project_root=repo_root,
            codex_bin=CODEX_BIN, python_bin=PYTHON_BIN, mcp_server_script=MCP_SERVER,
            api_key=API_KEY, codex_model=model, solc_path_dir=solc_path_dir, solc_remaps=remaps,
            scratch_root=scratch_root, cost_ceiling_usd=cost_ceiling_usd,
            run_arm_g_bundle_fn=run_arm_g_bundle_fn,
            max_concurrent_investigations=max_concurrent_investigations,
            run_variant=run_variant or config,
        )

        aggregated = aggregate_properties_to_requirements(verdicts, properties_by_id)
        new_routed = dict(run.routed)
        for req_id, state in aggregated.items():
            prior = new_routed[req_id]
            new_routed[req_id] = replace(prior, conformance_state=state)
        new_routed = compute_aggregation_requirements(new_routed, requirement_levels)

        fail_req_ids = [k for k, v in new_routed.items() if v.conformance_state == ConformanceState.FAIL]

        return {
            "entry": rel_path, "config": config, "grouping_policy": policy_name,
            "investigation_model": model,
            "wall_s": time.time() - t0, "codex_cost": cost,
            "num_properties": len(properties), "num_investigation_instances": len(arm_g_results),
            "num_clusters": len(clusters),
            "conformance_by_req": {k: (v.conformance_state.value if v.conformance_state else None) for k, v in new_routed.items()},
            "fail_count": len(fail_req_ids),
            "fail_req_ids": fail_req_ids,
            "properties_by_id": {pid: asdict(p) for pid, p in properties_by_id.items()},
            "property_verdicts": {pid: {"conformance_state": v.conformance_state.value, "reason": v.reason} for pid, v in verdicts.items()},
            "raw_property_entries": raw_entries,
            "run_metadata": RunMetadata(grouping_policy=policy_name).as_dict(),
        }
    except Exception as e:  # noqa: BLE001 -- one entry's crash must not kill the whole audit
        return {"entry": rel_path, "config": config, "error": f"{type(e).__name__}: {e}",
                "traceback": traceback.format_exc()[-3000:], "wall_s": time.time() - t0}


def render_ablation_audit_md(audit_id: str, config: str, entry_results: list[dict]) -> str:
    """Renders a simple, real audit.md-shaped report from one config's
    entry results -- reusing raw_property_entries for evidence text
    (not report_generator.py's schema, which is req_id-only; this report
    is property-level, a strict superset of detail)."""
    lines = [f"# Security Audit Report: {audit_id} (config {config})\n"]
    any_fail = False
    for entry in entry_results:
        if entry.get("error"):
            lines.append(f"## Entry `{entry['entry']}`: ERROR\n{entry['error']}\n")
            continue
        for req_id in entry.get("fail_req_ids", []):
            any_fail = True
            lines.append(f"## {req_id} (entry: `{entry['entry']}`)\n")
            for pid, pv in entry.get("property_verdicts", {}).items():
                prop = entry.get("properties_by_id", {}).get(pid, {})
                if prop.get("requirement_id") != req_id or pv.get("conformance_state") != "FAIL":
                    continue
                raw = entry.get("raw_property_entries", {}).get(pid, {})
                lines.append(f"### Property `{pid}`\n")
                lines.append(f"**Target:** `{prop.get('target_contract')}.{prop.get('target_function')}`\n")
                lines.append(f"**Property text:** {prop.get('property_text')}\n")
                if raw.get("evidence"):
                    lines.append(f"**Evidence:** {raw['evidence']}\n")
                if raw.get("reasoning"):
                    lines.append(f"**Reasoning:** {raw['reasoning']}\n")
                if raw.get("vulnerable_location"):
                    lines.append(f"**Location:** {raw['vulnerable_location']}\n")
    if not any_fail:
        lines.append("No FAIL findings were produced by this configuration.\n")
    return "\n".join(lines)


def run_audit_ablation(
    audit_id: str, repo_root: Path, scope_files: list[str], scratch_root: Path, artifacts_dir: Path,
    per_entry_cost_ceiling_usd: float, default_solc_version: str, path_prefix_overrides: dict[str, str] | None = None,
    extra_solc_args: list[str] | None = None, max_concurrent_investigations: int = 1,
) -> dict:
    """Runs BOTH configuration B and D for every scope file, saving
    per-entry results to disk immediately after each (so a crash
    mid-run doesn't lose already-completed, already-paid-for entries).
    """
    path_prefix_overrides = path_prefix_overrides or {}
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    scratch_root.mkdir(parents=True, exist_ok=True)

    summary = {"audit_id": audit_id, "scope_files": scope_files, "configs": {}}

    for config in ("B", "D"):
        entry_results = []
        total_cost = 0.0
        for i, rel_path in enumerate(scope_files):
            result_path = artifacts_dir / f"entry_{i:02d}_{Path(rel_path).stem}_{config}.json"
            if result_path.exists():
                result = json.loads(result_path.read_text())
                print(f"[{audit_id}][{config}] entry {i+1}/{len(scope_files)}: {rel_path} -- RESUMED", flush=True)
            else:
                print(f"[{audit_id}][{config}] entry {i+1}/{len(scope_files)}: {rel_path} -- running...", flush=True)
                result = run_config_entry(
                    audit_id=audit_id, rel_path=rel_path, repo_root=repo_root, config=config,
                    scope_files=scope_files, scratch_root=scratch_root,
                    cost_ceiling_usd=per_entry_cost_ceiling_usd, default_solc_version=default_solc_version,
                    path_prefix_overrides=path_prefix_overrides, extra_solc_args=extra_solc_args,
                    max_concurrent_investigations=max_concurrent_investigations,
                )
                result_path.write_text(json.dumps(result, indent=2, default=str))
                print(f"[{audit_id}][{config}] entry {rel_path} DONE. cost=${result.get('codex_cost', 0.0):.4f} "
                      f"fails={result.get('fail_count', '?')} error={result.get('error')}", flush=True)
            entry_results.append(result)
            total_cost += result.get("codex_cost", 0.0)

        audit_md = render_ablation_audit_md(audit_id, config, entry_results)
        audit_md_path = artifacts_dir / f"audit_{config}.md"
        audit_md_path.write_text(audit_md)

        grade_result = None
        grade_error = None
        try:
            import asyncio
            grade_result = asyncio.run(run_grader(audit_id, audit_md_path, judge_model=CODEX_MODEL))
        except Exception as e:  # noqa: BLE001 -- grading failure must not lose the real investigation results
            grade_error = f"{type(e).__name__}: {e}"

        summary["configs"][config] = {
            "investigation_model": CODEX_MODEL,
            "judge_model": CODEX_MODEL,
            "total_codex_cost_usd": total_cost,
            "entries": entry_results,
            "total_fail_count": sum(r.get("fail_count", 0) for r in entry_results),
            "grade_result": grade_result,
            "grade_error": grade_error,
        }
        print(f"[{audit_id}][{config}] GRADED: {grade_result and grade_result.get('score')} "
              f"(error={grade_error})", flush=True)

    (artifacts_dir / "ablation_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    audit_id = sys.argv[1]
    repo_root = Path(sys.argv[2])
    scope_file = Path(sys.argv[3])
    artifacts_dir = Path(sys.argv[4])
    per_entry_ceiling = float(sys.argv[5]) if len(sys.argv) > 5 else 8.0
    default_solc_version = sys.argv[6] if len(sys.argv) > 6 else "0.8.20"
    overrides_json = sys.argv[7] if len(sys.argv) > 7 else "{}"

    scope_files = [l.strip() for l in scope_file.read_text().splitlines() if l.strip()]
    path_prefix_overrides = json.loads(overrides_json)
    import os
    job_dir = os.environ.get("CLAUDE_JOB_DIR", "/scratch/md5344/.claude/jobs/76236636")
    scratch_root = Path(f"{job_dir}/tmp/ablation_scratch/{audit_id}")

    run_audit_ablation(audit_id, repo_root, scope_files, scratch_root, artifacts_dir,
                        per_entry_ceiling, default_solc_version, path_prefix_overrides)
