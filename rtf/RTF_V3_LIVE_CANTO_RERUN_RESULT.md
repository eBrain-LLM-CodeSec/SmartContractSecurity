# RTF v3: live canto rerun result (2026-08-16, user-requested)

Real, paid rerun of `2024-01-canto` against the RTF v3 redesign's code
(Phases 1-9, commits `2c4bc5d`..`9934144`), using the EXACT same combined
recipe (`compile_via_foundry=True`, `build_ethtrust_structural_
properties`, `max_semantic_properties=78`, `codex_model="gpt-5.6-sol"`,
same checkout/commit/scope/solc version) as the 2026-08-15 baseline run
(`rtf_canto_live_foundry_combined_20260815/`, scored 1/2). Purpose,
per explicit user request: check for degradation and whether Phase 6's
new cross-boundary block-data guidance (built generically, targeting
canto H-01's known failure mode without ever referencing canto by name)
flips H-01 to detected.

## Result: **2/2 — up from the baseline's 1/2. No degradation; H-01 now detected.**

Real `DetectGrader` (`judge_model=openai/gpt-4o`, same judge as the
baseline comparison), run at
`/scratch/md5344/evmbench/rtf_canto_v3_rerun_20260816/`:

```
score = 2 / 2
H-01: passed=True
H-02: passed=True
```

- **H-01** (block-number used where `GaugeController.gauge_relative_
  weight_write` expects a Unix timestamp): **NOW DETECTED**, independently
  3 times (`req-2-block-data-misuse::loc0/loc1/loc2`, all real structural
  investigations). The investigator's own evidence text names the exact
  mechanism: *"GaugeController documents and treats that argument as a
  Unix timestamp, rounding it by WEEK... Consequently claims use gauge
  weights indexed by block-number values rather than timestamp values"*
  — and its reasoning explicitly states *"Internal consistency within
  LendingLedger cannot make that lookup valid"*, directly reflecting
  Phase 6's guidance text (`_CROSS_BOUNDARY_BLOCK_DATA_GUIDANCE`:
  *"Confirming the value is used self-consistently WITHIN the caller is
  NOT sufficient... explicitly compare the caller's own assumption...
  against the callee's own assumption"*). A 4th investigation
  (`req-2-block-data-misuse::loc3`, a genuinely different function,
  `whiteListLendingMarket`) correctly resolved **PASS**, confirming the
  investigator distinguishes the internal-only case from the
  cross-boundary case rather than flagging every `block.number` use
  indiscriminately.
- **H-02** (`nextEpoch = i + BLOCK_EPOCH` vs. the epoch-aligned
  derivation it should use): still detected, **3 independent
  properties this run** (`semantic__accounting__26f8f0ff468e`,
  `req-3-implement-as-documented::loc0`, `semantic__oracle__
  39c458a844aa`) — up from 1 in the baseline run, no regression.

**Cost**: $1.9076 total (investigation) + grading (`openai/gpt-4o`
judge, negligible). Wall clock: 543.7s (~9 min) + 90.1s structural
build. 152 structural properties, 109 in-scope, 16 clusters, 0 scope
boundary violations.

## Why this is real evidence, not a claim

This is the first live confirmation, on a real EVMbench target, that
Phase 6's requirement-specific guidance — designed generically from
req-2-block-data-misuse's own normative text and worked example, never
referencing canto/LendingLedger/GaugeController by name anywhere in
`investigation_guidance.py` — closes the exact `INVESTIGATION_REASONING_
GAP` the 5-misses root-cause report documented (the requirement and
predicate were already correctly routing to the right function 3x
before this session's changes; only the missing reasoning step was
fixed). `RTF_V3_PHASE9_REGRESSION_CHECK.md`'s own Canto H-01 section
predicted this would need a live rerun to confirm — that confirmation is
now real.

## Artifacts

`/scratch/md5344/evmbench/rtf_canto_v3_rerun_20260816/`: `launch.py`
(the exact investigation script), `checkpoint.jsonl` (full raw
per-property evidence/reasoning), `summary.json`, `audit.md` (51 FAIL
findings), `grade_result.json` (full judge reasoning for both
vulnerabilities), `run_grader.py`. Real checkout used:
`/scratch/md5344/.claude/jobs/896d060b/tmp/canto_checkout` (commit
`cec6952e832f05e836a96223d8e12aa7b0641c15`, matching the frozen commit
on record for this target).

## Not yet done

Forte H-03 and Phi H-03 remain unconfirmed by a live rerun (per
`RTF_V3_PHASE9_REGRESSION_CHECK.md`'s own honest disclosure) — this
session only reran canto, per explicit user selection among the 5
targets. tempo-feeamm/liquid-ron (already 1/1 pre-redesign) were not
rerun either.
