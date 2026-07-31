"""MGPR M7 CLI: the router-input sufficiency study (plan section 6).

This is an EVIDENCE REPORT, not a decision system: it contains no pass/fail
threshold, no success criterion, no go/no-go recommendation. For every
compiled audit's ground-truth findings, it records which P1/P2/P5 gate
predicates were SATISFIED/MISSING/UNRESOLVED/NOT_APPLICABLE, whether the
corresponding route would fire and the specific reason, and whether the
constructed context would have included the finding's own cited lines --
never whether that context was "enough." Interpretation is the user's
(plan section 8), not this script's.

Explicitly out of scope here: whether a Commentator flags the bug, whether
SuspicionRanker ranks it, whether the Agentic Auditor confirms it, final
EVMbench score. No LLM calls, no grading -- purely static/deterministic.

`python -m scripts.mgpr.run_feasibility_study
    data/mgpr/benchmark_registry.jsonl
    --checkouts-dir /path/to/extracted/checkouts
    [--out-dir data/mgpr]`
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from a4v.features import FeatureExtractor
from a4v.graph import FUNCTION, ProgramGraph
from a4v.mgpr.router import evaluate_gate
from a4v.mgpr.spec import load_routing_spec, RoutingSpec
from scripts.mgpr.build_manifests import _run_cmd_dir, build_manifest_for_audit

_DEFAULT_EVMBENCH_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")
_AGENT4VUL_ROOT = Path("/scratch/md5344/evmbench/agent4vul")
_DEFAULT_ROUTING_SPEC = _AGENT4VUL_ROOT / "routing_spec.yaml"

_CITATION_RE = re.compile(
    r"https://github\.com/[^/]+/[^/]+/blob/[0-9a-fA-F]+/(?P<path>[^#\s]+)#L(?P<start>\d+)(?:-L(?P<end>\d+))?"
)

# Dataset-construction labeling heuristic, NOT a router decision and NOT an
# experimental result (plan section 6's explicit allowance: "A coding agent
# may generate expected-route labels from audit ground truth, but these
# labels are dataset-construction inputs"). Keyword matching, transparent
# and inspectable, not an LLM call. Order matters: first match wins.
#
# Matched against the finding's FULL findings/<VULN-ID>.md text when
# available, not just task_info.csv's one-line `description` column --
# confirmed necessary by direct inspection: pooltogether's H-02
# (`description`: "A malicious user can steal other user's deposits from
# Vault.sol") states IMPACT, not mechanism; only the full writeup mentions
# "Cast" / "convert from uint256 to uint96" at all. Keywords below were
# chosen by reading real findings text (H-02, H-04 for pooltogether; H-01
# for tempo-feeamm), not guessed in the abstract -- still an imperfect
# heuristic, reported as such, not a claim of precise classification.
_FAMILY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("P2_REENTRANCY", ["reentran", "re-entran"]),
    ("P5_ARITHMETIC_PRECISION", [
        "downcast", "truncat", "precision loss", "overflow", "underflow",
        "rounding", "cast", "narrowing", "convert from",
    ]),
    ("P1_AUTHORIZATION", [
        "access control", "unauthorized", "authoriz", "anyone", "any user can",
        "onlyowner", "without permission", "no permission", "called by anyone",
        "lacks a check", "privilege",
    ]),
]


def assign_expected_family(description: str, full_text: str | None = None) -> str | None:
    """Returns a P1/P2/P5 family name or None (NOT_APPLICABLE for this
    slice -- the text doesn't obviously match one of the three families
    this slice specifies; it may belong to one of the 13 NOT_YET_SPECIFIED
    families instead). `full_text` (the finding's own findings/*.md
    content, when available) is checked alongside the short description --
    see the module-level note on why the short description alone is
    insufficient for some real findings.
    """
    lowered = f"{description}\n{full_text or ''}".lower()
    for family, keywords in _FAMILY_KEYWORDS:
        if any(kw in lowered for kw in keywords):
            return family
    return None


def resolve_citation(citation_url: str, checkout_root: Path, run_cmd_dir: str) -> tuple[Path, int, int] | None:
    m = _CITATION_RE.match(citation_url)
    if not m:
        return None
    start = int(m.group("start"))
    end = int(m.group("end") or start)
    local_path = (checkout_root / run_cmd_dir / m.group("path")).resolve()
    return local_path, start, end


# Slither synthesizes these bookkeeping functions on nearly every contract
# that declares state variables, regardless of whether they have inline
# initializers -- not real source-level functions, and their line-span
# attribution is broad enough to spuriously overlap unrelated citations
# (confirmed live: matched multiple, unrelated H-02 citations). Same
# exclusion already established in scripts/etl/build_feasibility_report.py
# for the same reason, applied here independently since that script is for
# the unrelated Messi-Q GNN corpus, not EVMbench audits.
_SLITHER_SYNTHETIC_FUNCTION_NAMES = {"slitherConstructorVariables", "slitherConstructorConstantVariables"}


def find_routing_units_for_citation(pg: ProgramGraph, local_path: Path, start: int, end: int) -> list[str]:
    """Function nodes whose own source span overlaps [start, end] in
    local_path. Multiple matches (nested/overlapping functions) or zero
    matches are both real, reportable outcomes, not resolved arbitrarily."""
    matches = []
    for node_id in pg.nodes_of_kind(FUNCTION):
        data = pg.graph.nodes[node_id]
        if data.get("name") in _SLITHER_SYNTHETIC_FUNCTION_NAMES:
            continue
        node_file = data.get("file")
        node_lines = data.get("lines") or []
        if not node_file or not node_lines:
            continue
        try:
            if Path(node_file).resolve() != local_path:
                continue
        except OSError:
            continue
        node_start, node_end = min(node_lines), max(node_lines)
        if node_start <= end and start <= node_end:
            matches.append((node_id, node_end - node_start))
    matches.sort(key=lambda pair: pair[1])  # smallest enclosing span first (most specific)
    return [node_id for node_id, _span in matches]


def _evaluate_finding(
    finding: dict, pg: ProgramGraph, features: dict, spec: RoutingSpec,
    checkout_root: Path, run_cmd_dir: str,
) -> tuple[list[dict], list[dict]]:
    """Returns (gate_evaluation_rows, context_manifest_rows) for one
    finding. Always emits at least one gate_evaluation row, even when the
    family is unassigned or the citation is unresolved -- unresolved cases
    are recorded explicitly (plan section 6), never dropped."""
    audit_id, _, vuln = finding["finding_id"].partition("/")
    full_text = None
    if finding.get("findings_md_path"):
        try:
            full_text = Path(finding["findings_md_path"]).read_text(errors="ignore")
        except OSError:
            full_text = None
    family = assign_expected_family(finding["description"], full_text)

    if family is None:
        return [{
            "finding_id": finding["finding_id"], "audit_id": audit_id,
            "routing_unit": None, "unit_type": None,
            "expected_primary_family": None, "gate": None,
            "predicates": [], "route_would_fire": None,
            "reason": "NOT_APPLICABLE: description did not match any P1/P2/P5 labeling keyword "
                      "(may belong to a NOT_YET_SPECIFIED family)",
            "unresolved_or_missing": [],
        }], []

    citations = finding.get("github_cited_locations") or []
    if not citations:
        return [{
            "finding_id": finding["finding_id"], "audit_id": audit_id,
            "routing_unit": None, "unit_type": None,
            "expected_primary_family": family, "gate": None,
            "predicates": [], "route_would_fire": None,
            "reason": "UNRESOLVED: no GitHub line citation found in the finding's own writeup "
                      "to resolve a routing unit from",
            "unresolved_or_missing": [],
        }], []

    gate_rows: list[dict] = []
    context_rows: list[dict] = []
    family_spec = spec.families[family]
    resolved_any_unit = False

    for citation in citations:
        resolved = resolve_citation(citation, checkout_root, run_cmd_dir)
        if resolved is None:
            gate_rows.append({
                "finding_id": finding["finding_id"], "audit_id": audit_id,
                "routing_unit": None, "unit_type": None,
                "expected_primary_family": family, "gate": None,
                "predicates": [], "route_would_fire": None,
                "reason": f"UNRESOLVED: citation URL did not match the expected GitHub blob#L pattern: {citation}",
                "unresolved_or_missing": [],
            })
            continue

        local_path, start, end = resolved
        units = find_routing_units_for_citation(pg, local_path, start, end)
        if not units:
            gate_rows.append({
                "finding_id": finding["finding_id"], "audit_id": audit_id,
                "routing_unit": None, "unit_type": None,
                "expected_primary_family": family, "gate": None,
                "predicates": [], "route_would_fire": None,
                "reason": f"UNRESOLVED: no compiled function node's source span covers "
                          f"{local_path}:{start}-{end}",
                "unresolved_or_missing": [],
            })
            continue

        resolved_any_unit = True
        # every overlapping unit is reported -- an ambiguous (>1) match is
        # itself evidence to report, not silently collapsed to one.
        for node_id in units:
            node_features = features.get(node_id)
            for gate in family_spec.gates:
                route = evaluate_gate(pg, node_id, node_features, family_spec, gate)
                gate_rows.append({
                    "finding_id": finding["finding_id"], "audit_id": audit_id,
                    "routing_unit": node_id, "unit_type": "function",
                    "expected_primary_family": family, "gate": gate.id,
                    "predicates": [vars(s) for s in route.predicates],
                    "route_would_fire": route.route_would_fire,
                    "reason": route.reason,
                    "unresolved_or_missing": route.unresolved_or_missing,
                    "citation_ambiguous": len(units) > 1,
                })

    return gate_rows, context_rows


def run_study(
    registry: list[dict], build_manifest_rows: dict[str, dict], routing_spec: RoutingSpec,
    checkouts_dir: Path, evmbench_root: Path, repair,
) -> tuple[list[dict], dict]:
    """Returns (gate_evaluation_rows, feasibility_report_dict). Only audits
    with status COMPILED in build_manifest_rows are evaluated; every other
    audit is reported (in the feasibility report's per-audit-status counts)
    but contributes no gate_evaluation rows -- gated, not silently omitted.
    """
    all_gate_rows: list[dict] = []
    audit_status_counts: dict[str, int] = {}
    per_family: dict[str, dict] = {
        name: {"findings_considered": 0, "predicate_status_counts": {}, "route_fire_count": 0,
               "route_not_fire_count": 0, "unresolved_routing_unit_count": 0,
               "blocking_reason_histogram": {}}
        for name in ("P1_AUTHORIZATION", "P2_REENTRANCY", "P5_ARITHMETIC_PRECISION")
    }
    not_applicable_count = 0
    total_findings_in_registry = sum(len(a["findings"]) for a in registry)
    findings_reached = 0  # findings whose audit actually reached COMPILED status

    for audit in registry:
        audit_id = audit["audit_id"]
        status = build_manifest_rows.get(audit_id, {}).get("status", "SKIPPED")
        audit_status_counts[status] = audit_status_counts.get(status, 0) + 1
        if status != "COMPILED":
            continue
        findings_reached += len(audit["findings"])

        checkout_root = checkouts_dir / audit_id
        run_cmd_dir = _run_cmd_dir(evmbench_root, audit_id)
        _build_row, _graph_row, pg = build_manifest_for_audit(audit_id, evmbench_root, checkouts_dir, repair)
        if pg is None:
            continue  # should not happen given status==COMPILED, but never assume
        features = FeatureExtractor.compute(pg)

        for finding in audit["findings"]:
            gate_rows, _context_rows = _evaluate_finding(
                finding, pg, features, routing_spec, checkout_root, run_cmd_dir
            )
            all_gate_rows.extend(gate_rows)

            family = gate_rows[0]["expected_primary_family"] if gate_rows else None
            if family is None:
                not_applicable_count += 1
                continue

            fam_report = per_family[family]
            fam_report["findings_considered"] += 1
            fired_any = False
            for row in gate_rows:
                if row["routing_unit"] is None:
                    fam_report["unresolved_routing_unit_count"] += 1
                    continue
                for pred in row["predicates"]:
                    key = f"{pred['predicate']}:{pred['status']}"
                    fam_report["predicate_status_counts"][key] = fam_report["predicate_status_counts"].get(key, 0) + 1
                if row["route_would_fire"]:
                    fired_any = True
                else:
                    blocker = row["reason"].split(":")[0]
                    fam_report["blocking_reason_histogram"][blocker] = (
                        fam_report["blocking_reason_histogram"].get(blocker, 0) + 1
                    )
            if fired_any:
                fam_report["route_fire_count"] += 1
            else:
                fam_report["route_not_fire_count"] += 1

    feasibility_report = {
        "registry_size": len(registry),
        "audit_status_counts": audit_status_counts,
        "total_findings_in_registry": total_findings_in_registry,
        "findings_reached_compiled_audits": findings_reached,
        "findings_blocked_by_audit_compile_status": total_findings_in_registry - findings_reached,
        "findings_not_applicable_to_p1_p2_p5": not_applicable_count,
        "per_family": per_family,
    }
    return all_gate_rows, feasibility_report


def main(argv: list[str] | None = None) -> int:
    from a4v.repair import EnvRepair

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("registry", type=Path)
    ap.add_argument("--evmbench-root", type=Path, default=_DEFAULT_EVMBENCH_ROOT)
    ap.add_argument("--routing-spec", type=Path, default=_DEFAULT_ROUTING_SPEC)
    ap.add_argument("--checkouts-dir", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=Path("data/mgpr"))
    args = ap.parse_args(argv)

    os.environ["PATH"] = (
        f"{_AGENT4VUL_ROOT / 'bin'}:{_AGENT4VUL_ROOT / '.venv' / 'bin'}:{os.environ.get('PATH', '')}"
    )

    registry = [json.loads(line) for line in args.registry.read_text().splitlines() if line.strip()]
    from a4v.mgpr.router import KNOWN_PREDICATES
    routing_spec = load_routing_spec(args.routing_spec, known_predicates=KNOWN_PREDICATES)
    repair = EnvRepair()

    build_manifest_rows: dict[str, dict] = {}
    for audit in registry:
        row, _graph_row, _graph = build_manifest_for_audit(
            audit["audit_id"], args.evmbench_root, args.checkouts_dir, repair
        )
        build_manifest_rows[audit["audit_id"]] = row
        print(f"{audit['audit_id']}: {row['status']}")

    gate_rows, feasibility_report = run_study(
        registry, build_manifest_rows, routing_spec, args.checkouts_dir, args.evmbench_root, repair
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "gate_evaluation.jsonl").write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in gate_rows) + ("\n" if gate_rows else "")
    )
    (args.out_dir / "feasibility_report.json").write_text(json.dumps(feasibility_report, indent=2, sort_keys=True))

    print(json.dumps(feasibility_report, indent=2, sort_keys=True))
    print(f"-> {args.out_dir / 'gate_evaluation.jsonl'}")
    print(f"-> {args.out_dir / 'feasibility_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
