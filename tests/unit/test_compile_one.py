import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

from a4v.gnn.etl import compile_one
from a4v.gnn.etl.compile_one import run_job

REPO_ROOT = Path(__file__).resolve().parents[2]
SOLC_820 = REPO_ROOT / ".venv/.solc-select/artifacts/solc-0.8.20/solc-0.8.20"
CASTS = REPO_ROOT / "tests/fixtures/features/Casts.sol"
VAULT = REPO_ROOT / "tests/fixtures/multi_contract/Vault.sol"


def _global_version_path():
    import os
    install_dir = os.environ.get("SOLC_SELECT_INSTALL_DIR")
    base = Path(install_dir) if install_dir else Path.home() / ".solc-select"
    return base / "global-version"


def _base_job(target, contract_id, out_dir, **overrides):
    job = {
        "target": str(target),
        "candidates": [{"solc_version": "0.8.20", "solc_path": str(SOLC_820)}],
        "candidate_timeout_seconds": 30,
        "class_names": ["reentrancy"],
        "contract_id": contract_id,
        "native_ids": [contract_id],
        "source_relpath": target.name,
        "content_sha256": contract_id,
        "out_dir": str(out_dir),
        "pragma_raw": ["^0.8.20"],
        "slither_version": "test",
        "crytic_compile_version": "test",
        "etl_git_rev": "test",
    }
    job.update(overrides)
    return job


def test_compiles_casts_non_empty_graph_global_version_unchanged(tmp_path):
    gv_path = _global_version_path()
    existed_before = gv_path.exists()

    job = _base_job(CASTS, "casts1" * 8, tmp_path / "out")
    result = run_job(job)
    assert result["status"] == compile_one.STATUS_OK
    assert (tmp_path / "out" / f"{job['contract_id']}.json").exists()
    assert (tmp_path / "out" / f"{job['contract_id']}.npz").exists()

    assert gv_path.exists() == existed_before


def test_compiles_vault_non_empty_graph(tmp_path):
    job = _base_job(VAULT, "vault1" * 8, tmp_path / "out")
    result = run_job(job)
    assert result["status"] == compile_one.STATUS_OK
    record = json.loads((tmp_path / "out" / f"{job['contract_id']}.json").read_text())
    assert record["meta"]["node_count"] > 0


def test_skip_non_self_contained_short_circuits(tmp_path):
    job = _base_job(CASTS, "skip1" * 8, tmp_path / "out", skip_non_self_contained=True, candidates=[])
    result = run_job(job)
    assert result["status"] == compile_one.STATUS_SKIPPED_NONSELFCONTAINED
    assert result["solc_attempts"] == []


def test_solc_missing_candidate_recorded_and_skipped(tmp_path):
    job = _base_job(CASTS, "missing1" * 8, tmp_path / "out", candidates=[
        {"solc_version": "9.9.9", "solc_path": "/no/such/solc"},
        {"solc_version": "0.8.20", "solc_path": str(SOLC_820)},
    ])
    result = run_job(job)
    assert result["status"] == compile_one.STATUS_OK
    assert result["solc_attempts"][0]["status"] == compile_one.STATUS_SOLC_MISSING
    assert result["solc_attempts"][1]["status"] == compile_one.STATUS_OK


def test_candidate_timeout_does_not_consume_whole_budget(tmp_path, monkeypatch):
    calls = []

    class FakeGraph:
        def __init__(self):
            import networkx as nx
            self.graph = nx.MultiDiGraph()
            self.graph.add_node("fn::x", kind="function", name="x")

        def nodes_of_kind(self, kind):
            return ["fn::x"] if kind == "function" else []

    class FakeProgramGraph:
        @classmethod
        def build(cls, target, extra_kwargs=None):
            version = extra_kwargs["solc"]
            calls.append(version)
            if version.endswith("hang"):
                time.sleep(5)
            return FakeGraph()

    monkeypatch.setattr(compile_one, "ProgramGraph", FakeProgramGraph)
    hang_path = tmp_path / "hang"
    ok_path = tmp_path / "ok"
    hang_path.write_text("x")
    ok_path.write_text("x")

    job = _base_job(CASTS, "timeout1" * 8, tmp_path / "out", candidates=[
        {"solc_version": "v1", "solc_path": str(hang_path)},
        {"solc_version": "v2", "solc_path": str(ok_path)},
    ], candidate_timeout_seconds=1)

    start = time.monotonic()
    result = run_job(job)
    elapsed = time.monotonic() - start

    assert calls == [str(hang_path), str(ok_path)]
    assert result["status"] == compile_one.STATUS_OK
    assert result["solc_attempts"][0]["status"] == compile_one.STATUS_TIMEOUT
    assert result["solc_attempts"][1]["status"] == compile_one.STATUS_OK
    assert elapsed < 4  # proves the 5s hang was cut short by the 1s per-candidate alarm


def test_empty_graph_status_when_zero_function_nodes(tmp_path, monkeypatch):
    class FakeGraph:
        def nodes_of_kind(self, kind):
            return []

    class FakeProgramGraph:
        @classmethod
        def build(cls, target, extra_kwargs=None):
            return FakeGraph()

    monkeypatch.setattr(compile_one, "ProgramGraph", FakeProgramGraph)
    job = _base_job(CASTS, "empty1" * 8, tmp_path / "out")
    result = run_job(job)
    assert result["status"] == compile_one.STATUS_EMPTY_GRAPH


def test_two_concurrent_subprocesses_do_not_cross_talk(tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    job_casts = _base_job(CASTS, "conc" + "a" * 60, out_dir)
    job_vault = _base_job(VAULT, "conc" + "b" * 60, out_dir)

    job_casts_path = tmp_path / "job_casts.json"
    job_vault_path = tmp_path / "job_vault.json"
    result_casts_path = tmp_path / "result_casts.json"
    result_vault_path = tmp_path / "result_vault.json"
    job_casts_path.write_text(json.dumps(job_casts))
    job_vault_path.write_text(json.dumps(job_vault))

    env_cmd = [sys.executable, "-m", "a4v.gnn.etl.compile_one"]
    p1 = subprocess.Popen(env_cmd + [str(job_casts_path), str(result_casts_path)], cwd=REPO_ROOT)
    p2 = subprocess.Popen(env_cmd + [str(job_vault_path), str(result_vault_path)], cwd=REPO_ROOT)
    rc1 = p1.wait(timeout=60)
    rc2 = p2.wait(timeout=60)

    assert rc1 == 0
    assert rc2 == 0
    result_casts = json.loads(result_casts_path.read_text())
    result_vault = json.loads(result_vault_path.read_text())
    assert result_casts["status"] == compile_one.STATUS_OK
    assert result_vault["status"] == compile_one.STATUS_OK

    record_casts = json.loads((out_dir / f"{job_casts['contract_id']}.json").read_text())
    record_vault = json.loads((out_dir / f"{job_vault['contract_id']}.json").read_text())
    casts_names = {a.get("name") for a in record_casts["node_attrs"]}
    vault_names = {a.get("name") for a in record_vault["node_attrs"]}
    assert "unsafeCast" in casts_names
    assert "unsafeCast" not in vault_names
    assert "setOracle" in vault_names
    assert "setOracle" not in casts_names
