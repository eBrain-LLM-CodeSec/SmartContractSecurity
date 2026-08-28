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

import inspect
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
from rtf.security_agent.evidence_store import EvidenceStore, UnknownEvidenceRefError

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


class ReadEvidenceResult(BaseModel):
    status: ToolStatus
    reason: str | None = None
    evidence_id: str | None = None
    content: str | None = None


_SEARCH_MAX_HITS = 200
_SEARCH_SKIP_EXTS = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".sif", ".zip", ".gz", ".so", ".o"}


class SecurityAgentTools:
    """One instance per cluster investigation, wrapping one already-built
    `ProgramGraph` plus the repo root it was compiled from. `repo_root`
    bounds `read_file`/`search_repository` -- the one real system-boundary
    validation this class does (an LLM-driven tool call is untrusted
    input in the sense that matters: a path that escapes the repo it's
    supposed to be investigating), everything else trusts the graph.

    `evidence_store`, when given, backs the `read_evidence` tool
    (RTF_SECURITY_AGENT_CONTEXT_MANAGEMENT_DESIGN.md section 4) -- the
    kernel is what actually STORES tool results there (it owns id
    generation via state.record_tool_call); this class only needs a
    reference to READ them back out on request. `None` (the default)
    disables `read_evidence` entirely -- callers that don't wire an
    EvidenceStore in get the exact same tool surface as before."""

    def __init__(self, program_graph: ProgramGraph, repo_root: Path,
                 evidence_store: "EvidenceStore | None" = None):
        self.pg = program_graph
        self.repo_root = repo_root.resolve()
        self.evidence_store = evidence_store

    # -- construction --------------------------------------------------------

    @classmethod
    def build(cls, repo_root: Path, entry_file: str | Path | None = None, *,
              compile_via_foundry: bool = False,
              solc_remaps: list[str] | None = None,
              extra_compile_kwargs: dict | None = None,
              evidence_store: "EvidenceStore | None" = None) -> "SecurityAgentTools":
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
        return cls(pg, repo_root, evidence_store=evidence_store)

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
        """Numbered source of one function, by contract+function name."""
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return SourceExcerptResult(status=status, reason=reason)
        return self._source_excerpt_for_node(node_id)

    def get_contract_source(self, contract: str) -> SourceExcerptResult:
        """Numbered source of an entire contract, by name."""
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
        """Functions (internal or via an external interface) that call this one."""
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return FunctionListResult(status=status, reason=reason)
        callers = set(self.pg.neighbors_by_kind(node_id, CALLS, direction="in"))
        callers |= set(self.pg.neighbors_by_kind(node_id, EXTERNAL_CALL, direction="in"))
        return FunctionListResult(status="OK", functions=[self._function_ref(n) for n in sorted(callers)])

    def get_callees(self, contract: str, function: str) -> FunctionListResult:
        """Internal/library functions this function calls."""
        node_id, status, reason = self._resolve_function(contract, function)
        if status != "OK":
            return FunctionListResult(status=status, reason=reason)
        callees = set(self.pg.neighbors_by_kind(node_id, CALLS, direction="out"))
        return FunctionListResult(status="OK", functions=[self._function_ref(n) for n in sorted(callees)])

    def get_external_calls(self, contract: str, function: str) -> ExternalCallListResult:
        """Cross-contract/interface/low-level calls this function makes."""
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
        """One-hop union of callers + callees + resolved external-call
        targets -- a single starting point for "what else is relevant
        here" without calling three separate tools first."""
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
        """State variables this function reads."""
        return self._state_vars(contract, function, STATE_READ)

    def get_state_writes(self, contract: str, function: str, *, include_transitive: bool = True) -> StateVarListResult:
        """State variables this function writes, directly or (by default)
        transitively via internal/library calls it makes."""
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
        """Modifiers applied to this function (e.g. onlyOwner)."""
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
        """Base contracts this contract inherits from."""
        node_id = f"contract::{contract}"
        if node_id not in self.pg.graph:
            return InheritanceResult(status="NOT_FOUND", reason=f"no contract node for {contract!r}")
        bases = self.pg.neighbors_by_kind(node_id, INHERITS, direction="out")
        base_names = [self.pg.graph.nodes[b]["name"] for b in bases]
        return InheritanceResult(status="OK", contract=contract, bases=base_names)

    # -- filesystem -----------------------------------------------------------

    def read_file(self, path: str) -> ReadFileResult:
        """Raw content of a file, by path relative to the repo root."""
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
        """Regex search over repository files (default: all .sol files),
        returning matching file/line/text hits."""
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

    def read_evidence(self, evidence_id: str | None = None) -> ReadEvidenceResult:
        """Retrieves the FULL raw content behind a compact evidence
        summary the kernel showed earlier (RTF_SECURITY_AGENT_CONTEXT_
        MANAGEMENT_DESIGN.md section 4) -- e.g. the complete source of a
        contract that was summarized/truncated in the conversation.
        Returns an ERROR status (not a crash) if no EvidenceStore was
        configured for this investigation, and NOT_FOUND for an unknown
        evidence_id -- both are normal tool outcomes, not exceptions.

        `evidence_id` defaults to None (real bug found live, 2026-08-26):
        the tool schema marks it required, but the model still called
        this with no arguments at all 3 times in one real cluster --
        this proxy doesn't hard-enforce required-argument completeness
        the way `strict: true` is documented to. Previously that produced
        a hard argument-binding failure with no hint of what to pass
        instead, so the model just repeated the same empty call. Handling
        None explicitly here lets the error message list the evidence
        ids that actually exist, so the model can self-correct on its
        very next attempt instead of guessing blindly."""
        if self.evidence_store is None:
            return ReadEvidenceResult(status="ERROR", reason="no evidence store configured for this investigation")
        if evidence_id is None:
            known = self.evidence_store.known_ids()
            return ReadEvidenceResult(
                status="ERROR",
                reason=f"evidence_id is required. Evidence ids available so far: {known or '(none yet)'}",
            )
        try:
            content = self.evidence_store.read(evidence_id)
        except UnknownEvidenceRefError:
            known = self.evidence_store.known_ids()
            return ReadEvidenceResult(
                status="NOT_FOUND",
                reason=f"no stored evidence for id {evidence_id!r}. Evidence ids available so far: {known or '(none yet)'}",
            )
        return ReadEvidenceResult(status="OK", evidence_id=evidence_id, content=content)

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

    # -- generic dispatch (for the kernel's tool-calling loop) ----------------

    TOOL_NAMES: "frozenset[str]" = frozenset({
        "get_function_source", "get_contract_source", "get_callers", "get_callees",
        "get_external_calls", "get_related_functions", "get_state_reads",
        "get_state_writes", "get_modifiers", "get_inheritance", "read_file", "search_repository",
        "read_evidence",
    })
    """Whitelist, not just a convenience list: `call()` dispatches by name
    ONLY through this set, so a model-supplied tool name can never reach
    `build`/private helpers/dunder methods -- the one real safety boundary
    on an otherwise-generic name->method dispatch."""

    def call(self, tool_name: str, args: dict) -> dict:
        """Generic dispatch for the kernel's tool-calling loop: validates
        `tool_name` against TOOL_NAMES, binds `args` against the real
        method signature (so a wrong/missing/extra argument is reported
        as a normal tool error, never a crash), and returns a plain JSON-
        serializable dict either way -- always feedable straight back
        into a chat message."""
        if tool_name not in self.TOOL_NAMES:
            return {"status": "ERROR", "reason": f"unknown tool {tool_name!r}; available: {sorted(self.TOOL_NAMES)}"}
        method = getattr(self, tool_name)
        try:
            bound = inspect.signature(method).bind(**args)
        except TypeError as e:
            return {"status": "ERROR", "reason": f"invalid arguments for {tool_name}({args}): {e}"}
        result = method(*bound.args, **bound.kwargs)
        return result.model_dump()


_JSON_SCHEMA_TYPE_BY_ANNOTATION = {"str": "string", "bool": "boolean", "int": "integer", "float": "number"}
"""Keyed by the annotation's STRING form, not the real type object: this
module has `from __future__ import annotations` (PEP 563) at the top, so
`inspect.signature(...).parameters[...].annotation` is always the raw
string `"bool"`/`"str"`/etc., never the actual `bool`/`str` type --
found live while adding `build_tool_schemas()` (a `str`-typed param
happened to still resolve correctly by accident, via the "string"
fallback below; `bool` did not, since its wrong fallback is also
"string")."""


def build_tool_schemas() -> list[dict]:
    """One native `tools=[...]` entry (OpenAI Responses-API function-
    calling shape, live-verified against z-ai/glm-5.2 in Part 0 of the
    native-tool-calling migration) per whitelisted tool, derived from the
    real method signature -- same "never a hand-maintained parallel
    copy" discipline as `describe_tools()`.

    Every declared parameter is listed in `required` unconditionally,
    including the two keyword-only-with-default cases
    (`get_state_writes.include_transitive: bool = True`,
    `search_repository.file_glob: str = "*.sol"`) -- NOT a change to what
    values are valid or what `SecurityAgentTools.call`'s own defaults are,
    only to whether the model may omit the key entirely. Real,
    live-blocking incompatibility found during the GPT-5.6 Sol controlled
    test (2026-08-27): OpenAI/Azure's own strict-mode function-calling
    validator rejects a `strict: true` schema that excludes any declared
    property from `required` outright (`400 invalid_function_parameters`,
    "'required' is required to be... an array including every key in
    properties") -- z-ai/glm-5.2/5.3 tolerate the omission loosely, but
    that is provider leniency, not a documented guarantee. This fix was
    first validated in isolation (a throwaway pinned checkout used for
    the GLM-5.3/GPT-5.6-Sol capability-test harness) before being applied
    here, permanently, to the committed kernel -- a wire-contract change
    with no effect on tool semantics or defaults, needed for ANY
    OpenAI-family model (including Sol) to run against this kernel at all."""
    schemas = []
    for name in sorted(SecurityAgentTools.TOOL_NAMES):
        method = getattr(SecurityAgentTools, name)
        sig = inspect.signature(method)
        properties: dict[str, dict] = {}
        required: list[str] = []
        for pname, param in sig.parameters.items():
            if pname == "self":
                continue
            json_type = _JSON_SCHEMA_TYPE_BY_ANNOTATION.get(str(param.annotation), "string")
            properties[pname] = {"type": json_type}
            required.append(pname)
        doc = (method.__doc__ or "").strip().splitlines()[0] if method.__doc__ else ""
        schemas.append({
            "type": "function",
            "name": name,
            "description": doc,
            "parameters": {
                "type": "object", "properties": properties, "required": required,
                "additionalProperties": False,
            },
            "strict": True,
        })
    return schemas


def describe_tools() -> str:
    """One line per whitelisted tool: `name(params) -- first docstring
    line`. Generated from the real method signatures/docstrings (not a
    hand-maintained parallel copy) so the prompt layer can never drift
    from what `SecurityAgentTools.call` actually accepts."""
    lines = []
    for name in sorted(SecurityAgentTools.TOOL_NAMES):
        method = getattr(SecurityAgentTools, name)
        sig = inspect.signature(method)
        params = ", ".join(p for p in sig.parameters if p != "self")
        doc = (method.__doc__ or "").strip().splitlines()[0] if method.__doc__ else ""
        lines.append(f"- {name}({params}) -- {doc}")
    return "\n".join(lines)
