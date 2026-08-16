"""The security-agent kernel's decide/execute/update control loop (brief
Phase 2). Deliberately small -- understandable by reading this file plus
state.py/tools.py/model_client.py/prompts.py in one sitting.

Increment 3 adds a structured final-answer boundary: a conclusion carries
one cluster-wide evidence pool and a separate Claim / Evidence ids /
Interpretation / Verdict chain for every property. No hypotheses,
counterexamples, or PASS-discipline gate yet (Increments 4-5).
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from rtf.security_agent.model_client import MalformedModelResponse, ModelClient
from rtf.security_agent.prompts import build_initial_user_message, build_system_prompt
from rtf.security_agent.state import ClusterInvestigationState, Evidence, RequirementResolution
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


class ConcludeAction(BaseModel):
    action: Literal["conclude"]
    evidence: list[EvidenceInput] = Field(min_length=1)
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
        return self


RESPONSE_MODELS: tuple[type[BaseModel], ...] = (ToolCallAction, ConcludeAction)


def _summarize_tool_result(result: dict) -> str:
    status = result.get("status", "?")
    if status != "OK":
        return f"{status}: {result.get('reason', '')}"
    payload_keys = [k for k in result if k not in ("status", "reason")]
    return f"OK ({', '.join(payload_keys)})"


class SecurityAgentKernel:
    def __init__(self, tools: SecurityAgentTools, model_client: ModelClient,
                 max_steps: int = DEFAULT_MAX_STEPS,
                 max_malformed_retries: int = DEFAULT_MAX_MALFORMED_RETRIES):
        self.tools = tools
        self.model_client = model_client
        self.max_steps = max_steps
        self.max_malformed_retries = max_malformed_retries

    def run_cluster(
        self, cluster_id: str, property_ids: list[str],
        protocol_context_md: str, requirement_context_by_property: dict[str, str],
        cluster_plan_md: str,
        parent_requirement_ids: dict[str, str | None] | None = None,
    ) -> ClusterInvestigationState:
        """One shared ClusterInvestigationState for the WHOLE cluster --
        never one state object per property_id, matching the brief's
        "one cluster does NOT create independent agent sessions"
        invariant (see state.test_one_cluster_multiple_requirements_is_
        one_shared_state_object for the state-layer version of this same
        check)."""
        state = ClusterInvestigationState.initial(cluster_id, property_ids, parent_requirement_ids)
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
                malformed_retries += 1
                if malformed_retries > self.max_malformed_retries:
                    self._finalize_unresolved(state, property_ids, "kernel_malformed_response_exhausted")
                    return state
                messages.append({"role": "assistant", "content": json.dumps(e.raw)})
                messages.append({"role": "user", "content":
                    f"Your last response did not match the required JSON shape ({e.errors}). "
                    "Respond again with exactly one fenced JSON block matching call_tool or conclude."})
                continue

            self._record_token_usage(state, turn.chat_result)
            messages.append({"role": "assistant", "content": json.dumps(turn.raw)})

            if isinstance(turn.parsed, ConcludeAction):
                self._apply_conclusion(state, property_ids, turn.parsed)
                return state

            action: ToolCallAction = turn.parsed
            result = self.tools.call(action.tool, action.args)
            state.record_tool_call(action.tool, action.args, _summarize_tool_result(result), result)
            messages.append({"role": "user", "content": f"Tool result for {action.tool}:\n{json.dumps(result)}"})

        self._finalize_unresolved(state, property_ids, "max_steps_exhausted")
        return state

    @staticmethod
    def _apply_conclusion(state: ClusterInvestigationState, property_ids: list[str],
                           conclude: ConcludeAction) -> None:
        for item in conclude.evidence:
            state.add_evidence(Evidence.model_validate(item.model_dump()))
        seen: set[str] = set()
        for entry in conclude.properties:
            if entry.property_id not in state.requirement_states:
                continue  # a hallucinated property_id -- ignored, not crashed on
            seen.add(entry.property_id)
            state.record_verdict(
                entry.property_id,
                claim=entry.claim,
                evidence_ids=entry.evidence_ids,
                interpretation=entry.interpretation,
                verdict=RequirementResolution(entry.verdict),
            )
        missing = set(property_ids) - seen
        if missing:
            SecurityAgentKernel._finalize_unresolved(
                state, sorted(missing), "conclude_response_missing_this_property_id")

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
