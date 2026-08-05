# L4 Analyzer Matching — progress notes (Track A, S-level requirements)

## Status

Completed for the 3 S-level requirements in the Track A tranche:

| req_id | Slither result | Overall status |
|---|---|---|
| `req-1-compiler-060` | `PARTIAL_MATCH` (`solc-version` detector's hardcoded-version check) | Evidence collector; override condition unresolvable (see below) |
| `req-1-compiler-sol-2021-4` | `PARTIAL_MATCH` (same detector, different code path) | Candidate generator only; doesn't check the triggering pattern |
| `req-1-eip155-chainid` | `NO_MATCH` (confirmed via full 104-detector review) | `UNKNOWN` overall — Mythril/Semgrep not installed, not evaluated |

Full derivation traces with source-inspection notes, pinned versions, and
semantic-boundary-test TODOs are in the per-requirement JSON files in this
directory.

## A discovery worth logging for Track B: the official EEA tool registry

While building the L2 context bundle for `req-1-eip155-chainid`, its
section's own introductory text (Security Level [S] intro) pointed to an
official EEA-maintained **EthTrust Tool Implementation Registry**
(`github.com/EntEthAlliance/ethtrust-tool-registry`, cited in the spec as
`[ET-tools]`). It lists three community-submitted tools with self-reported
per-requirement coverage claims:

- **Slither** (registry claims v0.10.4; this repo has v0.11.5 installed —
  version drift is itself worth noting for reproducibility) — claims Level
  S coverage of: No selfdestruct(), Use CEI, No Hashing Consecutive
  Variable-Length Args, Check External Calls Return, No delegatecall(),
  No tx.origin, Explicit Storage, Explicit Constructors.
- **Olympix** — broader claimed Level S *and* Level M coverage (reentrancy,
  randomness, integer casting, etc.)
- **EY Smart Contract Review Tool** — tx.origin, assembly, unsafe external
  calls, overflow/underflow, conflicting inheritance, external-call checks.

**None of these three tools' claimed lists include anything for our three
selected S requirements** (`req-1-eip155-chainid`, and the two compiler-bug
requirements aren't title-matched either) — consistent with, though not
proof of, the `NO_MATCH`/gap findings above.

**Important, and consistent with this framework's own design (decision
#1):** these are self-reported title-level claims with no derivation
trace, no source inspection, and no version-pinning rigor of their own —
they must NOT be accepted as `EXACT_MATCH` (or any match at all) without
this framework's own independent trigger/scope/outcome verification. Their
value here is as a **candidate-generation input** (a place to look first)
for Track B's full 81-requirement analyzer-matching pass — e.g. their
listed items (tx.origin, delegatecall, selfdestruct, CEI, exact-balance-
check) map directly onto `req-1-no-tx.origin`, `req-1-delegatecall`,
`req-1-self-destruct`, `req-1-use-c-e-i`, `req-1-exact-balance-check` in
our L1 corpus, none of which happen to be in this Track A tranche's six.
Logged here for reuse when Track B scales up, not acted on now.

## Outstanding for this tranche

- `req-2-verify-exact-balance-check` (M), `req-2-overflow-underflow` (M),
  `req-3-implement-as-documented` (Q) — L4 analyzer matching not yet done.
  Note that per the plan's architecture, L4 (analyzer matching) is
  primarily an S-level mechanism; the two M requirements' strategy work
  belongs mainly to L6 (Level M extraction: is a deterministic trigger
  derivable, or is this full semantic review?), and the Q requirement's
  work belongs to L7 (protocol conformance evidence assessment) — L4 may
  still apply as a component within a DETERMINISTIC_TRIGGER_SEMANTIC_
  CONDITION strategy if a concrete trigger exists, to be assessed in that
  pass rather than here.
- Mythril and Semgrep: neither is installed in this environment. Actually
  evaluating them (rather than leaving requirements at `UNKNOWN`) requires
  installing them first — real infrastructure work, distinct from and
  additional to the translation-methodology question itself, exactly as
  flagged when this broadened analyzer-evaluation scope was decided.
