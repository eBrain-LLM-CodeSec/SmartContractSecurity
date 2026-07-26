"""Dedup/merge confirmed findings into a report-ready model.

Because DetectGrader reads the whole audit.md and is recall-only, emitting
every confirmed finding is safe -- dedup here is about keeping the report
specific and readable, not about avoiding a false-positive penalty (there
isn't one).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from a4v.graph import ProgramGraph
from a4v.score import Candidate


@dataclass
class Finding:
    title: str
    contract: str
    vuln_class: str | None
    severity: str | None
    mechanism: str
    file: str | None
    lines: list[int]
    fix: str | None = None
    source_node_ids: list[str] = field(default_factory=list)


def _title(vuln_class: str | None, contract: str) -> str:
    label = (vuln_class or "issue").replace("_", " ")
    return f"{label.capitalize()} in {contract}"


def candidates_to_findings(candidates: list[Candidate], pg: ProgramGraph) -> list[Finding]:
    """Turn kept, Commentator-confirmed candidates into Findings (one per
    candidate; call `dedup_and_merge` afterward to collapse near-duplicates).
    """
    findings = []
    for c in candidates:
        if not c.kept or c.comment is None or not c.comment.suspicious:
            continue
        node_data = pg.graph.nodes[c.node_id]
        contract = node_data.get("contract", "")
        findings.append(Finding(
            title=_title(c.comment.vuln_class, contract),
            contract=contract,
            vuln_class=c.comment.vuln_class,
            severity=c.comment.severity,
            mechanism=c.comment.rationale,
            file=node_data.get("file"),
            lines=c.comment.lines or node_data.get("lines", []),
            source_node_ids=[c.node_id],
        ))
    return findings


def _dedup_key(f: Finding) -> tuple[str, str, str]:
    return (f.contract, f.vuln_class or "", f.file or "")


def dedup_and_merge(findings: list[Finding]) -> list[Finding]:
    """Merge findings that share (contract, vuln_class, file) -- same
    mechanism+location -- keeping the union of lines/source nodes and the
    highest severity."""
    severity_rank = {"high": 3, "medium": 2, "low": 1, None: 0}
    merged: dict[tuple[str, str, str], Finding] = {}
    for f in findings:
        key = _dedup_key(f)
        if key not in merged:
            merged[key] = f
            continue
        existing = merged[key]
        existing.lines = sorted(set(existing.lines) | set(f.lines))
        existing.source_node_ids = list(dict.fromkeys(existing.source_node_ids + f.source_node_ids))
        if severity_rank.get(f.severity, 0) > severity_rank.get(existing.severity, 0):
            existing.severity = f.severity
        if len(f.mechanism) > len(existing.mechanism):
            existing.mechanism = f.mechanism
    return list(merged.values())
