"""Unit tests for rtf.l11_investigation_grouping.property_grounding
(RTF v2 Phase 6/7: grounding/rejection + semantic-property dedup). Run
with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_property_grounding
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.property_grounding import (
    RejectedProperty, deduplicate_semantic_properties, ground_semantic_properties,
    ground_semantic_property, merge_property_pools, rejected_property_to_dict,
)
from rtf.l11_investigation_grouping.semantic_property_generation import ProjectManifest, RawSemanticProperty
from rtf.l11_investigation_grouping.taxonomy import ReasoningCategory
from rtf.l10_property_derivation.derive_investigations import InvestigationInstance
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata, derive_property_metadata

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


_MANIFEST = ProjectManifest(
    contracts=("Vault", "FeeManager"),
    functions=("Vault.totalAssets", "Vault.deposit", "FeeManager.accrue"),
    state_variables=("Vault.totalAssets_", "FeeManager.accruedFees"),
)


def _raw(**overrides) -> RawSemanticProperty:
    base = dict(
        statement="Vault.totalAssets must not include FeeManager.accruedFees already owed to fee recipients.",
        property_type="accounting",
        rationale="ERC-4626 totalAssets should reflect assets economically owned by shareholders.",
        affected_contracts=("Vault", "FeeManager"),
        affected_functions=("Vault.totalAssets",),
        affected_state_variables=("FeeManager.accruedFees",),
        source_refs=("gp-accepted-standard__erc-4626__erc4626-totalassets-must-include-fees",),
        confidence=0.7,
    )
    base.update(overrides)
    return RawSemanticProperty(**base)


# --- ground_semantic_property: acceptance -----------------------------

def test_ground_accepts_a_well_formed_property():
    result = ground_semantic_property(_raw(), _MANIFEST)
    check("ground: accepted (PropertyMetadata, not rejected)", isinstance(result, PropertyMetadata), result)
    md = result
    check("ground: source_kind=code_semantics", md.source_kind == "code_semantics")
    check("ground: generation_method=semantic_derivation", md.generation_method == "semantic_derivation")
    check("ground: requirement_level=SEMANTIC", md.requirement_level == "SEMANTIC")
    check("ground: property_text is the statement", md.property_text == _raw().statement)
    check("ground: target_contract/function from first affected_function",
          (md.target_contract, md.target_function) == ("Vault", "totalAssets"), (md.target_contract, md.target_function))
    check("ground: relevant_state_variables carries bare var names", md.relevant_state_variables == ("accruedFees",), md.relevant_state_variables)
    check("ground: reasoning_category mapped from property_type",
          md.reasoning_category == ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS, md.reasoning_category)
    check("ground: rationale preserved", md.rationale == _raw().rationale)
    check("ground: confidence preserved", md.confidence == 0.7)
    check("ground: grounding_evidence non-empty and includes the source_ref",
          any("erc4626-totalassets-must-include-fees" in e for e in md.grounding_evidence), md.grounding_evidence)


def test_ground_target_falls_back_to_contract_when_no_functions_named():
    raw = _raw(affected_functions=(), statement="FeeManager must track accruedFees accurately at all times.")
    result = ground_semantic_property(raw, _MANIFEST)
    check("ground: falls back to contract-only target", isinstance(result, PropertyMetadata), result)
    check("ground: target_function is None when no function named", result.target_function is None, result)
    check("ground: target_contract is the first affected_contract", result.target_contract == "Vault", result.target_contract)


# --- ground_semantic_property: rejection -------------------------------

def test_ground_rejects_unknown_contract_reference():
    raw = _raw(affected_contracts=("Vault", "ImaginaryContract"))
    result = ground_semantic_property(raw, _MANIFEST)
    check("ground: rejects a hallucinated contract name", isinstance(result, RejectedProperty), result)
    check("ground: reason names the bad reference", "ungrounded_reference" in result.reason and "ImaginaryContract" in result.reason, result.reason)


def test_ground_rejects_unknown_function_reference():
    raw = _raw(affected_functions=("Vault.imaginaryFunction",))
    result = ground_semantic_property(raw, _MANIFEST)
    check("ground: rejects a hallucinated function name", isinstance(result, RejectedProperty), result)
    check("ground: reason names it", "imaginaryFunction" in result.reason, result.reason)


def test_ground_rejects_no_concrete_target():
    raw = _raw(affected_contracts=(), affected_functions=(), affected_state_variables=())
    result = ground_semantic_property(raw, _MANIFEST)
    check("ground: rejects a property naming nothing concrete", isinstance(result, RejectedProperty), result)
    check("ground: reason is no_concrete_target_named", result.reason == "no_concrete_target_named", result.reason)


def test_ground_rejects_banned_generic_statements():
    for statement in (
        "The protocol should not lose money.",
        "The code should be secure.",
        "Accounting should be correct.",
    ):
        raw = _raw(statement=statement)
        result = ground_semantic_property(raw, _MANIFEST)
        check(f"ground: rejects banned generic statement {statement!r}", isinstance(result, RejectedProperty), result)
        check(f"ground: reason is generic_banned_statement for {statement!r}",
              isinstance(result, RejectedProperty) and result.reason.startswith("generic_banned_statement"), result)


def test_ground_rejects_statement_not_mentioning_its_own_affected_targets():
    # affected_* names real things, but the statement text itself never
    # references any of them -- still ungrounded prose, just not one of
    # the literal banned phrases.
    raw = _raw(statement="Something must always remain true across the whole system at every point in time.")
    result = ground_semantic_property(raw, _MANIFEST)
    check("ground: rejects a statement that never names its own concrete targets", isinstance(result, RejectedProperty), result)
    check("ground: reason is statement_not_concretely_grounded", result.reason == "statement_not_concretely_grounded", result.reason)


def test_ground_rejects_no_rationale_and_no_source_refs():
    raw = _raw(rationale="", source_refs=())
    result = ground_semantic_property(raw, _MANIFEST)
    check("ground: rejects a property with zero justification", isinstance(result, RejectedProperty), result)
    check("ground: reason is insufficient_grounding_evidence", result.reason == "insufficient_grounding_evidence", result.reason)


def test_ground_accepts_with_rationale_alone_even_without_source_refs():
    raw = _raw(source_refs=())
    result = ground_semantic_property(raw, _MANIFEST)
    check("ground: rationale alone is sufficient justification (source_refs not required)",
          isinstance(result, PropertyMetadata), result)


# --- batch grounding + observability serialization ----------------------

def test_ground_semantic_properties_batch_splits_accepted_and_rejected():
    good = _raw()
    bad = _raw(affected_contracts=("NotReal",), affected_functions=(), affected_state_variables=())
    accepted, rejected = ground_semantic_properties([good, bad], _MANIFEST)
    check("batch: exactly one accepted", len(accepted) == 1, accepted)
    check("batch: exactly one rejected", len(rejected) == 1, rejected)


def test_rejected_property_to_dict_is_json_safe():
    import json
    rejection = RejectedProperty(raw=_raw(), reason="no_concrete_target_named")
    d = rejected_property_to_dict(rejection)
    check("rejected_property_to_dict: JSON-serializable", json.dumps(d) is not None)
    check("rejected_property_to_dict: reason preserved", d["reason"] == "no_concrete_target_named", d)


# --- deduplicate_semantic_properties / merge_property_pools -------------

def _semantic_md(statement: str, state_vars: tuple[str, ...], property_id_suffix: str) -> PropertyMetadata:
    raw = _raw(statement=statement, affected_state_variables=tuple(f"FeeManager.{v}" for v in state_vars))
    md = ground_semantic_property(raw, _MANIFEST)
    assert isinstance(md, PropertyMetadata)
    from dataclasses import replace
    return replace(md, property_id=f"{md.property_id}-{property_id_suffix}")


def test_dedup_merges_near_duplicate_semantic_properties():
    p1 = _semantic_md("Vault.totalAssets must account for FeeManager.accruedFees owed to fee recipients.", ("accruedFees",), "a")
    p2 = _semantic_md("FeeManager.accruedFees must be excluded from Vault.totalAssets shareholder-backed value.", ("accruedFees",), "b")
    p3 = _semantic_md("Accrued FeeManager.accruedFees must not inflate Vault.totalAssets share value.", ("accruedFees",), "c")
    merged = deduplicate_semantic_properties([p1, p2, p3])
    check("dedup: three near-duplicates merge into one canonical property", len(merged) == 1, len(merged))
    check("dedup: canonical property_id is one of the three (deterministic tie-break by sorted property_id)",
          merged[0].property_id in (p1.property_id, p2.property_id, p3.property_id), merged[0].property_id)
    check("dedup: the other two statements are preserved (attributed) in explanatory text",
          "Consolidated duplicate" in merged[0].requirement_explanatory_text, merged[0].requirement_explanatory_text)


def test_dedup_does_not_merge_unrelated_properties():
    p1 = _semantic_md("Vault.totalAssets must account for FeeManager.accruedFees.", ("accruedFees",), "a")
    p2_raw = _raw(
        statement="FeeManager.accrue must only be callable by an authorized role, per access-control policy.",
        property_type="authorization", affected_state_variables=(), affected_functions=("FeeManager.accrue",),
        affected_contracts=("FeeManager",),
    )
    p2 = ground_semantic_property(p2_raw, _MANIFEST)
    assert isinstance(p2, PropertyMetadata)
    merged = deduplicate_semantic_properties([p1, p2])
    check("dedup: unrelated properties (different category, no shared state) stay separate", len(merged) == 2, len(merged))


def test_dedup_leaves_non_semantic_properties_untouched():
    instance = InvestigationInstance(
        req_id="req-3-all-valid-inputs", instance_id="req-3-all-valid-inputs::loc0",
        candidate_location="Vault.withdraw", focused_clause=None, clause_index=0, location_index=0,
    )
    structural = derive_property_metadata(
        instance, {"req_id": "req-3-all-valid-inputs", "level": "Q", "title": "x", "normative_text": "x"},
        parent_candidate_locations=["Vault.withdraw"],
    )
    result = deduplicate_semantic_properties([structural])
    check("dedup: non-semantic property passed through unchanged", result == [structural], result)


def test_merge_property_pools_combines_and_dedups():
    instance = InvestigationInstance(
        req_id="req-3-all-valid-inputs", instance_id="req-3-all-valid-inputs::loc0",
        candidate_location="Vault.withdraw", focused_clause=None, clause_index=0, location_index=0,
    )
    structural = derive_property_metadata(
        instance, {"req_id": "req-3-all-valid-inputs", "level": "Q", "title": "x", "normative_text": "x"},
        parent_candidate_locations=["Vault.withdraw"],
    )
    p1 = _semantic_md("Vault.totalAssets must account for FeeManager.accruedFees.", ("accruedFees",), "a")
    p2 = _semantic_md("FeeManager.accruedFees must not inflate Vault.totalAssets.", ("accruedFees",), "b")
    merged = merge_property_pools([structural], [p1, p2])
    check("merge: structural property present", structural in merged, merged)
    check("merge: semantic near-duplicates consolidated into one", len([m for m in merged if m.source_kind == "code_semantics"]) == 1, merged)
    check("merge: total pool size is 2 (1 structural + 1 consolidated semantic)", len(merged) == 2, len(merged))


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
