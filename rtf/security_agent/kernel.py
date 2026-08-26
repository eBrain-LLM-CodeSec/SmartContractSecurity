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

from pydantic import BaseModel, Field, ValidationError, model_validator

from rtf.security_agent import context_manager
from rtf.security_agent.completion import check_property_completion, cluster_can_conclude
from rtf.security_agent.evidence_store import EvidenceStore, UnknownEvidenceRefError
from rtf.security_agent.model_client import MalformedModelResponse, ModelClient
from rtf.security_agent.prompts import build_initial_user_message, build_system_prompt
from rtf.security_agent.state import (
    ClusterInvestigationState, Evidence, Hypothesis, HypothesisStatus,
    RequirementResolution, ToolCallRecord,
)
from rtf.security_agent.tools import SecurityAgentTools

DEFAULT_MAX_STEPS = 15
DEFAULT_MAX_MALFORMED_RETRIES = 2
DEFAULT_MAX_CONSECUTIVE_NO_PROGRESS = 6
DEFAULT_FORCED_CONCLUSION_MAX_TOKENS = 32000
"""Real incident #3 (2026-08-25, canto run): the steady-state completion
cap (model_client.DEFAULT_MAX_COMPLETION_TOKENS, 16000) truncated a
forced-conclusion turn's genuinely correct, detailed 8-property conclude
action mid-JSON-string, discarding real analysis as generic INCONCLUSIVE
purely because the response never finished, not because it was wrong.
Doubled specifically for this ONE rare, high-value call per cluster (at
most) -- not for every routine tool-call turn, so the cost impact is
bounded -- staying comfortably under the ~65,536-token pathological
ceiling documented in model_client.py's own incident #1."""

DEFAULT_REASONING_BUDGET_RETRY_MAX_TOKENS = 32000
"""Real gap found via trajectory analysis (RTF_SECURITY_AGENT_NATURAL_
CONCLUSION_INVESTIGATION_20260826.md): `_decide_with_bounded_retries`
retried a malformed response with the exact SAME max_tokens regardless of
WHY it failed -- a generic wrong-JSON-shape mistake and GLM-5.2 genuinely
exhausting its whole reasoning budget without emitting content
(model_client.py's own incident #2) got identical treatment, even though
the latter's actual fix is more headroom, not a corrective nudge. Live
evidence: clusters 002/003/007 each hit exactly this failure 3 times in a
row at unremarkable (~17K token) context sizes -- not a context-bloat
trigger, a budget one. A distinct constant from
DEFAULT_FORCED_CONCLUSION_MAX_TOKENS (same value today, but a different
knob semantically -- a mid-loop retry, not the one-per-cluster final
salvage turn) so the two can be tuned independently later."""


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
    """Record hypotheses and/or a resolved counterexample attempt before concluding. A PASS verdict is mechanically REJECTED unless the property has a resolved counterexample attempt on file -- via this tool, or inline on conclude's own counterexample_attempts field. This is enforced automatically, not a suggestion."""

    action: Literal["update_investigation"]
    hypotheses: list[HypothesisInput] = Field(default_factory=list)
    counterexample_attempts: list[CounterexampleAttemptInput] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    """Real gap found live (2026-08-26): `state.unresolved_questions`/
    `state.next_actions` (and `state.set_next_actions`) already existed
    and were already rendered in the compacted state summary, but
    NOTHING in this action schema let the model ever write to them --
    both were always empty in every real run. Both are optional
    (replacement, not append, matching `set_next_actions`'s existing
    semantics) -- an update that omits them leaves whatever was recorded
    in an earlier turn untouched; see `_apply_investigation_update`."""

    @model_validator(mode="after")
    def contains_an_update(self) -> "UpdateInvestigationAction":
        if not (self.hypotheses or self.counterexample_attempts
                or self.unresolved_questions or self.next_actions):
            raise ValueError("update_investigation must include a hypothesis, counterexample "
                             "attempt, unresolved question, or next action")
        return self


class ConcludeAction(BaseModel):
    """Conclude the investigation for every property in this cluster at once. PASS requires an actual falsification attempt on file for that property -- either a prior update_investigation call, or an inline counterexample_attempts entry on this same call. A PASS without one is mechanically rejected, not just discouraged."""

    action: Literal["conclude"]
    evidence: list[EvidenceInput] = Field(min_length=1)
    hypotheses: list[HypothesisInput] = Field(min_length=1)
    properties: list[PropertyVerdictInput]
    counterexample_attempts: list[CounterexampleAttemptInput] = Field(default_factory=list)
    """Inline fallback for the same falsification-attempt record
    `update_investigation` normally carries (root cause #1 fix,
    natural-conclusion investigation 20260826): real trajectories showed
    the model almost never called `update_investigation` before its
    first `conclude`, so a PASS could never satisfy completion.py's
    counterexample gate in one shot even when the model DID do the
    adversarial check in its own reasoning. Lets a single `conclude`
    call record it directly instead of requiring a separate prior turn.
    Applied via the same `state.record_counterexample_attempt` state
    method `_apply_investigation_update` already uses -- completion.py
    needs no changes, since its gate already reads
    `req.counterexample_attempts` mechanism-agnostically."""

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
        property_ids = {prop.property_id for prop in self.properties}
        unknown_ce_properties = sorted({a.property_id for a in self.counterexample_attempts
                                        if a.property_id not in property_ids})
        if unknown_ce_properties:
            raise ValueError(f"counterexample_attempts reference unknown property ids: {unknown_ce_properties}")
        unknown_ce_hypotheses = sorted({a.hypothesis_id for a in self.counterexample_attempts
                                        if a.hypothesis_id not in hypothesis_ids})
        if unknown_ce_hypotheses:
            raise ValueError(f"counterexample_attempts reference unknown hypothesis ids: {unknown_ce_hypotheses}")
        return self


RESPONSE_MODELS: tuple[type[BaseModel], ...] = (
    ToolCallAction, UpdateInvestigationAction, ConcludeAction,
)
"""Kept fully intact, unmodified, for the legacy (non-native) JSON-text
path -- confirmed required as-is by `test_model_client.py` (exercises
`ModelClient` directly against a plain `a4v.llm.ChatResult` via a
`FakeChatClient`, asserting `ToolCallAction` still parses) and by
`test_response_schema.py`/`test_kernel_mocked.py`/`test_fixture_matrix.py`.
Do not narrow or delete this."""

NATIVE_RESPONSE_MODELS: tuple[type[BaseModel], ...] = (
    UpdateInvestigationAction, ConcludeAction,
)
"""The 2 JSON-text action shapes still expected once native tool-calling
is active -- `ToolCallAction` is deliberately excluded: a tool call is
now a native `tools=[...]` request (`ModelTurn.tool_calls`), not a
JSON-text shape. Used (instead of `RESPONSE_MODELS`) for both the
`response_schema.py` schema build and the `ModelClient` construction at
`investigator.py`'s live-run call site -- this makes a stray
`call_tool`-shaped text reply correctly surface as malformed once
native tools are the intended path, the right diagnostic (the model
didn't honor native tool-calling), rather than being silently accepted
via the old text path."""


def _summarize_tool_result(result: dict) -> str:
    status = result.get("status", "?")
    if status != "OK":
        return f"{status}: {result.get('reason', '')}"
    payload_keys = [k for k in result if k not in ("status", "reason")]
    return f"OK ({', '.join(payload_keys)})"


def _render_dedup_replay(tool: str, duplicate: ToolCallRecord, evidence_store: EvidenceStore | None) -> str:
    """Kernel-controlled cached-result replay (found live, 2026-08-26):
    an exact-duplicate call gets the ORIGINAL full result back
    automatically -- not a pointer telling the model to fetch it itself.
    The model asking again is direct evidence it no longer has the
    information; a pointer would just reintroduce a dependency on the
    model noticing and acting on a hint, the same failure mode this fix
    exists to remove. Reuses the same "full detail, nothing held back"
    shape `_render_tool_result` already uses for a real `read_evidence`
    call -- this kernel already has exactly one no-compaction rendering
    convention, reused here rather than inventing a second one."""
    if evidence_store is not None:
        try:
            raw_result = json.loads(evidence_store.read(duplicate.id))
            return (f"Tool result for {tool} (CACHED -- deduplicated, no new tool "
                    f"execution, replaying original evidence_id={duplicate.id}):\n"
                    f"{json.dumps(raw_result)}")
        except UnknownEvidenceRefError:
            pass  # original was never persisted (shouldn't happen for a
                  # non-read_evidence duplicate when evidence_store is
                  # configured -- store() is unconditional -- kept as a
                  # defensive fallback, not expected to trigger in practice)
    return (f"Tool result for {tool} (CACHED -- deduplicated, no new tool execution; "
            f"only a short summary is available, no evidence store configured for "
            f"this investigation):\n{duplicate.result_summary}")


class SecurityAgentKernel:
    def __init__(self, tools: SecurityAgentTools, model_client: ModelClient,
                 max_steps: int = DEFAULT_MAX_STEPS,
                 max_malformed_retries: int = DEFAULT_MAX_MALFORMED_RETRIES,
                 enforce_completion: bool = True,
                 event_sink: Callable[[str, dict], None] | None = None,
                 evidence_store: EvidenceStore | None = None,
                 max_wall_clock_s: float | None = None,
                 max_cost_usd: float | None = None,
                 max_consecutive_no_progress: int = DEFAULT_MAX_CONSECUTIVE_NO_PROGRESS,
                 forced_conclusion_max_tokens: int = DEFAULT_FORCED_CONCLUSION_MAX_TOKENS,
                 reasoning_budget_retry_max_tokens: int = DEFAULT_REASONING_BUDGET_RETRY_MAX_TOKENS):
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
        self.forced_conclusion_max_tokens = forced_conclusion_max_tokens
        self.reasoning_budget_retry_max_tokens = reasoning_budget_retry_max_tokens

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
        #
        # A list of GROUPS, one per logical turn (native-tool-calling
        # migration, 2026-08-26), not a flat list of message dicts: a
        # plain turn is a 1-entry group; a native multi-tool-call turn is
        # ONE group holding its assistant tool_calls request entry plus
        # every one of that turn's tool-result entries together. This
        # keeps a turn atomic under `context_manager.build_context`'s
        # trimming -- splitting a multi-call turn's request from its own
        # results across a trim boundary would produce a
        # `function_call_output` with no matching `function_call`, an
        # invalid next request (Part 0, live-verified).
        recent_turns: list[list[dict]] = []

        def _append_group(entries: list[dict]) -> None:
            messages.extend(entries)
            recent_turns.append(entries)

        def _append_turn(entry: dict) -> None:
            _append_group([entry])

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
                "decide_calls_total": state.decide_calls_total,
                "deduplicated_calls_total": state.deduplicated_calls_total,
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
                # One real model round-trip (Part 8 instrumentation,
                # native-tool-calling migration): counted once per
                # SUCCESSFUL decide() call here, regardless of how many
                # tool calls that turn resolved -- distinct from
                # `state.step_count`, which no longer implies a 1:1 turn
                # count once a single decide() call can resolve several
                # tool calls at once. This is what makes the actual
                # efficiency claim ("same investigation depth, fewer
                # round-trips") directly measurable.
                state.decide_calls_total += 1
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
            # A native tool-calling turn's own assistant request entry is
            # constructed (with real call_ids) inside the `turn.tool_calls`
            # dispatch branch below, grouped atomically with its results --
            # nothing to append here for that case. Every other turn shape
            # still gets its raw JSON echoed as a single-entry group,
            # unchanged from before this migration.
            if turn.parsed is not None:
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
                if turn.tool_calls:
                    # Native multi-tool-call turn (Part 0, live-verified):
                    # the model can request several independent tool calls
                    # in one response instead of exactly one. All are
                    # executed; the assistant's own request entry plus
                    # every result entry are appended as ONE atomic group
                    # (see `_append_group`'s docstring above) so a later
                    # compaction trim can never split a `function_call`
                    # from its own `function_call_output`.
                    #
                    # `record_tool_call` increments `state.step_count`
                    # once per call, same as the legacy single-call path
                    # below -- N calls this turn advances the same
                    # investigation-depth counter N times, preserving
                    # `max_steps`'s existing meaning. A turn can therefore
                    # overshoot `max_steps` by up to one turn's worth of
                    # calls; deliberately not truncated mid-turn -- a
                    # truncated turn would leave some of the model's own
                    # `function_call` items without a matching
                    # `function_call_output`, an invalid next request.
                    entries = [{"role": "assistant", "tool_calls": [
                        {"call_id": call.call_id, "tool": call.tool, "args": call.args}
                        for call in turn.tool_calls
                    ]}]
                    for call in turn.tool_calls:
                        # `update_investigation`/`conclude` as native
                        # tools (root cause #1 fix, natural-conclusion
                        # investigation 20260826): promoted from
                        # free-text fenced-JSON conventions to real
                        # native tools alongside the 13 read-only ones
                        # (build_action_tool_schemas) -- live-verified
                        # the model reaches for them with the same
                        # tool-calling affordance as any other tool, and
                        # does NOT conclude prematurely just because the
                        # tool is now equally reachable. Dispatched here,
                        # before the generic self.tools.call(...)
                        # fallback below, since neither name is in
                        # SecurityAgentTools.TOOL_NAMES. A validation
                        # failure degrades to a normal tool-result
                        # message (same as _apply_investigation_update's
                        # own error-string convention) rather than
                        # raising -- this is a different failure class
                        # from a malformed top-level response, bounded by
                        # the existing no-progress/stagnation breaker
                        # instead of max_malformed_retries.
                        if call.tool == "update_investigation":
                            try:
                                validated_update = UpdateInvestigationAction.model_validate(
                                    {"action": "update_investigation", **call.args})
                            except ValidationError as e:
                                entries.append({"role": "tool", "call_id": call.call_id, "tool": call.tool,
                                                "content": f"Your update_investigation call did not match "
                                                           f"the required shape: {e}. Try again with valid "
                                                           "arguments."})
                                continue
                            error = self._apply_investigation_update(state, validated_update)
                            state.step_count += 1
                            entries.append({"role": "tool", "call_id": call.call_id, "tool": call.tool,
                                            "content": f"Investigation-state update "
                                                       f"{'rejected: ' + error if error else 'recorded.'}"})
                            self._emit("investigation_updated", {
                                "rejected_reason": error,
                                "hypothesis_ids": [h.id for h in validated_update.hypotheses],
                                "counterexample_attempts": len(validated_update.counterexample_attempts)})
                            continue

                        if call.tool == "conclude":
                            try:
                                validated_conclude = ConcludeAction.model_validate(
                                    {"action": "conclude", **call.args})
                            except ValidationError as e:
                                entries.append({"role": "tool", "call_id": call.call_id, "tool": call.tool,
                                                "content": f"Your conclude call did not match the required "
                                                           f"shape: {e}. Try again with valid arguments."})
                                continue
                            proposed = state.model_copy(deep=True)
                            self._apply_conclusion(proposed, property_ids, validated_conclude)
                            completion = cluster_can_conclude(proposed, reasoning_categories_by_property)
                            if self.enforce_completion and not completion.ready:
                                self._apply_conclusion_material(state, validated_conclude)
                                state.step_count += 1
                                entries.append({"role": "tool", "call_id": call.call_id, "tool": call.tool,
                                                "content": "Conclusion rejected by the mechanical completion "
                                                "gate: " + "; ".join(completion.blocking_reasons)
                                                + ". Continue investigating and update structured state "
                                                "before concluding again."})
                                self._emit("conclusion_rejected", {"blocking_reasons": completion.blocking_reasons})
                                continue
                            # Accepted: the cluster is done. Nothing else
                            # in this turn is processed -- mirrors the
                            # legacy text-mode conclude path's own
                            # precedent of never appending to `messages`
                            # on a successful conclude (nothing reads it
                            # again after return).
                            state = proposed
                            _finish("concluded")
                            return state

                        # Kernel-controlled cached-result replay (found
                        # live, 2026-08-26): an exact-duplicate call (same
                        # tool, same args, already in tool_history) is
                        # replayed from EvidenceStore instead of executed
                        # again -- automatically, with no dependency on
                        # the model noticing a hint. read_evidence,
                        # update_investigation, and conclude are all
                        # excluded: read_evidence is already a cheap disk
                        # read (never persisted to EvidenceStore in the
                        # first place); update_investigation/conclude are
                        # not idempotent reads -- replaying a stale
                        # "recorded"/rejection message instead of really
                        # re-running the completion gate against CURRENT
                        # state would be actively wrong, not just wasteful.
                        duplicate = (None if call.tool in {"read_evidence", "update_investigation", "conclude"}
                                     else state.find_duplicate_tool_call(call.tool, call.args))
                        if duplicate is not None:
                            state.deduplicated_calls_total += 1
                            self._emit("tool_call_deduplicated", {"tool": call.tool, "args": call.args,
                                                                   "original_id": duplicate.id})
                            entries.append({"role": "tool", "call_id": call.call_id, "tool": call.tool,
                                            "content": _render_dedup_replay(call.tool, duplicate, self.evidence_store)})
                            continue
                        result = self.tools.call(call.tool, call.args)
                        tool_record = state.record_tool_call(call.tool, call.args,
                                                              _summarize_tool_result(result), result)
                        self._emit("tool_result", {"tool": call.tool, "args": call.args,
                                                    "summary": _summarize_tool_result(result),
                                                    "native_call_id": call.call_id})
                        entries.append({"role": "tool", "call_id": call.call_id, "tool": call.tool,
                                        "content": self._render_tool_result(tool_record.id, call.tool, result)})
                    _append_group(entries)

                elif isinstance(turn.parsed, ConcludeAction):
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
                    duplicate = (None if action.tool == "read_evidence"
                                 else state.find_duplicate_tool_call(action.tool, action.args))
                    if duplicate is not None:
                        state.deduplicated_calls_total += 1
                        self._emit("tool_call_deduplicated", {"tool": action.tool, "args": action.args,
                                                               "original_id": duplicate.id})
                        _append_turn({"role": "user", "content":
                            _render_dedup_replay(action.tool, duplicate, self.evidence_store)})
                    else:
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
        even when the final attempt also fails and this raises.

        Adaptive retry (natural-conclusion investigation, 20260826): a
        generic wrong-shape mistake and GLM-5.2 genuinely exhausting its
        reasoning budget without emitting content (model_client.py's own
        incident #2 -- the exact marker text it raises with) are
        DIFFERENT failure modes and get different retries. Only the
        latter gets its `max_tokens` bumped to
        `self.reasoning_budget_retry_max_tokens` -- a wrong-shape mistake
        keeps the steady-state cap unchanged, since more tokens does
        nothing to fix a model that simply named the wrong action. Once
        bumped, stays bumped for the rest of THIS bounded-retry loop (a
        later different-cause failure in the same loop doesn't undo it)."""
        attempt = messages
        max_tokens_override: int | None = None
        while True:
            try:
                return self.model_client.decide(attempt, max_tokens=max_tokens_override)
            except MalformedModelResponse as e:
                self._emit("malformed_model_response", {"errors": e.errors, "raw": e.raw})
                retries_counter[0] += 1
                if retries_counter[0] > self.max_malformed_retries:
                    raise
                if "exhausted its reasoning budget" in e.errors:
                    max_tokens_override = self.reasoning_budget_retry_max_tokens
                attempt = messages + [{"role": "user", "content":
                    f"Your last response did not match a required shape ({e.errors}). "
                    "Respond again: either call a tool natively, or if you are not calling a "
                    "tool, respond with exactly one fenced JSON block matching update_investigation "
                    "or conclude."}]

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
        # Counted unconditionally (Part 8 instrumentation): this is one
        # real model round-trip regardless of whether it succeeds or
        # raises MalformedModelResponse below.
        state.decide_calls_total += 1
        try:
            # A materially higher cap than routine turns (real incident
            # #3, 2026-08-25 canto run -- see DEFAULT_FORCED_CONCLUSION_
            # MAX_TOKENS): this is the one turn asking the model to
            # synthesize a full CEIV chain for every property in the
            # cluster at once, and it is called at most once per cluster,
            # so the extra headroom's cost impact is bounded.
            turn = self.model_client.decide(forced_prompt, max_tokens=self.forced_conclusion_max_tokens)
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
        # Inline counterexample-attempt fallback (root cause #1 fix):
        # recorded via the SAME state method `_apply_investigation_update`
        # uses, after hypotheses are upserted above so a referenced
        # hypothesis_id is guaranteed to already exist. Runs before the
        # completion gate is checked against the proposed state copy in
        # `_apply_conclusion`.
        for attempt in conclude.counterexample_attempts:
            state.record_counterexample_attempt(
                attempt.property_id, attempt.hypothesis_id, attempt.attempt, attempt.result)

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
        # Closes a real gap found live (2026-08-26): these two state
        # fields (and set_next_actions) already existed and were already
        # rendered in the compacted state summary, but nothing wrote to
        # them from any model action -- always empty in every real run.
        # Replacement, not append (matches set_next_actions's existing
        # semantics), and only when THIS update actually provides a new
        # list -- an update that only touches hypotheses must not wipe
        # out what an earlier turn recorded.
        if update.unresolved_questions:
            state.unresolved_questions = list(update.unresolved_questions)
        if update.next_actions:
            state.set_next_actions(update.next_actions)
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
