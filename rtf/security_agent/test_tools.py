"""Unit tests for rtf.security_agent.tools, against a REAL Slither
compilation of the existing multi-contract fixture (tests/fixtures/
multi_contract/Vault.sol) -- not mocked, since the whole point of this
layer is thin wrapping over real graph queries. Run with:
    .venv/bin/python3 -m rtf.security_agent.test_tools
(run from the repo root that has .venv/ -- this worktree has no .venv of
its own; see SECURITY_AGENT_KERNEL_DESIGN.md's Increment 1 notes.)
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from rtf.security_agent.tools import SecurityAgentTools, describe_tools

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


_SOLC_SELECT_ARTIFACTS = Path.home() / ".solc-select" / "artifacts"


def _solc_bin_dir_for(version: str, scratch_root: Path) -> str:
    """Same pattern as rtf.l11_investigation_grouping.semantic_only_driver's
    own `_solc_bin_dir_for` (that module's docstring explains why this is
    duplicated per-caller rather than shared: each caller needs its own
    scratch-scoped symlink dir) -- a directory containing exactly one
    `solc` binary symlinked to a verified solc-select artifact, prepended
    to PATH so Slither/crytic-compile picks the fixture's own pragma
    version instead of whatever fixed system solc happens to be first on
    PATH (confirmed live: this host's PATH resolves plain `solc` to a
    fixed 0.7.6 binary, which cannot compile a ^0.8.20 fixture)."""
    artifact = _SOLC_SELECT_ARTIFACTS / f"solc-{version}" / f"solc-{version}"
    if not artifact.exists():
        raise RuntimeError(f"solc {version} is not installed via solc-select (expected {artifact})")
    real_version = subprocess.run([str(artifact), "--version"], capture_output=True, text=True, check=True).stdout
    if f"Version: {version}" not in real_version:
        raise RuntimeError(f"solc-select artifact at {artifact} does not report version {version}: {real_version.strip()!r}")
    bin_dir = scratch_root / f"solc_bin_{version.replace('.', '')}"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link = bin_dir / "solc"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(artifact)
    return str(bin_dir)


_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURES = _REPO_ROOT / "tests" / "fixtures"
_VAULT_DIR = _FIXTURES / "multi_contract"
_VAULT_SOL = _VAULT_DIR / "Vault.sol"

_TOOLS: SecurityAgentTools | None = None


def _tools() -> SecurityAgentTools:
    global _TOOLS
    if _TOOLS is None:
        import tempfile
        solc_dir = _solc_bin_dir_for("0.8.20", Path(tempfile.mkdtemp(prefix="security_agent_test_solc_")))
        os.environ["PATH"] = f"{solc_dir}:{os.environ.get('PATH', '')}"
        _TOOLS = SecurityAgentTools.build(repo_root=_VAULT_DIR, entry_file=_VAULT_SOL)
    return _TOOLS


# --- get_function_source / get_contract_source ---------------------------

def test_get_function_source_ok():
    result = _tools().get_function_source("Vault", "withdraw")
    check("status OK", result.status == "OK", result)
    check("source mentions getPrice", "getPrice" in (result.source or ""), result.source)
    check("file is Vault.sol", (result.file or "").endswith("Vault.sol"))
    check("lines present", len(result.lines) > 0)


def test_get_function_source_not_found():
    result = _tools().get_function_source("Vault", "doesNotExist")
    check("status NOT_FOUND", result.status == "NOT_FOUND", result)
    check("reason present", bool(result.reason))


def test_get_function_source_unknown_contract():
    result = _tools().get_function_source("NoSuchContract", "withdraw")
    check("status NOT_FOUND for unknown contract", result.status == "NOT_FOUND", result)


def test_get_contract_source_ok():
    result = _tools().get_contract_source("Vault")
    check("status OK", result.status == "OK", result)
    check("source mentions contract Vault", "contract Vault" in (result.source or ""))


def test_get_contract_source_not_found():
    result = _tools().get_contract_source("NoSuchContract")
    check("status NOT_FOUND", result.status == "NOT_FOUND", result)


# --- callers / callees / external calls -----------------------------------

def test_get_callers_of_internal_helper():
    result = _tools().get_callers("Vault", "_internalHelper")
    check("status OK", result.status == "OK", result)
    names = {f.name for f in result.functions}
    check("callHelper is a caller", "callHelper" in names, names)


def test_get_callees_of_call_helper():
    result = _tools().get_callees("Vault", "callHelper")
    check("status OK", result.status == "OK", result)
    names = {f.name for f in result.functions}
    check("_internalHelper is a callee", "_internalHelper" in names, names)


def test_get_external_calls_from_withdraw():
    result = _tools().get_external_calls("Vault", "withdraw")
    check("status OK", result.status == "OK", result)
    names = {c.name for c in result.external_calls}
    check("getPrice reachable as external call", any("getPrice" in n for n in names), names)


def test_get_external_calls_none_found():
    result = _tools().get_external_calls("Vault", "_internalHelper")
    check("status NOT_FOUND (pure internal function, no external calls)", result.status == "NOT_FOUND", result)


def test_get_related_functions_includes_caller_and_callee():
    result = _tools().get_related_functions("Vault", "callHelper")
    names = {f.name for f in result.functions}
    check("status OK", result.status == "OK", result)
    check("related includes _internalHelper (callee)", "_internalHelper" in names, names)


# --- state reads / writes / modifiers --------------------------------------

def test_get_state_writes_from_withdraw():
    result = _tools().get_state_writes("Vault", "withdraw")
    check("status OK", result.status == "OK", result)
    names = {v.name for v in result.state_vars}
    check("writes shares", "shares" in names, names)
    check("writes totalShares", "totalShares" in names, names)
    # regression check for the file-resolution bug fixed during Increment 1:
    # STATEVAR nodes have no direct `file` attr in a4v.graph, only
    # graph_navigation.node_file's indirect owning-contract lookup gives one.
    check("state var file resolved (not None)", all(v.file for v in result.state_vars), result.state_vars)
    check("state var file is Vault.sol", all((v.file or "").endswith("Vault.sol") for v in result.state_vars))


def test_get_state_reads_from_deposit():
    result = _tools().get_state_reads("Vault", "deposit")
    check("status OK", result.status == "OK", result)


def test_get_modifiers_on_set_oracle():
    result = _tools().get_modifiers("Vault", "setOracle")
    check("status OK", result.status == "OK", result)
    names = {m.name for m in result.modifiers}
    check("onlyOwner applied", "onlyOwner" in names, names)


def test_get_modifiers_none_on_withdraw():
    result = _tools().get_modifiers("Vault", "withdraw")
    check("status NOT_FOUND (withdraw has no modifier)", result.status == "NOT_FOUND", result)


# --- inheritance ------------------------------------------------------------

def test_get_inheritance_vault_extends_ownable():
    result = _tools().get_inheritance("Vault")
    check("status OK", result.status == "OK", result)
    check("Ownable is a base", "Ownable" in result.bases, result.bases)


def test_get_inheritance_unknown_contract():
    result = _tools().get_inheritance("NoSuchContract")
    check("status NOT_FOUND", result.status == "NOT_FOUND", result)


# --- filesystem: read_file / search_repository ------------------------------

def test_read_file_ok():
    result = _tools().read_file("Vault.sol")
    check("status OK", result.status == "OK", result)
    check("content mentions contract Vault", "contract Vault" in (result.content or ""))


def test_read_file_not_found():
    result = _tools().read_file("NoSuchFile.sol")
    check("status NOT_FOUND", result.status == "NOT_FOUND", result)


def test_read_file_blocks_path_traversal():
    result = _tools().read_file("../../../../../../etc/passwd")
    check("status ERROR (escapes repo_root)", result.status == "ERROR", result)
    check("did not leak /etc/passwd content", result.content is None)


def test_search_repository_finds_modifier():
    result = _tools().search_repository("onlyOwner")
    check("status OK", result.status == "OK", result)
    check("hit in Vault.sol", any(h.file.endswith("Vault.sol") for h in result.hits), result.hits)


def test_search_repository_no_match():
    result = _tools().search_repository("ThisPatternDoesNotExistAnywhere123")
    check("status NOT_FOUND", result.status == "NOT_FOUND", result)


def test_search_repository_invalid_regex():
    result = _tools().search_repository("(unclosed")
    check("status ERROR for invalid regex", result.status == "ERROR", result)


# --- generic dispatch (call/describe_tools) --------------------------------

def test_call_dispatches_by_name():
    result = _tools().call("get_function_source", {"contract": "Vault", "function": "withdraw"})
    check("call() returns a plain dict", isinstance(result, dict), type(result))
    check("call() status OK", result.get("status") == "OK", result)
    check("call() result matches direct method call",
          "getPrice" in (result.get("source") or ""), result)


def test_call_rejects_unknown_tool():
    result = _tools().call("build", {})
    check("call() rejects non-whitelisted method (safety boundary)", result["status"] == "ERROR", result)
    check("build is not reachable via call()", "unknown tool" in result["reason"], result)


def test_call_rejects_dunder_method():
    result = _tools().call("__init__", {})
    check("call() rejects dunder method", result["status"] == "ERROR", result)


def test_call_reports_invalid_arguments_without_crashing():
    result = _tools().call("get_function_source", {"contract": "Vault"})  # missing "function"
    check("call() reports missing arg as a tool error, not a crash", result["status"] == "ERROR", result)
    check("reason mentions the bad call", "get_function_source" in result["reason"], result)


def test_call_accepts_keyword_only_optional_arg():
    result = _tools().call("get_state_writes", {"contract": "Vault", "function": "withdraw",
                                                  "include_transitive": False})
    check("call() accepts a keyword-only optional arg", result["status"] == "OK", result)


def test_describe_tools_lists_every_whitelisted_tool_once():
    text = describe_tools()
    for name in SecurityAgentTools.TOOL_NAMES:
        check(f"describe_tools mentions {name}", text.count(name) >= 1, text)
    check("describe_tools never mentions build() (not a callable tool)", "- build(" not in text, text)


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
