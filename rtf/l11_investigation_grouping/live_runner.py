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

import json
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
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata, derive_property_metadata, enforce_scope_boundary
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
    scope_files: list[str] | None = None,
) -> list[PropertyMetadata]:
    """Derives the full atomic-property pool for every applicable,
    evidence-backed, not-yet-resolved requirement in `routed` -- exactly
    the same eligibility filter `pipeline_e2e.py`'s escalation loop
    already uses (applicable, `conformance_state is None`, has evidence,
    operational_status OK), so this pool always matches what would have
    been escalated under the pre-grouping architecture, property for
    property, just decomposed into `PropertyMetadata` instead of
    collapsed to one candidate_location per requirement.

    `scope_files`, when given, is forwarded to `rank_evidence` so an
    in-scope location doesn't lose the top-`max_locations` cut to a
    same-scored, alphabetically-earlier, out-of-scope sibling contract
    (see `evidence_ranking.is_in_declared_scope`'s docstring for the
    real case this closes). Optional and purely additive -- omitting it
    reproduces prior ranking exactly.
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

        ranked = rank_evidence(list(result.evidence), project_root, scope_files=scope_files)
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
    repo_root: Path | None = None,
    protocol_context_override: str | None = None,
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
    protocol_context_md = protocol_context_override
    if protocol_context_md is None:
        protocol_context_md = generate_protocol_context_md(
            audit_id, slither, scope_files, repo_root=repo_root,
        )

    corpus = corpus_by_req_id()
    # RTF_V3_REDESIGN_PLAN.md Phase 4: also render context for every
    # PARENT requirement a semantic property links to (`parent_requirement_
    # id`), not just each property's own `requirement_id` -- a semantic
    # property's own req_id is a synthetic hash with no real corpus entry
    # (see `property_grounding.py`'s fallback record below), so without
    # this its "requirement context" would be nothing but a restatement of
    # its own derived statement. The parent_requirement_id, when set, IS a
    # real static-corpus req_id, so `corpus.get(...)` resolves it to the
    # genuine official EthTrust text via the same, already-fixed
    # `generate_requirement_context_md` renderer -- no special-casing.
    all_req_ids = {p.requirement_id for p in properties} | {
        p.parent_requirement_id for p in properties if p.parent_requirement_id
    }
    requirement_context_by_req_id: dict[str, str] = {}
    for req_id in sorted(all_req_ids):
        record = corpus.get(req_id)
        if record is None:
            rep = next((p for p in properties if p.requirement_id == req_id), None)
            if rep is None:
                # A `parent_requirement_id` not resolvable in EITHER the
                # corpus or the property pool (corpus/taxonomy drift) --
                # skip rather than crash; this req_id was only a
                # supplementary parent link, not something anything else
                # depends on existing.
                continue
            record = {
                "req_id": req_id, "level": rep.requirement_level or "GP",
                "title": rep.requirement_semantic_intent or req_id,
                "normative_text": rep.property_text, "section": {},
            }
        requirement_context_by_req_id[req_id] = generate_requirement_context_md(
            record, explanatory_text=record.get("explanatory_text") or None
        )

    return clusters, properties_by_id, protocol_context_md, requirement_context_by_req_id


def prepare_cluster_investigations_with_scope_boundary(
    properties: list[PropertyMetadata],
    policy_name: str,
    audit_id: str,
    slither,
    scope_files: list[str],
    repo_root: Path | None = None,
    protocol_context_override: str | None = None,
) -> tuple[list[Cluster], dict[str, PropertyMetadata], str, dict[str, str], list[dict]]:
    """Boundary A (RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md SS9,
    Invariant F): defense-in-depth re-check of `properties` against
    `scope_files` immediately before clustering/investigation dispatch,
    via `property_metadata.enforce_scope_boundary` -- the same canonical
    `split_properties_by_scope` rule `semantic_only_driver.run_semantic_
    investigation`'s own primary filter already applies upstream
    (Invariant C: never a second matcher). In normal operation (the
    primary filter already ran) this is a no-op -- it exists to catch a
    property that reaches this call by some path that skipped the
    primary filter, not because the primary filter is expected to fail.

    Returns the same 4-tuple as `prepare_cluster_investigations` plus a
    5th element, `violations` (empty list in normal operation; each
    element is a `{"boundary": ..., "property_id": ..., "target_files":
    ...}` record).
    """
    kept, violations = enforce_scope_boundary(properties, scope_files, "boundary_a_pre_investigation")
    clusters, properties_by_id, protocol_context_md, req_ctx_by_id = prepare_cluster_investigations(
        kept, policy_name, audit_id, slither, scope_files, repo_root=repo_root,
        protocol_context_override=protocol_context_override,
    )
    return clusters, properties_by_id, protocol_context_md, req_ctx_by_id, violations


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


def _load_checkpoint(checkpoint_path: Path) -> tuple[dict[str, PropertyVerdict], dict[str, dict], float, set[str]]:
    """Reads a checkpoint file written by `_append_checkpoint` (one JSON
    line per completed Codex call, whether it finalized or split -- see
    that function's docstring for the exact shape). Returns
    (verdicts, raw_entries, total_cost_so_far, resolved_property_ids) --
    the last is used by `run_cluster_investigations_live` to skip
    re-dispatching a cluster whose every property already has a
    checkpointed verdict. Missing/empty file returns all-empty state, not
    an error -- a checkpoint is optional, additive persistence, never a
    precondition.
    """
    verdicts: dict[str, PropertyVerdict] = {}
    raw_entries: dict[str, dict] = {}
    total_cost = 0.0
    resolved_property_ids: set[str] = set()
    if not checkpoint_path.exists():
        return verdicts, raw_entries, total_cost, resolved_property_ids
    for line in checkpoint_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        total_cost += rec.get("cost_usd", 0.0)
        for pid, v in rec.get("verdicts", {}).items():
            verdicts[pid] = PropertyVerdict(ConformanceState(v["conformance_state"]), v.get("reason"))
            resolved_property_ids.add(pid)
        for pid, entry in rec.get("raw_entries", {}).items():
            raw_entries[pid] = entry
    return verdicts, raw_entries, total_cost, resolved_property_ids


def _append_checkpoint(
    checkpoint_path: Path, case_id: str, cost_usd: float,
    verdicts: dict[str, PropertyVerdict], raw_entries: dict[str, dict],
) -> None:
    """Appends ONE JSON line per completed Codex call (real, live-
    motivated fix, 2026-08-14: a real 2024-08-phi investigation run was
    interrupted mid-way and every in-memory verdict/cost record -- 7 of
    11 properties' worth of real, already-paid-for work -- was
    unrecoverable because nothing had been persisted incrementally).
    `cost_usd` is this SPECIFIC call's own cost contribution (recorded
    even when the call led to a split, i.e. `verdicts`/`raw_entries` are
    empty -- money was still spent and must still count toward a resumed
    run's `total_cost`/cost-ceiling accounting). `verdicts`/`raw_entries`
    are only the properties THIS call finalized (empty for a split).
    Append-only, one line per call -- safe to write from multiple worker
    threads only because each call's write is a single `open(...,
    "a")`+`write()` (atomic for a line this size on a local filesystem;
    no cross-thread locking added since `_process_result`, this
    function's only caller, already runs its own bookkeeping in the main
    thread per `run_cluster_investigations_live`'s own concurrency
    docstring).
    """
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "case_id": case_id,
        "cost_usd": cost_usd,
        "verdicts": {
            pid: {"conformance_state": v.conformance_state.value, "reason": v.reason}
            for pid, v in verdicts.items()
        },
        "raw_entries": raw_entries,
    }
    with open(checkpoint_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


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
    compile_via_foundry: bool = False,
    checkpoint_path: Path | None = None,
    estimated_cost_per_call_usd: float = 0.20,
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

    `compile_via_foundry` (default `False`, unchanged prior behavior):
    forwarded verbatim to every `run_arm_g_bundle_fn` call -- the real
    `arm_g_codex.run_arm_g_bundle` uses it to tell the graph MCP server
    subprocess (`GRAPH_COMPILE_VIA_FOUNDRY` env var) to build its
    `ProgramGraph` from the SAME already-compiled Foundry artifacts
    generation used, instead of an independent second compile. See
    RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md SS11-SS13 (Invariant E).

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

    `checkpoint_path` (default `None`, unchanged prior behavior -- no
    file I/O beyond what already existed): when given, every completed
    Codex call's cost and any verdicts it finalized are appended to this
    file as they happen (`_append_checkpoint`), and on entry, any
    already-checkpointed state is loaded (`_load_checkpoint`) and
    clusters whose every property already has a checkpointed verdict are
    skipped entirely -- a genuinely resumable run, not just a passive
    log. Real motivation, not speculative: a real 2024-08-phi
    investigation run (2026-08-14) was interrupted mid-way and lost 7
    already-completed, already-paid-for verdicts because nothing had
    been persisted incrementally.

    `estimated_cost_per_call_usd` (default `0.20`, this project's own
    observed historical per-investigation order of magnitude -- see
    RTF_V2_LIVE_VALIDATION_*.md): used only when `cost_ceiling_usd` is
    set, to decide how many calls it's safe to launch in the NEXT batch
    without overspending past the ceiling -- see the loop body below for
    why this is needed (real motivation: the same interrupted run
    reported the ceiling was "checked between concurrent batches, not
    reserved per in-flight call," meaning a full batch of
    `max_concurrent_investigations` calls could launch even with almost
    no budget left). Once at least one real call has completed, the
    RUNNING AVERAGE of actual `cost_usd` values replaces this estimate.
    """
    if run_arm_g_bundle_fn is None:
        from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import run_arm_g_bundle
        run_arm_g_bundle_fn = run_arm_g_bundle

    all_verdicts: dict[str, PropertyVerdict] = {}
    all_results: dict[str, object] = {}
    all_raw_entries: dict[str, dict] = {}
    total_cost = 0.0
    completed_calls = 0
    entry_slug = entry_sol_file.stem
    max_workers = max(1, max_concurrent_investigations)

    resolved_property_ids: set[str] = set()
    if checkpoint_path is not None:
        checkpoint_verdicts, checkpoint_raw_entries, checkpoint_cost, resolved_property_ids = _load_checkpoint(checkpoint_path)
        all_verdicts.update(checkpoint_verdicts)
        all_raw_entries.update(checkpoint_raw_entries)
        total_cost += checkpoint_cost

    def _prepare(cluster: Cluster) -> dict:
        # Include each member property's PARENT requirement id too (Phase
        # 4) -- otherwise the parent's context markdown, even though
        # `requirement_context_by_req_id` already has it, would never
        # actually be written to `extra_files`/linked in the cluster plan.
        req_ids_in_cluster = sorted({properties_by_id[pid].requirement_id for pid in cluster.property_ids} | {
            properties_by_id[pid].parent_requirement_id for pid in cluster.property_ids
            if properties_by_id[pid].parent_requirement_id
        })
        req_context_paths = {rid: f".rtf/context/requirements/{rid}.md" for rid in req_ids_in_cluster}
        plan_path = f".rtf/plans/{cluster.cluster_id}.md"

        extra_files = {".rtf/context/protocol_context.md": protocol_context_md}
        for rid in req_ids_in_cluster:
            content = requirement_context_by_req_id.get(rid)
            if content is not None:
                extra_files[req_context_paths[rid]] = content
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
            compile_via_foundry=compile_via_foundry,
        )

    def _process_result(cluster: Cluster, depth: int, case_id: str, result) -> None:
        nonlocal total_cost
        all_results[case_id] = result
        call_cost = getattr(result, "cost_usd", 0.0)
        total_cost += call_cost

        response = getattr(result, "final_decision", None)
        validation = validate_cluster_response(list(cluster.property_ids), response)
        resolved = resolve_property_verdicts(response, properties_by_id) if isinstance(response, dict) else {}
        call_raw_entries: dict[str, dict] = {}
        if isinstance(response, dict):
            for entry in response.get("properties", []):
                if isinstance(entry, dict) and entry.get("property_id"):
                    all_raw_entries[entry["property_id"]] = entry
                    call_raw_entries[entry["property_id"]] = entry

        split_reason = detect_split_reason(
            cluster, properties_by_id, budget=budget, validation_result=validation, resolved_verdicts=resolved,
        )
        if split_reason.should_split and depth < max_split_depth and len(cluster.property_ids) >= 2:
            half_a, half_b = split_cluster(cluster, properties_by_id)
            pending.append((half_a, depth + 1))
            pending.append((half_b, depth + 1))
            if checkpoint_path is not None:
                # Money was spent even though nothing finalized -- must
                # still be recorded so a resumed run's total_cost/ceiling
                # accounting reflects it (see _append_checkpoint docstring).
                _append_checkpoint(checkpoint_path, case_id, call_cost, {}, {})
            return

        call_verdicts: dict[str, PropertyVerdict] = {}
        for pid in cluster.property_ids:
            verdict = resolved.get(
                pid, PropertyVerdict(ConformanceState.INCONCLUSIVE, "cluster_investigation_incomplete_or_failed"),
            )
            all_verdicts[pid] = verdict
            call_verdicts[pid] = verdict
        if checkpoint_path is not None:
            _append_checkpoint(checkpoint_path, case_id, call_cost, call_verdicts, call_raw_entries)

    pending: list[tuple[Cluster, int]] = [
        (cluster, 0) for cluster in clusters
        if not resolved_property_ids or not set(cluster.property_ids) <= resolved_property_ids
    ]

    while pending:
        if cost_ceiling_usd is not None and total_cost >= cost_ceiling_usd:
            for cluster, _depth in pending:
                for pid in cluster.property_ids:
                    all_verdicts[pid] = PropertyVerdict(ConformanceState.INCONCLUSIVE, "cost_ceiling_reached")
            break

        # Concurrency-aware cost reservation: cap how many calls this
        # batch launches to what the REMAINING budget can plausibly
        # cover, using the running average of real completed-call costs
        # once any exist, else `estimated_cost_per_call_usd`. Without
        # this, the ceiling check above (only re-run BETWEEN batches) can
        # pass with a small amount of budget left and then still launch a
        # full `max_workers`-sized batch, overspending once they all
        # complete -- confirmed live, see this function's own docstring.
        if cost_ceiling_usd is not None:
            avg_cost_per_call = (total_cost / completed_calls) if completed_calls else estimated_cost_per_call_usd
            remaining_budget = cost_ceiling_usd - total_cost
            affordable = max(1, int(remaining_budget / avg_cost_per_call)) if avg_cost_per_call > 0 else max_workers
            batch_size = min(max_workers, affordable, len(pending))
        else:
            batch_size = min(max_workers, len(pending))

        batch = pending[:batch_size]
        pending = pending[batch_size:]
        items = [(_prepare(cluster), depth) for cluster, depth in batch]

        with ThreadPoolExecutor(max_workers=len(items)) as executor:
            future_to_item = {executor.submit(_invoke, item): (item, depth) for item, depth in items}
            for future in as_completed(future_to_item):
                item, depth = future_to_item[future]
                cluster = item["cluster"]
                try:
                    result = future.result()
                except Exception as e:  # noqa: BLE001 -- one cluster crashing must not kill the batch/run
                    completed_calls += 1
                    for pid in cluster.property_ids:
                        all_verdicts[pid] = PropertyVerdict(ConformanceState.INCONCLUSIVE, f"cluster_invocation_crashed:{type(e).__name__}")
                    continue
                completed_calls += 1
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
