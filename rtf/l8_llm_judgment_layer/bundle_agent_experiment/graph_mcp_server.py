"""Graph-navigation MCP server for Arm G (agent-driven graph navigation).

Runs as a SEPARATE process, launched by `codex mcp add` -- deliberately NOT
subject to the per-shell-command sandbox Codex CLI would otherwise apply,
because that sandbox (Landlock+seccomp) does not work at all on this
session's login node (kernel 4.18, predates Landlock's 5.13 introduction --
confirmed live via `codex sandbox linux`, which panics with
"error applying legacy Linux sandbox restrictions"). Because of that, this
experiment cannot filesystem-enforce Codex's shell-level file access the
way the prior G1-restricted experiment did (copy only the allowed files
into an isolated directory, then run fully sandboxed) -- Codex still runs
with `--dangerously-bypass-approvals-and-sandbox` (the only mode that
works here), so its shell COULD read anything on disk regardless of what
this server reveals.

This server is instead the *sanctioned* path: it is the only way new files
are meant to become visible, and the harness measures (does not merely
assume) compliance -- see AGENT_DRIVEN_GRAPH_NAVIGATION_EXPERIMENT.md's
divergence analysis for how a shell read of a never-revealed file is
detected after the fact via arm_c_codex.py's existing command-parsing
harness. This tradeoff (detection instead of prevention) is disclosed
explicitly in the preregistration and report, not hidden.

Env vars (set by the harness when registering this server per bundle):
  GRAPH_ENTRY_FILE       -- path to compile as the ProgramGraph.build() target
  GRAPH_SOLC_REMAPS      -- optional, ':'-joined solc remaps
  GRAPH_REPO_ROOT        -- root the investigation_dir's relative paths are computed against
  GRAPH_INVESTIGATION_DIR -- where revealed files get copied to
  GRAPH_CANDIDATE_LOCATION -- RTF's "Contract.function" location string
  GRAPH_TRACE_LOG_PATH   -- append-only JSONL of every tool call + result (harness-authoritative)
  GRAPH_SOLC_PATH_DIR    -- directory containing a `solc` binary to prepend to PATH before compiling
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
    CALLS, EXTERNAL_CALL, FUNCTION, INHERITS, STATE_READ, STATE_WRITE,
    STATE_WRITE_TRANSITIVE, STATEVAR, USES_MODIFIER, WRITE_AFTER_EXTERNAL_CALL,
    ProgramGraph,
)
from a4v.slice import numbered_source, _excerpt  # noqa: E402
from mcp.server import MCPServer  # noqa: E402

ENTRY_FILE = os.environ["GRAPH_ENTRY_FILE"]
REMAPS = os.environ.get("GRAPH_SOLC_REMAPS", "").split(":") if os.environ.get("GRAPH_SOLC_REMAPS") else None
REPO_ROOT = Path(os.environ["GRAPH_REPO_ROOT"]).resolve()
INVESTIGATION_DIR = Path(os.environ["GRAPH_INVESTIGATION_DIR"])
CANDIDATE_LOCATION = os.environ["GRAPH_CANDIDATE_LOCATION"]
TRACE_LOG_PATH = Path(os.environ["GRAPH_TRACE_LOG_PATH"])

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


def _get_graph() -> ProgramGraph:
    global _pg_cache
    if _pg_cache is None:
        _pg_cache = ProgramGraph.build(ENTRY_FILE, solc_remaps=REMAPS)
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


def _get_seed() -> str:
    global _seed_cache
    if _seed_cache is None:
        pg = _get_graph()
        prefix = f"fn::{CANDIDATE_LOCATION}("
        candidates = [n for n, d in pg.graph.nodes(data=True) if d.get("kind") == FUNCTION and n.startswith(prefix)]
        if len(candidates) != 1:
            raise ValueError(f"cannot uniquely resolve candidate {CANDIDATE_LOCATION!r}: {candidates}")
        _seed_cache = candidates[0]
    return _seed_cache


def _node_file(node: str) -> str | None:
    pg = _get_graph()
    data = pg.graph.nodes[node]
    f = data.get("file")
    if f:
        return f
    if data.get("kind") == STATEVAR:
        owner = node.removeprefix("var::").rsplit(".", 1)[0]
        cnode = f"contract::{owner}"
        if cnode in pg.graph:
            return pg.graph.nodes[cnode].get("file")
    return None


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
    """Reveals the candidate function's own file and returns its source excerpt and node id. Call this first."""
    pg = _get_graph()
    seed = _get_seed()
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
