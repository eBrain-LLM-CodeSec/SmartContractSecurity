"""Extends the MGPR feasibility study (previously only ever run against 4
audits with pre-existing local checkouts: pooltogether, phi, liquid-ron,
tempo-feeamm) across all 27 audits now known to compile after this
session's build-infra fixes. Reuses run_feasibility_study.py's own
per-finding/per-route evaluation functions UNMODIFIED -- this script only
adds the orchestration (clone -> audit-specific setup recipe -> compile ->
evaluate -> delete checkout) needed to reach 27 audits instead of 4,
processing exactly one audit's checkout on disk at a time (never all 27
simultaneously) to stay within the account's file-count quota -- the same
constraint that caused the earlier 92,912-file container-cache incident.

Citation resolution only needs Path string comparison (resolve_citation +
find_routing_units_for_citation), never file content, so deleting a
checkout immediately after evaluating it does not affect this study's
results -- confirmed by reading resolve_citation's implementation: it never
opens the file, only builds and compares Path objects against the `file`
attribute Slither already recorded on each graph node at compile time.
"""
import json
import os
import random
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import yaml

from a4v.features import FeatureExtractor
from a4v.graph import BuildFailed, ProgramGraph
from a4v.mgpr.router import KNOWN_PREDICATES
from a4v.mgpr.spec import load_routing_spec
from a4v.repair import EnvRepair
from scripts.benchmark.compiler_resolver import CompilerResolutionStatus, resolve_compiler
from scripts.benchmark.provision_toolchains import populate_svm_cache, provision_solc, _fetch_official_checksums
from scripts.mgpr.build_manifests import _run_cmd_dir
from scripts.mgpr.run_dockerfile_recipes import CONTAINER_HOME, clear_container_home_caches, sh
from scripts.mgpr.run_feasibility_study import (
    _evaluate_finding,
    build_route_and_context_manifests,
)

EVMBENCH_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")
# Resolved from this file's own location -- not hardcoded to the main
# checkout. See run_feasibility_study.py's identical fix: hardcoding this
# to /scratch/md5344/evmbench/agent4vul silently pointed PATH at a stale
# bin/forge lacking this worktree's own solc_version-key/FORGE_FORCE_SOLC
# fixes, causing audits that compile cleanly with the correct bin/forge on
# PATH (confirmed live: 2024-01-canto, 2025-04-forte) to fail here instead.
AGENT4VUL_ROOT = Path(__file__).resolve().parents[2]
ROUTING_SPEC_PATH = AGENT4VUL_ROOT / "routing_spec.yaml"
# WORK_DIR/OUT_DIR/REGISTRY_PATH previously hardcoded a *specific prior
# session's* job-scratch path (/scratch/.../jobs/506f33b3/tmp/...), which
# does not exist in a fresh session -- the exact "session-specific state"
# problem this benchmark-infrastructure work exists to eliminate. Now
# overridable via env vars, defaulting to a location under this repo's own
# .benchmark/ directory rather than any one session's scratch.
_DEFAULT_RUN_ROOT = AGENT4VUL_ROOT / ".benchmark" / "runs" / "default"
WORK_DIR = Path(os.environ.get("BENCHMARK_WORK_DIR", str(_DEFAULT_RUN_ROOT / "study_checkouts")))
OUT_DIR = Path(os.environ.get("BENCHMARK_OUT_DIR", str(_DEFAULT_RUN_ROOT / "study_full")))
REGISTRY_PATH = Path(os.environ.get(
    "BENCHMARK_REGISTRY_PATH", str(AGENT4VUL_ROOT / "data" / "mgpr" / "benchmark_registry.jsonl")
))
# SOLC_DISCOVERY (a hand-curated, one-off JSON of {audit_id: {"solc": "X.Y.Z"}}
# guesses from a prior session) is superseded by
# scripts.benchmark.compiler_resolver's deterministic, multi-format resolver
# (Phase 1) -- kept only as an optional supplementary hint when its file
# happens to exist, never required.
_solc_discovery_path = Path(os.environ.get(
    "BENCHMARK_SOLC_DISCOVERY_HINT", "/scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_full_run2/solc_discovery.json"
))
SOLC_DISCOVERY = json.loads(_solc_discovery_path.read_text()) if _solc_discovery_path.exists() else {}
BENCHMARK_STRICT_OFFLINE = os.environ.get("BENCHMARK_STRICT_OFFLINE") == "1"
# Immutable, checksum-verified, shared ACROSS runs (unlike WORK_DIR/OUT_DIR
# above, which are per-run mutable state) -- see Phase 4's "separate:
# immutable provisioned tools; per-run mutable build cache; generated
# benchmark artifacts" in the accompanying report.
TOOLCHAIN_DIR = Path(os.environ.get("BENCHMARK_TOOLCHAIN_DIR", str(AGENT4VUL_ROOT / ".benchmark" / "toolchains")))

_PRAGMA_RE = re.compile(r"pragma\s+solidity\s+([^;]+);")
_EXACT_VERSION_RE = re.compile(r"(\d+\.\d+\.\d+)")

GENERIC_AUDITS = [
    "2023-07-pooltogether", "2025-04-forte", "2026-01-tempo-feeamm", "2024-08-phi", "2025-01-liquid-ron",
    "2025-06-panoptic", "2026-01-tempo-mpp-streams", "2026-01-tempo-stablecoin-dex", "2024-01-canto",
    "2024-05-loop", "2024-06-vultisig", "2025-10-sequence", "2024-07-basin", "2024-07-benddao",
    "2024-12-secondswap", "2024-05-munchables", "2024-01-renft", "2025-02-thorwallet",
]
BESPOKE_AUDITS = [
    "2023-10-nextgen", "2024-01-curves", "2024-07-traitforge", "2025-04-virtuals", "2025-05-blackhole",
    "2023-12-ethereumcreditguild", "2024-06-thorchain", "2024-06-size", "2024-04-noya",
]
ALL_27 = GENERIC_AUDITS + BESPOKE_AUDITS


# Phase 5: structured failure taxonomy, replacing a single generic
# COMPILE_FAILED bucket that collapsed together causes with very different
# remedies (a toolchain never provisioned vs. an audit's own npm
# dependency genuinely failing to install vs. Slither choking on a real
# unsupported language construct vs. this deployment's own container
# infrastructure being unavailable) -- distinguishing them post-hoc from
# the raised BuildFailed's own message, since the raise sites already
# each describe which step failed distinctly (see compile_generic et al.
# above); not a full custom-exception-hierarchy rewrite, which would be a
# much larger change for the same observability this already achieves.
_FAILURE_CLASSIFIERS: list[tuple[str, tuple[str, ...]]] = [
    ("TOOLCHAIN_NOT_PROVISIONED", ("TOOLCHAIN_NOT_PROVISIONED",)),
    ("AMBIGUOUS_COMPILER_CONFIGURATION", ("AMBIGUOUS_COMPILER_CONFIGURATION",)),
    ("NO_CONFIGURATION_FOUND", ("NO_CONFIGURATION_FOUND",)),
    ("DEPENDENCY_INSTALL_FAILED", ("npm install", "forge install", "yarn install", "pnpm install")),
    ("INFRASTRUCTURE_FAILURE", ("Read-only file system", "singularity", "Singularity",
                                  "No such file or directory: 'solc'", "Exhausted repair budget")),
    ("SLITHER_UNSUPPORTED_LANGUAGE_FEATURE", ("SlithIR", "not supported", "NotImplementedError",
                                                "Impossible to generate IR")),
]


def classify_build_failure(reason: str) -> str:
    for status, markers in _FAILURE_CLASSIFIERS:
        if any(m in reason for m in markers):
            return status
    return "SOURCE_COMPILE_FAILED"


def clone(audit_id: str, dest: Path) -> tuple[bool, str]:
    url = f"https://github.com/evmbench-org/{audit_id}.git"
    r = subprocess.run(["git", "clone", "--quiet", "--recurse", url, str(dest)],
                        capture_output=True, text=True, timeout=900)
    return r.returncode == 0, r.stderr[-500:]


def needs_npm_install(target: Path) -> bool:
    foundry_toml = target / "foundry.toml"
    if not foundry_toml.exists():
        return False
    text = foundry_toml.read_text(errors="ignore")
    return "node_modules" in text and (target / "package.json").exists()


def detect_pragma_solc(target: Path) -> str | None:
    counts = Counter()
    for sol_file in target.rglob("*.sol"):
        if "lib" in sol_file.parts or "node_modules" in sol_file.parts:
            continue
        try:
            text = sol_file.read_text(errors="ignore")
        except OSError:
            continue
        for m in _PRAGMA_RE.finditer(text):
            for v in _EXACT_VERSION_RE.findall(m.group(1)):
                counts[v] += 1
    return counts.most_common(1)[0][0] if counts else None


_official_checksums_cache: dict[str, str] | None = None


def _official_checksums() -> dict[str, str]:
    global _official_checksums_cache
    if _official_checksums_cache is None:
        _official_checksums_cache = _fetch_official_checksums()
    return _official_checksums_cache


# Phase 6 (cross-run compiler-selection comparison) needs to know exactly
# which compiler version(s) were actually selected for each audit, not
# just whether it compiled -- populated by _select_compiler below, keyed
# by the `audit_id` its caller passes, and copied into that audit's
# build_manifest.jsonl row in main() right after a successful compile.
LAST_COMPILER_SELECTION: dict[str, dict] = {}


def _select_compiler(target: Path, toolchain_dir: Path, audit_id: str | None = None) -> str:
    """Resolves + provisions the compiler(s) required for `target` (Phase
    1-3: scripts.benchmark.compiler_resolver's deterministic, multi-format
    resolver -- foundry.toml solc/solc_version/solc-version under any
    profile, Hardhat's solidity.compilers[].version, a Dockerfile's own
    solc-select directive, pragma fallback only as a last resort), then
    sets exactly one of two mutually-exclusive env vars bin/forge reads:

    - a single required version -> BENCHMARK_SOLC_PATH (the existing,
      simpler `--use <path>` global pin).
    - genuinely multiple required versions (e.g. a project's own `src/`
      pins one version while a handful of test-mock/script files pin
      another, confirmed real for 2024-06-size/2025-06-panoptic/2024-07-
      basin -- not an authoring conflict, see compiler_resolver's own
      docstring) -> populates this process's CONTAINER_HOME with a real
      `~/.svm/<version>/solc-<version>` entry for every required version
      (populate_svm_cache) and sets BENCHMARK_FORGE_OFFLINE_AUTODETECT=1,
      so bin/forge passes `--offline` and lets Foundry's OWN per-file
      auto-detection resolve each source file against the provisioned set
      -- confirmed live: zero network access, fails closed (never a
      silent download) for any version not pre-populated.

    Returns a detail string for logging. Raises BuildFailed if resolution
    is not RESOLVED (under BENCHMARK_STRICT_OFFLINE), or if any required
    version cannot be provisioned/populated.
    """
    resolution = resolve_compiler(target)
    if resolution.status is not CompilerResolutionStatus.RESOLVED:
        if audit_id is not None:
            LAST_COMPILER_SELECTION[audit_id] = {
                "status": resolution.status.value, "versions": [], "mode": None, "detail": resolution.detail,
            }
        if BENCHMARK_STRICT_OFFLINE:
            raise BuildFailed(f"{resolution.status.value}: {resolution.detail}")
        os.environ.pop("BENCHMARK_SOLC_PATH", None)
        os.environ.pop("BENCHMARK_FORGE_OFFLINE_AUTODETECT", None)
        return resolution.detail

    try:
        entries = [provision_solc(v, toolchain_dir, _official_checksums()) for v in resolution.versions]
        if len(entries) > 1:
            populate_svm_cache(resolution.versions, toolchain_dir, Path(CONTAINER_HOME))
    except Exception as e:  # noqa: BLE001 -- structured taxonomy, not an uncaught crash
        raise BuildFailed(f"TOOLCHAIN_NOT_PROVISIONED: could not provision/populate "
                           f"{resolution.versions}: {e}") from e

    if len(entries) == 1:
        os.environ["BENCHMARK_SOLC_PATH"] = entries[0].path
        os.environ.pop("BENCHMARK_FORGE_OFFLINE_AUTODETECT", None)
        mode = "single_use_pin"
    else:
        os.environ["BENCHMARK_FORGE_OFFLINE_AUTODETECT"] = "1"
        os.environ.pop("BENCHMARK_SOLC_PATH", None)
        mode = "multi_version_offline_autodetect"
    if audit_id is not None:
        LAST_COMPILER_SELECTION[audit_id] = {
            "status": resolution.status.value, "versions": resolution.versions, "mode": mode,
            "detail": resolution.detail,
        }
    return resolution.detail


def compile_generic(audit_id: str, dest: Path, repair: EnvRepair, toolchain_dir: Path | None = None) -> ProgramGraph:
    rcd = _run_cmd_dir(EVMBENCH_ROOT, audit_id)
    target = dest / rcd
    os.environ["FORGE_GIT_ROOT"] = str(dest)
    try:
        if needs_npm_install(target):
            ok, out = sh("npm install --no-audit --no-fund", target, git_root=dest, timeout=900)
            if not ok:
                raise BuildFailed(f"npm install (hybrid npm+forge deps) failed: {out[-1000:]}")
        ok, out = sh("forge install", target, git_root=dest, timeout=600)
        if not ok:
            raise BuildFailed(f"forge install failed: {out[-1000:]}")

        if toolchain_dir is not None:
            # Explicit path (Phase 1-3): deterministic resolver + checksum-
            # verified provisioning, never svm's own implicit download.
            _select_compiler(target, toolchain_dir, audit_id=audit_id)
            os.environ.pop("FORGE_FORCE_SOLC", None)
        else:
            # Legacy path (kept for callers that haven't opted into
            # toolchain provisioning): the old hand-curated hint file plus
            # a bare pragma scan, both strictly weaker than the resolver
            # above -- superseded, not removed, so existing non-benchmark
            # callers of this function are unaffected.
            pinned = SOLC_DISCOVERY.get(audit_id, {}).get("solc")
            guessed = pinned or detect_pragma_solc(target)
            if guessed:
                os.environ["FORGE_FORCE_SOLC"] = guessed
            else:
                os.environ.pop("FORGE_FORCE_SOLC", None)
        result = repair.build_until_success(target)
        return result.graph
    finally:
        os.environ.pop("FORGE_FORCE_SOLC", None)
        os.environ.pop("BENCHMARK_SOLC_PATH", None)
        os.environ.pop("BENCHMARK_FORGE_OFFLINE_AUTODETECT", None)
        os.environ.pop("FORGE_GIT_ROOT", None)


def compile_generic_hardhat(audit_id: str, dest: Path) -> ProgramGraph:
    rcd = _run_cmd_dir(EVMBENCH_ROOT, audit_id)
    target = dest / rcd
    ok, out = sh("npm install --no-audit --no-fund", target, git_root=dest, timeout=900)
    if not ok:
        raise BuildFailed(f"npm install failed: {out[-1000:]}")
    return ProgramGraph.build(target)


def compile_npm_hardhat_force(audit_id: str, dest: Path, subdir: str = ".", extra: list[str] | None = None) -> ProgramGraph:
    target = dest / subdir
    ok, out = sh("npm install --force", target, git_root=dest, timeout=900)
    if not ok:
        raise BuildFailed(f"npm install failed: {out[-1000:]}")
    for cmd in (extra or []):
        sh(cmd, target, git_root=dest, timeout=300)
    ok, out = sh("npx hardhat compile", target, git_root=dest, timeout=900)
    if not ok:
        raise BuildFailed(f"npx hardhat compile failed: {out[-1000:]}")
    return ProgramGraph.build(target)


def compile_ethereumcreditguild(dest: Path, toolchain_dir: Path | None = None) -> ProgramGraph:
    import os
    os.environ["FORGE_VERSION"] = "nightly-5b7e4cb3c882b28f3c32ba580de27ce7381f415a"
    os.environ["FORGE_GIT_ROOT"] = str(dest)
    try:
        ok, out = sh("forge install", dest, git_root=dest, timeout=600)
        if not ok:
            raise BuildFailed(f"forge install failed: {out[-1000:]}")
        ok, out = sh("npm install", dest, git_root=dest, timeout=900)
        if not ok:
            raise BuildFailed(f"npm install failed: {out[-1000:]}")
        if toolchain_dir is not None:
            # Wired to the same deterministic resolver/provisioning as
            # compile_generic (Phase 2) -- confirmed real: this audit's own
            # src/test code unanimously pins 0.8.13 once forge-std's
            # vendored-outside-lib/ range pragmas are correctly excluded
            # (see compiler_resolver's nested-vendor-dir + exact-pin
            # fixes); FORGE_VERSION above pins the Foundry *tool* release
            # this project's own forge-std/solmate versions require, an
            # entirely separate concern from the Solidity *compiler*
            # version selected here.
            _select_compiler(dest, toolchain_dir, audit_id="2023-12-ethereumcreditguild")
        return ProgramGraph.build(dest)
    finally:
        os.environ.pop("FORGE_VERSION", None)
        os.environ.pop("FORGE_GIT_ROOT", None)
        os.environ.pop("BENCHMARK_SOLC_PATH", None)
        os.environ.pop("BENCHMARK_FORGE_OFFLINE_AUTODETECT", None)


def compile_size(dest: Path, toolchain_dir: Path | None = None) -> ProgramGraph:
    import os
    os.environ["FORGE_VERSION"] = "v0.3.0"
    os.environ["FORGE_GIT_ROOT"] = str(dest)
    try:
        ok, out = sh("forge install", dest, git_root=dest, timeout=600)
        if not ok:
            raise BuildFailed(f"forge install failed: {out[-1000:]}")
        if toolchain_dir is not None:
            # Genuinely multi-version (0.8.13/0.8.19/0.8.23 -- a dominant
            # src/ pin plus a few test-mock/script files pinned
            # differently, confirmed real, not an authoring conflict) --
            # routes through _select_compiler's offline-autodetect branch.
            _select_compiler(dest, toolchain_dir, audit_id="2024-06-size")
        return ProgramGraph.build(dest)
    finally:
        os.environ.pop("FORGE_VERSION", None)
        os.environ.pop("FORGE_GIT_ROOT", None)
        os.environ.pop("BENCHMARK_SOLC_PATH", None)
        os.environ.pop("BENCHMARK_FORGE_OFFLINE_AUTODETECT", None)


def compile_noya(dest: Path, toolchain_dir: Path | None = None) -> ProgramGraph:
    sh("npm install --force", dest, git_root=dest, timeout=900)
    sh("npx hardhat compile", dest, git_root=dest, timeout=900)
    try:
        if toolchain_dir is not None:
            # Resolves cleanly to a single version (0.8.20, via
            # hardhat.config.ts) -- was simply never wired to the
            # provisioned toolchain/BENCHMARK_SOLC_PATH at all before this.
            _select_compiler(dest, toolchain_dir, audit_id="2024-04-noya")
        sh("forge install", dest, git_root=dest, timeout=600)
        return ProgramGraph.build(dest)
    finally:
        os.environ.pop("BENCHMARK_SOLC_PATH", None)
        os.environ.pop("BENCHMARK_FORGE_OFFLINE_AUTODETECT", None)


def compile_thorchain(dest: Path) -> dict[str, ProgramGraph]:
    """Returns {subdir_name: graph} -- thorchain builds TWO independent
    Hardhat projects (ethereum/, avalanche/); ground-truth findings only
    cite files under ethereum/contracts/, but both are real compiled units
    MGPR would route in production, so both contribute route_manifest rows
    tagged to this audit_id; only 'ethereum' can ever match a citation."""
    graphs = {}
    for sub in ("ethereum", "avalanche"):
        target = dest / sub
        cfg_src = EVMBENCH_ROOT / "audits" / "2024-06-thorchain" / sub / "hardhat.config.js"
        dst_name = "hardhat.config.js" if sub == "ethereum" else "hardhat.config.ts"
        if cfg_src.exists():
            shutil.copy(cfg_src, target / dst_name)
        ok, out = sh("npm install --legacy-peer-deps", target, git_root=dest, timeout=900)
        if not ok:
            print(f"  thorchain/{sub}: npm install failed, skipping this subgraph: {out[-300:]}")
            continue
        sh("npx hardhat clean", target, git_root=dest, timeout=300)
        ok, out = sh("npx hardhat compile", target, git_root=dest, timeout=900)
        if not ok:
            print(f"  thorchain/{sub}: hardhat compile failed, skipping this subgraph: {out[-300:]}")
            continue
        try:
            graphs[sub] = ProgramGraph.build(target)
        except BuildFailed as e:
            print(f"  thorchain/{sub}: ProgramGraph.build failed, skipping this subgraph: {e}")
    return graphs


def evaluate_and_accumulate(audit_id, pg, checkout_root, run_cmd_dir, registry_by_id, spec,
                             all_gate_rows, all_route_rows, all_context_rows, per_family, not_applicable_counter,
                             evaluate_findings=True):
    """`evaluate_findings=False` skips gate_evaluation.jsonl / feasibility_report
    contributions for this call -- used for multi-subgraph audits (thorchain:
    ethereum/ + avalanche/, two independently compiled projects under one
    audit_id) so each ground-truth finding is evaluated exactly once, against
    whichever subgraph its citation actually resolves in, instead of once per
    subgraph (which double-counted every thorchain finding in an earlier
    version of this script -- confirmed live: findings_considered summed to
    52 instead of the correct 50 before this fix). route_manifest/
    context_manifest rows are NOT subject to this double-count risk (each
    subgraph's fired routes are genuinely distinct routing units) and are
    always recorded regardless of this flag.
    """
    features = FeatureExtractor.compute(pg)
    audit = registry_by_id.get(audit_id)
    findings = audit["findings"] if audit else []

    route_rows, context_rows = build_route_and_context_manifests(
        audit_id, pg, features, spec, findings, checkout_root, run_cmd_dir
    )
    all_route_rows.extend(route_rows)
    all_context_rows.extend(context_rows)
    if not evaluate_findings:
        return 0

    for finding in findings:
        gate_rows = _evaluate_finding(finding, pg, features, spec, checkout_root, run_cmd_dir)
        all_gate_rows.extend(gate_rows)
        family = gate_rows[0]["expected_primary_family"] if gate_rows else None
        if family is None:
            not_applicable_counter[0] += 1
            continue
        fam_report = per_family[family]
        fam_report["findings_considered"] += 1
        fired_any = False
        for row in gate_rows:
            if row["routing_unit"] is None:
                fam_report["unresolved_routing_unit_count"] += 1
                continue
            for pred in row["predicates"]:
                key = f"{pred['predicate']}:{pred['status']}"
                fam_report["predicate_status_counts"][key] = fam_report["predicate_status_counts"].get(key, 0) + 1
            if row["route_would_fire"]:
                fired_any = True
            else:
                blocker = row["reason"].split(":")[0]
                fam_report["blocking_reason_histogram"][blocker] = fam_report["blocking_reason_histogram"].get(blocker, 0) + 1
        if fired_any:
            fam_report["route_fire_count"] += 1
        else:
            fam_report["route_not_fire_count"] += 1
    return len(findings)


# Phase 5 (cross-run reproducibility validation): each of the 3 required
# independent cold-start runs must process audits in a genuinely different
# order, so that any hidden cross-audit state leak (a global left set by
# one audit silently affecting the NEXT one processed, e.g. an env var
# this script forgot to pop in a `finally`) would show up as an
# order-dependent result instead of being masked by always running the
# same sequence. Deterministic given a seed (so a specific run is still
# individually reproducible/debuggable), but the seed itself varies across
# the 3 runs by design -- BENCHMARK_AUDIT_ORDER_SEED, unset by default
# (original fixed ALL_27 order, matching every run before this).
_AUDIT_ORDER_SEED = os.environ.get("BENCHMARK_AUDIT_ORDER_SEED")


def audit_order() -> list[str]:
    if _AUDIT_ORDER_SEED is None:
        return list(ALL_27)
    order = list(ALL_27)
    random.Random(int(_AUDIT_ORDER_SEED)).shuffle(order)
    return order


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    order = audit_order()
    (OUT_DIR / "audit_order.json").write_text(json.dumps(
        {"seed": _AUDIT_ORDER_SEED, "order": order}, indent=2))

    registry = [json.loads(l) for l in REGISTRY_PATH.read_text().splitlines() if l.strip()]
    registry_by_id = {a["audit_id"]: a for a in registry}
    spec = load_routing_spec(ROUTING_SPEC_PATH, known_predicates=KNOWN_PREDICATES)
    repair = EnvRepair()

    build_rows = []
    graph_rows = []
    all_gate_rows, all_route_rows, all_context_rows = [], [], []
    per_family = {
        name: {"findings_considered": 0, "predicate_status_counts": {}, "route_fire_count": 0,
               "route_not_fire_count": 0, "unresolved_routing_unit_count": 0, "blocking_reason_histogram": {}}
        for name in ("P1_AUTHORIZATION", "P2_REENTRANCY", "P5_ARITHMETIC_PRECISION")
    }
    not_applicable_counter = [0]
    findings_reached = 0

    for audit_id in order:
        print(f"\n--- STUDY {audit_id} ---", flush=True)
        dest = WORK_DIR / audit_id
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        ok, err = clone(audit_id, dest)
        if not ok:
            print(f"CLONE FAILED (unexpected for a known-compiling audit): {err}")
            build_rows.append({"audit_id": audit_id, "status": "COMPILE_FAILED", "reason": f"reclone failed: {err}",
                                "compiler_selection": None})
            continue

        try:
            if audit_id == "2024-06-thorchain":
                graphs = compile_thorchain(dest)
                rcd = "."  # citation paths already include "ethereum/..." prefix
                # findings only cite ethereum/contracts/... -- evaluate
                # ground-truth findings against that subgraph ONLY (else
                # every finding gets double-counted: once resolved against
                # ethereum, once spuriously UNRESOLVED against avalanche).
                # route_manifest/context_manifest still get BOTH subgraphs'
                # fired routes, via evaluate_findings=False on avalanche.
                n_findings = 0
                for sub, pg in sorted(graphs.items()):
                    n_findings = evaluate_and_accumulate(
                        audit_id, pg, dest, rcd, registry_by_id, spec,
                        all_gate_rows, all_route_rows, all_context_rows, per_family, not_applicable_counter,
                        evaluate_findings=(sub == "ethereum"),
                    )
                findings_reached += n_findings
                nc = {}
                for pg in graphs.values():
                    for _, d in pg.graph.nodes(data=True):
                        nc[d.get("kind", "unknown")] = nc.get(d.get("kind", "unknown"), 0) + 1
                build_rows.append({"audit_id": audit_id, "status": "COMPILED", "reason": f"subgraphs: {sorted(graphs)}",
                                    "compiler_selection": None})
                graph_rows.append({"audit_id": audit_id, "status": "COMPILED", "node_counts": nc})
                print(f"COMPILED (2 subgraphs) {audit_id}: {nc}", flush=True)
            else:
                if audit_id in GENERIC_AUDITS:
                    if audit_id == "2025-02-thorwallet":
                        pg = compile_generic_hardhat(audit_id, dest)
                    else:
                        pg = compile_generic(audit_id, dest, repair, toolchain_dir=TOOLCHAIN_DIR)
                elif audit_id in ("2023-10-nextgen",):
                    pg = compile_npm_hardhat_force(audit_id, dest, subdir="hardhat", extra=["npm up hardhat"])
                elif audit_id in ("2024-01-curves", "2024-07-traitforge", "2025-04-virtuals", "2025-05-blackhole"):
                    pg = compile_npm_hardhat_force(audit_id, dest, subdir=".")
                elif audit_id == "2023-12-ethereumcreditguild":
                    pg = compile_ethereumcreditguild(dest, toolchain_dir=TOOLCHAIN_DIR)
                elif audit_id == "2024-06-size":
                    pg = compile_size(dest, toolchain_dir=TOOLCHAIN_DIR)
                elif audit_id == "2024-04-noya":
                    pg = compile_noya(dest, toolchain_dir=TOOLCHAIN_DIR)
                else:
                    raise RuntimeError(f"no recipe registered for {audit_id}")

                rcd = _run_cmd_dir(EVMBENCH_ROOT, audit_id)
                checkout_root = dest
                n_findings = evaluate_and_accumulate(
                    audit_id, pg, checkout_root, rcd, registry_by_id, spec,
                    all_gate_rows, all_route_rows, all_context_rows, per_family, not_applicable_counter,
                )
                findings_reached += n_findings
                nc = {}
                for _, d in pg.graph.nodes(data=True):
                    nc[d.get("kind", "unknown")] = nc.get(d.get("kind", "unknown"), 0) + 1
                build_rows.append({"audit_id": audit_id, "status": "COMPILED", "reason": None,
                                    "compiler_selection": LAST_COMPILER_SELECTION.get(audit_id)})
                graph_rows.append({"audit_id": audit_id, "status": "COMPILED", "node_counts": nc})
                print(f"COMPILED {audit_id}: {nc}", flush=True)
        except BuildFailed as e:
            reason = str(e)[:1000]
            status = classify_build_failure(reason)
            build_rows.append({"audit_id": audit_id, "status": status, "reason": reason,
                                "compiler_selection": LAST_COMPILER_SELECTION.get(audit_id)})
            graph_rows.append({"audit_id": audit_id, "status": status, "node_counts": {}})
            print(f"{status} {audit_id}: {reason[:300]}", flush=True)
        finally:
            LAST_COMPILER_SELECTION.pop(audit_id, None)
            shutil.rmtree(dest, ignore_errors=True)
            clear_container_home_caches()

        (OUT_DIR / "build_manifest.jsonl").write_text("\n".join(json.dumps(r, sort_keys=True) for r in build_rows) + "\n")
        (OUT_DIR / "graph_manifest.jsonl").write_text("\n".join(json.dumps(r, sort_keys=True) for r in graph_rows) + "\n")
        (OUT_DIR / "gate_evaluation.jsonl").write_text("\n".join(json.dumps(r, sort_keys=True) for r in all_gate_rows) + "\n")
        (OUT_DIR / "route_manifest.jsonl").write_text("\n".join(json.dumps(r, sort_keys=True) for r in all_route_rows) + "\n")
        (OUT_DIR / "context_manifest.jsonl").write_text("\n".join(json.dumps(r, sort_keys=True) for r in all_context_rows) + "\n")

    total_findings_in_registry = sum(len(a["findings"]) for a in registry)
    feasibility_report = {
        "registry_size": len(registry),
        "audits_attempted_this_study": len(ALL_27),
        "audits_compiled": sum(1 for r in build_rows if r["status"] == "COMPILED"),
        "total_findings_in_registry": total_findings_in_registry,
        "findings_reached_compiled_audits": findings_reached,
        "findings_blocked_by_audit_compile_status": total_findings_in_registry - findings_reached,
        "findings_not_applicable_to_p1_p2_p5": not_applicable_counter[0],
        "total_fired_routes_across_compiled_audits": len(all_route_rows),
        "per_family": per_family,
    }
    (OUT_DIR / "feasibility_report.json").write_text(json.dumps(feasibility_report, indent=2, sort_keys=True))

    print("\n=== FULL STUDY DONE ===")
    print(json.dumps(feasibility_report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
