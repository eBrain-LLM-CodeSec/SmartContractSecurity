"""A8 -- feasibility report & decision (see plan A8).

The deliverable that decides Part B. Reports the **full funnel as counts**,
never a single conflated rate (a bare "60% mapping" is uninterpretable
because it mixes compile loss with mapping loss).

This module's `compute_feasibility` is pure aggregation over a list of
per-contract `ContractOutcome` summaries -- it doesn't touch disk. The glue
that builds those summaries from the real manifest + serialized records
(`data/gnn/manifests/manifest.jsonl`, `data/gnn/processed/<id>.json`) lives
in `scripts/etl/run_sample.py`'s reporting step, since it's an I/O-heavy
join over live pipeline state that isn't meaningfully unit-testable without
the real Part-A run.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ContractOutcome:
    contract_id: str
    labeled: bool = False
    label_granularity: str = "none"
    compile_status: str = "OK"
    solc_version: str | None = None
    node_mapped: bool = False
    # class -> True if >=1 node captured that ground-truth-positive class,
    # False if the class was ground-truth-positive but never mapped to any
    # node. Only classes this contract is ground-truth-positive for appear
    # as keys.
    per_class_mapped: dict[str, bool] = field(default_factory=dict)
    node_count: int = 0
    edge_count: int = 0
    empty_graph: bool = False
    label_conflict: bool = False
    disconnected: bool = False

    @property
    def compiled_ok(self) -> bool:
        return self.compile_status == "OK"


STRANDING_STATUSES = {"SOLC_MISSING", "UNRESOLVED_DEPS"}


def _rate(numerator: int, denominator: int) -> float | None:
    return (numerator / denominator) if denominator else None


def compute_feasibility(
    outcomes: list[ContractOutcome],
    class_names: list[str],
    cell_counts: dict[str, int],
    self_contained_rate: float,
    non_self_contained_count: int,
) -> dict:
    sampled = len(outcomes)
    labeled = sum(1 for o in outcomes if o.labeled)
    compiled_ok = sum(1 for o in outcomes if o.compiled_ok)
    labeled_and_compiled = [o for o in outcomes if o.labeled and o.compiled_ok]
    node_mapped = sum(1 for o in labeled_and_compiled if o.node_mapped)

    funnel = {
        "sampled": sampled,
        "labeled": labeled,
        "compiled_ok": compiled_ok,
        "labeled_and_compiled": len(labeled_and_compiled),
        "node_mapped": node_mapped,
    }

    by_version: dict[str, dict[str, int]] = {}
    for o in outcomes:
        if not o.solc_version:
            continue
        major_minor = ".".join(o.solc_version.split(".")[:2])
        bucket = by_version.setdefault(major_minor, {"attempted": 0, "ok": 0})
        bucket["attempted"] += 1
        if o.compiled_ok:
            bucket["ok"] += 1
    compile_success_by_version = {
        v: {"attempted": b["attempted"], "ok": b["ok"], "rate": _rate(b["ok"], b["attempted"])}
        for v, b in sorted(by_version.items())
    }

    stranded = sum(1 for o in outcomes if o.compile_status in STRANDING_STATUSES)

    per_class_mapping: dict[str, dict] = {}
    for c in class_names:
        denom = sum(1 for o in labeled_and_compiled if c in o.per_class_mapped)
        num = sum(1 for o in labeled_and_compiled if o.per_class_mapped.get(c))
        per_class_mapping[c] = {"mapped": num, "labeled_and_compiled": denom, "rate": _rate(num, denom)}

    empty_graph_count = sum(1 for o in outcomes if o.empty_graph)
    label_conflict_count = sum(1 for o in outcomes if o.label_conflict)
    disconnected_count = sum(1 for o in outcomes if o.disconnected)

    ok_outcomes = [o for o in outcomes if o.compiled_ok]
    graph_stats = {
        "avg_node_count": (sum(o.node_count for o in ok_outcomes) / len(ok_outcomes)) if ok_outcomes else None,
        "avg_edge_count": (sum(o.edge_count for o in ok_outcomes) / len(ok_outcomes)) if ok_outcomes else None,
        "disconnected_share": _rate(disconnected_count, len(ok_outcomes)),
    }

    return {
        "funnel": funnel,
        "cell_counts": dict(cell_counts),
        "compile_success_rate": _rate(compiled_ok, sampled),
        "compile_success_by_version": compile_success_by_version,
        "old_solc_stranding_rate": _rate(stranded, sampled),
        "annotation_mapping_rate": _rate(node_mapped, len(labeled_and_compiled)),
        "annotation_mapping_numerator": node_mapped,
        "annotation_mapping_denominator": len(labeled_and_compiled),
        "per_class_mapping": per_class_mapping,
        "label_conflict_count": label_conflict_count,
        "self_contained_rate": self_contained_rate,
        "non_self_contained_count": non_self_contained_count,
        "empty_graph_count": empty_graph_count,
        "graph_stats": graph_stats,
    }
