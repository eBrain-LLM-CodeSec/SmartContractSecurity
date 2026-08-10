"""Phase 6 of the grouped-investigation architecture: a deterministic
investigation-complexity score, plus configurable cluster budgets.

Complexity is computed at the CLUSTER level (not per-property): "how
hard would investigating this GROUP of properties together be" is
inherently a property of the group, not any one member -- a single
property has no complexity of its own until it's being considered
alongside others for one shared investigation. `PropertyMetadata.
estimated_complexity` therefore stays `None` even after this phase (as
documented in `property_metadata.py`); this module attaches complexity
to `Cluster` objects instead, via `with_complexity`.

Every input to the score is either already computed by Phase 4's engine
(`Cluster.estimated_context_size`) or directly countable from the
cluster's own members' `PropertyMetadata` -- no EVMbench-derived signal
anywhere. Weights are declared, not fitted; Phase 13's controlled
cluster-size study is where their real-world effect gets measured, not
assumed here.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from rtf.l11_investigation_grouping.grouping_engine import Cluster
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.l11_investigation_grouping.taxonomy import ReasoningCategory

# Reasoning categories whose own text (per RTF_INVESTIGATION_GROUPING_
# TAXONOMY.md) inherently requires reasoning about a SEQUENCE of states/
# events over time, not a single-point-in-time check -- block/epoch
# semantics, MEV/ordering, external-call-interaction ordering (CEI).
_TEMPORAL_REASONING_CATEGORIES = frozenset({
    ReasoningCategory.TIME_BLOCK_MEV_ORDERING,
    ReasoningCategory.EXTERNAL_CALL_INTERACTION,
    ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,  # timelock/revocation are inherently state-transition properties
})

# Categories whose reasoning is fundamentally about boundary/arithmetic
# correctness -- per the taxonomy doc's own category definitions.
_ARITHMETIC_REASONING_CATEGORIES = frozenset({
    ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS,
    ReasoningCategory.INPUT_DOMAIN_VALIDATION,
    ReasoningCategory.GAS_DOS_STATE_GROWTH,
})

# Declared, not fitted -- see module docstring. Each represents "how much
# this one factor should move the score," roughly calibrated so that a
# single dimension growing noticeably (e.g. 5 extra properties, 5 extra
# contracts) has a comparable effect to another dimension doing the same
# -- not claimed as validated against any real outcome.
_WEIGHT_PROPERTIES = 1.0
_WEIGHT_FILES = 1.5
_WEIGHT_FUNCTIONS = 1.0
_WEIGHT_CONTRACTS = 2.5
"""Contracts weighted heaviest of the count-based factors: reasoning
across multiple contracts (trust boundaries, cross-contract call
semantics) is qualitatively harder than reasoning across multiple
functions in the SAME contract."""
_WEIGHT_STATE_VARIABLES = 0.5
_WEIGHT_CROSS_CONTRACT_DEPENDENCIES = 3.0
"""Heaviest single weight -- a property whose callgraph genuinely
crosses a contract boundary (not just co-located in the same cluster,
but a real caller/callee edge into another contract) is the single
strongest complexity signal this module can compute without a live,
much deeper call-graph traversal (out of scope for this pass)."""
_WEIGHT_SOURCE_CONTEXT = 0.3
_WEIGHT_TEMPORAL_REASONING = 2.0
_WEIGHT_ARITHMETIC_REASONING = 2.0


@dataclass(frozen=True)
class ComplexityBreakdown:
    num_properties: int
    num_files: int
    num_functions: int
    num_contracts: int
    num_state_variables: int
    num_cross_contract_dependencies: int
    """Count of DISTINCT contracts referenced by any member's
    `callgraph_neighbors` that are NOT among the cluster's own
    `target_contract` set -- a real, callgraph-derived cross-contract
    signal (not just "more than one target_contract in the cluster",
    which `num_contracts` already covers)."""
    source_context_size: int
    """Reuses `Cluster.estimated_context_size` directly -- not
    recomputed, so the two never silently drift apart."""
    requires_temporal_reasoning: bool
    requires_arithmetic_reasoning: bool
    score: float

    def as_dict(self) -> dict:
        return {
            "num_properties": self.num_properties, "num_files": self.num_files,
            "num_functions": self.num_functions, "num_contracts": self.num_contracts,
            "num_state_variables": self.num_state_variables,
            "num_cross_contract_dependencies": self.num_cross_contract_dependencies,
            "source_context_size": self.source_context_size,
            "requires_temporal_reasoning": self.requires_temporal_reasoning,
            "requires_arithmetic_reasoning": self.requires_arithmetic_reasoning,
            "score": self.score,
        }


def compute_complexity(cluster: Cluster, properties_by_id: dict[str, PropertyMetadata]) -> ComplexityBreakdown:
    members = [properties_by_id[pid] for pid in cluster.property_ids]

    files = {f for m in members for f in m.relevant_files}
    functions = {f"{m.target_contract}.{m.target_function}" for m in members if m.target_contract and m.target_function}
    contracts = {m.target_contract for m in members if m.target_contract}
    state_vars = {v for m in members for v in m.relevant_state_variables}

    cross_contract_targets: set[str] = set()
    for m in members:
        for neighbor in m.callgraph_neighbors:
            # Node ids are "fn::Contract.function(...)" (see
            # graph_navigation.py's own documented format) -- extract the
            # contract name and check it's outside this cluster's own set.
            if neighbor.startswith("fn::"):
                rest = neighbor[len("fn::"):]
                neighbor_contract = rest.split(".", 1)[0] if "." in rest else None
                if neighbor_contract and neighbor_contract not in contracts:
                    cross_contract_targets.add(neighbor_contract)

    categories = {m.reasoning_category for m in members if m.reasoning_category is not None}
    requires_temporal = bool(categories & _TEMPORAL_REASONING_CATEGORIES)
    requires_arithmetic = bool(categories & _ARITHMETIC_REASONING_CATEGORIES)

    score = (
        _WEIGHT_PROPERTIES * len(members)
        + _WEIGHT_FILES * len(files)
        + _WEIGHT_FUNCTIONS * len(functions)
        + _WEIGHT_CONTRACTS * len(contracts)
        + _WEIGHT_STATE_VARIABLES * len(state_vars)
        + _WEIGHT_CROSS_CONTRACT_DEPENDENCIES * len(cross_contract_targets)
        + _WEIGHT_SOURCE_CONTEXT * cluster.estimated_context_size
        + (_WEIGHT_TEMPORAL_REASONING if requires_temporal else 0.0)
        + (_WEIGHT_ARITHMETIC_REASONING if requires_arithmetic else 0.0)
    )

    return ComplexityBreakdown(
        num_properties=len(members), num_files=len(files), num_functions=len(functions),
        num_contracts=len(contracts), num_state_variables=len(state_vars),
        num_cross_contract_dependencies=len(cross_contract_targets),
        source_context_size=cluster.estimated_context_size,
        requires_temporal_reasoning=requires_temporal, requires_arithmetic_reasoning=requires_arithmetic,
        score=score,
    )


def with_complexity(cluster: Cluster, properties_by_id: dict[str, PropertyMetadata]) -> Cluster:
    """Returns a copy of `cluster` with `estimated_complexity` populated
    (Phase 4 always leaves it None -- this is the dedicated Phase 6 step
    that fills it in, kept as an explicit, separate call rather than
    baked into `cluster_properties` itself, so complexity scoring can
    evolve independently of the clustering algorithm)."""
    breakdown = compute_complexity(cluster, properties_by_id)
    return replace(cluster, estimated_complexity=breakdown.score)


@dataclass(frozen=True)
class ClusterBudget:
    """Configurable limits -- NONE of these are claimed as an
    experimentally-validated optimum (Phase 13's job); these are
    starting, deliberately permissive defaults that at least prevent a
    pathological giant cluster."""
    max_properties_per_cluster: int | None = None
    max_files_per_cluster: int | None = None
    max_context_tokens: int | None = None
    """NOT wired to a real token count in this phase -- Phase 12's
    caching/token instrumentation is where a real tokenizer-backed count
    would come from. When set here, it's compared against
    `Cluster.estimated_context_size` as an approximate STAND-IN (the same
    proxy the engine's own `max_context_size` already uses), not an
    actual token count -- documented so a caller doesn't mistake this
    field for a precise budget."""
    max_complexity_score: float | None = None


DEFAULT_BUDGET = ClusterBudget()
"""No limits at all -- an explicit opt-in is required to enforce any
budget, matching every other Phase 1-5 mechanism's "off by default,
additive" convention."""


def budget_violations(cluster: Cluster, properties_by_id: dict[str, PropertyMetadata], budget: ClusterBudget) -> list[str]:
    """Returns the list of SPECIFIC violated-limit names (empty if none)
    -- never a bare bool, so a caller (Phase 10's splitting logic) knows
    exactly which dimension to address, not just that "something" is too
    big.
    """
    violations: list[str] = []
    members = [properties_by_id[pid] for pid in cluster.property_ids]

    if budget.max_properties_per_cluster is not None and len(members) > budget.max_properties_per_cluster:
        violations.append("max_properties_per_cluster")

    files = {f for m in members for f in m.relevant_files}
    if budget.max_files_per_cluster is not None and len(files) > budget.max_files_per_cluster:
        violations.append("max_files_per_cluster")

    if budget.max_context_tokens is not None and cluster.estimated_context_size > budget.max_context_tokens:
        violations.append("max_context_tokens")

    if budget.max_complexity_score is not None:
        breakdown = compute_complexity(cluster, properties_by_id)
        if breakdown.score > budget.max_complexity_score:
            violations.append("max_complexity_score")

    return violations


def within_budget(cluster: Cluster, properties_by_id: dict[str, PropertyMetadata], budget: ClusterBudget) -> bool:
    return not budget_violations(cluster, properties_by_id, budget)
