# RTF v3: requirement-level implementation status report

Phase 8 deliverable. Generated from `l12_evaluation/requirement_fidelity_
audit.py`'s real, mechanical audit of the live `rtf-v2-redesign` codebase
(`requirement_fidelity_audit_after_phase7.json` — regenerate with
`.venv/bin/python3 -m rtf.l12_evaluation.requirement_fidelity_audit` from
the repo root; add `--skip-conformance-suite` for a faster run that keeps
every requirement below `CONFORMANCE_PASS`). Every number below is read
directly from that JSON, not hand-counted or asserted from memory.

**Definitions (deliberately strict — matches the task brief's explicit
instruction not to assume "parsed" means "supported"):**

- `UNIMPLEMENTED` — no predicate registered at all.
- `PARTIAL` — only a generic documentary-evidence collector registered;
  no code-pattern predicate exists for this requirement's own subject
  matter, so applicability depends on the target's own documentation.
- `IMPLEMENTED_UNTESTED` — a real structural predicate + routing exist,
  but no conformance fixture/test yet.
- `CONFORMANCE_PASS` — structural predicate + a real fixture pair +
  a green end-to-end conformance run (`tests/ethtrust_conformance/`).
- `N/A_COMPOSITE` — a pure aggregation over every other requirement
  ("pass Level 1/2" / "meet all applicable requirements") — has no
  independent predicate by design, not a gap.

## Headline numbers

```
Requirements parsed (corpus size):        81
Composite aggregates (N/A by design):       3
Requirements with applicability
  implementation (structural predicate):   59
Requirements applicability-only via
  documentary evidence (PARTIAL):          19
Requirements with end-to-end
  conformance tests (CONFORMANCE_PASS):     6
Requirements still only
  IMPLEMENTED_UNTESTED:                    53
```

**We do NOT claim all 81 parsed requirements are "supported."** 53 of 81
(65%) have real routing/predicate machinery but no conformance test yet
— genuinely `IMPLEMENTED_UNTESTED`, not silently upgraded. 19 of 81
(23%) have only documentary-evidence applicability, a real but weaker
signal than a structural predicate. Full-corpus conformance coverage was
explicitly out of scope for this effort (see "Migration strategy" in
`RTF_V3_REDESIGN_PLAN.md` §E) — this report exposes that honestly rather
than projecting it as done.

## By level (S/M/Q/GP)

| Level | CONFORMANCE_PASS | IMPLEMENTED_UNTESTED | PARTIAL | N/A_COMPOSITE | Total |
|---|---|---|---|---|---|
| S (22) | 1 | 21 | 0 | 0 | 22 |
| M (24) | 2 | 19 | 2 | 1 | 24 |
| Q (24) | 3 | 7 | 13 | 1 | 24 |
| GP (11) | 0 | 6 | 4 | 1 | 11 |

Q-level (broad, holistic requirements — "Document Contract Logic",
"Manage Gas Use Increases", process/documentation obligations) has both
the highest CONFORMANCE_PASS count (3 — including this effort's own
newly-added `req-3-enough-gas`) and the highest PARTIAL count (13) —
consistent with Q-level's own character: many Q requirements ask
genuinely doc-vs-implementation comparison questions with no nameable
syntactic anchor (per the corpus's own `NO_PREDICATE_POSSIBLE`/
`NOT_IMPLEMENTED` classification, `registry.py`'s own docstring), so the
documentary-evidence collector is often the CORRECT mechanism, not a gap
— e.g. `req-3-document-threats`/`req-3-documented` genuinely require
comparing prose claims to implementation, not a code pattern.

## The 6 CONFORMANCE_PASS requirements (this effort's representative slice)

| req_id | Category | Mechanism |
|---|---|---|
| `req-2-block-data-misuse` | Block data / cross-boundary semantics | 2 structural predicates (own-read + cross-boundary-argument); mocked-agent Tier 2 |
| `req-3-all-valid-inputs` | Input domain validation | 2 structural predicates; safe fixture resolves PASS with **zero agent calls** (real "unconditioned" path) |
| `req-3-enough-gas` | Growing persistent state / gas | **New Phase 5 predicate** (`find_unbounded_growth_with_downstream_iteration`) + pre-existing documentary collector |
| `req-3-access-control` | Access control | Pre-existing structural predicate; mocked-agent Tier 2 |
| `req-2-external-calls` | External calls | Pre-existing structural predicate; safe fixture resolves **NOT_APPLICABLE with zero agent calls** |
| `req-1-no-tx.origin` | Static/deterministic | `DETERMINISTIC_COMPLETE` — vulnerable/safe both resolve fully deterministically, **zero LLM involvement at all** |

3 of 6 (`req-3-all-valid-inputs`'s safe side, `req-2-external-calls`'s
safe side, both sides of `req-1-no-tx.origin`) reach a genuine FAIL/PASS/
NOT_APPLICABLE conformance result with **zero mocking and zero LLM
cost** — real architecture behavior, not a testing artifact. The other
3 (both sides of `req-2-block-data-misuse`/`req-3-access-control`,
vulnerable side of `req-3-enough-gas`/`req-3-all-valid-inputs`) require
an agent investigation by design (the predicate correctly stays
over-inclusive/APPLICABLE in both the vulnerable and safe case — the
distinguishing judgment genuinely belongs to the investigator, not
routing) and are conformance-tested via the mocked-agent Tier 2 harness
(`tests/ethtrust_conformance/conformance_harness.py`), per the task
brief's explicit "deterministic/mock LLM behavior... for CI" instruction.

## The 19 PARTIAL (documentary-evidence-only) requirements

```
req-2-enforce-eval-order, req-2-no-homoglyph-attack,
req-3-timelock-for-privileged-actions, req-3-check-oracles,
req-3-block-front-running, req-3-block-mev, req-3-protect-governance,
req-3-no-private-data, req-3-intended-replay, req-3-documented,
req-3-document-system, req-3-document-threats,
req-3-implement-as-documented, req-3-revocable-permisions,
req-3-no-single-admin-eoa, req-R-check-new-bugs, req-R-clean-code,
req-R-notify-news, req-R-multisig-threshold
```

Each of these was independently assessed in Track A's own design record
as `NO_PREDICATE_POSSIBLE`/`NOT_IMPLEMENTED` because it requires
comparing DOCUMENTED claims against IMPLEMENTATION behavior, or reviews
a broad organizational/process practice with no nameable syntactic
anchor (`registry.py`'s own `_DOC_EVIDENCE_REQ_IDS` docstring). This is
NOT automatically wrong — `req-3-enough-gas`/`req-3-protect-gas` are the
two requirements this effort found and fixed with a genuine structural
predicate (Phase 5), proving the classification is not permanent, but
the remaining 19 have not been re-examined this session; each would need
its own Phase-5-style code-pattern investigation, individually, before
being upgraded — explicitly flagged as future work, not claimed done.

## The 3 N/A_COMPOSITE requirements

`req-2-pass-l1`, `req-3-pass-l2`, `req-R-meet-all-possible` — pure
aggregations ("pass Level 1" / "pass Level 2" / "meet all applicable
requirements"). By design, these have no independent predicate; their
real conformance is a function of every constituent requirement's own
state, resolved by `compute_aggregation_requirements`, not investigated
independently. Not a gap.

## What changed this session vs. baseline

| Metric | Pre-Phase-1 baseline | After Phase 5 | After Phase 7 (final) |
|---|---|---|---|
| structural_predicate applicability | 57 | 59 | 59 |
| documentary_evidence_only (PARTIAL) | 21 | 19 | 19 |
| CONFORMANCE_PASS | 0 | 0 | 6 |
| IMPLEMENTED_UNTESTED | 57 | 59 | 53 |

(`requirement_fidelity_audit_baseline.json` → `_after_phase5.json` →
`_after_phase7.json`, all committed, all reproducible by re-running the
audit script at each corresponding commit.)

## Limitations, stated plainly

- **Full-corpus conformance coverage was never the goal of this
  effort.** 6 of 81 requirements have real end-to-end conformance
  fixtures; the remaining 75 (including all 19 PARTIAL ones) do not.
  Extending Phase 7's fixture methodology to the rest of the corpus is
  real, valuable, and NOT done here — explicitly future work.
- **The mocked-agent Tier 2 harness tests verdict-resolution PLUMBING,
  not real LLM reasoning quality.** A live-Codex variant of the same 6
  fixtures (real spend, opt-in, per the task brief's explicit
  instruction to keep live-agent tests separate) would be the next real
  validation step, not done this session.
- **Phase 5's new growth predicate is deliberately per-contract**, not a
  whole-project call-graph search like `find_cross_boundary_block_data_
  argument` — a genuinely cross-contract growth/iteration split (growth
  in contract A, iteration in contract B) would not be caught yet;
  documented in the predicate's own docstring, not silently assumed
  covered.
- **Phase 6's guidance table covers 3 reasoning shapes out of many** the
  81-requirement corpus's own `ReasoningCategory` taxonomy names (16
  categories total). Extending it further should follow the same
  discipline (grounded in verbatim requirement text, mechanically
  checked for benchmark-identifier leakage) but was not attempted beyond
  the representative slice.
