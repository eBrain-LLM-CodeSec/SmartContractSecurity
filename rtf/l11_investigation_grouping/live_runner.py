"""Live wiring for the grouped-investigation architecture: connects
property derivation (Phase 2/3) -> grouping (Phase 4/5) -> context
generation (Phase 7) -> the cluster prompt (Phase 8) -> real Codex
investigation calls (`arm_g_codex.run_arm_g_bundle`) -> response
validation/resolution (Phase 9) -> automatic splitting on failure
(Phase 10) -> per-requirement aggregation (reusing Phase 2/3's
FAIL-wins `aggregate_instance_verdicts`).

This is the ONLY module in `rtf.l11_investigation_grouping` that can
spend real money -- every other module in this package is pure/
deterministic. `run_arm_g_bundle` is always passed in as
`run_arm_g_bundle_fn` (defaulting to the real one), specifically so
every code path here is exercised by mocked tests with zero real calls
before any live run -- see `test_live_runner.py`.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

from rtf.l10_property_derivation.derive_investigations import aggregate_instance_verdicts, expand_investigation_instances
from rtf.l11_investigation_grouping.cluster_prompt import build_cluster_investigation_prompt
from rtf.l11_investigation_grouping.cluster_response_validation import (
    PropertyVerdict, resolve_property_verdicts, validate_cluster_response,
)
from rtf.l11_investigation_grouping.cluster_splitting import detect_split_reason, split_cluster
from rtf.l11_investigation_grouping.complexity import ClusterBudget
from rtf.l11_investigation_grouping.context_artifacts import (
    generate_cluster_plan_md, generate_protocol_context_md, generate_requirement_context_md,
)
from rtf.l11_investigation_grouping.grouping_engine import Cluster
from rtf.l11_investigation_grouping.policies import apply_grouping_policy
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata, derive_property_metadata
from rtf.l11_investigation_grouping.taxonomy import categorize_generated_clause, categorize_requirement
from rtf.l12_evaluation.codex_bridge import build_codex_prompt_inputs, corpus_by_req_id
from rtf.l12_evaluation.evidence_ranking import rank_evidence
from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState, RoutedRequirementResult


def build_property_pool(
    routed: dict[str, RoutedRequirementResult],
    project_root: Path,
    generated_bundles: dict[str, dict] | None = None,
    pg=None,
    slither=None,
    max_locations: int = 5,
    max_total_instances: int = 6,
) -> list[PropertyMetadata]:
    """Derives the full atomic-property pool for every applicable,
    evidence-backed, not-yet-resolved requirement in `routed` -- exactly
    the same eligibility filter `pipeline_e2e.py`'s escalation loop
    already uses (applicable, `conformance_state is None`, has evidence,
    operational_status OK), so this pool always matches what would have
    been escalated under the pre-grouping architecture, property for
    property, just decomposed into `PropertyMetadata` instead of
    collapsed to one candidate_location per requirement.
    """
    generated_bundles = generated_bundles or {}
    properties: list[PropertyMetadata] = []
    corpus = corpus_by_req_id()

    for req_id, result in routed.items():
        if result.applicability_state != ApplicabilityState.APPLICABLE:
            continue
        if result.conformance_state is not None:
            continue
        if not result.evidence or result.operational_status.value != "OK":
            continue

        ranked = rank_evidence(list(result.evidence), project_root)
        locations = [r.item.location for r in ranked]
        top_location = locations[0] if locations else ""

        prompt_inputs = build_codex_prompt_inputs(
            req_id, top_location, result, project_root, None, bundle_record=generated_bundles.get(req_id),
        )
        instances = expand_investigation_instances(
            req_id, prompt_inputs.requirement_text, locations,
            max_locations=max_locations, max_total_instances=max_total_instances,
        )

        req_record = corpus.get(req_id)
        if req_record is None:
            bundle_self = (generated_bundles.get(req_id) or {}).get("bundle", {}).get("self", req_id)
            req_record = {
                "req_id": req_id, "level": "GP", "title": bundle_self[:80],
                "normative_text": prompt_inputs.requirement_text, "section": {},
            }

        evidence_by_location: dict[str, object] = {}
        for item in result.evidence:
            evidence_by_location.setdefault(item.location, item)

        category = categorize_requirement(req_id)
        if category is None:
            category = categorize_generated_clause(req_record.get("normative_text", ""))

        for instance in instances:
            evidence = evidence_by_location.get(instance.candidate_location)
            prop = derive_property_metadata(
                instance, req_record, parent_candidate_locations=locations,
                evidence=evidence, pg=pg, slither=slither,
            )
            if category is not None:
                prop = replace(prop, reasoning_category=category)
            properties.append(prop)

    return properties


def prepare_cluster_investigations(
    properties: list[PropertyMetadata],
    policy_name: str,
    audit_id: str,
    slither,
    scope_files: list[str],
) -> tuple[list[Cluster], dict[str, PropertyMetadata], str, dict[str, str]]:
    """Groups `properties` under `policy_name` and generates the reusable
    Markdown context (protocol context once, requirement context once
    per distinct requirement_id represented). Returns
    (clusters, properties_by_id, protocol_context_md,
    requirement_context_md_by_req_id) -- everything
    `run_cluster_investigations_live` needs, all pure/deterministic
    (no I/O, no Codex calls) up to this point.
    """
    properties_by_id = {p.property_id: p for p in properties}
    clusters = apply_grouping_policy(properties, policy_name)
    protocol_context_md = generate_protocol_context_md(audit_id, slither, scope_files)

    corpus = corpus_by_req_id()
    requirement_context_by_req_id: dict[str, str] = {}
    for req_id in sorted({p.requirement_id for p in properties}):
        record = corpus.get(req_id)
        if record is None:
            rep = next(p for p in properties if p.requirement_id == req_id)
            record = {
                "req_id": req_id, "level": rep.requirement_level or "GP",
                "title": rep.requirement_semantic_intent or req_id,
                "normative_text": rep.property_text, "section": {},
            }
        requirement_context_by_req_id[req_id] = generate_requirement_context_md(
            record, explanatory_text=record.get("explanatory_text") or None
        )

    return clusters, properties_by_id, protocol_context_md, requirement_context_by_req_id


def _candidate_location_hint(cluster: Cluster, properties_by_id: dict[str, PropertyMetadata]) -> str:
    """Best-effort HINT for the graph MCP server (never a precondition --
    same convention every other candidate_location use in this codebase
    already follows). Uses the first member's own target as a starting
    point; a cluster spanning multiple locations still benefits from
    seeding the graph tools at one real location rather than none.
    """
    first = properties_by_id[cluster.property_ids[0]]
    if first.target_contract and first.target_function:
        return f"{first.target_contract}.{first.target_function}"
    return first.target_contract or ""


def run_cluster_investigations_live(
    clusters: list[Cluster],
    properties_by_id: dict[str, PropertyMetadata],
    protocol_context_md: str,
    requirement_context_by_req_id: dict[str, str],
    *,
    audit_id: str,
    entry_sol_file: Path,
    project_root: Path,
    codex_bin: Path,
    python_bin: Path,
    mcp_server_script: Path,
    api_key: str,
    codex_model: str,
    solc_path_dir: str,
    solc_remaps: list[str] | None,
    scratch_root: Path,
    codex_timeout_s: int = 900,
    cost_ceiling_usd: float | None = None,
    max_split_depth: int = 2,
    budget: ClusterBudget | None = None,
    run_arm_g_bundle_fn=None,
    max_concurrent_investigations: int = 1,
    run_variant: str | None = None,
) -> tuple[dict[str, PropertyVerdict], dict[str, object], float, dict[str, dict]]:
    """The live (or, under test, mocked) execution loop. Returns
    (property_verdicts, arm_g_results_by_case_id, total_cost_usd,
    raw_property_entries_by_id) -- the last is the raw per-property JSON
    entry each property_id's LATEST (post-split, if any) response
    contained, for callers building a human-readable report that wants
    the actual evidence/reasoning text, not just the resolved
    ConformanceState.

    `run_arm_g_bundle_fn` defaults to the real
    `arm_g_codex.run_arm_g_bundle` -- resolved lazily inside this
    function (not at import time) so tests can inject a mock without
    needing a real Codex binary/API key anywhere in the process.

    Automatic splitting (Phase 10): after each cluster investigation,
    `detect_split_reason` checks the response; if it signals a problem
    and `depth < max_split_depth` and the cluster has >=2 properties,
    the cluster is split in half and EACH half is enqueued for its own
    (later) investigation. A property is only ever finalized once its
    cluster investigation succeeds or the split depth is exhausted -- at
    exhaustion, any property still missing a verdict resolves to
    INCONCLUSIVE with an explicit reason, never silently dropped.

    `max_concurrent_investigations` (default 1 -- exactly serial,
    byte-behavior-identical to before this parameter existed, so every
    existing test/caller that omits it is unaffected): clusters are
    processed in batches of this size via a `ThreadPoolExecutor`, same
    pattern `pipeline_e2e._run_escalations_concurrent` already
    established -- each Codex call is I/O-bound (subprocess + network
    wait), safe to parallelize because each already writes to its own
    isolated scratch path keyed by `case_id`. All bookkeeping (`all_
    verdicts`/`all_results`/`total_cost`/the pending-work queue) happens
    in the MAIN thread only, as each future resolves via `as_completed`
    -- worker threads only call `run_arm_g_bundle_fn` and return its
    result. A split cluster's two halves are appended to the SAME
    pending queue (processed in a later batch), not recursed into
    immediately -- so splitting works correctly under concurrency too,
    not just the serial default.
    """
    if run_arm_g_bundle_fn is None:
        from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import run_arm_g_bundle
        run_arm_g_bundle_fn = run_arm_g_bundle

    all_verdicts: dict[str, PropertyVerdict] = {}
    all_results: dict[str, object] = {}
    all_raw_entries: dict[str, dict] = {}
    total_cost = 0.0
    entry_slug = entry_sol_file.stem
    max_workers = max(1, max_concurrent_investigations)

    def _prepare(cluster: Cluster) -> dict:
        req_ids_in_cluster = sorted({properties_by_id[pid].requirement_id for pid in cluster.property_ids})
        req_context_paths = {rid: f".rtf/context/requirements/{rid}.md" for rid in req_ids_in_cluster}
        plan_path = f".rtf/plans/{cluster.cluster_id}.md"

        extra_files = {".rtf/context/protocol_context.md": protocol_context_md}
        for rid in req_ids_in_cluster:
            extra_files[req_context_paths[rid]] = requirement_context_by_req_id[rid]
        extra_files[plan_path] = generate_cluster_plan_md(
            cluster, properties_by_id, ".rtf/context/protocol_context.md", req_context_paths,
        )
        prompt = build_cluster_investigation_prompt(
            ".rtf/context/protocol_context.md",
            [req_context_paths[rid] for rid in req_ids_in_cluster], plan_path,
        )
        return {
            "cluster": cluster,
            "case_id": "__".join(filter(None, (audit_id, entry_slug, run_variant, cluster.cluster_id))),
            "prompt": prompt, "extra_files": extra_files,
            "candidate_location": _candidate_location_hint(cluster, properties_by_id),
        }

    def _invoke(item: dict):
        return run_arm_g_bundle_fn(
            codex_bin=codex_bin, python_bin=python_bin, mcp_server_script=mcp_server_script,
            api_key=api_key, model=codex_model, case_id=item["case_id"],
            entry_file=entry_sol_file, repo_root=project_root,
            candidate_location=item["candidate_location"],
            solc_path_dir=solc_path_dir, solc_remaps=solc_remaps, prompt=item["prompt"],
            scratch_root=scratch_root, timeout_s=codex_timeout_s, extra_files=item["extra_files"],
        )

    def _process_result(cluster: Cluster, depth: int, case_id: str, result) -> None:
        nonlocal total_cost
        all_results[case_id] = result
        total_cost += getattr(result, "cost_usd", 0.0)

        response = getattr(result, "final_decision", None)
        validation = validate_cluster_response(list(cluster.property_ids), response)
        resolved = resolve_property_verdicts(response) if isinstance(response, dict) else {}
        if isinstance(response, dict):
            for entry in response.get("properties", []):
                if isinstance(entry, dict) and entry.get("property_id"):
                    all_raw_entries[entry["property_id"]] = entry

        split_reason = detect_split_reason(
            cluster, properties_by_id, budget=budget, validation_result=validation, resolved_verdicts=resolved,
        )
        if split_reason.should_split and depth < max_split_depth and len(cluster.property_ids) >= 2:
            half_a, half_b = split_cluster(cluster, properties_by_id)
            pending.append((half_a, depth + 1))
            pending.append((half_b, depth + 1))
            return

        for pid in cluster.property_ids:
            all_verdicts[pid] = resolved.get(
                pid, PropertyVerdict(ConformanceState.INCONCLUSIVE, "cluster_investigation_incomplete_or_failed"),
            )

    pending: list[tuple[Cluster, int]] = [(cluster, 0) for cluster in clusters]

    while pending:
        if cost_ceiling_usd is not None and total_cost >= cost_ceiling_usd:
            for cluster, _depth in pending:
                for pid in cluster.property_ids:
                    all_verdicts[pid] = PropertyVerdict(ConformanceState.INCONCLUSIVE, "cost_ceiling_reached")
            break

        batch = pending[:max_workers]
        pending = pending[max_workers:]
        items = [(_prepare(cluster), depth) for cluster, depth in batch]

        with ThreadPoolExecutor(max_workers=len(items)) as executor:
            future_to_item = {executor.submit(_invoke, item): (item, depth) for item, depth in items}
            for future in as_completed(future_to_item):
                item, depth = future_to_item[future]
                cluster = item["cluster"]
                try:
                    result = future.result()
                except Exception as e:  # noqa: BLE001 -- one cluster crashing must not kill the batch/run
                    for pid in cluster.property_ids:
                        all_verdicts[pid] = PropertyVerdict(ConformanceState.INCONCLUSIVE, f"cluster_invocation_crashed:{type(e).__name__}")
                    continue
                _process_result(cluster, depth, item["case_id"], result)

    return all_verdicts, all_results, total_cost, all_raw_entries


def aggregate_properties_to_requirements(
    property_verdicts: dict[str, PropertyVerdict], properties_by_id: dict[str, PropertyMetadata],
) -> dict[str, ConformanceState]:
    """FAIL-wins aggregation of every property's verdict back to its
    parent requirement -- reuses `aggregate_instance_verdicts` verbatim
    (the exact same precedence Phase 2/3 already established for
    combining multiple instances of one requirement).
    """
    by_req: dict[str, list[ConformanceState]] = {}
    for pid, verdict in property_verdicts.items():
        req_id = properties_by_id[pid].requirement_id
        by_req.setdefault(req_id, []).append(verdict.conformance_state)
    return {req_id: aggregate_instance_verdicts(states) for req_id, states in by_req.items()}
