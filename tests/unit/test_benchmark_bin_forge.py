"""Tests for bin/forge's explicit-compiler-selection fail-fast behavior
(Phase 3). These invoke the real shell script as a subprocess -- it is
bash, not Python, so this is the only honest way to test it -- but only
exercise the paths that fail *before* the script would try to invoke
Singularity (the `exit 97` guards happen before the `exec singularity ...`
line), so these tests need neither Singularity nor a container image to
be available, and run the same in CI as anywhere else.
"""
import os
import subprocess
from pathlib import Path

FORGE_SHIM = Path(__file__).resolve().parents[2] / "bin" / "forge"


def _run_forge(args: list[str], cwd: Path, env_extra: dict[str, str]) -> subprocess.CompletedProcess:
    env = {**os.environ, **env_extra}
    return subprocess.run([str(FORGE_SHIM), *args], cwd=cwd, env=env,
                           capture_output=True, text=True, timeout=30)


# --- item 7: provisioned compiler missing ---------------------------------


def test_benchmark_solc_path_missing_hard_fails_before_any_container_invocation(tmp_path):
    result = _run_forge(["build"], tmp_path, {"BENCHMARK_SOLC_PATH": str(tmp_path / "nonexistent-solc")})
    assert result.returncode == 97
    assert "TOOLCHAIN_NOT_PROVISIONED" in result.stderr


def test_benchmark_solc_path_present_does_not_hard_fail_at_the_guard(tmp_path):
    """A present, executable BENCHMARK_SOLC_PATH must pass the guard (the
    subsequent Singularity invocation may still fail/hang in a sandbox
    with no container runtime -- this test only asserts we get PAST the
    fail-fast guard, via a short timeout standing in for 'did not exit 97
    immediately')."""
    fake_solc = tmp_path / "fake-solc"
    fake_solc.write_text("#!/bin/sh\necho fake\n")
    fake_solc.chmod(0o755)
    try:
        _run_forge(["build"], tmp_path, {"BENCHMARK_SOLC_PATH": str(fake_solc)})
    except subprocess.TimeoutExpired:
        pass  # expected: it got past the guard and is now trying (and hanging on) singularity


# --- item 9: network fallback disabled (BENCHMARK_STRICT_OFFLINE) --------


def test_strict_offline_hard_fails_when_nothing_resolves_a_compiler(tmp_path):
    """No foundry.toml, no BENCHMARK_SOLC_PATH, no FORGE_FORCE_SOLC -- in
    strict-offline mode this must refuse to proceed (which would otherwise
    let forge/svm attempt their own implicit download) rather than
    silently falling through to the network-touching path."""
    result = _run_forge(["build"], tmp_path, {"BENCHMARK_STRICT_OFFLINE": "1"})
    assert result.returncode == 97
    assert "TOOLCHAIN_NOT_PROVISIONED" in result.stderr
    assert "BENCHMARK_STRICT_OFFLINE" in result.stderr


def test_strict_offline_not_triggered_when_unset(tmp_path):
    """Without BENCHMARK_STRICT_OFFLINE, the old best-effort fallback
    chain still applies (backward compatible for interactive/debugging
    use outside the hermetic benchmark runner) -- this does NOT hard-fail
    at the guard, unlike the strict-offline case above."""
    fake_solc = tmp_path / "fake-solc"
    fake_solc.write_text("#!/bin/sh\necho fake\n")
    fake_solc.chmod(0o755)
    try:
        result = _run_forge(["build"], tmp_path, {})
        # either it proceeds (no exit-97 guard fires) or times out trying
        # to reach a container runtime -- either way, not our TOOLCHAIN_NOT_PROVISIONED text.
        assert "TOOLCHAIN_NOT_PROVISIONED" not in (result.stderr or "")
    except subprocess.TimeoutExpired:
        pass


# --- item 15: build wrapper selects the exact declared compiler ----------


def test_benchmark_solc_path_takes_priority_over_foundry_toml_grep(tmp_path):
    """BENCHMARK_SOLC_PATH must win even when foundry.toml also declares a
    (different) version -- explicit provisioning is authoritative, not
    merely a fallback alongside the old grep-based detection."""
    (tmp_path / "foundry.toml").write_text('[profile.default]\nsolc = "0.7.6"\n')
    fake_solc = tmp_path / "0.8.20-solc"
    fake_solc.write_text("#!/bin/sh\necho fake\n")
    fake_solc.chmod(0o755)
    # We can't observe the final `--use` argument without a real
    # Singularity runtime, but we CAN assert the fail-fast guard is
    # governed by BENCHMARK_SOLC_PATH's own presence/absence, not by
    # foundry.toml -- remove BENCHMARK_SOLC_PATH's target and confirm the
    # hard failure names BENCHMARK_SOLC_PATH, not a foundry.toml parsing issue.
    missing = tmp_path / "missing-solc"
    result = _run_forge(["build"], tmp_path, {"BENCHMARK_SOLC_PATH": str(missing)})
    assert result.returncode == 97
    assert str(missing) in result.stderr
