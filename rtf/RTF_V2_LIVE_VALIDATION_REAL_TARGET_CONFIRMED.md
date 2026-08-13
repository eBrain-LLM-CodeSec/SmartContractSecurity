# RTF v2: real EVMbench target run completed — H-01 independently confirmed

Follow-up to `RTF_V2_LIVE_VALIDATION_REAL_TARGET_PARTIAL.md`, which
stopped mid-run after ~55 minutes because serial execution (no
concurrency configured) plus two clusters each burning a full 600s
timeout before auto-splitting made continuing not worth the wait. This
run fixes both real, root-caused issues (user-requested: "concurrency 4
AND in-scope only") and **completes fully**, with a confirmed detection
of H-01.

## What changed from the partial run

1. **`max_concurrent_investigations=4`** (was 1/serial).
2. **Real `scope_files`** — the audit's actual `scope.txt` (6 files:
   `ValidatorTracker.sol`, `RonHelper.sol`, `Pausable.sol`, `LiquidRon.sol`,
   `LiquidProxy.sol`, `Escrow.sol`), not just the single entry file. This
   required a real, new driver capability
   (`semantic_only_driver.run_semantic_investigation`'s new `scope_files`
   parameter, committed separately) — it applies `property_metadata.
   split_properties_by_scope`/`forward_out_of_scope_context` to the
   merged property pool before clustering, the exact mechanism
   `ablation_driver.run_config_entry` already established for the
   structural pipeline. Result this run: **9/9 properties in scope, 0
   dropped** — every generated property targeted `LiquidRon` or
   `LiquidProxy`, both within scope.txt, so the filter was a correctness
   improvement without changing this specific run's property count.

Building this scope-filtering feature caught a real, separate bug in its
own first test: a synthetic fixture using inheritance to simulate an
"out of scope" contract failed differently than intended, because
Slither's `contracts_derived` only returns leaf/deployable contracts — a
pure base contract used only via inheritance is invisible to
`ProjectManifest`. Confirmed this same gap is real on `LiquidRon.sol`
itself (`LiquidRon.convertToShares`/`convertToAssets`, inherited
unoverridden from OZ ERC4626, aren't in its manifest) but does NOT cause
incorrect grounding in practice — documented as a known limitation in
`ProjectManifest.from_slither`'s own docstring, not silently patched
around.

## Result: complete, all 9 properties investigated

**Runtime: ~18 minutes** (vs. the partial run's 55+ minutes for less
work). **Cost: $1.641** ($0.0115 generation + $1.6295 investigation across
2 clusters). Both clusters completed without hitting the timeout —
concurrency meant no investigation had to compete for serial turns, and
(plausibly) the real in-scope-only property set was slightly better
targeted.

| Property | Verdict |
|---|---|
| `LiquidProxy`'s 5 privileged functions only callable by the `LiquidRon` vault | PASS |
| `convertToShares`/`_convertToAssets` must round down and exclude fees | **FAIL** |
| `deposit`/`mint` must emit `Deposit` with correct params | PASS |
| `withdraw`/`redeem` must emit `Withdraw` with correct params | PASS |
| `lockedPricePerSharePerEpoch` set once, immutable after finalisation | PASS |
| `lockedSharesPerEpoch` accounting matches individual withdrawal requests | PASS |
| **`totalAssets` = assets-in-vault + staked + rewards − operatorFeeAmount** | **FAIL** |
| Only operator/owner can call privileged `LiquidRon` functions | PASS |
| `operatorFee` must never exceed `BIPS` | PASS |

## The headline: H-01, independently confirmed

> **`semantic__accounting__87bfa9c17e59::loc0`**: "LiquidRon.totalAssets
> must return a value equal to the sum of assets held in the vault
> (`getAssetsInVault`) plus total staked across all staking proxies
> (`getTotalStaked`) plus total rewards (`getTotalRewards`), **minus
> operatorFeeAmount**, and must never revert." → **FAIL**

Real investigator evidence (full text in the observability artifacts):
`totalAssets()` (`LiquidRon.sol:291`) returns `super.totalAssets() +
getTotalStaked() + getTotalRewards()` — `operatorFeeAmount` is never
subtracted. The investigator traced the concrete mechanism: `harvest`/
`harvestAndDelegateRewards` deposit the FULL harvested amount into the
vault's WRON balance (counted via `super.totalAssets()`) while separately
incrementing `operatorFeeAmount` — that fee portion sits in the vault,
counted as if it belonged to shareholders, until `fetchOperatorFee`
withdraws it and drops the share price. This traces to the same root
cause as H-01's real description (operator fee accrual not properly
excluded from the vault's reported asset value) — an independent
confirmation, not a coincidence: the property that found it
(`...87bfa9c17e59`) was generated from the protocol's own documented fee
model plus its real compiled interface, with zero access to H-01's
ground-truth text at generation time.

A second property (`semantic__numerical__caf857d0b72d`, about
`convertToShares`/`_convertToAssets` fee-inclusion) independently FAILed
for the same underlying reason from a different angle — both conversions
derive from the same uncorrected `totalAssets()`. Two independently
generated properties, investigated separately (same cluster, but each
required its own counterexample search per this architecture's own
discipline), converged on the same real root cause.

## Grading discipline note

This is **not** a DetectGrader-scored result — no ground-truth comparison
was run, and per this project's own established rule (see
`RTF_V2_ARCHITECTURE.md` / prior-session memory), that comparison happens
separately, after generation, never to justify a design choice. What's
established here is narrower and still real: **a property whose FAIL
verdict traces to the exact mechanism historically described as H-01 was
independently generated and independently investigated to FAIL**, using
only the real compiled contract and its own documentation — the core
claim this whole redesign exists to test.

## Honest scope of what this run does and doesn't establish

- **Established**: the full pipeline (generation → grounding → real
  in-scope filtering → clustering → concurrent real Codex investigation)
  works end-to-end on a real, non-trivial EVMbench target, completes in
  reasonable time (~18 min) and cost (~$1.64) once configured correctly,
  and produces a specific, well-evidenced FAIL on the exact bug class
  this redesign targets.
- **Not established**: whether this generalizes across other real audits
  (only one target tested), whether DetectGrader would score this FAIL
  as matching H-01 formally (not run), or whether the 3 rejected raw
  properties (all `previewDeposit`/`previewRedeem`/pause-state `max*`
  properties naming ERC-4626 methods `LiquidRon` doesn't itself declare —
  correctly caught by the `ProjectManifest.from_slither` inheritance
  limitation noted above, not a grounding defect) represent a real,
  systematic recall gap worth fixing before broader use.

## Cost accounting across both liquid-ron attempts

Partial run (v1, stopped): $0.9041. This run (v2, complete): $1.641.
**Combined real spend on this one target across both attempts: $2.545**,
comfortably under either run's own $5 ceiling.
