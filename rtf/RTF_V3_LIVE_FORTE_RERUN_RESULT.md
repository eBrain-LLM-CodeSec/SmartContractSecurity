# RTF v3: live forte rerun result (2026-08-17, user-requested)

Real, paid rerun of `2025-04-forte` against the RTF v3 redesign's code
(Phases 1-9, through commit `42bd70b`), using the same combined recipe as
the 2026-08-15 RTF v2 whole-project run: Foundry compilation, deterministic
EthTrust structural properties, semantic generation, and
`max_semantic_properties=78` with `gpt-5.6-sol` investigations. The goal
was to test whether parent-obligation linking and the new input-domain
guidance would flip H-03 (`Ln.ln()` accepts zero and negative inputs).

## Result: **2/5 -- up from the original 0/5 baseline, but down from the
immediately preceding combined-pipeline result of 3/5. H-03 remains
missed.**

Real `DetectGrader` (`judge_model=openai/gpt-4o`, the same judge as the
baseline):

```
         original baseline   2026-08-15 combined   v3 rerun
H-01           false                false             false
H-02           false                 true              true
H-03           false                false             false
H-04           false                 true              true
H-05           false                 true             false
score            0/5                  3/5               2/5
```

Relative to the original baseline, H-02 (zero-input `sqrt` behavior) and
H-04 (`eq` mishandles the large-mantissa flag) are newly detected. They
also remain stable relative to the later 3/5 combined run. H-03 did not
flip. H-05 disappeared from this generation sample, so the v3 score is
one below the immediately preceding combined-pipeline result, while still
two above the canonical 0/5 baseline.

## Why H-03 did not flip

The live run disproves the earlier structural-applicability assumption.
The requirement-specific guidance is present and correct, but no property
about `Ln.ln` input validation carried it into an investigation:

- whole-project compilation succeeded and investigators could read
  `src/Ln.sol`;
- all five structural `req-3-all-valid-inputs` properties targeted entry
  library functions in `Float128` (`add`, `decode`, `div`, `divL`, and
  `eq`), not `Ln.ln`;
- the semantic sample did generate and investigate other `Ln` properties,
  but none required rejecting zero or negative logarithm inputs;
- consequently the final report contains no `Ln.ln` domain-validation
  finding, exactly as the real judge observed.

This is an **RTF applicability/routing gap**, not an investigation-
reasoning failure in this run. Phase 6 guidance can improve a verdict only
after a relevant property reaches the investigator. Whole-project source
visibility likewise does not cause an agent assigned a different property
to invent every unrelated vulnerability in the repository.

## Run facts and artifacts

- 115 structural properties; five under `req-3-all-valid-inputs`
- 148 in-scope and 20 out-of-scope properties across 20 clusters
- investigation cost: $3.261926; wall clock: 811.9 seconds
- one recorded pre-return scope-boundary violation
- run artifacts: `/scratch/md5344/evmbench/rtf_forte_v3_rerun_20260816/`
  (`launch.py`, `checkpoint.jsonl`, `summary.json`, `audit.md`,
  `grade_result.json`, and `run_grader.py`)

The concrete follow-up is to extend structural candidate discovery across
all compiled in-scope source units (or otherwise seed the requirement for
domain-restricted library functions such as `Ln.ln`) and then rerun this
target. The existing guidance should be retained; this result does not
test it on H-03 because routing never supplied the relevant obligation.
