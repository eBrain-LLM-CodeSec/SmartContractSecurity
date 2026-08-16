# Phase 9: regression check against the known misses

Per the task brief's explicit instruction: this check happens AFTER the
generic fixes (Phases 3-6) were designed and implemented, using the
known misses only to verify the generic fixes naturally address them —
not the other way around. No requirement/predicate/guidance text in this
effort was written by reading these misses first (see each Phase's own
commit message for the actual grounding: verbatim EthTrust normative
text, generic Solidity semantics). This document is honest about what is
**structurally addressed by code now in the repo** vs. what would need a
**live rerun** (explicitly NOT done here, matching this project's
established convention of requiring explicit user authorization before
any paid Codex run) to actually confirm a flipped verdict.

Source: `RTF_V2_COMBINED_PIPELINE_5MISSES_ROOT_CAUSE.md`.

---

## Canto H-01 — block-number used where GaugeController expects elapsed time

**Prior classification**: `INVESTIGATION_REASONING_GAP` — the exact
requirement (`req-2-block-data-misuse`) was applied to the exact function
THREE separate times; each investigation confirmed `block.number` is
used *self-consistently within the caller* but never asked whether the
*callee* interprets the same value the same way.

**What this effort changed**: Phase 6's `investigation_guidance.py`
attaches `_CROSS_BOUNDARY_BLOCK_DATA_GUIDANCE` to every property whose
`requirement_id` (or, via Phase 4's parent-linking, `parent_requirement_
id`) is `req-2-block-data-misuse`/`req-2-random-enough`. Its text
directly names the missing reasoning step: *"Confirming the value is
used self-consistently WITHIN the caller is NOT sufficient... explicitly
compare the caller's own assumption... against the callee's own
assumption... A mismatch here is a violation even if every use inside
the caller itself is internally consistent."*

**Structurally addressed: YES, with a caveat.** This guidance text is
now genuinely wired into `generate_cluster_plan_md`'s per-property block
(verified live in `tests/ethtrust_conformance/req-2-block-data-misuse/`
— both the vulnerable AND safe fixtures independently mirror Canto
H-01's exact mechanism, and the conformance suite's Tier 2 mocked-agent
layer confirms the full pipeline — routing, property derivation,
context assembly, guidance attachment, verdict resolution — produces
the correct FAIL/PASS shape end-to-end). **The caveat**: whether a REAL
Codex agent, reading this guidance, actually performs the two-hop check
correctly is a live-LLM reasoning question this session's mocked
harness cannot answer — only a real rerun against the actual
`2025-01-canto` checkout would confirm the verdict flips. Not run this
session (would require real spend + explicit authorization, per this
project's established convention — see `RTF_V2_WHOLE_PROJECT_
COMPILATION_PLAN.md`'s own repeated pattern of deferring paid reruns).

**Remaining gap if it doesn't flip**: would be a genuine reasoning-depth
limit of the underlying model, not a fixable RTF architecture problem —
the guidance now poses the exact right question; whether the agent
answers it correctly is outside RTF's control at that point.

**UPDATE (2026-08-16, live rerun, user-requested): CONFIRMED FLIPPED.**
Real `DetectGrader` result on `2024-01-canto`: **2/2, up from 1/2** — H-01
now detected, independently 3 times, with evidence text directly
reflecting the Phase 6 guidance's own language ("the caller's own
assumption... against the callee's own assumption"; "Internal consistency
within LendingLedger cannot make that lookup valid"). Full writeup:
`RTF_V3_LIVE_CANTO_RERUN_RESULT.md`. The live-rerun caveat above is
resolved — this is no longer a prediction.

---

## Forte H-03 — `Ln.ln()` accepts negative/zero input without validation

**Prior classification**: hybrid — the investigator's own reasoning
trace named the exact defect ("the only bypass is a mathematical one,
for which `ln` returns zero") and still resolved PASS, because the
semantic property's own wording was framed around "correctness" rather
than "must reject invalid input."

**What this effort changed, two independent fixes**:

1. **Phase 4** (semantic properties are no longer parentless): a
   generated property about `Ln.ln`'s behavior, if its `property_type`/
   statement maps to `INPUT_DOMAIN_VALIDATION` (`semantic_taxonomy.
   map_property_type_to_reasoning_category` — direct for `property_type
   in {"...}"` or keyword fallback via `categorize_generated_clause` for
   "structural"/"semantic"/"standard_conformance" types, checking for
   "validate"/"revert"/"zero address"/"input" in the statement text),
   now gets `parent_requirement_id="req-3-all-valid-inputs"` attached
   (verified: `requirements_in_category(INPUT_DOMAIN_VALIDATION) ==
   ("req-3-all-valid-inputs",)`, the ONLY static-corpus member). The
   investigator then receives req-3-all-valid-inputs's FULL normative
   text ("MUST validate inputs, **and function correctly whether the
   input is as designed or malformed**") alongside the narrow property,
   with the Phase 4 dual-obligation gate (`parent_obligation_check`)
   requiring the verdict to address BOTH.
2. **Phase 6**: `_INPUT_DOMAIN_VALIDATION_GUIDANCE`, attached whenever
   `req-3-all-valid-inputs` is the property's own OR parent requirement,
   states directly: *"Distinguish CORRECT BEHAVIOR ON VALID INPUT from
   REJECTION OF INVALID INPUT... A function that computes the right
   answer for well-formed input can still violate this requirement if
   it silently returns a default, zero, or otherwise-garbage value...
   Do not treat successful execution (no revert) as evidence of safety
   by itself."* This is a near-verbatim restatement of Forte H-03's
   exact failure mode.

**Structurally addressed: YES, with the same live-rerun caveat as
above** — verified end-to-end via `tests/ethtrust_conformance/req-3-all-
valid-inputs/` (a domain-invalid-input Ln-shaped fixture, deliberately
NOT copied from the real Forte `Ln.sol` source, built independently from
req-3-all-valid-inputs's own normative text) plus the mutation-testing
PoC, which shows that REMOVING the domain check on an otherwise-safe
fixture is mechanically detected by the structural predicate
(`find_unvalidated_function_parameters`) again. **Additional real
finding this session**: `find_unvalidated_function_parameters` is a
STRUCTURAL predicate (not semantic-generator-dependent) already
registered under `req-3-all-valid-inputs` — if it independently fires on
the real `Ln.sol`'s `ln(int256)` signature (plausible: an unvalidated
int256 parameter to a domain-restricted math function is exactly its
trigger shape, though not verified against the real Forte checkout in
this session), Phase 6's guidance would reach the investigator via the
STRUCTURAL path directly, independent of whether semantic generation
even proposes a matching property that run — a more robust route to
closing this miss than semantic-property parent-linking alone.

---

## Phi H-03 — `Cred.sol` `shareBalance` `EnumerableMap` bloat DoS

**Prior classification**: `REQUIREMENT_TAXONOMY_GAP` — "EthTrust lacks
this vulnerability class," reached because every requirement category
routed to `_updateCuratorShareBalance` (checks-effects-interactions,
external-call safety) was the wrong SHAPE of question, and the semantic
generator never proposed an "unbounded resource growth" property across
three independent attempts.

**This effort's Phase 1 finding directly disputes the prior
classification** (`RTF_V3_REDESIGN_PLAN.md` finding 4): `req-3-enough-
gas` is a REAL, parsed, `AGENT_REQUIRED` corpus requirement whose own
explanatory text ("Iterating over a structure whose size is not clear in
advance... can result in significant increases in gas usage") describes
this EXACT mechanism. The true root cause was `RTF_APPLICABILITY_GAP` —
no predicate represented the code pattern — not a taxonomy gap.

**What this effort changed**: Phase 5's `find_unbounded_growth_with_
downstream_iteration`, validated live against a Slither-compiled fixture
deliberately shaped to mirror `Cred.sol`'s real pattern (struct-wrapped
`bytes32[] _keys` + mapping, `.set()`/`.length()`/`.at()` library calls,
insertion called, removal never called, iterated in a loop) — confirmed
to fire correctly (`tests/ethtrust_conformance/req-3-enough-gas/`,
`l5_predicates/test_predicates.py`'s growth tests, and the mutation PoC
showing that removing the pruning path from an otherwise-safe fixture is
detected).

**Structurally PARTIALLY addressed — one real, disclosed limitation
remains.** Re-reading the 5-misses report's own text carefully for this
check: the growth happens in `Cred.sol`'s `_updateCuratorShareBalance`,
but the ENUMERATION happens in a **separate contract**,
`CuratorRewardsDistributor`. Phase 5's predicate (per its own docstring,
written honestly BEFORE this check, not retrofitted after) is
**deliberately per-contract, not a whole-project call-graph search**
like `find_cross_boundary_block_data_argument` — it only looks for the
insertion/removal/iteration triad within ONE contract's own declared
functions. On the REAL Phi target as described in the root-cause report,
this predicate would need `shareBalance` (or a public accessor to it) to
be read by a loop inside `CuratorRewardsDistributor` itself to fire — if
`CuratorRewardsDistributor` instead calls into `Cred` to read it (via an
external call/getter, not a direct state-variable read in its own AST),
the current single-contract predicate would **not** detect this specific
real case as implemented.

**Honest classification (as first written, before the live check)**:
`RTF_APPLICABILITY_GAP`, now CORRECTLY reachable in the single-contract
case (a real, generalized fix, proven live), but the specific REAL Phi
H-03 instance's cross-contract split means this session's fix likely
does **not** yet flip that specific finding without a further extension.
**Not verified against the real Phi checkout this session** — flagged
honestly as an assumption, not a live-checked fact.

**UPDATE (2026-08-16, live rerun, user-requested — and a direct,
warranted user correction of the paragraph above): CONFIRMED FLIPPED,
via a DIFFERENT mechanism than assumed.** Real `DetectGrader` result on
`2024-08-phi`: **5/6, up from 4/6** — H-03 now detected. The user
correctly pushed back on the cross-contract framing above: it conflated
"Phase 5's predicate is scoped per-contract" with "RTF can only find
this via that predicate's own candidate location." Two things the
original paragraph underweighted: (1) `Cred.sol` itself contains
`_getCuratorData`, an in-contract function that enumerates the SAME
growing `shareBalance` map — the predicate fired entirely within one
contract's own scope, no cross-contract extension needed on THIS real
target; (2) even where a predicate's routing signal is narrower, whole-
project Foundry compilation gives the investigating agent full multi-
file access regardless, and Phase 6's guidance is attached at the
requirement level, not scoped to the predicate's own candidate location.
Real evidence (`req-3-enough-gas::loc0`, FAIL): *"Cred._getCuratorData
iterates from start_ to shareBalance[credId_].length() when stop_ is
zero. _updateCuratorShareBalance sets a fully sold holder's value to
zero but never calls EnumerableMap.remove... Because stale entries are
never pruned, sufficient gas is not assured over the contract
lifetime."* Independently confirmed by the real judge's own reasoning
(`grade_result.json`). Full writeup: `RTF_V3_LIVE_PHI_RERUN_RESULT.md`.
**The whole-project/cross-contract limitation described above remains a
real, disclosed architectural gap in the predicate's own design** — it
just wasn't the deciding factor for THIS specific target's H-03, which
this session originally assumed without checking. The corrected lesson:
don't infer an end-to-end miss from a routing-layer gap alone without a
live check, especially once whole-project context + requirement-level
guidance are both already in place.

---

## Existing successful findings — not regressed

Per the task brief's explicit instruction to also check that prior
successes aren't broken: every fix this session was additive (new
optional fields defaulting to `None`/unchanged behavior, new predicates
registered ALONGSIDE existing ones never replacing them, new guidance
text appended to existing sections never removing any) and verified via
the FULL existing regression suite after every phase (~700+ checks
across `test_context_artifacts.py`, `test_codex_bridge.py`, `test_live_
runner.py`, `test_property_grounding.py`, `test_cluster_response_
validation.py`, `test_predicates.py`, `test_agentic_architecture.py`,
`test_concurrent_escalation.py`, `test_runtime_coverage.py`, `test_mock_
codex_routing.py`, `test_semantic_property_generation.py`, `test_
semantic_pipeline.py`, `test_semantic_only_driver.py`, `test_end_to_end_
integration.py`, `test_instance_expansion.py`), zero failures at any
commit. The one real regression found DURING this work (Phase 4's
`requirement_text` field accidentally corrupting `expand_investigation_
instances`' clause-splitter) was caught by this SAME existing suite
before being committed, then fixed at its root (splitting into
`requirement_text`/`requirement_context_text`) — not worked around.

**UPDATE (2026-08-17, live rerun): NOT FLIPPED.** The real rerun scored
**2/5**, down from the 3/5 baseline: H-02 and H-04 remained detected,
H-03 remained missed, and H-05 was absent from this generation sample.
The five real `req-3-all-valid-inputs` structural properties all targeted
`Float128` functions (`add`, `decode`, `div`, `divL`, and `eq`); none
targeted `Ln.ln`. Semantic generation covered other `Ln` behavior but did
not generate its invalid-domain obligation. Thus the paragraph above's
"if it independently fires" assumption was false on the real checkout.
The reclassification is now an **RTF applicability/routing gap**: the
guidance was never invoked for the relevant function, so this run does
not support the earlier "structurally addressed" conclusion. Full result:
`RTF_V3_LIVE_FORTE_RERUN_RESULT.md`.

---

## Summary table

| Miss | Prior classification | This effort's reclassification | Status after Phases 3-6 (updated 2026-08-16 with live results) |
|---|---|---|---|
| Canto H-01 | `INVESTIGATION_REASONING_GAP` | Confirmed, unchanged | **LIVE-CONFIRMED FLIPPED**: real DetectGrader 2/2 (was 1/2). `RTF_V3_LIVE_CANTO_RERUN_RESULT.md` |
| Forte H-03 | Hybrid (weak property + reasoning) | **`RTF_APPLICABILITY_GAP` live-confirmed** | **NOT FLIPPED**: real DetectGrader 2/5 (was 3/5); no property routed `Ln.ln` invalid inputs. `RTF_V3_LIVE_FORTE_RERUN_RESULT.md` |
| Phi H-03 | `REQUIREMENT_TAXONOMY_GAP` | **`RTF_APPLICABILITY_GAP`** (reclassified, evidence-based) | **LIVE-CONFIRMED FLIPPED**: real DetectGrader 5/6 (was 4/6), via an in-contract path (`_getCuratorData`) this document originally didn't credit. `RTF_V3_LIVE_PHI_RERUN_RESULT.md` |

All three misses now have live re-graded evidence. Canto H-01 and Phi
H-03 flipped; Forte H-03 did not. Forte also fell from 3/5 to 2/5 because
H-05 was not present in this generation sample, while baseline detections
H-02 and H-04 remained stable.
