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

    def generate(self, raw_features: dict[str, NodeFeatures], run_commentator: bool = True,
                 strategy: int | None = None) -> tuple[list[SeedNode], dict[str, Comment]]:
        static_seeds = self.static_rule_seeds(raw_features)

        comments: dict[str, Comment] = {}
        commentator_seed_list: list[SeedNode] = []
        if run_commentator and self.commentator is not None:
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
