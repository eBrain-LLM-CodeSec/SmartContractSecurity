import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, '/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench')
sys.path.insert(0, '/scratch/md5344/evmbench/repo/frontier-evals/project/common/nanoeval')
sys.path.insert(0, '/scratch/md5344/evmbench/repo/frontier-evals/project/common/preparedness_turn_completer')

os.environ['OPENAI_API_KEY'] = Path('/scratch/md5344/evmbench/run/task5_secrets/openrouter.key').read_text().strip()
os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

from evmbench.audit import audit_registry
from evmbench.nano.grade.base import GraderContext, JudgeResult
from evmbench.nano.grade.detect import DetectGrader
from preparedness_turn_completer.oai_completions_turn_completer import OpenAICompletionsTurnCompleter
from preparedness_turn_completer import utils as _ptc_utils

_ptc_utils.CONTEXT_WINDOW_LENGTHS['openai/gpt-4o'] = 128_000

RUN_DIR = Path("/scratch/md5344/evmbench/rtf_canto_full_rerun_sol_20260828")


async def main() -> None:
    audit = audit_registry.get_audit('2024-01-canto')
    print(f'Loaded audit: {audit.id}, {len(audit.vulnerabilities)} vulnerabilities: '
          f'{[v.id for v in audit.vulnerabilities]}')

    completer = OpenAICompletionsTurnCompleter(model='openai/gpt-4o', response_format=JudgeResult)

    grader = DetectGrader(computer=None, turn_completer=completer)

    ctx = GraderContext(
        audit=audit,
        mode='detect',
        agent_output_path=RUN_DIR / "audit.md",
        run_group_id='canto-sol-full-rerun-grade',
        run_id='canto-sol-full-rerun-grade',
        runs_dir=str(RUN_DIR),
    )

    grade = await grader.grade(ctx)

    print()
    print('=== REAL GRADE RESULT ===')
    print(f'score = {grade.evmbench_result.score} / {grade.evmbench_result.max_score}')
    print(f'detect_award = {grade.evmbench_result.detect_award} / {grade.evmbench_result.detect_max_award}')
    for vr in grade.evmbench_result.details['vulnerability_results']:
        print(f'  {vr.vulnerability_id}: passed={vr.passed}')
    for jr in grade.evmbench_result.details['judge_results']:
        print(f'  judge: detected={jr.detected} reasoning={jr.reasoning[:400]}')

    import json
    out = {
        "audit_id": audit.id,
        "agent_output_path": str(RUN_DIR / "audit.md"),
        "judge_model": "openai/gpt-4o",
        "score": grade.evmbench_result.score,
        "max_score": grade.evmbench_result.max_score,
        "detect_award": grade.evmbench_result.detect_award,
        "detect_max_award": grade.evmbench_result.detect_max_award,
        "vulnerability_results": [
            {"vulnerability_id": vr.vulnerability_id, "passed": vr.passed}
            for vr in grade.evmbench_result.details['vulnerability_results']
        ],
        "judge_results": [
            {"detected": jr.detected, "reasoning": jr.reasoning}
            for jr in grade.evmbench_result.details['judge_results']
        ],
    }
    (RUN_DIR / "grade_result.json").write_text(json.dumps(out, indent=2), encoding="utf-8")


asyncio.run(main())
