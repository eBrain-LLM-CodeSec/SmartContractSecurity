# Phase H work items 6-7: LLM stability + model comparison — pre-registration

**Written and frozen BEFORE any experimental call in this batch is made.**
Per work item 7's explicit rule ("must not become open-ended model
shopping... pre-register candidate models, repetition count, acceptance
metrics, and the decision rule for selecting a configuration BEFORE
running") and work item 9's acceptance-criteria-before-execution rule.

**Budget constraint (explicit user instruction, this session):** hard
cap of $5.00 total spend, self-enforced (the OpenRouter key's own
account limit is $300, not $5 — nothing stops calls automatically).
Enforcement: `a4v/llm.py`'s token log now records real per-call
`cost_usd` (from OpenRouter's `usage.cost`, confirmed present and
immediate — not the account `/auth/key` endpoint, which lags by
minutes). A spend-guard script sums the real, uncached log entries
before/after each case and hard-stops before $4.00 (leaving a $1.00
safety margin under the $5.00 cap). Calibration (2 real calls, already
spent, ~$0.012 total) showed per-call cost on the order of $0.01-0.025
for prompts in the few-hundred-to-few-thousand-token range this
experiment uses — the full design below (9 cases x 2 passes x 2 models
= 36 calls) is estimated at well under $1.00, leaving generous margin,
but every case is still gated on a live spend check, not the estimate
alone.

## Candidate models (fixed, not shopped)

Exactly the two models this project has ALREADY validated end-to-end in
prior runs — not a new search:
1. `openai/gpt-5.1-codex-max` — used for L8 in v2 run 1 and every prior
   live validation run.
2. `z-ai/glm-5.2` — used for L8 in v2 run 2 (the GLM judge-strictness
   comparison), already confirmed compatible with this project's
   fenced-JSON extraction call shape.

No other model is considered in this pass.

## The 9 fixed cases (frozen, not tuned after seeing any result)

All cases use REAL, already-produced RTF evidence (either fully
synthetic fixtures already used and reported in this project's prior
live-validation runs, per README's "Run 3"/"Run 4" sections, or the
REAL archived v2 run 1 evidence for Tempo/PoolTogether, requiring zero
new predicate execution). Nothing here is newly invented for this
experiment.

| # | Case | Source | req_id |
|---|---|---|---|
| 1 | Unsafe narrowing cast (clear violation) | synthetic, from `test_predicates.py`'s `find_unsafe_narrowing_cast` fixture shape | req-3-all-valid-inputs |
| 2 | Safe narrowing cast w/ correct bound check (clear pass) | synthetic, same predicate's negative fixture shape | req-3-all-valid-inputs |
| 3 | Unchecked ecrecover result (clear violation) | synthetic, from `find_unchecked_ecrecover_result`'s fixture shape | req-2-signature-verification |
| 4 | Correctly-checked ecrecover result (clear pass) | synthetic, same predicate's negative fixture shape | req-2-signature-verification |
| 5 | Genuinely borderline case | the SAME read-only-reentrancy candidate used in live_validation Run 3 (`LiquidationPair.maxAmountIn`) | req-2-avoid-readonly-reentrancy |
| 6 | Insufficient-evidence case | the SAME bare `block.timestamp` read used in live_validation Run 3 | req-2-block-data-misuse |
| 7 | PoolTogether relevant evidence, in ISOLATION | real: ONLY `Vault._burn`'s `find_unsafe_narrowing_cast` finding from the real archived v2 run 1 evidence | req-3-all-valid-inputs |
| 8 | PoolTogether relevant evidence, inside the FULL ranked bundle set | real: all 739 archived items, run through this session's new `rank_evidence`/`build_evidence_bundles`/`apply_evidence_budget` pipeline (budget=30) | req-3-all-valid-inputs |
| 9 | Tempo relevant evidence | real: all 5 archived `req-2-signature-verification` items (small enough that isolation vs. full-set is not a meaningful distinction for this case) | req-2-signature-verification |

Cases 1-4 are constructed to MIRROR the exact predicate output shape
already validated in `rtf/l5_predicates/test_predicates.py` (same
`structured` field keys/format) — not hand-waved prose, so this
experiment tests the LLM's handling of RTF's real evidence shape, not a
simplified stand-in.

## Repetition count

**Exactly 1 stability run per (case, model) pair**, using the existing,
already-implemented `judge_with_second_pass()` — which itself makes 2
independent calls (first pass + a cache-bypassed second pass) per run.
This is NOT the same as work item 6's own optional `judge_stability()`
n=10 repeated-run flip-rate test — that deeper stability sweep is
explicitly OUT OF SCOPE for this pass under the $5 budget (10 reruns x
9 cases x 2 models = 180 calls would consume the entire budget on this
one sub-experiment alone). What IS measured here — first-vs-second-pass
agreement, per-case decision, citation validity — is the minimum the
plan's own mandatory-second-pass rule already requires for every real
judgment, so it comes at no extra design cost.

Total calls: 9 cases x 2 passes x 2 models = **36 real API calls**,
each independently gated by the spend guard.

## Fixed settings (pinned, per work item 1's config-pinning discipline)

`temperature=0.0`, `top_p=1.0` (LLMJudgmentLayer's default pin),
`max_tokens=4096`, `use_second_pass=True`. Identical prompt template
(`build_judgment_prompt`/`build_judgment_question` or
`build_ranked_judgment_question` for cases 7-8, which need the ranking
pipeline) across both models — no per-model prompt tuning.

## Acceptance metrics recorded per (case, model)

- First-pass decision, second-pass decision, agreement (AGREE/DISAGREE).
- Final resolved conformance state (`resolve_conformance_from_judgment`).
- Whether the decision matches the case's PRE-STATED expectation (cases
  1-4 have an unambiguous expected decision; cases 5-9 do NOT — a
  confident PASS/FAIL there is itself a data point, not necessarily
  "correct" or "wrong", per the plan's explicit rule that
  INCONCLUSIVE/INSUFFICIENT_EVIDENCE are legitimate outcomes).
- Citation validity: whether `evidence[].location` values cited by the
  model correspond to locations actually present in the evidence it was
  given.
- `confidence` field returned.
- prompt/completion token counts and real `cost_usd` (now logged
  automatically per work item 1).

## Decision rule for selecting a configuration (fixed before running)

RTF's LIVE default model configuration (used in `LLMJudgmentLayer`'s
default construction going forward) is changed away from
`openai/gpt-5.1-codex-max` ONLY IF the alternative model
(`z-ai/glm-5.2`) demonstrates a clear win on AT LEAST 3 of these 4
criteria, none of which is "EVMbench score" or any benchmark-derived
signal:
1. Higher first/second-pass agreement rate across the 9 cases.
2. Correctly resolves cases 5-6 (borderline/insufficient-evidence) to
   INCONCLUSIVE/INSUFFICIENT_EVIDENCE rather than a falsely confident
   PASS/FAIL, at least as often as the comparison model.
3. Equal or better citation validity rate.
4. Lower or comparable cost per case, as a tiebreaker ONLY (never a
   primary criterion on its own).

If no model wins on 3+ criteria, the current default
(`openai/gpt-5.1-codex-max`) is kept, and the comparison is reported as
inconclusive-but-informative, not forced to a pick either way. This
rule is fixed now, before either model has been run on any of these 9
cases in this experiment.
