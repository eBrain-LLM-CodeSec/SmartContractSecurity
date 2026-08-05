# Level M extraction — full corpus (24/24)

Track A covered 2 M-level requirements. This extends to all 24, and is
the single most direct answer this project has to the plan's core open
research question: *can routing strategies be extracted from EthTrust's
own text?*

## Classification breakdown

| Classification | Count |
|---|---|
| `DETERMINISTIC_TRIGGER_SEMANTIC_CONDITION` | 15 |
| `FULLY_DETERMINISTIC` | 7 |
| `FULL_SEMANTIC_REVIEW` | 2 |
| `UNTRANSLATABLE_*` (any variant) | 0 |

**Zero requirements landed in an untranslatable bucket.** Every M-level
requirement in the corpus yielded either a fully mechanical strategy or a
text-derived deterministic trigger paired with a narrowed semantic
question — never a case where no routing signal could be extracted at
all. This is a genuinely informative research result, not a foregone
conclusion: Track A's own selection process picked
`req-2-overflow-underflow` specifically as a *candidate* for
`FULL_SEMANTIC_REVIEW`/untranslatable, and even that one resolved to
`DETERMINISTIC_TRIGGER_SEMANTIC_CONDITION` on full reading. The two
requirements that DID land at `FULL_SEMANTIC_REVIEW`
(`req-2-enforce-eval-order`, `req-2-signature-verification`) are broad
correctness properties with no nameable syntactic anchor, not requirements
where the extraction attempt merely failed for lack of effort.

## `FULLY_DETERMINISTIC` is mostly the compiler-bug sub-batch

6 of the 7 `FULLY_DETERMINISTIC` requirements are compiler-bug variants
(`req-2-compiler-060`, `SOL-2023-1`, `SOL-2022-7`, `SOL-2022-5-assembly`,
`SOL-2022-4`, `SOL-2021-3`) plus `req-2-pass-l1` (a certification-process
bookkeeping rule, not really an independent analysis strategy). Real
corroboration found in Slither's own `buggy_versions.py` for 3 of the 5
pattern-specific ones: `SOL-2022-7` → `StorageWriteRemovalBefore
ConditionalTermination` (near-verbatim name match at both ends of the
stated range), `SOL-2023-1` → `MissingSideEffectsOnSelectorAccess`
(matched at *both* boundary versions of a wide 0.6.2–0.8.20 range),
`SOL-2021-3` → `SignedImmutables`. `SOL-2022-4` found no corroboration
despite a targeted search — logged honestly, not forced.

## A genuine cross-requirement reuse discovery

Writing `req-2-protect-create2`'s record surfaced something not
anticipated when the S-level and M-level work were done separately: its
sub-clauses ("deployed CREATE2 contract MUST NOT use selfdestruct/
delegatecall/callcode") can reuse the **exact same custom predicates**
already scoped for `req-1-self-destruct` and `req-1-delegatecall` — just
applied to the CREATE2-deployed target's bytecode instead of the calling
contract's own. Similarly, `req-2-self-destruct`'s semantic condition
("only authorised parties can call") is exactly what Slither's own
`suicidal` detector checks via `is_protected()` — the detector explicitly
**rejected** as a match for the S-level mere-presence question in
`req-1-self-destruct`'s own record turns out to be the *right* tool one
level up. Neither of these reuse opportunities were designed in advance;
both fell out of doing the translation work honestly requirement-by-
requirement rather than templating a shape onto each one.

## A real, substantial gap found in Slither's own randomness detector

`req-2-random-enough`'s natural analyzer candidate, Slither's
`weak-prng`, was read in full: it only flags a **modulo operation**
whose operand depends on `block.timestamp`/`now`/`blockhash()`. It does
not check `block.difficulty`/`block.prevrandao` at all — arguably the
most commonly cited weak-randomness source in post-merge Solidity — nor
non-modulo uses of any of these values (e.g. as a `keccak256` seed, or a
direct threshold comparison). Logged as a real, substantial scope gap,
not a technicality.
