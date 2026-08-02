"""Tests for scripts.benchmark.audit_build_manifest -- offline, using
synthetic checkout fixtures (no real clone/network needed)."""
import json
from dataclasses import asdict
from pathlib import Path

import scripts.benchmark.audit_build_manifest as abm
from scripts.benchmark.audit_build_manifest import _clone, build_record_for_subproject
from scripts.benchmark.audit_registry import AuditSpec, SubprojectSpec


def test_clone_does_not_double_apply_cwd(tmp_path, monkeypatch):
    """Regression guard for a real bug found live during this work's own
    validation: `_clone` originally passed `dest` (already a path relative
    to this process's own cwd) to `git clone`, while ALSO overriding the
    subprocess's cwd to `dest.parent` -- making git resolve `dest` a
    second time on top of that override, cloning into the wrong location
    while still reporting success (`ok=True`, but `dest.exists()` was
    False). Every subsequent step in this module reported the correct-
    looking-but-wrong NO_CONFIGURATION_FOUND/BUILD_RECIPE_FAILED status
    for every single audit as a result -- confirmed to reproduce for
    every audit tried, not an isolated fluke."""
    captured = {}

    def _fake_sh(cmd, cwd, timeout=900):
        captured["cwd"] = cwd
        return True, ""

    monkeypatch.setattr(abm, "_sh", _fake_sh)
    dest = tmp_path / "checkouts" / "2024-01-example"
    _clone("2024-01-example", dest)
    assert captured["cwd"] == Path.cwd(), (
        f"expected the subprocess cwd to be this process's own cwd (so `dest`, "
        f"already relative to it, resolves correctly), got {captured['cwd']!r} instead"
    )
    assert captured["cwd"] != dest.parent


def test_missing_subproject_root_is_build_recipe_failed(tmp_path):
    audit = AuditSpec("2099-01-fake", (SubprojectSpec("default", "does-not-exist"),))
    record = build_record_for_subproject(audit, audit.subprojects[0], tmp_path)
    assert record.status == "BUILD_RECIPE_FAILED"
    assert "does-not-exist" in record.failure_reason


def test_resolved_foundry_subproject_record_fields(tmp_path):
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.17"\n')
    (tmp_path / "package-lock.json").write_text('{"lockfileVersion": 3}')
    audit = AuditSpec("2099-01-fake", (SubprojectSpec("default", "."),))
    record = build_record_for_subproject(audit, audit.subprojects[0], tmp_path)
    assert record.status == "RESOLVED"
    assert record.compiler_resolution_status == "RESOLVED"
    assert record.required_compiler_versions == ["0.8.17"]
    assert record.build_system == "FOUNDRY"
    assert record.build_command == "forge build"
    assert record.dependency_lockfile_path == "package-lock.json"
    assert record.dependency_lockfile_sha256 is not None
    assert record.network_required_for_provisioning is True
    assert record.network_allowed_for_benchmark_execution is False


def test_ambiguous_configuration_propagates_as_failure_reason(tmp_path):
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.17"\nsolc_version = "0.8.16"\n')
    audit = AuditSpec("2099-01-fake", (SubprojectSpec("default", "."),))
    record = build_record_for_subproject(audit, audit.subprojects[0], tmp_path)
    assert record.status == "AMBIGUOUS_COMPILER_CONFIGURATION"
    assert record.failure_reason is not None


def test_compatibility_override_recorded_when_present(tmp_path):
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.20"\n')
    audit = AuditSpec(
        "2099-01-fake", (SubprojectSpec("default", "."),),
        foundry_version_override="v0.3.0", override_reason="test override",
    )
    record = build_record_for_subproject(audit, audit.subprojects[0], tmp_path)
    assert record.compatibility_overrides["foundry_version_override"] == "v0.3.0"
    assert record.compatibility_overrides["override_reason"] == "test override"
    assert record.foundry_version == "v0.3.0"


def test_no_compatibility_override_recorded_when_absent(tmp_path):
    """Overrides must not leak into an audit's record when it has none."""
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.20"\n')
    audit = AuditSpec("2099-01-fake", (SubprojectSpec("default", "."),))
    record = build_record_for_subproject(audit, audit.subprojects[0], tmp_path)
    assert record.compatibility_overrides == {}
    assert record.foundry_version is None


# --- item 13: serialization determinism -----------------------------------


def test_record_serializes_deterministically(tmp_path):
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.17"\n')
    audit = AuditSpec("2099-01-fake", (SubprojectSpec("default", "."),))
    r1 = build_record_for_subproject(audit, audit.subprojects[0], tmp_path)
    r2 = build_record_for_subproject(audit, audit.subprojects[0], tmp_path)
    d1, d2 = asdict(r1), asdict(r2)
    d1.pop("source_commit", None)
    d2.pop("source_commit", None)  # only varies if tmp_path were a real git repo mid-history
    assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)
