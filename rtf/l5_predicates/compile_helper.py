"""Shared helper: compile a Solidity source string with a pinned solc
version and return a real Slither object, for testing RTF custom
predicates against actual compiled code (not just source-text pattern
matching) -- per the plan's verification requirement (synthetic
positive/negative snippet tests per strategy component).
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from slither import Slither

VENV_BIN = Path(__file__).resolve().parents[2] / ".venv" / "bin"
SOLC_SELECT = str(VENV_BIN / "solc-select")


def _env_with_venv_bin_on_path() -> dict:
    # Slither/crytic-compile shell out to a bare `solc` on PATH -- the
    # solc-select shim lives at .venv/bin/solc but that directory isn't on
    # PATH by default in this environment. Prepend it rather than relying
    # on the caller's shell PATH already including it.
    env = os.environ.copy()
    env["PATH"] = f"{VENV_BIN}:{env.get('PATH', '')}"
    return env


def compile_source(solidity_code: str, solc_version: str = "0.8.20", extra_args: list[str] | None = None) -> Slither:
    """Writes `solidity_code` to a temp .sol file, pins solc to
    `solc_version` via solc-select, and returns a compiled Slither object.
    Raises if compilation fails (never silently swallowed -- a fixture
    that doesn't compile is a bug in the fixture, not a soft failure).
    """
    env = _env_with_venv_bin_on_path()
    subprocess.run([SOLC_SELECT, "use", solc_version], check=True, capture_output=True, text=True, env=env)
    os.environ["PATH"] = env["PATH"]  # Slither's own subprocess calls inherit this process's environ

    with tempfile.TemporaryDirectory() as tmp:
        sol_path = Path(tmp) / "Fixture.sol"
        sol_path.write_text(solidity_code, encoding="utf-8")
        return Slither(str(sol_path), **({} if not extra_args else {"solc_args": " ".join(extra_args)}))


def _collect_remappings(project_root: Path) -> list[str]:
    """Recursively find every `remappings.txt` under `project_root`
    (Foundry projects nest one per vendored `lib/` dependency, each
    written relative to ITS OWN directory) and merge them into a single
    flat list of absolute-path remappings solc can consume directly,
    without needing `forge` to resolve them.

    Confirmed empirically necessary, not a defensive guess: a real
    EVMbench target (2023-07-pooltogether's `vault/`) has 5 separate
    `remappings.txt` files at different nesting depths (`vault/`,
    `vault/lib/pt-v5-prize-pool/`, `vault/lib/pt-v5-prize-pool/lib/
    prb-math/`, `vault/lib/brokentoken/`, `vault/lib/pt-v5-liquidator/`)
    -- using only the top-level one fails to resolve nested imports like
    `prb-math/SD59x18.sol`, which only pt-v5-prize-pool's OWN nested
    remappings.txt declares.

    Shallower files are walked first and a prefix already seen from a
    shallower file is kept over a deeper redefinition -- not a perfect
    reproduction of Foundry's own context-aware remapping resolution
    (which resolves remappings per-importing-file, not globally), but a
    defensible, simple approximation: the project's OWN top-level choice
    for a given prefix should generally take precedence over a vendored
    dependency's internal one.
    """
    remap_files = sorted(
        project_root.rglob("remappings.txt"),
        key=lambda p: len(p.relative_to(project_root).parts),
    )
    seen_prefixes: set[str] = set()
    merged: list[str] = []
    for rf in remap_files:
        base = rf.parent
        for line in rf.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or "=" not in line:
                continue
            prefix, relpath = line.split("=", 1)
            if prefix in seen_prefixes:
                continue
            seen_prefixes.add(prefix)
            abspath = (base / relpath).resolve()
            merged.append(f"{prefix}={abspath}/")
    return merged


def compile_evmbench_target(entry_sol_file: Path, project_root: Path, solc_version: str) -> Slither:
    """Compile a real, multi-file EVMbench audit target directly via
    solc, WITHOUT needing `forge`/Foundry installed.

    Necessary, not a stylistic preference: `forge` cannot be installed on
    this specific HPC node (Foundry's precompiled binaries require
    GLIBC >= 2.29; this node has an older glibc -- confirmed via a real
    `foundryup` install attempt, not assumed) -- see AR-009. Slither's
    own crytic-compile, when pointed at a target inside a Foundry project
    (a `foundry.toml` present anywhere up the directory tree), otherwise
    unconditionally shells out to `forge config`/`forge build`, even when
    a plain-solc compile is explicitly requested via
    `compile_force_framework`.

    Two things must both hold to avoid that: (1) `cwd` must be set to a
    directory with NO `foundry.toml` reachable from it, so crytic-
    compile's working-directory Foundry auto-detection (a SEPARATE check
    from `compile_force_framework`, which alone is not sufficient) never
    fires; and (2) all import remappings must be supplied explicitly, as
    ABSOLUTE paths (not relative to the now-unrelated `cwd`), collected
    via `_collect_remappings` -- both confirmed necessary by direct,
    repeated trial against a real target, not assumed.

    Raises if compilation fails, same discipline as `compile_source`.
    """
    remaps = _collect_remappings(project_root)
    env = _env_with_venv_bin_on_path()
    subprocess.run([SOLC_SELECT, "use", solc_version], check=True, capture_output=True, text=True, env=env)
    os.environ["PATH"] = env["PATH"]

    with tempfile.TemporaryDirectory() as neutral_cwd:
        return Slither(
            str(entry_sol_file.resolve()),
            solc_remaps=remaps,
            cwd=neutral_cwd,
            compile_force_framework="solc",
        )
