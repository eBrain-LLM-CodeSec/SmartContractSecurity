"""Unit tests for rtf.l11_investigation_grouping.semantic_property_generation.
Zero real LLM calls -- a fake chat_client injects canned responses, same
"mock-tested only" convention as test_live_runner.py's `run_arm_g_bundle_fn`
injection. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_property_generation
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.semantic_property_generation import (
    GenerationRejection, ProjectManifest, RawSemanticProperty, build_prompt_messages,
    generate_semantic_properties, raw_property_to_dict, rejection_to_dict,
)

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
        self.calls: list[tuple[list[dict], float]] = []

    def complete_json(self, messages, temperature=0.0, **kwargs):
        self.calls.append((messages, temperature))
        return self.response, None


_MANIFEST = ProjectManifest(
    contracts=("Vault", "FeeManager"),
    functions=("Vault.totalAssets", "Vault.deposit", "FeeManager.accrue"),
    state_variables=("Vault.totalAssets_", "FeeManager.accruedFees"),
)

_GOOD_ENTRY = {
    "statement": "Vault.totalAssets must not include FeeManager.accruedFees already owed to fee recipients.",
    "property_type": "accounting",
    "rationale": "ERC-4626 totalAssets should reflect assets economically owned by shareholders.",
    "affected_contracts": ["Vault", "FeeManager"],
    "affected_functions": ["Vault.totalAssets"],
    "affected_state_variables": ["FeeManager.accruedFees"],
    "source_refs": ["gp-accepted-standard__erc-4626__erc4626-totalassets-must-include-fees"],
    "confidence": 0.7,
}


def test_generate_accepts_a_well_formed_entry():
    client = FakeChatClient({"properties": [_GOOD_ENTRY]})
    accepted, rejected = generate_semantic_properties("protocol context md", _MANIFEST, client)
    check("generate: one accepted", len(accepted) == 1, accepted)
    check("generate: zero rejected", rejected == [], rejected)
    check("generate: statement round-trips", accepted[0].statement == _GOOD_ENTRY["statement"])
    check("generate: property_type round-trips", accepted[0].property_type == "accounting")
    check("generate: confidence round-trips", accepted[0].confidence == 0.7)


def test_generate_rejects_missing_required_keys():
    bad = {"property_type": "accounting", "rationale": "x"}  # missing "statement"
    client = FakeChatClient({"properties": [bad]})
    accepted, rejected = generate_semantic_properties("ctx", _MANIFEST, client)
    check("generate: nothing accepted", accepted == [])
    check("generate: one rejection", len(rejected) == 1, rejected)
    check("generate: rejection names the missing key", "missing_required_keys" in rejected[0].reason, rejected[0].reason)


def test_generate_rejects_verdict_shaped_entries():
    bad = dict(_GOOD_ENTRY)
    bad["verdict"] = "FAIL"
    client = FakeChatClient({"properties": [bad]})
    accepted, rejected = generate_semantic_properties("ctx", _MANIFEST, client)
    check("generate: verdict-shaped entry never accepted even if otherwise well-formed", accepted == [], accepted)
    check("generate: rejection reason names the verdict discipline violation",
          len(rejected) == 1 and "verdict_shaped_response_rejected" in rejected[0].reason, rejected)


def test_generate_rejects_other_verdict_shaped_keys():
    for key, value in (("vulnerable", True), ("pass", True), ("severity", "HIGH"), ("exploit", "reentrancy")):
        bad = dict(_GOOD_ENTRY)
        bad[key] = value
        client = FakeChatClient({"properties": [bad]})
        accepted, rejected = generate_semantic_properties("ctx", _MANIFEST, client)
        check(f"generate: '{key}' key alone triggers rejection", accepted == [] and len(rejected) == 1, (key, accepted, rejected))


def test_generate_rejects_invalid_property_type():
    bad = dict(_GOOD_ENTRY)
    bad["property_type"] = "made_up_category"
    client = FakeChatClient({"properties": [bad]})
    accepted, rejected = generate_semantic_properties("ctx", _MANIFEST, client)
    check("generate: invalid property_type rejected", accepted == [] and "invalid_property_type" in rejected[0].reason, rejected)


def test_generate_handles_missing_properties_list():
    client = FakeChatClient({"not_properties": []})
    accepted, rejected = generate_semantic_properties("ctx", _MANIFEST, client)
    check("generate: no crash on malformed top-level response", accepted == [])
    check("generate: rejection recorded, not silently swallowed",
          len(rejected) == 1 and rejected[0].reason == "response_missing_properties_list", rejected)


def test_generate_clamps_out_of_range_confidence():
    entry = dict(_GOOD_ENTRY)
    entry["confidence"] = 1.7
    client = FakeChatClient({"properties": [entry]})
    accepted, _rejected = generate_semantic_properties("ctx", _MANIFEST, client)
    check("generate: confidence clamped to [0,1]", accepted[0].confidence == 1.0, accepted[0].confidence)


def test_generate_rejects_non_numeric_confidence():
    entry = dict(_GOOD_ENTRY)
    entry["confidence"] = "high"
    client = FakeChatClient({"properties": [entry]})
    accepted, rejected = generate_semantic_properties("ctx", _MANIFEST, client)
    check("generate: non-numeric confidence rejected", accepted == [] and "confidence_not_numeric" in rejected[0].reason, rejected)


def test_generate_truncates_to_max_properties():
    entries = [dict(_GOOD_ENTRY, statement=f"statement {i} names Vault.totalAssets") for i in range(5)]
    client = FakeChatClient({"properties": entries})
    accepted, _rejected = generate_semantic_properties("ctx", _MANIFEST, client, max_properties=2)
    check("generate: truncated to max_properties", len(accepted) == 2, len(accepted))


def test_prompt_forbids_verdict_language():
    messages = build_prompt_messages("some protocol context", _MANIFEST)
    system = messages[0]["content"]
    check("prompt: instructs proposing properties, not finding vulnerabilities",
          "propose" in system.lower() and "must never" in system.lower(), system[:200])
    check("prompt: explicitly forbids verdict words", "PASS" in system and "vulnerable" in system.lower(), system)
    check("prompt: lists the controlled property_type vocabulary", "accounting" in system and "token_semantics" in system, system)
    check("prompt: includes the banned generic examples as counter-examples",
          "should not lose money" in system.lower(), system)


def test_prompt_includes_manifest_facts():
    messages = build_prompt_messages("ctx", _MANIFEST)
    user = messages[1]["content"]
    check("prompt: manifest contracts present", "Vault" in user and "FeeManager" in user, user)
    check("prompt: manifest functions present", "Vault.totalAssets" in user, user)


def test_manifest_from_slither_real_compile():
    import tempfile
    from pathlib import Path

    from rtf.l5_predicates.compile_helper import compile_evmbench_target

    source = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Vault {
    uint256 public totalAssets_;
    function totalAssets() external view returns (uint256) { return totalAssets_; }
    function deposit(uint256 amount) external { totalAssets_ += amount; }
}
"""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "Vault.sol").write_text(source, encoding="utf-8")
        slither = compile_evmbench_target(repo / "Vault.sol", repo, solc_version="0.8.20")
        manifest = ProjectManifest.from_slither(slither)
        check("manifest: Vault contract found", "Vault" in manifest.contracts, manifest.contracts)
        check("manifest: functions qualified as Contract.function",
              "Vault.totalAssets" in manifest.functions and "Vault.deposit" in manifest.functions, manifest.functions)
        check("manifest: state variable qualified", "Vault.totalAssets_" in manifest.state_variables, manifest.state_variables)


def test_raw_property_to_dict_round_trips_and_rejection_to_dict_is_json_safe():
    import json

    raw = RawSemanticProperty(
        statement="s", property_type="accounting", rationale="r",
        affected_contracts=("Vault",), affected_functions=(), affected_state_variables=(),
        source_refs=(), confidence=0.5,
    )
    d = raw_property_to_dict(raw)
    check("raw_property_to_dict: JSON-serializable", json.dumps(d) is not None)
    check("raw_property_to_dict: fields present", d["statement"] == "s" and d["property_type"] == "accounting", d)

    rej = GenerationRejection(raw_entry={"statement": "x"}, reason="missing_required_keys:['rationale']")
    rd = rejection_to_dict(rej)
    check("rejection_to_dict: JSON-serializable", json.dumps(rd) is not None, rd)


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
