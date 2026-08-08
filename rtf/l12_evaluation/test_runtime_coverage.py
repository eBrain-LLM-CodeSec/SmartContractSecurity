"""Unit tests for the RTF runtime-coverage-completeness fix: every
applicable requirement must reach an explicit terminal state, never
silently vanish. Covers `run_rtf.py`'s full-corpus loop, the aggregation
requirements, `compute_terminal_status`/`compute_integrity_report`, and
the new generic documentary-evidence collector. No live LLM/Codex calls
-- pure synthetic + real-compile-but-local checks, no network, no spend.
Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_runtime_coverage
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l5_predicates import predicates as P
from rtf.l12_evaluation.failure_taxonomy import OperationalStatus
from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState, EvidenceItem, RoutedRequirementResult
from rtf.l12_evaluation.pipeline_e2e import (
    compute_aggregation_requirements,
    compute_integrity_report,
    compute_terminal_status,
)
from rtf.l12_evaluation.registry import AGGREGATION_REQ_IDS, LLM_MEDIATED_REQ_IDS, REGISTRY
from rtf.l12_evaluation.run_rtf import (
    build_context_for_evmbench_target,
    load_requirement_levels,
    load_unconditioned_map,
    run_rtf,
)

CORPUS_PATH = Path(__file__).resolve().parents[1] / "l1_corpus" / "requirement_corpus.json"
VAULT_SOL = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "multi_contract" / "Vault.sol"

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _result(req_id, applicability, conformance=None, evidence=(), op_status=OperationalStatus.OK):
    return RoutedRequirementResult(req_id=req_id, applicability_state=applicability,
                                    conformance_state=conformance, evidence=tuple(evidence),
                                    operational_status=op_status)


# --- 1/4: registry coverage matches the requirement corpus exactly ---------

def test_registry_plus_aggregation_covers_full_corpus_exactly():
    unconditioned_map = load_unconditioned_map(CORPUS_PATH)
    corpus_req_ids = set(unconditioned_map.keys())
    covered = set(REGISTRY.keys()) | set(AGGREGATION_REQ_IDS)
    check("coverage: REGISTRY + AGGREGATION_REQ_IDS covers every corpus req_id",
          corpus_req_ids <= covered, sorted(corpus_req_ids - covered))
    check("coverage: REGISTRY and AGGREGATION_REQ_IDS are disjoint (no double-registration)",
          not (set(REGISTRY.keys()) & set(AGGREGATION_REQ_IDS)),
          set(REGISTRY.keys()) & set(AGGREGATION_REQ_IDS))
    check("coverage: LLM_MEDIATED_REQ_IDS is a subset of REGISTRY",
          set(LLM_MEDIATED_REQ_IDS) <= set(REGISTRY.keys()),
          set(LLM_MEDIATED_REQ_IDS) - set(REGISTRY.keys()))
    check("coverage: total corpus is exactly 81 requirements (documented size, not assumed)",
          len(corpus_req_ids) == 81, len(corpus_req_ids))


# --- 2/4: every applicable requirement reaches a terminal state ------------

def test_run_rtf_covers_full_corpus_not_just_registry():
    ctx, err = build_context_for_evmbench_target(VAULT_SOL, VAULT_SOL.parent, "0.8.20")
    check("run_rtf: real fixture compiles cleanly for this test", err is None, err)
    unconditioned_map = load_unconditioned_map(CORPUS_PATH)
    run, raw = run_rtf(ctx, "test-audit", unconditioned_map)
    check("run_rtf: routed dict covers the full 81-requirement corpus, not just REGISTRY's 78",
          len(run.routed) == len(unconditioned_map), (len(run.routed), len(unconditioned_map)))
    check("run_rtf: no requirement is silently absent from routed",
          set(run.routed.keys()) == set(unconditioned_map.keys()),
          set(unconditioned_map.keys()) - set(run.routed.keys()))


def test_previously_missing_q_requirements_now_get_real_evidence():
    ctx, err = build_context_for_evmbench_target(VAULT_SOL, VAULT_SOL.parent, "0.8.20")
    unconditioned_map = load_unconditioned_map(CORPUS_PATH)
    run, raw = run_rtf(ctx, "test-audit", unconditioned_map)
    for req_id in ("req-3-documented", "req-3-implement-as-documented"):
        r = run.routed.get(req_id)
        check(f"{req_id}: present in routed (was silently absent before this fix)", r is not None, "")
        if r is None:
            continue
        check(f"{req_id}: APPLICABLE", r.applicability_state == ApplicabilityState.APPLICABLE, r.applicability_state)
        check(f"{req_id}: operational_status OK (real predicate ran, not UNSUPPORTED_ANALYZER)",
              r.operational_status == OperationalStatus.OK, r.operational_status)
        check(f"{req_id}: has real evidence (deferred to L8, not silently PASSed)", len(r.evidence) > 0, len(r.evidence))
        check(f"{req_id}: conformance_state is None (pending L8 judgment, not auto-resolved)",
              r.conformance_state is None, r.conformance_state)


def test_synthetic_unregistered_requirement_gets_unsupported_analyzer_not_silence():
    """A requirement with no predicate, no aggregation rule -- the exact
    shape that used to vanish entirely -- must now surface as an explicit
    UNSUPPORTED_ANALYZER entry. Uses a synthetic req_id that genuinely
    isn't registered anywhere (proves the fallback branch itself works,
    independent of which real requirements happen to be covered today).
    """
    ctx, err = build_context_for_evmbench_target(VAULT_SOL, VAULT_SOL.parent, "0.8.20")
    fake_map = dict(load_unconditioned_map(CORPUS_PATH))
    fake_map["req-synthetic-never-registered"] = True
    run, raw = run_rtf(ctx, "test-audit", fake_map)
    r = run.routed.get("req-synthetic-never-registered")
    check("synthetic unregistered req: present in routed (not silently dropped)", r is not None, "")
    if r is not None:
        check("synthetic unregistered req: marked UNSUPPORTED_ANALYZER",
              r.operational_status == OperationalStatus.UNSUPPORTED_ANALYZER, r.operational_status)
        check("synthetic unregistered req: still marked APPLICABLE (never silently NOT_APPLICABLE)",
              r.applicability_state == ApplicabilityState.APPLICABLE, r.applicability_state)


# --- 3/4: aggregation requirements resolve correctly ------------------------

def test_aggregation_pass_when_all_constituents_pass_or_not_applicable():
    levels = {"req-A": "S", "req-B": "S", "req-2-pass-l1": "M"}
    routed = {
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, ConformanceState.PASS),
        "req-B": _result("req-B", ApplicabilityState.NOT_APPLICABLE),
        "req-2-pass-l1": _result("req-2-pass-l1", ApplicabilityState.APPLICABLE),
    }
    updated = compute_aggregation_requirements(routed, levels)
    check("aggregation: PASS+NOT_APPLICABLE constituents -> req-2-pass-l1 PASS",
          updated["req-2-pass-l1"].conformance_state == ConformanceState.PASS,
          updated["req-2-pass-l1"].conformance_state)


def test_aggregation_fail_when_any_constituent_fails():
    levels = {"req-A": "S", "req-B": "S", "req-2-pass-l1": "M"}
    routed = {
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, ConformanceState.PASS),
        "req-B": _result("req-B", ApplicabilityState.APPLICABLE, ConformanceState.FAIL),
        "req-2-pass-l1": _result("req-2-pass-l1", ApplicabilityState.APPLICABLE),
    }
    updated = compute_aggregation_requirements(routed, levels)
    check("aggregation: any FAIL constituent -> req-2-pass-l1 FAIL",
          updated["req-2-pass-l1"].conformance_state == ConformanceState.FAIL,
          updated["req-2-pass-l1"].conformance_state)


def test_aggregation_inconclusive_when_unresolved_but_no_fail():
    levels = {"req-A": "S", "req-B": "S", "req-2-pass-l1": "M"}
    routed = {
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, ConformanceState.PASS),
        "req-B": _result("req-B", ApplicabilityState.APPLICABLE, ConformanceState.INSUFFICIENT_EVIDENCE),
        "req-2-pass-l1": _result("req-2-pass-l1", ApplicabilityState.APPLICABLE),
    }
    updated = compute_aggregation_requirements(routed, levels)
    check("aggregation: unresolved (no FAIL) constituent -> req-2-pass-l1 INCONCLUSIVE, not a false PASS",
          updated["req-2-pass-l1"].conformance_state == ConformanceState.INCONCLUSIVE,
          updated["req-2-pass-l1"].conformance_state)


def test_meet_all_possible_never_hard_fails():
    levels = {"req-A": "S", "req-R-meet-all-possible": "GP"}
    routed = {
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, ConformanceState.FAIL),
        "req-R-meet-all-possible": _result("req-R-meet-all-possible", ApplicabilityState.APPLICABLE),
    }
    updated = compute_aggregation_requirements(routed, levels)
    check("aggregation: req-R-meet-all-possible is SHOULD-level, never FAIL even with a FAIL constituent",
          updated["req-R-meet-all-possible"].conformance_state != ConformanceState.FAIL,
          updated["req-R-meet-all-possible"].conformance_state)


# --- 4/4: terminal-status mapping + integrity report ------------------------

def test_compute_terminal_status_covers_every_shape():
    check("terminal_status: NOT_APPLICABLE",
          compute_terminal_status(_result("r", ApplicabilityState.NOT_APPLICABLE)) == "NOT_APPLICABLE", "")
    check("terminal_status: UNSUPPORTED_ANALYZER",
          compute_terminal_status(_result("r", ApplicabilityState.APPLICABLE,
                                           op_status=OperationalStatus.UNSUPPORTED_ANALYZER)) == "UNSUPPORTED_ANALYZER", "")
    check("terminal_status: EXECUTION_ERROR (any other non-OK operational status)",
          compute_terminal_status(_result("r", ApplicabilityState.APPLICABLE,
                                           op_status=OperationalStatus.COMPILATION_FAILURE)) == "EXECUTION_ERROR", "")
    check("terminal_status: PASS",
          compute_terminal_status(_result("r", ApplicabilityState.APPLICABLE, ConformanceState.PASS)) == "PASS", "")
    check("terminal_status: FAIL",
          compute_terminal_status(_result("r", ApplicabilityState.APPLICABLE, ConformanceState.FAIL)) == "FAIL", "")
    check("terminal_status: pending (conformance None, OK, applicable) -> PENDING_UNRESOLVED, the silently-missing signal",
          compute_terminal_status(_result("r", ApplicabilityState.APPLICABLE)) == "PENDING_UNRESOLVED", "")


def test_integrity_report_detects_silently_missing():
    routed_bad = {
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, ConformanceState.PASS),
        "req-B": _result("req-B", ApplicabilityState.APPLICABLE),  # pending forever -- the bug this whole fix targets
    }
    report = compute_integrity_report(routed_bad)
    check("integrity_report: detects a requirement stuck at PENDING_UNRESOLVED",
          report.silently_missing == 1, report.silently_missing)
    check("integrity_report: names the specific req_id", report.silently_missing_req_ids == ["req-B"], report.silently_missing_req_ids)
    check("integrity_report: marks the whole report invalid", report.valid is False, report.valid)
    check("integrity_report: invalid_reason is populated, not silent", bool(report.invalid_reason), "")


def test_integrity_report_valid_when_everything_resolved():
    routed_good = {
        "req-A": _result("req-A", ApplicabilityState.APPLICABLE, ConformanceState.PASS),
        "req-B": _result("req-B", ApplicabilityState.NOT_APPLICABLE),
        "req-C": _result("req-C", ApplicabilityState.APPLICABLE, op_status=OperationalStatus.UNSUPPORTED_ANALYZER),
    }
    report = compute_integrity_report(routed_good)
    check("integrity_report: silently_missing == 0 when every requirement has a real terminal state",
          report.silently_missing == 0, report.silently_missing)
    check("integrity_report: valid == True", report.valid is True, report.valid)


def test_integrity_report_classifies_deterministic_vs_llm_mediated():
    routed = {req_id: _result(req_id, ApplicabilityState.APPLICABLE) for req_id in
              (next(iter(set(REGISTRY.keys()) - set(LLM_MEDIATED_REQ_IDS))), next(iter(LLM_MEDIATED_REQ_IDS)))}
    report = compute_integrity_report(routed)
    check("integrity_report: at least 1 deterministic-executed requirement counted",
          report.applicable_executed_deterministic >= 1, report.applicable_executed_deterministic)
    check("integrity_report: at least 1 LLM-mediated-executed requirement counted",
          report.applicable_executed_llm_mediated >= 1, report.applicable_executed_llm_mediated)


# --- Judgment-layer failures cannot silently become absence ----------------

def test_judge_result_environment_failure_still_returns_a_present_result():
    """A broken judgment_layer (simulating a wrong-ChatClient-type-style
    wiring bug) must degrade the ONE requirement to ENVIRONMENT_FAILURE
    with the result still returned, never raise/vanish -- the exact
    per-requirement isolation `judge_with_l8.judge_result` already
    implements; this test proves it stays true after this session's
    changes, not just before.
    """
    from rtf.l12_evaluation.judge_with_l8 import judge_result

    class _BrokenJudgmentLayer:
        def judge_with_second_pass(self, *a, **kw):
            raise AttributeError("'NoneType' object has no attribute '_cache_key' (simulated wiring bug)")

    result = _result("req-3-documented", ApplicabilityState.APPLICABLE,
                      evidence=[EvidenceItem(predicate="test", location="x", detail="y")])
    bundles_dir_exists = (Path(__file__).resolve().parents[1] / "l2_context_bundles" / "req-3-documented.json").exists()
    check("judge_result test precondition: req-3-documented has a real L2 bundle to load", bundles_dir_exists, "")
    if not bundles_dir_exists:
        return
    updated, raw = judge_result(_BrokenJudgmentLayer(), "req-3-documented", result, repo_root=None)
    check("judge_result: a broken judgment layer degrades the result, does not raise",
          updated is not None, "")
    check("judge_result: degraded result carries ENVIRONMENT_FAILURE, not silently OK",
          updated.operational_status == OperationalStatus.ENVIRONMENT_FAILURE, updated.operational_status)
    check("judge_result: raw output records the real error, not silently empty",
          raw is not None and "error" in raw, raw)


# --- Existing deterministic predicates unchanged ----------------------------

def test_existing_deterministic_predicates_unchanged_by_this_session():
    sample_before = {
        "req-1-compiler-060": "check_compiler_version_floor",
        "req-1-eip155-chainid": "find_keccak256_calls_chainid_dependency",
        "req-3-event-on-state-change": "find_state_write_without_event",
        "req-R-define-license": "find_spdx_or_license_file",
    }
    for req_id, expected_func_name in sample_before.items():
        specs = REGISTRY.get(req_id)
        check(f"{req_id}: still registered", specs is not None, "")
        if specs:
            actual = getattr(specs[0].func, "__name__", None)
            check(f"{req_id}: predicate function unchanged ({expected_func_name})",
                  actual == expected_func_name, actual)


def test_new_generic_collector_never_returns_empty_evidence():
    """Correctness-critical: if this predicate ever returned an empty
    list, run_rtf.py's "no evidence + unconditioned -> auto PASS"
    shortcut (correct for prohibition-shaped requirements) would silently
    mis-resolve an affirmative-obligation requirement like "MUST have
    documentation" to PASS whenever nothing was found -- see the
    predicate's own docstring for the full explanation. This test proves
    the guarantee holds even in the worst case (no README, no docs/, no
    NatSpec, using an isolated empty temp repo).
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp)
        entry = repo_root / "Empty.sol"
        entry.write_text("pragma solidity ^0.8.0;\ncontract Empty {}\n")
        findings = P.collect_documentary_and_implementation_evidence("req-test", entry, repo_root)
        check("generic collector: never returns empty findings, even with zero README/docs/NatSpec",
              len(findings) > 0, len(findings))
        check("generic collector: explicitly states README absence rather than silently omitting it",
              any("No README" in f["detail"] for f in findings), [f["detail"][:60] for f in findings])


def main() -> int:
    tests = [
        test_registry_plus_aggregation_covers_full_corpus_exactly,
        test_run_rtf_covers_full_corpus_not_just_registry,
        test_previously_missing_q_requirements_now_get_real_evidence,
        test_synthetic_unregistered_requirement_gets_unsupported_analyzer_not_silence,
        test_aggregation_pass_when_all_constituents_pass_or_not_applicable,
        test_aggregation_fail_when_any_constituent_fails,
        test_aggregation_inconclusive_when_unresolved_but_no_fail,
        test_meet_all_possible_never_hard_fails,
        test_compute_terminal_status_covers_every_shape,
        test_integrity_report_detects_silently_missing,
        test_integrity_report_valid_when_everything_resolved,
        test_integrity_report_classifies_deterministic_vs_llm_mediated,
        test_judge_result_environment_failure_still_returns_a_present_result,
        test_existing_deterministic_predicates_unchanged_by_this_session,
        test_new_generic_collector_never_returns_empty_evidence,
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
