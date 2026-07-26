from a4v.gnn.etl.report import ContractOutcome, compute_feasibility

CLASS_NAMES = ["reentrancy", "access_control"]


def test_funnel_counts_are_explicit_not_conflated():
    outcomes = [
        ContractOutcome(contract_id="c1", labeled=True, compile_status="OK", node_mapped=True,
                         per_class_mapped={"reentrancy": True}),
        ContractOutcome(contract_id="c2", labeled=True, compile_status="COMPILE_FAILED"),
        ContractOutcome(contract_id="c3", labeled=False, compile_status="OK"),
        ContractOutcome(contract_id="c4", labeled=True, compile_status="OK", node_mapped=False,
                         per_class_mapped={"reentrancy": False}),
    ]
    report = compute_feasibility(outcomes, CLASS_NAMES, cell_counts={}, self_contained_rate=1.0,
                                  non_self_contained_count=0)
    assert report["funnel"] == {
        "sampled": 4, "labeled": 3, "compiled_ok": 3, "labeled_and_compiled": 2, "node_mapped": 1,
    }


def test_annotation_mapping_rate_has_numerator_and_denominator():
    outcomes = [
        ContractOutcome(contract_id="c1", labeled=True, compile_status="OK", node_mapped=True),
        ContractOutcome(contract_id="c2", labeled=True, compile_status="OK", node_mapped=False),
    ]
    report = compute_feasibility(outcomes, CLASS_NAMES, {}, 1.0, 0)
    assert report["annotation_mapping_numerator"] == 1
    assert report["annotation_mapping_denominator"] == 2
    assert report["annotation_mapping_rate"] == 0.5


def test_per_class_mapping_uses_its_own_denominator():
    outcomes = [
        ContractOutcome(contract_id="c1", labeled=True, compile_status="OK",
                         per_class_mapped={"reentrancy": True}),
        ContractOutcome(contract_id="c2", labeled=True, compile_status="OK",
                         per_class_mapped={"reentrancy": False, "access_control": True}),
        ContractOutcome(contract_id="c3", labeled=True, compile_status="OK",
                         per_class_mapped={"access_control": False}),
    ]
    report = compute_feasibility(outcomes, CLASS_NAMES, {}, 1.0, 0)
    assert report["per_class_mapping"]["reentrancy"] == {"mapped": 1, "labeled_and_compiled": 2, "rate": 0.5}
    assert report["per_class_mapping"]["access_control"] == {
        "mapped": 1, "labeled_and_compiled": 2, "rate": 0.5,
    }


def test_compile_success_by_version_and_stranding_rate():
    outcomes = [
        ContractOutcome(contract_id="c1", compile_status="OK", solc_version="0.8.20"),
        ContractOutcome(contract_id="c2", compile_status="OK", solc_version="0.8.4"),
        ContractOutcome(contract_id="c3", compile_status="COMPILE_FAILED", solc_version="0.8.4"),
        ContractOutcome(contract_id="c4", compile_status="SOLC_MISSING"),
    ]
    report = compute_feasibility(outcomes, CLASS_NAMES, {}, 1.0, 0)
    assert report["compile_success_rate"] == 0.5
    assert report["compile_success_by_version"]["0.8"] == {"attempted": 3, "ok": 2, "rate": 2 / 3}
    assert report["old_solc_stranding_rate"] == 0.25


def test_no_labeled_and_compiled_contracts_gives_none_rate_not_zero_division():
    outcomes = [ContractOutcome(contract_id="c1", labeled=False, compile_status="COMPILE_FAILED")]
    report = compute_feasibility(outcomes, CLASS_NAMES, {}, 1.0, 0)
    assert report["annotation_mapping_rate"] is None


def test_graph_stats_only_over_compiled_ok():
    outcomes = [
        ContractOutcome(contract_id="c1", compile_status="OK", node_count=10, edge_count=20, disconnected=True),
        ContractOutcome(contract_id="c2", compile_status="OK", node_count=20, edge_count=40, disconnected=False),
        ContractOutcome(contract_id="c3", compile_status="COMPILE_FAILED", node_count=999, edge_count=999),
    ]
    report = compute_feasibility(outcomes, CLASS_NAMES, {}, 1.0, 0)
    assert report["graph_stats"]["avg_node_count"] == 15
    assert report["graph_stats"]["avg_edge_count"] == 30
    assert report["graph_stats"]["disconnected_share"] == 0.5


def test_empty_graph_and_label_conflict_counts_passed_through():
    outcomes = [
        ContractOutcome(contract_id="c1", empty_graph=True),
        ContractOutcome(contract_id="c2", label_conflict=True),
        ContractOutcome(contract_id="c3"),
    ]
    report = compute_feasibility(outcomes, CLASS_NAMES, {}, 0.9, 3)
    assert report["empty_graph_count"] == 1
    assert report["label_conflict_count"] == 1
    assert report["self_contained_rate"] == 0.9
    assert report["non_self_contained_count"] == 3
