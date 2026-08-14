"""Real-compile proof that `build_context_for_evmbench_target`'s new
`compile_via_foundry` param closes the SAME sibling-scope-file visibility
gap for EthTrust/structural predicates that
RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md already closed for RTF v2's
semantic generator -- a sibling scope file the entry doesn't import is
invisible to `ctx.slither` (and therefore to every Slither-backed
predicate) under the old single-entry compile, and visible under
`compile_via_foundry=True`. Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_run_rtf_foundry
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l11_investigation_grouping.live_runner import build_property_pool
from rtf.l12_evaluation.pipeline_e2e import CORPUS_PATH
from rtf.l12_evaluation.run_rtf import build_context_for_evmbench_target, load_unconditioned_map, run_rtf

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


_FOUNDRY_TOML = """[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc = "0.8.20"
"""

_ENTRY_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Entry {
    uint256 public entryState;
    function bump() external { entryState += 1; }
}
"""

# Deliberately NOT imported by Entry.sol -- same shape as the real
# 2025-04-forte Ln.sol / 2024-08-phi Cred.sol gap
# RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md documents for semantic
# generation. Contains a real, easy-to-trigger req-2-block-data-misuse
# pattern (block.timestamp used as a stored value) -- the same fixture
# shape test_live_runner.py's own block-data-misuse tests already use.
_SIBLING_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Sibling {
    uint256 public lastSeen;
    function touch() public {
        lastSeen = block.timestamp;
    }
}
"""


def _write_fixture(repo: Path) -> Path:
    (repo / "src").mkdir()
    (repo / "foundry.toml").write_text(_FOUNDRY_TOML, encoding="utf-8")
    (repo / "src" / "Entry.sol").write_text(_ENTRY_SOURCE, encoding="utf-8")
    (repo / "src" / "Sibling.sol").write_text(_SIBLING_SOURCE, encoding="utf-8")
    return repo / "src" / "Entry.sol"


def test_old_path_never_sees_the_sibling_contract():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        entry = _write_fixture(repo)
        ctx, error = build_context_for_evmbench_target(entry, repo, "0.8.20")
        check("old path: compiled without error", ctx.slither is not None, error)
        names = {c.name for c in ctx.slither.contracts} if ctx.slither else set()
        check("old path: Entry visible", "Entry" in names, names)
        check("old path: Sibling NOT visible (the confirmed gap this fix closes)",
              "Sibling" not in names, names)


def test_foundry_mode_makes_the_sibling_contract_visible_to_structural_predicates():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        entry = _write_fixture(repo)
        try:
            ctx, error = build_context_for_evmbench_target(entry, repo, "0.8.20", compile_via_foundry=True)
        except Exception as e:  # noqa: BLE001
            check("foundry mode ctx build skipped/failed (container unavailable here?)",
                  False, f"{type(e).__name__}: {e}")
            return
        check("foundry mode: compiled without error", ctx.slither is not None, error)
        names = {c.name for c in ctx.slither.contracts} if ctx.slither else set()
        check("foundry mode: Entry visible", "Entry" in names, names)
        check("foundry mode: Sibling ALSO visible", "Sibling" in names, names)

        unconditioned_map = load_unconditioned_map(CORPUS_PATH)
        run, _raw = run_rtf(ctx, "test-audit-foundry", unconditioned_map)
        block_data_result = run.routed.get("req-2-block-data-misuse")
        check("req-2-block-data-misuse: requirement present in routed output",
              block_data_result is not None, list(run.routed.keys())[:5])
        evidence_locations = [e.location for e in (block_data_result.evidence if block_data_result else [])]
        check("req-2-block-data-misuse: real evidence found targeting Sibling.touch",
              any("Sibling" in loc for loc in evidence_locations), evidence_locations)

        properties = build_property_pool(run.routed, repo, slither=ctx.slither)
        sibling_props = [p for p in properties if p.target_contract == "Sibling"]
        check("build_property_pool: a real PropertyMetadata was derived targeting Sibling",
              len(sibling_props) > 0, [(p.target_contract, p.target_function) for p in properties])


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
