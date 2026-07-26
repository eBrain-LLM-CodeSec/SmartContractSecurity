#!/usr/bin/env python
"""Standalone DetectGrader runner -- generalizes
run/task10_real_entry/run_real_grader.py over --audit and --report so any
agent4vul-produced audit.md can be scored without the full RabbitMQ/instancer
stack.

Usage:
    uv run python scripts/grade.py --audit 2023-07-pooltogether --report out/2023-07-pooltogether/audit.md
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

_SECRETS_KEY = Path("/scratch/md5344/evmbench/run/task5_secrets/openrouter.key")

os.environ.setdefault("OPENAI_API_KEY", _SECRETS_KEY.read_text().strip())
os.environ.setdefault("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

from evmbench.audit import audit_registry
from evmbench.nano.grade.base import GraderContext, JudgeResult
from evmbench.nano.grade.detect import DetectGrader
from preparedness_turn_completer.oai_completions_turn_completer import OpenAICompletionsTurnCompleter
from preparedness_turn_completer import utils as _ptc_utils

# CONTEXT_WINDOW_LENGTHS only recognizes bare OpenAI model names (e.g. "gpt-4o"),
# not OpenRouter's provider-prefixed form ("openai/gpt-4o"). This lookup is a
# client-side sanity check only -- it has no effect on what's actually sent to
# the API -- so it's safe to extend rather than work around some other way.
_ptc_utils.CONTEXT_WINDOW_LENGTHS.setdefault("openai/gpt-4o", 128_000)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, help="EVMbench audit id, e.g. 2023-07-pooltogether")
    parser.add_argument("--report", required=True, type=Path, help="Path to the audit.md report to grade")
    parser.add_argument("--judge-model", default="openai/gpt-4o", help="Judge model (default matches upstream grader)")
    parser.add_argument("--runs-dir", default=None, help="Scratch dir the grader may write to (defaults next to --report)")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional path to dump the grade result as JSON")
    return parser.parse_args()


async def main() -> int:
    args = parse_args()

    audit = audit_registry.get_audit(args.audit)
    print(f"Loaded audit: {audit.id}, {len(audit.vulnerabilities)} vulnerabilities: "
          f"{[v.id for v in audit.vulnerabilities]}")

    if not args.report.exists():
        print(f"ERROR: report path does not exist: {args.report}", file=sys.stderr)
        return 2

    completer = OpenAICompletionsTurnCompleter(model=args.judge_model, response_format=JudgeResult)
    grader = DetectGrader(computer=None, turn_completer=completer)

    runs_dir = args.runs_dir or str(args.report.resolve().parent)
    ctx = GraderContext(
        audit=audit,
        mode="detect",
        agent_output_path=args.report.resolve(),
        run_group_id=f"agent4vul-{args.audit}",
        run_id=f"agent4vul-{args.audit}",
        runs_dir=runs_dir,
    )

    grade = await grader.grade(ctx)

    result = grade.evmbench_result
    print()
    print("=== GRADE RESULT ===")
    print(f"score = {result.score} / {result.max_score}")
    print(f"detect_award = {result.detect_award} / {result.detect_max_award}")
    for vr in result.details["vulnerability_results"]:
        print(f"  {vr.vulnerability_id}: passed={vr.passed}")
    for jr in result.details["judge_results"]:
        print(f"  judge: detected={jr.detected} reasoning={jr.reasoning[:300]}")

    if args.json_out:
        payload = {
            "audit_id": args.audit,
            "report": str(args.report),
            "score": result.score,
            "max_score": result.max_score,
            "detect_award": result.detect_award,
            "detect_max_award": result.detect_max_award,
            "vulnerability_results": [
                {"vulnerability_id": vr.vulnerability_id, "passed": vr.passed}
                for vr in result.details["vulnerability_results"]
            ],
            "judge_results": [
                {"detected": jr.detected, "reasoning": jr.reasoning}
                for jr in result.details["judge_results"]
            ],
        }
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2))
        print(f"\nWrote {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
