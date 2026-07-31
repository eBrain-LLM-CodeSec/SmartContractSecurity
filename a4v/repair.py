"""Mandatory compile + bounded environment repair.

A valid Slither program graph is a hard prerequisite for the rest of the
pipeline. There is no degraded-analysis mode: if compilation fails, this
module attempts a bounded set of reproducible repairs (solc version,
submodules, deps) and retries; if the budget is exhausted it raises
BuildFailed and the caller marks the audit BUILD_FAILED. It never falls back
to regex parsing or a partial graph.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from solc_select import solc_select as ss

from a4v.graph import ProgramGraph, BuildFailed

_PRAGMA_RE = re.compile(r"pragma\s+solidity\s+([^;]+);")


@dataclass
class RepairAttempt:
    action: str
    detail: str
    ok: bool
    error: str | None = None


@dataclass
class BuildResult:
    graph: ProgramGraph
    solc_version: str
    attempts: list[RepairAttempt] = field(default_factory=list)


def _log_attempt(log_path: Path, attempt: RepairAttempt) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(json.dumps({
            "action": attempt.action,
            "detail": attempt.detail,
            "ok": attempt.ok,
            "error": attempt.error,
            "ts": time.time(),
        }) + "\n")


def _detect_pragma_versions(project_dir: Path) -> list[str]:
    """Best-effort scrape of `pragma solidity` constraints across .sol files,
    used only to pick a solc version to try -- never used to synthesize a
    graph without an actual successful Slither compile.
    """
    versions: list[str] = []
    for sol_file in project_dir.rglob("*.sol"):
        try:
            text = sol_file.read_text(errors="ignore")
        except OSError:
            continue
        for m in _PRAGMA_RE.finditer(text):
            versions.append(m.group(1).strip())
    return versions


def _candidate_versions_from_pragma(pragma_exprs: list[str]) -> list[str]:
    """Turn pragma expressions like '^0.8.20', '>=0.8.0 <0.9.0', '0.4.24'
    into a list of concrete solc versions to try, most-specific first.
    """
    candidates: list[str] = []
    exact = re.compile(r"(\d+\.\d+\.\d+)")
    for expr in pragma_exprs:
        for m in exact.finditer(expr):
            v = m.group(1)
            if v not in candidates:
                candidates.append(v)
    return candidates


def _ensure_solc(version: str, log_path: Path) -> RepairAttempt:
    try:
        installed = ss.installed_versions()
        if version not in installed:
            ss.install_artifacts([version], silent=True)
        ss.switch_global_version(version, always_install=True, silent=True)
        # For directory targets, crytic-compile auto-detects Foundry/Hardhat
        # and shells out to `forge`/`npx hardhat` (graph.py:_compile never
        # passes a `solc` kwarg in that case) -- solc-select's *global*
        # version this call just switched is never consulted by those
        # subprocess calls, so it alone has zero effect there. `bin/forge`
        # reads FORGE_FORCE_SOLC instead; setting it here is what actually
        # makes this repair action do anything for a real audit checkout
        # (confirmed live: previously, all pragma-driven retries against a
        # Foundry project directory failed identically every time, since
        # nothing forge-side ever changed between attempts).
        os.environ["FORGE_FORCE_SOLC"] = version
        attempt = RepairAttempt(action="solc_select", detail=f"switched to {version}", ok=True)
    except Exception as e:  # noqa: BLE001
        attempt = RepairAttempt(action="solc_select", detail=f"tried {version}", ok=False, error=str(e))
    _log_attempt(log_path, attempt)
    return attempt


def _submodules_need_init(project_dir: Path) -> bool:
    gitmodules = project_dir / ".gitmodules"
    if not gitmodules.exists():
        return False
    for line in gitmodules.read_text().splitlines():
        line = line.strip()
        if line.startswith("path ="):
            sub_path = project_dir / line.split("=", 1)[1].strip()
            if not sub_path.exists() or not any(sub_path.iterdir()):
                return True
    return False


def _git_submodule_update(project_dir: Path, log_path: Path) -> RepairAttempt:
    try:
        proc = subprocess.run(
            ["git", "submodule", "update", "--init"],
            cwd=project_dir, capture_output=True, text=True, timeout=300,
        )
        ok = proc.returncode == 0
        attempt = RepairAttempt(
            action="git_submodule_update", detail=proc.stdout[-2000:], ok=ok,
            error=None if ok else proc.stderr[-2000:],
        )
    except Exception as e:  # noqa: BLE001
        attempt = RepairAttempt(action="git_submodule_update", detail="", ok=False, error=str(e))
    _log_attempt(log_path, attempt)
    return attempt


class EnvRepair:
    def __init__(self, max_attempts: int = 6, max_wall_clock_seconds: int = 1800):
        self.max_attempts = max_attempts
        self.max_wall_clock_seconds = max_wall_clock_seconds

    def build_until_success(self, target: Path, repair_log_path: Path | None = None) -> BuildResult:
        """Attempt to compile+build the program graph for `target` (a .sol
        file or a project directory), applying bounded repairs on failure.
        Raises BuildFailed if the graph cannot be built within the budget --
        never returns a partial/degraded result.
        """
        target = Path(target)
        project_dir = target if target.is_dir() else target.parent
        log_path = repair_log_path or (project_dir / "repair.jsonl")
        attempts: list[RepairAttempt] = []
        start = time.monotonic()
        # A prior build_until_success call in this same process may have set
        # this for a different audit's checkout; never let it leak forward.
        os.environ.pop("FORGE_FORCE_SOLC", None)

        # Attempt 0: try as-is first (covers the common case where nothing needs repair).
        try:
            graph = ProgramGraph.build(target)
            return BuildResult(graph=graph, solc_version=ss.current_version()[0], attempts=attempts)
        except BuildFailed as e:
            attempts.append(RepairAttempt(action="initial_build", detail=str(target), ok=False, error=str(e)))
            _log_attempt(log_path, attempts[-1])

        pragma_versions = _candidate_versions_from_pragma(_detect_pragma_versions(project_dir))

        repair_actions: list[tuple[str, str]] = []
        if _submodules_need_init(project_dir):
            repair_actions.append(("submodules", ""))
        for v in pragma_versions:
            repair_actions.append(("solc_version", v))

        for action, arg in repair_actions:
            if time.monotonic() - start > self.max_wall_clock_seconds:
                break
            if len(attempts) >= self.max_attempts:
                break

            if action == "submodules":
                _git_submodule_update(project_dir, log_path)
            elif action == "solc_version":
                _ensure_solc(arg, log_path)

            try:
                graph = ProgramGraph.build(target)
                return BuildResult(graph=graph, solc_version=ss.current_version()[0], attempts=attempts)
            except BuildFailed as e:
                attempts.append(RepairAttempt(action=f"retry_after_{action}", detail=str(arg), ok=False, error=str(e)))
                _log_attempt(log_path, attempts[-1])

        raise BuildFailed(
            f"Exhausted repair budget ({len(attempts)} attempts) for {target}; see {log_path}"
        )
