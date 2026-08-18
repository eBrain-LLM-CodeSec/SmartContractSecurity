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
    state = ClusterInvestigationState.initial("c1", ["p1"])
    turns = [{"role": "user", "content": f"turn-{i}"} for i in range(10)]
    messages = cm.build_context(state, _CONTEXT, recent_turns=turns)
    tail = messages[3:]
    assert len(tail) == cm.RECENT_TURNS_KEPT
    assert [m["content"] for m in tail] == [f"turn-{i}" for i in range(10 - cm.RECENT_TURNS_KEPT, 10)]


def test_build_context_shrinks_tail_further_if_still_over_hard_threshold():
    state = ClusterInvestigationState.initial("c1", ["p1"])
    huge_turns = [{"role": "user", "content": "x" * 300_000} for _ in range(cm.RECENT_TURNS_KEPT)]
    messages = cm.build_context(state, _CONTEXT, recent_turns=huge_turns)
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
