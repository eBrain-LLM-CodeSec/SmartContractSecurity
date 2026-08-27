#!/usr/bin/env python3
"""Standalone subprocess worker: the ONLY place this harness imports
`rtf.security_agent.investigator`/`kernel`/`l11_investigation_grouping`
etc. from the frozen baseline checkout (a61d547 + the independent
rank_evidence fix, 881eeb3 -- the exact scaffold GLM-5.3 and GPT-5.6 Sol
were already tested against) rather than from this worktree's own,
possibly-different copy (e.g. a future 73bf68c anti-anchoring gate).

Why a SEPARATE PROCESS rather than an in-process import: this file lives
inside the `rtf.security_agent.eval` package, so simply running it as
`python3 _frozen_worker.py` would still resolve `rtf` via whatever is on
sys.path[0] (the script's own directory) UNLESS invoked with a bare
filename and its OWN directory as cwd/sys.path[0] -- which is exactly how
it's invoked: `run_model_eval.py` launches it as
`subprocess.run([python_bin, str(WORKER_SCRIPT_PATH), ...])`, a fresh
Python process with its own sys.modules, so there is no risk of the
worktree's already-imported `rtf.security_agent` package colliding with
the frozen checkout's copy -- the exact fragility that would occur trying
to do this via `sys.path.insert(0, ...)` tricks inside a process that has
already imported `rtf.security_agent` (as `run_model_eval.py` necessarily
has, being part of that same package). This mirrors, and generalizes,
the standalone-script pattern glm53_capability_test_launch.py and
gpt56sol_capability_test_launch.py already proved out twice.

Secrets: the API key is passed via the `MODEL_EVAL_API_KEY` environment
variable (subprocess env dict), never via argv (visible in `ps`) and
never written to any artifact this worker produces.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Same pattern as rtf.security_agent.investigator._PROPERTY_HEADING (the
# frozen checkout's copy) -- duplicated here, at module level, rather than
# imported, so `trim_plan_to_single_property` is unit-testable without a
# live baseline-checkout import (test_frozen_worker.py). A stable,
# trivial regex; not expected to drift, but if it ever needs to,
# investigator.py's copy is the one actually used at runtime -- keep both
# in sync.
_PROPERTY_HEADING = re.compile(r"^### `([^`]+)`\s*$", re.MULTILINE)


def trim_plan_to_single_property(full_plan: str, property_id: str) -> str:
    """Keeps the plan's preamble (objective/grouping/files sections, up to
    the first property heading) plus exactly one property's own section --
    the mechanism that keeps a single-property investigation from ever
    seeing sibling properties' candidate locations/context (Phase 16 Test
    4: single-property selection excludes all other properties)."""
    matches = list(_PROPERTY_HEADING.finditer(full_plan))
    starts = [m.start() for m in matches] + [len(full_plan)]
    for idx, m in enumerate(matches):
        if m.group(1) == property_id:
            return full_plan[:matches[0].start()] + full_plan[m.start():starts[idx + 1]]
    raise ValueError(f"{property_id} not found in plan headings: {[m.group(1) for m in matches]}")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline-checkout", required=True)
    p.add_argument("--audit-id")
    p.add_argument("--repo-root")
    p.add_argument("--scope-files", help="JSON list")
    p.add_argument("--solc-version")
    p.add_argument("--entry-file-relative")
    p.add_argument("--property-id")
    p.add_argument("--model")
    p.add_argument("--reasoning-effort", default="low")
    p.add_argument("--case-id")
    p.add_argument("--scratch-root")
    p.add_argument("--generation-cache-dir")
    p.add_argument("--generation-model", default="z-ai/glm-5.2")
    p.add_argument("--generation-tokens-log")
    p.add_argument("--max-steps", type=int, default=60)
    p.add_argument("--max-cost-usd", type=float, default=0.30)
    p.add_argument("--max-wall-clock-s", type=float, default=900.0)
    p.add_argument("--result-path", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--emit-tool-schemas", action="store_true",
                    help="Write the frozen checkout's real tool schema list (13 read tools + "
                         "native action tools) to --result-path and exit -- no pipeline regen, "
                         "no investigation. Lets preflight.py test the EXACT wire schema the real "
                         "run will send, from the same pinned checkout, without importing kernel "
                         "code in-process (see module docstring).")
    return p.parse_args()


_REQUIRED_FOR_REAL_RUN = (
    "audit_id", "repo_root", "scope_files", "solc_version", "entry_file_relative",
    "property_id", "model", "case_id", "scratch_root", "generation_cache_dir", "generation_tokens_log",
)


def main() -> None:
    args = _parse_args()
    sys.path.insert(0, args.baseline_checkout)

    if args.emit_tool_schemas:
        from rtf.security_agent.kernel import NATIVE_RESPONSE_MODELS
        from rtf.security_agent.response_schema import build_action_tool_schemas
        from rtf.security_agent.tools import build_tool_schemas
        schemas = build_tool_schemas() + build_action_tool_schemas(NATIVE_RESPONSE_MODELS)
        Path(args.result_path).write_text(json.dumps(schemas, indent=2), encoding="utf-8")
        return

    missing = [name for name in _REQUIRED_FOR_REAL_RUN if getattr(args, name) is None]
    if missing:
        raise SystemExit(f"missing required arguments for a real (non --emit-tool-schemas) run: {missing}")

    from a4v.llm import ChatClient
    from rtf.l11_investigation_grouping.context_artifacts import generate_cluster_plan_md
    from rtf.l11_investigation_grouping.live_runner import prepare_cluster_investigations_with_scope_boundary
    from rtf.l11_investigation_grouping.property_metadata import forward_out_of_scope_context, split_properties_by_scope
    from rtf.l11_investigation_grouping.protocol_context import generate_enriched_protocol_context_md
    from rtf.l11_investigation_grouping.run_metadata import GROUPING_POLICY_G2_CONTEXT_AWARE
    from rtf.l11_investigation_grouping.semantic_only_driver import _solc_bin_dir_for, build_ethtrust_structural_properties
    from rtf.l11_investigation_grouping.semantic_pipeline import build_full_property_pool
    from rtf.l11_investigation_grouping.semantic_property_generation import ProjectManifest
    from rtf.l5_predicates.compile_helper import compile_evmbench_target_via_foundry
    from rtf.security_agent.investigator import run_security_agent_bundle
    from rtf.standards.registry import StandardsRegistry

    repo_root = Path(args.repo_root)
    scope_files = json.loads(args.scope_files)
    entry_file = repo_root / args.entry_file_relative
    scratch_root = Path(args.scratch_root)
    scratch_root.mkdir(parents=True, exist_ok=True)

    structural_properties, _ = build_ethtrust_structural_properties(
        audit_id=args.audit_id, repo_root=repo_root, entry_sol_file=entry_file,
        solc_version=args.solc_version, scope_files=scope_files, compile_via_foundry=True,
    )
    generation_client = ChatClient(
        base_url="https://openrouter.ai/api/v1", api_key=os.environ["MODEL_EVAL_API_KEY"],
        model=args.generation_model, cache_dir=Path(args.generation_cache_dir),
        token_log_path=Path(args.generation_tokens_log),
    )
    slither = compile_evmbench_target_via_foundry(repo_root)
    manifest = ProjectManifest.from_slither(slither, repo_root=repo_root)
    protocol_context_md = generate_enriched_protocol_context_md(
        args.audit_id, repo_root, entry_file, slither, scope_files=scope_files, registry=StandardsRegistry(),
    )
    full_pool, _ = build_full_property_pool(
        structural_properties, protocol_context_md, manifest, generation_client, slither=slither, max_properties=78,
    )
    in_scope, out_of_scope = split_properties_by_scope(full_pool, scope_files)
    pool = forward_out_of_scope_context(in_scope, out_of_scope)

    clusters, properties_by_id, protocol_context_md_out, req_ctx_by_id, _ = (
        prepare_cluster_investigations_with_scope_boundary(
            pool, GROUPING_POLICY_G2_CONTEXT_AWARE, args.audit_id, slither, scope_files,
            repo_root=repo_root, protocol_context_override=protocol_context_md,
        )
    )
    target_cluster = next((c for c in clusters if args.property_id in c.property_ids), None)
    if target_cluster is None:
        raise SystemExit(
            f"target property {args.property_id!r} not found in ANY regenerated cluster -- "
            "pool/clustering drifted, stop and investigate"
        )

    req_ids_in_cluster = sorted({properties_by_id[pid].requirement_id for pid in target_cluster.property_ids} | {
        properties_by_id[pid].parent_requirement_id for pid in target_cluster.property_ids
        if properties_by_id[pid].parent_requirement_id
    })
    req_context_paths = {rid: f".rtf/context/requirements/{rid}.md" for rid in req_ids_in_cluster}
    extra_files = {".rtf/context/protocol_context.md": protocol_context_md_out}
    for rid in req_ids_in_cluster:
        content = req_ctx_by_id.get(rid)
        if content is not None:
            extra_files[req_context_paths[rid]] = content

    full_plan = generate_cluster_plan_md(
        target_cluster, properties_by_id, ".rtf/context/protocol_context.md", req_context_paths,
    )
    trimmed_plan = trim_plan_to_single_property(full_plan, args.property_id)
    plan_path = f".rtf/plans/{target_cluster.cluster_id}.md"
    extra_files[plan_path] = trimmed_plan

    dry_run_info = {
        "cluster_id": target_cluster.cluster_id,
        "cluster_property_ids": list(target_cluster.property_ids),
        "trimmed_plan_length": len(trimmed_plan),
        "full_cluster_plan_length": len(full_plan),
        "trimmed_plan_sha256": __import__("hashlib").sha256(trimmed_plan.encode()).hexdigest(),
    }
    if args.dry_run:
        Path(args.result_path).write_text(json.dumps({"dry_run": True, **dry_run_info}, indent=2), encoding="utf-8")
        return

    solc_path_dir = _solc_bin_dir_for(args.solc_version, scratch_root)

    started = time.time()
    result = run_security_agent_bundle(
        codex_bin=Path("unused"), python_bin=Path("unused"), mcp_server_script=Path("unused"),
        api_key=os.environ["MODEL_EVAL_API_KEY"], model=args.model, case_id=args.case_id,
        entry_file=entry_file, repo_root=repo_root, candidate_location="",
        solc_path_dir=solc_path_dir, solc_remaps=None, prompt="",
        scratch_root=scratch_root, timeout_s=int(args.max_wall_clock_s), extra_files=extra_files,
        compile_via_foundry=True, max_steps=args.max_steps, max_cost_usd=args.max_cost_usd,
        reasoning_effort=args.reasoning_effort,
    )
    wall_s = time.time() - started
    state = result.investigation_state
    target_req = state.requirement_states[args.property_id]
    summary = {
        "dry_run": False,
        **dry_run_info,
        "case_id": args.case_id, "model": args.model, "wall_clock_s": wall_s,
        "cost_usd": result.cost_usd,
        "decide_calls_total": result.decide_calls_total, "tool_calls_total": result.tool_calls,
        "deduplicated_calls_total": result.deduplicated_calls_total,
        "input_tokens": result.input_tokens, "cached_input_tokens": result.cached_input_tokens,
        "output_tokens": result.output_tokens,
        "files_inspected": result.files_inspected,
        "target_property_verdict": target_req.status.value,
        "target_property_reason": target_req.resolution_reason,
        "all_verdicts": {pid: rs.status.value for pid, rs in state.requirement_states.items()},
        "trajectory_path": result.trajectory_path,
        "state_path": str(scratch_root / "security_agent" / args.case_id / "state.json"),
        "case_root": str(scratch_root / "security_agent" / args.case_id),
    }
    Path(args.result_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
