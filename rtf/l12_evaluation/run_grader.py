"""Generic, parameterized DetectGrader invocation for RTF pipeline output.

Reuses the exact same OpenRouter-backed judge-model wiring as the
existing task10/PoolTogether-specific one-off scripts
(`/scratch/md5344/evmbench/run/task10_real_entry/run_real_grader.py` and
the `pipeline_validation` variants) -- the harness's own model registry
(`preparedness_turn_completer`) only recognizes bare OpenAI model names,
hence `_ptc_utils.CONTEXT_WINDOW_LENGTHS` gets the same client-side-only
patch those scripts already apply. Grading logic itself
(`evmbench.nano.grade.detect.DetectGrader`) is untouched -- this module
only generalizes which audit/report/output path get passed in.

Usage:
    python run_grader.py <audit_id> <agent_output_path> [--output <json_path>] [--judge-model MODEL]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

EVMBENCH_PROJECT = "/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench"
NANOEVAL_COMMON = "/scratch/md5344/evmbench/repo/frontier-evals/project/common/nanoeval"
PTC_COMMON = "/scratch/md5344/evmbench/repo/frontier-evals/project/common/preparedness_turn_completer"
DEFAULT_OPENROUTER_KEY_PATH = Path("/scratch/md5344/evmbench/run/task5_secrets/openrouter.key")


def _ensure_grader_env(openrouter_key_path: Path) -> None:
    for p in (EVMBENCH_PROJECT, NANOEVAL_COMMON, PTC_COMMON):
        if p not in sys.path:
            sys.path.insert(0, p)
    os.environ["OPENAI_API_KEY"] = openrouter_key_path.read_text().strip()
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"


async def run_grader(
    audit_id: str,
    agent_output_path: Path,
    judge_model: str = "openai/gpt-4o",
    runs_dir: str | None = None,
    openrouter_key_path: Path = DEFAULT_OPENROUTER_KEY_PATH,
) -> dict:
    _ensure_grader_env(openrouter_key_path)

    from evmbench.audit import audit_registry
    from evmbench.nano.grade.base import GraderContext, JudgeResult
    from evmbench.nano.grade.detect import DetectGrader
    from preparedness_turn_completer.oai_completions_turn_completer import OpenAICompletionsTurnCompleter
    from preparedness_turn_completer import utils as _ptc_utils

    _ptc_utils.CONTEXT_WINDOW_LENGTHS.setdefault(judge_model, 128_000)

    audit = audit_registry.get_audit(audit_id)
    completer = OpenAICompletionsTurnCompleter(model=judge_model, response_format=JudgeResult)
    grader = DetectGrader(computer=None, turn_completer=completer)

    ctx = GraderContext(
        audit=audit, mode="detect", agent_output_path=agent_output_path,
        run_group_id=f"{audit_id}-e2e-grade", run_id=f"{audit_id}-e2e-grade",
        runs_dir=runs_dir or str(agent_output_path.parent),
    )
    grade = await grader.grade(ctx)

    result = {
        "audit_id": audit_id,
        "agent_output_path": str(agent_output_path),
        "judge_model": judge_model,
        "score": grade.evmbench_result.score,
        "max_score": grade.evmbench_result.max_score,
        "detect_award": grade.evmbench_result.detect_award,
        "detect_max_award": grade.evmbench_result.detect_max_award,
        "vulnerability_results": [
            {"vulnerability_id": vr.vulnerability_id, "passed": vr.passed}
            for vr in grade.evmbench_result.details["vulnerability_results"]
        ],
        "judge_results": [
            {"detected": jr.detected, "reasoning": jr.reasoning}
            for jr in grade.evmbench_result.details["judge_results"]
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit_id")
    parser.add_argument("agent_output_path", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--judge-model", default="openai/gpt-4o")
    args = parser.parse_args()

    result = asyncio.run(run_grader(args.audit_id, args.agent_output_path, args.judge_model))

    print(f"score = {result['score']} / {result['max_score']}")
    for vr in result["vulnerability_results"]:
        print(f"  {vr['vulnerability_id']}: passed={vr['passed']}")

    if args.output:
        args.output.write_text(json.dumps(result, indent=2))
        print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
