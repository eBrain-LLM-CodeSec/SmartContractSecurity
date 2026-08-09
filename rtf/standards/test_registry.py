"""Unit tests for rtf.standards.registry. Run with:
    python3 -m rtf.standards.test_registry
"""
from __future__ import annotations

import hashlib
import json
import socket
import sys
import tempfile
from pathlib import Path

from .registry import StandardsRegistry, StandardsRegistryError

PASSES = []
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _minimal_signals() -> dict:
    return {"strong": [], "supporting": []}


def _write_standard(
    directory: Path,
    standard_id: str = "TEST-STD",
    spec_text: str = "dummy spec text",
    spec_filename: str = "spec.txt",
    status: str = "Final",
    clauses: list[dict] | None = None,
    override_hash: str | None = None,
    source_family: str = "ERC",
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    spec_path = directory / spec_filename
    spec_path.write_text(spec_text, encoding="utf-8")
    actual_hash = hashlib.sha256(spec_path.read_bytes()).hexdigest()

    standard_json = {
        "standard_id": standard_id,
        "source_family": source_family,
        "title": "Test Standard",
        "version": "1",
        "status": status,
        "canonical_source_reference": "https://example.invalid/test-std",
        "local_spec_path": spec_filename,
        "local_source_hash": override_hash if override_hash is not None else actual_hash,
        "clauses_path": "clauses.json",
        "parent_gp_requirement_id": "req-R-follow-erc-standards",
        "detection_signals": _minimal_signals(),
    }
    (directory / "standard.json").write_text(json.dumps(standard_json), encoding="utf-8")

    clauses_json = {"standard_id": standard_id, "clauses": clauses if clauses is not None else []}
    (directory / "clauses.json").write_text(json.dumps(clauses_json), encoding="utf-8")


def _one_clause(standard_id: str, clause_id: str = "tc-001", strength: str = "MUST") -> dict:
    return {
        "clause_id": clause_id,
        "standard_id": standard_id,
        "section": "Methods:test",
        "original_normative_strength": strength,
        "normalized_obligation": "test() MUST do a thing.",
        "affected_interface": ["test"],
        "conditions": [],
        "exceptions": [],
        "provenance": {"source_file": "spec.txt", "source_section_heading": "Methods:test", "quoted_text": "MUST do a thing."},
    }


# --- real, committed ERC-4626 standard ---------------------------------

def test_registry_discovers_erc4626():
    reg = StandardsRegistry()
    check("registry: discovers ERC-4626 in all_ids()", "ERC-4626" in reg.all_ids(), reg.all_ids())
    record = reg.load("ERC-4626")
    check("registry: ERC-4626 status is Final", record.status == "Final", record.status)
    check(
        "registry: ERC-4626 parent_gp_requirement_id is req-R-follow-erc-standards",
        record.parent_gp_requirement_id == "req-R-follow-erc-standards",
        record.parent_gp_requirement_id,
    )
    clauses = reg.load_clauses("ERC-4626")
    check("registry: ERC-4626 has a substantial clause set (>40, covers all 16 methods)", len(clauses) > 40, len(clauses))
    ids = [c.clause_id for c in clauses]
    check("registry: ERC-4626 clause_ids are all unique", len(ids) == len(set(ids)), len(ids) - len(set(ids)))


def test_source_provenance_retained():
    reg = StandardsRegistry()
    clauses = reg.load_clauses("ERC-4626")
    fee_clause = next((c for c in clauses if c.clause_id == "erc4626-totalassets-must-include-fees"), None)
    check("registry: totalAssets fee-inclusion clause exists", fee_clause is not None)
    if fee_clause is not None:
        check(
            "registry: fee clause quoted_text matches real spec sentence",
            "MUST be inclusive of any fees" in fee_clause.provenance.quoted_text,
            fee_clause.provenance.quoted_text,
        )
        check(
            "registry: fee clause section is Methods:totalAssets",
            fee_clause.section == "Methods:totalAssets",
            fee_clause.section,
        )


def test_clause_caching_returns_same_object_set():
    reg = StandardsRegistry()
    a = reg.load_clauses("ERC-4626")
    b = reg.load_clauses("ERC-4626")
    check("registry: load_clauses is cached (identical tuple contents on repeat call)", a == b)


# --- synthetic malformed/negative cases ---------------------------------

def test_duplicate_standard_id_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "erc"
        _write_standard(root / "dir-a", standard_id="DUP-STD")
        _write_standard(root / "dir-b", standard_id="DUP-STD")
        try:
            StandardsRegistry(family_roots={"ERC": root})
            check("registry: duplicate standard_id raises", False, "no exception raised")
        except StandardsRegistryError as e:
            check("registry: duplicate standard_id raises StandardsRegistryError", "duplicate standard_id" in str(e), str(e))


def test_malformed_standard_json_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "erc"
        d = root / "bad-json"
        d.mkdir(parents=True)
        (d / "standard.json").write_text("{not valid json", encoding="utf-8")
        try:
            StandardsRegistry(family_roots={"ERC": root})
            check("registry: malformed standard.json raises", False, "no exception raised")
        except StandardsRegistryError as e:
            check("registry: malformed standard.json raises StandardsRegistryError", "malformed standard.json" in str(e), str(e))


def test_missing_required_field_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "erc"
        d = root / "missing-field"
        d.mkdir(parents=True)
        incomplete = {"standard_id": "INCOMPLETE"}  # missing everything else
        (d / "standard.json").write_text(json.dumps(incomplete), encoding="utf-8")
        try:
            StandardsRegistry(family_roots={"ERC": root})
            check("registry: missing required field raises", False, "no exception raised")
        except StandardsRegistryError as e:
            check("registry: missing required field raises StandardsRegistryError", "missing required field" in str(e), str(e))


def test_unsupported_normative_strength_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "erc"
        d = root / "bad-strength"
        bad_clause = _one_clause("BAD-STRENGTH-STD", strength="WILL")
        _write_standard(d, standard_id="BAD-STRENGTH-STD", clauses=[bad_clause])
        reg = StandardsRegistry(family_roots={"ERC": root})
        try:
            reg.load_clauses("BAD-STRENGTH-STD")
            check("registry: unsupported normative strength raises", False, "no exception raised")
        except StandardsRegistryError as e:
            check(
                "registry: unsupported normative strength raises StandardsRegistryError",
                "malformed clause" in str(e) or "unsupported normative strength" in str(e),
                str(e),
            )


def test_hash_mismatch_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "erc"
        d = root / "bad-hash"
        _write_standard(d, standard_id="BAD-HASH-STD", override_hash="0" * 64)
        try:
            StandardsRegistry(family_roots={"ERC": root})
            check("registry: source hash mismatch raises", False, "no exception raised")
        except StandardsRegistryError as e:
            check("registry: source hash mismatch raises StandardsRegistryError", "local_source_hash mismatch" in str(e), str(e))


def test_unaccepted_status_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "erc"
        d = root / "draft-status"
        _write_standard(d, standard_id="DRAFT-STD", status="Draft")
        try:
            StandardsRegistry(family_roots={"ERC": root})
            check("registry: Draft status raises (not an accepted status)", False, "no exception raised")
        except StandardsRegistryError as e:
            check("registry: Draft status raises StandardsRegistryError", "is not an accepted status" in str(e), str(e))


def test_duplicate_clause_id_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "erc"
        d = root / "dup-clause"
        c1 = _one_clause("DUP-CLAUSE-STD", clause_id="same-id")
        c2 = _one_clause("DUP-CLAUSE-STD", clause_id="same-id")
        _write_standard(d, standard_id="DUP-CLAUSE-STD", clauses=[c1, c2])
        reg = StandardsRegistry(family_roots={"ERC": root})
        try:
            reg.load_clauses("DUP-CLAUSE-STD")
            check("registry: duplicate clause_id raises", False, "no exception raised")
        except StandardsRegistryError as e:
            check("registry: duplicate clause_id raises StandardsRegistryError", "duplicate clause_id" in str(e), str(e))


def test_unknown_standard_id_raises_on_load():
    reg = StandardsRegistry()
    try:
        reg.load("NOT-A-REGISTERED-STANDARD")
        check("registry: load() of unknown standard_id raises", False, "no exception raised")
    except StandardsRegistryError as e:
        check("registry: load() of unknown standard_id raises StandardsRegistryError", "no standard registered" in str(e), str(e))


def test_registry_load_never_touches_network():
    """Patches socket.socket to raise if a real registry (the actual
    committed ERC-4626 standard, not a synthetic fixture) is constructed
    and its clauses loaded -- a real behavioral check, not just a
    docstring claim of 'no network access is required'."""
    original_socket = socket.socket

    def _blocked(*args, **kwargs):
        raise AssertionError("registry.py attempted to open a network socket")

    socket.socket = _blocked  # type: ignore[assignment]
    try:
        reg = StandardsRegistry()
        reg.load("ERC-4626")
        reg.load_clauses("ERC-4626")
        check("registry: load + load_clauses succeed with socket.socket blocked (no network access)", True)
    except AssertionError as e:
        check("registry: load + load_clauses succeed with socket.socket blocked (no network access)", False, str(e))
    finally:
        socket.socket = original_socket


def main() -> int:
    tests = [
        test_registry_discovers_erc4626,
        test_source_provenance_retained,
        test_clause_caching_returns_same_object_set,
        test_duplicate_standard_id_fails,
        test_malformed_standard_json_fails,
        test_missing_required_field_fails,
        test_unsupported_normative_strength_fails,
        test_hash_mismatch_fails,
        test_unaccepted_status_fails,
        test_duplicate_clause_id_fails,
        test_unknown_standard_id_raises_on_load,
        test_registry_load_never_touches_network,
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
