"""Unit tests for rtf.l5_predicates.compile_helper's multi-file compilation
support -- real synthetic Foundry-shaped fixtures, not mocked. Covers the
three real gaps found live while onboarding new EVMbench targets (2025-04-
forte, 2026-01-tempo-feeamm, 2024-01-canto): foundry.toml-only remappings,
a relative import escaping its own source directory, and a target that
genuinely needs --via-ir to compile. Run with:
    .venv/bin/python3 -m rtf.l5_predicates.test_compile_helper
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import shutil

from .compile_helper import (
    _collect_remappings, _foundry_toml_remapping_lines, compile_evmbench_target, compile_evmbench_target_via_foundry,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


IFACE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IThing {
    function thing() external view returns (uint256);
}
"""


def test_foundry_toml_remapping_lines_parses_real_toml():
    with tempfile.TemporaryDirectory() as tmp:
        toml_path = Path(tmp) / "foundry.toml"
        toml_path.write_text(
            '[profile.default]\n'
            'src = "src"\n'
            'remappings = [\n'
            '    "@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/",\n'
            '    "forge-std/=lib/forge-std/src/",\n'
            ']\n',
            encoding="utf-8",
        )
        lines = _foundry_toml_remapping_lines(toml_path)
        check("foundry.toml: both remapping lines extracted", len(lines) == 2, lines)
        check("foundry.toml: @openzeppelin prefix present", any(l.startswith("@openzeppelin/contracts/=") for l in lines), lines)


def test_foundry_toml_without_remappings_key_returns_empty():
    with tempfile.TemporaryDirectory() as tmp:
        toml_path = Path(tmp) / "foundry.toml"
        toml_path.write_text('[profile.default]\nsrc = "src"\n', encoding="utf-8")
        lines = _foundry_toml_remapping_lines(toml_path)
        check("foundry.toml: no remappings key -> empty list, not a crash", lines == [], lines)


def test_malformed_foundry_toml_does_not_crash():
    with tempfile.TemporaryDirectory() as tmp:
        toml_path = Path(tmp) / "foundry.toml"
        toml_path.write_text("this is not [ valid toml", encoding="utf-8")
        lines = _foundry_toml_remapping_lines(toml_path)
        check("foundry.toml: malformed TOML degrades to empty list, not a crash", lines == [], lines)


def test_collect_remappings_from_foundry_toml_only():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "foundry.toml").write_text(
            '[profile.default]\nremappings = ["@dep/=lib/dep-package/"]\n', encoding="utf-8",
        )
        remaps = _collect_remappings(root)
        check("collect: foundry-toml-only project yields the @dep remap", any(r.startswith("@dep/=") for r in remaps), remaps)


def test_collect_remappings_shallower_wins_across_both_source_types():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "foundry.toml").write_text(
            '[profile.default]\nremappings = ["@dep/=lib/top-level-choice/"]\n', encoding="utf-8",
        )
        nested = root / "lib" / "vendored"
        nested.mkdir(parents=True)
        (nested / "remappings.txt").write_text("@dep/=../nested-choice/\n", encoding="utf-8")
        remaps = _collect_remappings(root)
        dep_remap = next((r for r in remaps if r.startswith("@dep/=")), None)
        check("collect: shallower foundry.toml remap wins over a deeper remappings.txt for the same prefix", dep_remap is not None and "top-level-choice" in dep_remap, dep_remap)


def test_collect_remappings_still_handles_remappings_txt_only():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "remappings.txt").write_text("@only/=lib/only-dep/\n", encoding="utf-8")
        remaps = _collect_remappings(root)
        check("collect: remappings.txt-only project still works (regression)", any(r.startswith("@only/=") for r in remaps), remaps)


# --- compile_evmbench_target: real compile-time behavior -------------------

def test_allow_paths_widened_for_relative_import_escaping_src_dir():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src").mkdir()
        (root / "lib").mkdir()
        (root / "lib" / "Helper.sol").write_text(
            "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\n"
            "library Helper { function id(uint256 x) internal pure returns (uint256) { return x; } }\n",
            encoding="utf-8",
        )
        entry = root / "src" / "Main.sol"
        entry.write_text(
            "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\n"
            'import {Helper} from "../lib/Helper.sol";\n'
            "contract Main { function f(uint256 x) public pure returns (uint256) { return Helper.id(x); } }\n",
            encoding="utf-8",
        )
        slither = compile_evmbench_target(entry, root, "0.8.20")
        contracts = [c.name for c in slither.contracts_derived]
        check(
            "allow-paths: a relative import escaping its own directory into a sibling one compiles successfully",
            "Main" in contracts and "Helper" in contracts,
            contracts,
        )


def test_extra_solc_args_via_ir_fixes_stack_too_deep():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src").mkdir()
        entry = root / "src" / "Deep.sol"
        # 20 local uint256s used in a way the legacy codegen can't fit on
        # the stack without --via-ir -- a real, minimal repro of the same
        # class of failure found live on 2024-01-canto's GaugeController.sol.
        var_decls = "\n".join(f"        uint256 v{i} = a + {i};" for i in range(20))
        var_sum = " + ".join(f"v{i}" for i in range(20))
        entry.write_text(
            "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\n"
            "contract Deep {\n"
            "    function f(uint256 a) public pure returns (uint256) {\n"
            f"{var_decls}\n"
            f"        return {var_sum};\n"
            "    }\n"
            "}\n",
            encoding="utf-8",
        )
        try:
            compile_evmbench_target(entry, root, "0.8.20")
            check("via-ir: precondition -- fixture fails to compile WITHOUT --via-ir (else this test proves nothing)", False, "fixture compiled without --via-ir; not a real repro of the stack-too-deep case")
        except Exception:
            check("via-ir: precondition -- fixture fails to compile WITHOUT --via-ir (else this test proves nothing)", True)

        # --via-ir alone is insufficient -- solc's own error message says
        # so explicitly ("while enabling the optimizer"), confirmed live
        # on both this fixture and the real 2024-01-canto target.
        slither = compile_evmbench_target(entry, root, "0.8.20", extra_solc_args=["--via-ir", "--optimize"])
        contracts = [c.name for c in slither.contracts_derived]
        check("via-ir: the SAME fixture compiles successfully WITH --via-ir + --optimize passed through extra_solc_args", "Deep" in contracts, contracts)


# --- compile_evmbench_target_via_foundry: real EVMbench target, real container ---

_REAL_TEMPO_FEEAMM_CHECKOUT = Path("/scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm")


def test_compile_via_foundry_real_target_multi_file_visibility():
    """Real-target regression test, skips gracefully if the fixed checkout
    or the container isn't present in this environment (same convention
    `scope_discovery.py`'s own real-target tests already use) -- not a
    synthetic fixture, because reproducing a real, correctly-vendored
    Foundry project (lib/forge-std etc.) synthetically would be as much
    work as the real checkout already sitting on disk. Confirms the two
    concrete claims this whole function exists for: (1) it works with
    zero `forge`/Foundry install on the host (this environment's own
    `forge` binary is confirmed broken -- GLIBC_2.29 missing -- so a
    passing test here IS the proof), and (2) real project-wide
    compilation succeeds using ONLY the project's own `foundry.toml`
    settings, no manually-discovered flags.
    """
    if not _REAL_TEMPO_FEEAMM_CHECKOUT.is_dir():
        check("compile_via_foundry: real-target test skipped (fixture checkout not present in this environment)", True)
        return

    with tempfile.TemporaryDirectory() as tmp:
        project_copy = Path(tmp) / "tempo-feeamm"
        shutil.copytree(_REAL_TEMPO_FEEAMM_CHECKOUT, project_copy)
        try:
            slither = compile_evmbench_target_via_foundry(project_copy)
        except Exception as e:  # noqa: BLE001
            check("compile_via_foundry: real target compiles via the container (skip if container unavailable here)",
                  False, f"{type(e).__name__}: {e}")
            return
        contracts = [c.name for c in slither.contracts_derived if not c.is_interface]
        check("compile_via_foundry: real target's own contract present, no manual solc flags needed",
              "FeeAMM" in contracts, contracts)


def main() -> int:
    tests = [
        test_foundry_toml_remapping_lines_parses_real_toml,
        test_foundry_toml_without_remappings_key_returns_empty,
        test_malformed_foundry_toml_does_not_crash,
        test_collect_remappings_from_foundry_toml_only,
        test_collect_remappings_shallower_wins_across_both_source_types,
        test_collect_remappings_still_handles_remappings_txt_only,
        test_allow_paths_widened_for_relative_import_escaping_src_dir,
        test_extra_solc_args_via_ir_fixes_stack_too_deep,
        test_compile_via_foundry_real_target_multi_file_visibility,
    ]
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
