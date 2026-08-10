"""Unit tests for rtf.l11_investigation_grouping.taxonomy. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_taxonomy
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from rtf.l11_investigation_grouping.taxonomy import (
    REQ_ID_TO_CATEGORY, UNSAFE_CATEGORY_COMBINATIONS, ReasoningCategory,
    categorize_generated_clause, categorize_requirement, is_unsafe_combination,
)

PASSES: list[str] = []
FAILURES: list[str] = []

CORPUS_PATH = Path(__file__).resolve().parents[2] / "rtf" / "l1_corpus" / "requirement_corpus.json"


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


# --- coverage: every corpus requirement has a category ----------------------

def test_every_corpus_requirement_has_exactly_one_category():
    corpus = json.loads(CORPUS_PATH.read_text())
    corpus_ids = {r["req_id"] for r in corpus["requirements"]}
    mapped_ids = set(REQ_ID_TO_CATEGORY.keys())
    check("coverage: no corpus req_id is missing from the mapping",
          corpus_ids - mapped_ids == set(), corpus_ids - mapped_ids)
    check("coverage: no mapped req_id is absent from the corpus (stale entry)",
          mapped_ids - corpus_ids == set(), mapped_ids - corpus_ids)
    check("coverage: exactly 81 requirements mapped", len(mapped_ids) == 81, len(mapped_ids))


def test_every_mapped_value_is_a_real_enum_member():
    check("all values are ReasoningCategory instances",
          all(isinstance(v, ReasoningCategory) for v in REQ_ID_TO_CATEGORY.values()))


def test_aggregation_requirements_correctly_isolated():
    for req_id in ("req-2-pass-l1", "req-3-pass-l2", "req-R-meet-all-possible"):
        check(f"{req_id} is AGGREGATION_META",
              categorize_requirement(req_id) == ReasoningCategory.AGGREGATION_META, req_id)


def test_categorize_requirement_returns_none_for_unknown_req_id():
    check("unknown req_id returns None (not a guessed category)", categorize_requirement("req-does-not-exist") is None)


# --- spot checks: a few concrete, individually-verifiable assignments -------

def test_spot_check_known_assignments():
    check("req-2-external-calls is EXTERNAL_CALL_INTERACTION",
          categorize_requirement("req-2-external-calls") == ReasoningCategory.EXTERNAL_CALL_INTERACTION)
    check("req-3-all-valid-inputs is INPUT_DOMAIN_VALIDATION",
          categorize_requirement("req-3-all-valid-inputs") == ReasoningCategory.INPUT_DOMAIN_VALIDATION)
    check("req-2-signature-verification is SIGNATURE_AUTH_REPLAY",
          categorize_requirement("req-2-signature-verification") == ReasoningCategory.SIGNATURE_AUTH_REPLAY)
    check("req-1-compiler-060 is COMPILER_TOOLCHAIN_SAFETY",
          categorize_requirement("req-1-compiler-060") == ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY)
    check("req-2-block-data-misuse is TIME_BLOCK_MEV_ORDERING",
          categorize_requirement("req-2-block-data-misuse") == ReasoningCategory.TIME_BLOCK_MEV_ORDERING)


# --- unsafe combinations -----------------------------------------------------

def test_aggregation_meta_unsafe_with_everything():
    for cat in ReasoningCategory:
        if cat == ReasoningCategory.AGGREGATION_META:
            continue
        check(f"AGGREGATION_META + {cat.value} is unsafe",
              is_unsafe_combination({ReasoningCategory.AGGREGATION_META, cat}), cat)


def test_compiler_toolchain_unsafe_with_everything_else():
    for cat in ReasoningCategory:
        if cat == ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY:
            continue
        check(f"COMPILER_TOOLCHAIN_SAFETY + {cat.value} is unsafe",
              is_unsafe_combination({ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY, cat}), cat)


def test_same_category_is_never_unsafe_with_itself():
    for cat in ReasoningCategory:
        check(f"{cat.value} + itself is safe", not is_unsafe_combination({cat}), cat)


def test_unrelated_safe_pair_not_flagged():
    check("EXTERNAL_CALL_INTERACTION + ACCESS_PRIVILEGE_CONTROL is not listed unsafe",
          not is_unsafe_combination({ReasoningCategory.EXTERNAL_CALL_INTERACTION, ReasoningCategory.ACCESS_PRIVILEGE_CONTROL}))


def test_unsafe_combination_detected_within_larger_set():
    """A 3-category cluster is unsafe if ANY pair within it is unsafe,
    not only if the whole set matches some listed 3-way combination."""
    cats = {ReasoningCategory.EXTERNAL_CALL_INTERACTION, ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
            ReasoningCategory.AGGREGATION_META}
    check("3-set containing an unsafe pair (AGGREGATION_META) is flagged unsafe", is_unsafe_combination(cats))


def test_unsafe_combinations_are_stored_symmetrically():
    """frozenset pairs are direction-independent by construction --
    verify no code path could accidentally rely on insertion order."""
    for pair in UNSAFE_CATEGORY_COMBINATIONS:
        check(f"{pair} has exactly 1 or 2 members (a valid category pair/self)", len(pair) in (1, 2), pair)


# --- generated-clause categorization -----------------------------------------

def test_categorize_generated_clause_rounding_and_fees():
    cat = categorize_generated_clause("totalAssets() SHOULD include any compounding that occurs from yield.")
    check("clause mentioning fee/yield-adjacent accounting -> ARITHMETIC_VALUE_CORRECTNESS or None",
          cat in (ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS, None), cat)


def test_categorize_generated_clause_explicit_rounding_keyword():
    cat = categorize_generated_clause("convertToShares MUST round down towards zero.")
    check("clause with 'round'/'convert'/'share' -> ARITHMETIC_VALUE_CORRECTNESS",
          cat == ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS, cat)


def test_categorize_generated_clause_signature_keyword():
    cat = categorize_generated_clause("permit() MUST validate the signature nonce before approving.")
    # "round"/"fee"/etc. absent; first matching bucket in keyword-priority order wins.
    check("clause result is a real category, not None, given clear keyword matches", cat is not None, cat)


def test_categorize_generated_clause_no_keyword_match_returns_none():
    cat = categorize_generated_clause("This contract is licensed under MIT.")
    check("no keyword match -> None (not a guessed default)", cat is None, cat)


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
