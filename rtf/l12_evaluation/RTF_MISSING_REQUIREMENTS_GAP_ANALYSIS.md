# RTF Missing Requirements -- Root Cause Classification

Companion to `RTF_RUNTIME_COVERAGE_AUDIT.md`. Classifies each of the 25
requirements that had no runtime execution mechanism before this
session's fix, per the user's schema:

```
A. Deterministic predicate exists but is not registered
B. Intended for shared LLM judgment but never wired
C. Analyzer/reviewer genuinely not implemented (deterministic trigger
   considered plausible/buildable, declined for a specific reason, not
   built)
D. Applicability/translation defect
E. Requirement cannot currently be operationalized (no repository-visible
   evidence exists of ANY kind, or requires dynamic/runtime information
   outside this framework's static-analysis design)
F. Other implementation defect
```

Explicit finding up front, per instruction not to treat
`NO_PREDICATE_POSSIBLE` as "skip requirement": **20 of the 25 (categories
B, C, and E combined) are now wired to the SAME generic
`collect_documentary_and_implementation_evidence` predicate -> shared L8
judgment pipeline** (see `RTF_RUNTIME_COVERAGE_AUDIT.md` section 2 /
`rtf/l5_predicates/predicates.py`). This is deliberate and uniform, not
hand-tuned per requirement: a genuinely NO_PREDICATE_POSSIBLE requirement
(category B) gets the same honest opportunity to reach a real
PASS/FAIL/INCONCLUSIVE verdict from L8 as a requirement whose
deterministic trigger was merely declined for infrastructure reasons
(category C) or one that structurally lacks repo-visible evidence
(category E) -- the latter two will typically and correctly resolve
INSUFFICIENT_EVIDENCE/INCONCLUSIVE rather than a confident verdict, which
is itself the honest, expected outcome given their own root cause, not a
defect in the fix.

## Category A -- predicate exists, was not registered (1 requirement)

### `req-R-use-latest-compiler`
**Root cause**: `check_compiler_version_is_latest_stable` (in
`rtf/l5_predicates/predicates.py`) was implemented AND tested
(`rtf/l5_predicates/test_predicates.py`) but the line adding it to
`REGISTRY` was simply never written. The comment previously at that spot
in `registry.py` claimed a "special-cased handling" in `run_rtf.py` that
does not exist anywhere in the codebase (confirmed via grep across
`run_rtf.py`/`pipeline_e2e.py`/`pilot5_driver.py`) -- a second,
independent documentation/code discrepancy on top of the missing
registration itself.
**Fix**: registered with an explicit, dated, sourced
`latest_known_stable_version="0.8.36"` parameter (Solidity's actual
latest stable release as of 2026-08-09, verified via web search, not
guessed) -- see `registry.py`'s own inline comment for the full
justification and staleness disclosure.

## Category F -- pure aggregation, not an independent predicate (3 requirements)

### `req-2-pass-l1`, `req-3-pass-l2`, `req-R-meet-all-possible`
**Root cause**: correctly identified in their own Track A design records
as pure aggregations over OTHER requirements' already-computed results
("composing an L12-evaluation-level result, not writing a predicate"),
not a "no predicate possible" gap in the same sense as the others -- but
the aggregation itself was never actually implemented anywhere, so these
3 were just as silently absent as the genuine `NO_PREDICATE_POSSIBLE`
cases.
**Why this can't be an L5/L6 predicate**: `run_rtf.py`'s deterministic
layer runs BEFORE L8 judgment/escalation resolve any OTHER requirement's
final conformance_state -- at that point in the pipeline almost every
evidence-backed requirement is still `conformance_state=None` ("pending
L8"), so "AND over every Level S requirement's conformance_state" would
be computed over data that doesn't exist yet.
**Fix**: `pipeline_e2e.compute_aggregation_requirements`, run AFTER the
full per-requirement L8/escalation loop completes. Rule (mechanical, from
each requirement's own normative text, not benchmark-derived): PASS iff
every constituent is PASS or NOT_APPLICABLE; FAIL iff any constituent is
FAIL; INCONCLUSIVE otherwise (something unresolved, but nothing shown to
violate). `req-R-meet-all-possible` (SHOULD-level, advisory, and this
framework has no concept of "the security level for which it is
certified" to compare against) is deliberately never given a hard FAIL,
consistent with AR-006's already-logged open question on SHOULD-level
semantics.

## Category B -- intended for shared LLM judgment, never wired (12 requirements)

Each of these was marked `NO_PREDICATE_POSSIBLE` specifically because the
requirement's own design record identified NO deterministic trigger at
all and explicitly or implicitly pointed at semantic/contextual review as
the only viable path -- exactly the shape the task description's example
covers ("read documentation, extract behavioral claims, inspect
implementation, determine contradiction").

| req_id | Why B, specifically | Track A's own words |
|---|---|---|
| `req-2-enforce-eval-order` | Explicit: routes to L8, no L5/L6 component at all | "FULL_SEMANTIC_REVIEW by design... routes directly to the L8 LLM Judgment Layer with no L5/L6 predicate component" |
| `req-R-clean-code` | Explicit: routes to L8 | "routes directly to the L8 LLM Judgment Layer with no L5 predicate component at all" |
| `req-3-documented` | Documentation-existence assessment, the archetypal L7 shape | "assessing whether adequate business-logic documentation EXISTS... is inherently semantic" |
| `req-3-document-system` | Same shape as `req-3-documented`, for architecture docs | "assessing actual documentation CONTENT against the code is inherently semantic" |
| `req-3-document-threats` | Same shape, for threat-model docs | same reasoning as `req-3-document-system` |
| `req-3-implement-as-documented` | The archetypal claims-vs-implementation cross-check | "comparing implementation behavior against documentation claims is the archetypal L7 evidence-vs-claim cross-check" |
| `req-3-intended-replay` | Requires understanding documented purpose/intent | "replay-intent assessment requires understanding the contract's documented purpose, inherently semantic" |
| `req-3-no-private-data` | Semantic review of what's stored/emitted (NOT a keyword scan -- see the naming-collision warning already logged in Track A: `private` visibility != confidentiality) | "no syntactic proxy to check at all; a `private`-keyword scan would be actively WRONG" |
| `req-3-block-front-running` | Broad economic/ordering property, LLM can still meaningfully review for known mitigation patterns (commit-reveal, etc.) | "front-running protection is an economic/ordering property... no single named Solidity construct to anchor a trigger on" |
| `req-3-block-mev` | Same shape as front-running | "MEV protection is a broad economic-design property" |
| `req-3-protect-gas` | Broad design property; an LLM can still read for obvious gas-griefing patterns even without a named construct | "gas-griefing protection is a broad design property without a single named construct to anchor on" |
| `req-3-protect-governance` | Broad design property, architecture-review-shaped | "governance-attack protection is a broad design property, not a syntactic pattern" |

## Category C -- deterministic analyzer genuinely not implemented (5 requirements)

Distinct from category B: each of these records identifies a SPECIFIC,
concretely buildable deterministic trigger, and explains exactly why it
was declined -- a real infrastructure gap or an explicit refusal to
invent an un-text-grounded heuristic, not "inherently semantic."

| req_id | The buildable trigger that was declined, and why |
|---|---|
| `req-2-no-homoglyph-attack` | A real Unicode-confusables-database check (e.g. `confusable_homoglyphs`) -- declined only because the library isn't installed in this environment ("real, legitimate infrastructure work... same category of gap already logged for Mythril/Semgrep"), not a design limitation. |
| `req-3-check-oracles` | Oracle call-site detection -- "a real, buildable trigger," declined because it would require hardcoding known oracle interface signatures (e.g. Chainlink's `latestRoundData`), which the record explicitly treats as an invented heuristic rather than a text-grounded derivation. |
| `req-3-revocable-permisions` | Presence of a revoke/transfer function -- "checkable," declined because it would require matching function-NAMING conventions (not a formally named Solidity construct EthTrust's text anchors on). |
| `req-3-timelock-for-privileged-actions` | Presence of a two-step commit/execute timelock pattern -- "fairly checkable," declined because recognizing the PATTERN across arbitrary naming/structuring choices risks becoming an invented heuristic. |
| `req-R-multisig-threshold` | A deployment script setting an explicit multisig threshold -- declined because it would require hardcoding a specific multisig factory's ABI (e.g. Gnosis Safe's `setup(...)`), and unlike `req-R-follow-erc-standards`' ERC20/ERC721 predicate, there is no Slither-native canonical signature list to reuse. |

**Disposition**: all 5 are wired to the SAME generic LLM-mediated path as
category B for this pass (an honest, generic attempt is strictly better
than continued silence), but a TRUE fix for these specifically would be a
real deterministic predicate (installing the missing dependency for
homoglyph detection; a config-driven, not hardcoded, oracle/multisig
signature list) -- flagged as a distinct follow-up, not conflated with
the B-shaped requirements where no deterministic path was ever plausible.

## Category E -- cannot currently be operationalized from repo-visible evidence (4 requirements)

| req_id | Why no repository-visible evidence can ground this at all |
|---|---|
| `req-3-enough-gas` | "gas-sufficiency is a runtime/economic property... would require gas-estimation/simulation, out of this framework's static-analysis scope as built" -- a structural scope boundary, not a missing predicate. |
| `req-3-no-single-admin-eoa` | Whether an admin address is a multisig contract or a plain EOA is a DEPLOYMENT fact -- "explicitly out of L7's repository-visible scope per the Rev. 3 re-scoping." Source code can show the admin role is generically parameterized, but not what was actually deployed. |
| `req-R-check-new-bugs` | "REQUIRES_EXTERNAL_EVIDENCE about an ongoing process outside the spec's fixed cutoff date... no repository-visible artifact could ground a predicate here." Also has no RFC2119 modality at all (a genuine, separately-logged spec-content gap, `rtf/l1_corpus/PARSING_NOTES.md`). |
| `req-R-notify-news` | "an external, post-hoc team action, not a repository-visible artifact of any kind. No predicate, however written, could assess this from source code." |

**Disposition**: also wired to the generic LLM-mediated path (per the
task's own instruction not to pre-judge these as unactionable) --
`collect_documentary_and_implementation_evidence`'s explicit
absence-evidence lines ("No README file was found...") give L8 exactly
what it needs to correctly and honestly resolve these to
`INSUFFICIENT_EVIDENCE` rather than a confident guess, which is the
CORRECT terminal state for a category-E requirement, not a residual gap.

## Category D -- applicability/translation defect

**None found.** L1 (translation), L2 (context bundling), and L3
(applicability) were verified faithful and correct for all 25 previously-
missing requirements (see `RTF_RUNTIME_COVERAGE_AUDIT.md` section 4) --
the gap was entirely downstream of correct translation/applicability
work, in predicate registration and orchestrator iteration scope.

## Cross-cutting: two additional confirmed documentation/code discrepancies

Found while producing this classification, both now fixed as part of the
same change:

1. `registry.py`'s own module docstring claimed "the orchestrator must
   not silently skip [unregistered requirements] without comment" --
   `run_rtf.py` had no such handling at all prior to this fix.
2. `registry.py`'s comment for `req-R-use-latest-compiler` claimed a
   "special-cased handling" in `run_rtf.py` that did not exist anywhere
   in the codebase.

Both are the kind of drift this whole exercise exists to catch: a
correct-sounding comment is not the same as verified behavior.

## Summary count

| Category | Count | req_ids |
|---|---|---|
| A (predicate existed, unregistered) | 1 | `req-R-use-latest-compiler` |
| B (LLM-mediated, never wired) | 12 | `req-2-enforce-eval-order`, `req-R-clean-code`, `req-3-documented`, `req-3-document-system`, `req-3-document-threats`, `req-3-implement-as-documented`, `req-3-intended-replay`, `req-3-no-private-data`, `req-3-block-front-running`, `req-3-block-mev`, `req-3-protect-gas`, `req-3-protect-governance` |
| C (analyzer genuinely not implemented) | 5 | `req-2-no-homoglyph-attack`, `req-3-check-oracles`, `req-3-revocable-permisions`, `req-3-timelock-for-privileged-actions`, `req-R-multisig-threshold` |
| D (applicability/translation defect) | 0 | none |
| E (cannot currently be operationalized) | 4 | `req-3-enough-gas`, `req-3-no-single-admin-eoa`, `req-R-check-new-bugs`, `req-R-notify-news` |
| F (other -- pure aggregation) | 3 | `req-2-pass-l1`, `req-3-pass-l2`, `req-R-meet-all-possible` |
| **Total** | **25** | |
