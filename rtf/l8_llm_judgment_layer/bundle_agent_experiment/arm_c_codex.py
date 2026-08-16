"""Arm C: the REAL Codex CLI (not a hand-built imitation), one fresh
session per bundle. Adapts the exact invocation pattern this project's
own production worker pipeline already uses
(evmbench `repo/.claude/worktrees/evmbench-jubail-singularity-backend/
backend/worker_runner/common.py::build_codex_cmd`/`run_codex_stage` and
`docker/worker/init.py::_write_codex_proxy_config`) rather than
reinventing it -- verified against that source before writing this file.

Key differences from that production pipeline, all deliberate for this
experiment:
  - runs standalone on this login node (binary downloaded directly from
    the codex GitHub releases, musl static build to avoid libssl.so.3),
    not inside the SLURM+Singularity worker stack -- confirmed feasible
    by a live smoke test (see THREE_ARM_BUNDLE_INVESTIGATION_PREREGISTRATION.md).
  - points directly at OpenRouter (same base_url RTF's own a4v.llm.ChatClient
    uses), no local oai_proxy hop -- this mirrors the deployment's own
    "proxy_static" mode, which (per env stack.env) already points
    OAI_PROXY_BASE_URL at https://openrouter.ai/api/v1 directly.
  - one throwaway, isolated $CODEX_HOME per bundle (no shared auth/session
    dir across bundles) -- guarantees no cross-bundle memory, since a
    plain `codex exec` call is already a fresh one-shot session, and a
    fresh HOME additionally isolates any on-disk session/auth state.
  - cost is computed from OpenRouter's published per-token pricing for
    this model (queried once, see PRICING below) applied to codex's own
    reported input_tokens/cached_input_tokens/output_tokens, since codex
    CLI does not expose OpenRouter's usage.cost field the way
    a4v.llm.ChatClient does.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

# Published OpenRouter pricing for openai/gpt-5.1-codex-max, queried
# 2026-08-07 via GET https://openrouter.ai/api/v1/models (public, no
# auth needed) -- $/token. Frozen for this experiment's cost accounting;
# re-query before reuse in a future session since provider pricing can change.
PRICE_PROMPT_PER_TOKEN = 0.00000125       # uncached input
PRICE_CACHED_INPUT_PER_TOKEN = 0.000000125  # OpenRouter input_cache_read
PRICE_COMPLETION_PER_TOKEN = 0.00001      # output

DEFAULT_MODEL = "openai/gpt-5.1-codex-max"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_WIRE_API = "responses"

# Best-effort regexes for extracting file paths a shell command actually
# touched, for the citation-provenance check. Not exhaustive -- documented
# as a best-effort authoritative-adjacent signal, not a perfect parser, in
# the preregistration and report.
_FILE_READ_CMD_PATTERNS = [
    re.compile(r"\bcat\s+(?:-[A-Za-z]+\s+)*([^\s|>]+)"),
    re.compile(r"\bhead\s+(?:-\S+\s+)*([^\s|>]+)"),
    re.compile(r"\btail\s+(?:-\S+\s+)*([^\s|>]+)"),
    re.compile(r"\bsed\s+-n\s+\S+\s+([^\s|>]+)"),
    re.compile(r"\brg\s+[^|]*?\s([^\s|>]+\.(?:sol|md|json|toml))\b"),
    re.compile(r"\bgrep\s+[^|]*?\s([^\s|>]+\.(?:sol|md|json|toml))\b"),
    re.compile(r"\bwc\s+(?:-\S+\s+)*([^\s|>]+)"),
]


def compute_cost(input_tokens: int, cached_input_tokens: int, output_tokens: int) -> float:
    uncached = max(0, input_tokens - cached_input_tokens)
    return (
        uncached * PRICE_PROMPT_PER_TOKEN
        + cached_input_tokens * PRICE_CACHED_INPUT_PER_TOKEN
        + output_tokens * PRICE_COMPLETION_PER_TOKEN
    )


def prepare_isolated_repo(fixture_dir: Path, scratch_root: Path, label: str) -> Path:
    """Copy a synthetic fixture into a fresh, non-git scratch directory.

    Without this, `-C <fixture_dir>` would let Codex's git-repo detection
    see that the fixture lives inside this experiment's own (much larger)
    git worktree -- `--skip-git-repo-check` only skips Codex's own dirty-
    tree warning, it does not stop the agent from noticing/traversing a
    parent repository. Copying breaks that ancestry cleanly. Real-repo
    bundles (PoolTogether) skip this -- their repo_root is already an
    independent checkout with no such parent-repo bleed-through.
    """
    dest = scratch_root / f"{label}_repo"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(fixture_dir, dest)
    return dest


def write_codex_config(home: Path, base_url: str = DEFAULT_BASE_URL, wire_api: str = DEFAULT_WIRE_API) -> None:
    config_dir = home / ".codex"
    config_dir.mkdir(parents=True, exist_ok=True)
    base_url = base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    config = (
        'model_provider = "proxy"\n\n'
        "[model_providers.proxy]\n"
        'name = "proxy"\n'
        f'base_url = "{base_url}"\n'
        f'wire_api = "{wire_api}"\n'
        'env_key = "OPENAI_API_KEY"\n'
    )
    (config_dir / "config.toml").write_text(config, encoding="utf-8")


def codex_login(codex_bin: Path, home: Path, api_key: str) -> None:
    subprocess.run(
        [str(codex_bin), "login", "--with-api-key"],
        input=api_key + "\n", capture_output=True, text=True,
        env={"HOME": str(home)}, check=False,
    )


def load_frozen_arm_c_prompt() -> str:
    path = Path(__file__).parent / "CODEX_SYSTEM_PROMPT_v2_arm_c.md"
    text = path.read_text(encoding="utf-8")
    marker = "## ROLE"
    return text[text.index(marker):]


def build_arm_c_prompt(requirement_text: str, context_bundle_text: str, candidate_location: str,
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
    return load_frozen_arm_c_prompt() + "\n\n---\n\n" + body


def _extract_last_fenced_json(text: str) -> dict | None:
    """Return the last valid JSON object in a Markdown code fence.

    Agent responses commonly contain an explanatory Solidity/Python fence
    before their final JSON fence.  Pair fences rather than spanning from
    the first opening fence to the last closing fence.
    """
    parts = text.split("```")
    for body in reversed(parts[1::2]):
        first_newline = body.find("\n")
        if first_newline != -1 and body[:first_newline].strip().isalpha():
            body = body[first_newline + 1:]
        try:
            parsed = json.loads(body.strip())
        except json.JSONDecodeError:
            try:
                parsed, _ = json.JSONDecoder().raw_decode(body.strip())
            except json.JSONDecodeError:
                continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _extract_touched_files(command: str) -> list[str]:
    touched = []
    for pat in _FILE_READ_CMD_PATTERNS:
        m = pat.search(command)
        if m:
            candidate = m.group(1).strip("'\"")
            if not candidate.startswith("-"):
                touched.append(candidate)
    return touched


@dataclass
class ArmCResult:
    case_id: str
    repetition: int
    final_decision: dict | None
    reasoning_text: str  # full agent_message text, for cases where fenced JSON wasn't found
    actual_tool_calls: int
    actual_commands: list[str]
    actual_files_touched: list[str]
    repository_commit: str | None
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    cost_usd: float
    wall_clock_s: float
    timed_out: bool
    session_log_path: str
    protocol_violation: str | None  # non-None if mandatory-investigation gate failed
    citation_provenance_failures: list[str]


def run_arm_c_bundle(*, codex_bin: Path, api_key: str, model: str, case_id: str, repetition: int,
                      investigation_dir: Path, prompt: str, unresolved_facts: list[str],
                      scratch_root: Path, timeout_s: int = 480) -> ArmCResult:
    home = scratch_root / f"{case_id}_r{repetition}_home"
    if home.exists():
        shutil.rmtree(home)
    home.mkdir(parents=True)
    write_codex_config(home)
    codex_login(codex_bin, home, api_key)

    out_path = scratch_root / f"{case_id}_r{repetition}_out.txt"
    log_path = scratch_root / f"{case_id}_r{repetition}_stream.jsonl"
    out_path.unlink(missing_ok=True)
    log_path.unlink(missing_ok=True)

    cmd = [
        str(codex_bin), "exec",
        "--model", model,
        "--dangerously-bypass-approvals-and-sandbox",
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

    # --- parse the streamed JSON events for harness-authoritative tool trace ---
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

    # --- final decision: prefer -o out_path, fall back to agent_message text ---
    final_text = out_path.read_text(encoding="utf-8", errors="replace") if out_path.exists() else agent_message_text
    final_decision = _extract_last_fenced_json(final_text)

    # --- repository commit, if the investigation dir is a real git checkout ---
    repo_commit = None
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(investigation_dir),
                            capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            repo_commit = r.stdout.strip()
    except Exception:
        pass

    # --- mandatory-investigation gate (section 9 of the task spec) ---
    protocol_violation = None
    if unresolved_facts and len(commands) == 0:
        protocol_violation = (
            "unresolved_facts was non-empty but zero real command_execution events were recorded "
            "-- mandatory-first-action gate violated (or the agent answered from reasoning alone "
            "without ever touching the filesystem)"
        )

    # --- citation provenance check: does every source-like path in the final
    #     decision correspond to a file actually cat/head/tail/rg/grep'd? ---
    citation_failures: list[str] = []
    if final_decision:
        touched_basenames = {Path(f).name for f in files_touched}
        for section in ("initial_evidence_verification", "resolved_facts"):
            for entry in final_decision.get(section, []) or []:
                if not isinstance(entry, dict):
                    continue
                src = str(entry.get("source", ""))
                if not src or src == "...":
                    continue
                # best-effort: does any touched file's basename appear in the cited source string?
                if not any(bn and bn in src for bn in touched_basenames):
                    citation_failures.append(f"{section}: {src!r} does not match any inspected file {sorted(touched_basenames)}")

    cost = compute_cost(input_tokens, cached_input_tokens, output_tokens)

    return ArmCResult(
        case_id=case_id, repetition=repetition, final_decision=final_decision,
        reasoning_text=agent_message_text, actual_tool_calls=len(commands),
        actual_commands=commands, actual_files_touched=sorted(set(files_touched)),
        repository_commit=repo_commit, input_tokens=input_tokens,
        cached_input_tokens=cached_input_tokens, output_tokens=output_tokens,
        cost_usd=cost, wall_clock_s=wall_clock_s, timed_out=timed_out,
        session_log_path=str(log_path), protocol_violation=protocol_violation,
        citation_provenance_failures=citation_failures,
    )
