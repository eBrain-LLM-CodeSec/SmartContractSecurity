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
from slither.slithir.operations import Binary, BinaryType, TypeConversion

from a4v.features import NodeFeatures, arithmetic_op_count as _arithmetic_op_count
from a4v.graph import (
    ProgramGraph, CALLS, EXTERNAL_CALL, WRITE_AFTER_EXTERNAL_CALL, STATE_WRITE, STATE_WRITE_TRANSITIVE,
    STATE_READ,
)
from a4v.mgpr.resolution import (
    EvidenceResolution,
    NegativeFeatureState,
    authorization_control_state,
)

_INT_BITS_RE = re.compile(r"^u?int(\d+)$")
_ARITHMETIC_OP_TYPES = (BinaryType.MULTIPLICATION, BinaryType.DIVISION, BinaryType.POWER)


@dataclass
class PredicateStatus:
    predicate: str
    status: str  # SATISFIED | MISSING | UNRESOLVED | NOT_APPLICABLE
    evidence: list[str] = field(default_factory=list)
    extraction_method: str = ""
    resolution_state: str = EvidenceResolution.EXACT.value


# --- boolean predicates -------------------------------------------------


def external_call_exists(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    targets = pg.neighbors_by_kind(node_id, EXTERNAL_CALL)
    status = "SATISFIED" if targets else "MISSING"
    return PredicateStatus(
        predicate="external_call_exists",
        status=status,
        evidence=[f"{node_id} -> {t} (EXTERNAL_CALL)" for t in targets],
        extraction_method="graph.py: EXTERNAL_CALL edges",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def write_after_external_call_exists(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    targets = pg.neighbors_by_kind(node_id, WRITE_AFTER_EXTERNAL_CALL)
    status = "SATISFIED" if targets else "MISSING"
    return PredicateStatus(
        predicate="write_after_external_call_exists",
        status=status,
        evidence=[f"{node_id} -> {t} (WRITE_AFTER_EXTERNAL_CALL)" for t in targets],
        extraction_method="graph.py: WRITE_AFTER_EXTERNAL_CALL edges (CFG-derived ordering)",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def unsafe_cast_count_gt_zero(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    count = int(features.unsafe_cast_count) if features else 0
    status = "SATISFIED" if count > 0 else "MISSING"
    return PredicateStatus(
        predicate="unsafe_cast_count_gt_zero",
        status=status,
        evidence=[f"{node_id}: unsafe_cast_count={count}"],
        extraction_method="features.py:_unsafe_cast_count (SlithIR TypeConversion scan)",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def state_write_exists(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    """Broadened (Gap A) to also count STATE_WRITE_TRANSITIVE edges -- a
    write that only happens via an internal/library call (e.g. a pure
    library function's own body has no state vars at all, but the caller's
    write happens through it) still counts as "this routing unit writes
    state" for gate purposes. Evidence is tagged by which edge kind matched,
    so a route's trace still distinguishes direct from transitive writes.
    """
    direct = pg.neighbors_by_kind(node_id, STATE_WRITE)
    transitive = pg.neighbors_by_kind(node_id, STATE_WRITE_TRANSITIVE)
    status = "SATISFIED" if (direct or transitive) else "MISSING"
    evidence = (
        [f"{node_id} -> {t} (STATE_WRITE)" for t in direct]
        + [f"{node_id} -> {t} (STATE_WRITE_TRANSITIVE)" for t in transitive]
    )
    return PredicateStatus(
        predicate="state_write_exists",
        status=status,
        evidence=evidence,
        extraction_method="graph.py: STATE_WRITE + STATE_WRITE_TRANSITIVE edges",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def visibility_is_public_or_external(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    vis = pg.graph.nodes.get(node_id, {}).get("visibility")
    status = "SATISFIED" if vis in ("public", "external") else "MISSING"
    return PredicateStatus(
        predicate="visibility_is_public_or_external",
        status=status,
        evidence=[f"{node_id}: visibility={vis!r}"],
        extraction_method="graph.py: function node 'visibility' attribute",
        resolution_state=EvidenceResolution.EXACT.value,
    )


def not_constructor(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
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


# --- Gap D: curated callback-interface signature predicate ----------------

# EXACT tier: full elementary-type signatures for well-known callback
# interfaces (ERC721/1155/777 receivers, ERC1271, Uniswap/flash-loan
# callbacks) -- matched against Function.full_name ("name(type1,type2)"),
# confirmed live against the installed Slither version to normalize
# elementary types exactly this way (e.g. "uint256", not "uint").
_CALLBACK_EXACT_SIGNATURES = {
    "onERC721Received(address,address,uint256,bytes)",
    "onERC1155Received(address,address,uint256,uint256,bytes)",
    "onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)",
    "tokensReceived(address,address,address,uint256,bytes,bytes)",  # ERC777
    "isValidSignature(bytes32,bytes)",  # ERC1271
    "isValidSignature(bytes,bytes)",    # ERC1271 draft/alt variant
    "uniswapV2Call(address,uint256,uint256,bytes)",
    "uniswapV3SwapCallback(int256,int256,bytes)",
    "uniswapV3MintCallback(uint256,uint256,bytes)",
    "uniswapV3FlashCallback(uint256,uint256,bytes)",
    "executeOperation(address[],uint256[],uint256[],address,bytes)",  # Aave flash loan
    "onFlashLoan(address,address,uint256,uint256,bytes)",             # ERC3156
}

# HEURISTIC tier: name-only match for callback interfaces whose signature
# takes a struct parameter (e.g. Seaport's zone/contract-order callbacks).
# Confirmed live: Slither's Function.full_name renders a struct parameter
# by its bare local type name (e.g. "validateOrder(Order,bytes)"), which
# varies project-to-project (different projects define their own
# differently-shaped "Order"-like structs) -- so an EXACT full-signature
# match isn't reliable here the way it is for the elementary-type ERC
# callbacks above. The function NAME is the stable, reliable signal.
_CALLBACK_HEURISTIC_NAMES = {
    "validateOrder",
    "isValidOrder",
    "generateOrder",
    "ratifyOrder",
}


def callback_interface_signature_match(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    function = _function_by_node_id(pg, node_id)
    if function is None or not isinstance(function, (Function, FunctionContract)):
        return PredicateStatus(
            predicate="callback_interface_signature_match",
            status="MISSING",
            evidence=[],
            extraction_method="mgpr/predicates.py: Function.full_name / Function.name against curated allowlist",
            resolution_state=EvidenceResolution.EXACT.value,
        )

    full_sig = function.full_name
    if full_sig in _CALLBACK_EXACT_SIGNATURES:
        return PredicateStatus(
            predicate="callback_interface_signature_match",
            status="SATISFIED",
            evidence=[f"{node_id}: EXACT signature match {full_sig!r}"],
            extraction_method="mgpr/predicates.py: Function.full_name against curated EXACT-tier allowlist",
            resolution_state=EvidenceResolution.EXACT.value,
        )
    if function.name in _CALLBACK_HEURISTIC_NAMES:
        return PredicateStatus(
            predicate="callback_interface_signature_match",
            status="SATISFIED",
            evidence=[f"{node_id}: HEURISTIC name-only match {function.name!r} (struct-param signature {full_sig!r})"],
            extraction_method="mgpr/predicates.py: Function.name against curated HEURISTIC-tier struct-param callback names",
            resolution_state=EvidenceResolution.HEURISTIC.value,
        )
    return PredicateStatus(
        predicate="callback_interface_signature_match",
        status="MISSING",
        evidence=[],
        extraction_method="mgpr/predicates.py: Function.full_name / Function.name against curated allowlist",
        resolution_state=EvidenceResolution.EXACT.value,
    )


# --- Gap B: accounting-identifier + precision-sensitive-arithmetic gates --

# Broad vocabulary (Revision 3): held-out terms added generally, not tuned
# to any one specific target finding.
_ACCOUNTING_VOCAB = {
    "share", "shares", "asset", "assets", "balance", "price", "rate", "reward", "fee", "cap",
    "limit", "deposit", "withdraw", "mint", "burn", "redeem", "borrow", "repay", "convert",
    "collateral", "debt", "yield", "principal", "interest", "liquidity", "pool", "vault",
    "exchange", "claim", "claimable", "precision", "round", "scale", "decimal", "exponent",
    "mantissa", "amount", "supply", "total", "reserve", "ratio", "index", "utilization",
}

# Narrower, verb-focused vocabulary used only by accounting_action_identifier_signal
# (P5_ACCOUNTING_ENTRYPOINT), to keep that gate's precision tighter than the
# broad-vocabulary gates.
_ACCOUNTING_ACTION_VOCAB = {
    "deposit", "mint", "redeem", "withdraw", "borrow", "repay", "stake", "unstake",
}

_CAMEL_SPLIT_RE = re.compile(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])")


def _tokenize_identifier(identifier: str) -> list[str]:
    """camelCase/snake_case -> lowercase whole-token split, e.g.
    "totalDebtAmount" -> ["total", "debt", "amount"], "toPackedFloat" ->
    ["to", "packed", "float"]. Whole-token matching only (never substring)
    -- "captureEvent" -> ["capture", "event"], neither of which equals the
    vocabulary token "cap".
    """
    tokens: list[str] = []
    for chunk in identifier.split("_"):
        if not chunk:
            continue
        tokens.extend(m.group(0).lower() for m in _CAMEL_SPLIT_RE.finditer(chunk))
    return tokens


def _identifier_sources(pg: ProgramGraph, node_id: str) -> list[tuple[str, str]]:
    """(source_label, identifier) pairs scanned by the accounting-identifier
    signals: function name; read/written state-var names (STATE_READ /
    STATE_WRITE / STATE_WRITE_TRANSITIVE neighbors); and -- scope widened
    per Revision 3 review, required to catch e.g. a pure library function
    with no state variables at all whose only accounting vocabulary lives
    in its own parameter names -- parameter, local-variable, and
    return-variable names via the Slither Function object.
    """
    sources: list[tuple[str, str]] = []
    name = pg.graph.nodes.get(node_id, {}).get("name")
    if name:
        sources.append(("function_name", name))

    seen_vars: set[str] = set()
    for edge_kind in (STATE_READ, STATE_WRITE, STATE_WRITE_TRANSITIVE):
        for v in pg.neighbors_by_kind(node_id, edge_kind):
            if v in seen_vars:
                continue
            seen_vars.add(v)
            var_name = pg.graph.nodes.get(v, {}).get("name")
            if var_name:
                sources.append(("state_var", var_name))

    function = _function_by_node_id(pg, node_id)
    if function is not None:
        for p in function.parameters:
            if p.name:
                sources.append(("parameter", p.name))
        for lv in function.local_variables:
            if lv.name:
                sources.append(("local_variable", lv.name))
        for rv in function.returns:
            if rv.name:
                sources.append(("return_variable", rv.name))
    return sources


def _identifier_vocab_signal(
    pg: ProgramGraph, node_id: str, vocab: set[str], predicate_name: str,
) -> PredicateStatus:
    matches: set[str] = set()
    for source_label, identifier in _identifier_sources(pg, node_id):
        for token in _tokenize_identifier(identifier):
            if token in vocab:
                matches.add(f"{source_label}:{identifier} (token={token!r})")
    status = "SATISFIED" if matches else "MISSING"
    return PredicateStatus(
        predicate=predicate_name,
        status=status,
        evidence=sorted(matches),
        extraction_method=(
            "mgpr/predicates.py: function name + STATE_READ/STATE_WRITE/STATE_WRITE_TRANSITIVE "
            "neighbor names + Function.parameters/local_variables/returns, tokenized "
            "(camelCase/snake_case) and matched as whole tokens against a curated vocabulary"
        ),
        resolution_state=EvidenceResolution.HEURISTIC.value,
    )


def accounting_identifier_signal(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    return _identifier_vocab_signal(pg, node_id, _ACCOUNTING_VOCAB, "accounting_identifier_signal")


def accounting_action_identifier_signal(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    return _identifier_vocab_signal(pg, node_id, _ACCOUNTING_ACTION_VOCAB, "accounting_action_identifier_signal")


def _bounded_internal_callees(pg: ProgramGraph, node_id: str, max_depth: int) -> list[tuple[str, int]]:
    """Bounded-depth BFS over CALLS edges (internal/library calls),
    mirroring `authorization_control_state`'s own bounded-helper search in
    resolution.py rather than inventing a new pattern. Returns
    (callee_node_id, depth) pairs, depth >= 1, excluding the seed itself.
    """
    seen = {node_id}
    frontier = [node_id]
    depth = 0
    visited: list[tuple[str, int]] = []
    while frontier and depth < max_depth:
        next_frontier: list[str] = []
        for n in sorted(frontier):
            for callee_id in sorted(pg.neighbors_by_kind(n, CALLS)):
                if callee_id in seen:
                    continue
                seen.add(callee_id)
                next_frontier.append(callee_id)
                visited.append((callee_id, depth + 1))
        frontier = next_frontier
        depth += 1
    return visited


def precision_sensitive_arithmetic_exists(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    """Two independent branches, either sufficient: (1) transitive
    arithmetic-operation count -- a bounded-depth internal-call BFS
    checking `features.arithmetic_op_count` on the seed and each visited
    internal callee (recovers e.g. arithmetic that lives one call away in
    an internal helper); (2) assembly-awareness -- `Function.contains_assembly`
    on the same seed+callee set, since precision-sensitive math inside an
    inline `assembly` block is invisible to the SlithIR Binary-op scan.
    The two branches are tagged distinctly in evidence so it's clear in the
    trace which one fired -- required so a downstream noise audit (inline
    assembly is also routinely used for memory copying, calldata decoding,
    hashing, storage-slot access, proxy forwarding -- none of which are
    precision-sensitive arithmetic) can count them separately rather than
    averaging them into one number.
    """
    max_depth = int((params or {}).get("p5_arithmetic_search_max_helper_depth", 2))
    seed_function = _function_by_node_id(pg, node_id)
    if seed_function is None:
        return PredicateStatus(
            predicate="precision_sensitive_arithmetic_exists",
            status="MISSING",
            evidence=[],
            extraction_method="mgpr/predicates.py: no Slither Function resolvable for this node",
            resolution_state=EvidenceResolution.EXACT.value,
        )

    candidates: list[tuple[str, "Function", int]] = [(node_id, seed_function, 0)]
    for callee_id, depth in _bounded_internal_callees(pg, node_id, max_depth):
        callee_function = _function_by_node_id(pg, callee_id)
        if callee_function is not None:
            candidates.append((callee_id, callee_function, depth))

    evidence: list[str] = []
    fired = False
    for visited_id, fn, depth in candidates:
        count = _arithmetic_op_count(fn)
        if count > 0:
            fired = True
            where = "at seed" if depth == 0 else f"via {visited_id} (depth {depth})"
            evidence.append(f"transitive arithmetic_op_count={count} {where}")
        if fn.contains_assembly:
            fired = True
            where = "seed" if depth == 0 else f"{visited_id} (depth {depth})"
            evidence.append(f"{where} contains inline assembly (arithmetic may be present but not IR-visible)")

    status = "SATISFIED" if fired else "MISSING"
    return PredicateStatus(
        predicate="precision_sensitive_arithmetic_exists",
        status=status,
        evidence=evidence,
        extraction_method=(
            "features.py:arithmetic_op_count (SlithIR Binary MULTIPLICATION/DIVISION/POWER scan) "
            f"+ Function.contains_assembly, bounded internal-call BFS depth={max_depth}"
        ),
        resolution_state=EvidenceResolution.HEURISTIC.value,
    )


def arithmetic_op_sites(pg: ProgramGraph, node_id: str) -> list[dict]:
    """Line-level evidence for arithmetic-operation sites in `node_id`'s own
    function body -- mirrors `unsafe_cast_sites`'s exact shape. Seed-only
    (depth 0); does not descend into internal callees -- that expansion is
    `precision_sensitive_arithmetic_exists`'s job for gate evaluation, not
    this evidence helper's.
    """
    function = _function_by_node_id(pg, node_id)
    if function is None or not isinstance(function, (Function, FunctionContract)):
        return []
    sites: list[dict] = []
    for node in function.nodes:
        for ir in node.irs:
            if isinstance(ir, Binary) and ir.type in _ARITHMETIC_OP_TYPES:
                lines = node.source_mapping.lines if node.source_mapping else []
                sites.append({
                    "line": min(lines) if lines else None,
                    "expression": str(node.expression) if node.expression else str(ir),
                    "op": ir.type.name,
                })
    return sites


def external_call_and_state_write_exists(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    """Renamed from an earlier draft's `external_value_flows_into_state_write`
    -- this predicate only establishes that a function has both an
    EXTERNAL_CALL and a STATE_WRITE/STATE_WRITE_TRANSITIVE edge. It does
    NOT trace whether the external call's return value actually flows into
    the write (real dataflow tracing is out of scope for this predicate) --
    co-occurrence, not a traced value flow. Never describe this as "value
    flows into" anywhere (name, evidence, or routing_spec.yaml comment).
    """
    ext_targets = pg.neighbors_by_kind(node_id, EXTERNAL_CALL)
    write_targets = pg.neighbors_by_kind(node_id, STATE_WRITE) + pg.neighbors_by_kind(node_id, STATE_WRITE_TRANSITIVE)
    status = "SATISFIED" if (ext_targets and write_targets) else "MISSING"
    evidence = [
        "co-occurrence only: external interaction + accounting-related state update present "
        "in the same function -- not a traced value flow",
    ]
    evidence += [f"{node_id} -> {t} (EXTERNAL_CALL)" for t in ext_targets]
    evidence += [f"{node_id} -> {t} (STATE_WRITE/STATE_WRITE_TRANSITIVE)" for t in write_targets]
    return PredicateStatus(
        predicate="external_call_and_state_write_exists",
        status=status,
        evidence=evidence if status == "SATISFIED" else [],
        extraction_method=(
            "graph.py: EXTERNAL_CALL + STATE_WRITE/STATE_WRITE_TRANSITIVE edge co-occurrence -- "
            "the function contains both an external interaction and an accounting-related state "
            "update -- co-occurrence, not a traced value flow"
        ),
        resolution_state=EvidenceResolution.EXACT.value,
    )


def numeric_user_input_exists(
    pg: ProgramGraph, node_id: str, features: NodeFeatures | None, params: dict | None = None,
) -> PredicateStatus:
    function = _function_by_node_id(pg, node_id)
    if function is None:
        return PredicateStatus(
            predicate="numeric_user_input_exists",
            status="MISSING",
            evidence=[],
            extraction_method="mgpr/predicates.py: Function.parameters + _int_bits (uint*/int* elementary types)",
            resolution_state=EvidenceResolution.EXACT.value,
        )
    numeric_params = [p.name for p in function.parameters if _int_bits(p.type) is not None]
    status = "SATISFIED" if numeric_params else "MISSING"
    return PredicateStatus(
        predicate="numeric_user_input_exists",
        status=status,
        evidence=[f"{node_id}: numeric parameter {p!r}" for p in numeric_params],
        extraction_method="mgpr/predicates.py: Function.parameters + _int_bits (uint*/int* elementary types)",
        resolution_state=EvidenceResolution.EXACT.value,
    )
