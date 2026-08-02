"""Third pass: replicate each remaining audit's OWN Dockerfile build recipe
verbatim (pinned Foundry version via foundryup, correct package manager,
correct flags, correct per-audit subdirectories, bundled config-file
overrides) instead of the generic one-size-fits-all approach from passes 1
and 2. Only the BUILD/COMPILE steps are replicated, not `forge test`/
`npx hardhat test` (unnecessary for producing Slither-readable artifacts,
and some take 10+ minutes by the Dockerfile's own comment).

10 of the 22 remaining audits have a Dockerfile that is JUST `git clone` --
no build step at all. Those are reported as NOT_BUILD_VERIFIED_BY_HARNESS,
not attempted: forcing a generic build on them would not be "replicating
the recipe", since the recipe has none.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from a4v.graph import ProgramGraph, BuildFailed

SIF = "/scratch/md5344/evmbench/containers/evmbench-worker.sif"
AGENT4VUL = str(_REPO_ROOT)
# CONTAINER_HOME/REAL_TMP default to the same shared, mutable locations
# this script has always used (backward compatible for interactive/
# debugging use), but are overridable via env vars -- the hermetic offline
# runner (scripts/benchmark/run_offline.py) always sets both to a fresh,
# run-scoped directory under .benchmark/runs/<run_id>/, never a previous
# session's job-scratch path. REAL_TMP previously hardcoded exactly such a
# path (a specific prior session's /scratch/.../jobs/506f33b3/tmp/...),
# which does not exist in a fresh session -- confirmed live as one of this
# repo's own instances of the session-state-dependency problem this work
# exists to eliminate.
CONTAINER_HOME = os.environ.get("BENCHMARK_CONTAINER_HOME", f"{AGENT4VUL}/.container_home")
FOUNDRY_VERSIONS = os.environ.get("BENCHMARK_FOUNDRY_VERSIONS", f"{AGENT4VUL}/.venv/.foundry-versions")
REAL_TMP = os.environ.get("BENCHMARK_CONTAINER_TMP", f"{AGENT4VUL}/.container_tmp")
# singularity's --bind requires every source path to already exist.
Path(CONTAINER_HOME).mkdir(parents=True, exist_ok=True)
Path(REAL_TMP).mkdir(parents=True, exist_ok=True)
EVMBENCH_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")
WORK_DIR = Path("/scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_full_run2/checkout_scratch3")
OUT_DIR = Path("/scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_full_run2")

NO_BUILD_AUDITS = {
    "2024-01-init-capital-invitational", "2024-02-althea-liquid-infrastructure",
    "2024-03-abracadabra-money", "2024-03-canto", "2024-03-coinbase",
    "2024-03-gitcoin", "2024-03-neobase", "2024-05-arbitrum-foundation",
    "2024-07-munchables", "2025-01-next-generation",
}


def sh(cmd: str, cwd: Path, git_root: Path | None = None, timeout: int = 900) -> tuple[bool, str]:
    binds = [f"{CONTAINER_HOME}:/home/build_home", f"{cwd}:{cwd}",
             f"{AGENT4VUL}:{AGENT4VUL}", f"{REAL_TMP}:/tmp"]
    if git_root and git_root != cwd:
        binds.append(f"{git_root}:{git_root}")
    bind_args = []
    for b in binds:
        bind_args += ["--bind", b]
    full_cmd = ["singularity", "exec", "--containall", "--no-home", "--pwd", str(cwd),
                *bind_args, SIF, "bash", "-c", f"export HOME=/home/build_home; {cmd}"]
    r = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout or "") + (r.stderr or "")
    out = "\n".join(l for l in out.splitlines() if "Could not find any nv" not in l
                     and "nvliblist.conf" not in l and l.strip() != "INFO:")
    return r.returncode == 0, out


def clone(audit_id: str, dest: Path) -> tuple[bool, str]:
    url = f"https://github.com/evmbench-org/{audit_id}.git"
    r = subprocess.run(["git", "clone", "--quiet", "--recurse", url, str(dest)],
                        capture_output=True, text=True, timeout=900)
    return r.returncode == 0, r.stderr[-500:]


def clear_container_home_caches() -> None:
    """npm/yarn/pnpm/hardhat each cache packages under CONTAINER_HOME (shared
    across every audit, since it's the one writable $HOME all these recipes
    use) and none of it is cleaned by the per-audit checkout rmtree -- it
    silently grew to 92,912 files / 3.4GB over one run of this script and
    pushed the account's file-count quota to 114%. It's pure, regenerable
    package cache, safe to clear after every audit."""
    for sub in (".npm", ".cache", ".yarn", ".local/share/pnpm", ".local/state/pnpm",
                ".local/share/hardhat-nodejs", ".local/share/buidler-nodejs", ".config/hardhat-nodejs"):
        shutil.rmtree(Path(CONTAINER_HOME) / sub, ignore_errors=True)


def graph_summary(pg: ProgramGraph):
    node_counts, edge_counts = {}, {}
    for _, d in pg.graph.nodes(data=True):
        node_counts[d.get("kind", "unknown")] = node_counts.get(d.get("kind", "unknown"), 0) + 1
    for _, _, d in pg.graph.edges(data=True):
        edge_counts[d.get("kind", "unknown")] = edge_counts.get(d.get("kind", "unknown"), 0) + 1
    return node_counts, edge_counts


def try_build(target: Path) -> tuple[bool, str, dict, dict]:
    try:
        pg = ProgramGraph.build(target)
        nc, ec = graph_summary(pg)
        return True, "", nc, ec
    except BuildFailed as e:
        return False, str(e)[:1200], {}, {}


# --- per-audit recipes -------------------------------------------------

def recipe_npm_hardhat(audit_id: str, dest: Path, subdir: str = ".", extra_npm: list[str] | None = None):
    target = dest / subdir
    npm_flags = " ".join(extra_npm or ["--force"])
    ok, out = sh(f"npm install {npm_flags}", target, git_root=dest, timeout=900)
    if not ok:
        return "COMPILE_FAILED", f"npm install failed: {out[-1000:]}", {}, {}
    ok, out = sh("npx hardhat compile", target, git_root=dest, timeout=900)
    if not ok:
        return "COMPILE_FAILED", f"npx hardhat compile failed: {out[-1000:]}", {}, {}
    ok, reason, nc, ec = try_build(target)
    return ("COMPILED" if ok else "COMPILE_FAILED"), reason, nc, ec


def recipe_2023_10_nextgen(dest: Path):
    target = dest / "hardhat"
    ok, out = sh("npm install --force", target, git_root=dest, timeout=900)
    if not ok:
        return "COMPILE_FAILED", f"npm install failed: {out[-1000:]}", {}, {}
    sh("npm up hardhat", target, git_root=dest, timeout=300)  # best-effort, Dockerfile runs it unconditionally
    ok, out = sh("npx hardhat compile", target, git_root=dest, timeout=900)
    if not ok:
        return "COMPILE_FAILED", f"npx hardhat compile failed: {out[-1000:]}", {}, {}
    ok, reason, nc, ec = try_build(target)
    return ("COMPILED" if ok else "COMPILE_FAILED"), reason, nc, ec


def recipe_2023_12_ethereumcreditguild(dest: Path):
    version = "nightly-5b7e4cb3c882b28f3c32ba580de27ce7381f415a"
    import os
    os.environ["FORGE_VERSION"] = version
    os.environ["FORGE_GIT_ROOT"] = str(dest)
    try:
        ok, out = sh("forge install", dest, git_root=dest, timeout=600)
        if not ok:
            return "COMPILE_FAILED", f"forge install failed: {out[-1000:]}", {}, {}
        # Dockerfile also runs `npm install; npm run test` after foundryup --
        # the remappings resolve some imports (e.g. @openzeppelin) through
        # node_modules, not lib/, so skipping this (as the first version of
        # this recipe did) leaves those unresolved. `npm run test` itself is
        # skipped (runs the actual forge test suite, not needed to compile).
        ok, out = sh("npm install", dest, git_root=dest, timeout=900)
        if not ok:
            return "COMPILE_FAILED", f"npm install failed: {out[-1000:]}", {}, {}
        ok, reason, nc, ec = try_build(dest)
        return ("COMPILED" if ok else "COMPILE_FAILED"), reason, nc, ec
    finally:
        os.environ.pop("FORGE_VERSION", None)
        os.environ.pop("FORGE_GIT_ROOT", None)


def recipe_2024_06_thorchain(dest: Path):
    results = {}
    for sub in ("ethereum", "avalanche"):
        target = dest / sub
        src_cfg = EVMBENCH_ROOT / "audits" / "2024-06-thorchain" / sub / "hardhat.config.js"
        dst_name = "hardhat.config.js" if sub == "ethereum" else "hardhat.config.ts"
        if src_cfg.exists():
            shutil.copy(src_cfg, target / dst_name)
        ok, out = sh("npm install --legacy-peer-deps", target, git_root=dest, timeout=900)
        if not ok:
            results[sub] = ("COMPILE_FAILED", f"npm install failed: {out[-800:]}", {}, {})
            continue
        sh("npx hardhat clean", target, git_root=dest, timeout=300)
        ok, out = sh("npx hardhat compile", target, git_root=dest, timeout=900)
        if not ok:
            results[sub] = ("COMPILE_FAILED", f"npx hardhat compile failed: {out[-800:]}", {}, {})
            continue
        ok, reason, nc, ec = try_build(target)
        results[sub] = ("COMPILED" if ok else "COMPILE_FAILED", reason, nc, ec)
    all_ok = all(v[0] == "COMPILED" for v in results.values())
    reason = "; ".join(f"{k}: {v[0]}" + (f" ({v[1][:200]})" if v[0] != "COMPILED" else "") for k, v in results.items())
    nc_merged, ec_merged = {}, {}
    for _, _, nc, ec in results.values():
        for k, v in nc.items():
            nc_merged[k] = nc_merged.get(k, 0) + v
        for k, v in ec.items():
            ec_merged[k] = ec_merged.get(k, 0) + v
    return ("COMPILED" if all_ok else "PARTIALLY_COMPILED"), reason, nc_merged, ec_merged


def recipe_2024_05_olas(dest: Path):
    results = {}
    for sub in ("tokenomics", "registries", "governance"):
        target = dest / sub
        if not target.exists():
            results[sub] = ("COMPILE_FAILED", "subdir not present after clone", {}, {})
            continue
        ok, out = sh("yarn install", target, git_root=dest, timeout=900)
        if not ok:
            results[sub] = ("COMPILE_FAILED", f"yarn install failed: {out[-800:]}", {}, {})
            continue
        ok, out = sh("npx hardhat compile", target, git_root=dest, timeout=900)
        if not ok:
            results[sub] = ("COMPILE_FAILED", f"npx hardhat compile failed: {out[-800:]}", {}, {})
            continue
        ok, reason, nc, ec = try_build(target)
        results[sub] = ("COMPILED" if ok else "COMPILE_FAILED", reason, nc, ec)
    all_ok = all(v[0] == "COMPILED" for v in results.values())
    reason = "; ".join(f"{k}: {v[0]}" + (f" ({v[1][:200]})" if v[0] != "COMPILED" else "") for k, v in results.items())
    nc_merged, ec_merged = {}, {}
    for _, _, nc, ec in results.values():
        for k, v in nc.items():
            nc_merged[k] = nc_merged.get(k, 0) + v
        for k, v in ec.items():
            ec_merged[k] = ec_merged.get(k, 0) + v
    return ("COMPILED" if all_ok else "PARTIALLY_COMPILED"), reason, nc_merged, ec_merged


def recipe_forge_pinned(dest: Path, version: str):
    import os
    os.environ["FORGE_VERSION"] = version
    os.environ["FORGE_GIT_ROOT"] = str(dest)
    try:
        ok, out = sh("forge install", dest, git_root=dest, timeout=600)
        if not ok:
            return "COMPILE_FAILED", f"forge install failed: {out[-1000:]}", {}, {}
        ok, reason, nc, ec = try_build(dest)
        return ("COMPILED" if ok else "COMPILE_FAILED"), reason, nc, ec
    finally:
        os.environ.pop("FORGE_VERSION", None)
        os.environ.pop("FORGE_GIT_ROOT", None)


def recipe_2024_03_taiko(dest: Path):
    import os
    target = dest / "packages" / "protocol"
    version = "nightly-de33b6af53005037b463318d2628b5cfcaf39916"
    ok, out = sh("pnpm install", target, git_root=dest, timeout=900)
    if not ok:
        return "COMPILE_FAILED", f"pnpm install failed: {out[-1000:]}", {}, {}
    script = EVMBENCH_ROOT / "audits" / "2024-03-taiko" / "replace_symlinks_with_real_files.sh"
    if script.exists():
        shutil.copy(script, target / "replace_symlinks_with_real_files.sh")
        ok, out = sh("bash replace_symlinks_with_real_files.sh", target, git_root=dest, timeout=300)
        if not ok:
            return "COMPILE_FAILED", f"replace_symlinks script failed: {out[-800:]}", {}, {}
    os.environ["FORGE_VERSION"] = version
    os.environ["FORGE_GIT_ROOT"] = str(dest)
    try:
        ok, out = sh("pnpm compile", target, git_root=dest, timeout=900)
        if not ok:
            return "COMPILE_FAILED", f"pnpm compile failed: {out[-1000:]}", {}, {}
        ok, reason, nc, ec = try_build(target)
        return ("COMPILED" if ok else "COMPILE_FAILED"), reason, nc, ec
    finally:
        os.environ.pop("FORGE_VERSION", None)
        os.environ.pop("FORGE_GIT_ROOT", None)


def recipe_2024_04_noya(dest: Path):
    ok, out = sh("npm install --force", dest, git_root=dest, timeout=900)
    if not ok:
        return "COMPILE_FAILED", f"npm install failed: {out[-1000:]}", {}, {}
    ok, out = sh("npx hardhat compile", dest, git_root=dest, timeout=900)
    hardhat_ok = ok
    ok, out2 = sh("forge install", dest, git_root=dest, timeout=600)
    forge_ok = ok
    ok, reason, nc, ec = try_build(dest)
    status = "COMPILED" if ok else "COMPILE_FAILED"
    detail = reason if not ok else f"hardhat_compile_ok={hardhat_ok} forge_install_ok={forge_ok}"
    return status, detail, nc, ec


RECIPES = {
    "2023-10-nextgen": lambda dest: recipe_2023_10_nextgen(dest),
    "2024-01-curves": lambda dest: recipe_npm_hardhat("2024-01-curves", dest),
    "2024-07-traitforge": lambda dest: recipe_npm_hardhat("2024-07-traitforge", dest),
    "2025-04-virtuals": lambda dest: recipe_npm_hardhat("2025-04-virtuals", dest),
    "2025-05-blackhole": lambda dest: recipe_npm_hardhat("2025-05-blackhole", dest),
    "2023-12-ethereumcreditguild": recipe_2023_12_ethereumcreditguild,
    "2024-06-thorchain": recipe_2024_06_thorchain,
    "2024-05-olas": recipe_2024_05_olas,
    "2024-06-size": lambda dest: recipe_forge_pinned(dest, "v0.3.0"),
    "2024-08-wildcat": lambda dest: recipe_forge_pinned(dest, "v0.3.0"),
    "2024-03-taiko": recipe_2024_03_taiko,
    "2024-04-noya": recipe_2024_04_noya,
}


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    build_rows, graph_rows = [], []

    for audit_id in sorted(NO_BUILD_AUDITS):
        build_rows.append({"audit_id": audit_id, "status": "NOT_BUILD_VERIFIED_BY_HARNESS",
                            "reason": "audit's own Dockerfile has no build/compile step at all -- "
                                      "the original EVMbench harness never verifies this audit compiles"})
        graph_rows.append({"audit_id": audit_id, "status": "NOT_BUILD_VERIFIED_BY_HARNESS",
                            "node_counts": {}, "edge_counts": {}})
    print(f"{len(NO_BUILD_AUDITS)} audits marked NOT_BUILD_VERIFIED_BY_HARNESS (no Dockerfile build step)", flush=True)

    for audit_id, recipe in RECIPES.items():
        dest = WORK_DIR / audit_id
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        print(f"\n--- RECIPE {audit_id} ---", flush=True)
        ok, err = clone(audit_id, dest)
        if not ok:
            build_rows.append({"audit_id": audit_id, "status": "COMPILE_FAILED",
                                "reason": f"checkout preparation failed: {err}"})
            graph_rows.append({"audit_id": audit_id, "status": "COMPILE_FAILED", "node_counts": {}, "edge_counts": {}})
            shutil.rmtree(dest, ignore_errors=True)
            continue
        try:
            status, reason, nc, ec = recipe(dest)
        except Exception as e:  # noqa: BLE001
            status, reason, nc, ec = "COMPILE_FAILED", f"recipe raised: {e}"[:1000], {}, {}
        build_rows.append({"audit_id": audit_id, "status": status, "reason": reason or None})
        graph_rows.append({"audit_id": audit_id, "status": status, "node_counts": nc, "edge_counts": ec})
        print(f"{status} {audit_id}: {nc if status in ('COMPILED','PARTIALLY_COMPILED') else reason[:300]}", flush=True)
        shutil.rmtree(dest, ignore_errors=True)
        clear_container_home_caches()
        (OUT_DIR / "recipe_build_manifest.jsonl").write_text(
            "\n".join(json.dumps(r, sort_keys=True) for r in build_rows) + "\n")
        (OUT_DIR / "recipe_graph_manifest.jsonl").write_text(
            "\n".join(json.dumps(r, sort_keys=True) for r in graph_rows) + "\n")

    print("\n=== RECIPE PASS DONE ===")
    from collections import Counter
    print(Counter(r["status"] for r in build_rows))


if __name__ == "__main__":
    main()
