"""Tests for scripts.benchmark.compiler_resolver -- deterministic,
multi-format compiler-version resolution. All fixture text is either
literal snippets from real audits' actual configuration files (fetched
during this work's own investigation) or minimal synthetic constructions
of the same shapes, never invented formats these audits don't actually
use.
"""
from pathlib import Path

from scripts.benchmark.compiler_resolver import (
    BuildSystem,
    CompilerResolutionStatus,
    detect_build_system,
    resolve_compiler,
)


def _write(path: Path, name: str, content: str) -> None:
    (path / name).write_text(content)


# --- item 1: each real compiler-configuration form ---------------------


def test_foundry_solc_key(tmp_path):
    """Real form: 2023-07-pooltogether's own foundry.toml."""
    _write(tmp_path, "foundry.toml", '[profile.default]\nsolc = "0.8.17"\n')
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert res.primary_version == "0.8.17"
    assert res.build_system is BuildSystem.FOUNDRY


def test_foundry_solc_version_key(tmp_path):
    """Real form: 2024-01-canto's own foundry.toml -- the key the OLD
    bin/forge regex never matched (confirmed live: `solc_version =` broke
    a pattern anchored on `solc[[:space:]]*=`)."""
    _write(tmp_path, "foundry.toml", '[profile.default]\nsolc_version = "0.8.17"\n')
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert res.primary_version == "0.8.17"


def test_hardhat_solidity_compilers_version(tmp_path):
    """Real form: 2025-02-thorwallet's hardhat.config.ts."""
    _write(tmp_path, "hardhat.config.ts", 'export default { solidity: { version: "0.8.22" } };\n')
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert res.primary_version == "0.8.22"
    assert res.build_system is BuildSystem.HARDHAT


def test_dockerfile_solc_select_directive(tmp_path):
    _write(tmp_path, "Dockerfile", "RUN solc-select install 0.8.19 && solc-select use 0.8.19\n")
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert res.primary_version == "0.8.19"


def test_pragma_fallback_when_no_config_declares_a_version(tmp_path):
    """Real situation: 7 of the 27 audits (e.g. 2025-04-forte) declare no
    solc version in any project file at all."""
    (tmp_path / "src").mkdir()
    _write(tmp_path / "src", "A.sol", "pragma solidity 0.8.28;\ncontract A {}\n")
    _write(tmp_path / "src", "B.sol", "pragma solidity 0.8.28;\ncontract B {}\n")
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert res.primary_version == "0.8.28"
    assert res.candidates[0].source == "pragma_fallback"


# --- item 2: multiple Foundry profiles ----------------------------------


def test_multiple_foundry_profiles_default_wins(tmp_path):
    _write(tmp_path, "foundry.toml", (
        '[profile.default]\nsolc = "0.8.20"\n\n'
        '[profile.ci]\nsolc = "0.8.19"\n'
    ))
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert res.primary_version == "0.8.20"  # only [profile.default] is authoritative


def test_foundry_profile_with_no_default_version_falls_through_to_pragma(tmp_path):
    """[profile.default] declares nothing; a non-default profile's pin
    does not apply unless FOUNDRY_PROFILE selects it, so this must NOT be
    silently borrowed -- falls through to pragma scanning instead."""
    _write(tmp_path, "foundry.toml", '[profile.default]\noptimizer = true\n\n[profile.ci]\nsolc = "0.8.19"\n')
    (tmp_path / "src").mkdir()
    _write(tmp_path / "src", "A.sol", "pragma solidity 0.8.9;\ncontract A {}\n")
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert res.primary_version == "0.8.9"
    assert res.candidates[0].source == "pragma_fallback"


# --- item 5: ambiguous configuration ------------------------------------


def test_ambiguous_when_default_profile_itself_conflicts(tmp_path):
    _write(tmp_path, "foundry.toml", '[profile.default]\nsolc = "0.8.20"\nsolc_version = "0.8.19"\n')
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.AMBIGUOUS_COMPILER_CONFIGURATION
    assert res.primary_version is None


def test_ambiguous_pragma_scan_with_no_dominant_version(tmp_path):
    (tmp_path / "src").mkdir()
    _write(tmp_path / "src", "A.sol", "pragma solidity 0.8.20;\ncontract A {}\n")
    _write(tmp_path / "src", "B.sol", "pragma solidity 0.7.6;\ncontract B {}\n")
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.AMBIGUOUS_COMPILER_CONFIGURATION
    assert set(res.versions) == {"0.7.6", "0.8.20"}


def test_hardhat_multi_compiler_is_resolved_not_ambiguous(tmp_path):
    """Real situation: 2024-01-curves declares two Solidity compiler
    versions (0.8.7 and 0.5.15) -- a legitimate, Hardhat-native
    multi-compiler project, not an authoring conflict."""
    _write(tmp_path, "hardhat.config.ts", (
        'export default { solidity: { compilers: ['
        '{ version: "0.8.7" }, { version: "0.5.15" }] } };\n'
    ))
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert set(res.versions) == {"0.5.15", "0.8.7"}


# --- item 4: missing configuration ---------------------------------------


def test_no_configuration_found_when_nothing_present(tmp_path):
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.NO_CONFIGURATION_FOUND
    assert res.versions == []
    assert res.build_system is BuildSystem.UNKNOWN


def test_vendored_pragmas_excluded_from_fallback_scan(tmp_path):
    """A vendored dependency tree's pragma statements must not leak into
    fallback resolution -- only the project's own .sol files count."""
    (tmp_path / "src").mkdir()
    (tmp_path / "lib" / "vendor").mkdir(parents=True)
    _write(tmp_path / "src", "A.sol", "pragma solidity 0.8.20;\ncontract A {}\n")
    _write(tmp_path / "lib" / "vendor", "Old.sol", "pragma solidity 0.4.24;\ncontract Old {}\n")
    res = resolve_compiler(tmp_path)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert res.primary_version == "0.8.20"


# --- item 17: build-system detection -------------------------------------


def test_detect_build_system_foundry(tmp_path):
    _write(tmp_path, "foundry.toml", "")
    assert detect_build_system(tmp_path) is BuildSystem.FOUNDRY


def test_detect_build_system_hardhat(tmp_path):
    _write(tmp_path, "hardhat.config.js", "")
    assert detect_build_system(tmp_path) is BuildSystem.HARDHAT


def test_detect_build_system_unknown(tmp_path):
    assert detect_build_system(tmp_path) is BuildSystem.UNKNOWN


# --- item 19: determinism -------------------------------------------------


def test_pragma_fallback_not_confused_by_vendor_dir_name_in_ancestor_path(tmp_path):
    """Regression guard for a real bug found live: the pragma-fallback
    vendor-exclusion filter checked EVERY component of a .sol file's full
    path, including the caller's own ancestor scratch directories -- a
    checkout under a path that happened to contain a literal "artifacts"
    segment (unrelated to the project's own Hardhat build-output dir of
    the same name) caused every .sol file in the entire project to be
    wrongly excluded, resolving to NO_CONFIGURATION_FOUND regardless of
    real, unambiguous source content. Exclusion must only look at path
    components INSIDE the project (relative to subproject_root)."""
    project_root = tmp_path / "artifacts" / "some_scratch_dir" / "the_actual_project"
    (project_root / "src").mkdir(parents=True)
    _write(project_root / "src", "A.sol", "pragma solidity 0.8.24;\ncontract A {}\n")
    res = resolve_compiler(project_root)
    assert res.status is CompilerResolutionStatus.RESOLVED
    assert res.primary_version == "0.8.24"


def test_resolution_is_deterministic_across_calls(tmp_path):
    _write(tmp_path, "foundry.toml", '[profile.default]\nsolc = "0.8.17"\n')
    r1 = resolve_compiler(tmp_path)
    r2 = resolve_compiler(tmp_path)
    assert r1.as_dict() == r2.as_dict()
