"""Leakage guard: the target audit's own findings (and its fork-family
mates') must never end up in the corpus used to detect/rank/embed for that
audit's own run.
"""
from pathlib import Path

import pytest

from a4v.corpus import EVMbenchCorpus, ExternalCorpus, ForkFamilyMap, LeakageError


@pytest.fixture
def fake_audits_dir(tmp_path: Path) -> Path:
    audits_dir = tmp_path / "audits"
    for audit_id, finding_text in [
        ("audit-a", "A's own finding: reentrancy in Foo"),
        ("audit-a-fork", "audit-a-fork's finding: same codebase as audit-a"),
        ("audit-b", "B's unrelated finding: access control in Bar"),
    ]:
        findings_dir = audits_dir / audit_id / "findings"
        findings_dir.mkdir(parents=True)
        (findings_dir / "H-01.md").write_text(finding_text)
    return audits_dir


def test_load_excluding_never_includes_target_audits_own_findings(fake_audits_dir):
    corpus = EVMbenchCorpus(fake_audits_dir, fork_map=ForkFamilyMap())
    entries = corpus.load_excluding("audit-a")
    assert all(e.audit_id != "audit-a" for e in entries)
    assert any(e.audit_id == "audit-b" for e in entries)


def test_fork_family_exclusion(fake_audits_dir):
    fork_map = ForkFamilyMap({"family1": ["audit-a", "audit-a-fork"]})
    corpus = EVMbenchCorpus(fake_audits_dir, fork_map=fork_map)
    entries = corpus.load_excluding("audit-a")
    assert all(e.audit_id not in ("audit-a", "audit-a-fork") for e in entries)
    assert any(e.audit_id == "audit-b" for e in entries)


def test_without_fork_family_naive_loao_still_leaks_the_fork_mate(fake_audits_dir):
    """Demonstrates why fork-family exclusion matters: excluding only the
    exact target id (naive LOAO) still leaks audit-a-fork's near-identical
    findings when no fork map is configured."""
    corpus = EVMbenchCorpus(fake_audits_dir, fork_map=ForkFamilyMap())
    entries = corpus.load_excluding("audit-a")
    assert any(e.audit_id == "audit-a-fork" for e in entries)


def test_assert_no_leakage_raises_on_target_audit_entry(fake_audits_dir):
    corpus = EVMbenchCorpus(fake_audits_dir, fork_map=ForkFamilyMap())
    from a4v.corpus import CorpusEntry
    bad_entries = [CorpusEntry(source="evmbench", id="audit-a/H-01.md", text="leak", audit_id="audit-a")]
    with pytest.raises(LeakageError):
        corpus.assert_no_leakage("audit-a", bad_entries)


def test_external_corpus_is_leakage_free_by_construction(tmp_path):
    ext_dir = tmp_path / "external"
    ext_dir.mkdir()
    (ext_dir / "swc-107-reentrancy.md").write_text("SWC-107: Reentrancy")
    entries = ExternalCorpus.load(ext_dir)
    assert len(entries) == 1
    assert entries[0].source == "external"
    assert entries[0].audit_id is None
