# RTF Trigger Coverage Report

Zero-cost (no live Codex/LLM calls anywhere) trigger-coverage study of the
standards-driven GP requirement generator, per the implementation plan's
§19-§21. Machine-readable results: `rtf_trigger_coverage.json`.

## Scope

**Covered**: `2025-01-liquid-ron`, all 6 in-scope files
(`LiquidRon.sol`, `Escrow.sol`, `LiquidProxy.sol`, `RonHelper.sol`,
`ValidatorTracker.sol`, `Pausable.sol`), against this audit's one graded
ground-truth finding, **H-01**.

**Explicitly deferred** (not attempted this session): the other 4 EVMbench
audits RTF has previously been validated against (canto, vultisig,
arbitrum-foundation, sequence). This was a direct choice by the user
(`AskUserQuestion`, this session) after the Liquid-Ron sanity check passed
cleanly: *"Just finish liquid-ron's other 5 entries first"* — full
multi-audit trigger coverage remains a distinct, larger undertaking
(real compute cost even at $0, compiling many real audit repos) pending a
later explicit request. This report does not claim coverage beyond what
is stated here.

**Methodology discipline maintained**: ground truth (H-01's finding text)
was used only as a comparison oracle, never fed into standard detection,
clause extraction, requirement generation, applicability determination, or
routing. See `ETH_TRUST_GP_IMPLEMENTATION_REPORT.md`'s §13 for one
important, honestly-disclosed caveat to this: H-01's text had already
entered this conversation's context in a prior session before this
GP-generator implementation began, so "frozen before consultation" here
means the CODE was frozen and pushed before this specific comparison was
written down — not that H-01 was never read by anyone at any point before
any of this code existed. Independent evidence the mechanism was not
tuned toward H-01 regardless: the generated clause is a verbatim
transcription of the real EIP-4626 spec sentence, not a paraphrase of
H-01's bug description; the same code produces correct negative results
(`UNCERTAIN`/`NOT_APPLICABLE`) on 5 other real files from this same audit;
ERC-20 was generated with equal rigor despite zero relationship to H-01;
all 16 ERC-4626 methods got clauses, not a hand-picked subset around
`totalAssets`.

## Finding-by-finding results

### H-01 (`2025-01-liquid-ron`) — **RTF_TRIGGER_COVERED**

| | |
|---|---|
| Relevant code | `src/LiquidRon.sol` `totalAssets()`, `operatorFeeAmount` accrual/withdrawal |
| Mapped RTF requirement | `gp-accepted-standard__erc-4626__erc4626-totalassets-must-include-fees` |
| Requirement source | `req-R-follow-erc-standards` → ERC-4626 (EIP-4626, `status: Final`) → clause `erc4626-totalassets-must-include-fees` |
| Source clause text | *"totalAssets() MUST be inclusive of any fees that are charged against assets in the Vault."* |
| Standard discovered? | **Yes** — inheritance (`is ERC4626, ...` / `IERC4626`) + documentation claim + 16/16 signature match + both events |
| Requirement generated? | **Yes** |
| Applicable? | **Yes** — `totalAssets` is present on `LiquidRon`, no unresolved condition |
| Evaluator | AGENT_REQUIRED (unconditional for this derivation type) |
| Mock Codex invoked? | **Yes**, verified by `test_mock_codex_routing.py` (39/39 passing) against the real orchestrator |
| Trigger covered? | **Yes** |

**Rationale**: every step of the zero-cost-answerable chain — discovered,
generated, applicable, fired, would reach the agent — is independently
confirmed with real evidence (see `rtf_trigger_coverage.json` for the
full evidence list and `GP_LIQUID_RON_SANITY_CHECK.md` for the raw run
output). This is **not** a claim that a real investigation would
correctly diagnose H-01's exact mechanism — that distinction (an accrued
operator fee being a third-party claim rather than a vault-level dilution
fee, which EIP-4626's own spec text does not itself draw) is exactly the
kind of semantic reasoning question routed to a real agent, not resolved
here. Verifying it requires a real, currently-ungated Codex investigation.

**Contrast with the pre-GP-generator architecture**: a prior session's
forensic classification of this same miss (using only the static
81-requirement EthTrust corpus, before any of this GP-generator work
existed) concluded primarily **E** — requirement-coverage limitation: no
EthTrust requirement was shaped to ask this specific accounting question,
despite 4 independent investigations reading the exact relevant code
under different lenses (rounding, front-running, gas, ERC-interface
conformance). This GP generator closes exactly that requirement-coverage
gap — a requirement now exists whose text is precisely on-topic. Whether
it also closes the gap at the *investigation* level remains untested.

## Coverage summary (this session's scope only)

| Classification | Count |
|---|---|
| RTF_TRIGGER_COVERED | 1 (H-01) |
| NO_REQUIREMENT | 0 |
| STANDARD_DISCOVERY_FAILURE | 0 |
| STANDARD_TRANSLATION_FAILURE | 0 |
| APPLICABILITY_FAILURE | 0 |
| ROUTING_FAILURE | 0 |
| UNSUPPORTED_RUNTIME | 0 |
| **Total findings evaluated** | **1 of 1 in scope (100%)** |

**This is not a claim of 100% EVMbench-wide coverage.** It is 100% of the
single finding in the single audit this session's explicitly-authorized
scope covers. The other 4 previously-validated audits (and the rest of
EVMbench) have not been run through this mechanism and make no
contribution to this number.

## Acceptance gate status (plan §23, in-scope items only)

All 14 gates that don't require the deferred multi-audit study are
satisfied — see `ETH_TRUST_GP_IMPLEMENTATION_REPORT.md` for the full,
itemized verification of each. Gate 14 ("Liquid-Ron independently
activates the expected applicable-standard mechanism before H-01 ground
truth is consulted") is satisfied with the one honest caveat disclosed
above and in that report's §13.

**No paid EVMbench run has been started or is planned by this report.**
Per the plan's explicit instruction, coverage below 100% would mean STOP
and analyze every uncovered finding first — that scenario did not arise
in-scope, but the study also did not cover enough of EVMbench to draw any
conclusion about full-corpus coverage either way. Extending this study to
the other 4 audits (or the full benchmark) remains available on explicit
request.
