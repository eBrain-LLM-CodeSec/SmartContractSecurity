"""Tests for evidence_ranking.py (Phase H work items 2-5).

Two kinds of coverage, deliberately kept separate:
1. Fully synthetic unit tests (deterministic, no external state) covering
   the ranking/bundling/budget mechanics themselves.
2. A REAL regression test against the actual, already-collected
   2023-07-pooltogether v2 run 1 evidence artifact
   (`v2_run1_artifacts/pooltogether_routed.json`, 739 raw
   `req-3-all-valid-inputs` items, no new LLM/API calls needed to check
   this) proving the specific, concrete gap this module was built to fix:
   `Vault._burn`'s narrowing-cast evidence (raw index 737/739, previously
   excluded by the flat `evidence[:30]` cutoff) now survives a
   requirement-aware bundle budget. Skips gracefully (reported, not
   silently passed) if the real checkout this needs isn't present on
   this machine -- external filesystem state, not something to hardcode
   as a hard dependency of this test suite.

Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_evidence_ranking
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from .evidence_ranking import (
    apply_evidence_budget,
    build_evidence_bundles,
    concrete_operation_named,
    is_priority_contract,
    rank_evidence,
    structured_specificity_score,
)
from .metrics import EvidenceItem

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


# --- synthetic fixtures --------------------------------------------------

def _write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def test_is_priority_contract_distinguishes_src_from_lib() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/Ledger.sol", "contract Ledger { function record() public {} }")
        _write(root, "lib/forge-std/src/console2.sol", "contract console2 { function log() public {} }")

        check("priority: real src/ contract is priority", is_priority_contract("Ledger.record", root) is True)
        check("priority: lib/ vendored contract is NOT priority", is_priority_contract("console2.log", root) is False)
        check("priority: unknown contract name returns None (not False)", is_priority_contract("Nonexistent.foo", root) is None)


def test_is_priority_contract_returns_none_without_repo_root() -> None:
    check("priority: no repo_root -> None (neutral), not False", is_priority_contract("Anything.fn", None) is None)


def test_structured_specificity_ordering() -> None:
    full = EvidenceItem(predicate="p", location="C.f", detail="d", structured={
        "operation": "cast", "input": {"name": "x", "type": "uint256"}, "source_type": "uint256",
        "destination_type": "uint96", "validation_found": "none", "missing_safety_condition": "x <= max",
        "risk": "truncation", "affected_functions": ["C.f"],
    })
    partial = EvidenceItem(predicate="p", location="C.g", detail="d", structured={"operation": "cast"})
    bare = EvidenceItem(predicate="p", location="C.h", detail="no require() found")

    s_full, s_partial, s_bare = structured_specificity_score(full), structured_specificity_score(partial), structured_specificity_score(bare)
    check("specificity: fully-populated structured evidence scores highest", s_full > s_partial > s_bare, (s_full, s_partial, s_bare))
    check("specificity: bare detail-only evidence scores exactly 0", s_bare == 0.0, s_bare)


def test_concrete_operation_named_uses_structured_then_keyword_fallback() -> None:
    structured_item = EvidenceItem(predicate="p", location="C.f", detail="x", structured={"operation": "narrowing cast"})
    keyword_item = EvidenceItem(predicate="p", location="C.f", detail="unchecked ecrecover(...) result")
    generic_item = EvidenceItem(predicate="p", location="C.f", detail="no require() references this parameter")

    check("operation: structured.operation counts", concrete_operation_named(structured_item))
    check("operation: keyword fallback catches 'ecrecover'", concrete_operation_named(keyword_item))
    check("operation: generic unvalidated-parameter phrasing does NOT count as a named operation", not concrete_operation_named(generic_item))


def test_rank_evidence_dedupes_exact_duplicates() -> None:
    a = EvidenceItem(predicate="p", location="C.f", detail="same finding")
    b = EvidenceItem(predicate="p", location="C.f", detail="same finding")  # exact duplicate
    c = EvidenceItem(predicate="p", location="C.g", detail="different finding")
    ranked = rank_evidence([a, b, c], repo_root=None)
    check("rank_evidence: exact duplicate (same predicate+location+detail) collapses to one", len(ranked) == 2, len(ranked))


def test_rank_evidence_prioritizes_priority_contract_and_specificity() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/Ledger.sol", "contract Ledger {}")
        _write(root, "lib/vendor/src/Vendored.sol", "contract Vendored {}")

        priority_specific = EvidenceItem(predicate="p", location="Ledger.record", detail="d", structured={
            "operation": "cast", "validation_found": "none", "missing_safety_condition": "x <= max",
        })
        vendored_bare = EvidenceItem(predicate="p", location="Vendored.log", detail="no require() references this parameter")

        ranked = rank_evidence([vendored_bare, priority_specific], repo_root=root)
        check(
            "rank_evidence: a priority-contract, specific-structured item outranks a vendored, bare-detail item",
            ranked[0].item.location == "Ledger.record",
            [(r.item.location, r.score) for r in ranked],
        )


def test_build_evidence_bundles_merges_same_location_findings() -> None:
    generic = EvidenceItem(predicate="find_unvalidated_function_parameters", location="Vault._burn",
                            detail="none of this function's parameters are referenced in any require()/assert() call")
    specific = EvidenceItem(predicate="find_unsafe_narrowing_cast", location="Vault._burn",
                             detail="unchecked narrowing cast", structured={
                                 "operation": "narrowing type conversion uint256 -> uint96",
                                 "input": {"name": "_shares", "type": "uint256"},
                                 "validation_found": "none", "missing_safety_condition": "_shares <= type(uint96).max",
                                 "risk": "truncation",
                             })
    ranked = rank_evidence([generic, specific], repo_root=None)
    bundles = build_evidence_bundles("req-3-all-valid-inputs", "requirement text", ranked)

    check("bundles: two findings at the SAME location merge into exactly ONE bundle", len(bundles) == 1, len(bundles))
    b = bundles[0]
    check("bundles: merged bundle's target identifies the right contract/function", b["target"]["contract"] == "Vault" and b["target"]["function"] == "_burn", b["target"])
    check("bundles: merged bundle carries the specific predicate's operation field", "narrowing" in (b["observed_operation"] or ""), b["observed_operation"])
    check("bundles: merged bundle records BOTH contributing predicates in supporting_evidence_ids", len(b["supporting_evidence_ids"]) == 2, b["supporting_evidence_ids"])
    check("bundles: possible_failure_mechanism is hedged ('may'), not an exploit-impact claim", "may" in (b["possible_failure_mechanism"] or ""), b["possible_failure_mechanism"])


def test_apply_evidence_budget_splits_included_excluded() -> None:
    ranked = rank_evidence([EvidenceItem(predicate="p", location=f"C.f{i}", detail=f"finding {i}") for i in range(10)], repo_root=None)
    bundles = build_evidence_bundles("req-x", "text", ranked)
    result = apply_evidence_budget(bundles, max_bundles=3)
    check("budget: included count respects max_bundles", len(result.included) == 3, len(result.included))
    check("budget: excluded count is the remainder", len(result.excluded) == 7, len(result.excluded))
    check("budget: prompt_char_estimate is a positive int", result.prompt_char_estimate > 0, result.prompt_char_estimate)


# --- real-data regression test -------------------------------------------

REAL_ARTIFACT = Path(__file__).resolve().parents[2] / "rtf" / "l12_evaluation" / "v2_run1_artifacts" / "pooltogether_routed.json"
REAL_CHECKOUT = Path("/scratch/md5344/evmbench/agent4vul/out/2023-07-pooltogether/checkout/vault")


def test_real_pooltogether_narrowing_cast_survives_budget_that_previously_excluded_it() -> None:
    if not REAL_ARTIFACT.exists():
        check("real-data regression: SKIPPED (real artifact not present on this machine)", True)
        return
    if not REAL_CHECKOUT.exists():
        check("real-data regression: SKIPPED (real checkout not present on this machine)", True)
        return

    routed = json.loads(REAL_ARTIFACT.read_text())
    raw_evidence = routed["req-3-all-valid-inputs"]["evidence"]
    check("real-data regression: real artifact reproduces the documented 739-item count", len(raw_evidence) == 739, len(raw_evidence))

    items = [EvidenceItem(predicate=e["predicate"], location=e["location"], detail=e.get("detail", ""), structured=e.get("structured")) for e in raw_evidence]

    # Confirm the OLD flat-list behavior really did exclude it, as documented.
    old_top_30_locations = {it.location for it in items[:30]}
    check(
        "real-data regression: OLD flat evidence[:30] cutoff did NOT include Vault._burn (confirms the documented bug, not just asserted)",
        "Vault._burn" not in old_top_30_locations,
        sorted(old_top_30_locations),
    )

    ranked = rank_evidence(items, repo_root=REAL_CHECKOUT)
    bundles = build_evidence_bundles("req-3-all-valid-inputs", "requirement text", ranked)
    budget = apply_evidence_budget(bundles, max_bundles=30)
    included_locations = {b["target"]["source_location"] for b in budget.included}

    check(
        "real-data regression: NEW ranked+bundled budget DOES include Vault._burn within the same 30-item budget",
        "Vault._burn" in included_locations,
        sorted(included_locations),
    )

    burn_bundle = next(b for b in bundles if b["target"]["source_location"] == "Vault._burn")
    check(
        "real-data regression: Vault._burn's bundle carries the specific narrowing-cast operation, not just the generic unvalidated-parameter signal",
        "narrowing" in (burn_bundle["observed_operation"] or "").lower(),
        burn_bundle["observed_operation"],
    )

    # console2 noise check: confirm it no longer dominates the budget.
    console2_included = sum(1 for b in budget.included if b["target"]["contract"] == "console2")
    check(
        "real-data regression: console2 (forge-std debug shim, 52% of raw items) does not dominate the ranked 30-item budget",
        console2_included < 15,
        console2_included,
    )


def main() -> int:
    tests = [
        test_is_priority_contract_distinguishes_src_from_lib,
        test_is_priority_contract_returns_none_without_repo_root,
        test_structured_specificity_ordering,
        test_concrete_operation_named_uses_structured_then_keyword_fallback,
        test_rank_evidence_dedupes_exact_duplicates,
        test_rank_evidence_prioritizes_priority_contract_and_specificity,
        test_build_evidence_bundles_merges_same_location_findings,
        test_apply_evidence_budget_splits_included_excluded,
        test_real_pooltogether_narrowing_cast_survives_budget_that_previously_excluded_it,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
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
