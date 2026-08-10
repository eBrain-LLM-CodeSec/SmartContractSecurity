"""Phase 11 of the grouped-investigation architecture: end-to-end
integration tests over synthetic, non-EVMbench-derived fixtures.

Exercises the FULL pipeline built across Phases 2-10 in one continuous
path: derive_property_metadata -> apply_grouping_policy ->
generate_*_context_md / generate_cluster_plan_md ->
build_cluster_investigation_prompt -> (a MOCKED Codex JSON response,
never a live call) -> validate_cluster_response -> resolve_property_
verdicts. No EVMbench code or vulnerability description was used to
design any fixture below -- each is an invented synthetic contract
built specifically to exercise the property this test checks. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_end_to_end_integration
"""
from __future__ import annotations

import sys

from a4v.graph import ProgramGraph
from rtf.l10_property_derivation.derive_investigations import InvestigationInstance
from rtf.l11_investigation_grouping.cluster_prompt import build_cluster_investigation_prompt
from rtf.l11_investigation_grouping.cluster_response_validation import (
    resolve_property_verdicts, validate_cluster_response,
)
from rtf.l11_investigation_grouping.context_artifacts import (
    generate_cluster_plan_md, generate_protocol_context_md, generate_requirement_context_md,
)
from rtf.l11_investigation_grouping.policies import apply_grouping_policy
from rtf.l11_investigation_grouping.property_metadata import derive_property_metadata
from rtf.l11_investigation_grouping.run_metadata import GROUPING_POLICY_G2_CONTEXT_AWARE
from rtf.l12_evaluation.metrics import ConformanceState
from rtf.l5_predicates.compile_helper import compile_source

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


# --- Scenario 1: several arithmetic functions with boundary-domain obligations --
# (synthetic, invented for this test; no EVMbench code)

_ARITHMETIC_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MathLib {
    uint256 public totalSupply;

    function addShares(uint256 amount) public {
        totalSupply += amount;
    }

    function removeShares(uint256 amount) public {
        totalSupply -= amount;
    }

    function halveShares() public {
        totalSupply = totalSupply / 2;
    }
}
"""

_REQ_RECORD = {
    "req_id": "req-3-all-valid-inputs", "level": "Q", "title": "Process All Inputs",
    "normative_text": "Tested Code MUST validate inputs, and function correctly whether the input is as designed or malformed.",
    "section": {"secno": "5.3"},
}


def _instance(req_id: str, candidate_location: str, instance_suffix: str) -> InvestigationInstance:
    return InvestigationInstance(
        req_id=req_id, instance_id=f"{req_id}::{instance_suffix}", candidate_location=candidate_location,
        focused_clause=None, clause_index=0, location_index=0,
    )


def test_full_pipeline_groups_related_properties_and_generates_valid_plan():
    slither = compile_source(_ARITHMETIC_SOURCE)
    pg = ProgramGraph.from_slither(slither)

    # 3 properties, all from the SAME requirement, SAME contract -- these
    # should group together under G2 (shared requirement + contract).
    instances = [
        _instance("req-3-all-valid-inputs", "MathLib.addShares", "loc0"),
        _instance("req-3-all-valid-inputs", "MathLib.removeShares", "loc1"),
        _instance("req-3-all-valid-inputs", "MathLib.halveShares", "loc2"),
    ]
    props = [
        derive_property_metadata(inst, _REQ_RECORD, parent_candidate_locations=[i.candidate_location for i in instances],
                                  pg=pg, slither=slither)
        for inst in instances
    ]
    by_id = {p.property_id: p for p in props}

    clusters = apply_grouping_policy(props, GROUPING_POLICY_G2_CONTEXT_AWARE)
    check("3 related properties -> 1 cluster under G2", len(clusters) == 1, clusters)
    cluster = clusters[0]
    check("cluster contains all 3 properties", set(cluster.property_ids) == set(by_id.keys()), cluster.property_ids)

    protocol_md = generate_protocol_context_md("test-audit", slither, ["src/MathLib.sol"])
    req_md = generate_requirement_context_md(_REQ_RECORD)
    plan_md = generate_cluster_plan_md(cluster, by_id, ".rtf/context/protocol_context.md",
                                        {"req-3-all-valid-inputs": ".rtf/context/requirements/req-3-all-valid-inputs.md"})

    check("protocol context mentions MathLib", "MathLib" in protocol_md, protocol_md)
    check("requirement context has the real normative text", _REQ_RECORD["normative_text"] in req_md, req_md)
    check("cluster plan lists all 3 property ids", all(pid in plan_md for pid in by_id), plan_md)

    prompt = build_cluster_investigation_prompt(
        ".rtf/context/protocol_context.md", [".rtf/context/requirements/req-3-all-valid-inputs.md"],
        ".rtf/plans/cluster_000.md",
    )
    check("prompt references all 3 file paths", all(
        p in prompt for p in (".rtf/context/protocol_context.md", ".rtf/context/requirements/req-3-all-valid-inputs.md", ".rtf/plans/cluster_000.md")
    ), prompt)


def test_grouped_execution_catches_one_failing_property_while_passing_siblings():
    """The core claim Phase 11 exists to verify: a MOCKED cluster
    response where the agent correctly found halveShares() has NO
    zero-check (a real, if synthetic, division-truncation issue: a
    single share left after repeated halving silently becomes 0) while
    addShares/removeShares are genuinely fine -- and the harness
    resolves each property independently and correctly, not
    contaminating siblings.
    """
    slither = compile_source(_ARITHMETIC_SOURCE)
    pg = ProgramGraph.from_slither(slither)
    instances = [
        _instance("req-3-all-valid-inputs", "MathLib.addShares", "loc0"),
        _instance("req-3-all-valid-inputs", "MathLib.removeShares", "loc1"),
        _instance("req-3-all-valid-inputs", "MathLib.halveShares", "loc2"),
    ]
    props = [
        derive_property_metadata(inst, _REQ_RECORD, parent_candidate_locations=[i.candidate_location for i in instances],
                                  pg=pg, slither=slither)
        for inst in instances
    ]
    by_id = {p.property_id: p for p in props}
    cluster = apply_grouping_policy(props, GROUPING_POLICY_G2_CONTEXT_AWARE)[0]

    add_id = next(pid for pid in cluster.property_ids if "loc0" in pid)
    remove_id = next(pid for pid in cluster.property_ids if "loc1" in pid)
    halve_id = next(pid for pid in cluster.property_ids if "loc2" in pid)

    # A plausible, well-formed MOCKED response -- never generated by this
    # test from the cluster plan (which never states an expected
    # outcome); this simulates what a real Codex investigation session
    # would independently return after actually reading the code.
    mocked_response = {
        "properties": [
            {
                "property_id": add_id, "verdict": "PASS",
                "counterexample_attempt": "Considered whether a very large amount could overflow totalSupply.",
                "counterexample_result": "Solidity 0.8+ default checked arithmetic reverts on overflow; no silent wraparound possible.",
                "reasoning": "addShares uses += with no unchecked block; overflow reverts by default.",
                "files_read": ["src/MathLib.sol"], "vulnerable_location": None, "confidence": "HIGH",
            },
            {
                "property_id": remove_id, "verdict": "PASS",
                "counterexample_attempt": "Considered whether amount > totalSupply could underflow.",
                "counterexample_result": "Solidity 0.8+ default checked arithmetic reverts on underflow; confirmed no unchecked block wraps this.",
                "reasoning": "removeShares uses -= with no unchecked block; underflow reverts by default.",
                "files_read": ["src/MathLib.sol"], "vulnerable_location": None, "confidence": "HIGH",
            },
            {
                "property_id": halve_id, "verdict": "FAIL",
                "evidence": "totalSupply / 2 silently truncates; a single remaining share (totalSupply=1) becomes 0.",
                "reasoning": "Integer division truncates toward zero with no rounding-loss check or event, losing the last unit of value silently.",
                "files_read": ["src/MathLib.sol"], "vulnerable_location": "src/MathLib.sol:halveShares",
                "confidence": "HIGH",
            },
        ]
    }

    validation = validate_cluster_response(list(cluster.property_ids), mocked_response)
    check("mocked response is structurally complete", validation.complete, validation)
    check("no duplicated reasoning flagged (each property genuinely distinct)", validation.duplicated_reasoning_groups == (), validation.duplicated_reasoning_groups)

    resolved = resolve_property_verdicts(mocked_response)
    check("addShares resolves to PASS", resolved[add_id].conformance_state == ConformanceState.PASS, resolved[add_id])
    check("removeShares resolves to PASS", resolved[remove_id].conformance_state == ConformanceState.PASS, resolved[remove_id])
    check("halveShares resolves to FAIL", resolved[halve_id].conformance_state == ConformanceState.FAIL, resolved[halve_id])
    check("the FAIL on halveShares did not affect addShares' independent PASS",
          resolved[add_id].conformance_state == ConformanceState.PASS and resolved[add_id].reason is None)
    check("the FAIL on halveShares did not affect removeShares' independent PASS",
          resolved[remove_id].conformance_state == ConformanceState.PASS and resolved[remove_id].reason is None)


def test_grouped_execution_rejects_a_lazy_pass_without_real_counterexample_search():
    """Same 3-property cluster, but the mocked response gives a lazy,
    unsupported PASS for one property -- the harness must downgrade
    THAT property to INCONCLUSIVE without affecting the others."""
    slither = compile_source(_ARITHMETIC_SOURCE)
    pg = ProgramGraph.from_slither(slither)
    instances = [
        _instance("req-3-all-valid-inputs", "MathLib.addShares", "loc0"),
        _instance("req-3-all-valid-inputs", "MathLib.removeShares", "loc1"),
    ]
    props = [
        derive_property_metadata(inst, _REQ_RECORD, parent_candidate_locations=[i.candidate_location for i in instances],
                                  pg=pg, slither=slither)
        for inst in instances
    ]
    by_id = {p.property_id: p for p in props}
    cluster = apply_grouping_policy(props, GROUPING_POLICY_G2_CONTEXT_AWARE)[0]
    add_id = next(pid for pid in cluster.property_ids if "loc0" in pid)
    remove_id = next(pid for pid in cluster.property_ids if "loc1" in pid)

    mocked_response = {
        "properties": [
            {"property_id": add_id, "verdict": "PASS", "counterexample_attempt": "n/a", "counterexample_result": "n/a",
             "reasoning": "Looks fine."},
            {"property_id": remove_id, "verdict": "PASS",
             "counterexample_attempt": "Considered amount > totalSupply causing underflow.",
             "counterexample_result": "Confirmed default checked arithmetic reverts; no unchecked block present.",
             "reasoning": "removeShares is safe."},
        ]
    }
    resolved = resolve_property_verdicts(mocked_response)
    check("lazy PASS (thin counterexample) downgraded to INCONCLUSIVE",
          resolved[add_id].conformance_state == ConformanceState.INCONCLUSIVE, resolved[add_id])
    check("well-supported sibling PASS unaffected by the other's downgrade",
          resolved[remove_id].conformance_state == ConformanceState.PASS, resolved[remove_id])


# --- Scenario 2: multiple signature-authorized actions ----------------------
# (synthetic, invented for this test; no EVMbench code)

_SIGNATURE_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SignatureGate {
    mapping(bytes32 => bool) public used;

    function claimA(bytes32 messageHash, uint8 v, bytes32 r, bytes32 s) public {
        address signer = ecrecover(messageHash, v, r, s);
        require(signer != address(0), "bad sig");
        used[messageHash] = true;
    }

    function claimB(bytes32 messageHash, uint8 v, bytes32 r, bytes32 s) public {
        address signer = ecrecover(messageHash, v, r, s);
        used[messageHash] = true;
    }
}
"""

_SIG_REQ_RECORD = {
    "req_id": "req-2-signature-verification", "level": "M", "title": "Proper Signature Verification",
    "normative_text": "Tested Code MUST properly verify signatures to ensure authenticity of messages that were signed off-chain.",
    "section": {"secno": "5.2.4"},
}


def test_signature_scenario_groups_and_independently_flags_the_unchecked_one():
    slither = compile_source(_SIGNATURE_SOURCE)
    pg = ProgramGraph.from_slither(slither)
    instances = [
        _instance("req-2-signature-verification", "SignatureGate.claimA", "loc0"),
        _instance("req-2-signature-verification", "SignatureGate.claimB", "loc1"),
    ]
    props = [
        derive_property_metadata(inst, _SIG_REQ_RECORD, parent_candidate_locations=[i.candidate_location for i in instances],
                                  pg=pg, slither=slither)
        for inst in instances
    ]
    by_id = {p.property_id: p for p in props}
    clusters = apply_grouping_policy(props, GROUPING_POLICY_G2_CONTEXT_AWARE)
    check("both signature-verification properties group (same requirement+contract)", len(clusters) == 1, clusters)
    cluster = clusters[0]
    a_id = next(pid for pid in cluster.property_ids if "loc0" in pid)
    b_id = next(pid for pid in cluster.property_ids if "loc1" in pid)

    mocked_response = {
        "properties": [
            {"property_id": a_id, "verdict": "PASS",
             "counterexample_attempt": "Considered whether an invalid signature returning address(0) could be accepted.",
             "counterexample_result": "require(signer != address(0)) rejects the zero-address failure case.",
             "reasoning": "claimA checks the ecrecover result before using it."},
            {"property_id": b_id, "verdict": "FAIL",
             "evidence": "claimB never checks `signer` against address(0) or anything else before marking used[messageHash]=true.",
             "reasoning": "An invalid signature (ecrecover returns address(0)) is silently accepted as authorization."},
        ]
    }
    resolved = resolve_property_verdicts(mocked_response)
    check("claimA (checked) resolves PASS", resolved[a_id].conformance_state == ConformanceState.PASS, resolved[a_id])
    check("claimB (unchecked) resolves FAIL, independently of claimA's PASS", resolved[b_id].conformance_state == ConformanceState.FAIL, resolved[b_id])


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
