"""Shared RTF-candidate <-> `a4v.graph.ProgramGraph` node resolution.

Promoted out of `bundle_agent_experiment/graph_relevance.py` (where it was
first built and used only for that experiment's own file-relevance
generator) so that both the experiment code and production L12 pipeline
code (`pipeline_e2e.py`) call the exact same, already-hardened resolution
logic instead of drifting duplicates -- `graph_mcp_server.py` had
independently reimplemented the same prefix-match/ambiguity-check inline
in `_get_seed()` before this promotion; that duplication is fixed by this
module too (see `graph_mcp_server.py`'s own `_get_seed`).

RTF's predicate `location` field is a bare "Contract.function" string (no
parameter types -- see `rtf/l5_predicates/predicates.py`'s
`location = f"{contract.name}.{func.name}"`), while the graph's function-
node ids are "fn::Contract.function(paramtypes)"
(`a4v.graph._node_id_function`, `f.canonical_name`). `resolve_seed_node`
bridges the two by prefix match.
"""
from __future__ import annotations

from a4v.graph import FUNCTION, STATEVAR, ProgramGraph


def resolve_seed_node(pg: ProgramGraph, candidate_location: str) -> str:
    """candidate_location is RTF's bare "Contract.function" string. Finds
    the matching "fn::Contract.function(...)" node.

    Matches against the node id's own "fn::Contract.function(" prefix
    (derived from Slither's `canonical_name`, set once at node creation),
    not the node's `contract` data attribute.

    Raises if zero or >1 match. Zero means RTF's candidate doesn't
    resolve to any function the graph knows about (a real integration
    gap, not something to guess past). More than one means an overload
    RTF's own bare location format can't disambiguate -- this must fail
    explicitly rather than silently pick one, per the project's standing
    rule against guessing on ambiguous resolution.
    """
    prefix = f"fn::{candidate_location}("
    candidates = [node for node, data in pg.graph.nodes(data=True)
                  if data.get("kind") == FUNCTION and node.startswith(prefix)]
    if len(candidates) == 0:
        raise ValueError(f"no graph node found for candidate_location={candidate_location!r} "
                          f"(looked for node id prefix {prefix!r})")
    if len(candidates) > 1:
        raise ValueError(f"ambiguous candidate_location={candidate_location!r}: "
                          f"{len(candidates)} overloads {candidates} -- RTF's bare "
                          f"Contract.function location format cannot disambiguate")
    return candidates[0]


def node_file(pg: ProgramGraph, node: str) -> str | None:
    """The source file a graph node lives in. STATEVAR nodes never get a
    direct `file` attribute (`ProgramGraph.build` never sets one for a
    `var::` node) -- resolved indirectly via the owning contract, using
    the node id's own "var::Owner.name" prefix (set once from the
    variable's true declaring contract, never overwritten after
    creation) rather than the node's `contract` data attribute.
    """
    data = pg.graph.nodes[node]
    f = data.get("file")
    if f:
        return f
    if data.get("kind") == STATEVAR:
        owner = node.removeprefix("var::").rsplit(".", 1)[0]
        contract_node = f"contract::{owner}"
        if contract_node in pg.graph:
            return pg.graph.nodes[contract_node].get("file")
    return None


def files_for_nodes(pg: ProgramGraph, nodes: set[str]) -> set[str]:
    files = set()
    for n in nodes:
        f = node_file(pg, n)
        if f:
            files.add(f)
    return files
