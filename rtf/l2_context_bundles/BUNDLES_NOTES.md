# L2 context bundles — full corpus (Track B kickoff)

Track A validated the adaptive-expansion context-bundle mechanism against
6 hand-selected requirements (see `rtf/track_a/`). The mechanism is
purely data-driven off the L1 corpus (no per-requirement code, no manual
tuning), so once Track A's go/no-go passed, it was re-run unchanged
against all 81 requirements as the first piece of Track B.

**Result: 81/81 succeeded, zero cap hits.** Depth distribution: 53 at
depth 1, 26 at depth 2, 2 at depth 0 (`req-R-notify-news`,
`req-R-multisig-threshold` — both simple, self-contained Recommended-
Good-Practice one-liners with no cross-references to expand into).

This directory was relocated from `rtf/track_a/context_bundles/` (its
original, Track-A-scoped name) now that it holds the full corpus — the
old name would have misled anyone reading it later into thinking it was
still just the 6-requirement tranche.

## What this does and doesn't establish

Zero cap hits across all 81 is a genuinely good sign — it means the
adaptive-expansion design (1-hop start, expand only on unresolved
reference, cap at 3) never had to fall back to its "bundle insufficiency"
escape hatch anywhere in the corpus, at least for the depth of
cross-reference EthTrust's own text exhibits. It does **not** mean every
bundle is *sufficient* for translation — L2 only assembles *directly
cited* context; whether that's enough to correctly derive applicability
and strategy (L3+) still requires the same careful, per-requirement
reading Track A did (see AR-001: L1's mechanical flags can miss
predicate-embedded restrictions, and no volume of successful L2 runs
changes that — L3 still needs a human/LLM re-read of every requirement's
full text, not just its structured fields).

## What's NOT done yet for Track B

L3 (applicability), L4 (analyzer matching), L5/L6/L7 (strategy
derivation), and L8 execution for the other 75 requirements are
unstarted. These require the same per-requirement judgment and
verification Track A's 6 requirements got — not something to run as a
single mechanical batch job. Scoping and pacing that work is a decision
for whoever picks Track B back up, not something to commit to
unilaterally in this pass.
