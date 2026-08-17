# RTF v3: live forte rerun result (2026-08-16/17, user-requested)

Real, paid rerun of `2025-04-forte` against the RTF v3 redesign's code
(Phases 1-9), using the same combined recipe as the 2026-08-15 baseline
run (`rtf_forte_live_foundry_combined_20260815/`, scored 3/5): Foundry
compilation, deterministic EthTrust structural properties, semantic
generation (`max_semantic_properties=78`), `gpt-5.6-sol` investigations.
Goal: test whether Phase 4's parent-obligation linking and Phase 6's
input-domain-validation guidance flip H-03 (`Ln.ln()` accepts negative/
zero input without validation).

**Note on how this document came together**: two sessions were
independently working this same branch. ONE real investigation was run
(confirmed via file timestamps: `launch.py` written 00:18, `checkpoint.
jsonl`/`audit.md` finalized ~00:32, cost $3.261926, 811.9s wall clock) —
not two. That single `audit.md` was then independently graded by
`DetectGrader` multiple times by both sessions, and — unexpectedly —
**the grader itself did not return the same score twice**, surfacing a
real, separate finding documented below.

## Result: **the investigation itself is unambiguous. The DetectGrader score is NOT — it ranged 2/5 to 4/5 across 5 independent gradings of the SAME unchanged audit report.**

```
grading pass:        #1     #2     #3     #4     #5
H-01                False  False  False  False  False   <- stable, always missed
H-02                True   True   True   True   True    <- stable, always detected
H-03                False  False  False  True   False   <- UNSTABLE (1/5 detected)
H-04                True   True   True   True   True    <- stable, always detected
H-05                True   False  True   False  True     <- UNSTABLE (3/5 detected)
score                3/5    2/5    3/5    4/5    2/5
```

Compared against the 2026-08-15 baseline (also 3/5: H-02/H-04/H-05
detected, H-01/H-03 missed) and the canonical 0/5 baseline (nothing
detected): **H-01 and H-03 are consistently missed across every real
grading of this run; H-02 and H-04 are consistently detected, matching
the prior baseline exactly; H-05 and (in one pass) H-03 flip between
grading passes on IDENTICAL input.**

## H-03: the real, stable finding underneath the score noise

Regardless of which grading pass you read, the underlying evidence never
changed, and it's conclusive on why H-03 wasn't reliably caught:

- All 5 real structural `req-3-all-valid-inputs` properties targeted
  `Float128`'s own functions (`add`/`decode`/`div`/`divL`/`eq`) —
  **none targeted `Ln.ln`**, the function H-03 is actually about.
- The semantic generator proposed 11 properties touching `Ln.sol` this
  run, but all were framed around numerical precision/consistency
  (constant-encoding correctness, output-resolution loss, term-addition
  behavior) — **none asked "does `ln()` reject negative/zero input."**
- Pass #4's single `H-03: True` result is a genuine outlier: even that
  judge run's own reasoning (not separately inspected here — a real,
  disclosed gap in this write-up) would need to have matched something
  in the report to a claim about invalid-domain rejection that, per
  every other pass's independent read of the SAME report, isn't there.
  The honest read is that 4 of 5 passes (including 3 that agree with
  each other on every single vulnerability) are more likely correct than
  the 1 outlier, not that H-03 was "sometimes really detected."

**Classification: `RTF_APPLICABILITY_GAP` — a generation-coverage gap,
not a reasoning gap.** Phase 6's guidance can only improve a verdict
once a relevant property already exists and targets the right function;
neither Phase 4 nor Phase 6 can invent a property that generation never
proposed. This is a different, harder failure class than canto H-01 or
phi H-03 (both of which flipped because the right property/predicate
already existed and just needed better reasoning guidance once it fired).

## A separate, newly-surfaced finding: DetectGrader judge non-determinism

This is distinct from the already-documented semantic-*generation*
non-determinism (phi H-07's kind: two different LLM calls propose a
different property SET). Here, the property set and the full audit
report were byte-identical across all 5 gradings — only the LLM judge's
own borderline call on H-03/H-05 changed. **Practical implication: a
single DetectGrader run should not be treated as a definitive score for
a borderline case** — this session's own accidental 5x repeat-grading
(not a designed experiment) is the first real evidence of this specific
noise source in this project's history. Worth a deliberate, designed
follow-up (multiple grading passes + majority vote, mirroring the
generation-side mitigation already proposed for phi H-07) if precise
scores on borderline findings start mattering for real decisions.

## Run facts and artifacts

- 115 structural properties; 5 under `req-3-all-valid-inputs`
- 148 in-scope, 20 out-of-scope properties, across 20 clusters (2 split
  into `_a`/`_b` halves under budget pressure)
- investigation cost: $3.261926; wall clock: 811.9s (~13.5 min)
- one recorded scope-boundary violation (`req-2-overflow-underflow::
  clause0::loc5`, `not_in_known_scope_checked_pool`) — informational,
  did not block grading
- Live scratch-reaper mitigation used throughout (same as the phi
  rerun); no quota crash
- Real checkout: `/scratch/md5344/.claude/jobs/896d060b/tmp/forte_checkout`
  (commit `97a6a8b`, the evmbench-org mirror's own single init commit)
- Run artifacts: `/scratch/md5344/evmbench/rtf_forte_v3_rerun_20260816/`
  (`launch.py`, `reaper.sh`, `checkpoint.jsonl`, `summary.json`,
  `audit.md`, `grade_result.json`, `run_grader.py`)

## Combined picture across all 3 live reruns this session

| Target | Baseline (2026-08-15) | This session's rerun | Delta |
|---|---|---|---|
| canto | 1/2 | **2/2** | +1 (H-01 newly detected) |
| phi | 4/6 | **5/6** | +1 (H-03 newly detected) |
| forte | 3/5 | **2-4/5** (grading-noise range; 4/5 passes agree at 2-3/5) | ~0 (H-03 still missed in the great majority of gradings — real generation-coverage gap, not closed by this session's fixes) |

Two of three known misses closed; the third (forte H-03) is honestly
still open, and the live evidence now pinpoints exactly why — generation
never proposed the right property, a different failure class from what
Phases 4/6 were built to fix. The concrete next step, if pursued, is
generation reliability (multiple independent semantic-generation
samples + deduplication) — already flagged as separate, deferred scope
in `RTF_V3_REDESIGN_PLAN.md` and the original task brief's own
"Non-determinism" section.
