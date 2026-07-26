"""Numeric per-node features -- ranking signals only, never a decision
surface (see plan: "Numeric features (ranking only, NOT a decision
surface)"). Computed straight off the already-built ProgramGraph/Slither
compilation so counts stay consistent with the graph's own edges.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
from slither.slithir.operations import TypeConversion

from a4v.graph import ProgramGraph, EXTERNAL_CALL, WRITE_AFTER_EXTERNAL_CALL

_ELEMENTARY_INT_RE = re.compile(r"^u?int(\d+)$")


def _int_bits(type_obj) -> int | None:
    m = _ELEMENTARY_INT_RE.match(str(type_obj))
    if not m:
        return None
    return int(m.group(1))


def _cyclomatic_complexity(function) -> int:
    """McCabe complexity as decision_points + 1. The textbook E - N + 2
    formula assumes a single-exit CFG; Solidity functions routinely have
    multiple early `return`s with no back-edge to a shared exit node, which
    undercounts branching there. Counting branch points (out-degree >= 2)
    directly is robust to that."""
    decision_points = sum(1 for node in function.nodes if len(node.sons) >= 2)
    return decision_points + 1


def _unsafe_cast_count(function) -> int:
    count = 0
    for node in function.nodes:
        for ir in node.irs:
            if isinstance(ir, TypeConversion):
                src_bits = _int_bits(ir.variable.type)
                dst_bits = _int_bits(ir.type)
                if src_bits is not None and dst_bits is not None and dst_bits < src_bits:
                    count += 1
    return count


@dataclass
class NodeFeatures:
    node_id: str
    cyclomatic_complexity: float
    external_call_count: float
    unsafe_cast_count: float
    write_after_external_call_count: float


FEATURE_NAMES = (
    "cyclomatic_complexity",
    "external_call_count",
    "unsafe_cast_count",
    "write_after_external_call_count",
)


class FeatureExtractor:
    @staticmethod
    def compute(pg: ProgramGraph) -> dict[str, NodeFeatures]:
        """Raw (not yet z-scored) features for every function node."""
        by_canonical = {}
        for contract in pg.slither.contracts:
            for function in contract.functions:
                by_canonical[f"fn::{function.canonical_name}"] = function

        raw: dict[str, NodeFeatures] = {}
        for node_id in pg.nodes_of_kind("function"):
            function = by_canonical.get(node_id)
            external_calls = len(pg.neighbors_by_kind(node_id, EXTERNAL_CALL))
            write_after = len(pg.neighbors_by_kind(node_id, WRITE_AFTER_EXTERNAL_CALL))
            if function is None:
                # external/interface stub with no Slither Function body
                raw[node_id] = NodeFeatures(node_id, 0.0, float(external_calls), 0.0, float(write_after))
                continue
            raw[node_id] = NodeFeatures(
                node_id=node_id,
                cyclomatic_complexity=float(_cyclomatic_complexity(function)),
                external_call_count=float(external_calls),
                unsafe_cast_count=float(_unsafe_cast_count(function)),
                write_after_external_call_count=float(write_after),
            )
        return raw

    @staticmethod
    def zscore(raw: dict[str, NodeFeatures]) -> dict[str, dict[str, float]]:
        """Z-score each feature column across the project. Returns
        {node_id: {feature_name: z}}."""
        node_ids = list(raw.keys())
        matrix = np.array([[getattr(raw[nid], f) for f in FEATURE_NAMES] for nid in node_ids])
        mean = matrix.mean(axis=0)
        std = matrix.std(axis=0)
        std[std == 0] = 1.0  # constant column -> z = 0 for everyone, not div-by-zero
        z = (matrix - mean) / std
        return {nid: dict(zip(FEATURE_NAMES, z[i].tolist())) for i, nid in enumerate(node_ids)}
