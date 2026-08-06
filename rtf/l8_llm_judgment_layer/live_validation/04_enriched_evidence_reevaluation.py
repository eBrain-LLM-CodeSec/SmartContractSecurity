import sys
sys.path.insert(0, "/scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2")

from pathlib import Path
import json

from a4v.llm import ChatClient
from rtf.l8_llm_judgment_layer.judgment_layer import LLMJudgmentLayer
from rtf.l12_evaluation.judge_with_l8 import judge_result
from rtf.l12_evaluation.metrics import ApplicabilityState, EvidenceItem, RoutedRequirementResult
from rtf.l12_evaluation.failure_taxonomy import OperationalStatus

API_KEY_FILE = Path("/scratch/md5344/evmbench/run/task5_secrets/openrouter.key")
CACHE_DIR = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/l8_cache_enriched")

chat_client = ChatClient(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY_FILE.read_text().strip(),
    model="openai/gpt-5.1-codex-max",
    cache_dir=CACHE_DIR,
    token_log_path=CACHE_DIR / "tokens.jsonl",
)
layer = LLMJudgmentLayer(chat_client=chat_client, model_version="openai/gpt-5.1-codex-max")

cases = {
    "CLEAR (Tempo H-03, enriched)": (
        "req-2-signature-verification",
        RoutedRequirementResult(
            req_id="req-2-signature-verification",
            applicability_state=ApplicabilityState.APPLICABLE,
            operational_status=OperationalStatus.OK,
            conformance_state=None,
            evidence=(EvidenceItem(
                predicate="find_unchecked_ecrecover_result",
                location="TempoStreamChannel.settle",
                detail="ecrecover() result (via local wrapper function '_recoverSigner') (assigned to 'signer') is never compared against address(0) anywhere in this function",
                structured={
                    "operation": "ecrecover(...) (via local wrapper function '_recoverSigner')",
                    "input": {"name": "signer", "type": "address"},
                    "possible_result": "address(0) for an invalid/malformed signature (documented Solidity/EVM behavior)",
                    "validation_found": "none",
                    "missing_safety_condition": "signer != address(0)",
                    "risk": "an invalid signature recovers to address(0) and, if address(0) is ever treated as authorized (e.g. an unset/default signer field), an invalid signature would be accepted as authentic",
                    "affected_functions": ["TempoStreamChannel.settle"],
                },
            ),),
        ),
        "expected: FAIL -- this is the real, enriched H-03 evidence naming the exact missing condition",
    ),
    "CLEAR (PoolTogether H-02, enriched)": (
        "req-3-all-valid-inputs",
        RoutedRequirementResult(
            req_id="req-3-all-valid-inputs",
            applicability_state=ApplicabilityState.APPLICABLE,
            operational_status=OperationalStatus.OK,
            conformance_state=None,
            evidence=(EvidenceItem(
                predicate="find_unsafe_narrowing_cast",
                location="Vault._burn",
                detail="unchecked narrowing cast: _shares (uint256) -> uint96, no bound check found",
                structured={
                    "operation": "narrowing type conversion uint256 -> uint96",
                    "input": {"name": "_shares", "type": "uint256"},
                    "source_type": "uint256",
                    "destination_type": "uint96",
                    "validation_found": "none",
                    "missing_safety_condition": "_shares <= type(uint96).max",
                    "risk": "values of _shares above uint96's maximum representable value (79228162514264337593543950335) are silently truncated by this cast rather than rejected",
                    "affected_functions": ["Vault._burn"],
                },
            ),),
        ),
        "expected: FAIL -- this is the real, enriched H-02 evidence naming the exact missing condition",
    ),
    "INSUFFICIENT_EVIDENCE (structural, from the predicate's own UNKNOWN case)": (
        "req-2-signature-verification",
        RoutedRequirementResult(
            req_id="req-2-signature-verification",
            applicability_state=ApplicabilityState.APPLICABLE,
            operational_status=OperationalStatus.OK,
            conformance_state=None,
            evidence=(EvidenceItem(
                predicate="find_unchecked_ecrecover_result",
                location="TempoStreamChannel._recoverSigner",
                detail="ecrecover() result used without an intermediate named variable -- cannot trace whether it is checked",
                structured={
                    "operation": "ecrecover(...)",
                    "possible_result": "address(0) for an invalid/malformed signature",
                    "validation_found": "UNKNOWN -- result not assigned to a traceable named variable",
                    "risk": "cannot be determined by this predicate; requires manual/semantic review",
                },
            ),),
        ),
        "expected: INSUFFICIENT_EVIDENCE -- the predicate itself says UNKNOWN",
    ),
}

results = {}
for case_name, (req_id, result, expectation) in cases.items():
    print(f"=== {case_name} ({req_id}) ===")
    print(f"Expectation: {expectation}")
    updated, raw = judge_result(layer, req_id, result, repo_root=None, use_second_pass=True)
    print(f"L8 decision: {updated.conformance_state}")
    if isinstance(raw, dict) and "first_pass" in raw:
        fp = raw["first_pass"]
        print(f"Confidence: {fp.get('confidence')}")
        print(f"Reasoning: {fp.get('reasoning_summary', '')[:500]}")
        print(f"Second-pass agreement: {raw.get('agree')}")
    print()
    results[case_name] = {"req_id": req_id, "decision": updated.conformance_state.value if updated.conformance_state else None, "raw": raw}

with open("/scratch/md5344/.claude/jobs/318205ae/tmp/l8_enriched_cases_result.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("Saved.")
