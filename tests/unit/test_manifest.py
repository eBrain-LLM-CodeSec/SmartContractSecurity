import json

import pytest

from a4v.gnn.etl.manifest import (
    Attempt,
    SameRunDuplicateClaim,
    append_attempt,
    merge_manifest,
    read_attempts,
    write_manifest,
)


def test_same_run_duplicate_claim_raises():
    attempts = [
        {"contract_id": "c1", "status": "OK", "run_id": "100", "ts": 1.0},
        {"contract_id": "c1", "status": "COMPILE_FAILED", "run_id": "100", "ts": 2.0},
    ]
    with pytest.raises(SameRunDuplicateClaim):
        merge_manifest(attempts)


def test_cross_run_retry_last_wins_by_run_id_not_ts():
    # run_id="200" ts is *earlier* than run_id="100"'s ts (clock skew) --
    # run_id must dominate, so "200" wins regardless.
    attempts = [
        {"contract_id": "c1", "status": "COMPILE_FAILED", "run_id": "100", "ts": 100.0},
        {"contract_id": "c1", "status": "TIMEOUT", "run_id": "200", "ts": 5.0},
    ]
    merged = merge_manifest(attempts)
    assert merged["c1"]["run_id"] == "200"
    assert merged["c1"]["status"] == "TIMEOUT"


def test_ok_is_sticky_never_downgraded_by_later_run():
    attempts = [
        {"contract_id": "c1", "status": "OK", "run_id": "100", "ts": 1.0},
        {"contract_id": "c1", "status": "COMPILE_FAILED", "run_id": "200", "ts": 2.0},
    ]
    merged = merge_manifest(attempts)
    assert merged["c1"]["status"] == "OK"
    assert merged["c1"]["run_id"] == "100"


def test_ok_sticky_picks_latest_ok_among_multiple_ok_rows():
    attempts = [
        {"contract_id": "c1", "status": "OK", "run_id": "100", "ts": 1.0},
        {"contract_id": "c1", "status": "OK", "run_id": "200", "ts": 2.0},
    ]
    merged = merge_manifest(attempts)
    assert merged["c1"]["run_id"] == "200"


def test_skipped_resume_is_a_log_event_not_a_status():
    attempts = [
        {"contract_id": "c1", "status": "OK", "run_id": "100", "ts": 1.0},
        {"contract_id": "c1", "status": "SKIPPED_RESUME", "run_id": "200", "ts": 2.0},
    ]
    merged = merge_manifest(attempts)
    assert merged["c1"]["status"] == "OK"
    assert merged["c1"]["run_id"] == "100"


def test_skipped_resume_alone_never_creates_a_contract_row():
    attempts = [{"contract_id": "c1", "status": "SKIPPED_RESUME", "run_id": "100", "ts": 1.0}]
    merged = merge_manifest(attempts)
    assert merged == {}


def test_truncated_trailing_line_is_tolerated(tmp_path):
    log_path = tmp_path / "attempts.jsonl"
    good = json.dumps({"contract_id": "c1", "status": "OK", "run_id": "100", "ts": 1.0})
    log_path.write_text(good + "\n" + '{"contract_id": "c2", "status": "O')  # truncated mid-write
    attempts = read_attempts(log_path)
    assert len(attempts) == 1
    assert attempts[0]["contract_id"] == "c1"


def test_malformed_non_trailing_line_raises(tmp_path):
    from a4v.gnn.etl.manifest import CorruptAttemptLog

    log_path = tmp_path / "attempts.jsonl"
    good = json.dumps({"contract_id": "c1", "status": "OK", "run_id": "100", "ts": 1.0})
    log_path.write_text("not json at all\n" + good + "\n")
    with pytest.raises(CorruptAttemptLog):
        read_attempts(log_path)


def test_append_attempt_is_append_only(tmp_path):
    log_path = tmp_path / "attempts.jsonl"
    append_attempt(log_path, Attempt(contract_id="c1", status="OK", run_id="100", ts=1.0))
    append_attempt(log_path, Attempt(contract_id="c2", status="OK", run_id="100", ts=2.0))
    attempts = read_attempts(log_path)
    assert [a["contract_id"] for a in attempts] == ["c1", "c2"]


def test_write_manifest_is_deterministic_ordering(tmp_path):
    manifest_path = tmp_path / "manifest.jsonl"
    merged = {
        "zzz": {"contract_id": "zzz", "status": "OK", "run_id": "1", "ts": 1.0},
        "aaa": {"contract_id": "aaa", "status": "OK", "run_id": "1", "ts": 1.0},
    }
    write_manifest(manifest_path, merged)
    lines = manifest_path.read_text().splitlines()
    ids = [json.loads(l)["contract_id"] for l in lines]
    assert ids == ["aaa", "zzz"]
