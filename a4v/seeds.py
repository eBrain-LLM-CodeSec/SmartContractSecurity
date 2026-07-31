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
from a4v.mgpr.context import build_context
from a4v.mgpr.router import fired_routes, route_all
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
        and for each FIRED route builds family-specific context via
        `mgpr.context.build_context` instead of
        `BundleBuilder.expand(seed, hops=1)`, then calls the Commentator
        with that route's family-specific `prompt_id`. A routing unit that
        fires multiple families' gates gets one Commentator call per fired
        route (multi-label, plan section 6.1) -- not one per unit, and not
        a call for every in-scope function regardless of any signal.
        """
        if self.commentator is None:
            raise ValueError("no Commentator configured -- pass one to SeedGenerator or skip mgpr_commentator_seeds")
        seeds: list[SeedNode] = []
        comments: dict[str, Comment] = {}
        for route in fired_routes(route_all(self.pg, raw_features, routing_spec)):
            bundle, _record = build_context(self.pg, route)
            comment = self.commentator.comment_bundle(bundle, strategy=route.prompt_id)
            # keyed by (unit, family), not just unit -- a single function
            # can produce multiple comments under multi-label routing, and
            # a plain node_id key would silently overwrite one with another.
            comments[f"{route.routing_unit}::{route.family}"] = comment
            if comment.suspicious:
                seeds.append(SeedNode(
                    node_id=route.routing_unit,
                    reasons=[f"mgpr:{route.family}:{route.gate}"],
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
