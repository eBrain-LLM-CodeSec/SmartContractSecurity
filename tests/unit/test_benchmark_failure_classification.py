"""Tests for run_full_study_batch.classify_build_failure -- the structured
failure taxonomy replacing a single generic COMPILE_FAILED bucket."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.mgpr.run_full_study_batch import classify_build_failure


def test_toolchain_not_provisioned():
    reason = "TOOLCHAIN_NOT_PROVISIONED: BENCHMARK_SOLC_PATH=/x/solc does not exist"
    assert classify_build_failure(reason) == "TOOLCHAIN_NOT_PROVISIONED"


def test_ambiguous_compiler_configuration():
    reason = "AMBIGUOUS_COMPILER_CONFIGURATION for 2024-01-example: conflicting versions"
    assert classify_build_failure(reason) == "AMBIGUOUS_COMPILER_CONFIGURATION"


def test_no_configuration_found():
    reason = "NO_CONFIGURATION_FOUND: no foundry.toml/hardhat-config compiler version"
    assert classify_build_failure(reason) == "NO_CONFIGURATION_FOUND"


def test_dependency_install_failed():
    assert classify_build_failure("npm install (hybrid npm+forge deps) failed: ...") == "DEPENDENCY_INSTALL_FAILED"
    assert classify_build_failure("forge install failed: fatal error") == "DEPENDENCY_INSTALL_FAILED"


def test_infrastructure_failure():
    """Item 20's counterpart: environment/infrastructure failures must not
    be classified the same as an audit's own source problem."""
    assert classify_build_failure("stderr: Error: Read-only file system (os error 30)") == "INFRASTRUCTURE_FAILURE"
    assert classify_build_failure("Exhausted repair budget (6 attempts) for /x") == "INFRASTRUCTURE_FAILURE"


def test_slither_unsupported_language_feature_not_classified_as_infrastructure():
    """Item 20: a genuine Slither limitation (e.g. a language construct it
    cannot IR-generate) must be distinguished from an environment failure
    -- these have entirely different remedies (neither is 'provision a
    compiler' or 'fix the container')."""
    reason = "Impossible to generate IR for TierCalculationLib.getTierOdds: 'NoneType' object has no attribute 'parameters'"
    assert classify_build_failure(reason) == "SLITHER_UNSUPPORTED_LANGUAGE_FEATURE"


def test_unrecognized_reason_falls_back_to_source_compile_failed():
    assert classify_build_failure("some genuinely novel solc syntax error") == "SOURCE_COMPILE_FAILED"


def test_classification_checks_toolchain_markers_before_generic_ones():
    """A TOOLCHAIN_NOT_PROVISIONED message that also happens to mention
    'forge install' in its surrounding context must still classify as the
    more specific toolchain failure, not the generic dependency-install
    bucket -- classifier order matters and is itself tested here."""
    reason = "forge install succeeded, but then TOOLCHAIN_NOT_PROVISIONED: BENCHMARK_SOLC_PATH missing"
    assert classify_build_failure(reason) == "TOOLCHAIN_NOT_PROVISIONED"
