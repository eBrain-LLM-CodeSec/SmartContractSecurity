"""Deterministic tests for Increment 10's A/B harness; no paid calls."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from rtf.security_agent.eval.ab_runner import input_fingerprint, run_ab_comparison

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name, condition, detail=""):
    (PASSES if condition else FAILURES).append(name if condition else f"{name}: {detail}")


def _kwargs():
    return dict(
        codex_bin=Path("codex"), python_bin=Path("python"), mcp_server_script=Path("mcp.py"),
        api_key="secret-not-hashed-differently-between-arms", model="same-model", case_id="case-1",
        entry_file=Path("Fixture.sol"), repo_root=Path("."), candidate_location="C.f",
        solc_path_dir="/solc", solc_remaps=None, prompt="same prompt", scratch_root=Path("scratch"),
        timeout_s=120, extra_files={"plan.md": "same plan"}, compile_via_foundry=False,
    )


def test_fingerprint_stable_and_sensitive_to_semantic_input():
    first = input_fingerprint(_kwargs())
    reordered = dict(reversed(list(_kwargs().items())))
    check("fingerprint stable across dict order", first == input_fingerprint(reordered))
    changed = _kwargs(); changed["prompt"] = "different prompt"
    check("fingerprint changes with prompt", first != input_fingerprint(changed))


def test_both_arms_receive_identical_inputs_and_metrics_compare():
    seen = []

    def codex(**kwargs):
        seen.append(("codex", kwargs))
        return SimpleNamespace(final_decision={"properties": [{"property_id": "p1", "verdict": "PASS"}]},
                               cost_usd=.02, input_tokens=100, output_tokens=20,
                               graph_tool_calls=3, revealed_files=["A.sol"], wall_clock_s=4)

    def agent(**kwargs):
        seen.append(("agent", kwargs))
        return SimpleNamespace(final_decision={"properties": [{"property_id": "p1", "verdict": "FAIL"}]},
                               cost_usd=.01, input_tokens=80, output_tokens=15,
                               tool_calls=2, files_inspected=1, wall_clock_s=3)

    report = Path(tempfile.mkdtemp(prefix="ab_runner_test_")) / "report.json"
    result = run_ab_comparison(bundle_kwargs=_kwargs(), codex_runner=codex,
                               security_agent_runner=agent, report_path=report)
    check("arms received value-identical inputs", seen[0][1] == seen[1][1])
    check("input dicts are independent copies", seen[0][1] is not seen[1][1])
    check("disagreement identified", result.metrics.verdict_disagreement_ids == ("p1",))
    check("costs projected per arm", result.metrics.codex.cost_usd == .02 and
          result.metrics.security_agent.cost_usd == .01)
    persisted = json.loads(report.read_text())
    check("report persists fingerprint", persisted["input_fingerprint"] == result.input_fingerprint)


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as exc:
                FAILURES.append(f"{name}: CRASHED -- {type(exc).__name__}: {exc}")
    print(f"PASSED: {len(PASSES)}")
    for item in PASSES:
        print(f"  ok - {item}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for item in FAILURES:
            print(f"  FAIL - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
