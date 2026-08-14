"""Graph-navigation MCP server for the RTF agent investigation (formerly
"Arm G", now the PRODUCTION path for every AGENT_REQUIRED_REQ_IDS
requirement -- see `registry.py`).

**Architecture as of the "revisit the RTF architecture" redesign**: this
server is a SUPPLEMENTARY structural-query capability, not the exclusive
or "sanctioned" channel for file visibility. `arm_g_codex.run_arm_g_bundle`
now gives the agent a full copy of the repository from the start (its own
`GRAPH_INVESTIGATION_DIR`, which is also where the agent's shell already
runs) -- `ls`/`find`/`grep`/`cat`/`sed` all work over the real repository
immediately, with no reveal-gating. This server's `investigate`/
`read_source`/`show_candidate` tools remain genuinely useful for
STRUCTURAL questions a grep can't easily answer (real caller/callee/
state-read/state-write/inheritance/external-call edges from the actual
compiled program graph, not text pattern matching) -- but failing to
resolve a candidate, or never calling these tools at all, must never
block or diminish an investigation. `candidate_location` is a best-effort
HINT (may be empty, or a non-function-shaped string like "compiler
config") -- see `_get_seed()`'s graceful-failure handling.

Runs as a SEPARATE process, launched by `codex mcp add` -- deliberately
NOT subject to the per-shell-command sandbox Codex CLI would otherwise
apply, because that sandbox (Landlock+seccomp) does not work at all on
this session's login node (kernel 4.18, predates Landlock's 5.13
introduction -- confirmed live via `codex sandbox linux`, which panics
with "error applying legacy Linux sandbox restrictions"). Codex runs with
`--dangerously-bypass-approvals-and-sandbox` (the only mode that works
here) inside its own disposable repository copy (see
`arm_g_codex.run_arm_g_bundle`'s docstring for why a copy, not the live
repo).

Historical note: an EARLIER version of this module (see
AGENT_DRIVEN_GRAPH_NAVIGATION_EXPERIMENT.md) deliberately restricted
initial visibility to test whether graph-mediated navigation alone
sufficiently informs an investigation, treating any shell read of a
never-"revealed" file as a measured protocol violation. That was a valid
research design for that specific question, but is NOT the production
architecture -- artificially restricting what the agent can see was
identified as a real failure mode (an evidence-construction bug caused a
real missed finding by truncating a file before the agent could ever see
the relevant function) and is deliberately removed here.

Env vars (set by the harness when registering this server per bundle):
  GRAPH_ENTRY_FILE       -- path to compile as the ProgramGraph.build() target (inside the repo copy)
  GRAPH_SOLC_REMAPS      -- optional, ':'-joined solc remaps (re-anchored onto the repo copy)
  GRAPH_REPO_ROOT        -- the repo copy root (same as GRAPH_INVESTIGATION_DIR)
  GRAPH_INVESTIGATION_DIR -- the repo copy root the agent's shell already has full access to
  GRAPH_CANDIDATE_LOCATION -- best-effort hint, "Contract.function" or "" if none available
  GRAPH_TRACE_LOG_PATH   -- append-only JSONL of every tool call + result (harness-authoritative, for observability)
  GRAPH_SOLC_PATH_DIR    -- directory containing a `solc` binary to prepend to PATH before compiling
  GRAPH_SOLC_CWD         -- optional: cwd to compile with, matching
                            `compile_helper.compile_evmbench_target`'s
                            neutral-cwd Foundry-autodetection guard (a
                            directory with no `foundry.toml` reachable from
                            it). Without this, `ProgramGraph.build`'s
                            underlying compile is at risk of the same
                            "stack too deep" divergence confirmed live on
                            canto's LendingLedger.sol when the deterministic
                            L5 compile (neutral cwd) and this graph compile
                            (no cwd override) picked up Foundry autodetection
                            differently. Falls back to the process's own cwd
                            if unset, matching prior behavior exactly.
  GRAPH_COMPILE_VIA_FOUNDRY -- optional, "1" to activate. When set, `_get_graph()`
                            builds the graph from the investigation copy's OWN
                            already-compiled Foundry artifacts
                            (`Slither(INVESTIGATION_DIR, foundry_ignore_compile=True,
                            compile_force_framework="Foundry")` ->
                            `ProgramGraph.from_slither`) instead of an
                            independent `ProgramGraph.build(ENTRY_FILE, ...)`
                            second compile -- see
                            RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md SS11-SS13.
                            This is what makes a property generated from a
                            sibling contract the entry file doesn't import
                            (visible only because generation used whole-
                            project Foundry compilation) structurally
                            resolvable during investigation too -- without
                            this, `ProgramGraph.build(ENTRY_FILE, ...)`
                            rebuilds from ENTRY_FILE's own narrower import
                            graph regardless of how generation compiled,
                            and the sibling is never in the resulting graph
                            at all. Unset/"0" (the default): completely
                            unchanged old behavior.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT_PY = "/scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2"
sys.path.insert(0, REPO_ROOT_PY)

if os.environ.get("GRAPH_SOLC_PATH_DIR"):
    os.environ["PATH"] = f"{os.environ['GRAPH_SOLC_PATH_DIR']}:{os.environ.get('PATH', '')}"

from a4v.graph import (  # noqa: E402
    CALLS, EXTERNAL_CALL, STATE_READ, STATE_WRITE,
    STATE_WRITE_TRANSITIVE, STATEVAR, USES_MODIFIER, WRITE_AFTER_EXTERNAL_CALL,
    ProgramGraph,
)
from a4v.slice import numbered_source, _excerpt  # noqa: E402
from mcp.server import MCPServer  # noqa: E402
from rtf.l8_llm_judgment_layer.graph_navigation import (  # noqa: E402
    node_file as _shared_node_file, resolve_seed_node,
)
from slither import Slither  # noqa: E402

ENTRY_FILE = os.environ["GRAPH_ENTRY_FILE"]
REMAPS = os.environ.get("GRAPH_SOLC_REMAPS", "").split(":") if os.environ.get("GRAPH_SOLC_REMAPS") else None
REPO_ROOT = Path(os.environ["GRAPH_REPO_ROOT"]).resolve()
INVESTIGATION_DIR = Path(os.environ["GRAPH_INVESTIGATION_DIR"])
CANDIDATE_LOCATION = os.environ["GRAPH_CANDIDATE_LOCATION"]
TRACE_LOG_PATH = Path(os.environ["GRAPH_TRACE_LOG_PATH"])
SOLC_CWD = os.environ.get("GRAPH_SOLC_CWD") or None
GRAPH_COMPILE_VIA_FOUNDRY = os.environ.get("GRAPH_COMPILE_VIA_FOUNDRY", "") == "1"

INVESTIGATION_DIR.mkdir(parents=True, exist_ok=True)
TRACE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Lazily built, not at import time: a real repository's Slither compile
# (PoolTogether: ~9.4s, confirmed live) can exceed codex's MCP handshake
# timeout if it blocks server startup -- confirmed live as the actual
# cause of the first PoolTogether Arm G attempt showing zero available
# MCP tools at all (codex's own `list_mcp_resources`/`list_mcp_resource_
# templates` calls came back empty; the model correctly, honestly
# reported INSUFFICIENT_EVIDENCE given no tools were exposed -- a real
# harness bug in this experiment's own new code, not a4v/graph.py, and
# not evidence about Codex or the graph itself). Fixed by deferring the
# build to the first actual tool call, after the server has already
# completed its MCP initialize handshake.
_pg_cache: ProgramGraph | None = None


def _build_graph_for_investigation(
    investigation_dir: Path,
    entry_file: str,
    compile_via_foundry: bool,
    solc_remaps: list[str] | None,
    extra_kwargs: dict | None,
) -> ProgramGraph:
    """Build the investigation graph from the selected compilation view.

    Foundry mode reads the build-info already copied into the investigation
    directory and deliberately never calls ``ProgramGraph.build``.  The
    legacy branch remains the original single-entry compilation path.
    """
    if compile_via_foundry:
        slither = Slither(
            str(investigation_dir),
            foundry_ignore_compile=True,
            compile_force_framework="Foundry",
        )
        return ProgramGraph.from_slither(slither)
    return ProgramGraph.build(entry_file, solc_remaps=solc_remaps, extra_kwargs=extra_kwargs)


def _get_graph() -> ProgramGraph:
    global _pg_cache
    if _pg_cache is None:
        extra_kwargs = {"cwd": SOLC_CWD} if SOLC_CWD else None
        _pg_cache = _build_graph_for_investigation(
            INVESTIGATION_DIR, ENTRY_FILE, GRAPH_COMPILE_VIA_FOUNDRY,
            REMAPS, extra_kwargs,
        )
    return _pg_cache


RELATION_MAP = {
    "CALLEES": (CALLS, "out"),
    "EXTERNAL_TARGETS": (EXTERNAL_CALL, "out"),
    "INTERFACES": (EXTERNAL_CALL, "out"),
    "MODIFIERS": (USES_MODIFIER, "out"),
    "STATE_READS": (STATE_READ, "out"),
    "STATE_WRITES": (STATE_WRITE, "out"),
    "STATE_WRITES_TRANSITIVE": (STATE_WRITE_TRANSITIVE, "out"),
    "WRITE_AFTER_EXTERNAL_CALL": (WRITE_AFTER_EXTERNAL_CALL, "out"),
    "WRITERS_OF_STATE": ((STATE_WRITE, STATE_WRITE_TRANSITIVE), "in"),
    "CALLERS": ((CALLS, EXTERNAL_CALL), "in"),
}


_seed_cache: str | None = None
_seed_resolution_error: str | None = None
_seed_attempted = False


def _get_seed() -> str | None:
    """Best-effort candidate resolution -- NOT a precondition for the agent
    to do anything else. Per the "revisit the RTF architecture" directive,
    `candidate_location` is a HINT, possibly empty or non-function-shaped
    (e.g. "compiler config", "project documentation"); failing to resolve
    it must never block the investigation, only mean `show_candidate()`
    has nothing pre-identified to hand back. Resolution logic itself is
    unchanged (`graph_navigation.resolve_seed_node`, shared with
    `pipeline_e2e.py`) -- only the caller's reaction to failure changed
    (graceful `None`, not a crash).
    """
    global _seed_cache, _seed_resolution_error, _seed_attempted
    if _seed_attempted:
        return _seed_cache
    _seed_attempted = True
    if not CANDIDATE_LOCATION:
        _seed_resolution_error = "no candidate_location hint was provided for this requirement"
        return None
    try:
        _seed_cache = resolve_seed_node(_get_graph(), CANDIDATE_LOCATION)
    except Exception as e:  # noqa: BLE001 -- any resolution failure (zero match, ambiguous, etc.) degrades to "no hint", never a crash
        _seed_resolution_error = f"{type(e).__name__}: {e}"
    return _seed_cache


def _node_file(node: str) -> str | None:
    return _shared_node_file(_get_graph(), node)


def _reveal(file_path: str) -> str | None:
    """Copies file_path into INVESTIGATION_DIR, preserving its path relative
    to REPO_ROOT. Returns the relative path, or None if file_path is outside
    REPO_ROOT (shouldn't happen for a correctly-compiled project, logged if
    it does rather than silently skipped)."""
    try:
        rel = Path(file_path).resolve().relative_to(REPO_ROOT)
    except ValueError:
        return None
    dest = INVESTIGATION_DIR / rel
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(file_path, dest)
    return str(rel)


def _log(event: dict) -> None:
    with TRACE_LOG_PATH.open("a") as f:
        f.write(json.dumps(event) + "\n")


def _node_summary(node: str) -> dict:
    pg = _get_graph()
    data = pg.graph.nodes[node]
    f = _node_file(node)
    revealed_rel = _reveal(f) if f else None
    return {
        "node_id": node,
        "kind": data.get("kind"),
        "name": data.get("name"),
        "file": revealed_rel,
        "lines": data.get("lines"),
    }


mcp = MCPServer("rtf-graph-navigation")


@mcp.tool()
def show_candidate() -> dict:
    """Reveals the candidate function's own file and returns its source
    excerpt and node id, IF a resolvable candidate hint exists for this
    requirement. Call this first -- but a `NO_CANDIDATE_HINT` response is
    a legitimate, expected outcome (not an error): many requirements have
    no single function-shaped candidate at all (documentation review,
    broad design properties, project-wide checks). When this happens, you
    already have the whole repository available through your normal file
    tools (`ls`, `find`, `grep`, `cat`, `sed`) -- start there instead;
    discovering the relevant location yourself is part of the
    investigation, not a blocker."""
    seed = _get_seed()
    if seed is None:
        result = {"status": "NO_CANDIDATE_HINT", "reason": _seed_resolution_error,
                   "guidance": "No pre-identified candidate location for this requirement. "
                               "Explore the repository directly with your normal file tools "
                               "(ls/find/grep/cat/sed) to find the relevant code, "
                               "README/docs/NatSpec, or configuration."}
        _log({"tool": "show_candidate", "args": {}, "result": result})
        return result
    pg = _get_graph()
    summary = _node_summary(seed)
    data = pg.graph.nodes[seed]
    excerpt = _excerpt(data)
    result = {**summary, "source": numbered_source(excerpt, min(data.get("lines") or [1])) if excerpt else None}
    _log({"tool": "show_candidate", "args": {}, "result": result})
    return result


@mcp.tool()
def investigate(node_id: str, relation: str, unresolved_fact: str, why_needed: str) -> dict:
    """Follows a structural relation (one of: CALLERS, CALLEES, EXTERNAL_TARGETS,
    INTERFACES, MODIFIERS, STATE_READS, STATE_WRITES, STATE_WRITES_TRANSITIVE,
    WRITERS_OF_STATE, WRITE_AFTER_EXTERNAL_CALL) from node_id (a node id you
    already have, e.g. from show_candidate or a prior investigate call).
    unresolved_fact and why_needed are short strings stating what you're
    trying to determine and why this specific relation should help -- logged
    for auditability, not otherwise enforced. Returns the connected nodes,
    revealing their files as a side effect (they become readable via your
    normal file tools). If the relation cannot be resolved (an unresolved
    external target, a low-level call with no specific target, a missing
    graph edge, etc.), returns {"status": "GRAPH_UNRESOLVED", "reason": "..."}
    instead -- this is a legitimate, expected outcome, not an error; do not
    retry the same request when you see it.
    """
    pg = _get_graph()
    if node_id not in pg.graph:
        result = {"status": "GRAPH_UNRESOLVED", "reason": f"unknown node_id {node_id!r}"}
        _log({"tool": "investigate", "args": locals_args(node_id, relation, unresolved_fact, why_needed), "result": result})
        return result
    if relation not in RELATION_MAP:
        result = {"status": "GRAPH_UNRESOLVED", "reason": f"unsupported relation {relation!r}; allowed: {sorted(RELATION_MAP)}"}
        _log({"tool": "investigate", "args": locals_args(node_id, relation, unresolved_fact, why_needed), "result": result})
        return result

    kinds, direction = RELATION_MAP[relation]
    kinds = (kinds,) if isinstance(kinds, str) else kinds
    neighbors: list[str] = []
    for k in kinds:
        neighbors.extend(pg.neighbors_by_kind(node_id, k, direction=direction))
    neighbors = sorted(set(neighbors))

    resolved = [_node_summary(n) for n in neighbors if _node_file(n)]
    unresolved_targets = [n for n in neighbors if not _node_file(n)]

    if not resolved and not unresolved_targets:
        result = {"status": "GRAPH_UNRESOLVED",
                   "reason": f"no {relation} edges found from {node_id} -- either genuinely none exist "
                              f"(e.g. a leaf function with no callers) or the construct is not represented "
                              f"in the graph (see PROGRAM_GRAPH_RELEVANCE_BOUNDARY_EXPERIMENT.md's capability matrix)"}
    elif not resolved and unresolved_targets:
        result = {"status": "GRAPH_UNRESOLVED",
                   "reason": f"{relation} from {node_id} resolves only to unrepresented targets "
                              f"({unresolved_targets}) -- likely an unresolved external interface call or a "
                              f"low-level call (.call/.delegatecall/.staticcall) with no specific target in the graph"}
    else:
        result = {"status": "OK", "nodes": resolved}
        if unresolved_targets:
            result["also_unresolved"] = unresolved_targets

    _log({"tool": "investigate", "args": locals_args(node_id, relation, unresolved_fact, why_needed), "result": result})
    return result


@mcp.tool()
def read_source(node_id: str) -> dict:
    """Returns the numbered source excerpt for a node you have already
    reached (via show_candidate or investigate). Also reveals its file as a
    side effect if not already visible."""
    pg = _get_graph()
    if node_id not in pg.graph:
        result = {"status": "GRAPH_UNRESOLVED", "reason": f"unknown node_id {node_id!r}"}
        _log({"tool": "read_source", "args": {"node_id": node_id}, "result": result})
        return result
    data = pg.graph.nodes[node_id]
    excerpt = _excerpt(data)
    if not excerpt:
        result = {"status": "GRAPH_UNRESOLVED", "reason": f"no source excerpt available for {node_id!r}"}
    else:
        summary = _node_summary(node_id)
        result = {**summary, "source": numbered_source(excerpt, min(data.get("lines") or [1]))}
    _log({"tool": "read_source", "args": {"node_id": node_id}, "result": result})
    return result


def locals_args(node_id, relation, unresolved_fact, why_needed):
    return {"node_id": node_id, "relation": relation, "unresolved_fact": unresolved_fact, "why_needed": why_needed}


if __name__ == "__main__":
    mcp.run()
