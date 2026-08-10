"""Phase 8 of the grouped-investigation architecture: the
execution-oriented cluster-investigation prompt.

Distinct from the single-property `ARM_G_PROMPT_v3.md` (still used
unchanged for `G0_UNGROUPED` investigations) -- `ARM_G_CLUSTER_PROMPT_v1.md`
is minimal by design: it does not restate the requirement text, protocol
architecture, or candidate locations inline. Instead it tells Codex to
READ the three real Markdown artifacts Phase 7 already generated
(protocol context, requirement context, cluster plan), matching the
plan's own instruction: "Codex should not have to reconstruct basic
architecture or EthTrust meaning every time."

This module builds the CONCRETE prompt string for one cluster
investigation (frozen contract text + this cluster's specific file
paths) -- it does not itself invoke Codex; wiring this into the live
escalation loop (replacing per-instance calls with per-cluster calls
when a non-G0 policy is active) is deliberately deferred to when the
ablation study (Phase 14) needs it, not blocking Phases 9-13's synthetic
validation work.
"""
from __future__ import annotations

from pathlib import Path

CLUSTER_PROMPT_PATH = Path(__file__).resolve().parents[1] / "l8_llm_judgment_layer" / "bundle_agent_experiment" / "ARM_G_CLUSTER_PROMPT_v1.md"


def load_frozen_cluster_prompt() -> str:
    text = CLUSTER_PROMPT_PATH.read_text(encoding="utf-8")
    marker = "## ROLE"
    return text[text.index(marker):]


def build_cluster_investigation_prompt(
    protocol_context_path: str,
    requirement_context_paths: list[str],
    cluster_plan_path: str,
) -> str:
    """Assembles the full prompt for one cluster investigation: the
    frozen contract text plus this cluster's specific file paths.
    `requirement_context_paths` should be deduplicated and sorted by the
    caller for deterministic output (not done here, to keep this
    function a pure formatter over whatever order it's given -- see
    `rtf.l11_investigation_grouping.context_artifacts`'s own
    deterministic-ordering convention for where that responsibility
    belongs).
    """
    req_context_block = "\n".join(f"- {p}" for p in requirement_context_paths) or "(none)"
    body = f"""Protocol context file (read first): {protocol_context_path}

Requirement context file(s) (read one per distinct requirement in this cluster):
{req_context_block}

Cluster investigation plan (read last, then execute exactly): {cluster_plan_path}
"""
    return load_frozen_cluster_prompt() + "\n\n---\n\n" + body
