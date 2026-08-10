"""Unit tests for rtf.l12_evaluation.simple_baseline's pure rendering
logic (no live Codex calls). Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_simple_baseline
"""
from __future__ import annotations

import sys

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_c_codex import ArmCResult
from rtf.l12_evaluation.simple_baseline import render_baseline_audit_md

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _fake_result(final_decision, reasoning_text="") -> ArmCResult:
    return ArmCResult(
        case_id="test", repetition=1, final_decision=final_decision, reasoning_text=reasoning_text,
        actual_tool_calls=0, actual_commands=[], actual_files_touched=[], repository_commit=None,
        input_tokens=0, cached_input_tokens=0, output_tokens=0, cost_usd=0.0, wall_clock_s=0.0,
        timed_out=False, session_log_path="", protocol_violation=None, citation_provenance_failures=[],
    )


def test_renders_well_formed_vulnerabilities_json():
    payload = {
        "vulnerabilities": [
            {
                "title": "Reentrancy in withdraw",
                "severity": "high",
                "summary": "Withdraw sends ETH before updating balance.",
                "description": [{"file": "src/Vault.sol", "line_start": 10, "line_end": 20, "desc": "External call precedes state update."}],
                "impact": "Attacker can drain the vault.",
                "proof_of_concept": "Call withdraw() from a malicious fallback.",
                "remediation": "Use checks-effects-interactions.",
            }
        ]
    }
    md = render_baseline_audit_md(_fake_result(payload), audit_title="test-audit")
    check("renders title", "test-audit" in md)
    check("renders vulnerability title", "Reentrancy in withdraw" in md)
    check("renders severity", "high" in md)
    check("renders location", "src/Vault.sol:10-20" in md)
    check("renders impact", "drain the vault" in md)
    check("renders remediation", "checks-effects-interactions" in md)


def test_renders_empty_vulnerabilities_list():
    md = render_baseline_audit_md(_fake_result({"vulnerabilities": []}), audit_title="clean-audit")
    check("empty list: reports no vulnerabilities", "No vulnerabilities were reported" in md, md)


def test_falls_back_to_raw_text_when_no_valid_json():
    md = render_baseline_audit_md(_fake_result(None, reasoning_text="I found nothing conclusive."), audit_title="fallback-audit")
    check("fallback: raw reasoning text preserved", "I found nothing conclusive." in md, md)
    check("fallback: explains the schema mismatch rather than silently hiding it", "did not return the expected" in md, md)


def test_falls_back_when_json_present_but_missing_vulnerabilities_key():
    md = render_baseline_audit_md(_fake_result({"something_else": []}, reasoning_text="raw text here"), audit_title="fallback-audit-2")
    check("fallback: missing vulnerabilities key still falls back to raw text, not a crash", "raw text here" in md, md)


def main() -> int:
    tests = [
        test_renders_well_formed_vulnerabilities_json,
        test_renders_empty_vulnerabilities_list,
        test_falls_back_to_raw_text_when_no_valid_json,
        test_falls_back_when_json_present_but_missing_vulnerabilities_key,
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
