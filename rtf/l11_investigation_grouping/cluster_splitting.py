"""Phase 10 of the grouped-investigation architecture: automatic cluster
splitting when an investigation shows signs the grouping was too
aggressive.

Per the plan: if a cluster investigation exceeds its context budget,
fails structured output, omits properties, returns weak/no evidence,
fails counterexample requirements, or appears to conflate obligations --
split the cluster (e.g. `[P1..P6] -> [P1,P2,P3] + [P4,P5,P6]`), record
why, and never silently lose a property.

Two pieces: `detect_split_reason` (should THIS cluster be split, and
why -- checked against Phase 6's budget, Phase 9's completeness/
counterexample/duplicated-reasoning signals) and `split_cluster` (the
actual, deterministic bisection). Splitting produces exactly 2 halves
per call; a caller that needs to split further (a half still too big)
calls this again on that half -- kept simple and composable rather than
baking recursion into one function.
"""
from __future__ import annotations

from dataclasses import dataclass

from rtf.l11_investigation_grouping.cluster_response_validation import ClusterValidationResult, PropertyVerdict
from rtf.l11_investigation_grouping.complexity import ClusterBudget, budget_violations
from rtf.l11_investigation_grouping.grouping_engine import Cluster, _estimate_context_size, _shared_context_for
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata


@dataclass(frozen=True)
class SplitReason:
    should_split: bool
    reason_code: str | None
    """One of: "exceeds_context_budget", "incomplete_response",
    "insufficient_counterexample_rigor", "conflated_obligations"
    (duplicated reasoning across properties) -- None iff should_split is
    False."""
    detail: str | None


def detect_split_reason(
    cluster: Cluster,
    properties_by_id: dict[str, PropertyMetadata],
    budget: ClusterBudget | None = None,
    validation_result: ClusterValidationResult | None = None,
    resolved_verdicts: dict[str, PropertyVerdict] | None = None,
) -> SplitReason:
    """Checked in a fixed precedence order -- the FIRST applicable
    reason is returned (a cluster can have more than one problem at
    once; the caller gets one clear, actionable reason per split
    decision, not a combined list to disentangle). Every argument beyond
    `cluster`/`properties_by_id` is optional: a caller checking budget
    BEFORE ever invoking Codex only has `budget` to pass; a caller
    checking a real response has `validation_result`/`resolved_verdicts`
    too. Returns `should_split=False` if nothing given signals a problem
    (never assumes a split is needed absent real evidence).
    """
    if budget is not None:
        violations = budget_violations(cluster, properties_by_id, budget)
        if violations:
            return SplitReason(True, "exceeds_context_budget", f"violated: {', '.join(violations)}")

    if validation_result is not None and not validation_result.complete:
        return SplitReason(True, "incomplete_response", "; ".join(validation_result.issues) or "response was incomplete")

    if resolved_verdicts is not None:
        insufficient = [pid for pid, v in resolved_verdicts.items()
                         if v.reason and v.reason.startswith("insufficient_reasoning_rigor")]
        if insufficient:
            return SplitReason(True, "insufficient_counterexample_rigor",
                                f"properties with insufficient counterexample rigor: {sorted(insufficient)}")

    if validation_result is not None and validation_result.duplicated_reasoning_groups:
        return SplitReason(True, "conflated_obligations",
                            f"identical reasoning across properties: {validation_result.duplicated_reasoning_groups}")

    return SplitReason(False, None, None)


def split_cluster(cluster: Cluster, properties_by_id: dict[str, PropertyMetadata]) -> tuple[Cluster, Cluster]:
    """Deterministic bisection: sorts `cluster.property_ids`, splits into
    two halves (the first half gets the extra member when the count is
    odd), and rebuilds each half as its own real `Cluster` (recomputed
    `shared_context`/`estimated_context_size` from just that half's
    members -- NOT a stale copy of the original's). `grouping_reason` on
    each half is empty for a size-1 result (matches
    `grouping_engine.cluster_properties`'s own singleton convention) or
    a note that this half resulted from a split, for size>1.

    Raises ValueError if `cluster` has fewer than 2 properties (nothing
    to split). Every property from the original appears in EXACTLY one
    resulting half -- verified directly by tests, not just asserted
    here.
    """
    ids = sorted(cluster.property_ids)
    if len(ids) < 2:
        raise ValueError(f"cannot split a cluster with fewer than 2 properties (has {len(ids)}: {ids})")

    midpoint = (len(ids) + 1) // 2  # first half gets the extra member on an odd count
    first_ids, second_ids = tuple(ids[:midpoint]), tuple(ids[midpoint:])

    def _build(pids: tuple[str, ...], suffix: str) -> Cluster:
        members = [properties_by_id[pid] for pid in pids]
        reason = (f"split_from:{cluster.cluster_id}",) if len(pids) > 1 else ()
        return Cluster(
            cluster_id=f"{cluster.cluster_id}_{suffix}", property_ids=pids, grouping_reason=reason,
            shared_context=_shared_context_for(members), estimated_context_size=_estimate_context_size(members),
        )

    return _build(first_ids, "a"), _build(second_ids, "b")
