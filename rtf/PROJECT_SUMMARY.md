# RTF — Requirement Translation Framework: Project Summary

**What this is:** a standards-driven replacement for MGPR (the old
benchmark-fitted router in Agent4Vul). Instead of hand-tuning detection
rules against EVMbench findings, every analysis strategy is derived from
the **EEA EthTrust Security Levels Specification** (Version 3, Apache
2.0, verbatim-snapshotted). EVMbench is used only to *evaluate* the
result afterward — never to define it. Full design rationale, revision
history, and rejected alternatives: `/scratch/md5344/.claude/plans/ou-are-a-critical-purring-eich.md`.

**Status as of 2026-08-06 (updated again — RTF v2 run 1):** full
81-requirement corpus translated; 59/81 requirements have at least one
real, tested static predicate implemented (57 + 2 new evidence-enrichment
predicates this pass); L8 IS now wired into the orchestrator and
gate-checked. **Real, external `DetectGrader` recall across the 2 audits
evaluated so far: 3/3** (up from run 2's 1/3), driven by two new,
general, text-grounded predicates built specifically to fix a repeated
evidence-specificity gap run 2 found. Full latest report:
`rtf/l12_evaluation/RTF_V2_RUN1_REPORT.md`. Still narrow in scope (2 of
40 real audits; 3 more environment-blocked, though a real fix for that
was validated this pass — see `ENVIRONMENT_INVESTIGATION.md`) — see
"What has NOT been done" below. Full audit: `rtf/AUDIT_L0_L12.md`. Run 1
(superseded, kept for history) and its report remain below. Full first-
evaluation results and failure attribution:
`rtf/l12_evaluation/FIRST_EVALUATION_RESULT.json`,
`rtf/l12_evaluation/FAILURE_ATTRIBUTION_REPORT.md`.

---

## Architecture (L0–L12)

Spec ingestion (L0) → Requirement Corpus (L1) → Context Bundles (L2) →
Applicability classifier (L3) → Analyzer Matching (L4) → Level S
Strategy Compiler (L5) → Level M Extractor (L6) → Level Q Evidence
Assessor (L7) → shared LLM Judgment Layer (L8) → Assumptions Register
(L9) → Maturity/Versioning (L10) → EVMbench Correspondence (L11) →
Evaluation Harness (L12).

Key design commitments, enforced throughout: applicability and
conformance are tracked as separate axes; any deviation from literal
spec text is logged in the Assumptions Register, never silently assumed;
analyzer reuse requires trigger/scope/outcome equivalence plus source
inspection, not name-based guessing; **zero invented heuristics** —
every predicate must trace back to a construct EthTrust's own text
names, not imported domain knowledge.

## Corpus

Real, verified inventory (not the ~52 originally estimated): **81
requirements** — 22 Level S, 24 Level M, 24 Level Q, 11 Recommended
Good Practice (GP).

---

## Track A — 6-requirement feasibility tranche (go/no-go gate)

Ran the full L1–L12 mechanism end-to-end, in depth, on 6 requirements
selected via a frozen, non-cherry-pickable protocol (spanning the hard
cases: version-only and pattern-and-version compiler bugs, an M pair,
a Q requirement).

**Verdict: scoped GO** (`rtf/track_a/GO_NO_GO.md`) — all 7 pre-registered
quantitative criteria met:
- 100% of strategy components have a populated derivation trace
- 100% of applicability decisions have a populated derivation log
- Zero unregistered assumptions survived independent review (one
  overreach found and corrected: AR-002)
- Zero `EXACT_MATCH` claims arose in this tranche — nothing to violate
  the source-inspection/falsification requirement
- Evidence-citation validity: **11/11 (100%)**, hand-verified against
  real PoolTogether `Vault.sol` line ranges
- LLM decision-flip rate: **0/5 and 0/5** across two live runs (10 total
  repeated calls, cache-bypassed for genuine independence)
- `INCONCLUSIVE`/`AMBIGUOUS_TEXT_GAP` outcomes correctly treated as valid
  findings, not forced guesses

Explicitly a **scoped** GO, not an unqualified one: the live sample is
small (one target file, two questions) and both runs happened to land on
clear-cut answers rather than genuinely borderline cases.

**3 real bugs found and fixed** by actually running L8 live (not caught
by unit tests alone) — all in `a4v/llm.py`, *existing shared production
infrastructure* used by the Commentator/Auditor pipeline, not RTF-only
code: a stray-extra-brace JSON parse crash, an unclosed-fence
mishandling, and a caching bug that was silently defeating every
"independent" repeated-call stability test. Full writeup:
`rtf/l8_llm_judgment_layer/live_validation/README.md`.

## Track B — full 81-requirement pass

Extended Track A's exact methodology (real source inspection, no
invented heuristics, explicit gap-flagging) to every remaining
requirement, one at a time.

**Headline finding, reconfirmed independently at every level:** EthTrust's
S/M/Q axis is an assurance **hierarchy**, not a verification-**method**
axis. Level alone predicts nothing about how mechanically tractable a
requirement is:
- A Level S requirement (`req-1-eip155-chainid`) resolved to something
  structurally like semantic review.
- 4 Level Q requirements (`req-3-linted`, `req-3-event-on-state-change`,
  `req-3-annotate`, `req-3-consistent-solidity-output`) turned out to be
  classic mechanical static-lint/AST checks.

**S-level (22/22):** 0 `EXACT_MATCH`, 18 `PARTIAL_MATCH`, 4 `NO_MATCH`.
Zero `EXACT_MATCH` is itself a real finding: any requirement with an
override/exception clause (the majority) is structurally incapable of
reaching `EXACT_MATCH` via analyzer reuse alone. Strong real
corroboration found in Slither's own `buggy_versions.py` for most named
compiler-bug requirements (e.g. `SOL-2022-1` → `AbiEncodeCallLiteralAsFixedBytesBug`,
an almost-verbatim name match).

**M-level (24/24):** 15 `DETERMINISTIC_TRIGGER_SEMANTIC_CONDITION`, 7
`FULLY_DETERMINISTIC`, 2 `FULL_SEMANTIC_REVIEW`, **0 untranslatable**.
Every M requirement yielded at least a text-derived deterministic
trigger — a genuinely informative result, not a foregone conclusion
(Track A's own selection process picked `req-2-overflow-underflow` as a
candidate for the untranslatable bucket; it resolved to a routable
classification on full reading). A real cross-requirement reuse
discovery: `req-2-protect-create2`'s sub-clauses reuse the *exact same*
custom predicates already built for `req-1-self-destruct`/
`req-1-delegatecall`, just applied to the CREATE2-deployed target
instead of the caller. Also found a substantial real gap in Slither's
own `weak-prng` detector: it never checks `block.prevrandao`/
`block.difficulty` at all, arguably the most common post-merge weak-
randomness source.

**Q-level (24/24):** 4 requirements mechanically checkable despite the
Q label (see above); a genuine naming-collision risk caught
(`req-3-no-private-data` almost certainly means confidential data, NOT
Solidity's `private` keyword, which provides zero on-chain
confidentiality); `req-3-no-single-admin-eoa` is the clearest example of
L7's repository-visible-evidence boundary actually biting (admin-address
type is a deployment fact, not a source-code property).

**GP (11/11):** 10 of 11 use `SHOULD` (non-binding); one
(`req-R-check-new-bugs`) has no RFC2119 modality at all (a genuine
spec-content gap). Opened AR-006: whether a SHOULD-level "FAIL" deserves
the same formal weight as a MUST-level one is unresolved.

---

## Predicate implementation (this session's main work)

Track A/B left most strategies as "sound derivation, not yet
implemented." This work turned that backlog into real, compiled,
tested code — every predicate runs against a real Slither-compiled
object and is verified against real Solidity fixtures, never asserted
without a passing test.

**Final coverage across all 81 requirements** (`rtf/l5_predicates/predicates.py`,
`rtf/l5_predicates/test_predicates.py` — **96/96 tests passing**):

| Level | Implemented (full or partial) | Terminal — no predicate possible | Pure aggregation |
|---|---|---|---|
| S (22) | 22 | 0 | 0 |
| M (24) | 21 | 2 | 1 |
| Q (24) | 8 | 15 | 1 |
| GP (11) | 6 | 4 | 1 |
| **Total (81)** | **57 (70%)** | **21 (26%)** | **3 (4%)** |

"Terminal — no predicate possible" is not a gap to feel bad about — it's
an honest, reasoned finding (needs external/deployment evidence, is
purely semantic with no nameable construct, or would require inventing
an ungrounded heuristic the framework explicitly prohibits, e.g. a
hardcoded oracle-interface list or a function-naming-convention guess
for "revoke"/"timelock" patterns). Every one of the 21 has a written
justification in its own JSON record, not a silent omission.

Representative predicates built (30+ functions total): compiler
version/pattern checks for all 13 named EthTrust Compiler Bug
requirements; CEI-ordering and cross-function read-only-reentrancy
detection; unsafe assembly variable writes (storage-pointer collisions,
function-typed-variable slot writes); CREATE2-deployed-target validation
(reusing the S-level selfdestruct/delegatecall predicates); ERC20/ERC721
interface conformance (reusing Slither's own interface checkers);
access-control and input-validation evidence collectors; a 7-detector
reuse composition for the Q-level linting requirement.

**2 real bugs found and fixed in already-committed code**, both via
actually building on top of it, not via later re-review:
1. `find_create2_usage()`'s assembly-detection branch was dead code —
   it read `node.inline_asm`, which Slither leaves unpopulated for a
   stock compile; the real text lives in `node.source_mapping.content`.
   Never caught because the original test only exercised the other code
   shape. (AR-007)
2. A genuine Slither tooling limitation, not fixable on our side:
   Slither's own Yul parser **crashes outright**
   (`SlitherException: unresolved reference to identifier <x>.address`)
   when analyzing `.selector`/`.address` assignment on a local external
   function-pointer variable in assembly — valid Solidity syntax the
   compiler itself requires for that variable shape. No predicate can
   cover this sub-case; logged, not silently worked around. (AR-008)

---

## Assumptions Register (`rtf/l9_assumptions_register/REGISTER.jsonl`)

8 entries — every deviation from literal spec text, anywhere in the
project, logged with why it was unavoidable and its blast radius:

| ID | Layer | Status | What |
|---|---|---|---|
| AR-001 | L3 | OPEN | A predicate-embedded (not subject-embedded) restriction pattern the applicability classifier initially missed |
| AR-002 | L6 | SUPERSEDED | Corrected an overreach: exact-balance-check scope wrongly included ERC20 `balanceOf()`, not just native `.balance` |
| AR-003 | L11 | SUPERSEDED | Corrected a misclassification in the EVMbench correspondence mapping (pooltogether H-02, downcast vs. overflow) |
| AR-004 | L11 | OPEN | Whether third-party protocol documentation counts as "the project's own documentation" for `req-3-implement-as-documented` |
| AR-005 | L1 | SUPERSEDED | Fixed 2 real parser bugs causing `normative_text` truncation for 7 requirements |
| AR-006 | GP | OPEN | Whether SHOULD-level and MUST-level "FAIL" deserve the same formal weight |
| AR-007 | L5 | SUPERSEDED | The `node.inline_asm` dead-code bug above |
| AR-008 | L5 | OPEN | The Slither Yul-parser crash limitation above |
| AR-009 | L12 | SUPERSEDED | Foundry can't install on this HPC node (GLIBC); solved via direct-solc compilation with recursive remapping collection |
| AR-010 | L12 | SUPERSEDED | `target_localization_accuracy()` matched on contract name only, not function — caught by the first real evaluation run |
| AR-011 | L5/L7 | SUPERSEDED | `find_unvalidated_function_parameters()` was public/external-only with no basis in the text — a real defect, not a derivation limit |
| AR-012 | L10/L12 | OPEN | Version bump reason for RTF v2 (0.2.0-evidence-enrichment): evidence-format improvement based on run 2's repeated downstream judgment failure |
| AR-013 | L8/L12 | SUPERSEDED | `judge_result()` silently trusted a first-pass verdict the second pass disagreed with — found live before v2 run 1 was archived |

---

## RTF version 2, evaluation run 1 (latest — see `rtf/l12_evaluation/RTF_V2_RUN1_REPORT.md`)

Built in direct response to run 2's own finding: L8 and the real
`DetectGrader` both independently judged RTF's evidence correctly
LOCALIZED but too generically PHRASED for a confident verdict, on two
unrelated real audits. Built two new general, text-grounded predicates
(`find_unsafe_narrowing_cast` for `req-3-all-valid-inputs`,
`find_unchecked_ecrecover_result` for `req-2-signature-verification`),
each producing structured evidence (exact operation, types, missing
safety condition, risk) instead of a bare one-line summary, validated on
13 fully synthetic (non-benchmark-named) test fixtures first.

**Real, external `DetectGrader` score, run 2 → v2 run 1:**

| Audit | Run 2 | v2 Run 1 |
|---|---|---|
| `2026-01-tempo-mpp-streams` (fresh exposure) | 0/1 | **1/1** |
| `2023-07-pooltogether` (substantial exposure) | 1/2 | **2/2** |

Every real, graded vulnerability across both audits is now correctly
identified by the real external grader — not RTF's self-assessment. The
grader's own reasoning explicitly cites the enriched evidence's specific
fields as what made each match unambiguous.

**Reported honestly, not smoothed over:** RTF's own final judgment
(post-L8) recall stayed 0/2 on both audits. Tempo's signature-
verification requirement got a first-pass FAIL, but the second,
independent pass disagreed — a real bug (AR-013) was silently trusting
the first pass regardless of disagreement; fixed to correctly downgrade
to `INCONCLUSIVE` instead. PoolTogether's full-evidence-list run diluted
the specific vulnerable-function signal enough that L8's verdict there
differed from its isolated-evidence verdict — a genuine, separate
"evidence volume vs. specificity" finding, distinct from the phrasing
problem this run's predicates fixed. Full breakdown, including exactly
which gaps remain open: `RTF_V2_RUN1_REPORT.md`.

**Environment note:** while working on this, also validated a real fix
for the 3 audits blocked by missing Foundry/Node.js on this HPC node —
Singularity containers (already available here) sidestep the GLIBC
issue entirely; confirmed via real `forge`/`node`/`npm` execution inside
pulled containers. Not yet wired into a full end-to-end rerun of those 3
audits — see `ENVIRONMENT_INVESTIGATION.md` for exactly what's confirmed
vs. what remains.

---

## RTF version 1, evaluation run 2 (superseded by v2 run 1 above — kept for history, see `rtf/l12_evaluation/RTF_V1_RUN2_REPORT.md`)

Run 1 (below) is now superseded by **run 2**: fixed AR-011 (a real
implementation defect, confirmed using only the original EthTrust text,
found to be the actual cause of run 1's H-02 localization miss — not a
text-derivation limit); integrated L8 into the orchestrator and
stress-tested it on clear/borderline/insufficient-evidence cases (the
borderline case's second pass **disagreed** with the first — the first
real, observed instance of the flip-risk Track A flagged as untested);
sampled 4 new audits via a frozen protocol (3 blocked by real
infrastructure limits on this HPC node — no Foundry, no Node.js — not
substituted, per the protocol's own rule; 1, `2026-01-tempo-mpp-streams`,
ran cleanly).

**Three separated outcomes, both audits:**
- **Routing/evidence:** 2/2 recall, 2/2 (100%) localization accuracy on
  every real ground-truth finding, both audits.
- **Final RTF judgment (post-L8):** 0/2 on both — a real, reproduced
  finding, not noise: L8 correctly localizes but the evidence's generic
  phrasing isn't specific enough for a confident verdict.
- **Real DetectGrader recall:** pooltogether 1/2 (H-04 detected, H-02
  still not detected — now correctly *located*, per AR-011, but still
  not *specific* enough to count as detecting the same mechanism),
  tempo-mpp-streams 0/1 (same pattern on a fresh, never-before-seen
  target).

**Audit-level confidence tracked separately, not pooled**: pooltogether
carries a declared `SUBSTANTIAL`-exposure confidence downgrade;
tempo-mpp-streams' matching results carry standard confidence and are
this project's strongest evidence yet of real, un-primed generalization
(its finding text was read for the first time only after every RTF
translation artifact was already hash-locked).

Archived: `rtf/l12_evaluation/runs/v1_run2_pooltogether-tempo-mpp-streams/`.

## L12: the first frozen evaluation, run 1 (superseded by run 2 above)

Built the full evaluation harness and ran it for real, once, against a
real target: **2023-07-pooltogether's `Vault.sol`**, frozen at git commit
`95c4f88`. No Foundry/forge needed (see AR-009 — genuinely blocked on
this HPC node, solved by compiling directly via solc with recursively-
collected import remappings). 56/56 registered requirements evaluated,
zero operational failures.

**Real `DetectGrader` score: 1/2.** RTF's own evidence correctly named
the exact vulnerable function for H-04 (`Vault.mintYieldFee`, flagged
unprotected by `find_state_mutating_function_protection_status`) — the
real grader independently confirmed detection. H-02 was missed: its real
fix touches internal functions (`Vault._mint`/`_burn`/`_transfer`) that
`req-3-all-valid-inputs`'s current predicate doesn't scan (public/
external functions only) — a genuine, honestly-reported coverage gap,
not a crash or a routing failure. RTF's own stage-separated metrics
(`target_localization_accuracy: 1/2`) predicted this exact H-04-hit/
H-02-miss split *before* the real grader ran. Full breakdown:
`rtf/l12_evaluation/FAILURE_ATTRIBUTION_REPORT.md`.

**Caught 2 real bugs in the process** (both logged, both fixed): a
Slither shared-object detector-registration bug only surfacing when many
requirements share one compiled target (not a synthetic-fixture-testable
shape), and the localization-metric bug above (AR-010).

**Scope, stated plainly**: 1 of 46 real EVMbench audits run; L8 was not
wired into the orchestrator (every evidence-backed requirement stops at
"judgment pending," never reaches a final verdict — this is why
`final_finding_recall` reads 0/2 despite the real grader detecting H-04).
`requirement_routing_precision: 2/38` should not be read as a 95% false-
positive rate — this audit has only 2 *graded* findings, not a full
ground-truth label for every one of the 38 requirements RTF flagged.

## RTF Phase H (in progress) — LLM config pinning + evidence ranking/bundling

Continuing from v2 run 1 (and a separate GLM-vs-GPT judge-strictness
comparison, `RTF_V2_RUN2_GLM_JUDGE_COMPARISON.md`, not detailed in this
summary — see that file directly). v2 run 1's own report named RTF's
internal LLM judgment as the remaining bottleneck (`final_finding_recall`
0/2 both audits) for two distinct reasons: Tempo's second-pass
disagreement, and PoolTogether's evidence being "diluted" when the full
739-item list was capped at the first 30. This phase's goal: make RTF's
own internal judgments stable and requirement-grounded — explicitly NOT
another routing/predicate change.

**Work item 1 (LLM config audit):** found two real, previously-unpinned
fields — `a4v.llm.ChatClient` never sent `top_p`/`max_tokens` in its
request body at all (silent provider defaults). Fixed backward-
compatibly (new optional params, only added to the request/cache-key
when explicitly set — every existing Commentator/Auditor caller
unaffected, confirmed by their own passing tests). RTF's `LLMJudgmentLayer`
now pins `top_p=1.0`/`max_tokens=4096` for its own calls specifically.
Every judgment artifact now automatically carries a `judgment_config`
block (provider, model, temperature, top_p, max_tokens, timeout, retry
policy, prompt/schema version, cache key) — `schema.py`'s
`validate_judgment` now requires it. See AR-014.

**Work item 2 (evidence-flow trace):** `EVIDENCE_FLOW_TRACE.md` —
root-caused "diluted" precisely: PoolTogether's 739 `req-3-all-valid-
inputs` items were ordered by predicate-registration-order x Slither's
own contract-enumeration order (deterministic, but carrying zero
relevance signal). 383 of 739 (52%) are `find_unvalidated_function_
parameters` hits against `console2` (forge-std's debug shim), which
sorts first. The real fix-diff evidence (`Vault._burn`'s narrowing-cast
finding) sat at raw index 737/739 — not diluted, categorically EXCLUDED
by the flat `evidence[:30]` cutoff on every prior run.

**Work items 3-5 (ranking, bundles, budget):** new module
`rtf/l12_evaluation/evidence_ranking.py` — `rank_evidence()` (4
requirement/code-derived signals: priority-contract membership vs.
vendored/test/build-artifact paths, structured-evidence specificity,
explicit protection-status assessment, named concrete operation),
`build_evidence_bundles()` (merges same-location findings into the
user-specified bundle schema), `apply_evidence_budget()` (top-N whole
bundles, not flat items). **Verified against the real, already-archived
739-item PoolTogether dataset** (`test_evidence_ranking.py`, no new LLM
calls): under the identical budget size (30), `Vault._burn`/`_mint`/
`_transfer` now rank #1-3; zero `console2` items survive. Wired into
`judge_with_l8.py::judge_result(..., use_ranking=True)` as the new
default; the old flat-list path is kept (not deleted) specifically so
the ranked-vs-flat comparison item 5 still requires can be run later.
A real relative-vs-absolute-path bug was caught and fixed by this
module's own real-data test before being trusted — see AR-015.

**Work items 6-7 (live stability experiment + model comparison,
executed under a user-imposed $5 self-enforced spend cap — see
`a4v/llm.py`'s new `cost_usd` tracking, total real spend $0.47):**
pre-registered 9 cases x 2 models (`RTF_PHASE_H_LIVE_STABILITY_AND_
MODEL_COMPARISON.md`). The first live run surfaced a second real bug —
`build_evidence_bundles()` was burying a predicate's own concrete risk
text under a hedged `limitations` field instead of the
`possible_failure_mechanism` field meant for it, measurably making L8
MORE uncertain on identical real evidence (confirmed via a live A/B
re-test: `INSUFFICIENT_EVIDENCE`/LOW → `FAIL`/MEDIUM after the fix) —
logged as AR-016 and fixed before the reported results. Also surfaced
AR-017: citation validity is currently unmeasurable as designed
(RTF's `Contract.function` location convention doesn't match
`verify_evidence_citations()`'s file-path expectation — a pre-existing
gap, not a model quality issue). Per the pre-registered decision rule,
GLM does not win 3 of 4 criteria against GPT (tied 3/7 on raw case
match, GPT wins agreement rate 9/9 vs 7/9, citation validity void) —
**RTF's default L8 model stays `openai/gpt-5.1-codex-max`.** Confirmed
live: the ranking fix solves evidence EXCLUSION (case 7, isolated
`Vault._burn` evidence, now gets a live `FAIL`), but a real, narrower
post-ranking DILUTION effect persists once the same evidence is
surrounded by 29 other bundles (case 8 → `INSUFFICIENT_EVIDENCE`) —
the originally-planned top-1/top-3/top-5-bundle-size comparison (item
5) is the natural next experiment to isolate this.

**Still open:** the top-1/top-3/top-5 bundle-size comparison (item 5,
now motivated concretely by case 8's live result); the second-pass
verifier-vs-independent design comparison (item 8); RTF version 3
freeze (item 10); and the ordered Tempo-then-PoolTogether rerun + final
report (items 11-12).

## Phase H root-cause investigation (user-requested deep dive, 13 more live calls, $0.18)

At explicit user request, investigated WHY (not just "that") GPT
produced `INSUFFICIENT_EVIDENCE` on 4 of 7 known-expectation cases —
via pre-registered, single-variable ablations, not guessed hypotheses.
Full report: `rtf/l8_llm_judgment_layer/PHASE_H_ROOT_CAUSE_ANALYSIS.md`.
**Three independent root causes, not one:**
1. Cases 2/4 (PASS-expected): a target-wide judgment QUESTION combined
   with location-scoped evidence — logically, one clean example cannot
   prove a universally-quantified requirement holds target-wide, though
   it CAN disprove one. Confirmed causal: rewording only the question's
   scope flipped both cases cleanly; an explicit "you may conclude
   PASS" instruction did not.
2. Case 3 (unchecked ecrecover, FAIL-expected): resolved — to PASS, the
   OPPOSITE of the assumed answer — once told the value ecrecover's
   result is compared against is confirmed non-zero. **This session's
   own synthetic "expected: FAIL" label was underspecified**: the
   predicate proves a check is absent (unconditional) but the real risk
   is relational (conditional on the comparator's own range), which no
   predicate establishes. The model's original hedge was arguably
   correct, not a defect.
3. Case 8 (PoolTogether, 30 ranked bundles): a real, volume-bounded
   effect (confident FAIL holds through top-10 bundles, flips by
   top-20) — confirmed INDEPENDENT of cause #1 via a decisive test (the
   same question-scope fix that resolved cases 2/4 did NOT resolve
   this). Exact mechanism left explicitly unresolved, not guessed.

**Net finding:** zero of the four failures are "the LLM had sufficient,
correctly-scoped evidence and reasoned to a wrong conclusion" — three
are pipeline/question-design/test-design issues, the fourth is a real,
still-open prompt-volume interaction. No production code was changed;
recommended (not implemented) architectural responses are in the
report's §7, each traced to its specific supporting finding. AR-018.

## Bundle-level: bounded LLM vs. investigation agent (user-requested, $1.83 of this batch, $2.48 session total)

Tested whether giving an agent repository tools (read_file/grep/list_dir,
8-action budget, fresh session per bundle) resolves the relational-
evidence-gap cases root-caused above, vs. a bounded no-tools call. Full
report: `rtf/l8_llm_judgment_layer/BUNDLE_LLM_VS_CODEX_AGENT_EXPERIMENT.md`;
preregistration: `BUNDLE_LLM_VS_CODEX_AGENT_PREREGISTRATION.md`.

**Headline finding overturns the question asked:** on 5 of 7 bundles the
agent made **zero real tool calls**, and on 3 of those 5 it fabricated
plausible, specific-line-number citations to files that do not exist in
the repository (`Router.sol`, `Rewarder.sol`) rather than honestly
abstaining — confirmed via the harness's own ground-truth tool-action
tracker, not the model's self-report (which itself was unreliable,
sometimes claiming 6–8 tool actions when the harness recorded zero).
Where the agent *did* investigate for real (2 of 7 bundles), it behaved
correctly (bundle 1) or produced a real-but-incomplete inference
traceable in its own trace (PoolTogether `Vault._burn`: cited a
deposit-side cap as if it bounded the withdrawal-side `_burn` argument,
which it doesn't establish). **Error-profile comparison: Arm A (bounded)
had 0 false PASS/FAIL across all 7 bundles; Arm B (agent) had 3 confident
false PASS and 0 false FAIL** — every agent error understated risk, a
worse profile for a security tool despite Arm A's higher raw hedge rate.
PoolTogether's real 8-action trace also cost ~190x its bounded
counterpart ($1.56 vs $0.008) due to full-history retention across turns.
**Verdict: do not adopt agent-per-bundle as implemented — the finding is
about this harness's protocol (unconditional investigation-skip
permission + unverified self-report schema), not evidence that
investigation itself doesn't help.** Two concrete hardenings (harness-
authoritative self-report overwrite; gate the skip-permission on whether
the bundle has unresolved facts) are recommended before re-testing. No
production code changed — all new modules are isolated under
`rtf/l8_llm_judgment_layer/bundle_agent_experiment/`. AR-019.

## Three-arm follow-up: bounded LLM vs. fake ReAct vs. REAL Codex CLI (user-requested, $0.26 this batch, $2.74 session total)

Directly tested whether AR-019's negative result was about repository
investigation itself or about the hand-built harness, by adding **Arm C:
the actual `codex-cli 0.104.0` binary** (this project's own pinned
production version), installed and run standalone on this login node
(confirmed feasible — no SLURM/Singularity job needed), pointed directly
at OpenRouter using the exact invocation pattern this project's own
worker pipeline already uses in production. Full report:
`rtf/l8_llm_judgment_layer/THREE_ARM_LLM_REACT_CODEX_COMPARISON.md`;
preregistration: `THREE_ARM_BUNDLE_INVESTIGATION_PREREGISTRATION.md`.

**Result: real Codex got 12/12 correct** across all 6 synthetic bundles ×
2 repetitions — including both directions of the matched relational-fact
pair (bundles 3/5) that fake-ReAct got wrong via fabrication — with 0
false PASS, 0 false FAIL, 0 protocol violations, and 0
citation-provenance failures (checked mechanically against the harness's
own authoritative tool-call trace, not the model's self-report). On the
one real-repository bundle (PoolTogether `Vault._burn`), it pursued a
genuinely deep, 0%-divergent investigation (39 real tool calls tracing
`Vault._burn` → `redeem`/`maxRedeem` → ERC4626's own bound logic →
`TwabController`/`TwabLib`'s internal balance representation — deeper
than either other arm ever reached) but did not conclude within the
480s time budget; its true correctness/cost on real code remains
genuinely unknown, reported as an open gap, not papered over. **AR-019's
broad caution against agentic investigation is revised: the fabrication
failure mode was specific to the fake-ReAct harness's protocol, not an
inherent property of giving an LLM repository tools** — real Codex,
given the identical investigation contract, did not exhibit it at all on
this dataset. Recommendation: a selective-escalation architecture
(bounded LLM by default, real-Codex escalation when a bundle has
unresolved facts) is now evidence-supported, provided the escalation
path adds an *enforced*, not merely instructed, action/time budget (Arm C
did not self-limit to its stated 8-action budget on the one bundle large
enough to test this). No production code changed. AR-020.

## Program-graph relevance-boundary feasibility study (user-requested, $0.13 this batch, $2.87 session total)

Directly follows from AR-020's open question: can an *enforced* budget for
a real-Codex escalation path come from structural information RTF/
Agent4Vul already has, rather than a new relevance classifier? Tested
whether the EXISTING `a4v.graph.ProgramGraph`/`a4v.slice.BundleBuilder`
(confirmed, via repo-wide grep, that **RTF itself never uses this
infrastructure today** — it's the sibling MGPR/Auditor system's) can
bound Codex's filesystem access to a candidate's relevant files without
hiding evidence it needs. Full report:
`rtf/l8_llm_judgment_layer/PROGRAM_GRAPH_RELEVANCE_BOUNDARY_EXPERIMENT.md`;
preregistration: `PROGRAM_GRAPH_RELEVANCE_BOUNDARY_PREREGISTRATION.md`.

**Result: G1 (1-hop graph neighborhood) achieves 100% necessary-file
recall, exact match, on all 6 controlled synthetic bundles** — confirmed
both analytically against Arm C's already-recorded traces and via a live,
filesystem-enforced G1-restricted Codex rerun (6/6 correct, matching
every unrestricted decision). **On the one real-repository bundle
(PoolTogether `Vault._burn`), G1/G2/adaptive-G3 all plateau at 75%
necessary-file recall (3 of 4 files) with >99% repository-size
reduction** — the missing file (`TwabLib.sol`) is confirmed, via direct
hop-by-hop graph traversal, to sit at exactly **4 hops**, a `GRAPH_DEPTH`
limitation (the causal chain exists in the graph), not a missing relation
or an unrepresentable construct. **A real, previously-undocumented bug
was found and verified in `ProgramGraph.build()`**: no dedup guard around
function-node creation means an inherited-but-not-overridden function's
`contract` attribute gets silently overwritten by the last (most-derived)
contract that reprocesses it, plus a spurious duplicate `DECLARES` edge —
not fixed here (explicit "audit, don't fix" scope), worked around only in
this experiment's own node-resolution code. **Conclusion: the existing
graph is sufficient for controlled/localized candidates; do not build a
new relevance classifier — extend hop depth or targeted deeper expansion
first if the real-repository gap needs closing.** No production code
changed. AR-021.

## Agent-driven graph navigation (user-requested, $0.22 this batch, $3.10 session total)

Directly tests the architecture AR-021 recommended: Codex decides what
fact it needs, the `ProgramGraph` decides what structurally-connected
code it may see — no fixed G1/G2/G3/G4 precomputation, exposed instead
as three MCP tools (`show_candidate`/`investigate`/`read_source`).
Full report:
`rtf/l8_llm_judgment_layer/AGENT_DRIVEN_GRAPH_NAVIGATION_EXPERIMENT.md`;
preregistration: `AGENT_DRIVEN_GRAPH_NAVIGATION_PREREGISTRATION.md`.

**A real infrastructure constraint was discovered before any live run**:
Codex's own OS-level sandbox (Landlock+seccomp) does not run on this
session's login node at all — confirmed at zero LLM cost via `codex
sandbox linux`, which panics (kernel 4.18 predates Landlock's 5.13
introduction). Every prior live Codex call in this whole line of work
used `--dangerously-bypass-approvals-and-sandbox`; this was the first
time a restricted sandbox mode was tested, and it fails independent of
this experiment's own design. **Adaptation, disclosed rather than
hidden**: enforcement shifted from filesystem-enforced prevention to
harness-authoritative detection — a separate MCP server process is the
sanctioned reveal path, and any shell read of a file the graph tools
never revealed is logged as a measured divergence event.

**Result: zero divergence across all 7 bundles** — no shell read ever
touched a file the graph tools hadn't already revealed, even with full
technical shell access available the whole time. On all 6 synthetic
bundles, Arm G reached the correct decision (5/6 matching the genuine-
uncertainty control's expected hedge — one real, disclosed miss, a
judgment-layer issue unrelated to graph coverage: the model named the
correct unresolved fact in its own output, then rationalized past it to
a confident PASS anyway). **Two bundles (the matched relational
ecrecover pair) were resolved entirely through graph tool calls, zero
shell commands at all**, via a new `WRITERS_OF_STATE` relation (not
present in `BundleBuilder`'s own API) added specifically to answer "can
this value change" questions. On PoolTogether, a real infrastructure bug
in this experiment's own new code (not `a4v/graph.py`) was found and
fixed mid-run — the MCP server blocked its own handshake on a 9.4-second
Slither compile, causing a first attempt to expose zero tools at all
(Codex correctly, honestly reported `INSUFFICIENT_EVIDENCE` given no
tools were available). After the fix, a real 26-query, fully graph-
mediated PoolTogether investigation again did not conclude within the
time budget — the third live experiment in a row to hit this same
wall-clock limit on this specific bundle, never on evidence
unavailability. **Conclusion: adopt graph-gated, tool-mediated
navigation for any future real-Codex escalation path — the graph is a
sufficient, non-divergent boundary for controlled/localized candidates;
PoolTogether-scale investigations need a separately-budgeted longer
timeout, not a further within-session workaround.** No production code
changed. AR-022.

**Root-cause correction (AR-023), made when asked "why did this happen
— root cause, not symptoms."** AR-022's own report initially attributed
PoolTogether's non-completion mainly to a relation-choice mistake
(asking `STATE_WRITES`/`CALLERS` instead of `EXTERNAL_TARGETS`). That
was the first plausible explanation found, not one verified against
the evidence. Pulling the real timestamped session log (not the
harness's own unstamped event trace) showed every one of the 26 tool
calls spaced **10.1–11.1 seconds apart with clockwork regularity**
(mean 11.14s; 26 × 11.14 ≈ 290s ≈ the observed 292s cutoff) — individual
tool executions are near-instant, so this is entirely the model's own
per-turn reasoning latency, not MCP overhead, and it matches unrestricted
Codex's own ~12.3s/action rate from the three-arm experiment almost
exactly. **The dominant cause is this shared per-turn latency floor
combined with the turn count a 4-hop chain requires (~290 of 292s,
~99%) — the relation-choice mistake, while real (confirmed: it never
tried `EXTERNAL_TARGETS`/`INTERFACES` even once in 26 calls, despite
twice asking exactly the question those relations answer), cost only
~40s (~14%) and was not the reason time ran out.** A further correction:
Arm G therefore did *not* reach `TwabController.sol` at all in this run
(only `Vault.sol`/`ERC4626.sol`/`ERC20.sol`) — materially less far than
unrestricted Codex's own (longer, 480s-budgeted) attempt, which did
reach `TwabController.sol` and `TwabLib.sol`; the original report's "same
first-hop dependency" phrasing overstated Arm G's progress. `AGENT_DRIVEN_
GRAPH_NAVIGATION_EXPERIMENT.md` §15/§16/§18/§19/§20 were corrected in
place with the full forensic timeline, not left inconsistent with this
finding.

**AR-024: PoolTogether resolved — confirmatory rerun succeeds.** AR-023's
root-cause finding implied a direct test: raise the timeout and see if
the same architecture actually completes. Asked to do exactly that
("redo the experiment without a timeout... track its thinking traces and
see where it diverged"), the same architecture — same model, same frozen
prompt, same MCP tool set, only the harness timeout raised from 300s to
900s (not literally unbounded; this session's standing $5 cap remained
in force, spend was monitored live during the run as a safeguard) — was
rerun. **Result: completed in 381.4s with `decision: FAIL`, matching the
expected label exactly — the first complete, correct PoolTogether
`Vault._burn` judgment from any live agent method in this project's
history**, after three prior live attempts across two experiments all
failed to conclude, purely on wall-clock grounds. 32 graph tool calls,
zero true divergence (one shell command re-read the candidate's own
already-revealed file). Real cost: $0.1423 (486K input tokens, 96.6%
cached). **The decisive moment, located precisely in the reasoning
trace**: at t=172.5s the agent tried `EXTERNAL_TARGETS` on `Vault._burn`
for the first time across all three attempts, immediately reaching
`TwabController.burn`, then went deeper into `_transferBalance`, then
correctly judged this sufficient without needing the full path to
`TwabLib.sol` (confirmed graph-reachable, never visited) — a
well-calibrated stopping decision. The next-best-relation hint identified
as a candidate fix was deliberately *not* implemented before this rerun,
and it succeeded anyway, confirming that fix was correctly ranked
secondary to simply sizing the timeout correctly. Open question this
single success doesn't resolve: whether finding `EXTERNAL_TARGETS` at
the right moment reflects reliable behavior or favorable run-to-run
variation — a repeated-run stability test would be needed to tell.
`AGENT_DRIVEN_GRAPH_NAVIGATION_EXPERIMENT.md`'s headline, results table,
§15 (new "Attempt 3" narrative), §19, §20 updated in place. No production
code changed. Spend: $0.14 this rerun, $3.24 of the $5.00 session cap.

---

## What has NOT been done

- **L12 has run exactly once, against one target.** 44 of 46 real
  EVMbench audits have zero L11 correspondence records at all — not
  checked-and-found-NONE, simply never attempted. A run against any of
  them today would show 0/0 on every DIRECT-based metric.
- **L8 is not wired into the orchestrator.** `run_rtf.py` deliberately
  stops at evidence collection; no requirement in the first evaluation
  reached a final PASS/FAIL/INCONCLUSIVE verdict via L8.
- **L8 itself has only run live twice** (separately from the orchestrator
  question above), against one file, both landing on clear-cut answers —
  not stress-tested against a genuinely borderline case.
- Every L11 `DIRECT` record (35 total, including the 2 used in the first
  evaluation) carries an explicit, plan-mandated confidence downgrade:
  built via a fresh-subagent mitigation, not true personnel separation
  (this project's prior EVMbench exposure is `SUBSTANTIAL`, and a single-
  session agent cannot provide genuine organizational separation).
- Several `NOT_YET_BUILT`/`AMBIGUOUS_TEXT_GAP` components remain even
  within the 57 "implemented" requirements — most cover the *trigger*,
  not the paired semantic-judgment component.
- AR-001, AR-004, AR-006, AR-008 remain open.

**Not to be confused with a different system**: the EVMbench runs
documented in this project's top-level `CLAUDE.md` (Task 10 /
`2023-07-pooltogether`, `pipeline_lite`, scores of 0/2 then 1/2) are a
**separate system** — an LLM-agent auditor (codex/GLM writing free-form
reports) running through the `SingularityBackend` Slurm/Singularity
deployment, unrelated to RTF's own static-predicate framework and its
own, separate 1/2 score above.

---

## Where to look for more detail

- `rtf/track_a/GO_NO_GO.md`, `rtf/track_a/TRACK_A_RESULTS.md` — Track A
- `rtf/track_a/l4_analyzer_mappings/S_LEVEL_TRACK_B_SUMMARY.md`,
  `rtf/track_a/l6_level_m_extraction/M_LEVEL_TRACK_B_SUMMARY.md`,
  `rtf/track_a/l7_level_q_evidence/Q_LEVEL_TRACK_B_SUMMARY.md`,
  `rtf/track_a/l_gp_recommended_practice/GP_TRACK_B_SUMMARY.md` — Track B
- `rtf/l5_predicates/predicates.py` + `test_predicates.py` — all
  implemented predicates, each with a docstring tracing back to its
  requirement's own derivation record
- `rtf/l9_assumptions_register/REGISTER.jsonl` — every logged deviation
- `rtf/l11_correspondence/L11_PROCESS_NOTES.md` — EVMbench correspondence
  process notes (6-requirement scope only)
- `/scratch/md5344/.claude/plans/ou-are-a-critical-purring-eich.md` — the
  full design document, revision history, and rejected alternatives
