"""L12 end-to-end orchestrator: EthTrust requirements -> routing (fully
deterministic vs. agent-required, decided ahead of time from each
requirement's own Track A design record) -> deterministic-complete
requirements resolved directly from predicate evidence, agent-required
requirements investigated directly by a full-repository-access Codex
agent -> merged per-requirement conformance results.

**Architecture history, current as of the "revisit the RTF architecture"
redesign**: an EARLIER version of this module ran bounded L8 first for
every evidence-backed requirement and escalated to Codex only when L8's
own judgment was uncertain (INSUFFICIENT_EVIDENCE/INCONCLUSIVE/LOW
confidence). That "bounded L8 as an escalation gate" design was found to
violate the intended architecture: it let LLM-required requirements
terminate on a bounded judgment without ever giving an agent the chance
to actually explore the repository, and (combined with a separate
generic-evidence-collector's fixed-size excerpt) produced a real, found-
by-forensic-inspection missed finding on `2025-01-liquid-ron`'s H-01 --
see RTF_AGENTIC_ARCHITECTURE.md for the full analysis. Bounded L8 is no
longer a gate: every requirement is routed exactly once, ahead of time
(`registry.DETERMINISTIC_COMPLETE_REQ_IDS` vs
`registry.AGENT_REQUIRED_REQ_IDS`), and `judge_with_l8.judge_result` is
not called anywhere in this file's main loop -- see
`RTF_AGENTIC_ARCHITECTURE.md` for what, if anything, still uses it.

`run_rtf.py` (deterministic layer + routing), `codex_bridge.py` +
`bundle_agent_experiment/arm_g_codex.py` (the now-mandatory-when-routed
agent investigation, with full repository access -- see
`arm_g_codex.run_arm_g_bundle`'s own docstring) are chained here into one
call.

**Known architecture gap, not silently worked around:** the frozen 5-audit
pilot architecture describes "one evidence bundle per candidate location."
The actually-wired L1-L8 pipeline operates at REQUIREMENT granularity --
one `RoutedRequirementResult` can carry evidence at several different
locations. This orchestrator resolves that mismatch pragmatically: when a
requirement escalates, the single HIGHEST-RANKED evidence location (by
the same deterministic `rank_evidence` scoring L8's own prompt uses)
becomes the graph-navigation seed/candidate_location, while Codex still
receives the full ranked evidence-bundle text (all locations, not just
the seed) as context. This is a real, load-bearing simplification, not a
cosmetic one -- true per-candidate routing (one escalation per distinct
location, not per requirement) is a larger change than "fix implementation
defects" covers and belongs in the preregistration's known-limitations
section.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

from a4v.graph import ProgramGraph
from rtf.l5_predicates.compile_helper import _collect_remappings
from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import ArmGResult, build_arm_g_prompt, run_arm_g_bundle
from rtf.l8_llm_judgment_layer.graph_navigation import resolve_seed_node
from rtf.l8_llm_judgment_layer.judgment_layer import LLMJudgmentLayer
from rtf.l12_evaluation.codex_bridge import build_codex_prompt_inputs, resolve_conformance_from_arm_g
from rtf.l12_evaluation.evidence_ranking import rank_evidence
from rtf.l12_evaluation.failure_taxonomy import OperationalStatus
from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState, RoutedRequirementResult, TargetRunResult
from rtf.l12_evaluation.registry import AGGREGATION_REQ_IDS, LLM_MEDIATED_REQ_IDS, REGISTRY
from rtf.l12_evaluation.run_rtf import (
    RunContext,
    build_context_for_evmbench_target,
    load_requirement_levels,
    load_unconditioned_map,
    run_rtf,
)
from rtf.standards.routing import StandardsIntegrityReport, build_standards_routed_requirements

CORPUS_PATH = Path(__file__).resolve().parents[2] / "rtf" / "l1_corpus" / "requirement_corpus.json"


def compute_aggregation_requirements(
    routed: dict[str, RoutedRequirementResult],
    requirement_levels: dict[str, str],
) -> dict[str, RoutedRequirementResult]:
    """Resolves the 3 pure-aggregation requirements
    (`registry.AGGREGATION_REQ_IDS`) from every OTHER requirement's own
    FINAL `conformance_state`. Must run AFTER L8 judgment/escalation have
    resolved everything else in `routed` -- `run_rtf.py`'s own
    deterministic-only pass cannot compute these (almost every
    evidence-backed requirement is still `conformance_state=None`,
    "pending L8", at that point), which is exactly why `run_rtf.py`
    leaves them as an explicit placeholder rather than a real verdict.

    Aggregation rule for req-2-pass-l1 ("MUST meet the requirements for
    ... Security Level [S]") / req-3-pass-l2 (same, for Level [M]) --
    mechanical AND, directly from each requirement's own normative text,
    over every OTHER requirement at that level (never itself):
      - PASS: every constituent is PASS, or NOT_APPLICABLE (a conditioned
        requirement whose trigger never fired was never violated).
      - FAIL: any constituent is FAIL.
      - INCONCLUSIVE: no FAIL, but at least one constituent is unresolved
        (INCONCLUSIVE / INSUFFICIENT_EVIDENCE / an operational failure /
        UNSUPPORTED_ANALYZER) -- this framework cannot honestly claim the
        level was met, but nothing has been shown to violate it either.

    req-R-meet-all-possible ("SHOULD meet as many requirements ... as
    possible") is advisory, not a MUST gate, and this framework has no
    concept of "the security level for which it is certified" to compare
    against (an external, undefined input the requirement's own text
    presupposes) -- per RFC2119 a SHOULD is never given a hard FAIL by an
    invented threshold (consistent with AR-006's already-logged open
    question on SHOULD-level semantics). Resolved as PASS only if every
    OTHER applicable requirement in the ENTIRE corpus is PASS/
    NOT_APPLICABLE (the maximal case), else INCONCLUSIVE -- never FAIL.

    Neither rule was derived from, or tuned against, any EVMbench ground
    truth -- both are the literal, mechanical reading of each
    requirement's own normative text applied to results this framework
    already produced for unrelated reasons.
    """
    updated = dict(routed)
    by_level: dict[str, list[str]] = {}
    for req_id, level in requirement_levels.items():
        by_level.setdefault(level, []).append(req_id)

    def _aggregate(constituent_req_ids: list[str]) -> ConformanceState:
        saw_fail = False
        saw_unresolved = False
        for rid in constituent_req_ids:
            r = routed.get(rid)
            if r is None:
                saw_unresolved = True
                continue
            if r.applicability_state == ApplicabilityState.NOT_APPLICABLE:
                continue
            if r.conformance_state == ConformanceState.PASS:
                continue
            if r.conformance_state == ConformanceState.FAIL:
                saw_fail = True
            else:
                saw_unresolved = True
        if saw_fail:
            return ConformanceState.FAIL
        if saw_unresolved:
            return ConformanceState.INCONCLUSIVE
        return ConformanceState.PASS

    def _replace(req_id: str, state: ConformanceState) -> None:
        prior = routed[req_id]
        updated[req_id] = RoutedRequirementResult(
            req_id=req_id, applicability_state=prior.applicability_state,
            operational_status=prior.operational_status, conformance_state=state,
            evidence=prior.evidence,
        )

    if "req-2-pass-l1" in routed:
        _replace("req-2-pass-l1", _aggregate([r for r in by_level.get("S", []) if r != "req-2-pass-l1"]))
    if "req-3-pass-l2" in routed:
        _replace("req-3-pass-l2", _aggregate([r for r in by_level.get("M", []) if r != "req-3-pass-l2"]))
    if "req-R-meet-all-possible" in routed:
        all_other = [rid for rid in routed if rid != "req-R-meet-all-possible" and rid not in AGGREGATION_REQ_IDS]
        state = _aggregate(all_other)
        if state == ConformanceState.FAIL:  # SHOULD-level: never a hard FAIL, see docstring
            state = ConformanceState.INCONCLUSIVE
        _replace("req-R-meet-all-possible", state)

    return updated


def compute_terminal_status(r: RoutedRequirementResult) -> str:
    """Maps a requirement's full (applicability, operational_status,
    conformance_state) result onto the flat terminal-status vocabulary
    the supervised-validation invariant requires: PASS, FAIL,
    INCONCLUSIVE, NOT_APPLICABLE, UNSUPPORTED_ANALYZER, EXECUTION_ERROR --
    plus INSUFFICIENT_EVIDENCE (an existing, load-bearing
    `ConformanceState` value used throughout this codebase; kept as its
    own bucket rather than folded into INCONCLUSIVE, which would lose
    real information already being tracked) and PENDING_UNRESOLVED
    (should NEVER appear in a valid run's final counts -- see
    `compute_integrity_report`; its presence is exactly what
    `silently_missing` measures).
    """
    if r.applicability_state == ApplicabilityState.NOT_APPLICABLE:
        return "NOT_APPLICABLE"
    if r.operational_status == OperationalStatus.UNSUPPORTED_ANALYZER:
        return "UNSUPPORTED_ANALYZER"
    if r.operational_status != OperationalStatus.OK:
        return "EXECUTION_ERROR"
    if r.conformance_state is not None:
        return r.conformance_state.value
    return "PENDING_UNRESOLVED"


@dataclass
class IntegrityReport:
    total_requirements: int = 0
    applicable: int = 0
    not_applicable: int = 0
    applicable_executed_deterministic: int = 0
    applicable_executed_llm_mediated: int = 0
    terminal_status_counts: dict = field(default_factory=dict)
    silently_missing: int = 0
    silently_missing_req_ids: list = field(default_factory=list)
    valid: bool = True
    invalid_reason: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def compute_integrity_report(routed: dict[str, RoutedRequirementResult]) -> IntegrityReport:
    """The "fail loudly" invariant this whole change exists to enforce:
    applicable requirements = executed + explicitly unsupported, and
    `silently_missing` is ALWAYS 0 for a run to be considered VALID.

    "Silently missing" means: applicable, operationally OK, not one of
    the explicit terminal states -- i.e. `compute_terminal_status`
    returned `PENDING_UNRESOLVED`. After this change's fixes
    (`run_rtf.py` iterating the full corpus + explicit
    `UNSUPPORTED_ANALYZER` + `compute_aggregation_requirements` run
    before this function), this should be empirically impossible for any
    of the 81 corpus requirements -- but this function does not assume
    that; it counts and reports, and callers (`pilot5_driver.py`) must
    treat `valid=False` as grounds to mark the whole run INVALID rather
    than a normal benchmark result, per the supervised-validation task's
    own explicit instruction.
    """
    report = IntegrityReport(total_requirements=len(routed))
    for req_id, r in routed.items():
        if r.applicability_state == ApplicabilityState.NOT_APPLICABLE:
            report.not_applicable += 1
        else:
            report.applicable += 1
            if r.applicability_state == ApplicabilityState.APPLICABLE and r.operational_status == OperationalStatus.OK:
                if req_id in AGGREGATION_REQ_IDS:
                    pass  # aggregation requirements are neither deterministic nor LLM-mediated evidence collection
                elif req_id in LLM_MEDIATED_REQ_IDS:
                    report.applicable_executed_llm_mediated += 1
                elif req_id in REGISTRY:
                    report.applicable_executed_deterministic += 1

        status = compute_terminal_status(r)
        report.terminal_status_counts[status] = report.terminal_status_counts.get(status, 0) + 1
        if status == "PENDING_UNRESOLVED":
            report.silently_missing += 1
            report.silently_missing_req_ids.append(req_id)

    report.valid = report.silently_missing == 0
    if not report.valid:
        report.invalid_reason = (
            f"{report.silently_missing} applicable requirement(s) reached no explicit terminal "
            f"state: {report.silently_missing_req_ids}"
        )
    return report


@dataclass
class StageMetrics:
    requirements_considered: int = 0
    requirements_applicable: int = 0
    evidence_bundles_generated: int = 0  # requirements with >=1 evidence item
    # As of the "revisit the RTF architecture" redesign, bounded L8 is NOT
    # called in this loop at all (no gate before the agent) -- these three
    # fields are always 0 in the live path now. Kept, not deleted, on the
    # StageMetrics dataclass because judge_with_l8.judge_result itself is
    # kept as a reusable component for the documented (but not currently
    # wired) optional post-agent verifier role -- see
    # RTF_AGENTIC_ARCHITECTURE.md. A nonzero value here would only appear
    # if that role is wired back in later.
    judgments_attempted: int = 0
    judgments_succeeded: int = 0
    judgments_failed: int = 0
    # Always 0 now for the same reason -- every AGENT_REQUIRED_REQ_IDS
    # requirement that reaches the loop body goes straight to the agent,
    # none are "judged without" it anymore.
    bundles_judged_without_codex: int = 0
    # "Codex"/"agent" are used interchangeably below -- every one of these
    # is now an unconditional agent investigation (per AGENT_REQUIRED_REQ_IDS
    # routing), not a maybe-escalation gated on bounded-L8 uncertainty.
    bundles_escalated_to_codex: int = 0
    codex_investigations_completed: int = 0
    codex_investigations_timed_out: int = 0
    codex_investigations_skipped_cost_ceiling: int = 0
    final_decisions: dict = field(default_factory=lambda: {s.value: 0 for s in ConformanceState})

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PipelineArtifacts:
    run: TargetRunResult
    stage_metrics: StageMetrics
    raw_l8_judgments: dict  # req_id -> raw judge_with_l8 output
    codex_results: dict  # req_id -> ArmGResult (only escalated reqs)
    escalation_skip_reasons: dict  # req_id -> reason string, for requirements that should have escalated but didn't (cost ceiling)
    codex_outcome_reasons: dict  # req_id -> machine-readable reason (codex_timeout/codex_no_decision/codex_unknown_decision:<x>), only set when Codex's own outcome wasn't a genuine parsed decision -- see codex_bridge.resolve_conformance_from_arm_g
    total_codex_cost_usd: float
    integrity_report: IntegrityReport  # see compute_integrity_report -- callers MUST check .valid before treating this run as a normal result
    standards_report: StandardsIntegrityReport = field(default_factory=StandardsIntegrityReport)
    """Additive breakdown for rtf/standards/-generated requirements (§12):
    standards discovered, clauses loaded, requirements generated/applicable/
    routed. Defaulted so existing callers constructing PipelineArtifacts
    without this field (if any exist outside this module) keep working."""
    graph_seed_resolved: dict = field(default_factory=dict)  # req_id -> bool, whether a pre-resolved graph hint was available BEFORE the agent started (observability only -- never gates whether the agent runs, see arm_g_codex.py's redesign)
    generated_bundles: dict = field(default_factory=dict)
    """req_id -> in-memory L2-bundle-shaped dict, for generated (ERC-
    standard-derived) requirements only -- lets report_generator.py look
    up a real title/obligation text for a generated req_id instead of
    falling back to the bare req_id string, without report_generator.py
    needing to import anything from rtf.standards itself."""


def _run_escalations_concurrent(
    *,
    routed: dict[str, RoutedRequirementResult],
    new_routed: dict[str, RoutedRequirementResult],
    ctx: RunContext,
    compile_error,
    project_root: Path,
    entry_sol_file: Path,
    generated_bundles: dict[str, dict],
    audit_id: str,
    codex_bin: Path,
    python_bin: Path,
    mcp_server_script: Path,
    api_key: str,
    codex_model: str,
    solc_path_dir: str,
    scratch_root: Path,
    codex_timeout_s: int,
    cost_ceiling_usd: float | None,
    max_workers: int,
    metrics: StageMetrics,
    codex_results: dict,
    escalation_skip_reasons: dict[str, str],
    codex_outcome_reasons: dict[str, str],
    graph_seed_resolved: dict[str, bool],
) -> float:
    """Concurrent counterpart to `run_pipeline_e2e`'s serial escalation
    loop. Two phases, deliberately kept separate:

    Phase 1 (sequential, cheap, local -- no I/O): for every requirement
    needing escalation, resolve `candidate_location` (rank_evidence),
    attempt graph-seed resolution against the ONE shared `ProgramGraph`
    (built lazily once, same as the serial path), and build the full
    prompt. Stays single-threaded because it touches shared mutable state
    (`pg`) and is fast/local anyway -- no benefit to parallelizing it.

    Phase 2 (concurrent, I/O-bound): only the actual `run_arm_g_bundle`
    subprocess calls, in batches of `max_workers` via a
    `ThreadPoolExecutor`. Threads, not processes: each call is I/O-bound
    (subprocess + network wait), not CPU-bound. Safe to parallelize
    because each call already writes to its own isolated scratch path
    keyed by `case_id` (`arm_g_codex.run_arm_g_bundle`'s own docstring:
    unconditionally rm-trees/unlinks any pre-existing path for that
    `case_id` -- distinct req_ids in the same entry never collide). All
    dict/counter bookkeeping (`metrics`, `codex_results`, `new_routed`,
    etc.) happens in the MAIN thread only, as each future resolves via
    `as_completed` -- worker threads only call `run_arm_g_bundle` and
    return its result, they never touch shared mutable state directly.

    Cost-ceiling enforcement is checked once per BATCH (before submitting
    it), using only cost from batches that have FULLY completed -- a
    call's real cost is only known after it returns, so under concurrency
    up to `max_workers - 1` extra investigations may already be in flight
    when the ceiling is crossed mid-batch. A wider (but still bounded, and
    explicitly documented) version of the same limitation the serial path
    already has.
    """
    escalation_items: list[dict] = []
    pg: ProgramGraph | None = None

    for req_id, result in routed.items():
        if result.applicability_state != ApplicabilityState.APPLICABLE:
            continue
        if result.conformance_state is not None:
            continue
        if not result.evidence or result.operational_status.value != "OK":
            continue

        updated = result
        ranked = rank_evidence(list(updated.evidence), project_root)
        candidate_location = ranked[0].item.location if ranked else ""

        graph_seed_resolved[req_id] = False
        try:
            if pg is None:
                if ctx.slither is None:
                    raise RuntimeError(
                        f"no compiled Slither object available (compile_error={compile_error!r})"
                    )
                pg = ProgramGraph.from_slither(ctx.slither)
            if candidate_location:
                resolve_seed_node(pg, candidate_location)
                graph_seed_resolved[req_id] = True
        except Exception as e:  # noqa: BLE001 -- resolution failure is informational only, never blocks the agent
            escalation_skip_reasons[req_id] = f"graph_seed_not_resolved (agent still investigates): {type(e).__name__}: {e}"

        prompt_inputs = build_codex_prompt_inputs(
            req_id, candidate_location, updated, project_root, None,
            bundle_record=generated_bundles.get(req_id),
        )
        prompt = build_arm_g_prompt(
            prompt_inputs.requirement_text, prompt_inputs.context_bundle_text,
            prompt_inputs.candidate_location, prompt_inputs.evidence_bundle_text,
            prompt_inputs.unresolved_facts,
        )
        entry_slug = entry_sol_file.stem
        escalation_items.append({
            "req_id": req_id, "updated": updated,
            "case_id": f"{audit_id}__{entry_slug}__{req_id}",
            "candidate_location": candidate_location, "prompt": prompt,
        })

    remaps = _collect_remappings(project_root)
    total_codex_cost = 0.0

    def _invoke(item: dict):
        return run_arm_g_bundle(
            codex_bin=codex_bin, python_bin=python_bin, mcp_server_script=mcp_server_script,
            api_key=api_key, model=codex_model, case_id=item["case_id"],
            entry_file=entry_sol_file, repo_root=project_root,
            candidate_location=item["candidate_location"],
            solc_path_dir=solc_path_dir, solc_remaps=remaps, prompt=item["prompt"],
            scratch_root=scratch_root, timeout_s=codex_timeout_s,
        )

    i = 0
    while i < len(escalation_items):
        if cost_ceiling_usd is not None and total_codex_cost >= cost_ceiling_usd:
            for item in escalation_items[i:]:
                req_id = item["req_id"]
                metrics.codex_investigations_skipped_cost_ceiling += 1
                escalation_skip_reasons[req_id] = "cost_ceiling_reached"
                new_routed[req_id] = replace(item["updated"], conformance_state=ConformanceState.INCONCLUSIVE)
            break

        batch = escalation_items[i:i + max_workers]
        i += len(batch)

        with ThreadPoolExecutor(max_workers=len(batch)) as executor:
            future_to_item = {executor.submit(_invoke, item): item for item in batch}
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                req_id = item["req_id"]
                updated = item["updated"]
                try:
                    codex_result = future.result()
                except Exception as e:  # noqa: BLE001 -- one investigation crashing must not kill the batch/run
                    escalation_skip_reasons[req_id] = f"codex_invocation_crashed: {type(e).__name__}: {e}"
                    new_routed[req_id] = replace(updated, conformance_state=ConformanceState.INCONCLUSIVE)
                    continue

                codex_results[req_id] = codex_result
                total_codex_cost += codex_result.cost_usd
                metrics.bundles_escalated_to_codex += 1
                if codex_result.timed_out:
                    metrics.codex_investigations_timed_out += 1
                else:
                    metrics.codex_investigations_completed += 1

                outcome = resolve_conformance_from_arm_g(codex_result.final_decision, codex_result.timed_out)
                if outcome.reason is not None:
                    codex_outcome_reasons[req_id] = outcome.reason
                new_routed[req_id] = RoutedRequirementResult(
                    req_id=req_id, applicability_state=updated.applicability_state,
                    operational_status=updated.operational_status,
                    conformance_state=outcome.conformance_state, evidence=updated.evidence,
                )

    return total_codex_cost


def run_pipeline_e2e(
    *,
    audit_id: str,
    entry_sol_file: Path,
    project_root: Path,
    solc_version: str,
    judgment_layer: LLMJudgmentLayer,
    codex_bin: Path,
    python_bin: Path,
    mcp_server_script: Path,
    api_key: str,
    codex_model: str,
    solc_path_dir: str,
    scratch_root: Path,
    escalation_enabled: bool = True,
    codex_timeout_s: int = 900,
    cost_ceiling_usd: float | None = None,
    known_limitations: dict[str, str] | None = None,
    only_req_ids: set[str] | None = None,
    max_concurrent_investigations: int = 1,
    extra_solc_args: list[str] | None = None,
) -> PipelineArtifacts:
    """Runs the full L1->L8->(escalation)->Arm G chain for one real target.

    `max_concurrent_investigations`: defaults to 1 -- EXACTLY the original
    serial behavior (unchanged code path, see `_run_escalations_serial`).
    When > 1, Codex investigations for this entry run concurrently in
    batches of that size instead (`_run_escalations_concurrent`) -- each
    investigation already gets its own isolated scratch directory keyed by
    `case_id` (`arm_g_codex.run_arm_g_bundle`'s own docstring), so this is
    safe: no shared mutable state is touched from more than one thread.
    Wall-clock time only (real Codex/API cost is per-investigation and
    unaffected by how many run at once). The cost ceiling is still
    enforced, but at BATCH granularity under concurrency, not per-call --
    up to `max_concurrent_investigations - 1` extra investigations may
    already be in flight when the ceiling is crossed, since a call's real
    cost is only known after it returns (same documented limitation the
    serial path already has, just with a slightly larger bound under
    concurrency). See RTF_CONCURRENT_INVESTIGATIONS.md.

    `cost_ceiling_usd`, if given, is enforced INCREMENTALLY: before
    launching each new Codex escalation, the sum of `cost_usd` already
    spent by Codex calls completed so far IN THIS RUN is checked against
    the ceiling (a call's real cost is only known after it returns, so
    this is the finest-grained enforcement possible without a live,
    separately-polled OpenRouter balance check, which is out of scope for
    this pass -- see the pilot report for this documented limitation).
    Once the ceiling is hit, remaining escalation-eligible requirements
    are marked `ConformanceState.INCONCLUSIVE` with reason
    "cost_ceiling_reached" rather than silently dropped or attempted
    anyway.
    """
    metrics = StageMetrics()
    unconditioned_map = load_unconditioned_map(CORPUS_PATH)
    requirement_levels = load_requirement_levels(CORPUS_PATH)
    ctx, compile_error = build_context_for_evmbench_target(
        entry_sol_file, project_root, solc_version, extra_solc_args=extra_solc_args,
    )

    run, _raw = run_rtf(ctx, audit_id, unconditioned_map, known_limitations)

    # --- Standards-driven GP requirement generation (additive) ---
    # Merges dynamically-generated ERC-standard-derived requirements
    # (rtf/standards/) into `run.routed` BEFORE the escalation loop below,
    # which is already fully generic over (req_id -> RoutedRequirementResult)
    # and needs no further changes to process them identically to the
    # frozen 81-requirement corpus. Skipped (not a crash) when compilation
    # failed -- discovery genuinely needs a compiled Slither object, same
    # precondition every other Slither-backed predicate already has.
    generated_bundles: dict[str, dict] = {}
    standards_report = StandardsIntegrityReport()
    if ctx.slither is not None and ctx.repo_root is not None:
        generated_routed, standards_report, generated_bundles = build_standards_routed_requirements(
            repo_root=ctx.repo_root, entry_sol_file=entry_sol_file, slither=ctx.slither,
        )
        run = TargetRunResult(audit_id=run.audit_id, routed={**run.routed, **generated_routed})

    if only_req_ids is not None:
        run = TargetRunResult(audit_id=run.audit_id,
                               routed={k: v for k, v in run.routed.items() if k in only_req_ids})

    metrics.requirements_considered = len(run.routed)
    metrics.requirements_applicable = sum(
        1 for r in run.routed.values() if r.applicability_state == ApplicabilityState.APPLICABLE
    )
    metrics.evidence_bundles_generated = sum(1 for r in run.routed.values() if r.evidence)

    raw_l8_judgments: dict = {}
    codex_results: dict[str, ArmGResult] = {}
    escalation_skip_reasons: dict[str, str] = {}
    codex_outcome_reasons: dict[str, str] = {}
    graph_seed_resolved: dict[str, bool] = {}
    total_codex_cost = 0.0
    pg: ProgramGraph | None = None  # built lazily, once, only if an escalation actually happens

    new_routed = dict(run.routed)
    if max_concurrent_investigations <= 1:
        # Original serial path -- byte-for-byte unchanged from before
        # `max_concurrent_investigations` existed, so every existing test
        # (which calls this function without that parameter, defaulting to
        # 1) continues to exercise EXACTLY this code, unmodified.
        for req_id, result in run.routed.items():
            if result.applicability_state != ApplicabilityState.APPLICABLE:
                continue
            if result.conformance_state is not None:
                continue  # already resolved deterministically (DETERMINISTIC_COMPLETE_REQ_IDS, run_rtf.py) -- no agent needed at all
            if not result.evidence or result.operational_status.value != "OK":
                continue

            # By construction (registry.py's own asserted partition), every
            # requirement that reaches this point -- applicable, evidence-
            # backed, not yet resolved -- is in AGENT_REQUIRED_REQ_IDS.
            # Per the "revisit the RTF architecture" directive: bounded L8 is
            # NOT a gate that decides whether an agent investigation happens.
            # It goes straight to the agent. `judge_with_l8.judge_result` is
            # no longer called in this path at all (kept, untouched, as a
            # reusable component for the optional post-agent verifier role --
            # see RTF_AGENTIC_ARCHITECTURE.md).
            updated = result

            if cost_ceiling_usd is not None and total_codex_cost >= cost_ceiling_usd:
                metrics.codex_investigations_skipped_cost_ceiling += 1
                escalation_skip_reasons[req_id] = "cost_ceiling_reached"
                new_routed[req_id] = replace(updated, conformance_state=ConformanceState.INCONCLUSIVE)
                continue

            # Best-effort HINT only -- the single highest-ranked evidence
            # location for this requirement, by the same deterministic
            # `rank_evidence` scoring L8's own prompt used to use. Never a
            # precondition: if this doesn't resolve on the graph (non-
            # function-shaped location, ambiguous overload, or simply no
            # evidence-derived location at all), the agent still runs with
            # full repository access and discovers the relevant location
            # itself -- see arm_g_codex.py/graph_mcp_server.py's redesign.
            ranked = rank_evidence(list(updated.evidence), project_root)
            candidate_location = ranked[0].item.location if ranked else ""

            graph_seed_resolved[req_id] = False
            try:
                if pg is None:
                    if ctx.slither is None:
                        raise RuntimeError(
                            f"no compiled Slither object available (compile_error={compile_error!r})"
                        )
                    pg = ProgramGraph.from_slither(ctx.slither)
                if candidate_location:
                    resolve_seed_node(pg, candidate_location)
                    graph_seed_resolved[req_id] = True
            except Exception as e:  # noqa: BLE001 -- resolution failure is informational only now, never blocks the agent
                escalation_skip_reasons[req_id] = f"graph_seed_not_resolved (agent still investigates): {type(e).__name__}: {e}"

            prompt_inputs = build_codex_prompt_inputs(
                req_id, candidate_location, updated, project_root, None,
                bundle_record=generated_bundles.get(req_id),
            )
            prompt = build_arm_g_prompt(
                prompt_inputs.requirement_text, prompt_inputs.context_bundle_text,
                prompt_inputs.candidate_location, prompt_inputs.evidence_bundle_text,
                prompt_inputs.unresolved_facts,
            )

            remaps = _collect_remappings(project_root)
            # `case_id` doubles as the scratch-artifact path (ghome/gview dirs,
            # gout.txt, gstream.jsonl, graph_trace.jsonl -- see
            # arm_g_codex.run_arm_g_bundle, which unconditionally rm-trees/
            # unlinks any pre-existing path with this case_id before writing).
            # Must include the entry file, not just (audit_id, req_id): a real,
            # confirmed-live bug found by forensic inspection AFTER this
            # session's own liquid-ron validation run completed -- the same
            # req_id (e.g. "req-3-event-on-state-change") legitimately escalates
            # across MULTIPLE different scope entries in one audit, and
            # (audit_id, req_id) alone collided across all of them, silently
            # overwriting every earlier entry's raw Codex session transcript
            # with the last one's. Did NOT affect that run's actual counted
            # results (each entry's ArmGResult was captured in memory and
            # persisted into ITS OWN stage.json before the next entry could
            # overwrite the shared scratch path) -- this is a forensic-replay/
            # observability gap, not a correctness defect, but one that would
            # compound badly on audits with far more scope entries and req_id
            # repetition (e.g. arbitrum-foundation's 39, sequence's 47).
            entry_slug = entry_sol_file.stem
            codex_result = run_arm_g_bundle(
                codex_bin=codex_bin, python_bin=python_bin, mcp_server_script=mcp_server_script,
                api_key=api_key, model=codex_model, case_id=f"{audit_id}__{entry_slug}__{req_id}",
                entry_file=entry_sol_file, repo_root=project_root, candidate_location=candidate_location,
                solc_path_dir=solc_path_dir, solc_remaps=remaps, prompt=prompt,
                scratch_root=scratch_root, timeout_s=codex_timeout_s,
            )
            codex_results[req_id] = codex_result
            total_codex_cost += codex_result.cost_usd
            metrics.bundles_escalated_to_codex += 1
            if codex_result.timed_out:
                metrics.codex_investigations_timed_out += 1
            else:
                metrics.codex_investigations_completed += 1

            outcome = resolve_conformance_from_arm_g(codex_result.final_decision, codex_result.timed_out)
            if outcome.reason is not None:
                # A non-None reason means this ISN'T a genuine parsed Codex
                # decision (codex_timeout / codex_no_decision / codex_unknown_
                # decision:<x>) -- record it so a bare INCONCLUSIVE in the
                # final result is never indistinguishable from one Codex
                # actually reasoned to, per codex_bridge.resolve_conformance_
                # from_arm_g's own documented requirement.
                codex_outcome_reasons[req_id] = outcome.reason
            new_routed[req_id] = RoutedRequirementResult(
                req_id=req_id, applicability_state=updated.applicability_state,
                operational_status=updated.operational_status,
                conformance_state=outcome.conformance_state, evidence=updated.evidence,
            )
    else:
        # Concurrent path -- see _run_escalations_concurrent's own
        # docstring for the design (resolve everything cheap/local
        # sequentially first, only the actual Codex subprocess calls run
        # concurrently, batch-bounded cost-ceiling enforcement).
        total_codex_cost = _run_escalations_concurrent(
            routed=run.routed, new_routed=new_routed, ctx=ctx, compile_error=compile_error,
            project_root=project_root, entry_sol_file=entry_sol_file,
            generated_bundles=generated_bundles, audit_id=audit_id,
            codex_bin=codex_bin, python_bin=python_bin, mcp_server_script=mcp_server_script,
            api_key=api_key, codex_model=codex_model, solc_path_dir=solc_path_dir,
            scratch_root=scratch_root, codex_timeout_s=codex_timeout_s,
            cost_ceiling_usd=cost_ceiling_usd, max_workers=max_concurrent_investigations,
            metrics=metrics, codex_results=codex_results,
            escalation_skip_reasons=escalation_skip_reasons,
            codex_outcome_reasons=codex_outcome_reasons, graph_seed_resolved=graph_seed_resolved,
        )

    # Pure-aggregation requirements (req-2-pass-l1/req-3-pass-l2/
    # req-R-meet-all-possible) can only be resolved now that every OTHER
    # requirement's L8/escalation verdict is final -- see
    # compute_aggregation_requirements's own docstring for why this can't
    # happen inside run_rtf.py. Skipped when `only_req_ids` restricts this
    # run to a deliberate subset (tests/cost-bounded runs): the full
    # corpus isn't present, so "AND over every Level S requirement" would
    # be computed over an arbitrary partial view, not a meaningful result.
    if only_req_ids is None:
        new_routed = compute_aggregation_requirements(new_routed, requirement_levels)

    final_run = TargetRunResult(audit_id=audit_id, routed=new_routed)
    for r in final_run.routed.values():
        if r.conformance_state is not None:
            metrics.final_decisions[r.conformance_state.value] += 1

    # The "fail loudly" invariant: applicable requirements = executed +
    # explicitly unsupported, silently_missing == 0. Same restriction as
    # above -- a deliberately-restricted `only_req_ids` run is not the
    # full corpus and would spuriously report requirements as "missing"
    # that were simply never in scope for this call.
    if only_req_ids is None:
        integrity_report = compute_integrity_report(new_routed)
    else:
        integrity_report = IntegrityReport(
            total_requirements=len(new_routed), valid=True,
            invalid_reason="only_req_ids restricted this run to a deliberate subset; "
                            "integrity checking is only meaningful for a full-corpus run",
        )

    return PipelineArtifacts(
        run=final_run, stage_metrics=metrics, raw_l8_judgments=raw_l8_judgments,
        codex_results=codex_results, escalation_skip_reasons=escalation_skip_reasons,
        codex_outcome_reasons=codex_outcome_reasons,
        total_codex_cost_usd=total_codex_cost,
        integrity_report=integrity_report,
        standards_report=standards_report,
        graph_seed_resolved=graph_seed_resolved,
        generated_bundles=generated_bundles,
    )
