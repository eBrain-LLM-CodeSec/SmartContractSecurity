"""Phase 2 conformance audit: classify every EthTrust requirement RTF
currently claims to "support" along the fidelity dimensions the redesign
plan (`RTF_V3_REDESIGN_PLAN.md`) requires, instead of assuming that
"parsed into the corpus" == "implemented."

Purely mechanical / deterministic -- no LLM calls. Reads the real corpus
(`l1_corpus/requirement_corpus.json`) and the real predicate registry
(`l12_evaluation/registry.py`), so results reflect actual current code,
not a hand-maintained list that can drift.

Usage: `.venv/bin/python3 -m rtf.l12_evaluation.requirement_fidelity_audit
[--out PATH]` from the repo root (parent of `rtf/`).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from rtf.l12_evaluation import registry
from rtf.l5_predicates import predicates as P

CORPUS_PATH = Path(__file__).resolve().parent.parent / "l1_corpus" / "requirement_corpus.json"
CONFORMANCE_DIR = Path(__file__).resolve().parent.parent / "tests" / "ethtrust_conformance"

# Predicates that produce evidence purely by comparing documentation claims
# against implementation (no code-PATTERN detector) -- weaker applicability
# signal than a real structural predicate, per the redesign plan's B2
# finding. Kept as an explicit name list (not a heuristic) so it is exact
# and auditable.
_DOCUMENTARY_ONLY_FUNCS = {P.collect_documentary_and_implementation_evidence}

# The 3 corpus requirements that are pure aggregations over every other
# requirement ("pass Level 1" / "pass Level 2" / "meet all applicable
# requirements") -- by design they have no independent predicate; their
# real "check" is "did every constituent requirement resolve favorably."
_COMPOSITE_AGGREGATE_REQ_IDS = {
    "req-2-pass-l1",
    "req-3-pass-l2",
    "req-R-meet-all-possible",
}

# Phase 6 investigation-shape classification -- generic keyword signals
# derived from each requirement's OWN normative_text, not from any
# EVMbench finding. Order matters: first match wins. Kept in sync with
# the real guidance table in context_artifacts.py (INVESTIGATION_SHAPE_
# GUIDANCE) -- see that module for the guidance text itself.
_SHAPE_PATTERNS: list[tuple[str, re.Pattern]] = [
    (
        "cross_boundary_semantics",
        re.compile(
            r"\bblock\.(number|timestamp)\b|\bexternal (call|contract)\b.*\b(block|time|argument)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "domain_validation",
        re.compile(
            r"\binvalid\b|\bout[- ]of[- ]range\b|\bdomain\b|\bmalform|\breject\b|\bvalidat",
            re.IGNORECASE,
        ),
    ),
    (
        "resource_growth",
        re.compile(
            r"\bgrow(s|th)?\b|\bincreas.*over time\b|\bdata structures?\b.*\bgas\b|\bgas\b.*\bdata structures?\b",
            re.IGNORECASE,
        ),
    ),
]


def _classify_shape(normative_text: str) -> str:
    for shape, pattern in _SHAPE_PATTERNS:
        if pattern.search(normative_text or ""):
            return shape
    return "generic"


def _load_corpus() -> list[dict[str, Any]]:
    data = json.loads(CORPUS_PATH.read_text())
    return data if isinstance(data, list) else data.get("requirements", data)


def _applicability_for(req_id: str) -> str:
    specs = registry.REGISTRY.get(req_id)
    if specs is None:
        return "not_routed"
    funcs = {spec.func for spec in specs}
    if funcs - _DOCUMENTARY_ONLY_FUNCS:
        return "structural_predicate"
    return "documentary_evidence_only"


def _routing_for(req_id: str) -> str:
    if req_id in registry.DETERMINISTIC_COMPLETE_REQ_IDS:
        return "deterministic"
    if req_id in registry.AGENT_REQUIRED_REQ_IDS:
        return "agent_required"
    return "not_routed"


def _conformance_fixtures_for(req_id: str) -> tuple[bool, bool]:
    """(positive_test_exists, negative_test_exists) -- presence of a
    vulnerable/safe Solidity fixture pair under tests/ethtrust_conformance/
    for this req_id. Purely a filesystem check; existence of the FIXTURE
    is necessary but not sufficient for CONFORMANCE_PASS (the harness must
    also have actually run green -- see `--results` handling below)."""
    if not CONFORMANCE_DIR.exists():
        return False, False
    req_dir = CONFORMANCE_DIR / req_id
    if not req_dir.exists():
        return False, False
    vuln = any(req_dir.glob("*vulnerable*.sol"))
    safe = any(req_dir.glob("*safe*.sol"))
    return vuln, safe


def audit_requirement(record: dict[str, Any], conformance_results: dict[str, str]) -> dict[str, Any]:
    req_id = record["req_id"]
    normative_text = record.get("normative_text", "")
    source_preserved = bool(normative_text.strip())

    if req_id in _COMPOSITE_AGGREGATE_REQ_IDS:
        return {
            "requirement_id": req_id,
            "level": record.get("level"),
            "source_preserved": source_preserved,
            "applicability": "composite_aggregate",
            "routing": "composite_aggregate",
            "investigation_shape": "generic",
            "positive_test_exists": False,
            "negative_test_exists": False,
            "end_to_end_test_exists": False,
            "state": "N/A_COMPOSITE",
            "notes": (
                "Pure aggregation over every other requirement (\"pass Level "
                "1/2\"/\"meet all applicable requirements\") -- has no "
                "independent predicate BY DESIGN, not a gap. Its real "
                "conformance is a function of every constituent requirement's "
                "own state."
            ),
        }

    applicability = _applicability_for(req_id)
    routing = _routing_for(req_id)
    has_exceptions_or_overrides = bool(
        record.get("exceptions_referenced") or record.get("overriding_requirements")
        or record.get("referenced_requirements")
    )
    shape = _classify_shape(normative_text)
    pos, neg = _conformance_fixtures_for(req_id)
    e2e_state = conformance_results.get(req_id)
    e2e_exists = e2e_state == "PASS"

    # Strict, conservative state assignment -- never assume implemented
    # merely because parsed/routed.
    if applicability == "not_routed":
        state = "UNIMPLEMENTED"
        notes = "No predicate registered at all -- never routed to any evidence collection."
    elif applicability == "documentary_evidence_only":
        state = "PARTIAL"
        notes = (
            "Only a generic documentary-evidence collector is registered -- "
            "no structural code-pattern predicate exists for this "
            "requirement's own subject matter, so applicability depends on "
            "the target's own documentation rather than its code."
        )
    elif pos and neg and e2e_exists:
        state = "CONFORMANCE_PASS"
        notes = "Structural predicate + fixture pair + green end-to-end conformance run."
    elif applicability == "structural_predicate":
        state = "IMPLEMENTED_UNTESTED"
        notes = "Structural predicate + routing exist; no conformance fixture/test yet."
    else:
        state = "PARTIAL"
        notes = "Unclassified partial state."

    return {
        "requirement_id": req_id,
        "level": record.get("level"),
        "source_preserved": source_preserved,
        "has_exceptions_or_overriding_or_references": has_exceptions_or_overrides,
        "applicability": applicability,
        "routing": routing,
        "investigation_shape": shape,
        "positive_test_exists": pos,
        "negative_test_exists": neg,
        "end_to_end_test_exists": e2e_exists,
        "state": state,
        "notes": notes,
    }


def run_audit(conformance_results: dict[str, str] | None = None) -> list[dict[str, Any]]:
    conformance_results = conformance_results or {}
    return [audit_requirement(r, conformance_results) for r in _load_corpus()]


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    from collections import Counter

    state_counts = Counter(r["state"] for r in results)
    applicability_counts = Counter(r["applicability"] for r in results)
    shape_counts = Counter(r["investigation_shape"] for r in results)
    return {
        "total_requirements": len(results),
        "by_state": dict(state_counts),
        "by_applicability": dict(applicability_counts),
        "by_investigation_shape": dict(shape_counts),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("l12_evaluation/requirement_fidelity_audit.json"))
    args = parser.parse_args()

    results = run_audit()
    summary = summarize(results)
    payload = {"summary": summary, "requirements": results}
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"Wrote {len(results)} requirement records to {args.out}")


if __name__ == "__main__":
    main()
