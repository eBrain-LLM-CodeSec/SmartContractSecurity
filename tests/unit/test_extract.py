from pathlib import Path

from a4v.gnn.etl.extract import build_index, canonicalize_unit, content_sha256, extract_one


def _write(root: Path, relpath: str, text: str) -> Path:
    p = root / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def test_content_hash_stable_across_simulated_move(tmp_path):
    root_a = tmp_path / "a"
    root_b = tmp_path / "b" / "reorg" / "deeper"
    content = "pragma solidity ^0.8.0;\ncontract X {}\n"
    file_a = _write(root_a, "contracts/X.sol", content)
    file_b = _write(root_b, "contracts/X.sol", content)

    row_a, ok_a = extract_one(file_a, root_a)
    row_b, ok_b = extract_one(file_b, root_b)
    assert ok_a and ok_b
    assert row_a.contract_id == row_b.contract_id


def test_content_hash_sensitive_to_relpath_and_filename(tmp_path):
    root = tmp_path
    content = "pragma solidity ^0.8.0;\ncontract X {}\n"
    file_1 = _write(root, "one/X.sol", content)
    file_2 = _write(root, "two/Renamed.sol", content)

    row_1, _ = extract_one(file_1, root)
    row_2, _ = extract_one(file_2, root)
    assert row_1.contract_id != row_2.contract_id


def test_dedup_collapses_duplicate_content_to_one_row_with_both_native_ids(tmp_path):
    root = tmp_path
    content = "pragma solidity ^0.8.0;\ncontract Dup {}\n"
    _write(root, "d1/Dup.sol", content)
    _write(root, "d2/Dup.sol", content)
    sol_files = sorted(root.rglob("*.sol"))

    label_refs = {
        "d1/Dup.sol": {"native_id": "native-1"},
        "d2/Dup.sol": {"native_id": "native-2"},
    }
    rows, non_self_contained = build_index(sol_files, root, label_refs_by_relpath=label_refs)
    assert non_self_contained == 0
    assert len(rows) == 1
    assert set(rows[0].native_ids) == {"native-1", "native-2"}


def test_multi_file_unit_id_sensitive_to_imported_file_content(tmp_path):
    root = tmp_path
    _write(root, "u1/Main.sol", 'pragma solidity ^0.8.0;\nimport "./Lib.sol";\ncontract Main {}\n')
    _write(root, "u1/Lib.sol", "pragma solidity ^0.8.0;\nlibrary Lib { uint256 constant V = 1; }\n")
    main_1 = root / "u1" / "Main.sol"
    row_1, ok_1 = extract_one(main_1, root)
    assert ok_1
    assert row_1.extra_source_paths == ["u1/Lib.sol"]

    root2 = tmp_path.parent / (tmp_path.name + "_v2")
    _write(root2, "u1/Main.sol", 'pragma solidity ^0.8.0;\nimport "./Lib.sol";\ncontract Main {}\n')
    _write(root2, "u1/Lib.sol", "pragma solidity ^0.8.0;\nlibrary Lib { uint256 constant V = 2; }\n")  # different!
    main_2 = root2 / "u1" / "Main.sol"
    row_2, ok_2 = extract_one(main_2, root2)
    assert ok_2
    assert row_1.contract_id != row_2.contract_id


def test_conflicting_label_dup_is_flagged_not_dropped(tmp_path):
    root = tmp_path
    content = "pragma solidity ^0.8.0;\ncontract Dup {}\n"
    _write(root, "d1/Dup.sol", content)
    _write(root, "d2/Dup.sol", content)
    sol_files = sorted(root.rglob("*.sol"))

    label_refs = {
        "d1/Dup.sol": {"native_id": "native-1", "positive_classes": ["reentrancy"]},
        "d2/Dup.sol": {"native_id": "native-2", "negative_classes": ["reentrancy"]},
    }
    rows, _ = build_index(sol_files, root, label_refs_by_relpath=label_refs)
    assert len(rows) == 1
    assert rows[0].label_conflict is True
    assert "reentrancy" in rows[0].merged_classes  # kept for review, not dropped


def test_non_relative_package_import_is_not_self_contained(tmp_path):
    root = tmp_path
    _write(root, "u1/Main.sol", 'pragma solidity ^0.8.0;\nimport "@openzeppelin/contracts/token/ERC20.sol";\ncontract Main {}\n')
    sol_files = sorted(root.rglob("*.sol"))
    rows, non_self_contained = build_index(sol_files, root)
    assert rows == []
    assert non_self_contained == 1


def test_dangling_relative_import_is_not_self_contained(tmp_path):
    root = tmp_path
    _write(root, "u1/Main.sol", 'pragma solidity ^0.8.0;\nimport "./Missing.sol";\ncontract Main {}\n')
    sol_files = sorted(root.rglob("*.sol"))
    rows, non_self_contained = build_index(sol_files, root)
    assert rows == []
    assert non_self_contained == 1


def test_canonicalize_unit_normalizes_line_endings_and_trailing_whitespace():
    files_a = {"X.sol": "pragma solidity ^0.8.0;\r\ncontract X {}   \n"}
    files_b = {"X.sol": "pragma solidity ^0.8.0;\ncontract X {}"}
    assert canonicalize_unit(files_a) == canonicalize_unit(files_b)
    assert content_sha256(files_a) == content_sha256(files_b)


def test_canonicalize_unit_separator_prevents_boundary_collision():
    # Without a name-carrying separator, {"a.sol": "AB"} and
    # {"a.sol": "A", "b.sol": "B"} could hash the same via naive concatenation.
    files_1 = {"a.sol": "AB\n"}
    files_2 = {"a.sol": "A\n", "b.sol": "B\n"}
    assert canonicalize_unit(files_1) != canonicalize_unit(files_2)
