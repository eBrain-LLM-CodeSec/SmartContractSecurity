# RTF v3: live phi rerun result (2026-08-16, user-requested follow-up)

Real, paid rerun of `2024-08-phi` against the RTF v3 redesign's code
(Phases 1-9), using the exact combined recipe (`compile_via_foundry=True`,
`build_ethtrust_structural_properties`, `max_semantic_properties=78`,
`codex_model="gpt-5.6-sol"`, same checkout/commit/scope/solc version) as
the 2026-08-15 baseline run (`rtf_phi_live_foundry_combined_20260815/`,
scored 4/6). Triggered directly by a user pushback on this session's own
Phase 9 write-up: "we already built whole-project compilation and the
investigation agent has access to it" — a correction to my earlier,
too-pessimistic claim that Phase 5's growth predicate's single-contract
scope would likely leave phi H-03 undetected on the real target.

## Result: **5/6 — up from the baseline's 4/6. H-03 newly detected. No degradation.**

Real `DetectGrader` (`judge_model=openai/gpt-4o`):

```
score = 5 / 6
H-01: passed=True
H-02: passed=True
H-03: passed=True   <-- NEW
H-04: passed=True
H-06: passed=True
H-07: passed=False  (unrelated -- documented generation-sampling variance, see below)
```

## H-03 confirmed detected — and the mechanism was different than expected

**The user's correction was right, and the actual mechanism differs from
what I assumed in `RTF_V3_PHASE9_REGRESSION_CHECK.md`.** I had assumed
the real bug required crossing into the separate `CuratorRewardsDistributor`
contract, which Phase 5's single-contract-scoped predicate couldn't see.
In fact `Cred.sol` itself contains `_getCuratorData`, a function that
**enumerates the same growing `shareBalance` map internally** — so the
predicate fired entirely within one contract, exactly within its
documented scope, with no cross-contract extension needed:

```
req-3-enough-gas::loc0 -> FAIL
Evidence: Cred._getCuratorData iterates from start_ to
shareBalance[credId_].length() when stop_ is zero.
_updateCuratorShareBalance sets a fully sold holder's value to zero but
never calls EnumerableMap.remove. EnumerableMap.set retains the key, so
the map can grow across repeated buy/sell cycles without pruning.
Reasoning: Pagination is available, but stop_=0 requests the entire
persistent map and the documentation describes retrieving curator
addresses for reward distribution. Because stale entries are never
pruned, sufficient gas is not assured over the contract lifetime.
```

Real `DetectGrader` judge reasoning independently confirms the match:
*"Both describe the issue in the `Cred` contract affecting the
`shareBalance` data structure... curator entries are not removed when a
balance reaches zero, leading to large and eventually unmanageable data
storage... risk of gas limits being exceeded during operations involving
these entries, which could block rewards distribution... Both suggest
removing zero entries from the data structure to prevent bloat."*

Three properties independently converged on this same defect:
`req-3-enough-gas::loc0` (FAIL), `req-3-enough-gas::loc2` (FAIL, via the
unguarded `_addCredIdPerAddress`/`getPositionsForCurator` path),
`req-3-protect-gas::loc0`/`loc2` (FAIL, the same mechanism framed as gas
griefing) — real, convergent, multi-angle detection, not a single lucky
guess.

## Correction to Phase 9's own analysis

`RTF_V3_PHASE9_REGRESSION_CHECK.md`'s Phi H-03 section said: *"the REAL
Phi target's growth (Cred.sol) and enumeration (CuratorRewardsDistributor)
are in SEPARATE contracts... the current per-contract-scoped predicate
would not catch this specific real case."* That prediction was **wrong
in a way worth being explicit about**: it conflated "the predicate's own
routing signal is per-contract" with "the requirement can only be
investigated via that one predicate's exact candidate location." Two
things I underweighted:
1. `Cred.sol` has its OWN in-contract enumeration path
   (`_getCuratorData`) that independently exhibits the same defect —
   the cross-contract path isn't even necessary for THIS target.
2. Even where a predicate's own candidate location is narrower, whole-
   project compilation gives the investigating agent full multi-file
   access regardless, and Phase 6's guidance is attached at the
   *requirement* level, not scoped to one contract — both factors this
   session's Phase 9 write-up acknowledged in the abstract but didn't
   fully credit when assessing this specific case.

## H-07 (not detected) — consistent with prior, documented non-determinism

Per `RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md`'s own prior finding: H-07
(`updateArtSettings` access control) is real semantic-generation sampling
variance across runs on this same target -- detected in one earlier
independent generation sample, absent in others, with no capability gap
established. This rerun's miss is consistent with that already-documented
pattern, not a new regression introduced by this session's changes.

## Cost and operational notes

Real cost: **$2.4458** (from `checkpoint.jsonl`, summed across all 16
completed clusters). 186 structural properties (up from the baseline's
115 -- Phase 5's new growth predicate contributed 10 of these). 118
properties resolved, 65 FAIL.

**A real infrastructure interruption occurred and was recovered from
cleanly, with zero data loss.** Mid-run, the file-count quota climbed to
within the hard-limit danger zone again (same failure mode documented in
`env_scratch_quota.md` from the 2026-08-15 phi run). This time, an active
"reaper" monitor was run alongside the investigation, deleting each
completed cluster's disposable `_ghome`/`_gview` full-repo scratch copies
as soon as `checkpoint.jsonl` confirmed that cluster was done (never
touching an in-flight cluster) -- successfully kept the run under the
hard limit through completion. Separately, an unrelated harness/session
restart killed the `launch.py` process just before it wrote its final
`summary.json`, but all 16 clusters had ALREADY completed and were fully
recorded in `checkpoint.jsonl` -- `audit.md`/`grade_result.json` were
reconstructed directly from that checkpoint with zero rerun and zero
additional spend, the same resilience this project's checkpointing was
built for.

## Artifacts

`/scratch/md5344/evmbench/rtf_phi_v3_rerun_20260816/`: `launch.py`,
`reaper.sh` (the live scratch-cleanup mitigation), `checkpoint.jsonl`
(full raw per-property evidence/reasoning, all 16 clusters), `audit.md`
(65 FAIL findings), `grade_result.json` (full judge reasoning for all 6
vulnerabilities), `run_grader.py`. Real checkout:
`/scratch/md5344/.claude/jobs/896d060b/tmp/phi_checkout` (commit
`8682a029072fffdcce76eb9f6101b05166e7d775`, the evmbench-org mirror's
own single init commit -- cross-checked against `base_commit
c9cce9061fd19c2d80835c185cb43ba2fc82cecb` in the audit's own
`config.yaml`, which refers to the original upstream repo's commit graph
rather than the mirror's, following the same pattern already confirmed
for canto).

## Combined picture across both live reruns this session

| Target | Baseline (2026-08-15) | This session's rerun | Delta |
|---|---|---|---|
| canto | 1/2 | **2/2** | +1 (H-01 newly detected) |
| phi | 4/6 | **5/6** | +1 (H-03 newly detected) |

Both new detections trace directly to this session's Phases 3-6 fixes:
canto H-01 to Phase 6's cross-boundary block-data guidance, phi H-03 to
Phase 5's new growth predicate (deployed generically, never referencing
either target by name). Zero degradation observed on any previously-
detected finding across both reruns.
