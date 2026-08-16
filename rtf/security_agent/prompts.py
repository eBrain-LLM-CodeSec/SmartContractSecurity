"""Prompt assembly for the security-agent kernel's cluster investigation
loop.

Increment 2 scope only: a plain "inspect the code, cite evidence,
conclude" instruction set. Deliberately does NOT yet include the
counterexample-driven/hypothesis-first framing (brief Phases 4-5) --
that is a separate, later increment, kept out here on purpose so a
future before/after comparison between increments is meaningful (the
brief's own "keep RTF + clustering fixed, change only the investigator"
discipline applies just as much between OUR OWN increments as it does
against Codex).

Generic reasoning-shape guidance only where it does appear -- no
benchmark-specific hints anywhere in this module (brief's explicit
anti-benchmark-tuning constraint, same discipline
RTF_V3_REDESIGN_PLAN.md's own guidance table follows).
"""
from __future__ import annotations

from rtf.security_agent.tools import describe_tools

SYSTEM_PROMPT_TEMPLATE = """You are a security investigation agent examining ONE CLUSTER of related \
smart-contract security requirements/properties in a single session. All \
properties in this cluster share code context (contract, state, or \
callgraph) -- the reason they are grouped together is that evidence \
relevant to one is often relevant to the others too. Investigate them \
together; reuse what you learn across properties rather than treating \
each in total isolation.

You have the following tools available. Call at most ONE tool per turn.

{tool_descriptions}

## How to respond

Respond with EXACTLY ONE fenced JSON code block (```json ... ```), \
containing EXACTLY ONE of the two shapes below. Nothing else in your \
response is read -- only this JSON block is parsed.

To call a tool:
```json
{{"action": "call_tool", "tool": "<tool name>", "args": {{"...": "..."}}, "reasoning": "<why you need this>"}}
```

To conclude the investigation for ALL properties in this cluster at once:
```json
{{"action": "conclude", "properties": [
  {{"property_id": "<id>", "verdict": "PASS", "reasoning": "<cite specific evidence: file, contract, function, and what it shows>"}}
]}}
```

`verdict` must be exactly one of PASS, FAIL, or NOT_APPLICABLE.

`conclude` must include EXACTLY one entry for EVERY property_id listed \
in the initial message -- no more, no fewer. Do not conclude until you \
have actually inspected the relevant code with your tools; a PASS or \
FAIL with no cited file/function evidence is not acceptable. NOT_APPLICABLE \
is for a property whose subject matter genuinely does not apply to this \
codebase (e.g. it concerns a language construct or pattern the code \
never uses) -- it is not a way to skip investigating something that does \
apply.
"""


def build_system_prompt() -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(tool_descriptions=describe_tools())


def build_initial_user_message(
    property_ids: list[str],
    protocol_context_md: str,
    requirement_context_by_property: dict[str, str],
    cluster_plan_md: str,
) -> str:
    """The three artifacts the existing Codex path also gets (protocol
    context / requirement context / cluster plan -- see
    rtf.l11_investigation_grouping.context_artifacts), inlined directly
    into the first message instead of written to disk and discovered via
    a file-reveal mechanism: this kernel already has full, direct access
    to everything through its own tools from turn one, so there is no
    "must call a tool to see the plan" step to preserve."""
    req_context_block = "\n\n".join(
        f"### Requirement context: {rid}\n{content}"
        for rid, content in requirement_context_by_property.items()
    ) or "(none provided)"
    return f"""## Properties in this cluster

{", ".join(property_ids)}

## Protocol context

{protocol_context_md}

## Requirement context

{req_context_block}

## Cluster investigation plan

{cluster_plan_md}

Begin your investigation. Use your tools to inspect the actual code \
before concluding anything about any property.
"""
