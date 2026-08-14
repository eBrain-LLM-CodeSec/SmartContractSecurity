"""Unit tests for `arm_g_codex.run_arm_g_bundle`'s `compile_via_foundry`
propagation (RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md SS12-SS13, Goal 2).

No real Codex binary/API key needed: `write_g_config` (which serializes
`GRAPH_COMPILE_VIA_FOUNDRY` into the MCP server's env block) runs BEFORE
`codex_login`'s `subprocess.run([codex_bin, ...])` call, so pointing
`codex_bin` at a nonexistent path makes `codex_login` raise
`FileNotFoundError` right after the config file is already written --
letting this test inspect the real written config without ever invoking
codex. Same "mock/stub the expensive edge, verify the real
deterministic part" discipline as every other test in this package.
Run with:
    .venv/bin/python3 -m rtf.l8_llm_judgment_layer.bundle_agent_experiment.test_arm_g_codex_foundry_wiring
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import run_arm_g_bundle

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _run_and_read_config(tmp: Path, *, compile_via_foundry: bool | None) -> str:
    repo = tmp / "repo"
    repo.mkdir()
    (repo / "Entry.sol").write_text("contract Entry {}\n", encoding="utf-8")
    scratch = tmp / "scratch"
    scratch.mkdir()

    kwargs = dict(
        codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
        mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", model="unused",
        case_id="foundry-wiring-test", entry_file=repo / "Entry.sol", repo_root=repo,
        candidate_location="", solc_path_dir="/nonexistent/solc_bin", solc_remaps=None,
        prompt="unused", scratch_root=scratch,
    )
    if compile_via_foundry is not None:
        kwargs["compile_via_foundry"] = compile_via_foundry

    try:
        run_arm_g_bundle(**kwargs)
    except Exception:  # noqa: BLE001 -- codex_bin is deliberately nonexistent
        pass

    config_path = scratch / "foundry-wiring-test_ghome" / ".codex" / "config.toml"
    return config_path.read_text(encoding="utf-8")


def test_compile_via_foundry_true_is_written_into_the_mcp_env_block():
    with tempfile.TemporaryDirectory() as tmp:
        config = _run_and_read_config(Path(tmp), compile_via_foundry=True)
        check("config.toml: GRAPH_COMPILE_VIA_FOUNDRY = \"1\" when compile_via_foundry=True",
              'GRAPH_COMPILE_VIA_FOUNDRY = "1"' in config, config)


def test_compile_via_foundry_false_is_written_into_the_mcp_env_block():
    with tempfile.TemporaryDirectory() as tmp:
        config = _run_and_read_config(Path(tmp), compile_via_foundry=False)
        check("config.toml: GRAPH_COMPILE_VIA_FOUNDRY absent when compile_via_foundry=False",
              "GRAPH_COMPILE_VIA_FOUNDRY" not in config, config)


def test_compile_via_foundry_omitted_defaults_to_unchanged_prior_behavior():
    with tempfile.TemporaryDirectory() as tmp:
        config = _run_and_read_config(Path(tmp), compile_via_foundry=None)
        check("config.toml: GRAPH_COMPILE_VIA_FOUNDRY absent when the param is omitted (legacy behavior)",
              "GRAPH_COMPILE_VIA_FOUNDRY" not in config, config)


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
