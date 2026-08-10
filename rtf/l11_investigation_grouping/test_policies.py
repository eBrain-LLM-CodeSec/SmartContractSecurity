"""Unit tests for rtf.l11_investigation_grouping.policies (G0-G3).
Synthetic PropertyMetadata fixtures only. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_policies
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.policies import apply_grouping_policy, g1_hard_gate
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.l11_investigation_grouping.run_metadata import (
    GROUPING_POLICY_G0_UNGROUPED, GROUPING_POLICY_G1_CONSERVATIVE,
    GROUPING_POLICY_G2_CONTEXT_AWARE, GROUPING_POLICY_G3_ADAPTIVE,
)
from rtf.l11_investigation_grouping.taxonomy import ReasoningCategory

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _prop(pid: str, **overrides) -> PropertyMetadata:
    base = dict(
        property_id=pid, requirement_id=f"req-{pid}", requirement_level="Q",
        requirement_semantic_intent="Test Requirement", property_text="test",
        target_contract=None, target_function=None, candidate_locations=(),
    )
    base.update(overrides)
    return PropertyMetadata(**base)


# --- G0: never groups, regardless of similarity -----------------------------

def test_g0_never_groups_even_identical_properties():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    b = _prop("p2", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    clusters = apply_grouping_policy([a, b], GROUPING_POLICY_G0_UNGROUPED)
    check("G0: always 2 singleton clusters for 2 properties", len(clusters) == 2, clusters)
    check("G0: every cluster has exactly 1 property", all(len(c.property_ids) == 1 for c in clusters), clusters)


def test_g0_covers_every_property_with_no_drops():
    props = [_prop(f"p{i}", requirement_id="req-x", target_contract="Vault") for i in range(10)]
    clusters = apply_grouping_policy(props, GROUPING_POLICY_G0_UNGROUPED)
    check("G0: 10 properties -> 10 singleton clusters", len(clusters) == 10, len(clusters))


# --- G1: strict AND gate (same requirement + category + contract) ----------

def test_g1_hard_gate_requires_all_three_conditions():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    b = _prop("p2", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    check("g1_hard_gate: same req + category + contract -> True", g1_hard_gate(a, b))


def test_g1_hard_gate_fails_if_categories_differ():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    b = _prop("p2", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.ACCESS_PRIVILEGE_CONTROL)
    check("g1_hard_gate: different categories -> False", not g1_hard_gate(a, b))


def test_g1_hard_gate_fails_if_contracts_differ():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    b = _prop("p2", requirement_id="req-x", target_contract="Other", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    check("g1_hard_gate: different contracts -> False", not g1_hard_gate(a, b))


def test_g1_hard_gate_fails_if_requirements_differ():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    b = _prop("p2", requirement_id="req-y", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    check("g1_hard_gate: different requirements -> False", not g1_hard_gate(a, b))


def test_g1_groups_when_all_three_match():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION,
              candidate_locations=("Vault.f",))
    b = _prop("p2", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION,
              candidate_locations=("Vault.f",))
    clusters = apply_grouping_policy([a, b], GROUPING_POLICY_G1_CONSERVATIVE)
    check("G1: same requirement+category+contract -> 1 cluster", len(clusters) == 1, clusters)


def test_g1_does_not_group_same_requirement_but_unrelated_contracts():
    """Plan's own example: 'same requirement but unrelated contracts ->
    does not necessarily group'."""
    a = _prop("p1", requirement_id="req-x", target_contract="Alpha", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    b = _prop("p2", requirement_id="req-x", target_contract="Beta", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    clusters = apply_grouping_policy([a, b], GROUPING_POLICY_G1_CONSERVATIVE)
    check("G1: same requirement, different contracts -> stays separate", len(clusters) == 2, clusters)


def test_g1_does_not_group_different_reasoning_categories():
    """Plan's own example: 'different reasoning categories -> split'."""
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    b = _prop("p2", requirement_id="req-x", target_contract="Vault", reasoning_category=ReasoningCategory.ACCESS_PRIVILEGE_CONTROL)
    clusters = apply_grouping_policy([a, b], GROUPING_POLICY_G1_CONSERVATIVE)
    check("G1: different reasoning categories -> stays separate", len(clusters) == 2, clusters)


# --- G2: context-aware, groups on shared state/callgraph even across contracts --

def test_g2_groups_across_contracts_when_sharing_substantial_state():
    """Plan's own example: 'shared state/callgraph -> may group'."""
    a = _prop("p1", requirement_id="req-x", target_contract="Alpha", relevant_state_variables=("sharedVar",))
    b = _prop("p2", requirement_id="req-y", target_contract="Beta", relevant_state_variables=("sharedVar",))
    clusters = apply_grouping_policy([a, b], GROUPING_POLICY_G2_CONTEXT_AWARE)
    check("G2: shared state variable across different contracts -> groups", len(clusters) == 1, clusters)


def test_g2_still_splits_on_unsafe_combination():
    a = _prop("p1", target_contract="Vault", candidate_locations=("Vault.f",), reasoning_category=ReasoningCategory.AGGREGATION_META)
    b = _prop("p2", target_contract="Vault", candidate_locations=("Vault.f",), reasoning_category=ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    clusters = apply_grouping_policy([a, b], GROUPING_POLICY_G2_CONTEXT_AWARE)
    check("G2: unsafe combination never groups even with strong overlap", len(clusters) == 2, clusters)


def test_g2_does_not_group_fully_unrelated_properties():
    a = _prop("p1", target_contract="Alpha", relevant_files=("Alpha.sol",), relevant_state_variables=("x",))
    b = _prop("p2", target_contract="Beta", relevant_files=("Beta.sol",), relevant_state_variables=("y",))
    clusters = apply_grouping_policy([a, b], GROUPING_POLICY_G2_CONTEXT_AWARE)
    check("G2: no shared context anywhere -> stays separate", len(clusters) == 2, clusters)


# --- G3: adaptive, respects a context-size budget ---------------------------

def test_g3_splits_when_combined_context_exceeds_budget():
    """Plan's own example: 'excessive context -> split'. Builds enough
    DISJOINT distinct files per property that the union clearly exceeds
    the default context budget (20)."""
    a = _prop("p1", requirement_id="req-x", target_contract="Vault",
              relevant_files=tuple(f"AFile{i}.sol" for i in range(15)))
    b = _prop("p2", requirement_id="req-x", target_contract="Vault",
              relevant_files=tuple(f"BFile{i}.sol" for i in range(15)))
    clusters = apply_grouping_policy([a, b], GROUPING_POLICY_G3_ADAPTIVE)
    check("G3: excessive combined context -> does not merge", len(clusters) == 2, clusters)


def test_g3_groups_normally_when_under_budget():
    a = _prop("p1", requirement_id="req-x", target_contract="Vault", candidate_locations=("Vault.f",))
    b = _prop("p2", requirement_id="req-x", target_contract="Vault", candidate_locations=("Vault.f",))
    clusters = apply_grouping_policy([a, b], GROUPING_POLICY_G3_ADAPTIVE)
    check("G3: small combined context -> groups normally", len(clusters) == 1, clusters)


def test_g3_has_no_fixed_cluster_size_cap():
    """G3's adaptivity comes from context-size budget, not a fixed count
    -- confirm max_cluster_size is genuinely None for this policy
    (distinguishing it from G1/G2's fixed cap)."""
    from rtf.l11_investigation_grouping.policies import POLICIES
    check("G3 has no fixed max_cluster_size", POLICIES[GROUPING_POLICY_G3_ADAPTIVE].max_cluster_size is None)
    check("G3 has a real max_context_size budget", POLICIES[GROUPING_POLICY_G3_ADAPTIVE].max_context_size is not None)


# --- cross-policy: unknown name, coverage guarantees ------------------------

def test_unknown_policy_name_raises_keyerror():
    a = _prop("p1")
    try:
        apply_grouping_policy([a], "NOT_A_REAL_POLICY")
        check("unknown policy name raises", False, "did not raise")
    except KeyError:
        check("unknown policy name raises", True)


def test_all_four_policies_cover_every_property_no_drops():
    props = [_prop(f"p{i}", requirement_id=f"req-{i % 3}", target_contract=f"C{i % 4}",
                    reasoning_category=list(ReasoningCategory)[i % 3]) for i in range(12)]
    for policy in (GROUPING_POLICY_G0_UNGROUPED, GROUPING_POLICY_G1_CONSERVATIVE,
                   GROUPING_POLICY_G2_CONTEXT_AWARE, GROUPING_POLICY_G3_ADAPTIVE):
        clusters = apply_grouping_policy(props, policy)
        all_ids = sorted(pid for c in clusters for pid in c.property_ids)
        check(f"{policy}: no property dropped/duplicated", all_ids == sorted(p.property_id for p in props), (policy, all_ids))


def test_policies_are_deterministic():
    props = [_prop(f"p{i}", requirement_id=f"req-{i % 3}", target_contract=f"C{i % 4}") for i in range(10)]
    for policy in (GROUPING_POLICY_G0_UNGROUPED, GROUPING_POLICY_G1_CONSERVATIVE,
                   GROUPING_POLICY_G2_CONTEXT_AWARE, GROUPING_POLICY_G3_ADAPTIVE):
        r1 = [c.property_ids for c in apply_grouping_policy(props, policy)]
        r2 = [c.property_ids for c in apply_grouping_policy(props, policy)]
        check(f"{policy}: deterministic across repeated calls", r1 == r2, (policy, r1, r2))


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
