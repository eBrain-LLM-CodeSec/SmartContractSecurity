"""Deterministic MGPR predicate library -- pure functions over ProgramGraph
+ per-function structural features. See routing_spec.yaml (P1/P2/P5) and
the plan's section 3 gate corrections for exactly which of these are
zero-extraction (read an existing graph.py/features.py field verbatim) vs.
additive (new, small, evidence-producing scans that don't modify graph.py
or features.py).

Every predicate function has the boolean signature
`(pg, node_id, features) -> PredicateStatus`, except
`authorization_control_state_predicate`, which additionally takes the
family's `params` dict and the gate's expected enum value (see router.py's
ENUM_PREDICATES dispatch).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from slither.core.declarations import Function, FunctionContract
from slither.slithir.operations import TypeConversion

from a4v.features import NodeFeatures
from a4v.graph import ProgramGraph, EXTERNAL_CALL, WRITE_AFTER_EXTERNAL_CALL, STATE_WRITE
from a4v.mgpr.resolution import (
    EvidenceResolution,
    NegativeFeatureState,
    authorization_control_state,
)

_INT_BITS_RE = re.compile(r"^u?int(\d+)$")


@dataclass
class PredicateStatus:
    predicate: str
    status: str  # SATISFIED | MISSING | UNRESOLVED | NOT_APPLICABLE
    evidence: list[str] = field(default_factory=list)
    extraction_method: str = ""
    resolution_state: str = EvidenceResolution.EXACT.value


# --- boolean predicates -------------------------------------------------


def external_call_exists(pg: ProgramGraph, node_id: str, features: NodeFeatures | None) -> PredicateStatus:
    targets = pg.neighbors_by_kind(node_id, EXTERNAL_CALL)
    status = "SATISFIED" if targets else "MISSING"
    return PredicateStatus(
        predicate="external_call_exists",
        status=status,
        evidence=[f"{node_id} -> {t} (EXTERNAL_CALL)" for t in targets],
        extraction_method="graph.py: EXTERNAL_CALL edges",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def write_after_external_call_exists(pg: ProgramGraph, node_id: str, features: NodeFeatures | None) -> PredicateStatus:
    targets = pg.neighbors_by_kind(node_id, WRITE_AFTER_EXTERNAL_CALL)
    status = "SATISFIED" if targets else "MISSING"
    return PredicateStatus(
        predicate="write_after_external_call_exists",
        status=status,
        evidence=[f"{node_id} -> {t} (WRITE_AFTER_EXTERNAL_CALL)" for t in targets],
        extraction_method="graph.py: WRITE_AFTER_EXTERNAL_CALL edges (CFG-derived ordering)",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def unsafe_cast_count_gt_zero(pg: ProgramGraph, node_id: str, features: NodeFeatures | None) -> PredicateStatus:
    count = int(features.unsafe_cast_count) if features else 0
    status = "SATISFIED" if count > 0 else "MISSING"
    return PredicateStatus(
        predicate="unsafe_cast_count_gt_zero",
        status=status,
        evidence=[f"{node_id}: unsafe_cast_count={count}"],
        extraction_method="features.py:_unsafe_cast_count (SlithIR TypeConversion scan)",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def state_write_exists(pg: ProgramGraph, node_id: str, features: NodeFeatures | None) -> PredicateStatus:
    targets = pg.neighbors_by_kind(node_id, STATE_WRITE)
    status = "SATISFIED" if targets else "MISSING"
    return PredicateStatus(
        predicate="state_write_exists",
        status=status,
        evidence=[f"{node_id} -> {t} (STATE_WRITE)" for t in targets],
        extraction_method="graph.py: STATE_WRITE edges",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def visibility_is_public_or_external(pg: ProgramGraph, node_id: str, features: NodeFeatures | None) -> PredicateStatus:
    vis = pg.graph.nodes.get(node_id, {}).get("visibility")
    status = "SATISFIED" if vis in ("public", "external") else "MISSING"
    return PredicateStatus(
        predicate="visibility_is_public_or_external",
        status=status,
        evidence=[f"{node_id}: visibility={vis!r}"],
        extraction_method="graph.py: function node 'visibility' attribute",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def not_constructor(pg: ProgramGraph, node_id: str, features: NodeFeatures | None) -> PredicateStatus:
    # graph.py does not store an explicit is_constructor flag on function
    # nodes (it only uses Slither's is_constructor at build time, to decide
    # whether to skip internal constructors entirely -- see graph.py:183-184).
    # Slither's convention names the constructor function "constructor", so
    # this is a name-based heuristic, not an exact stored flag.
    name = pg.graph.nodes.get(node_id, {}).get("name", "")
    is_ctor = name == "constructor"
    status = "MISSING" if is_ctor else "SATISFIED"
    return PredicateStatus(
        predicate="not_constructor",
        status=status,
        evidence=[f"{node_id}: name={name!r}"],
        extraction_method="graph.py: function node 'name' attribute (heuristic: name == 'constructor')",
        resolution_state=EvidenceResolution.HEURISTIC.value,
    )


# --- enum predicate (authorization_control_state) ------------------------


def authorization_control_state_predicate(
    pg: ProgramGraph,
    node_id: str,
    features: NodeFeatures | None,
    params: dict,
    expected: str,
) -> PredicateStatus:
    max_depth = int(params.get("authorization_search_max_helper_depth", 2))
    result = authorization_control_state(pg, node_id, max_helper_depth=max_depth)

    if result.state == NegativeFeatureState.UNRESOLVED_BY_EXTRACTION:
        status = "UNRESOLVED"
    elif result.state.value == expected:
        status = "SATISFIED"
    else:
        status = "MISSING"

    return PredicateStatus(
        predicate="authorization_control_state",
        status=status,
        evidence=[f"resolved_state={result.state.value}"] + result.evidence + result.notes,
        extraction_method=(
            "mgpr/resolution.py:authorization_control_state (function body, applied modifiers, "
            f"bounded internal-helper BFS depth={max_depth}, inherited base-contract modifiers)"
        ),
        resolution_state=EvidenceResolution.HEURISTIC.value,
    )


# --- evidence-only helper (not a gate predicate itself) -------------------

_by_canonical_cache: dict[int, dict[str, Function]] = {}


def _function_by_node_id(pg: ProgramGraph, node_id: str) -> Function | None:
    cache = _by_canonical_cache.get(id(pg))
    if cache is None:
        cache = {}
        for contract in pg.slither.contracts:
            for function in contract.functions:
                cache[f"fn::{function.canonical_name}"] = function
        _by_canonical_cache[id(pg)] = cache
    return cache.get(node_id)


def _int_bits(type_obj) -> int | None:
    m = _INT_BITS_RE.match(str(type_obj))
    return int(m.group(1)) if m else None


def unsafe_cast_sites(pg: ProgramGraph, node_id: str) -> list[dict]:
    """Line-level evidence for narrowing casts in `node_id`'s function body
    -- independently re-scans the same SlithIR TypeConversion ops
    features.py:_unsafe_cast_count already scans, but retains
    (line, expression_text) per cast instead of collapsing to a count.
    Does not modify features.py; used only for gate_evaluation.jsonl
    evidence and P5's context construction (plan section 3, P5 correction).
    """
    function = _function_by_node_id(pg, node_id)
    if function is None or not isinstance(function, (Function, FunctionContract)):
        return []
    sites: list[dict] = []
    for node in function.nodes:
        for ir in node.irs:
            if isinstance(ir, TypeConversion):
                src_bits = _int_bits(ir.variable.type)
                dst_bits = _int_bits(ir.type)
                if src_bits is not None and dst_bits is not None and dst_bits < src_bits:
                    lines = node.source_mapping.lines if node.source_mapping else []
                    sites.append({
                        "line": min(lines) if lines else None,
                        "expression": str(node.expression) if node.expression else str(ir),
                    })
    return sites
