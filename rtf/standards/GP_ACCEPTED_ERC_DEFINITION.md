# What counts as an "accepted ERC" — decision record

Per the implementation plan's instruction ("Verify from the actual EthTrust
specification what qualifies as an 'accepted' ERC and implement that
interpretation explicitly. Do not invent the definition. Document the
decision."), this file records how that question was actually answered.

## The requirement's own text

`rtf/l1_corpus/requirement_corpus.json`, `req_id=req-R-follow-erc-standards`:

> The Tested Code SHOULD conform to **finalized** [ERC] standards when it is
> reasonably capable of doing so for its use-case.

The operative word is "finalized" — not "popular", "widely-used", or
"OpenZeppelin-implemented". EthTrust does not define "finalized" inline in
this requirement's own text.

## Tracing the citation

The `[ERC]` token is a bibliographic link. In the pinned, verbatim EthTrust
spec source (`rtf/standards/ethtrust/ethtrust-sl.raw.html`), the bibliography
entry it resolves to is:

```
[ERC] ERC Final - Ethereum Improvement Proposals. Ethereum Foundation.
URL: https://eips.ethereum.org/erc
```

That is EthTrust's own citation for what "ERC" (and therefore "finalized
ERC") means — the canonical EIP process's **`Final`** status, as tracked at
`eips.ethereum.org/erc` (the index of ERC-category EIPs, which itself is
organized by status). This was found by grep-searching the raw spec source
for the citation anchor, not inferred or assumed.

## The EIP-1 status lifecycle

EIP-1 (the process document all EIPs/ERCs follow) defines the status
lifecycle: `Idea → Draft → Review → Last Call → Final | Stagnant | Withdrawn`,
plus `Living` for a small number of continuously-amended process documents
(EIP-1 itself is the canonical example — not applicable to application-level
ERCs like token/vault standards). `Final` is the terminal, completed status
for a standard that the community has settled on.

## The interpretation implemented here

**A standard registered in `rtf/standards/` is only treated as an "accepted"
ERC per `req-R-follow-erc-standards` if its pinned snapshot's own frontmatter
status is `Final`** (or, in principle, `Living` — included for completeness
per the EIP-1 lifecycle, though no registered standard currently uses it).
Anything else (`Draft`, `Review`, `Last Call`, `Stagnant`, `Withdrawn`, or a
missing/unrecognized status) is rejected at registry load time — see
`rtf/standards/registry.py`'s `ACCEPTED_STATUSES` — rather than silently
accepted or silently skipped. This directly satisfies the unit-test
requirement that "unsupported normative strength fails explicitly": here,
an unaccepted standard status fails explicitly the same way.

ERC-4626's pinned snapshot (`rtf/standards/erc/ERC-4626/erc-4626.raw.md`)
states `status: Final` in its frontmatter, confirmed by direct fetch on
2026-08-09 — it qualifies.
