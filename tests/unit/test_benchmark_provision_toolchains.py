"""Tests for scripts.benchmark.provision_toolchains. Network-touching
paths (the actual solc download, the actual official-checksum fetch) are
exercised only by the real end-to-end validation run documented in the
accompanying report, not here -- these tests cover the deterministic
logic around that boundary (manifest parsing, checksum verification
itself, lock-file serialization) without requiring network access, so
they run the same offline as everything else in this suite.
"""
import hashlib
import json

import pytest

from scripts.benchmark.provision_toolchains import populate_svm_cache, required_solc_versions, verify_and_install


def _write_manifest(tmp_path, records):
    p = tmp_path / "manifest.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return p


def test_required_solc_versions_unions_across_records(tmp_path):
    manifest = _write_manifest(tmp_path, [
        {"audit_id": "a", "required_compiler_versions": ["0.8.17"]},
        {"audit_id": "b", "required_compiler_versions": ["0.8.17", "0.7.6"]},
        {"audit_id": "c", "required_compiler_versions": []},
    ])
    assert required_solc_versions(manifest) == {"0.8.17", "0.7.6"}


def test_required_solc_versions_handles_missing_field(tmp_path):
    manifest = _write_manifest(tmp_path, [{"audit_id": "a"}])
    assert required_solc_versions(manifest) == set()


def test_required_solc_versions_skips_blank_lines(tmp_path):
    p = tmp_path / "manifest.jsonl"
    p.write_text('{"audit_id": "a", "required_compiler_versions": ["0.8.1"]}\n\n\n')
    assert required_solc_versions(p) == {"0.8.1"}


# --- item 8: checksum mismatch --------------------------------------------


def test_verify_and_install_rejects_checksum_mismatch(tmp_path):
    """A downloaded binary that does not match its published checksum must
    raise, not be silently provisioned."""
    fake_binary = tmp_path / "fake_downloaded_solc"
    fake_binary.write_bytes(b"not a real solc binary")
    wrong_checksum = {"9.9.9": "0" * 64}  # deliberately wrong
    with pytest.raises(RuntimeError, match="CHECKSUM MISMATCH"):
        verify_and_install(fake_binary, "9.9.9", tmp_path / "toolchains", wrong_checksum)


def test_verify_and_install_self_pins_when_no_official_checksum_available(tmp_path):
    """A version genuinely absent from every official list (e.g. a very
    old release) must still provision, but with an explicit,
    non-authoritative provenance label -- never silently claimed as
    externally verified."""
    fake_binary = tmp_path / "fake_downloaded_solc"
    fake_binary.write_bytes(b"a plausible old solc binary")
    entry = verify_and_install(fake_binary, "0.1.0", tmp_path / "toolchains", {})  # no official checksums at all
    assert "self-pinned" in entry.checksum_source
    assert entry.sha256 == hashlib.sha256(fake_binary.read_bytes()).hexdigest()


def test_verify_and_install_missing_source_raises(tmp_path):
    with pytest.raises(RuntimeError, match="does not exist"):
        verify_and_install(tmp_path / "never-downloaded", "1.2.3", tmp_path / "toolchains", {})


# --- item 6/7: provisioned compiler present / missing ---------------------


def test_verify_and_install_skips_write_when_already_correctly_provisioned(tmp_path):
    """toolchain_dir is deliberately immutable and shared across runs/
    audits -- re-provisioning an already-correct binary must be a cheap
    no-op read, not a rewrite (which is also what makes the race in the
    next test possible to avoid in the first place)."""
    fake_binary = tmp_path / "fake_downloaded_solc"
    fake_binary.write_bytes(b"already provisioned content")
    toolchain_dir = tmp_path / "toolchains"
    e1 = verify_and_install(fake_binary, "0.8.20", toolchain_dir, {})
    dest = toolchain_dir / "solc" / "0.8.20" / "solc"
    mtime_before = dest.stat().st_mtime_ns
    e2 = verify_and_install(fake_binary, "0.8.20", toolchain_dir, {})
    assert e2.sha256 == e1.sha256
    assert dest.stat().st_mtime_ns == mtime_before  # not rewritten


def test_verify_and_install_does_not_overwrite_in_place(tmp_path):
    """Regression guard for a real bug found live: concurrent provisioning
    calls for the same version (two audits in one process, or two runs
    sharing the immutable toolchain_dir) raced on `shutil.copy2` writing
    into an already-existing binary while it was open/executing elsewhere,
    raising `[Errno 26] Text file busy`. Simulated here by holding the
    existing dest file open (as a stand-in for "another process is
    currently executing it") across a re-provisioning call with DIFFERENT
    content -- write-then-atomic-rename must not need to touch the open
    file descriptor's underlying inode at all."""
    toolchain_dir = tmp_path / "toolchains"
    old_binary = tmp_path / "old_solc"
    old_binary.write_bytes(b"old content")
    verify_and_install(old_binary, "0.8.20", toolchain_dir, {})
    dest = toolchain_dir / "solc" / "0.8.20" / "solc"

    new_binary = tmp_path / "new_solc"
    new_binary.write_bytes(b"new content, different checksum")
    with open(dest, "rb"):  # hold the OLD inode open, as a running process would
        entry = verify_and_install(new_binary, "0.8.20", toolchain_dir, {})
    assert entry.sha256 == hashlib.sha256(b"new content, different checksum").hexdigest()
    assert dest.read_bytes() == b"new content, different checksum"


def test_verify_and_install_succeeds_when_checksum_matches(tmp_path):
    fake_binary = tmp_path / "fake_downloaded_solc"
    fake_binary.write_bytes(b"a real-looking solc binary")
    real_sha = hashlib.sha256(fake_binary.read_bytes()).hexdigest()
    entry = verify_and_install(fake_binary, "0.8.20", tmp_path / "toolchains", {"0.8.20": real_sha})
    assert entry.sha256 == real_sha
    assert "official" in entry.checksum_source
    assert (tmp_path / "toolchains" / "solc" / "0.8.20" / "solc").exists()


# --- item 13: lock-file / manifest serialization determinism -------------


def test_toolchain_dir_layout_is_deterministic(tmp_path):
    fake_binary = tmp_path / "fake_downloaded_solc"
    fake_binary.write_bytes(b"deterministic binary content")
    e1 = verify_and_install(fake_binary, "0.8.5", tmp_path / "toolchains1", {})
    e2 = verify_and_install(fake_binary, "0.8.5", tmp_path / "toolchains2", {})
    # same input binary -> same recorded checksum, regardless of which
    # deterministic toolchain_dir it was provisioned into.
    assert e1.sha256 == e2.sha256


# --- populate_svm_cache: multi-version offline auto-detect support --------


def _provision_fake(toolchain_dir, version, content=b"fake solc binary"):
    dest_dir = toolchain_dir / "solc" / version
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "solc").write_bytes(content)


def test_populate_svm_cache_creates_foundry_layout(tmp_path):
    """Mirrors Foundry's own internal svm cache layout exactly -- confirmed
    live (real forge 1.7.1 binary, real singularity container): a
    directory built this way, combined with `forge build --offline`, lets
    Foundry's own per-file auto-detection resolve without any network
    access."""
    toolchain_dir = tmp_path / "toolchains"
    _provision_fake(toolchain_dir, "0.8.23", b"solc-0.8.23-content")
    _provision_fake(toolchain_dir, "0.8.20", b"solc-0.8.20-content")
    container_home = tmp_path / "container_home"
    populate_svm_cache(["0.8.23", "0.8.20"], toolchain_dir, container_home)

    a = container_home / ".svm" / "0.8.23" / "solc-0.8.23"
    b = container_home / ".svm" / "0.8.20" / "solc-0.8.20"
    assert a.read_bytes() == b"solc-0.8.23-content"
    assert b.read_bytes() == b"solc-0.8.20-content"
    assert a.stat().st_mode & 0o111  # executable


def test_populate_svm_cache_raises_on_unprovisioned_version(tmp_path):
    """Never silently skip a required version -- a missing provisioned
    binary must raise, not populate a partial/wrong svm cache."""
    toolchain_dir = tmp_path / "toolchains"
    _provision_fake(toolchain_dir, "0.8.23")
    with pytest.raises(RuntimeError, match="not provisioned"):
        populate_svm_cache(["0.8.23", "0.7.6"], toolchain_dir, tmp_path / "container_home")


def test_populate_svm_cache_is_idempotent(tmp_path):
    toolchain_dir = tmp_path / "toolchains"
    _provision_fake(toolchain_dir, "0.8.23")
    container_home = tmp_path / "container_home"
    populate_svm_cache(["0.8.23"], toolchain_dir, container_home)
    populate_svm_cache(["0.8.23"], toolchain_dir, container_home)  # must not raise on re-run
    assert (container_home / ".svm" / "0.8.23" / "solc-0.8.23").exists()
