"""MGPR M7 CLI: the router-input sufficiency study (plan section 6).

This is an EVIDENCE REPORT, not a decision system: it contains no pass/fail
threshold, no success criterion, no go/no-go recommendation. For every
compiled audit's ground-truth findings, it records which P1/P2/P5 gate
predicates were SATISFIED/MISSING/UNRESOLVED/NOT_APPLICABLE, whether the
corresponding route would fire and the specific reason, and whether the
constructed context would have included the finding's own cited lines --
never whether that context was "enough." Interpretation is the user's
(plan section 8), not this script's.

Produces all six of the plan's per-run artifacts (section 17) from a single
coherent compile pass per audit (each audit is compiled exactly once, not
once per artifact):
  - build_manifest.jsonl / graph_manifest.jsonl (compile status + graph metadata)
  - gate_evaluation.jsonl (ground-truth-finding-focused predicate trace)
  - route_manifest.jsonl (every fired route across the WHOLE compiled graph,
    not just ground-truth-cited units -- what MGPR would actually route in
    production for this audit)
  - context_manifest.jsonl (constructed context per fired route, cross-
    referenced against ground truth where a finding cites that routing unit)
  - feasibility_report.json (aggregate raw counts)
(benchmark_registry.jsonl itself is produced separately by build_registry.py.)

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
from pathlib import Path

from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.mgpr.context import build_context
from a4v.mgpr.router import KNOWN_PREDICATES, evaluate_gate, fired_routes, route_all
from a4v.mgpr.spec import RoutingSpec, load_routing_spec
from scripts.mgpr.build_manifests import _run_cmd_dir, build_manifest_for_audit
from scripts.mgpr.citation_resolution import (  # noqa: F401 -- resolve_citation/find_routing_units_for_citation re-exported for backward compat
    CitationOutcome,
    find_routing_units_for_citation,
    location_covered_by_nodes,
    resolve_citation,
    resolve_citation_string,
)

_DEFAULT_EVMBENCH_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")
# Resolved from this file's own location, NOT hardcoded to the main
# checkout -- confirmed live during this work's own infra investigation
# that hardcoding this to /scratch/md5344/evmbench/agent4vul (rather than
# resolving whichever checkout/worktree this script actually lives in)
# silently pointed `PATH` at a stale, less-capable bin/forge, causing
# audits (e.g. 2024-01-canto, 2025-04-forte) to fail here that compile
# cleanly with the current worktree's own bin/forge on PATH.
_AGENT4VUL_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_ROUTING_SPEC = _AGENT4VUL_ROOT / "routing_spec.yaml"

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


def _evaluate_finding(
    finding: dict, pg: ProgramGraph, features: dict, spec: RoutingSpec,
    checkout_root: Path, run_cmd_dir: str,
) -> list[dict]:
    """Returns gate_evaluation_rows for one finding. Always emits at least
    one row, even when the family is unassigned or the citation is
    unresolved -- unresolved cases are recorded explicitly (plan section
    6), never dropped."""
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
            "unresolved_or_missing": [], "citation_outcome": None, "citation": None,
        }]

    citations = finding.get("github_cited_locations") or []
    if not citations:
        return [{
            "finding_id": finding["finding_id"], "audit_id": audit_id,
            "routing_unit": None, "unit_type": None,
            "expected_primary_family": family, "gate": None,
            "predicates": [], "route_would_fire": None,
            "reason": f"{CitationOutcome.NO_CITATION.value}: no citation (GitHub blob link or relative "
                      f"Markdown code-location link) found in the finding's own writeup",
            "unresolved_or_missing": [], "citation_outcome": CitationOutcome.NO_CITATION.value,
            "citation": None,
        }]

    gate_rows: list[dict] = []
    family_spec = spec.families[family]

    for citation in citations:
        res = resolve_citation_string(
            citation, audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
        )
        if res.outcome is not CitationOutcome.RESOLVED:
            gate_rows.append({
                "finding_id": finding["finding_id"], "audit_id": audit_id,
                "routing_unit": None, "unit_type": None,
                "expected_primary_family": family, "gate": None,
                "predicates": [], "route_would_fire": None,
                "reason": f"{res.outcome.value}: {res.detail}",
                "unresolved_or_missing": [], "citation_outcome": res.outcome.value,
                "citation_parser_format": res.parser_format, "citation_repo_identity": res.repo_identity,
                "citation": citation,
            })
            continue

        units = res.routing_units
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
                    "citation_outcome": res.outcome.value,
                    "citation_parser_format": res.parser_format, "citation_repo_identity": res.repo_identity,
                    "citation": citation,
                })

    return gate_rows


def build_route_and_context_manifests(
    audit_id: str, pg: ProgramGraph, features: dict, spec: RoutingSpec,
    findings: list[dict], checkout_root: Path, run_cmd_dir: str,
) -> tuple[list[dict], list[dict]]:
    """route_manifest.jsonl / context_manifest.jsonl rows for every fired
    route across the ENTIRE compiled graph -- not just ground-truth-cited
    units. This is what MGPR would actually route in production for this
    audit, independent of whether a route happens to match a known
    finding. When a fired route's routing unit is cited by one of this
    audit's ground-truth findings, the context_manifest row additionally
    records whether that finding's OTHER cited locations (not just the
    seed itself) landed inside the constructed context; otherwise those
    fields are null, not fabricated as true/false.
    """
    grouped: dict[tuple[str, str], list] = {}
    for route in fired_routes(route_all(pg, features, spec)):
        grouped.setdefault((route.routing_unit, route.family), []).append(route)

    route_rows: list[dict] = []
    context_rows: list[dict] = []
    for (routing_unit, family), routes in sorted(grouped.items()):
        gates_fired = sorted({r.gate for r in routes})
        route_rows.append({
            "audit_id": audit_id, "routing_unit": routing_unit, "unit_type": "function",
            "family": family, "gates_fired": gates_fired, "prompt_id": routes[0].prompt_id,
            "resolution_notes": [],
        })

        bundle, record = build_context(pg, routes[0])
        included_node_ids = set(bundle.neighborhood) | {routing_unit}

        relevant_findings = []
        for finding in findings:
            for citation in finding.get("github_cited_locations") or []:
                res = resolve_citation_string(
                    citation, audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
                )
                if res.outcome is not CitationOutcome.RESOLVED:
                    continue
                if routing_unit in res.routing_units:
                    relevant_findings.append(finding)
                    break

        if relevant_findings:
            all_cited: list[str] = []
            any_included, any_excluded_or_unresolved = False, False
            for finding in relevant_findings:
                for citation in finding.get("github_cited_locations") or []:
                    all_cited.append(citation)
                    res = resolve_citation_string(
                        citation, audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
                    )
                    if res.outcome is not CitationOutcome.RESOLVED:
                        continue
                    local_path, start, end = Path(res.normalized_path), res.start, res.end
                    if location_covered_by_nodes(pg, local_path, start, end, included_node_ids):
                        any_included = True
                    else:
                        any_excluded_or_unresolved = True
            context_rows.append({
                "audit_id": audit_id, "routing_unit": routing_unit, "family": family,
                "included": record.included, "excluded": record.excluded, "unresolved": record.unresolved,
                "matching_finding_ids": [f["finding_id"] for f in relevant_findings],
                "ground_truth_cited_locations": all_cited,
                "ground_truth_locations_in_included": any_included,
                "ground_truth_locations_in_excluded_or_unresolved": any_excluded_or_unresolved,
            })
        else:
            context_rows.append({
                "audit_id": audit_id, "routing_unit": routing_unit, "family": family,
                "included": record.included, "excluded": record.excluded, "unresolved": record.unresolved,
                "matching_finding_ids": [],
                "ground_truth_cited_locations": [],
                "ground_truth_locations_in_included": None,
                "ground_truth_locations_in_excluded_or_unresolved": None,
            })

    return route_rows, context_rows


def run_study(
    registry: list[dict], compiled_audits: dict[str, tuple[ProgramGraph, dict]],
    build_manifest_rows: dict[str, dict], routing_spec: RoutingSpec,
    checkouts_dir: Path, evmbench_root: Path,
) -> tuple[list[dict], list[dict], list[dict], dict]:
    """Returns (gate_evaluation_rows, route_manifest_rows,
    context_manifest_rows, feasibility_report_dict). Only audits present in
    `compiled_audits` are evaluated; every other audit is reported (in the
    feasibility report's per-audit-status counts) but contributes no rows
    to any of the three per-unit artifacts -- gated, not silently omitted.
    """
    all_gate_rows: list[dict] = []
    all_route_rows: list[dict] = []
    all_context_rows: list[dict] = []
    audit_status_counts: dict[str, int] = {}
    per_family: dict[str, dict] = {
        name: {"findings_considered": 0, "predicate_status_counts": {}, "route_fire_count": 0,
               "route_not_fire_count": 0, "unresolved_routing_unit_count": 0,
               "blocking_reason_histogram": {}, "citation_outcome_histogram": {}}
        for name in ("P1_AUTHORIZATION", "P2_REENTRANCY", "P5_ARITHMETIC_PRECISION")
    }
    not_applicable_count = 0
    total_findings_in_registry = sum(len(a["findings"]) for a in registry)
    findings_reached = 0  # findings whose audit actually reached COMPILED status
    overall_citation_outcome_histogram: dict[str, int] = {}

    for audit in registry:
        audit_id = audit["audit_id"]
        status = build_manifest_rows.get(audit_id, {}).get("status", "SKIPPED")
        audit_status_counts[status] = audit_status_counts.get(status, 0) + 1
        if audit_id not in compiled_audits:
            continue
        findings_reached += len(audit["findings"])

        pg, features = compiled_audits[audit_id]
        checkout_root = checkouts_dir / audit_id
        run_cmd_dir = _run_cmd_dir(evmbench_root, audit_id)

        route_rows, context_rows = build_route_and_context_manifests(
            audit_id, pg, features, routing_spec, audit["findings"], checkout_root, run_cmd_dir
        )
        all_route_rows.extend(route_rows)
        all_context_rows.extend(context_rows)

        for finding in audit["findings"]:
            gate_rows = _evaluate_finding(finding, pg, features, routing_spec, checkout_root, run_cmd_dir)
            all_gate_rows.extend(gate_rows)

            family = gate_rows[0]["expected_primary_family"] if gate_rows else None
            if family is None:
                not_applicable_count += 1
                continue

            fam_report = per_family[family]
            fam_report["findings_considered"] += 1
            fired_any = False
            # counted per distinct (finding, citation) pair, not per gate_row --
            # a single RESOLVED citation can produce multiple rows (one per
            # matched unit x per gate), which would otherwise inflate the
            # histogram relative to how many citations were actually resolved.
            seen_citations: set[str] = set()
            for row in gate_rows:
                citation_key = row.get("citation")
                if citation_key not in seen_citations:
                    seen_citations.add(citation_key)
                    outcome = row.get("citation_outcome")
                    if outcome is not None:
                        fam_report["citation_outcome_histogram"][outcome] = (
                            fam_report["citation_outcome_histogram"].get(outcome, 0) + 1
                        )
                        overall_citation_outcome_histogram[outcome] = (
                            overall_citation_outcome_histogram.get(outcome, 0) + 1
                        )
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
        "total_fired_routes_across_compiled_audits": len(all_route_rows),
        "per_family": per_family,
        "citation_outcome_histogram": overall_citation_outcome_histogram,
    }
    return all_gate_rows, all_route_rows, all_context_rows, feasibility_report


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
    routing_spec = load_routing_spec(args.routing_spec, known_predicates=KNOWN_PREDICATES)
    repair = EnvRepair()

    # Each audit is compiled exactly ONCE here -- build_manifest.jsonl /
    # graph_manifest.jsonl and the study below both come from this same
    # pass, so they can never disagree with each other about compile status.
    build_rows, graph_rows = [], []
    compiled_audits: dict[str, tuple[ProgramGraph, dict]] = {}
    for audit in registry:
        audit_id = audit["audit_id"]
        build_row, graph_row, pg = build_manifest_for_audit(audit_id, args.evmbench_root, args.checkouts_dir, repair)
        build_rows.append(build_row)
        graph_rows.append(graph_row)
        print(f"{audit_id}: {build_row['status']}")
        if pg is not None:
            compiled_audits[audit_id] = (pg, FeatureExtractor.compute(pg))

    build_manifest_rows = {r["audit_id"]: r for r in build_rows}
    gate_rows, route_rows, context_rows, feasibility_report = run_study(
        registry, compiled_audits, build_manifest_rows, routing_spec, args.checkouts_dir, args.evmbench_root
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)

    def _write_jsonl(name: str, rows: list[dict]) -> None:
        path = args.out_dir / name
        path.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + ("\n" if rows else ""))
        print(f"-> {path} ({len(rows)} row(s))")

    _write_jsonl("build_manifest.jsonl", build_rows)
    _write_jsonl("graph_manifest.jsonl", graph_rows)
    _write_jsonl("gate_evaluation.jsonl", gate_rows)
    _write_jsonl("route_manifest.jsonl", route_rows)
    _write_jsonl("context_manifest.jsonl", context_rows)

    (args.out_dir / "feasibility_report.json").write_text(json.dumps(feasibility_report, indent=2, sort_keys=True))
    print(json.dumps(feasibility_report, indent=2, sort_keys=True))
    print(f"-> {args.out_dir / 'feasibility_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
