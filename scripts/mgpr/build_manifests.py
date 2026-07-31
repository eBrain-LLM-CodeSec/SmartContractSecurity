"""MGPR M6 CLI: attempts a real compile of each registry audit's local
checkout (if available) and records build_manifest.jsonl / graph_manifest.jsonl
entries -- reusing a4v.repair.EnvRepair's existing bounded solc-repair loop,
not reimplementing it. Audits without an available local checkout are
recorded as SKIPPED, not silently omitted (plan section 6.2) -- cloning the
other pinned audits from GitHub is deliberately NOT done by this script
(see the MGPR plan's implementation-status note: this account's file-count
quota is tight, and bulk-cloning full smart-contract repos risks recreating
the exact problem that was just cleaned up). This script takes a
`--checkouts-dir` of whatever local checkouts already exist instead.

`python -m scripts.mgpr.build_manifests data/mgpr/benchmark_registry.jsonl
    --checkouts-dir /path/to/extracted/checkouts [--out-dir data/mgpr]`
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import yaml

from a4v.graph import BuildFailed, ProgramGraph
from a4v.repair import EnvRepair

_DEFAULT_EVMBENCH_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")
_AGENT4VUL_ROOT = Path("/scratch/md5344/evmbench/agent4vul")


def _run_cmd_dir(evmbench_root: Path, audit_id: str) -> str:
    """Each audit's own config.yaml may point the actual Foundry project
    root at a subdirectory of the checkout (e.g. pooltogether's `vault/`)
    rather than the checkout root itself."""
    config_path = evmbench_root / "audits" / audit_id / "config.yaml"
    if not config_path.exists():
        return "."
    data = yaml.safe_load(config_path.read_text()) or {}
    return data.get("run_cmd_dir", ".")


def _node_edge_counts(pg: ProgramGraph) -> tuple[dict, dict]:
    node_counts: dict[str, int] = {}
    for _, d in pg.graph.nodes(data=True):
        kind = d.get("kind", "unknown")
        node_counts[kind] = node_counts.get(kind, 0) + 1
    edge_counts: dict[str, int] = {}
    for _, _, d in pg.graph.edges(data=True):
        kind = d.get("kind", "unknown")
        edge_counts[kind] = edge_counts.get(kind, 0) + 1
    return node_counts, edge_counts


def build_manifest_for_audit(
    audit_id: str, evmbench_root: Path, checkouts_dir: Path | None, repair: EnvRepair,
) -> tuple[dict, dict, ProgramGraph | None]:
    """Returns (build_manifest_row, graph_manifest_row, ProgramGraph|None).
    The ProgramGraph itself is returned, not serialized -- a caller in the
    same process (run_feasibility_study.py) can reuse it directly without
    recompiling. graph_manifest.jsonl only ever records metadata (node/edge
    kind counts), never the graph.
    """
    checkout_root = (checkouts_dir / audit_id) if checkouts_dir else None
    if checkout_root is None or not checkout_root.exists():
        return (
            {"audit_id": audit_id, "status": "SKIPPED", "reason": "no local checkout available",
             "solc_version": None, "repair_attempts": 0},
            {"audit_id": audit_id, "status": "SKIPPED", "node_counts": {}, "edge_counts": {},
             "unresolved_counts": {}},
            None,
        )

    target = checkout_root / _run_cmd_dir(evmbench_root, audit_id)
    try:
        result = repair.build_until_success(target)
    except BuildFailed as e:
        return (
            {"audit_id": audit_id, "status": "COMPILE_FAILED", "reason": str(e)[:2000],
             "solc_version": None, "repair_attempts": 0},
            {"audit_id": audit_id, "status": "COMPILE_FAILED", "node_counts": {}, "edge_counts": {},
             "unresolved_counts": {}},
            None,
        )

    node_counts, edge_counts = _node_edge_counts(result.graph)
    return (
        {"audit_id": audit_id, "status": "COMPILED", "reason": None,
         "solc_version": result.solc_version, "repair_attempts": len(result.attempts)},
        {"audit_id": audit_id, "status": "COMPILED", "node_counts": node_counts, "edge_counts": edge_counts,
         # no resolution-state tagging exists yet in this slice -- see the
         # graph-requirement matrix's note that EXACT/HEURISTIC/UNRESOLVED
         # tagging is new work, not built here.
         "unresolved_counts": {}},
        result.graph,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("registry", type=Path, help="benchmark_registry.jsonl from build_registry.py")
    ap.add_argument("--evmbench-root", type=Path, default=_DEFAULT_EVMBENCH_ROOT)
    ap.add_argument("--checkouts-dir", type=Path, default=None,
                     help="directory of already-extracted local checkouts, one subdir per audit_id")
    ap.add_argument("--out-dir", type=Path, default=Path("data/mgpr"))
    args = ap.parse_args(argv)

    # bin/forge shim + solc-select venv artifacts must be on PATH for
    # Slither's crytic-compile to shell out to forge for Foundry-project
    # audits (see agent4vul/bin/forge's own docstring for why this shim
    # exists on this host).
    os.environ["PATH"] = (
        f"{_AGENT4VUL_ROOT / 'bin'}:{_AGENT4VUL_ROOT / '.venv' / 'bin'}:{os.environ.get('PATH', '')}"
    )

    audit_ids = [json.loads(line)["audit_id"] for line in args.registry.read_text().splitlines() if line.strip()]
    repair = EnvRepair()

    build_rows, graph_rows = [], []
    for audit_id in audit_ids:
        build_row, graph_row, _graph = build_manifest_for_audit(
            audit_id, args.evmbench_root, args.checkouts_dir, repair
        )
        build_rows.append(build_row)
        graph_rows.append(graph_row)
        print(f"{audit_id}: {build_row['status']}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "build_manifest.jsonl").write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in build_rows) + "\n"
    )
    (args.out_dir / "graph_manifest.jsonl").write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in graph_rows) + "\n"
    )

    counts: dict[str, int] = {}
    for r in build_rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"summary: {counts}")
    print(f"-> {args.out_dir / 'build_manifest.jsonl'}")
    print(f"-> {args.out_dir / 'graph_manifest.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
