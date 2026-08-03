"""Phases 4-6: builds the corrected evaluation's clean populations, finding-
level metrics, whole-graph route labeling, and structured miss analysis --
purely from already-produced artifacts (gate_evaluation.jsonl,
incorrect_gate_evaluation.jsonl, route_manifest.jsonl), no compilation, no
MGPR behavior touched. Deterministic given the same input artifacts.

`python -m scripts.mgpr.generate_corrected_metrics --study-dir <dir> --out <report.json>`

Populations (Phase 4):
  - accepted_positive: accepted findings with a CONFIRMED/CORRECTED P1/P2/P5
    label (per the Phase 2 reviewed-label artifact, already baked into
    gate_evaluation.jsonl's `expected_primary_family`/`family_outcome`
    fields by run_full_study_batch.py) that resolve to >=1 routing unit.
  - accepted_unresolved: same family confidence, but NO citation resolves
    to any routing unit -- NOT counted as a gate miss (plan section 6/
    Phase 4's explicit instruction).
  - incorrect_claim (resolved): incorrect claims (Phase 3) with an assigned
    family that resolve to >=1 routing unit.
  - unconfirmed routes: whole-graph fired routes matching neither
    population -- labeled UNCONFIRMED, never called false positives (no
    negative-labeled ground truth exists for them).
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


_FAMILIES = ("P1_AUTHORIZATION", "P2_REENTRANCY", "P5_ARITHMETIC_PRECISION")


def _group_by_finding(rows: list[dict], id_field: str) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        grouped[r[id_field]].append(r)
    return dict(grouped)


def build_accepted_populations(gate_rows: list[dict]) -> dict:
    """Returns {"accepted_positive": [...], "accepted_unresolved": [...],
    "not_applicable": [...], "uncertain": [...]}, one summary dict per
    finding (not per raw row)."""
    by_finding = _group_by_finding(gate_rows, "finding_id")

    accepted_positive, accepted_unresolved, not_applicable, uncertain = [], [], [], []
    for finding_id, rows in by_finding.items():
        family_outcome = rows[0].get("family_outcome")
        audit_id = rows[0]["audit_id"]
        if family_outcome == "NOT_APPLICABLE":
            not_applicable.append({"finding_id": finding_id, "audit_id": audit_id})
            continue
        if family_outcome == "UNCERTAIN":
            uncertain.append({"finding_id": finding_id, "audit_id": audit_id})
            continue
        if family_outcome not in _FAMILIES:
            continue

        resolved_units = sorted({
            (r["routing_unit"], r["gate"]) for r in rows if r["routing_unit"] is not None
        })
        fired = any(r["route_would_fire"] for r in rows if r["routing_unit"] is not None)
        summary = {
            "finding_id": finding_id, "audit_id": audit_id, "family": family_outcome,
            "reviewed": rows[0].get("reviewed", False), "reviewer_status": rows[0].get("reviewer_status"),
            "routing_units": sorted({u for u, _g in resolved_units}),
            "gate_fired": fired,
        }
        if resolved_units:
            accepted_positive.append(summary)
        else:
            accepted_unresolved.append({**summary, "gate_fired": None})

    return {
        "accepted_positive": accepted_positive, "accepted_unresolved": accepted_unresolved,
        "not_applicable": not_applicable, "uncertain": uncertain,
    }


def build_incorrect_claim_population(incorrect_gate_rows: list[dict]) -> list[dict]:
    by_claim = _group_by_finding(incorrect_gate_rows, "incorrect_finding_id")
    resolved_claims = []
    for claim_id, rows in by_claim.items():
        family_outcome = rows[0].get("family_outcome")
        if family_outcome not in _FAMILIES:
            continue
        routing_units = sorted({r["routing_unit"] for r in rows if r["routing_unit"] is not None})
        if not routing_units:
            continue
        fired = any(r["route_would_fire"] for r in rows if r["routing_unit"] is not None)
        resolved_claims.append({
            "incorrect_finding_id": claim_id, "audit_id": rows[0]["audit_id"], "severity": rows[0].get("severity"),
            "family": family_outcome, "routing_units": routing_units, "gate_fired": fired,
        })
    return resolved_claims


def label_routes(
    route_rows: list[dict], accepted_positive: list[dict], incorrect_claims_resolved: list[dict],
) -> list[dict]:
    """Every whole-graph fired route gets exactly one label:
    ACCEPTED_MATCHED, INCORRECT_CLAIM_MATCHED, BOTH_MATCHED, or UNCONFIRMED
    -- never "false positive" (Phase 4's explicit constraint)."""
    accepted_units: set[tuple[str, str, str]] = set()
    for f in accepted_positive:
        for u in f["routing_units"]:
            accepted_units.add((f["audit_id"], u, f["family"]))

    incorrect_units: set[tuple[str, str, str]] = set()
    for c in incorrect_claims_resolved:
        for u in c["routing_units"]:
            incorrect_units.add((c["audit_id"], u, c["family"]))

    labeled = []
    for route in route_rows:
        key = (route["audit_id"], route["routing_unit"], route["family"])
        in_accepted, in_incorrect = key in accepted_units, key in incorrect_units
        if in_accepted and in_incorrect:
            label = "BOTH_MATCHED"
        elif in_accepted:
            label = "ACCEPTED_MATCHED"
        elif in_incorrect:
            label = "INCORRECT_CLAIM_MATCHED"
        else:
            label = "UNCONFIRMED"
        labeled.append({**route, "route_label": label})
    return labeled


# --- Phase 6: structured miss analysis ---------------------------------------

_MISS_CATEGORIES = (
    "EXTRACTION_FAILURE", "CURRENT_GATE_STRUCTURALLY_INAPPLICABLE",
    "GROUND_TRUTH_MAPPING_QUESTION", "UNCERTAIN_REQUIRES_REVIEW",
)

# Hand-confirmed classifications for specific findings, established by
# reading the finding's own text and the gate's predicate trace directly
# (see this project's prior root-cause validation) -- kept as an explicit,
# auditable override table rather than folded silently into the automatic
# rule, since the distinguishing evidence (e.g. "this is a cross-function/
# cross-contract callback shape a single intra-procedural gate cannot
# capture by construction") is not mechanically derivable from the
# predicate rows alone.
_HAND_CLASSIFIED_MISSES: dict[str, tuple[str, str]] = {
    "2024-01-renft/H-03": (
        "GROUND_TRUTH_MAPPING_QUESTION",
        "The reentrant callback (onERC1155Receive) fires during an external protocol's (Seaport's) "
        "own token transfer, and the vulnerable state write happens afterward in a SEPARATE function "
        "invoked as that protocol's own callback -- not 'this function calls out, then writes state "
        "within itself.' A single intra-procedural call-then-write gate cannot capture this shape by "
        "construction; whether the citation's routing unit is even the right seed for this cross-"
        "function exploit is itself the open question.",
    ),
}


def _predicate_summary(rows: list[dict]) -> dict:
    evaluated, satisfied, missing, unresolved = set(), set(), set(), set()
    for row in rows:
        if row["routing_unit"] is None:
            continue
        for pred in row["predicates"]:
            name, status = pred["predicate"], pred["status"]
            evaluated.add(name)
            if status == "SATISFIED":
                satisfied.add(name)
            elif status == "MISSING":
                missing.add(name)
            elif status == "UNRESOLVED":
                unresolved.add(name)
    return {
        "predicates_evaluated": sorted(evaluated), "predicates_satisfied": sorted(satisfied),
        "predicates_missing": sorted(missing), "predicates_unresolved": sorted(unresolved),
    }


def _auto_classify_miss(pred_summary: dict) -> tuple[str, str]:
    if pred_summary["predicates_unresolved"]:
        return "EXTRACTION_FAILURE", (
            f"At least one predicate ({', '.join(pred_summary['predicates_unresolved'])}) could not "
            f"be resolved by the bounded extraction search -- 'could not determine' is never silently "
            f"treated as 'proven absent,' so this is an extraction gap, not a genuine gate miss."
        )
    if pred_summary["predicates_missing"]:
        return "CURRENT_GATE_STRUCTURALLY_INAPPLICABLE", (
            f"All predicates resolved cleanly; the gate did not fire because "
            f"{', '.join(pred_summary['predicates_missing'])} was genuinely MISSING for this routing "
            f"unit -- the finding's real mechanism is not the structural shape this gate checks for."
        )
    return "UNCERTAIN_REQUIRES_REVIEW", (
        "No unresolved or missing predicate explains the non-fire from the predicate trace alone; "
        "needs direct human review against the finding's own text."
    )


def build_miss_analysis(accepted_positive: list[dict], gate_rows: list[dict]) -> list[dict]:
    by_finding = _group_by_finding(gate_rows, "finding_id")
    misses = []
    for f in accepted_positive:
        if f["gate_fired"]:
            continue
        rows = by_finding[f["finding_id"]]
        pred_summary = _predicate_summary(rows)
        if f["finding_id"] in _HAND_CLASSIFIED_MISSES:
            category, mechanism_note = _HAND_CLASSIFIED_MISSES[f["finding_id"]]
        else:
            category, mechanism_note = _auto_classify_miss(pred_summary)
        misses.append({
            "finding_id": f["finding_id"], "audit_id": f["audit_id"], "family": f["family"],
            "resolved_routing_units": f["routing_units"],
            **pred_summary,
            "vulnerability_mechanism_note": mechanism_note,
            "category": category,
        })
    assert all(m["category"] in _MISS_CATEGORIES for m in misses)
    return misses


# --- aggregate metrics (Phase 5) ---------------------------------------------


def build_metrics(
    accepted_populations: dict, incorrect_claims_resolved: list[dict], labeled_routes: list[dict],
    citation_outcome_histogram_accepted: dict, citation_outcome_histogram_incorrect: dict,
) -> dict:
    accepted_positive = accepted_populations["accepted_positive"]

    per_family_accepted = {}
    for fam in _FAMILIES:
        confirmed = [f for f in accepted_positive + accepted_populations["accepted_unresolved"] if f["family"] == fam]
        resolved = [f for f in accepted_positive if f["family"] == fam]
        unresolved = [f for f in accepted_populations["accepted_unresolved"] if f["family"] == fam]
        fired = [f for f in resolved if f["gate_fired"]]
        per_family_accepted[fam] = {
            "total_confirmed_findings": len(confirmed), "resolved_findings": len(resolved),
            "unresolved_findings": len(unresolved), "findings_with_gate_fire": len(fired),
            "findings_with_no_gate_fire": len(resolved) - len(fired),
            "gate_coverage_among_resolved": (len(fired) / len(resolved)) if resolved else None,
        }
    total_confirmed = sum(v["total_confirmed_findings"] for v in per_family_accepted.values())
    total_resolved = sum(v["resolved_findings"] for v in per_family_accepted.values())
    assert total_confirmed == len(accepted_positive) + len(accepted_populations["accepted_unresolved"]), \
        "per-family totals must sum to the global total"

    incorrect_fired = [c for c in incorrect_claims_resolved if c["gate_fired"]]
    incorrect_metrics = {
        "total_classified_incorrect_claims": len(incorrect_claims_resolved),
        "resolved_incorrect_claims": len(incorrect_claims_resolved),  # population is already resolved-only
        "incorrect_claims_where_gate_fires": len(incorrect_fired),
        "gate_fire_rate_on_resolved_incorrect_claims": (
            len(incorrect_fired) / len(incorrect_claims_resolved) if incorrect_claims_resolved else None
        ),
    }

    route_label_counts: dict[str, int] = defaultdict(int)
    audit_distribution: dict[str, int] = defaultdict(int)
    family_distribution: dict[str, int] = defaultdict(int)
    for r in labeled_routes:
        route_label_counts[r["route_label"]] += 1
        audit_distribution[r["audit_id"]] += 1
        family_distribution[r["family"]] += 1
    route_metrics = {
        "total_routes": len(labeled_routes),
        "unique_routing_units": len({(r["audit_id"], r["routing_unit"]) for r in labeled_routes}),
        "accepted_matched_routes": route_label_counts["ACCEPTED_MATCHED"],
        "incorrect_claim_matched_routes": route_label_counts["INCORRECT_CLAIM_MATCHED"],
        "both_matched_routes": route_label_counts["BOTH_MATCHED"],
        "unconfirmed_routes": route_label_counts["UNCONFIRMED"],
        "family_distribution": dict(family_distribution),
        "audit_distribution": dict(audit_distribution),
    }

    return {
        "accepted_findings": {
            "per_family": per_family_accepted,
            "total_confirmed_findings": total_confirmed,
            "total_resolved_findings": total_resolved,
            "total_findings_with_gate_fire": sum(v["findings_with_gate_fire"] for v in per_family_accepted.values()),
            "total_resolved_findings_with_no_fire": sum(
                v["findings_with_no_gate_fire"] for v in per_family_accepted.values()
            ),
            "not_applicable_count": len(accepted_populations["not_applicable"]),
            "uncertain_count": len(accepted_populations["uncertain"]),
            "citation_outcome_histogram": citation_outcome_histogram_accepted,
        },
        "incorrect_claims": {**incorrect_metrics, "citation_outcome_histogram": citation_outcome_histogram_incorrect},
        "whole_graph_routes": route_metrics,
    }


def _citation_outcome_histogram(gate_rows: list[dict], id_field: str) -> dict[str, int]:
    hist: dict[str, int] = defaultdict(int)
    seen: set[tuple] = set()
    for row in gate_rows:
        key = (row[id_field], row.get("citation"))
        if key in seen:
            continue
        seen.add(key)
        outcome = row.get("citation_outcome")
        if outcome is not None:
            hist[outcome] += 1
    return dict(hist)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--study-dir", type=Path, required=True, help="Directory with gate_evaluation.jsonl etc.")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    gate_rows = _read_jsonl(args.study_dir / "gate_evaluation.jsonl")
    incorrect_gate_rows = _read_jsonl(args.study_dir / "incorrect_gate_evaluation.jsonl")
    route_rows = _read_jsonl(args.study_dir / "route_manifest.jsonl")

    accepted_populations = build_accepted_populations(gate_rows)
    incorrect_claims_resolved = build_incorrect_claim_population(incorrect_gate_rows)
    labeled_routes = label_routes(route_rows, accepted_populations["accepted_positive"], incorrect_claims_resolved)
    miss_analysis = build_miss_analysis(accepted_populations["accepted_positive"], gate_rows)
    metrics = build_metrics(
        accepted_populations, incorrect_claims_resolved, labeled_routes,
        _citation_outcome_histogram(gate_rows, "finding_id"),
        _citation_outcome_histogram(incorrect_gate_rows, "incorrect_finding_id"),
    )

    report = {
        "metrics": metrics,
        "accepted_positive_population": accepted_populations["accepted_positive"],
        "accepted_unresolved_population": accepted_populations["accepted_unresolved"],
        "incorrect_claim_population": incorrect_claims_resolved,
        "miss_analysis": miss_analysis,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
