"""Deterministic (non-LLM) context compaction for the security-agent
kernel (RTF_SECURITY_AGENT_CONTEXT_MANAGEMENT_DESIGN.md section 5).

The root cause fixed here (RTF_SECURITY_AGENT_EFFICIENCY_INVESTIGATION_
20260817.md): `kernel.py` used to append every tool result and every
turn to `messages` forever, with nothing ever pruned. Context grew
without bound, and once it crossed the model's effective reasoning
budget the response quality degraded (empty/capped completions), which
triggered a retry that appended even MORE context -- a compounding
failure spiral, not a one-off bug.

Compaction here is a pure function of `ClusterInvestigationState` (the
authoritative record) plus a small window of recent raw turns -- never
an LLM summarization call -- so it is reproducible and unit-testable
without a model in the loop, and the model-facing context can always be
rebuilt from state alone if raw turns were lost.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from rtf.security_agent.prompts import build_initial_user_message, build_system_prompt
from rtf.security_agent.state import ClusterInvestigationState, ToolCallRecord

# Rationale (not arbitrary -- tied to the efficiency investigation's own
# data): the pathological clusters' prompts were consistently fine under
# ~29K tokens and consistently produced empty/capped completions once
# they crossed ~42K. SOFT_COMPACTION_TOKENS leaves real headroom before
# that danger zone; HARD_COMPACTION_TOKENS sits just under the ~65K
# pathological ceiling observed pre-fix, as a last-resort safety net if
# even a freshly-rebuilt context (system + cluster context + state
# summary + recent turns) is still too large. Both are named constants,
# explicitly not claimed final -- real post-fix instrumentation is the
# actual basis for tuning these later, not this one-time estimate.
SOFT_COMPACTION_TOKENS = 20_000
HARD_COMPACTION_TOKENS = 60_000
RECENT_TURNS_KEPT = 4
MAX_TOOL_QUERY_INDEX_LINES = 40
"""Bounds the "already asked" index (render_state_summary) the same way
RECENT_TURNS_KEPT bounds the raw-turn tail: a real gap found via
trajectory analysis (RTF_SECURITY_AGENT_NATURAL_CONCLUSION_INVESTIGATION_
20260826.md) is that `state.tool_history` -- which DOES store the exact
(tool, args) signature of every call ever made -- was never rendered into
the model-visible context at all once its raw turn aged out of
RECENT_TURNS_KEPT, so the model had no way to recognize "I already asked
this" before re-asking (dedup only fires reactively, after the repeat is
already requested). Named, not claimed final -- same discipline as the
other constants in this module."""


def _evidence_scope(ev) -> str:
    if ev.source_contract and ev.source_function:
        return f"{ev.source_contract}.{ev.source_function}"
    return ev.source_contract or ev.source_function or ""


_ARG_VALUE_TRUNCATE_CHARS = 40


def _render_tool_query_index(state: ClusterInvestigationState) -> list[str]:
    """One line per unique (tool, args) signature already tried, so the
    model can recognize a prior request even after its raw turn has been
    compacted away -- generic across every tool (not a per-tool
    heuristic), since it renders whatever args each call actually used
    rather than guessing at a "salient" key. Deduplicated using the same
    (tool, json.dumps(args, sort_keys=True)) key scheme
    `state.progress_fingerprint()` already uses, for consistency. Bounded
    to the MOST RECENT `MAX_TOOL_QUERY_INDEX_LINES` unique calls -- older
    ones are the ones most likely already folded into the evidence index
    above, and recency is what matters most for avoiding an immediate
    re-ask right after a compaction."""
    evidence_id_by_tool_call_id = {
        ev.tool_call_id: eid for eid, ev in state.evidence.items() if ev.tool_call_id
    }
    seen: dict[tuple[str, str], ToolCallRecord] = {}
    for record in state.tool_history:
        key = (record.tool, json.dumps(record.args, sort_keys=True))
        seen.setdefault(key, record)
    kept = list(seen.values())[-MAX_TOOL_QUERY_INDEX_LINES:]
    lines = []
    for record in kept:
        args_str = ", ".join(
            f"{k}={str(v)[:_ARG_VALUE_TRUNCATE_CHARS]}" for k, v in sorted(record.args.items())
        )
        pointer = evidence_id_by_tool_call_id.get(record.id)
        suffix = f" -> {pointer}" if pointer else f" -> {record.id}"
        lines.append(f"- {record.tool}({args_str}){suffix}")
    return lines


def estimate_tokens(text: str) -> int:
    """A cheap, dependency-free heuristic (~4 chars/token), deliberately
    conservative. No tokenizer dependency added for this -- real token
    counts are already logged post-hoc via ChatResult and can
    validate/recalibrate this constant later without changing any of
    this module's call sites."""
    return max(1, len(text) // 4)


def estimate_messages_tokens(messages: list[dict]) -> int:
    """Whole-entry estimation (found live, native-tool-calling migration,
    2026-08-26): the prior `m.get("content", "")`-only estimate silently
    counted a tool-call-REQUEST entry (`{"role": "assistant",
    "tool_calls": [...]}`, no `content` key at all) as ~1 token
    regardless of its real payload size (tool names + JSON args can be
    substantial), delaying compaction past the point it's actually
    needed -- exactly the pathology this module exists to prevent.
    `json.dumps` over the whole entry is strictly more accurate for
    every existing entry shape too, not just the new one."""
    return sum(estimate_tokens(json.dumps(m)) for m in messages)


def should_compact(messages: list[dict], threshold: int = SOFT_COMPACTION_TOKENS) -> bool:
    return estimate_messages_tokens(messages) >= threshold


@dataclass(frozen=True)
class ClusterContext:
    """The static artifacts that define a cluster investigation --
    everything `build_initial_user_message` needs. Bundled once so
    `build_context` can be called repeatedly (cluster start, then again
    on every compaction) without threading four separate parameters
    through the kernel's control loop each time."""

    property_ids: list[str]
    protocol_context_md: str
    requirement_context_by_property: dict[str, str]
    cluster_plan_md: str


def render_state_summary(state: ClusterInvestigationState) -> str:
    """Deterministic markdown rendering of everything the design
    requires to survive compaction: property statuses, an evidence
    INDEX (id/claim/location only -- not full excerpts, those stay on
    disk behind `read_evidence`), hypotheses, unresolved questions, and
    next actions. Iteration order is always sorted by id, never
    dict/insertion order, so two calls against equal state produce byte-
    identical output."""
    lines = ["## Investigation state so far (compacted)", "", "### Property status"]
    for pid in state.property_ids:
        req = state.requirement_states[pid]
        suffix = f" -- {req.resolution_reason}" if req.resolution_reason else ""
        lines.append(f"- {pid}: {req.status.value}{suffix}")

    lines += ["", "### Evidence index (use read_evidence(evidence_id) for full content)"]
    if state.evidence:
        for eid in sorted(state.evidence):
            ev = state.evidence[eid]
            location = ev.source_file + (f":{ev.source_lines}" if ev.source_lines else "")
            scope = _evidence_scope(ev)
            prefix = f"{scope} " if scope else ""
            lines.append(f"- {eid}: {ev.claim} @ {prefix}{location}")
    else:
        lines.append("(none yet)")

    lines += ["", "### Already asked (avoid repeating these -- nothing new will be learned)"]
    tool_query_lines = _render_tool_query_index(state)
    lines += tool_query_lines if tool_query_lines else ["(none yet)"]

    lines += ["", "### Hypotheses"]
    if state.hypotheses:
        for hid in sorted(state.hypotheses):
            hyp = state.hypotheses[hid]
            props = ", ".join(hyp.originating_property_ids)
            lines.append(f"- {hid} [{hyp.status.value}] (properties: {props}): {hyp.claim}")
    else:
        lines.append("(none yet)")

    lines += [
        "",
        "### Inspected so far",
        f"Files: {', '.join(sorted(state.inspected_files)) or '(none)'}",
        f"Contracts: {', '.join(sorted(state.inspected_contracts)) or '(none)'}",
        f"Functions: {', '.join(sorted(state.inspected_functions)) or '(none)'}",
        "",
        "### Unresolved questions",
    ]
    lines += [f"- {q}" for q in state.unresolved_questions] or ["(none)"]

    lines += ["", "### Next actions (your own prior notes)"]
    lines += [f"- {a}" for a in state.next_actions] or ["(none recorded)"]

    lines += [
        "",
        "This is a COMPACTED context: older raw tool outputs and turns have "
        "been dropped to stay within budget. Full content for any evidence "
        "item is still available via read_evidence(evidence_id). The "
        "structured state above is authoritative -- trust it over anything "
        "not repeated here.",
    ]
    return "\n".join(lines)


def build_context(
    state: ClusterInvestigationState,
    cluster_context: ClusterContext,
    recent_turns: list[list[dict]],
) -> list[dict]:
    """Deterministically rebuilds the full model-facing `messages` list:
    system prompt + cluster context (unchanged -- protocol/requirement/
    plan) + a structured state summary + only the last RECENT_TURNS_KEPT
    raw turns verbatim. Called once at cluster start (recent_turns=[])
    and again whenever the soft token threshold is crossed.

    `recent_turns` is a list of GROUPS, one per logical turn (see
    `kernel.py`'s `_append_group`) -- a plain turn is a 1-entry group; a
    native multi-tool-call turn is one group holding its request entry
    plus all of that turn's result entries together. Group-aware (found
    live, native-tool-calling migration, 2026-08-26): trimming a flat
    list of individual message dicts could split a multi-call turn's
    request entry from its own result entries across the trim boundary,
    producing a `function_call_output` with no matching earlier
    `function_call` -- an invalid next request (Part 0, live-verified).
    Selecting whole GROUPS keeps every turn atomic; `RECENT_TURNS_KEPT`
    now means what its own name already claims -- the last N raw turns,
    not N raw message dicts.

    Falls back to fewer recent turns (down to zero) if even the
    compacted result is still over HARD_COMPACTION_TOKENS -- the state
    summary itself is never dropped, only the raw-turn tail shrinks
    further.
    """
    header = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": build_initial_user_message(
            cluster_context.property_ids, cluster_context.protocol_context_md,
            cluster_context.requirement_context_by_property, cluster_context.cluster_plan_md)},
        {"role": "user", "content": render_state_summary(state)},
    ]
    kept = RECENT_TURNS_KEPT
    while True:
        tail = [entry for group in recent_turns[-kept:] for entry in group] if kept > 0 else []
        messages = header + tail
        if kept == 0 or estimate_messages_tokens(messages) <= HARD_COMPACTION_TOKENS:
            return messages
        kept -= 1
