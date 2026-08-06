import sys
sys.path.insert(0, "/scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2")

from pathlib import Path
import json

from a4v.llm import ChatClient
from rtf.l8_llm_judgment_layer.judgment_layer import LLMJudgmentLayer
from rtf.l12_evaluation.judge_with_l8 import judge_result
from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState, EvidenceItem, RoutedRequirementResult
from rtf.l12_evaluation.failure_taxonomy import OperationalStatus

API_KEY_FILE = Path("/scratch/md5344/evmbench/run/task5_secrets/openrouter.key")
CACHE_DIR = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/l8_cache")

chat_client = ChatClient(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY_FILE.read_text().strip(),
    model="openai/gpt-5.1-codex-max",
    cache_dir=CACHE_DIR,
    token_log_path=CACHE_DIR / "tokens.jsonl",
)
layer = LLMJudgmentLayer(chat_client=chat_client, model_version="openai/gpt-5.1-codex-max")

cases = {
    "CLEAR": (
        "req-3-access-control",
        RoutedRequirementResult(
            req_id="req-3-access-control",
            applicability_state=ApplicabilityState.APPLICABLE,
            operational_status=OperationalStatus.OK,
            conformance_state=None,
            evidence=(EvidenceItem(
                predicate="find_state_mutating_function_protection_status",
                location="Vault.mintYieldFee",
                detail="state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here",
            ),),
        ),
        "expected: FAIL (this is the real EVMbench H-04 vulnerability -- unprotected privileged function)",
    ),
    "BORDERLINE": (
        "req-2-avoid-readonly-reentrancy",
        RoutedRequirementResult(
            req_id="req-2-avoid-readonly-reentrancy",
            applicability_state=ApplicabilityState.APPLICABLE,
            operational_status=OperationalStatus.OK,
            conformance_state=None,
            evidence=(EvidenceItem(
                predicate="find_readonly_reentrancy_candidates",
                location="LiquidationPair.maxAmountIn",
                detail="view/pure function reads state variable(s) ['virtualReserveIn', 'virtualReserveOut'], which can be written AFTER an external call elsewhere in this contract (functions with the post-call write: ['swapExactAmountIn', 'swapExactAmountOut']) -- candidate read-only reentrancy, structural precondition only",
            ),),
        ),
        "expected: genuinely uncertain -- INCONCLUSIVE or a well-reasoned PASS/FAIL with explicit caveats, not a confident snap judgment",
    ),
    "INSUFFICIENT_EVIDENCE": (
        "req-2-block-data-misuse",
        RoutedRequirementResult(
            req_id="req-2-block-data-misuse",
            applicability_state=ApplicabilityState.APPLICABLE,
            operational_status=OperationalStatus.OK,
            conformance_state=None,
            evidence=(EvidenceItem(
                predicate="find_block_data_usage",
                location="ERC20Permit.permit",
                detail="reads block.timestamp",
            ),),
        ),
        "expected: INSUFFICIENT_EVIDENCE -- the evidence alone (bare 'reads block.timestamp') doesn't show HOW it's used (deadline check vs. randomness vs. critical branch)",
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
    else:
        print("RAW:", json.dumps(raw, indent=2)[:1000] if raw else None)
    print()
    results[case_name] = {"req_id": req_id, "decision": updated.conformance_state.value if updated.conformance_state else None, "raw": raw}

with open("/scratch/md5344/.claude/jobs/318205ae/tmp/l8_three_cases_result.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("Saved.")
