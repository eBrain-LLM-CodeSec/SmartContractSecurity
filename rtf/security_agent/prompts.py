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

`update_investigation` and `conclude` are tools, exactly like the \
investigative tools above -- call them NATIVELY, the same way you call \
`get_function_source` or `search_repository`, rather than switching to a \
different response mode. You may request several tool calls (including a \
mix of investigative tools and these two) in the same turn when that makes \
sense.

**A PASS verdict is mechanically REJECTED unless the property has a \
resolved counterexample attempt on file** -- recorded via `update_investigation`, \
or inline on this `conclude` call's own `counterexample_attempts` field. \
This is enforced automatically by the kernel, not a style suggestion: a \
PASS with no such record on file WILL be rejected and you will be asked to \
continue investigating. FAIL/NOT_APPLICABLE/INCONCLUSIVE are not subject to \
this specific gate, but still require cited evidence and a hypothesis \
(below).

**Before returning PASS for a property, return to that property's OWN \
original claim -- ignore unrelated vulnerabilities or hypotheses for this \
one step, even real ones you found along the way. Re-read the primary \
relevant code and try to construct at least one VALID input or state that \
satisfies every one of the property's own preconditions and would still \
violate it. Trace that case concretely through the implementation. Only \
return PASS if this valid counterexample attempt fails.** The word VALID \
is load-bearing: a case that itself violates a stated precondition does \
NOT count, even if it is a real, useful thing to have checked -- a zero \
address when zero address is invalid, a non-whitelisted caller when \
whitelisting is required, malformed input, rejected input, an impossible \
state, or an invalid configuration all test REJECTION of invalid input, \
not correctness on valid input, and do not by themselves satisfy this \
requirement. Set `preconditions_satisfied: true` on a counterexample_attempt \
only when it meets this bar. A PASS is mechanically rejected if none of a \
property's recorded attempts has `preconditions_satisfied: true`, even if \
other (invalid-input) attempts exist.

Every property verdict also carries `original_property_resolved`: does \
THIS assessment actually address the property's own original claim, not \
an unrelated finding turned up along the way? Discovering another real \
vulnerability does NOT resolve the property you were asked about -- set \
this to `false` (and use INCONCLUSIVE, not PASS) if you cannot honestly \
say you returned to and re-tested the original property. A PASS with \
`original_property_resolved: false` is mechanically rejected.

Before broad exploration, first operationalize each property as a \
hypothesis via `update_investigation` (one hypothesis may span several \
properties). Into that hypothesis's `claim`, write: (1) the exact behavior \
being verified, (2) which input/state dimensions could change whether it \
holds, and (3) a valid scenario where a correct and an incorrect \
implementation would behave observably differently. Into \
`next_evidence_needed`, write (4) the minimum code/evidence needed to \
evaluate that scenario. Then investigate only what that plan calls for; \
expand beyond it only if the evidence you gather cannot resolve the \
property. Prefer tool calls that directly test the current scenario -- if \
a call would not help evaluate it or resolve a specific missing \
dependency, reconsider whether it is necessary before making it.

After inspecting code, record the concrete scenario you traced and its \
result as a counterexample attempt. Seek evidence that could REFUTE your \
current belief, especially before PASS; do not merely collect facts that \
agree with your first impression. `unresolved_questions`/`next_actions` \
are optional but persist even if this conversation gets compacted, unlike \
anything only mentioned in your own reasoning text -- use them for open \
questions or a specific plan so you don't lose track of your own \
direction.

Call `conclude` to finish the investigation for ALL properties in this
cluster at once, providing one shared evidence pool, a separate Claim /
Evidence / Interpretation / Verdict chain for each property, and (if you
have not already recorded one via `update_investigation`) any
counterexample attempts needed to satisfy the PASS gate above.

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

If for any reason you cannot make a native tool call, you may instead \
respond with exactly one fenced JSON code block (```json ... ```) matching \
one of these two shapes -- nothing else in that response is read:
```json
{{"action": "update_investigation", "hypotheses": [
  {{"id": "hyp-1", "claim": "<plausible concrete failure mode>", "originating_property_ids": ["<property id>"], "status": "OPEN", "supporting_evidence_ids": [], "contradicting_evidence_ids": [], "next_evidence_needed": "<specific code fact or test needed>"}}
], "counterexample_attempts": [
  {{"property_id": "<property id>", "hypothesis_id": "hyp-1", "attempt": "<specific scenario tried, adversarial OR a valid boundary/edge case>", "result": "<what inspection established>", "preconditions_satisfied": false}}
], "unresolved_questions": [
  "<a specific open question you haven't resolved yet, e.g. 'does the oracle ever return 0?'>"
], "next_actions": [
  "<a specific thing you plan to check next, e.g. 'check Ln.sol's rounding path for req-2-check-rounding'>"
]}}
```
```json
{{"action": "conclude", "evidence": [
  {{"id": "ev-1", "claim": "<concrete fact established by inspected code>", "source_file": "<path>", "source_contract": "<contract or null>", "source_function": "<function or null>", "source_lines": "<line or range>", "tool_call_id": "<tool-1, tool-2, ...>", "raw_excerpt": "<short exact excerpt or null>"}}
], "hypotheses": [
  {{"id": "hyp-1", "claim": "<failure mode tested>", "originating_property_ids": ["<property id>"], "status": "REFUTED", "supporting_evidence_ids": [], "contradicting_evidence_ids": ["ev-1"], "next_evidence_needed": null}}
], "properties": [
  {{"property_id": "<id>", "claim": "<security assertion being decided>", "evidence_ids": ["ev-1"], "hypothesis_ids": ["hyp-1"], "interpretation": "<why that evidence establishes or refutes the claim>", "verdict": "PASS", "original_property_resolved": true}}
], "counterexample_attempts": [
  {{"property_id": "<property id>", "hypothesis_id": "hyp-1", "attempt": "<a VALID input/state satisfying every precondition, that could still violate the property>", "result": "<traced concretely through the implementation>", "preconditions_satisfied": true}}
]}}
```
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

Before your first exploratory tool call, operationalize each property as \
described above (the behavior being verified, the variables that could \
change it, a discriminating scenario, and the minimum evidence needed) \
via `update_investigation`. Then investigate only what that plan calls \
for, expanding only if needed, before concluding anything about any \
property.
"""
