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
from a4v.mgpr.context import RouteContextGroup, build_context
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
from scripts.mgpr.family_classification import FamilyOutcome, classify_family

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

_FAMILY_VALUES = {"P1_AUTHORIZATION", "P2_REENTRANCY", "P5_ARITHMETIC_PRECISION"}


def load_reviewed_labels(path: Path | None) -> dict[str, dict]:
    """Loads the Phase 2 gold-label review artifact (one JSON object per
    line, keyed by `finding_id`) into a lookup dict. Returns {} if `path` is
    None or does not exist -- evaluation then falls back to the raw
    deterministic classifier for every finding, which is the correct
    behavior before a review pass has been run (e.g. while iterating on the
    classifier itself), NOT a silent substitute for review in the final
    baseline (the decision rule requires every P1/P2/P5-classified accepted
    finding to actually have a review entry; callers that need to enforce
    that check `reviewed` in the returned gate_evaluation rows)."""
    if path is None or not path.exists():
        return {}
    labels: dict[str, dict] = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        labels[row["finding_id"]] = row
    return labels


def _read_full_text(path_str: str | None) -> str | None:
    if not path_str:
        return None
    try:
        return Path(path_str).read_text(errors="ignore")
    except OSError:
        return None


def _classification_row(base_row: dict, classification_debug: dict, reason_prefix: str) -> dict:
    matched_rule = classification_debug["raw_classification"]["matched_rule"]
    confidence = classification_debug["raw_classification"]["confidence"]
    if matched_rule:
        reason = f"{reason_prefix}: matched {matched_rule!r} (confidence={confidence})"
    else:
        reason = f"{reason_prefix}: no P1/P2/P5 evidence found by the deterministic classifier"
    return {
        **base_row,
        "routing_unit": None, "unit_type": None,
        "expected_primary_family": None, "family_outcome": reason_prefix, "gate": None,
        "predicates": [], "route_would_fire": None,
        "reason": reason,
        "unresolved_or_missing": [], "citation_outcome": None, "citation": None,
        **classification_debug,
    }


def _resolve_citations_to_gate_rows(
    citations: list[str], family: str, base_row: dict, classification_debug: dict,
    pg: ProgramGraph, features: dict, spec: RoutingSpec, audit_id: str, checkout_root: Path, run_cmd_dir: str,
) -> list[dict]:
    """Shared citation-resolution -> gate-evaluation expansion used by both
    accepted findings and incorrect claims (Phase 1 + Phase 3): identical
    deterministic pipeline, per the task's explicit instruction that
    incorrect claims run through "the same deterministic citation and
    family-classification pipeline"."""
    if not citations:
        return [{
            **base_row, "routing_unit": None, "unit_type": None,
            "expected_primary_family": family, "family_outcome": family, "gate": None,
            "predicates": [], "route_would_fire": None,
            "reason": f"{CitationOutcome.NO_CITATION.value}: no citation (GitHub blob link or relative "
                      f"Markdown code-location link) found in the writeup",
            "unresolved_or_missing": [], "citation_outcome": CitationOutcome.NO_CITATION.value,
            "citation": None, **classification_debug,
        }]

    gate_rows: list[dict] = []
    family_spec = spec.families[family]

    for citation in citations:
        res = resolve_citation_string(
            citation, audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
        )
        if res.outcome is not CitationOutcome.RESOLVED:
            gate_rows.append({
                **base_row, "routing_unit": None, "unit_type": None,
                "expected_primary_family": family, "family_outcome": family, "gate": None,
                "predicates": [], "route_would_fire": None,
                "reason": f"{res.outcome.value}: {res.detail}",
                "unresolved_or_missing": [], "citation_outcome": res.outcome.value,
                "citation_parser_format": res.parser_format, "citation_repo_identity": res.repo_identity,
                "citation": citation, **classification_debug,
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
                    **base_row, "routing_unit": node_id, "unit_type": "function",
                    "expected_primary_family": family, "family_outcome": family, "gate": gate.id,
                    "predicates": [vars(s) for s in route.predicates],
                    "route_would_fire": route.route_would_fire,
                    "reason": route.reason,
                    "unresolved_or_missing": route.unresolved_or_missing,
                    "citation_ambiguous": len(units) > 1,
                    "citation_outcome": res.outcome.value,
                    "citation_parser_format": res.parser_format, "citation_repo_identity": res.repo_identity,
                    "citation": citation, **classification_debug,
                })

    return gate_rows


def _evaluate_finding(
    finding: dict, pg: ProgramGraph, features: dict, spec: RoutingSpec,
    checkout_root: Path, run_cmd_dir: str, reviewed_labels: dict[str, dict] | None = None,
) -> list[dict]:
    """Returns gate_evaluation_rows for one ACCEPTED finding. Always emits
    at least one row, even when the family is unassigned/uncertain or the
    citation is unresolved -- unresolved cases are recorded explicitly
    (plan section 6), never dropped.

    Family assignment (Phase 2): the deterministic `classify_family`
    replaces the old broad-substring heuristic. When `reviewed_labels`
    contains a manually-reviewed entry for this finding (Phase 2's gold-
    label review artifact), that entry's `final_family` is authoritative
    and overrides the raw classifier output -- "the manually reviewed
    labels become the evaluation labels for this study." Every row records
    both the raw classification and whether/how it was reviewed, so the
    override is always auditable, never silent.
    """
    audit_id, _, vuln = finding["finding_id"].partition("/")
    full_text = _read_full_text(finding.get("findings_md_path"))
    raw = classify_family(finding.get("title"), finding.get("description"), full_text)

    review = (reviewed_labels or {}).get(finding["finding_id"])
    if review is not None:
        final_outcome = FamilyOutcome(review["final_family"])
        reviewer_status = review.get("reviewer_status")
    else:
        final_outcome = raw.outcome
        reviewer_status = None

    classification_debug = {
        "raw_classification": raw.as_dict(),
        "reviewed": review is not None,
        "reviewer_status": reviewer_status,
    }
    base_row = {"finding_id": finding["finding_id"], "audit_id": audit_id}

    if final_outcome is FamilyOutcome.NOT_APPLICABLE:
        return [_classification_row(base_row, classification_debug, "NOT_APPLICABLE")]
    if final_outcome is FamilyOutcome.UNCERTAIN:
        return [_classification_row(base_row, classification_debug, "UNCERTAIN")]

    family = final_outcome.value
    citations = finding.get("github_cited_locations") or []
    return _resolve_citations_to_gate_rows(
        citations, family, base_row, classification_debug, pg, features, spec, audit_id, checkout_root, run_cmd_dir,
    )


def _evaluate_incorrect_claim(
    claim: dict, pg: ProgramGraph, features: dict, spec: RoutingSpec, checkout_root: Path, run_cmd_dir: str,
) -> list[dict]:
    """Phase 3: runs the SAME deterministic citation + family-classification
    pipeline as `_evaluate_finding` against one `findings/incorrect/`
    claim. No manual review is applied here (the decision rule only
    requires manual review of accepted P1/P2/P5 labels; reviewing the full
    incorrect-claim population -- routinely 3-6x the accepted-finding count
    per audit -- is out of this pass's scope and explicitly noted as such in
    the deliverables, not silently skipped).

    An incorrect claim resolving to a routing unit and firing a gate means:
    "a specific vulnerability mechanism someone actually claimed at this
    location, that was judged incorrect, still causes MGPR's gate to fire."
    This is real, usable per-claim signal about the gate's specificity --
    it is NOT proof the routing unit is safe in general (an incorrect claim
    about mechanism X says nothing about other, un-submitted mechanisms at
    the same location).
    """
    full_text = _read_full_text(claim.get("source_path"))
    raw = classify_family(claim.get("title"), None, full_text)
    classification_debug = {"raw_classification": raw.as_dict(), "reviewed": False, "reviewer_status": None}
    base_row = {
        "incorrect_finding_id": claim["incorrect_finding_id"], "audit_id": claim["audit_id"],
        "severity": claim["severity"], "title": claim.get("title"),
    }

    if raw.outcome is FamilyOutcome.NOT_APPLICABLE:
        return [_classification_row(base_row, classification_debug, "NOT_APPLICABLE")]
    if raw.outcome is FamilyOutcome.UNCERTAIN:
        return [_classification_row(base_row, classification_debug, "UNCERTAIN")]

    family = raw.outcome.value
    citations = claim.get("github_cited_locations") or []
    return _resolve_citations_to_gate_rows(
        citations, family, base_row, classification_debug, pg, features, spec,
        claim["audit_id"], checkout_root, run_cmd_dir,
    )


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
    all_routes = route_all(pg, features, spec)
    fired = fired_routes(all_routes)
    fired_unit_families = {(r.routing_unit, r.family) for r in fired}

    grouped: dict[tuple[str, str], list] = {}
    for route in fired:
        grouped.setdefault((route.routing_unit, route.family), []).append(route)

    grouped_unresolved: dict[tuple[str, str], list] = {}
    for route in all_routes:
        key = (route.routing_unit, route.family)
        if route.decision_blocking_unresolved and key in fired_unit_families:
            grouped_unresolved.setdefault(key, []).append(route)

    route_rows: list[dict] = []
    context_rows: list[dict] = []
    for (routing_unit, family), routes in sorted(grouped.items()):
        gates_fired = sorted({r.gate for r in routes})
        route_rows.append({
            "audit_id": audit_id, "routing_unit": routing_unit, "unit_type": "function",
            "family": family, "gates_fired": gates_fired, "prompt_id": routes[0].prompt_id,
            "resolution_notes": [],
        })

        group = RouteContextGroup(
            fired_routes=routes, unresolved_routes=grouped_unresolved.get((routing_unit, family), []),
        )
        bundle, record = build_context(pg, group)
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
    checkouts_dir: Path, evmbench_root: Path, reviewed_labels: dict[str, dict] | None = None,
) -> tuple[list[dict], list[dict], list[dict], dict]:
    """Returns (gate_evaluation_rows, route_manifest_rows,
    context_manifest_rows, feasibility_report_dict). Only audits present in
    `compiled_audits` are evaluated; every other audit is reported (in the
    feasibility report's per-audit-status counts) but contributes no rows
    to any of the three per-unit artifacts -- gated, not silently omitted.

    `reviewed_labels` (Phase 2 gold-label review artifact, see
    `load_reviewed_labels`) is threaded through to `_evaluate_finding`;
    omitted, every finding falls back to the raw deterministic classifier.
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
    uncertain_count = 0
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
            gate_rows = _evaluate_finding(
                finding, pg, features, routing_spec, checkout_root, run_cmd_dir, reviewed_labels,
            )
            all_gate_rows.extend(gate_rows)

            family_outcome = gate_rows[0]["family_outcome"] if gate_rows else None
            if family_outcome == FamilyOutcome.UNCERTAIN.value:
                uncertain_count += 1
                continue
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
        "findings_uncertain_family": uncertain_count,
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
    ap.add_argument("--reviewed-labels", type=Path, default=None,
                     help="Phase 2 gold-label review artifact (JSONL); overrides the raw classifier "
                          "for any finding it covers.")
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
    reviewed_labels = load_reviewed_labels(args.reviewed_labels)
    gate_rows, route_rows, context_rows, feasibility_report = run_study(
        registry, compiled_audits, build_manifest_rows, routing_spec, args.checkouts_dir, args.evmbench_root,
        reviewed_labels,
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
