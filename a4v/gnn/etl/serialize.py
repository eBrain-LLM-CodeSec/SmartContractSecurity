"""A6 -- raw graph serialization (see plan A6).

Serializes a real `ProgramGraph` + its label mapping (from `map_labels.py`)
into a content-addressed pair of files per contract: `<contract_id>.npz`
(arrays only) + `<contract_id>.json` (everything else, canonical). No
sharding at Part-A's 200-contract scale -- loose files.

Deliberately **no feature matrix `x`** -- PageRank/centrality/
`FeatureExtractor` outputs are a downstream, versioned modeling transform
(Part B), not extraction.

Determinism is **content-level, not byte-level** (npz is a ZIP whose entry
headers embed a timestamp; JSON float formatting is locale-sensitive):
- The JSON side is written canonically (`sort_keys=True,
  separators=(",", ":"), ensure_ascii=True`) and contains **only ints and
  strings** -- no floats anywhere (arrays live in the npz; meta values are
  version strings/counts) -- which makes canonical determinism trivially
  true.
- The npz side is compared by loaded array equality (`np.array_equal` per
  key), never raw bytes.

Both files are written **atomically** (`tmp` + `os.replace` on the same
filesystem) so a crash mid-write can never leave a corrupt final file.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from a4v.graph import (
    CALLS, DECLARES, EXTERNAL_CALL, INHERITS, STATE_READ, STATE_WRITE,
    USES_MODIFIER, WRITE_AFTER_EXTERNAL_CALL,
)

SCHEMA_VERSION = "1"
CLASS_VOCAB_VERSION = "1"

# The 8 canonical edge kinds graph.py emits -- fixed column order for edge_type.
EDGE_KINDS: list[str] = [
    CALLS, INHERITS, USES_MODIFIER, STATE_READ, STATE_WRITE,
    EXTERNAL_CALL, WRITE_AFTER_EXTERNAL_CALL, DECLARES,
]
_EDGE_KIND_INDEX = {k: i for i, k in enumerate(EDGE_KINDS)}


class NonCanonicalRecord(ValueError):
    pass


def _check_json_safe(obj, path: str = "$") -> None:
    """No floats anywhere in the JSON part -- arrays (which may be float
    dtype in a future feature stage, though not in Part A) never belong
    here; catching an accidental float early is cheap insurance.
    """
    if isinstance(obj, float):
        raise NonCanonicalRecord(f"float found in JSON record at {path} (arrays belong in the npz)")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _check_json_safe(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _check_json_safe(v, f"{path}[{i}]")


def build_record(
    graph,
    *,
    contract_id: str,
    native_ids: list[str],
    source_relpath: str,
    content_sha256: str,
    label_granularity: str,
    class_names: list[str],
    node_labels: np.ndarray | None,
    graph_labels: np.ndarray | None,
    solc_version: str | None,
    solc_attempts: list[dict],
    pragma_raw: list[str],
    slither_version: str,
    crytic_compile_version: str,
    etl_git_rev: str,
) -> tuple[dict, dict]:
    """Returns (json_part, arrays_part) -- see module docstring for the
    JSON-vs-npz split. `graph` is anything exposing `.graph` (a networkx
    MultiDiGraph with graph.py's node/edge attribute conventions) -- a real
    `ProgramGraph` in production, a duck-typed fake in tests.
    """
    node_ids = list(graph.graph.nodes())
    node_attrs = [dict(graph.graph.nodes[n]) for n in node_ids]
    row_by_id = {nid: i for i, nid in enumerate(node_ids)}

    edges = list(graph.graph.edges(data=True))
    edge_index = np.zeros((2, len(edges)), dtype=np.int64)
    edge_type = np.zeros(len(edges), dtype=np.int64)
    for i, (u, v, data) in enumerate(edges):
        edge_index[0, i] = row_by_id[u]
        edge_index[1, i] = row_by_id[v]
        edge_type[i] = _EDGE_KIND_INDEX[data["kind"]]

    json_part = {
        "schema_version": SCHEMA_VERSION,
        "class_vocab_version": CLASS_VOCAB_VERSION,
        "contract_id": contract_id,
        "native_ids": list(native_ids),
        "source_relpath": source_relpath,
        "content_sha256": content_sha256,
        "node_ids": node_ids,
        "node_attrs": node_attrs,
        "edge_kinds": EDGE_KINDS,
        "labels": {
            "granularity": label_granularity,
            "class_names": list(class_names),
        },
        "meta": {
            "solc_version": solc_version,
            "solc_attempts": solc_attempts,
            "pragma_raw": list(pragma_raw),
            "slither_version": slither_version,
            "crytic_compile_version": crytic_compile_version,
            "node_count": len(node_ids),
            "edge_count": len(edges),
            "etl_git_rev": etl_git_rev,
        },
    }
    _check_json_safe(json_part)

    arrays_part: dict[str, np.ndarray] = {
        "edge_index": edge_index,
        "edge_type": edge_type,
    }
    if node_labels is not None:
        arrays_part["node_labels"] = node_labels.astype(np.int8)
    if graph_labels is not None:
        arrays_part["graph_labels"] = graph_labels.astype(np.int8)

    return json_part, arrays_part


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def canonical_json_bytes(json_part: dict) -> bytes:
    return json.dumps(
        json_part, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")


def write_record(out_dir: Path, contract_id: str, json_part: dict, arrays_part: dict) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{contract_id}.json"
    npz_path = out_dir / f"{contract_id}.npz"

    _atomic_write_bytes(json_path, canonical_json_bytes(json_part))

    npz_tmp = npz_path.with_suffix(".npz.tmp")
    # np.savez appends ".npz" to its target if given a bare path/string that
    # doesn't already end in ".npz" -- pass an open file handle instead so
    # our ".npz.tmp" name is used exactly (no silent ".npz.tmp.npz").
    with npz_tmp.open("wb") as f:
        np.savez(f, **arrays_part)
        f.flush()
        os.fsync(f.fileno())
    os.replace(npz_tmp, npz_path)

    return json_path, npz_path


def read_record(out_dir: Path, contract_id: str) -> tuple[dict, dict]:
    json_path = out_dir / f"{contract_id}.json"
    npz_path = out_dir / f"{contract_id}.npz"
    json_part = json.loads(json_path.read_text())
    with np.load(npz_path) as npz:
        arrays_part = {k: npz[k] for k in npz.files}
    return json_part, arrays_part
