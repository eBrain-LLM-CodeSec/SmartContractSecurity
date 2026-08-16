"""The security-agent kernel's decide/execute/update control loop (brief
Phase 2). Deliberately small -- understandable by reading this file plus
state.py/tools.py/model_client.py/prompts.py in one sitting.

Increment 5 applies a mechanical completion gate to proposed conclusions.
Premature PASS verdicts are rejected back into the same loop with concrete
blocking reasons; FAIL remains CEIV/evidence-gated without PASS-only rules.
"""
from __future__ import annotations

import json
from typing import Callable, Literal

from pydantic import BaseModel, Field, model_validator

from rtf.security_agent.completion import cluster_can_conclude
from rtf.security_agent.model_client import MalformedModelResponse, ModelClient
from rtf.security_agent.prompts import build_initial_user_message, build_system_prompt
from rtf.security_agent.state import (
    ClusterInvestigationState, Evidence, Hypothesis, HypothesisStatus,
    RequirementResolution,
)
from rtf.security_agent.tools import SecurityAgentTools

DEFAULT_MAX_STEPS = 15
DEFAULT_MAX_MALFORMED_RETRIES = 2


class ToolCallAction(BaseModel):
    action: Literal["call_tool"]
    tool: str
    args: dict = Field(default_factory=dict)
    reasoning: str = ""


class PropertyVerdictInput(BaseModel):
    property_id: str
    claim: str
    evidence_ids: list[str] = Field(min_length=1)
    hypothesis_ids: list[str] = Field(min_length=1)
    interpretation: str
    verdict: Literal["PASS", "FAIL", "NOT_APPLICABLE"]


class EvidenceInput(BaseModel):
    id: str
    claim: str
    source_file: str
    source_contract: str | None = None
    source_function: str | None = None
    source_lines: str | None = None
    tool_call_id: str | None = None
    raw_excerpt: str | None = None


class HypothesisInput(BaseModel):
    id: str
    claim: str
    originating_property_ids: list[str] = Field(min_length=1)
    status: Literal["OPEN", "SUPPORTED", "REFUTED", "INCONCLUSIVE"] = "OPEN"
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    next_evidence_needed: str | None = None


class CounterexampleAttemptInput(BaseModel):
    property_id: str
    hypothesis_id: str
    attempt: str = Field(min_length=1)
    result: str = Field(min_length=1)


class UpdateInvestigationAction(BaseModel):
    action: Literal["update_investigation"]
    hypotheses: list[HypothesisInput] = Field(default_factory=list)
    counterexample_attempts: list[CounterexampleAttemptInput] = Field(default_factory=list)

    @model_validator(mode="after")
    def contains_an_update(self) -> "UpdateInvestigationAction":
        if not self.hypotheses and not self.counterexample_attempts:
            raise ValueError("update_investigation must include a hypothesis or counterexample attempt")
        return self


class ConcludeAction(BaseModel):
    action: Literal["conclude"]
    evidence: list[EvidenceInput] = Field(min_length=1)
    hypotheses: list[HypothesisInput] = Field(min_length=1)
    properties: list[PropertyVerdictInput]

    @model_validator(mode="after")
    def evidence_references_are_complete(self) -> "ConcludeAction":
        ids = [item.id for item in self.evidence]
        if len(ids) != len(set(ids)):
            raise ValueError("evidence ids must be unique")
        known = set(ids)
        missing = sorted({eid for prop in self.properties
                          for eid in prop.evidence_ids if eid not in known})
        if missing:
            raise ValueError(f"property assessments reference unknown evidence ids: {missing}")
        hypothesis_ids = {item.id for item in self.hypotheses}
        missing_hypotheses = sorted({hid for prop in self.properties
                                     for hid in prop.hypothesis_ids if hid not in hypothesis_ids})
        if missing_hypotheses:
            raise ValueError(f"property assessments reference unknown hypothesis ids: {missing_hypotheses}")
        hypothesis_evidence = {eid for hypothesis in self.hypotheses
                               for eid in (*hypothesis.supporting_evidence_ids,
                                           *hypothesis.contradicting_evidence_ids)}
        if not hypothesis_evidence <= known:
            raise ValueError("hypotheses reference unknown evidence ids")
        return self


RESPONSE_MODELS: tuple[type[BaseModel], ...] = (
    ToolCallAction, UpdateInvestigationAction, ConcludeAction,
)


def _summarize_tool_result(result: dict) -> str:
    status = result.get("status", "?")
    if status != "OK":
        return f"{status}: {result.get('reason', '')}"
    payload_keys = [k for k in result if k not in ("status", "reason")]
    return f"OK ({', '.join(payload_keys)})"


class SecurityAgentKernel:
    def __init__(self, tools: SecurityAgentTools, model_client: ModelClient,
                 max_steps: int = DEFAULT_MAX_STEPS,
                 max_malformed_retries: int = DEFAULT_MAX_MALFORMED_RETRIES,
                 enforce_completion: bool = True,
                 event_sink: Callable[[str, dict], None] | None = None):
        self.tools = tools
        self.model_client = model_client
        self.max_steps = max_steps
        self.max_malformed_retries = max_malformed_retries
        self.enforce_completion = enforce_completion
        self.event_sink = event_sink

    def run_cluster(
        self, cluster_id: str, property_ids: list[str],
        protocol_context_md: str, requirement_context_by_property: dict[str, str],
        cluster_plan_md: str,
        parent_requirement_ids: dict[str, str | None] | None = None,
        reasoning_categories_by_property: dict[str, str | None] | None = None,
    ) -> ClusterInvestigationState:
        """One shared ClusterInvestigationState for the WHOLE cluster --
        never one state object per property_id, matching the brief's
        "one cluster does NOT create independent agent sessions"
        invariant (see state.test_one_cluster_multiple_requirements_is_
        one_shared_state_object for the state-layer version of this same
        check)."""
        state = ClusterInvestigationState.initial(cluster_id, property_ids, parent_requirement_ids)
        self._emit("cluster_started", {"cluster_id": cluster_id, "property_ids": property_ids})
        messages: list[dict] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_initial_user_message(
                property_ids, protocol_context_md, requirement_context_by_property, cluster_plan_md)},
        ]

        malformed_retries = 0
        while state.step_count < self.max_steps:
            try:
                turn = self.model_client.decide(messages)
            except MalformedModelResponse as e:
                self._emit("malformed_model_response", {"errors": e.errors, "raw": e.raw})
                malformed_retries += 1
                if malformed_retries > self.max_malformed_retries:
                    self._finalize_unresolved(state, property_ids, "kernel_malformed_response_exhausted")
                    self._emit("cluster_finished", {"reason": "kernel_malformed_response_exhausted"})
                    return state
                messages.append({"role": "assistant", "content": json.dumps(e.raw)})
                messages.append({"role": "user", "content":
                    f"Your last response did not match the required JSON shape ({e.errors}). "
                    "Respond again with exactly one fenced JSON block matching call_tool or conclude."})
                continue

            self._record_token_usage(state, turn.chat_result)
            self._emit("model_action", {"action": turn.raw,
                                         "token_usage": state.token_usage.model_dump()})
            messages.append({"role": "assistant", "content": json.dumps(turn.raw)})

            if isinstance(turn.parsed, ConcludeAction):
                proposed = state.model_copy(deep=True)
                self._apply_conclusion(proposed, property_ids, turn.parsed)
                completion = cluster_can_conclude(proposed, reasoning_categories_by_property)
                if self.enforce_completion and not completion.ready:
                    self._apply_conclusion_material(state, turn.parsed)
                    state.step_count += 1
                    messages.append({"role": "user", "content":
                        "Conclusion rejected by the mechanical completion gate: "
                        + "; ".join(completion.blocking_reasons)
                        + ". Continue investigating and update structured state before concluding again."})
                    self._emit("conclusion_rejected", {"blocking_reasons": completion.blocking_reasons})
                    continue
                state = proposed
                self._emit("cluster_finished", {"reason": "concluded",
                                                 "verdicts": {pid: rs.status.value
                                                              for pid, rs in state.requirement_states.items()}})
                return state

            if isinstance(turn.parsed, UpdateInvestigationAction):
                error = self._apply_investigation_update(state, turn.parsed)
                state.step_count += 1
                messages.append({"role": "user", "content":
                    f"Investigation-state update {'rejected: ' + error if error else 'recorded.'}"})
                self._emit("investigation_updated", {"rejected_reason": error,
                                                      "hypothesis_ids": [h.id for h in turn.parsed.hypotheses],
                                                      "counterexample_attempts": len(turn.parsed.counterexample_attempts)})
                continue

            action: ToolCallAction = turn.parsed
            result = self.tools.call(action.tool, action.args)
            state.record_tool_call(action.tool, action.args, _summarize_tool_result(result), result)
            self._emit("tool_result", {"tool": action.tool, "args": action.args,
                                        "summary": _summarize_tool_result(result)})
            messages.append({"role": "user", "content": f"Tool result for {action.tool}:\n{json.dumps(result)}"})

        self._finalize_unresolved(state, property_ids, "max_steps_exhausted")
        self._emit("cluster_finished", {"reason": "max_steps_exhausted"})
        return state

    def _emit(self, event_type: str, payload: dict) -> None:
        if self.event_sink is not None:
            self.event_sink(event_type, payload)

    @staticmethod
    def _apply_conclusion(state: ClusterInvestigationState, property_ids: list[str],
                           conclude: ConcludeAction) -> None:
        SecurityAgentKernel._apply_conclusion_material(state, conclude)
        seen: set[str] = set()
        for entry in conclude.properties:
            if entry.property_id not in state.requirement_states:
                continue  # a hallucinated property_id -- ignored, not crashed on
            seen.add(entry.property_id)
            state.record_verdict(
                entry.property_id,
                claim=entry.claim,
                evidence_ids=entry.evidence_ids,
                hypothesis_ids=entry.hypothesis_ids,
                interpretation=entry.interpretation,
                verdict=RequirementResolution(entry.verdict),
            )
        missing = set(property_ids) - seen
        if missing:
            SecurityAgentKernel._finalize_unresolved(
                state, sorted(missing), "conclude_response_missing_this_property_id")

    @staticmethod
    def _apply_conclusion_material(state: ClusterInvestigationState,
                                   conclude: ConcludeAction) -> None:
        for item in conclude.evidence:
            state.upsert_evidence(Evidence.model_validate(item.model_dump()))
        for item in conclude.hypotheses:
            state.upsert_hypothesis(Hypothesis.model_validate(item.model_dump()))

    @staticmethod
    def _apply_investigation_update(state: ClusterInvestigationState,
                                    update: UpdateInvestigationAction) -> str | None:
        property_ids = set(state.property_ids)
        mentioned_properties = {pid for h in update.hypotheses for pid in h.originating_property_ids}
        mentioned_properties |= {a.property_id for a in update.counterexample_attempts}
        unknown_properties = sorted(mentioned_properties - property_ids)
        if unknown_properties:
            return f"unknown property ids: {unknown_properties}"
        known_hypotheses = set(state.hypotheses) | {h.id for h in update.hypotheses}
        unknown_hypotheses = sorted({a.hypothesis_id for a in update.counterexample_attempts}
                                    - known_hypotheses)
        if unknown_hypotheses:
            return f"unknown hypothesis ids: {unknown_hypotheses}"
        for item in update.hypotheses:
            state.upsert_hypothesis(Hypothesis.model_validate(item.model_dump()))
        for attempt in update.counterexample_attempts:
            state.record_counterexample_attempt(
                attempt.property_id, attempt.hypothesis_id, attempt.attempt, attempt.result)
        return None

    @staticmethod
    def _finalize_unresolved(state: ClusterInvestigationState, property_ids: list[str], reason: str) -> None:
        for pid in property_ids:
            state.mark_unresolved_reason(pid, reason)

    @staticmethod
    def _record_token_usage(state: ClusterInvestigationState, chat_result) -> None:
        if chat_result is None:  # test doubles that don't model token accounting
            return
        state.token_usage.input_tokens += chat_result.prompt_tokens
        state.token_usage.output_tokens += chat_result.completion_tokens
        if chat_result.cached:
            state.token_usage.cached_input_tokens += chat_result.prompt_tokens
        if chat_result.cost_usd:
            state.token_usage.cost_usd += chat_result.cost_usd
