"""Arm G: agent-driven graph navigation. Codex starts with only the
candidate's own file visible; further code becomes visible only through
the graph_mcp_server.py MCP tools (investigate/read_source/show_candidate).

See graph_mcp_server.py's own docstring for why this cannot be a
filesystem-enforced restriction the way the prior G1-restricted
experiment was: Codex's own Landlock-based sandbox does not run on this
session's login node (kernel 4.18, predates Landlock's 5.13
introduction -- confirmed via `codex sandbox linux`, which panics).
Enforcement here is therefore detection-based: the MCP server is the
sanctioned reveal path, and divergence (a shell read of a file the graph
tools never revealed) is measured after the fact from the real command
trace, not physically prevented. Disclosed in the preregistration and
report, not hidden.
"""
from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_c_codex import (
    DEFAULT_BASE_URL, DEFAULT_WIRE_API, _extract_last_fenced_json,
    _extract_touched_files, codex_login, compute_cost,
)

ARM_G_PROMPT_PATH = Path(__file__).parent / "ARM_G_PROMPT_v2.md"
"""v2: full-repository access, no graph-gated visibility restriction --
see ARM_G_PROMPT_v2.md's own header for why this supersedes v1. v1 is
kept on disk (not deleted) as the historical record of the earlier
graph-gated-navigation research design; nothing in the live pipeline
loads it anymore."""


def load_frozen_arm_g_prompt() -> str:
    text = ARM_G_PROMPT_PATH.read_text(encoding="utf-8")
    marker = "## ROLE"
    return text[text.index(marker):]


def build_arm_g_prompt(requirement_text: str, context_bundle_text: str, candidate_location: str,
                        evidence_bundle_text: str, unresolved_facts: list[str]) -> str:
    unresolved_block = "\n".join(f"- {f}" for f in unresolved_facts) if unresolved_facts else "(none explicitly stated)"
    body = f"""EthTrust requirement:
{requirement_text}

Applicable context (definitions / parent section / related requirements):
{context_bundle_text}

Candidate location under investigation: {candidate_location}

Initial evidence bundle for this candidate (a starting hypothesis, not ground truth -- you may verify it):
{evidence_bundle_text}

Explicitly unresolved facts noted by the tool that produced this evidence:
{unresolved_block}
"""
    return load_frozen_arm_g_prompt() + "\n\n---\n\n" + body


def write_g_config(home: Path, mcp_command: str, mcp_args: list[str], mcp_env: dict,
                    base_url: str = DEFAULT_BASE_URL, wire_api: str = DEFAULT_WIRE_API) -> None:
    config_dir = home / ".codex"
    config_dir.mkdir(parents=True, exist_ok=True)
    base_url = base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    args_toml = ", ".join(f'"{a}"' for a in mcp_args)
    env_toml = "\n".join(f'{k} = "{v}"' for k, v in mcp_env.items())
    config = (
        'model_provider = "proxy"\n\n'
        "[model_providers.proxy]\n"
        'name = "proxy"\n'
        f'base_url = "{base_url}"\n'
        f'wire_api = "{wire_api}"\n'
        'env_key = "OPENAI_API_KEY"\n\n'
        "[mcp_servers.rtf-graph-navigation]\n"
        f'command = "{mcp_command}"\n'
        f"args = [{args_toml}]\n\n"
        "[mcp_servers.rtf-graph-navigation.env]\n"
        f"{env_toml}\n"
    )
    (config_dir / "config.toml").write_text(config, encoding="utf-8")


@dataclass
class ArmGResult:
    case_id: str
    final_decision: dict | None
    reasoning_text: str
    actual_shell_commands: int
    actual_shell_files_touched: list[str]
    revealed_files: list[str]
    graph_tool_calls: int
    graph_unresolved_events: list[dict]
    max_hop_depth_seen: int | None
    divergent_files: list[str]
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    cost_usd: float
    wall_clock_s: float
    timed_out: bool
    session_log_path: str
    trace_log_path: str


_COPY_IGNORE = shutil.ignore_patterns(".git")


def prepare_full_repo_investigation_dir(repo_root: Path, investigation_dir: Path) -> Path:
    """The full-repository-access fix, isolated as its own testable
    function: a fresh, complete copy of `repo_root` (minus `.git`) at
    `investigation_dir`, which becomes the agent's cwd -- so `ls`/`find`/
    `grep`/`cat`/`sed` see the REAL repository from turn one, not a
    near-empty directory that only grows as graph tools "reveal" files.
    Extracted from `run_arm_g_bundle` specifically so this property (a
    file beyond any fixed-size excerpt cutoff is genuinely reachable) is
    unit-testable without needing a real Codex binary/API key -- see
    `test_agentic_architecture.py`.

    `symlinks=True` -- confirmed necessary by a real, live crash: an
    EVMbench audit clone can accumulate stray symlinks from earlier,
    unrelated tooling runs (found live: a dangling `solc` symlink at
    `2025-01-liquid-ron`'s repo root, pointing into a since-cleaned-up
    prior job's Codex home directory). `shutil.copytree`'s DEFAULT
    behavior (`symlinks=False`) dereferences every symlink and copies the
    TARGET's content, which raises `shutil.Error` outright for a dangling
    one -- aborting the entire investigation before the agent ever starts,
    for a stray artifact with nothing to do with the actual audit source.
    `symlinks=True` copies symlinks AS symlinks (standard `cp -a`/rsync
    semantics for a full tree copy) -- a dangling one just stays a
    harmless dangling symlink in the copy, never a fatal error.
    """
    if investigation_dir.exists():
        shutil.rmtree(investigation_dir)
    shutil.copytree(repo_root, investigation_dir, ignore=_COPY_IGNORE, symlinks=True)
    return investigation_dir


def run_arm_g_bundle(*, codex_bin: Path, python_bin: Path, mcp_server_script: Path,
                      api_key: str, model: str, case_id: str,
                      entry_file: Path, repo_root: Path, candidate_location: str,
                      solc_path_dir: str, solc_remaps: list[str] | None,
                      prompt: str, scratch_root: Path, timeout_s: int = 300) -> ArmGResult:
    """Runs one graph-gated-but-not-graph-RESTRICTED Codex investigation.

    Per the "revisit the RTF architecture" directive: the agent gets REAL,
    full repository access from the start (a full copy of `repo_root`,
    read/write/exec within its own scratch copy, normal shell tools --
    `grep`/`find`/`cat`/`sed`/`ls` all work exactly as they would in the
    real repo), not a near-empty directory that only grows as graph tools
    "reveal" files. Graph-navigation MCP tools remain available as an
    ADDITIONAL structural-query capability (callers/callees/state-read/
    state-write/inheritance), never the exclusive channel. `candidate_
    location` is a best-effort HINT (may be "", or a non-function-shaped
    string like "compiler config" or "project documentation") -- the
    agent is expected to discover the relevant location itself when no
    resolvable hint exists, not blocked from starting because one
    doesn't. See ARM_G_PROMPT_v2.md for the full instruction set.

    A full copy (not the live `repo_root` itself) is used deliberately:
    Codex runs with `--dangerously-bypass-approvals-and-sandbox` (the
    only mode that works on this kernel -- see module docstring) and
    could technically write/delete within its own cwd; giving it its own
    disposable copy means an errant write can't corrupt the actual
    cloned audit repo other entries/predicates still need to read.
    """
    home = scratch_root / f"{case_id}_ghome"
    if home.exists():
        shutil.rmtree(home)
    home.mkdir(parents=True)

    investigation_dir = scratch_root / f"{case_id}_gview"
    prepare_full_repo_investigation_dir(repo_root, investigation_dir)

    # A separate, GUARANTEED-empty neutral cwd for the graph MCP server's
    # own solc compile (see graph_mcp_server.py's GRAPH_SOLC_CWD docstring
    # for why this must be foundry.toml-free) -- investigation_dir is now
    # a full repo copy and WOULD contain a foundry.toml, so it can no
    # longer serve as its own neutral cwd the way the old near-empty
    # investigation_dir incidentally could.
    solc_neutral_cwd = scratch_root / f"{case_id}_solc_neutral"
    if solc_neutral_cwd.exists():
        shutil.rmtree(solc_neutral_cwd)
    solc_neutral_cwd.mkdir(parents=True)

    # entry_file's path relative to the ORIGINAL repo_root, re-anchored
    # onto the copy -- the graph MCP server compiles this file location.
    entry_file_in_copy = investigation_dir / entry_file.resolve().relative_to(repo_root.resolve())

    trace_log_path = scratch_root / f"{case_id}_graph_trace.jsonl"
    trace_log_path.unlink(missing_ok=True)

    mcp_env = {
        "GRAPH_ENTRY_FILE": str(entry_file_in_copy),
        "GRAPH_REPO_ROOT": str(investigation_dir),
        "GRAPH_INVESTIGATION_DIR": str(investigation_dir),
        "GRAPH_CANDIDATE_LOCATION": candidate_location or "",
        "GRAPH_TRACE_LOG_PATH": str(trace_log_path),
        "GRAPH_SOLC_PATH_DIR": solc_path_dir,
        "GRAPH_SOLC_CWD": str(solc_neutral_cwd),
    }
    if solc_remaps:
        # Remaps were collected against the ORIGINAL repo_root; re-anchor
        # each absolute path onto the copy so they still resolve.
        repo_root_resolved = str(repo_root.resolve())
        investigation_dir_resolved = str(investigation_dir.resolve())
        remapped = [
            r.replace(repo_root_resolved, investigation_dir_resolved) if repo_root_resolved in r else r
            for r in solc_remaps
        ]
        mcp_env["GRAPH_SOLC_REMAPS"] = ":".join(remapped)

    write_g_config(home, str(python_bin), [str(mcp_server_script)], mcp_env)
    codex_login(codex_bin, home, api_key)

    out_path = scratch_root / f"{case_id}_gout.txt"
    log_path = scratch_root / f"{case_id}_gstream.jsonl"
    out_path.unlink(missing_ok=True)
    log_path.unlink(missing_ok=True)

    cmd = [
        str(codex_bin), "exec",
        "--model", model,
        "--dangerously-bypass-approvals-and-sandbox",  # only mode that works on this kernel; see module docstring
        "--skip-git-repo-check",
        "-C", str(investigation_dir),
        "-o", str(out_path), "--json",
        prompt,
    ]
    env = {"HOME": str(home), "OPENAI_API_KEY": api_key, "CODEX_API_KEY": api_key,
           "PATH": "/usr/bin:/bin"}

    start = time.time()
    timed_out = False
    with open(log_path, "w") as logf:
        try:
            subprocess.run(cmd, cwd=str(investigation_dir), env=env,
                            stdout=logf, stderr=subprocess.STDOUT,
                            timeout=timeout_s, check=False)
        except subprocess.TimeoutExpired:
            timed_out = True
    wall_clock_s = time.time() - start

    import json
    commands: list[str] = []
    files_touched: list[str] = []
    input_tokens = cached_input_tokens = output_tokens = 0
    agent_message_text = ""
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = ev.get("item") or {}
            if ev.get("type") == "item.completed" and item.get("type") == "command_execution":
                cmd_text = item.get("command", "")
                commands.append(cmd_text)
                files_touched.extend(_extract_touched_files(cmd_text))
            if ev.get("type") == "item.completed" and item.get("type") == "agent_message":
                agent_message_text += item.get("text", "")
            if ev.get("type") == "turn.completed":
                usage = ev.get("usage", {})
                input_tokens = usage.get("input_tokens", input_tokens)
                cached_input_tokens = usage.get("cached_input_tokens", cached_input_tokens)
                output_tokens = usage.get("output_tokens", output_tokens)

    final_text = out_path.read_text(encoding="utf-8", errors="replace") if out_path.exists() else agent_message_text
    final_decision = _extract_last_fenced_json(final_text)

    graph_tool_calls = 0
    graph_unresolved: list[dict] = []
    revealed_files: set[str] = set()
    if trace_log_path.exists():
        for line in trace_log_path.read_text().splitlines():
            if not line.strip():
                continue
            ev = json.loads(line)
            graph_tool_calls += 1
            result = ev.get("result", {})
            if result.get("status") == "GRAPH_UNRESOLVED":
                graph_unresolved.append({"tool": ev["tool"], "args": ev.get("args"), "reason": result.get("reason")})
            for n in result.get("nodes", []):
                if n.get("file"):
                    revealed_files.add(n["file"])
            if result.get("file"):
                revealed_files.add(result["file"])

    revealed_basenames = {Path(f).name for f in revealed_files}
    divergent = sorted({f for f in files_touched if Path(f).name not in revealed_basenames})

    cost = compute_cost(input_tokens, cached_input_tokens, output_tokens)

    return ArmGResult(
        case_id=case_id, final_decision=final_decision, reasoning_text=agent_message_text,
        actual_shell_commands=len(commands), actual_shell_files_touched=sorted(set(files_touched)),
        revealed_files=sorted(revealed_files), graph_tool_calls=graph_tool_calls,
        graph_unresolved_events=graph_unresolved, max_hop_depth_seen=None,
        divergent_files=divergent, input_tokens=input_tokens, cached_input_tokens=cached_input_tokens,
        output_tokens=output_tokens, cost_usd=cost, wall_clock_s=wall_clock_s, timed_out=timed_out,
        session_log_path=str(log_path), trace_log_path=str(trace_log_path),
    )
