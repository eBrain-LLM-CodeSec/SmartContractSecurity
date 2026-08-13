"""Integration tests for rtf.l11_investigation_grouping.semantic_pipeline,
and the task brief's Section 17-G synthetic end-to-end scenario: an
ERC-4626-shaped vault with a fee accumulator, with NO hand-written
"bad totalAssets" predicate anywhere in this codebase, still produces a
grounded semantic property about the totalAssets/fee relationship, and
that property clusters correctly with the grouping engine. Zero real LLM
calls (fake chat_client). Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_pipeline
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from rtf.l11_investigation_grouping.grouping_engine import cluster_properties
from rtf.l11_investigation_grouping.policies import GROUPING_POLICY_G2_CONTEXT_AWARE, apply_grouping_policy
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.l11_investigation_grouping.semantic_pipeline import (
    build_full_property_pool, generate_and_ground_semantic_properties, write_observability_artifacts,
)
from rtf.l11_investigation_grouping.semantic_property_generation import ProjectManifest
from rtf.l5_predicates.compile_helper import compile_evmbench_target

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


class FakeChatClient:
    def __init__(self, response: dict):
        self.response = response

    def complete_json(self, messages, temperature=0.0, **kwargs):
        return self.response, None


_VAULT_WITH_FEE_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Vault {
    uint256 public totalAssetsHeld;
    uint256 public accruedFees;

    function deposit(uint256 amount) external {
        totalAssetsHeld += amount;
    }

    function accrueFee(uint256 amount) external {
        accruedFees += amount;
    }

    // Intentionally does not subtract accruedFees -- the synthetic bug
    // this test's semantic property is ABOUT, not something this test's
    // production code (semantic_property_generation.py/property_grounding.py)
    // knows about or hard-codes.
    function totalAssets() external view returns (uint256) {
        return totalAssetsHeld;
    }

    function withdrawFees(address to, uint256 amount) external {
        accruedFees -= amount;
    }
}
"""

_TOTAL_ASSETS_FEE_PROPERTY_ENTRY = {
    "statement": "Vault.totalAssets must not include amounts already owed via Vault.accruedFees.",
    "property_type": "accounting",
    "rationale": "Assets already accrued as fees are no longer economically owned by shareholders; "
                 "totalAssets should reflect only shareholder-backed assets.",
    "affected_contracts": ["Vault"],
    "affected_functions": ["Vault.totalAssets", "Vault.accrueFee"],
    "affected_state_variables": ["Vault.totalAssetsHeld", "Vault.accruedFees"],
    "source_refs": ["synthetic-fixture-erc4626-fee-accounting"],
    "confidence": 0.8,
}


def _compile_vault():
    tmp = tempfile.TemporaryDirectory()
    repo = Path(tmp.name)
    (repo / "Vault.sol").write_text(_VAULT_WITH_FEE_SOURCE, encoding="utf-8")
    slither = compile_evmbench_target(repo / "Vault.sol", repo, solc_version="0.8.20")
    return tmp, repo, slither


def test_generate_and_ground_produces_the_fee_accounting_property_with_no_hand_written_predicate():
    tmp, repo, slither = _compile_vault()
    try:
        manifest = ProjectManifest.from_slither(slither)
        client = FakeChatClient({"properties": [_TOTAL_ASSETS_FEE_PROPERTY_ENTRY]})
        grounded, observability = generate_and_ground_semantic_properties(
            "protocol context for a fee-charging vault", manifest, client, slither=slither,
        )
        check("e2e: exactly one property grounded", len(grounded) == 1, grounded)
        check("e2e: nothing rejected at generation", observability["rejected_generation"] == [], observability)
        check("e2e: nothing rejected at grounding", observability["rejected_grounding"] == [], observability)
        prop = grounded[0]
        check("e2e: source_kind=code_semantics (not a structural predicate)", prop.source_kind == "code_semantics")
        check("e2e: property references totalAssets", "totalAssets" in prop.property_text, prop.property_text)
        check("e2e: property references accruedFees", "accruedFees" in prop.property_text, prop.property_text)
        check("e2e: relevant_state_variables includes both accounting fields",
              {"totalAssetsHeld", "accruedFees"} <= set(prop.relevant_state_variables), prop.relevant_state_variables)
        check("e2e: property carries NO verdict -- generation ≠ finding",
              not any(k in prop.property_text.lower() for k in ("vulnerable", "confirmed", "exploit")), prop.property_text)
    finally:
        tmp.cleanup()


def test_build_full_property_pool_merges_structural_and_semantic():
    tmp, repo, slither = _compile_vault()
    try:
        manifest = ProjectManifest.from_slither(slither)
        client = FakeChatClient({"properties": [_TOTAL_ASSETS_FEE_PROPERTY_ENTRY]})
        structural = [PropertyMetadata(
            property_id="req-1-no-assembly::loc0", requirement_id="req-1-no-assembly",
            requirement_level="S", requirement_semantic_intent="No Assembly",
            property_text="Tested Code MUST NOT use assembly.", target_contract="Vault", target_function="deposit",
            location="Vault.deposit",
        )]
        merged, observability = build_full_property_pool(structural, "ctx", manifest, client, slither=slither)
        check("pool: structural property present", any(p.source_kind != "code_semantics" for p in merged), merged)
        check("pool: semantic property present", any(p.source_kind == "code_semantics" for p in merged), merged)
        check("pool: observability reports counts", observability["structural_count"] == 1 and observability["semantic_grounded_count"] == 1, observability)
    finally:
        tmp.cleanup()


def test_semantic_property_clusters_with_related_structural_property_via_shared_state():
    """Section 17-F: a semantic property should cluster with an unrelated-
    looking structural property IF they genuinely share state -- here,
    both target Vault and both touch `accruedFees`."""
    tmp, repo, slither = _compile_vault()
    try:
        manifest = ProjectManifest.from_slither(slither)
        client = FakeChatClient({"properties": [_TOTAL_ASSETS_FEE_PROPERTY_ENTRY]})
        grounded, _obs = generate_and_ground_semantic_properties("ctx", manifest, client, slither=slither)
        semantic_prop = grounded[0]

        related_structural = PropertyMetadata(
            property_id="req-2-check-rounding::loc0", requirement_id="req-2-check-rounding",
            requirement_level="M", requirement_semantic_intent="Ensure Proper Rounding",
            property_text="Tested code MUST NOT unintentionally lose value.",
            target_contract="Vault", target_function="withdrawFees", location="Vault.withdrawFees",
            relevant_state_variables=("accruedFees",),
        )
        unrelated_structural = PropertyMetadata(
            property_id="req-1-no-tx.origin::loc0", requirement_id="req-1-no-tx.origin",
            requirement_level="S", requirement_semantic_intent="No tx.origin",
            property_text="Tested Code MUST NOT use tx.origin for authorization.",
            target_contract="SomeOtherContract", target_function="someFunction", location="SomeOtherContract.someFunction",
        )
        clusters = cluster_properties([semantic_prop, related_structural, unrelated_structural])
        by_member = {frozenset(c.property_ids): c for c in clusters}
        same_cluster = any(
            {semantic_prop.property_id, related_structural.property_id} <= set(ids) for ids in by_member
        )
        different_cluster = not any(
            {semantic_prop.property_id, unrelated_structural.property_id} <= set(ids) for ids in by_member
        )
        check("grouping: semantic property clusters with the state-sharing structural property", same_cluster, clusters)
        check("grouping: semantic property does NOT cluster with the unrelated structural property", different_cluster, clusters)
    finally:
        tmp.cleanup()


def test_write_observability_artifacts_writes_all_sections():
    tmp, repo, slither = _compile_vault()
    try:
        manifest = ProjectManifest.from_slither(slither)
        client = FakeChatClient({"properties": [_TOTAL_ASSETS_FEE_PROPERTY_ENTRY]})
        grounded, observability = generate_and_ground_semantic_properties("ctx", manifest, client, slither=slither)
        clusters = apply_grouping_policy(grounded, GROUPING_POLICY_G2_CONTEXT_AWARE)

        with tempfile.TemporaryDirectory() as out_tmp:
            root = Path(out_tmp)
            written = write_observability_artifacts(
                root, "test-audit",
                applicable_standards=[{"standard_id": "ERC-4626", "applicable": "APPLICABLE"}],
                structural_properties=[],
                semantic_pipeline_observability=observability,
                semantic_properties_grounded=grounded,
                property_clusters=[c.as_dict() for c in clusters],
            )
            check("observability: all 5 sections written", set(written.keys()) == {
                "applicable_standards", "structural_properties", "semantic_properties_raw",
                "rejected_properties", "semantic_properties_grounded", "property_clusters",
            }, written)
            for name, rel_path in written.items():
                full = root / rel_path
                check(f"observability: {name} is valid JSON on disk", json.loads(full.read_text()) is not None, full)
            grounded_json = json.loads((root / written["semantic_properties_grounded"]).read_text())
            check("observability: grounded JSON contains the fee-accounting property's text",
                  any("accruedFees" in p["property_text"] for p in grounded_json), grounded_json)
    finally:
        tmp.cleanup()


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
