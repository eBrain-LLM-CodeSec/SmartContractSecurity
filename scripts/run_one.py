#!/usr/bin/env python
"""Run the agent4vul pipeline on one target.

--source <file.sol>  smoke mode: single-file/local fixture, no EVMbench
                      audit metadata needed.
--audit <audit_id>    full EVMbench audit (needs checkout.py -- Phase 3).

Usage:
    uv run python scripts/run_one.py --source path/to/File.sol --out out/smoke
"""
import argparse
from pathlib import Path

import yaml

from a4v.commentator import Commentator
from a4v.consolidate import candidates_to_findings, dedup_and_merge
from a4v.features import FeatureExtractor
from a4v.llm import ChatClient
from a4v.repair import EnvRepair
from a4v.report import write_report
from a4v.score import SuspicionRanker, dynamic_threshold
from a4v.seeds import SeedGenerator


def load_config(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text())


def run_source(source_path: Path, out_dir: Path, config: dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    repair = EnvRepair(
        max_attempts=config["repair"]["max_attempts"],
        max_wall_clock_seconds=config["repair"]["max_wall_clock_seconds"],
    )
    build = repair.build_until_success(source_path, repair_log_path=out_dir / "repair.jsonl")
    pg = build.graph

    raw_features = FeatureExtractor.compute(pg)
    z_features = FeatureExtractor.zscore(raw_features)

    client = ChatClient.from_config(
        config["llm"], model=config["llm"]["commentator_model"],
        cache_dir=out_dir / "cache" / "llm", token_log_path=out_dir / "tokens.json",
    )
    commentator = Commentator(client, strategies=[config["fpsl"]["strategies_default"]])
    seed_gen = SeedGenerator(pg, commentator=commentator)
    _, comments = seed_gen.generate(raw_features, run_commentator=True)

    ranker = SuspicionRanker()
    candidates = ranker.rank(raw_features, z_features, comments=comments)
    dynamic_threshold(
        candidates,
        mode=config["ranking"]["threshold_mode"],
        percentile=config["ranking"]["percentile"],
    )

    findings = dedup_and_merge(candidates_to_findings(candidates, pg))

    audit_id = source_path.stem
    return write_report(audit_id, findings, out_dir / "audit.md")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="single .sol fixture file (smoke mode)")
    parser.add_argument("--audit", help="EVMbench audit_id")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1] / "config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.source:
        report_path = run_source(args.source, args.out, config)
    elif args.audit:
        raise NotImplementedError(
            "--audit mode needs checkout.py + the real Auditor (Phase 3); use --source for the smoke test"
        )
    else:
        parser.error("must pass --source or --audit")
        return

    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
