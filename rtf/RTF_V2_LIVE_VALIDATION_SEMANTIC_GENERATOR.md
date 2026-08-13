# RTF v2: first live-model validation of the semantic property generator

Every test in this branch up to this point used a fake `chat_client` (by
design — see `RTF_V2_ARCHITECTURE.md` section D). This is the first real
call against an actual OpenRouter model, run on request to check whether
the prompt/grounding logic holds up against real model output, not just
hand-written fixtures.

**Not a permanent test** — no assertions, run manually via a scratch
script (`/scratch/md5344/.claude/jobs/a22997fe/tmp/live_semantic_gen_check.py`,
not committed — it's a throwaway harness, not project code). This
document is the durable record of what it found.

## Setup

- Model: `z-ai/glm-5.2` via OpenRouter (the exact model this branch's
  `pilot5_driver.py`/`ablation_driver.py` already use for bounded JSON
  calls, per `CODEX_MODEL` — reused for consistency, not chosen fresh).
- Fixture: the same synthetic ERC-4626-shaped vault
  (`test_semantic_pipeline.py`'s `_VAULT_WITH_FEE_SOURCE`) plus a short
  README describing it as a fee-charging asset vault. The real bug: a
  `Vault.totalAssets()` that returns `totalAssetsHeld` without subtracting
  `accruedFees` — same shape as the real liquid-ron/H-01 miss this whole
  redesign was motivated by, but never told to the model or hard-coded
  anywhere in `semantic_property_generation.py`/`property_grounding.py`.
- Inputs given to the model: `generate_enriched_protocol_context_md`'s
  real output (Slither-derived facts + the README purpose excerpt) and a
  `ProjectManifest` of the compiled contract's real names. Nothing about
  "fees" or "totalAssets" being suspicious was hinted at beyond what the
  README itself says.

## Result

**8 properties proposed, 8 accepted at generation (0 rejected — no
verdict-shaped keys, all well-formed), 8 accepted at grounding (0
rejected — every reference real, every statement concretely grounded).**
Cost: **$0.00392**, 870 prompt / 1422 completion tokens, one call.

The model spontaneously proposed, unprompted:

> `semantic__accounting__1df9d981e766`: "Vault.totalAssets must return a
> value equal to Vault.totalAssetsHeld minus Vault.accruedFees, reflecting
> that accrued fees are deducted from assets available to depositors."
> (confidence 0.6, `reasoning_category=ARITHMETIC_VALUE_CORRECTNESS`)

This is exactly the invariant the fixture's synthetic bug violates
(`totalAssets()` does NOT subtract `accruedFees`) — reached purely from
the README's "charges a management fee ... accrues separately" sentence
plus the manifest's real state-variable names, with **no hand-written
"bad totalAssets" predicate anywhere in this diff** (the thing Section 22
of the task brief explicitly forbids).

The other 7 properties are also real, well-formed, and non-generic:
deposit/accrual/withdrawal accounting invariants, a cross-function
`STATE_CONSISTENCY` solvency invariant (`totalAssetsHeld >= accruedFees +
depositor claims`, spanning `deposit`/`accrueFee`/`withdrawFees` — the
kind of multi-function invariant a single-predicate/single-requirement
architecture structurally cannot express), and an
`EXTERNAL_CALL_INTERACTION` property about the fee-withdrawal
destination. One property used `property_type="semantic"` (one of the 3
deliberately under-specified types) and was correctly mapped to
`ARITHMETIC_VALUE_CORRECTNESS` via `categorize_generated_clause`'s
keyword fallback, confirming that fallback path works on live output too,
not just the hand-written unit test for it.

## What this validates

- The prompt's "propose what must hold, never a verdict" discipline held
  on a real model — zero verdict-shaped rejections, and reading the raw
  proposals confirms the model never used PASS/FAIL/vulnerable language.
- The grounding logic's false-positive rate on genuine, well-formed real
  output is 0/8 here — it didn't reject anything it shouldn't have.
  (Its false-NEGATIVE behavior — correctly rejecting genuinely bad
  output — is what the hand-written fixtures in
  `test_property_grounding.py` already cover; this run doesn't add
  evidence there since the model didn't produce any bad output to catch.)
- The core recall claim from `RTF_V2_ARCHITECTURE.md` section A.5/B holds
  in practice, not just in the architecture argument: a property targeting
  the exact real-world miss class this redesign was built for gets
  generated from protocol semantics alone, with zero requirement/predicate
  involvement.

## What this does NOT validate (explicitly, so it isn't overclaimed)

- Whether an investigating Codex agent, given this property inside a real
  cluster plan, would actually confirm the violation — that's a separate,
  not-yet-run step (grounding a property is not evidence of a finding,
  same discipline as everywhere else in this redesign).
- Whether this holds on a REAL EVMbench target (much larger, noisier
  protocol context, more distracting detail) rather than this small,
  clean synthetic fixture.
- The dedup-Jaccard threshold (0.3) and grounding rules' calibration
  against a broader distribution of real model output across many
  targets/models — this is one run, one model, one fixture.

## Next step

If this warrants continuing: wire `semantic_pipeline.build_full_property_pool`
into an actual driver and cluster+investigate this same fixture's
properties end-to-end (including the totalAssets one) to see whether a
real Codex investigation session, given the resulting cluster plan,
reaches `FAIL`. That's a materially larger, still-cheap next step (one
more LLM call plus a real Codex investigation), not yet run.
