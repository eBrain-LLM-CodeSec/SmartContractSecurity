"""Tests for run_full_study_batch._select_compiler -- the shared
single-vs-multi-version toolchain-selection helper used by compile_generic
and the three previously-unwired bespoke recipes (compile_noya,
compile_ethereumcreditguild, compile_size). Exercises the env-var wiring
and provisioning/population calls with a fake provision_solc (no network,
no real solc binaries) so these run offline like the rest of the suite;
the real end-to-end behavior (an actual provisioned solc, an actual
`forge build --offline` picking it up from ~/.svm) is covered by the
accompanying report's live validation, not here.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

import scripts.mgpr.run_full_study_batch as batch
from a4v.graph import BuildFailed


@pytest.fixture(autouse=True)
def _clean_env():
    for key in ("BENCHMARK_SOLC_PATH", "BENCHMARK_FORGE_OFFLINE_AUTODETECT", "BENCHMARK_STRICT_OFFLINE"):
        os.environ.pop(key, None)
    yield
    for key in ("BENCHMARK_SOLC_PATH", "BENCHMARK_FORGE_OFFLINE_AUTODETECT", "BENCHMARK_STRICT_OFFLINE"):
        os.environ.pop(key, None)


class _FakeEntry:
    def __init__(self, version):
        self.version = version
        self.path = f"/fake/toolchains/solc/{version}/solc"


def _fake_provision_solc(version, toolchain_dir, checksums):
    return _FakeEntry(version)


def _fake_official_checksums():
    return {}


def test_single_version_sets_benchmark_solc_path(tmp_path, monkeypatch):
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.20"\n')
    monkeypatch.setattr(batch, "provision_solc", _fake_provision_solc)
    monkeypatch.setattr(batch, "_official_checksums", _fake_official_checksums)
    detail = batch._select_compiler(tmp_path, tmp_path / "toolchains")
    assert os.environ["BENCHMARK_SOLC_PATH"] == "/fake/toolchains/solc/0.8.20/solc"
    assert "BENCHMARK_FORGE_OFFLINE_AUTODETECT" not in os.environ
    assert "profile.default" in detail


def test_multi_version_sets_offline_autodetect_and_populates_svm(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "A.sol").write_text("pragma solidity 0.8.20;\ncontract A {}\n")
    (tmp_path / "src" / "B.sol").write_text("pragma solidity 0.7.6;\ncontract B {}\n")
    monkeypatch.setattr(batch, "provision_solc", _fake_provision_solc)
    monkeypatch.setattr(batch, "_official_checksums", _fake_official_checksums)
    populated = {}
    monkeypatch.setattr(batch, "populate_svm_cache",
                         lambda versions, toolchain_dir, container_home: populated.update(versions=list(versions)))
    batch._select_compiler(tmp_path, tmp_path / "toolchains")
    assert os.environ["BENCHMARK_FORGE_OFFLINE_AUTODETECT"] == "1"
    assert "BENCHMARK_SOLC_PATH" not in os.environ
    assert populated["versions"] == ["0.7.6", "0.8.20"]


def test_multi_version_does_not_populate_svm_for_single_result(tmp_path, monkeypatch):
    """populate_svm_cache is only meaningful (and only called) once there
    is genuinely more than one required version -- calling it for a
    single-version resolution would be harmless but wasteful, and this
    guards against silently changing that."""
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.20"\n')
    monkeypatch.setattr(batch, "provision_solc", _fake_provision_solc)
    monkeypatch.setattr(batch, "_official_checksums", _fake_official_checksums)
    called = []
    monkeypatch.setattr(batch, "populate_svm_cache", lambda *a, **k: called.append(True))
    batch._select_compiler(tmp_path, tmp_path / "toolchains")
    assert called == []


def test_unresolved_raises_under_strict_offline(tmp_path, monkeypatch):
    # BENCHMARK_STRICT_OFFLINE is deliberately a module-level constant
    # captured once at import time (matching WORK_DIR/OUT_DIR/TOOLCHAIN_DIR
    # -- the whole run-scoping design sets env vars BEFORE the process
    # starts, not dynamically mid-run), so exercising this branch means
    # patching the module attribute directly, not os.environ at test time.
    monkeypatch.setattr(batch, "BENCHMARK_STRICT_OFFLINE", True)
    with pytest.raises(BuildFailed, match="NO_CONFIGURATION_FOUND"):
        batch._select_compiler(tmp_path, tmp_path / "toolchains")


def test_unresolved_does_not_raise_without_strict_offline(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "BENCHMARK_STRICT_OFFLINE", False)
    detail = batch._select_compiler(tmp_path, tmp_path / "toolchains")
    assert "BENCHMARK_SOLC_PATH" not in os.environ
    assert "BENCHMARK_FORGE_OFFLINE_AUTODETECT" not in os.environ
    assert "no foundry.toml/hardhat-config" in detail


def test_provisioning_failure_converts_to_build_failed_not_raw_exception(tmp_path, monkeypatch):
    """A real bug this guards against: the original single-version path
    called provision_solc directly with no try/except, so any provisioning
    error (network failure, a genuinely bad version) would propagate as an
    uncaught RuntimeError past run_full_study_batch.main()'s own `except
    BuildFailed` handler and crash the whole 27-audit batch instead of
    being recorded as one classified failure for that audit."""
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.20"\n')

    def _boom(version, toolchain_dir, checksums):
        raise RuntimeError("network unreachable")

    monkeypatch.setattr(batch, "provision_solc", _boom)
    monkeypatch.setattr(batch, "_official_checksums", _fake_official_checksums)
    with pytest.raises(BuildFailed, match="TOOLCHAIN_NOT_PROVISIONED"):
        batch._select_compiler(tmp_path, tmp_path / "toolchains")


def test_select_compiler_records_last_selection_for_single_version(tmp_path, monkeypatch):
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.20"\n')
    monkeypatch.setattr(batch, "provision_solc", _fake_provision_solc)
    monkeypatch.setattr(batch, "_official_checksums", _fake_official_checksums)
    batch.LAST_COMPILER_SELECTION.clear()
    batch._select_compiler(tmp_path, tmp_path / "toolchains", audit_id="test-audit")
    rec = batch.LAST_COMPILER_SELECTION["test-audit"]
    assert rec["status"] == "RESOLVED"
    assert rec["versions"] == ["0.8.20"]
    assert rec["mode"] == "single_use_pin"


def test_select_compiler_records_last_selection_for_multi_version(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "A.sol").write_text("pragma solidity 0.8.20;\ncontract A {}\n")
    (tmp_path / "src" / "B.sol").write_text("pragma solidity 0.7.6;\ncontract B {}\n")
    monkeypatch.setattr(batch, "provision_solc", _fake_provision_solc)
    monkeypatch.setattr(batch, "_official_checksums", _fake_official_checksums)
    monkeypatch.setattr(batch, "populate_svm_cache", lambda *a, **k: None)
    batch.LAST_COMPILER_SELECTION.clear()
    batch._select_compiler(tmp_path, tmp_path / "toolchains", audit_id="test-audit-multi")
    rec = batch.LAST_COMPILER_SELECTION["test-audit-multi"]
    assert rec["status"] == "RESOLVED"
    assert rec["versions"] == ["0.7.6", "0.8.20"]
    assert rec["mode"] == "multi_version_offline_autodetect"


def test_select_compiler_without_audit_id_does_not_record(tmp_path, monkeypatch):
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.8.20"\n')
    monkeypatch.setattr(batch, "provision_solc", _fake_provision_solc)
    monkeypatch.setattr(batch, "_official_checksums", _fake_official_checksums)
    batch.LAST_COMPILER_SELECTION.clear()
    batch._select_compiler(tmp_path, tmp_path / "toolchains")
    assert batch.LAST_COMPILER_SELECTION == {}


def test_audit_order_defaults_to_fixed_all_27(monkeypatch):
    monkeypatch.setattr(batch, "_AUDIT_ORDER_SEED", None)
    assert batch.audit_order() == batch.ALL_27


def test_audit_order_with_seed_is_a_permutation(monkeypatch):
    monkeypatch.setattr(batch, "_AUDIT_ORDER_SEED", "42")
    order = batch.audit_order()
    assert sorted(order) == sorted(batch.ALL_27)
    assert order != batch.ALL_27  # a real shuffle, not a no-op


def test_audit_order_is_deterministic_for_a_given_seed(monkeypatch):
    monkeypatch.setattr(batch, "_AUDIT_ORDER_SEED", "7")
    assert batch.audit_order() == batch.audit_order()


def test_audit_order_differs_across_seeds(monkeypatch):
    monkeypatch.setattr(batch, "_AUDIT_ORDER_SEED", "1")
    order1 = batch.audit_order()
    monkeypatch.setattr(batch, "_AUDIT_ORDER_SEED", "2")
    order2 = batch.audit_order()
    assert order1 != order2


def test_svm_population_failure_converts_to_build_failed(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "A.sol").write_text("pragma solidity 0.8.20;\ncontract A {}\n")
    (tmp_path / "src" / "B.sol").write_text("pragma solidity 0.7.6;\ncontract B {}\n")
    monkeypatch.setattr(batch, "provision_solc", _fake_provision_solc)
    monkeypatch.setattr(batch, "_official_checksums", _fake_official_checksums)

    def _boom(versions, toolchain_dir, container_home):
        raise RuntimeError("solc 0.7.6 not provisioned")

    monkeypatch.setattr(batch, "populate_svm_cache", _boom)
    with pytest.raises(BuildFailed, match="TOOLCHAIN_NOT_PROVISIONED"):
        batch._select_compiler(tmp_path, tmp_path / "toolchains")
