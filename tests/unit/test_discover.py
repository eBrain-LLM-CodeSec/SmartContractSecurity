from pathlib import Path

from a4v.gnn.etl.discover import discover

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "gnn_discover_sample"


def test_discover_counts_sol_and_label_files():
    report = discover(FIXTURE_ROOT)
    assert report.sol_file_count == 3
    assert report.label_file_count == 1
    assert report.label_files == ["labels/vuln_labels.json"]


def test_discover_infers_function_granularity_and_classes():
    report = discover(FIXTURE_ROOT)
    assert report.label_granularity == "function"
    assert report.vuln_classes == ["reentrancy", "unchecked_call"]


def test_discover_pragma_histogram():
    report = discover(FIXTURE_ROOT)
    assert report.pragma_histogram == {"^0.8.0": 2, "^0.4.24": 1}


def test_discover_self_containment_probe():
    report = discover(FIXTURE_ROOT)
    # A.sol -> ./B.sol resolves; C.sol -> ./DoesNotExist.sol dangles.
    assert report.total_import_count == 2
    assert report.dangling_import_count == 1
    assert report.self_contained_rate == 0.5


def test_discover_finds_readme_and_instructions():
    report = discover(FIXTURE_ROOT)
    assert report.readme_paths == ["README.md"]
    assert report.instructions_paths == ["instructions/notes.txt"]


def test_discover_on_empty_tree_reports_none_granularity(tmp_path):
    (tmp_path / "empty.sol").write_text("pragma solidity ^0.8.0;\ncontract Empty {}\n")
    report = discover(tmp_path)
    assert report.label_file_count == 0
    assert report.label_granularity == "none"
    assert report.warnings  # flags the no-label-files-found case
