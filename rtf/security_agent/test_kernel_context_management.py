"""Deterministic tests for the context-management redesign's kernel.py
changes (RTF_SECURITY_AGENT_CONTEXT_MANAGEMENT_DESIGN.md sections 4/5/
6/7/8): retry semantics that don't grow the permanent conversation,
circuit breakers + forced conclusion, no-progress detection, and
evidence-store wiring. NO real LLM calls -- reuses the ScriptedChatClient/
tools fixtures from test_kernel_mocked.py. Plain pytest asserts (unlike
that file's own check()-based convention, which is only enforced by its
own __main__ runner, not by plain `pytest` collection).
"""
from __future__ import annotations

from pathlib import Path

from a4v.llm import ChatResult

from rtf.security_agent.evidence_store import EvidenceStore
from rtf.security_agent.kernel import RESPONSE_MODELS, SecurityAgentKernel
from rtf.security_agent.model_client import ModelClient
from rtf.security_agent.state import RequirementResolution
from rtf.security_agent.test_kernel_mocked import (
    _CONTEXT, _PROPERTY_IDS, ScriptedChatClient, _tools,
)


def _kernel_with(script, tmp_path=None, **kwargs) -> tuple[SecurityAgentKernel, ScriptedChatClient]:
    fake = ScriptedChatClient(script)
    mc = ModelClient(fake, RESPONSE_MODELS)
    kwargs.setdefault("enforce_completion", False)
    tools = _tools()
    evidence_store = EvidenceStore(tmp_path) if tmp_path is not None else None
    if evidence_store is not None:
        kwargs.setdefault("evidence_store", evidence_store)
        # `_tools()` is a cached module-level singleton (real Slither
        # compilation, reused across every test in this file for speed)
        # built without a store -- the kernel's OWN evidence_store isn't
        # enough on its own, since `read_evidence` is dispatched through
        # `self.tools.call(...)`, which consults the TOOLS object's own
        # `evidence_store` attribute, not the kernel's. Rebinding it here
        # (a plain attribute, not construction-only) is what a real
        # investigator.py call site does implicitly by passing the same
        # store to both `build_tools(...)` and `SecurityAgentKernel(...)`.
        tools.evidence_store = evidence_store
    else:
        tools.evidence_store = None  # undo a prior test's mutation of this shared singleton
    kernel = SecurityAgentKernel(tools, mc, **kwargs)
    return kernel, fake


# --- Part 6: malformed retries branch from the last valid state, don't grow --

def test_malformed_retry_corrective_message_does_not_persist_into_later_calls():
    garbage = ({"action": "something_unrecognized"}, None)
    good_update = ({"action": "update_investigation", "hypotheses": [{
        "id": "hyp-1", "claim": "x", "originating_property_ids": ["p1"], "status": "OPEN",
    }], "counterexample_attempts": []}, None)
    conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel_with([garbage, good_update, conclude], max_malformed_retries=2)
    kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    assert len(fake.calls) == 3
    # call[1] is the retry attempt for the malformed call[0] -- it SHOULD
    # carry the corrective message (that's the whole point of the retry).
    assert any("did not match the required JSON shape" in str(m.get("content", ""))
               for m in fake.calls[1])
    # call[2] is a genuinely later turn, built from `messages` (never from
    # the retry-only `attempt` list) -- the corrective must NOT still be
    # sitting in the permanent conversation by this point.
    assert not any("did not match the required JSON shape" in str(m.get("content", ""))
                  for m in fake.calls[2])


def test_malformed_retry_each_attempt_branches_from_same_base_not_previous_attempt():
    """Two consecutive malformed responses must each retry from the SAME
    base `messages`, not accumulate on top of each other -- call[2]'s
    message list must be exactly one corrective longer than call[0]'s,
    never two independent correctives stacked."""
    garbage = ({"action": "nonsense"}, None)
    conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel_with([garbage, garbage, conclude], max_malformed_retries=2)
    kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    assert len(fake.calls) == 3
    assert len(fake.calls[1]) == len(fake.calls[0]) + 1
    assert len(fake.calls[2]) == len(fake.calls[0]) + 1  # not +2


# --- Part 7: circuit breakers + forced conclusion ---------------------------

def test_wall_clock_breaker_forces_conclusion_instead_of_bare_unresolved():
    forced_conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "INCONCLUSIVE", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel_with([forced_conclude], max_wall_clock_s=0.0)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    assert len(fake.calls) == 1  # the forced-conclusion turn only
    assert state.requirement_states["p1"].status == RequirementResolution.FAIL
    assert state.requirement_states["p2"].status == RequirementResolution.INCONCLUSIVE


def test_wall_clock_breaker_with_no_usable_response_still_produces_inconclusive_not_unresolved():
    garbage = ({"action": "nonsense"}, None)
    kernel, fake = _kernel_with([garbage] * 10, max_wall_clock_s=0.0, max_malformed_retries=2)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    assert all(rs.status == RequirementResolution.INCONCLUSIVE for rs in state.requirement_states.values())
    assert all("forced_conclusion" in (rs.resolution_reason or "") for rs in state.requirement_states.values())


def test_cost_breaker_forces_conclusion_after_budget_exceeded():
    expensive = ChatResult(content="", prompt_tokens=10, completion_tokens=10, cached=False, cost_usd=5.0)
    tool_call = ({"action": "call_tool", "tool": "get_contract_source",
                  "args": {"contract": "Vault"}, "reasoning": "r"}, expensive)
    forced_conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "NOT_APPLICABLE", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel_with([tool_call, forced_conclude], max_cost_usd=1.0)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    assert len(fake.calls) == 2
    assert state.requirement_states["p1"].status == RequirementResolution.FAIL
    assert state.requirement_states["p2"].status == RequirementResolution.NOT_APPLICABLE


def test_forced_conclusion_downgrades_ungrounded_pass_to_inconclusive_not_silently_accepted():
    """Constraint: do not weaken PASS evidence requirements merely to
    raise resolution, even under a budget-exhaustion forced conclusion.
    A PASS with no counterexample attempt at all must be downgraded, not
    accepted as-is, and the downgrade reason must be recorded."""
    forced_conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "looks safe, no time to verify"},
        {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel_with([forced_conclude], max_wall_clock_s=0.0)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    assert state.requirement_states["p1"].status == RequirementResolution.INCONCLUSIVE
    assert "forced_conclusion_pass_rejected" in (state.requirement_states["p1"].resolution_reason or "")
    assert state.requirement_states["p2"].status == RequirementResolution.FAIL


def test_forced_conclusion_missing_property_id_becomes_inconclusive():
    forced_conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
        # p2 omitted entirely
    ]}, None)
    kernel, fake = _kernel_with([forced_conclude], max_wall_clock_s=0.0)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    assert state.requirement_states["p1"].status == RequirementResolution.FAIL
    assert state.requirement_states["p2"].status == RequirementResolution.INCONCLUSIVE
    assert "forced_conclusion_missing_property_id" == state.requirement_states["p2"].resolution_reason


# --- Part 8: deterministic no-progress detection -----------------------------

def test_no_progress_breaker_triggers_on_repeated_identical_tool_call():
    repeat_call = ({"action": "call_tool", "tool": "get_contract_source",
                    "args": {"contract": "Vault"}, "reasoning": "r"}, None)
    forced_conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "INCONCLUSIVE", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "INCONCLUSIVE", "reasoning": "r2"},
    ]}, None)
    # 1st call is real progress (a newly-inspected contract); repeats add
    # nothing new to inspected_files/contracts/evidence/hypotheses/etc.
    script = [repeat_call, repeat_call, repeat_call, forced_conclude]
    kernel, fake = _kernel_with(script, max_consecutive_no_progress=2, max_steps=20)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    assert len(fake.calls) == 4  # stalls out before exhausting max_steps=20
    assert state.requirement_states["p1"].status == RequirementResolution.INCONCLUSIVE


def test_no_progress_breaker_does_not_trigger_when_each_call_is_genuinely_new():
    calls = [
        ({"action": "call_tool", "tool": "get_contract_source",
          "args": {"contract": "Vault"}, "reasoning": "r"}, None),
        ({"action": "call_tool", "tool": "get_function_source",
          "args": {"contract": "Vault", "function": "withdraw"}, "reasoning": "r"}, None),
    ]
    conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel_with(calls + [conclude], max_consecutive_no_progress=2)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    assert len(fake.calls) == 3
    assert all(rs.status == RequirementResolution.PASS for rs in state.requirement_states.values())


# --- Part 4: evidence-store wiring -------------------------------------------

def test_tool_result_externalized_to_evidence_store_and_summarized_in_conversation(tmp_path):
    call = ({"action": "call_tool", "tool": "get_contract_source",
             "args": {"contract": "Vault"}, "reasoning": "r"}, None)
    conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel_with([call, conclude], tmp_path=tmp_path)
    kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    tool_result_message = fake.calls[1][-1]["content"]
    assert "evidence_id=tool-1" in tool_result_message
    assert "read_evidence" in tool_result_message
    # the full contract source is long -- it must not be inlined verbatim
    # once a store is configured.
    assert len(tool_result_message) < 2000


def test_read_evidence_tool_retrieves_full_content_via_kernel_loop(tmp_path):
    call = ({"action": "call_tool", "tool": "get_contract_source",
             "args": {"contract": "Vault"}, "reasoning": "r"}, None)
    read_back = ({"action": "call_tool", "tool": "read_evidence",
                 "args": {"evidence_id": "tool-1"}, "reasoning": "need the full source"}, None)
    conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel_with([call, read_back, conclude], tmp_path=tmp_path)
    kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    read_evidence_result = fake.calls[2][-1]["content"]
    assert '"status": "OK"' in read_evidence_result or '"status":"OK"' in read_evidence_result
    assert "contract Vault" in read_evidence_result


def test_no_evidence_store_configured_falls_back_to_inline_tool_result():
    """Backward compatibility: a kernel built without an evidence_store
    (the pre-redesign call pattern) must behave exactly as before --
    full inline tool results, no evidence_id."""
    call = ({"action": "call_tool", "tool": "get_contract_source",
             "args": {"contract": "Vault"}, "reasoning": "r"}, None)
    conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel_with([call, conclude])
    kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    tool_result_message = fake.calls[1][-1]["content"]
    assert "evidence_id=" not in tool_result_message
    assert "contract Vault" in tool_result_message
