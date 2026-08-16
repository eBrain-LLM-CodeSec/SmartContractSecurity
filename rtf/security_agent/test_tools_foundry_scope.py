"""Real, live ($0, no LLM -- Singularity+forge only) end-to-end test
proving the multi-file/sibling-visibility fix
(RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md) carries through
rtf.security_agent.tools.SecurityAgentTools, not just the existing
Codex-facing graph_mcp_server.py path. Increment 1 shipped the
compile_via_foundry=True code path in SecurityAgentTools.build but never
exercised it end-to-end -- this closes that gap.

Run with:
    .venv/bin/python3 -m rtf.security_agent.test_tools_foundry_scope
Skips gracefully (prints a note, does not fail the suite) if Singularity/
the worker container aren't reachable in this environment -- same
convention rtf.l11_investigation_grouping.test_semantic_only_driver's own
scope-matrix test already uses.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from rtf.l5_predicates.compile_helper import compile_evmbench_target_via_foundry
from rtf.security_agent.tools import SecurityAgentTools

PASSES: list[str] = []
FAILURES: list[str] = []
SKIPPED: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


_SOLC_SELECT_ARTIFACTS = Path.home() / ".solc-select" / "artifacts"


def _ensure_solc_0_8_20_on_path() -> None:
    """Same PATH-prepend workaround as rtf.security_agent.test_tools --
    this host's default `solc` on PATH is a fixed 0.7.6 binary that
    cannot compile ^0.8.20 fixtures. compile_evmbench_target_via_foundry
    doesn't need this (it compiles inside the container, which has its
    own toolchain) -- only the plain SecurityAgentTools.build(entry_file=...)
    path in the first test below does."""
    artifact = _SOLC_SELECT_ARTIFACTS / "solc-0.8.20" / "solc-0.8.20"
    if not artifact.exists():
        return
    bin_dir = Path(tempfile.mkdtemp(prefix="security_agent_test_solc_"))
    link = bin_dir / "solc"
    link.symlink_to(artifact)
    os.environ["PATH"] = f"{bin_dir}:{os.environ.get('PATH', '')}"


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

# In scope, NOT imported by Entry.sol -- same shape as the real
# 2025-04-forte Ln.sol / 2024-08-phi Cred.sol gap this fix targets
# (confirmed against RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md's own
# account of those two live misses).
_SIBLING_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Sibling {
    uint256 public siblingState;
    function bump() external { siblingState += 1; }
}
"""


def _write_fixture(repo: Path) -> None:
    (repo / "foundry.toml").write_text(_FOUNDRY_TOML, encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "Entry.sol").write_text(_ENTRY_SOURCE, encoding="utf-8")
    (repo / "src" / "Sibling.sol").write_text(_SIBLING_SOURCE, encoding="utf-8")


def test_single_entry_compile_cannot_see_unimported_sibling():
    """Reproduces the ORIGINAL bug (pre-whole-project-compile): compiling
    only Entry.sol's own import graph, Sibling.sol (never imported) is
    invisible to the tool layer. Needs no Singularity/forge -- plain
    single-entry-file compile path."""
    _ensure_solc_0_8_20_on_path()
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_fixture(repo)
        tools = SecurityAgentTools.build(repo_root=repo, entry_file=repo / "src" / "Entry.sol")
        entry_result = tools.get_contract_source("Entry")
        sibling_result = tools.get_contract_source("Sibling")
        check("Entry visible under single-entry compile", entry_result.status == "OK", entry_result)
        check("Sibling INVISIBLE under single-entry compile (reproduces the original bug)",
              sibling_result.status == "NOT_FOUND", sibling_result)


def test_compile_via_foundry_makes_sibling_visible():
    """The actual fix, exercised through rtf.security_agent.tools for the
    FIRST time. A real `forge build` inside the pre-existing
    evmbench-worker.sif container, then
    SecurityAgentTools.build(..., compile_via_foundry=True) reading those
    artifacts. Skips gracefully (does not fail the suite) if Singularity/
    the container aren't reachable here."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_fixture(repo)
        try:
            compile_evmbench_target_via_foundry(repo)
        except Exception as e:  # noqa: BLE001 -- container/forge unavailable in this environment
            SKIPPED.append(f"test_compile_via_foundry_makes_sibling_visible: {type(e).__name__}: {e}")
            return

        tools = SecurityAgentTools.build(repo_root=repo, compile_via_foundry=True)
        entry_result = tools.get_contract_source("Entry")
        sibling_result = tools.get_contract_source("Sibling")
        check("Entry still visible under whole-project compile", entry_result.status == "OK", entry_result)
        check("Sibling NOW VISIBLE under whole-project compile (the actual fix)",
              sibling_result.status == "OK", sibling_result)
        check("Sibling source content correct", "contract Sibling" in (sibling_result.source or ""))

        # Bonus: prove STRUCTURAL graph queries (not just raw source text)
        # work on the sibling too.
        writes = tools.get_state_writes("Sibling", "bump")
        check("Sibling.bump's state write resolved via the graph", writes.status == "OK", writes)
        if writes.status == "OK":
            check("Sibling.bump writes siblingState", any(v.name == "siblingState" for v in writes.state_vars),
                  writes.state_vars)


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
    if SKIPPED:
        print(f"SKIPPED: {len(SKIPPED)}")
        for s in SKIPPED:
            print(f"  skip - {s}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
