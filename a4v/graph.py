"""Source-level program graph over a Slither-compiled project.

This replaces the paper's trained GAT with an explicit, untrained graph: we
use neighborhoods for context expansion and ranking, never learned
message-passing (see plan: "The program graph (replaces the handcrafted-
feature GAT substitute)").

A valid graph is a hard prerequisite for seed generation and Auditor
investigation -- there is no degraded/partial-graph mode. Callers that cannot
get a Slither compilation to succeed must go through repair.py; this module
never falls back to regex parsing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import networkx as nx

try:
    from slither import Slither
    from slither.core.declarations import Contract, Function, FunctionContract, Modifier
    from slither.core.variables.state_variable import StateVariable
    from slither.core.cfg.node import Node, NodeType
except ImportError as e:  # pragma: no cover - dependency wiring issue, not a build failure
    raise ImportError(
        "slither-analyzer is required to build the program graph; "
        "run `uv sync` in agent4vul/"
    ) from e

# --- node kinds -------------------------------------------------------------
CONTRACT = "contract"
FUNCTION = "function"
MODIFIER = "modifier"
STATEVAR = "statevar"

# --- typed edge kinds --------------------------------------------------------
CALLS = "calls"                                  # function -> function (internal/library)
INHERITS = "inherits"                            # contract -> base contract
USES_MODIFIER = "uses_modifier"                  # function -> modifier
STATE_READ = "state_read"                        # function -> statevar
STATE_WRITE = "state_write"                      # function -> statevar
EXTERNAL_CALL = "external_call"                  # function -> function|contract|"<external>"
WRITE_AFTER_EXTERNAL_CALL = "write_after_external_call"  # function -> statevar (control-flow ordering)
DECLARES = "declares"                            # contract -> function/modifier/statevar


class BuildFailed(Exception):
    """Raised when Slither cannot compile/analyze the scoped project.

    Callers (repair.py, pipeline.py) are responsible for turning this into a
    BUILD_FAILED status -- graph.py itself never substitutes a partial graph.
    """


@dataclass(frozen=True)
class CompileResult:
    slither: "Slither"
    contracts: list[Contract]


def _compile(target: str | Path, solc_remaps: list[str] | None = None,
             extra_kwargs: dict | None = None) -> CompileResult:
    # A single .sol file has no compilation framework to detect -- force
    # plain solc (this is also what the fixture tests rely on). A directory
    # (a real audit's project root) must NOT force solc: crytic-compile needs
    # to auto-detect Foundry/Hardhat and shell out to `forge`/`npx hardhat`
    # accordingly (see codex_runtime/bin/forge for how `forge` reaches the
    # container from this host).
    kwargs: dict = {} if Path(target).is_dir() else {"compile_force_framework": "solc"}
    if solc_remaps:
        kwargs["solc_remaps"] = solc_remaps
    if extra_kwargs:
        kwargs.update(extra_kwargs)
    try:
        sl = Slither(str(target), **kwargs)
    except Exception as e:  # noqa: BLE001 - Slither/solc raise a wide variety of errors
        raise BuildFailed(f"Slither compilation failed for {target}: {e}") from e
    if not sl.contracts:
        raise BuildFailed(f"Slither produced zero contracts for {target}")
    return CompileResult(slither=sl, contracts=list(sl.contracts))


def _node_id_function(f: Function) -> str:
    return f"fn::{f.canonical_name}"


def _node_id_modifier(m: Modifier) -> str:
    return f"mod::{m.canonical_name}"


def _node_id_statevar(v: StateVariable, contract: Contract) -> str:
    # Prefer the declaring contract so inherited vars keep a stable id.
    owner = v.contract.name if getattr(v, "contract", None) else contract.name
    return f"var::{owner}.{v.name}"


def _node_id_contract(c: Contract) -> str:
    return f"contract::{c.name}"


def _has_call_before_write(function: Function) -> set[str]:
    """Returns the set of statevar node ids written on some path *after* a
    high/low-level external call within the same function (write-after-
    external-call ordering), via CFG reachability over `.sons`.
    """
    call_nodes: list[Node] = [
        n for n in function.nodes if n.high_level_calls or n.low_level_calls or n.internal_calls_as_expressions
    ]
    # Only high/low-level calls are "external" in the relevant sense; internal
    # calls to library/internal helpers can't reenter.
    external_call_nodes = [n for n in function.nodes if n.high_level_calls or n.low_level_calls]
    if not external_call_nodes:
        return set()

    written_after: set[str] = set()
    for call_node in external_call_nodes:
        seen: set[int] = set()
        stack = list(call_node.sons)
        while stack:
            n = stack.pop()
            if n.node_id in seen:
                continue
            seen.add(n.node_id)
            for v in n.state_variables_written:
                written_after.add(f"var::{v.contract.name}.{v.name}" if getattr(v, "contract", None) else f"var::{function.contract.name}.{v.name}")
            stack.extend(n.sons)
    return written_after


def _lines(obj) -> list[int]:
    sm = getattr(obj, "source_mapping", None)
    return list(sm.lines) if sm and sm.lines else []


class ProgramGraph:
    """Builds and wraps a networkx MultiDiGraph over one Slither compilation."""

    def __init__(self, graph: nx.MultiDiGraph, slither: "Slither"):
        self.graph = graph
        self.slither = slither

    # --- construction --------------------------------------------------------
    @classmethod
    def build(cls, target: str | Path, solc_remaps: list[str] | None = None,
              extra_kwargs: dict | None = None) -> "ProgramGraph":
        """Compile `target` (a file, or a project dir Slither can detect) and
        build the typed program graph. Raises BuildFailed -- never returns a
        partial graph.
        """
        compiled = _compile(target, solc_remaps=solc_remaps, extra_kwargs=extra_kwargs)
        g = nx.MultiDiGraph()

        for contract in compiled.contracts:
            cid = _node_id_contract(contract)
            g.add_node(cid, kind=CONTRACT, name=contract.name,
                       file=str(contract.source_mapping.filename.absolute) if contract.source_mapping else None,
                       lines=_lines(contract))

            for base in contract.inheritance:
                bid = _node_id_contract(base)
                g.add_node(bid, kind=CONTRACT, name=base.name,
                           file=str(base.source_mapping.filename.absolute) if base.source_mapping else None,
                           lines=_lines(base))
                g.add_edge(cid, bid, kind=INHERITS)

            for modifier in contract.modifiers_declared:
                mid = _node_id_modifier(modifier)
                g.add_node(mid, kind=MODIFIER, name=modifier.name, contract=contract.name, lines=_lines(modifier))
                g.add_edge(cid, mid, kind=DECLARES)

            for var in contract.state_variables_ordered:
                vid = _node_id_statevar(var, contract)
                if vid in g:
                    continue
                g.add_node(vid, kind=STATEVAR, name=var.name, contract=contract.name,
                           type=str(var.type), lines=_lines(var))
                g.add_edge(cid, vid, kind=DECLARES)

            for function in contract.functions:
                if function.is_constructor and function.visibility == "internal":
                    continue
                fid = _node_id_function(function)
                g.add_node(fid, kind=FUNCTION, name=function.name,
                            canonical_name=function.canonical_name,
                            contract=contract.name,
                            visibility=function.visibility,
                            file=str(function.source_mapping.filename.absolute) if function.source_mapping else None,
                            lines=_lines(function),
                            view=function.view, pure=function.pure)
                g.add_edge(cid, fid, kind=DECLARES)

                for modifier in function.modifiers:
                    mid = _node_id_modifier(modifier)
                    if mid not in g:
                        g.add_node(mid, kind=MODIFIER, name=modifier.name,
                                   contract=modifier.contract_declarer.name if modifier.contract_declarer else contract.name,
                                   lines=_lines(modifier))
                    g.add_edge(fid, mid, kind=USES_MODIFIER)

                for var in function.state_variables_read:
                    vid = _node_id_statevar(var, contract)
                    if vid not in g:
                        g.add_node(vid, kind=STATEVAR, name=var.name, contract=contract.name,
                                   type=str(var.type), lines=_lines(var))
                    g.add_edge(fid, vid, kind=STATE_READ)

                for var in function.state_variables_written:
                    vid = _node_id_statevar(var, contract)
                    if vid not in g:
                        g.add_node(vid, kind=STATEVAR, name=var.name, contract=contract.name,
                                   type=str(var.type), lines=_lines(var))
                    g.add_edge(fid, vid, kind=STATE_WRITE)

                for call_op in function.internal_calls:
                    callee = getattr(call_op, "function", None)
                    if isinstance(callee, Modifier):
                        continue  # already captured as USES_MODIFIER
                    if isinstance(callee, (Function, FunctionContract)):
                        callee_id = _node_id_function(callee)
                        if callee_id not in g:
                            # FunctionTopLevel (file-level free functions) has no .contract.
                            callee_contract = getattr(callee, "contract", None)
                            g.add_node(callee_id, kind=FUNCTION, name=callee.name,
                                       canonical_name=callee.canonical_name,
                                       contract=callee_contract.name if callee_contract else None,
                                       visibility=callee.visibility,
                                       file=str(callee.source_mapping.filename.absolute) if callee.source_mapping else None,
                                       lines=_lines(callee))
                        g.add_edge(fid, callee_id, kind=CALLS)
                    # else: builtin/solidity call (require, keccak256, ...) -- not graph-worthy

                for target_contract, call_op in function.high_level_calls:
                    target_function = getattr(call_op, "function", None)
                    if isinstance(target_function, (Function, FunctionContract)):
                        callee_id = _node_id_function(target_function)
                        if callee_id not in g:
                            g.add_node(callee_id, kind=FUNCTION, name=target_function.name,
                                       canonical_name=target_function.canonical_name,
                                       contract=target_contract.name,
                                       visibility=getattr(target_function, "visibility", "external"),
                                       lines=_lines(target_function))
                        g.add_edge(fid, callee_id, kind=EXTERNAL_CALL)
                    else:
                        ext_id = f"ext::{target_contract.name}.{getattr(call_op, 'function_name', call_op)}"
                        if ext_id not in g:
                            g.add_node(ext_id, kind=FUNCTION, name=str(getattr(call_op, "function_name", call_op)),
                                        contract=target_contract.name, external=True)
                        g.add_edge(fid, ext_id, kind=EXTERNAL_CALL)

                if function.low_level_calls:
                    ext_id = "ext::<low-level-call>"
                    if ext_id not in g:
                        g.add_node(ext_id, kind=FUNCTION, name="<low-level-call>", external=True)
                    g.add_edge(fid, ext_id, kind=EXTERNAL_CALL)

                for var_id in _has_call_before_write(function):
                    if var_id not in g:
                        # var may belong to another contract's inherited state; still record it
                        g.add_node(var_id, kind=STATEVAR, name=var_id.split(".")[-1])
                    g.add_edge(fid, var_id, kind=WRITE_AFTER_EXTERNAL_CALL)

        return cls(g, compiled.slither)

    # --- queries --------------------------------------------------------------
    def nodes_of_kind(self, kind: str) -> list[str]:
        return [n for n, d in self.graph.nodes(data=True) if d.get("kind") == kind]

    def edges_of_kind(self, kind: str) -> list[tuple[str, str]]:
        return [(u, v) for u, v, d in self.graph.edges(data=True) if d.get("kind") == kind]

    def neighbors_by_kind(self, node: str, edge_kind: str, direction: str = "out") -> list[str]:
        if direction == "out":
            return [v for _, v, d in self.graph.out_edges(node, data=True) if d.get("kind") == edge_kind]
        return [u for u, _, d in self.graph.in_edges(node, data=True) if d.get("kind") == edge_kind]

    def expand(self, seed: str, hops: int = 1) -> set[str]:
        """BFS neighborhood over all edge kinds, both directions, `hops` deep."""
        frontier = {seed}
        visited = {seed}
        for _ in range(hops):
            next_frontier: set[str] = set()
            for node in frontier:
                next_frontier |= set(self.graph.successors(node))
                next_frontier |= set(self.graph.predecessors(node))
            next_frontier -= visited
            visited |= next_frontier
            frontier = next_frontier
        return visited
