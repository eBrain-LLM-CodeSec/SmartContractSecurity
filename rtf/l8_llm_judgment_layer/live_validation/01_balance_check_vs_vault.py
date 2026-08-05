"""One-off live validation of L8's LLM Judgment Layer, run manually (not part
of the rtf/ package) against a real target: PoolTogether's Vault.sol.

Scope deliberately kept small (n_runs=5, one component) to control cost for
this first live-execution check, per the go/no-go criteria this exists to
fill in (evidence-citation validity, LLM decision-flip rate) -- not a full
Track A evaluation sweep.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2")

from a4v.llm import ChatClient
from rtf.l8_llm_judgment_layer.judgment_layer import LLMJudgmentLayer

REPO_ROOT = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/pooltogether_src")
CONTEXT_BUNDLE_PATH = Path(
    "/scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2/"
    "rtf/track_a/context_bundles/req-2-verify-exact-balance-check.json"
)
CACHE_DIR = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/l8_live_cache")
API_KEY_FILE = Path("/scratch/md5344/evmbench/run/task5_secrets/openrouter.key")

VAULT_SOL_PATH = "vault/src/Vault.sol"


def build_question(source_text: str) -> str:
    return (
        "Below is the full real source of vault/src/Vault.sol (a real ERC4626-based vault contract), "
        "with line numbers prefixed. Does this contract contain any exact-equality (`==`) comparison "
        "against a balance (e.g. `address(this).balance == x`, or a token/share balance compared for "
        "exact equality to a specified amount or variable)? If so, cite the exact line number, and assess "
        "whether the code protects against transfers affecting the balance between the check and its use "
        "(e.g. via checks-effects-interactions ordering, a reentrancy guard, or atomic balance "
        "snapshotting). If no such exact-balance-equality check exists anywhere in the file, say so "
        "explicitly -- do not force a PASS/FAIL if the requirement simply does not apply.\n\n"
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

    print(f"Running judge_stability(n_runs=5) against {REPO_ROOT} ({len(lines)} lines of real source embedded in prompt)...")
    result = layer.judge_stability(bundle_record, question, n_runs=5, repo_root=REPO_ROOT)

    out_path = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/l8_live_result.json")
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n=== STABILITY ===")
    print(json.dumps(result["stability"], indent=2))

    print("\n=== CITATION VALIDITY PER RUN ===")
    for i, run in enumerate(result["runs"]):
        cc = run.get("citation_check")
        print(f"run {i}: decision={run['decision']} confidence={run['confidence']} "
              f"citation_check={cc['valid']}/{cc['total']} valid" if cc else f"run {i}: decision={run['decision']} (no evidence to check)")

    print(f"\nFull output written to {out_path}")


if __name__ == "__main__":
    main()
