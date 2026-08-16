"""Typed investigation tools over the EXISTING Slither/ProgramGraph
infrastructure (`a4v.graph.ProgramGraph`), called in-process.

Deliberately does NOT reimplement call-graph/state-read-write/inheritance
analysis -- every method here is a thin, typed wrapper over graph queries
`a4v/graph.py` and `rtf/l8_llm_judgment_layer/graph_navigation.py` already
provide (the exact same functions `graph_mcp_server.py` uses to serve
Codex). The one real difference from `graph_mcp_server.py`: that module
exists as a SEPARATE MCP subprocess because Codex is a separate process;
our own kernel runs in the same process as its control loop, so there is
no MCP/JSON-RPC layer here, no "reveal file into a scratch copy" step
(the kernel already has full repo access), and no env-var wiring -- just
plain Python method calls returning Pydantic models.

V0 scope (brief Phase 18): read-only. No run_command/run_foundry_test/
generate_temporary_poc here yet -- those are later, explicitly deferred
increments, added only once static investigation is proven.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from a4v.graph import (
    CALLS, CONTRACT, DECLARES, EXTERNAL_CALL, FUNCTION, INHERITS, MODIFIER,
    STATE_READ, STATE_WRITE, STATE_WRITE_TRANSITIVE, STATEVAR, USES_MODIFIER,
    ProgramGraph,
)
from a4v.slice import _excerpt, numbered_source
from rtf.l8_llm_judgment_layer.graph_navigation import node_file, resolve_seed_node

ToolStatus = Literal["OK", "NOT_FOUND", "AMBIGUOUS", "ERROR"]


class FunctionRef(BaseModel):
    node_id: str
    contract: str | None = None
    name: str
    canonical_name: str | None = None
    file: str | None = None
    lines: list[int] = Field(default_factory=list)
    visibility: str | None = None


class StateVarRef(BaseModel):
    node_id: str
    contract: str | None = None
    name: str
    type: str | None = None
    file: str | None = None
    lines: list[int] = Field(default_factory=list)


class ModifierRef(BaseModel):
    node_id: str
    contract: str | None = None
    name: str
    file: str | None = None
    lines: list[int] = Field(default_factory=list)


class ExternalCallRef(BaseModel):
    node_id: str
    contract: str | None = None
    name: str
    file: str | None = None
    lines: list[int] = Field(default_factory=list)
    resolved: bool
    """False for an unresolved external interface call or a low-level
    call (.call/.delegatecall/.staticcall) with no specific target in
    the graph -- mirrors graph_mcp_server.investigate's `also_unresolved`
    handling, but surfaced explicitly per-item instead of as a side list."""


class SourceExcerptResult(BaseModel):
    status: ToolStatus
    reason: str | None = None
    node_id: str | None = None
    contract: str | None = None
    name: str | None = None
    file: str | None = None
    lines: list[int] = Field(default_factory=list)
    source: str | None = None
    """Numbered source text (via a4v.slice.numbered_source), so the agent
    can cite exact absolute line numbers in Evidence -- matching the
    brief's Phase 10 requirement that findings reference concrete
    file/line locations, not paraphrased ones."""


class FunctionListResult(BaseModel):
    status: ToolStatus
    reason: str | None = None
    functions: list[FunctionRef] = Field(default_factory=list)


class StateVarListResult(BaseModel):
    status: ToolStatus
    reason: str | None = None
    state_vars: list[StateVarRef] = Field(default_factory=list)


class ModifierListResult(BaseModel):
    status: ToolStatus
    reason: str | None = None
    modifiers: list[ModifierRef] = Field(default_factory=list)


class ExternalCallListResult(BaseModel):
    status: ToolStatus
    reason: str | None = None
    external_calls: list[ExternalCallRef] = Field(default_factory=list)


class InheritanceResult(BaseModel):
    status: ToolStatus
    reason: str | None = None
    contract: str | None = None
    bases: list[str] = Field(default_factory=list)
    """Direct + transitive base contract names, in `contract.inheritance`
    order (Slither's own MRO-linearized order), NOT just one hop."""


class ReadFileResult(BaseModel):
    status: ToolStatus
    reason: str | None = None
    path: str | None = None
    content: str | None = None


class SearchHit(BaseModel):
    file: str
    line: int
    text: str


class SearchRepositoryResult(BaseModel):
    status: ToolStatus
    reason: str | None = None
    hits: list[SearchHit] = Field(default_factory=list)
    truncated: bool = False


_SEARCH_MAX_HITS = 200
_SEARCH_SKIP_EXTS = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".sif", ".zip", ".gz", ".so", ".o"}


class SecurityAgentTools:
    """One instance per cluster investigation, wrapping one already-built
    `ProgramGraph` plus the repo root it was compiled from. `repo_root`
    bounds `read_file`/`search_repository` -- the one real system-boundary
    validation this class does (an LLM-driven tool call is untrusted
    input in the sense that matters: a path that escapes the repo it's
    supposed to be investigating), everything else trusts the graph."""

    def __init__(self, program_graph: ProgramGraph, repo_root: Path):
        self.pg = program_graph
        self.repo_root = repo_root.resolve()

    # -- construction --------------------------------------------------------

    @classmethod
    def build(cls, repo_root: Path, entry_file: str | Path | None = None, *,
              compile_via_foundry: bool = False,
              solc_remaps: list[str] | None = None,
              extra_compile_kwargs: dict | None = None) -> "SecurityAgentTools":
        """Mirrors graph_mcp_server._build_graph_for_investigation exactly
        (same two branches, same reasoning) -- reused here as plain
        in-process calls instead of MCP env-var wiring. `compile_via_foundry`
        reads the repo's ALREADY-compiled Foundry artifacts
        (out/build-info/) via Slither directly, matching
        RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md's whole-project visibility
        fix -- without this, a sibling contract the entry file doesn't
        `import` is invisible to the graph, same as it would be to Codex.
        """
        if compile_via_foundry:
            from slither import Slither
            slither = Slither(str(repo_root), foundry_ignore_compile=True, compile_force_framework="Foundry")
            pg = ProgramGraph.from_slither(slither)
        else:
            if entry_file is None:
                raise ValueError("entry_file is required when compile_via_foundry=False")
            pg = ProgramGraph.build(entry_file, solc_remaps=solc_remaps, extra_kwargs=extra_compile_kwargs)
        return cls(pg, repo_root)

    # -- function/contract source --------------------------------------------

    def _resolve_function(self, contract: str, function: str) -> tuple[str | None, ToolStatus, str | None]:
        """Returns (node_id, status, reason). Reuses
        graph_navigation.resolve_seed_node's exact prefix-match logic
        (RTF's own bare "Contract.function" -> "fn::Contract.function("
        bridging) rather than reimplementing it -- only adds structured
        NOT_FOUND/AMBIGUOUS status codes around its raise-on-failure
        contract."""
        try:
            node_id = resolve_seed_node(self.pg, f"{contract}.{function}")
            return node_id, "OK", None
        except ValueError as e:
            status: ToolStatus = "AMBIGUOUS" if "ambiguous" in str(e).lower() else "NOT_FOUND"
            return None, status, str(e)

    def get_function_source(self, contract: str, function: str) -> SourceExcerptResult:
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return SourceExcerptResult(status=status, reason=reason)
        return self._source_excerpt_for_node(node_id)

    def get_contract_source(self, contract: str) -> SourceExcerptResult:
        node_id = f"contract::{contract}"
        if node_id not in self.pg.graph:
            return SourceExcerptResult(status="NOT_FOUND", reason=f"no contract node for {contract!r}")
        return self._source_excerpt_for_node(node_id)

    def _source_excerpt_for_node(self, node_id: str) -> SourceExcerptResult:
        data = self.pg.graph.nodes[node_id]
        excerpt = _excerpt(data)
        if not excerpt:
            return SourceExcerptResult(status="NOT_FOUND", reason=f"no source excerpt available for {node_id!r}",
                                        node_id=node_id, contract=data.get("contract") or data.get("name"))
        lines = data.get("lines") or [1]
        return SourceExcerptResult(
            status="OK", node_id=node_id, contract=data.get("contract") or data.get("name"),
            name=data.get("name"), file=data.get("file"), lines=lines,
            source=numbered_source(excerpt, min(lines)),
        )

    # -- callers / callees / external calls ----------------------------------

    def get_callers(self, contract: str, function: str) -> FunctionListResult:
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return FunctionListResult(status=status, reason=reason)
        callers = set(self.pg.neighbors_by_kind(node_id, CALLS, direction="in"))
        callers |= set(self.pg.neighbors_by_kind(node_id, EXTERNAL_CALL, direction="in"))
        return FunctionListResult(status="OK", functions=[self._function_ref(n) for n in sorted(callers)])

    def get_callees(self, contract: str, function: str) -> FunctionListResult:
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return FunctionListResult(status=status, reason=reason)
        callees = set(self.pg.neighbors_by_kind(node_id, CALLS, direction="out"))
        return FunctionListResult(status="OK", functions=[self._function_ref(n) for n in sorted(callees)])

    def get_external_calls(self, contract: str, function: str) -> ExternalCallListResult:
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return ExternalCallListResult(status=status, reason=reason)
        targets = sorted(set(self.pg.neighbors_by_kind(node_id, EXTERNAL_CALL, direction="out")))
        if not targets:
            return ExternalCallListResult(status="NOT_FOUND",
                                           reason=f"no external calls found from {contract}.{function}")
        refs = []
        for n in targets:
            data = self.pg.graph.nodes[n]
            refs.append(ExternalCallRef(
                node_id=n, contract=data.get("contract"), name=data.get("name") or n,
                file=data.get("file"), lines=data.get("lines") or [],
                resolved=bool(data.get("file")),
            ))
        return ExternalCallListResult(status="OK", external_calls=refs)

    def get_related_functions(self, contract: str, function: str) -> FunctionListResult:
        """One-hop union: callers + callees + resolved external-call
        targets. A single starting point for "what else is relevant here"
        without the agent having to call three separate tools first."""
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return FunctionListResult(status=status, reason=reason)
        related = set(self.pg.neighbors_by_kind(node_id, CALLS, direction="in"))
        related |= set(self.pg.neighbors_by_kind(node_id, EXTERNAL_CALL, direction="in"))
        related |= set(self.pg.neighbors_by_kind(node_id, CALLS, direction="out"))
        related |= {n for n in self.pg.neighbors_by_kind(node_id, EXTERNAL_CALL, direction="out")
                    if self.pg.graph.nodes[n].get("file")}
        related.discard(node_id)
        return FunctionListResult(status="OK", functions=[self._function_ref(n) for n in sorted(related)])

    # -- state reads / writes / modifiers -------------------------------------

    def get_state_reads(self, contract: str, function: str) -> StateVarListResult:
        return self._state_vars(contract, function, STATE_READ)

    def get_state_writes(self, contract: str, function: str, *, include_transitive: bool = True) -> StateVarListResult:
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return StateVarListResult(status=status, reason=reason)
        var_nodes = set(self.pg.neighbors_by_kind(node_id, STATE_WRITE, direction="out"))
        if include_transitive:
            var_nodes |= set(self.pg.neighbors_by_kind(node_id, STATE_WRITE_TRANSITIVE, direction="out"))
        if not var_nodes:
            return StateVarListResult(status="NOT_FOUND", reason=f"no state writes found for {contract}.{function}")
        return StateVarListResult(status="OK", state_vars=[self._statevar_ref(n) for n in sorted(var_nodes)])

    def _state_vars(self, contract: str, function: str, edge_kind: str) -> StateVarListResult:
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return StateVarListResult(status=status, reason=reason)
        var_nodes = self.pg.neighbors_by_kind(node_id, edge_kind, direction="out")
        if not var_nodes:
            return StateVarListResult(status="NOT_FOUND", reason=f"no matching state variables for {contract}.{function}")
        return StateVarListResult(status="OK", state_vars=[self._statevar_ref(n) for n in sorted(var_nodes)])

    def get_modifiers(self, contract: str, function: str) -> ModifierListResult:
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return ModifierListResult(status=status, reason=reason)
        mod_nodes = self.pg.neighbors_by_kind(node_id, USES_MODIFIER, direction="out")
        if not mod_nodes:
            return ModifierListResult(status="NOT_FOUND", reason=f"{contract}.{function} applies no modifiers")
        refs = []
        for n in sorted(mod_nodes):
            data = self.pg.graph.nodes[n]
            refs.append(ModifierRef(node_id=n, contract=data.get("contract"), name=data.get("name"),
                                     file=data.get("file"), lines=data.get("lines") or []))
        return ModifierListResult(status="OK", modifiers=refs)

    # -- inheritance --------------------------------------------------------

    def get_inheritance(self, contract: str) -> InheritanceResult:
        node_id = f"contract::{contract}"
        if node_id not in self.pg.graph:
            return InheritanceResult(status="NOT_FOUND", reason=f"no contract node for {contract!r}")
        bases = self.pg.neighbors_by_kind(node_id, INHERITS, direction="out")
        base_names = [self.pg.graph.nodes[b]["name"] for b in bases]
        return InheritanceResult(status="OK", contract=contract, bases=base_names)

    # -- filesystem -----------------------------------------------------------

    def read_file(self, path: str) -> ReadFileResult:
        try:
            resolved = (self.repo_root / path).resolve()
        except (ValueError, OSError) as e:
            return ReadFileResult(status="ERROR", reason=str(e), path=path)
        if self.repo_root not in resolved.parents and resolved != self.repo_root:
            return ReadFileResult(status="ERROR", reason=f"path {path!r} escapes repo_root", path=path)
        if not resolved.exists():
            return ReadFileResult(status="NOT_FOUND", reason=f"no such file: {path}", path=path)
        try:
            content = resolved.read_text(errors="ignore")
        except (OSError, UnicodeDecodeError) as e:
            return ReadFileResult(status="ERROR", reason=str(e), path=path)
        return ReadFileResult(status="OK", path=str(resolved.relative_to(self.repo_root)), content=content)

    def search_repository(self, pattern: str, *, file_glob: str = "*.sol") -> SearchRepositoryResult:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            return SearchRepositoryResult(status="ERROR", reason=f"invalid regex: {e}")
        hits: list[SearchHit] = []
        truncated = False
        for path in sorted(self.repo_root.rglob(file_glob)):
            if not path.is_file() or path.suffix in _SEARCH_SKIP_EXTS:
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                if regex.search(line):
                    if len(hits) >= _SEARCH_MAX_HITS:
                        truncated = True
                        break
                    hits.append(SearchHit(file=str(path.relative_to(self.repo_root)), line=lineno, text=line.strip()))
            if truncated:
                break
        if not hits:
            return SearchRepositoryResult(status="NOT_FOUND", reason=f"no matches for {pattern!r}")
        return SearchRepositoryResult(status="OK", hits=hits, truncated=truncated)

    # -- node -> typed ref helpers --------------------------------------------

    def _function_ref(self, node_id: str) -> FunctionRef:
        data = self.pg.graph.nodes[node_id]
        return FunctionRef(node_id=node_id, contract=data.get("contract"), name=data.get("name") or node_id,
                            canonical_name=data.get("canonical_name"), file=data.get("file"),
                            lines=data.get("lines") or [], visibility=data.get("visibility"))

    def _statevar_ref(self, node_id: str) -> StateVarRef:
        data = self.pg.graph.nodes[node_id]
        # STATEVAR nodes never carry a direct `file` attribute (a4v.graph
        # never sets one for var:: nodes) -- node_file() resolves it
        # indirectly via the owning contract, same as graph_mcp_server does.
        return StateVarRef(node_id=node_id, contract=data.get("contract"), name=data.get("name") or node_id,
                            type=data.get("type"), file=node_file(self.pg, node_id), lines=data.get("lines") or [])
