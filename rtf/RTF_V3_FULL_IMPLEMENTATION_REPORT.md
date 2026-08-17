# RTF v3: full implementation report — every change, why, how, and results

First-hand report covering the RTF v3 requirement-fidelity redesign
(commits `2c4bc5d`..`9012c9f` on `rtf-v2-redesign`), organized by change
rather than by timeline. Companion documents referenced throughout are
the source of record for detail this report summarizes rather than
repeats: `RTF_V3_REDESIGN_PLAN.md` (the Phase-1 architecture trace and
plan), `RTF_V3_IMPLEMENTATION_STATUS_REPORT.md` (Phase 8's requirement-
support statistics), `RTF_V3_PHASE9_REGRESSION_CHECK.md`, and the three
`RTF_V3_LIVE_*_RERUN_RESULT.md` documents (the actual graded live runs).

This is distinct from `RTF_V2_WHOLE_PROJECT_COMPILE_IMPLEMENTATION_
REPORT.md`, a separate, earlier body of work (whole-project Foundry
compilation + EthTrust structural routing) done by a concurrent session
on this same branch; its own Section 13 addendum about this RTF v3 work
predates this document and used a since-superseded forte number (see
the Results section below for why).

## 0. The task, in one paragraph

The brief: RTF (the EthTrust Requirement Translation Framework) can have
the right EthTrust requirement and the right code in view, and still
fail — because the requirement's real obligation gets weakened, mis-
routed, or interpreted too narrowly somewhere in the pipeline. Three
known EVMbench misses (canto H-01, forte H-03, phi H-03) were given as
diagnostic examples, explicitly NOT as the design target — the mandate
was to audit the pipeline end-to-end first, fix the general architecture
where it loses meaning, and only then check whether the generic fixes
happen to close those three misses (they were never allowed to shape the
fixes themselves). No new intermediate requirement language was allowed;
every fix had to strengthen an existing stage.

## 1. Phase 1 — Architecture trace (read-only, before any code change)

Two parallel, read-only traces (documented in full in `RTF_V3_REDESIGN_
PLAN.md`) walked the pipeline from the raw EthTrust spec through to the
verdict parser. Headline findings, each later confirmed against real
code with file:line citations:

- **The corpus parser already extracts far more than reaches the
  investigator.** `l1_corpus/parse_spec.py` captures `exceptions_
  referenced`, `overriding_requirements`, `referenced_requirements`, and
  `explanatory_text` for every requirement — but `context_artifacts.
  generate_requirement_context_md` (the function that renders what the
  investigator actually reads) only used 4 of ~10 available fields. An
  applicable EthTrust "Overriding Requirement" — a first-class spec
  concept — was silently invisible.
- **Two parallel prompt-building paths with different fidelity.** The
  newer, grouped v2 path (`live_runner.py`) was richer but still capped
  by the gap above; an older, still-live single-property path
  (`codex_bridge.py`, used by `pilot5_driver.py`) forwarded only the bare
  normative sentence, with its own code comment admitting the richer
  field was "deliberately deferred."
- **Semantic-v2 (LLM-generated) properties were never anchored to any
  parent EthTrust requirement at all** — by the module's own docstring,
  they're derived purely from protocol facts/standards, with no
  `normative_text`/`explanatory_text` ever in scope. This is the literal
  code-level shape of "generated property could replace, not supplement,
  the original obligation."
- **No requirement-category-specific investigation guidance existed
  anywhere.** Every requirement — whether about cross-contract semantic
  contracts, input validation, or gas growth — got the exact same
  generic "investigate whether this holds" procedure text.
- **Negative result, verified, not just assumed**: zero EVMbench-target-
  specific hardcoding anywhere in the predicate layer or corpus parser.

## 2. Phase 2 — Mechanical fidelity audit of all 81 requirements

`l12_evaluation/requirement_fidelity_audit.py`: reads the real registry
and corpus directly (can't drift from code), classifies every
requirement into `UNIMPLEMENTED` / `PARTIAL` (documentary-evidence-only
applicability) / `IMPLEMENTED_UNTESTED` / `CONFORMANCE_PASS`. Baseline
(before any fix): 57 with a real structural predicate, 21 documentary-
evidence-only, 3 composite aggregates, **0 with an actual conformance
test** — the audit deliberately never assumed "parsed" meant "supported."

## 3. Phase 3 — Preserve the full obligation in the existing schema

**Why**: Phase 1's single biggest finding — exceptions/overrides/
references were parsed but dropped before reaching the investigator.

**How**: `context_artifacts.generate_requirement_context_md` now renders
`exceptions_referenced`/`overriding_requirements` (deduplicated by
`(req_id, relation)`, since the parser puts the same cross-reference in
both lists) and `referenced_requirements`, each clearly labeled and
visually separated from the normative text (RTF-added framing is never
mixed with official spec text). `codex_bridge.build_codex_prompt_inputs`
(the older single-property path) now reuses the SAME renderer instead of
forwarding a bare sentence, closing the second fidelity gap independently.

**A real regression was found and fixed while building this**: reusing
the richer text for `codex_bridge`'s single `requirement_text` field
also corrupted `derive_investigations.expand_investigation_instances`'
clause-splitter, which needs the bare normative sentence, not a markdown
block with headers — caught by the existing test suite before commit,
fixed by splitting into two fields (`requirement_text`, bare; `
requirement_context_text`, rich) rather than worked around.

**Tests**: 53 + 20 checks (`test_context_artifacts.py`, `test_codex_
bridge.py`), all new assertions plus the full pre-existing suite,
zero regressions.

## 4. Phase 4 — Anchor semantic properties to a parent requirement

**Why**: the Phase-1 finding above — semantic properties reach the
investigator with no parent obligation, so a narrowly-worded generated
property can never be checked against the requirement it's supposed to
be an angle on. This is forte H-03's real shape (traced in Phase 9): the
investigator named the exact defect and still resolved PASS because the
generated property's own wording asked only about "correctness," not
"rejection of invalid input."

**How**: `PropertyMetadata` gains `parent_requirement_id` (additive,
default `None`). `property_grounding.ground_semantic_property`
deterministically attaches a real static-corpus `req_id` sharing the
property's `reasoning_category` (reusing the EXISTING `ReasoningCategory`
taxonomy via a new `taxonomy.requirements_in_category` reverse lookup —
no new categorization scheme). `live_runner.prepare_cluster_
investigations` now also renders and ships the PARENT's own official
context markdown, not just the property's own synthetic context.
`generate_cluster_plan_md` surfaces a "Parent EthTrust obligation" line
plus a new `parent_obligation_check` schema field; `cluster_response_
validation.parent_obligation_check_is_sufficient` downgrades a PASS to
INCONCLUSIVE if a parent-linked property's PASS doesn't engage the
parent's obligation — the same downgrade mechanism the existing
counterexample-search-sufficiency gate already used, extended rather
than duplicated.

**Tests**: 48 + 47 + 60 checks across `test_property_grounding.py`,
`test_cluster_response_validation.py`, `test_context_artifacts.py`.

## 5. Phase 5 — Generic growing-persistent-structure predicate

**Why**: Phase 1's reclassification of phi H-03 — `req-3-enough-gas`
("Sufficient Gas MUST be available to work with data structures... that
grow over time") is a REAL, parsed, `AGENT_REQUIRED` corpus requirement,
not a taxonomy gap as the prior root-cause report concluded. Its only
predicate was a generic documentary-evidence collector with zero
code-pattern detection — applicability silently depended on whether a
target happened to document its own growth-management approach.

**How**: `l5_predicates.find_unbounded_growth_with_downstream_iteration`
— purely structural, verified against a real compiled fixture shaped
exactly like OpenZeppelin's EnumerableMap (`struct { bytes32[] _keys;
mapping(...) _values; }`), using generic method-name substring matching
(`.set(`/`.remove(`/`.push(`/etc.) that naturally catches `using-for`
library calls without ever resolving the call target or naming
"EnumerableMap"/"EnumerableSet" anywhere in the detection logic. Flags a
function that iterates a growth-capable container (dynamic array, plain
mapping, or any struct wrapping one) with an insertion path and no
detected removal path anywhere in the same contract. Registered
alongside (not replacing) the existing documentary-evidence collector
under both `req-3-enough-gas` and `req-3-protect-gas`.

**Tests**: 10 new predicate tests with 5 real-compile fixture pairs
(vulnerable/safe array, vulnerable/safe OZ-shaped struct-map, grown-but-
never-iterated negative control) — 141 total in `test_predicates.py`.

## 6. Phase 6 — Requirement-specific investigation guidance

**Why**: Phase 1's finding that every requirement gets identical generic
procedure text — canto H-01's real shape (traced in Phase 9): the exact
right requirement/predicate/function were already correctly connected
three times; no investigation ever asked the specific two-hop question a
cross-boundary block-data value requires.

**How**: new `investigation_guidance.py` — a small, explicit `req_id`-
keyed dict (NOT a new requirement language), 3 compact (≤10 line)
guidance blocks, each grounded in verbatim normative/explanatory text
cited in its own code comment: cross-boundary block-data semantics
(`req-2-block-data-misuse`/`req-2-random-enough`), input domain
validation (`req-3-all-valid-inputs`), growing persistent state/gas
(`req-3-enough-gas`/`req-3-protect-gas`). Applies to a property's own
`requirement_id` OR (Phase 4 synergy) its `parent_requirement_id`, so an
anchored semantic property gets both the dual-obligation check and the
matching guidance. Wired per-property (not cluster-wide) into `generate_
cluster_plan_md`, so a mixed cluster never leaks one property's guidance
onto another.

**Tests**: 37 new checks, including a mechanical banned-benchmark-
identifier scan over the guidance TEXT ITSELF (not just fixtures) and a
compactness check (constraint: no blanket "be more thorough" expansion).

## 7. Phase 7 — EthTrust conformance test suite + mutation testing

**Why**: the brief's own explicit critical deliverable — synthetic
Solidity fixtures built from official requirement text, independently of
EVMbench ground truth, proving detection end-to-end rather than by
architectural argument alone.

**How**: `rtf/tests/ethtrust_conformance/` — 6 real vulnerable/safe
fixture pairs for a representative slice (block-data cross-boundary,
input validation, gas growth, access control, external calls, one
static requirement), each provenance-commented with its exact `req_id`
and verbatim spec text. A two-tier harness: Tier 1 runs the REAL routing
pipeline with zero mocking (several requirements resolve a genuine
FAIL/PASS/NOT_APPLICABLE with no LLM at all, via `DETERMINISTIC_
COMPLETE` routing or the "unconditioned" absence-of-evidence path); Tier
2 runs the real property pool + real verdict-resolution plumbing with
only the final "what would the agent conclude" step scripted — the
"deterministic/mock LLM behavior for CI" the brief explicitly asked for.
Plus a 3-mutation-class proof of concept (remove access modifier / remove
domain validation / remove pruning path) showing that deliberately
breaking a real safe fixture is mechanically detected by the same
pipeline. The provenance-check scan caught two real issues live: a
fixture accidentally sharing the real Canto target's exact contract
name, and an overly-broad substring check false-positiving on the word
"phishable."

**Tests**: 167 (conformance) + 12 (mutation PoC) checks, all green.

## 8. Phase 8 — Requirement-level implementation status report

`RTF_V3_IMPLEMENTATION_STATUS_REPORT.md`: mechanically generated from
the Phase 2 audit script, re-run after Phases 3-7. Explicitly does NOT
claim all 81 requirements are supported — final state: 59 with a real
structural predicate (up from 57), 19 still documentary-evidence-only
(down from 21), 6 with a genuine end-to-end conformance test (up from
0), 53 still `IMPLEMENTED_UNTESTED`. Full by-level breakdown and
disclosed limitations (full-corpus coverage out of scope; Phase 5's
predicate is per-contract, not whole-project; Phase 6 covers 3 of 16
reasoning categories) in that document.

## 9. Phase 9 — Regression check against the 3 known misses (code-level, then live-confirmed)

Original Phase 9 (no live spend): traced whether Phases 3-6's fixes
structurally addressed each miss's documented root cause, honestly
flagging what would need a live rerun to confirm. Then, at explicit user
request, all three targets WERE rerun live — see the Results section
below for the real, graded numbers. The Phase 9 document itself was
updated in place with `UPDATE` annotations rather than silently rewritten
when live results arrived, including one place where the original
prediction was wrong (phi H-03's mechanism) and the correction is
preserved alongside the original text, not hidden.

---

# Results — every real, graded run

## Full 5-target picture

| Target | Baseline (pre-RTF-v3, 2026-08-15) | RTF v3 (this session) | Delta |
|---|---|---|---|
| tempo-feeamm | 1/1 | *not rerun* | — |
| canto | 1/2 | **2/2** | **+1** |
| forte | 3/5 | **2-4/5** (grading-noise range — see below) | **~0** |
| phi | 4/6 | **5/6** | **+1** |
| liquid-ron | 1/1 | *not rerun* | — |
| **Total (confirmed slots)** | **10/15** | **~11-12/15** | — |

tempo-feeamm and liquid-ron were already 1/1 pre-redesign and were not
selected for live rerun this session (user chose canto, phi, forte —
the three targets with a documented, unresolved miss). Their baseline
numbers are carried forward unverified against RTF v3, not claimed.

## Canto — real DetectGrader 2/2, up from 1/2

`RTF_V3_LIVE_CANTO_RERUN_RESULT.md`. **H-01 (block-number used where
`GaugeController` expects elapsed time) newly detected**, independently
3 times, with investigator evidence text directly mirroring Phase 6's
guidance language ("the caller's own assumption... against the callee's
own assumption"; "Internal consistency... cannot make that lookup
valid"). H-02 also detected (3 properties this run vs. 1 in the
baseline). Cost: $1.9076. This is canto H-01's first-ever detection
across every RTF architecture this project has tried, per the project's
own history.

## Phi — real DetectGrader 5/6, up from 4/6

`RTF_V3_LIVE_PHI_RERUN_RESULT.md`. **H-03 (`Cred.sol` `shareBalance`
`EnumerableMap` bloat DoS) newly detected** — via a mechanism different
from what Phase 9's original (pre-live-rerun) analysis assumed: `Cred.
sol` has its OWN in-contract enumeration function (`_getCuratorData`)
hitting the same growing map, so Phase 5's predicate fired within its
normal single-contract scope, with no cross-contract extension needed
on this real target. This corrected an over-pessimistic prediction in
the original Phase 9 write-up (documented as a corrected `UPDATE`, not
silently fixed). H-01/H-02/H-04/H-06 unchanged; H-07 still missed
(pre-existing, documented generation-sampling variance, confirmed via
this session's own checkpoint data showing zero mentions of
`updateArtSettings` anywhere in either run — not a new regression).
Cost: $2.4458.

**Real infrastructure recovery during this run**: a live scratch-reaper
kept the run under the file-count hard limit that crashed the prior
architecture's own phi run at this exact stage; separately, an unrelated
harness/session restart killed the launch process right before its
final summary write, but all 16 clusters had already completed and were
fully recorded in `checkpoint.jsonl` — the audit report and grade were
reconstructed with zero rerun, zero additional spend.

## Forte — real DetectGrader score range 2-4/5, no clear change from baseline's 3/5

`RTF_V3_LIVE_FORTE_RERUN_RESULT.md`, `RTF_V3_PHASE9_REGRESSION_CHECK.md`.
**H-03 (`Ln.ln()` accepts negative/zero input) NOT reliably detected.**
ONE real investigation was run ($3.2619, 811.9s, 115 structural
properties, 148 in-scope, 20 clusters). Its `audit.md` was then
independently graded 5 separate times (across two sessions working this
branch), returning scores of 3/5, 2/5, 3/5, 4/5, 2/5 — **H-01/H-02/H-04
were stable in every pass; H-03 and H-05 were NOT, despite the graded
input never changing.** This is a genuinely new, previously-undocumented
finding: DetectGrader judge-side non-determinism, distinct from the
already-known semantic-*generation* non-determinism (phi H-07's kind).
The underlying substantive finding is stable across all 5 passes
regardless of the score noise: none of the 5 real `req-3-all-valid-
inputs` structural properties targeted `Ln.ln` (all 5 targeted
`Float128`'s own functions instead), and semantic generation proposed
11 `Ln.sol`-touching properties this run, none framed as a domain-
validation claim. **Classification: `RTF_APPLICABILITY_GAP` — a
generation-coverage gap** (the right property was never proposed), a
genuinely different, harder failure class than canto H-01/phi H-03
(both of which flipped because the right property already existed and
just needed better reasoning guidance once it fired). Phase 4/6's fixes
cannot invent a property that generation never proposed — that's
future, separate scope (multiple independent generation samples +
deduplication, already flagged in `RTF_V3_REDESIGN_PLAN.md`).

## Total real spend this session (live reruns only)

$1.9076 (canto) + $2.4458 (phi) + $3.2619 (forte investigation) ≈
**$7.62**, plus a handful of cheap `openai/gpt-4o` judge calls for
grading (5 total forte grading passes, 1 each for canto/phi).

## What changed vs. what didn't

**Closed, live-confirmed**: canto H-01 (a reasoning-guidance gap), phi
H-03 (an applicability gap, though the real closing mechanism differed
from what was originally predicted). **Not closed**: forte H-03 (a
generation-coverage gap — a fundamentally different problem from what
Phases 3-6 were built to fix). **Zero degradation** on any previously-
detected finding across all three reruns — every FAIL that DetectGrader
credited in the pre-RTF-v3 baseline still resolved correctly this
session.

## Limitations carried forward

See `RTF_V3_IMPLEMENTATION_STATUS_REPORT.md`'s own Limitations section
for the full list (full-corpus conformance coverage, Phase 5's per-
contract scope, Phase 6's 3-of-16 category coverage). Added this
session: (1) DetectGrader judge non-determinism on borderline calls is
real and now documented, not previously known; (2) tempo-feeamm and
liquid-ron were never rerun on RTF v3 — their contribution to the "12/15
possible" total is a plausible-but-unverified assumption, not a live
result; (3) forte H-03 remains genuinely open — closing it needs
generation-reliability work (multi-sample + dedup), not another
translation-fidelity fix in this family.
