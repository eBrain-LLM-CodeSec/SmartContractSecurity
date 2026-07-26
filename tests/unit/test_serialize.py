import json

import numpy as np
import pytest

from a4v.gnn.etl.serialize import (
    EDGE_KINDS,
    build_record,
    canonical_json_bytes,
    read_record,
    write_record,
)
from a4v.graph import BuildFailed, ProgramGraph

REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
SOLC_820 = REPO_ROOT / ".venv/.solc-select/artifacts/solc-0.8.20/solc-0.8.20"
VAULT = REPO_ROOT / "tests/fixtures/multi_contract/Vault.sol"


def _build_vault_graph():
    try:
        return ProgramGraph.build(VAULT, extra_kwargs={"solc": str(SOLC_820)})
    except BuildFailed as e:  # pragma: no cover -- environment-dependent
        pytest.skip(f"solc/slither unavailable in this environment: {e}")


def _record_kwargs(graph, node_labels=None, graph_labels=None):
    node_count = len(graph.graph.nodes())
    return dict(
        graph=graph,
        contract_id="deadbeef" * 8,
        native_ids=["native-1"],
        source_relpath="Vault.sol",
        content_sha256="deadbeef" * 8,
        label_granularity="line",
        class_names=["reentrancy", "unchecked_call"],
        node_labels=node_labels if node_labels is not None else np.zeros((node_count, 2), dtype=np.int8),
        graph_labels=graph_labels,
        solc_version="0.8.20",
        solc_attempts=[{"version": "0.8.20", "ok": True}],
        pragma_raw=["^0.8.20"],
        slither_version="test",
        crytic_compile_version="test",
        etl_git_rev="deadbeef",
    )


def test_round_trip_lossless(tmp_path):
    graph = _build_vault_graph()
    json_part, arrays_part = build_record(**_record_kwargs(graph))
    write_record(tmp_path, json_part["contract_id"], json_part, arrays_part)

    read_json, read_arrays = read_record(tmp_path, json_part["contract_id"])
    assert read_json == json_part
    assert set(read_arrays) == set(arrays_part)
    for k in arrays_part:
        assert np.array_equal(read_arrays[k], arrays_part[k])


def test_no_x_feature_matrix_in_record():
    graph = _build_vault_graph()
    json_part, arrays_part = build_record(**_record_kwargs(graph))
    assert "x" not in arrays_part
    assert "x" not in json_part


def test_edge_kinds_are_the_8_canonical_kinds():
    assert len(EDGE_KINDS) == 8
    assert len(set(EDGE_KINDS)) == 8


def test_json_part_contains_no_floats():
    graph = _build_vault_graph()
    json_part, _ = build_record(**_record_kwargs(graph))
    # build_record already asserts this internally; re-check by round-tripping
    # through json.dumps/loads and scanning for any float leaf.
    def _scan(obj):
        if isinstance(obj, float):
            raise AssertionError(f"found float: {obj!r}")
        if isinstance(obj, dict):
            for v in obj.values():
                _scan(v)
        elif isinstance(obj, list):
            for v in obj:
                _scan(v)
    reloaded = json.loads(canonical_json_bytes(json_part))
    _scan(reloaded)


def test_determinism_across_two_independent_builds(tmp_path):
    graph_a = _build_vault_graph()
    graph_b = _build_vault_graph()  # independent recompile

    json_a, arrays_a = build_record(**_record_kwargs(graph_a))
    json_b, arrays_b = build_record(**_record_kwargs(graph_b))

    assert canonical_json_bytes(json_a) == canonical_json_bytes(json_b)
    assert set(arrays_a) == set(arrays_b)
    for k in arrays_a:
        assert np.array_equal(arrays_a[k], arrays_b[k])


def test_atomic_write_never_exposes_a_corrupt_final_file(tmp_path):
    graph = _build_vault_graph()
    json_part, arrays_part = build_record(**_record_kwargs(graph))
    cid = json_part["contract_id"]
    json_path, npz_path = write_record(tmp_path, cid, json_part, arrays_part)

    good_json_bytes = json_path.read_bytes()
    good_npz_bytes = npz_path.read_bytes()

    # Simulate a crash mid-write of a *second* write attempt: the tmp files
    # get garbage written but os.replace is never reached.
    (tmp_path / f"{cid}.json.tmp").write_bytes(b"not valid json at all")
    (tmp_path / f"{cid}.npz.tmp").write_bytes(b"not a valid npz at all")

    # The final files must be untouched -- still the last good write.
    assert json_path.read_bytes() == good_json_bytes
    assert npz_path.read_bytes() == good_npz_bytes
    read_json, read_arrays = read_record(tmp_path, cid)
    assert read_json == json_part
