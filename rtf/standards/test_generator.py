"""Unit tests for rtf.standards.generator. Run with:
    python3 -m rtf.standards.test_generator
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l5_predicates.compile_helper import compile_evmbench_target

from .discovery import discover_applicable_standards
from .generator import determine_clause_applicability, generate_requirements_for_standard, generated_requirement_id
from .models import ApplicabilityStatus, DerivationType, NormativeStrength
from .registry import StandardsRegistry
from .test_discovery import IERC4626_INTERFACE, _ERC20_METHOD_BODIES, _ERC4626_METHOD_BODIES

PASSES = []
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _registry() -> StandardsRegistry:
    return StandardsRegistry()


def _full_vault_repo(tmp: str, contract_name: str = "MyVault", extra_body: str = "") -> Path:
    repo = Path(tmp)
    (repo / "interfaces").mkdir(parents=True, exist_ok=True)
    (repo / "interfaces" / "IERC4626.sol").write_text(IERC4626_INTERFACE, encoding="utf-8")
    source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

contract {contract_name} is IERC4626 {{
{_ERC20_METHOD_BODIES}
{_ERC4626_METHOD_BODIES}
{extra_body}
}}
"""
    (repo / f"{contract_name}.sol").write_text(source, encoding="utf-8")
    return repo


# --- requirement generation -------------------------------------------

def test_generation_is_deterministic_byte_for_byte():
    reg = _registry()
    record = reg.load("ERC-4626")
    clauses = reg.load_clauses("ERC-4626")
    run1 = [r.to_dict() for r in generate_requirements_for_standard(record, clauses)]
    run2 = [r.to_dict() for r in generate_requirements_for_standard(record, clauses)]
    check("generator: two generation runs produce byte-identical output", run1 == run2, "outputs differ")


def test_requirement_ids_deterministic_and_stable():
    check(
        "generator: requirement_id is a pure function of (standard_id, clause_id)",
        generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees")
        == generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees"),
    )
    rid = generated_requirement_id("ERC-4626", "erc4626-totalassets-must-include-fees")
    check("generator: requirement_id embeds the standard and clause identity", "erc-4626" in rid and "totalassets" in rid, rid)


def test_provenance_and_parent_gp_correct():
    reg = _registry()
    record = reg.load("ERC-4626")
    clauses = reg.load_clauses("ERC-4626")
    reqs = generate_requirements_for_standard(record, clauses)
    fee_req = next(r for r in reqs if r.clause_id == "erc4626-totalassets-must-include-fees")
    check("generator: parent_requirement_id is req-R-follow-erc-standards", fee_req.parent_requirement_id == "req-R-follow-erc-standards", fee_req.parent_requirement_id)
    check("generator: source_id is ERC-4626", fee_req.source_id == "ERC-4626", fee_req.source_id)
    check("generator: source_family is ERC", fee_req.source_family == "ERC", fee_req.source_family)
    check("generator: derivation_type is STANDARD_CLAUSE_DIRECT", fee_req.derivation_type == DerivationType.STANDARD_CLAUSE_DIRECT)
    check("generator: source_url_or_local_spec is the canonical EIP-4626 URL", "eips.ethereum.org" in fee_req.source_url_or_local_spec, fee_req.source_url_or_local_spec)


def test_normative_strength_preserved_not_flattened():
    reg = _registry()
    record = reg.load("ERC-4626")
    clauses = reg.load_clauses("ERC-4626")
    reqs = generate_requirements_for_standard(record, clauses)
    by_clause = {r.clause_id: r for r in reqs}
    check(
        "generator: MUST clause preserved as MUST",
        by_clause["erc4626-totalassets-must-include-fees"].normative_strength == NormativeStrength.MUST,
    )
    check(
        "generator: SHOULD clause preserved as SHOULD (not upgraded to MUST)",
        by_clause["erc4626-totalassets-should-include-yield"].normative_strength == NormativeStrength.SHOULD,
    )
    check(
        "generator: MAY clause preserved as MAY (not upgraded)",
        by_clause["erc4626-nontransferable-may-revert-transfer"].normative_strength == NormativeStrength.MAY,
    )


def test_conditions_preserved():
    reg = _registry()
    record = reg.load("ERC-4626")
    clauses = reg.load_clauses("ERC-4626")
    reqs = generate_requirements_for_standard(record, clauses)
    conditional = next(r for r in reqs if r.clause_id == "erc4626-nontransferable-may-revert-transfer")
    check("generator: conditional clause's condition text is preserved on the generated requirement", len(conditional.conditions) == 1 and "non-transferrable" in conditional.conditions[0], conditional.conditions)


def test_requirement_count_matches_clause_count():
    reg = _registry()
    record = reg.load("ERC-4626")
    clauses = reg.load_clauses("ERC-4626")
    reqs = generate_requirements_for_standard(record, clauses)
    check("generator: one requirement generated per clause, none dropped/duplicated", len(reqs) == len(clauses), (len(reqs), len(clauses)))
    check("generator: all requirement_ids unique", len({r.requirement_id for r in reqs}) == len(reqs))


# --- clause applicability (§11) -----------------------------------------

def test_applicable_standard_and_implemented_function():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _full_vault_repo(tmp)
        slither = compile_evmbench_target(repo / "MyVault.sol", repo, "0.8.20")
        reg = _registry()
        detections = discover_applicable_standards(repo, repo / "MyVault.sol", slither, reg)
        detection = next(d for d in detections if d.standard_id == "ERC-4626")
        record = reg.load("ERC-4626")
        clauses = reg.load_clauses("ERC-4626")
        reqs = generate_requirements_for_standard(record, clauses)
        fee_req = next(r for r in reqs if r.clause_id == "erc4626-totalassets-must-include-fees")
        result = determine_clause_applicability(fee_req, detection, slither)
        check(
            "applicability: totalAssets clause is APPLICABLE when totalAssets() is implemented on the identified contract",
            result.status == ApplicabilityStatus.APPLICABLE,
            result,
        )
        check("applicability: reason is non-empty and explicit", bool(result.reason))


def test_applicable_standard_and_inherited_function():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "interfaces").mkdir(parents=True, exist_ok=True)
        (repo / "interfaces" / "IERC4626.sol").write_text(IERC4626_INTERFACE, encoding="utf-8")
        source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

abstract contract BaseVault is IERC4626 {{
{_ERC20_METHOD_BODIES}
{_ERC4626_METHOD_BODIES}
}}

contract ChildVault is BaseVault {{}}
"""
        (repo / "ChildVault.sol").write_text(source, encoding="utf-8")
        slither = compile_evmbench_target(repo / "ChildVault.sol", repo, "0.8.20")
        reg = _registry()
        detections = discover_applicable_standards(repo, repo / "ChildVault.sol", slither, reg)
        detection = next(d for d in detections if d.standard_id == "ERC-4626")
        record = reg.load("ERC-4626")
        clauses = reg.load_clauses("ERC-4626")
        reqs = generate_requirements_for_standard(record, clauses)
        fee_req = next(r for r in reqs if r.clause_id == "erc4626-totalassets-must-include-fees")
        result = determine_clause_applicability(fee_req, detection, slither)
        check(
            "applicability: totalAssets clause is APPLICABLE via inherited implementation (ChildVault -> BaseVault)",
            result.status == ApplicabilityStatus.APPLICABLE,
            result,
        )


def test_conditional_clause_status_is_unknown_not_silently_dropped():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _full_vault_repo(tmp)
        slither = compile_evmbench_target(repo / "MyVault.sol", repo, "0.8.20")
        reg = _registry()
        detections = discover_applicable_standards(repo, repo / "MyVault.sol", slither, reg)
        detection = next(d for d in detections if d.standard_id == "ERC-4626")
        record = reg.load("ERC-4626")
        clauses = reg.load_clauses("ERC-4626")
        reqs = generate_requirements_for_standard(record, clauses)
        conditional_req = next(r for r in reqs if r.clause_id == "erc4626-nontransferable-may-revert-transfer")
        result = determine_clause_applicability(conditional_req, detection, slither)
        check(
            "applicability: a clause with an unresolvable activation condition is UNKNOWN, not silently APPLICABLE or NOT_APPLICABLE",
            result.status == ApplicabilityStatus.UNKNOWN,
            result,
        )
        check("applicability: UNKNOWN reason explicitly names the condition", "non-transferrable" in result.reason, result.reason)


def test_unrelated_clause_not_applicable_when_standard_not_applicable():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        source = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract Unrelated { uint256 public x; }
"""
        (repo / "Unrelated.sol").write_text(source, encoding="utf-8")
        slither = compile_evmbench_target(repo / "Unrelated.sol", repo, "0.8.20")
        reg = _registry()
        detections = discover_applicable_standards(repo, repo / "Unrelated.sol", slither, reg)
        detection = next(d for d in detections if d.standard_id == "ERC-4626")
        record = reg.load("ERC-4626")
        clauses = reg.load_clauses("ERC-4626")
        reqs = generate_requirements_for_standard(record, clauses)
        fee_req = next(r for r in reqs if r.clause_id == "erc4626-totalassets-must-include-fees")
        result = determine_clause_applicability(fee_req, detection, slither)
        check(
            "applicability: every clause of a NOT_APPLICABLE standard is itself NOT_APPLICABLE, with an explicit reason",
            result.status == ApplicabilityStatus.NOT_APPLICABLE and bool(result.reason),
            result,
        )


def test_clause_not_applicable_when_optional_function_absent():
    # A vault that implements the required 16 methods but not the OPTIONAL
    # EIP-2612 permit feature -- the "may implement EIP-2612" clause itself
    # doesn't name a checkable function target (affected_interface is
    # contract-level), so this test instead uses a clause naming a specific
    # function absent from a deliberately incomplete (but still-detected-
    # applicable-via-other-signals) contract shape is out of scope for this
    # fixture set; covered structurally by discovery's fixture 5 (interface
    # referenced, nothing implemented => standard itself NOT_APPLICABLE,
    # already exercised above). This test instead confirms the "missing
    # named target" branch fires for a clause whose function name is
    # deliberately absent even though the standard IS applicable, by
    # checking against a requirement generated for a target name that
    # cannot exist on this contract.
    with tempfile.TemporaryDirectory() as tmp:
        repo = _full_vault_repo(tmp)
        slither = compile_evmbench_target(repo / "MyVault.sol", repo, "0.8.20")
        reg = _registry()
        detections = discover_applicable_standards(repo, repo / "MyVault.sol", slither, reg)
        detection = next(d for d in detections if d.standard_id == "ERC-4626")
        record = reg.load("ERC-4626")
        clauses = reg.load_clauses("ERC-4626")
        reqs = generate_requirements_for_standard(record, clauses)
        # every real ERC-4626 clause's target IS implemented in this fixture,
        # so directly construct one whose target is guaranteed absent via
        # dataclasses.replace to isolate the "missing named target" branch.
        import dataclasses
        fee_req = next(r for r in reqs if r.clause_id == "erc4626-totalassets-must-include-fees")
        fabricated = dataclasses.replace(fee_req, affected_interface=("thisFunctionDoesNotExistAnywhere",))
        result = determine_clause_applicability(fabricated, detection, slither)
        check(
            "applicability: a clause naming a function absent from the implementing contract is NOT_APPLICABLE with an explicit reason",
            result.status == ApplicabilityStatus.NOT_APPLICABLE and "thisFunctionDoesNotExistAnywhere" in result.reason,
            result,
        )


def main() -> int:
    tests = [
        test_generation_is_deterministic_byte_for_byte,
        test_requirement_ids_deterministic_and_stable,
        test_provenance_and_parent_gp_correct,
        test_normative_strength_preserved_not_flattened,
        test_conditions_preserved,
        test_requirement_count_matches_clause_count,
        test_applicable_standard_and_implemented_function,
        test_applicable_standard_and_inherited_function,
        test_conditional_clause_status_is_unknown_not_silently_dropped,
        test_unrelated_clause_not_applicable_when_standard_not_applicable,
        test_clause_not_applicable_when_optional_function_absent,
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
