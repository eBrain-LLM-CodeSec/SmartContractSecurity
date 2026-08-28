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

from rtf.security_agent.tools import SecurityAgentTools, build_tool_schemas, describe_tools

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


# --- read_evidence (graceful missing/unknown id handling) -------------------

def _tools_with_evidence_store() -> SecurityAgentTools:
    import tempfile
    from rtf.security_agent.evidence_store import EvidenceStore
    base = _tools()
    store_dir = Path(tempfile.mkdtemp(prefix="security_agent_test_evidence_"))
    return SecurityAgentTools(base.pg, base.repo_root, evidence_store=EvidenceStore(store_dir))


def test_read_evidence_with_no_id_lists_known_ids_instead_of_crashing():
    """Real bug found live (2026-08-26, native-tool-calling canto rerun):
    the model called read_evidence with NO arguments 3 times in one real
    cluster, despite evidence_id being schema-required -- this proxy
    doesn't hard-enforce required-argument completeness. Must degrade to
    a self-correcting ERROR (listing what IS available), never crash at
    argument-binding time with no guidance."""
    tools = _tools_with_evidence_store()
    tools.evidence_store.store("tool-1", "get_contract_source", {"status": "OK", "file": "Vault.sol"})
    result = tools.read_evidence()
    check("status is ERROR, not a crash", result.status == "ERROR", result)
    check("lists the known evidence id", "tool-1" in (result.reason or ""), result.reason)


def test_read_evidence_with_no_id_and_nothing_stored_yet():
    tools = _tools_with_evidence_store()
    result = tools.read_evidence()
    check("status is ERROR", result.status == "ERROR", result)
    check("says none yet rather than an empty/confusing list", "none yet" in (result.reason or ""), result.reason)


def test_read_evidence_with_unknown_id_also_lists_known_ids():
    tools = _tools()  # cached singleton, no evidence_store -- exercises the "no store configured" path is unaffected
    result = tools.read_evidence("definitely-not-a-real-id")
    check("status is ERROR (no evidence store configured for this singleton)", result.status == "ERROR", result)


def test_read_evidence_via_generic_call_dispatch_with_empty_args():
    """The exact real shape the model sent live: a native tool call with
    an empty args dict, dispatched through the generic call() path (not
    calling read_evidence directly) -- this is what SecurityAgentKernel's
    dispatch loop actually does."""
    tools = _tools_with_evidence_store()
    tools.evidence_store.store("tool-7", "search_repository", {"status": "OK", "hits": []})
    result = tools.call("read_evidence", {})
    check("no crash, a normal ERROR dict result", result.get("status") == "ERROR", result)
    check("lists the known evidence id via generic dispatch too", "tool-7" in (result.get("reason") or ""), result)


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


# --- build_tool_schemas() (native Responses-API tools=[...] entries) --------

def test_build_tool_schemas_covers_every_whitelisted_tool_exactly_once():
    schemas = build_tool_schemas()
    names = [s["name"] for s in schemas]
    check("one schema per whitelisted tool, no duplicates",
          set(names) == SecurityAgentTools.TOOL_NAMES and len(names) == len(set(names)), names)
    for schema in schemas:
        check(f"{schema['name']} declared as a strict function schema",
              schema["type"] == "function" and schema["strict"] is True, schema)
        check(f"{schema['name']} forbids additional properties",
              schema["parameters"]["additionalProperties"] is False, schema)


def test_build_tool_schemas_marks_required_positional_str_params_required():
    schemas = {s["name"]: s for s in build_tool_schemas()}
    params = schemas["get_callers"]["parameters"]
    check("contract is required", "contract" in params["required"], params)
    check("function is required", "function" in params["required"], params)
    check("both typed as string", params["properties"]["contract"] == {"type": "string"}
          and params["properties"]["function"] == {"type": "string"}, params)


def test_build_tool_schemas_requires_every_declared_param_including_defaulted_ones():
    """The two non-trivial cases in the whitelist: `get_state_writes`'s
    `include_transitive: bool = True` and `search_repository`'s
    `file_glob: str = "*.sol"` -- both keyword-only WITH a Python default,
    but BOTH must still appear in the wire schema's `required` list (real,
    live-blocking incompatibility found during the GPT-5.6 Sol controlled
    test, 2026-08-27: OpenAI/Azure's strict-mode validator rejects any
    schema that excludes a declared property from `required`, unlike
    OpenRouter's GLM-family proxy, which tolerates the omission). This is
    a wire-contract change only -- `SecurityAgentTools.call`'s own Python
    defaults are untouched; the model must now always pass an explicit
    value rather than being allowed to omit the key."""
    schemas = {s["name"]: s for s in build_tool_schemas()}

    gsw_params = schemas["get_state_writes"]["parameters"]
    check("include_transitive is declared AND required",
          "include_transitive" in gsw_params["properties"]
          and "include_transitive" in gsw_params["required"], gsw_params)
    check("include_transitive typed as boolean",
          gsw_params["properties"]["include_transitive"] == {"type": "boolean"}, gsw_params)
    check("contract/function still required for get_state_writes",
          {"contract", "function"} <= set(gsw_params["required"]), gsw_params)

    sr_params = schemas["search_repository"]["parameters"]
    check("file_glob is declared AND required",
          "file_glob" in sr_params["properties"] and "file_glob" in sr_params["required"], sr_params)
    check("file_glob typed as string",
          sr_params["properties"]["file_glob"] == {"type": "string"}, sr_params)
    check("pattern still required for search_repository",
          "pattern" in sr_params["required"], sr_params)


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
