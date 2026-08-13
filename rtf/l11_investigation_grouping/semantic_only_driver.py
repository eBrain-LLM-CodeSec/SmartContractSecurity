"""RTF v2: a real driver that runs the semantic-property pipeline
end-to-end -- generation (Phase 5) -> grounding (Phase 6/7) -> clustering
(existing G0-G3 engine) -> REAL Codex cluster investigation
(`live_runner.run_cluster_investigations_live`) -- for a repo that has no
EthTrust/ERC-requirement routing of its own (a synthetic fixture, or any
target being checked for semantic coverage in isolation from the
structural pipeline). `structural_properties`, when given, is merged in
exactly like `semantic_pipeline.build_full_property_pool` already does --
this driver is not semantic-only by architecture, only by default.

Deliberately does NOT import `rtf.l12_evaluation.pilot5_driver`: that
module hardcodes `REPO_ROOT` to a SPECIFIC worktree checkout and
`sys.path.insert(0, str(REPO_ROOT))`s it at import time -- importing it
from a different worktree would shadow this branch's own `rtf.*` modules
with that other checkout's copies for the rest of the process. The small
amount of solc-bin-dir logic this driver needs is duplicated locally
instead (see `_solc_bin_dir_for`), not shared via that import.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from rtf.l11_investigation_grouping.live_runner import prepare_cluster_investigations, run_cluster_investigations_live
from rtf.l11_investigation_grouping.property_metadata import (
    PropertyMetadata, forward_out_of_scope_context, split_properties_by_scope,
)
from rtf.l11_investigation_grouping.protocol_context import generate_enriched_protocol_context_md
from rtf.l11_investigation_grouping.run_metadata import GROUPING_POLICY_G2_CONTEXT_AWARE
from rtf.l11_investigation_grouping.semantic_pipeline import build_full_property_pool, write_observability_artifacts
from rtf.l11_investigation_grouping.semantic_property_generation import ProjectManifest
from rtf.l5_predicates.compile_helper import compile_evmbench_target
from rtf.standards.registry import StandardsRegistry

_SOLC_SELECT_ARTIFACTS = Path.home() / ".solc-select" / "artifacts"


def _solc_bin_dir_for(version: str, scratch_root: Path) -> str:
    """Same real-artifact-verification discipline as
    `pilot5_driver._solc_bin_dir_for` (never trust a version label without
    checking `solc --version` actually reports it) -- duplicated locally,
    see module docstring for why. A directory containing exactly one
    `solc` binary symlinked to the verified `solc-select` artifact, for
    the graph-navigation MCP server's own `PATH` override."""
    artifact = _SOLC_SELECT_ARTIFACTS / f"solc-{version}" / f"solc-{version}"
    if not artifact.exists():
        raise RuntimeError(f"solc {version} is not installed via solc-select (expected {artifact})")
    real_version = subprocess.run([str(artifact), "--version"], capture_output=True, text=True, check=True).stdout
    if f"Version: {version}" not in real_version:
        raise RuntimeError(f"solc-select artifact at {artifact} does not report version {version}: {real_version.strip()!r}")
    bin_dir = scratch_root / f"solc_bin_{version.replace('.', '')}"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link = bin_dir / "solc"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(artifact)
    return str(bin_dir)


def run_semantic_investigation(
    *, audit_id: str, repo_root: Path, entry_sol_file: Path, solc_version: str,
    chat_client, codex_bin: Path, python_bin: Path, mcp_server_script: Path,
    api_key: str, codex_model: str, scratch_root: Path,
    structural_properties: list[PropertyMetadata] | None = None,
    grouping_policy: str = GROUPING_POLICY_G2_CONTEXT_AWARE,
    max_semantic_properties: int = 12, codex_timeout_s: int = 900,
    cost_ceiling_usd: float | None = None, max_concurrent_investigations: int = 1,
    observability_root: Path | None = None, run_arm_g_bundle_fn=None,
    scope_files: list[str] | None = None, extra_solc_args: list[str] | None = None,
) -> dict:
    """Compiles `entry_sol_file`, builds the enriched protocol context +
    manifest, runs Phase 5/6/7 (real LLM call via `chat_client`), clusters
    the resulting pool, and runs REAL Codex cluster investigation(s)
    (`live_runner.run_cluster_investigations_live` -- real spend, real
    subprocess calls, per that module's own documented behavior).

    `scope_files`, when given (e.g. the audit's real `scope.txt` list),
    is the audit's declared in-scope file set -- the generated property
    pool is filtered to it via `property_metadata.split_properties_by_
    scope`/`forward_out_of_scope_context` BEFORE clustering, the exact
    same mechanism (and the exact same functions) `ablation_driver.
    run_config_entry` already established for the structural pipeline --
    not a new, parallel scoping rule. Properties targeting a file outside
    `scope_files` (e.g. a vendored dependency, or a project file the
    entry's own import graph reaches but the audit didn't declare in
    scope) are dropped from investigation, but their `requirement_
    explanatory_text` is still forwarded to any KEPT property they're
    callgraph-adjacent to (same behavior as the structural pipeline).
    Defaults to `None`, which reproduces the prior behavior exactly:
    scope is just `entry_sol_file`'s own relative path, a no-op filter
    since every generated property already targets something in that
    one compiled file's own contracts.

    `extra_solc_args`, when given, is forwarded verbatim to
    `compile_evmbench_target` (e.g. `["--via-ir", "--optimize",
    "--optimize-runs", "1000"]` for a target whose own `foundry.toml`
    needs `via-ir` to avoid a real "stack too deep" solc error --
    confirmed live on `2024-01-canto`'s `LendingLedger.sol`).

    Returns a dict: `properties_by_id`, `clusters`, `property_verdicts`
    (`{property_id: PropertyVerdict}`), `raw_property_entries_by_id`
    (the investigator's own JSON entry per property, for human-readable
    reporting), `total_cost_usd`, `semantic_observability` (Phase 5/6's
    own raw/rejected records), `in_scope_count`/`out_of_scope_count`.
    If `observability_root` is given, also writes the Section-19 JSON
    artifacts there via `semantic_pipeline.write_observability_artifacts`.
    """
    scratch_root.mkdir(parents=True, exist_ok=True)
    slither = compile_evmbench_target(entry_sol_file, repo_root, solc_version=solc_version, extra_solc_args=extra_solc_args)
    manifest = ProjectManifest.from_slither(slither)
    effective_scope_files = scope_files if scope_files is not None else (
        [str(entry_sol_file.relative_to(repo_root))] if entry_sol_file.is_relative_to(repo_root) else []
    )

    protocol_context_md = generate_enriched_protocol_context_md(
        audit_id, repo_root, entry_sol_file, slither, scope_files=effective_scope_files, registry=StandardsRegistry(),
    )

    full_pool, semantic_observability = build_full_property_pool(
        structural_properties or [], protocol_context_md, manifest, chat_client, slither=slither,
        max_properties=max_semantic_properties,
    )

    in_scope, out_of_scope = split_properties_by_scope(full_pool, effective_scope_files)
    pool = forward_out_of_scope_context(in_scope, out_of_scope)

    clusters, properties_by_id, protocol_context_md_out, req_ctx_by_id = prepare_cluster_investigations(
        pool, grouping_policy, audit_id, slither, effective_scope_files,
    )

    solc_path_dir = _solc_bin_dir_for(solc_version, scratch_root)

    property_verdicts, arm_g_results, total_cost, raw_entries = run_cluster_investigations_live(
        clusters, properties_by_id, protocol_context_md_out, req_ctx_by_id,
        audit_id=audit_id, entry_sol_file=entry_sol_file, project_root=repo_root,
        codex_bin=codex_bin, python_bin=python_bin, mcp_server_script=mcp_server_script,
        api_key=api_key, codex_model=codex_model, solc_path_dir=solc_path_dir, solc_remaps=None,
        scratch_root=scratch_root, codex_timeout_s=codex_timeout_s, cost_ceiling_usd=cost_ceiling_usd,
        max_concurrent_investigations=max_concurrent_investigations, run_arm_g_bundle_fn=run_arm_g_bundle_fn,
    )

    if observability_root is not None:
        write_observability_artifacts(
            observability_root, audit_id,
            structural_properties=[p for p in in_scope if p.source_kind != "code_semantics"],
            semantic_pipeline_observability=semantic_observability,
            semantic_properties_grounded=[p for p in pool if p.source_kind == "code_semantics"],
            property_clusters=[c.as_dict() for c in clusters],
        )

    return {
        "properties_by_id": properties_by_id,
        "clusters": clusters,
        "property_verdicts": property_verdicts,
        "arm_g_results": arm_g_results,
        "raw_property_entries_by_id": raw_entries,
        "total_cost_usd": total_cost,
        "semantic_observability": semantic_observability,
        "in_scope_count": len(in_scope),
        "out_of_scope_count": len(out_of_scope),
        "out_of_scope_properties": out_of_scope,
    }
