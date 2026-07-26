"""A2 -- mapping parsed labels onto graph nodes (see plan A2).

The piece the prior draft left homeless: `map_to_nodes(label_record, graph,
class_names)` turns a `LabelRecord` (labels.py's output) into a per-class,
per-node label matrix over a real `ProgramGraph`.

Rules (per plan):
- **Line-granularity**: a node is positive for class `c` iff the
  annotation's **file matches the node's `file` attr** *and* its line range
  overlaps the node's `lines` -- file-match first, so a line from file A
  never lights up a node in file B. Nodes with missing `file`/`lines` (ext
  stubs, the write-after-external-call fallback statevar) are unmappable.
- **Function-granularity**, keyed by name: key on `(contract, name,
  signature)` where available, not bare name, to avoid overload / base-
  derived same-name collisions. If an annotation doesn't carry a signature,
  fall back to `(contract, name)` **only if that combination is unambiguous**
  among the graph's function nodes; otherwise log it as ambiguous and skip
  (never silently pick one).
- **File-granularity**: no node mapping; only `graph_labels` (file-level
  multi-hot) is set.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from a4v.gnn.etl.labels import Annotation, LabelRecord


def _node_signature(canonical_name: str | None) -> str | None:
    if not canonical_name or "(" not in canonical_name:
        return None
    return canonical_name[canonical_name.index("("):]


def _is_mappable_file_line_node(attrs: dict) -> bool:
    return bool(attrs.get("file")) and bool(attrs.get("lines"))


def _lines_overlap(a: tuple[int, ...], b: list[int] | tuple[int, ...]) -> bool:
    if not a or not b:
        return False
    b_set = set(b)
    return any(ln in b_set for ln in a)


@dataclass
class AmbiguousMatch:
    annotation_index: int
    contract: str | None
    function_name: str | None
    candidate_node_ids: list[str]


@dataclass
class MappingResult:
    node_ids: list[str]
    class_names: list[str]
    node_labels: np.ndarray | None  # i8[N, C], or None at file granularity
    graph_labels: np.ndarray | None  # i8[C], or None when node-mapped
    ambiguous: list[AmbiguousMatch] = field(default_factory=list)
    unmappable_annotation_count: int = 0


def _build_function_index(
    node_ids: list[str], attrs_by_id: dict[str, dict]
) -> tuple[dict[tuple, list[str]], dict[tuple, list[str]]]:
    """Returns (by_full_key, by_name_only):
    - `by_full_key`: (contract, name, signature) -> [node_id, ...], keyed
      only by each node's *actual* (possibly-None) signature -- an exact
      match here means the annotation's signature (if any) matched a real
      node signature, never a None-to-None coincidence.
    - `by_name_only`: (contract, name) -> [node_id, ...], used only for the
      explicit no-signature fallback, so ambiguity there is judged against
      every overload, not silently short-circuited by the full-key index.
    """
    by_full_key: dict[tuple, list[str]] = {}
    by_name_only: dict[tuple, list[str]] = {}
    for nid in node_ids:
        attrs = attrs_by_id[nid]
        if attrs.get("kind") != "function":
            continue
        contract = attrs.get("contract")
        name = attrs.get("name")
        sig = _node_signature(attrs.get("canonical_name"))
        by_full_key.setdefault((contract, name, sig), []).append(nid)
        by_name_only.setdefault((contract, name), []).append(nid)
    return by_full_key, by_name_only


def map_to_nodes(label_record: LabelRecord, graph, class_names: list[str]) -> MappingResult:
    node_ids = list(graph.graph.nodes())
    attrs_by_id = {nid: graph.graph.nodes[nid] for nid in node_ids}
    class_index = {c: i for i, c in enumerate(class_names)}

    if label_record.granularity == "file":
        graph_labels = np.zeros(len(class_names), dtype=np.int8)
        for ann in label_record.annotations:
            if ann.vuln_class in class_index:
                graph_labels[class_index[ann.vuln_class]] = 1
        return MappingResult(
            node_ids=node_ids,
            class_names=class_names,
            node_labels=None,
            graph_labels=graph_labels,
        )

    node_labels = np.zeros((len(node_ids), len(class_names)), dtype=np.int8)
    row_by_id = {nid: i for i, nid in enumerate(node_ids)}
    ambiguous: list[AmbiguousMatch] = []
    unmappable = 0
    if label_record.granularity == "function":
        func_by_full_key, func_by_name_only = _build_function_index(node_ids, attrs_by_id)
    else:
        func_by_full_key, func_by_name_only = {}, {}

    for i, ann in enumerate(label_record.annotations):
        if ann.vuln_class not in class_index:
            continue
        col = class_index[ann.vuln_class]

        if ann.granularity == "line":
            matched_any = False
            for row, nid in enumerate(node_ids):
                attrs = attrs_by_id[nid]
                if not _is_mappable_file_line_node(attrs):
                    continue
                if attrs["file"] != ann.file:
                    continue  # file-match first: never bleed across files
                if _lines_overlap(ann.lines, attrs["lines"]):
                    node_labels[row, col] = 1
                    matched_any = True
            if not matched_any:
                unmappable += 1

        elif ann.granularity == "function":
            candidates = None
            if ann.signature is not None:
                candidates = func_by_full_key.get((ann.contract, ann.function_name, ann.signature))
                if candidates is None:
                    # Signature was given but matched no real node -- do not
                    # fall back to name-only guessing; a wrong/stale
                    # signature is an unmappable annotation, not an
                    # ambiguity to resolve by dropping the caller's signal.
                    unmappable += 1
                    continue
            else:
                # No signature given -- try the (contract, name) bucket, but
                # only if it's unambiguous (exactly one distinct node);
                # never guess among overloads/base-derived collisions.
                bucket = func_by_name_only.get((ann.contract, ann.function_name), [])
                distinct = sorted(set(bucket))
                if len(distinct) == 1:
                    candidates = distinct
                elif len(distinct) > 1:
                    ambiguous.append(AmbiguousMatch(
                        annotation_index=i, contract=ann.contract,
                        function_name=ann.function_name, candidate_node_ids=distinct,
                    ))
                    continue
            if not candidates:
                unmappable += 1
                continue
            for nid in set(candidates):
                node_labels[row_by_id[nid], col] = 1

        else:  # pragma: no cover -- file-granularity annotations shouldn't reach here
            unmappable += 1

    return MappingResult(
        node_ids=node_ids,
        class_names=class_names,
        node_labels=node_labels,
        graph_labels=None,
        ambiguous=ambiguous,
        unmappable_annotation_count=unmappable,
    )
