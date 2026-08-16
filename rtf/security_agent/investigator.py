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
from rtf.security_agent.kernel import RESPONSE_MODELS, SecurityAgentKernel
from rtf.security_agent.model_client import ModelClient
from rtf.security_agent.state import ClusterInvestigationState
from rtf.security_agent.tools import SecurityAgentTools

_PROPERTY_HEADING = re.compile(r"^### `([^`]+)`\s*$", re.MULTILINE)
_PARENT_LINE = re.compile(r"\*\*Parent EthTrust obligation\*\*: `([^`]+)`")


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
) -> SecurityAgentResult:
    """Signature-compatible replacement for `run_arm_g_bundle`.

    Codex-specific arguments are intentionally accepted but unused. The
    adapter consumes the exact same context artifacts and project scope.
    """
    del codex_bin, python_bin, mcp_server_script, candidate_location, prompt
    started = time.monotonic()
    protocol, requirement_contexts, plan = _extract_context(extra_files)
    property_ids, parent_ids = _property_metadata_from_plan(plan)

    case_root = Path(scratch_root) / "security_agent" / case_id
    case_root.mkdir(parents=True, exist_ok=True)
    chat_factory = chat_client_factory or ChatClient
    chat = chat_factory(
        os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key, model, case_root / "cache", case_root / "tokens.jsonl", timeout=timeout_s,
    )
    build_tools = tools_factory or SecurityAgentTools.build
    compile_kwargs = None
    if not compile_via_foundry:
        compile_kwargs = {"solc": str(Path(solc_path_dir) / "solc")}
    tools = build_tools(
        repo_root=Path(repo_root), entry_file=Path(entry_file),
        compile_via_foundry=compile_via_foundry, solc_remaps=solc_remaps,
        extra_compile_kwargs=compile_kwargs,
    )
    kernel = SecurityAgentKernel(tools, ModelClient(chat, RESPONSE_MODELS))
    state = kernel.run_cluster(
        case_id, property_ids, protocol, requirement_contexts, plan,
        parent_requirement_ids=parent_ids,
    )
    state_path = case_root / "state.json"
    state_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    attempts = sum(len(req.counterexample_attempts) for req in state.requirement_states.values())
    return SecurityAgentResult(
        case_id=case_id,
        final_decision={"properties": state.to_property_verdict_entries()},
        cost_usd=state.token_usage.cost_usd,
        investigation_state=state,
        trajectory_path=str(state_path),
        wall_clock_s=time.monotonic() - started,
        input_tokens=state.token_usage.input_tokens,
        cached_input_tokens=state.token_usage.cached_input_tokens,
        output_tokens=state.token_usage.output_tokens,
        tool_calls=len(state.tool_history),
        files_inspected=len(state.inspected_files),
        hypotheses_generated=len(state.hypotheses),
        counterexamples_attempted=attempts,
    )
