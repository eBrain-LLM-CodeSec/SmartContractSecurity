"""Drop-in adapter from RTF's existing bundle-investigator seam to the
custom security-agent kernel."""
from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from a4v.llm import ChatClient
from rtf.security_agent.evidence_store import EvidenceStore
from rtf.security_agent.kernel import NATIVE_RESPONSE_MODELS, RESPONSE_MODELS, SecurityAgentKernel
from rtf.security_agent.model_client import DEFAULT_MAX_COMPLETION_TOKENS, ModelClient
from rtf.security_agent.responses_client import ResponsesChatClient
from rtf.security_agent.state import ClusterInvestigationState
from rtf.security_agent.tools import SecurityAgentTools, build_tool_schemas
from rtf.security_agent.trajectory import TrajectoryWriter

_PROPERTY_HEADING = re.compile(r"^### `([^`]+)`\s*$", re.MULTILINE)
_PARENT_LINE = re.compile(r"\*\*Parent EthTrust obligation\*\*: `([^`]+)`")

# RTF_SECURITY_AGENT_EFFICIENCY_INVESTIGATION_20260817.md section 2.2: "the
# other 18 clusters mostly resolved (concluded or exhausted) in under 15
# minutes each" -- a healthy cluster's own natural ceiling, well below the
# 4 pathological clusters that separately consumed 536 cumulative minutes.
# Circuit-breaker default for live runs, not a claim this is final --
# Part 10's own instrumentation is the real basis for retuning it later.
DEFAULT_MAX_CLUSTER_WALL_CLOCK_S = 900.0

# rtf.security_agent.state.RequirementResolution (PASS/FAIL/NOT_APPLICABLE/
# UNRESOLVED, taken literally from the kernel's own task brief) does not
# line up with the pre-existing pipeline's rtf.l12_evaluation.metrics.
# ConformanceState (PASS/FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE) --
# confirmed live (2026-08-17 forte run, 15/147 properties): cluster_
# response_validation.py's _DECISION_TO_CONFORMANCE only recognizes the
# latter four literal strings; NOT_APPLICABLE/UNRESOLVED fell through as
# "unknown_verdict:X" and were force-downgraded to INCONCLUSIVE anyway,
# just with the WRONG reason recorded and no chance for the legacy
# harness's own PASS-sufficiency checks to even run. Translated here,
# isolated to this adapter -- cluster_response_validation.py (shared with
# the real Codex path) is untouched. NOT_APPLICABLE has no real analog in
# ConformanceState; INSUFFICIENT_EVIDENCE ("not enough of a signal for a
# real PASS/FAIL") is the closer of the two non-terminal states. UNRESOLVED
# (the kernel's own "gave up, reason recorded" state) maps cleanly onto
# INCONCLUSIVE -- the same concept under a different name.
_VERDICT_FOR_LEGACY_HARNESS = {"NOT_APPLICABLE": "INSUFFICIENT_EVIDENCE", "UNRESOLVED": "INCONCLUSIVE"}


def _property_entries_for_legacy_harness(state: ClusterInvestigationState) -> list[dict]:
    entries = []
    for entry in state.to_property_verdict_entries():
        entry = dict(entry)
        entry["verdict"] = _VERDICT_FOR_LEGACY_HARNESS.get(entry["verdict"], entry["verdict"])
        entries.append(entry)
    return entries


@dataclass
class SecurityAgentResult:
    case_id: str
    final_decision: dict | None
    cost_usd: float
    investigation_state: ClusterInvestigationState
    trajectory_path: str
    wall_clock_s: float
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    tool_calls: int
    files_inspected: int
    hypotheses_generated: int
    counterexamples_attempted: int
    decide_calls_total: int
    """Real model round-trips, distinct from `tool_calls` (native-tool-
    calling migration, Part 8): a single decide() call can now resolve
    several tool calls at once, so `tool_calls / decide_calls_total`
    directly measures the migration's efficiency claim ("same
    investigation depth, fewer round-trips") on a real run."""
    deduplicated_calls_total: int
    """Exact-duplicate tool calls the kernel caught and replayed from
    cache instead of re-executing (see ClusterInvestigationState's own
    field docstring). tool_calls (already on this dataclass) is real
    unique executions; tool_calls + deduplicated_calls_total is the
    total the model actually requested."""


def _extract_context(extra_files: dict[str, str]) -> tuple[str, dict[str, str], str]:
    protocol = extra_files.get(".rtf/context/protocol_context.md", "")
    requirements = {
        Path(path).stem: content for path, content in extra_files.items()
        if path.startswith(".rtf/context/requirements/") and path.endswith(".md")
    }
    plans = [content for path, content in extra_files.items()
             if path.startswith(".rtf/plans/") and path.endswith(".md")]
    if len(plans) != 1:
        raise ValueError(f"expected exactly one cluster plan in extra_files, found {len(plans)}")
    return protocol, requirements, plans[0]


def _property_metadata_from_plan(plan: str) -> tuple[list[str], dict[str, str | None]]:
    matches = list(_PROPERTY_HEADING.finditer(plan))
    if not matches:
        raise ValueError("cluster plan contains no property headings")
    property_ids = [match.group(1) for match in matches]
    parents: dict[str, str | None] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(plan)
        parent = _PARENT_LINE.search(plan[match.end():end])
        parents[match.group(1)] = parent.group(1) if parent else None
    return property_ids, parents


def run_security_agent_bundle(
    *, codex_bin, python_bin, mcp_server_script, api_key: str, model: str,
    case_id: str, entry_file: Path, repo_root: Path, candidate_location: str,
    solc_path_dir: str, solc_remaps: list[str] | None, prompt: str,
    scratch_root: Path, timeout_s: int, extra_files: dict[str, str],
    compile_via_foundry: bool,
    chat_client_factory: Callable[..., ChatClient] | None = None,
    tools_factory: Callable[..., SecurityAgentTools] | None = None,
    max_completion_tokens: int = DEFAULT_MAX_COMPLETION_TOKENS,
    reasoning_effort: str = "low",
    max_steps: int | None = None,
    max_cost_usd: float | None = None,
) -> SecurityAgentResult:
    """Signature-compatible replacement for `run_arm_g_bundle`.

    Codex-specific arguments are intentionally accepted but unused. The
    adapter consumes the exact same context artifacts and project scope.

    Defaults to `ResponsesChatClient` (the OpenAI Responses API wire
    format, `POST {base_url}/responses`) rather than `a4v.llm.ChatClient`
    (`POST {base_url}/chat/completions`) -- the SAME wire format the real
    Codex investigator already uses successfully against this project's
    models (`arm_c_codex.py`'s `DEFAULT_WIRE_API = "responses"`).

    Real root cause this fixes (found live, 2026-08-17): z-ai/glm-5.2 is
    a reasoning model that can exhaust its ENTIRE completion budget on
    internal reasoning tokens without ever emitting a visible answer
    (confirmed via `chat_client_factory=ChatClient`'s
    `Chat Completions` path, multiple times, on real forte clusters) --
    `max_tokens`/`max_output_tokens` caps reasoning+output COMBINED in
    both wire formats (confirmed against OpenAI's own docs), so switching
    wire format alone does not fix this. The actual fix is
    `reasoning.effort`, a Responses-API-only control absent from Chat
    Completions entirely -- explicitly bounding how much the model
    reasons before answering, rather than gambling on token-count math.
    `chat_client_factory` remains overridable (tests, or a future
    `ChatClient`-based comparison) -- this default is what real live runs
    should use.

    `max_steps`/`max_cost_usd` (added 2026-08-26, native-tool-calling
    canto rerun): both None by default, which reproduces prior behavior
    exactly (kernel.py's own DEFAULT_MAX_STEPS=15, no per-cluster cost
    ceiling at all). Real gap found live: `SecurityAgentKernel.max_steps`
    was tuned under the OLD one-tool-call-per-turn design and was never
    re-checked once a single turn could resolve several tool calls at
    once -- 3 for 3 real clusters hit it before reaching a conclusion,
    landing every property INCONCLUSIVE. Exposed here so a caller can
    raise/remove it for an experiment without changing the tool's global
    default for every other caller. `max_cost_usd` is offered alongside
    it deliberately: removing the step count as the binding constraint
    removes the only per-cluster safety net that existed before this
    change (the only other bound, `max_wall_clock_s`, is real wall time,
    not spend) -- a caller that raises max_steps should almost always
    also set a per-cluster cost ceiling as a replacement guardrail.
    """
    del codex_bin, python_bin, mcp_server_script, candidate_location, prompt
    started = time.monotonic()
    protocol, requirement_contexts, plan = _extract_context(extra_files)
    property_ids, parent_ids = _property_metadata_from_plan(plan)

    case_root = Path(scratch_root) / "security_agent" / case_id
    case_root.mkdir(parents=True, exist_ok=True)
    if chat_client_factory is not None:
        chat = chat_client_factory(
            os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key, model, case_root / "cache", case_root / "tokens.jsonl", timeout=timeout_s,
        )
    else:
        chat = ResponsesChatClient(
            os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key, model, case_root / "cache", case_root / "tokens.jsonl", timeout=timeout_s,
            reasoning_effort=reasoning_effort,
            # NO response_schema/text.format here -- real bug found live
            # (2026-08-26, native-tool-calling smoke test): with `tools`
            # AND `text.format` BOTH set, z-ai/glm-5.2 ALWAYS answers in
            # the schema-conformant JSON text shape and never emits a
            # native tool call, even for a prompt that unambiguously
            # needs one -- confirmed via a direct side-by-side live test
            # (identical prompt/tools, only `text` present/absent
            # differs: absent -> correct function_call; present ->
            # schema-conformant text every time). This is exactly the
            # contingency Part 0/Part 5 anticipated ("if tools+text.format
            # don't coexist cleanly, drop text.format") -- Part 0's own
            # Test 4 didn't catch it because it only checked the
            # "model told NOT to call a tool" case, not the steady-state
            # "model should call a tool" case this run's 8-turn,
            # zero-tool-call trajectory exposed. `ModelClient`'s existing
            # post-hoc Pydantic validation against NATIVE_RESPONSE_MODELS
            # (2 remaining text shapes) is relied on instead, same as
            # before structured output was ever added.
            session_id=case_id,
            tools=build_tool_schemas(), tool_choice="auto", parallel_tool_calls=True,
        )
    evidence_store = EvidenceStore(case_root)
    build_tools = tools_factory or SecurityAgentTools.build
    compile_kwargs = None
    if not compile_via_foundry:
        compile_kwargs = {"solc": str(Path(solc_path_dir) / "solc")}
    tools = build_tools(
        repo_root=Path(repo_root), entry_file=Path(entry_file),
        compile_via_foundry=compile_via_foundry, solc_remaps=solc_remaps,
        extra_compile_kwargs=compile_kwargs, evidence_store=evidence_store,
    )
    trajectory_path = case_root / "trajectory.jsonl"
    # RESPONSE_MODELS (all 3 shapes, including ToolCallAction) only makes
    # sense for a non-native `chat_client_factory` override -- the live
    # default path above always wires native tool-calling, where a tool
    # call is `ModelTurn.tool_calls`, not a JSON-text shape, so only the
    # 2 remaining action shapes are ever valid text responses.
    response_models = RESPONSE_MODELS if chat_client_factory is not None else NATIVE_RESPONSE_MODELS
    model_client = ModelClient(chat, response_models, max_tokens=max_completion_tokens)
    kernel_overrides = {}
    if max_steps is not None:
        kernel_overrides["max_steps"] = max_steps
    if max_cost_usd is not None:
        kernel_overrides["max_cost_usd"] = max_cost_usd
    kernel = SecurityAgentKernel(
        tools, model_client, event_sink=TrajectoryWriter(trajectory_path),
        evidence_store=evidence_store, max_wall_clock_s=DEFAULT_MAX_CLUSTER_WALL_CLOCK_S,
        **kernel_overrides,
    )
    state = kernel.run_cluster(
        case_id, property_ids, protocol, requirement_contexts, plan,
        parent_requirement_ids=parent_ids,
    )
    state_path = case_root / "state.json"
    state_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    attempts = sum(len(req.counterexample_attempts) for req in state.requirement_states.values())
    return SecurityAgentResult(
        case_id=case_id,
        final_decision={"properties": _property_entries_for_legacy_harness(state)},
        cost_usd=state.token_usage.cost_usd,
        investigation_state=state,
        trajectory_path=str(trajectory_path),
        wall_clock_s=time.monotonic() - started,
        input_tokens=state.token_usage.input_tokens,
        cached_input_tokens=state.token_usage.cached_input_tokens,
        output_tokens=state.token_usage.output_tokens,
        tool_calls=len(state.tool_history),
        files_inspected=len(state.inspected_files),
        hypotheses_generated=len(state.hypotheses),
        counterexamples_attempted=attempts,
        decide_calls_total=state.decide_calls_total,
        deduplicated_calls_total=state.deduplicated_calls_total,
    )
