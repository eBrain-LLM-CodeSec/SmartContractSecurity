# Track A — extraction results (L1–L7, six-requirement tranche)

This is the per-requirement extraction-results table the plan calls a
"first-class research output" (L6 deliverable, generalized here to cover
S and Q too since the findings are informative across all three levels).
Not yet done: L8 (shared LLM Judgment Layer implementation), L9 completion
audit, L10 maturity promotion, L11 (correspondence layer), L12
(evaluation execution), and step 3 (go/no-go against the quantitative
thresholds) — see "What's left" at the end.

| req_id | Level | L3 applicability basis | L4/L5/L6 classification | Strategy status |
|---|---|---|---|---|
| `req-1-compiler-060` | S | `logical_scope_entailment` (unconditioned) | Slither `solc-version`, `PARTIAL_MATCH` | **INCONCLUSIVE by design** when trigger fires — override references a different spec version (V2) we don't have; correctly refuses to guess FAIL |
| `req-1-eip155-chainid` | S | `explicit_spec_language` (predicate-embedded restriction, not subject-embedded — see AR-001) | Slither `NO_MATCH` (confirmed); Mythril/Semgrep `NOT_EVALUATED` | **`AMBIGUOUS_TEXT_GAP` on applicability** — the only genuine "spec text doesn't support derivation" case in the tranche; converges toward semantic review despite being Level S |
| `req-1-compiler-sol-2021-4` | S | `explicit_spec_language` | Slither `PARTIAL_MATCH` (candidate generator only) | **Sound derivation, not yet implemented** — both components (UDVT-width predicate, exact-version check) are legitimately text-grounded, just not coded yet |
| `req-2-verify-exact-balance-check` | M | `explicit_spec_language` | `DETERMINISTIC_TRIGGER_SEMANTIC_CONDITION`, narrow/clean trigger | Sound derivation, components not yet implemented (needs L8) |
| `req-2-overflow-underflow` | M | `explicit_spec_language` (predicate-embedded restriction — AR-001) | `DETERMINISTIC_TRIGGER_SEMANTIC_CONDITION`, but **coarse/over-inclusive trigger** — selection-time proxy underestimated how routable this looked | Sound derivation, heavier semantic-reviewer burden than the other M candidate; components not yet implemented |
| `req-3-implement-as-documented` | Q | `explicit_spec_language` (unconditioned; applicability ≠ assessability) | L7 rubric fully specified, not executed | Needs L8 + a real target repo to run |

## What this six-requirement sample already answers

**Headline research question** (*how much of EthTrust can be translated
faithfully without introducing unsupported interpretation?*): of six
requirements pushed through the full mechanism, **zero required an
invented heuristic to reach their current state.** Every gap encountered
was logged as one of three honestly-distinguished kinds, not collapsed
into a single "couldn't do it":
1. **Out-of-scope external dependency** (`req-1-compiler-060`'s override
   lives in a different spec version we haven't acquired).
2. **Sound derivation, not yet engineered** (`req-1-compiler-sol-2021-4`,
   both M requirements, the Q rubric) — the *translation* succeeded; only
   the *implementation* is pending.
3. **Genuine text-derivation limit** (`req-1-eip155-chainid`'s
   applicability condition) — the one case where the spec's own text
   doesn't support a deterministic predicate without importing outside
   Solidity-ecosystem convention knowledge, honestly flagged rather than
   papered over.

**On Level M routing extraction** (the plan's explicit open research
question): both M requirements resolved to `DETERMINISTIC_TRIGGER_
SEMANTIC_CONDITION`, but with a real and informative difference in trigger
*precision* — one narrow and clean, one coarse enough that the "semantic"
half of the split has to do more work than a bounded exception check.
This is exactly the kind of nuance the plan predicted disagreement/
gradient at the DETERMINISTIC_TRIGGER_SEMANTIC_CONDITION / FULL_SEMANTIC_
REVIEW boundary would surface — and it surfaced on the very first attempt,
on a requirement (`req-2-overflow-underflow`) that the cheap, mechanical,
non-cherry-picking selection-time proxy had actually predicted would be
the "hard, unroutable" one. The selection proxy underestimating routability
here is a feature of the design working as intended (selection stayed
non-cherry-picked; the *actual* classification work is what's allowed to
disagree with it), not a flaw to fix.

**On the S/M/Q-is-not-a-verification-method-axis thesis**: strongly
reconfirmed. `req-1-eip155-chainid` (Level S) ended up needing something
structurally like semantic review, while both Level M requirements
resolved to a clean deterministic-trigger-plus-narrow-semantic-condition
shape — level alone predicted nothing about translation difficulty.

## What's left before Track A step 3 (go/no-go)

- **L8**: build the actual shared LLM Judgment Layer (schema validation,
  citation-existence checks, second-pass disagreement detection, stability
  testing, pinned versions, caching). Every `llm_condition_review`/
  `llm_full_semantic_review`/Q-rubric component in this tranche is
  currently specified but unexecuted, blocked on this.
- **L9 audit**: one entry logged so far (`AR-001`, the L1-flag limitation).
  Needs a completeness pass once L8 exists and produces its own logged
  assumptions.
- **L11**: the EVMbench correspondence layer, including the exposure
  declaration and (given this project's prior MGPR work on this same
  corpus) the required personnel-separation step — not started.
- **L12 / step 3**: no evaluation has run yet; the quantitative go/no-go
  thresholds (100% derivation-trace coverage, 100% applicability-log
  coverage, etc.) can be partially checked already (traces/logs exist for
  every requirement above) but citation-validity and LLM-stability metrics
  are undefined until L8 exists and actually runs.
