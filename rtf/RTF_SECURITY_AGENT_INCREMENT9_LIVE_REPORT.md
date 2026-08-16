# Security-agent Increment 9: live single-cluster validation

Date: 2026-08-16. Model: `z-ai/glm-5.2` through OpenRouter. User explicitly
authorized sending the synthetic fixture/context and incurring the small
charge. No EVMbench target source was sent: all runs used
`security_agent/fixtures/input_validation_ok/Fixture.sol`.

## Result

Three independent prompt variants all ended at the expected `PASS` for the
safe input-domain property. Each inspected the real fixture through the
Slither-backed tool layer, formed/refuted an invalid-input hypothesis, and
recorded zero/negative boundary attempts. Final tool-call counts were 1, 3,
and 1 respectively; the second repetition needed extra inspection after a
mechanically rejected citation.

Actual non-cached usage, including turns spent exposing and validating the
fixes below:

| Repetition | Live calls | Cached replay calls | Input | Output | Cost |
|---|---:|---:|---:|---:|---:|
| r1 | 3 | 0 | 4,598 | 791 | $0.001222521300 |
| r2 | 7 | 5 | 14,645 | 2,052 | $0.003433980132 |
| r3 | 5 | 3 | 9,328 | 1,740 | $0.003638413944 |
| **Total** | **15** | **8** | **28,571** | **4,583** | **$0.008294915376** |

Cached replay calls were local cache reads with no additional spend and are
excluded from token/cost totals.

## Bugs found live and fixed

1. **Rejected-conclusion evidence was discarded.** In r2 the model cited
   `"tool-1, tool-2"` as one invalid tool ID. The PASS gate correctly
   rejected it, but the next hypothesis update referenced the rejected
   conclusion's evidence and crashed on a dangling ID. Rejected verdicts now
   retain/upsert their evidence and hypotheses while leaving the verdict
   unresolved, allowing the same loop to repair the blocked fields. A
   deterministic regression reproduces this exact transition.
2. **A `Pending inspection` result counted as a counterexample.** R3's first
   PASS had a concrete attempt but a placeholder result. The gate previously
   checked only that an attempt record existed. It now requires at least one
   resolved, non-placeholder result of meaningful length; the replay was
   rejected until the model recorded the actual zero/negative guard outcome.
3. **Trajectory sequence reset on case replay.** `TrajectoryWriter` appended
   to an existing JSONL file but restarted numbering at 1. It now resumes
   from the last valid persisted sequence; a reopen regression test covers
   this. Historical r2/r3 files retain their original reset segments rather
   than being silently rewritten after the fact.

## Interpretation

The live vertical slice validates the owned model loop, typed tools, CEIV
answer boundary, first-class hypotheses/counterexamples, PASS gate, adapter,
cost accounting, and observability together. Three-of-three verdict agreement
on one small synthetic safe case is useful integration evidence, not a claim
about real-audit recall. The next paid milestone is the Codex A/B harness and
comparison; it remains separate from this result.
