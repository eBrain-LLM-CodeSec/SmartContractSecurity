# Level Q evidence rubrics — full corpus (24/24)

Track A covered 1 Q-level requirement. This extends to all 24.

## The most important finding: S/M/Q is not a verification-method axis, again

Four requirements in this batch are **mechanically checkable**, not
inherently in need of semantic review, despite sitting at EthTrust's
highest assurance tier:

- `req-3-linted` — unused variables, name collisions, dead `assert()`s,
  unreachable code: all classic static-lint rules.
- `req-3-event-on-state-change` — every state-mutating function must emit
  an event: a direct trigger/outcome cross-reference, no ambiguity.
- `req-3-annotate` — NatSpec presence on public interfaces: a syntactic
  property Slither's own AST parsing already exposes.
- `req-3-consistent-solidity-output` — pragma version-range narrowness: a
  compiler-metadata question, the same shape as the S-level compiler-bug
  requirements.

This is the third time this exact finding has surfaced independently in
Track B (after `req-1-eip155-chainid` landing closer to semantic review
despite being Level S, and the M-level batch's uniform text-extractability
result) — strong, repeated evidence that EthTrust's S/M/Q labels track
assurance *stacking*, not analysis *difficulty* or *method*. None of these
four were built out to full L4-style analyzer-matching depth in this pass
(flagged, not implemented, to keep this batch's pace consistent with the
rest of Q) — but the finding itself is real and worth acting on in a
future pass.

## A genuine naming-collision risk caught and flagged

`req-3-no-private-data` ("Tested code MUST NOT store Private Data on the
blockchain") almost certainly means genuinely confidential data (PII,
secrets, credentials) — **not** Solidity's `private` visibility keyword,
which restricts compile-time access but provides zero on-chain
confidentiality (all contract storage is publicly readable regardless).
A naive reading risks checking the wrong thing entirely — worth
flagging explicitly rather than letting the naming collision go
unaddressed.

## Where L7's repository-visible-evidence bound actually bites

`req-3-no-single-admin-eoa` is the clearest case in this batch: whether
an admin address is a multisig contract or a plain EOA is fundamentally
a *deployment* fact. Source code can show whether the admin role is
parameterized generically (compatible with either), but generally cannot
itself prove which was deployed — explicitly logged as
`REQUIRES_EXTERNAL_EVIDENCE`, consistent with the Rev. 3 re-scoping of L7
to repository-visible evidence only.

## Two requirements now have their own first-class entries

`req-3-documented` and `req-3-document-system` were previously only
*referenced* (as the two evidence categories Track A's
`req-3-implement-as-documented` rubric checks against) — they now have
their own L7 rubrics as independent requirements in their own right,
closing a real gap in the original single-requirement treatment.
