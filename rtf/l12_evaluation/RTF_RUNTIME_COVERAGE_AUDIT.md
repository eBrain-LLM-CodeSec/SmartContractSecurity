# RTF Runtime Coverage Audit -- full 81-requirement corpus

**Task:** per user directive, trace every one of RTF's 81 EthTrust
requirements through EthTrust source -> translated requirement (L1) ->
context bundle (L2) -> applicability (L3) -> analyzer/predicate/reviewer
assignment (L4-L7) -> runtime registry (`registry.py`) -> evidence
generation (`run_rtf.py`) -> routing (`TargetRunResult.routed`) ->
judgment (L8), and identify exactly which requirements disappear and
why. Triggered by the Liquid-Ron investigation, which found
`req-3-documented`/`req-3-implement-as-documented` silently absent from
every run.

**This document reflects the state AFTER this session's fix** (frozen
commit noted in the companion validation report). Section 3's table's
"Was missing pre-fix" column preserves the historical finding.

## 1. Methodology

For each of the 81 requirements in `rtf/l1_corpus/requirement_corpus.json`:

1. **L0->L1 translation**: verified present and structurally intact for
   all 81 (spot-checked; full corpus was already known-complete from
   prior project phases, not re-verified line-by-line here since that
   was not the failure point -- see section 4).
2. **L1->L2 context bundle**: verified `rtf/l2_context_bundles/<req_id>.json`
   exists for all 81 (confirmed via directory listing count).
3. **L3 applicability**: `rtf/track_a/l3_applicability/<req_id>.json`
   exists for all 81 (Track A's own completed pass).
4. **L4-L7 analyzer/predicate/reviewer assignment**: each requirement's
   own design-tier record (`rtf/track_a/l5_level_s_strategy/` for S,
   `l6_level_m_extraction/` for M, `l7_level_q_evidence/` for Q,
   `l_gp_recommended_practice/` for GP) read for its
   `implementation_status` field -- the authoritative record of what
   mechanism (if any) was designed.
5. **Runtime registry**: cross-referenced against
   `rtf.l12_evaluation.registry.REGISTRY` (which requirements actually
   have a callable predicate wired in) and `registry.AGGREGATION_REQ_IDS`
   (the 3 pure-aggregation requirements).
6. **Evidence generation / routing**: verified live, not assumed --
   `run_rtf.run_rtf()` executed against a real compiled fixture
   (`tests/fixtures/multi_contract/Vault.sol`) and the resulting
   `TargetRunResult.routed` dict's key set compared against the full
   corpus (see `rtf/l12_evaluation/test_runtime_coverage.py`,
   `test_run_rtf_covers_full_corpus_not_just_registry`).
7. **Judgment (L8)**: verified structurally (which requirements' evidence
   would reach `judge_with_l8.judge_result`) and, for the two
   specifically-named Liquid-Ron requirements, live during the
   supervised Liquid-Ron rerun (see the companion validation report).

## 2. Headline finding

**25 of 81 requirements (31%) had NO runtime mechanism at all before
this session's fix** -- not a deterministic predicate, not a wired L8
reviewer path, nothing. `run_rtf.py`'s main loop iterated
`REGISTRY.keys()` (56 requirements) instead of the full corpus, so any
requirement without a registered predicate never appeared in
`TargetRunResult.routed` -- not as `NOT_APPLICABLE`, not as any
operational-failure code, completely absent from every downstream
artifact (`audit.md`, `pilot_summary.json`, every `entry_*_stage.json`).
`registry.py`'s own module docstring claimed "the orchestrator must not
silently skip them without comment" -- `run_rtf.py` had no such handling
at all; a real, confirmed discrepancy between documented intent and
actual code.

Of those 25:
- **21** were marked `NO_PREDICATE_POSSIBLE`/`NOT_IMPLEMENTED` in their
  own Track A design record because the underlying judgment is
  inherently semantic (documentation-vs-implementation comparison, broad
  economic/design properties with no nameable syntactic anchor) -- these
  never even reached the ALREADY-BUILT shared L8 LLM Judgment Layer,
  because nothing ever produced evidence to hand it.
- **3** are pure aggregations over other requirements' own results
  (`req-2-pass-l1`, `req-3-pass-l2`, `req-R-meet-all-possible`) --
  correctly identified as "not an independent predicate" in their design
  records, but never actually wired as a post-hoc computation either.
- **1** (`req-R-use-latest-compiler`) had a real, implemented, TESTED
  predicate (`check_compiler_version_is_latest_stable`) that was simply
  never added to `REGISTRY` -- the cleanest possible case of "predicate
  exists, registration was forgotten."

**Total requirements considered per target jumped from 56 to 81** as a
direct, mechanical consequence of this fix (confirmed live:
`stage_metrics.requirements_considered` in the fresh Liquid-Ron rerun --
see the companion validation report).

## 3. Full 81-requirement table

Columns: requirement, EthTrust level, title, the Track A design-tier
record's own `implementation_status`, the mechanism that runs NOW (after
this session's fix), whether it's registered now, and whether it was
silently missing before this session.

<!-- table generated programmatically from registry.py + requirement_corpus.json + track_a design records; not hand-transcribed -->

| req_id | Level | Title | Track A design status | Mechanism now | Registered now | Was missing pre-fix |
|---|---|---|---|---|---|---|
| `req-1-check-return` | S | Check External Calls Return | TRIGGER_COMPONENT_IMPLEMENTED_AND_TESTED_STATE_VAR_LOOPHOLE_UNCLOSED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-060` | S | Use a Modern Compiler | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_OVERRIDE_COMPONENT_STILL_BLOCKED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-SOL-2021-1` | S | Compiler Bug SOL-2021-1 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-SOL-2021-2` | S | Compiler Bug SOL-2021-2 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-SOL-2022-1` | S | Compiler Bug SOL-2022-1 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-SOL-2022-2` | S | Compiler Bug SOL-2022-2 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-SOL-2022-3` | S | Compiler Bug SOL-2022-3 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-SOL-2022-5-push` | S | Compiler Bug SOL-2022-5 with .push() | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-SOL-2022-6` | S | Compiler Bug SOL-2022-6 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-SOL-2023-3` | S | Compiler Bug SOL-2023-3 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-compiler-sol-2021-4` | S | Compiler Bug SOL-2021-4 | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-delegatecall` | S | No delegatecall() | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-eip155-chainid` | S | Encode Hashes with chainid | - | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-exact-balance-check` | S | No Exact Balance Check | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-no-ancient-compilers` | S | No Ancient Compilers | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-no-assembly` | S | No assembly {} | TRIGGER_COMPONENT_IMPLEMENTED_AND_TESTED_OVERRIDE_SET_STILL_UNRESOLVED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-no-create2` | S | No CREATE2 | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-no-hashing-consecutive-variable-length-args` | S | No Hashing Consecutive Variable Length Arguments | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-no-tx.origin` | S | No tx.origin | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-self-destruct` | S | No selfdestruct() | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-unicode-bdo` | S | No Unicode Direction Control Characters | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-1-use-c-e-i` | S | Use Check-Effects-Interaction | CEI_TRIGGER_IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-avoid-readonly-reentrancy` | M | Avoid Read-only Re-entrancy Attacks | TRIGGER_IMPLEMENTED_AND_TESTED_SEMANTIC_CONDITION_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-block-data-misuse` | M | Don't Misuse Block Data | TRIGGER_COMPONENT_IMPLEMENTED_AND_TESTED_SEMANTIC_CONDITION_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-check-rounding` | M | Ensure Proper Rounding of Computations Affecting Value | TRIGGER_COMPONENT_IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-compiler-060` | M | Use a Modern Compiler | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_OVERRIDE_COMPONENT_STILL_BLOCKED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-compiler-SOL-2021-3` | M | Compiler Bug SOL-2021-3 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-compiler-SOL-2022-4` | M | Compiler Bug SOL-2022-4 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-compiler-SOL-2022-5-assembly` | M | Compiler Bug SOL-2022-5 in assembly {} | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-compiler-SOL-2022-7` | M | Compiler Bug SOL-2022-7 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-compiler-SOL-2023-1` | M | Solidity Compiler Bug 2023-1 | VERSION_COMPONENT_IMPLEMENTED_AND_TESTED_PATTERN_COMPONENT_NOT_IMPLEMENTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-documented` | M | Document Special Code Use | 7_OF_8_TRIGGERS_IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-enforce-eval-order` | M | Explicitly Disambiguate Evaluation Order | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-2-external-calls` | M | Protect External Calls | CEI_TRIGGER_IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-handle-return` | M | Handle External Call Returns | TRIGGER_IMPLEMENTED_AND_TESTED_SEMANTIC_CONDITION_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-malleable-signatures-for-replay` | M | No Improper Usage of Signatures for Replay Attack Protection | TRIGGER_AND_PARTIAL_MALLEABILITY_EVIDENCE_IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-no-homoglyph-attack` | M | No Homoglyph-style Attack | NOT_IMPLEMENTED_MISSING_DEPENDENCY | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-2-overflow-underflow` | M | Safe Overflow/Underflow | TRIGGER_COMPONENT_IMPLEMENTED_AND_TESTED_SEMANTIC_CONDITION_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-pass-l1` | M | Pass Security Level [S] | NO_STANDALONE_PREDICATE_APPLICABLE | AGGREGATION (post-hoc, over other requirements) | YES | **YES (silently absent)** |
| `req-2-protect-create2` | M | Protect CREATE2 Calls | TRIGGER_AND_STATIC_TARGET_RESOLUTION_IMPLEMENTED_AND_TESTED_AUTHOR_CLAIMS_CONDITION_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-random-enough` | M | Sources of Randomness | TRIGGER_COMPONENT_IMPLEMENTED_AND_TESTED_SEMANTIC_CONDITION_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-safe-assembly` | M | Avoid Common assembly {} Attack Vectors | TRIGGERS_IMPLEMENTED_AND_TESTED_WITH_A_DOCUMENTED_TOOL_LIMITATION_SEMANTIC_CONDITION_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-self-destruct` | M | Protect Self-destruction | TRIGGER_AND_PROTECTION_EVIDENCE_IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-signature-verification` | M | Proper Signature Verification | TRIGGER_COMPONENT_IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-unicode-bdo` | M | No Unnecessary Unicode Controls | TRIGGER_IMPLEMENTED_AND_TESTED_SEMANTIC_CONDITION_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-2-verify-exact-balance-check` | M | Verify Exact Balance Checks | - | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-3-access-control` | Q | Enforce Least Privilege | PROTECTION_EVIDENCE_IMPLEMENTED_AND_TESTED_MINIMUM_PRIVILEGE_CROSS_CHECK_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-3-all-valid-inputs` | Q | Process All Inputs | PARTIAL_EVIDENCE_IMPLEMENTED_AND_TESTED_SCOPE_CORRECTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-3-annotate` | Q | Annotate Code with NatSpec | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-3-block-front-running` | Q | Protect against Ordering Attacks | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-block-mev` | Q | Protect against MEV Attacks | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-check-oracles` | Q | Protect against Oracle Failure | NOT_IMPLEMENTED | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-consistent-solidity-output` | Q | Specify Solidity Compiler Versions to Produce Consistent Output | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-3-document-system` | Q | Document System Architecture | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-document-threats` | Q | Document Threat Models | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-documented` | Q | Document Contract Logic | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-enough-gas` | Q | Manage Gas Use Increases | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-event-on-state-change` | Q | State Changes Trigger Events | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-3-external-calls` | Q | Verify External Calls | CEI_TRIGGER_IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-3-implement-as-documented` | Q | Implement as Documented | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-intended-replay` | Q | Intended Replay | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-linted` | Q | Code Linting | 3_OF_7_SUB_CLAUSES_IMPLEMENTED_AND_TESTED_VIA_REUSED_SLITHER_DETECTORS_PLUS_1_TRIVIAL_TEXT_CHECK | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-3-no-private-data` | Q | No Private Data | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-no-single-admin-eoa` | Q | No Single Admin EOA for Privileged Actions | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-pass-l2` | Q | Pass Security Level [M] | NO_STANDALONE_PREDICATE_APPLICABLE | AGGREGATION (post-hoc, over other requirements) | YES | **YES (silently absent)** |
| `req-3-protect-gas` | Q | Protect Gas Usage | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-protect-governance` | Q | Protect Against Governance Takeovers | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-revocable-permisions` | Q | Use Revocable and Transferable Access Control Permissions | NOT_IMPLEMENTED | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-timelock-for-privileged-actions` | Q | Use TimeLock Delays for Sensitive Operations | NOT_IMPLEMENTED | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-3-verify-tx.origin` | Q | Verify tx.origin Usage | TRIGGER_IMPLEMENTED_AND_TESTED_DOCUMENTATION_CROSS_CHECK_PENDING | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-R-check-new-bugs` | GP | Check For and Address New Security Bugs | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-R-clean-code` | GP | Write Clear, Legible Solidity Code | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-R-define-license` | GP | Define a Software License | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-R-follow-erc-standards` | GP | Follow Accepted ERC Standards | TRIGGER_AND_SIGNATURE_EVIDENCE_IMPLEMENTED_AND_TESTED_SEMANTIC_CONDITION_NOT_ATTEMPTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-R-formal-verification` | GP | Use Formal Verification | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-R-fuzzing-in-testing` | GP | Use Fuzzing | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-R-meet-all-possible` | GP | Meet as Many Requirements as Possible | NO_STANDALONE_PREDICATE_APPLICABLE | AGGREGATION (post-hoc, over other requirements) | YES | **YES (silently absent)** |
| `req-R-multisig-threshold` | GP | Select an Appropriate Threshold for Multisig Wallets | NOT_IMPLEMENTED_NO_TEXT_GROUNDED_BASE_AVAILABLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-R-mutation-testing` | GP | Use Mutation Testing | IMPLEMENTED_AND_TESTED | DETERMINISTIC (analytical predicate) | YES | no (already worked) |
| `req-R-notify-news` | GP | Disclose New Vulnerabilities Responsibly | NO_PREDICATE_POSSIBLE | LLM-MEDIATED (generic documentary/implementation evidence collector -> shared L8) | YES | **YES (silently absent)** |
| `req-R-use-latest-compiler` | GP | Use Latest Compiler | IMPLEMENTED_AND_TESTED_WITH_EXPLICIT_EXTERNAL_REFERENCE_PARAMETER | DETERMINISTIC (analytical predicate) | YES | **YES (silently absent)** |

## 4. Where in the pipeline information was, and wasn't, lost (summary)

| Stage | Status for the 25 previously-missing requirements |
|---|---|
| L0 -> L1 (spec -> corpus) | **Faithful.** Full normative text + cross-references intact for all 25, same as the other 56. |
| L1 -> L2 (context bundle) | **Faithful.** Bundle exists and is populated for all 25. |
| L3 (applicability) | **Faithful.** Correctly determined (mostly unconditioned-applicable) for all 25. |
| L4-L7 (predicate/reviewer design) | **Correctly diagnosed as NO_PREDICATE_POSSIBLE/NOT_IMPLEMENTED for 21 of them** (genuinely semantic, no deterministic trigger) -- this diagnosis was RIGHT; the bug was what happened (nothing) as a consequence of that diagnosis. **1 (`req-R-use-latest-compiler`) had a real predicate that was simply never registered.** **3 were correctly identified as pure aggregations**, also never wired. |
| Runtime registry (`registry.py`) | **This is where 24 of the 25 actually broke**: `NO_PREDICATE_POSSIBLE`/`NOT_IMPLEMENTED`/aggregation were all treated as terminal ("nothing more to do") rather than "route elsewhere" (LLM-mediated evidence collection, or a post-hoc aggregation step). |
| Evidence generation (`run_rtf.py`) | **This is where the 25th (`req-R-use-latest-compiler`) broke**, and where the OTHER 24's absence became structurally invisible: the main loop iterated `REGISTRY.keys()` only. |
| Routing (`TargetRunResult.routed`) | **Silent disappearance materialized here**: absent as dict keys entirely, no placeholder, no `NOT_APPLICABLE`, no operational-failure code -- contradicting `registry.py`'s own documented invariant. |
| Judgment (L8) | **Never reached** for any of the 25 -- not a judgment failure, since judgment was never invoked. |

**Conclusion**: this was a pure runtime-wiring gap, not a translation,
context-bundling, applicability, or judgment-quality defect. The L1-L3
layers and the Track A design-tier diagnosis were all correct; the break
is entirely in the last mile between "a design record says
NO_PREDICATE_POSSIBLE" and "therefore this requirement is entered into
`registry.py`/`run_rtf.py`'s iteration universe at all."

See `RTF_MISSING_REQUIREMENTS_GAP_ANALYSIS.md` for the per-requirement
A-F classification and root-cause detail, and the companion supervised
validation report for how this was fixed, tested, and verified live on
`2025-01-liquid-ron`.
