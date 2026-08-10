"""Unit tests for rtf.l12_evaluation.baseline_extraction, plus a real
(zero-cost) regression check against actual pilot5_driver.py artifacts
already on disk. Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_baseline_extraction
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from rtf.l12_evaluation.baseline_extraction import extract_audit_baseline, extract_entry_baseline

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _synthetic_entry(**overrides) -> dict:
    base = {
        "entry": "src/Test.sol",
        "wall_s": 100.0,
        "codex_cost": 1.5,
        "stage_metrics": {
            "requirements_considered": 172,
            "requirements_applicable": 50,
            "evidence_bundles_generated": 30,
            "bundles_escalated_to_codex": 20,
            "final_decisions": {"PASS": 15, "FAIL": 3, "INCONCLUSIVE": 1, "INSUFFICIENT_EVIDENCE": 1},
        },
        "escalation_skip_reasons": {},
        "codex_outcome_reasons": {},
    }
    base.update(overrides)
    return base


def test_entry_without_run_metadata_defaults_to_1to1_instances():
    entry = _synthetic_entry()
    b = extract_entry_baseline(entry)
    check("no run_metadata: grouping_policy is None (honest unknown)", b.grouping_policy is None)
    check("no num_investigation_instances field: instances == escalations",
          b.investigation_instances == b.investigations_escalated == 20, b)
    check("avg properties per call is 1.0 for a 1:1 historical run", b.avg_properties_per_call == 1.0, b.avg_properties_per_call)


def test_entry_with_run_metadata_and_instance_count_uses_real_values():
    entry = _synthetic_entry(
        run_metadata={"grouping_policy": "G0_UNGROUPED", "cluster_size": None,
                      "planner_version": "none", "context_version": "none",
                      "investigation_prompt_version": "ARM_G_PROMPT_v3"},
        num_investigation_instances=35,
    )
    entry["stage_metrics"]["bundles_escalated_to_codex"] = 20
    b = extract_entry_baseline(entry)
    check("real run_metadata: grouping_policy read through", b.grouping_policy == "G0_UNGROUPED", b.grouping_policy)
    check("real instance count: instances != escalations (expansion happened)",
          b.investigation_instances == 35 and b.investigations_escalated == 20, b)
    check("avg properties per call reflects real expansion ratio",
          abs(b.avg_properties_per_call - 20 / 35) < 1e-9, b.avg_properties_per_call)


def test_pass_fail_inconclusive_counts_extracted():
    b = extract_entry_baseline(_synthetic_entry())
    check("PASS count", b.pass_count == 15)
    check("FAIL count", b.fail_count == 3)
    check("INCONCLUSIVE count", b.inconclusive_count == 1)
    check("INSUFFICIENT_EVIDENCE count", b.insufficient_evidence_count == 1)


def test_exploration_failed_counted_from_skip_and_outcome_reasons():
    entry = _synthetic_entry(
        escalation_skip_reasons={"req-a": "codex_invocation_crashed: RuntimeError: boom"},
        codex_outcome_reasons={"req-b": "codex_timeout", "req-c": "codex_no_decision"},
    )
    b = extract_entry_baseline(entry)
    check("exploration_failed_count counts crash + timeout + no_decision", b.exploration_failed_count == 3, b.exploration_failed_count)


def test_graph_seed_not_resolved_alone_not_counted_as_exploration_failed():
    """A graph-seed-resolution note is informational, not an exploration
    failure -- the agent still investigated (see pipeline_e2e.py's own
    comment: 'agent still investigates')."""
    entry = _synthetic_entry(
        escalation_skip_reasons={"req-a": "graph_seed_not_resolved (agent still investigates): ValueError: x"},
    )
    b = extract_entry_baseline(entry)
    check("graph-seed-only note: NOT counted as exploration failure", b.exploration_failed_count == 0, b.exploration_failed_count)


def test_audit_baseline_aggregates_across_entries():
    summary = {
        "audit_id": "test-audit", "scope_entries": 2, "total_codex_cost_usd": 3.0,
        "per_entry_summaries": [_synthetic_entry(entry="A.sol"), _synthetic_entry(entry="B.sol")],
    }
    ab = extract_audit_baseline(summary)
    check("audit baseline: 2 entries", len(ab.entries) == 2)
    check("audit baseline: total escalations summed", ab.total_investigations_escalated == 40, ab.total_investigations_escalated)
    check("audit baseline: total fail count summed", ab.total_fail_count == 6, ab.total_fail_count)


# --- real-regression check against actual artifacts on disk -----------------

_ARTIFACTS_DIR = Path(__file__).resolve().parent / "pilot5_artifacts"


def test_real_forte_artifact_extracts_cleanly():
    path = _ARTIFACTS_DIR / "2025-04-forte_rtf_vs_baseline" / "pilot_summary.json"
    if not path.exists():
        check("real forte artifact: SKIPPED (not present)", True)
        return
    summary = json.loads(path.read_text())
    ab = extract_audit_baseline(summary)
    check("real forte: audit_id matches", ab.audit_id == "2025-04-forte", ab.audit_id)
    check("real forte: total_codex_cost_usd matches the known real spend",
          abs(ab.total_codex_cost_usd - 2.83640575) < 1e-6, ab.total_codex_cost_usd)
    check("real forte: 26 investigations escalated (matches stage_metrics)",
          ab.total_investigations_escalated == 26, ab.total_investigations_escalated)
    check("real forte: no run_metadata on this historical artifact (predates the field)",
          ab.entries[0].grouping_policy is None, ab.entries[0].grouping_policy)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
