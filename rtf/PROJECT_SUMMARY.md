# RTF — Requirement Translation Framework: Project Summary

**What this is:** a standards-driven replacement for MGPR (the old
benchmark-fitted router in Agent4Vul). Instead of hand-tuning detection
rules against EVMbench findings, every analysis strategy is derived from
the **EEA EthTrust Security Levels Specification** (Version 3, Apache
2.0, verbatim-snapshotted). EVMbench is used only to *evaluate* the
result afterward — never to define it. Full design rationale, revision
history, and rejected alternatives: `/scratch/md5344/.claude/plans/ou-are-a-critical-purring-eich.md`.

**Status as of 2026-08-06 (updated):** full 81-requirement corpus
translated (applicability + strategy derivation); 57/81 requirements
have at least one real, tested static predicate implemented; **the first
frozen EVMbench evaluation has now been run** — a real orchestrator
against a real target (2023-07-pooltogether), scored 1/2 by the real
upstream `DetectGrader`. Still narrow in scope (1 of 46 real audits, L8
not yet wired into the orchestrator — see "What has NOT been done"
below) but no longer zero. Full audit: `rtf/AUDIT_L0_L12.md`. Full first-
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

---

## L12: the first frozen evaluation (new this session)

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
