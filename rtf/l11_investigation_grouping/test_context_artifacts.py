"""Unit tests for rtf.l11_investigation_grouping.context_artifacts.
Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_context_artifacts
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l11_investigation_grouping.context_artifacts import (
    generate_cluster_plan_md, generate_protocol_context_md, generate_requirement_context_md,
    write_context_artifacts,
)
from rtf.l11_investigation_grouping.grouping_engine import Cluster
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.l5_predicates.compile_helper import compile_source

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _prop(pid: str, **overrides) -> PropertyMetadata:
    base = dict(
        property_id=pid, requirement_id=f"req-{pid}", requirement_level="Q",
        requirement_semantic_intent="Test Requirement", property_text="Tested code MUST do the thing.",
        target_contract="Vault", target_function="withdraw", candidate_locations=("Vault.withdraw",),
        source_provenance=f"req_id=req-{pid}; spec_section=5.3",
    )
    base.update(overrides)
    return PropertyMetadata(**base)


# --- generate_requirement_context_md ----------------------------------------

_REQ_RECORD = {
    "req_id": "req-3-all-valid-inputs", "level": "Q", "title": "Process All Inputs",
    "normative_text": "Tested Code MUST validate inputs, and function correctly whether the input is as designed or malformed.",
    "section": {"secno": "5.3"},
}


def test_requirement_context_includes_normative_text_verbatim():
    md = generate_requirement_context_md(_REQ_RECORD)
    check("normative text present verbatim", _REQ_RECORD["normative_text"] in md, md)
    check("req_id present", "req-3-all-valid-inputs" in md, md)
    check("level present", "[Q]" in md, md)
    check("title present", "Process All Inputs" in md, md)
    check("spec section present", "5.3" in md, md)


def test_requirement_context_includes_explanatory_text_when_given():
    explanatory = "It is important to consider whether input requirements are too strict, as well as too lax."
    md = generate_requirement_context_md(_REQ_RECORD, explanatory_text=explanatory)
    check("explanatory text included when given", explanatory in md, md)


def test_requirement_context_omits_explanatory_section_when_absent():
    md = generate_requirement_context_md(_REQ_RECORD)
    check("no explanatory section header when not given", "## Explanatory text" not in md, md)


def test_requirement_context_includes_counterexample_obligation():
    md = generate_requirement_context_md(_REQ_RECORD)
    check("mentions counterexample search obligation", "counterexample_search" in md or "counterexample search" in md.lower(), md)


# --- generate_cluster_plan_md -------------------------------------------

def test_cluster_plan_includes_every_property():
    a = _prop("p1", requirement_id="req-a", source_provenance="req_id=req-a; spec_section=5.3")
    b = _prop("p2", requirement_id="req-b", target_function="deposit", candidate_locations=("Vault.deposit",),
              source_provenance="req_id=req-b; spec_section=5.2")
    cluster = Cluster(cluster_id="cluster_001", property_ids=("p1", "p2"),
                       grouping_reason=("same_contract",), shared_context={"files": ["Vault.sol"], "contracts": ["Vault"]},
                       estimated_context_size=4)
    md = generate_cluster_plan_md(cluster, {"p1": a, "p2": b}, "protocol_context.md", {})
    check("plan includes p1", "p1" in md, md)
    check("plan includes p2", "p2" in md, md)
    check("plan includes candidate locations", "Vault.withdraw" in md and "Vault.deposit" in md, md)
    check("plan includes EthTrust provenance for both", "req_id=req-a" in md and "req_id=req-b" in md, md)


def test_cluster_plan_references_protocol_context_path():
    a = _prop("p1")
    cluster = Cluster(cluster_id="cluster_002", property_ids=("p1",), grouping_reason=(),
                       shared_context={}, estimated_context_size=1)
    md = generate_cluster_plan_md(cluster, {"p1": a}, ".rtf/context/protocol_context.md", {})
    check("plan references the given protocol context path", ".rtf/context/protocol_context.md" in md, md)


def test_cluster_plan_includes_grouping_rationale():
    a = _prop("p1")
    b = _prop("p2")
    cluster = Cluster(cluster_id="cluster_003", property_ids=("p1", "p2"),
                       grouping_reason=("same_requirement", "same_contract"), shared_context={}, estimated_context_size=2)
    md = generate_cluster_plan_md(cluster, {"p1": a, "p2": b}, "protocol_context.md", {})
    check("grouping reasons named", "same_requirement" in md and "same_contract" in md, md)


def test_cluster_plan_never_leaks_an_expected_verdict():
    """The most important structural guarantee: everything BEFORE the
    'Required output schema' section (where PASS/FAIL are legitimately
    named as SCHEMA VALUES, not conclusions) must contain no verdict-like
    token at all."""
    a = _prop("p1", property_text="Tested Code MUST validate inputs correctly.")
    cluster = Cluster(cluster_id="cluster_004", property_ids=("p1",), grouping_reason=(),
                       shared_context={}, estimated_context_size=1)
    md = generate_cluster_plan_md(cluster, {"p1": a}, "protocol_context.md", {})
    before_schema = md.split("## Required output schema")[0]
    for forbidden in ("PASS", "FAIL", "CONFIRMED_VIOLATION", "CONFIRMED_SATISFACTION", "vulnerable", "VULNERABLE"):
        check(f"no leaked verdict token {forbidden!r} before the output-schema section",
              forbidden not in before_schema, before_schema)


def test_cluster_plan_includes_investigation_procedure_steps():
    a = _prop("p1")
    cluster = Cluster(cluster_id="cluster_005", property_ids=("p1",), grouping_reason=(),
                       shared_context={}, estimated_context_size=1)
    md = generate_cluster_plan_md(cluster, {"p1": a}, "protocol_context.md", {})
    check("procedure mentions counterexample construction", "counterexample" in md.lower(), md)
    check("procedure mentions independent verdict per property", "independent verdict" in md.lower(), md)


def test_cluster_plan_includes_requirement_context_reference_when_given():
    a = _prop("p1", requirement_id="req-3-all-valid-inputs")
    cluster = Cluster(cluster_id="cluster_006", property_ids=("p1",), grouping_reason=(),
                       shared_context={}, estimated_context_size=1)
    md = generate_cluster_plan_md(cluster, {"p1": a}, "protocol_context.md",
                                   {"req-3-all-valid-inputs": ".rtf/context/requirements/req-3-all-valid-inputs.md"})
    check("requirement context path referenced", ".rtf/context/requirements/req-3-all-valid-inputs.md" in md, md)


# --- generate_protocol_context_md (real compiled fixture) -----------------

_PROTOCOL_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IVault {
    function withdraw(uint256 amount) external;
}

abstract contract Ownable {
    address public owner;
    modifier onlyOwner() { _; }
}

contract Vault is Ownable, IVault {
    uint256 public totalShares;
    uint256 public constant MAX_SHARES = 1_000_000;

    function withdraw(uint256 amount) external {
        totalShares -= amount;
    }

    function setOwner(address newOwner) external onlyOwner {
        owner = newOwner;
    }

    function _internalHelper() internal {}
}
"""


def test_real_protocol_context_lists_contracts_and_inheritance():
    slither = compile_source(_PROTOCOL_SOURCE)
    md = generate_protocol_context_md("test-audit", slither, ["src/Vault.sol"])
    check("Vault contract listed", "**Vault**" in md, md)
    check("Vault's inheritance from Ownable listed", "Ownable" in md, md)
    check("interface IVault listed as interface", "IVault" in md and "interface" in md, md)


def test_real_protocol_context_lists_external_entry_points_not_internal():
    slither = compile_source(_PROTOCOL_SOURCE)
    md = generate_protocol_context_md("test-audit", slither, ["src/Vault.sol"])
    entry_points_section = md.split("## Externally callable entry points")[1].split("##")[0]
    check("withdraw (external) listed as entry point", "withdraw" in entry_points_section, entry_points_section)
    check("setOwner (external) listed as entry point", "setOwner" in entry_points_section, entry_points_section)
    check("_internalHelper (internal) NOT listed as entry point", "_internalHelper" not in entry_points_section, entry_points_section)


def test_real_protocol_context_lists_constants():
    slither = compile_source(_PROTOCOL_SOURCE)
    md = generate_protocol_context_md("test-audit", slither, ["src/Vault.sol"])
    check("MAX_SHARES constant listed", "MAX_SHARES" in md and "constant" in md, md)


def test_real_protocol_context_flags_privilege_suggestive_modifier():
    slither = compile_source(_PROTOCOL_SOURCE)
    md = generate_protocol_context_md("test-audit", slither, ["src/Vault.sol"])
    trust_section = md.split("## Trust boundaries")[1]
    check("setOwner flagged under onlyOwner modifier heuristic", "setOwner" in trust_section, trust_section)


def test_protocol_context_lists_scope_files():
    slither = compile_source(_PROTOCOL_SOURCE)
    md = generate_protocol_context_md("test-audit", slither, ["src/Vault.sol", "src/Other.sol"])
    check("scope files listed", "src/Vault.sol" in md and "src/Other.sol" in md, md)


def test_protocol_context_empty_scope_reports_not_available_not_silent():
    slither = compile_source(_PROTOCOL_SOURCE)
    md = generate_protocol_context_md("test-audit", slither, [])
    check("empty scope: explicit 'not available' note, not silently blank",
          "not available" in md.lower(), md)


# --- write_context_artifacts (real filesystem I/O) --------------------------

def test_write_context_artifacts_creates_expected_files():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        result = write_context_artifacts(
            root, "test-audit", "# protocol\n",
            {"req-x": "# requirement req-x\n"}, {"cluster_000": "# plan cluster_000\n"},
        )
        check("protocol_context.md written", (root / ".rtf" / "context" / "protocol_context.md").exists())
        check("requirement context written", (root / ".rtf" / "context" / "requirements" / "req-x.md").exists())
        check("cluster plan written", (root / ".rtf" / "plans" / "cluster_000.md").exists())
        check("returned relative paths are correct",
              result["protocol_context"] == str(Path(".rtf/context/protocol_context.md")), result)
        check("content matches what was passed in",
              (root / ".rtf" / "context" / "protocol_context.md").read_text() == "# protocol\n")


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
