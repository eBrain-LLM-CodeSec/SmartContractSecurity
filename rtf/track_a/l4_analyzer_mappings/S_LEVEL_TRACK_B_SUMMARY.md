# S-level analyzer matching — full corpus (22/22)

Track A covered 3 S-level requirements (`req-1-compiler-060`,
`req-1-eip155-chainid`, `req-1-compiler-sol-2021-4`). This extends
coverage to all 22, using the same standard: real source inspection of
Slither 0.11.5's actual detector code, not name-based guessing.

## Match classification summary

| Classification | Count | Requirements |
|---|---|---|
| `NO_MATCH` | 4 | `req-1-no-create2`, `req-1-exact-balance-check`, `req-1-self-destruct` (considered `suicidal`, rejected as answering a different question), `req-1-no-ancient-compilers` (existing detector's hardcoded threshold is wrong for this specific requirement) |
| `PARTIAL_MATCH` | 18 | Everything else — every requirement with an override/exception clause structurally caps out below `EXACT_MATCH`, since no detector can resolve the override on its own (see below) |
| `EXACT_MATCH` | 0 | None found in the full S-level corpus |

**Zero `EXACT_MATCH` across all 22 S-level requirements is itself a
significant, honest finding.** Every requirement with a Set/singular
Overriding Requirement clause (the large majority) is structurally
incapable of reaching `EXACT_MATCH` via analyzer reuse alone: a detector
can confirm the *trigger* condition (the prohibited construct is present)
but cannot resolve whether an override applies, so outcome equivalence
never fully holds. This isn't a weakness of Slither specifically — it
reflects how EthTrust's own Level S requirements are structured (a
presence-check plus an escape hatch), and it's consistent with what
`req-1-compiler-060` already showed in Track A.

## Recurring structural pattern, found repeatedly

Across `req-1-no-tx.origin`, `req-1-no-hashing-consecutive-variable-
length-args`, `req-1-delegatecall`, and others, the same shape recurs:
Slither's detector suite checks *dangerous usage* (tainted/attacker-
controlled input, unprotected access) while EthTrust's S-level text
prohibits *mere presence*. This is a real, consistent scope gap, not a
one-off — Slither's detectors and EthTrust's Level S requirements are
answering genuinely different questions by design (Slither: "is this
exploitable right now"; EthTrust Level S: "does this construct appear at
all, deferring the safety question to the M/Q override").

## Notably strong corroboration in the compiler-bug sub-batch

Beyond `req-1-compiler-sol-2021-4`'s `UserDefinedValueTypesBug` match
(Track A), 6 of the 8 remaining `PATTERN_AND_VERSION` compiler-bug
requirements found a real, named entry in Slither's own
`buggy_versions.py` at the exact version boundary EthTrust states —
strongest: `req-1-compiler-SOL-2022-1`'s
`AbiEncodeCallLiteralAsFixedBytesBug`, an almost-verbatim name match.
`req-1-compiler-SOL-2022-5-push` found **no** corroborating entry despite
an explicit targeted search — logged honestly as a real gap, not glossed
over. `req-1-compiler-SOL-2021-1`'s `KeccakCaching` match was missed on
a first pass and found only on a second, more targeted search — a small
reminder that "no obvious name match" isn't the same as "confirmed
absent" until actually searched for.

## The simplest requirement found in the whole S-level corpus

`req-1-no-ancient-compilers`: unconditioned subject, no override clause,
single numeric version threshold. The entire strategy is a one-line
comparison (`compilation_unit.solc_version < '0.3.0'`) — no pattern
component, no override-resolution component. Worth noting precisely
because it's the exception: almost every other S-level requirement needed
at least two components (trigger + override-or-pattern resolution).
