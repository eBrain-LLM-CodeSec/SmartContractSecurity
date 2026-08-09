"""Unit tests for rtf.standards.clause_parser -- the GENERIC RFC2119
extractor (never used for production standards, see the module docstring).
Run with:
    python3 -m rtf.standards.test_clause_parser
"""
from __future__ import annotations

import sys

from .clause_parser import extract_clauses
from .models import NormativeStrength

PASSES = []
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _extract(text: str):
    return extract_clauses(text, standard_id="TEST-STD", section="Methods:test", source_file="fixture.md")


def test_extracts_must():
    clauses = _extract("The Vault MUST implement EIP-20 to represent shares.")
    check("clause_parser: MUST extracted", len(clauses) == 1, clauses)
    if clauses:
        check("clause_parser: MUST strength normalized correctly", clauses[0].original_normative_strength == NormativeStrength.MUST)


def test_extracts_must_not():
    clauses = _extract("totalAssets() MUST NOT revert.")
    check("clause_parser: MUST NOT extracted as one clause (not MUST + separate NOT)", len(clauses) == 1, clauses)
    if clauses:
        check("clause_parser: MUST NOT strength normalized correctly", clauses[0].original_normative_strength == NormativeStrength.MUST_NOT)


def test_extracts_shall_and_shall_not():
    must = _extract("The contract SHALL emit an event.")
    must_not = _extract("The contract SHALL NOT allow reentrant calls.")
    check("clause_parser: SHALL extracted", len(must) == 1 and must[0].original_normative_strength == NormativeStrength.SHALL, must)
    check("clause_parser: SHALL NOT extracted", len(must_not) == 1 and must_not[0].original_normative_strength == NormativeStrength.SHALL_NOT, must_not)


def test_extracts_should_and_should_not():
    should = _extract("The name function SHOULD reflect the underlying token's name.")
    should_not = _extract("Implementations SHOULD NOT rely on tx.origin.")
    check("clause_parser: SHOULD extracted", len(should) == 1 and should[0].original_normative_strength == NormativeStrength.SHOULD, should)
    check("clause_parser: SHOULD NOT extracted", len(should_not) == 1 and should_not[0].original_normative_strength == NormativeStrength.SHOULD_NOT, should_not)


def test_extracts_may():
    clauses = _extract("The Vault MAY revert on calls to transfer.")
    check("clause_parser: MAY extracted", len(clauses) == 1 and clauses[0].original_normative_strength == NormativeStrength.MAY, clauses)


def test_extracts_condition_without_flattening_to_unconditional():
    clauses = _extract("If a Vault is to be non-transferrable, it MAY revert on calls to transfer.")
    check("clause_parser: conditional sentence produces exactly one clause", len(clauses) == 1, clauses)
    if clauses:
        clause = clauses[0]
        check("clause_parser: condition captured separately", len(clause.conditions) == 1 and "non-transferrable" in clause.conditions[0], clause.conditions)
        check(
            "clause_parser: obligation text does NOT silently become unconditional (condition text stripped out of obligation)",
            "If" not in clause.normalized_obligation and "non-transferrable" not in clause.normalized_obligation,
            clause.normalized_obligation,
        )
        check("clause_parser: obligation keyword still present after condition stripped", "MAY" in clause.normalized_obligation, clause.normalized_obligation)


def test_extracts_exception():
    clauses = _extract("convertToShares MUST NOT revert unless due to integer overflow caused by an unreasonably large input.")
    check("clause_parser: exception sentence produces exactly one clause", len(clauses) == 1, clauses)
    if clauses:
        clause = clauses[0]
        check("clause_parser: exception captured separately", len(clause.exceptions) == 1 and "overflow" in clause.exceptions[0], clause.exceptions)
        check("clause_parser: obligation text excludes the 'unless...' tail", "unless" not in clause.normalized_obligation.lower(), clause.normalized_obligation)


def test_section_provenance_recorded():
    clauses = _extract("The Vault MUST implement EIP-20.")
    check("clause_parser: section provenance recorded on the clause itself", clauses[0].section == "Methods:test", clauses[0].section)
    check("clause_parser: source_file provenance recorded", clauses[0].provenance.source_file == "fixture.md", clauses[0].provenance)
    check("clause_parser: quoted_text provenance is the real source sentence", "MUST implement EIP-20" in clauses[0].provenance.quoted_text, clauses[0].provenance.quoted_text)


def test_multiline_statement():
    text = "The Vault\nMUST\nimplement EIP-20 to represent\nshares."
    clauses = _extract(text)
    check("clause_parser: multiline statement (embedded newlines) still extracted as one clause", len(clauses) == 1, clauses)
    if clauses:
        check("clause_parser: multiline obligation text has newlines normalized to spaces", "\n" not in clauses[0].normalized_obligation, clauses[0].normalized_obligation)


def test_multiple_normative_terms_in_one_paragraph():
    text = (
        "The Vault MUST implement EIP-20 to represent shares. "
        "The name function SHOULD reflect the underlying token's name. "
        "Implementations MAY implement EIP-2612."
    )
    clauses = _extract(text)
    check("clause_parser: multiple sentences each with one keyword produce multiple clauses", len(clauses) == 3, clauses)
    strengths = sorted(c.original_normative_strength.value for c in clauses)
    check(
        "clause_parser: all three distinct strengths captured, none dropped",
        strengths == sorted([NormativeStrength.MUST.value, NormativeStrength.SHOULD.value, NormativeStrength.MAY.value]),
        strengths,
    )


def test_two_keywords_in_one_sentence_via_semicolon():
    text = "The function MUST return a value; it SHOULD also emit an event."
    clauses = _extract(text)
    check("clause_parser: semicolon-joined dual-clause sentence yields two clauses, not one", len(clauses) == 2, clauses)


def test_false_positive_lowercase_must_not_extracted():
    clauses = _extract("The implementation must have a valid address before deployment.")
    check(
        "clause_parser: lowercase 'must' in prose is NOT extracted as normative (false-positive avoidance)",
        len(clauses) == 0,
        clauses,
    )


def test_false_positive_mixed_case_prose_with_real_keyword_elsewhere():
    text = (
        "Developers must be careful when integrating this contract. "
        "The Vault MUST implement EIP-20 to represent shares."
    )
    clauses = _extract(text)
    check(
        "clause_parser: only the real ALL-CAPS keyword sentence is extracted; the lowercase-prose sentence is skipped",
        len(clauses) == 1,
        clauses,
    )
    if clauses:
        check("clause_parser: the extracted clause is the real one, not the false-positive sentence", "EIP-20" in clauses[0].normalized_obligation, clauses[0])


def test_no_keyword_produces_no_clauses():
    clauses = _extract("This section provides background information with no obligations.")
    check("clause_parser: prose with zero RFC2119 keywords produces zero clauses", len(clauses) == 0, clauses)


def test_clause_ids_are_unique_across_a_full_extraction():
    text = (
        "The Vault MUST implement EIP-20. "
        "The Vault MUST implement EIP-20's optional metadata extensions. "
        "It SHOULD reflect the underlying name."
    )
    clauses = _extract(text)
    ids = [c.clause_id for c in clauses]
    check("clause_parser: clause_ids unique even for repeated identical keyword+near-identical text", len(ids) == len(set(ids)), ids)


def main() -> int:
    tests = [
        test_extracts_must,
        test_extracts_must_not,
        test_extracts_shall_and_shall_not,
        test_extracts_should_and_should_not,
        test_extracts_may,
        test_extracts_condition_without_flattening_to_unconditional,
        test_extracts_exception,
        test_section_provenance_recorded,
        test_multiline_statement,
        test_multiple_normative_terms_in_one_paragraph,
        test_two_keywords_in_one_sentence_via_semicolon,
        test_false_positive_lowercase_must_not_extracted,
        test_false_positive_mixed_case_prose_with_real_keyword_elsewhere,
        test_no_keyword_produces_no_clauses,
        test_clause_ids_are_unique_across_a_full_extraction,
    ]
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
