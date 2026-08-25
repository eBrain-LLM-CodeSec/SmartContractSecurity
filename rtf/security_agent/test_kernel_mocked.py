"""Deterministic tests for rtf.security_agent.kernel's control loop --
NO real LLM calls anywhere in this file (a ScriptedChatClient test
double stands in for a4v.llm.ChatClient, matching this codebase's own
established mock-first convention, e.g.
rtf.l11_investigation_grouping.test_semantic_only_driver.FakeChatClient).
Real Slither compilation of the existing tests/fixtures/multi_contract/
Vault.sol fixture IS used for the tool layer -- that part is already
proven correct by test_tools.py; here it just needs to behave like real
tools inside a real multi-turn loop. Run with:
    .venv/bin/python3 -m rtf.security_agent.test_kernel_mocked
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from a4v.llm import ChatResult
from pydantic import ValidationError

from rtf.security_agent.kernel import ConcludeAction, RESPONSE_MODELS, SecurityAgentKernel
from rtf.security_agent.model_client import ModelClient
from rtf.security_agent.state import RequirementResolution
from rtf.security_agent.tools import SecurityAgentTools

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


# --- real tools, over the existing Vault.sol fixture (see test_tools.py) --

_SOLC_SELECT_ARTIFACTS = Path.home() / ".solc-select" / "artifacts"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_VAULT_DIR = _REPO_ROOT / "tests" / "fixtures" / "multi_contract"
_VAULT_SOL = _VAULT_DIR / "Vault.sol"
_TOOLS: SecurityAgentTools | None = None


def _solc_bin_dir_for(version: str, scratch_root: Path) -> str:
    """Same pattern as test_tools.py/test_tools_foundry_scope.py -- see
    those files' own docstrings for why it's duplicated per-caller."""
    artifact = _SOLC_SELECT_ARTIFACTS / f"solc-{version}" / f"solc-{version}"
    if not artifact.exists():
        raise RuntimeError(f"solc {version} is not installed via solc-select (expected {artifact})")
    real_version = subprocess.run([str(artifact), "--version"], capture_output=True, text=True, check=True).stdout
    if f"Version: {version}" not in real_version:
        raise RuntimeError(f"solc-select artifact at {artifact} does not report version {version}: {real_version.strip()!r}")
    bin_dir = scratch_root / f"solc_bin_{version.replace('.', '')}"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link = bin_dir / "solc"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(artifact)
    return str(bin_dir)


def _tools() -> SecurityAgentTools:
    global _TOOLS
    if _TOOLS is None:
        solc_dir = _solc_bin_dir_for("0.8.20", Path(tempfile.mkdtemp(prefix="security_agent_test_solc_")))
        os.environ["PATH"] = f"{solc_dir}:{os.environ.get('PATH', '')}"
        _TOOLS = SecurityAgentTools.build(repo_root=_VAULT_DIR, entry_file=_VAULT_SOL)
    return _TOOLS


# --- scripted model responses -----------------------------------------------

class ScriptedChatClient:
    """Stands in for a4v.llm.ChatClient. ModelClient.decide() calls
    .complete() directly (not .complete_json()) so it can inspect
    content=None before extract_last_fenced_json ever sees it -- each
    script entry's raw_dict is JSON-serialized and fence-wrapped into a
    real ChatResult.content string, so the real extract_last_fenced_json
    parsing path is genuinely exercised, not bypassed. Records every
    `messages` list it was called with, so tests can assert on
    conversation growth (e.g. a corrective retry message got appended)."""

    def __init__(self, script: list[tuple[dict, "ChatResult | None"]]):
        self._script = list(script)
        self.calls: list[list[dict]] = []
        self.max_tokens_calls: list[int | None] = []

    def complete(self, messages, temperature: float = 0.0, top_p=None, max_tokens=None):
        self.calls.append([dict(m) for m in messages])
        self.max_tokens_calls.append(max_tokens)
        if len(self.calls) > len(self._script):
            raise AssertionError(f"kernel made more model calls ({len(self.calls)}) than scripted ({len(self._script)})")
        raw, result = self._script[len(self.calls) - 1]
        # Keep Increment-2 scenario fixtures concise while exercising the
        # stricter Increment-3 production schema. Tests specifically about
        # CEIV behavior below provide the full shape themselves.
        if raw.get("action") == "conclude":
            raw = dict(raw)
            raw.setdefault("evidence", [{
                "id": "ev-shared", "claim": "inspected fixture evidence",
                "source_file": "Vault.sol", "source_contract": "Vault",
                "source_function": "withdraw", "source_lines": "30-42",
                "tool_call_id": "tool-1", "raw_excerpt": None,
            }])
            first_evidence_id = raw["evidence"][0]["id"]
            raw.setdefault("hypotheses", [{
                "id": "hyp-shared", "claim": "fixture failure hypothesis",
                "originating_property_ids": [p["property_id"] for p in raw["properties"]],
                "status": "SUPPORTED", "supporting_evidence_ids": [first_evidence_id],
                "contradicting_evidence_ids": [], "next_evidence_needed": None,
            }])
            raw["properties"] = [dict(
                p,
                claim=p.get("claim", p.get("reasoning", "property claim")),
                evidence_ids=p.get("evidence_ids", [first_evidence_id]),
                hypothesis_ids=p.get("hypothesis_ids", [raw["hypotheses"][0]["id"]]),
                interpretation=p.get("interpretation", p.get("reasoning", "fixture interpretation")),
            ) for p in raw["properties"]]
            for prop in raw["properties"]:
                prop.pop("reasoning", None)
        content = "```json\n" + json.dumps(raw) + "\n```"
        if result is None:
            return ChatResult(content=content, prompt_tokens=0, completion_tokens=0, cached=False, cost_usd=None)
        return ChatResult(content=content, prompt_tokens=result.prompt_tokens,
                          completion_tokens=result.completion_tokens, cached=result.cached, cost_usd=result.cost_usd)


def _model_client(script: list[tuple[dict, "ChatResult | None"]]) -> ModelClient:
    return ModelClient(ScriptedChatClient(script), RESPONSE_MODELS)


_PROPERTY_IDS = ["p1", "p2"]
_CONTEXT = ("protocol context text", {"req-1": "requirement context text"}, "cluster plan text")


def _kernel(script, **kwargs) -> tuple[SecurityAgentKernel, ScriptedChatClient]:
    fake = ScriptedChatClient(script)
    mc = ModelClient(fake, RESPONSE_MODELS)
    kwargs.setdefault("enforce_completion", False)
    kernel = SecurityAgentKernel(_tools(), mc, **kwargs)
    return kernel, fake


# --- happy path: tool call then a conclude resolving all properties --------

def test_tool_call_then_conclude_resolves_all_properties():
    script = [
        ({"action": "call_tool", "tool": "get_contract_source", "args": {"contract": "Vault"}, "reasoning": "look"}, None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "withdraw pays out before decrementing shares (Vault.sol)"},
            {"property_id": "p2", "verdict": "PASS", "reasoning": "setOracle is gated by onlyOwner"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("p1 resolved FAIL", state.requirement_states["p1"].status == RequirementResolution.FAIL)
    check("p2 resolved PASS", state.requirement_states["p2"].status == RequirementResolution.PASS)
    check("reasoning recorded on p1", "withdraw" in (state.requirement_states["p1"].resolution_reason or ""))
    check("exactly 2 model calls made", len(fake.calls) == 2, len(fake.calls))
    check("one tool call recorded in shared tool_history", len(state.tool_history) == 1, state.tool_history)
    check("tool_history entry is get_contract_source", state.tool_history[0].tool == "get_contract_source")


def test_structured_conclusion_records_shared_ceiv_chain():
    script = [({"action": "conclude", "evidence": [{
        "id": "ev-ordering", "claim": "external call precedes share decrement",
        "source_file": "Vault.sol", "source_contract": "Vault",
        "source_function": "withdraw", "source_lines": "38-41",
        "tool_call_id": "tool-1", "raw_excerpt": "call; shares -= amount;",
    }], "properties": [
        {"property_id": "p1", "claim": "withdraw follows checks-effects-interactions",
         "evidence_ids": ["ev-ordering"],
         "interpretation": "the observed ordering refutes the claim", "verdict": "FAIL"},
        {"property_id": "p2", "claim": "the same ordering preserves accounting invariants",
         "evidence_ids": ["ev-ordering"],
         "interpretation": "stale accounting also refutes this claim", "verdict": "FAIL"},
    ]}, None)]
    kernel, _fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("one shared evidence object stored", list(state.evidence) == ["ev-ordering"], state.evidence)
    check("both assessments reference the same evidence id", all(
        rs.final_assessment and rs.final_assessment.evidence_ids == ["ev-ordering"]
        for rs in state.requirement_states.values()))
    check("claim is separate from interpretation",
          state.requirement_states["p1"].final_assessment.claim ==
          "withdraw follows checks-effects-interactions")
    check("interpretation becomes compatibility reason",
          state.requirement_states["p1"].resolution_reason ==
          "the observed ordering refutes the claim")


def test_structured_conclusion_rejects_dangling_evidence_reference():
    try:
        ConcludeAction.model_validate({
            "action": "conclude",
            "evidence": [{"id": "ev-known", "claim": "fact", "source_file": "Vault.sol"}],
            "hypotheses": [{"id": "hyp-1", "claim": "failure", "originating_property_ids": ["p1"]}],
            "properties": [{
                "property_id": "p1", "claim": "claim",
                "evidence_ids": ["ev-missing"],
                "hypothesis_ids": ["hyp-1"],
                "interpretation": "interpretation", "verdict": "FAIL",
            }],
        })
        check("dangling evidence id rejected", False, "did not raise")
    except ValidationError:
        check("dangling evidence id rejected", True)


def test_hypothesis_update_and_counterexample_are_state_transitions():
    script = [
        ({"action": "update_investigation", "hypotheses": [{
            "id": "hyp-reentry", "claim": "withdraw can re-enter before accounting updates",
            "originating_property_ids": ["p1", "p2"], "status": "OPEN",
            "next_evidence_needed": "ordering of the external call and share decrement",
        }], "counterexample_attempts": []}, None),
        ({"action": "update_investigation", "hypotheses": [{
            "id": "hyp-reentry", "claim": "withdraw can re-enter before accounting updates",
            "originating_property_ids": ["p1", "p2"], "status": "SUPPORTED",
            "next_evidence_needed": None,
        }], "counterexample_attempts": [{
            "property_id": "p1", "hypothesis_id": "hyp-reentry",
            "attempt": "receiver re-enters withdraw from its fallback",
            "result": "share decrement occurs only after the receiver call",
        }]}, None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "reentrant ordering"},
            {"property_id": "p2", "verdict": "PASS", "reasoning": "separate property holds"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("one loop handles updates and final conclusion", len(fake.calls) == 3)
    check("hypothesis persisted as first-class state",
          state.hypotheses["hyp-reentry"].status.value == "SUPPORTED")
    check("one hypothesis is shared across both properties", all(
        "hyp-reentry" in state.requirement_states[pid].hypothesis_ids for pid in _PROPERTY_IDS))
    check("counterexample attempt recorded on property",
          "receiver re-enters" in state.requirement_states["p1"].counterexample_attempts[0])


def test_completion_gate_rejects_premature_pass_then_accepts_grounded_pass():
    premature = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "looks safe"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "looks safe"},
    ]}, None)
    inspect = ({"action": "call_tool", "tool": "get_contract_source",
                "args": {"contract": "Vault"}, "reasoning": "inspect before PASS"}, None)
    falsify = ({"action": "update_investigation", "hypotheses": [{
        "id": "hyp-shared", "claim": "the relevant controls can be bypassed",
        "originating_property_ids": ["p1", "p2"], "status": "REFUTED",
        "contradicting_evidence_ids": ["ev-shared"],
    }], "counterexample_attempts": [
        {"property_id": "p1", "hypothesis_id": "hyp-shared",
         "attempt": "adversarial caller tries the protected path", "result": "guard rejects it"},
        {"property_id": "p2", "hypothesis_id": "hyp-shared",
         "attempt": "boundary path tries to bypass the guard", "result": "guard still applies"},
    ]}, None)
    grounded = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "guard blocks adversary"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "guard covers boundary"},
    ]}, None)
    kernel, fake = _kernel([premature, inspect, falsify, grounded], enforce_completion=True)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("premature conclusion caused another model turn", len(fake.calls) == 4, len(fake.calls))
    check("gate feedback was sent to model", any(
        "completion gate" in str(message.get("content", ""))
        for message in fake.calls[1]))
    check("grounded PASS accepted after inspection and falsification", all(
        state.requirement_states[pid].status == RequirementResolution.PASS for pid in _PROPERTY_IDS))


def test_one_cluster_multiple_properties_is_one_shared_loop():
    """Kernel-level version of the state-layer invariant: a cluster with
    multiple properties runs through ONE model_client.decide/tool_call
    sequence and returns ONE ClusterInvestigationState -- never one
    per-property sub-loop."""
    script = [
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("single model call resolved BOTH properties in one turn", len(fake.calls) == 1, len(fake.calls))
    check("single cluster_id", state.cluster_id == "c1")


# --- termination: max_steps exhaustion --------------------------------------

def test_max_steps_exhausted_attempts_forced_conclusion_instead_of_bare_unresolved():
    """Real gap found live (2026-08-25 canto run): plain max_steps
    exhaustion -- the most common way a cluster naturally runs out of
    budget -- used to skip straight to bare UNRESOLVED with no
    forced-conclusion salvage attempt at all, discarding real
    investigation work. Now matches every other circuit breaker's own
    forced-conclusion-then-INCONCLUSIVE-if-that-also-fails discipline."""
    # Always returns a tool_call for the first 3 (real) turns, exhausting
    # max_steps=3; the 4th scripted entry is the forced-conclusion turn.
    script = [({"action": "call_tool", "tool": "get_contract_source", "args": {"contract": "Vault"},
                "reasoning": "r"}, None)] * 3 + [
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "INCONCLUSIVE", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script, max_steps=3)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("step_count reached max_steps", state.step_count == 3, state.step_count)
    check("exactly one extra call made for the forced-conclusion turn", len(fake.calls) == 4, len(fake.calls))
    check("p1 salvaged to a real verdict, not left bare UNRESOLVED",
          state.requirement_states["p1"].status == RequirementResolution.FAIL)
    check("p2 salvaged to INCONCLUSIVE", state.requirement_states["p2"].status == RequirementResolution.INCONCLUSIVE)


def test_max_steps_exhausted_with_no_usable_forced_response_still_produces_inconclusive_not_unresolved():
    """If the forced-conclusion turn itself also fails (e.g. the model
    can't produce valid JSON even under a final-turn prompt), properties
    still end up honestly INCONCLUSIVE -- never silently dropped back to
    bare UNRESOLVED."""
    garbage = ({"action": "nonsense"}, None)
    script = [({"action": "call_tool", "tool": "get_contract_source", "args": {"contract": "Vault"},
                "reasoning": "r"}, None)] * 3 + [garbage]
    kernel, fake = _kernel(script, max_steps=3, max_malformed_retries=0)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("p1 ends up INCONCLUSIVE, not UNRESOLVED",
          state.requirement_states["p1"].status == RequirementResolution.INCONCLUSIVE)
    check("reason records the forced-conclusion failure",
          "forced_conclusion" in (state.requirement_states["p1"].resolution_reason or ""),
          state.requirement_states["p1"].resolution_reason)


# --- conclude response missing a property_id --------------------------------

def test_conclude_missing_a_property_id_marks_only_that_one_unresolved():
    script = [({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
        # p2 is missing entirely.
    ]}, None)]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("p1 resolved normally", state.requirement_states["p1"].status == RequirementResolution.PASS)
    check("p2 left UNRESOLVED", state.requirement_states["p2"].status == RequirementResolution.UNRESOLVED)
    check("p2 has the specific missing-id reason",
          state.requirement_states["p2"].resolution_reason == "conclude_response_missing_this_property_id",
          state.requirement_states["p2"].resolution_reason)


def test_hallucinated_property_id_in_conclude_is_ignored_not_crashed():
    script = [({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
        {"property_id": "p999-does-not-exist", "verdict": "FAIL", "reasoning": "hallucinated"},
    ]}, None)]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("did not crash on hallucinated property_id", True)
    check("p1/p2 still resolved correctly",
          state.requirement_states["p1"].status == RequirementResolution.PASS and
          state.requirement_states["p2"].status == RequirementResolution.PASS)


# --- malformed model response: retry then give up ---------------------------

def test_malformed_response_exhaustion_attempts_forced_conclusion_salvage():
    """Real gap found live (2026-08-25 canto run, cluster_002): a run of
    JSON-shape mistakes used to go straight to bare UNRESOLVED with no
    salvage attempt at all. A forced-conclusion prompt is a materially
    simpler, more constrained ask than the general decide loop that just
    failed, so it often succeeds even when that loop didn't."""
    garbage = ({"action": "something_unrecognized", "whatever": True}, None)
    forced_conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "INCONCLUSIVE", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel([garbage, garbage, garbage, forced_conclude], max_malformed_retries=2)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("3 malformed attempts, plus one extra call for the forced-conclusion turn",
          len(fake.calls) == 4, len(fake.calls))
    check("p1 salvaged to a real verdict, not left bare UNRESOLVED",
          state.requirement_states["p1"].status == RequirementResolution.FAIL)
    check("p2 salvaged to INCONCLUSIVE", state.requirement_states["p2"].status == RequirementResolution.INCONCLUSIVE)
    check("a corrective retry message was appended during the malformed retries",
          any("did not match the required JSON shape" in str(m.get("content", "")) for m in fake.calls[2]),
          fake.calls[2])


def test_malformed_response_exhaustion_with_no_usable_forced_response_still_produces_inconclusive():
    garbage = ({"action": "something_unrecognized", "whatever": True}, None)
    kernel, fake = _kernel([garbage, garbage, garbage, garbage], max_malformed_retries=2)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("both properties end up INCONCLUSIVE, not UNRESOLVED", all(
        state.requirement_states[pid].status == RequirementResolution.INCONCLUSIVE for pid in _PROPERTY_IDS))
    check("reason records the forced-conclusion failure",
          "forced_conclusion" in (state.requirement_states["p1"].resolution_reason or ""),
          state.requirement_states["p1"].resolution_reason)


def test_malformed_response_recovers_on_retry():
    garbage = ({"action": "nonsense"}, None)
    good = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
    ]}, None)
    kernel, fake = _kernel([garbage, good], max_malformed_retries=2)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("recovered after one malformed turn", len(fake.calls) == 2, len(fake.calls))
    check("both properties resolved PASS after recovery", all(
        state.requirement_states[pid].status == RequirementResolution.PASS for pid in _PROPERTY_IDS))


# --- token/cost accounting ---------------------------------------------------

def test_token_usage_accumulates_across_turns():
    cr1 = ChatResult(content="", prompt_tokens=100, completion_tokens=20, cached=False, cost_usd=0.01)
    cr2 = ChatResult(content="", prompt_tokens=150, completion_tokens=30, cached=True, cost_usd=None)
    script = [
        ({"action": "call_tool", "tool": "get_contract_source", "args": {"contract": "Vault"}, "reasoning": "r"}, cr1),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
        ]}, cr2),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("input_tokens summed", state.token_usage.input_tokens == 250, state.token_usage)
    check("output_tokens summed", state.token_usage.output_tokens == 50, state.token_usage)
    check("cached_input_tokens only counts the cached turn", state.token_usage.cached_input_tokens == 150,
          state.token_usage)
    check("cost_usd summed (None contributes 0)", abs(state.token_usage.cost_usd - 0.01) < 1e-9,
          state.token_usage.cost_usd)


# --- root cause 2: update_investigation citing unknown evidence ids --------

def test_update_investigation_with_unknown_evidence_id_is_rejected_not_crashed():
    """Real live crash (2026-08-17 forte run,
    cluster_invocation_crashed:UnknownEvidenceIdError, 42/147 properties):
    a hypothesis's supporting_evidence_ids referenced an id that was
    never declared via a conclude action's own evidence list --
    upsert_hypothesis -> add_hypothesis's _require_evidence raised
    uncaught. Before the fix this test's kernel.run_cluster call itself
    raised UnknownEvidenceIdError; after the fix it's a normal rejected
    update, and the loop continues to a real conclusion."""
    script = [
        ({"action": "update_investigation", "hypotheses": [{
            "id": "hyp-1", "claim": "x", "originating_property_ids": ["p1"],
            "status": "OPEN", "supporting_evidence_ids": ["ev-never-declared"],
        }], "counterexample_attempts": []}, None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("did not crash with UnknownEvidenceIdError", True)
    check("hypothesis with the bad reference was NOT recorded", "hyp-1" not in state.hypotheses, state.hypotheses)
    check("a corrective rejection message was sent",
          any("unknown evidence ids" in str(m.get("content", "")) for m in fake.calls[-1]), fake.calls[-1])
    check("loop continued to a real conclusion afterward", all(
        state.requirement_states[pid].status == RequirementResolution.PASS for pid in _PROPERTY_IDS))


def test_update_investigation_with_known_evidence_id_still_works():
    """Regression guard for the fix above, at the unit level (avoids
    ScriptedChatClient's own conclude auto-fill defaults, which are
    tuned for the happy-path tests elsewhere and would obscure this
    specific check): a hypothesis referencing evidence that WAS already
    established must still be accepted normally, not rejected."""
    from rtf.security_agent.kernel import HypothesisInput, SecurityAgentKernel as K, UpdateInvestigationAction
    from rtf.security_agent.state import ClusterInvestigationState, Evidence

    state = ClusterInvestigationState.initial("c1", _PROPERTY_IDS)
    state.add_evidence(Evidence(id="ev-1", claim="fact", source_file="Vault.sol"))
    update = UpdateInvestigationAction(action="update_investigation", hypotheses=[
        HypothesisInput(id="hyp-1", claim="x", originating_property_ids=["p1"],
                        status="SUPPORTED", supporting_evidence_ids=["ev-1"]),
    ])
    error = K._apply_investigation_update(state, update)
    check("no rejection error for a known evidence id", error is None, error)
    check("hypothesis referencing already-known evidence was accepted", "hyp-1" in state.hypotheses, state.hypotheses)


# --- root cause 3 (defense in depth): any unexpected exception during ------
# --- action application is retried, then gives up gracefully --------------

class _ExplodingTools:
    """A tools stub whose call() raises an arbitrary exception a fixed
    number of times before succeeding -- simulates an unanticipated bug
    in action-application code that isn't specifically validated against
    (unlike root cause 2 above), the general backstop this fix adds."""

    def __init__(self, exceptions: list[Exception]):
        self._exceptions = list(exceptions)
        self.calls = 0

    def call(self, tool, args):
        self.calls += 1
        if self._exceptions:
            raise self._exceptions.pop(0)
        return {"status": "OK", "source": "ok"}


def test_unexpected_exception_during_tool_call_exhaustion_attempts_forced_conclusion_salvage():
    """Same salvage discipline as the malformed-response/budget-
    exhaustion paths: an internal error applying a PREVIOUS action says
    nothing about whether a forced-conclusion prompt (a fresh, unrelated
    decide() call) can succeed."""
    script = [({"action": "call_tool", "tool": "read_file", "args": {"path": "x"},
                "reasoning": "r"}, None)] * 3 + [
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "INCONCLUSIVE", "reasoning": "r2"},
        ]}, None),
    ]
    fake = ScriptedChatClient(script)
    mc = ModelClient(fake, RESPONSE_MODELS)
    exploding = _ExplodingTools([RuntimeError("boom"), RuntimeError("boom"), RuntimeError("boom")])
    kernel = SecurityAgentKernel(exploding, mc, enforce_completion=False, max_malformed_retries=2)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("gave up after max_malformed_retries+1 attempts, then one forced-conclusion call",
          exploding.calls == 3 and len(fake.calls) == 4, (exploding.calls, len(fake.calls)))
    check("did not crash the whole process", True)
    check("p1 salvaged to a real verdict, not left bare UNRESOLVED",
          state.requirement_states["p1"].status == RequirementResolution.FAIL)
    check("p2 salvaged to INCONCLUSIVE", state.requirement_states["p2"].status == RequirementResolution.INCONCLUSIVE)


def test_unexpected_exception_during_tool_call_recovers_on_retry():
    script = [
        ({"action": "call_tool", "tool": "read_file", "args": {"path": "x"}, "reasoning": "r"}, None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
        ]}, None),
    ]
    fake = ScriptedChatClient(script)
    mc = ModelClient(fake, RESPONSE_MODELS)
    exploding = _ExplodingTools([RuntimeError("boom")])
    kernel = SecurityAgentKernel(exploding, mc, enforce_completion=False)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("recovered and reached a real conclusion", all(
        state.requirement_states[pid].status == RequirementResolution.PASS for pid in _PROPERTY_IDS))


# --- an ERROR tool result (e.g. bad args) doesn't crash the loop -----------

def test_tool_error_result_does_not_crash_loop():
    script = [
        ({"action": "call_tool", "tool": "get_function_source", "args": {"contract": "Vault"},  # missing "function"
          "reasoning": "oops"}, None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "PASS", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("loop continued past a tool-call error", len(fake.calls) == 2, len(fake.calls))
    check("error tool result summarized, not crashed", "ERROR" in state.tool_history[0].result_summary,
          state.tool_history[0].result_summary)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
