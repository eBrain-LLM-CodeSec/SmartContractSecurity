# MGPR Evidence Analysis (P1/P2/P5 slice)

**Purpose of this document.** This is a descriptive analysis of the seven
artifacts produced by one run of the MGPR router-input sufficiency study
(`benchmark_registry.jsonl`, `build_manifest.jsonl`, `graph_manifest.jsonl`,
`gate_evaluation.jsonl`, `route_manifest.jsonl`, `context_manifest.jsonl`,
`feasibility_report.json`). It contains no pass/fail verdict, no readiness
label, and no recommendation. Every count below states its own denominator.
Interpretation — whether any of this is "enough," what to build next, whether
to expand to more families or more audits — is left to the reader.

Run identity: registry generated from `splits/detect-tasks.txt` (40 pinned
audits); checkouts available locally for 3 of those 40; routing spec =
`routing_spec.yaml` (P1_AUTHORIZATION, P2_REENTRANCY, P5_ARITHMETIC_PRECISION
`SPECIFIED`, 13 other families `NOT_YET_SPECIFIED`).

---

## 1. Registry and build coverage

| Metric | Value | Denominator |
|---|---|---|
| Total registered audits | 40 | pinned `detect-tasks.txt` |
| Total findings in registry | 120 | 40 audits |
| Audits with a local checkout attempted | 3 | 40 |
| Audits with no local checkout (`SKIPPED`) | 37 | 40 |
| Audits `COMPILED` | 2 | 40 (3 attempted) |
| Audits `COMPILE_FAILED` | 1 | 40 (3 attempted) |
| Findings belonging to a `COMPILED` audit | 3 | 120 |
| Findings blocked by audit compile status (not evaluated below) | 117 | 120 |

Audits attempted (3 of 40): `2023-07-pooltogether`, `2025-04-forte`,
`2026-01-tempo-feeamm`.

- `2023-07-pooltogether` → **COMPILED**. 2 findings in registry: `H-02`, `H-04`.
- `2026-01-tempo-feeamm` → **COMPILED**. 1 finding in registry: `H-01`.
- `2025-04-forte` → **COMPILE_FAILED**. Reason recorded in
  `build_manifest.jsonl`: `"Exhausted repair budget (6 attempts) for
  .../2025-04-forte; see .../2025-04-forte/repair.jsonl"`. 5 findings in
  registry for this audit (`H-01`–`H-05`); none evaluated.

**Every observation in sections 2–4 below is drawn from exactly 2 compiled
audits and the 3 findings whose audit compiled.** 37 of 40 registered audits
and 117 of 120 registered findings contributed zero data to this run because
their audit was not compiled (`SKIPPED`, no local checkout) or failed to
compile (`COMPILE_FAILED`). This is the single largest scope constraint on
everything that follows.

---

## 2. Ground-truth-focused gate analysis

`gate_evaluation.jsonl` contains 5 records, covering the 3 findings whose
audit compiled. One finding (`H-02`) produced 3 records because its writeup
cites 3 distinct GitHub locations, each independently resolved to a routing
unit and evaluated.

| # | Finding | Expected family | Gate | Routing unit | Route fired? | Predicate statuses (evidence) | Unresolved/missing |
|---|---|---|---|---|---|---|---|
| 1 | `2023-07-pooltogether/H-02` | P5_ARITHMETIC_PRECISION | P5_NARROWING_CAST | `fn::Vault._burn(address,uint256)` | **true** | `unsafe_cast_count_gt_zero`: SATISFIED — evidence: `"fn::Vault._burn(address,uint256): unsafe_cast_count=1"` | none |
| 2 | `2023-07-pooltogether/H-02` | P5_ARITHMETIC_PRECISION | P5_NARROWING_CAST | `fn::Vault.deposit(uint256,address)` | false | `unsafe_cast_count_gt_zero`: MISSING — evidence: `"fn::Vault.deposit(uint256,address): unsafe_cast_count=0"` | `unsafe_cast_count_gt_zero` |
| 3 | `2023-07-pooltogether/H-02` | P5_ARITHMETIC_PRECISION | P5_NARROWING_CAST | `fn::Vault.withdraw(uint256,address,address)` | false | `unsafe_cast_count_gt_zero`: MISSING — evidence: `"fn::Vault.withdraw(uint256,address,address): unsafe_cast_count=0"` | `unsafe_cast_count_gt_zero` |
| 4 | `2023-07-pooltogether/H-04` | P1_AUTHORIZATION | P1_STATE_CHANGE_NO_AUTH_DOMINATOR | `fn::Vault.mintYieldFee(uint256,address)` | **true** | `visibility_is_public_or_external`: SATISFIED (`visibility='external'`); `state_write_exists`: SATISFIED (`-> var::Vault._yieldFeeTotalSupply`); `not_constructor`: SATISFIED (`name='mintYieldFee'`); `authorization_control_state`: SATISFIED (`resolved_state=ABSENT`) | none |
| 5 | `2026-01-tempo-feeamm/H-01` | P2_REENTRANCY | — (none evaluated) | — (none resolved) | null | — | reason: `"UNRESOLVED: no GitHub line citation found in the finding's own writeup to resolve a routing unit from"` |

### Cited-location coverage, per finding

Coverage here means: of the GitHub line citations present in the finding's
own writeup, how many resolved to a compiled-graph routing unit (regardless
of whether the gate then fired at that unit).

| Finding | Citations in writeup | Citations resolved to a routing unit | Coverage |
|---|---|---|---|
| `2023-07-pooltogether/H-02` | 3 | 3 (`Vault._burn`, `Vault.deposit`, `Vault.withdraw`) | **FULL** (3/3) |
| `2023-07-pooltogether/H-04` | 1 | 1 (`Vault.mintYieldFee`) | **FULL** (1/1) |
| `2026-01-tempo-feeamm/H-01` | 0 | 0 | **ABSENT** — the finding's `findings/H-01.md` (182 lines) contains no GitHub `blob/.../#L` link at all; this is a property of the source document, not a resolution failure |

No finding in this run had PARTIAL coverage (some citations resolved, others
not) — the only two outcomes observed were FULL (both pooltogether findings)
and ABSENT (the one tempo-feeamm finding). This is a fact about these 3
findings specifically, not a general claim about citation coverage.

### Aggregate gate/predicate status counts (from `feasibility_report.json`)

| Family | Findings considered | Route fired | Route not fired | Routing unit unresolved | Predicate status counts |
|---|---|---|---|---|---|
| P1_AUTHORIZATION | 1 | 1 | 0 | 0 | `authorization_control_state:SATISFIED`=1, `not_constructor:SATISFIED`=1, `state_write_exists:SATISFIED`=1, `visibility_is_public_or_external:SATISFIED`=1 |
| P2_REENTRANCY | 1 | 0 | 1 | 1 | (none — no predicate was evaluated because no routing unit resolved) |
| P5_ARITHMETIC_PRECISION | 1 | 1 | 0 | 0 | `unsafe_cast_count_gt_zero:SATISFIED`=1, `unsafe_cast_count_gt_zero:MISSING`=2 |

"Findings considered" = 1 per family here because exactly one of the 3
reached findings was labeled into each of P1/P2/P5 by the keyword heuristic
(`assign_expected_family`); 0 findings were labeled `NOT_APPLICABLE` in this
run (`findings_not_applicable_to_p1_p2_p5: 0`).

---

## 3. Whole-graph routing behavior

Source: `route_manifest.jsonl`, which records every **fired** route across
the entire compiled graph of each `COMPILED` audit — not only routes tied to
a known finding. This section describes routing behavior independent of
ground truth.

| Metric | Value | Denominator |
|---|---|---|
| Total route records | 62 | 2 compiled audits |
| Unique (audit, routing_unit) pairs | 52 | 62 route records |
| Routing units firing more than one family (multi-label) | 7 | 52 unique units |

### Routes by family

| Family | Route records | Share of 62 |
|---|---|---|
| P5_ARITHMETIC_PRECISION | 42 | 67.7% |
| P1_AUTHORIZATION | 13 | 21.0% |
| P2_REENTRANCY | 7 | 11.3% |

### Routes by audit and family

| Audit | P1 | P2 | P5 | Total |
|---|---|---|---|---|
| `2023-07-pooltogether` | 9 | 4 | 38 | 51 |
| `2026-01-tempo-feeamm` | 4 | 3 | 4 | 11 |

### Multi-label overlap (7 of 52 unique units fire more than one family)

| Audit | Routing unit | Families fired |
|---|---|---|
| pooltogether | `LiquidationPair.swapExactAmountIn(...)` | P1_AUTHORIZATION, P2_REENTRANCY |
| pooltogether | `LiquidationPair.swapExactAmountOut(...)` | P1_AUTHORIZATION, P2_REENTRANCY |
| pooltogether | `PrizePool.claimPrize(...)` | P1_AUTHORIZATION, P5_ARITHMETIC_PRECISION |
| tempo-feeamm | `FeeAMM.burn(...)` | P1_AUTHORIZATION, P2_REENTRANCY, P5_ARITHMETIC_PRECISION |
| tempo-feeamm | `FeeAMM.executeFeeSwap(...)` | P1_AUTHORIZATION, P2_REENTRANCY, P5_ARITHMETIC_PRECISION |
| tempo-feeamm | `FeeAMM.mint(...)` | P1_AUTHORIZATION, P2_REENTRANCY, P5_ARITHMETIC_PRECISION |
| tempo-feeamm | `FeeAMM.rebalanceSwap(...)` | P1_AUTHORIZATION, P5_ARITHMETIC_PRECISION |

### Routes per 100 functions

| Audit | Function nodes in graph | Fired routes | Routes per 100 functions |
|---|---|---|---|
| `2023-07-pooltogether` | 833 | 51 | 6.12 |
| `2026-01-tempo-feeamm` | 16 | 11 | 68.75 |

These two ratios differ by more than a factor of 11. pooltogether is a
large, multi-contract protocol (37 contracts) where most functions are in
library/utility code; tempo-feeamm is a 2-contract, 16-function codebase
where a larger proportion of functions are state-changing entry points. This
document does not interpret which ratio, if either, is more representative.

### Routes without a corresponding ground-truth finding in this registry

**Do not read the numbers in this subsection as false positives.** A route
firing at a location with no matching entry in `task_info.csv` means only
that this registry's ground-truth list does not cite that location — it says
nothing about whether the underlying code is actually vulnerable, since that
determination is explicitly out of scope for this study (no Commentator, no
grader, no human review was run against these locations).

Of 62 route records, 2 correspond to a routing unit also cited by a
ground-truth finding (`Vault._burn` / H-02, `Vault.mintYieldFee` / H-04); the
other 60 do not. Grouped by the contract the routing unit belongs to
(descriptive grouping only):

| Audit | Contract | Unmatched route count |
|---|---|---|
| pooltogether | `PrizePool` | 12 |
| tempo-feeamm | `FeeAMM` | 11 |
| pooltogether | `TieredLiquidityDistributor` | 7 |
| pooltogether | `TwabLib` | 6 |
| pooltogether | `LiquidatorLib` | 5 |
| pooltogether | `DrawAccumulatorLib` | 4 |
| pooltogether | `LiquidationPair` | 4 |
| pooltogether | `Vault` | 4 |
| pooltogether | `ECDSA` | 1 |
| pooltogether | `ERC4626` | 1 |
| pooltogether | `ObservationLib` | 1 |
| pooltogether | `OverflowSafeComparatorLib` | 1 |
| pooltogether | `TierCalculationLib` | 1 |
| pooltogether | `TwabController` | 1 |
| pooltogether | `VaultFactory` | 1 |

A secondary, name-pattern-only grouping (contract name matches a common
library/utility naming convention such as `*Lib`, `ECDSA`, `ERC20`,
`Ownable`, etc. — a naming heuristic, not a semantic determination of
"vendored" vs. "protocol-specific" code): 19 of the 60 unmatched routes are
on contracts named `DrawAccumulatorLib`, `ECDSA`, `LiquidatorLib`,
`ObservationLib`, `OverflowSafeComparatorLib`, `TierCalculationLib`, or
`TwabLib`; the remaining 41 are on contracts named `ERC4626`, `FeeAMM`,
`LiquidationPair`, `PrizePool`, `TieredLiquidityDistributor`,
`TwabController`, `Vault`, or `VaultFactory`.

---

## 4. Context behavior

Source: `context_manifest.jsonl`, 62 records (one per fired route in
`route_manifest.jsonl`).

### Included/excluded/unresolved entity counts

| | n | min | max | mean | median |
|---|---|---|---|---|---|
| Included entities per route | 62 | 1 | 108 | 5.31 | 2.0 |
| Excluded entities per route | 62 | 0 | 1 | 0.68 | 1.0 |
| Unresolved entities per route | 62 | 0 | 1 | 0.11 | 0.0 |

Total included entities summed across all 62 context records: 329.

### Context size by family (included-entity count per route)

| Family | n (routes) | min | max | mean | median |
|---|---|---|---|---|---|
| P5_ARITHMETIC_PRECISION | 42 | 2 | 5 | 2.57 | 2.0 |
| P1_AUTHORIZATION | 13 | 1 | 3 | 1.31 | 1.0 |
| P2_REENTRANCY | 7 | 11 | 108 | 29.14 | 13.0 |

P2's included-entity range (11–108) is far wider than P1's (1–3) or P5's
(2–5). This follows directly from each family's `context_policy` (plan
section 3): P5 stops at `single_function_scope`; P1 includes only the seed
plus applied/base-contract modifiers; P2 performs a fixed-point traversal
over shared state, which can pull in a variable number of functions
depending on how many other functions touch the same state variables in a
given contract.

### Stopping-rule / exclusion reasons

| Family | Excluded-note text | Occurrences |
|---|---|---|
| P5_ARITHMETIC_PRECISION | `(single_function_scope: no neighbor functions/contracts included)` | 42 |
| P1_AUTHORIZATION | (none recorded) | 0 |
| P2_REENTRANCY | (none recorded) | 0 |

| Family | Unresolved-note text | Occurrences |
|---|---|---|
| P2_REENTRANCY | `callback_reachable_entrypoints: deferred, requires callback_potential extraction not built in this slice` | 7 (all 7 P2 routes) |
| P1_AUTHORIZATION | (none recorded) | 0 |
| P5_ARITHMETIC_PRECISION | (none recorded) | 0 |

Every one of the 7 P2_REENTRANCY context records carries the same deferred
note: this is the same, single, already-documented gap (callback-potential
extraction is not built in this slice) appearing once per fired P2 route,
not 7 independent gaps.

### Ground-truth location coverage in constructed context

Of the 62 context records, 2 have a matching ground-truth finding
(`matching_finding_ids` non-empty); for the other 60, the ground-truth
comparison fields are `null` (not computed — no finding cites that routing
unit, so there is nothing to compare against).

| Routing unit | Family | Matching finding | Ground-truth locations cited | In included set? | In excluded/unresolved set? |
|---|---|---|---|---|---|
| `fn::Vault._burn(address,uint256)` | P5_ARITHMETIC_PRECISION | H-02 | 3 (`#L1138-L1139`, `#L407-L415`, `#L509-L521`) | **true** | **true** |
| `fn::Vault.mintYieldFee(uint256,address)` | P1_AUTHORIZATION | H-04 | 1 (`#L394-L402`) | **true** | false |

For `Vault._burn` (H-02), both flags are `true` simultaneously: the
`#L1138-L1139` citation (the `_burn` function itself) falls inside the
constructed context's included set, while the other two citations
(`#L407-L415`, `#L509-L521`, which fall inside `Vault.withdraw` and
`Vault.deposit` respectively) fall outside it — a direct, mechanical
consequence of P5's `single_function_scope` stopping rule recorded above,
not a separate anomaly.

### Estimated Commentator call count and context exposure

MGPR's design invokes the Commentator once per fired route (plan section 2).
Under that design, for these 2 compiled audits:

| Audit | Function nodes in graph (= calls under the prior full-scan design) | Fired routes (= calls under MGPR) |
|---|---|---|
| `2023-07-pooltogether` | 833 | 51 |
| `2026-01-tempo-feeamm` | 16 | 11 |
| **Combined** | **849** | **62** |

"Context exposure" (how much source/graph content a Commentator call would
see) is the included-entity count reported above: median 2 entities for
P5-routed calls, 1 for P1-routed calls, 13 for P2-routed calls, with a
combined mean of 5.31 entities per call across all 62 calls and 329 entities
total. This document does not characterize whether 62 calls or 329 total
included entities constitute a small, large, adequate, or inadequate volume.

---

## 5. Engineering evidence

### Tests

121 MGPR-specific unit tests across 10 test files
(`test_mgpr_spec.py`, `test_mgpr_predicates.py`, `test_mgpr_resolution.py`,
`test_mgpr_router.py`, `test_mgpr_context.py`, `test_mgpr_fpsl_wiring.py`,
`test_mgpr_seeds_wiring.py`, `test_mgpr_build_registry.py`,
`test_mgpr_build_manifests.py`, `test_mgpr_run_feasibility_study.py`), all
passing at time of writing. A broader run additionally including 7
pre-existing, unmodified core test files (`test_graph.py`, `test_features.py`,
`test_commentator.py`, `test_llm.py`, `test_score.py`, `test_slice.py`,
`test_scope.py`) plus `test_repair.py` produced 132 passed, 1 failed (see
below) out of 133 collected.

### Reproducibility

The full study (`run_feasibility_study.py` against the same 40-audit
registry and the same 3 available checkouts) was run twice independently.
`gate_evaluation.jsonl` and `feasibility_report.json` were byte-for-byte
identical between the two runs (`diff` exit code 0 on both files).

### Known-case cross-checks

Two ground-truth findings from `2023-07-pooltogether` — already documented
in this repository's own prior work (`evmbench/CLAUDE.md`, Run 4) as
independently-confirmed real vulnerabilities — were checked against this
run's output:

- H-02 (uint96 downcast in `Vault._burn`): row 1 of section 2's table above
  — route fired, `unsafe_cast_count_gt_zero` SATISFIED with evidence citing
  `Vault._burn` directly.
- H-04 (missing access control on `Vault.mintYieldFee`): row 4 of section
  2's table above — route fired, all four P1 predicates SATISFIED, including
  `authorization_control_state` resolving to `ABSENT`.

This is 2 of 3 reached findings (the third, tempo-feeamm's H-01, had no
citation to resolve a routing unit from at all, as recorded in section 2).

### Documented pre-existing failure

`tests/unit/test_repair.py::test_repair_fixes_wrong_solc_version` fails with
`a4v.graph.BuildFailed: Exhausted repair budget (2 attempts) for
.../tests/fixtures/wrong_solc/OldStyle.sol` (raised at `a4v/repair.py:178`).
This was run and captured on two checkouts:

- The MGPR worktree (`worktree_run.txt`): same failure, same error message,
  path `.../worktrees/mgpr-router2/tests/fixtures/wrong_solc/OldStyle.sol`.
- The untouched main checkout (`main_checkout_run.txt`), confirmed via
  `git status` to have `a4v/repair.py` and `tests/unit/test_repair.py` at
  their committed state with no local modifications: same failure, same
  error message, path `.../agent4vul/tests/fixtures/wrong_solc/OldStyle.sol`.

Both captured outputs are saved verbatim as separate files, not paraphrased
here.
