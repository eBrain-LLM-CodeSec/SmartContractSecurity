"""Phase 4: fine-grained applicability/coverage telemetry.

The pre-existing telemetry (`ApplicabilityState` x `ConformanceState`,
`escalation_skip_reasons`, `codex_outcome_reasons`, `graph_seed_resolved`)
already carries enough raw signal to distinguish SEVERAL genuinely
different "why did this requirement end up here" stories, but nothing
in `pipeline_e2e.py`/`report_generator.py` actually surfaces that
distinction anywhere -- a FAIL/PASS/INCONCLUSIVE final state looks
identical whether the agent explored the exact right function and
reasoned about it, whether it never got past a crash, or whether the
requirement was only ever investigated once at a generic, unscoped
location even though its own evidence pointed at several distinct sites.

This module adds ONE new, purely-derived (no pipeline control-flow
changes) classification, `CoverageState`, computed from data
`run_pipeline_e2e`/`_run_escalations_concurrent` already produce (plus
the ranked-evidence locations, recomputed the same way
`codex_bridge`/`pipeline_e2e` already do) -- a strict readout of EXISTING
telemetry, not a new judgment mechanism.

Mechanically distinguishes 6 states (the taxonomy named in
`RTF_ETHTRUST_TRANSLATION_AUDIT.md`'s follow-on work):

  NEVER_CONSIDERED         -- not in `routed` at all, or applicable but
                               never reached escalation (no evidence /
                               operational failure before the agent step)
  NOT_APPLICABLE            -- applicability_state == NOT_APPLICABLE
  EXPLORATION_FAILED        -- escalated but the agent investigation
                               itself never completed meaningfully
                               (timeout / crash / no parseable decision)
  APPLIED_TO_WRONG_FUNCTIONS -- escalated, agent completed, but the ONE
                               seed location this requirement resolved to
                               never actually resolved on the code graph
                               (graph_seed_resolved=False for a non-empty
                               candidate_location)
  APPLIED_ONCE_GLOBALLY      -- escalated, agent completed at a resolved
                               location, BUT the requirement's own ranked
                               evidence spans MORE THAN ONE distinct
                               location and only one was ever
                               investigated -- real, precise under-
                               coverage, not merely "this requirement
                               only ever had one relevant site" (that
                               case is NOT flagged here, see below)
  REASONING_FAILED           -- everything mechanical worked: applicable,
                               escalated, agent completed, seed resolved,
                               and either only one location ever existed
                               (nothing to under-cover) or multiple
                               locations were each actually investigated.
                               NOT a claim the reasoning WAS wrong -- the
                               name reflects that if this outcome turns
                               out wrong against ground truth, the cause
                               must be reasoning quality, since every
                               mechanical precondition was met. This is
                               the honest "nothing else explains it"
                               bucket, never asserted as a positive
                               finding on its own.

Precedence matters (checked in the order above) -- e.g. a crashed
investigation is EXPLORATION_FAILED even if its evidence also spanned
multiple locations, since the crash is the more specific, more useful
explanation of what actually happened.
"""
from __future__ import annotations

from enum import Enum

from rtf.l10_property_derivation.derive_investigations import distinct_locations
from rtf.l12_evaluation.evidence_ranking import rank_evidence
from rtf.l12_evaluation.metrics import ApplicabilityState, RoutedRequirementResult


class CoverageState(str, Enum):
    NEVER_CONSIDERED = "NEVER_CONSIDERED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    EXPLORATION_FAILED = "EXPLORATION_FAILED"
    APPLIED_TO_WRONG_FUNCTIONS = "APPLIED_TO_WRONG_FUNCTIONS"
    APPLIED_ONCE_GLOBALLY = "APPLIED_ONCE_GLOBALLY"
    REASONING_FAILED = "REASONING_FAILED"


_EXPLORATION_FAILURE_REASON_PREFIXES = ("codex_timeout", "codex_no_decision", "codex_unknown_decision")


def classify_coverage(
    req_id: str,
    routed: dict[str, RoutedRequirementResult],
    escalation_skip_reasons: dict[str, str],
    codex_outcome_reasons: dict[str, str],
    graph_seed_resolved: dict[str, bool],
    instance_results: dict[str, list] | None = None,
    project_root=None,
) -> CoverageState:
    """Classifies ONE requirement's coverage outcome for ONE entry, from
    telemetry a completed `run_pipeline_e2e` call already produced (see
    `PipelineArtifacts`). `instance_results`/`project_root` are only
    needed to compute the APPLIED_ONCE_GLOBALLY distinction precisely --
    both are optional (default to an empty dict / None) and safely
    degrade to skipping that specific distinction (falling through to
    REASONING_FAILED) when omitted, rather than crashing -- a caller
    inspecting only the cheaper telemetry (no instance data available,
    e.g. from an older saved stage.json) still gets a meaningful,
    honest answer for the other 5 states.
    """
    instance_results = instance_results or {}
    result = routed.get(req_id)
    if result is None:
        return CoverageState.NEVER_CONSIDERED
    if result.applicability_state == ApplicabilityState.NOT_APPLICABLE:
        return CoverageState.NOT_APPLICABLE
    if result.conformance_state is None:
        # Applicable, but never even reached escalation -- e.g. no
        # evidence at all, or an operational failure (UNSUPPORTED_
        # ANALYZER / compile error) upstream of the agent step. This is
        # the SAME "never actually looked at it" story as not being in
        # `routed` at all, just discovered one layer later.
        return CoverageState.NEVER_CONSIDERED

    skip_reason = escalation_skip_reasons.get(req_id, "")
    outcome_reason = codex_outcome_reasons.get(req_id, "")
    if "codex_invocation_crashed" in skip_reason or any(
        outcome_reason.startswith(p) for p in _EXPLORATION_FAILURE_REASON_PREFIXES
    ):
        return CoverageState.EXPLORATION_FAILED

    if "graph_seed_not_resolved" in skip_reason and graph_seed_resolved.get(req_id) is False:
        return CoverageState.APPLIED_TO_WRONG_FUNCTIONS

    instances = instance_results.get(req_id)
    n_investigated_locations = len(instances) if instances else 1
    if n_investigated_locations <= 1 and result.evidence and project_root is not None:
        ranked = rank_evidence(list(result.evidence), project_root)
        n_distinct_locations = len(distinct_locations([r.item.location for r in ranked], max_locations=99))
        if n_distinct_locations > 1:
            return CoverageState.APPLIED_ONCE_GLOBALLY

    return CoverageState.REASONING_FAILED


def classify_all(
    routed: dict[str, RoutedRequirementResult],
    escalation_skip_reasons: dict[str, str],
    codex_outcome_reasons: dict[str, str],
    graph_seed_resolved: dict[str, bool],
    instance_results: dict[str, list] | None = None,
    project_root=None,
) -> dict[str, CoverageState]:
    """Convenience: classify every req_id in `routed` at once."""
    return {
        req_id: classify_coverage(
            req_id, routed, escalation_skip_reasons, codex_outcome_reasons,
            graph_seed_resolved, instance_results, project_root,
        )
        for req_id in routed
    }
