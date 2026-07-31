"""Four-state negative-feature resolution model and the
authorization_control_state search chain that uses it (plan section 5).

`NegativeFeatureState` distinguishes a confirmed-missing control (ABSENT)
from a search that could not be completed (UNRESOLVED_BY_EXTRACTION) --
these must never be conflated, since a gate that fires on "not proven
present" instead of "proven absent" would silently treat unresolved graph
information as evidence of a missing control, which the plan explicitly
forbids.

`EvidenceResolution` is a separate, orthogonal axis: how confidently a given
piece of *positive* evidence (an edge, a matched pattern) was derived.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from a4v.graph import ProgramGraph, CALLS, INHERITS, USES_MODIFIER


class NegativeFeatureState(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    UNRESOLVED_BY_EXTRACTION = "UNRESOLVED_BY_EXTRACTION"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class EvidenceResolution(str, Enum):
    EXACT = "EXACT"
    STATICALLY_RESOLVED = "STATICALLY_RESOLVED"
    SELECTOR_INFERRED = "SELECTOR_INFERRED"
    HEURISTIC = "HEURISTIC"
    UNRESOLVED = "UNRESOLVED"


@dataclass
class SearchResult:
    state: NegativeFeatureState
    evidence: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


# Heuristic (not exact) text pattern for "some authorization control is
# present" -- require(msg.sender==...), common onlyOwner/onlyRole/hasRole/
# AccessControl idioms. This is a coarse, regex-based signal consistent
# with the rest of a4v's existing heuristics (e.g. features.py's cast-type
# regex, repair.py's pragma regex) -- not a claim of semantic understanding.
_AUTH_PATTERN_RE = re.compile(
    r"require\s*\(\s*msg\.sender\s*(==|!=)"
    r"|onlyOwner|onlyRole\s*\("
    r"|hasRole\s*\("
    r"|_checkOwner\s*\("
    r"|AccessControl"
    r"|msg\.sender\s*==\s*owner",
    re.IGNORECASE,
)

_source_cache: dict[str, list[str]] = {}


def _read_lines(path: str) -> list[str] | None:
    if path not in _source_cache:
        try:
            _source_cache[path] = Path(path).read_text(errors="ignore").splitlines()
        except OSError:
            return None
    return _source_cache[path]


def _node_source_text(pg: ProgramGraph, node_id: str) -> str | None:
    if node_id not in pg.graph:
        return None
    data = pg.graph.nodes[node_id]
    path = data.get("file")
    lines = data.get("lines")
    if not path or not lines:
        return None
    all_lines = _read_lines(path)
    if all_lines is None:
        return None
    start, end = min(lines), max(lines)
    return "\n".join(all_lines[start - 1 : end])


def authorization_control_state(
    pg: ProgramGraph, function_node_id: str, max_helper_depth: int = 2,
) -> SearchResult:
    """Search, in order: (1) function body, (2) applied modifiers,
    (3) internal helper calls up to `max_helper_depth`, (4) the function's
    contract's transitive INHERITS closure, for an authorization-control
    text pattern. Returns ABSENT only if every step resolved cleanly with
    no match found; UNRESOLVED_BY_EXTRACTION if any step's source/target
    could not be read, regardless of whether other steps resolved cleanly.
    """
    evidence: list[str] = []
    notes: list[str] = []
    unresolved = False

    # (1) function body directly
    body = _node_source_text(pg, function_node_id)
    if body is None:
        notes.append(f"{function_node_id}: source unavailable")
        unresolved = True
    elif _AUTH_PATTERN_RE.search(body):
        evidence.append(f"{function_node_id}: auth pattern in function body")
        return SearchResult(NegativeFeatureState.PRESENT, evidence, notes)

    # (2) applied modifiers -- graph.py already resolves function.modifiers
    # (including inherited-and-applied ones) onto the correct
    # declaring-contract modifier node, so this covers inheritance for
    # modifiers actually in effect on this function.
    for mod_id in pg.neighbors_by_kind(function_node_id, USES_MODIFIER):
        mod_text = _node_source_text(pg, mod_id)
        if mod_text is None:
            notes.append(f"{mod_id}: modifier source unavailable")
            unresolved = True
            continue
        if _AUTH_PATTERN_RE.search(mod_text):
            evidence.append(f"{mod_id}: auth pattern in applied modifier")
            return SearchResult(NegativeFeatureState.PRESENT, evidence, notes)

    # (3) internal helper calls, bounded-depth BFS
    seen = {function_node_id}
    frontier = [function_node_id]
    depth = 0
    while frontier and depth < max_helper_depth:
        next_frontier: list[str] = []
        for node in frontier:
            for callee_id in pg.neighbors_by_kind(node, CALLS):
                if callee_id in seen:
                    continue
                seen.add(callee_id)
                next_frontier.append(callee_id)
                callee_text = _node_source_text(pg, callee_id)
                if callee_text is None:
                    notes.append(f"{callee_id}: internal helper source unavailable")
                    unresolved = True
                    continue
                if _AUTH_PATTERN_RE.search(callee_text):
                    evidence.append(f"{callee_id}: auth pattern in internal helper (depth {depth + 1})")
                    return SearchResult(NegativeFeatureState.PRESENT, evidence, notes)
        frontier = next_frontier
        depth += 1

    # (4) the function's contract's transitive INHERITS closure. Given (2)
    # already resolves applied-and-inherited modifiers onto the correct
    # node, this step's role is narrower: flag when a base contract isn't
    # present in the compile unit at all (a genuine resolution gap), not to
    # newly discover protection -- a modifier merely *declared* in a base
    # contract that this function never applies is not evidence that this
    # function is protected.
    contract_name = pg.graph.nodes[function_node_id].get("contract")
    if contract_name:
        contract_id = f"contract::{contract_name}"
        if contract_id in pg.graph:
            base_chain = list(pg.neighbors_by_kind(contract_id, INHERITS))
            visited = {contract_id}
            i = 0
            while i < len(base_chain):
                base_id = base_chain[i]
                i += 1
                if base_id in visited:
                    continue
                visited.add(base_id)
                # networkx auto-creates an attribute-less node for any edge
                # endpoint that was never explicitly added, so `base_id not
                # in pg.graph` can never be true here -- check for real
                # attributes instead (a genuine graph.py-built contract node
                # always has `kind` set).
                if not pg.graph.nodes[base_id].get("kind"):
                    notes.append(f"{base_id}: base contract not present in compile unit")
                    unresolved = True
                    continue
                base_chain.extend(pg.neighbors_by_kind(base_id, INHERITS))

    if unresolved:
        return SearchResult(NegativeFeatureState.UNRESOLVED_BY_EXTRACTION, evidence, notes)
    return SearchResult(NegativeFeatureState.ABSENT, evidence, notes)
