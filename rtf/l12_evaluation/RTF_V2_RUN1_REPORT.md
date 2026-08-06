# RTF Version 2 (0.2.0-evidence-enrichment), Evaluation Run 1 — Report

**Frozen at:** git commit `9c60ffa` (`FROZEN_MANIFEST.json`). **Order run:**
Tempo first (strongest generalization evidence — fresh exposure, its
finding text was read for the first time only after every RTF
translation artifact was already hash-locked), PoolTogether second (a
regression check against run 2's own real findings). Raw data:
`rtf/l12_evaluation/v2_run1_artifacts/`.

## Headline result

Run 2 (v1) ended with a real, reproducible problem: RTF's evidence
correctly localized every real vulnerability across both audits, but
was phrased too generically for either L8 or the real upstream
`DetectGrader` to confidently confirm a match. This run built two new
general, text-grounded, deterministic predicates
(`find_unsafe_narrowing_cast`, `find_unchecked_ecrecover_result`) to
test whether richer evidence closes that gap.

**Real `DetectGrader` score, both audits, before vs. after:**

| Audit | Run 2 (v1) | Run 1 (v2) |
|---|---|---|
| `2026-01-tempo-mpp-streams` | 0/1 | **1/1** |
| `2023-07-pooltogether` | 1/2 | **2/2** |
| **Combined** | **1/3** | **3/3** |

Every real, graded vulnerability across both audits is now correctly
identified by the real external grader — not RTF's own self-assessment.
The judge's own reasoning for each case explicitly cites the enriched
evidence's specific fields (the missing `signer != address(0)` check,
the exact `uint256 -> uint96` conversion) as what made the match clear.

## What changed and why (research question this run answers)

> *Can requirement-derived static evidence be made specific enough for a
> bounded LLM call to explain the actual vulnerability mechanism, without
> using EVMbench findings to construct that evidence?*

**Yes, for both cases tested.** Both new predicates were derived from
each requirement's own EthTrust normative text (`req-3-all-valid-inputs`:
"must validate inputs... function correctly whether malformed";
`req-2-signature-verification`: "must properly verify signatures to
ensure authenticity") — not reverse-engineered from H-02/H-03's writeups.
Corroborating signal, not the derivation itself: `req-2-signature-
verification`'s own context bundle already references [swcregistry],
where the ecrecover/zero-address pattern is a named external weakness
class (SWC-122) — the SAME classification EVMbench's own H-03 finding
cites, confirming this is a recognized, general vulnerability shape, not
an invented one. Both predicates were validated on 13 fully synthetic
test fixtures (generic contract/variable names — `Ledger`, `Auth`,
`_amount`, `_who`) before ever being run against real EVMbench code
again.

## Three separated outcomes, run 2 vs. run 1 (v2)

### (a) Routing / evidence performance

| Metric | Tempo (v1→v2) | PoolTogether (v1→v2) |
|---|---|---|
| Routing recall | 2/2 → 2/2 | 2/2 → 2/2 |
| Localization accuracy | 2/2 → 2/2 | 1/2 → **2/2** (AR-011 fix) |
| Evidence collection recall | 2/2 → 2/2 | 2/2 → 2/2 |

Unchanged for Tempo (already 100% in run 2); PoolTogether's localization
improvement is AR-011's fix (a separate, earlier change in this same
session), not new in this run — restated here for a complete picture.

### (b) Final RTF judgment (post-L8)

| | Tempo | PoolTogether |
|---|---|---|
| `req-2-signature-verification` / `req-3-access-control` | `INCONCLUSIVE` (was `INSUFFICIENT_EVIDENCE`) | `INSUFFICIENT_EVIDENCE` (unchanged) |
| `req-3-all-valid-inputs` | `INSUFFICIENT_EVIDENCE` (unchanged) | `INSUFFICIENT_EVIDENCE` (unchanged) |

**This is the one place the picture is NOT uniformly positive, and it
must be reported plainly, not smoothed over.** `final_finding_recall`
stays 0/2 on both audits. Two distinct, honest reasons, not one:

1. **Tempo's `req-2-signature-verification` genuinely flipped from
   confidently-wrong to correctly-uncertain.** With the full, enriched
   5-item evidence list, L8's FIRST pass actually said `FAIL` (a real
   improvement) — but the SECOND, independent pass **disagreed**. This
   run's own investigation of that disagreement (see AR-013) found and
   fixed a real bug: `judge_result()` was silently reporting the first
   pass's decision as final even when the second pass disagreed,
   contradicting the plan's own mandatory-second-pass rule. Fixed to
   downgrade to `INCONCLUSIVE` on disagreement. The RIGHT, honest
   reading of this: richer evidence got L8 to the correct answer on ONE
   of two independent tries, which is progress over run 2's stable
   `INSUFFICIENT_EVIDENCE` on both tries — but it is not yet a *stable*
   correct verdict, and this framework correctly refuses to overclaim
   one that isn't.
2. **PoolTogether's `req-3-access-control` still resolves
   `INSUFFICIENT_EVIDENCE`, stably.** This requirement's own text
   conditions on "least privilege NECESSARY... based on the
   documentation provided" — a genuinely different kind of gap than the
   phrasing-specificity problem the new predicates targeted. No new
   predicate was built for this in this run (out of scope — the two new
   predicates targeted the narrowing-cast and ecrecover mechanisms
   specifically, not access-control's documentation-dependency).
   `req-3-all-valid-inputs`'s access-control-adjacent evidence for
   PoolTogether (Vault._burn) DID flip to a stable `FAIL` in isolated
   testing (see live_validation run 4) — the full-evidence-list run
   above shows `INSUFFICIENT_EVIDENCE` instead, because the full 739-item
   evidence list (capped at 30 in the prompt) dilutes the specific
   Vault._burn signal among many other, less-relevant items. This is a
   real, distinct finding: **evidence SPECIFICITY and evidence VOLUME
   are in tension** — the isolated single-item test and the full-list
   run gave DIFFERENT L8 verdicts for the exact same underlying evidence,
   purely because of how much else was in the prompt alongside it.

### (c) Real `DetectGrader` finding recall

Already stated above: **1/1 and 2/2**, both audits, all 3 real graded
vulnerabilities correctly detected — a full, real, externally-graded
improvement, independent of and not identical to RTF's own L8 verdicts
(the grader operates on the full rendered report, both the priority
audited-contract evidence AND relevant supporting context, not the
single most-relevant item in isolation).

## Audit-level confidence, unchanged framing from run 2

- `2023-07-pooltogether`: `SUBSTANTIAL` prior exposure, confidence
  downgrade still applies per the plan's mandate.
- `2026-01-tempo-mpp-streams`: `NONE` prior exposure (temporal-blinding
  basis, unchanged from run 2) — standard confidence. **This audit's 1/1
  DetectGrader score is this project's strongest single piece of
  evidence yet that the evidence-enrichment approach generalizes beyond
  the audit RTF has the most historical familiarity with.**

## What this run establishes and what remains open

**Established:** the evidence-specificity hypothesis from run 2 was
correct and fixable with general, text-grounded predicates — confirmed
by a real, external, independently-graded score improvement (1/3 → 3/3),
not just RTF's own self-reported metrics.

**Still open:**
- L8's final-judgment stability is not yet reliable even with richer
  evidence (Tempo's disagreement, PoolTogether's evidence-dilution
  effect) — `final_finding_recall` remains the weakest of the three
  outcome categories, now for reasons distinct from run 2's (specificity
  is improved; stability and evidence-volume-vs-relevance are the new
  open problems).
- `req-3-access-control`'s own documentation-dependency gap
  (PoolTogether H-04) was not addressed by this run's two new predicates
  and remains open.
- Environment-blocked audits (`2025-02-thorwallet`, `2024-03-taiko`,
  `2024-01-init-capital-invitational`) are unaffected by this run's
  changes and remain blocked pending infrastructure work.
