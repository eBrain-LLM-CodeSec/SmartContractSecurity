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
