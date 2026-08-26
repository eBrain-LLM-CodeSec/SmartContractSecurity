"""Prompt assembly for the security-agent kernel's cluster investigation
loop.

Increment 4 makes hypotheses and counterexample attempts first-class state
transitions. The model must formulate plausible failure hypotheses before
concluding and explicitly try to falsify its emerging answer.

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

You have tools available for inspecting the code -- see their declared \
schemas for exact names and parameters. Call a tool whenever you need \
information; if you already know you need several independent facts, \
request them together in the same turn rather than one at a time.

{tool_descriptions}

## How to respond

When you are NOT calling a tool, respond with EXACTLY ONE fenced JSON \
code block (```json ... ```), containing EXACTLY ONE of the two shapes \
below. Nothing else in your response is read -- only this JSON block is \
parsed.

To record or update hypotheses and counterexample attempts:
```json
{{"action": "update_investigation", "hypotheses": [
  {{"id": "hyp-1", "claim": "<plausible concrete failure mode>", "originating_property_ids": ["<property id>"], "status": "OPEN", "supporting_evidence_ids": [], "contradicting_evidence_ids": [], "next_evidence_needed": "<specific code fact or test needed>"}}
], "counterexample_attempts": [
  {{"property_id": "<property id>", "hypothesis_id": "hyp-1", "attempt": "<specific adversarial scenario tried>", "result": "<what inspection established>"}}
]}}
```

Use `update_investigation` before concluding. Start with at least one
plausible failure hypothesis per property (one hypothesis may span several
properties). After inspecting code, record the concrete adversarial or
boundary scenario you tried and its result. Seek evidence that could REFUTE
your current belief, especially before PASS; do not merely collect facts
that agree with your first impression.

To conclude the investigation for ALL properties in this cluster at once,
provide one shared evidence pool followed by a separate Claim / Evidence /
Interpretation / Verdict chain for each property:
```json
{{"action": "conclude", "evidence": [
  {{"id": "ev-1", "claim": "<concrete fact established by inspected code>", "source_file": "<path>", "source_contract": "<contract or null>", "source_function": "<function or null>", "source_lines": "<line or range>", "tool_call_id": "<tool-1, tool-2, ...>", "raw_excerpt": "<short exact excerpt or null>"}}
], "hypotheses": [
  {{"id": "hyp-1", "claim": "<failure mode tested>", "originating_property_ids": ["<property id>"], "status": "REFUTED", "supporting_evidence_ids": [], "contradicting_evidence_ids": ["ev-1"], "next_evidence_needed": null}}
], "properties": [
  {{"property_id": "<id>", "claim": "<security assertion being decided>", "evidence_ids": ["ev-1"], "hypothesis_ids": ["hyp-1"], "interpretation": "<why that evidence establishes or refutes the claim>", "verdict": "PASS"}}
]}}
```

`verdict` must be exactly one of PASS, FAIL, NOT_APPLICABLE, or INCONCLUSIVE. \
Use INCONCLUSIVE only after genuinely investigating -- when the evidence \
you were able to gather is real but insufficient to decide PASS or FAIL \
with confidence. It is not a way to skip investigation, and it does not \
relax the evidence/hypothesis citation requirement below.

Every property must cite at least one evidence id from the shared evidence
pool and one hypothesis that was actually investigated. Reuse the same evidence id across properties when one inspected fact
is relevant to several properties; do not duplicate it. `tool_call_id`
refers to calls in order (`tool-1`, `tool-2`, ...).

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
