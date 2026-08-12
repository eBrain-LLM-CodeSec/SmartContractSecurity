"""Phase 4 of the grouped-investigation architecture: a deterministic,
explainable clustering engine over `PropertyMetadata`.

Explicitly NOT LLM-based (per the plan's own instruction: "Do NOT start
with LLM clustering"). Two stages:

1. `compatibility_score(a, b)` -- a pairwise, fully-explainable
   compatibility score between two properties, built from the strong/
   weak positive and strong negative signals the plan specifies. Every
   contributing signal is named in the returned `reasons` list -- no
   opaque scalar with no explanation.
2. `cluster_properties(...)` -- greedy agglomerative clustering over
   those pairwise scores: repeatedly merge the highest-scoring
   still-mergeable pair, subject to a hard veto (an unsafe category
   combination, from `taxonomy.is_unsafe_combination`, blocks a merge
   unconditionally regardless of score) and an optional cluster-size cap.

This module defines the SCORING/CLUSTERING MECHANISM only, parameterized
by weights and a merge threshold -- it does not itself decide what a
"good" threshold is. Phase 5's G1/G2/G3 policies are specific weight/
threshold PRESETS built on top of this engine, not separate
implementations. Phase 6's complexity/context-budget enforcement is a
further, separate cap layered on top of `max_cluster_size` here, not
yet implemented in this module.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata, shares_callgraph_region
from rtf.l11_investigation_grouping.taxonomy import is_unsafe_combination

# Signal weights -- deliberately simple, additive, and fully documented;
# not tuned against any benchmark outcome. Each weight reflects how
# STRONGLY the plan's own signal categorization (strong positive / weak
# positive / strong negative) should move the score, not a fitted value.
STRONG_POSITIVE_WEIGHT = 3.0
WEAK_POSITIVE_WEIGHT = 1.0
STRONG_NEGATIVE_WEIGHT = 4.0
"""Outweighs a single strong positive signal on its own -- an unrelated-
contracts-no-shared-context signal should not be overridden by e.g. two
properties merely sharing a reasoning category."""

HARD_VETO_SCORE = float("-inf")


@dataclass(frozen=True)
class CompatibilityResult:
    score: float
    reasons: tuple[str, ...]
    hard_veto: bool


def compatibility_score(a: PropertyMetadata, b: PropertyMetadata) -> CompatibilityResult:
    """Symmetric (compatibility_score(a, b) == compatibility_score(b, a)
    up to reason ordering) pairwise compatibility between two properties.
    """
    if a.property_id == b.property_id:
        return CompatibilityResult(HARD_VETO_SCORE, ("same_property_id",), True)

    if a.reasoning_category is not None and b.reasoning_category is not None:
        if is_unsafe_combination({a.reasoning_category, b.reasoning_category}):
            return CompatibilityResult(HARD_VETO_SCORE, ("unsafe_category_combination",), True)

    score = 0.0
    reasons: list[str] = []

    def strong(condition: bool, reason: str) -> None:
        nonlocal score
        if condition:
            score += STRONG_POSITIVE_WEIGHT
            reasons.append(reason)

    def weak(condition: bool, reason: str) -> None:
        nonlocal score
        if condition:
            score += WEAK_POSITIVE_WEIGHT
            reasons.append(reason)

    # --- strong positive signals ---
    strong(a.requirement_id == b.requirement_id, "same_requirement")
    strong(a.reasoning_category is not None and a.reasoning_category == b.reasoning_category, "same_reasoning_category")
    strong(bool(a.target_contract) and a.target_contract == b.target_contract, "same_contract")
    strong(bool(set(a.relevant_state_variables) & set(b.relevant_state_variables)), "shared_state_variables")
    strong(bool(set(a.relevant_types) & set(b.relevant_types)), "shared_types")
    strong(bool(set(a.relevant_constants) & set(b.relevant_constants)), "shared_constants")
    shared_callgraph_region = shares_callgraph_region(a, b)
    strong(shared_callgraph_region, "same_callgraph_region")
    strong(bool(set(a.candidate_locations) & set(b.candidate_locations)), "overlapping_candidate_locations")

    # --- weak positive signals ---
    weak(bool(set(a.relevant_files) & set(b.relevant_files)), "source_proximity_same_file")
    weak(bool(set(a.inheritance_context) & set(b.inheritance_context)), "same_inheritance_hierarchy")
    weak(bool(a.relevant_symbols) and bool(set(a.relevant_symbols) & set(b.relevant_symbols)), "shared_symbols")

    # --- strong negative signals ---
    # Unrelated contracts with genuinely NO shared dependency/context --
    # only penalized if nothing else above already found a connection
    # (an explicit-veto-free "these two share literally nothing" case).
    both_contracts_known = bool(a.target_contract) and bool(b.target_contract)
    different_contracts = both_contracts_known and a.target_contract != b.target_contract
    no_shared_context = not any([
        set(a.relevant_state_variables) & set(b.relevant_state_variables),
        set(a.relevant_files) & set(b.relevant_files),
        set(a.inheritance_context) & set(b.inheritance_context),
        shared_callgraph_region,
        set(a.candidate_locations) & set(b.candidate_locations),
    ])
    if different_contracts and no_shared_context:
        score -= STRONG_NEGATIVE_WEIGHT
        reasons.append("unrelated_contracts_no_shared_context")

    return CompatibilityResult(score, tuple(reasons), False)


@dataclass(frozen=True)
class Cluster:
    cluster_id: str
    property_ids: tuple[str, ...]
    grouping_reason: tuple[str, ...]
    """Union of every pairwise reason that contributed to this cluster's
    formation -- deduped, not per-pair (see `shared_context` for the
    concrete overlapping values, not just the reason names)."""
    shared_context: dict
    """{"contracts": [...], "files": [...], "state_variables": [...],
    "reasoning_categories": [...]} -- the actual union of context values
    across this cluster's members, for the planner (Phase 7) to build a
    real cluster-context artifact from."""
    estimated_context_size: int
    """A rough, cheap proxy for how much context this cluster's
    investigation would need -- count of distinct (files + state
    variables + callgraph neighbors + candidate locations) across all
    members. NOT a token estimate (that's Phase 12's job); a monotonic,
    explainable stand-in usable for size comparisons NOW."""
    estimated_complexity: float | None = None
    """Left None -- Phase 6's dedicated complexity scorer, not computed
    here."""

    def as_dict(self) -> dict:
        return {
            "cluster_id": self.cluster_id, "property_ids": list(self.property_ids),
            "grouping_reason": list(self.grouping_reason), "shared_context": self.shared_context,
            "estimated_context_size": self.estimated_context_size,
            "estimated_complexity": self.estimated_complexity,
        }


def _shared_context_for(members: list[PropertyMetadata]) -> dict:
    return {
        "contracts": sorted({m.target_contract for m in members if m.target_contract}),
        "functions": sorted({f"{m.target_contract}.{m.target_function}" for m in members
                              if m.target_contract and m.target_function}),
        "files": sorted({f for m in members for f in m.relevant_files}),
        "state_variables": sorted({v for m in members for v in m.relevant_state_variables}),
        "reasoning_categories": sorted({m.reasoning_category.value for m in members if m.reasoning_category}),
        "requirement_ids": sorted({m.requirement_id for m in members}),
    }


def _estimate_context_size(members: list[PropertyMetadata]) -> int:
    files = {f for m in members for f in m.relevant_files}
    state_vars = {v for m in members for v in m.relevant_state_variables}
    neighbors = {n for m in members for n in m.callgraph_neighbors}
    locations = {loc for m in members for loc in m.candidate_locations}
    return len(files) + len(state_vars) + len(neighbors) + len(locations)


def cluster_properties(
    properties: list[PropertyMetadata],
    min_score_to_group: float = STRONG_POSITIVE_WEIGHT,
    max_cluster_size: int | None = None,
    max_context_size: int | None = None,
    hard_gate=None,
) -> list[Cluster]:
    """Deterministic greedy agglomerative clustering.

    Algorithm: compute every pairwise `compatibility_score`, sort
    candidate merges by score descending (ties broken by property_id for
    full reproducibility), then repeatedly merge the highest-scoring
    still-eligible pair of CLUSTERS (not just properties -- once two
    properties merge, the resulting cluster's compatibility with a third
    property is the MINIMUM pairwise score between the third property
    and every existing member, a conservative choice: a cluster is only
    as compatible with a newcomer as its weakest existing member is).
    A merge is blocked (regardless of score) if: any pairwise score
    within the resulting cluster would be a hard veto, the merge would
    exceed `max_cluster_size`, the merge's `estimated_context_size` would
    exceed `max_context_size`, or (when `hard_gate` is given) any pair
    within the resulting cluster fails `hard_gate(a, b)`.

    `min_score_to_group`: only pairs scoring at or above this threshold
    are ever considered for merging -- defaults to exactly one strong
    positive signal's worth (a single strong-positive-signal match is
    the minimum bar to even consider grouping; ties/weak-only overlap
    never merges on its own).

    `hard_gate`, when given, is an ADDITIONAL required condition
    (`Callable[[PropertyMetadata, PropertyMetadata], bool]`) checked
    alongside the score threshold, not instead of it -- both must pass.
    This is how Phase 5's G1 ("conservative": same requirement AND same
    category AND same contract, a strict boolean AND the additive score
    alone cannot faithfully express, since other signal combinations
    could reach the same numeric total) is built on top of this same
    engine rather than needing a separate implementation.

    Returns one `Cluster` per group, covering every input property
    exactly once (singletons included) -- `cluster_properties` never
    drops a property.
    """
    by_id = {p.property_id: p for p in properties}
    # Start: every property its own singleton cluster.
    clusters: list[list[str]] = [[p.property_id] for p in properties]

    # Precompute every property-pair's compatibility ONCE (O(n^2) property
    # comparisons total, not re-run on every cluster-merge iteration) --
    # the O(k^2) cluster-level loop below then does cheap dict lookups
    # instead of re-deriving PropertyMetadata comparisons from scratch
    # every time, which matters once cluster sizes grow past 1.
    pair_cache: dict[frozenset, CompatibilityResult] = {}
    ids = [p.property_id for p in properties]
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            pair_cache[frozenset((ids[i], ids[j]))] = compatibility_score(by_id[ids[i]], by_id[ids[j]])

    def pairwise_min_score(cluster_a: list[str], cluster_b: list[str]) -> tuple[float, bool, tuple[str, ...]]:
        """Conservative cross-cluster score: the MINIMUM pairwise score
        across every (member_a, member_b) pair, and True if ANY pair is
        a hard veto (a single incompatible pair anywhere blocks the
        whole merge)."""
        min_score = float("inf")
        any_veto = False
        all_reasons: set[str] = set()
        for pid_a in cluster_a:
            for pid_b in cluster_b:
                result = pair_cache[frozenset((pid_a, pid_b))]
                if result.hard_veto:
                    any_veto = True
                min_score = min(min_score, result.score)
                all_reasons.update(result.reasons)
        return min_score, any_veto, tuple(sorted(all_reasons))

    merged = True
    while merged:
        merged = False
        best_pair = None
        best_score = min_score_to_group - 1e-9  # must be >= threshold to merge
        best_reasons: tuple[str, ...] = ()
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                if max_cluster_size is not None and len(clusters[i]) + len(clusters[j]) > max_cluster_size:
                    continue
                score, veto, reasons = pairwise_min_score(clusters[i], clusters[j])
                if veto:
                    continue
                if hard_gate is not None and not all(
                    hard_gate(by_id[pid_a], by_id[pid_b])
                    for pid_a in clusters[i] for pid_b in clusters[j]
                ):
                    continue
                if max_context_size is not None:
                    merged_members = [by_id[pid] for pid in clusters[i] + clusters[j]]
                    if _estimate_context_size(merged_members) > max_context_size:
                        continue
                if score > best_score or (
                    score == best_score and best_pair is not None
                    and (clusters[i][0], clusters[j][0]) < (clusters[best_pair[0]][0], clusters[best_pair[1]][0])
                ):
                    best_score = score
                    best_pair = (i, j)
                    best_reasons = reasons
        if best_pair is not None:
            i, j = best_pair
            new_cluster = clusters[i] + clusters[j]
            clusters = [c for k, c in enumerate(clusters) if k not in (i, j)]
            clusters.append(new_cluster)
            merged = True

    result: list[Cluster] = []
    for idx, member_ids in enumerate(sorted(clusters, key=lambda c: sorted(c)[0])):
        members = [by_id[pid] for pid in member_ids]
        result.append(Cluster(
            cluster_id=f"cluster_{idx:03d}",
            property_ids=tuple(sorted(member_ids)),
            grouping_reason=_cluster_grouping_reasons(members),
            shared_context=_shared_context_for(members),
            estimated_context_size=_estimate_context_size(members),
        ))
    return result


def _cluster_grouping_reasons(members: list[PropertyMetadata]) -> tuple[str, ...]:
    if len(members) <= 1:
        return ()
    reasons: set[str] = set()
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            reasons.update(compatibility_score(members[i], members[j]).reasons)
    return tuple(sorted(reasons))
