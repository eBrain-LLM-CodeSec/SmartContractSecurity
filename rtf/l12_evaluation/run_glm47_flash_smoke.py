"""Five-cluster Canto smoke test for GLM 4.7 Flash.

This intentionally reuses configuration D's deterministic property pool and
grouping policy, but isolates all paid artifacts under run variant
``FLASH47_SMOKE5`` so it cannot read or overwrite the GLM 5.2 checkpoints.
"""
from __future__ import annotations

import json
from pathlib import Path

from rtf.l11_investigation_grouping.ablation_driver import run_config_entry


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "rtf/l12_evaluation/ablation_artifacts/2024-01-canto/flash47_smoke_5clusters.json"


def main() -> None:
    result = run_config_entry(
        audit_id="2024-01-canto",
        rel_path="src/LendingLedger.sol",
        repo_root=Path("/scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto"),
        config="D",
        scope_files=["src/LendingLedger.sol"],
        scratch_root=Path("/scratch/md5344/.claude/jobs/76236636/tmp/ablation_scratch/2024-01-canto-flash47-smoke"),
        cost_ceiling_usd=0.50,
        default_solc_version="0.8.17",
        path_prefix_overrides={},
        extra_solc_args=["--via-ir", "--optimize"],
        max_concurrent_investigations=5,
        investigation_model="z-ai/glm-4.7-flash",
        cluster_limit=5,
        run_variant="FLASH47_SMOKE5",
    )
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(json.dumps({
        "artifact": str(ARTIFACT),
        "model": result.get("investigation_model"),
        "wall_s": result.get("wall_s"),
        "cost_estimate_usd": result.get("codex_cost"),
        "clusters": result.get("num_clusters"),
        "investigation_instances": result.get("num_investigation_instances"),
        "error": result.get("error"),
    }, indent=2))


if __name__ == "__main__":
    main()
