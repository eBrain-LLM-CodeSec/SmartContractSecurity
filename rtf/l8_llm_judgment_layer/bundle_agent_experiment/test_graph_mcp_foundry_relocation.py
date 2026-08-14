"""Real Foundry artifact-relocation and graph-view consistency test."""
from __future__ import annotations

import importlib
import os
import sys
import tempfile
from pathlib import Path

from rtf.l5_predicates.compile_helper import compile_evmbench_target_via_foundry
from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import (
    prepare_full_repo_investigation_dir,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    (PASSES if condition else FAILURES).append(name if condition else f"{name}: {detail}")


def _write_fixture(repo: Path) -> None:
    (repo / "src").mkdir()
    (repo / "lib").mkdir()
    (repo / "foundry.toml").write_text(
        '[profile.default]\nsrc = "src"\nout = "out"\nlibs = ["lib"]\nsolc = "0.8.20"\n',
        encoding="utf-8",
    )
    for name in ("Entry", "Sibling", "Helper"):
        (repo / "src" / f"{name}.sol").write_text(
            f"// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\n"
            f"contract {name} {{ uint256 public value; function bump() external {{ value += 1; }} }}\n",
            encoding="utf-8",
        )
    (repo / "lib" / "Vendor.sol").write_text(
        "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\ncontract Vendor {}\n",
        encoding="utf-8",
    )


def _import_server(copy: Path):
    env = {
        "GRAPH_ENTRY_FILE": str(copy / "src" / "Entry.sol"),
        "GRAPH_REPO_ROOT": str(copy),
        "GRAPH_INVESTIGATION_DIR": str(copy),
        "GRAPH_CANDIDATE_LOCATION": "Sibling.bump",
        "GRAPH_TRACE_LOG_PATH": str(copy / "trace.jsonl"),
        "GRAPH_COMPILE_VIA_FOUNDRY": "1",
    }
    os.environ.update(env)
    module_name = "rtf.l8_llm_judgment_layer.bundle_agent_experiment.graph_mcp_server"
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def test_copied_foundry_artifacts_resolve_sibling_without_legacy_compile() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        repo = root / "repo"
        repo.mkdir()
        _write_fixture(repo)
        compile_evmbench_target_via_foundry(repo)
        copy = prepare_full_repo_investigation_dir(repo, root / "investigation")
        server = _import_server(copy)

        original_build = server.ProgramGraph.build
        server.ProgramGraph.build = classmethod(
            lambda cls, *args, **kwargs: (_ for _ in ()).throw(
                AssertionError("legacy ProgramGraph.build was called in Foundry mode")
            )
        )
        try:
            graph = server._build_graph_for_investigation(
                copy, str(copy / "src" / "Entry.sol"), True, None, None,
            )
        finally:
            server.ProgramGraph.build = original_build

        sibling_nodes = [
            (node_id, data) for node_id, data in graph.graph.nodes(data=True)
            if data.get("contract") == "Sibling" and data.get("name") == "bump"
        ]
        check("relocation: copied out/build-info exists", any((copy / "out" / "build-info").glob("*.json")))
        check("consistent view: copied graph contains Sibling.bump", bool(sibling_nodes), sibling_nodes)
        check("artifact provenance: Sibling node points into copied directory",
              bool(sibling_nodes) and str(copy) in str(sibling_nodes[0][1].get("file")), sibling_nodes)


def test_non_foundry_helper_preserves_legacy_build_call() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp)
        server = _import_server(copy)
        calls = []
        sentinel = object()
        original_build = server.ProgramGraph.build

        def fake_build(cls, target, solc_remaps=None, extra_kwargs=None):
            calls.append((target, solc_remaps, extra_kwargs))
            return sentinel

        server.ProgramGraph.build = classmethod(fake_build)
        try:
            result = server._build_graph_for_investigation(
                copy, "Entry.sol", False, ["@dep/=lib/dep/"], {"cwd": "/tmp/neutral"},
            )
        finally:
            server.ProgramGraph.build = original_build
        check("legacy helper: returns ProgramGraph.build result", result is sentinel, result)
        check("legacy helper: forwards byte-identical build arguments",
              calls == [("Entry.sol", ["@dep/=lib/dep/"], {"cwd": "/tmp/neutral"})], calls)


def main() -> int:
    for test in [
        test_copied_foundry_artifacts_resolve_sibling_without_legacy_compile,
        test_non_foundry_helper_preserves_legacy_build_call,
    ]:
        try:
            test()
        except Exception as exc:  # noqa: BLE001
            FAILURES.append(f"{test.__name__}: CRASHED -- {type(exc).__name__}: {exc}")
    print(f"PASSED: {len(PASSES)}")
    for item in PASSES:
        print(f"  ok - {item}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for item in FAILURES:
            print(f"  FAIL - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
