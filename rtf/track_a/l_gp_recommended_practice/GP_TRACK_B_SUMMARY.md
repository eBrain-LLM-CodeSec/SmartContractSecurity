# Recommended Good Practice — full corpus (11/11)

The last of the 81 requirements. GP is EthTrust's non-normative
section — 10 of 11 use `SHOULD`, one (`req-R-check-new-bugs`) has no
RFC2119 modality at all (the genuine spec-content gap documented in
`rtf/l1_corpus/PARSING_NOTES.md`).

## A real open question this batch surfaces (AR-006)

The framework's PASS/FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE schema was
designed around binding `MUST` requirements. Whether a "FAIL" on an
advisory `SHOULD` recommendation deserves the same formal weight, the
same downstream metrics treatment, or a distinguishable state entirely,
was not decided in this pass — logged as AR-006 rather than silently
reusing MUST-level vocabulary as if the question didn't exist.

## Two genuinely simple strategies

`req-R-define-license` (SPDX identifier / LICENSE file presence) and
`req-R-use-latest-compiler`'s trigger (compiled version, though its
comparison target is an external, time-anchored "latest" reference) are
about as mechanical as anything in the corpus — on par with
`req-1-no-ancient-compilers`'s one-line strategy from the S-level batch.

## The clearest process-only, code-independent requirements in the whole corpus

`req-R-notify-news` (responsible disclosure to the Working Group) and, to
a lesser extent, `req-R-check-new-bugs` (checking for post-cutoff bug
announcements) are about what a *team does*, not what the *code contains*
— `REQUIRES_EXTERNAL_EVIDENCE` in the strongest sense found anywhere in
Track B: no repository snapshot, however complete, can establish these
either way.

## Corpus complete

With this batch, all 81 EthTrust requirements — every S, M, Q, and GP
requirement in the current spec — have an L3 applicability record. L4
(S-level analyzer matching), L6 (M-level extraction), and L7 (Q-level
evidence rubrics) are similarly complete for their respective levels.
What remains for full Track B closure: implementing the many components
currently marked "sound derivation, not yet implemented" across all
levels, executing L8 live against real targets at scale, and building
the correspondence/evaluation layers (L11/L12) for the full corpus
(Track A's 6-requirement L11 work does not automatically extend to all
81 without its own correspondence-mapping effort).
