# RTF investigation-grouping taxonomy (Phase 3)

16 semantic reasoning categories, derived by reading every one of the 81
static EthTrust corpus requirements' own title and normative text
(`rtf/l1_corpus/requirement_corpus.json`) — **not** from any EVMbench
vulnerability family, finding, or label. Two requirements land in the
same category because EthTrust's own text points investigations at the
same kind of code (the same call sites, the same state, the same
reasoning shape), not because they happen to correlate with any
benchmark outcome. Mechanical mapping and full 81/81 coverage tests live
in `rtf/l11_investigation_grouping/taxonomy.py`.

These categories exist for exactly one purpose: to tell the Phase 4
grouping engine which properties can plausibly share one Codex
investigation's context (same reasoning shape, same code neighborhood)
versus which must never be grouped together (incompatible reasoning
shapes, even if they happen to touch the same file). The category names
are not vulnerability classes — several categories contain requirements
whose actual failure modes are entirely unrelated to each other; what
they share is the *kind of code and reasoning* the investigation needs.

## Categories

### 1. `COMPILER_TOOLCHAIN_SAFETY` (19 requirements)
Pinned compiler version + known-compiler-bug-window checks (every
`req-*-compiler-*`, `req-1-no-ancient-compilers`,
`req-3-consistent-solidity-output`, `req-R-use-latest-compiler`).
**Shared context**: `pragma solidity` version string alone — no
function/contract-specific code reasoning at all. **Why joint
investigation may help**: almost none of these ever reach Codex in the
first place (18 of 19 are `DETERMINISTIC_COMPLETE`, resolved directly
from the pinned version string, per `registry.py`). Included for
completeness/explainability, not because grouping matters here.
**Unsafe combinations**: with EVERY other category — a compiler-version
check has zero code-neighborhood overlap with anything else; grouping it
with a real code-reasoning property would waste that property's context
budget on an unrelated, already-resolved question.

### 2. `LOW_LEVEL_CONSTRUCT_SAFETY` (8 requirements)
`req-1-no-assembly`, `req-2-safe-assembly`, `req-1-delegatecall`,
`req-1-self-destruct`, `req-2-self-destruct`, `req-1-no-create2`,
`req-2-protect-create2`, `req-2-documented` (documents the same
constructs this category's other members check). **Shared context**:
presence and protection status of specific dangerous opcodes/patterns
(`assembly{}`, `delegatecall()`, `selfdestruct()`, `CREATE2`) at a
specific call site. **Why joint investigation may help**: a contract
using `CREATE2` for a factory pattern often has both the raw-usage
requirement (`req-1-no-create2`) and the protection requirement
(`req-2-protect-create2`) genuinely asking about the SAME lines — one
investigation reading that code once can honestly answer both.
**Unsafe combinations**: none listed beyond the two universal ones
(`AGGREGATION_META`, `COMPILER_TOOLCHAIN_SAFETY`) — this category is
internally cohesive.

### 3. `EXTERNAL_CALL_INTERACTION` (6 requirements)
`req-1-use-c-e-i`, `req-1-check-return`, `req-2-handle-return`,
`req-2-external-calls`, `req-3-external-calls`,
`req-2-avoid-readonly-reentrancy`. **Shared context**: the external-call
site itself — ordering relative to state writes (checks-effects-
interactions), return-value handling, reentrancy guards.
**Why grouping helps**: these are literally different facets of the
SAME question ("is this external call safe") asked by different
Security Levels (S/M/Q) — a single investigation reading one external
call site can honestly answer all of them together, avoiding 3+ separate
re-reads of the same 10 lines.

### 4. `ACCESS_PRIVILEGE_CONTROL` (6 requirements)
`req-3-access-control`, `req-3-no-single-admin-eoa`,
`req-3-revocable-permisions`, `req-3-protect-governance`,
`req-3-timelock-for-privileged-actions`, `req-R-multisig-threshold`.
**Shared context**: role/permission definitions, admin-gated function
signatures, governance execution paths. **Cross-cutting note**:
`req-3-timelock-for-privileged-actions` also touches time semantics
(category 9) — assigned here as primary because its own text's subject
is "sensitive operations" (privilege-gated actions), with the TimeLock
mechanism as the required MITIGATION, not the core reasoning target.
Flagged explicitly as a genuine cross-cutting case the grouping engine
should be able to query both ways, not force into one silo.

### 5. `SIGNATURE_AUTH_REPLAY` (6 requirements)
`req-2-signature-verification`, `req-2-malleable-signatures-for-replay`,
`req-3-intended-replay`, `req-1-eip155-chainid`, `req-1-no-tx.origin`,
`req-3-verify-tx.origin`. **Shared context**: signature-verification
call sites (`ecrecover`), replay-protection fields (nonce, chainid,
domain separator), and `tx.origin`-vs-`msg.sender` authentication
anti-patterns — all fundamentally "how does this contract establish who
is calling/authorizing this action." **Why grouping helps**: a single
signature-verification function commonly needs to satisfy 3-4 of these
requirements simultaneously (verify the sig, reject malleable variants,
bind chainid, reject replay) — one investigation reading that function
can honestly answer all of them.

### 6. `ARITHMETIC_VALUE_CORRECTNESS` (5 requirements)
`req-2-overflow-underflow`, `req-2-check-rounding`,
`req-1-exact-balance-check`, `req-2-verify-exact-balance-check`,
`req-2-enforce-eval-order`. **Shared context**: numeric computations
that determine token/value amounts — overflow bounds, rounding
direction, actual-vs-expected balance deltas, operation-order
sensitivity. **This is also where generated GP/ERC clauses land** (e.g.
ERC-4626's rounding-direction and fee-inclusion clauses,
`categorize_generated_clause`'s keyword set) — the same category
definition applied to a different requirement source, not a separate
scheme.

### 7. `INPUT_DOMAIN_VALIDATION` (1 requirement, `req-3-all-valid-inputs`)
Deliberately its own category despite being a single corpus entry: this
is the single broadest, most consequential Level-Q requirement
identified in the earlier translation-fidelity audit
(`RTF_ETHTRUST_TRANSLATION_AUDIT.md`), and — per that audit's own
findings — the requirement whose current narrow instantiation is most
responsible for missed input-boundary bugs (forte H-02, H-03 in the
reclassified root-cause report). Kept separate from
`ARITHMETIC_VALUE_CORRECTNESS` because its reasoning target is different:
"does this function behave correctly for ANY input, including malformed
ones," not "is this specific computation numerically correct."

### 8. `SOURCE_TEXT_INTEGRITY` (4 requirements)
`req-1-unicode-bdo`, `req-2-unicode-bdo`, `req-2-no-homoglyph-attack`,
`req-1-no-hashing-consecutive-variable-length-args`. **Shared context**:
these are about the SOURCE TEXT itself being deceptive or ambiguous
(Unicode bidi override characters, homoglyph identifiers, hash-collision-
prone argument encoding) — a fundamentally different, purely mechanical/
lexical reasoning shape from every other category (no state, no
call-graph, no business logic — just scanning source bytes). Two of the
four (`req-1-unicode-bdo`, and by extension its close relatives) are
already `DETERMINISTIC_COMPLETE`.

### 9. `FUNCTIONAL_CORRECTNESS_DOCUMENTATION` (6 requirements)
`req-3-documented`, `req-3-implement-as-documented`,
`req-3-document-system`, `req-3-document-threats`, `req-3-annotate`,
`req-3-linted`. **Shared context**: cross-referencing documented claims
(README, NatSpec, docs/) against actual code behavior. **Why grouping
helps**: all six read the SAME documentation artifacts as their primary
evidence source — one investigation gathering and reading a contract's
full documentation surface can honestly answer several of these at once.
**Unsafe combination**: with `ARITHMETIC_VALUE_CORRECTNESS` — the former
is a doc-vs-code cross-reference task, the latter is a numeric-reasoning
task; forcing them into one investigation risks the agent treating a
documented rounding claim as sufficient evidence for actual numeric
correctness, exactly the kind of conflation Phase 5's counterexample-
search requirement exists to prevent.

### 10. `TIME_BLOCK_MEV_ORDERING` (4 requirements)
`req-2-block-data-misuse`, `req-2-random-enough`, `req-3-block-mev`,
`req-3-block-front-running`. **Shared context**: `block.number`/
`block.timestamp`/`block.prevrandao` read sites and transaction-ordering
assumptions. `req-2-random-enough` and `req-2-block-data-misuse` already
share the identical predicate (`find_block_data_usage`) per
`registry.py` — a real, pre-existing structural signal this category
formalizes rather than invents.

### 11. `GAS_DOS_STATE_GROWTH` (2 requirements)
`req-3-enough-gas`, `req-3-protect-gas`. **Shared context**: loops over
potentially-unbounded state, gas-cost growth patterns. **Unsafe
combination**: with `SIGNATURE_AUTH_REPLAY` — a gas/DoS investigation
needs to reason about worst-case iteration counts across many calls,
while a signature investigation needs to reason about single-call
cryptographic correctness; conflating them risks shallow treatment of
both (an agent that split attention between "will this loop run out of
gas across 10,000 calls" and "is this one signature correctly verified"
is reasoning at two different timescales in the same breath).

### 12. `ORACLE_EXTERNAL_DEPENDENCY` (1 requirement, `req-3-check-oracles`)
Standalone — oracle-failure/staleness/manipulation reasoning has no
close relative in this corpus.

### 13. `STATE_CHANGE_OBSERVABILITY` (1 requirement,
`req-3-event-on-state-change`)
Standalone — a structural code-pattern check ("does every state-mutating
function emit a corresponding event"), mechanically distinct from
security-logic reasoning.

### 14. `PRIVACY_DATA_EXPOSURE` (1 requirement, `req-3-no-private-data`)
Standalone.

### 15. `PROCESS_GOVERNANCE_PRACTICE` (8 requirements)
`req-R-check-new-bugs`, `req-R-clean-code`, `req-R-define-license`,
`req-R-follow-erc-standards`, `req-R-formal-verification`,
`req-R-fuzzing-in-testing`, `req-R-mutation-testing`,
`req-R-notify-news`. **Shared context**: organizational/process-level GP
practices — license files, disclosure processes, testing methodology,
code-style conventions. Mostly `DETERMINISTIC_COMPLETE` or resolved from
generic documentary evidence (`collect_documentary_and_implementation_
evidence`); low priority for grouping since they rarely produce rich,
code-context-heavy Codex investigations in the first place.

### 16. `AGGREGATION_META` (3 requirements)
`req-2-pass-l1`, `req-3-pass-l2`, `req-R-meet-all-possible`. **Not a
reasoning category at all** — these are pure logical AND-aggregations
over every OTHER requirement's own final verdict
(`registry.AGGREGATION_REQ_IDS`, resolved by `pipeline_e2e.compute_
aggregation_requirements`), never independently investigated by Codex.
**Unsafe with everything**: they cannot be grouped because they are
never scheduled for investigation in the first place — included in the
mapping purely so `categorize_requirement` is total over the 81-corpus,
not because the grouping engine will ever see one.

## What this taxonomy is not

It is not a vulnerability taxonomy, and it was not checked against, or
tuned to match, EVMbench's own H-0X finding categories at any point
during its construction — every category above was assigned by reading
the requirement's own title and normative text in isolation, before any
EVMbench artifact was reopened for this phase. The Phase 15 rerun is
where this taxonomy gets tested against real detection outcomes, not
here.
