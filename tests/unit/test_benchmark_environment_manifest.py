"""Tests for scripts.benchmark.generate_environment_manifest -- Phase 5
needs a programmatically-generated (not hand-authored) environment record
per run so a cross-run comparison can distinguish "the code changed" from
"the environment underneath it changed"."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.benchmark.generate_environment_manifest import build_manifest


def test_build_manifest_has_required_top_level_fields():
    manifest = build_manifest()
    for field in ("schema", "generated_at", "os", "container_runtime", "python_version",
                  "git_commit_this_worktree", "run_scoped_environment_variables"):
        assert field in manifest


def test_build_manifest_captures_git_commit_of_this_worktree():
    manifest = build_manifest()
    commit = manifest["git_commit_this_worktree"]
    assert commit is not None
    assert len(commit) == 40  # a real git SHA, not a placeholder


def test_build_manifest_container_image_sha256_present_when_image_exists():
    manifest = build_manifest()
    if manifest["container_runtime"]["image_sha256"] is not None:
        assert len(manifest["container_runtime"]["image_sha256"]) == 64


def test_build_manifest_run_scoped_vars_reflect_current_environment(monkeypatch):
    monkeypatch.setenv("BENCHMARK_AUDIT_ORDER_SEED", "99")
    manifest = build_manifest()
    assert manifest["run_scoped_environment_variables"]["BENCHMARK_AUDIT_ORDER_SEED"] == "99"
