from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ArmMetrics:
    verdicts: dict[str, str]
    cost_usd: float
    input_tokens: int
    output_tokens: int
    tool_calls: int
    files_inspected: int
    wall_clock_s: float


@dataclass(frozen=True)
class ABMetrics:
    codex: ArmMetrics
    security_agent: ArmMetrics
    common_property_ids: tuple[str, ...]
    verdict_agreement_count: int
    verdict_disagreement_ids: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _verdicts(result) -> dict[str, str]:
    decision = getattr(result, "final_decision", None) or {}
    return {entry["property_id"]: entry.get("verdict", "")
            for entry in decision.get("properties", [])
            if isinstance(entry, dict) and entry.get("property_id")}


def arm_metrics(result) -> ArmMetrics:
    if hasattr(result, "tool_calls"):
        tool_calls = int(getattr(result, "tool_calls", 0) or 0)
    else:
        tool_calls = int(getattr(result, "graph_tool_calls", 0) or 0) + int(
            getattr(result, "actual_shell_commands", 0) or 0)
    if hasattr(result, "files_inspected"):
        files_inspected = int(getattr(result, "files_inspected", 0) or 0)
    else:
        files = set(getattr(result, "revealed_files", ()) or ())
        files.update(getattr(result, "actual_shell_files_touched", ()) or ())
        files_inspected = len(files)
    return ArmMetrics(
        verdicts=_verdicts(result), cost_usd=float(getattr(result, "cost_usd", 0.0) or 0.0),
        input_tokens=int(getattr(result, "input_tokens", 0) or 0),
        output_tokens=int(getattr(result, "output_tokens", 0) or 0),
        tool_calls=tool_calls,
        files_inspected=files_inspected,
        wall_clock_s=float(getattr(result, "wall_clock_s", 0.0) or 0.0),
    )


def compare_results(codex_result, security_agent_result) -> ABMetrics:
    codex = arm_metrics(codex_result)
    agent = arm_metrics(security_agent_result)
    common = tuple(sorted(set(codex.verdicts) & set(agent.verdicts)))
    disagreements = tuple(pid for pid in common if codex.verdicts[pid] != agent.verdicts[pid])
    return ABMetrics(
        codex=codex, security_agent=agent, common_property_ids=common,
        verdict_agreement_count=len(common) - len(disagreements),
        verdict_disagreement_ids=disagreements,
    )
