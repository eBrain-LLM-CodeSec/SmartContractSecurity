"""Renders a `pipeline_e2e.PipelineArtifacts` run into a gradeable
`audit.md` -- freeform markdown prose, not a strict schema, since
`DetectGrader` is an LLM judge reading free text (confirmed against the
real, already-graded `audit.md` from the PoolTogether task10 run: plain
prose, no special markup DetectGrader depends on).

One section per requirement whose FINAL conformance state is FAIL --
PASS/INCONCLUSIVE/INSUFFICIENT_EVIDENCE requirements are not findings and
are deliberately omitted from the report body (DetectGrader grades
reported findings against ground truth, not a full requirement-by-
requirement conformance matrix).
"""
from __future__ import annotations

from rtf.l12_evaluation.codex_bridge import corpus_by_req_id
from rtf.l12_evaluation.metrics import ConformanceState
from rtf.l12_evaluation.pipeline_e2e import PipelineArtifacts


def _evidence_citation_lines(evidence) -> list[str]:
    return [f"  - {e.location}: {e.detail}" if e.detail else f"  - {e.location}" for e in evidence]


def generate_audit_md(artifacts: PipelineArtifacts, audit_title: str = "") -> str:
    corpus = corpus_by_req_id()
    lines: list[str] = []
    title = audit_title or artifacts.run.audit_id
    lines.append(f"# Security Audit Report: {title}\n")
    lines.append(
        "Findings below were produced by the RTF (Requirement Translation Framework) "
        "pipeline: EthTrust requirement routing, deterministic evidence collection, "
        "bounded LLM judgment, and (where the bounded judgment was inconclusive, "
        "insufficient, or low-confidence) graph-gated Codex investigation.\n"
    )

    fail_req_ids = [
        req_id for req_id, r in artifacts.run.routed.items()
        if r.conformance_state == ConformanceState.FAIL
    ]

    if not fail_req_ids:
        lines.append("No FAIL findings were produced by this pipeline run.\n")
        return "\n".join(lines)

    for req_id in fail_req_ids:
        result = artifacts.run.routed[req_id]
        req_record = corpus.get(req_id, {})
        req_title = req_record.get("title", req_id)
        req_text = req_record.get("normative_text", "")

        escalated = req_id in artifacts.codex_results
        if escalated:
            codex_result = artifacts.codex_results[req_id]
            final_decision = codex_result.final_decision or {}
            reasoning = final_decision.get("reasoning_summary", "(no reasoning summary returned)")
            confidence = final_decision.get("confidence", "unknown")
            path_note = (
                f"Determined via graph-gated Codex investigation "
                f"({codex_result.graph_tool_calls} graph queries, {codex_result.wall_clock_s:.0f}s)."
            )
        else:
            raw = artifacts.raw_l8_judgments.get(req_id, {})
            first_pass = raw.get("first_pass", raw) if raw else {}
            reasoning = first_pass.get("reasoning_summary", "(no reasoning summary returned)")
            confidence = first_pass.get("confidence", "unknown")
            path_note = "Determined via bounded LLM judgment on deterministically-collected evidence."

        locations = sorted({e.location for e in result.evidence}) or ["(location not resolved)"]

        lines.append(f"## {req_id}: {req_title}\n")
        lines.append(f"**Requirement:** {req_text}\n")
        lines.append(f"**Location(s):** {', '.join(locations)}\n")
        lines.append(f"**Confidence:** {confidence}\n")
        lines.append(f"**Mechanism:** {reasoning}\n")
        if result.evidence:
            lines.append("**Supporting evidence:**")
            lines.extend(_evidence_citation_lines(result.evidence))
            lines.append("")
        lines.append(f"_{path_note}_\n")

    return "\n".join(lines)
