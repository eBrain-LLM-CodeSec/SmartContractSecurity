"""Builds G0/G1/G2/G3 graph-derived file sets for all 7 bundles and saves
them to phase_graph_relevance_artifacts/graph_file_sets.json. See
PROGRAM_GRAPH_RELEVANCE_BOUNDARY_EXPERIMENT.md.

Depends on ephemeral, job-scratch paths not present in this repo checkout:
  - PT_REMAPS: solc remaps for the PoolTogether checkout (see
    evmbench/CLAUDE.md's existing reproduction steps for how that checkout
    and its remaps were derived).
  - solc_819/solc_817: this experiment ran on a login node with no bare
    `solc` on PATH; each was a symlink to a solc-select-managed binary
    (`~/.solc-select/artifacts/solc-<version>/solc-<version>`) named
    literally `solc` in its own directory, prepended to PATH per bundle
    (synthetic fixtures need ^0.8.19; PoolTogether's foundry.toml pins
    0.8.17). Regenerate equivalently wherever this is rerun.
No live LLM calls -- this script only builds Slither/networkx graphs.
"""
import sys
REPO_ROOT = "/scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2"
sys.path.insert(0, REPO_ROOT)

import json
import os
from pathlib import Path

from a4v.graph import ProgramGraph
from rtf.l8_llm_judgment_layer.bundle_agent_experiment.graph_relevance import build_g0_g1_g2, build_g3_adaptive

FIXTURES = Path(REPO_ROOT) / "rtf/l8_llm_judgment_layer/bundle_agent_experiment/fixtures"
PT_REMAPS = [l.strip() for l in open("/scratch/md5344/.claude/jobs/318205ae/tmp/all_remaps.txt") if l.strip()]

BUNDLES = [
    dict(case_id="unsafe_narrowing_cast", entry=FIXTURES / "unsafe_narrowing_cast/Ledger.sol",
         candidate="Ledger.record", unresolved=[]),
    dict(case_id="safe_narrowing_cast", entry=FIXTURES / "safe_narrowing_cast/Ledger.sol",
         candidate="Ledger.record", unresolved=[]),
    dict(case_id="unchecked_ecrecover_mutable_signer", entry=FIXTURES / "unchecked_ecrecover_mutable_signer/AuthAdmin.sol",
         candidate="Auth.verify", unresolved=["Can authorizedSigner be, or become, the zero address anywhere in this repository?"]),
    dict(case_id="checked_ecrecover", entry=FIXTURES / "checked_ecrecover/Auth.sol",
         candidate="Auth.verify", unresolved=[]),
    dict(case_id="corrected_ecrecover_fixed_signer", entry=FIXTURES / "corrected_ecrecover_fixed_signer/Auth.sol",
         candidate="Auth.verify", unresolved=["Can authorizedSigner be, or become, the zero address anywhere in this repository?"]),
    dict(case_id="insufficient_evidence_timestamp", entry=FIXTURES / "insufficient_evidence_timestamp/RewardStream.sol",
         candidate="RewardStream.updateReward",
         unresolved=["What is the deployed/expected magnitude of rewardRatePerSecond relative to the protocol's total value"]),
    dict(case_id="pooltogether_vault_burn",
         entry=Path("/scratch/md5344/.claude/jobs/318205ae/tmp/pooltogether_src/vault/src/Vault.sol"),
         candidate="Vault._burn",
         unresolved=["Is _shares ever bound-checked to <= type(uint96).max before this cast -- earlier in _burn, in any caller, or via a prior mint that already enforced the same bound?"],
         remaps=PT_REMAPS),
]

REPO_ROOT_FOR_REDUCTION = {
    "unsafe_narrowing_cast": FIXTURES / "unsafe_narrowing_cast",
    "safe_narrowing_cast": FIXTURES / "safe_narrowing_cast",
    "unchecked_ecrecover_mutable_signer": FIXTURES / "unchecked_ecrecover_mutable_signer",
    "checked_ecrecover": FIXTURES / "checked_ecrecover",
    "corrected_ecrecover_fixed_signer": FIXTURES / "corrected_ecrecover_fixed_signer",
    "insufficient_evidence_timestamp": FIXTURES / "insufficient_evidence_timestamp",
    "pooltogether_vault_burn": Path("/scratch/md5344/.claude/jobs/318205ae/tmp/pooltogether_src/vault"),
}


def rel(root: Path, p: str) -> str:
    try:
        return str(Path(p).relative_to(root.resolve()))
    except ValueError:
        return p


def main():
    results = {}
    solc_819 = "/scratch/md5344/.claude/jobs/318205ae/tmp/solc_bin"
    solc_817 = "/scratch/md5344/.claude/jobs/318205ae/tmp/solc_bin_0817"
    base_path = os.environ.get("PATH", "")
    for b in BUNDLES:
        print(f"=== building graph for {b['case_id']} ===", file=sys.stderr)
        solc_dir = solc_817 if b["case_id"] == "pooltogether_vault_burn" else solc_819
        os.environ["PATH"] = f"{solc_dir}:{base_path}"
        pg = ProgramGraph.build(b["entry"], solc_remaps=b.get("remaps"))
        sets = build_g0_g1_g2(pg, b["candidate"])
        g3, steps = build_g3_adaptive(pg, b["candidate"], b["unresolved"])

        root = REPO_ROOT_FOR_REDUCTION[b["case_id"]]
        all_sol_files = list(root.resolve().rglob("*.sol"))
        # Repository-reduction denominator: ALL .sol files under repo_root,
        # including lib/ and test/ -- matches exactly the real accessible
        # surface an unrestricted Codex run could reach from this same
        # repo_root (confirmed: Arm C's unrestricted PoolTogether run did
        # read into lib/pt-v5-prize-pool/...). An earlier version of this
        # script excluded "vendored" paths from the denominator, reusing
        # evidence_ranking.py's _VENDORED_PATH_SEGMENTS convention -- that
        # was a category error (that convention exists to filter STATIC-
        # ANALYSIS-EVIDENCE noise, not to define "the accessible repo
        # surface") and produced a nonsensical result (G2's file count
        # exceeded the "countable" denominator). Fixed here, not silently
        # left in.
        results[b["case_id"]] = {
            "candidate": b["candidate"],
            "seed_node": sets.seed_node,
            "g0": sorted(rel(root, p) for p in sets.g0),
            "g1": sorted(rel(root, p) for p in sets.g1),
            "g2": sorted(rel(root, p) for p in sets.g2),
            "g3": sorted(rel(root, p) for p in g3),
            "g3_expansion_steps": [vars(s) for s in steps],
            "graph_nodes": pg.graph.number_of_nodes(),
            "graph_edges": pg.graph.number_of_edges(),
            "all_sol_files_total": len(all_sol_files),
        }
        print(f"  G0={len(sets.g0)} G1={len(sets.g1)} G2={len(sets.g2)} G3={len(g3)} "
              f"of {len(all_sol_files)} total .sol files", file=sys.stderr)

    out_path = Path(REPO_ROOT) / "rtf/l8_llm_judgment_layer/phase_graph_relevance_artifacts/graph_file_sets.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"saved to {out_path}")


if __name__ == "__main__":
    main()
