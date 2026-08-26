"""Unit tests for rtf.security_agent.evidence_store."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from rtf.security_agent.evidence_store import EvidenceStore, UnknownEvidenceRefError, _SUMMARY_PREVIEW_CHARS


def _store() -> EvidenceStore:
    return EvidenceStore(Path(tempfile.mkdtemp(prefix="evidence_store_test_")))


def test_store_then_read_roundtrips_full_content():
    store = _store()
    result = {"status": "OK", "file": "Vault.sol", "contract": "Vault", "source": "line one\nline two\nline three"}
    stored = store.store("tool-1", "get_contract_source", result)
    assert stored.evidence_id == "tool-1"
    assert json.loads(store.read("tool-1")) == result


def test_summary_is_short_and_carries_location():
    store = _store()
    huge_source = "x" * 5000
    result = {"status": "OK", "file": "Float128.sol", "contract": "Float128", "source": huge_source}
    stored = store.store("tool-2", "get_contract_source", result)
    # Bounded relative to the real preview constant (not a hardcoded
    # number) -- must still be MUCH shorter than the full 5000-char
    # source, whatever the constant is currently tuned to.
    assert len(stored.summary) < _SUMMARY_PREVIEW_CHARS + 200
    assert "Float128.sol" in stored.summary
    assert "get_contract_source" in stored.summary
    assert len(store.read("tool-2")) > 4000


def test_summary_carries_line_range_when_present():
    store = _store()
    result = {"status": "OK", "file": "Ln.sol", "lines": [80, 116], "source": "body"}
    stored = store.store("tool-3", "get_function_source", result)
    assert "80-116" in stored.summary


def test_read_unknown_evidence_id_raises_not_silently_empty():
    store = _store()
    try:
        store.read("does-not-exist")
        assert False, "expected UnknownEvidenceRefError"
    except UnknownEvidenceRefError:
        pass


def test_search_hits_summarized_without_full_dump():
    store = _store()
    result = {"status": "OK", "hits": [{"file": "A.sol", "line": 1, "text": "onlyOwner"} for _ in range(50)]}
    stored = store.store("tool-4", "search_repository", result)
    assert len(stored.summary) < 3000


def test_summary_is_retrievable_after_store():
    store = _store()
    result = {"status": "OK", "file": "X.sol", "source": "abc"}
    stored = store.store("tool-5", "get_contract_source", result)
    assert store.summary("tool-5") == stored.summary
    assert store.summary("tool-nope") is None
