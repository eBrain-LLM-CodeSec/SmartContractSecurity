"""RTF_V3_REDESIGN_PLAN.md Phase 6: compact, requirement-specific
investigation guidance.

The generic "Investigation procedure"/"What would constitute a
violation" text in `context_artifacts.generate_cluster_plan_md` is
IDENTICAL for every requirement regardless of its own reasoning shape --
confirmed by Phase 1's trace as a real gap (`RTF_V3_REDESIGN_PLAN.md`
finding 5/7). Canto H-01's root cause (`RTF_V2_COMBINED_PIPELINE_
5MISSES_ROOT_CAUSE.md`): the right requirement was applied to the right
function three times, but no investigation asked the specific two-hop
question a cross-boundary block-data value requires -- a missing
GUIDANCE problem, not a missing predicate or a missing requirement.

Deliberately a small, explicit dict keyed by REAL static-corpus
`req_id`s, each with a docstring-style comment citing the exact
normative/explanatory text it is grounded in -- NOT a new intermediate
requirement language, NOT keyed on any EVMbench finding/target/contract
name (checked by `test_investigation_guidance.py`'s own banned-
identifier scan), and NOT a blanket "be more thorough" addition (task
brief constraint #3): only requirements whose own text names a distinct
REASONING SHAPE (not just a code pattern) get an entry here. Most of the
81-requirement corpus intentionally has NO entry -- the existing generic
procedure remains correct and sufficient for those.

Applies to BOTH a property whose OWN `requirement_id` is one of these
keys (a structural/ERC-GP property) AND a semantic property whose
`parent_requirement_id` is one of these keys (RTF_V2 Phase 4) -- see
`guidance_for_property`.
"""
from __future__ import annotations

from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata

# --- req-2-block-data-misuse / req-2-random-enough ----------------------
# Grounded in req-2-block-data-misuse's own normative text, which gives
# as its OWN worked example a value "such as block.number / 14 as a
# proxy for elapsed seconds" -- a value computed in one place and
# potentially misinterpreted by whatever consumes it. The predicate
# layer already has a dedicated cross-boundary detector
# (`l5_predicates.find_cross_boundary_block_data_argument`) for exactly
# this pattern; this guidance is what tells the investigator to actually
# ASK the two-hop question that predicate's evidence makes possible.
_CROSS_BOUNDARY_BLOCK_DATA_GUIDANCE = """\
**Requirement-specific guidance (block-data / external-boundary semantics):**
This property concerns a value derived from `block.number`, `block.timestamp`, \
or similar block data.
- Trace this value from where it is read to EVERY place it is subsequently used, \
including as an argument to an external call, another contract's function, or a \
library call.
- Whenever the value crosses a function or contract boundary, inspect the \
CALLEE's own interface/implementation (when available in this repository) for \
what unit or semantics IT expects for that parameter.
- Confirming the value is used self-consistently WITHIN the caller is NOT \
sufficient -- explicitly compare the caller's own assumption (e.g. "this is a \
block count") against the callee's own assumption (e.g. "this is elapsed \
seconds"). A mismatch here is a violation even if every use inside the caller \
itself is internally consistent.
"""

# --- req-3-all-valid-inputs -----------------------------------------------
# Grounded verbatim in req-3-all-valid-inputs's own normative text:
# "Tested Code MUST validate inputs, and function correctly whether the
# input is as designed or malformed."  Two SEPARATE obligations in one
# sentence -- correctness on valid input, and (independently) rejection
# of invalid input. A property phrased only around the first half lets a
# silent-garbage-output-on-invalid-input bug hide even when the
# investigator's own reasoning surfaces the exact mechanism.
_INPUT_DOMAIN_VALIDATION_GUIDANCE = """\
**Requirement-specific guidance (input validation):**
This property concerns validating inputs, not merely computing correctly on \
well-formed ones.
- Identify the function's real input domain, including boundary/invalid values: \
zero, negative (where representable), the maximum representable magnitude, and \
any value outside the mathematically-defined region for the operation (e.g. a \
logarithm or square root of a non-positive number).
- Distinguish CORRECT BEHAVIOR ON VALID INPUT from REJECTION OF INVALID INPUT -- \
these are two separate obligations. A function that computes the right answer \
for well-formed input can still violate this requirement if it silently returns \
a default, zero, or otherwise-garbage value for a domain-invalid input instead \
of reverting.
- Do not treat successful execution (no revert) as evidence of safety by \
itself -- check specifically what value is produced for an out-of-domain input, \
and whether that value could be mistaken for a legitimate result by any caller.
"""

# --- req-3-enough-gas / req-3-protect-gas ---------------------------------
# Grounded verbatim in req-3-enough-gas's own explanatory text:
# "Iterating over a structure whose size is not clear in advance...
# can result in significant increases in gas usage" -- and req-3-
# protect-gas's normative text ("MUST protect against malicious actors
# stealing or wasting gas"). The structural predicate layer
# (`l5_predicates.find_unbounded_growth_with_downstream_iteration`) can
# only supply a candidate location; this guidance tells the investigator
# to reason about the structure's behavior OVER TIME/REPEATED CALLS, not
# just a single invocation.
_RESOURCE_GROWTH_GAS_GUIDANCE = """\
**Requirement-specific guidance (growing persistent state / gas):**
This property concerns a persistent data structure that can grow over the \
contract's operational lifetime.
- Identify EVERY insertion/growth path for the structure, and every deletion/\
pruning path (if any exists at all).
- Determine whether growth is bounded (a hard cap, or restricted to a small, \
trusted set of callers) or effectively unbounded (open to any user, with no \
removal path).
- Find every operation whose gas cost depends on the structure's CURRENT SIZE \
(full iteration, enumeration, or a loop bound derived from its length).
- Reason across REPEATED transactions over the contract's lifetime, not a \
single call in isolation -- a structure that is safe at size 10 may not be at \
size 10,000; consider whether an adversary can cheaply and permissibly drive it \
there.
"""

GUIDANCE_BY_REQ_ID: dict[str, str] = {
    "req-2-block-data-misuse": _CROSS_BOUNDARY_BLOCK_DATA_GUIDANCE,
    "req-2-random-enough": _CROSS_BOUNDARY_BLOCK_DATA_GUIDANCE,
    "req-3-all-valid-inputs": _INPUT_DOMAIN_VALIDATION_GUIDANCE,
    "req-3-enough-gas": _RESOURCE_GROWTH_GAS_GUIDANCE,
    "req-3-protect-gas": _RESOURCE_GROWTH_GAS_GUIDANCE,
}


def guidance_for_property(m: PropertyMetadata) -> str | None:
    """The guidance text for `m`, or `None` if neither its own
    `requirement_id` nor its `parent_requirement_id` (RTF v2 Phase 4 --
    a semantic property linked to a real static-corpus parent) has an
    entry above. Own `requirement_id` is checked first: a structural/
    ERC-GP property IS the requirement, so its own id takes priority
    over any (impossible, for those kinds) parent link.
    """
    direct = GUIDANCE_BY_REQ_ID.get(m.requirement_id)
    if direct is not None:
        return direct
    if m.parent_requirement_id:
        return GUIDANCE_BY_REQ_ID.get(m.parent_requirement_id)
    return None
