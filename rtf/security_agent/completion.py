"""Mechanical completion and PASS-discipline checks for the kernel.

These checks operate on structured state, never on whether free-form prose
"sounds convincing". FAIL/NOT_APPLICABLE remain evidence-gated by the CEIV
schema; PASS additionally requires an actual falsification attempt and no
open hypothesis or unresolved question.
"""
from __future__ import annotations

from dataclasses import dataclass

from rtf.l11_investigation_grouping.taxonomy import ReasoningCategory
from rtf.security_agent.state import (
    ClusterInvestigationState, HypothesisStatus, RequirementResolution,
)


@dataclass(frozen=True)
class CompletionCheck:
    ready: bool
    blocking_reasons: tuple[str, ...]


_SHAPE_TERMS: dict[ReasoningCategory, tuple[tuple[str, ...], ...]] = {
    ReasoningCategory.INPUT_DOMAIN_VALIDATION: (
        ("invalid", "malformed", "boundary", "out of range", "zero", "negative"),
    ),
    ReasoningCategory.ACCESS_PRIVILEGE_CONTROL: (
        ("unauthorized", "non-owner", "non owner", "least privileged", "unprivileged"),
    ),
    ReasoningCategory.GAS_DOS_STATE_GROWTH: (
        ("grow", "growth", "unbounded"), ("prun", "remov", "delete", "bounded"),
        ("iterat", "loop", "enumerat"),
    ),
}

_UNRESOLVED_RESULT_MARKERS = ("pending", "not yet", "unknown", "tbd", "to be determined")


def _resolved_counterexample_attempts(records: list[str]) -> list[str]:
    resolved = []
    for record in records:
        result = record.rsplit("; result:", 1)[-1].strip().lower()
        if len(result) >= 15 and not any(marker in result for marker in _UNRESOLVED_RESULT_MARKERS):
            resolved.append(record)
    return resolved


def _category(value: ReasoningCategory | str | None) -> ReasoningCategory | None:
    if value is None:
        return None
    try:
        return value if isinstance(value, ReasoningCategory) else ReasoningCategory(value)
    except ValueError:
        return None


def check_property_completion(
    state: ClusterInvestigationState, property_id: str,
    reasoning_category: ReasoningCategory | str | None = None,
) -> CompletionCheck:
    req = state.requirement_states[property_id]
    reasons: list[str] = []
    assessment = req.final_assessment
    if assessment is None:
        reasons.append("missing_final_assessment")
    elif not assessment.evidence_ids:
        reasons.append("missing_cited_evidence")
    elif not assessment.hypothesis_ids:
        reasons.append("missing_cited_hypothesis")

    if req.status != RequirementResolution.PASS:
        return CompletionCheck(not reasons, tuple(reasons))

    resolved_attempts = _resolved_counterexample_attempts(req.counterexample_attempts)
    if not req.counterexample_attempts:
        reasons.append("pass_without_counterexample_attempt")
    elif not resolved_attempts:
        reasons.append("pass_without_resolved_counterexample_result")
    valid_tool_ids = {call.id for call in state.tool_history}
    for evidence_id in assessment.evidence_ids if assessment else ():
        evidence = state.evidence.get(evidence_id)
        if evidence is None or not evidence.tool_call_id or evidence.tool_call_id not in valid_tool_ids:
            reasons.append(f"pass_evidence_not_from_recorded_tool:{evidence_id}")
    if req.unresolved_questions or state.unresolved_questions:
        reasons.append("pass_with_unresolved_questions")
    for hypothesis_id in req.hypothesis_ids:
        hypothesis = state.hypotheses.get(hypothesis_id)
        if hypothesis is None:
            reasons.append(f"unknown_hypothesis:{hypothesis_id}")
        elif hypothesis.status in (HypothesisStatus.OPEN, HypothesisStatus.INCONCLUSIVE):
            reasons.append(f"pass_with_unresolved_hypothesis:{hypothesis_id}")

    category = _category(reasoning_category)
    required_groups = _SHAPE_TERMS.get(category, ())
    attempts = " ".join(resolved_attempts).lower()
    for group in required_groups:
        if not any(term in attempts for term in group):
            reasons.append(f"missing_shape_counterexample:{category.value}:{'/'.join(group)}")

    return CompletionCheck(not reasons, tuple(dict.fromkeys(reasons)))


def cluster_can_conclude(
    state: ClusterInvestigationState,
    reasoning_categories_by_property: dict[str, ReasoningCategory | str | None] | None = None,
) -> CompletionCheck:
    categories = reasoning_categories_by_property or {}
    reasons: list[str] = []
    for property_id in state.property_ids:
        result = check_property_completion(state, property_id, categories.get(property_id))
        reasons.extend(f"{property_id}:{reason}" for reason in result.blocking_reasons)
    return CompletionCheck(not reasons, tuple(reasons))
