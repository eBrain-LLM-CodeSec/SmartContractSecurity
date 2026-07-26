from pathlib import Path

import pytest

from a4v.gnn.etl.labels import LabelParseError, parse_labels, parse_messiq_name_label_pairs

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "messiq_labels"
REAL_RAW_ROOT = (
    Path(__file__).resolve().parents[2]
    / "data/gnn/raw/dataset_preprocessing_for_vulnerabilities"
)


def test_line_granularity_off_by_one_default_is_1_indexed():
    raw = [{"native_id": "C1", "file": "A.sol", "line": 10, "vuln_type": "reentrancy"}]
    records = parse_labels(raw)
    ann = records["C1"].annotations[0]
    assert ann.lines == (10,)
    assert ann.granularity == "line"


def test_line_granularity_shifts_0_indexed_input_to_1_indexed():
    raw = [{"native_id": "C1", "file": "A.sol", "line": 9, "vuln_type": "reentrancy"}]
    records = parse_labels(raw, line_base=0)
    assert records["C1"].annotations[0].lines == (10,)


def test_line_range_start_end_inclusive():
    raw = [{"native_id": "C1", "file": "A.sol", "line_start": 5, "line_end": 7, "vuln_type": "x"}]
    records = parse_labels(raw)
    assert records["C1"].annotations[0].lines == (5, 6, 7)


def test_line_range_off_by_one_with_0_indexed_input():
    raw = [{"native_id": "C1", "file": "A.sol", "line_start": 4, "line_end": 6, "vuln_type": "x"}]
    records = parse_labels(raw, line_base=0)
    assert records["C1"].annotations[0].lines == (5, 6, 7)


def test_multiple_annotations_grouped_by_native_id():
    raw = [
        {"native_id": "C1", "file": "A.sol", "line": 3, "vuln_type": "reentrancy"},
        {"native_id": "C1", "file": "A.sol", "line": 9, "vuln_type": "unchecked_call"},
        {"native_id": "C2", "contract": "B", "function": "withdraw", "vuln_type": "reentrancy"},
    ]
    records = parse_labels(raw)
    assert len(records) == 2
    assert len(records["C1"].annotations) == 2
    assert records["C1"].granularity == "line"
    assert records["C2"].granularity == "function"


def test_function_granularity_no_lines():
    raw = [{"native_id": "C1", "contract": "Vault", "function": "withdraw", "signature": "(uint256)", "vuln_type": "reentrancy"}]
    records = parse_labels(raw)
    ann = records["C1"].annotations[0]
    assert ann.granularity == "function"
    assert ann.contract == "Vault"
    assert ann.function_name == "withdraw"
    assert ann.signature == "(uint256)"


def test_file_granularity_no_lines_no_function():
    raw = [{"native_id": "C1", "vuln_type": "reentrancy"}]
    records = parse_labels(raw)
    assert records["C1"].granularity == "file"


def test_missing_native_id_raises():
    with pytest.raises(LabelParseError):
        parse_labels([{"file": "A.sol", "line": 1, "vuln_type": "x"}])


def test_missing_vuln_class_raises():
    with pytest.raises(LabelParseError):
        parse_labels([{"native_id": "C1", "file": "A.sol", "line": 1}])


def test_record_granularity_is_finest_across_its_annotations():
    raw = [
        {"native_id": "C1", "vuln_type": "reentrancy"},  # file-level
        {"native_id": "C1", "file": "A.sol", "line": 4, "vuln_type": "unchecked_call"},  # line-level
    ]
    records = parse_labels(raw)
    assert records["C1"].granularity == "line"


# --- real Resource 2 format: parallel name.txt / label.txt pairs ---------

def test_messiq_pairs_native_id_is_class_scoped():
    records = parse_messiq_name_label_pairs(
        FIXTURE_DIR / "final_testclass_name.txt",
        FIXTURE_DIR / "final_testclass_label.txt",
        "testclass",
    )
    assert set(records) == {"testclass/3.sol", "testclass/4.sol", "testclass/347.sol"}


def test_messiq_pairs_label_1_yields_one_graph_level_annotation():
    records = parse_messiq_name_label_pairs(
        FIXTURE_DIR / "final_testclass_name.txt",
        FIXTURE_DIR / "final_testclass_label.txt",
        "testclass",
    )
    positive = records["testclass/4.sol"]
    assert positive.granularity == "file"
    assert len(positive.annotations) == 1
    assert positive.annotations[0].vuln_class == "testclass"
    assert positive.annotations[0].file is None
    assert positive.annotations[0].lines == ()


def test_messiq_pairs_label_0_yields_no_annotations():
    records = parse_messiq_name_label_pairs(
        FIXTURE_DIR / "final_testclass_name.txt",
        FIXTURE_DIR / "final_testclass_label.txt",
        "testclass",
    )
    assert records["testclass/3.sol"].annotations == ()
    assert records["testclass/347.sol"].annotations == ()


def test_messiq_pairs_mismatched_line_counts_raises(tmp_path):
    name_file = tmp_path / "name.txt"
    label_file = tmp_path / "label.txt"
    name_file.write_text("1.sol\n2.sol\n")
    label_file.write_text("0\n")
    with pytest.raises(LabelParseError):
        parse_messiq_name_label_pairs(name_file, label_file, "testclass")


def test_messiq_pairs_bad_label_value_raises(tmp_path):
    name_file = tmp_path / "name.txt"
    label_file = tmp_path / "label.txt"
    name_file.write_text("1.sol\n")
    label_file.write_text("2\n")
    with pytest.raises(LabelParseError):
        parse_messiq_name_label_pairs(name_file, label_file, "testclass")


def test_messiq_pairs_same_numeral_different_classes_are_distinct_native_ids():
    # Confirmed via real data (MANIFEST.md finding 3): "3.sol" in different
    # class dirs is a genuinely different contract -- native_id must scope
    # by class, never the bare filename.
    a = parse_messiq_name_label_pairs(
        FIXTURE_DIR / "final_testclass_name.txt", FIXTURE_DIR / "final_testclass_label.txt", "reentrancy",
    )
    b = parse_messiq_name_label_pairs(
        FIXTURE_DIR / "final_testclass_name.txt", FIXTURE_DIR / "final_testclass_label.txt", "timestamp",
    )
    assert "reentrancy/3.sol" in a
    assert "timestamp/3.sol" in b
    assert "reentrancy/3.sol" not in b


@pytest.mark.skipif(not REAL_RAW_ROOT.exists(), reason="real Resource 2 data not downloaded in this checkout")
def test_messiq_pairs_against_real_downloaded_reentrancy_data():
    cls_dir = REAL_RAW_ROOT / "reentrancy"
    records = parse_messiq_name_label_pairs(
        cls_dir / "final_reentrancy_name.txt", cls_dir / "final_reentrancy_label.txt", "reentrancy",
    )
    assert len(records) == 301  # wc -l undercounts by 1: the file has no trailing newline
    assert "reentrancy/347.sol" in records
    assert records["reentrancy/347.sol"].annotations[0].vuln_class == "reentrancy"
