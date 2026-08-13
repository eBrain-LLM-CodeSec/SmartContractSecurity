# RTF v2 vs. simple Codex baseline: 5-entry live comparison

User-requested, run live via SLURM job `17215379` (submitted mid-run
after the interactive session's own allocation neared its time limit —
see commit history for the sbatch migration). Two loops ran in parallel:
`semantic_only_driver.run_semantic_investigation` (RTF v2,
`max_concurrent_investigations=4`, real in-scope filtering via each
audit's own scope) vs. `simple_baseline.run_simple_baseline_audit`
(single-shot, full-repo, non-RTF Codex session using the production
`detect.md` prompt) — both grading with the real `DetectGrader`,
`judge_model=openai/gpt-4.1` for both, across the same 5 small targets:
`2026-01-tempo-feeamm`, `2024-01-canto`, `2025-04-forte`, `2024-08-phi`,
`2025-01-liquid-ron`.

## Headline scoreboard

| Target | RTF v2 | Baseline | RTF v2 cost | Baseline cost |
|---|---|---|---|---|
| `tempo-feeamm` | 0/1 | 1/1 | $2.50 | $0.00* |
| `canto` | **1/2** | 2/2 | $1.17 | $0.30 |
| `forte` | 0/5 | 0/5 | $0.70 | $0.00* |
| `phi` | 1/6 | 2/6 | $0.84 | $1.67 |
| `liquid-ron` | 0/1 | 1/1 | $0.54 | $1.35 |
| **Total** | **2/15** | **6/15** | **$5.75** | **$3.32 (undercounted)** |

\* Baseline timed out on `tempo-feeamm` and `forte` (hit the full 1200s
ceiling); the harness's cost accounting only captures a completed turn's
usage, so $0.00 almost certainly understates real spend on those two —
flagged, not taken at face value.

**Honest bottom line: baseline won this round, 6/15 to 2/15, at
comparable-or-lower cost.** This is consistent with this project's own
prior finding (the pre-v2 4-audit RTF-vs-baseline comparison) that a
single continuous holistic Codex session is a genuinely strong bar that
a more structured, multi-call pipeline doesn't automatically beat. RTF
v2 did not change that overall picture. What it DID change, and what's
worth reporting precisely rather than folding into one score, is
detailed below.

## What actually happened, target by target (root-caused, not guessed)

### `tempo-feeamm` (0/1) — investigation-execution timeout, not a generation/reasoning failure

Traced in full in `RTF_V2_TEMPO_FEEAMM_ROOT_CAUSE.md`. Generation
proposed the exact correct property (`FeeAMM.burn` must transfer tokens
*after* debiting liquidity — the precise CEI ordering the real bug
violates). Grounding accepted it. Clustering placed it in a large,
8-property cluster that split twice to reach `max_split_depth=2`; that
final leaf's investigation genuinely started (27 real tool-call events)
but never completed a turn within `codex_timeout_s=600`, and the
harness's own exhaustion fallback resolved it to `INCONCLUSIVE` — never
actually evaluated. Verified against the real `FeeAMM.sol:252-258`: the
external transfer really does precede the state update. **This is a
resource-budget problem in one specific cluster, not a coverage or
reasoning gap.**

Separately, `tempo-feeamm`'s own checked-out repository has a **real
data-contamination issue**: its `test/FeeAmmBasicInvariant.t.sol` file
contains NatSpec comments that literally say "Should pass with or
without the reentrancy patch" — naming the vulnerability class and a
"patch" that shouldn't be known pre-audit. Both pipelines get equal,
full repo access, so both were equally exposed; baseline's holistic
session apparently used this hint (whether directly or as ambient
context), RTF v2's cluster-scoped investigation did not. Checked the
other 4 targets' full source trees for the same pattern — none found.
This single result pair should be treated as compromised, not a clean
signal either way.

### `canto` (1/2) — a real, independent recall win over RTF v1

RTF v2 caught **H-01** (the block-number-vs-timestamp epoch bug in
`LendingLedger.update_market`) — the exact bug class the pre-v2
architecture scored **0/2** on historically, explicitly because
EthTrust's static requirement corpus had no clause shaped to ask this
specific economic-logic question (see prior-session memory,
`project_rtf_agentic_architecture.md`'s "primarily E" classification).
RTF v2's semantic generation closed that specific, previously-documented
gap. It missed H-02 (a subtler `nextEpoch` off-by-one loop-indexing bug)
— a genuine, different-mechanism miss, not investigated further this
session.

### `forte` (0/5, tied with baseline's 0/5)

Neither pipeline found anything on forte's five arithmetic-library bugs
(`Float128`/`Ln` fixed-point math edge cases). This matches this
project's own prior finding on the same audit with the pre-v2
architecture ("forte 0/5=0/5... all tied") — not a new RTF v2-specific
weakness. Not root-caused further this session (lower priority given the
symmetric result); a natural next step if this line of investigation
continues.

### `phi` (1/6 vs. baseline's 2/6)

RTF v2 caught H-07 (`updateArtSettings` using `onlyArtCreator` instead of
`onlyOwner`, letting artists modify royalties/soulbound/URI post-mint) —
the same finding baseline also caught. Baseline additionally caught one
more (not root-caused this session). RTF v2 missed H-01-H-04/H-06
(cross-chain signature replay, `createArt` signature reuse, curator
`EnumerableMap` DoS-via-bloat, `endTime` re-extension backrun, reentrancy
in `createCred`/`buyShareCred`) — five genuinely different bug classes,
not investigated further this session for root cause.

### `liquid-ron` (0/1 this run — contrast with an earlier, separate 1/1)

Earlier in this same session, a dedicated, separate live run
(`RTF_V2_LIVE_VALIDATION_REAL_TARGET_CONFIRMED.md`) scored **1/1** on
this exact target: the generator proposed a cleanly-worded property
("totalAssets must equal assets-in-vault+staked+rewards **minus**
operatorFeeAmount") that directly named the violation, and investigation
confirmed it FAIL.

**This run's generation call produced a different, worse-worded
property**: a compound statement merging two separate real ERC-4626
obligations ("totalAssets must **include**... accrued operator fees...
AND must not revert"). The investigator correctly evaluated both halves
independently — confirmed fee-inclusion as satisfied (per the property's
own stated requirement, which frames inclusion as CORRECT, inverted from
what the real economic bug needs) and found a second, genuinely real but
different bug (unguarded external calls in `totalAssets()` to
`roninStaking` that can revert under real conditions) for the FAIL.
Verified via the actual investigator transcript, not inferred.

**This is a real, honest reproducibility finding worth stating plainly:
semantic property generation is not deterministic in its exact framing
across independent runs on the same target**, and that framing quality
materially affects whether the resulting investigation lands on the
graded vulnerability. One run nailed it; this one didn't, on a property
that was merged/compound rather than singular and precise.

## What this comparison establishes, and what it doesn't

**Establishes**: RTF v2's semantic-generation layer works — it
repeatedly proposes real, targeted, non-generic properties from protocol
code/docs alone, and in at least two independently-confirmed cases
(`canto` H-01, `liquid-ron` H-01 in the earlier dedicated run) those
properties led to a correctly-graded detection of a bug class the
pre-v2, purely-structural architecture could not reach. It also
establishes concrete, fixable weaknesses: (1) cluster
investigation-execution can time out on complex/large clusters before
reaching max split depth, silently losing a well-formed property to
`INCONCLUSIVE`; (2) generated property wording is not perfectly
consistent run-to-run, and compound/merged properties can dilute a
finding's precision even when the underlying investigation reasoning is
correct.

**Does NOT establish**: that RTF v2 currently beats a strong single-shot
baseline in aggregate — it doesn't, on this 5-target sample (2/15 vs.
6/15). Does not establish generalization beyond these 5 small,
non-representative targets. Does not account for baseline's two $0.00
(likely undercounted) timeout costs fairly — a true apples-to-apples
cost comparison would need that fixed first.

## Honest disclosure: `tempo-feeamm` contamination

Investigated on explicit user request mid-run. Confirmed real (two
NatSpec comments in the checked-out repo's own test file name
"reentrancy" and reference "the patch"), confirmed isolated to this one
target (checked all 4 others' full source trees, no hits), and confirmed
it's a repo-level data-contamination issue available equally to both
pipelines, not a baseline-specific advantage by design. That target's
score pair should be excluded or asterisked in any headline comparison
number.

## Cost and time

Total real spend across both pipelines, all 5 targets: **~$9.07**
(RTF v2 $5.75 + baseline's reported $3.32, the latter understating two
timed-out runs' true cost). Total wall clock: ~89 minutes for the whole
job (both loops running in parallel with each other; each loop's own
5 targets ran sequentially within itself, per-target `wall_s` values
above).
