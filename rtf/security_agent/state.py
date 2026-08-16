"""Structured investigation state for the security-agent kernel.

Pydantic models, not plain dataclasses -- deliberately different from the
rest of `rtf/`, which uses frozen dataclasses everywhere (see
SECURITY_AGENT_KERNEL_DESIGN.md section 3 for why: validated tool I/O and
JSON-schema generation for LLM tool-calling are the actual new
capabilities Pydantic buys here, not just a style preference).

One `ClusterInvestigationState` is created per cluster (never per
property/requirement -- see `RequirementState`, one per property_id,
living INSIDE this single shared state object). Evidence lives once, in
`ClusterInvestigationState.evidence`, and is referenced by id from
`Hypothesis`/`RequirementState` -- this is what lets evidence discovered
while investigating one property be reused, without copying, by every
other property in the cluster that hypothesis/evidence is relevant to.
"""
from __future__ import annotations

import time
from enum import Enum

from pydantic import BaseModel, Field


class RequirementResolution(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class HypothesisStatus(str, Enum):
    OPEN = "OPEN"
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class UnknownEvidenceIdError(KeyError):
    """Raised when code tries to reference an evidence id that was never
    added via `ClusterInvestigationState.add_evidence` -- evidence must
    exist in the shared pool before anything can point at it, so a
    dangling reference is a bug, not a valid state."""


class DuplicateIdError(KeyError):
    """Raised when adding an evidence/hypothesis whose id already exists
    -- ids are meant to be assigned once by the kernel, never overwritten
    silently (an accidental id collision would otherwise let one call
    site's evidence silently clobber another's)."""


class ToolCallRecord(BaseModel):
    id: str
    tool: str
    args: dict
    result_summary: str
    timestamp: float = Field(default_factory=time.time)


class Evidence(BaseModel):
    """One concrete, citable fact gathered during investigation. Every
    final verdict must trace back to Evidence objects, never to bare
    free-form reasoning (brief Phase 10: Claim / Evidence /
    Interpretation / Verdict separation -- this model is the "Evidence"
    half of that split; "Claim" lives on the Hypothesis or
    RequirementState that cites this evidence, not here)."""

    id: str
    claim: str
    source_file: str
    source_contract: str | None = None
    source_function: str | None = None
    source_lines: str | None = None
    tool_call_id: str | None = None
    raw_excerpt: str | None = None


class VerdictRecord(BaseModel):
    """The final Claim/Evidence/Interpretation/Verdict chain for one
    property. Evidence is referenced from the cluster-wide pool by id,
    never copied into this record."""

    claim: str
    evidence_ids: list[str]
    interpretation: str
    verdict: RequirementResolution


class Hypothesis(BaseModel):
    id: str
    claim: str
    originating_property_ids: list[str] = Field(default_factory=list)
    """Which property/properties this hypothesis was raised while
    investigating -- can span more than one, since a single hypothesis
    (e.g. "this argument may be a block-number/timestamp mismatch across
    the call boundary") can be relevant to several requirements in the
    same cluster at once."""
    status: HypothesisStatus = HypothesisStatus.OPEN
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    next_evidence_needed: str | None = None


class RequirementState(BaseModel):
    """Per-property status living inside a cluster's shared
    ClusterInvestigationState. NOT a separate agent session or a separate
    top-level state object -- the cluster is the execution unit, this is
    only the per-property verdict/bookkeeping view over it."""

    property_id: str
    parent_requirement_id: str | None = None
    status: RequirementResolution = RequirementResolution.UNRESOLVED
    resolution_reason: str | None = None
    final_assessment: VerdictRecord | None = None
    hypothesis_ids: list[str] = Field(default_factory=list)
    evidence_for_ids: list[str] = Field(default_factory=list)
    evidence_against_ids: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    counterexample_attempts: list[str] = Field(default_factory=list)
    """What was actually TRIED (e.g. "zero-value transfer", "unauthorized
    caller"), recorded regardless of whether it found a violation -- this
    is what later lets a completion check (rtf.security_agent.completion,
    not implemented yet) verify real falsification attempts happened,
    not just that the model asserted PASS."""


class TokenUsage(BaseModel):
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


class ClusterInvestigationState(BaseModel):
    cluster_id: str
    property_ids: list[str]
    requirement_states: dict[str, RequirementState] = Field(default_factory=dict)
    hypotheses: dict[str, Hypothesis] = Field(default_factory=dict)
    evidence: dict[str, Evidence] = Field(default_factory=dict)
    inspected_files: set[str] = Field(default_factory=set)
    inspected_contracts: set[str] = Field(default_factory=set)
    inspected_functions: set[str] = Field(default_factory=set)
    tool_history: list[ToolCallRecord] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    step_count: int = 0

    @classmethod
    def initial(cls, cluster_id: str, property_ids: list[str],
                parent_requirement_ids: dict[str, str | None] | None = None) -> "ClusterInvestigationState":
        """One RequirementState per property_id, all UNRESOLVED -- the
        starting state for a fresh cluster investigation."""
        parent_requirement_ids = parent_requirement_ids or {}
        return cls(
            cluster_id=cluster_id,
            property_ids=list(property_ids),
            requirement_states={
                pid: RequirementState(property_id=pid, parent_requirement_id=parent_requirement_ids.get(pid))
                for pid in property_ids
            },
        )

    # -- evidence / hypotheses --------------------------------------------------

    def add_evidence(self, evidence: Evidence) -> None:
        if evidence.id in self.evidence:
            raise DuplicateIdError(f"evidence id already exists: {evidence.id}")
        self.evidence[evidence.id] = evidence
        if evidence.source_file:
            self.inspected_files.add(evidence.source_file)
        if evidence.source_contract:
            self.inspected_contracts.add(evidence.source_contract)
        if evidence.source_function:
            self.inspected_functions.add(f"{evidence.source_contract}.{evidence.source_function}"
                                          if evidence.source_contract else evidence.source_function)

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        if hypothesis.id in self.hypotheses:
            raise DuplicateIdError(f"hypothesis id already exists: {hypothesis.id}")
        for eid in (*hypothesis.supporting_evidence_ids, *hypothesis.contradicting_evidence_ids):
            self._require_evidence(eid)
        self.hypotheses[hypothesis.id] = hypothesis
        for pid in hypothesis.originating_property_ids:
            if pid in self.requirement_states:
                self.requirement_states[pid].hypothesis_ids.append(hypothesis.id)

    def link_evidence_to_requirement(self, property_id: str, evidence_id: str, *, supports: bool) -> None:
        """The mechanism that makes evidence SHARED rather than
        duplicated: evidence gathered once (via add_evidence, possibly
        while investigating a different property) can be linked to any
        number of RequirementStates in this same cluster by id, with no
        copy of the Evidence object itself."""
        self._require_evidence(evidence_id)
        req_state = self._require_requirement(property_id)
        target = req_state.evidence_for_ids if supports else req_state.evidence_against_ids
        if evidence_id not in target:
            target.append(evidence_id)

    def _require_evidence(self, evidence_id: str) -> Evidence:
        if evidence_id not in self.evidence:
            raise UnknownEvidenceIdError(evidence_id)
        return self.evidence[evidence_id]

    def _require_requirement(self, property_id: str) -> RequirementState:
        if property_id not in self.requirement_states:
            raise KeyError(f"property_id not in this cluster: {property_id}")
        return self.requirement_states[property_id]

    # -- requirement resolution --------------------------------------------------

    def resolve_requirement(self, property_id: str, status: RequirementResolution, reason: str | None = None) -> None:
        """Pure state transition -- whether a resolution is ALLOWED
        (e.g. "not PASS while a mandatory counterexample is unattempted")
        is deliberately NOT enforced here; that policy lives in
        rtf.security_agent.completion (increment 5), which calls this
        only after its own checks pass. Keeping the two separate means
        state.py stays a small, obviously-correct data layer."""
        req_state = self._require_requirement(property_id)
        req_state.status = status
        req_state.resolution_reason = reason

    def record_verdict(self, property_id: str, *, claim: str,
                       evidence_ids: list[str], interpretation: str,
                       verdict: RequirementResolution) -> None:
        """Persist one complete CEIV chain and resolve the property.

        Every evidence id must already exist in the shared cluster pool.
        The same id may therefore support several property assessments
        without duplicating the underlying Evidence object.
        """
        req_state = self._require_requirement(property_id)
        for evidence_id in evidence_ids:
            self._require_evidence(evidence_id)
            self.link_evidence_to_requirement(property_id, evidence_id, supports=True)
        req_state.final_assessment = VerdictRecord(
            claim=claim,
            evidence_ids=list(evidence_ids),
            interpretation=interpretation,
            verdict=verdict,
        )
        self.resolve_requirement(property_id, verdict, reason=interpretation)

    def mark_unresolved_reason(self, property_id: str, reason: str) -> None:
        """Records WHY a property is still UNRESOLVED (e.g. the kernel
        exhausted its step budget, or the model never mentioned this
        property_id in its final answer) without inventing a status the
        brief's own RequirementState schema doesn't define -- there is no
        INCONCLUSIVE in {UNRESOLVED, PASS, FAIL, NOT_APPLICABLE}.
        UNRESOLVED + a recorded reason IS the "gave up explicitly, never
        silently dropped" signal; to_property_verdict_entries() surfaces
        it the same way a genuine resolution's reason is surfaced. A
        no-op if the property was already resolved (never overwrites a
        real PASS/FAIL/NOT_APPLICABLE with a bookkeeping note)."""
        req_state = self._require_requirement(property_id)
        if req_state.status == RequirementResolution.UNRESOLVED:
            req_state.resolution_reason = reason

    def evidence_for(self, property_id: str) -> list[Evidence]:
        req_state = self._require_requirement(property_id)
        return [self.evidence[eid] for eid in req_state.evidence_for_ids]

    def evidence_against(self, property_id: str) -> list[Evidence]:
        req_state = self._require_requirement(property_id)
        return [self.evidence[eid] for eid in req_state.evidence_against_ids]

    # -- tool bookkeeping --------------------------------------------------

    def record_tool_call(self, tool: str, args: dict, result_summary: str,
                         result: dict | None = None) -> ToolCallRecord:
        record = ToolCallRecord(id=f"tool-{len(self.tool_history) + 1}", tool=tool,
                                args=args, result_summary=result_summary)
        self.tool_history.append(record)
        self.step_count += 1
        if result and result.get("status") == "OK":
            file = result.get("file") or result.get("path")
            contract = result.get("contract")
            name = result.get("name")
            if file:
                self.inspected_files.add(file)
            if contract:
                self.inspected_contracts.add(contract)
            if name and tool == "get_function_source":
                self.inspected_functions.add(f"{contract}.{name}" if contract else name)
        return record

    # -- result mapping --------------------------------------------------

    def all_resolved(self) -> bool:
        return all(rs.status != RequirementResolution.UNRESOLVED for rs in self.requirement_states.values())

    def to_property_verdict_entries(self) -> list[dict]:
        """The `{"properties": [...]}` shape cluster_response_validation.py
        already expects from a Codex response -- one entry per property_id
        in this cluster, always the exact set (never missing/duplicate),
        so a `SecurityAgentResult.final_decision` built from this passes
        the same `validate_cluster_response` completeness check Codex
        responses go through today."""
        entries = []
        for pid in self.property_ids:
            req_state = self.requirement_states[pid]
            entries.append({
                "property_id": pid,
                "verdict": req_state.status.value,
                "reason": req_state.resolution_reason,
                "claim": req_state.final_assessment.claim if req_state.final_assessment else None,
                "interpretation": (req_state.final_assessment.interpretation
                                   if req_state.final_assessment else None),
                "evidence_ids": (list(req_state.final_assessment.evidence_ids)
                                 if req_state.final_assessment else []),
                "counterexample_attempts": list(req_state.counterexample_attempts),
                "evidence_for": [self.evidence[eid].model_dump() for eid in req_state.evidence_for_ids],
                "evidence_against": [self.evidence[eid].model_dump() for eid in req_state.evidence_against_ids],
            })
        return entries
