"""G0/G1/G2/G3 graph-derived file-relevance sets, built entirely from the
EXISTING `a4v.graph.ProgramGraph` / `a4v.slice.BundleBuilder` machinery
(the sibling MGPR/Auditor system's infrastructure -- confirmed, via a
direct grep across rtf/, that RTF itself never constructs a ProgramGraph
or calls BundleBuilder today; this module is the first thing that wires
the two together for RTF's own candidates). No new relevance classifier,
embedding, or learned ranking is introduced -- see
PROGRAM_GRAPH_RELEVANCE_BOUNDARY_EXPERIMENT.md sec. 1 for the full
capability audit this module's design follows from.

RTF's predicate `location` field is a bare "Contract.function" string
(no parameter types -- see rtf/l5_predicates/predicates.py's
`location = f"{contract.name}.{func.name}"`, the exact root cause AR-017
already documented), while the graph's function-node ids are
"fn::Contract.function(paramtypes)" (`a4v.graph._node_id_function`,
`f.canonical_name`). `resolve_seed_node` (now in `rtf.l8_llm_judgment_
layer.graph_navigation`, promoted out of this module so production L12
code can share it rather than duplicate it -- see that module's
docstring for the full inherited-function history) bridges the two by
prefix match.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from a4v.graph import (
    CALLS, CONTRACT, DECLARES, EXTERNAL_CALL, FUNCTION, INHERITS, MODIFIER,
    STATE_READ, STATE_WRITE, STATE_WRITE_TRANSITIVE, STATEVAR,
    USES_MODIFIER, WRITE_AFTER_EXTERNAL_CALL, ProgramGraph,
)
from a4v.slice import BundleBuilder
from rtf.l8_llm_judgment_layer.graph_navigation import (
    files_for_nodes, node_file as _node_file, resolve_seed_node,
)


@dataclass
class GraphFileSets:
    seed_node: str
    seed_file: str
    g0: set[str] = field(default_factory=set)
    g1: set[str] = field(default_factory=set)
    g2: set[str] = field(default_factory=set)
    g1_nodes: set[str] = field(default_factory=set)
    g2_nodes: set[str] = field(default_factory=set)


def build_g0_g1_g2(pg: ProgramGraph, candidate_location: str) -> GraphFileSets:
    seed = resolve_seed_node(pg, candidate_location)
    seed_file = _node_file(pg, seed)
    if not seed_file:
        raise ValueError(f"seed node {seed!r} has no resolvable file")

    g1_nodes = pg.expand(seed, hops=1)
    g2_nodes = pg.expand(seed, hops=2)

    return GraphFileSets(
        seed_node=seed, seed_file=seed_file,
        g0={seed_file},
        g1=files_for_nodes(pg, g1_nodes) | {seed_file},
        g2=files_for_nodes(pg, g2_nodes) | {seed_file},
        g1_nodes=g1_nodes, g2_nodes=g2_nodes,
    )


@dataclass
class AdaptiveExpansionStep:
    hop: int
    trigger_symbol: str
    trigger_relation: str
    file_added: str


def build_g3_adaptive(pg: ProgramGraph, candidate_location: str, unresolved_facts: list[str],
                       max_hops: int = 3) -> tuple[set[str], list[AdaptiveExpansionStep]]:
    """Starts at G1. For each unresolved fact, checks whether the fact
    names a symbol (by simple substring match against node names already
    in the current node set's 1-hop-further neighbors) whose definition/
    write-site/caller lies just outside the current set -- if so, expands
    one more hop specifically via that symbol's own graph edges, not a
    blanket "expand everything one more hop." This is a simple, honest,
    keyword-substring heuristic over EXISTING graph node names (not a new
    classifier over source text) -- documented as such, including its
    real limitation: it can only find a symbol this way if the unresolved-
    fact text names it in a form matching a graph node's own `name`
    field (e.g. "authorizedSigner"), which is true for this experiment's
    hand-written unresolved_facts (they were written by the same project
    that also builds the predicates) but would not generalize to
    free-text unresolved-fact phrasing without a real text-matching step
    -- out of scope for this experiment per its own "no new classifier"
    constraint.
    """
    seed = resolve_seed_node(pg, candidate_location)
    current_nodes = pg.expand(seed, hops=1)
    current_files = files_for_nodes(pg, current_nodes) | {pg.graph.nodes[seed]["file"]}
    steps: list[AdaptiveExpansionStep] = []

    hop = 1
    while hop < max_hops:
        expanded_any = False
        # any node one hop further than the current set, whose name is
        # substring-mentioned in some unresolved fact, triggers pulling
        # it (and its file) in.
        frontier = pg.expand(seed, hops=hop + 1) - current_nodes
        for node in sorted(frontier):
            data = pg.graph.nodes[node]
            name = data.get("name", "")
            if not name:
                continue
            for fact in unresolved_facts:
                if name in fact:
                    nf = _node_file(pg, node)
                    if nf and nf not in current_files:
                        # find which relation actually connects it, for the trace
                        relation = "unknown"
                        for _, v, d in pg.graph.out_edges(node, data=True):
                            if v in current_nodes:
                                relation = d.get("kind", relation)
                        for u, _, d in pg.graph.in_edges(node, data=True):
                            if u in current_nodes:
                                relation = d.get("kind", relation)
                        steps.append(AdaptiveExpansionStep(hop=hop + 1, trigger_symbol=name,
                                                            trigger_relation=relation, file_added=nf))
                        current_files.add(nf)
                        expanded_any = True
                    current_nodes = current_nodes | {node}
        hop += 1
        if not expanded_any:
            break

    return current_files, steps
