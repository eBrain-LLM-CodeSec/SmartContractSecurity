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
    """Stands in for a4v.llm.ChatClient: complete_json(messages, ...)
    returns the next (raw_dict, ChatResult|None) pair from a pre-scripted
    list, in order. Records every `messages` list it was called with, so
    tests can assert on conversation growth (e.g. a corrective retry
    message got appended)."""

    def __init__(self, script: list[tuple[dict, "ChatResult | None"]]):
        self._script = list(script)
        self.calls: list[list[dict]] = []

    def complete_json(self, messages, temperature: float = 0.0, **kwargs):
        self.calls.append([dict(m) for m in messages])
        if len(self.calls) > len(self._script):
            raise AssertionError(f"kernel made more model calls ({len(self.calls)}) than scripted ({len(self._script)})")
        raw, result = self._script[len(self.calls) - 1]
        # Keep Increment-2 scenario fixtures concise while exercising the
        # stricter Increment-3 production schema. Tests specifically about
        # CEIV behavior below provide the full shape themselves.
        if raw.get("action") == "conclude" and "evidence" not in raw:
            raw = dict(raw)
            raw["evidence"] = [{
                "id": "ev-shared", "claim": "inspected fixture evidence",
                "source_file": "Vault.sol", "source_contract": "Vault",
                "source_function": "withdraw", "source_lines": "30-42",
                "tool_call_id": "tool-1", "raw_excerpt": None,
            }]
            raw["properties"] = [dict(
                p,
                claim=p.get("reasoning", "property claim"),
                evidence_ids=["ev-shared"],
                interpretation=p.get("reasoning", "fixture interpretation"),
            ) for p in raw["properties"]]
            for prop in raw["properties"]:
                prop.pop("reasoning", None)
        return raw, result


def _model_client(script: list[tuple[dict, "ChatResult | None"]]) -> ModelClient:
    return ModelClient(ScriptedChatClient(script), RESPONSE_MODELS)


_PROPERTY_IDS = ["p1", "p2"]
_CONTEXT = ("protocol context text", {"req-1": "requirement context text"}, "cluster plan text")


def _kernel(script, **kwargs) -> tuple[SecurityAgentKernel, ScriptedChatClient]:
    fake = ScriptedChatClient(script)
    mc = ModelClient(fake, RESPONSE_MODELS)
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
            "properties": [{
                "property_id": "p1", "claim": "claim",
                "evidence_ids": ["ev-missing"],
                "interpretation": "interpretation", "verdict": "FAIL",
            }],
        })
        check("dangling evidence id rejected", False, "did not raise")
    except ValidationError:
        check("dangling evidence id rejected", True)


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

def test_max_steps_exhausted_marks_all_unresolved_with_reason():
    # Always returns a tool_call, never concludes -- forces exhaustion.
    script = [({"action": "call_tool", "tool": "get_contract_source", "args": {"contract": "Vault"},
                "reasoning": "r"}, None)] * 3
    kernel, fake = _kernel(script, max_steps=3)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("step_count reached max_steps", state.step_count == 3, state.step_count)
    check("p1 still UNRESOLVED", state.requirement_states["p1"].status == RequirementResolution.UNRESOLVED)
    check("p1 has an explicit reason (never silently dropped)",
          state.requirement_states["p1"].resolution_reason == "max_steps_exhausted",
          state.requirement_states["p1"].resolution_reason)
    check("p2 also has the reason", state.requirement_states["p2"].resolution_reason == "max_steps_exhausted")


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

def test_malformed_response_retries_then_gives_up_with_reason():
    garbage = ({"action": "something_unrecognized", "whatever": True}, None)
    kernel, fake = _kernel([garbage, garbage, garbage], max_malformed_retries=2)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("gave up after max_malformed_retries+1 attempts", len(fake.calls) == 3, len(fake.calls))
    check("both properties left UNRESOLVED", all(
        state.requirement_states[pid].status == RequirementResolution.UNRESOLVED for pid in _PROPERTY_IDS))
    check("reason records malformed-response exhaustion",
          state.requirement_states["p1"].resolution_reason == "kernel_malformed_response_exhausted")
    check("a corrective retry message was appended to the conversation",
          any("did not match the required JSON shape" in str(m.get("content", "")) for m in fake.calls[-1]),
          fake.calls[-1])


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
