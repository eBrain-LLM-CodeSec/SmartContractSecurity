"""Unit tests for rtf.l11_investigation_grouping.property_metadata.
Synthetic fixtures only (invented Solidity, no EVMbench code). Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_property_metadata
"""
from __future__ import annotations

import sys

from dataclasses import replace

from a4v.graph import ProgramGraph
from rtf.l10_property_derivation.derive_investigations import InvestigationInstance
from rtf.l11_investigation_grouping.property_metadata import (
    derive_property_metadata, filter_properties_to_scope, parse_contract_function,
)
from rtf.l12_evaluation.metrics import EvidenceItem
from rtf.l5_predicates.compile_helper import compile_source

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


# --- parse_contract_function -------------------------------------------

def test_parse_contract_dot_function():
    check("parse: Contract.function", parse_contract_function("Vault.withdraw") == ("Vault", "withdraw"))


def test_parse_bare_contract():
    check("parse: bare contract (no function)", parse_contract_function("Vault") == ("Vault", None))


def test_parse_empty_string():
    check("parse: empty string -> (None, None)", parse_contract_function("") == (None, None))


# --- derive_property_metadata: pure/synthetic (no graph/slither) -----------

_REQ_RECORD = {
    "req_id": "req-3-all-valid-inputs", "level": "Q", "title": "Process All Inputs",
    "normative_text": "Process All Inputs Tested Code MUST validate inputs.",
    "section": {"secno": "5.3"},
}


def test_metadata_populates_spec_derived_fields():
    instance = InvestigationInstance(
        req_id="req-3-all-valid-inputs", instance_id="req-3-all-valid-inputs::loc0",
        candidate_location="Vault.withdraw", focused_clause=None, clause_index=0, location_index=0,
    )
    md = derive_property_metadata(instance, _REQ_RECORD, parent_candidate_locations=["Vault.withdraw", "Vault.deposit"])
    check("metadata: property_id from instance_id", md.property_id == "req-3-all-valid-inputs::loc0")
    check("metadata: requirement_id", md.requirement_id == "req-3-all-valid-inputs")
    check("metadata: requirement_level from corpus record", md.requirement_level == "Q")
    check("metadata: requirement_semantic_intent is the spec title", md.requirement_semantic_intent == "Process All Inputs")
    check("metadata: property_text falls back to full normative_text (no focused_clause)",
          md.property_text == _REQ_RECORD["normative_text"])
    check("metadata: target_contract/function parsed from candidate_location",
          (md.target_contract, md.target_function) == ("Vault", "withdraw"))
    check("metadata: location preserves the raw candidate_location verbatim",
          md.location == "Vault.withdraw", md.location)
    check("metadata: candidate_locations carries the FULL parent list, deduped",
          md.candidate_locations == ("Vault.withdraw", "Vault.deposit"), md.candidate_locations)
    check("metadata: reasoning_category is None (Phase 3 not run yet)", md.reasoning_category is None)
    check("metadata: estimated_complexity is None (Phase 6 not run yet)", md.estimated_complexity is None)
    check("metadata: source_provenance names the req_id and spec section",
          "req_id=req-3-all-valid-inputs" in md.source_provenance and "spec_section=5.3" in md.source_provenance,
          md.source_provenance)


def test_metadata_uses_focused_clause_as_property_text_when_multi_clause():
    instance = InvestigationInstance(
        req_id="req-2-check-rounding", instance_id="req-2-check-rounding::clause1",
        candidate_location="Vault._computeShares", focused_clause="Tested code MUST NOT unintentionally lose value.",
        clause_index=1, location_index=0,
    )
    md = derive_property_metadata(instance, {"req_id": "req-2-check-rounding", "level": "M", "title": "Ensure Proper Rounding"},
                                   parent_candidate_locations=["Vault._computeShares"])
    check("metadata: property_text is the focused clause, not the whole requirement",
          md.property_text == "Tested code MUST NOT unintentionally lose value.", md.property_text)
    check("metadata: source_provenance names the clause index", "clause_index=1" in md.source_provenance, md.source_provenance)


def test_metadata_with_no_evidence_or_graph_degrades_to_empty_enrichment():
    instance = InvestigationInstance(
        req_id="req-x", instance_id="req-x::loc0", candidate_location="Vault.f",
        focused_clause=None, clause_index=0, location_index=0,
    )
    md = derive_property_metadata(instance, {"req_id": "req-x"}, parent_candidate_locations=["Vault.f"])
    check("no enrichment: relevant_files empty", md.relevant_files == ())
    check("no enrichment: relevant_symbols empty", md.relevant_symbols == ())
    check("no enrichment: relevant_state_variables empty", md.relevant_state_variables == ())
    check("no enrichment: callgraph_neighbors empty", md.callgraph_neighbors == ())
    check("no enrichment: inheritance_context empty", md.inheritance_context == ())


def test_metadata_extracts_symbols_and_types_from_structured_evidence():
    instance = InvestigationInstance(
        req_id="req-3-all-valid-inputs", instance_id="req-3-all-valid-inputs::loc0",
        candidate_location="Vault._mint", focused_clause=None, clause_index=0, location_index=0,
    )
    evidence = EvidenceItem(
        predicate="find_unsafe_narrowing_cast", location="Vault._mint",
        detail="unsafe narrowing cast", structured={"input": {"name": "_shares", "type": "uint256"}},
    )
    md = derive_property_metadata(instance, _REQ_RECORD, parent_candidate_locations=["Vault._mint"], evidence=evidence)
    check("structured evidence: relevant_symbols has the input name", md.relevant_symbols == ("_shares",), md.relevant_symbols)
    check("structured evidence: relevant_types has the input type", md.relevant_types == ("uint256",), md.relevant_types)


def test_metadata_candidate_locations_dedupes_and_drops_empty():
    instance = InvestigationInstance(
        req_id="req-x", instance_id="req-x::loc0", candidate_location="Vault.f",
        focused_clause=None, clause_index=0, location_index=0,
    )
    md = derive_property_metadata(instance, {"req_id": "req-x"},
                                   parent_candidate_locations=["Vault.f", "Vault.g", "Vault.f", "", "Vault.g"])
    check("candidate_locations: deduped and empty dropped, order preserved",
          md.candidate_locations == ("Vault.f", "Vault.g"), md.candidate_locations)


# --- real graph/slither enrichment (compiled fixture, no EVMbench) ---------

_ENRICHMENT_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

abstract contract Ownable {
    address public owner;
}

contract Vault is Ownable {
    uint256 public totalShares;
    uint256 public constant MAX_SHARES = 1_000_000;

    function withdraw(uint256 amount) public {
        _burn(amount);
    }

    function _burn(uint256 amount) internal {
        totalShares -= amount;
    }
}
"""


def test_real_graph_enrichment_finds_callees_and_state_variables():
    slither = compile_source(_ENRICHMENT_SOURCE)
    pg = ProgramGraph.from_slither(slither)

    instance = InvestigationInstance(
        req_id="req-x", instance_id="req-x::loc0", candidate_location="Vault.withdraw",
        focused_clause=None, clause_index=0, location_index=0,
    )
    md = derive_property_metadata(
        instance, {"req_id": "req-x"}, parent_candidate_locations=["Vault.withdraw"], pg=pg, slither=slither,
    )
    check("real graph: withdraw's callgraph_neighbors includes _burn",
          any("_burn" in n for n in md.callgraph_neighbors), md.callgraph_neighbors)
    check("real slither: inheritance_context includes Ownable", "Ownable" in md.inheritance_context, md.inheritance_context)
    check("real slither: relevant_constants includes MAX_SHARES", "MAX_SHARES" in md.relevant_constants, md.relevant_constants)
    check("real slither: relevant_files is non-empty", len(md.relevant_files) > 0, md.relevant_files)


def test_real_graph_enrichment_state_variables_from_burn_function():
    slither = compile_source(_ENRICHMENT_SOURCE)
    pg = ProgramGraph.from_slither(slither)

    instance = InvestigationInstance(
        req_id="req-x", instance_id="req-x::loc0", candidate_location="Vault._burn",
        focused_clause=None, clause_index=0, location_index=0,
    )
    md = derive_property_metadata(instance, {"req_id": "req-x"}, parent_candidate_locations=["Vault._burn"], pg=pg)
    check("real graph: _burn's relevant_state_variables includes totalShares",
          any("totalShares" in v for v in md.relevant_state_variables), md.relevant_state_variables)


def test_unresolvable_candidate_location_on_real_graph_degrades_gracefully():
    slither = compile_source(_ENRICHMENT_SOURCE)
    pg = ProgramGraph.from_slither(slither)
    instance = InvestigationInstance(
        req_id="req-x", instance_id="req-x::loc0", candidate_location="Vault.doesNotExist",
        focused_clause=None, clause_index=0, location_index=0,
    )
    md = derive_property_metadata(instance, {"req_id": "req-x"}, parent_candidate_locations=["Vault.doesNotExist"], pg=pg)
    check("unresolvable location: no crash, empty graph enrichment", md.callgraph_neighbors == () and md.relevant_state_variables == ())


# --- filter_properties_to_scope -----------------------------------------

def _synthetic_property(location: str, relevant_files: tuple[str, ...] = ()):
    instance = InvestigationInstance(
        req_id="req-x", instance_id=f"req-x::{location}", candidate_location=location,
        focused_clause=None, clause_index=0, location_index=0,
    )
    md = derive_property_metadata(instance, {"req_id": "req-x"}, parent_candidate_locations=[location])
    return replace(md, relevant_files=relevant_files)


def test_scope_filter_keeps_property_whose_relevant_files_matches_scope():
    props = [_synthetic_property("Vault.withdraw", relevant_files=("src/Vault.sol",))]
    kept = filter_properties_to_scope(props, ["src/Vault.sol"])
    check("scope filter: in-scope relevant_files kept", kept == props)


def test_scope_filter_drops_vendored_library_not_in_scope():
    props = [_synthetic_property("Address._revert", relevant_files=("lib/openzeppelin-contracts/contracts/utils/Address.sol",))]
    kept = filter_properties_to_scope(props, ["src/Vault.sol"])
    check("scope filter: out-of-scope vendored lib dropped", kept == [])


def test_scope_filter_tolerates_relative_prefix_differences():
    props = [_synthetic_property("Vault.withdraw", relevant_files=("2024-01-project/src/Vault.sol",))]
    kept = filter_properties_to_scope(props, ["src/Vault.sol"])
    check("scope filter: differing relative prefixes still match (suffix comparison)", kept == props)


def test_scope_filter_falls_back_to_location_when_relevant_files_empty():
    in_scope = _synthetic_property("README.md")
    out_of_scope = _synthetic_property("README.md")
    kept_in = filter_properties_to_scope([in_scope], ["README.md"])
    kept_out = filter_properties_to_scope([out_of_scope], ["src/Vault.sol"])
    check("scope filter: location fallback keeps in-scope README.md", kept_in == [in_scope])
    check("scope filter: location fallback drops out-of-scope README.md", kept_out == [])


def test_scope_filter_always_keeps_non_file_pseudo_locations():
    props = [_synthetic_property("compiler config"), _synthetic_property("2024-01-project")]
    kept = filter_properties_to_scope(props, ["src/Vault.sol"])
    check("scope filter: non-file pseudo-locations (compiler config, bare project name) always kept",
          kept == props, kept)


def test_scope_filter_is_noop_with_empty_scope_files():
    props = [_synthetic_property("Address._revert", relevant_files=("lib/openzeppelin-contracts/contracts/utils/Address.sol",))]
    kept = filter_properties_to_scope(props, [])
    check("scope filter: empty scope_files is a no-op (keeps everything)", kept == props)


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
