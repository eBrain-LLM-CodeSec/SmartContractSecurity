"""The security-agent kernel's decide/execute/update control loop (brief
Phase 2). Deliberately small -- understandable by reading this file plus
state.py/tools.py/model_client.py/prompts.py in one sitting.

Increment 5 applies a mechanical completion gate to proposed conclusions.
Premature PASS verdicts are rejected back into the same loop with concrete
blocking reasons; FAIL remains CEIV/evidence-gated without PASS-only rules.
"""
from __future__ import annotations

import json
import time
from typing import Callable, Literal

from pydantic import BaseModel, Field, model_validator

from rtf.security_agent import context_manager
from rtf.security_agent.completion import check_property_completion, cluster_can_conclude
from rtf.security_agent.evidence_store import EvidenceStore
from rtf.security_agent.model_client import MalformedModelResponse, ModelClient
from rtf.security_agent.prompts import build_initial_user_message, build_system_prompt
from rtf.security_agent.state import (
    ClusterInvestigationState, Evidence, Hypothesis, HypothesisStatus,
    RequirementResolution,
)
from rtf.security_agent.tools import SecurityAgentTools

DEFAULT_MAX_STEPS = 15
DEFAULT_MAX_MALFORMED_RETRIES = 2
DEFAULT_MAX_CONSECUTIVE_NO_PROGRESS = 6


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
    verdict: Literal["PASS", "FAIL", "NOT_APPLICABLE", "INCONCLUSIVE"]


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
                 event_sink: Callable[[str, dict], None] | None = None,
                 evidence_store: EvidenceStore | None = None,
                 max_wall_clock_s: float | None = None,
                 max_cost_usd: float | None = None,
                 max_consecutive_no_progress: int = DEFAULT_MAX_CONSECUTIVE_NO_PROGRESS):
        self.tools = tools
        self.model_client = model_client
        self.max_steps = max_steps
        self.max_malformed_retries = max_malformed_retries
        self.enforce_completion = enforce_completion
        self.event_sink = event_sink
        self.evidence_store = evidence_store
        """Optional (RTF_SECURITY_AGENT_CONTEXT_MANAGEMENT_DESIGN.md
        section 4): when set, raw tool results are externalized to disk
        and replaced in the conversation with a compact summary plus an
        evidence_id the model can retrieve in full via `read_evidence`.
        When None, tool results are inlined verbatim (the pre-redesign
        behavior) -- kept so existing callers/tests that construct a
        kernel without a store see no behavior change."""
        self.max_wall_clock_s = max_wall_clock_s
        self.max_cost_usd = max_cost_usd
        """Circuit breakers (design section 7). None disables a given
        breaker -- deliberately opt-in so existing tests/callers that
        don't pass these keep the prior unbounded-within-max_steps
        behavior; a live run wires real budgets explicitly."""
        self.max_consecutive_no_progress = max_consecutive_no_progress

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
        cluster_context = context_manager.ClusterContext(
            property_ids=property_ids, protocol_context_md=protocol_context_md,
            requirement_context_by_property=requirement_context_by_property,
            cluster_plan_md=cluster_plan_md,
        )
        header: list[dict] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_initial_user_message(
                property_ids, protocol_context_md, requirement_context_by_property, cluster_plan_md)},
        ]
        messages: list[dict] = list(header)
        # Everything appended since cluster start -- the window
        # `context_manager.build_context` compacts its "recent turns"
        # tail from. Bounded in practice by max_steps (small), so kept
        # in full rather than trimmed for its own sake.
        recent_turns: list[dict] = []

        def _append_turn(entry: dict) -> None:
            messages.append(entry)
            recent_turns.append(entry)

        started_at = time.monotonic()
        action_error_retries = 0
        no_progress_streak = 0
        no_progress_events = 0
        last_fingerprint = state.progress_fingerprint()
        compaction_count = 0
        # Cumulative across the WHOLE cluster (not per-call, unlike
        # `_decide_with_bounded_retries`'s own local `retries`) -- one of
        # Part 10's requested per-cluster metrics.
        malformed_total = 0

        def _finish(reason: str, *, forced_conclusion: bool = False) -> None:
            self._emit("cluster_finished", {
                "reason": reason,
                "forced_conclusion": forced_conclusion,
                "verdicts": {pid: rs.status.value for pid, rs in state.requirement_states.items()},
                "step_count": state.step_count,
                "wall_clock_s": time.monotonic() - started_at,
                "token_usage": state.token_usage.model_dump(),
                "malformed_responses_total": malformed_total,
                "action_application_errors_total": action_error_retries,
                "no_progress_events_total": no_progress_events,
                "compaction_count": compaction_count,
                "tool_calls_total": len(state.tool_history),
            })

        while state.step_count < self.max_steps:
            breaker_reason = self._tripped_circuit_breaker(state, started_at)
            if breaker_reason is not None:
                state = self._attempt_forced_conclusion(
                    state, messages, property_ids, reasoning_categories_by_property, breaker_reason)
                _finish(breaker_reason, forced_conclusion=True)
                return state

            retries_counter = [0]
            try:
                turn = self._decide_with_bounded_retries(messages, retries_counter)
            except MalformedModelResponse:
                # Real gap found live (2026-08-25 canto run, cluster_002):
                # a run of malformed JSON-shape mistakes (e.g. the model
                # naming a tool directly as the top-level "action") used
                # to go straight to bare UNRESOLVED with no salvage
                # attempt, discarding whatever real investigation had
                # already happened. A forced-conclusion prompt is a
                # materially SIMPLER, more constrained ask than the
                # general decide loop it just failed at, so it is often
                # answerable even when the general loop wasn't -- same
                # salvage discipline as every budget-exhaustion path.
                malformed_total += retries_counter[0]
                state = self._attempt_forced_conclusion(
                    state, messages, property_ids, reasoning_categories_by_property,
                    "kernel_malformed_response_exhausted")
                _finish("kernel_malformed_response_exhausted", forced_conclusion=True)
                return state
            malformed_total += retries_counter[0]

            self._record_token_usage(state, turn.chat_result)
            self._emit("model_action", {"action": turn.raw,
                                         "token_usage": state.token_usage.model_dump()})
            _append_turn({"role": "assistant", "content": json.dumps(turn.raw)})

            # Defense in depth (2026-08-17 live run): everything below
            # applies an already-schema-validated action to state, but
            # "validated by Pydantic" only means internally consistent,
            # not consistent with everything the kernel already knows
            # (see _apply_investigation_update's own up-front evidence-id
            # check above for the specific bug this generalizes past).
            # ANY unexpected exception here previously propagated all the
            # way to live_runner.py's generic catch-all, discarding the
            # cluster's entire accumulated tool history/evidence/
            # hypotheses. Treated with the SAME bounded retry-then-give-up
            # discipline as a malformed response instead, so an unknown
            # bug degrades to one wasted turn, not a lost cluster.
            try:
                if isinstance(turn.parsed, ConcludeAction):
                    proposed = state.model_copy(deep=True)
                    self._apply_conclusion(proposed, property_ids, turn.parsed)
                    completion = cluster_can_conclude(proposed, reasoning_categories_by_property)
                    if self.enforce_completion and not completion.ready:
                        self._apply_conclusion_material(state, turn.parsed)
                        state.step_count += 1
                        _append_turn({"role": "user", "content":
                            "Conclusion rejected by the mechanical completion gate: "
                            + "; ".join(completion.blocking_reasons)
                            + ". Continue investigating and update structured state before concluding again."})
                        self._emit("conclusion_rejected", {"blocking_reasons": completion.blocking_reasons})
                    else:
                        state = proposed
                        _finish("concluded")
                        return state

                elif isinstance(turn.parsed, UpdateInvestigationAction):
                    error = self._apply_investigation_update(state, turn.parsed)
                    state.step_count += 1
                    _append_turn({"role": "user", "content":
                        f"Investigation-state update {'rejected: ' + error if error else 'recorded.'}"})
                    self._emit("investigation_updated", {"rejected_reason": error,
                                                          "hypothesis_ids": [h.id for h in turn.parsed.hypotheses],
                                                          "counterexample_attempts": len(turn.parsed.counterexample_attempts)})

                else:
                    action: ToolCallAction = turn.parsed
                    result = self.tools.call(action.tool, action.args)
                    tool_record = state.record_tool_call(action.tool, action.args,
                                                          _summarize_tool_result(result), result)
                    self._emit("tool_result", {"tool": action.tool, "args": action.args,
                                                "summary": _summarize_tool_result(result)})
                    _append_turn({"role": "user", "content":
                        self._render_tool_result(tool_record.id, action.tool, result)})
            except Exception as e:  # noqa: BLE001 -- see comment above: an unknown bug must not crash the cluster
                self._emit("action_application_error", {"error": f"{type(e).__name__}: {e}"})
                action_error_retries += 1
                if action_error_retries > self.max_malformed_retries:
                    # Same salvage discipline as the malformed-response and
                    # budget-exhaustion paths above: an internal error
                    # applying a PREVIOUS action says nothing about whether
                    # a forced-conclusion prompt (a fresh, unrelated
                    # decide() call) can succeed -- most of the time it can.
                    reason = f"kernel_action_application_error:{type(e).__name__}"
                    state = self._attempt_forced_conclusion(
                        state, messages, property_ids, reasoning_categories_by_property, reason)
                    _finish(reason, forced_conclusion=True)
                    return state
                state.step_count += 1
                _append_turn({"role": "user", "content":
                    f"An internal error occurred while applying your last action "
                    f"({type(e).__name__}: {e}). Try again -- only reference evidence/hypothesis "
                    "ids that were already established in a prior turn."})

            previous_streak = no_progress_streak
            no_progress_streak, last_fingerprint = self._update_progress(state, last_fingerprint, no_progress_streak)
            if no_progress_streak > previous_streak:
                no_progress_events += 1
                self._emit("no_progress", {"streak": no_progress_streak})
            if no_progress_streak >= self.max_consecutive_no_progress:
                state = self._attempt_forced_conclusion(
                    state, messages, property_ids, reasoning_categories_by_property, "no_progress_exhausted")
                _finish("no_progress_exhausted", forced_conclusion=True)
                return state

            if context_manager.should_compact(messages):
                messages = context_manager.build_context(state, cluster_context, recent_turns)
                compaction_count += 1
                self._emit("context_compacted", {"compaction_count": compaction_count,
                                                   "estimated_tokens": context_manager.estimate_messages_tokens(messages)})

        # Real gap found live (2026-08-25 canto run): plain max_steps
        # exhaustion -- by far the most common way a cluster naturally
        # runs out of budget, far more often than the wall-clock/cost
        # breakers below trip on cheap fast calls -- used to go straight
        # to bare _finalize_unresolved with no forced-conclusion attempt
        # at all, discarding a full budget's worth of real investigation
        # (evidence gathered, files read) as zero-coverage UNRESOLVED
        # instead of salvaging an honest INCONCLUSIVE. Matches the same
        # forced-conclusion salvage every other circuit breaker above
        # already gets (design section 7's own stated intent -- "preserve
        # partial coverage rather than zero-coverage failures").
        state = self._attempt_forced_conclusion(
            state, messages, property_ids, reasoning_categories_by_property, "max_steps_exhausted")
        _finish("max_steps_exhausted", forced_conclusion=True)
        return state

    def _decide_with_bounded_retries(self, messages: list[dict], retries_counter: list[int]):
        """One decide() call, retried on a malformed response WITHOUT
        growing `messages` (design section 6): each retry attempt
        branches fresh from the SAME last-valid `messages` passed in,
        never from the previous malformed attempt, so a run of malformed
        responses costs extra model calls but never permanently inflates
        the conversation the way the pre-redesign kernel did.

        `retries_counter[0]` is incremented on every malformed attempt
        (Part 10 instrumentation) -- a single-element list, not a return
        value, so the caller can still read how many retries happened
        even when the final attempt also fails and this raises."""
        attempt = messages
        while True:
            try:
                return self.model_client.decide(attempt)
            except MalformedModelResponse as e:
                self._emit("malformed_model_response", {"errors": e.errors, "raw": e.raw})
                retries_counter[0] += 1
                if retries_counter[0] > self.max_malformed_retries:
                    raise
                attempt = messages + [{"role": "user", "content":
                    f"Your last response did not match the required JSON shape ({e.errors}). "
                    "Respond again with exactly one fenced JSON block matching call_tool, "
                    "update_investigation, or conclude."}]

    def _render_tool_result(self, tool_call_id: str, tool: str, result: dict) -> str:
        """`read_evidence` is itself an on-demand full-detail fetch --
        shown in full, nothing left to compact. Every other tool result
        is externalized via `self.evidence_store` (when configured) so
        the conversation carries only a compact summary plus the
        evidence_id needed to retrieve the rest."""
        if tool == "read_evidence" or self.evidence_store is None:
            return f"Tool result for {tool}:\n{json.dumps(result)}"
        stored = self.evidence_store.store(tool_call_id, tool, result)
        return (f"Tool result for {tool} (evidence_id={stored.evidence_id}):\n{stored.summary}\n"
                f"Use read_evidence(\"{stored.evidence_id}\") to see the complete raw result if needed.")

    def _tripped_circuit_breaker(self, state: ClusterInvestigationState, started_at: float) -> str | None:
        if self.max_wall_clock_s is not None and time.monotonic() - started_at >= self.max_wall_clock_s:
            return "max_wall_clock_exceeded"
        if self.max_cost_usd is not None and state.token_usage.cost_usd >= self.max_cost_usd:
            return "max_cost_exceeded"
        return None

    @staticmethod
    def _update_progress(state: ClusterInvestigationState, last_fingerprint: tuple, streak: int) -> tuple[int, tuple]:
        """Deterministic stall detection (design section 8): a repeated
        fingerprint means no evidence, hypothesis, requirement status,
        question, next-action, or newly-inspected file/contract/function
        changed between turns -- real stagnation, not just raw turn
        count (which grows even on repeated malformed retries)."""
        fingerprint = state.progress_fingerprint()
        if fingerprint == last_fingerprint:
            return streak + 1, last_fingerprint
        return 0, fingerprint

    def _attempt_forced_conclusion(
        self, state: ClusterInvestigationState, messages: list[dict], property_ids: list[str],
        reasoning_categories_by_property: dict[str, str | None] | None, reason: str,
    ) -> ClusterInvestigationState:
        """Circuit-breaker last resort (design section 7): one final
        "wrap up with what you have" turn, so a budget exhaustion
        salvages honest partial coverage (PASS/FAIL/INCONCLUSIVE, each
        still evidence-gated) instead of silently discarding the whole
        cluster as bare UNRESOLVED. No single pathological cluster
        monopolizes its slot beyond this one extra call."""
        self._emit("circuit_breaker_tripped", {"reason": reason})
        forced_prompt = messages + [{"role": "user", "content":
            f"You have reached an investigation budget limit ({reason}). This is your "
            "final turn. Respond with exactly one `conclude` action covering EVERY "
            "property in this cluster, using everything already established. For any "
            "property you cannot support with real cited evidence, use INCONCLUSIVE "
            "rather than guessing PASS or FAIL."}]
        try:
            turn = self.model_client.decide(forced_prompt)
        except MalformedModelResponse:
            self._finalize_inconclusive(state, property_ids, f"forced_conclusion_failed:{reason}")
            return state
        self._record_token_usage(state, turn.chat_result)
        if not isinstance(turn.parsed, ConcludeAction):
            self._finalize_inconclusive(state, property_ids, f"forced_conclusion_not_conclude:{reason}")
            return state
        try:
            self._apply_forced_conclusion(state, property_ids, turn.parsed, reasoning_categories_by_property)
        except Exception as e:  # noqa: BLE001 -- last resort; a bad forced response must not crash the cluster
            self._finalize_inconclusive(state, property_ids, f"forced_conclusion_apply_error:{type(e).__name__}:{reason}")
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
    def _apply_forced_conclusion(
        state: ClusterInvestigationState, property_ids: list[str], conclude: ConcludeAction,
        reasoning_categories_by_property: dict[str, str | None] | None,
    ) -> None:
        """The forced-conclusion counterpart to `_apply_conclusion`.
        Unlike the normal path, this is never rejected wholesale by the
        completion gate -- there is no budget left to keep iterating --
        but PASS discipline is still enforced per property: any PASS
        that would fail `check_property_completion` is downgraded to
        INCONCLUSIVE with the blocking reasons recorded as its reason,
        never silently accepted (constraint: do not weaken PASS evidence
        requirements merely to raise resolution). FAIL/NOT_APPLICABLE/
        INCONCLUSIVE entries are accepted as given -- only PASS carries
        the extra falsification-attempt burden."""
        SecurityAgentKernel._apply_conclusion_material(state, conclude)
        categories = reasoning_categories_by_property or {}
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
            if entry.verdict == "PASS":
                check = check_property_completion(state, entry.property_id, categories.get(entry.property_id))
                if not check.ready:
                    state.resolve_requirement(
                        entry.property_id, RequirementResolution.INCONCLUSIVE,
                        reason="forced_conclusion_pass_rejected:" + ";".join(check.blocking_reasons))
        missing = set(property_ids) - seen
        if missing:
            SecurityAgentKernel._finalize_inconclusive(
                state, sorted(missing), "forced_conclusion_missing_property_id")

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
        # Real crash fixed here (2026-08-17 live run,
        # cluster_invocation_crashed:UnknownEvidenceIdError, 42 properties
        # across the run): a hypothesis's supporting/contradicting
        # evidence ids were never checked against state.evidence before
        # upsert_hypothesis -> add_hypothesis's own _require_evidence
        # call raised uncaught. The prompt actively encourages recording
        # hypotheses via update_investigation BEFORE a conclude action
        # has declared evidence, so this fired often, not as an edge
        # case. Validated up front, like the two checks above, so nothing
        # is mutated before we know the whole update is applicable.
        referenced_evidence = {eid for h in update.hypotheses
                               for eid in (*h.supporting_evidence_ids, *h.contradicting_evidence_ids)}
        unknown_evidence = sorted(referenced_evidence - set(state.evidence))
        if unknown_evidence:
            return (f"unknown evidence ids in hypotheses: {unknown_evidence} -- evidence must be "
                    "declared via a conclude action's own evidence list before a hypothesis can cite it")
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
    def _finalize_inconclusive(state: ClusterInvestigationState, property_ids: list[str], reason: str) -> None:
        """Distinct from `_finalize_unresolved`: used when a real
        finalization attempt was made (a circuit breaker forced a
        conclude turn) and either failed or omitted some properties --
        an honest INCONCLUSIVE, not a bookkeeping UNRESOLVED note.
        Never overwrites a property that already reached a real
        PASS/FAIL/NOT_APPLICABLE/INCONCLUSIVE verdict."""
        for pid in property_ids:
            req_state = state.requirement_states[pid]
            if req_state.status == RequirementResolution.UNRESOLVED:
                state.resolve_requirement(pid, RequirementResolution.INCONCLUSIVE, reason=reason)

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
