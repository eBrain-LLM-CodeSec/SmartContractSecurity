# Gap analysis: why `[Q] Document Contract Logic` / `[Q] Implement as
# Documented` never produced semantic/business-logic analysis of
# LiquidRon's `totalAssets()`/fee-accounting/share-pricing behavior

**Diagnosis only, per explicit instruction — no pipeline code touched.**
Scope: trace `req-3-documented` ("Document Contract Logic") and
`req-3-implement-as-documented` ("Implement as Documented") from the
original EthTrust spec text through L1 translation, L4/L5/L6/L7 predicate
construction, L12 evidence generation/routing, and the L8/Commentator
judgment call, for the `2025-01-liquid-ron` supervised validation run
(commit `5b74644`).

## Answer, up front

**The chain breaks at predicate construction (L4-L7), before evidence
generation ever begins.** Both requirements were faithfully translated
(L1) and correctly context-bundled (L2), but were assessed at the
strategy-design stage (Track A, `rtf/track_a/l7_level_q_evidence/`) as
`NO_PREDICATE_POSSIBLE` and consequently were **never added to
`rtf/l12_evaluation/registry.py`**. Because `run_rtf.py`'s evidence-
collection loop iterates `REGISTRY.items()` only, these two requirements
never entered `run.routed` at all for LiquidRon — not as `NOT_APPLICABLE`,
not as an operational failure, not as anything. They are completely
absent from every downstream stage: no evidence, no L8 bounded judgment,
no escalation, no Codex/Commentator investigation. This is true for
**every** EVMbench target evaluated by the currently-wired pipeline, not
something specific to LiquidRon.

A fully-specified reviewer rubric for exactly this semantic check DOES
already exist on paper (see below) — it was simply never turned into
code once the tool it depended on (L8) was actually built.

## Stage-by-stage trace

### L0 → L1 (EthTrust spec text → requirement corpus): faithful, no loss

`rtf/l1_corpus/requirement_corpus.json`:

```
req-3-documented:
  normative_text: "Document Contract Logic A specification of the
  business logic that the Tested code functionality is intended to
  implement MUST be available to anyone who can call the Tested Code."

req-3-implement-as-documented:
  normative_text: "Implement as Documented The Tested code MUST behave
  as described in the documentation provided for [Q] Document Contract
  Logic, and [Q] Document System Architecture."
  referenced_requirements: [req-3-documented, req-3-document-system]
```

Both are level Q, modality MUST, section 5.3.1 "Documentation
requirements." The cross-reference from `req-3-implement-as-documented`
to `req-3-documented`/`req-3-document-system` is correctly captured as a
structured `referenced_requirements` link, not lost in prose. Nothing is
weakened or paraphrased relative to the original spec wording.

### L1 → L2 (context bundle): faithful, no loss

`rtf/l2_context_bundles/req-3-documented.json` and
`.../req-3-implement-as-documented.json` both exist and are populated —
confirmed present on disk. Context-bundle construction ran for these two
requirements exactly like every other requirement in the corpus; there is
no asymmetry here versus the 56 requirements that DO have predicates.

### L3 (applicability): correctly determined, no loss

Per `rtf/track_a/l7_level_q_evidence/req-3-implement-as-documented.json`:
`"applicability": "APPLICABLE to all Tested Code, unconditionally"` — a
correct, unconditioned reading (there is no conditioned-scope clause
narrowing this requirement to a subset of contracts). LiquidRon.sol would
have been in scope had a predicate existed.

### L4-L7 (predicate/strategy construction): **this is where the chain breaks**

`rtf/track_a/l7_level_q_evidence/SCHEMA.md` fully specifies a rubric for
exactly this class of requirement — an LLM-mediated "claims vs.
implementation" cross-check:

1. `evidence_expected` — look for a business-logic spec in README/NatSpec/
   docs/whitepaper (for `req-3-documented`) and system-architecture
   documentation (for `req-3-document-system`, referenced by
   `req-3-implement-as-documented`).
2. `claims_vs_implementation_procedure` — "For each documented behavioral
   claim found..., locate the code component(s) that appear to implement
   it..., then assess consistency: does the code actually behave as the
   documentation states?"
3. A `conformance_state_decision_rule`: FAIL if "a documented claim is
   directly contradicted by code behavior"; INSUFFICIENT_EVIDENCE if
   there's nothing to compare against; INCONCLUSIVE if documentation is
   too vague.

This rubric is precisely the mechanism that COULD have compared LiquidRon's
own documentation about `totalAssets()`/fee behavior against what the code
actually does — see the honest caveat below on whether it actually would
have caught H-01.

But its own file says explicitly:

```
"implementation_status": {
  "status": "NO_PREDICATE_POSSIBLE",
  "note": "NO_PREDICATE_POSSIBLE -- comparing implementation behavior
  against documentation claims is the archetypal L7 evidence-vs-claim
  cross-check; inherently semantic, no mechanical trigger identified in
  this record."
}
"not_yet_done": "This rubric has not been executed against any real
repository in Track A -- doing so requires the L8 shared LLM Judgment
Layer ... which is not yet built. Recorded here as the fully-specified
next step, not faked."
```

That "not yet built" blocker no longer applies — L8 (`judgment_layer.py`,
`judge_with_l8.py`) was built later, in Phase H, and is exactly what this
session's liquid-ron run used successfully for the other 56 requirements.
**The rubric was never revisited or wired into `registry.py` once its own
stated blocker was resolved.** This is not a currently-open TODO anyone
is actively tracking that I could find — `registry.py`'s own module
docstring lists both as part of "24 requirements with no implemented
predicate," a static fact, not a flagged pending item.

### L12 evidence generation (`run_rtf.py`): never runs for these two req_ids

```python
for req_id, specs in REGISTRY.items():
    ...
```

`req-3-documented` and `req-3-implement-as-documented` are not keys in
`REGISTRY` (confirmed: `REGISTRY` has 56 entries; the full corpus has 81;
these two are 2 of the 25 absent). The loop that collects predicate
evidence, decides `ApplicabilityState`, and builds `RoutedRequirementResult`
never executes for them at all. This is upstream of "insufficient
evidence" — it's zero attempts, not a null result from a real attempt.

### Routing (`TargetRunResult.routed`): silently absent, contradicting the registry's own stated invariant

Confirmed directly against this run's own artifacts
(`entry_03_LiquidRon_stage.json`'s `conformance_by_req`): both req_ids are
**not present as keys at all** (not `null`, literally absent), alongside
`stage_metrics.requirements_considered == 56 == len(REGISTRY)` for every
one of the 6 liquid-ron entries. Neither `audit.md` nor `pilot_summary.json`
mentions these two requirements, or the other 23 unregistered ones,
anywhere.

This is worth flagging precisely because `registry.py`'s own module
docstring states an invariant that current behavior does not honor:

```
"""Deliberately excludes the 24 requirements with no implemented
predicate (21 terminal NO_PREDICATE_POSSIBLE/NOT_IMPLEMENTED + 3 pure
aggregation) -- the orchestrator must not silently skip them without
comment; see run_rtf.py's handling of requirements absent from this
registry."""
```

`run_rtf.py` has no such handling — there is no "requirements absent from
this registry" branch at all, silent or otherwise. The 25 unregistered
requirements (31% of the 81-requirement corpus) produce zero trace in any
artifact this pipeline writes. This is a real, confirmed discrepancy
between documented design intent and actual code — a finding in its own
right, separate from (but related to) the main answer above. **Not fixed
as part of this diagnosis, per instruction.**

### L8 bounded judgment / escalation / Commentator (Codex): never reached

`run_pipeline_e2e`'s escalation loop iterates `run.routed.items()` only.
Since these two req_ids are never keys in `routed`, they never reach
`judge_with_l8.judge_result`, never get an escalation decision from
`escalation.decide_escalation`, and never reach
`codex_bridge`/`arm_g_codex`/Commentator. **This is not a case of the LLM
judgment layer or Codex investigation reasoning about LiquidRon's
`totalAssets()`/fee logic and reaching the wrong conclusion — neither was
ever invoked for these two requirements, on this target or any other.**

## Where information was and wasn't lost — summary table

| Stage | Requirement content preserved? | Executed for LiquidRon? |
|---|---|---|
| L0 → L1 (spec → corpus) | Yes, faithful, normative text + cross-references intact | N/A |
| L1 → L2 (context bundle) | Yes, bundle exists and is populated | N/A |
| L3 (applicability) | Yes, correctly APPLICABLE-unconditional | N/A |
| L4-L7 (predicate/strategy) | Rubric fully specified, but marked `NO_PREDICATE_POSSIBLE` and never coded | **No — never implemented** |
| L12 evidence generation | N/A (nothing to generate without a predicate) | **No — loop never reaches these req_ids** |
| Routing (`TargetRunResult.routed`) | N/A | **No — absent as keys, no placeholder** |
| L8 bounded judgment | N/A | **No — never called** |
| Escalation / Commentator (Codex) | N/A | **No — never called** |

## Honest caveat: would the rubric, if implemented, have actually caught H-01?

Not necessarily, and this matters for calibrating how much this gap
"cost." Checked directly against LiquidRon's real source and README
(read-only, post-grading, for this diagnostic purpose only):

- `totalAssets()`'s own NatSpec is generic: `/// @dev Gets the total
  amount of assets the vault controls` — it makes no explicit claim about
  whether `operatorFeeAmount` should be included or excluded. There is no
  specific documented claim for the rubric's `claims_vs_implementation`
  step to directly contradict.
- The README's "Automated Findings / Publicly Known Issues" section
  (which the C4 process treats as pre-disclosed, normally
  award-ineligible) contains a direct sponsor quote: *"I am aware that
  the operator fee changing impacts the total assets calculation in the
  vault... I am aware of it and I am ok with the behaviour."* A
  claims-vs-implementation check reading this text would plausibly see it
  as **consistent, disclosed, accepted behavior**, not a contradiction —
  yet H-01 was still submitted, accepted, and the judge raised it to
  **High** severity specifically because the real exploit (value
  transferred to whoever redeems before a fee harvest vs. after) is a
  narrower, more specific mechanism than the sponsor's own general
  disclaimer about directional fee impact.
- Per the rubric's own decision rule, this shape of evidence
  (generic NatSpec + a vague, arguably-covering sponsor disclaimer) would
  most plausibly land as **INCONCLUSIVE or a contested PASS**, not a
  clean FAIL — the same kind of judgment-call risk this project's own
  Phase H work already found LLM judges struggle with on ambiguous cases.

**Conclusion:** closing the L4-L7 gap (implementing and wiring the
existing rubric) would give these two requirements a genuine chance to
run, which they currently never get — a real, worthwhile fix in its own
right, and separately worth doing since `req-3-implement-as-documented`
already has 40 L11 correspondence records against OTHER real EVMbench
findings (`rtf/l9_assumptions_register/REGISTER.jsonl` AR-004), i.e. this
project's own prior analysis already treats it as one of the more
consequential Q-level requirements in the corpus. But it should **not**
be sold as a guaranteed catch for H-01 specifically — the documentation
evidence available in this particular repository is genuinely ambiguous
enough that even a working implementation might not have flagged it. The
real, unambiguous finding here is architectural (a designed-but-unbuilt
capability, silently absent from every run), not a specific missed-catch
guarantee.

## What this is and isn't

- **Is:** a real, confirmed capability gap — 25 of 81 requirements (31%
  of the corpus), including both requirements traced here, never execute
  in the currently-wired pipeline, for any target, and this fact is
  invisible in every artifact the pipeline currently writes.
- **Is:** a secondary, smaller discrepancy between `registry.py`'s stated
  design invariant ("must not silently skip... without comment") and
  `run_rtf.py`'s actual behavior (no such comment/placeholder exists).
- **Is not:** an evidence-generation bug, a routing bug, or a Commentator/
  Codex reasoning failure — none of those stages were ever reached for
  these two requirements.
- **Is not:** proof that implementing the existing rubric would have
  caught LiquidRon's H-01 specifically — the available documentation
  evidence in this repo is genuinely ambiguous.
- **No pipeline code was changed to produce this analysis.**
