"""Externalizes large raw tool outputs to disk, keeping the model-facing
conversation compact (RTF_SECURITY_AGENT_CONTEXT_MANAGEMENT_DESIGN.md
section 4).

The measured bloat source (RTF_SECURITY_AGENT_EFFICIENCY_INVESTIGATION_
20260817.md) is NOT the model-authored `state.Evidence` objects -- those
are already compact by prompt design (a short claim + a short excerpt).
It is the RAW TOOL RESULT dict appended verbatim into the conversation at
every `call_tool` turn (`get_contract_source` on a large contract alone
can be tens of thousands of tokens), resent on every subsequent turn
because nothing in the kernel ever prunes history. This module is what
lets the kernel append a short summary instead, while keeping the full
result retrievable (auditability preserved, not weakened) via a stable
evidence_id.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_SUMMARY_PREVIEW_CHARS = 2000
"""Raised from 400 (found live, 2026-08-26, native-tool-calling canto
rerun): 400 chars is well under a typical Solidity function body, so
almost every get_function_source/get_contract_source result got
truncated -- forcing a SEPARATE read_evidence call just to see what the
agent had, in effect, already fetched. Quantified in a real cluster: 7
of 16 tool-call steps (44% of that cluster's entire step budget) were
pure re-fetch overhead, not new investigation. This was always true
under the single-tool-per-turn design too, but cost proportionally less
there (one extra turn either way); under native multi-tool-calling it
now costs a whole separate round-trip on top of an otherwise-batched
turn. 2000 chars covers most single-function reads without truncation
while still bounding a large multi-hit search or whole-contract dump."""


class UnknownEvidenceRefError(KeyError):
    """Raised by `EvidenceStore.read` for an evidence_id that was never
    stored -- a model reference to a nonexistent id is a real error to
    surface, not something to silently return empty content for."""


@dataclass
class StoredEvidence:
    evidence_id: str
    summary: str
    path: Path


def _preview(text: str, limit: int = _SUMMARY_PREVIEW_CHARS) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"... [{len(text) - limit} more chars, use read_evidence to see the rest]"


def _describe_tool_result(tool: str, result: dict) -> str:
    """Deterministic, non-LLM summary: file/contract/function/line-range
    (whatever the result dict actually has) plus a short text preview.
    Never calls a model -- cheap, reproducible, and testable without one."""
    location_bits = []
    for key in ("file", "path", "contract", "name"):
        value = result.get(key)
        if value:
            location_bits.append(f"{key}={value}")
    lines = result.get("lines")
    if lines:
        location_bits.append(f"lines={min(lines)}-{max(lines)}" if isinstance(lines, list) else f"lines={lines}")
    location = ", ".join(location_bits) or "(no location fields in result)"

    text_field = result.get("source") or result.get("content") or ""
    hits = result.get("hits")
    if hits and not text_field:
        text_field = "\n".join(f"{h.get('file')}:{h.get('line')}: {h.get('text')}" for h in hits[:20])

    preview = _preview(text_field) if text_field else "(no textual content in result)"
    return f"{tool} -- {location}\n{preview}"


class EvidenceStore:
    """One instance per cluster investigation, rooted at that cluster's
    own scratch directory (`scratch/security_agent/<cluster>/evidence/`
    -- alongside the existing `cache/`/`trajectory.jsonl` files that
    directory already holds)."""

    def __init__(self, cluster_scratch_dir: Path):
        self.evidence_dir = Path(cluster_scratch_dir) / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self._summaries: dict[str, str] = {}

    def store(self, tool_call_id: str, tool: str, result: dict) -> StoredEvidence:
        """`tool_call_id` (e.g. "tool-3", matching `ToolCallRecord.id`)
        is reused as the evidence_id -- one tool call, one evidence
        entry, no separate id scheme to keep in sync."""
        path = self.evidence_dir / f"{tool_call_id}.json"
        path.write_text(json.dumps({"tool": tool, "result": result}, indent=2), encoding="utf-8")
        summary = _describe_tool_result(tool, result)
        self._summaries[tool_call_id] = summary
        return StoredEvidence(evidence_id=tool_call_id, summary=summary, path=path)

    def read(self, evidence_id: str) -> str:
        path = self.evidence_dir / f"{evidence_id}.json"
        if not path.exists():
            raise UnknownEvidenceRefError(evidence_id)
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data["result"], indent=2)

    def summary(self, evidence_id: str) -> str | None:
        return self._summaries.get(evidence_id)

    def known_ids(self) -> list[str]:
        """All evidence ids stored so far, sorted. Used by `read_evidence`
        to give a self-correcting error message when the model calls it
        with a missing/wrong id (found live, 2026-08-26: the model called
        `read_evidence({})` -- no evidence_id at all -- 3 times in one
        cluster, each one a wasted step, despite the tool schema marking
        `evidence_id` as required; this proxy does not hard-enforce
        required-argument completeness the way `strict: true` is
        documented to)."""
        return sorted(self._summaries)
