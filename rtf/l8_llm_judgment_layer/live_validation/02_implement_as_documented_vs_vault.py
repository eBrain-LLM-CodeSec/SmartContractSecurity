"""Second live L8 validation run -- req-3-implement-as-documented against
Vault.sol, chosen specifically because it's much more likely to produce
real evidence citations than the first run (which correctly found no
exact-balance-check pattern at all, so had nothing to cite)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2")

from a4v.llm import ChatClient
from rtf.l8_llm_judgment_layer.judgment_layer import LLMJudgmentLayer

REPO_ROOT = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/pooltogether_src")
CONTEXT_BUNDLE_PATH = Path(
    "/scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2/"
    "rtf/track_a/context_bundles/req-3-implement-as-documented.json"
)
CACHE_DIR = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/l8_live_cache")
API_KEY_FILE = Path("/scratch/md5344/evmbench/run/task5_secrets/openrouter.key")
VAULT_SOL_PATH = "vault/src/Vault.sol"


def build_question(source_text: str) -> str:
    return (
        "Below is the full real source of vault/src/Vault.sol, with line numbers prefixed. "
        "The contract declares (via NatSpec @notice comments) several documented error conditions, "
        "including: 'Emitted when the yield fee percentage being set is greater than 1' and "
        "'Emitted when the vault is under-collateralized'. For EACH of these two specific documented "
        "claims, find the actual function that is supposed to enforce it, cite its exact line number, "
        "and assess whether the code's real behavior matches what the NatSpec comment documents. "
        "If you cannot find where the check is actually implemented, say so explicitly as "
        "INSUFFICIENT_EVIDENCE rather than guessing.\n\n"
        "--- vault/src/Vault.sol ---\n" + source_text
    )


def main():
    chat_client = ChatClient(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY_FILE.read_text().strip(),
        model="openai/gpt-5.1-codex-max",
        cache_dir=CACHE_DIR,
        token_log_path=CACHE_DIR / "tokens.jsonl",
    )
    layer = LLMJudgmentLayer(chat_client=chat_client, model_version="openai/gpt-5.1-codex-max")
    bundle_record = json.loads(CONTEXT_BUNDLE_PATH.read_text())

    vault_sol = REPO_ROOT / VAULT_SOL_PATH
    lines = vault_sol.read_text(encoding="utf-8", errors="replace").splitlines()
    numbered_source = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))
    question = build_question(numbered_source)

    print(f"Running judge_stability(n_runs=5) against {REPO_ROOT} ({len(lines)} lines embedded)...")
    result = layer.judge_stability(bundle_record, question, n_runs=5, repo_root=REPO_ROOT)

    out_path = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/l8_live_result2.json")
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n=== STABILITY ===")
    print(json.dumps(result["stability"], indent=2))

    print("\n=== CITATION VALIDITY PER RUN ===")
    total_valid, total_evidence = 0, 0
    for i, run in enumerate(result["runs"]):
        cc = run.get("citation_check")
        if cc:
            print(f"run {i}: decision={run['decision']} confidence={run['confidence']} citations {cc['valid']}/{cc['total']} valid")
            total_valid += cc["valid"]
            total_evidence += cc["total"]
        else:
            print(f"run {i}: decision={run['decision']} (no evidence)")
    print(f"\nAGGREGATE citation validity: {total_valid}/{total_evidence}" if total_evidence else "\nNo evidence emitted across any run")
    print(f"Full output written to {out_path}")


if __name__ == "__main__":
    main()
