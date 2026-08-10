"""Unit + real-regression tests for rtf.l12_evaluation.scope_discovery.
Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_scope_discovery
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l12_evaluation.scope_discovery import (
    discover_scope_files, discover_scope_files_from_scope_txt, discover_scope_files_heuristic,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _write(root: Path, rel: str, source: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


# --- scope.txt path (highest-priority signal) -------------------------------

def test_scope_txt_present_returns_its_contents_verbatim():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scope.txt").write_text("src/A.sol\nsrc/B.sol\n\n  src/C.sol  \n", encoding="utf-8")
        result = discover_scope_files_from_scope_txt(root)
        check("scope.txt: parsed lines, blank dropped, whitespace stripped",
              result == ["src/A.sol", "src/B.sol", "src/C.sol"], result)


def test_scope_txt_absent_returns_none_not_empty_list():
    with tempfile.TemporaryDirectory() as tmp:
        result = discover_scope_files_from_scope_txt(Path(tmp))
        check("no scope.txt: returns None (distinguishable from an empty scope.txt)", result is None)


def test_discover_scope_files_prefers_scope_txt_over_heuristic_scan():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scope.txt").write_text("src/OnlyThisOne.sol\n", encoding="utf-8")
        _write(root, "src/OnlyThisOne.sol", "contract OnlyThisOne {}")
        _write(root, "src/AlsoPresentButNotInScope.sol", "contract AlsoPresentButNotInScope {}")
        result = discover_scope_files(root)
        check("scope.txt wins: only the declared file, not the heuristic-discoverable second one",
              result == ["src/OnlyThisOne.sol"], result)


# --- heuristic fallback ------------------------------------------------------

def test_heuristic_finds_plain_contract_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/Vault.sol", "pragma solidity ^0.8.20;\ncontract Vault {\n  function f() public {}\n}\n")
        result = discover_scope_files_heuristic(root)
        check("heuristic: plain contract file found", result == ["src/Vault.sol"], result)


def test_heuristic_finds_abstract_contract_as_in_scope():
    """Directly justified by phi's own README: /src/abstract/Claimable.sol
    (an `abstract contract`) is explicitly listed in "Files in scope",
    not excluded -- an abstract contract carries real logic that gets
    inherited, not a pure interface."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/abstract/Claimable.sol", "abstract contract Claimable {\n  function claim() internal {}\n}\n")
        result = discover_scope_files_heuristic(root)
        check("heuristic: abstract contract counted as in-scope", result == ["src/abstract/Claimable.sol"], result)


def test_heuristic_excludes_pure_interface_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/interfaces/IVault.sol", "interface IVault {\n  function deposit() external;\n}\n")
        result = discover_scope_files_heuristic(root)
        check("heuristic: pure interface file excluded", result == [], result)


def test_heuristic_excludes_pure_library_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/lib/MathLib.sol", "library MathLib {\n  function add(uint a, uint b) internal pure returns (uint) { return a + b; }\n}\n")
        result = discover_scope_files_heuristic(root)
        check("heuristic: pure library file excluded", result == [], result)


def test_heuristic_excludes_conventional_non_source_directories():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/Vault.sol", "contract Vault {}")
        _write(root, "test/Vault.t.sol", "contract VaultTest {}")
        _write(root, "script/Deploy.s.sol", "contract Deploy {}")
        _write(root, "lib/openzeppelin/Ownable.sol", "contract Ownable {}")
        _write(root, "mocks/MockToken.sol", "contract MockToken {}")
        result = discover_scope_files_heuristic(root)
        check("heuristic: only the real src/ contract survives, test/script/lib/mocks excluded",
              result == ["src/Vault.sol"], result)


def test_heuristic_keeps_file_with_both_interface_and_contract():
    """A file that declares BOTH an interface and a real contract (a
    common single-file pattern) should still be kept -- the exclusion is
    about files with ONLY interface/library declarations."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/Token.sol", "interface IToken { function x() external; }\ncontract Token is IToken { function x() external {} }\n")
        result = discover_scope_files_heuristic(root)
        check("heuristic: mixed interface+contract file kept", result == ["src/Token.sol"], result)


def test_heuristic_returns_sorted_deterministic_order():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/Zebra.sol", "contract Zebra {}")
        _write(root, "src/Alpha.sol", "contract Alpha {}")
        result = discover_scope_files_heuristic(root)
        check("heuristic: sorted order", result == sorted(result), result)


# --- real-regression checks (skip gracefully if the checkout isn't present) -

_PHI_CHECKOUT = Path("/scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi")
_LIQUID_RON_CHECKOUT = Path("/scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron")
_CANTO_CHECKOUT = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto")


def test_real_phi_checkout_scope_txt_includes_both_cred_and_phifactory():
    """The concrete finding this module exists to fix: the 4-audit
    comparison's phi run only ever created ONE entry (Cred.sol) --
    PhiFactory.sol, 7 other README-declared in-scope files, were never
    scoped at all. This asserts the FIX actually surfaces both."""
    if not _PHI_CHECKOUT.exists():
        check("real-regression: phi SKIPPED (checkout not present on this machine)", True)
        return
    result = discover_scope_files(_PHI_CHECKOUT)
    check("real-regression: phi scope.txt used (not the heuristic fallback)",
          (_PHI_CHECKOUT / "scope.txt").exists())
    check("real-regression: phi scope includes src/Cred.sol",
          any("Cred.sol" in f for f in result), result)
    check("real-regression: phi scope includes src/PhiFactory.sol -- the file the prior run never scoped",
          any("PhiFactory.sol" in f for f in result), result)
    check("real-regression: phi scope has all 9 README-declared in-scope files, not just 1",
          len(result) == 9, result)


def test_real_liquid_ron_checkout_scope_has_more_than_the_one_entry_previously_run():
    if not _LIQUID_RON_CHECKOUT.exists():
        check("real-regression: liquid-ron SKIPPED (checkout not present on this machine)", True)
        return
    result = discover_scope_files(_LIQUID_RON_CHECKOUT)
    check("real-regression: liquid-ron scope has more than 1 file "
          "(the real paid run used only LiquidRon.sol -- 'LiquidRonOnly' in its artifact dir name)",
          len(result) > 1, result)
    check("real-regression: liquid-ron scope includes LiquidRon.sol itself",
          any("LiquidRon.sol" in f for f in result), result)


def test_real_canto_checkout_scope_matches_the_single_file_already_used():
    """Sanity check in the OTHER direction: canto's real scope.txt
    genuinely has only 1 file, so that prior run was NOT scope-incomplete
    -- confirms this mechanism doesn't just always claim "more files"."""
    if not _CANTO_CHECKOUT.exists():
        check("real-regression: canto SKIPPED (checkout not present on this machine)", True)
        return
    result = discover_scope_files(_CANTO_CHECKOUT)
    check("real-regression: canto scope is genuinely just LendingLedger.sol",
          result == ["src/LendingLedger.sol"], result)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
