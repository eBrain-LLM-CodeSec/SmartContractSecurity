"""Function context bundles: what the Auditor sees per candidate.

Per plan ("Function context bundle"): containing contract + a short summary,
inherited definitions relevant to the function, modifiers applied, relevant
state variables, callers/callees (1-2 hops), external interactions, and
related state reads/writes across the neighborhood. Built entirely from the
already-validated ProgramGraph -- never from a bare function in isolation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from a4v.graph import (
    ProgramGraph,
    CONTRACT, FUNCTION, MODIFIER, STATEVAR,
    CALLS, INHERITS, USES_MODIFIER, STATE_READ, STATE_WRITE,
    EXTERNAL_CALL, WRITE_AFTER_EXTERNAL_CALL, DECLARES,
)

_source_cache: dict[str, list[str]] = {}


def _read_lines(path: str) -> list[str]:
    if path not in _source_cache:
        _source_cache[path] = Path(path).read_text(errors="ignore").splitlines()
    return _source_cache[path]


def _excerpt(node_data: dict) -> str | None:
    path = node_data.get("file")
    lines = node_data.get("lines")
    if not path or not lines:
        return None
    all_lines = _read_lines(path)
    start, end = min(lines), max(lines)
    return "\n".join(all_lines[start - 1:end])


@dataclass
class ContextBundle:
    seed: str
    contract: str
    contract_summary: str
    inherited_defs: list[str] = field(default_factory=list)
    modifiers: list[str] = field(default_factory=list)
    state_vars: list[str] = field(default_factory=list)
    callers: list[str] = field(default_factory=list)
    callees: list[str] = field(default_factory=list)
    external_interactions: list[str] = field(default_factory=list)
    write_after_external_call_vars: list[str] = field(default_factory=list)
    neighborhood: set[str] = field(default_factory=set)
    source_excerpts: dict[str, str] = field(default_factory=dict)
    source_excerpt_start_lines: dict[str, int] = field(default_factory=dict)
    source_files: dict[str, str] = field(default_factory=dict)


def numbered_source(source: str, start_line: int) -> str:
    """Prefix each line with its absolute file line number, so the LLM can
    report exact locations rather than snippet-relative line numbers."""
    lines = source.splitlines()
    width = len(str(start_line + len(lines) - 1))
    return "\n".join(f"{start_line + i:>{width}}: {line}" for i, line in enumerate(lines))


class BundleBuilder:
    def __init__(self, pg: ProgramGraph):
        self.pg = pg

    def _contract_summary(self, contract_node: str) -> str:
        data = self.pg.graph.nodes[contract_node]
        functions = self.pg.neighbors_by_kind(contract_node, DECLARES)
        fn_names = [self.pg.graph.nodes[f]["name"] for f in functions if self.pg.graph.nodes[f].get("kind") == FUNCTION]
        bases = self.pg.neighbors_by_kind(contract_node, INHERITS)
        base_names = [self.pg.graph.nodes[b]["name"] for b in bases]
        parts = [f"contract {data['name']}"]
        if base_names:
            parts.append(f"inherits {', '.join(base_names)}")
        if fn_names:
            parts.append(f"functions: {', '.join(fn_names)}")
        return "; ".join(parts)

    def expand(self, seed: str, hops: int = 1) -> ContextBundle:
        if self.pg.graph.nodes[seed].get("kind") != FUNCTION:
            raise ValueError(f"seed {seed!r} is not a function node -- bundles are built around functions")

        seed_data = self.pg.graph.nodes[seed]
        contract_name = seed_data.get("contract")
        contract_node = f"contract::{contract_name}" if contract_name else None

        neighborhood = self.pg.expand(seed, hops=hops)

        inherited = []
        if contract_node and contract_node in self.pg.graph:
            for base in self.pg.neighbors_by_kind(contract_node, INHERITS):
                inherited.append(self.pg.graph.nodes[base]["name"])

        modifiers = [self.pg.graph.nodes[m]["name"] for m in self.pg.neighbors_by_kind(seed, USES_MODIFIER)]
        state_read = [self.pg.graph.nodes[v]["name"] for v in self.pg.neighbors_by_kind(seed, STATE_READ)]
        state_written = [self.pg.graph.nodes[v]["name"] for v in self.pg.neighbors_by_kind(seed, STATE_WRITE)]
        state_vars = sorted(set(state_read) | set(state_written))

        callers = [n for n in self.pg.graph.predecessors(seed)
                   if self.pg.graph.nodes[n].get("kind") == FUNCTION]
        callees = self.pg.neighbors_by_kind(seed, CALLS)
        external = self.pg.neighbors_by_kind(seed, EXTERNAL_CALL)
        write_after = [self.pg.graph.nodes[v]["name"] for v in self.pg.neighbors_by_kind(seed, WRITE_AFTER_EXTERNAL_CALL)]

        source_excerpts = {}
        source_start_lines = {}
        source_files = {}
        for node in neighborhood | {seed}:
            data = self.pg.graph.nodes[node]
            if data.get("kind") in (FUNCTION, CONTRACT):
                excerpt = _excerpt(data)
                if excerpt:
                    source_excerpts[node] = excerpt
                    lines = data.get("lines") or []
                    if lines:
                        source_start_lines[node] = min(lines)
                    if data.get("file"):
                        source_files[node] = data["file"]

        return ContextBundle(
            seed=seed,
            contract=contract_name or "",
            contract_summary=self._contract_summary(contract_node) if contract_node in self.pg.graph else "",
            inherited_defs=inherited,
            modifiers=modifiers,
            state_vars=state_vars,
            callers=callers,
            callees=callees,
            external_interactions=external,
            write_after_external_call_vars=write_after,
            neighborhood=neighborhood,
            source_excerpts=source_excerpts,
            source_excerpt_start_lines=source_start_lines,
            source_files=source_files,
        )
