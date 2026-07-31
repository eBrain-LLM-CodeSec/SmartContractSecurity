"""Commentator agent: per-function structured suspicion comments, driven by
one FPSL prompt strategy (Agent4Vul's Commentator, adapted -- see fpsl.py).
Cost control: config defaults to 1 strategy per function rather than all 5.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from a4v import fpsl
from a4v.llm import ChatClient
from a4v.slice import ContextBundle, numbered_source


@dataclass
class Comment:
    suspicious: bool
    vuln_class: str | None
    severity: str | None
    rationale: str
    lines: list[int] = field(default_factory=list)
    strategy: int | str = 5
    prompt_tokens: int = 0
    completion_tokens: int = 0


def _bundle_context_text(bundle: ContextBundle) -> str:
    parts = [f"Contract: {bundle.contract} ({bundle.contract_summary})"]
    if bundle.inherited_defs:
        parts.append(f"Inherits: {', '.join(bundle.inherited_defs)}")
    if bundle.modifiers:
        parts.append(f"Modifiers applied: {', '.join(bundle.modifiers)}")
    if bundle.state_vars:
        parts.append(f"State variables touched: {', '.join(bundle.state_vars)}")
    if bundle.external_interactions:
        parts.append(f"External interactions: {len(bundle.external_interactions)}")
    if bundle.write_after_external_call_vars:
        parts.append(
            f"State written AFTER an external call in this function: {', '.join(bundle.write_after_external_call_vars)}"
        )
    return "\n".join(parts)


class Commentator:
    def __init__(self, chat_client: ChatClient, strategies: list[int | str] | None = None):
        self.chat_client = chat_client
        self.strategies = strategies or [5]

    def comment_source(self, source: str, context: str | None = None, strategy: int | str | None = None) -> Comment:
        strat = strategy or self.strategies[0]
        messages = fpsl.build_prompt(strat, source, context)
        data, result = self.chat_client.complete_json(messages)
        lines_raw = data.get("lines") or []
        return Comment(
            suspicious=bool(data.get("suspicious", False)),
            vuln_class=data.get("vuln_class"),
            severity=data.get("severity"),
            rationale=data.get("rationale", ""),
            lines=[int(x) for x in lines_raw if isinstance(x, (int, float))],
            strategy=strat,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
        )

    def comment_bundle(self, bundle: ContextBundle, strategy: int | str | None = None) -> Comment:
        raw_source = bundle.source_excerpts.get(bundle.seed, "")
        start_line = bundle.source_excerpt_start_lines.get(bundle.seed, 1)
        source = numbered_source(raw_source, start_line)
        context = _bundle_context_text(bundle)
        return self.comment_source(source, context=context, strategy=strategy)
