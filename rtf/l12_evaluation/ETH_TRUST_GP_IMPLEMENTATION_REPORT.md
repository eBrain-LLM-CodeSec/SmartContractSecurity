# EthTrust [GP] Follow Accepted ERC Standards — Implementation Report

Implements EthTrust's `req-R-follow-erc-standards` (`[GP] Follow Accepted
ERC Standards`) as a generic, standards-driven RTF requirement generator,
per the phased plan this report closes out. Branch `worktree-mgpr-router2`,
commits `9cafd70`..`ddda827` (6 commits, Phases 1-5 + a live-found bug fix).

## 1. Architecture

```
EthTrust GP (req-R-follow-erc-standards, already a distinct "GP" level
in the frozen 81-requirement l1 corpus -- see §2)
      |
StandardsRegistry.all_ids()  ── discover which standards are registered
      |
discover_applicable_standards(repo, entry, slither)  ── per-standard,
      |                                                   data-driven
      |                                                   detection
generate_requirements_for_standard(record, clauses)  ── 1 clause = 1
      |                                                   GeneratedRequirement
determine_clause_applicability(req, detection, slither)  ── 2-level
      |                                                       (standard +
      |                                                       clause)
classify_requirement(req)  ── routing decision (currently always
      |                        AGENT_REQUIRED)
build_standards_routed_requirements(...)  ── merges into the SAME
      |                                       RoutedRequirementResult
      |                                       shape the 81-corpus uses
pipeline_e2e.run_pipeline_e2e's EXISTING Codex-escalation loop
      (zero changes to its core logic -- confirmed generic in Phase 0's
      architecture trace, verified by every test in this report)
```

Each stage is its own module under `rtf/standards/`, independently
unit-tested, with zero dependency on any specific audit/benchmark entry.

## 2. Files changed

**New, isolated package** (`rtf/standards/`, nothing here existed before
this work):
- `models.py` -- `NormativeStrength`, `NormativeClause`, `StandardRecord`,
  `DetectionSignal`, `StandardDetectionResult`, `GeneratedRequirement`,
  `RequirementApplicabilityResult`, `DerivationType`.
- `registry.py` -- `StandardsRegistry`: loads/validates `standard.json` +
  `clauses.json` per standard, hash-pins the spec snapshot, enforces the
  "accepted ERC" status gate (`ACCEPTED_STATUSES = {"Final", "Living"}`).
- `clause_parser.py` -- generic RFC2119 extractor, proven against
  synthetic fixtures only (never used for production clauses.json — see
  §5).
- `discovery.py` -- `discover_applicable_standards`: data-driven,
  standard-agnostic detection off each standard's own registered
  `detection_signals`.
- `generator.py` -- `generate_requirements_for_standard`,
  `determine_clause_applicability`.
- `routing.py` -- `classify_requirement`,
  `render_generated_requirement_bundle`,
  `build_standards_routed_requirements` (the pipeline bridge — the only
  module here that imports from `rtf.l12_evaluation`).
- `GP_ACCEPTED_ERC_DEFINITION.md` -- the "what counts as accepted"
  decision record (§4).
- `erc/ERC-4626/` -- pinned spec snapshot + 77 hand-authored clauses.
- `erc/ERC-20/` -- pinned spec snapshot + 14 hand-authored clauses
  (second standard, registered specifically to prove genericity — §11).
- 6 test files (`test_registry.py`, `test_clause_parser.py`,
  `test_discovery.py`, `test_generator.py`, `test_routing.py`,
  `test_mock_codex_routing.py`) — 144 tests total.

**Minimal, additive changes to existing pipeline files** (nothing removed
or behaviorally changed for the frozen 81-requirement path — confirmed by
re-running every existing test suite after each change, §9):
- `rtf/l12_evaluation/codex_bridge.py`: `build_codex_prompt_inputs` gains
  one new optional parameter, `bundle_record: dict | None = None`
  (default preserves existing behavior exactly). When given, skips the
  `rtf/l2_context_bundles/<req_id>.json` file requirement — the one seam a
  dynamically-generated req_id needs, since it has no on-disk L2 bundle
  file and never will.
- `rtf/l12_evaluation/pipeline_e2e.py`: after `run_rtf()`, merges
  `build_standards_routed_requirements()`'s output into `run.routed`
  (additive dict merge). The existing Codex-escalation loop needed **zero
  changes** to its routing/escalation logic — it was already fully
  generic over `(req_id, RoutedRequirementResult)` pairs. `PipelineArtifacts`
  gains two new, defaulted fields: `standards_report`, `generated_bundles`.
- `rtf/l12_evaluation/report_generator.py`: falls back to a generated
  requirement's real bundle text for its `audit.md` title/body instead of
  the bare (long, opaque) requirement_id string.

## 3. GP representation (not a silent 82nd requirement)

`req-R-follow-erc-standards` remains exactly what it already was in the
frozen L1 corpus: one `level: "GP"` entry among 81, distinct from `S`/`M`/`Q`
(this distinction pre-dates this work — see `rtf/l1_corpus/
requirement_corpus.json`'s `by_level` field). What's new is that its
`parent_requirement_id` now anchors an entirely separate,
`EXTERNAL_STANDARD_DERIVED` pool: each `GeneratedRequirement` carries
`source_family="ERC"`, `source_id="ERC-4626"|"ERC-20"`,
`parent_requirement_id="req-R-follow-erc-standards"`,
`derivation_type=STANDARD_CLAUSE_DIRECT` — never merged into
`requirement_corpus.json`, never counted toward the "81." Two of the two
existing static-corpus-size tests (`test_runtime_coverage.py`,
`test_agentic_architecture.py`) still assert `== 81` unmodified and still
pass, because generated requirements are a logically separate pool by
construction.

## 4. Standards registry + "accepted ERC" definition

`GP_ACCEPTED_ERC_DEFINITION.md` traces EthTrust's own citation for
"finalized [ERC]" to `eips.ethereum.org/erc` ("ERC Final") in the pinned
EthTrust spec source itself — not invented. `registry.py`'s
`ACCEPTED_STATUSES = {"Final", "Living"}` enforces this as a hard,
tested load-time gate (`test_unaccepted_status_fails`): a standard whose
pinned snapshot doesn't say `status: Final` (or `Living`) fails to
register at all.

Two standards are currently registered, both real, pinned, hash-verified
snapshots fetched by direct HTTPS GET (not a summarizing WebFetch — same
precedent the project's own EthTrust spec snapshot already established):
- **ERC-4626** (Tokenized Vaults, `status: Final`): 77 clauses covering
  every one of its 16 methods (`asset` through `redeem`), both events, the
  top-level EIP-20-conformance MUSTs, and the one explicit cross-function
  Security-Considerations invariant.
- **ERC-20** (Token Standard, `status: Final`): 14 clauses — deliberately
  smaller, because EIP-20's own text is genuinely terser (3 of its 6 core
  view methods carry no RFC2119 keyword at all — documented honestly in
  `clauses.json`'s own `excluded_as_non_normative_note`, not padded out).
  Registered specifically to prove the mechanism generalizes beyond
  ERC-4626, not as an exhaustive ERC-20 translation.

## 5. Clause extraction: reviewed/pinned, not auto-parsed

Per the plan's own explicit fallback instruction, **production clauses
are manually authored** by reading the pinned spec text section by
section (`extraction_method: "MANUAL_REVIEWED_PINNED"` in both
`clauses.json` files, with an `extraction_method_note` explaining why —
real EIP prose is too irregular for a fully automatic pass: many method
descriptions share the identical bare sentence "MUST NOT revert." across
different functions with no distinguishing text; the `Security
Considerations` section states its one MUST as cross-function prose, not
a per-method bullet). `clause_parser.py`'s generic RFC2119 extractor is
built and unit-tested (29 tests) purely to prove the extraction MECHANISM
works generically — conditions, exceptions, multiline statements,
multiple-keyword paragraphs, and false-positive avoidance (a lowercase
"must" in ordinary prose is correctly never extracted, matching RFC2119's
own capitalization convention) — and is deliberately never run against
either standard's real production `clauses.json`.

## 6. Standard discovery: generic, data-driven, no per-standard code

`discovery.py` interprets each standard's own registered
`detection_signals` (from `standard.json`) generically by `signal_type`
(`inheritance`/`import`/`natspec`/`documentation_claim` as strong;
`function_signatures`/`events`/`known_library_import` as supporting).
**Zero ERC-4626-specific or ERC-20-specific code exists anywhere in this
file** — confirmed both by code inspection and by the fact that adding
ERC-20 as a second standard required editing zero lines of `discovery.py`,
only registering a new `standard.json`.

Vendored-dependency-aware: a project contract inheriting from a vendored
OpenZeppelin/Solmate base is correctly detected (the base's definition may
live under `lib/`); the vendored library's OWN internal definitions are
never themselves credited as "the audited project's implementation"
(`_is_interface`/`_is_vendored_path` guards, both added after real bugs —
see §8).

## 7. Requirement generation: source-driven, deterministic

`generate_requirements_for_standard` produces exactly one
`GeneratedRequirement` per `NormativeClause` (`DerivationType.
STANDARD_CLAUSE_DIRECT` — the only derivation type this generator
currently performs). `requirement_id` is a pure function of
`(standard_id, clause_id)` — no timestamp, no randomness — verified
byte-for-byte-identical across repeated generation runs
(`test_generation_is_deterministic_byte_for_byte`). Every provenance
field the plan required is populated and tested: `source_family`,
`source_id`, `source_title`, `source_url_or_local_spec`, `source_version`,
`source_section`, `normative_strength` (preserved, never flattened —
MUST/SHOULD/MAY stay distinct all the way through), `parent_requirement_id`,
`derivation_type`, plus `conditions`/`exceptions` kept as separate lists
from `obligation_text` (never silently folded into an unconditional
statement — a dedicated test, `test_extracts_condition_without_
flattening_to_unconditional`, exercises exactly this).

## 8. Applicability: two-level, every branch explicit

Per §11: `discover_applicable_standards` answers "is the standard
applicable at all" (contract-level); `determine_clause_applicability`
separately answers "is THIS clause's specific target present" — an
optional-feature clause (e.g. a function absent from this specific
implementation) resolves `NOT_APPLICABLE` with an explicit reason, never
silently dropped. A clause with an activation CONDITION that cannot be
mechanically evaluated from structure alone (e.g. "if the Vault is
non-transferrable...") resolves `UNKNOWN` — routed to the agent to resolve
from real repository content, not silently assumed true or false.

**Two real bugs were found and fixed by testing against real code, not
assumed safe:**
1. **Interface-to-interface inheritance** (`interface IERC4626 is IERC20
   {...}`) was initially miscounted as `IERC4626` "implementing" ERC-20 —
   Slither's `contracts_derived` includes interface declarations
   alongside real contracts, and `.inheritance` treats an ancestor
   interface exactly like it would a real base contract. Fixed by
   excluding `contract_kind == "interface"` from every implementer-
   candidate loop; caught by a negative test built for exactly this case
   (`test_negative_erc20_imported_as_dependency_not_implemented`), not
   discovered by inspection.
2. **Project-wide documentation-claim over-attribution**, found live
   against a real EVMbench target (`2025-01-liquid-ron`'s
   `Pausable.sol`, `RonHelper.sol`, and 3 other unrelated helper files):
   a repo-wide README claim ("this project implements ERC-4626") was
   being auto-credited to whichever single contract happened to be the
   sole non-vendored contract in an isolated single-file compilation
   unit — which for a file with no imports is trivially that file's own
   contract, regardless of relevance. Fixed by removing that fallback
   entirely; a bare documentation claim with no corroborating code
   signal now correctly resolves `UNCERTAIN`, never a false `APPLICABLE`.
   Full writeup: `GP_LIQUID_RON_SANITY_CHECK.md`.

## 9. Routing: always to the agent, conservative by default

`classify_requirement` returns `AGENT_REQUIRED` unconditionally for every
`STANDARD_CLAUSE_DIRECT` requirement — documented rationale: ERC clause
obligations (accounting correctness, exact behavioral relationships
between two DIFFERENT functions in the same transaction, rounding-
direction correctness) are inherently semantic, not mechanically
decidable, mirroring `rtf.l12_evaluation.registry`'s own conservative-
default discipline (19 of 78 registered requirements are
`DETERMINISTIC_COMPLETE`; the rest default to agent). No deterministic
carve-out was invented without justification — the `RoutingDecision.
DETERMINISTIC_COMPLETE` branch exists in `routing.py` but is
unreachable, reserved for a future, individually-justified narrower path.

Proven, not merely claimed, via 39 tests spying on the REAL Codex
invocation boundary (`patch.object(pipeline_e2e, "run_arm_g_bundle", ...)`,
never simulated independently): every sampled agent-required generated
requirement invokes the mock exactly once; `NOT_APPLICABLE` requirements
never invoke it; the 81-corpus's own deterministic requirements still
never invoke it with standards generation running alongside; an unrelated
repository produces zero invocations while every requirement still
reaches an explicit `NOT_APPLICABLE` terminal state; a graph-seed
resolution failure (mocked to always raise) does not block invocation; no
generated requirement's `conformance_state` is ever non-`None` without a
real, corresponding `codex_results` entry.

## 10. Integrity accounting

Two invariants, both independently checked:
1. `pipeline_e2e.compute_integrity_report` (UNMODIFIED code) runs over the
   FULL merged `routed` dict (81-corpus + generated) — `silently_missing`
   genuinely covers generated requirements too, not just the frozen
   corpus.
2. `routing.StandardsIntegrityReport` (new, additive, never bolted onto
   `IntegrityReport`'s own shape) tracks the §12 breakdown specifically:
   standards considered/discovered-applicable/uncertain/not-applicable,
   clauses loaded, requirements generated/applicable/not-applicable/
   routed(deterministic|agent), with its own `silently_missing` computed
   independently (a requirement_id -> exactly-one-terminal-status set
   difference, not inherited from #1).

Confirmed `silently_missing == 0` and `valid == True` in every unit test
AND on the real `2025-01-liquid-ron` target (all 6 in-scope files).

## 11. Multi-standard proof

ERC-20 was registered specifically to prove genericity, not as a second
production translation target. `test_multi_standard_erc4626_and_erc20_
both_discovered_independently` confirms both standards fire independently
on a synthetic dual-conformant vault with fully separate, non-colliding
provenance. **Independently reconfirmed on the real target**: `LiquidRon.sol`
triggers both ERC-4626 (91→77 of its clauses) and ERC-20 (14 clauses)
with distinct evidence trails, exactly as the synthetic fixture predicted.

## 12. Tests

144 new tests across 6 files (all passing, `.venv/bin/python3 -m
rtf.standards.test_X` — this project's real `check()`/`PASSES`/`FAILURES`
harness convention, not bare `pytest`):
- `test_registry.py` (18): load-by-ID, provenance retention, hash
  stability, duplicate/malformed/unsupported-strength/hash-mismatch/
  unaccepted-status failures, no-network-access enforcement.
- `test_clause_parser.py` (29): all 5 RFC2119 keyword pairs, conditions,
  exceptions, multiline, multi-keyword paragraphs, false-positive
  avoidance (twice — bare lowercase mention, and a lowercase-prose
  sentence alongside a real one in the same paragraph).
- `test_discovery.py` (18): fixtures 1-6 (correct impl, >8000-char
  late-file impl, inherited impl, cross-function accounting,
  interface-only-not-implemented, partial/nonconforming-still-detected),
  4 negative cases, 1 multi-standard fixture — all against REAL compiled
  Solidity, never mocked.
- `test_generator.py` (21): determinism, provenance, normative-strength
  preservation, condition preservation, both applicability levels.
- `test_routing.py` (19): routing-decision classification, full
  `build_standards_routed_requirements` end-to-end (real evidence, real
  bundle text, real integrity counters), the not-applicable path.
- `test_mock_codex_routing.py` (39): §16/§17 positive and negative
  routing against the real `run_pipeline_e2e` orchestrator.

**Full existing regression suite, re-run fresh**: all 6 existing
`rtf/l12_evaluation` test suites (168 tests) pass unchanged.
`rtf/l5_predicates/test_predicates.py`: 120/121 pass — the 1 failure is a
pre-existing, unrelated, confirmed environmental flake (`solc-select`'s
global version file is shared mutable state across this machine's many
concurrent background sessions; `compile_helper.py` and `predicates.py`
are untouched by any commit in this entire effort).

## 13. Known limitations

- **Routing is not literally blind to H-01.** `findings/H-01.md`'s full
  text was already present in this conversation's context from a prior
  session, before this GP-generator implementation began (visible as an
  already-read file in the system-reminder that opened this
  conversation). This is a real, material caveat to the plan's §19/§23
  ("Liquid-Ron independently activates the expected applicable-standard
  mechanism before H-01 ground truth is consulted") — the discipline here
  could not be a literal blind construction in the strictest sense, since
  the finding text had already entered context. What CAN be claimed, and
  is independently verifiable: (a) every ERC-4626 clause is a direct,
  section-by-section transcription of the real EIP-4626 spec text — the
  `totalAssets` fee-inclusion clause's wording is the spec's own sentence,
  not a paraphrase of H-01's bug description; (b) the discovery/generation/
  routing code contains no LiquidRon-specific or H-01-specific term
  anywhere, confirmed by grep and by the fact that the exact same code
  correctly produces `UNCERTAIN`/`NOT_APPLICABLE` on 5 other real files
  from the same audit that have nothing to do with H-01; (c) ERC-20 was
  generated with equal rigor (14 real clauses) despite zero relationship
  to H-01; (d) 77 total ERC-4626 clauses were extracted covering all 16
  methods, not a hand-picked subset around `totalAssets`. This is offered
  as the honest basis for confidence, not a claim of literal blindness.
- **Zero-cost preflight proves opportunity, not success.** Confirming a
  generated requirement is applicable and would reach a real Codex
  investigation is not the same as confirming that investigation would
  correctly diagnose the underlying issue — that remains an empirical
  question for a real (paid, currently ungated) run. See
  `GP_LIQUID_RON_SANITY_CHECK.md`'s own "Honest scoping" section.
- **`known_library_import` supporting signals rarely fire on real
  Foundry-remapped imports** (`import "@openzeppelin/..."` doesn't
  literally contain the full library path `known_library_import`'s
  patterns check for). Harmless in practice — the strong `inheritance`
  signal already carries detection on every real target checked so far —
  but a real gap in that one specific supporting signal, not hidden.
- **`ERC-4626`/`ERC-20` are the only two registered standards.** The
  mechanism is built to scale (registering a third standard is a
  `standard.json` + `clauses.json` addition, zero code changes), but only
  these two have been built and clause-authored.
- **Full multi-audit EVMbench trigger-coverage study was explicitly
  deferred by the user** to `2025-01-liquid-ron` only (all 6 in-scope
  files) for this session — see `RTF_TRIGGER_COVERAGE_REPORT.md` for the
  resulting, honestly-scoped coverage classification and what remains
  out of scope.
