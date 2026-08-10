# RTF Pipeline & Requirements Reference

A complete reference for how the RTF (Requirement Translation Framework)
pipeline currently works, what requirement "rules" exist and where they
come from, and — grounded in a real, completed, paid run against
`2025-01-liquid-ron`'s `LiquidRon.sol` — exactly which requirements fired,
how, and why. Every number and finding in the "How they fired" section
below is pulled directly from that real run's artifacts
(`rtf/l12_evaluation/pilot5_artifacts/2025-01-liquid-ron_v5_gp_generator_LiquidRonOnly/`),
not invented or approximated.

---

## 1. Architecture overview

```
                     TWO REQUIREMENT SOURCES, MERGED INTO ONE POOL
   ┌─────────────────────────────┐        ┌───────────────────────────────────┐
   │ A. Frozen EthTrust corpus    │        │ B. GP/ERC-standards generator      │
   │    81 requirements           │        │    (rtf/standards/)                │
   │    (S / M / Q / GP levels)   │        │    dynamically generates N reqs    │
   └──────────────┬───────────────┘        └────────────────┬────────────────────┘
                  │                                          │
                  └───────────────────┬──────────────────────┘
                                       ▼
                       ROUTING (per requirement, one of):
                 NOT_APPLICABLE │ DETERMINISTIC_COMPLETE │ AGENT_REQUIRED │ AGGREGATION
                                       │
                          (AGENT_REQUIRED requirements only)
                                       ▼
                    CODEX INVESTIGATION (full repo access, real reasoning)
                 optionally CONCURRENT (max_concurrent_investigations)
                                       │
                                       ▼
                        RESULT MERGE → audit.md (FAIL findings only)
                                       │
                                       ▼
                      DetectGrader (external, real upstream LLM judge)
```

### 1.1 Source A: the frozen EthTrust corpus

`rtf/l1_corpus/requirement_corpus.json` — 81 requirements hand-translated
from the real EEA EthTrust Security Levels spec (Version 3), split into
4 levels:

| Level | Count | Meaning |
|---|---|---|
| **S** | 22 | Level S (baseline security) normative requirements |
| **M** | 24 | Level M (medium) normative requirements |
| **Q** | 24 | Level Q (high) normative requirements |
| **GP** | 11 | Good Practice (advisory, non-certification-blocking) |

Each requirement has: `req_id`, `level`, `title`, `normative_text`,
`modality` (MUST/SHOULD/etc.), and a `conditioned_scope_clause` stating
what subject it applies to. This corpus is **frozen** — never modified by
anything the GP generator does.

### 1.2 Source B: the GP/ERC-standards generator (`rtf/standards/`)

One specific corpus entry, `req-R-follow-erc-standards` ("[GP] Follow
Accepted ERC Standards"), is not evaluated directly like the other 80 —
it acts as a **generator**. Its pipeline:

```
StandardsRegistry (rtf/standards/registry.py)
   loads pinned, hash-verified spec snapshots from rtf/standards/erc/<ID>/
        │
        ▼
discover_applicable_standards(repo, entry, slither)
   per registered standard, entirely DATA-DRIVEN off that standard's own
   standard.json "detection_signals" -- inheritance / imports / NatSpec /
   documentation claims (strong) + function-signature/event overlap
   (supporting, never sufficient alone)
        │
        ▼
generate_requirements_for_standard(record, clauses)
   ONE GeneratedRequirement per normative clause, deterministic ID,
   full provenance (source spec, section, normative strength,
   conditions/exceptions never flattened)
        │
        ▼
determine_clause_applicability(req, detection, slither)
   two levels: is the STANDARD applicable to this contract, AND does
   THIS clause's specific target (a named function/event) actually
   exist on the implementing contract
```

Currently two standards are registered:

| Standard | Status | Clauses | Source |
|---|---|---|---|
| **ERC-4626** (Tokenized Vaults) | Final | 77 | `rtf/standards/erc/ERC-4626/` — pinned EIP-4626 spec text |
| **ERC-20** (Token Standard) | Final | 14 | `rtf/standards/erc/ERC-20/` — pinned EIP-20 spec text |

"Accepted ERC" = EIP status `Final` (or `Living`), traced to EthTrust's
own bibliography citation for "[ERC]" (`"ERC Final"` →
`eips.ethereum.org/erc`) — not an invented definition. See
`rtf/standards/GP_ACCEPTED_ERC_DEFINITION.md`.

**Every generated requirement routes to a real agent investigation,
unconditionally** — `rtf/standards/routing.py::classify_requirement`
always returns `AGENT_REQUIRED` for the only derivation type currently
produced (`STANDARD_CLAUSE_DIRECT`), on the same conservative-default
logic as the 81-corpus (below): none of these obligations are
mechanically decidable without real reasoning.

### 1.3 Routing rules (how a requirement's evaluation path is decided)

For the **81-corpus**, `rtf/l12_evaluation/registry.py` partitions every
requirement with a registered predicate into exactly one of:

| Routing | Count (of 81) | Meaning |
|---|---|---|
| **DETERMINISTIC_COMPLETE** | 19 | Predicate evidence IS the final verdict — no LLM/agent at all |
| **AGENT_REQUIRED** | 59 | Routes directly to a full-repo-access Codex investigation — **no bounded pre-filter gate**; this used to exist and is what caused a real missed finding earlier in this project (see §5) |
| **AGGREGATION** | 3 | Pure AND-aggregation over other already-resolved requirements (`req-2-pass-l1`, `req-3-pass-l2`, `req-R-meet-all-possible`) |

For the **generated pool**, every requirement is `AGENT_REQUIRED`
(§1.2). A requirement can also resolve to **NOT_APPLICABLE** before
routing matters at all, if its `conditioned_scope_clause` (81-corpus) or
`determine_clause_applicability` result (generated) rules it out for
this specific contract — with an explicit reason recorded either way,
never a silent drop.

### 1.4 The agent investigation itself

Every `AGENT_REQUIRED` requirement with evidence gets a real Codex
investigation (`rtf/l8_llm_judgment_layer/bundle_agent_experiment/arm_g_codex.py`):

- **Full repository access** — a complete copy of the repo (not an
  excerpt, not a graph-revealed subset) becomes the agent's working
  directory from turn one.
- **The requirement's exact text** — obligation, normative strength,
  conditions/exceptions, and (for generated requirements) the real
  detection evidence explaining *why* the standard was determined
  applicable.
- **Normal shell tools** (`grep`/`find`/`cat`/`sed`) plus optional
  structural graph-query tools (callers/callees/state-reads/inheritance)
  — the graph tools are a convenience, never a precondition; there is no
  `candidate_location` requirement and no fixed source-excerpt limit.
- Returns `PASS` / `FAIL` / `INCONCLUSIVE` / `INSUFFICIENT_EVIDENCE`
  with a `reasoning_summary`, `confidence`, and structured evidence.

**Concurrency**: `run_pipeline_e2e(..., max_concurrent_investigations=N)`
runs up to N of these investigations at once via a `ThreadPoolExecutor`.
Each investigation is fully isolated (own repo copy, own home directory,
own solc working directory, all keyed by a unique `case_id`) — confirmed
both architecturally and empirically (grepped real command logs from a
live concurrent run: zero genuine race/interference signatures). Default
is `1` (fully serial, unchanged legacy behavior); the real run below used
`8`.

### 1.5 Result merge, reporting, grading

- Every `FAIL` result across the merged pool becomes one section of
  `audit.md` (requirement text, location, confidence, agent reasoning,
  evidence). `PASS`/`INCONCLUSIVE`/`INSUFFICIENT_EVIDENCE` are not
  findings and are omitted from the report body.
- `audit.md` is graded by the real upstream **DetectGrader** — an LLM
  judge external to RTF, comparing reported findings against the audit's
  actual ground-truth vulnerabilities. RTF cannot see or influence this.
- Integrity is checked two ways: the existing invariant (every
  requirement reaches exactly one terminal status, `silently_missing ==
  0`) now runs over the full merged pool; a separate
  `StandardsIntegrityReport` tracks the generated-pool-specific
  breakdown (standards discovered, clauses loaded, requirements
  generated/applicable/routed).

---

## 2. How they fired — real results from `2025-01-liquid-ron`'s `LiquidRon.sol`

**Run summary** (from `pilot_summary.json` / `entry_00_LiquidRon_stage.json`):

| Metric | Value |
|---|---|
| Requirements considered | **172** (81 from the EthTrust corpus + 91 generated: 77 ERC-4626 + 14 ERC-20) |
| Requirements applicable | 149 |
| Real Codex investigations | 124 |
| Real cost | **$13.6056** |
| Wall clock | ~88.7 minutes (8x concurrent) |
| Integrity | **valid=True**, `silently_missing=0` |
| Final decisions | **95 PASS · 46 FAIL · 23 NOT_APPLICABLE · 5 EXECUTION_ERROR · 3 INCONCLUSIVE** |
| DetectGrader score | **1/1 — H-01 detected** (`judge_model=openai/gpt-4.1`; standard `gpt-4o` hit its 128k context limit on this 46-finding report, same documented substitution as a prior run) |

Both standards fired independently on `LiquidRon.sol`: ERC-4626 via real
`is ERC4626`/`is IERC4626` inheritance + a README documentation claim
(16/16 canonical signatures, both events); ERC-20 the same way (a vault
is inherently a token too).

### 2.1 The H-01 detection, in detail

**Ground truth (H-01)**: `totalAssets()` incorrectly handles
`operatorFeeAmount` — an accrued-but-unpaid operator fee still sitting in
the vault's balance gets excluded from `totalAssets()` prematurely
(via `getTotalRewards()` subtracting it), which under/over-values shares
around the fee-payout event and can cost depositors real funds.

**Detecting requirement**: `gp-accepted-standard__erc-4626__erc4626-totalassets-must-include-fees`

- **Source**: ERC-4626 clause `erc4626-totalassets-must-include-fees`,
  normative strength `MUST`, generated verbatim from the pinned EIP-4626
  spec text (`rtf/standards/erc/ERC-4626/clauses.json`) — **not** derived
  from H-01's description in any way.
- **Rule text**: *"totalAssets() MUST be inclusive of any fees that are
  charged against assets in the Vault -- amounts owed to a third party
  (e.g. an accrued operator/management fee) that are still held in the
  Vault's asset balance are still part of totalAssets() until actually
  paid out."*
- **Applicability**: standard ERC-4626 applicable (contract `LiquidRon`,
  confidence 0.95, evidence: inheritance + doc claim + 16/16 signatures +
  both events); clause target `totalAssets` present, no unresolved
  condition → `APPLICABLE`.
- **Routing**: `AGENT_REQUIRED` (unconditional for generated requirements).
- **Real agent's finding** (HIGH confidence): *"totalAssets relies on
  getTotalRewards which subtracts operator fees before adding rewards to
  the total, causing unpaid fees still in vault custody to be omitted and
  violating ERC-4626's requirement to include such fees until paid."*
- **DetectGrader's judgment**: `detected: true` — *"The mechanisms and
  code locations match the described vulnerability: both highlight that
  operatorFeeAmount ... is not handled properly in totalAssets(),
  leading to incorrect valuation and potential user losses."*

**Why this matters**: before the GP/ERC-standards generator existed, a
prior session's forensic analysis of this exact same target (using only
the static 81-requirement corpus) classified this miss as primarily
class **E** — a genuine *requirement-coverage limitation*: no EthTrust
requirement was shaped to ask this specific ERC-4626 accounting
question, despite 4 independent investigations reading the exact
relevant code under different lenses (rounding, front-running, gas,
generic ERC-interface conformance — see the `req-2-check-rounding`,
`req-3-block-front-running`, `req-3-enough-gas`, and
`req-R-follow-erc-standards` FAIL findings in §2.2, all of which touch
the same code region without directly stating H-01's mechanism). The
generator closed exactly that gap: a requirement whose text is precisely
on-topic now exists, fires, and — in this real, paid run — a real agent
used it to correctly diagnose the issue.

### 2.2 FAIL findings (46) — full detail

Every requirement whose final state was `FAIL`, across both requirement
sources, with the real agent's (or deterministic predicate's) reasoning.

| req_id | source | level/std | strength | routing | confidence | mechanism (agent reasoning) |
|---|---|---|---|---|---|---|
| `gp-accepted-standard__erc-20__erc20-callers-must-handle-false-return` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | ERC20 methods are invoked via IERC20 without using SafeERC20 or checking returned bool for approve and transferFrom, violating the requirement to handle false returns. |
| `gp-accepted-standard__erc-20__erc20-callers-must-not-assume-false-never-returned` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED | HIGH | ERC20 methods in LiquidRon and Escrow are invoked without checking their boolean return values, directly assuming success; this violates the ERC-20 note that callers must not assume these functions never return false. |
| `gp-accepted-standard__erc-4626__erc4626-converttoassets-must-not-include-fees` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED | MEDIUM | LiquidRon inherits OZ convertToAssets, which uses totalAssets. LiquidRon overrides totalAssets to subtract operator fees from rewards (getTotalRewards returns rewards minus fee). Thus convertToAssets uses a fee-reduced … |
| `gp-accepted-standard__erc-4626__erc4626-converttoshares-must-not-include-fees` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED | MEDIUM | convertToShares relies on totalAssets, which LiquidRon overrides to exclude operator fees via getTotalRewards subtraction. This makes convertToShares’ result inclusive of fees charged against assets, violating the MUST_… |
| `gp-accepted-standard__erc-4626__erc4626-converttoshares-must-not-revert-unless-overflow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED | MEDIUM | convertToShares is inherited from OpenZeppelin ERC4626. In LiquidRon, it relies on a totalAssets override that performs external Ronin validator calls. Any failure in those external view calls will revert convertToShare… |
| `gp-accepted-standard__erc-4626__erc4626-maxdeposit-must-factor-in-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | LiquidRon is an ERC4626 vault that pauses deposits via the whenNotPaused modifier, disabling deposits when paused. However, it does not override maxDeposit, so the inherited ERC4626 implementation always returns the max… |
| `gp-accepted-standard__erc-4626__erc4626-maxdeposit-must-not-overestimate` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | Because LiquidRon does not override maxDeposit, it always returns an unlimited value. However, deposits are blocked when paused, making the actual permissible deposit 0 in that state. maxDeposit therefore overestimates … |
| `gp-accepted-standard__erc-4626__erc4626-maxmint-must-factor-in-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | LiquidRon inherits ERC4626.maxMint which always returns uint256.max. The contract pauses mint/deposit via whenNotPaused, disabling minting, but maxMint remains unlimited and does not return 0 or reflect any limits. Ther… |
| `gp-accepted-standard__erc-4626__erc4626-maxmint-must-not-overestimate` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | LiquidRon inherits OZ ERC4626 maxMint which always returns the maximum uint256. Minting is gated by whenNotPaused, so when the vault is paused maxMint overestimates the actual allowable mint amount (should be zero). Thi… |
| `gp-accepted-standard__erc-4626__erc4626-maxredeem-must-factor-in-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | LiquidRon inherits ERC4626 without overriding maxRedeem, so the function always returns the caller’s share balance. The contract disables redemption via whenNotPaused on withdraw/redeem, but maxRedeem does not factor th… |
| `gp-accepted-standard__erc-4626__erc4626-maxredeem-must-not-overestimate` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | The contract is pausable; when paused, redeems/withdraws revert, so the maximum permitted redemption is zero. LiquidRon does not override ERC4626’s maxRedeem, which always returns the caller’s share balance and ignores … |
| `gp-accepted-standard__erc-4626__erc4626-maxwithdraw-must-factor-in-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | LiquidRon relies on Pausable to block withdrawals, but maxWithdraw is inherited from OZ and ignores pause or other limits, returning full convertible assets even when withdrawals are disabled. Requirement demands maxWit… |
| `gp-accepted-standard__erc-4626__erc4626-previewdeposit-must-include-fees` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | LiquidRon relies on OpenZeppelin ERC4626.previewDeposit with no overrides or deposit-fee adjustments. The contract has no deposit fee mechanism; only operator fees on rewards. Thus previewDeposit cannot include deposit … |
| `gp-accepted-standard__erc-4626__erc4626-previewwithdraw-must-include-fees` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | LiquidRon inherits ERC4626 and does not override previewWithdraw; the inherited function performs a simple asset-to-share conversion without fee handling. The contract implements only an operator fee on rewards, with no… |
| `gp-accepted-standard__erc-4626__erc4626-redeem-may-support-preexisting-shares-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED | HIGH | The ERC-4626 redeem override delegates to OpenZeppelin’s redeem which enforces share ownership/allowance and burns shares in-call, assuming shares are moved during execution. There is no alternate logic to recognize sha… |
| `gp-accepted-standard__erc-4626__erc4626-totalassets-must-include-fees` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED | HIGH | totalAssets relies on getTotalRewards which subtracts operator fees before adding rewards to the total, causing unpaid fees still in vault custody to be omitted and violating ERC-4626’s requirement to include such fees … |
| `gp-accepted-standard__erc-4626__erc4626-totalassets-must-not-revert` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED | HIGH | LiquidRon.totalAssets aggregates staking proxies and rewards by calling external staking contract view functions without safeguards; any revert bubbles up, violating ERC-4626 requirement that totalAssets must not revert. |
| `req-1-no-assembly` | EthTrust-corpus | S | MUST NOT | AGENT_REQUIRED | HIGH | Inline assembly is present in Math.mulDiv (and elsewhere in Math) within the tested codebase. The requirement prohibits assembly unless the set of overriding requirements is met; no such justification or documentation i… |
| `req-1-no-hashing-consecutive-variable-length-args` | EthTrust-corpus | S | MUST NOT | DETERMINISTIC_COMPLETE |  |  |
| `req-1-use-c-e-i` | EthTrust-corpus | S | MUST | AGENT_REQUIRED | HIGH | harvest/harvestAndDelegateRewards perform external calls to LiquidProxy before state updates and without reentrancy guards, allowing reentrancy to repeat harvesting/fees; CEI not followed. |
| `req-2-check-rounding` | EthTrust-corpus | M | MUST,MUST,MUST NOT,MUST | AGENT_REQUIRED | MEDIUM | Reward and fee calculations round down via integer division, and redemption uses floor rounding with heuristic offsets. No code comments or documentation identify rounding risks or quantify possible error, violating the… |
| `req-2-documented` | EthTrust-corpus | M | MUST | AGENT_REQUIRED | MEDIUM | The requirement mandates documentation of the need for each special operation, including external calls. The Escrow constructor performs an external approve without any accompanying explanation, and other external calls… |
| `req-2-pass-l1` | EthTrust-corpus | M | MUST | AGGREGATION |  |  |
| `req-3-access-control` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | HIGH | Documentation gives operators and owner staking-control privileges, but onlyOperator is misimplemented to revert for any operator, allowing only a non-operator owner. All staking-control functions are therefore inaccess… |
| `req-3-annotate` | EthTrust-corpus | Q | MUST | DETERMINISTIC_COMPLETE |  |  |
| `req-3-block-front-running` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | MEDIUM | The vault’s user-facing deposit/withdraw/redeem paths execute immediately against the current price-per-share with no slippage or delay controls. Operators can change totalAssets via harvest/delegate/undelegate right be… |
| `req-3-block-mev` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | MEDIUM | Across LiquidRon, no MEV-aware design (deadlines, slippage, sequencing locks) is implemented. Conversions for deposits/withdrawals and epoch redemption rely on mutable totals that block producers or operators can reorde… |
| `req-3-consistent-solidity-output` | EthTrust-corpus | Q | MUST | DETERMINISTIC_COMPLETE |  |  |
| `req-3-document-system` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | MEDIUM | Repository documentation covers system design, roles, and usage, but lacks explicit security assumptions required by the EthTrust requirement. |
| `req-3-document-threats` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | HIGH | Searched README.md and source files for threat/assumption/attack terms and reviewed README content; found no documented threat models detailing threats, security assumptions, expected responses, or outcomes, so the requ… |
| `req-3-enough-gas` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | MEDIUM | User-facing ERC4626 flows invoke totalAssets(), which loops over staking proxies and all validators. Validators are appended whenever operators touch a new consensus address and are only optionally pruned, so the loop c… |
| `req-3-event-on-state-change` | EthTrust-corpus | Q | MUST | DETERMINISTIC_COMPLETE |  |  |
| `req-3-external-calls` | EthTrust-corpus | Q | MUST,MUST | AGENT_REQUIRED | MEDIUM | External calls to proxies are documented as operator-only, but the implemented onlyOperator modifier rejects marked operators and only permits the owner, making the protection incompatible with the documented access ass… |
| `req-3-implement-as-documented` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | HIGH | Documentation promises operators can manage staking and finalize withdrawal epochs, but onlyOperator logic requires sender be owner and not marked operator, so all operator-only functions are owner-only. This contradict… |
| `req-3-no-single-admin-eoa` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | HIGH | All privileged operations are gated by a single Ownable `owner` address; operator functions are also effectively owner-only due to the `onlyOperator` condition. There is no multisig or higher-privileged multisig overrid… |
| `req-3-pass-l2` | EthTrust-corpus | Q | MUST | AGGREGATION |  |  |
| `req-3-protect-governance` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | HIGH | Governance is entirely centralized in a single owner with no timelock or multisig, and the operator role is unusable due to the onlyOperator check, meaning all operational and parameter controls rest on one key. This de… |
| `req-3-revocable-permisions` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | HIGH | LiquidRon gates privileged functions with owner-only controls and an operator mapping, but the onlyOperator modifier is flawed and rejects operators, and there is no explicit revocation/transfer mechanism for operators … |
| `req-3-timelock-for-privileged-actions` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED | HIGH | Sensitive owner-controlled operations (fee changes, operator assignment, proxy deployment, pause/unpause) execute immediately without any timelock. No timelock contract is integrated despite a comment acknowledging it c… |
| `req-R-check-new-bugs` | EthTrust-corpus | GP | ? | AGENT_REQUIRED | MEDIUM | Project still targets solc 0.8.20 and contains no documentation or mitigation addressing compiler security bugs disclosed after Nov 1, 2023; requirement explicitly calls for such a review, so it is not satisfied. |
| `req-R-clean-code` | EthTrust-corpus | GP | SHOULD | AGENT_REQUIRED | MEDIUM | Readability is reduced by mislabeled/incorrect `onlyOperator` logic that hides actual access behavior and by two differently behaving `redeem` functions sharing a name, making the code harder to understand and reason ab… |
| `req-R-follow-erc-standards` | EthTrust-corpus | GP | SHOULD | AGENT_REQUIRED | MEDIUM | Although LiquidRon inherits ERC4626, its withdraw/redeem functions divert the asset transfer to the vault and pay out native RON instead of delivering the ERC4626 asset to the receiver, violating ERC4626 behavioral expe… |
| `req-R-fuzzing-in-testing` | EthTrust-corpus | GP | SHOULD | DETERMINISTIC_COMPLETE |  |  |
| `req-R-multisig-threshold` | EthTrust-corpus | GP | SHOULD | AGENT_REQUIRED | HIGH | All admin and pause functions rely on OpenZeppelin Ownable single-owner gating; no multisig or threshold is implemented, making privileged actions effectively 1-of-1, contrary to the requirement. |
| `req-R-notify-news` | EthTrust-corpus | GP | SHOULD | AGENT_REQUIRED | MEDIUM | Requirement recommends providing a responsible-disclosure process. Searched primary documentation (README.md, README-sponsor.md) and contract files; no instructions or references to reporting vulnerabilities were found,… |
| `req-R-use-latest-compiler` | EthTrust-corpus | GP | SHOULD | DETERMINISTIC_COMPLETE |  |  |

### 2.3 PASS (95)

Requirements the agent (or a deterministic predicate) investigated and
found genuinely satisfied.

| req_id | source | level/std | strength | routing |
|---|---|---|---|---|
| `gp-accepted-standard__erc-20__erc20-approval-event-must-trigger-on-approve` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-decimals-must-not-be-relied-upon` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-name-must-not-be-relied-upon` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-symbol-must-not-be-relied-upon` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-transfer-event-must-trigger-on-transfer` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-transfer-event-should-trigger-on-mint-from-zero` | ERC-20 | EXTERNAL_STANDARD_DERIVED | SHOULD | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-transfer-must-fire-transfer-event` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-transfer-should-throw-on-insufficient-balance` | ERC-20 | EXTERNAL_STANDARD_DERIVED | SHOULD | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-transfer-zero-value-must-fire-event` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-transferfrom-must-fire-transfer-event` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-transferfrom-should-throw-if-unauthorized` | ERC-20 | EXTERNAL_STANDARD_DERIVED | SHOULD | AGENT_REQUIRED |
| `gp-accepted-standard__erc-20__erc20-transferfrom-zero-value-must-fire-event` | ERC-20 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-asset-must-be-erc20-token` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-asset-must-not-revert` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-convertto-functions-must-both-round-down` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-converttoassets-must-not-reflect-slippage` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-converttoassets-must-not-revert-unless-overflow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-converttoassets-must-not-vary-by-caller` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-converttoassets-must-round-down` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-converttoshares-must-not-reflect-slippage` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-converttoshares-must-not-vary-by-caller` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-converttoshares-must-round-down` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-deposit-event-must-be-emitted` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-deposit-may-support-preexisting-balance-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-deposit-must-emit-event` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-deposit-must-revert-if-cannot-complete` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-deposit-must-support-approve-transferfrom-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-eip2612-may-implement` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-maxdeposit-must-not-revert` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-maxdeposit-must-return-max-uint-if-unlimited` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-maxmint-must-not-revert` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-maxmint-must-return-max-uint-if-unlimited` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-maxredeem-must-not-revert` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-maxwithdraw-must-not-overestimate` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-maxwithdraw-must-not-revert` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-mint-may-support-preexisting-balance-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-mint-must-emit-event` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-mint-must-revert-if-cannot-complete` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-mint-must-support-approve-transferfrom-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-name-symbol-should-reflect-underlying` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | SHOULD | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-nontransferable-may-revert-transfer` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewdeposit-may-revert-for-other-conditions` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewdeposit-must-approximate-paired-action` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewdeposit-must-not-account-for-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewdeposit-must-not-revert-for-vault-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewmint-may-revert-for-other-conditions` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewmint-must-approximate-paired-action` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewmint-must-include-fees` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewmint-must-not-account-for-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewmint-must-not-revert-for-vault-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewredeem-may-revert-for-other-conditions` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewredeem-must-approximate-paired-action` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewredeem-must-include-fees` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewredeem-must-not-account-for-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewredeem-must-not-revert-for-vault-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewwithdraw-may-revert-for-other-conditions` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewwithdraw-must-approximate-paired-action` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewwithdraw-must-not-account-for-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-previewwithdraw-must-not-revert-for-vault-limits` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST_NOT | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-redeem-must-revert-if-cannot-complete` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-redeem-must-support-erc20-allowance-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-redeem-must-support-owner-is-sender-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-redeem-should-check-spender-allowance` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | SHOULD | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-totalassets-should-include-yield` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | SHOULD | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-vault-must-implement-erc20` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-vault-must-implement-erc20-metadata` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-withdraw-event-must-be-emitted` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-withdraw-may-support-preexisting-shares-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MAY | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-withdraw-must-emit-event` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-withdraw-must-revert-if-cannot-complete` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-withdraw-must-support-erc20-allowance-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-withdraw-must-support-owner-is-sender-flow` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `gp-accepted-standard__erc-4626__erc4626-withdraw-should-check-spender-allowance` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | SHOULD | AGENT_REQUIRED |
| `req-1-compiler-060` | EthTrust-corpus | S | MUST NOT | AGENT_REQUIRED |
| `req-1-compiler-SOL-2023-3` | EthTrust-corpus | S | MUST | AGENT_REQUIRED |
| `req-1-delegatecall` | EthTrust-corpus | S | MUST NOT | DETERMINISTIC_COMPLETE |
| `req-1-eip155-chainid` | EthTrust-corpus | S | MUST | DETERMINISTIC_COMPLETE |
| `req-1-exact-balance-check` | EthTrust-corpus | S | MUST NOT | DETERMINISTIC_COMPLETE |
| `req-1-no-ancient-compilers` | EthTrust-corpus | S | MUST NOT | DETERMINISTIC_COMPLETE |
| `req-1-no-create2` | EthTrust-corpus | S | MUST NOT | DETERMINISTIC_COMPLETE |
| `req-1-no-tx.origin` | EthTrust-corpus | S | MUST NOT | DETERMINISTIC_COMPLETE |
| `req-1-self-destruct` | EthTrust-corpus | S | MUST NOT | DETERMINISTIC_COMPLETE |
| `req-2-compiler-060` | EthTrust-corpus | M | MUST NOT | AGENT_REQUIRED |
| `req-2-compiler-SOL-2023-1` | EthTrust-corpus | M | MUST | AGENT_REQUIRED |
| `req-2-enforce-eval-order` | EthTrust-corpus | M | MUST NOT | AGENT_REQUIRED |
| `req-2-no-homoglyph-attack` | EthTrust-corpus | M | MUST | AGENT_REQUIRED |
| `req-2-overflow-underflow` | EthTrust-corpus | M | MUST NOT | AGENT_REQUIRED |
| `req-2-safe-assembly` | EthTrust-corpus | M | MUST NOT | AGENT_REQUIRED |
| `req-2-signature-verification` | EthTrust-corpus | M | MUST | AGENT_REQUIRED |
| `req-3-all-valid-inputs` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED |
| `req-3-check-oracles` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED |
| `req-3-documented` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED |
| `req-3-intended-replay` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED |
| `req-3-no-private-data` | EthTrust-corpus | Q | MUST NOT | AGENT_REQUIRED |
| `req-3-protect-gas` | EthTrust-corpus | Q | MUST | AGENT_REQUIRED |

### 2.4 NOT_APPLICABLE (23)

Requirements whose `conditioned_scope_clause` (81-corpus) correctly
ruled them out for this specific contract before any investigation was
needed — e.g. compiler-bug requirements for solc versions this project
doesn't use, or requirements about constructs (CREATE2, `tx.origin`
verification, malleable-signature replay) simply absent from this
codebase.

| req_id | source | level/std | title/obligation |
|---|---|---|---|
| `req-1-check-return` | EthTrust-corpus | S | Check External Calls Return |
| `req-1-compiler-SOL-2021-1` | EthTrust-corpus | S | Compiler Bug SOL-2021-1 |
| `req-1-compiler-SOL-2021-2` | EthTrust-corpus | S | Compiler Bug SOL-2021-2 |
| `req-1-compiler-SOL-2022-1` | EthTrust-corpus | S | Compiler Bug SOL-2022-1 |
| `req-1-compiler-SOL-2022-2` | EthTrust-corpus | S | Compiler Bug SOL-2022-2 |
| `req-1-compiler-SOL-2022-3` | EthTrust-corpus | S | Compiler Bug SOL-2022-3 |
| `req-1-compiler-SOL-2022-5-push` | EthTrust-corpus | S | Compiler Bug SOL-2022-5 with .push() |
| `req-1-compiler-SOL-2022-6` | EthTrust-corpus | S | Compiler Bug SOL-2022-6 |
| `req-1-compiler-sol-2021-4` | EthTrust-corpus | S | Compiler Bug SOL-2021-4 |
| `req-2-avoid-readonly-reentrancy` | EthTrust-corpus | M | Avoid Read-only Re-entrancy Attacks |
| `req-2-block-data-misuse` | EthTrust-corpus | M | Don't Misuse Block Data |
| `req-2-compiler-SOL-2021-3` | EthTrust-corpus | M | Compiler Bug SOL-2021-3 |
| `req-2-compiler-SOL-2022-4` | EthTrust-corpus | M | Compiler Bug SOL-2022-4 |
| `req-2-compiler-SOL-2022-5-assembly` | EthTrust-corpus | M | Compiler Bug SOL-2022-5 in assembly {} |
| `req-2-compiler-SOL-2022-7` | EthTrust-corpus | M | Compiler Bug SOL-2022-7 |
| `req-2-handle-return` | EthTrust-corpus | M | Handle External Call Returns |
| `req-2-malleable-signatures-for-replay` | EthTrust-corpus | M | No Improper Usage of Signatures for Replay Attack Protection |
| `req-2-protect-create2` | EthTrust-corpus | M | Protect CREATE2 Calls |
| `req-2-random-enough` | EthTrust-corpus | M | Sources of Randomness |
| `req-2-self-destruct` | EthTrust-corpus | M | Protect Self-destruction |
| `req-2-verify-exact-balance-check` | EthTrust-corpus | M | Verify Exact Balance Checks |
| `req-3-verify-tx.origin` | EthTrust-corpus | Q | Verify tx.origin Usage |
| `req-R-mutation-testing` | EthTrust-corpus | GP | Use Mutation Testing |

### 2.5 INCONCLUSIVE (3)

| req_id | source | level/std | strength | routing |
|---|---|---|---|---|
| `gp-accepted-standard__erc-4626__erc4626-redeem-must-emit-event` | ERC-4626 | EXTERNAL_STANDARD_DERIVED | MUST | AGENT_REQUIRED |
| `req-2-external-calls` | EthTrust-corpus | M | MUST,MUST,MUST,MUST | AGENT_REQUIRED |
| `req-R-meet-all-possible` | EthTrust-corpus | GP | SHOULD | AGGREGATION |

### 2.6 EXECUTION_ERROR (5)

| req_id | source | level | title |
|---|---|---|---|
| `req-1-unicode-bdo` | EthTrust-corpus | S | No Unicode Direction Control Characters |
| `req-2-unicode-bdo` | EthTrust-corpus | M | No Unnecessary Unicode Controls |
| `req-3-linted` | EthTrust-corpus | Q | Code Linting |
| `req-R-define-license` | EthTrust-corpus | GP | Define a Software License |
| `req-R-formal-verification` | EthTrust-corpus | GP | Use Formal Verification |

---

## 3. Where things live (file map)

| Path | What |
|---|---|
| `rtf/l1_corpus/requirement_corpus.json` | Frozen 81-requirement EthTrust corpus |
| `rtf/l12_evaluation/registry.py` | `DETERMINISTIC_COMPLETE_REQ_IDS` / `AGENT_REQUIRED_REQ_IDS` / `AGGREGATION_REQ_IDS` partition |
| `rtf/standards/registry.py` | Loads/validates pinned standard snapshots |
| `rtf/standards/discovery.py` | Generic, data-driven standard-applicability detection |
| `rtf/standards/generator.py` | Clause → `GeneratedRequirement` translation + applicability |
| `rtf/standards/routing.py` | Bridges generated requirements into the pipeline's `RoutedRequirementResult` shape |
| `rtf/standards/erc/ERC-4626/clauses.json` | All 77 ERC-4626 normative clauses, with provenance |
| `rtf/standards/erc/ERC-20/clauses.json` | All 14 ERC-20 normative clauses, with provenance |
| `rtf/l12_evaluation/pipeline_e2e.py` | Main orchestrator — routing, escalation loop (serial + concurrent), integrity |
| `rtf/l12_evaluation/pilot5_driver.py` | Multi-entry driver: runs the pipeline per scope file, merges FAILs, grades |
| `rtf/l12_evaluation/report_generator.py` | Renders `PipelineArtifacts` → `audit.md` |
| `rtf/l12_evaluation/ETH_TRUST_GP_IMPLEMENTATION_REPORT.md` | Full architecture/design report for the GP generator |
| `rtf/l12_evaluation/RTF_TRIGGER_COVERAGE_REPORT.md` | Pre-run zero-cost prediction that this exact requirement would cover H-01 |
| `rtf/l12_evaluation/RTF_CONCURRENT_INVESTIGATIONS.md` | Concurrency design + verification |
| `rtf/l12_evaluation/pilot5_artifacts/2025-01-liquid-ron_v5_gp_generator_LiquidRonOnly/` | This run's real artifacts: `audit.md`, `pilot_summary.json`, `entry_00_LiquidRon_stage.json` |
