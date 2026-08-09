"""Unit tests for rtf.standards.routing. Run with:
    python3 -m rtf.standards.test_routing
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState, OperationalStatus
from rtf.l5_predicates.compile_helper import compile_evmbench_target

from .discovery import discover_applicable_standards
from .generator import generate_requirements_for_standard, generated_requirement_id
from .registry import StandardsRegistry
from .routing import build_standards_routed_requirements, classify_requirement, render_generated_requirement_bundle
from .test_discovery import IERC4626_INTERFACE, _ERC20_METHOD_BODIES, _ERC4626_METHOD_BODIES

PASSES = []
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _full_vault_repo(tmp: str, contract_name: str = "MyVault") -> Path:
    repo = Path(tmp)
    (repo / "interfaces").mkdir(parents=True, exist_ok=True)
    (repo / "interfaces" / "IERC4626.sol").write_text(IERC4626_INTERFACE, encoding="utf-8")
    source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

contract {contract_name} is IERC4626 {{
{_ERC20_METHOD_BODIES}
{_ERC4626_METHOD_BODIES}
}}
"""
    (repo / f"{contract_name}.sol").write_text(source, encoding="utf-8")
    return repo


def test_routing_decision_is_agent_required_for_standard_clause_direct():
    reg = StandardsRegistry()
    record = reg.load("ERC-4626")
    clauses = reg.load_clauses("ERC-4626")
    reqs = generate_requirements_for_standard(record, clauses)
    from .routing import RoutingDecision
    check(
        "routing: every currently-generated requirement classifies as AGENT_REQUIRED",
        all(classify_requirement(r) == RoutingDecision.AGENT_REQUIRED for r in reqs),
    )


def test_build_standards_routed_requirements_end_to_end():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _full_vault_repo(tmp)
        slither = compile_evmbench_target(repo / "MyVault.sol", repo, "0.8.20")
        routed, report, bundles = build_standards_routed_requirements(repo, repo / "MyVault.sol", slither)

        fee_req_id = generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees")
        check("routing: the totalAssets fee-inclusion requirement is in the routed dict", fee_req_id in routed, list(routed)[:5])

        result = routed[fee_req_id]
        check("routing: it's APPLICABLE", result.applicability_state == ApplicabilityState.APPLICABLE, result)
        check("routing: operational_status is OK", result.operational_status == OperationalStatus.OK, result)
        check(
            "routing: conformance_state is None (pending agent investigation, not pre-judged)",
            result.conformance_state is None,
            result,
        )
        check("routing: it carries real evidence (not empty)", len(result.evidence) >= 1, result.evidence)
        check("routing: evidence location names the identified contract", result.evidence[0].location == "MyVault", result.evidence[0])

        check("routing: a bundle was rendered for this requirement", fee_req_id in bundles, list(bundles)[:5])
        bundle = bundles[fee_req_id]
        check("routing: bundle's 'self' text contains the real obligation text", "inclusive of any fees" in bundle["bundle"]["self"], bundle["bundle"]["self"])
        check(
            "routing: bundle's parent_section_context explains WHY the standard was applicable (real detector reason, not asserted)",
            "APPLICABLE" in bundle["bundle"]["parent_section_context"],
            bundle["bundle"]["parent_section_context"],
        )

        check(
            "routing: StandardsIntegrityReport.requirements_generated matches ERC-4626's 77 clauses (plus ERC-20's, since a vault is also a token)",
            report.requirements_generated > 77,
            report.requirements_generated,
        )
        check("routing: silently_missing is 0 (every generated requirement reached a terminal routing status)", report.silently_missing == 0, report.silently_missing_requirement_ids)
        check("routing: report.valid is True", report.valid, report.invalid_reason)


def test_not_applicable_standard_produces_no_evidence_and_no_bundle():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        source = "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\ncontract Unrelated { uint256 public x; }\n"
        (repo / "Unrelated.sol").write_text(source, encoding="utf-8")
        slither = compile_evmbench_target(repo / "Unrelated.sol", repo, "0.8.20")
        routed, report, bundles = build_standards_routed_requirements(repo, repo / "Unrelated.sol", slither)

        fee_req_id = generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees")
        check("routing: NOT_APPLICABLE standard's clause requirement is still present in routed (not silently dropped)", fee_req_id in routed)
        result = routed[fee_req_id]
        check("routing: it's NOT_APPLICABLE", result.applicability_state == ApplicabilityState.NOT_APPLICABLE, result)
        check("routing: no evidence attached for a NOT_APPLICABLE requirement", result.evidence == (), result.evidence)
        check("routing: no bundle rendered for a NOT_APPLICABLE requirement (nothing to send an agent)", fee_req_id not in bundles)
        check("routing: report still reports valid=True (every requirement DID reach a terminal state, just NOT_APPLICABLE)", report.valid, report.invalid_reason)
        check("routing: requirements_applicable is 0 for a wholly unrelated contract", report.requirements_applicable == 0, report.requirements_applicable)


def main() -> int:
    tests = [
        test_routing_decision_is_agent_required_for_standard_clause_direct,
        test_build_standards_routed_requirements_end_to_end,
        test_not_applicable_standard_produces_no_evidence_and_no_bundle,
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
