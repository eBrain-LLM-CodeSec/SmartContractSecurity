"""L12 end-to-end orchestrator: EthTrust requirements -> deterministic
predicates -> bounded L8 judgment -> (escalation rule) -> graph-gated
Codex investigation -> merged per-requirement conformance results.

This is the first module that actually chains `run_rtf.py` (L1-L5
deterministic layer), `judge_with_l8.py` (bounded L8), the escalation
rule (`escalation.py`), and the graph-gated Codex path (`codex_bridge.py`
+ `bundle_agent_experiment/arm_g_codex.py`) into one call -- before this,
every piece existed and worked in isolation but nothing invoked them
together (confirmed by a repo-wide grep finding zero references to
`ProgramGraph`/`arm_g_codex`/escalation logic anywhere outside the
`bundle_agent_experiment/` folder).

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
from dataclasses import asdict, dataclass, field
from pathlib import Path

from a4v.graph import ProgramGraph
from rtf.l5_predicates.compile_helper import _collect_remappings
from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import ArmGResult, build_arm_g_prompt, run_arm_g_bundle
from rtf.l8_llm_judgment_layer.graph_navigation import resolve_seed_node
from rtf.l8_llm_judgment_layer.judgment_layer import LLMJudgmentLayer
from rtf.l12_evaluation.codex_bridge import build_codex_prompt_inputs, resolve_conformance_from_arm_g
from rtf.l12_evaluation.escalation import decide_escalation
from rtf.l12_evaluation.evidence_ranking import rank_evidence
from rtf.l12_evaluation.judge_with_l8 import judge_result
from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState, RoutedRequirementResult, TargetRunResult
from rtf.l12_evaluation.run_rtf import RunContext, build_context_for_evmbench_target, load_unconditioned_map, run_rtf

CORPUS_PATH = Path(__file__).resolve().parents[2] / "rtf" / "l1_corpus" / "requirement_corpus.json"


@dataclass
class StageMetrics:
    requirements_considered: int = 0
    requirements_applicable: int = 0
    evidence_bundles_generated: int = 0  # requirements with >=1 evidence item
    # Bounded-L8 judgment attempts: every evidence-backed requirement this
    # loop hands to `judge_result` is "attempted"; "succeeded" means the L8
    # call itself returned a real response (no exception, no `"error"` key
    # in the raw output -- see `judge_with_l8.judge_result`'s own per-
    # requirement isolation); "failed" is the rest (network/schema/API
    # error, degraded to ENVIRONMENT_FAILURE). Added specifically so a
    # systemic wiring bug (e.g. a wrong ChatClient type, which judge_result
    # silently converts to ENVIRONMENT_FAILURE per requirement) is visible
    # as a spike in judgments_failed rather than only showing up as an
    # oddly-clean all-INSUFFICIENT_EVIDENCE run.
    judgments_attempted: int = 0
    judgments_succeeded: int = 0
    judgments_failed: int = 0
    bundles_judged_without_codex: int = 0
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
) -> PipelineArtifacts:
    """Runs the full L1->L8->(escalation)->Arm G chain for one real target.

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
    ctx, compile_error = build_context_for_evmbench_target(entry_sol_file, project_root, solc_version)

    run, _raw = run_rtf(ctx, audit_id, unconditioned_map, known_limitations)
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
    total_codex_cost = 0.0
    pg: ProgramGraph | None = None  # built lazily, once, only if an escalation actually happens

    new_routed = dict(run.routed)
    for req_id, result in run.routed.items():
        if result.applicability_state != ApplicabilityState.APPLICABLE:
            continue
        if result.conformance_state is not None:
            continue  # already resolved deterministically (DETERMINISTIC_COMPLETE) -- no L8, no escalation
        if not result.evidence or result.operational_status.value != "OK":
            continue

        updated, raw = judge_result(judgment_layer, req_id, result, project_root, use_second_pass=True, use_ranking=True)
        new_routed[req_id] = updated
        if raw is not None:
            raw_l8_judgments[req_id] = raw
        metrics.judgments_attempted += 1
        if raw is not None and "error" not in raw:
            metrics.judgments_succeeded += 1
        else:
            metrics.judgments_failed += 1

        confidence = (raw or {}).get("first_pass", {}).get("confidence") if raw else None
        should_escalate = escalation_enabled and decide_escalation(updated.conformance_state, confidence)

        if not should_escalate:
            metrics.bundles_judged_without_codex += 1
            continue

        if cost_ceiling_usd is not None and total_codex_cost >= cost_ceiling_usd:
            metrics.codex_investigations_skipped_cost_ceiling += 1
            escalation_skip_reasons[req_id] = "cost_ceiling_reached"
            new_routed[req_id] = updated  # keep the bounded (INCONCLUSIVE/etc) verdict as final
            continue

        # Resolve the seed candidate location: the single highest-ranked
        # evidence location for this requirement (see module docstring's
        # "known architecture gap" note on requirement- vs candidate-level
        # granularity).
        ranked = rank_evidence(list(updated.evidence), project_root)
        if not ranked:
            continue
        candidate_location = ranked[0].item.location

        try:
            if pg is None:
                # Reuse the EXACT SAME compiled Slither object `run_rtf`
                # already produced via `compile_evmbench_target` (neutral
                # cwd, Foundry-autodetection-safe) instead of triggering a
                # second, independently-configured compile of the same
                # file. A second `ProgramGraph.build(entry_sol_file, ...)`
                # call here used to compile through `a4v.graph._compile`
                # directly (no neutral cwd), which let crytic-compile's
                # Foundry auto-detection fire differently and produced a
                # real, confirmed-live "stack too deep" BuildFailed on
                # canto's LendingLedger.sol that the first compile never
                # hit -- see ProgramGraph.from_slither's docstring.
                if ctx.slither is None:
                    raise RuntimeError(
                        f"no compiled Slither object available (compile_error={compile_error!r}); "
                        "cannot build a navigation graph for a target whose deterministic compile "
                        "already failed"
                    )
                pg = ProgramGraph.from_slither(ctx.slither)
            resolve_seed_node(pg, candidate_location)  # raises explicitly if unresolved/ambiguous -- fail loud, don't guess
        except Exception as e:  # noqa: BLE001 -- one requirement's graph-resolution failure must not abort the run
            escalation_skip_reasons[req_id] = f"graph_resolution_failed: {type(e).__name__}: {e}"
            metrics.bundles_judged_without_codex += 1
            new_routed[req_id] = updated
            continue

        open_questions = (raw or {}).get("first_pass", {}).get("open_questions") if raw else None
        prompt_inputs = build_codex_prompt_inputs(req_id, candidate_location, updated, project_root, open_questions)
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

    final_run = TargetRunResult(audit_id=audit_id, routed=new_routed)
    for r in final_run.routed.values():
        if r.conformance_state is not None:
            metrics.final_decisions[r.conformance_state.value] += 1

    return PipelineArtifacts(
        run=final_run, stage_metrics=metrics, raw_l8_judgments=raw_l8_judgments,
        codex_results=codex_results, escalation_skip_reasons=escalation_skip_reasons,
        codex_outcome_reasons=codex_outcome_reasons,
        total_codex_cost_usd=total_codex_cost,
    )
