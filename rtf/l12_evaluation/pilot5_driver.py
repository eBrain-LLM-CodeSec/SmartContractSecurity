"""Pilot-level driver: runs the frozen L1-L8-escalation-Codex pipeline
once per scope.txt entry file for one real EVMbench audit (multi-entry
compilation, since Foundry auto-build is unavailable on this node --
AR-009 -- so compile_evmbench_target only sees one file's import graph
per call), then merges FAIL results into one audit.md and grades it.

This script is PILOT SCAFFOLDING, not part of the frozen pipeline itself
(rtf/l12_evaluation/pipeline_e2e.py, escalation.py, codex_bridge.py,
report_generator.py are unmodified and untouched by this script -- it
only calls them, once per scope entry). The multi-entry decision and its
rationale belong in the pilot report, not silently treated as "the
architecture."

No manual candidate/requirement/file selection beyond "iterate every
scope.txt-listed file as an entry point" -- mechanical, not cherry-picked.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import traceback
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path("/scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2")
sys.path.insert(0, str(REPO_ROOT))

from rtf.l12_evaluation.pipeline_e2e import compute_terminal_status, run_pipeline_e2e, StageMetrics  # noqa: E402
from rtf.l12_evaluation.report_generator import generate_audit_md  # noqa: E402
from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState, EvidenceItem, OperationalStatus, RoutedRequirementResult, TargetRunResult  # noqa: E402
from rtf.l12_evaluation.run_grader import run_grader  # noqa: E402
from rtf.l12_evaluation.run_rtf import build_context_for_evmbench_target  # noqa: E402
from rtf.l12_evaluation.scope_discovery import discover_scope_files  # noqa: E402
from rtf.standards.routing import build_standards_routed_requirements  # noqa: E402
import asyncio  # noqa: E402

CODEX_BIN = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/codex_bin/codex")
PYTHON_BIN = REPO_ROOT / ".venv/bin/python3"
MCP_SERVER = REPO_ROOT / "rtf/l8_llm_judgment_layer/bundle_agent_experiment/graph_mcp_server.py"
API_KEY = Path("/scratch/md5344/evmbench/run/task5_secrets/openrouter.key").read_text().strip()
CODEX_MODEL = "openai/gpt-5.1-codex-max"

_SOLC_SELECT_ARTIFACTS = Path.home() / ".solc-select" / "artifacts"
_SOLC_BIN_DIR_CACHE: dict[str, str] = {}


def _solc_bin_dir_for(version: str, scratch_root: Path) -> str:
    """A directory containing exactly one `solc` binary, pinned to
    `version`, for `GRAPH_SOLC_PATH_DIR` (the graph-navigation MCP server's
    own PATH override -- see graph_mcp_server.py's docstring).

    Deliberately NOT solc-select's own `use` command: that mutates
    machine-global state (gotcha #3 in HANDOFF_NEXT_SESSION.md -- never
    safe across concurrent/differently-versioned compiles), which is
    exactly why this mechanism exists as a separate PATH-prepend instead.

    Replaces a real, confirmed bug: this used to be one hardcoded
    module-level constant (`SOLC_PATH_DIR`, pointed at a directory
    misleadingly named `solc_bin_0817` whose `solc` symlink actually
    resolves to a mislabeled 0.8.20 binary) reused for EVERY audit
    regardless of that audit's own `entry_solc_version` -- it only
    happened to be correct for `2025-01-liquid-ron` (needs 0.8.20) by
    coincidence. For any audit needing a different version (canto/
    arbitrum-foundation need 0.8.17, vultisig needs 0.7.6/0.8.24, sequence
    needs 0.8.28), the graph-navigation compile the live Codex
    investigation actually queries would have silently used the wrong
    compiler version -- a real "inconsistent compilation paths/settings"
    defect, not a hypothetical one.
    """
    if version in _SOLC_BIN_DIR_CACHE:
        return _SOLC_BIN_DIR_CACHE[version]
    artifact = _SOLC_SELECT_ARTIFACTS / f"solc-{version}" / f"solc-{version}"
    if not artifact.exists():
        raise RuntimeError(
            f"solc {version} is not installed via solc-select (expected {artifact}); "
            f"run `solc-select install {version}` before this audit can compile"
        )
    real_version = subprocess.run([str(artifact), "--version"], capture_output=True, text=True, check=True).stdout
    if f"Version: {version}" not in real_version:
        raise RuntimeError(
            f"solc-select artifact at {artifact} does not actually report version {version} "
            f"(reported: {real_version.strip()!r}) -- refusing to use a mislabeled binary"
        )
    bin_dir = scratch_root.parent / f"solc_bin_{version.replace('.', '')}"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link = bin_dir / "solc"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(artifact)
    _SOLC_BIN_DIR_CACHE[version] = str(bin_dir)
    return str(bin_dir)


def _solc_version_for(rel_path: str, default_version: str, path_prefix_overrides: dict[str, str]) -> str:
    """Mechanical, not a judgment call: each audit's default solc version
    comes from its own foundry.toml pin (satisfies every scope file's own
    pragma range, confirmed by direct inspection before this pilot run --
    see PILOT5_AUDIT_SELECTION.md/pilot run notes). `path_prefix_overrides`
    covers the one audit (vultisig) with a genuinely separate sub-project
    (its own hardhat.config.ts, own solc version) inside one repo.
    """
    norm = rel_path.lstrip("./")
    for prefix, version in path_prefix_overrides.items():
        if norm.startswith(prefix):
            return version
    return default_version


def run_one_audit(
    audit_id: str,
    repo_root: Path,
    scope_files: list[str],
    scratch_root: Path,
    artifacts_dir: Path,
    per_audit_codex_ceiling_usd: float,
    default_solc_version: str,
    path_prefix_overrides: dict[str, str] | None = None,
    l8_cache_dir: Path | None = None,
    max_concurrent_investigations: int = 1,
    extra_solc_args: list[str] | None = None,
) -> dict:
    """`extra_solc_args`, when given, applies uniformly to every entry in
    this call (e.g. `["--via-ir", "--optimize"]` for a target whose own
    foundry.toml requires it) -- flat, not per-path, since callers that
    need per-path granularity within one multi-entry audit don't exist
    yet; add a prefix-keyed override dict here (mirroring
    `path_prefix_overrides`) if that need arises."""
    path_prefix_overrides = path_prefix_overrides or {}
    from a4v.llm import ChatClient
    from rtf.l8_llm_judgment_layer.judgment_layer import LLMJudgmentLayer

    # Defaults to a directory alongside THIS run's own scratch_root, not a
    # hardcoded path into a different, arbitrary prior job's ephemeral tmp
    # (a real fragility: that job's scratch has no lifetime guarantee and
    # has nothing to do with this run's reproducibility). Callers that
    # deliberately want to reuse a prior run's L8 cache (cache hits, no
    # new spend, for judgments whose prompt/bundle content is unchanged)
    # may still pass one explicitly.
    l8_cache_dir = l8_cache_dir or (scratch_root.parent / "pilot5_l8_cache")
    chat_client = ChatClient(
        base_url="https://openrouter.ai/api/v1", api_key=API_KEY, model=CODEX_MODEL,
        cache_dir=l8_cache_dir, token_log_path=l8_cache_dir / "tokens.jsonl",
    )
    judgment_layer = LLMJudgmentLayer(chat_client=chat_client, model_version=CODEX_MODEL)

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    scratch_root.mkdir(parents=True, exist_ok=True)

    merged_routed: dict[str, RoutedRequirementResult] = {}
    per_entry_summaries = []
    total_codex_cost = 0.0
    stage_totals = StageMetrics()
    all_raw_l8 = {}
    all_codex_results = {}
    all_generated_bundles = {}
    infra_failures = []

    remaining_ceiling = per_audit_codex_ceiling_usd

    for i, rel_path in enumerate(scope_files):
        stage_path = artifacts_dir / f"entry_{i:02d}_{Path(rel_path).stem}_stage.json"
        if stage_path.exists():
            # Resume: this entry already completed in a prior (interrupted)
            # run of this same audit. Re-hydrate its recorded results
            # instead of re-executing -- re-running would both burn real
            # money again and silently double-count stage metrics.
            saved = json.loads(stage_path.read_text())
            remaining_ceiling -= saved["codex_cost"]
            total_codex_cost += saved["codex_cost"]
            for k, v in saved["stage_metrics"].items():
                if isinstance(v, dict):
                    for kk, vv in v.items():
                        stage_totals.final_decisions[kk] = stage_totals.final_decisions.get(kk, 0) + vv
                else:
                    setattr(stage_totals, k, getattr(stage_totals, k, 0) + v)
            fail_req_ids = [fdet["req_id"] for fdet in saved.get("fail_details", [])]
            resumed_bundles: dict = {}
            if any(rid.startswith("gp-accepted-standard__") for rid in fail_req_ids):
                # Resuming an entry with generated (ERC-standard-derived) FAIL
                # findings: the saved stage.json doesn't persist bundle text
                # (only req_id/evidence/reasoning), and this resume path
                # otherwise skips run_pipeline_e2e entirely (by design -- no
                # re-spending). Regenerate the bundles for FREE by re-running
                # ONLY the deterministic, already-tested standards pipeline
                # (compile + discover + generate; zero Codex/LLM calls) --
                # not a re-derivation of anything Codex decided, purely the
                # same source-driven text build_standards_routed_requirements
                # would have produced originally.
                entry_solc_version = _solc_version_for(rel_path, default_solc_version, path_prefix_overrides)
                resume_ctx, resume_compile_error = build_context_for_evmbench_target(
                    repo_root / rel_path.lstrip("./"), repo_root, entry_solc_version,
                )
                if resume_ctx.slither is not None and resume_ctx.repo_root is not None:
                    _, _, resumed_bundles = build_standards_routed_requirements(
                        repo_root=resume_ctx.repo_root,
                        entry_sol_file=repo_root / rel_path.lstrip("./"),
                        slither=resume_ctx.slither,
                    )
                else:
                    print(f"[{audit_id}] entry {rel_path}: could not recompile to regenerate bundles for "
                          f"resumed generated FAIL findings ({resume_compile_error!r}) -- their audit.md "
                          f"entries will fall back to the bare req_id string, not a crash", flush=True)

            for fdet in saved.get("fail_details", []):
                key = f"{fdet['req_id']}::{rel_path}"
                evidence = tuple(EvidenceItem(**e) for e in fdet["evidence"])
                merged_routed[key] = RoutedRequirementResult(
                    req_id=fdet["req_id"], applicability_state=ApplicabilityState.APPLICABLE,
                    operational_status=OperationalStatus.OK, conformance_state=ConformanceState.FAIL,
                    evidence=evidence,
                )
                if fdet["req_id"] in resumed_bundles:
                    all_generated_bundles[key] = resumed_bundles[fdet["req_id"]]
                if fdet["escalated"]:
                    all_codex_results[key] = SimpleNamespace(
                        graph_tool_calls=fdet["graph_tool_calls"], wall_clock_s=fdet["wall_clock_s"],
                        final_decision={"reasoning_summary": fdet["reasoning_summary"], "confidence": fdet["confidence"]},
                    )
                else:
                    all_raw_l8[key] = {"first_pass": {"reasoning_summary": fdet["reasoning_summary"],
                                                        "confidence": fdet["confidence"]}}
            per_entry_summaries.append(saved)
            print(f"[{audit_id}] entry {i+1}/{len(scope_files)}: {rel_path} -- RESUMED from prior run "
                  f"(codex_cost=${saved['codex_cost']:.4f}, fails={saved['fail_count']})", flush=True)
            continue

        entry_file = repo_root / rel_path.lstrip("./")
        if not entry_file.exists():
            infra_failures.append({"entry": rel_path, "error": "file_not_found"})
            continue

        print(f"[{audit_id}] entry {i+1}/{len(scope_files)}: {rel_path} "
              f"(remaining codex ceiling ${remaining_ceiling:.2f})", flush=True)

        if remaining_ceiling <= 0:
            infra_failures.append({"entry": rel_path, "error": "SKIPPED_AUDIT_COST_CEILING"})
            continue

        entry_solc_version = _solc_version_for(rel_path, default_solc_version, path_prefix_overrides)
        entry_solc_path_dir = _solc_bin_dir_for(entry_solc_version, scratch_root)
        t0 = time.time()
        try:
            artifacts = run_pipeline_e2e(
                audit_id=audit_id, entry_sol_file=entry_file, project_root=repo_root,
                solc_version=entry_solc_version, judgment_layer=judgment_layer,
                codex_bin=CODEX_BIN, python_bin=PYTHON_BIN, mcp_server_script=MCP_SERVER,
                api_key=API_KEY, codex_model=CODEX_MODEL, solc_path_dir=entry_solc_path_dir,
                scratch_root=scratch_root, escalation_enabled=True, codex_timeout_s=900,
                cost_ceiling_usd=remaining_ceiling,
                max_concurrent_investigations=max_concurrent_investigations,
                extra_solc_args=extra_solc_args,
            )
        except Exception as e:  # noqa: BLE001 -- one entry's crash must not kill the whole audit
            infra_failures.append({"entry": rel_path, "error": f"{type(e).__name__}: {e}",
                                    "traceback": traceback.format_exc()[-3000:]})
            print(f"[{audit_id}] entry {rel_path} FAILED: {type(e).__name__}: {e}", flush=True)
            continue

        dt = time.time() - t0
        remaining_ceiling -= artifacts.total_codex_cost_usd
        total_codex_cost += artifacts.total_codex_cost_usd

        fail_details = []
        for req_id, r in artifacts.run.routed.items():
            if r.conformance_state != ConformanceState.FAIL:
                continue
            key = f"{req_id}::{rel_path}"
            merged_routed[key] = r
            if req_id in artifacts.generated_bundles:
                all_generated_bundles[key] = artifacts.generated_bundles[req_id]
            escalated = req_id in artifacts.codex_results
            if escalated:
                cr = artifacts.codex_results[req_id]
                all_codex_results[key] = cr
                fd = cr.final_decision or {}
                fail_details.append({
                    "req_id": req_id, "escalated": True,
                    "evidence": [asdict(e) for e in r.evidence],
                    "reasoning_summary": fd.get("reasoning_summary"), "confidence": fd.get("confidence"),
                    "graph_tool_calls": cr.graph_tool_calls, "wall_clock_s": cr.wall_clock_s,
                })
            else:
                raw = artifacts.raw_l8_judgments.get(req_id, {})
                all_raw_l8[key] = raw
                first_pass = raw.get("first_pass", raw) if raw else {}
                fail_details.append({
                    "req_id": req_id, "escalated": False,
                    "evidence": [asdict(e) for e in r.evidence],
                    "reasoning_summary": first_pass.get("reasoning_summary"), "confidence": first_pass.get("confidence"),
                })

        for k, v in asdict(artifacts.stage_metrics).items():
            if isinstance(v, dict):
                for kk, vv in v.items():
                    stage_totals.final_decisions[kk] = stage_totals.final_decisions.get(kk, 0) + vv
            else:
                setattr(stage_totals, k, getattr(stage_totals, k, 0) + v)

        if not artifacts.integrity_report.valid:
            print(f"[{audit_id}] entry {rel_path}: INTEGRITY CHECK FAILED -- "
                  f"{artifacts.integrity_report.invalid_reason}", flush=True)

        per_entry_summaries.append({
            "entry": rel_path, "wall_s": dt, "codex_cost": artifacts.total_codex_cost_usd,
            "stage_metrics": asdict(artifacts.stage_metrics),
            "fail_count": len(fail_details),
            "fail_details": fail_details,
            "escalation_skip_reasons": artifacts.escalation_skip_reasons,
            "codex_outcome_reasons": artifacts.codex_outcome_reasons,
            "conformance_by_req": {k: (v.conformance_state.value if v.conformance_state else None)
                                    for k, v in artifacts.run.routed.items()},
            "terminal_status_by_req": {k: compute_terminal_status(v) for k, v in artifacts.run.routed.items()},
            "integrity_report": artifacts.integrity_report.to_dict(),
        })
        (artifacts_dir / f"entry_{i:02d}_{Path(rel_path).stem}_stage.json").write_text(
            json.dumps(per_entry_summaries[-1], indent=2, default=str))

    class _FakeArtifacts:
        pass
    fake = _FakeArtifacts()
    fake.run = TargetRunResult(audit_id=audit_id, routed=merged_routed)
    fake.codex_results = all_codex_results
    fake.raw_l8_judgments = all_raw_l8
    fake.generated_bundles = all_generated_bundles

    audit_md = generate_audit_md(fake, audit_title=audit_id)
    audit_md_path = artifacts_dir / "audit.md"
    audit_md_path.write_text(audit_md)

    grade_result = None
    grade_error = None
    try:
        grade_result = asyncio.run(run_grader(audit_id, audit_md_path))
    except Exception as e:  # noqa: BLE001
        grade_error = f"{type(e).__name__}: {e}"

    # Aggregate integrity validity across every entry -- the supervised-
    # validation invariant's own instruction: "fail the validation run"
    # (mark it INVALID, not a normal benchmark result) if ANY entry's
    # `silently_missing` was nonzero. Entries resumed from a stage.json
    # written before this integrity-report field existed report `None`
    # (unknown, not proven valid) rather than being silently assumed
    # valid -- disclosed explicitly, matching this project's existing
    # "known data gap" discipline for old-format resumed entries.
    entry_integrity = []
    for s in per_entry_summaries:
        ir = s.get("integrity_report")
        entry_integrity.append({"entry": s["entry"], "valid": ir.get("valid") if ir else None,
                                 "invalid_reason": ir.get("invalid_reason") if ir else "pre-integrity-report format (resumed old entry)"})
    overall_integrity_valid = all(e["valid"] is True for e in entry_integrity) if entry_integrity else True
    unknown_integrity_entries = [e["entry"] for e in entry_integrity if e["valid"] is None]

    summary = {
        "audit_id": audit_id, "scope_entries": len(scope_files),
        "total_codex_cost_usd": total_codex_cost,
        "stage_totals": asdict(stage_totals),
        "infra_failures": infra_failures,
        "per_entry_summaries": per_entry_summaries,
        "fail_findings_count": len(merged_routed),
        "grade_result": grade_result, "grade_error": grade_error,
        "integrity_valid": overall_integrity_valid,
        "integrity_by_entry": entry_integrity,
        "integrity_unknown_entries": unknown_integrity_entries,
    }
    (artifacts_dir / "pilot_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    integrity_flag = "VALID" if overall_integrity_valid else "**INTEGRITY CHECK FAILED -- INVALID**"
    print(f"[{audit_id}] DONE. codex_cost=${total_codex_cost:.4f} fails={len(merged_routed)} "
          f"infra_failures={len(infra_failures)} grade={grade_result and grade_result.get('score')} "
          f"integrity={integrity_flag}", flush=True)
    if unknown_integrity_entries:
        print(f"[{audit_id}] WARNING: {len(unknown_integrity_entries)} resumed entries predate the "
              f"integrity-report field and were not re-validated: {unknown_integrity_entries}", flush=True)
    return summary


if __name__ == "__main__":
    audit_id = sys.argv[1]
    repo_root = Path(sys.argv[2])
    scope_file_arg = sys.argv[3]
    artifacts_dir = Path(sys.argv[4])
    ceiling = float(sys.argv[5]) if len(sys.argv) > 5 else 3.0
    default_solc_version = sys.argv[6] if len(sys.argv) > 6 else "0.8.20"
    overrides_json = sys.argv[7] if len(sys.argv) > 7 else "{}"
    max_concurrent_investigations = int(sys.argv[8]) if len(sys.argv) > 8 else 1
    path_prefix_overrides = json.loads(overrides_json)

    if scope_file_arg == "auto":
        # Repo-structure-derived scope discovery (rtf.l12_evaluation.
        # scope_discovery): prefers the audit's own scope.txt when
        # present, else a heuristic repo scan -- see that module's
        # docstring for why this exists (a real, found-by-inspection gap:
        # a manually-curated scope_files list can silently under-cover a
        # repo's own documented in-scope files, e.g. 2024-08-phi's
        # PhiFactory.sol never got its own entry in an earlier run here).
        scope_files = discover_scope_files(repo_root)
        print(f"[{audit_id}] scope 'auto' -> {len(scope_files)} file(s) discovered: {scope_files}", flush=True)
    else:
        scope_files = [l.strip() for l in Path(scope_file_arg).read_text().splitlines() if l.strip()]
    # Scoped to THIS run's own job tmp (falls back to the historical
    # job-318205ae location only if invoked outside a job context) --
    # a hardcoded fixed job's tmp dir here has no lifetime guarantee and
    # is not this run's own scratch space to write into.
    _job_dir = os.environ.get("CLAUDE_JOB_DIR", "/scratch/md5344/.claude/jobs/318205ae")
    scratch_root = Path(f"{_job_dir}/tmp/pilot5_scratch/{audit_id}")

    run_one_audit(audit_id, repo_root, scope_files, scratch_root, artifacts_dir, ceiling,
                  default_solc_version, path_prefix_overrides,
                  max_concurrent_investigations=max_concurrent_investigations)
