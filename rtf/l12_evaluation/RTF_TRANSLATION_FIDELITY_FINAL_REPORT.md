# RTF translation-fidelity work: final report

Consolidates a 7-phase investigation and architecture change, triggered
by the hypothesis that `RTF_MISSED_FINDINGS_ROOT_CAUSE_REPORT.md`'s
Class-E ("EthTrust requirement-coverage gap") classifications were
partly misclassifications — that RTF's translation of broad EthTrust
requirements into investigation questions, not EthTrust's own text, was
the real limiting factor for several misses. Methodology throughout:
**EthTrust spec text and RTF's own code are the source of truth; EVMbench
is used only afterward, to measure, never to justify a change.** No
requirement, predicate, prompt instruction, or property in this work was
derived from an EVMbench finding — every change traces to spec text or a
generic architectural property, verified against synthetic fixtures
before any EVMbench-derived data was consulted.

## 1. Root cause of the prior behavior

Two structurally distinct problems, both confirmed by direct code
tracing, not assumption (`RTF_ETHTRUST_TRANSLATION_AUDIT.md`):

1. **Information loss between spec and prompt.** The corpus's stored
   `normative_text` for several requirements dropped real explanatory
   text (interpretive guidance, worked examples) present in the raw
   spec HTML, and — for `req-2-documented` specifically — dropped two
   entire MUST-obligations due to a genuine parser bug (a text-
   completeness heuristic treated a clause ending in a bare comma as
   finished). Fixed at the root (AR-027).
2. **1:1 requirement-to-investigation cardinality, regardless of scope.**
   `pipeline_e2e.py`'s escalation loop collapsed every `AGENT_REQUIRED`
   requirement to exactly one investigation at the single top-ranked
   evidence location (`candidate_location = ranked[0].item.location`),
   and forwarded a multi-clause requirement's several distinct
   obligations as one undifferentiated block of text — even when a
   requirement's own predicate evidence spanned many distinct sites,
   or its own sentence structure named several separate MUST clauses.
   This was already self-documented as a known, deferred simplification
   in `pipeline_e2e.py`'s own module docstring before this work began.

A third, independent, empirically-confirmed cause was found while
investigating multi-contract scoping: `2024-08-phi`'s real 4-audit-
comparison run only ever created **one** investigation entry
(`Cred.sol`), while the audit's own `scope.txt` declares **9** in-scope
contracts — `PhiFactory.sol` (source of 3 of phi's 5 misses) was never
scoped at all. This was a run-configuration gap (a manually-curated
entry list for cost control), not an RTF architecture limitation.

## 2. Architectural changes made

| # | Change | File(s) | Justification |
|---|---|---|---|
| 1 | Corpus text-extraction fix — a clause ending in a comma/dangling connective is no longer treated as complete | `rtf/l1_corpus/parse_spec.py` | Direct HTML re-read; recovered missing text for 6 requirements |
| 2 | Property/clause derivation — splits a multi-clause requirement into its constituent MUST/MUST-NOT sentences | `rtf/l10_property_derivation/derive_investigations.py` | Spec sentence structure itself (`derive_clauses`), no invented decomposition |
| 3 | Instance expansion — one requirement can produce up to N scoped investigations (one per derived clause × distinct evidence location, capped, every clause guaranteed ≥1 instance first) | same module + `pipeline_e2e.py`'s `_run_escalations_concurrent` | Evidence SHAPE already produced by existing predicates; opt-in (`instance_expansion_enabled`, default False) |
| 4 | FAIL-wins aggregation of multiple instance verdicts into one final requirement verdict | `derive_investigations.aggregate_instance_verdicts` | Reuses the identical precedence `compute_aggregation_requirements` already used for a different aggregation |
| 5 | Repo-structure-derived scope-file discovery (prefers the audit's own `scope.txt`, falls back to a heuristic repo scan) | `rtf/l12_evaluation/scope_discovery.py` | The audit's own self-declared scope; heuristic fallback excludes test/script/mock/vendored dirs and pure interface/library files |
| 6 | 6-state coverage telemetry (`NEVER_CONSIDERED`/`NOT_APPLICABLE`/`EXPLORATION_FAILED`/`APPLIED_TO_WRONG_FUNCTIONS`/`APPLIED_ONCE_GLOBALLY`/`REASONING_FAILED`) | `rtf/l12_evaluation/coverage_telemetry.py` | Purely derived from existing telemetry fields, no new pipeline control flow |
| 7 | Required, harness-enforced counterexample search before `CONFIRMED_SATISFACTION` | `ARM_G_PROMPT_v3.md`, `reasoning_rigor.py`, `codex_bridge.resolve_conformance_from_arm_g` | Generic (not property-specific); an unsupported PASS is downgraded to INCONCLUSIVE with a machine-readable reason, never silently trusted |

All seven are additive and (with the exception of the corpus text fix,
which is a text-fidelity correction with zero logic change) **off by
default** — no existing caller's cost or behavior changes unless
explicitly opted in, mirroring how `max_concurrent_investigations` was
itself introduced.

## 3. Which EthTrust requirements' translation changed

- `req-2-documented` (`Document Special Code Use`): corpus text fixed,
  now carries both previously-missing MUST obligations.
- `req-2-external-calls`, `req-2-self-destruct`, `req-2-protect-create2`,
  `req-2-malleable-signatures-for-replay`, `req-2-compiler-060`: same
  parser fix recovered missing text/structured override relations for
  these five, found as a side effect of fixing the general heuristic
  (not individually targeted).
- Every multi-clause requirement (any `normative_text` with >1 real
  sentence, e.g. `req-2-check-rounding`'s 3 obligations) is now eligible
  for clause-level decomposition when `instance_expansion_enabled=True`.
- Every requirement whose predicate evidence spans >1 distinct location
  (e.g. `req-2-block-data-misuse` on a contract with multiple
  `block.timestamp` reads) is now eligible for multi-location
  investigation under the same flag.

No requirement's applicability logic or predicate trigger changed.

## 4. Before/after investigation-task example

**`req-2-check-rounding`** ("Ensure Proper Rounding of Computations
Affecting Value" — 3 MUST/MUST NOT obligations in one sentence group),
investigated against a contract with one division operation:

- **Before**: 1 investigation. Prompt receives the full 3-clause text
  as one undifferentiated block; the agent must self-decompose which of
  the three obligations (document the error range / don't lose value /
  don't allow exploitable round-trips) it's actually checking, with no
  guarantee all three get equal attention.
- **After** (`instance_expansion_enabled=True`): 3 investigations, one
  per clause, each prompt appending: *"For THIS SPECIFIC investigation,
  focus specifically on the following part of the requirement above...
  [clause text]"* — verified end-to-end in
  `test_instance_expansion.py::test_enabled_multi_clause_requirement_expands_even_with_one_location`.

**`req-2-block-data-misuse`**, contract with 2 functions each reading
`block.timestamp`:

- **Before**: 1 investigation, seeded at whichever function ranked
  higher; the other function's `block.timestamp` read is never
  independently investigated under this requirement.
- **After**: 2 investigations, one per function, final verdict is FAIL
  if either finds a violation (aggregation) — verified in
  `test_instance_expansion.py::test_enabled_multi_location_requirement_expands_into_multiple_calls`.

## 5. Synthetic (non-EVMbench) test results

120 new tests added across 6 new/modified test files, all synthetic
fixtures or real (but ground-truth-independent) spec/repo-structure
data — zero derived from EVMbench vulnerability labels:

| File | Tests | What it covers |
|---|---|---|
| `test_derive_investigations.py` | 40 | Clause derivation (real spec text + synthetic sentences), instance expansion, FAIL-wins aggregation |
| `test_instance_expansion.py` | 15 | End-to-end pipeline wiring, mocked Codex, real multi-location/multi-clause synthetic fixtures |
| `test_scope_discovery.py` | 17 | 8 synthetic temp-dir fixtures + 3 real (zero-cost) checks against actual phi/liquid-ron/canto `scope.txt` |
| `test_coverage_telemetry.py` | 15 | All 6 coverage states, synthetic `RoutedRequirementResult` fixtures |
| `test_reasoning_rigor.py` | 18 | Counterexample-search sufficiency, synthetic decision payloads |
| `test_codex_bridge.py` | 15 | PASS-downgrade behavior, pre-existing timeout/crash behavior unaffected |

Plus the full pre-existing suite (~300 tests across `rtf/l1_corpus`,
`rtf/l2_context_bundles`, `rtf/l5_predicates` (124), `rtf/l8_llm_judgment_layer`,
`rtf/l12_evaluation`, `rtf/standards`) re-verified green after every
phase, including after the corpus regeneration and the PASS-resolution
logic change (which required fixing 2 pre-existing mock fixtures that
simulated a bare PASS with no `counterexample_search` — now opt in to a
well-formed one, since they test concurrency/expansion, not rigor
enforcement).

## 6. EVMbench regression results

**None run.** Per the standing rule (Section 9 of the originating
request: ground truth may only measure improvement, never justify a
change, and only after all implementation work is complete), no paid
Codex run was launched against the fixed pipeline. `scope_discovery.py`
was checked against real audit checkouts, but only for **structural**
correctness (does it recover the file list the audit's own
documentation declares) — never for whether doing so improves detection
scores. That measurement is the natural, explicitly deferred next step,
requiring authorization given real per-run cost (~$2-4/entry × up to 9
entries for phi alone).

## 7. Cost/runtime impact

- Corpus fix, coverage telemetry, reasoning-rigor enforcement: **zero**
  runtime/cost impact on existing runs (text-fidelity/telemetry-only, or
  gated on a PASS already being returned).
- Instance expansion, scope discovery: **zero impact on existing
  callers** (both off by default / additive CLI opt-ins). Enabling
  either multiplies real investigation count and cost proportionally —
  instance expansion is capped at `max_instances_per_requirement`
  (default 6) per requirement; scope discovery's cost impact scales with
  how many additional files an audit's own `scope.txt` declares beyond
  whatever subset was previously hand-picked (e.g. phi: 1 → 9 entries,
  a real, undertaken-with-eyes-open cost increase if ever enabled for a
  live run).

## 8. Remaining genuine EthTrust coverage gaps

From the 12-finding regression-diagnosis sample (see the Revision
section of `RTF_MISSED_FINDINGS_ROOT_CAUSE_REPORT.md`), 2 findings
(`canto` H-01, H-02 — a block-number/timestamp unit mismatch and a
loop-index arithmetic off-by-one) hold up as genuine candidates for
"EthTrust's own text doesn't cover this even under a generous reading":
both are implementation-arithmetic bugs with no named mechanism anywhere
in EthTrust's 81-requirement corpus, static or GP/ERC-generated, and the
`Implement as Documented` broadened-reading argument that explains
several other misses is a real stretch for these two specifically (no
documentation this session found describes the intended epoch protocol
precisely enough to derive the check from). Reported honestly as
unresolved, not forced into an RTF-side bucket for the sake of a cleaner
story.

## 9. Cases where a benchmark vulnerability cannot currently be derived from EthTrust

`forte` H-04 (`eq()` compares raw bit-patterns across different internal
packed-float representations) is the clearest case: even the broadened
`Implement as Documented` functional-correctness reading is a stretch —
representation-invariant equality for a *custom floating-point encoding*
is a benchmark-specific implementation detail EthTrust, a general
smart-contract security standard, was not plausibly written with in
mind. Reported as mixed (`RTF_TRANSLATION_GAP` / `TRUE_ETH_TRUST_GAP`)
rather than resolved either way.

## 10. Answer to the standing question

**Is RTF currently failing because EthTrust lacks the security
requirement, or because RTF fails to translate broad EthTrust functional
requirements into sufficiently concrete protocol-specific properties?**

For the 12-finding sample this investigation is grounded in: **primarily
the latter, and to a real, separately-confirmed degree, a scoping
problem distinct from either.** Of 12 misses:

- **4** (`phi` H-01, H-02 partial, H-04, H-07) trace to a **confirmed**
  scope-exploration gap — `PhiFactory.sol` was never a designated
  investigation entry, and `scope_discovery.py` demonstrably recovers it
  from the audit's own `scope.txt`.
- **5** (`forte` H-01, H-02, H-04, `phi` H-02 secondary) have a
  **plausible, spec-text-grounded, but unconfirmed** translation-gap
  explanation: EthTrust's own Level-Q functional-correctness intent
  plausibly covers them, but RTF's current instantiation of `Implement
  as Documented`/`Process All Inputs` never derives the per-function
  correctness check that would ask the right question.
- **2** (`forte` H-05, `phi` H-03) are reasoning failures, one of which
  (`forte` H-05) is a strong structural match for what the new
  counterexample-search requirement targets.
- **Only 2** (`canto` H-01, H-02) hold up, honestly, as likely genuine
  EthTrust coverage gaps.

This is not proof that RTF's translation is now fixed — none of the
"plausible, unconfirmed" claims above were validated by an actual rerun,
by explicit design (ground truth measures, never justifies, and only
after implementation is complete). It is, however, direct, code-level,
spec-text-grounded evidence that the *dominant* explanation for this
sample's misses was never "EthTrust doesn't cover this" — it was RTF's
own translation, instantiation, and scoping choices, three of which now
have implemented, tested, and (for scoping) empirically-verified fixes.
The next, explicitly deferred step is a real, paid rerun of the three
affected audits with these mechanisms enabled, to see how many of the
"plausible, unconfirmed" reclassifications actually flip to DETECTED.
