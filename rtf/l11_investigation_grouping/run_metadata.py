"""Phase 1 of the grouped-investigation architecture: stable run metadata.

Per the controlled-implementation-and-ablation-study plan (not "just add
clustering"): every run must record WHICH experimental configuration
produced it, so later phases (ablation, cluster-size study, Pareto
selection) can compare runs by configuration rather than by guessing
from context. This module defines that configuration surface and its
values -- it does not itself change any investigation behavior.

`GROUPING_POLICY_G0_UNGROUPED` names the CURRENT, pre-existing behavior
(one derived property -> one Codex investigation, via
`rtf.l10_property_derivation.derive_investigations.expand_investigation_
instances` when `instance_expansion_enabled=True`, or the original
1-requirement-1-investigation path when it's False) -- this is the
reference/accuracy baseline every later grouping policy is measured
against, per the plan's explicit instruction not to remove it.
`G1_CONSERVATIVE`/`G2_CONTEXT_AWARE`/`G3_ADAPTIVE` (Phase 5,
`rtf.l11_investigation_grouping.policies`) are now real, implemented
policies built on top of the Phase 4 grouping engine -- constructing a
`RunMetadata` with any of them no longer raises. A genuinely unknown
policy name still raises `ValueError` (never silently accepted).
"""
from __future__ import annotations

from dataclasses import dataclass

GROUPING_POLICY_G0_UNGROUPED = "G0_UNGROUPED"
GROUPING_POLICY_G1_CONSERVATIVE = "G1_CONSERVATIVE"
GROUPING_POLICY_G2_CONTEXT_AWARE = "G2_CONTEXT_AWARE"
GROUPING_POLICY_G3_ADAPTIVE = "G3_ADAPTIVE"

KNOWN_GROUPING_POLICIES = frozenset({
    GROUPING_POLICY_G0_UNGROUPED,
    GROUPING_POLICY_G1_CONSERVATIVE,
    GROUPING_POLICY_G2_CONTEXT_AWARE,
    GROUPING_POLICY_G3_ADAPTIVE,
})

# Policies with an actual implementation as of this phase. Referencing a
# name from KNOWN_GROUPING_POLICIES that isn't in this set is a
# legitimate future policy (safe to name in config/telemetry), but
# invoking it is not yet supported -- see run_metadata_for_policy.
IMPLEMENTED_GROUPING_POLICIES = frozenset({
    GROUPING_POLICY_G0_UNGROUPED, GROUPING_POLICY_G1_CONSERVATIVE,
    GROUPING_POLICY_G2_CONTEXT_AWARE, GROUPING_POLICY_G3_ADAPTIVE,
})
"""As of Phase 5 (`rtf.l11_investigation_grouping.policies`), all 4 named
policies have a real implementation -- see that module for each one's
exact parameterization of the Phase 4 grouping engine. Kept as a
separate, manually-updated set here (not derived by importing policies.py)
to avoid a circular import: policies.py already imports the policy name
constants from this module."""

# Bumped only when the underlying mechanism actually changes -- lets a
# later analysis distinguish "same policy name, different behavior
# because the code changed" from a genuine apples-to-apples comparison.
CURRENT_PLANNER_VERSION = "none"
"""No cluster-planning artifacts exist yet (Phase 7 of the plan) -- G0
runs have no planner at all, so this is the honest value until Phase 7
lands, not a placeholder to be silently forgotten."""

CURRENT_CONTEXT_VERSION = "none"
"""No reusable Markdown context artifacts exist yet (Phase 7) -- see
CURRENT_PLANNER_VERSION's note."""

CURRENT_INVESTIGATION_PROMPT_VERSION = "ARM_G_PROMPT_v3"
"""The frozen prompt `arm_g_codex.ARM_G_PROMPT_PATH` currently loads --
kept as a bare string (not a filesystem read) so this module has no
import-time dependency on the prompt file existing, and so a caller can
still record what generated an OLDER run's data even if the active
prompt has since moved to v4+."""


@dataclass(frozen=True)
class RunMetadata:
    """Stable, comparable-across-runs configuration record. Every field
    has an honest default matching the CURRENT (pre-grouping) pipeline
    state -- constructing this with no arguments describes exactly what
    every run before this phase actually did.
    """
    grouping_policy: str = GROUPING_POLICY_G0_UNGROUPED
    cluster_size: int | None = None
    """None for G0 (no clustering, cluster size is meaningless -- NOT
    1, which would wrongly imply a cluster-size concept was active)."""
    planner_version: str = CURRENT_PLANNER_VERSION
    context_version: str = CURRENT_CONTEXT_VERSION
    investigation_prompt_version: str = CURRENT_INVESTIGATION_PROMPT_VERSION

    def __post_init__(self) -> None:
        if self.grouping_policy not in KNOWN_GROUPING_POLICIES:
            raise ValueError(
                f"unknown grouping_policy {self.grouping_policy!r}; must be one of "
                f"{sorted(KNOWN_GROUPING_POLICIES)}"
            )
        if self.grouping_policy not in IMPLEMENTED_GROUPING_POLICIES:
            raise NotImplementedError(
                f"grouping_policy {self.grouping_policy!r} is a named future policy, "
                f"not yet implemented (see IMPLEMENTED_GROUPING_POLICIES)"
            )
        if self.grouping_policy == GROUPING_POLICY_G0_UNGROUPED and self.cluster_size is not None:
            raise ValueError("G0_UNGROUPED has no cluster concept; cluster_size must be None")

    def as_dict(self) -> dict:
        return {
            "grouping_policy": self.grouping_policy,
            "cluster_size": self.cluster_size,
            "planner_version": self.planner_version,
            "context_version": self.context_version,
            "investigation_prompt_version": self.investigation_prompt_version,
        }


def default_run_metadata() -> RunMetadata:
    """The metadata every existing call site should attach until it
    explicitly opts into a later grouping policy -- honestly describes
    current (G0, no planner, no reusable context) behavior."""
    return RunMetadata()
