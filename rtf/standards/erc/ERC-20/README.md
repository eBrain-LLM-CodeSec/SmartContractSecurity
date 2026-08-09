# ERC-20 (Token Standard) — pinned standard snapshot

Second registered standard, added specifically to prove `rtf/standards/
discovery.py` and (once built) `generator.py` are genuinely generic across
standard families -- not an ERC-4626 special case. See
`metadata.json`'s `registered_reason` and `note_on_terseness`.

Deliberately smaller than `../ERC-4626/`: 14 hand-authored clauses instead
of 77, because EIP-20's actual specification text is much terser (three of
its six core view methods carry no RFC2119 keyword at all -- see
`clauses.json`'s `excluded_as_non_normative_note`). This isn't a shortcut;
it's an honest reflection of what the real spec text says.

Same file layout and provenance discipline as `../ERC-4626/`:
`erc-20.raw.md` (pinned verbatim snapshot), `metadata.json` (provenance),
`standard.json` (StandardRecord + detection signals), `clauses.json`
(reviewed normative clauses).
