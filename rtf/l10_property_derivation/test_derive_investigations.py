"""Unit tests for rtf.l10_property_derivation.derive_investigations.

All fixtures below are either the REAL, already-fixed EthTrust v3
normative text for two requirements (`req-2-check-rounding`,
`req-3-all-valid-inputs`, quoted directly from
`rtf/l1_corpus/requirement_corpus.json` post-AR-027) or fully synthetic
strings invented for this test only -- nothing here is derived from, or
tuned against, any EVMbench audit entry or finding. Run with:
    .venv/bin/python3 -m rtf.l10_property_derivation.test_derive_investigations
"""
from __future__ import annotations

import sys

from rtf.l10_property_derivation.derive_investigations import (
    aggregate_instance_verdicts, derive_clauses, distinct_locations, expand_investigation_instances,
)
from rtf.l12_evaluation.metrics import ConformanceState

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


# --- derive_clauses -------------------------------------------------------

_REAL_ROUNDING_TEXT = (
    "Ensure Proper Rounding of Computations Affecting Value Tested code MUST "
    "identify and protect against exploiting rounding errors: The possible "
    "range of error introduced by such rounding MUST be documented. Tested "
    "code MUST NOT unintentionally create or lose value through rounding. "
    "Tested code MUST apply rounding in a way that does not allow "
    'round-trips "creating" value to repeat causing unexpectedly large '
    "transfers."
)

_REAL_SINGLE_CLAUSE_TEXT = (
    "Process All Inputs Tested Code MUST validate inputs, and function "
    "correctly whether the input is as designed or malformed."
)


def test_multi_clause_real_text_splits_into_expected_sentence_count():
    # 3 sentences, not 4: the first sentence's internal ':'-introduced
    # sub-clause ("...rounding errors: The possible range...MUST be
    # documented.") is correctly kept as ONE sentence -- a colon is not
    # sentence-terminal punctuation, so the split only occurs at the
    # period that actually ends it. This mirrors AR-027's own corpus-fix
    # rule (only '.', '!', '?' count as terminal).
    clauses = derive_clauses(_REAL_ROUNDING_TEXT)
    check("rounding: splits into 3 sentences", len(clauses) == 3, clauses)
    check("rounding: clause 1 covers both 'MUST identify' and 'MUST be documented'",
          "MUST identify" in clauses[0] and "MUST be documented" in clauses[0], clauses[0])
    check("rounding: clause 2 is the 'MUST NOT unintentionally' sentence",
          "MUST NOT unintentionally" in clauses[1], clauses[1])
    check("rounding: clause 3 is the round-trip sentence",
          "round-trips" in clauses[2], clauses[2])


def test_single_clause_real_text_returns_one_clause():
    clauses = derive_clauses(_REAL_SINGLE_CLAUSE_TEXT)
    check("single-clause: returns exactly 1 clause", len(clauses) == 1, clauses)
    check("single-clause: unchanged text", clauses[0] == _REAL_SINGLE_CLAUSE_TEXT, clauses[0])


def test_empty_text_does_not_crash():
    clauses = derive_clauses("")
    check("empty text: returns a non-empty list, not a crash", len(clauses) == 1, clauses)


def test_synthetic_three_sentence_text_splits_correctly():
    text = "Widgets MUST be blue. Widgets MUST NOT be square. Widgets SHOULD be shiny."
    clauses = derive_clauses(text)
    check("synthetic: 3 clauses", clauses == [
        "Widgets MUST be blue.", "Widgets MUST NOT be square.", "Widgets SHOULD be shiny."], clauses)


# --- distinct_locations ----------------------------------------------------

def test_distinct_locations_dedupes_preserving_first_occurrence_order():
    ranked = ["Vault.withdraw", "Vault.deposit", "Vault.withdraw", "Token.transfer"]
    result = distinct_locations(ranked, max_locations=10)
    check("dedupe: preserves first-seen order", result == ["Vault.withdraw", "Vault.deposit", "Token.transfer"], result)


def test_distinct_locations_respects_cap():
    ranked = ["A.f1", "A.f2", "A.f3", "A.f4", "A.f5"]
    result = distinct_locations(ranked, max_locations=2)
    check("dedupe: cap respected", result == ["A.f1", "A.f2"], result)


def test_distinct_locations_drops_empty_strings():
    ranked = ["A.f1", "", "A.f2"]
    result = distinct_locations(ranked, max_locations=10)
    check("dedupe: empty location dropped", result == ["A.f1", "A.f2"], result)


# --- expand_investigation_instances -----------------------------------------

def test_single_clause_single_location_matches_old_single_instance_behavior():
    """Backward-compatibility anchor: a requirement with one clause and
    exactly one evidence location must produce exactly ONE instance,
    identical in shape to the pre-existing single-instance pipeline --
    the new mechanism must not multiply cost for the common case.
    """
    instances = expand_investigation_instances(
        "req-x", _REAL_SINGLE_CLAUSE_TEXT, ["Vault.withdraw"])
    check("single/single: exactly 1 instance", len(instances) == 1, instances)
    check("single/single: candidate_location is the one location", instances[0].candidate_location == "Vault.withdraw")
    check("single/single: focused_clause is None (whole text, as before)", instances[0].focused_clause is None)


def test_single_clause_multi_location_expands_one_instance_per_location():
    instances = expand_investigation_instances(
        "req-x", _REAL_SINGLE_CLAUSE_TEXT,
        ["Vault.withdraw", "Vault.deposit", "Vault.mint"], max_total_instances=6)
    check("single/multi: one instance per distinct location", len(instances) == 3, instances)
    check("single/multi: locations preserved in rank order",
          [i.candidate_location for i in instances] == ["Vault.withdraw", "Vault.deposit", "Vault.mint"])
    check("single/multi: all focused_clause None (not multi-clause)", all(i.focused_clause is None for i in instances))


def test_single_clause_multi_location_respects_total_cap():
    instances = expand_investigation_instances(
        "req-x", _REAL_SINGLE_CLAUSE_TEXT,
        [f"C.f{i}" for i in range(20)], max_locations=10, max_total_instances=3)
    check("single/multi/cap: capped at max_total_instances", len(instances) == 3, len(instances))


def test_multi_clause_no_locations_produces_one_instance_per_clause():
    """A documentary-evidence-only requirement (no localizable evidence)
    still gets its clauses split -- candidate_location falls back to "",
    matching the pre-existing `ranked[0].item.location if ranked else ""`
    fallback exactly.
    """
    instances = expand_investigation_instances("req-y", _REAL_ROUNDING_TEXT, [])
    check("multi/none: one instance per clause", len(instances) == 3, instances)
    check("multi/none: every candidate_location is empty", all(i.candidate_location == "" for i in instances))
    check("multi/none: focused_clause set for every instance", all(i.focused_clause for i in instances))


def test_multi_clause_single_location_puts_every_clause_at_that_location():
    instances = expand_investigation_instances("req-y", _REAL_ROUNDING_TEXT, ["Vault._computeShares"])
    check("multi/single-loc: one instance per clause", len(instances) == 3, instances)
    check("multi/single-loc: all at the one location", all(i.candidate_location == "Vault._computeShares" for i in instances))
    clause_texts = [i.focused_clause for i in instances]
    check("multi/single-loc: clause texts match derive_clauses output", clause_texts == derive_clauses(_REAL_ROUNDING_TEXT))


def test_multi_clause_multi_location_guarantees_every_clause_at_least_one_instance():
    """The core combinatorial-control guarantee: even with a cap smaller
    than clauses x locations, every derived clause gets AT LEAST one
    investigation before any clause gets a second location.
    """
    instances = expand_investigation_instances(
        "req-y", _REAL_ROUNDING_TEXT,
        ["Vault._computeShares", "Vault._computeAssets", "Vault._rebase"],
        max_total_instances=6)
    check("multi/multi: total instances == 5 (3 clauses + 2 extra top-clause locations)", len(instances) == 5, len(instances))
    clause_indices = [i.clause_index for i in instances]
    check("multi/multi: every clause index 0-2 appears at least once",
          set(clause_indices) == {0, 1, 2}, clause_indices)
    top_clause_instances = [i for i in instances if i.clause_index == 0]
    check("multi/multi: clause 0 got the extra location budget (3 instances: 1 base + 2 extra)",
          len(top_clause_instances) == 3, top_clause_instances)
    check("multi/multi: clause 0's extra instances use the 2nd/3rd locations",
          {i.candidate_location for i in top_clause_instances} == {"Vault._computeShares", "Vault._computeAssets", "Vault._rebase"})


def test_multi_clause_multi_location_with_tight_cap_still_covers_all_clauses_when_possible():
    instances = expand_investigation_instances(
        "req-y", _REAL_ROUNDING_TEXT,
        ["Vault._computeShares", "Vault._computeAssets"], max_total_instances=3)
    check("multi/multi/tight: exactly 3 instances (one per clause, no budget left for extra locations)",
          len(instances) == 3, len(instances))
    check("multi/multi/tight: no extra-location instances for clause 0",
          sum(1 for i in instances if i.clause_index == 0) == 1)


def test_multi_clause_cap_smaller_than_clause_count_truncates_clauses_not_crashes():
    instances = expand_investigation_instances("req-y", _REAL_ROUNDING_TEXT, [], max_total_instances=2)
    check("multi/cap-below-clauses: capped at 2, no crash", len(instances) == 2, len(instances))
    check("multi/cap-below-clauses: first two clauses, in order",
          [i.clause_index for i in instances] == [0, 1])


def test_instance_ids_are_unique_within_one_expansion():
    instances = expand_investigation_instances(
        "req-y", _REAL_ROUNDING_TEXT,
        ["Vault._computeShares", "Vault._computeAssets", "Vault._rebase"], max_total_instances=6)
    ids = [i.instance_id for i in instances]
    check("instance_id uniqueness: no duplicates", len(ids) == len(set(ids)), ids)


# --- aggregate_instance_verdicts --------------------------------------------

def test_aggregate_single_instance_passes_through():
    check("aggregate: single PASS -> PASS", aggregate_instance_verdicts([ConformanceState.PASS]) == ConformanceState.PASS)
    check("aggregate: single FAIL -> FAIL", aggregate_instance_verdicts([ConformanceState.FAIL]) == ConformanceState.FAIL)


def test_aggregate_any_fail_wins_even_with_passes():
    result = aggregate_instance_verdicts([ConformanceState.PASS, ConformanceState.PASS, ConformanceState.FAIL])
    check("aggregate: any FAIL wins over PASSes", result == ConformanceState.FAIL, result)


def test_aggregate_all_pass_is_pass():
    result = aggregate_instance_verdicts([ConformanceState.PASS, ConformanceState.PASS])
    check("aggregate: all PASS -> PASS", result == ConformanceState.PASS, result)


def test_aggregate_mixed_pass_and_inconclusive_is_inconclusive():
    result = aggregate_instance_verdicts([ConformanceState.PASS, ConformanceState.INCONCLUSIVE])
    check("aggregate: PASS+INCONCLUSIVE -> INCONCLUSIVE (not silently PASS)", result == ConformanceState.INCONCLUSIVE, result)


def test_aggregate_insufficient_evidence_treated_as_unresolved():
    result = aggregate_instance_verdicts([ConformanceState.PASS, ConformanceState.INSUFFICIENT_EVIDENCE])
    check("aggregate: PASS+INSUFFICIENT_EVIDENCE -> INCONCLUSIVE", result == ConformanceState.INCONCLUSIVE, result)


def test_aggregate_empty_raises():
    try:
        aggregate_instance_verdicts([])
        check("aggregate: empty list raises ValueError", False, "did not raise")
    except ValueError:
        check("aggregate: empty list raises ValueError", True)


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
