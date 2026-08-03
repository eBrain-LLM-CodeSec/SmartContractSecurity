from pathlib import Path

from scripts.mgpr.build_registry import build_incorrect_claims_registry, build_registry


def _make_fake_evmbench_root(tmp_path: Path) -> Path:
    root = tmp_path / "evmbench"
    (root / "splits").mkdir(parents=True)
    (root / "audits").mkdir(parents=True)
    (root / "audits" / "fakeaudit-1" / "findings").mkdir(parents=True)
    (root / "audits" / "fakeaudit-2" / "findings").mkdir(parents=True)

    (root / "splits" / "detect-tasks.txt").write_text("fakeaudit-1\nfakeaudit-2\n")

    (root / "audits" / "task_info_audits.csv").write_text(
        "audit,project,codebase_sloc,n_contracts\n"
        "fakeaudit-1,A fake lending protocol,1000,5\n"
        "fakeaudit-2,A fake DEX,2000,8\n"
        # extra row for an audit NOT in the pinned split -- must not appear
        # in the registry at all.
        "fakeaudit-not-pinned,Should never appear,999,1\n"
    )

    (root / "audits" / "task_info.csv").write_text(
        "audit,vuln,description,n_auditors_found,award\n"
        'fakeaudit-1,H-01,"Reentrancy in withdraw",3,100.0\n'
        'fakeaudit-1,H-02,"Missing access control",1,50.0\n'
        'fakeaudit-2,H-01,"Oracle manipulation",2,75.5\n'
        'fakeaudit-not-pinned,H-01,"Should never appear",1,1.0\n'
    )

    (root / "audits" / "fakeaudit-1" / "findings" / "H-01.md").write_text(
        "# [H-01] Reentrancy in withdraw\n\n"
        "See https://github.com/fake/repo/blob/deadbeef/src/Vault.sol#L10-L20 "
        "and also https://github.com/fake/repo/blob/deadbeef/src/Vault.sol#L10-L20 (duplicate on purpose).\n"
    )
    (root / "audits" / "fakeaudit-1" / "findings" / "H-02.md").write_text(
        "# [H-02] Missing access control\n\nNo citation link in this one.\n"
    )
    # fakeaudit-2's H-01.md deliberately absent -- tests the missing-file path.

    return root


def test_registry_size_matches_pinned_list_not_hardcoded(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    registry = build_registry(root)
    assert len(registry) == 2  # exactly the pinned split's 2 audits, no more, no less
    assert {r["audit_id"] for r in registry} == {"fakeaudit-1", "fakeaudit-2"}


def test_audits_not_in_pinned_split_are_excluded(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    registry = build_registry(root)
    all_findings = [f["finding_id"] for r in registry for f in r["findings"]]
    assert not any("fakeaudit-not-pinned" in fid for fid in all_findings)


def test_finding_count_is_read_not_multiplied(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    registry = build_registry(root)
    by_audit = {r["audit_id"]: r for r in registry}
    assert len(by_audit["fakeaudit-1"]["findings"]) == 2
    assert len(by_audit["fakeaudit-2"]["findings"]) == 1  # different count per audit, not len(splits)


def test_audit_metadata_joined_correctly(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    registry = build_registry(root)
    by_audit = {r["audit_id"]: r for r in registry}
    assert by_audit["fakeaudit-1"]["project_description"] == "A fake lending protocol"
    assert by_audit["fakeaudit-1"]["codebase_sloc"] == 1000
    assert by_audit["fakeaudit-1"]["n_contracts"] == 5


def test_github_citations_extracted_and_deduplicated(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    registry = build_registry(root)
    by_audit = {r["audit_id"]: r for r in registry}
    finding = next(f for f in by_audit["fakeaudit-1"]["findings"] if f["vuln"] == "H-01")
    assert finding["github_cited_locations"] == [
        "https://github.com/fake/repo/blob/deadbeef/src/Vault.sol#L10-L20"
    ]  # the deliberate duplicate in the source text is deduplicated


def test_finding_with_no_citations_gets_empty_list(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    registry = build_registry(root)
    by_audit = {r["audit_id"]: r for r in registry}
    finding = next(f for f in by_audit["fakeaudit-1"]["findings"] if f["vuln"] == "H-02")
    assert finding["github_cited_locations"] == []


def test_missing_findings_md_recorded_as_none_not_dropped(tmp_path):
    """fakeaudit-2's H-01.md doesn't exist on disk -- the finding must still
    appear in the registry (read directly from task_info.csv), with
    findings_md_path=None and no citations, not silently dropped."""
    root = _make_fake_evmbench_root(tmp_path)
    registry = build_registry(root)
    by_audit = {r["audit_id"]: r for r in registry}
    finding = by_audit["fakeaudit-2"]["findings"][0]
    assert finding["vuln"] == "H-01"
    assert finding["findings_md_path"] is None
    assert finding["github_cited_locations"] == []


def test_title_extracted_from_heading():
    from scripts.mgpr.build_registry import _extract_title
    assert _extract_title("# [H-01] Reentrancy in withdraw\n\nbody") == "Reentrancy in withdraw"


def test_title_none_when_no_matching_heading():
    from scripts.mgpr.build_registry import _extract_title
    assert _extract_title("Some prose with no bracketed-id heading at all") is None


# --- incorrect-claims registry (Phase 3) -------------------------------------


def _add_incorrect_claims(root: Path) -> None:
    """`high/H-01.md` and `low/H-01.md` are DELIBERATELY distinct claims
    sharing the bare index -- confirmed as a real EVMbench pattern by direct
    sampling (see build_registry.py's own module comment)."""
    high_dir = root / "audits" / "fakeaudit-1" / "findings" / "incorrect" / "high"
    low_dir = root / "audits" / "fakeaudit-1" / "findings" / "incorrect" / "low"
    high_dir.mkdir(parents=True)
    low_dir.mkdir(parents=True)
    (high_dir / "H-01.md").write_text(
        "# [H-01] Reentrancy claim in withdraw (rejected)\n\n"
        "https://github.com/fake/repo/blob/deadbeef/src/Vault.sol#L10-L20\n"
    )
    (low_dir / "H-01.md").write_text(
        "# [H-01] Rounding claim in swap (rejected, different issue entirely)\n\nNo citation here.\n"
    )
    # fakeaudit-2 has no incorrect/ directory at all -- must not error.


def test_incorrect_claims_registry_distinguishes_same_index_across_severities(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    _add_incorrect_claims(root)
    rows = build_incorrect_claims_registry(root)
    ids = {r["incorrect_finding_id"] for r in rows}
    assert "fakeaudit-1/incorrect/high/H-01" in ids
    assert "fakeaudit-1/incorrect/low/H-01" in ids
    high = next(r for r in rows if r["incorrect_finding_id"] == "fakeaudit-1/incorrect/high/H-01")
    low = next(r for r in rows if r["incorrect_finding_id"] == "fakeaudit-1/incorrect/low/H-01")
    assert high["title"] != low["title"]
    assert high["severity"] == "high"
    assert low["severity"] == "low"


def test_incorrect_claims_registry_captures_source_path_and_citations(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    _add_incorrect_claims(root)
    rows = build_incorrect_claims_registry(root)
    high = next(r for r in rows if r["incorrect_finding_id"] == "fakeaudit-1/incorrect/high/H-01")
    assert high["audit_id"] == "fakeaudit-1"
    assert high["source_path"].endswith("findings/incorrect/high/H-01.md")
    assert high["github_cited_locations"] == ["https://github.com/fake/repo/blob/deadbeef/src/Vault.sol#L10-L20"]


def test_incorrect_claims_registry_handles_audit_with_no_incorrect_dir(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    _add_incorrect_claims(root)  # only fakeaudit-1 gets incorrect/
    rows = build_incorrect_claims_registry(root)
    assert not any(r["audit_id"] == "fakeaudit-2" for r in rows)


def test_incorrect_claims_registry_restricted_to_given_audit_ids(tmp_path):
    root = _make_fake_evmbench_root(tmp_path)
    _add_incorrect_claims(root)
    rows = build_incorrect_claims_registry(root, audit_ids=["fakeaudit-2"])
    assert rows == []  # fakeaudit-1's claims excluded when restricted to fakeaudit-2 only
