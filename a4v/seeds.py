"""Seed generation: static-analysis rules UNION Commentator per-function
pass (plan: "Seed generation (static-analysis rules ∪ Commentator per-
function pass)"). Seeds are function nodes worth ranking/expanding --
never a final verdict.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from a4v.commentator import Comment, Commentator
from a4v.features import NodeFeatures
from a4v.graph import ProgramGraph
from a4v.mgpr.context import RouteContextGroup, build_context, build_investigation_context
from a4v.mgpr.router import (
    DEFAULT_UNRESOLVED_INVESTIGATION_MAX_PER_AUDIT,
    INVESTIGATION_SELECTED,
    fired_routes,
    route_all,
    unresolved_investigation_units,
)
from a4v.mgpr.spec import RoutingSpec
from a4v.slice import BundleBuilder


@dataclass
class SeedNode:
    node_id: str
    reasons: list[str] = field(default_factory=list)
    comment: Comment | None = None


class SeedGenerator:
    def __init__(self, pg: ProgramGraph, commentator: Commentator | None = None,
                 bundle_builder: BundleBuilder | None = None):
        self.pg = pg
        self.commentator = commentator
        self.bundle_builder = bundle_builder or BundleBuilder(pg)

    def static_rule_seeds(self, raw_features: dict[str, NodeFeatures]) -> list[SeedNode]:
        seeds = []
        for node_id, f in raw_features.items():
            reasons = []
            if f.write_after_external_call_count > 0:
                reasons.append("static_rule:write_after_external_call")
            if f.unsafe_cast_count > 0:
                reasons.append("static_rule:unsafe_cast")
            if reasons:
                seeds.append(SeedNode(node_id=node_id, reasons=reasons))
        return seeds

    def commentator_seeds(self, function_node_ids: list[str],
                           strategy: int | None = None) -> tuple[list[SeedNode], dict[str, Comment]]:
        if self.commentator is None:
            raise ValueError("no Commentator configured -- pass one to SeedGenerator or skip commentator_seeds")
        seeds = []
        comments: dict[str, Comment] = {}
        for node_id in function_node_ids:
            bundle = self.bundle_builder.expand(node_id, hops=1)
            comment = self.commentator.comment_bundle(bundle, strategy=strategy)
            comments[node_id] = comment
            if comment.suspicious:
                seeds.append(SeedNode(node_id=node_id, reasons=["commentator"], comment=comment))
        return seeds, comments

    def mgpr_commentator_seeds(self, raw_features: dict[str, NodeFeatures],
                                routing_spec: RoutingSpec) -> tuple[list[SeedNode], dict[str, Comment]]:
        """MGPR-routed replacement for `commentator_seeds`'s fixed-hops full
        scan: evaluates `routing_spec`'s gates via `mgpr.router.route_all`,
        groups fired routes by (routing_unit, family) -- Gap D/B's
        additional gates mean more than one gate can now fire for the same
        unit/family, and those must be MERGED into one context/one
        Commentator call, never picked-one and never double-billed -- and
        for each group builds family-specific context via
        `mgpr.context.build_context` instead of
        `BundleBuilder.expand(seed, hops=1)`, then calls the Commentator
        with that family's `prompt_id`. A routing unit that fires multiple
        DIFFERENT families' gates still gets one Commentator call per
        family (multi-label, plan section 6.1) -- not one per unit, and not
        a call for every in-scope function regardless of any signal. Any
        decision-blocking-unresolved route for the same (unit, family) pair
        rides along in the same call via `RouteContextGroup.unresolved_routes`
        (Gap C, Workstream 2's redundancy reduction) rather than triggering
        a second, separate investigation call.
        """
        if self.commentator is None:
            raise ValueError("no Commentator configured -- pass one to SeedGenerator or skip mgpr_commentator_seeds")
        seeds: list[SeedNode] = []
        comments: dict[str, Comment] = {}

        all_routes = route_all(self.pg, raw_features, routing_spec)
        fired = fired_routes(all_routes)
        fired_unit_families = {(r.routing_unit, r.family) for r in fired}

        grouped_fired: dict[tuple[str, str], list] = {}
        for r in fired:
            grouped_fired.setdefault((r.routing_unit, r.family), []).append(r)

        grouped_unresolved: dict[tuple[str, str], list] = {}
        for r in all_routes:
            key = (r.routing_unit, r.family)
            if r.decision_blocking_unresolved and key in fired_unit_families:
                grouped_unresolved.setdefault(key, []).append(r)

        for (routing_unit, family), routes in sorted(grouped_fired.items()):
            group = RouteContextGroup(
                fired_routes=routes, unresolved_routes=grouped_unresolved.get((routing_unit, family), []),
            )
            bundle, _record = build_context(self.pg, group)
            gates_fired = sorted({r.gate for r in routes})
            comment = self.commentator.comment_bundle(bundle, strategy=routes[0].prompt_id)
            # keyed by (unit, family), not just unit -- a single function
            # can produce multiple comments under multi-label routing, and
            # a plain node_id key would silently overwrite one with another.
            comments[f"{routing_unit}::{family}"] = comment
            if comment.suspicious:
                seeds.append(SeedNode(
                    node_id=routing_unit,
                    reasons=[f"mgpr:{family}:{gate}" for gate in gates_fired],
                    comment=comment,
                ))
        return seeds, comments

    def mgpr_investigation_seeds(
        self, raw_features: dict[str, NodeFeatures], routing_spec: RoutingSpec,
        max_per_audit: int = DEFAULT_UNRESOLVED_INVESTIGATION_MAX_PER_AUDIT,
    ) -> tuple[list[SeedNode], dict[str, Comment]]:
        """Gap C, Workstream 2's investigation fallback: for every
        decision-blocking-unresolved routing unit NOT already covered by a
        normal fired route in the same family (see
        `router.unresolved_investigation_units`), issues one Commentator
        call per `INVESTIGATION_SELECTED` unit only -- explicit opt-in,
        separately measurable cost from `mgpr_commentator_seeds`, never
        merged into it.
        """
        if self.commentator is None:
            raise ValueError("no Commentator configured -- pass one to SeedGenerator or skip mgpr_investigation_seeds")
        seeds: list[SeedNode] = []
        comments: dict[str, Comment] = {}

        all_routes = route_all(self.pg, raw_features, routing_spec)
        units = unresolved_investigation_units(self.pg, all_routes, max_per_audit=max_per_audit)

        for unit in units:
            if unit.status != INVESTIGATION_SELECTED:
                continue
            bundle, _record = build_investigation_context(self.pg, unit)
            comment = self.commentator.comment_bundle(bundle, strategy="UNRESOLVED_INVESTIGATION_v1")
            comments[f"{unit.routing_unit}::investigation"] = comment
            if comment.suspicious:
                seeds.append(SeedNode(
                    node_id=unit.routing_unit,
                    reasons=[f"mgpr_investigation:{fam}" for fam in unit.families_blocked],
                    comment=comment,
                ))
        return seeds, comments

    def generate(self, raw_features: dict[str, NodeFeatures], run_commentator: bool = True,
                 strategy: int | None = None,
                 routing_spec: RoutingSpec | None = None) -> tuple[list[SeedNode], dict[str, Comment]]:
        static_seeds = self.static_rule_seeds(raw_features)

        comments: dict[str, Comment] = {}
        commentator_seed_list: list[SeedNode] = []
        if run_commentator and self.commentator is not None:
            if routing_spec is not None:
                commentator_seed_list, comments = self.mgpr_commentator_seeds(raw_features, routing_spec)
            else:
                commentator_seed_list, comments = self.commentator_seeds(list(raw_features.keys()), strategy=strategy)

        combined: dict[str, SeedNode] = {}
        for s in static_seeds + commentator_seed_list:
            if s.node_id not in combined:
                combined[s.node_id] = SeedNode(node_id=s.node_id, reasons=list(s.reasons), comment=s.comment)
            else:
                existing = combined[s.node_id]
                for r in s.reasons:
                    if r not in existing.reasons:
                        existing.reasons.append(r)
                if s.comment is not None:
                    existing.comment = s.comment
        return list(combined.values()), comments
