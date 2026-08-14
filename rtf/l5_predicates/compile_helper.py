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
import tomllib
from pathlib import Path

from slither import Slither

VENV_BIN = Path(__file__).resolve().parents[2] / ".venv" / "bin"
SOLC_SELECT = str(VENV_BIN / "solc-select")


def _env_with_venv_bin_on_path(solc_version: str | None = None) -> dict:
    # Slither/crytic-compile shell out to a bare `solc` on PATH -- the
    # solc-select shim lives at .venv/bin/solc but that directory isn't on
    # PATH by default in this environment. Prepend it rather than relying
    # on the caller's shell PATH already including it.
    env = os.environ.copy()
    env["PATH"] = f"{VENV_BIN}:{env.get('PATH', '')}"
    if solc_version is not None:
        # Pin the solc-select shim per subprocess.  Calling
        # `solc-select use` mutates ~/.solc-select/global-version, which
        # is both unavailable in sandboxed runs and racy when different
        # compiler versions are used concurrently.
        env["SOLC_VERSION"] = solc_version
    return env


def compile_source(solidity_code: str, solc_version: str = "0.8.20", extra_args: list[str] | None = None) -> Slither:
    """Writes `solidity_code` to a temp .sol file, pins solc to
    `solc_version` via solc-select, and returns a compiled Slither object.
    Raises if compilation fails (never silently swallowed -- a fixture
    that doesn't compile is a bug in the fixture, not a soft failure).
    """
    env = _env_with_venv_bin_on_path(solc_version)
    os.environ["PATH"] = env["PATH"]  # Slither's own subprocess calls inherit this process's environ
    previous_solc_version = os.environ.get("SOLC_VERSION")
    os.environ["SOLC_VERSION"] = solc_version

    try:
        with tempfile.TemporaryDirectory() as tmp:
            sol_path = Path(tmp) / "Fixture.sol"
            sol_path.write_text(solidity_code, encoding="utf-8")
            return Slither(str(sol_path), **({} if not extra_args else {"solc_args": " ".join(extra_args)}))
    finally:
        if previous_solc_version is None:
            os.environ.pop("SOLC_VERSION", None)
        else:
            os.environ["SOLC_VERSION"] = previous_solc_version


def _foundry_toml_remapping_lines(foundry_toml_path: Path) -> list[str]:
    """Some Foundry projects declare remappings directly in
    `[profile.default].remappings` inside `foundry.toml` instead of (or as
    well as) a standalone `remappings.txt` -- confirmed empirically
    necessary, not a defensive guess: a real EVMbench target
    (2026-01-tempo-feeamm) has NO remappings.txt at all, only
    `foundry.toml`'s own `remappings = ["@openzeppelin/contracts/=lib/
    openzeppelin-contracts/contracts/", ...]`; without parsing this, that
    import is unresolvable and compilation fails outright. Returns the
    same "prefix=relpath" line format `remappings.txt` uses, so callers
    can treat both sources identically.
    """
    try:
        with foundry_toml_path.open("rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError):
        return []
    profile = data.get("profile", {}).get("default", {})
    remappings = profile.get("remappings")
    if not isinstance(remappings, list):
        return []
    return [str(r) for r in remappings if isinstance(r, str) and "=" in r]


def _collect_remappings(project_root: Path) -> list[str]:
    """Recursively find every `remappings.txt` AND every `foundry.toml`
    with a `[profile.default].remappings` array under `project_root`
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
    remappings.txt declares. A separate real target (2026-01-tempo-feeamm)
    declares its remappings ONLY in `foundry.toml`, with no
    `remappings.txt` at all -- see `_foundry_toml_remapping_lines`.

    Shallower files are walked first (both kinds interleaved by directory
    depth) and a prefix already seen from a shallower file is kept over a
    deeper redefinition -- not a perfect reproduction of Foundry's own
    context-aware remapping resolution (which resolves remappings
    per-importing-file, not globally), but a defensible, simple
    approximation: the project's OWN top-level choice for a given prefix
    should generally take precedence over a vendored dependency's
    internal one.
    """
    remap_files = sorted(
        list(project_root.rglob("remappings.txt")) + list(project_root.rglob("foundry.toml")),
        key=lambda p: len(p.relative_to(project_root).parts),
    )
    seen_prefixes: set[str] = set()
    merged: list[str] = []
    for rf in remap_files:
        base = rf.parent
        lines = (
            _foundry_toml_remapping_lines(rf)
            if rf.name == "foundry.toml"
            else rf.read_text(encoding="utf-8", errors="replace").splitlines()
        )
        for line in lines:
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


def compile_evmbench_target(
    entry_sol_file: Path, project_root: Path, solc_version: str,
    extra_solc_args: list[str] | None = None,
) -> Slither:
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

    `--allow-paths` is always widened to include `project_root` itself,
    on top of crytic-compile's own default (`.` + the entry file's own
    directory) -- confirmed necessary, not a defensive guess: a real
    EVMbench target (2025-04-forte) has a plain relative import that
    escapes its own directory into a sibling one
    (`import {Uint512} from "../lib/Uint512.sol";` in `src/Float128.sol`,
    reaching a top-level `lib/Uint512.sol`), which solc's default
    allow-paths otherwise rejects as outside the allowed set. Purely a
    widening of which paths solc may READ (never write), not a semantic
    or codegen change -- safe to always apply.

    `extra_solc_args`, when given, are passed through verbatim to solc
    (e.g. `["--via-ir", "--optimize"]` -- solc's own error message says
    `--via-ir` alone is insufficient for a genuine stack-too-deep case,
    "while enabling the optimizer" is required alongside it; confirmed by
    trial against both a synthetic fixture and the real target below).
    Deliberately opt-in, never auto-detected or silently added: unlike
    `--allow-paths`, `--via-ir`/`--optimize` change codegen (and which
    compiler diagnostics surface), so a caller must choose them
    explicitly for a specific target known to need it (confirmed real,
    not hypothetical: 2024-01-canto's own `foundry.toml` declares
    `via-ir=true` and `optimizer=true`, and its `GaugeController.sol`
    fails with solc's own "Stack too deep. Try compiling with --via-ir"
    error otherwise) rather than have it silently applied everywhere.

    Raises if compilation fails, same discipline as `compile_source`.
    """
    remaps = _collect_remappings(project_root)
    env = _env_with_venv_bin_on_path(solc_version)
    os.environ["PATH"] = env["PATH"]
    previous_solc_version = os.environ.get("SOLC_VERSION")
    os.environ["SOLC_VERSION"] = solc_version

    allow_paths = f".,{entry_sol_file.resolve().parent},{project_root.resolve()}"
    solc_args_parts = ["--allow-paths", allow_paths]
    if extra_solc_args:
        solc_args_parts.extend(extra_solc_args)

    try:
        with tempfile.TemporaryDirectory() as neutral_cwd:
            return Slither(
                str(entry_sol_file.resolve()),
                solc_remaps=remaps,
                cwd=neutral_cwd,
                compile_force_framework="solc",
                solc_args=" ".join(solc_args_parts),
            )
    finally:
        if previous_solc_version is None:
            os.environ.pop("SOLC_VERSION", None)
        else:
            os.environ["SOLC_VERSION"] = previous_solc_version


# The SingularityBackend deployment's own worker image (built for a DIFFERENT
# system -- the LLM-agent-auditor pipeline documented in the top-level
# /scratch/md5344/evmbench/CLAUDE.md, not RTF) happens to carry a real,
# working Foundry install. Reused here purely as a compilation utility: `forge
# build` runs INSIDE the container (whose own bundled libc isn't affected by
# this host's GLIBC < 2.29 limitation -- confirmed live, see AR-009 and this
# function's own docstring below), producing real `out/build-info/*.json`
# artifacts; Slither then reads those artifacts on the HOST via crytic-
# compile's `ignore_compile` mode, which never invokes `forge` itself. No
# `forge`/Foundry dependency on the host at all.
_SINGULARITY_BIN = Path("/share/apps/NYUAD5/singularity/current/bin/singularity")
_EVMBENCH_WORKER_SIF = Path("/scratch/md5344/evmbench/containers/evmbench-worker.sif")


def compile_evmbench_target_via_foundry(
    project_root: Path, extra_forge_build_args: list[str] | None = None, timeout_s: int = 300,
) -> Slither:
    """Compiles `project_root` (a real Foundry project -- must contain a
    `foundry.toml`) via a real `forge build` run inside the pre-existing
    `evmbench-worker.sif` container, then loads the result with Slither on
    the host via crytic-compile's `ignore_compile` mode -- no `forge`
    binary needed on the host (confirmed live: the host's own `forge`
    install fails with a GLIBC_2.29 error; the containerized one works).

    Unlike `compile_evmbench_target` (which follows exactly one entry
    file's own `import` graph via raw solc), this compiles the WHOLE
    project the way `forge build` normally would -- every file under the
    project's own configured `src` path becomes part of one compilation
    unit, correctly resolving remappings/`via-ir`/optimizer settings from
    the project's own `foundry.toml` rather than requiring them to be
    manually discovered and passed as `extra_solc_args` (confirmed live
    against `2024-01-canto`, whose `foundry.toml` declares `via-ir=true`
    -- `forge` picked it up automatically with zero manual flags, unlike
    `compile_evmbench_target`, which needed that discovered by trial and
    error and passed explicitly). This is what structurally closes the
    "sibling file the entry never imports is invisible to Slither" gap
    confirmed live on `2025-04-forte` (`Ln.sol`, imported only BY
    `Float128.sol`... wait, imports `Float128.sol`, not the reverse, so
    never reachable FROM `Float128.sol` as entry) and `2024-08-phi`
    (`Cred.sol`, a sibling of `PhiFactory.sol`, not on its import graph).

    `test`/`script` directories are always skipped (`--skip ./test/**
    ./script/** --force`, matching crytic-compile's own Foundry platform
    default) -- they're out of audit scope anyway, and real EVMbench test
    suites sometimes depend on unvendored npm packages (`node_modules`)
    that were never installed, which would otherwise fail the whole build
    over files nothing here needs (confirmed live on `2024-08-phi`:
    `test/*.t.sol` needs `@prb/test`, absent; skipping tests fixed it,
    with zero effect on the real `src/` compilation).

    Caller's responsibility, not handled here: `project_root` should be a
    dedicated, non-concurrently-shared copy of the checkout -- `forge
    build` writes real files into `project_root/out/` and `project_root/
    cache/`, which would race if two calls targeted the same directory at
    once (the same category of shared-mutable-state hazard already
    documented for `solc-select`'s own global version file elsewhere in
    this module, not a new risk pattern).

    Raises `RuntimeError` (with real `forge` stdout/stderr, not swallowed)
    if the build fails; raises whatever Slither itself raises if loading
    the produced artifacts fails.
    """
    cmd = [
        str(_SINGULARITY_BIN), "exec",
        "--bind", f"{project_root.resolve()}:/work",
        "--pwd", "/work",
        str(_EVMBENCH_WORKER_SIF),
        "forge", "build", "--build-info", "--skip", "./test/**", "./script/**", "--force",
    ]
    if extra_forge_build_args:
        cmd.extend(extra_forge_build_args)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    if result.returncode != 0:
        raise RuntimeError(
            f"forge build (via container) failed, exit {result.returncode}:\n"
            f"--- stdout (tail) ---\n{result.stdout[-4000:]}\n"
            f"--- stderr (tail) ---\n{result.stderr[-4000:]}"
        )

    return Slither(str(project_root.resolve()), foundry_ignore_compile=True, compile_force_framework="Foundry")
