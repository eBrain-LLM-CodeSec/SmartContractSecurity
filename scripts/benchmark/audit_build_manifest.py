"""Builds `audit-build-manifest.jsonl`: one authoritative, machine-readable
record per audit subproject, tracing `audit_id -> checkout -> subproject
root -> compiler-version resolution -> (declared) build/Slither commands`.

This is a *planning* artifact, produced once (or whenever an audit's
upstream repository changes), consumed by `provision_toolchains.py`
(Phase 2, to determine what to provision) and by the offline benchmark
runner (Phase 3, to select the exact provisioned compiler per subproject
without ever letting Forge/Hardhat decide dynamically). It does not itself
compile anything.

`python -m scripts.benchmark.audit_build_manifest
    --evmbench-root /scratch/md5344/evmbench/repo/frontier-evals/project/evmbench
    --work-dir /scratch/.../scratch/checkouts
    --out audit-build-manifest.jsonl`

Processes exactly one audit checkout on disk at a time (clone -> inspect
-> hash lockfile -> delete), the same quota-safe pattern already
established by `run_full_study_batch.py` -- never all 27 simultaneously.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from scripts.benchmark.audit_registry import AUDITS, AuditSpec, SubprojectSpec
from scripts.benchmark.compiler_resolver import (
    BuildSystem,
    CompilerResolutionStatus,
    detect_build_system,
    resolve_compiler,
)

_LOCKFILE_NAMES = (
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "foundry.lock", "soldeer.lock",
)


@dataclass
class SubprojectBuildRecord:
    audit_id: str
    subproject_id: str
    source_commit: str | None
    checkout_relative_path: str
    build_system: str
    build_command: str
    slither_command: str
    required_compiler_versions: list[str]
    primary_compiler_version: str | None
    compiler_version_source: str
    compiler_resolution_status: str
    foundry_version: str | None
    node_version: str | None
    package_manager: str | None
    package_manager_version: str | None
    dependency_lockfile_path: str | None
    dependency_lockfile_sha256: str | None
    docker_image: str | None
    expected_artifact_dir: str
    required_env_vars: dict[str, str]
    network_required_for_provisioning: bool
    network_allowed_for_benchmark_execution: bool
    compatibility_overrides: dict
    status: str
    failure_reason: str | None


def _sh(cmd: list[str], cwd: Path, timeout: int = 300) -> tuple[bool, str]:
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return False, "timeout"


def _clone(audit_id: str, dest: Path) -> tuple[bool, str]:
    # cwd is the process's OWN current directory, not dest.parent: `dest`
    # is passed to git as a path relative to wherever the caller
    # constructed it from (this process's cwd), so overriding the
    # subprocess's cwd to dest.parent would make git resolve that same
    # relative path a second time on top of it -- confirmed live: `ok`
    # came back True but `dest.exists()` was False afterward, because the
    # repo landed one directory level away from where every subsequent
    # check looked for it. run_full_study_batch.py's own, already-proven
    # _clone never overrides cwd for exactly this reason.
    ok, out = _sh(["git", "clone", "--quiet", "--recurse",
                    f"https://github.com/evmbench-org/{audit_id}.git", str(dest)], Path.cwd(), timeout=900)
    return ok, out[-800:]


def _source_commit(repo_root: Path) -> str | None:
    ok, out = _sh(["git", "rev-parse", "HEAD"], repo_root)
    return out.strip() if ok else None


def _lockfile(subproject_root: Path) -> tuple[Path | None, str | None]:
    for name in _LOCKFILE_NAMES:
        p = subproject_root / name
        if p.exists():
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            return p, digest
    return None, None


def _node_version_from_engines(subproject_root: Path) -> str | None:
    pkg = subproject_root / "package.json"
    if not pkg.exists():
        return None
    try:
        data = json.loads(pkg.read_text(errors="ignore"))
    except (json.JSONDecodeError, OSError):
        return None
    return (data.get("engines") or {}).get("node")


def _package_manager(subproject_root: Path) -> tuple[str | None, str | None]:
    if (subproject_root / "pnpm-lock.yaml").exists():
        return "pnpm", None
    if (subproject_root / "yarn.lock").exists():
        return "yarn", None
    if (subproject_root / "package-lock.json").exists():
        return "npm", None
    return None, None


def _build_command(build_system: BuildSystem, npm_flags: tuple[str, ...]) -> str:
    if build_system == BuildSystem.FOUNDRY:
        return "forge build"
    if build_system == BuildSystem.HARDHAT:
        flags = " ".join(npm_flags) or "--no-audit --no-fund"
        return f"npm install {flags} && npx hardhat compile"
    return "(unknown build system -- no declared build command)"


def build_record_for_subproject(
    audit: AuditSpec, sub: SubprojectSpec, checkout_root: Path,
) -> SubprojectBuildRecord:
    subproject_root = checkout_root / sub.relative_root
    status, failure_reason = "RESOLVED", None

    if not subproject_root.exists():
        return SubprojectBuildRecord(
            audit_id=audit.audit_id, subproject_id=sub.subproject_id, source_commit=None,
            checkout_relative_path=sub.relative_root, build_system="UNKNOWN", build_command="", slither_command="",
            required_compiler_versions=[], primary_compiler_version=None, compiler_version_source="",
            compiler_resolution_status="NO_CONFIGURATION_FOUND", foundry_version=None, node_version=None,
            package_manager=None, package_manager_version=None, dependency_lockfile_path=None,
            dependency_lockfile_sha256=None, docker_image=None, expected_artifact_dir="", required_env_vars={},
            network_required_for_provisioning=False, network_allowed_for_benchmark_execution=False,
            compatibility_overrides={}, status="BUILD_RECIPE_FAILED",
            failure_reason=f"declared subproject root {sub.relative_root!r} does not exist in the checkout",
        )

    resolution = resolve_compiler(subproject_root)
    if resolution.status is not CompilerResolutionStatus.RESOLVED:
        status = resolution.status.value
        failure_reason = resolution.detail

    build_system = resolution.build_system if sub.build_system_hint is None else BuildSystem(sub.build_system_hint.upper())
    lockfile_path, lockfile_hash = _lockfile(subproject_root)
    pkg_manager, pkg_manager_version = _package_manager(subproject_root)
    node_version = _node_version_from_engines(subproject_root)

    required_env: dict[str, str] = {}
    if audit.foundry_version_override:
        required_env["FOUNDRY_VERSION_OVERRIDE"] = audit.foundry_version_override

    docker_image = "evmbench-worker.sif (Singularity, digest-pinned -- see environment-manifest.json)"

    return SubprojectBuildRecord(
        audit_id=audit.audit_id, subproject_id=sub.subproject_id, source_commit=_source_commit(checkout_root),
        checkout_relative_path=sub.relative_root, build_system=build_system.value,
        build_command=_build_command(build_system, audit.npm_install_flags),
        slither_command=f"slither {subproject_root.as_posix()}",
        required_compiler_versions=resolution.versions, primary_compiler_version=resolution.primary_version,
        compiler_version_source=resolution.detail, compiler_resolution_status=resolution.status.value,
        foundry_version=audit.foundry_version_override,  # None means "the deployment's generally-pinned Foundry release"
        node_version=node_version, package_manager=pkg_manager, package_manager_version=pkg_manager_version,
        dependency_lockfile_path=str(lockfile_path.relative_to(checkout_root)) if lockfile_path else None,
        dependency_lockfile_sha256=lockfile_hash, docker_image=docker_image,
        expected_artifact_dir=str((subproject_root / "out").relative_to(checkout_root))
        if build_system == BuildSystem.FOUNDRY else "artifacts/",
        required_env_vars=required_env,
        network_required_for_provisioning=True,   # cloning + npm/forge dependency install always needs network
        network_allowed_for_benchmark_execution=False,  # the whole point of this work
        compatibility_overrides={
            "foundry_version_override": audit.foundry_version_override,
            "override_reason": audit.override_reason,
            "npm_install_flags": list(audit.npm_install_flags),
        } if audit.foundry_version_override or audit.npm_install_flags else {},
        status=status, failure_reason=failure_reason,
    )


def build_manifest_for_audit(audit: AuditSpec, work_dir: Path) -> list[SubprojectBuildRecord]:
    dest = work_dir / audit.audit_id
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    ok, err = _clone(audit.audit_id, dest)
    try:
        if not ok:
            return [SubprojectBuildRecord(
                audit_id=audit.audit_id, subproject_id=sub.subproject_id, source_commit=None,
                checkout_relative_path=sub.relative_root, build_system="UNKNOWN", build_command="",
                slither_command="", required_compiler_versions=[], primary_compiler_version=None,
                compiler_version_source="", compiler_resolution_status="NO_CONFIGURATION_FOUND",
                foundry_version=None, node_version=None, package_manager=None, package_manager_version=None,
                dependency_lockfile_path=None, dependency_lockfile_sha256=None, docker_image=None,
                expected_artifact_dir="", required_env_vars={}, network_required_for_provisioning=True,
                network_allowed_for_benchmark_execution=False, compatibility_overrides={},
                status="INFRASTRUCTURE_FAILURE", failure_reason=f"git clone failed: {err}",
            ) for sub in audit.subprojects]
        return [build_record_for_subproject(audit, sub, dest) for sub in audit.subprojects]
    finally:
        shutil.rmtree(dest, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--audit", action="append", default=None,
                     help="restrict to specific audit_id(s); repeatable. Default: all 27.")
    args = ap.parse_args(argv)

    args.work_dir.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    audits = [a for a in AUDITS if args.audit is None or a.audit_id in args.audit]
    records: list[SubprojectBuildRecord] = []
    for audit in audits:
        print(f"--- {audit.audit_id} ---", flush=True)
        recs = build_manifest_for_audit(audit, args.work_dir)
        for r in recs:
            print(f"  {r.subproject_id}: {r.compiler_resolution_status} "
                  f"versions={r.required_compiler_versions} status={r.status}", flush=True)
        records.extend(recs)

    with args.out.open("w") as f:
        for r in records:
            f.write(json.dumps(asdict(r), sort_keys=True) + "\n")

    counts: dict[str, int] = {}
    for r in records:
        counts[r.compiler_resolution_status] = counts.get(r.compiler_resolution_status, 0) + 1
    print(f"\nsummary (compiler resolution): {counts}")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
