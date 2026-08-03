"""Tests for scripts.mgpr.generate_corrected_metrics -- Phases 4-6's clean
population construction, route labeling, and structured miss analysis, all
operating purely on already-produced gate/route-evaluation artifacts."""
import json

from scripts.mgpr.generate_corrected_metrics import (
    build_accepted_populations,
    build_incorrect_claim_population,
    build_metrics,
    build_miss_analysis,
    label_routes,
)


def _row(finding_id, audit_id, family_outcome, routing_unit=None, gate=None, fired=None,
         predicates=None, citation="cite-1", citation_outcome="RESOLVED", reviewed=False, reviewer_status=None):
    return {
        "finding_id": finding_id, "audit_id": audit_id, "family_outcome": family_outcome,
        "expected_primary_family": family_outcome if family_outcome in
        ("P1_AUTHORIZATION", "P2_REENTRANCY", "P5_ARITHMETIC_PRECISION") else None,
        "routing_unit": routing_unit, "gate": gate, "route_would_fire": fired,
        "predicates": predicates or [], "citation": citation, "citation_outcome": citation_outcome,
        "reviewed": reviewed, "reviewer_status": reviewer_status,
    }


# --- required test 14: finding-level aggregation does not double-count -----


def test_finding_level_aggregation_does_not_double_count_multi_citation_findings():
    rows = [
        _row("a/H-01", "a", "P2_REENTRANCY", "fn::X", "G1", fired=False, citation="c1"),
        _row("a/H-01", "a", "P2_REENTRANCY", "fn::Y", "G1", fired=False, citation="c2"),
    ]
    pops = build_accepted_populations(rows)
    assert len(pops["accepted_positive"]) == 1  # ONE finding, not two rows


# --- required test 15: one firing + one non-firing unit counts as fired ---


def test_one_firing_and_one_nonfiring_unit_counts_as_fired():
    rows = [
        _row("a/H-01", "a", "P2_REENTRANCY", "fn::X", "G1", fired=False, citation="c1"),
        _row("a/H-01", "a", "P2_REENTRANCY", "fn::Y", "G1", fired=True, citation="c2"),
    ]
    pops = build_accepted_populations(rows)
    assert pops["accepted_positive"][0]["gate_fired"] is True


# --- required test 16: unresolved accepted findings are not gate misses ---


def test_unresolved_accepted_finding_not_counted_as_gate_miss():
    rows = [_row("a/H-01", "a", "P1_AUTHORIZATION", routing_unit=None, fired=None,
                  citation=None, citation_outcome="NO_CITATION")]
    pops = build_accepted_populations(rows)
    assert pops["accepted_positive"] == []
    assert len(pops["accepted_unresolved"]) == 1
    assert pops["accepted_unresolved"][0]["gate_fired"] is None
    # a miss analysis built only from accepted_positive must never include it
    misses = build_miss_analysis(pops["accepted_positive"], rows)
    assert misses == []


def test_not_applicable_and_uncertain_kept_separate():
    rows = [
        _row("a/H-01", "a", "NOT_APPLICABLE"),
        _row("a/H-02", "a", "UNCERTAIN"),
    ]
    pops = build_accepted_populations(rows)
    assert len(pops["not_applicable"]) == 1
    assert len(pops["uncertain"]) == 1
    assert pops["accepted_positive"] == []
    assert pops["accepted_unresolved"] == []


# --- required test 17: unmatched routes labeled unconfirmed, not FP -------


def test_unmatched_routes_labeled_unconfirmed_not_false_positive():
    routes = [{"audit_id": "a", "routing_unit": "fn::Z", "family": "P1_AUTHORIZATION",
               "unit_type": "function", "gates_fired": ["G1"], "prompt_id": "p", "resolution_notes": []}]
    labeled = label_routes(routes, accepted_positive=[], incorrect_claims_resolved=[])
    assert labeled[0]["route_label"] == "UNCONFIRMED"
    assert "FALSE_POSITIVE" not in labeled[0]["route_label"]


def test_accepted_matched_route_labeled():
    routes = [{"audit_id": "a", "routing_unit": "fn::X", "family": "P2_REENTRANCY",
               "unit_type": "function", "gates_fired": ["G1"], "prompt_id": "p", "resolution_notes": []}]
    accepted_positive = [{"finding_id": "a/H-01", "audit_id": "a", "family": "P2_REENTRANCY",
                           "routing_units": ["fn::X"], "gate_fired": True}]
    labeled = label_routes(routes, accepted_positive, [])
    assert labeled[0]["route_label"] == "ACCEPTED_MATCHED"


def test_incorrect_claim_matched_route_labeled():
    routes = [{"audit_id": "a", "routing_unit": "fn::X", "family": "P5_ARITHMETIC_PRECISION",
               "unit_type": "function", "gates_fired": ["G1"], "prompt_id": "p", "resolution_notes": []}]
    incorrect = [{"incorrect_finding_id": "a/incorrect/high/H-01", "audit_id": "a", "severity": "high",
                  "family": "P5_ARITHMETIC_PRECISION", "routing_units": ["fn::X"], "gate_fired": True}]
    labeled = label_routes(routes, [], incorrect)
    assert labeled[0]["route_label"] == "INCORRECT_CLAIM_MATCHED"


def test_route_matched_by_both_populations_labeled_both():
    routes = [{"audit_id": "a", "routing_unit": "fn::X", "family": "P1_AUTHORIZATION",
               "unit_type": "function", "gates_fired": ["G1"], "prompt_id": "p", "resolution_notes": []}]
    accepted_positive = [{"finding_id": "a/H-01", "audit_id": "a", "family": "P1_AUTHORIZATION",
                           "routing_units": ["fn::X"], "gate_fired": True}]
    incorrect = [{"incorrect_finding_id": "a/incorrect/high/H-01", "audit_id": "a", "severity": "high",
                  "family": "P1_AUTHORIZATION", "routing_units": ["fn::X"], "gate_fired": True}]
    labeled = label_routes(routes, accepted_positive, incorrect)
    assert labeled[0]["route_label"] == "BOTH_MATCHED"


# --- required test 19: per-family totals sum to the global total ----------


def test_per_family_totals_sum_to_global_total():
    rows = [
        _row("a/H-01", "a", "P1_AUTHORIZATION", "fn::X", "G1", fired=True, citation="c1"),
        _row("a/H-02", "a", "P2_REENTRANCY", "fn::Y", "G1", fired=False, citation="c2"),
        _row("a/H-03", "a", "P5_ARITHMETIC_PRECISION", routing_unit=None, fired=None,
             citation=None, citation_outcome="NO_CITATION"),
    ]
    pops = build_accepted_populations(rows)
    metrics = build_metrics(pops, [], [], {}, {})
    per_family_sum = sum(v["total_confirmed_findings"] for v in metrics["accepted_findings"]["per_family"].values())
    assert per_family_sum == metrics["accepted_findings"]["total_confirmed_findings"] == 3


# --- required test 20: full-registry processing is deterministic ----------


def test_processing_is_deterministic_across_repeated_runs():
    rows = [
        _row("a/H-01", "a", "P1_AUTHORIZATION", "fn::X", "G1", fired=True, citation="c1"),
        _row("a/H-02", "a", "P2_REENTRANCY", "fn::Y", "G1", fired=False, citation="c2"),
    ]
    routes = [{"audit_id": "a", "routing_unit": "fn::X", "family": "P1_AUTHORIZATION",
               "unit_type": "function", "gates_fired": ["G1"], "prompt_id": "p", "resolution_notes": []}]

    def _run():
        pops = build_accepted_populations(rows)
        labeled = label_routes(routes, pops["accepted_positive"], [])
        metrics = build_metrics(pops, [], labeled, {}, {})
        return json.dumps(metrics, sort_keys=True)

    assert _run() == _run()


# --- incorrect-claim population --------------------------------------------


def test_incorrect_claim_population_only_includes_resolved_p1p2p5():
    rows = [
        {"incorrect_finding_id": "a/incorrect/high/H-01", "audit_id": "a", "severity": "high",
         "family_outcome": "P1_AUTHORIZATION", "routing_unit": "fn::X", "route_would_fire": True},
        {"incorrect_finding_id": "a/incorrect/high/H-02", "audit_id": "a", "severity": "high",
         "family_outcome": "NOT_APPLICABLE", "routing_unit": None, "route_would_fire": None},
        {"incorrect_finding_id": "a/incorrect/low/H-01", "audit_id": "a", "severity": "low",
         "family_outcome": "P2_REENTRANCY", "routing_unit": None, "route_would_fire": None},
    ]
    resolved = build_incorrect_claim_population(rows)
    ids = {r["incorrect_finding_id"] for r in resolved}
    assert ids == {"a/incorrect/high/H-01"}  # NOT_APPLICABLE excluded, unresolved P2 excluded


# --- miss analysis ------------------------------------------------------


def test_miss_analysis_extraction_failure_from_unresolved_predicate():
    accepted_positive = [{"finding_id": "a/H-01", "audit_id": "a", "family": "P1_AUTHORIZATION",
                           "routing_units": ["fn::X"], "gate_fired": False}]
    gate_rows = [_row("a/H-01", "a", "P1_AUTHORIZATION", "fn::X", "G1", fired=False,
                       predicates=[{"predicate": "authorization_control_state", "status": "UNRESOLVED"}])]
    misses = build_miss_analysis(accepted_positive, gate_rows)
    assert misses[0]["category"] == "EXTRACTION_FAILURE"


def test_miss_analysis_structurally_inapplicable_from_clean_missing_predicate():
    accepted_positive = [{"finding_id": "a/H-01", "audit_id": "a", "family": "P1_AUTHORIZATION",
                           "routing_units": ["fn::X"], "gate_fired": False}]
    gate_rows = [_row("a/H-01", "a", "P1_AUTHORIZATION", "fn::X", "G1", fired=False,
                       predicates=[{"predicate": "state_write_exists", "status": "MISSING"}])]
    misses = build_miss_analysis(accepted_positive, gate_rows)
    assert misses[0]["category"] == "CURRENT_GATE_STRUCTURALLY_INAPPLICABLE"


def test_miss_analysis_hand_classified_override_used():
    accepted_positive = [{"finding_id": "2024-01-renft/H-03", "audit_id": "2024-01-renft",
                           "family": "P2_REENTRANCY", "routing_units": ["fn::X"], "gate_fired": False}]
    gate_rows = [_row("2024-01-renft/H-03", "2024-01-renft", "P2_REENTRANCY", "fn::X", "G1", fired=False,
                       predicates=[{"predicate": "external_call_exists", "status": "SATISFIED"}])]
    misses = build_miss_analysis(accepted_positive, gate_rows)
    assert misses[0]["category"] == "GROUND_TRUTH_MAPPING_QUESTION"


def test_miss_analysis_skips_findings_that_fired():
    accepted_positive = [{"finding_id": "a/H-01", "audit_id": "a", "family": "P1_AUTHORIZATION",
                           "routing_units": ["fn::X"], "gate_fired": True}]
    gate_rows = [_row("a/H-01", "a", "P1_AUTHORIZATION", "fn::X", "G1", fired=True)]
    assert build_miss_analysis(accepted_positive, gate_rows) == []
