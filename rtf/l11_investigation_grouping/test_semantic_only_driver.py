"""Wiring test for rtf.l11_investigation_grouping.semantic_only_driver.
Zero real LLM/Codex calls -- fake chat_client + a mocked
run_arm_g_bundle_fn, same "mock-tested first" convention as
test_live_runner.py. Verifies the full generation -> grounding ->
clustering -> (mocked) investigation -> verdict-resolution wiring is
correct BEFORE any live run. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_only_driver
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l11_investigation_grouping.semantic_only_driver import run_semantic_investigation
from rtf.l12_evaluation.metrics import ConformanceState
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


_VAULT_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Vault {
    uint256 public totalAssetsHeld;
    uint256 public accruedFees;

    function deposit(uint256 amount) external { totalAssetsHeld += amount; }
    function accrueFee(uint256 amount) external { accruedFees += amount; }
    function totalAssets() external view returns (uint256) { return totalAssetsHeld; }
}
"""

_ONE_PROPERTY_ENTRY = {
    "statement": "Vault.totalAssets must not include amounts already owed via Vault.accruedFees.",
    "property_type": "accounting",
    "rationale": "Accrued fees are no longer shareholder-backed assets.",
    "affected_contracts": ["Vault"],
    "affected_functions": ["Vault.totalAssets"],
    "affected_state_variables": ["Vault.totalAssetsHeld", "Vault.accruedFees"],
    "source_refs": ["synthetic-fixture"],
    "confidence": 0.8,
}


class FakeArmGResult:
    def __init__(self, final_decision, cost_usd=0.01):
        self.final_decision = final_decision
        self.cost_usd = cost_usd


def _fake_run_arm_g_bundle(*, case_id, **kwargs):
    # Echo back a FAIL for every property in this cluster -- proves the
    # driver's own property_id set (not a hardcoded guess) drives the
    # response shape, and that verdicts round-trip end to end.
    prompt = kwargs.get("prompt", "")
    return FakeArmGResult(final_decision={
        "properties": [
            {
                "property_id": "semantic__accounting__PLACEHOLDER",
                "verdict": "FAIL",
                "evidence": "totalAssets() returns totalAssetsHeld without subtracting accruedFees.",
                "files_read": ["Vault.sol"],
                "counterexample_attempt": "accrueFee(100) then totalAssets() still returns full totalAssetsHeld.",
                "counterexample_result": "confirmed: accruedFees is never subtracted.",
                "reasoning": "Direct code read.",
                "vulnerable_location": "Vault.totalAssets",
                "confidence": "HIGH",
            }
        ]
    })


def test_driver_wires_generation_through_to_a_mocked_investigation():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "Vault.sol").write_text(_VAULT_SOURCE, encoding="utf-8")
        client = FakeChatClient({"properties": [_ONE_PROPERTY_ENTRY]})

        # The driver assigns a real, content-derived property_id we can't
        # predict in advance -- capture it via a closure so the fake
        # investigation function can echo the CORRECT id, exactly like a
        # real Codex response naming the property_id it was actually given.
        captured = {}

        def _run_arm_g_bundle_fn(*, case_id, prompt, extra_files, candidate_location, **kwargs):
            import re
            haystack = "\n".join(extra_files.values())
            m = re.search(r"`(semantic__[a-z_]+__[0-9a-f]+::loc0)`", haystack)
            pid = m.group(1) if m else None
            captured["property_id"] = pid
            return FakeArmGResult(final_decision={"properties": [{
                "property_id": pid, "verdict": "FAIL",
                "evidence": "totalAssets() never subtracts accruedFees.",
                "files_read": ["Vault.sol"], "counterexample_attempt": "accrueFee then totalAssets",
                "counterexample_result": "confirmed", "reasoning": "direct read",
                "vulnerable_location": "Vault.totalAssets", "confidence": "HIGH",
            }]})

        with tempfile.TemporaryDirectory() as scratch:
            result = run_semantic_investigation(
                audit_id="wiring-test", repo_root=repo, entry_sol_file=repo / "Vault.sol",
                solc_version="0.8.20", chat_client=client,
                codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
                mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
                scratch_root=Path(scratch), run_arm_g_bundle_fn=_run_arm_g_bundle_fn,
            )

        check("driver: exactly one cluster formed", len(result["clusters"]) == 1, result["clusters"])
        check("driver: exactly one property in the pool", len(result["properties_by_id"]) == 1, result["properties_by_id"])
        pid = captured["property_id"]
        check("driver: mocked investigation received the real property_id", pid is not None, captured)
        check("driver: property_verdicts resolved to FAIL",
              result["property_verdicts"][pid].conformance_state == ConformanceState.FAIL,
              result["property_verdicts"])
        check("driver: total_cost_usd reflects the mocked call's cost", result["total_cost_usd"] == 0.01, result["total_cost_usd"])
        check("driver: raw_property_entries_by_id carries the investigator's own evidence text",
              "accruedFees" in result["raw_property_entries_by_id"][pid]["evidence"], result["raw_property_entries_by_id"])
        check("driver: semantic_observability recorded zero rejections",
              result["semantic_observability"]["rejected_generation"] == [] and
              result["semantic_observability"]["rejected_grounding"] == [], result["semantic_observability"])


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
