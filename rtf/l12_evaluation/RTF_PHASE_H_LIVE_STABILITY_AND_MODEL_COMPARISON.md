# Phase H work items 6-7: LLM stability + model comparison — live results

Executed exactly the design frozen in
`PHASE_H_STABILITY_EXPERIMENT_PREREGISTRATION.md`, BEFORE which model
would be preferred was decided. Total real spend across the whole Phase
H live-call session (calibration + A/B debugging + both experiment
runs): **$0.471** of a self-enforced $5.00 cap (account limit is
actually $300; nothing else would have stopped this automatically —
see `a4v/llm.py`'s new per-call `cost_usd` tracking and
`spend_guard.py`).

## A real bug found mid-experiment, not glossed over

The FIRST full run of this experiment (18 calls, $0.208) showed
`openai/gpt-5.1-codex-max` landing on `INCONCLUSIVE`/`INSUFFICIENT_EVIDENCE`
on every single case — including a case (`Vault._burn`'s real
narrowing-cast evidence, in isolation) that an earlier live-validation
run had already gotten a confident `FAIL` on with byte-identical
underlying evidence. Investigated before trusting any of that batch's
results:

1. **Hypothesis 1 (ruled out by direct test):** this session's own new
   `max_tokens=4096` pin (work item 1) suppressing the model's
   reasoning. A 3-way A/B call (uncapped / 4096 / 16000, identical
   prompt) gave the SAME `FAIL`/MEDIUM-confidence result all three ways
   — cleanly ruled out.
2. **Real cause, found by reconstructing the exact prompt text (free,
   deterministic) and comparing it side-by-side against the A/B test:**
   `evidence_ranking.py::build_evidence_bundles()` was taking a
   predicate's own concrete risk explanation (e.g. "values above X are
   silently truncated by this cast rather than rejected" — the single
   most informative part of the evidence) and filing it under the
   bundle's `limitations` field with a `"predicate-assessed risk (not
   an exploit claim): ..."` hedging prefix, instead of populating
   `possible_failure_mechanism` (the field meant to carry exactly this
   information) directly. This actively signaled uncertainty about a
   finding's own mechanism. **Fixed and confirmed with a live A/B
   re-test on the identical real evidence: `INSUFFICIENT_EVIDENCE`/LOW
   → `FAIL`/MEDIUM.** Logged as AR-016. This bug affected ALL 9 cases
   in the first run (all go through the bundle-rendering path) — that
   batch is superseded, not reported as a result below.

The full 18-call battery was then re-run after the fix ($0.263 more).
**All results below are from the POST-FIX run.**

## A second real, distinct issue found: citation validity is currently unmeasurable

Citation validity (a pre-registered metric) came back 0/12 (GPT) and
0/19 (GLM) — investigated rather than reported at face value. Cause:
`verify_evidence_citations()` expects a file-path-shaped `location`
(`"path/to/file.sol:line"`); RTF's evidence rendering has always used
`"Contract.function"` labels instead (e.g. `"Vault._burn"`). Both models
faithfully echoed back exactly the location string they were shown, which
the checker then treats as a literal, nonexistent file path and marks
invalid — every time, regardless of claim accuracy. **This is a
pre-existing internal format mismatch in RTF's own design, not a model
citation-quality problem** — logged as AR-017, left open (out of this
pass's scope to redesign location tracking mid-experiment). Citation
validity is NOT usable as a discriminating metric in this comparison as
a result.

## Results (post-fix), the 9 cases x 2 models

| Case | Expected | GPT (gpt-5.1-codex-max) | GLM (glm-5.2) |
|---|---|---|---|
| 1. Unsafe narrowing cast | FAIL | **FAIL** ✓ | INCONCLUSIVE ✗ |
| 2. Safe narrowing cast (bound-checked) | PASS | INSUFFICIENT_EVIDENCE ✗ | **PASS** ✓ |
| 3. Unchecked ecrecover | FAIL | INSUFFICIENT_EVIDENCE ✗ | INCONCLUSIVE ✗ |
| 4. Checked ecrecover | PASS | INSUFFICIENT_EVIDENCE ✗ | **PASS** ✓ |
| 5. Borderline (readonly-reentrancy candidate) | (none — uncertainty is valid) | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE |
| 6. Insufficient evidence (bare `block.timestamp`) | INSUFFICIENT_EVIDENCE | **INSUFFICIENT_EVIDENCE** ✓ | **INSUFFICIENT_EVIDENCE** ✓ |
| 7. PoolTogether `Vault._burn`, isolation | FAIL | **FAIL** ✓ | INCONCLUSIVE ✗ |
| 8. PoolTogether, full 30-bundle ranked set | FAIL | INSUFFICIENT_EVIDENCE ✗ | INCONCLUSIVE ✗ |
| 9. Tempo real evidence | (none) | INSUFFICIENT_EVIDENCE | INCONCLUSIVE |

**Match rate on the 7 cases with a fixed expected outcome:** GPT 3/7
(cases 1, 6, 7), GLM 3/7 (cases 2, 4, 6). Exactly tied, on DIFFERENT
cases — GPT correctly flags violations (narrowing casts) but hedges to
`INSUFFICIENT_EVIDENCE` on clear-PASS and ecrecover cases; GLM correctly
confirms clear-PASS cases but never returns a confident `FAIL` anywhere
in this experiment at all (consistent with the earlier v2-run-2 finding
that GLM is a measurably more conservative judge in both the L8 and
`DetectGrader` roles).

**Case 8 vs case 7 (GPT):** case 7 (isolated evidence) got `FAIL`; case
8 (the SAME evidence, now correctly ranked #1 of 30 bundles, per this
session's earlier ranking fix) got `INSUFFICIENT_EVIDENCE`. **The
ranking/bundling fix solved the EXCLUSION problem (the evidence now
reaches the prompt at all, confirmed deterministically without any live
call) but a real, still-open dilution effect persists at the judgment
level once 30 bundles' worth of context surrounds the relevant one** —
this is now demonstrated live, not just inferred, and is a genuinely
different, narrower problem than before (post-ranking dilution, not
pre-ranking exclusion).

## Pre-registered acceptance metrics

| Metric | GPT | GLM |
|---|---|---|
| First/second-pass agreement rate | 9/9 | 7/9 |
| Case 5/6 (borderline/insufficient-evidence) handled without false confidence | yes (2/2) | yes (2/2) |
| Citation validity | unmeasurable (AR-017) | unmeasurable (AR-017) |
| Total cost (18 calls) | $0.1968 | $0.0308 |
| Avg cost/call | $0.0109 | $0.0017 |

## Decision (applying the pre-registered rule mechanically, not re-litigated after seeing results)

The rule (frozen before running): switch away from
`openai/gpt-5.1-codex-max` only if `z-ai/glm-5.2` wins at least 3 of 4
criteria (agreement rate, borderline/insufficient-evidence handling,
citation validity, cost-as-tiebreaker-only).

- Agreement rate: **GPT wins** (9/9 vs 7/9).
- Borderline/insufficient-evidence handling: **tie**.
- Citation validity: **void** (AR-017 — not usable to decide either way).
- Cost: GLM is ~6x cheaper per call, but the rule states cost is a
  tiebreaker ONLY among otherwise-tied/winning criteria — it does not
  get to independently swing the decision.

GLM does not win 3 of 4 criteria (it wins zero outright, ties one, one
is void). **Per the pre-registered rule: keep `openai/gpt-5.1-codex-max`
as RTF's default L8 model.** This is reported as an honest tie on raw
match rate (3/7 each) with GLM's much lower cost noted for the record —
not treated as grounds to override the rule that was fixed before this
data existed.

## What this experiment establishes and leaves open

**Established:**
- The evidence-ranking/bundling fix from earlier in this Phase H pass
  measurably works at the deterministic layer (confirmed without any
  live call) — the excluded-evidence problem (raw index 737/739) is
  fixed.
- A real, separate implementation bug in bundle rendering
  (`possible_failure_mechanism` vs. hedged `limitations`) was found and
  fixed live, with before/after confirmation on identical evidence
  (AR-016) — this is now the more significant of the two evidence-layer
  fixes made this session.
- Citation validity, as currently measured, reflects a real but
  unrelated format mismatch (AR-017), not model or evidence quality —
  important to not misreport as a citation-quality failure.
- GPT and GLM are genuinely different, not one strictly better: GPT
  catches violations more reliably, GLM confirms clean/PASS cases more
  reliably and is far cheaper; neither wins the pre-registered
  comparison outright.

**Still open:**
- Cases 2-4 (PASS/violation-in-a-clean-context cases) show BOTH models
  struggling to reach a confident, correct verdict from single-item
  evidence alone, GPT more so than GLM — this looks like a genuine
  evidence-sufficiency gap (the model wants to see surrounding source
  code, not just a structured description), a different, more
  fundamental issue than ranking/bundling and NOT something this
  session's work addresses.
- Case 8's post-ranking dilution (evidence present and top-ranked, but
  still surrounded by 29 other bundles) needs the token/evidence-budget
  size itself investigated as a variable (work item 5's originally
  planned top-1/top-3/top-5-bundle comparison, not yet run).
- Work item 8 (verifier-vs-independent second-pass design comparison)
  and freezing RTF v3 (item 10) remain open.
