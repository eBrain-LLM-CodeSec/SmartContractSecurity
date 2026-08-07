"""Scoped repository tools for the Arm B (Codex-investigator) agent loop in
the bundle-level LLM-vs-agent experiment
(BUNDLE_LLM_VS_CODEX_AGENT_PREREGISTRATION.md). Three tools only --
read_file, grep, list_dir -- each hard-scoped to a single bundle's
repo_root (path escape raises), plus a ToolBudget that mechanically caps
total tool actions at MAX_TOOL_ACTIONS (the investigation budget's hard
ceiling; hops/files-opened are tracked and reported for the over-search
analysis, per the pre-registration, rather than mechanically blocked --
the system prompt's own budget language treats those as soft guidance,
only total actions as a hard stop).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

MAX_TOOL_ACTIONS = 8
MAX_READ_LINES = 200
MAX_GREP_MATCHES = 30


class BudgetExhausted(Exception):
    pass


@dataclass
class ToolBudget:
    repo_root: Path
    max_actions: int = MAX_TOOL_ACTIONS
    actions_used: int = 0
    files_opened: set[str] = field(default_factory=set)
    trace: list[dict] = field(default_factory=list)

    def remaining(self) -> int:
        return self.max_actions - self.actions_used

    def expansion_hops(self) -> int:
        # Operational definition (logged, not just assumed): the candidate's
        # own file counts as hop 0; each additional distinct file opened via
        # read_file counts as one more hop. This is a proxy for "expansion
        # hops away from the candidate," not a semantic import-graph distance
        # -- documented as such in the preregistration.
        return max(0, len(self.files_opened) - 1)


def _resolve(repo_root: Path, rel_path: str) -> Path:
    root = repo_root.resolve()
    candidate = (root / rel_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise ValueError(f"path escapes repo_root: {rel_path}")
    return candidate


def read_file(repo_root: Path, path: str, start_line: int | None = None, end_line: int | None = None) -> str:
    fp = _resolve(repo_root, path)
    if not fp.is_file():
        return f"ERROR: not a file: {path}"
    lines = fp.read_text(errors="replace").splitlines()
    start = max(1, start_line or 1)
    end = min(len(lines), end_line or len(lines))
    if end - start + 1 > MAX_READ_LINES:
        end = start + MAX_READ_LINES - 1
    end = min(end, len(lines))
    if end < start:
        return "(empty range)"
    numbered = [f"{i}: {lines[i - 1]}" for i in range(start, end + 1)]
    return "\n".join(numbered)


def grep(repo_root: Path, pattern: str, glob: str = "**/*.sol") -> str:
    root = repo_root.resolve()
    try:
        rx = re.compile(pattern)
    except re.error as e:
        return f"ERROR: invalid regex: {e}"
    matches = []
    for fp in sorted(root.glob(glob)):
        if not fp.is_file():
            continue
        try:
            text = fp.read_text(errors="replace")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if rx.search(line):
                rel = fp.relative_to(root)
                matches.append(f"{rel}:{i}: {line.strip()}")
                if len(matches) >= MAX_GREP_MATCHES:
                    break
        if len(matches) >= MAX_GREP_MATCHES:
            break
    return "\n".join(matches) if matches else "(no matches)"


def list_dir(repo_root: Path, path: str = ".") -> str:
    dp = _resolve(repo_root, path)
    if not dp.is_dir():
        return f"ERROR: not a directory: {path}"
    root = repo_root.resolve()
    lines = []
    for e in sorted(dp.iterdir()):
        rel = e.relative_to(root)
        lines.append(f"{'DIR ' if e.is_dir() else 'FILE'} {rel}")
    return "\n".join(lines) if lines else "(empty)"


def execute_action(repo_root: Path, budget: ToolBudget, action: dict) -> str:
    """Executes one tool action, updates budget bookkeeping (actions_used,
    files_opened, trace), and returns the observation text. Raises
    BudgetExhausted if called after the action budget is already spent --
    callers must check budget.remaining() themselves before calling this,
    since the caller (not this function) decides how to handle exhaustion
    (forced-final prompt vs. synthesized fallback).
    """
    if budget.actions_used >= budget.max_actions:
        raise BudgetExhausted(f"tool-action budget ({budget.max_actions}) already exhausted")
    kind = action.get("action")
    if kind == "read_file":
        path = action.get("path", "")
        obs = read_file(repo_root, path, action.get("start_line"), action.get("end_line"))
        budget.files_opened.add(path)
    elif kind == "grep":
        obs = grep(repo_root, action.get("pattern", ""), action.get("glob", "**/*.sol"))
    elif kind == "list_dir":
        obs = list_dir(repo_root, action.get("path", "."))
    else:
        obs = f"ERROR: unknown action '{kind}' -- must be one of read_file, grep, list_dir, final"
    budget.actions_used += 1
    budget.trace.append({
        "action": kind,
        "args": {k: v for k, v in action.items() if k != "action"},
        "observation": obs,
    })
    return obs
