# RTF v2: first live run against a real EVMbench target (2025-01-liquid-ron) — partial, stopped by user

Follows the two synthetic-fixture live validations
(`RTF_V2_LIVE_VALIDATION_SEMANTIC_GENERATOR.md`,
`RTF_V2_LIVE_VALIDATION_E2E_INVESTIGATION.md`). This run targeted the
**real** `2025-01-liquid-ron` audit — the actual real-world case
(H-01, `totalAssets()`/operator-fee accounting) whose miss under the
pre-v2 architecture motivated this whole redesign (see
`RTF_V2_ARCHITECTURE.md` and prior-session memory). **Stopped
mid-investigation by explicit user request** after ~55 minutes, once it
became clear the remaining wall-clock time (due to a driver
misconfiguration, not an architectural limit — see "What went wrong"
below) wasn't worth the wait relative to what had already completed.
This document reports exactly what ran, what didn't, and why —
per Section 19's own discipline, a partial/inconclusive run is recorded
honestly, not glossed over.

## Setup

- Target: `2025-01-liquid-ron`, pinned commit `b0df3cf` (matches the
  frozen commit from prior sessions' preregistration), reused from an
  existing local checkout (`/scratch/md5344/.claude/jobs/506f33b3/tmp/
  mgpr_checkouts/2025-01-liquid-ron`) rather than re-cloning.
- Entry file: `src/LiquidRon.sol` (467 lines) — the same entry prior
  GP-generator validation used, and where the real H-01 bug lives.
  Compiled cleanly with `solc 0.8.20` before any paid call (zero-cost
  preflight, per this project's own established discipline).
- Semantic-only run (no EthTrust/ERC structural routing merged in — same
  scope choice as the synthetic-fixture runs; full structural+semantic
  merge is a separate, larger integration, not yet wired to a driver).
- `max_semantic_properties=12`, `codex_timeout_s=600`,
  `cost_ceiling_usd=5.0`. **`max_concurrent_investigations` left at its
  default of 1 (serial)** — this was the run's real bottleneck, see below.

## What was generated (before any investigation ran)

Property generation + grounding completed and clustered into **two
initial clusters of 5 properties each** (10 total, recovered from the
`.rtf/context/requirements/*.md` files each investigation's own scratch
copy carries — the top-level observability JSON dump never got written
since the run was killed before it completed). Both applicable-standard
detection and the accounting-relevant-state-variable heuristic correctly
picked up real ERC-4626 signal (properties reference `totalAssets`/
`totalSupply`/`convertToShares` — real methods on the real contract, not
invented).

**The two properties that matter most, generated with zero knowledge of
the ground truth:**

> `semantic__standard_conformance__14f6be530c46`: "LiquidRon.totalAssets
> must return a value that includes all assets delegated to staking
> proxies (via LiquidProxy) plus any assets held directly in the vault,
> and must not revert under any non-overflow condition."

> `semantic__accounting__eab12d1f0592`: "LiquidRon.harvest and
> LiquidRon.harvestAndDelegateRewards must collect all accrued rewards
> from every staking proxy and must correctly accrue operatorFeeAmount to
> feeRecipient based on operatorFee, **without diluting share value for
> existing depositors beyond the intended fee**."

The second one is, in substance, H-01: the real bug is that
`getTotalRewards()` subtracts the operator fee before adding rewards to
the total, so unpaid fees stay in vault custody but aren't reflected in
`totalAssets()` — exactly the "share value diluted/undercounted relative
to the intended fee" question this generated property asks. **This is
the headline result of this run**: the semantic generator, given only the
real compiled contract's manifest and its own protocol-context facts,
independently proposed the exact property whose violation IS H-01.

The other 8 properties are also real and non-generic: epoch-locked
withdrawal accounting, `convertToShares`/`convertToAssets`
caller-independence, `Deposit`/`Withdraw` event correctness,
pause-state `max*` behavior, an authorization property on
`setOperatorFee`/`updateOperator`/`updateFeeRecipient`, and a
state-consistency property on `deployStakingProxy`.

## What was investigated (and completed) before this run was stopped

Only **one** of the (eventually 6+) sub-cluster investigations finished:
`cluster_000_a`, covering 3 properties — **NOT** the two H-01-relevant
ones above (those were in the other initial cluster's sub-splits, which
were still timing out when the run was stopped).

| Property | Verdict | Confidence |
|---|---|---|
| `finaliseRonRewardsForEpoch` must set the locked price-per-share correctly and advance `withdrawalEpoch` | **PASS** | HIGH |
| `requestWithdrawal` must lock the user's shares until finalisation | **PASS** | HIGH |
| `convertToShares`/`convertToAssets` must not vary by caller or reflect slippage | **PASS** | HIGH |

All three PASSes carry real, specific evidence — exact line numbers
(`finaliseRonRewardsForEpoch (line 246-256)`), the actual call chain
through OpenZeppelin's `ERC4626._convertToAssets`, and an explicit
counterexample search for each (e.g., checking whether `totalSupply()`
is read before or after share-burning, whether any conversion path
references `msg.sender`). This is NOT a rubber stamp — full text
preserved in this branch's job scratch dir at time of writing
(`/scratch/md5344/.claude/jobs/a22997fe/tmp/live_liquidron_scratch/
2025-01-liquid-ron__LiquidRon__cluster_000_a_gout.txt`, not committed —
scratch, not project code).

**The two H-01-relevant properties (`...14f6be530c46`,
`...eab12d1f0592`) never reached a verdict.** This is an inconclusive
gap in this run, not a negative result — they were queued behind timed-
out sibling investigations when the run was stopped.

## What went wrong: why this took so long (root-caused, not guessed)

Reconstructed from real file timestamps in the scratch directory:

1. **`max_concurrent_investigations` was left at 1 (serial)** — the
   single biggest lever, and a driver configuration choice this run
   didn't set, not a hard limit. Every investigation ran strictly one
   after another.
2. **Both original clusters (`cluster_000`, `cluster_001`) appear to
   have hit the full `codex_timeout_s=600` (10 min) ceiling without
   completing a turn**, confirmed by their `gstream.jsonl` logs
   containing `turn.started` but no `turn.completed` event — each burned
   ~9-10 minutes before the existing automatic-split logic
   (`detect_split_reason`) kicked in and broke them into sub-clusters.
   That's ~20 minutes spent on two attempts that produced nothing usable
   before any real progress was made.
3. Automatic splitting then turned 2 planned investigations into up to
   6-8 sequential sub-investigations (each cluster can split up to
   `max_split_depth=2`), several of which (`cluster_000_b`) were
   *also* still timing out when the run was stopped — real repo
   complexity (a 467-line contract with real OpenZeppelin/Foundry
   dependencies, not a 20-line synthetic fixture) means each individual
   investigation naturally needs more exploration turns than the
   synthetic-fixture runs did.

None of this is an architectural defect in the RTF v2 design itself —
`run_semantic_investigation`/`live_runner.run_cluster_investigations_live`
both already support `max_concurrent_investigations>1` (built and tested
in an earlier session, per prior-session memory); this run simply didn't
use it.

## Real cost

**$0.9041 total** — $0.0228 for the one generation call (10 properties
proposed and grounded), $0.8813 for the one completed cluster
investigation. The timed-out attempts logged no completed turn and so
contributed ~$0 to `total_cost_usd` by this run's own accounting (their
real OpenRouter usage before being killed, if any, wasn't captured by the
`turn.completed` event this cost calculation depends on) — comfortably
under the $5 ceiling regardless.

## Honest assessment

This is a **real, partial, genuinely informative result**, not a full
validation:
- **Strong positive signal**: generation independently found the right
  property on a real target with a real historical miss, with zero
  benchmark-label involvement — the core claim this redesign exists to
  test.
- **Inconclusive**: whether investigation would have confirmed the
  violation is unknown — the relevant investigation never ran to
  completion.
- **Clear, fixable operational gap**: rerunning with
  `max_concurrent_investigations` set to something like 3-4 (already
  built, already tested against mocks — see `test_live_runner.py`'s
  concurrency tests from the prior session that built it) would let the
  remaining/repeat work finish in well under 20 minutes serial-equivalent
  time, likely for well under $2 more.

## Next step (not yet done, not yet authorized for this specific rerun)

Rerun `semantic_only_driver.run_semantic_investigation` against the same
target/entry file with `max_concurrent_investigations>=3`, specifically
to get a verdict on `semantic__accounting__eab12d1f0592` and
`semantic__standard_conformance__14f6be530c46`. Generation is cached
(same `audit_id`/protocol_context content → same cache key), so a rerun
would not re-spend the $0.02 generation cost, only new investigation
calls.
