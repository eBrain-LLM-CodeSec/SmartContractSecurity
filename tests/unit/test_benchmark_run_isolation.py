"""Tests for run-scoped isolation (Phase 4): fresh writable run caches,
no reuse of a parent/sibling checkout's own state, and separation between
immutable provisioned toolchains and per-run mutable build cache."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

_REPO_ROOT = Path(__file__).resolve().parents[2]


# --- item 11: no reuse of parent-worktree .venv / hardcoded main checkout -


def test_agent4vul_root_resolves_to_this_worktree_not_a_hardcoded_path():
    """Regression guard for the actual bug found live during this work's
    own investigation: run_feasibility_study.py, build_manifests.py, and
    run_full_study_batch.py all used to hardcode AGENT4VUL_ROOT to
    /scratch/md5344/evmbench/agent4vul (the main checkout) regardless of
    which worktree the script actually ran from -- silently pointing PATH
    at a stale, less-capable bin/forge and causing audits that compile
    cleanly from the correct worktree (confirmed live: 2024-01-canto,
    2025-04-forte) to fail. All three must resolve dynamically from their
    own file location instead."""
    import scripts.mgpr.run_feasibility_study as rfs
    import scripts.mgpr.build_manifests as bm
    import scripts.mgpr.run_full_study_batch as batch

    for module, name in ((rfs, "run_feasibility_study"), (bm, "build_manifests"), (batch, "run_full_study_batch")):
        root = getattr(module, "_AGENT4VUL_ROOT", None) or getattr(module, "AGENT4VUL_ROOT")
        assert root == _REPO_ROOT, f"{name}'s AGENT4VUL_ROOT resolved to {root}, not this worktree ({_REPO_ROOT})"


def test_run_full_study_batch_agent4vul_root_matches_this_worktree():
    import scripts.mgpr.run_full_study_batch as batch
    assert batch.AGENT4VUL_ROOT == _REPO_ROOT
    assert batch.ROUTING_SPEC_PATH == _REPO_ROOT / "routing_spec.yaml"
    assert batch.ROUTING_SPEC_PATH.exists()


# --- item 10: fresh writable run cache creation ----------------------------


def test_container_home_and_tmp_are_created_if_missing(tmp_path, monkeypatch):
    """run_dockerfile_recipes.sh()'s bind targets must exist before
    Singularity's --bind can succeed -- a fresh run-scoped directory that
    doesn't exist yet must be created, not assumed present."""
    fresh_home = tmp_path / "brand_new_run" / "container_home"
    fresh_tmp = tmp_path / "brand_new_run" / "container_tmp"
    assert not fresh_home.exists()
    assert not fresh_tmp.exists()

    monkeypatch.setenv("BENCHMARK_CONTAINER_HOME", str(fresh_home))
    monkeypatch.setenv("BENCHMARK_CONTAINER_TMP", str(fresh_tmp))
    # re-import to re-run the module-level mkdir calls with the new env
    import importlib
    import scripts.mgpr.run_dockerfile_recipes as rdr
    importlib.reload(rdr)
    try:
        assert fresh_home.exists()
        assert fresh_tmp.exists()
    finally:
        # restore the module to its default (shared) configuration for
        # any other test/process that imports it afterward in this session.
        monkeypatch.delenv("BENCHMARK_CONTAINER_HOME", raising=False)
        monkeypatch.delenv("BENCHMARK_CONTAINER_TMP", raising=False)
        importlib.reload(rdr)


# --- item 18: cleanup without deleting immutable toolchains ---------------


def test_work_dir_and_toolchain_dir_are_distinct_locations():
    """WORK_DIR (per-run mutable checkouts, deleted after every audit) and
    TOOLCHAIN_DIR (immutable, checksum-verified, shared across runs) must
    never be the same directory or nested inside one another -- otherwise
    a per-run cleanup pass risks deleting provisioned toolchains."""
    import scripts.mgpr.run_full_study_batch as batch
    work = batch.WORK_DIR.resolve()
    toolchains = batch.TOOLCHAIN_DIR.resolve()
    assert work != toolchains
    assert toolchains not in work.parents
    assert work not in toolchains.parents
