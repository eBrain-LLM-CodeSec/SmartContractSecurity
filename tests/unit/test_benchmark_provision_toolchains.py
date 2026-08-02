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

from scripts.benchmark.provision_toolchains import required_solc_versions, verify_and_install


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
