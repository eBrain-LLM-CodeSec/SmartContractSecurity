"""Phase 5: generates `environment-manifest.json` for ONE benchmark run,
programmatically rather than hand-authored -- captures exactly the
environment state a cross-run reproducibility comparison (Phase 6) needs to
distinguish "the code changed" from "the environment underneath it
changed": OS, Singularity + image digest, Python/venv, git commit of this
worktree, Foundry tool-version overrides available, and the run-scoped
environment variables actually in effect for that specific run.

`python -m scripts.benchmark.generate_environment_manifest --out <path>`
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_AGENT4VUL_ROOT = Path(__file__).resolve().parents[2]
_SIF = Path("/scratch/md5344/evmbench/containers/evmbench-worker.sif")
_FOUNDRY_VERSIONS_DIR = Path("/scratch/md5344/evmbench/agent4vul/.venv/.foundry-versions")

_RELEVANT_ENV_VARS = (
    "BENCHMARK_WORK_DIR", "BENCHMARK_OUT_DIR", "BENCHMARK_TOOLCHAIN_DIR",
    "BENCHMARK_CONTAINER_HOME", "BENCHMARK_CONTAINER_TMP", "BENCHMARK_REGISTRY_PATH",
    "BENCHMARK_STRICT_OFFLINE", "BENCHMARK_AUDIT_ORDER_SEED", "BENCHMARK_SOLC_DISCOVERY_HINT",
)


def _sh(cmd: list[str]) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _singularity_version() -> str | None:
    out = _sh(["singularity", "--version"])
    return out.removeprefix("singularity version ") if out else None


def _sif_sha256() -> str | None:
    if not _SIF.exists():
        return None
    h = hashlib.sha256()
    with open(_SIF, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(args: list[str]) -> str | None:
    return _sh(["git", "-C", str(_AGENT4VUL_ROOT), *args])


def build_manifest() -> dict:
    return {
        "schema": "environment-manifest/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "os": platform.platform(),
        "hostname": platform.node(),
        "container_runtime": {
            "type": "Singularity",
            "version": _singularity_version(),
            "image_path": str(_SIF),
            "image_sha256": _sif_sha256(),
        },
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "git_commit_this_worktree": _git(["rev-parse", "HEAD"]),
        "git_branch_this_worktree": _git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "git_dirty": _git(["status", "--porcelain"]) not in (None, ""),
        "foundry": {
            "pinned_overrides_available": sorted(
                p.name for p in _FOUNDRY_VERSIONS_DIR.iterdir() if p.is_dir()
            ) if _FOUNDRY_VERSIONS_DIR.exists() else [],
            "pinned_overrides_location": str(_FOUNDRY_VERSIONS_DIR),
        },
        "run_scoped_environment_variables": {k: os.environ.get(k) for k in _RELEVANT_ENV_VARS},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(build_manifest(), indent=2, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
