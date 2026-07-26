"""Phase 2 integration/smoke test: full source-mode pipeline on
VulnerableBank.sol must flag reentrancy with the external-call-before-state-
update mechanism.

Makes real OpenRouter LLM calls (Commentator pass over ~4 functions,
~$0.01-0.02 total at current pricing) -- gated behind RUN_LLM_TESTS=1 so a
plain `pytest` run never silently spends money.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

SOURCE = Path(
    "/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench/ploit/examples/reentrancy/contracts/VulnerableBank.sol"
)
SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "run_one.py"

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_LLM_TESTS") != "1",
    reason="makes real OpenRouter calls (~$0.01-0.02); set RUN_LLM_TESTS=1 to run",
)


def test_smoke_flags_reentrancy(tmp_path):
    out_dir = tmp_path / "smoke"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--source", str(SOURCE), "--out", str(out_dir)],
        capture_output=True, text=True, timeout=180, env={**os.environ},
    )
    assert result.returncode == 0, result.stderr

    audit_md = (out_dir / "audit.md").read_text()
    assert "reentrancy" in audit_md.lower()
    assert "external call" in audit_md.lower() or "before" in audit_md.lower()
    # a concrete location, not a vague flag
    assert "line" in audit_md.lower()
