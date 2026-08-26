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

from rtf.security_agent.evidence_store import EvidenceStore
from rtf.security_agent.kernel import ConcludeAction, RESPONSE_MODELS, SecurityAgentKernel
from rtf.security_agent.model_client import ModelClient
from rtf.security_agent.responses_client import NativeToolCall, ResponsesResult
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

class NativeCalls:
    """Script marker for a native multi-tool-call turn (native-tool-
    calling migration, 2026-08-26): `calls` is `[(tool, args), ...]`, all
    requested in ONE turn, mirroring what a real `ResponsesChatClient`
    returns when the model emits several sibling `function_call` items
    (Part 0, live-verified). Used as the first element of a script tuple
    in place of a plain action dict."""

    def __init__(self, calls: list[tuple[str, dict]]):
        self.calls = calls


class ScriptedChatClient:
    """Stands in for a4v.llm.ChatClient. ModelClient.decide() calls
    .complete() directly (not .complete_json()) so it can inspect
    content=None before extract_last_fenced_json ever sees it -- each
    script entry's raw_dict is JSON-serialized and fence-wrapped into a
    real ChatResult.content string, so the real extract_last_fenced_json
    parsing path is genuinely exercised, not bypassed. Records every
    `messages` list it was called with, so tests can assert on
    conversation growth (e.g. a corrective retry message got appended).

    A script entry's first element may also be a `NativeCalls` marker
    instead of a plain action dict -- returns a `ResponsesResult` with
    `tool_calls` populated (mirroring `ResponsesChatClient`) instead of a
    fenced-JSON `ChatResult`, exercising the SAME native-tool-calling
    branch `ModelClient.decide()` takes for a real client (via
    `getattr(chat_result, "tool_calls", None)`, not `isinstance`)."""

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
        if isinstance(raw, NativeCalls):
            tool_calls = [NativeToolCall(call_id=f"call_{i}", tool=tool, args=args)
                          for i, (tool, args) in enumerate(raw.calls)]
            if result is None:
                return ResponsesResult(content=None, prompt_tokens=0, completion_tokens=0,
                                       cached=False, cost_usd=None, tool_calls=tool_calls)
            return ResponsesResult(content=None, prompt_tokens=result.prompt_tokens,
                                   completion_tokens=result.completion_tokens, cached=result.cached,
                                   cost_usd=result.cost_usd, tool_calls=tool_calls)
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


def _kernel_with_evidence_store(script, **kwargs) -> tuple[SecurityAgentKernel, ScriptedChatClient]:
    """Same as `_kernel`, but with a REAL `EvidenceStore(tmp_path)`
    explicitly configured -- needed for dedup-replay tests, which must
    recover the original full result from durable storage, not from
    anything that only ever lived in the trimmed `recent_turns` window.
    None of `_kernel`'s existing callers pass an evidence_store today."""
    kwargs.setdefault("evidence_store", EvidenceStore(Path(tempfile.mkdtemp(prefix="security_agent_test_evidence_"))))
    return _kernel(script, **kwargs)


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


# --- native tool-calling: multiple tool calls resolved in ONE turn ---------

def test_native_multi_tool_call_turn_resolves_all_calls_in_one_decide_call():
    """The actual regression-proof of the efficiency claim behind this
    migration: one decide() call requesting several independent tool
    calls resolves ALL of them, not just one -- fewer expensive round-
    trips for the same investigation depth."""
    script = [
        (NativeCalls([
            ("get_contract_source", {"contract": "Vault"}),
            ("read_file", {"path": "x"}),
        ]), None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "PASS", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("only 2 model calls made (1 native multi-call turn + 1 conclude)",
          len(fake.calls) == 2, len(fake.calls))
    check("decide_calls_total tracks real round-trips, matching len(fake.calls)",
          state.decide_calls_total == 2, state.decide_calls_total)
    check("both tool calls recorded in shared tool_history",
          len(state.tool_history) == 2, state.tool_history)
    # step_count advances once per tool call (record_tool_call, x2 here) --
    # a SUCCESSFUL conclude does not itself increment step_count (existing
    # behavior, unrelated to this migration: only a rejected conclude,
    # an investigation update, or an action error does).
    check("step_count advanced by 2 for the native turn (once per call)",
          state.step_count == 2, state.step_count)
    check("p1 resolved FAIL", state.requirement_states["p1"].status == RequirementResolution.FAIL)
    check("p2 resolved PASS", state.requirement_states["p2"].status == RequirementResolution.PASS)


def test_native_turn_requesting_more_calls_than_remaining_max_steps_overshoots_then_stops():
    """Edge case decided in Part 3: a native turn can request more tool
    calls than remaining step budget. All requested calls execute anyway
    (truncating mid-turn would leave some function_call items without a
    matching function_call_output, an invalid next request) -- step_count
    overshoots within that one turn; the loop-top check only catches this
    on the NEXT iteration (which is the max_steps_exhausted salvage's own
    forced-conclusion decide() call, not a routine turn)."""
    script = [
        (NativeCalls([
            ("get_contract_source", {"contract": "Vault"}),
            ("read_file", {"path": "a"}),
            ("read_file", {"path": "b"}),
            ("read_file", {"path": "c"}),
            ("read_file", {"path": "d"}),
        ]), None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
        # FAIL for both (not PASS): `_apply_forced_conclusion` applies an
        # extra falsification-completeness check ONLY to PASS verdicts,
        # which this minimal scripted fixture (no update_investigation
        # step establishing hypotheses/counterexample attempts first)
        # would not satisfy -- orthogonal to what THIS test verifies
        # (the overshoot mechanic itself), so FAIL sidesteps it cleanly.
    ]
    kernel, fake = _kernel(script, max_steps=2)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("2 model calls made: the overshooting native turn, then the "
          "max_steps_exhausted forced-conclusion salvage",
          len(fake.calls) == 2, len(fake.calls))
    check("decide_calls_total counts the forced-conclusion salvage's own "
          "round-trip too, not just routine turns",
          state.decide_calls_total == 2, state.decide_calls_total)
    check("all 5 requested calls executed despite max_steps=2",
          len(state.tool_history) == 5, state.tool_history)
    check("step_count overshoots to 5 within the one turn", state.step_count == 5, state.step_count)
    check("forced-conclusion salvage still resolved both properties from the overshot state",
          state.requirement_states["p1"].status == RequirementResolution.FAIL)
    check("p2 resolved FAIL via salvage", state.requirement_states["p2"].status == RequirementResolution.FAIL)


# --- kernel-controlled cached-result replay (dedup) -------------------------

def test_native_same_turn_duplicate_executes_once_and_replays_the_cached_result():
    """Real bug found live (2026-08-26, native-tool-calling canto rerun):
    ~half a real cluster's step budget was spent re-investigating things
    already found. The kernel must catch an exact-duplicate call WITHIN
    the same native turn (not just across turns) and replay the ORIGINAL
    full result automatically -- not a pointer telling the model to go
    fetch it itself."""
    script = [
        (NativeCalls([
            ("get_contract_source", {"contract": "Vault"}),
            ("get_contract_source", {"contract": "Vault"}),
        ]), None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel_with_evidence_store(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("only 1 real tool_history record for 2 identical requests in one turn",
          len(state.tool_history) == 1, state.tool_history)
    check("exactly 1 dedup hit recorded", state.deduplicated_calls_total == 1, state.deduplicated_calls_total)
    check("step_count only advances once (the duplicate contributes zero new depth)",
          state.step_count == 1, state.step_count)
    # The 2nd native tool_calls entry's rendered content must contain the
    # REPLAYED original result, not a bare pointer telling the model to
    # go call read_evidence() itself.
    native_turn_messages = fake.calls[0]
    tool_call_group = fake.calls[1]  # messages passed to the model's 2nd decide() call
    replay_entries = [m for m in tool_call_group if m.get("role") == "tool" and "CACHED" in m.get("content", "")]
    check("the deduplicated call's response is a CACHED replay, present in the next turn's messages",
          len(replay_entries) == 1, tool_call_group)
    check("the replay contains the ORIGINAL evidence_id, not just a pointer telling the model to fetch it",
          "evidence_id=tool-1" in replay_entries[0]["content"], replay_entries[0]["content"])
    check("the replay contains real content (source), not just a summary label",
          "Vault" in replay_entries[0]["content"], replay_entries[0]["content"])


def test_later_turn_duplicate_is_replayed_without_a_second_real_execution():
    script = [
        (NativeCalls([("get_contract_source", {"contract": "Vault"})]), None),
        (NativeCalls([("get_function_source", {"contract": "Vault", "function": "withdraw"})]), None),
        (NativeCalls([("get_contract_source", {"contract": "Vault"})]), None),  # duplicate of turn 1
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel_with_evidence_store(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("only 2 real tool_history records (get_contract_source once, get_function_source once)",
          len(state.tool_history) == 2, state.tool_history)
    check("1 dedup hit recorded for the later, separate-turn duplicate",
          state.deduplicated_calls_total == 1, state.deduplicated_calls_total)
    # fake.calls[N] is the messages the model receives when deciding
    # turn N -- so turn 2's dedup replay (the response to turn 2's own
    # request) only appears in the messages for turn 3 (the conclude
    # call), i.e. fake.calls[3], not fake.calls[2].
    messages_after_turn_2 = fake.calls[3]
    replay_entries = [m for m in messages_after_turn_2 if m.get("role") == "tool" and "CACHED" in m.get("content", "")]
    check("turn 2's request was answered from cache, no read_evidence call needed by the model",
          len(replay_entries) == 1, messages_after_turn_2)


def test_legacy_single_tool_call_path_also_dedups_and_replays():
    duplicate_call = {"action": "call_tool", "tool": "get_contract_source",
                      "args": {"contract": "Vault"}, "reasoning": "r"}
    script = [
        (dict(duplicate_call), None),
        (dict(duplicate_call), None),  # exact duplicate, legacy (non-native) path
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel_with_evidence_store(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("only 1 real tool_history record via the legacy path", len(state.tool_history) == 1, state.tool_history)
    check("1 dedup hit recorded", state.deduplicated_calls_total == 1, state.deduplicated_calls_total)
    check("step_count only advances once", state.step_count == 1, state.step_count)
    # fake.calls[2] is the messages for the 3rd decide() call (the
    # conclude), which is what reflects turn 1's (the duplicate's) own
    # replayed result -- turn 0's real result shows up one call earlier.
    messages_after_turn_1 = fake.calls[2]
    check("legacy path's replay also carries CACHED content, role=user (matching this path's own convention)",
          any(m.get("role") == "user" and "CACHED" in m.get("content", "") for m in messages_after_turn_1),
          messages_after_turn_1)


def test_different_args_are_not_deduped():
    """Real regression guard: this is the exact case that must keep
    working unchanged."""
    script = [
        (NativeCalls([
            ("get_function_source", {"contract": "Vault", "function": "withdraw"}),
            ("get_function_source", {"contract": "Vault", "function": "deposit"}),
        ]), None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel_with_evidence_store(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("both distinct calls executed for real", len(state.tool_history) == 2, state.tool_history)
    check("no dedup hits", state.deduplicated_calls_total == 0, state.deduplicated_calls_total)


def test_read_evidence_itself_is_never_deduplicated():
    """read_evidence is excluded from dedup detection entirely: it's
    already a cheap disk read, and its own calls are never persisted to
    EvidenceStore in the first place (nothing to replay it FROM)."""
    script = [
        (NativeCalls([("get_contract_source", {"contract": "Vault"})]), None),
        (NativeCalls([("read_evidence", {"evidence_id": "tool-1"}),
                      ("read_evidence", {"evidence_id": "tool-1"})]), None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel_with_evidence_store(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("both identical read_evidence calls executed for real (excluded from dedup)",
          len(state.tool_history) == 3, state.tool_history)  # 1 get_contract_source + 2 read_evidence
    check("no dedup hits (read_evidence is never deduplicated)",
          state.deduplicated_calls_total == 0, state.deduplicated_calls_total)


def test_dedup_falls_back_to_summary_only_replay_when_no_evidence_store_configured():
    """The degraded-but-still-correct path: without an EvidenceStore,
    there is nowhere to recover the full original result from -- the
    kernel still avoids re-executing the real tool, but the replay is
    limited to the terse summary already on the ToolCallRecord."""
    script = [
        (NativeCalls([
            ("get_contract_source", {"contract": "Vault"}),
            ("get_contract_source", {"contract": "Vault"}),
        ]), None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)  # NO evidence_store
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("still only 1 real execution even without an evidence store",
          len(state.tool_history) == 1, state.tool_history)
    check("still 1 dedup hit", state.deduplicated_calls_total == 1, state.deduplicated_calls_total)
    turn_2 = fake.calls[1]
    replay_entries = [m for m in turn_2 if m.get("role") == "tool" and "CACHED" in m.get("content", "")]
    check("degraded replay still marked CACHED, notes no store configured",
          len(replay_entries) == 1 and "no evidence store configured" in replay_entries[0]["content"],
          replay_entries)


def test_concludeaction_and_updateinvestigationaction_unaffected_by_dedup():
    """Dedup only applies to tool-call dispatch -- no interaction with
    the other two action branches."""
    script = [
        ({"action": "update_investigation", "hypotheses": [{
            "id": "hyp-1", "claim": "x", "originating_property_ids": ["p1"], "status": "OPEN",
        }], "counterexample_attempts": []}, None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel_with_evidence_store(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("no dedup activity for non-tool-call actions", state.deduplicated_calls_total == 0)
    check("hypothesis still recorded normally", "hyp-1" in state.hypotheses)
    check("conclude still resolved both properties",
          state.requirement_states["p1"].status == RequirementResolution.FAIL and
          state.requirement_states["p2"].status == RequirementResolution.FAIL)


def test_compaction_regression_dedup_replay_survives_the_original_falling_out_of_recent_turns():
    """The actual bug class, not just the cache helper in isolation:
    force real compaction to run (context_manager.should_compact must be
    monkeypatched as a FUNCTION -- SOFT_COMPACTION_TOKENS is already
    bound into should_compact's own default argument at import time, so
    patching that module constant afterward silently does nothing),
    push the original result's turn out of the RECENT_TURNS_KEPT window,
    then re-request it -- the kernel must still recover it from durable
    state (EvidenceStore), not from anything that only lived in the
    trimmed raw turns."""
    from rtf.security_agent import context_manager
    original_should_compact = context_manager.should_compact
    context_manager.should_compact = lambda messages, threshold=None: True
    try:
        num_fillers = context_manager.RECENT_TURNS_KEPT + 2
        script = (
            [(NativeCalls([("get_contract_source", {"contract": "Vault"})]), None)]
            # Distinct filler calls (different function per turn) -- must
            # NOT collide with each other via dedup, only the deliberate
            # final re-request of get_contract_source should ever hit.
            + [(NativeCalls([("get_callers", {"contract": "Vault", "function": f"filler{i}"})]), None)
               for i in range(num_fillers)]
            + [(NativeCalls([("get_contract_source", {"contract": "Vault"})]), None)]  # re-request, now compacted away
            + [({"action": "conclude", "properties": [
                {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
                {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
            ]}, None)]
        )
        kernel, fake = _kernel_with_evidence_store(script)
        state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

        check(f"{1 + num_fillers} distinct real executions total (1 get_contract_source + {num_fillers} fillers)",
              len(state.tool_history) == 1 + num_fillers, state.tool_history)
        check("the re-request after compaction was a dedup hit, not a real re-execution",
              state.deduplicated_calls_total == 1, state.deduplicated_calls_total)
        # By the LAST decide() call (the conclude), should_compact having
        # been forced True on every turn means turn 0's own "assistant"
        # tool_calls entry (naming get_contract_source) is genuinely gone
        # from what the model sees -- proving the dedup hit a few turns
        # earlier was resolved from EvidenceStore, not from a raw turn
        # that just happened to still be present in a short window.
        final_messages = fake.calls[-1]
        # The re-request turn's OWN echo entry is always present
        # (kernel.py always echoes what the model asked, dedup or not) --
        # what must be GONE is turn 0's separate, original echo entry.
        # If both survived, this count would be 2, not 1.
        get_contract_source_echo_count = sum(
            1 for m in final_messages
            if m.get("role") == "assistant" and m.get("tool_calls")
            and any(c.get("tool") == "get_contract_source" for c in m["tool_calls"])
        )
        check("only the re-request's OWN echo entry remains -- turn 0's original echo entry is "
              "genuinely gone by the final turn (compacted away for real, not just theoretically)",
              get_contract_source_echo_count == 1, final_messages)
        check("a CACHED replay entry is present somewhere across the whole run",
              any("CACHED" in m.get("content", "") for call_messages in fake.calls for m in call_messages),
              "no CACHED entry found anywhere")
        check("the model reached a real conclusion afterward despite the compaction + dedup replay",
              state.requirement_states["p1"].status == RequirementResolution.FAIL)
    finally:
        context_manager.should_compact = original_should_compact


def test_stagnation_safety_repeated_dedup_hits_still_trigger_no_progress_breaker():
    """A model stuck requesting only already-cached calls must not loop
    forever: step_count freezes (dedup hits don't advance it), but
    progress_fingerprint()'s distinct_tool_calls signal already doesn't
    grow for a repeated call (confirmed unchanged, pre-existing
    behavior) -- so the existing no_progress circuit breaker must still
    fire within max_consecutive_no_progress turns, exactly as it does
    for a model stuck on real repeated NOT_FOUNDs today."""
    same_call = NativeCalls([("get_contract_source", {"contract": "Vault"})])
    forced_conclude = ({"action": "conclude", "properties": [
        {"property_id": "p1", "verdict": "INCONCLUSIVE", "reasoning": "r1"},
        {"property_id": "p2", "verdict": "INCONCLUSIVE", "reasoning": "r2"},
    ]}, None)
    # 1st is real (new signature); 2nd+ are dedup hits (identical
    # signature each time) -- with max_consecutive_no_progress=2, the
    # breaker must fire well before the script runs out.
    script = [(same_call, None)] * 5 + [forced_conclude]
    kernel, fake = _kernel_with_evidence_store(script, max_consecutive_no_progress=2)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)

    check("only 1 real execution ever, no matter how many times it was requested",
          len(state.tool_history) == 1, state.tool_history)
    check("step_count stayed frozen at 1 (dedup hits never advance it)", state.step_count == 1, state.step_count)
    check("the no-progress breaker fired well before all 5 repeats were scripted "
          "(fewer real model calls than the full script length)",
          len(fake.calls) < 6, len(fake.calls))
    check("both properties salvaged via the no-progress forced-conclusion path",
          state.requirement_states["p1"].status == RequirementResolution.INCONCLUSIVE and
          state.requirement_states["p2"].status == RequirementResolution.INCONCLUSIVE)


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


# --- unresolved_questions/next_actions (closing a dead-field gap) -----------

def test_update_investigation_with_only_unresolved_questions_is_valid():
    """Real gap found live (2026-08-26): unresolved_questions/
    next_actions already existed on state but nothing could ever write
    to them -- the schema validator used to reject an update containing
    ONLY these fields (no hypotheses/counterexample_attempts)."""
    script = [
        ({"action": "update_investigation", "unresolved_questions": ["does the oracle ever return 0?"]}, None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("update_investigation with only unresolved_questions was accepted, not rejected as malformed",
          len(fake.calls) == 2, len(fake.calls))
    check("unresolved_questions actually recorded on state",
          state.unresolved_questions == ["does the oracle ever return 0?"], state.unresolved_questions)


def test_update_investigation_with_only_next_actions_is_valid():
    script = [
        ({"action": "update_investigation", "next_actions": ["check Ln.sol's rounding path"]}, None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("next_actions actually recorded on state",
          state.next_actions == ["check Ln.sol's rounding path"], state.next_actions)


def test_later_update_omitting_the_fields_does_not_clear_previously_recorded_ones():
    """Replacement semantics only apply when THIS update actually
    provides a new list -- an update that only touches hypotheses must
    not silently wipe out unresolved_questions/next_actions recorded in
    an earlier turn."""
    script = [
        ({"action": "update_investigation", "unresolved_questions": ["q1"], "next_actions": ["a1"]}, None),
        ({"action": "update_investigation", "hypotheses": [{
            "id": "hyp-1", "claim": "x", "originating_property_ids": ["p1"], "status": "OPEN",
        }], "counterexample_attempts": []}, None),  # omits both fields entirely
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    check("unresolved_questions from turn 1 survives a turn 2 update that didn't mention it",
          state.unresolved_questions == ["q1"], state.unresolved_questions)
    check("next_actions from turn 1 survives a turn 2 update that didn't mention it",
          state.next_actions == ["a1"], state.next_actions)


def test_render_state_summary_reflects_unresolved_questions_and_next_actions():
    from rtf.security_agent import context_manager as cm
    script = [
        ({"action": "update_investigation", "unresolved_questions": ["does X happen?"],
          "next_actions": ["check Y"]}, None),
        ({"action": "conclude", "properties": [
            {"property_id": "p1", "verdict": "FAIL", "reasoning": "r1"},
            {"property_id": "p2", "verdict": "FAIL", "reasoning": "r2"},
        ]}, None),
    ]
    kernel, fake = _kernel(script)
    state = kernel.run_cluster("c1", _PROPERTY_IDS, *_CONTEXT)
    summary = cm.render_state_summary(state)
    check("unresolved question appears in the rendered state summary", "does X happen?" in summary, summary)
    check("next action appears in the rendered state summary", "check Y" in summary, summary)


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
    # 3 DISTINCT calls (not the same one 3x): the kernel now replays an
    # exact-duplicate call from cache instead of re-executing it, so 3
    # identical calls would only advance step_count once.
    script = [({"action": "call_tool", "tool": "get_contract_source", "args": {"contract": f"Vault{i}"},
                "reasoning": "r"}, None) for i in range(3)] + [
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
    # 3 DISTINCT tool calls (not the same one 3x): the kernel now
    # replays an exact-duplicate call from cache instead of re-executing
    # it, so 3 identical calls would only advance step_count once,
    # never exhausting max_steps=3 the way this test needs.
    script = [({"action": "call_tool", "tool": "get_contract_source", "args": {"contract": f"Vault{i}"},
                "reasoning": "r"}, None) for i in range(3)] + [garbage]
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
          any("did not match a required shape" in str(m.get("content", "")) for m in fake.calls[2]),
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
