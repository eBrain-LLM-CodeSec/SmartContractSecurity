"""A8 CLI: builds the real `feasibility.json` from the merged manifest +
serialized records + full index (see plan A8). Login-node safe (just reads
already-produced state, no compilation).

`python -m scripts.etl.build_feasibility_report <sample_json>
    <full_index_jsonl> <manifest_jsonl> <processed_dir>
    [--out data/gnn/reports/feasibility.json]`

**Headline honesty note** (this is the actual go/no-go signal, not a detail):
Resource 2's real labels are **file-granularity** (confirmed:
`data/gnn/raw/MANIFEST.md`). Per the plan's A2 semantics, file-granularity
sets only `graph_labels` -- `node_labels` is `None`, i.e. **zero node-level
mapping under the strict letter of the spec**, so the strict
`annotation_mapping_rate` below is 0% by construction, not a compile
failure. Separately reported: `single_function_contract_rate` -- the
fraction of successfully-compiled contracts with **exactly one** function
node (confirmed common in this corpus -- see MANIFEST.md finding 2). For
those, the file-level label unambiguously identifies the one function it
must refer to; A2's `map_labels.py` does not currently implement this
inference (kept strict to the plan's spec deliberately), but this number is
what the go/no-go decision should actually weigh -- not the literal 0%.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from a4v.gnn.etl.report import ContractOutcome, compute_feasibility

# Slither synthesizes bookkeeping functions with these exact names on nearly
# every contract that declares state variables (regardless of whether they
# have inline initializers) -- not real source-level functions. External
# call targets also show up as `kind="function"` nodes (`external=True` /
# `ext::` id prefix, per graph.py -- confirmed in Part 0). Both must be
# excluded when counting "real declared functions per file", or the count is
# dominated by this noise rather than the file's actual function.
_SLITHER_SYNTHETIC_FUNCTION_NAMES = {"slitherConstructorVariables", "slitherConstructorConstantVariables"}


def _real_declared_function_count(node_ids: list[str], node_attrs: list[dict]) -> int:
    count = 0
    for nid, attrs in zip(node_ids, node_attrs):
        if attrs.get("kind") != "function":
            continue
        if attrs.get("external") or nid.startswith("ext::"):
            continue
        if attrs.get("name") in _SLITHER_SYNTHETIC_FUNCTION_NAMES:
            continue
        count += 1
    return count


def _is_disconnected(node_count: int, edge_index: np.ndarray) -> bool:
    if node_count <= 1:
        return False
    # Cheap undirected-connectivity check via union-find over edge_index.
    parent = list(range(node_count))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(edge_index.shape[1]):
        a, b = int(edge_index[0, i]), int(edge_index[1, i])
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    roots = {find(i) for i in range(node_count)}
    return len(roots) > 1


def build_outcomes(
    sample_ids: list[str],
    index_rows_by_id: dict[str, dict],
    manifest_by_id: dict[str, dict],
    processed_dir: Path,
) -> tuple[list[ContractOutcome], int]:
    outcomes: list[ContractOutcome] = []
    single_function_count = 0

    for cid in sample_ids:
        row = index_rows_by_id.get(cid, {})
        manifest_row = manifest_by_id.get(cid)
        status = manifest_row["status"] if manifest_row else "UNRESOLVED_DEPS"
        merged_classes = row.get("merged_classes", [])
        labeled = bool(merged_classes)

        outcome = ContractOutcome(
            contract_id=cid,
            labeled=labeled,
            compile_status=status,
            label_conflict=row.get("label_conflict", False),
        )

        if status == "OK":
            json_path = processed_dir / f"{cid}.json"
            npz_path = processed_dir / f"{cid}.npz"
            record = json.loads(json_path.read_text())
            outcome.label_granularity = record["labels"]["granularity"]
            outcome.node_count = record["meta"]["node_count"]
            outcome.edge_count = record["meta"]["edge_count"]
            outcome.empty_graph = record["meta"]["node_count"] == 0
            solc_versions = [a["version"] for a in record["meta"]["solc_attempts"] if a.get("ok")]
            outcome.solc_version = solc_versions[0] if solc_versions else None

            fn_count = _real_declared_function_count(record["node_ids"], record["node_attrs"])
            if fn_count == 1:
                single_function_count += 1

            with np.load(npz_path) as npz:
                if "node_labels" in npz and npz["node_labels"] is not None:
                    node_labels = npz["node_labels"]
                    outcome.node_mapped = bool(node_labels.sum() > 0)
                    for i, c in enumerate(record["labels"]["class_names"]):
                        if c in merged_classes:
                            outcome.per_class_mapped[c] = bool(node_labels[:, i].sum() > 0)
                elif "graph_labels" in npz:
                    for c in merged_classes:
                        outcome.per_class_mapped[c] = False  # graph-level only, never node-mapped

                if "edge_index" in npz:
                    outcome.disconnected = _is_disconnected(outcome.node_count, npz["edge_index"])

        outcomes.append(outcome)

    return outcomes, single_function_count


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sample_json", type=Path)
    ap.add_argument("full_index_jsonl", type=Path)
    ap.add_argument("manifest_jsonl", type=Path)
    ap.add_argument("processed_dir", type=Path)
    ap.add_argument("--out", type=Path, default=Path("data/gnn/reports/feasibility.json"))
    ap.add_argument("--class-names", nargs="*",
                     default=["reentrancy", "timestamp", "Integeroverflow", "delegatecall"])
    args = ap.parse_args(argv)

    sample = json.loads(args.sample_json.read_text())
    sample_ids = sample["contract_ids"]

    index_rows_by_id = {}
    for line in args.full_index_jsonl.read_text().splitlines():
        row = json.loads(line)
        index_rows_by_id[row["contract_id"]] = row

    manifest_by_id = {}
    for line in args.manifest_jsonl.read_text().splitlines():
        row = json.loads(line)
        manifest_by_id[row["contract_id"]] = row

    outcomes, single_function_count = build_outcomes(
        sample_ids, index_rows_by_id, manifest_by_id, args.processed_dir,
    )

    report = compute_feasibility(
        outcomes,
        class_names=args.class_names,
        cell_counts=sample.get("cell_counts", {}),
        self_contained_rate=1.0,
        non_self_contained_count=0,
    )
    ok_count = sum(1 for o in outcomes if o.compiled_ok)
    report["single_function_contract_count"] = single_function_count
    report["single_function_contract_rate"] = single_function_count / ok_count if ok_count else None
    report["headline_note"] = (
        "annotation_mapping_rate is 0% under the plan's strict A2 semantics: "
        "Resource 2's real labels are file-granularity, and file-granularity "
        "sets only graph_labels (no node_labels), per spec. "
        "single_function_contract_rate is the number that should actually "
        "inform go/no-go: the fraction of compiled contracts with exactly "
        "one function node, where the file-level label unambiguously "
        "identifies that one function -- map_labels.py does not implement "
        "this inference yet (kept strict deliberately), but it is a well-"
        "defined, low-risk extension if Part B is greenlit."
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"\n-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
