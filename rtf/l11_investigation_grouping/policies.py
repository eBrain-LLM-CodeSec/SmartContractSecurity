"""Phase 5 of the grouped-investigation architecture: named grouping
policies (G0/G1/G2/G3), each a specific parameterization of Phase 4's
generic `cluster_properties` engine -- not a separate implementation
per policy.

- **G0_UNGROUPED**: the reference baseline (Phase 1). Every property is
  its own cluster. Implemented as `cluster_properties(..., min_score_to_
  group=inf)`, which structurally can never merge anything (no finite
  score exceeds infinity) -- reuses the same tested clustering code path
  rather than a separate "just don't cluster" branch, so G0's output
  shape is guaranteed identical to every other policy's.
- **G1_CONSERVATIVE**: "Group only if: same EthTrust requirement, same
  semantic reasoning category, same contract/component" -- a strict
  boolean AND the additive scoring engine alone cannot faithfully
  express (other signal combinations could reach the same numeric
  total), so this is built with `hard_gate` (Phase 4's own extension
  point for exactly this case), not a score threshold alone.
- **G2_CONTEXT_AWARE**: "Allow grouping across functions/contracts when
  properties share substantial state/types/callgraph/interfaces/
  semantic reasoning" -- the engine's own default scoring behavior,
  unconstrained by a hard gate, with a generous (but not unbounded)
  cluster-size cap.
- **G3_ADAPTIVE**: context-aware grouping (same scoring as G2) PLUS a
  context-size budget (`max_context_size`) that dynamically limits how
  large a cluster can grow based on how much material it would actually
  need to carry, rather than a fixed property count. This is a genuine,
  working adaptivity mechanism built from what Phase 4 already computes
  (`estimated_context_size`) -- Phase 6's dedicated complexity scorer
  will likely refine this budget function later without changing G3's
  identity or its callers.

All four policies are selectable by configuration
(`apply_grouping_policy(properties, policy_name)`); none is hardcoded as
"the" default anywhere in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rtf.l11_investigation_grouping.grouping_engine import STRONG_POSITIVE_WEIGHT, Cluster, cluster_properties
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.l11_investigation_grouping.run_metadata import (
    GROUPING_POLICY_G0_UNGROUPED, GROUPING_POLICY_G1_CONSERVATIVE,
    GROUPING_POLICY_G2_CONTEXT_AWARE, GROUPING_POLICY_G3_ADAPTIVE,
)

# Generous but not unbounded -- a real safety net against a pathological
# input (e.g. every property sharing the same requirement_id) producing
# one giant cluster with no cap at all. Not claimed as an experimentally
# optimal value; Phase 13's controlled cluster-size study is where that
# gets measured. This is a starting default, deliberately conservative.
_DEFAULT_MAX_CLUSTER_SIZE = 8

# A default context-size budget for G3, in the same units as
# `Cluster.estimated_context_size` (count of distinct files + state
# variables + callgraph neighbors + candidate locations across a
# cluster's members) -- not a token count. Same "starting default, not
# yet experimentally tuned" caveat as _DEFAULT_MAX_CLUSTER_SIZE.
_DEFAULT_MAX_CONTEXT_SIZE = 20


def g1_hard_gate(a: PropertyMetadata, b: PropertyMetadata) -> bool:
    """G1_CONSERVATIVE's own merge rule, verbatim from the plan: same
    requirement AND same reasoning category AND same contract/component.
    Both category and contract must be non-None -- two properties with
    unknown category/contract never satisfy "same X" (an unknown value
    matching another unknown value is not evidence of relatedness)."""
    return (
        a.requirement_id == b.requirement_id
        and a.reasoning_category is not None
        and a.reasoning_category == b.reasoning_category
        and a.target_contract is not None
        and a.target_contract == b.target_contract
    )


@dataclass(frozen=True)
class GroupingPolicySpec:
    name: str
    min_score_to_group: float
    max_cluster_size: int | None
    max_context_size: int | None
    hard_gate: Callable[[PropertyMetadata, PropertyMetadata], bool] | None


POLICIES: dict[str, GroupingPolicySpec] = {
    GROUPING_POLICY_G0_UNGROUPED: GroupingPolicySpec(
        name=GROUPING_POLICY_G0_UNGROUPED, min_score_to_group=float("inf"),
        max_cluster_size=1, max_context_size=None, hard_gate=None,
    ),
    GROUPING_POLICY_G1_CONSERVATIVE: GroupingPolicySpec(
        name=GROUPING_POLICY_G1_CONSERVATIVE, min_score_to_group=STRONG_POSITIVE_WEIGHT,
        max_cluster_size=_DEFAULT_MAX_CLUSTER_SIZE, max_context_size=None, hard_gate=g1_hard_gate,
    ),
    GROUPING_POLICY_G2_CONTEXT_AWARE: GroupingPolicySpec(
        name=GROUPING_POLICY_G2_CONTEXT_AWARE, min_score_to_group=STRONG_POSITIVE_WEIGHT,
        max_cluster_size=_DEFAULT_MAX_CLUSTER_SIZE, max_context_size=None, hard_gate=None,
    ),
    GROUPING_POLICY_G3_ADAPTIVE: GroupingPolicySpec(
        name=GROUPING_POLICY_G3_ADAPTIVE, min_score_to_group=STRONG_POSITIVE_WEIGHT,
        max_cluster_size=None, max_context_size=_DEFAULT_MAX_CONTEXT_SIZE, hard_gate=None,
    ),
}


def apply_grouping_policy(properties: list[PropertyMetadata], policy_name: str) -> list[Cluster]:
    """The one entry point every later phase (planner, ablation study,
    cluster-size study) should call -- selects a named policy's
    parameterization and runs it through the shared engine. Raises
    KeyError for an unknown policy name (never silently falls back to a
    default -- a typo'd policy name is a caller bug worth surfacing)."""
    spec = POLICIES[policy_name]
    return cluster_properties(
        properties, min_score_to_group=spec.min_score_to_group,
        max_cluster_size=spec.max_cluster_size, max_context_size=spec.max_context_size,
        hard_gate=spec.hard_gate,
    )
