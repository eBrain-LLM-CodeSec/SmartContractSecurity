"""Unit tests for rtf.security_agent.context_manager -- deterministic
context compaction (RTF_SECURITY_AGENT_CONTEXT_MANAGEMENT_DESIGN.md
section 5). No LLM calls anywhere in this file."""
from __future__ import annotations

from rtf.security_agent import context_manager as cm
from rtf.security_agent.state import (
    ClusterInvestigationState, Evidence, Hypothesis, HypothesisStatus,
    RequirementResolution,
)

_CONTEXT = cm.ClusterContext(
    property_ids=["p1", "p2"],
    protocol_context_md="protocol text",
    requirement_context_by_property={"req-1": "requirement text"},
    cluster_plan_md="plan text",
)


def test_estimate_tokens_is_positive_and_monotonic_in_length():
    assert cm.estimate_tokens("") >= 1
    assert cm.estimate_tokens("x" * 400) > cm.estimate_tokens("x" * 40)


def test_estimate_messages_tokens_counts_a_no_content_tool_call_entry_accurately():
    """Found live (native-tool-calling migration, 2026-08-26): the old
    `m.get("content", "")`-only estimate silently counted a tool-call-
    REQUEST entry (no `content` key at all) as ~1 token regardless of
    its real payload size, delaying compaction past the point it's
    actually needed. The whole-entry `json.dumps` estimate must scale
    with the real payload."""
    tiny = [{"role": "user", "content": "hi"}]
    big_tool_call_entry = [{"role": "assistant", "tool_calls": [
        {"call_id": "c1", "tool": "get_function_source",
         "args": {"contract": "Vault", "function": "x" * 2000}},
    ]}]
    assert cm.estimate_messages_tokens(big_tool_call_entry) > cm.estimate_messages_tokens(tiny) * 50


def test_should_compact_true_only_once_threshold_crossed():
    small = [{"role": "user", "content": "short"}]
    assert not cm.should_compact(small, threshold=1000)
    big = [{"role": "user", "content": "x" * 5000}]
    assert cm.should_compact(big, threshold=1000)


def test_build_context_always_includes_system_and_cluster_context():
    state = ClusterInvestigationState.initial("c1", ["p1", "p2"])
    messages = cm.build_context(state, _CONTEXT, recent_turns=[])
    assert messages[0]["role"] == "system"
    assert "protocol text" in messages[1]["content"]
    assert "plan text" in messages[1]["content"]


def test_build_context_state_summary_reflects_property_status_and_evidence():
    state = ClusterInvestigationState.initial("c1", ["p1", "p2"])
    state.add_evidence(Evidence(id="ev-1", claim="withdraw pays before decrementing",
                                source_file="Vault.sol", source_lines="30-42"))
    state.resolve_requirement("p1", RequirementResolution.FAIL, reason="reentrancy")
    messages = cm.build_context(state, _CONTEXT, recent_turns=[])
    summary = messages[2]["content"]
    assert "p1: FAIL" in summary
    assert "reentrancy" in summary
    assert "ev-1" in summary and "Vault.sol:30-42" in summary
    assert "p2: UNRESOLVED" in summary


def test_build_context_evidence_index_omits_raw_excerpt():
    """The evidence INDEX must stay compact -- full excerpt content
    belongs behind read_evidence, not inlined into every rebuilt
    context (that would defeat the whole point of externalizing it)."""
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.add_evidence(Evidence(id="ev-1", claim="c", source_file="F.sol",
                                raw_excerpt="X" * 2000))
    messages = cm.build_context(state, _CONTEXT, recent_turns=[])
    summary = messages[2]["content"]
    assert "X" * 2000 not in summary


def test_build_context_evidence_index_includes_source_contract_and_function():
    """Evidence carries source_contract/source_function, but the index
    LINE ITSELF used to drop both -- they only ever surfaced separately,
    in the coarse, unlinked 'Inspected so far' name sets. Checks the
    evidence-index bullet specifically (not just "somewhere in the
    summary"), since add_evidence already populates inspected_functions
    independently -- that would make this assertion pass even without
    the evidence-index fix if it only checked the whole summary."""
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.add_evidence(Evidence(id="ev-1", claim="c", source_file="Vault.sol",
                                source_contract="Vault", source_function="withdraw"))
    summary = cm.build_context(state, _CONTEXT, recent_turns=[])[2]["content"]
    evidence_line = next(l for l in summary.splitlines() if l.startswith("- ev-1:"))
    assert "Vault.withdraw" in evidence_line


def test_build_context_state_summary_lets_model_recognize_an_aged_out_tool_call_without_reasking():
    """The specific gap found via real trajectory analysis
    (RTF_SECURITY_AGENT_NATURAL_CONCLUSION_INVESTIGATION_20260826.md): once
    a tool call's own raw turn ages out past RECENT_TURNS_KEPT, nothing in
    the rendered summary let the model recognize it had already made that
    exact (tool, args) request -- state.tool_history stores the exact
    signature but was never rendered at all."""
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.record_tool_call("get_function_source", {"contract": "Vault", "function": "withdraw"},
                           "OK (source)", {"status": "OK", "file": "Vault.sol",
                                           "contract": "Vault", "name": "withdraw"})
    # The raw turn that actually made the call above is NOT in
    # recent_turns at all -- simulating it having already aged out past
    # RECENT_TURNS_KEPT and been dropped, exactly the real scenario.
    groups = [[{"role": "user", "content": f"turn-{i}"}] for i in range(cm.RECENT_TURNS_KEPT + 5)]
    messages = cm.build_context(state, _CONTEXT, recent_turns=groups)
    summary = messages[2]["content"]
    tail = messages[3:]
    assert not any("get_function_source" in str(m.get("content", "")) for m in tail), \
        "raw turn should be aged out of the tail"
    assert "get_function_source" in summary
    assert "Vault" in summary and "withdraw" in summary


def test_build_context_tool_query_index_is_bounded():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    for i in range(cm.MAX_TOOL_QUERY_INDEX_LINES + 20):
        state.record_tool_call("search_repository", {"pattern": f"pattern-{i}"}, "OK (hits)",
                               {"status": "OK", "hits": [{"file": "F.sol", "line": 1, "text": "x"}]})
    summary = cm.build_context(state, _CONTEXT, recent_turns=[])[2]["content"]
    query_index_lines = [l for l in summary.splitlines() if l.startswith("- search_repository(")]
    assert len(query_index_lines) == cm.MAX_TOOL_QUERY_INDEX_LINES


def test_build_context_includes_hypotheses_and_next_actions_and_questions():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    state.add_hypothesis(Hypothesis(id="hyp-1", claim="reentrancy possible",
                                    originating_property_ids=["p1"],
                                    status=HypothesisStatus.SUPPORTED))
    state.unresolved_questions.append("does the oracle ever return 0?")
    state.set_next_actions(["check Ln.sol rounding path"])
    summary = cm.build_context(state, _CONTEXT, recent_turns=[])[2]["content"]
    assert "hyp-1" in summary and "SUPPORTED" in summary and "reentrancy possible" in summary
    assert "does the oracle ever return 0?" in summary
    assert "check Ln.sol rounding path" in summary


def test_build_context_keeps_only_last_recent_turns_kept():
    """`recent_turns` is a list of GROUPS (one per logical turn), not a
    flat list of message dicts -- native-tool-calling migration,
    2026-08-26. Each group here is a 1-entry group (the legacy shape)."""
    state = ClusterInvestigationState.initial("c1", ["p1"])
    groups = [[{"role": "user", "content": f"turn-{i}"}] for i in range(10)]
    messages = cm.build_context(state, _CONTEXT, recent_turns=groups)
    tail = messages[3:]
    assert len(tail) == cm.RECENT_TURNS_KEPT
    assert [m["content"] for m in tail] == [f"turn-{i}" for i in range(10 - cm.RECENT_TURNS_KEPT, 10)]


def test_build_context_never_splits_a_multi_entry_group_across_the_trim_boundary():
    """The concrete risk this atomicity fix prevents (Part 0, live-
    verified): a native multi-tool-call turn's group holds its assistant
    request entry PLUS every one of that turn's result entries. Trimming
    must keep or drop the whole group, never leave a result entry
    without its own request entry (an invalid next request)."""
    state = ClusterInvestigationState.initial("c1", ["p1"])
    multi_entry_group = [
        {"role": "assistant", "tool_calls": [{"call_id": "c1", "tool": "get_callers", "args": {}}]},
        {"role": "tool", "call_id": "c1", "tool": "get_callers", "content": "result"},
    ]
    plain_group = [{"role": "user", "content": "plain-turn"}]
    groups = [multi_entry_group, plain_group]
    for kept in range(0, cm.RECENT_TURNS_KEPT + 1):
        original_kept = cm.RECENT_TURNS_KEPT
        cm.RECENT_TURNS_KEPT = kept
        try:
            messages = cm.build_context(state, _CONTEXT, recent_turns=groups)
        finally:
            cm.RECENT_TURNS_KEPT = original_kept
        tail = messages[3:]
        has_request = any(m.get("role") == "assistant" and "tool_calls" in m for m in tail)
        has_result = any(m.get("role") == "tool" for m in tail)
        assert has_request == has_result, (kept, tail)


def test_build_context_shrinks_tail_further_if_still_over_hard_threshold():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    huge_groups = [[{"role": "user", "content": "x" * 300_000}] for _ in range(cm.RECENT_TURNS_KEPT)]
    messages = cm.build_context(state, _CONTEXT, recent_turns=huge_groups)
    assert cm.estimate_messages_tokens(messages) <= cm.HARD_COMPACTION_TOKENS
    assert len(messages) < 3 + cm.RECENT_TURNS_KEPT


def test_build_context_is_deterministic_for_equal_state():
    """Same content in a different dict-insertion order must still
    render identically -- render_state_summary sorts by id, never
    relying on dict/insertion order."""
    state_a = ClusterInvestigationState.initial("c1", ["p1", "p2"])
    state_a.add_evidence(Evidence(id="ev-b", claim="b", source_file="B.sol"))
    state_a.add_evidence(Evidence(id="ev-a", claim="a", source_file="A.sol"))

    state_b = ClusterInvestigationState.initial("c1", ["p1", "p2"])
    state_b.add_evidence(Evidence(id="ev-a", claim="a", source_file="A.sol"))
    state_b.add_evidence(Evidence(id="ev-b", claim="b", source_file="B.sol"))

    assert cm.render_state_summary(state_a) == cm.render_state_summary(state_b)
