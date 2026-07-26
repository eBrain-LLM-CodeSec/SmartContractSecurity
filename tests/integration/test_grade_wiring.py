"""Phase 0: grader wiring re-grades a known-good prior report and reproduces
the previously observed score. See run/task10_real_entry (Run 3, 0/2) and
run/pipeline_validation (Run 4, 1/2) in evmbench/CLAUDE.md for the history
behind this fixture.

Makes 2 real OpenRouter judge calls (openai/gpt-4o, small prompts -- a
fraction of a cent) -- gated behind RUN_LLM_TESTS=1 so a plain `pytest` run
never silently spends money.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPORT = Path("/scratch/md5344/evmbench/run/pipeline_validation/run4_audit_report.md")
GRADE_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "grade.py"


@pytest.mark.skipif(not REPORT.exists(), reason="known-good fixture report not present on this machine")
@pytest.mark.skipif(
    os.environ.get("RUN_LLM_TESTS") != "1",
    reason="makes 2 real OpenRouter judge calls (~fraction of a cent); set RUN_LLM_TESTS=1 to run",
)
def test_reproduces_run4_score():
    result = subprocess.run(
        [sys.executable, str(GRADE_SCRIPT), "--audit", "2023-07-pooltogether", "--report", str(REPORT)],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ},
    )
    assert result.returncode == 0, result.stderr
    assert "score = 1 / 2" in result.stdout, result.stdout
    assert "H-04: passed=True" in result.stdout
    assert "H-02: passed=False" in result.stdout
