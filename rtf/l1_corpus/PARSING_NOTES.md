# L1 Requirement Corpus — parsing methodology and known limitations

`parse_spec.py` mechanically parses `standards/ethtrust/ethtrust-sl.raw.html`
into `requirement_corpus.json` (81 records) + `requirement_corpus.sha256`
(the freeze hash, per the RTF plan's freeze-checklist item #2).

## What "mechanical" means here

Every extracted field traces to an explicit markup pattern the spec itself
uses consistently, not to interpretation of meaning:

- **Requirement identity/title/level**: `<p id="req-...">` or
  `<div id="req-...">` wrapping `<b>[LEVEL] Title<selflink></b>`.
- **Modality**: `<em class="rfc2119" title="MUST|MUST NOT|SHOULD|...">` spans
  — the spec's own RFC2119 markup, not keyword-guessing over plain text.
- **Conditioned scope clause**: the text preceding the first RFC2119 span
  within the (possibly sibling-extended, see below) normative block.
- **Overriding/exception relationships**: both the singular
  `#dfn-overriding-requirement` and plural
  `#dfn-sets-of-overriding-requirements` link patterns, classified by
  looking at plain-text context immediately before/after the link (e.g.
  "unless" before it, "for" right after it) — not by keyword search over
  the whole paragraph, which would be too easily confused by unrelated
  uses of "for"/"unless".
- **Definitions/enumerated terms/external references**:
  `#dfn-*` links, `<code>` spans, `class="bibref"` links, and raw external
  `http(s)://` links respectively.

## Two real bugs found and fixed during development (not spec defects)

1. **Wrapper-tag undercounting.** A first pass only matched `<p id="req-...">`
   requirements (53) and missed 27 more written as
   `<div id="req-...">` wrapping an inner unlabeled `<p>`. True current
   total is **81** (54 `<p>` + 27 `<div>`), confirmed by a full tag-agnostic
   audit of every `id="req-*"` occurrence in the document (128 total: 81
   current + 47 `class="removed"` legacy entries from prior spec versions,
   intentionally excluded). This also corrected the requirement-inventory
   figure carried from planning (~52, from an AI-summarized fetch) — the
   real by-level breakdown is **S=22, M=24, Q=24, GP=11**.
2. **List-split normative clauses.** 13 requirements write their header
   paragraph without any RFC2119 keyword at all (e.g. "Tested code
   that</p>"), with the actual MUST/MUST NOT living inside a following
   `<ul>`'s `<li>` items, or in a sibling `<p>` after the list. The parser
   now glues immediately-following sibling `<ul>`/`<p>` blocks onto the
   header content (capped at 4 blocks) until an RFC2119 keyword is found,
   and logs every such extension in `parsing_notes` (`issue:
   "normative_clause_extended_into_sibling_blocks"`) so it's auditable,
   not silent. Also added the reverse "This is part of the Set of
   Overriding Requirements for [X]" direction, which doesn't have an
   adjacent `<ul>` to find (the `<ul>` lives at the *target* requirement's
   own location, listing all members of that set) — 2 requirements needed
   this before it resolved correctly.

## A third variant of the same bug, found during Track B (AR-005)

Bug 2 above (list-split normative clauses) only handled the case where
the header has **no** RFC2119 keyword at all. Two more shapes exist,
found while doing Track B's M-level analysis (they weren't present in
Track A's original 6 requirements, so went uncaught until the broader
sweep):

- **Colon-terminated header with an early keyword**: e.g.
  `req-2-documented`'s header reads "Tested Code MUST document the need
  for each instance of:" — a MUST is already present, so the original
  no-keyword check never triggered extension, silently truncating the
  actual 8-item list of named triggers that gives the requirement its
  real content.
- **Dangling keyword with an empty tail**: e.g. `req-2-self-destruct`'s
  header ends "...instructions MUST</p>" with the real predicate
  ("ensure that only authorised parties can call the method...") only
  starting in a following `<ul>`. The keyword is technically present, so
  this also evaded the original check.

Both are now covered by a generalized `_looks_incomplete()` check (not
just "keyword absent") that also fires on a colon-terminated header or a
keyword whose measured tail (correctly computed *after* the keyword's
closing `</em>` tag, not after its opening tag — an off-by-one caught
during this same fix) is near-empty. Re-running after the fix changed
`normative_text` for 7 requirements, all pure *extensions* — a diff
against the pre-fix corpus confirmed zero requirements got shorter,
zero requirements newly gained an unwanted extension, and referential
integrity (zero dangling cross-references) held both before and after.

One of the seven, `req-1-compiler-060` (already translated in Track A),
had its override-set's *contents* revealed for the first time — 9 named
EthTrust-SL v2 requirements, previously invisible because the truncation
landed exactly at the colon introducing that list. This narrowed, but
did not close, that research gap — see the requirement's own L4 record
(`rtf/track_a/l4_analyzer_mappings/req-1-compiler-060.json`) for the
update.

## One genuine spec-content gap (not a parser bug)

`req-R-check-new-bugs` ("[GP] Check For and Address New Security Bugs")
has **no RFC2119 keyword anywhere in its normative text**, even after
sibling-block extension — it's phrased as a bare imperative ("Check
[...] and address them") rather than using MUST/SHOULD. This is
correctly left with `modality: []` and flagged in `parsing_notes` rather
than guessed. Left as a research-gap candidate for the Assumptions
Register if this requirement is ever selected for translation.

## Known simplification, disclosed rather than silently accepted

For multi-clause list requirements (e.g. `req-2-external-calls`, which has
4 separate MUST clauses across its `<li>` items), `conditioned_scope_clause`
is a mechanical concatenation of the header lead-in text with the first
list item's pre-keyword text (e.g. "For Tested code that makes external
calls: all addresses called by the Tested code"). This is coherent as a
*shared* scope for the list's first clause but does not by itself
represent each list item as a separately-scoped sub-requirement. If such a
requirement is ever selected for Track A, its applicability/strategy
derivation (L3+) should treat each `<li>` as its own sub-clause rather
than relying on this single concatenated string — noted here so this
simplification doesn't get silently relied on downstream.

## Referential integrity

Every `req_id` target inside `overriding_requirements`/
`referenced_requirements` was checked against the 81-requirement corpus
after both bug fixes above: **zero dangling references remain.**

## Explanatory/informative content extraction

Root-caused via a real missed vulnerability in a paid audit run (canto,
config D, EthTrust requirement `req-2-block-data-misuse`): the parser
previously captured *only* the single bolded normative sentence for
each requirement into `normative_text`, stopping exactly at that
sentence's own `</p>`. Everything the spec says immediately after —
explanatory paragraphs, `div.warning`/`div.note` boxes,
`aside.example`/`div.example` code examples, `<dl>` definition lists,
and "See also the Related Requirements [...]" cross-references — was
silently dropped. For `req-2-block-data-misuse`, that dropped text
names the exact bug pattern later missed in the real audit: *"using
block.number / 14 as a proxy for elapsed seconds"* (SWC-116). This
section documents the fix.

**New fields, additive only.** `normative_text` and every field derived
from it (`modality`, `conditioned_scope_clause`, `overriding_
requirements`, `referenced_requirements`, `definitions_referenced`,
`exceptions_referenced`, `enumerated_terms`) are completely untouched —
verified byte-identical for all 81 requirements (see the superset diff
in `test_parse_spec.py` / `verify_explanatory_extraction.py`). This is
required, not a style choice: `rtf/l10_property_derivation/derive_
investigations.py`'s `derive_clauses()` sentence-splits `normative_text`
and treats every resulting sentence as its own investigatable property
— folding explanatory prose into that same string would inject
non-normative sentences into the split, diluting the per-requirement
investigation-instance cap with junk clauses.

Three new fields per requirement record:
- `explanatory_text: str` — a single flattened, whitespace-normalized
  rendering of every informative block following the normative
  sentence, in document order. Named to match `context_artifacts.
  generate_requirement_context_md`'s pre-existing (previously unused)
  `explanatory_text` parameter.
- `explanatory_blocks: list[dict]` — the structured source
  `explanatory_text` renders from:
  `{block_type, block_id, example_title, text, code,
  code_language_hint, raw_html}`, one entry per top-level block.
  `block_type` is one of `paragraph`, `list`, `definition_list`,
  `warning`, `note`, `example`, `illegal_example`, `unclassified`.
  Kept structured (not just flattened) so code examples survive
  verbatim with whitespace preserved (`strip_tags_preserve_whitespace`,
  distinct from the whitespace-collapsing `strip_tags` used for prose).
- `informative_tail_referenced_requirements: list[dict]` —
  `{req_id, link_text}`, every `#req-` cross-reference found anywhere
  in the tail (via the existing `REQ_LINK_RE`, scanned over the whole
  tail rather than trying to isolate a "See also" paragraph by phrasing
  — that phrasing isn't consistent enough to pattern-match reliably).
  Deliberately a separate field from the existing `referenced_
  requirements` (which stays scoped to the primary sentence only), so a
  future consumer (e.g. a new grouping-engine compatibility signal) can
  use it unambiguously without conflating primary-clause references
  with tail cross-references. Not deduplicated, matching `referenced_
  requirements`'s own existing behavior.

Corpus-level: `explanatory_tail_block_counts` — total block count per
`block_type` across all 81 requirements, for the independent audit
below.

**Attribution when content sits between two requirements.** Every
informative block is attributed to its nearest-*preceding* requirement
only, reusing the existing `next_boundary_after_start` boundary
computation (already used, unchanged, for `full_block`). Checked
directly against the one case that looked like it might need shared
attribution (`req-2-random-enough`'s and `req-2-block-data-misuse`'s
examples, both about block-data predictability): their HTML blocks do
NOT actually overlap — each requirement's tail is cleanly bounded and
each already cross-references the other via its own `informative_
tail_referenced_requirements`. Single-attribution loses nothing here.

**A real gap found and fixed while verifying this against the raw
HTML, not anticipated by the original design:** `req-R-mutation-
testing`'s tail uses a `<dl>` (definition list: `<dt>term</dt><dd>
description, possibly with a nested &lt;ul&gt;</dd>` pairs) to lay out
its four Mutation Operator categories — a structurally distinct shape
from `<ul>` that the classifier didn't originally recognize. Added a
dedicated `definition_list` block type (`DT_DD_PAIR_RE`, flattening
each nested `<ul>` into the same rendered text) rather than letting it
fall through to `unclassified`.

**Corrected block-occurrence counts** (measured directly against the
raw HTML, superseding earlier approximate figures from an earlier pass
of this investigation): `div.warning` = 8 total in the document (6
attributable to a requirement's own tail; the other 2 sit inside
sections that aren't a requirement's immediate tail), `div.note` = 12,
`aside.example`/`div.example` = 22 combined (21 `aside`, 1 rare nested
`div`), `div.illegal-example` = 0 real occurrences (the class exists
only in the document's `<style>` block, not in body content — designed
for, expected to log zero, not an error).

**Known limitation, disclosed rather than silently accepted.** A
handful of short connective fragments that sit *between* two
recognized blocks but aren't themselves wrapped in a recognized tag
(e.g. `req-1-delegatecall`'s "or it meets the Set of Overriding
Requirements", bridging its two alternative override-list branches)
are logged to `parsing_notes` (`issue: "unclassified_informative_text_
before_block"`) with a 200-char preview, but are not themselves added
as a block to `explanatory_blocks`/`explanatory_text`. In the one case
found in the live corpus, this fragment is part of a requirement's own
normative override-list structure (already flagged separately as
`set_of_overriding_requirements_mentioned_but_no_adjacent_ul_found`
before this change), not lost informative prose — but this is a
disclosed simplification for the general case, not a guarantee that no
future spec text could be lost this way. If `explanatory_tail_block_
counts` or a future parse shows this occurring more often, revisit
capturing these fragments as their own `unclassified` block rather
than log-only.

**Independent verification.** `rtf/l1_corpus/verify_explanatory_
extraction.py` re-counts every `warning`/`note`/`example`/
`illegal-example`-classed block document-wide using Python's stdlib
`html.parser.HTMLParser` (a real tokenizer, independent of this
parser's own regex-based classifier) and reconciles the total against
`explanatory_tail_block_counts`, accounting individually for any block
that exists in the document but outside any requirement's own tail.
