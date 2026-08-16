"""RTF_V3_REDESIGN_PLAN.md Phase 7: EthTrust conformance suite.

For each requirement in the first representative slice (RTF_V3_REDESIGN_
PLAN.md's "Representative first slice" table), asserts:
    vulnerable fixture -> FAIL (or, for req-3-all-valid-inputs' safe/
    req-2-external-calls' safe, the equally-legitimate real
    NOT_APPLICABLE/PASS-with-zero-evidence outcomes documented per case)
    safe fixture       -> PASS or NOT_APPLICABLE (never FAIL)

Every fixture is provenance-commented with its EXACT EthTrust req_id and
normative text (see each `.sol` file's own header) -- built from the
official corpus, never from EVMbench ground truth. Mechanically checked
below (`test_no_fixture_references_a_benchmark_target`).

Run with:
    .venv/bin/python3 -m rtf.tests.ethtrust_conformance.test_ethtrust_conformance
"""
from __future__ import annotations

import re
import sys
from dataclasses import replace

from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState
from rtf.tests.ethtrust_conformance.conformance_harness import FIXTURES_DIR, run_tier1, run_tier2

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _fixture(req_id: str, kind: str):
    return FIXTURES_DIR / req_id / f"{kind}.sol"


def _only(tier1, location: str):
    """Narrows a multi-property Tier1Result down to the single property
    at `location`, for requirements whose predicate legitimately
    produces more than one candidate (e.g. req-3-enough-gas also gets
    generic documentary-evidence properties alongside the growth-
    specific one)."""
    matches = [p for p in tier1.properties if p.location == location]
    return replace(tier1, properties=tuple(matches[:1]))


# --- req-2-block-data-misuse: both fixtures stay APPLICABLE (the same ------
# structural predicate correctly fires on both -- this is a genuine
# semantic-judgment case, not a routing/coverage case), Tier 2 mocked. ------

def test_block_data_misuse_vulnerable_resolves_fail():
    tier1 = run_tier1(_fixture("req-2-block-data-misuse", "vulnerable"), "req-2-block-data-misuse")
    check("vulnerable: APPLICABLE", tier1.applicability_state == ApplicabilityState.APPLICABLE, tier1)
    check("vulnerable: exactly one property (updateMarket)", len(tier1.properties) == 1, tier1.properties)
    state = run_tier2(tier1, "FAIL")
    check("vulnerable: resolves FAIL", state == ConformanceState.FAIL, state)


def test_block_data_misuse_safe_resolves_pass():
    tier1 = run_tier1(_fixture("req-2-block-data-misuse", "safe"), "req-2-block-data-misuse")
    check("safe: APPLICABLE (same predicate fires -- correct, this is a judgment case)", tier1.applicability_state == ApplicabilityState.APPLICABLE, tier1)
    state = run_tier2(tier1, "PASS")
    check("safe: resolves PASS", state == ConformanceState.PASS, state)


# --- req-3-all-valid-inputs --------------------------------------------

def test_all_valid_inputs_vulnerable_resolves_fail():
    tier1 = run_tier1(_fixture("req-3-all-valid-inputs", "vulnerable"), "req-3-all-valid-inputs")
    check("vulnerable: APPLICABLE, pending investigation", tier1.applicability_state == ApplicabilityState.APPLICABLE and tier1.conformance_state is None, tier1)
    check("vulnerable: exactly one property (Ln.ln)", len(tier1.properties) == 1, tier1.properties)
    state = run_tier2(tier1, "FAIL")
    check("vulnerable: resolves FAIL", state == ConformanceState.FAIL, state)


def test_all_valid_inputs_safe_resolves_pass_with_zero_agent_calls():
    """This requirement is corpus-classified "unconditioned": with the
    require() present, NEITHER registered predicate finds anything to
    flag, and absence-of-violation-evidence directly resolves PASS --
    a REAL, zero-mock conformance result, no Tier 2 needed at all."""
    tier1 = run_tier1(_fixture("req-3-all-valid-inputs", "safe"), "req-3-all-valid-inputs")
    check("safe: resolves PASS with zero agent calls (real, not mocked)", tier1.conformance_state == ConformanceState.PASS, tier1)
    check("safe: zero evidence (require() suppressed both predicates)", tier1.evidence_locations == (), tier1.evidence_locations)


# --- req-3-enough-gas (RTF v3 Phase 5's own new predicate) -------------

def test_enough_gas_vulnerable_resolves_fail():
    tier1 = run_tier1(_fixture("req-3-enough-gas", "vulnerable"), "req-3-enough-gas")
    check("vulnerable: growth predicate fires at Holders.distributeRewards", any(p.location == "Holders.distributeRewards" for p in tier1.properties), tier1.properties)
    narrowed = _only(tier1, "Holders.distributeRewards")
    state = run_tier2(narrowed, "FAIL")
    check("vulnerable: resolves FAIL", state == ConformanceState.FAIL, state)


def test_enough_gas_safe_growth_predicate_does_not_fire():
    """Non-applicability check for the NEW Phase 5 predicate
    specifically: with removeHolder() present, no property should ever
    target Holders.distributeRewards for this requirement, even though
    the (unrelated, pre-existing) documentary-evidence collector still
    produces its own generic evidence."""
    tier1 = run_tier1(_fixture("req-3-enough-gas", "safe"), "req-3-enough-gas")
    check(
        "safe: growth predicate does NOT flag Holders.distributeRewards (pruning path exists)",
        not any(p.location == "Holders.distributeRewards" for p in tier1.properties), tier1.properties,
    )


# --- req-3-access-control -----------------------------------------------

def test_access_control_vulnerable_resolves_fail():
    tier1 = run_tier1(_fixture("req-3-access-control", "vulnerable"), "req-3-access-control")
    check("vulnerable: APPLICABLE at Treasury.withdraw", any(p.location == "Treasury.withdraw" for p in tier1.properties), tier1.properties)
    narrowed = _only(tier1, "Treasury.withdraw")
    state = run_tier2(narrowed, "FAIL")
    check("vulnerable: resolves FAIL", state == ConformanceState.FAIL, state)


def test_access_control_safe_resolves_pass():
    tier1 = run_tier1(_fixture("req-3-access-control", "safe"), "req-3-access-control")
    narrowed = _only(tier1, "Treasury.withdraw")
    check("safe: exactly one property to narrow to", len(narrowed.properties) == 1, tier1.properties)
    state = run_tier2(narrowed, "PASS")
    check("safe: resolves PASS", state == ConformanceState.PASS, state)


# --- req-2-external-calls -----------------------------------------------

def test_external_calls_vulnerable_resolves_fail():
    tier1 = run_tier1(_fixture("req-2-external-calls", "vulnerable"), "req-2-external-calls")
    check("vulnerable: APPLICABLE at Vault.withdraw", any(p.location == "Vault.withdraw" for p in tier1.properties), tier1.properties)
    state = run_tier2(tier1, "FAIL")
    check("vulnerable: resolves FAIL", state == ConformanceState.FAIL, state)


def test_external_calls_safe_resolves_not_applicable_with_zero_agent_calls():
    """CEI-respecting ordering: the write-after-external-call predicate
    finds nothing at all -- a REAL, zero-mock NOT_APPLICABLE result."""
    tier1 = run_tier1(_fixture("req-2-external-calls", "safe"), "req-2-external-calls")
    check("safe: NOT_APPLICABLE with zero agent calls (real, not mocked)", tier1.applicability_state == ApplicabilityState.NOT_APPLICABLE, tier1)


# --- req-1-no-tx.origin: fully DETERMINISTIC_COMPLETE, zero mocking at all -

def test_no_tx_origin_vulnerable_resolves_fail_fully_deterministic():
    tier1 = run_tier1(_fixture("req-1-no-tx.origin", "vulnerable"), "req-1-no-tx.origin")
    check("vulnerable: resolves FAIL with zero agent calls (DETERMINISTIC_COMPLETE)", tier1.conformance_state == ConformanceState.FAIL, tier1)


def test_no_tx_origin_safe_resolves_pass_fully_deterministic():
    tier1 = run_tier1(_fixture("req-1-no-tx.origin", "safe"), "req-1-no-tx.origin")
    check("safe: resolves PASS with zero agent calls (DETERMINISTIC_COMPLETE)", tier1.conformance_state == ConformanceState.PASS, tier1)


# --- provenance discipline (task brief constraint #1) -------------------

# Word-boundary matched (`\b`), not bare substrings -- a naive substring
# check on short tokens like "phi"/"forte" false-positives on ordinary
# English words ("phishable", "comfortable"). Word-boundary matching
# still catches every genuine reference (e.g. "Phi H-03", "canto's").
_BANNED_BENCHMARK_IDENTIFIERS = (
    "canto", "forte", "phi", "evmbench", "lendingledger", "gaugecontroller",
    "cred", "updatecuratorsharebalance", "float128", "liquidron", "feeamm",
)


def test_no_fixture_references_a_benchmark_target():
    for sol_path in FIXTURES_DIR.glob("*/*.sol"):
        text = sol_path.read_text(encoding="utf-8").lower()
        for banned in _BANNED_BENCHMARK_IDENTIFIERS:
            pattern = r"\b" + re.escape(banned) + r"\b"
            check(f"{sol_path.relative_to(FIXTURES_DIR)} does not name benchmark identifier {banned!r}", re.search(pattern, text) is None, sol_path)


def test_every_fixture_directory_has_both_vulnerable_and_safe():
    req_dirs = sorted(p for p in FIXTURES_DIR.iterdir() if p.is_dir() and p.name.startswith("req-"))
    check("at least 6 requirement fixture directories exist", len(req_dirs) >= 6, req_dirs)
    for d in req_dirs:
        check(f"{d.name} has vulnerable.sol", (d / "vulnerable.sol").exists(), d)
        check(f"{d.name} has safe.sol", (d / "safe.sol").exists(), d)


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
