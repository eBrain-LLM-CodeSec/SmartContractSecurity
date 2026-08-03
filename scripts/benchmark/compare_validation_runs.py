"""Phase 6: compares N independent cold-start validation runs (each a
directory produced by run_three_validations.sh, containing study_full/*.jsonl
+ feasibility_report.json + audit_order.json + environment-manifest.json)
and reports every mismatch explicitly -- per this task's own instruction,
this script never averages or silently ignores a difference between runs.

`python -m scripts.benchmark.compare_validation_runs <run_dir_1> <run_dir_2> <run_dir_3> [--out report.json]`
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def _build_status_by_audit(run_dir: Path) -> dict[str, dict]:
    rows = _read_jsonl(run_dir / "study_full" / "build_manifest.jsonl")
    # Last row per audit_id wins (build_manifest.jsonl is rewritten
    # cumulatively after every audit during the run, so the file's final
    # state already has exactly one row per audit -- this dedup is a
    # defensive no-op for that case, and the correct behavior if it were
    # ever appended instead).
    by_audit: dict[str, dict] = {}
    for r in rows:
        by_audit[r["audit_id"]] = r
    return by_audit


def _graph_node_counts_by_audit(run_dir: Path) -> dict[str, dict]:
    rows = _read_jsonl(run_dir / "study_full" / "graph_manifest.jsonl")
    by_audit: dict[str, dict] = {}
    for r in rows:
        by_audit[r["audit_id"]] = r.get("node_counts", {})
    return by_audit


def load_run(run_dir: Path) -> dict:
    build = _build_status_by_audit(run_dir)
    graphs = _graph_node_counts_by_audit(run_dir)
    feasibility_path = run_dir / "study_full" / "feasibility_report.json"
    feasibility = json.loads(feasibility_path.read_text()) if feasibility_path.exists() else {}
    order_path = run_dir / "study_full" / "audit_order.json"
    order = json.loads(order_path.read_text()) if order_path.exists() else {}
    route_rows = _read_jsonl(run_dir / "study_full" / "route_manifest.jsonl")
    gate_rows = _read_jsonl(run_dir / "study_full" / "gate_evaluation.jsonl")
    return {
        "run_dir": str(run_dir),
        "build_status_by_audit": {a: r.get("status") for a, r in build.items()},
        "failure_reason_by_audit": {a: r.get("reason") for a, r in build.items() if r.get("status") != "COMPILED"},
        "compiler_selection_by_audit": {a: r.get("compiler_selection") for a, r in build.items()},
        "graph_node_counts_by_audit": graphs,
        "feasibility_report": feasibility,
        "audit_order": order.get("order"),
        "audit_order_seed": order.get("seed"),
        "route_manifest_row_count": len(route_rows),
        "gate_evaluation_row_count": len(gate_rows),
    }


def compare(runs: list[dict]) -> dict:
    mismatches: list[dict] = []
    labels = [r["run_dir"] for r in runs]

    all_audits = sorted(set().union(*(r["build_status_by_audit"].keys() for r in runs)))
    for audit_id in all_audits:
        statuses = [r["build_status_by_audit"].get(audit_id) for r in runs]
        if len(set(statuses)) > 1:
            mismatches.append({
                "kind": "build_status", "audit_id": audit_id,
                "values": dict(zip(labels, statuses)),
            })
            continue  # a status mismatch makes node-count/compiler comparison meaningless for this audit
        if statuses[0] != "COMPILED":
            continue

        counts = [r["graph_node_counts_by_audit"].get(audit_id) for r in runs]
        if len(set(json.dumps(c, sort_keys=True) for c in counts)) > 1:
            mismatches.append({
                "kind": "graph_node_counts", "audit_id": audit_id,
                "values": dict(zip(labels, counts)),
            })

        selections = [r["compiler_selection_by_audit"].get(audit_id) for r in runs]
        if len(set(json.dumps(s, sort_keys=True) for s in selections)) > 1:
            mismatches.append({
                "kind": "compiler_selection", "audit_id": audit_id,
                "values": dict(zip(labels, selections)),
            })

    compiled_sets = [set(a for a, s in r["build_status_by_audit"].items() if s == "COMPILED") for r in runs]
    if len(set(frozenset(s) for s in compiled_sets)) > 1:
        mismatches.append({
            "kind": "compiled_audit_set", "audit_id": None,
            "values": {labels[i]: sorted(compiled_sets[i]) for i in range(len(runs))},
        })

    route_counts = [r["route_manifest_row_count"] for r in runs]
    if len(set(route_counts)) > 1:
        mismatches.append({"kind": "route_manifest_row_count", "audit_id": None,
                            "values": dict(zip(labels, route_counts))})

    gate_counts = [r["gate_evaluation_row_count"] for r in runs]
    if len(set(gate_counts)) > 1:
        mismatches.append({"kind": "gate_evaluation_row_count", "audit_id": None,
                            "values": dict(zip(labels, gate_counts))})

    findings_reached = [r["feasibility_report"].get("findings_reached_compiled_audits") for r in runs]
    if len(set(findings_reached)) > 1:
        mismatches.append({"kind": "findings_reached_compiled_audits", "audit_id": None,
                            "values": dict(zip(labels, findings_reached))})

    orders = [r["audit_order"] for r in runs]
    orders_are_distinct = len(set(tuple(o) for o in orders if o)) == len([o for o in orders if o])

    return {
        "runs_compared": labels,
        "identical_coverage_and_graph_counts": not any(
            m["kind"] in ("build_status", "graph_node_counts", "compiled_audit_set") for m in mismatches
        ),
        "audit_orders_were_genuinely_randomized_and_distinct": orders_are_distinct,
        "mismatches": mismatches,
        "mismatch_count": len(mismatches),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dirs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    runs = [load_run(d) for d in args.run_dirs]
    result = compare(runs)

    print(json.dumps({k: v for k, v in result.items() if k != "mismatches"}, indent=2))
    if result["mismatches"]:
        print(f"\n{result['mismatch_count']} MISMATCH(ES) FOUND:")
        for m in result["mismatches"]:
            print(f"  [{m['kind']}] audit_id={m['audit_id']}: {json.dumps(m['values'])}")
    else:
        print("\nNo mismatches across all compared runs.")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True))
        print(f"\n-> {args.out}")

    return 1 if result["mismatches"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
