"""Unit tests for rtf.l11_investigation_grouping.run_metadata. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_run_metadata
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.run_metadata import (
    CURRENT_CONTEXT_VERSION, CURRENT_INVESTIGATION_PROMPT_VERSION, CURRENT_PLANNER_VERSION,
    GROUPING_POLICY_G0_UNGROUPED, GROUPING_POLICY_G1_CONSERVATIVE, RunMetadata, default_run_metadata,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def test_default_run_metadata_describes_current_pipeline_state():
    md = default_run_metadata()
    check("default: grouping_policy is G0_UNGROUPED", md.grouping_policy == GROUPING_POLICY_G0_UNGROUPED)
    check("default: cluster_size is None (no cluster concept in G0)", md.cluster_size is None)
    check("default: planner_version is 'none' (no planner exists yet)", md.planner_version == "none")
    check("default: context_version is 'none' (no reusable context yet)", md.context_version == "none")
    check("default: investigation_prompt_version matches the active frozen prompt",
          md.investigation_prompt_version == "ARM_G_PROMPT_v3")


def test_as_dict_round_trips_all_fields():
    md = RunMetadata()
    d = md.as_dict()
    check("as_dict: all 5 fields present",
          set(d.keys()) == {"grouping_policy", "cluster_size", "planner_version", "context_version", "investigation_prompt_version"}, d)


def test_g0_with_nonzero_cluster_size_rejected():
    try:
        RunMetadata(grouping_policy=GROUPING_POLICY_G0_UNGROUPED, cluster_size=4)
        check("G0 + cluster_size: rejected", False, "did not raise")
    except ValueError:
        check("G0 + cluster_size: rejected", True)


def test_unknown_policy_name_rejected():
    try:
        RunMetadata(grouping_policy="NOT_A_REAL_POLICY")
        check("unknown policy name: rejected", False, "did not raise")
    except ValueError:
        check("unknown policy name: rejected", True)


def test_g1_now_implemented_as_of_phase_5_constructs_cleanly():
    """G1 was a named-but-unimplemented future policy through Phase 4;
    as of Phase 5 (rtf.l11_investigation_grouping.policies) it's real --
    constructing a RunMetadata with it must no longer raise."""
    md = RunMetadata(grouping_policy=GROUPING_POLICY_G1_CONSERVATIVE, cluster_size=4)
    check("G1 constructs cleanly post-Phase-5", md.grouping_policy == GROUPING_POLICY_G1_CONSERVATIVE)


def test_unknown_policy_name_still_rejected_after_phase_5():
    try:
        RunMetadata(grouping_policy="TOTALLY_MADE_UP_POLICY")
        check("unknown policy name still rejected", False, "did not raise")
    except ValueError:
        check("unknown policy name still rejected", True)


def test_constants_are_consistent_with_defaults():
    md = RunMetadata()
    check("constants: planner_version matches", md.planner_version == CURRENT_PLANNER_VERSION)
    check("constants: context_version matches", md.context_version == CURRENT_CONTEXT_VERSION)
    check("constants: investigation_prompt_version matches", md.investigation_prompt_version == CURRENT_INVESTIGATION_PROMPT_VERSION)


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
