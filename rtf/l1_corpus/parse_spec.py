"""L1 Requirement Corpus parser (RTF Phase 0/1).

Mechanically parses the verbatim EthTrust spec snapshot
(standards/ethtrust/ethtrust-sl.raw.html) into structured requirement
records, per the L1 schema in the RTF plan
(/scratch/md5344/.claude/plans/ou-are-a-critical-purring-eich.md).

Deliberately mechanical, not NLP-based: every field is derived from an
explicit HTML/text pattern present in the spec's own markup (RFC2119
keyword spans, singular "Overriding Requirement" / plural "Set of
Overriding Requirements" phrasing, internal definition/requirement links,
<code> spans for enumerated syntactic terms). Anything that can't be
derived this way is left null and flagged in `parsing_notes`, not guessed.

Corrects a real bug found during development: a first pass only matched
requirements written as `<p id="req-...">`, missing 27 requirements the
spec writes as `<div id="req-...">` wrapping an inner `<p>` -- true
current requirement count is 81 (54 <p>-wrapped + 27 <div>-wrapped), not
53. A `class="removed"` group (47 ids) of requirements superseded from
prior spec versions is intentionally excluded from the current corpus.

This is intentionally a standalone script, not a package import, so it
can be re-run to regenerate the corpus if the spec snapshot changes
(bumping framework_version) without importing framework internals.

Also extracts each requirement's full informative "tail" -- the
explanatory paragraphs, warning/note/example boxes, and Related-
Requirements cross-references that follow the bolded normative
sentence in the real spec -- into `explanatory_text`/`explanatory_
blocks`/`informative_tail_referenced_requirements`. Previously only
the bolded sentence was captured; `RTF_ETHTRUST_TRANSLATION_AUDIT.md`
found this drops real, on-point guidance (e.g. req-2-block-data-
misuse's tail names the exact "block.number / 14 as a proxy for
elapsed seconds" bug pattern later missed in a real audit run). This
is purely additive: `normative_text` and every field derived from it
are untouched.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from html import unescape as html_unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_HTML = ROOT / "standards" / "ethtrust" / "ethtrust-sl.raw.html"
OUT_JSON = Path(__file__).resolve().parent / "requirement_corpus.json"
OUT_HASH = Path(__file__).resolve().parent / "requirement_corpus.sha256"

# Matches EITHER a <p id="req-..."> or a <div id="req-..."> (with an inner
# unlabeled <p>) requirement wrapper, immediately followed by the bold
# "[LEVEL] Title" + self-link, then captures the rest of that same <p> as
# the primary normative paragraph. `class="removed"` items never match
# this (they're on <a> tags in a changelog list, not <p>/<div>).
REQ_BLOCK_RE = re.compile(
    r'<p id="(req-[A-Za-z0-9._-]+)">|<div id="(req-[A-Za-z0-9._-]+)">\s*<p>'
)
TITLE_RE = re.compile(
    r'\s*<b>\s*\[(S|M|Q|GP|R)\]\s*(.*?)<a[^>]*class="selflink"[^>]*></a>\s*</b>(.*?)</p>',
    re.S,
)

HEADING_RE = re.compile(r'<h([2-4])[^>]*id="([^"]*)"[^>]*>(.*?)</h\1>', re.S)
SECNO_RE = re.compile(r'<bdi class="secno">\s*([\d.]+)\s*</bdi>')
RFC2119_RE = re.compile(r'<em class="rfc2119" title="([^"]+)">')
REQ_LINK_RE = re.compile(r'<a href="#(req-[A-Za-z0-9._-]+)"[^>]*>(.*?)</a>', re.S)
DFN_LINK_RE = re.compile(r'<a href="#(dfn-[A-Za-z0-9._-]+)"[^>]*class="internalDFN"[^>]*>(.*?)</a>', re.S)
BIBREF_RE = re.compile(r'<a class="bibref" href="#(bib-[A-Za-z0-9._-]+)"[^>]*>(.*?)</a>', re.S)
EXTERNAL_HREF_RE = re.compile(r'<a href="(https?://[^"#][^"]*)"[^>]*>(.*?)</a>', re.S)
CODE_RE = re.compile(r"<code>(.*?)</code>", re.S)
LI_RE = re.compile(r"<li>(.*?)</li>", re.S)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

OR_DFN_MENTION_RE = re.compile(
    r'<a href="#dfn-overriding-requirement"[^>]*>Overriding Requirement</a>'
)
OR_SET_DFN_MENTION_RE = re.compile(
    r'<a href="#dfn-sets-of-overriding-requirements"[^>]*>Set of Overriding Requirements</a>'
)
SET_OVERRIDES_FOR_RE = re.compile(
    r'part of the <a href="#dfn-sets-of-overriding-requirements"[^>]*>'
    r"Set of Overriding Requirements</a> for\s*"
    r'<a href="#(req-[A-Za-z0-9._-]+)"[^>]*>(.*?)</a>',
    re.S,
)
SIBLING_BLOCK_RE = re.compile(r"\s*(<ul>.*?</ul>|<p>.*?</p>)", re.S)

# --- Informative-tail extraction (explanatory paragraphs, warning/note/
# example boxes, "Related Requirements" cross-refs that follow a
# requirement's own primary normative sentence -- see PARSING_NOTES.md's
# "Explanatory/informative content extraction" section for the full
# rationale and the real audit gap this closes) ---
TAIL_BLOCK_OPEN_RE = re.compile(r"<(div|aside|ul|dl|p)\b([^>]*)>")
CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')
ID_ATTR_RE = re.compile(r'id="([^"]*)"')
EXAMPLE_TITLE_RE = re.compile(r'<span class="example-title">:?\s*(.*?)</span>', re.S)
PRE_CODE_RE = re.compile(r"<pre[^>]*>\s*<code([^>]*)>(.*?)</code>\s*</pre>", re.S)
DT_DD_PAIR_RE = re.compile(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", re.S)
UL_INNER_RE = re.compile(r"<ul>(.*?)</ul>", re.S)


def strip_tags(html_fragment: str) -> str:
    return WS_RE.sub(" ", TAG_RE.sub("", html_fragment)).strip()


def strip_tags_preserve_whitespace(html_fragment: str) -> str:
    """Like `strip_tags`, but does NOT collapse whitespace and DOES
    unescape entities. Needed specifically for <pre><code> content
    (e.g. the Scribble fuzzing-spec example under req-R-fuzzing-in-
    testing): collapsing newlines/indentation the way `strip_tags` does
    for prose would destroy the code's readability, and leaving
    entities like `&lt;`/`&gt;` un-unescaped would corrupt the source
    text `strip_tags` never needs to touch (prose doesn't round-trip
    through entity-escaped operators)."""
    return html_unescape(TAG_RE.sub("", html_fragment)).strip("\n")


def extract_balanced_tag(html: str, tag_name: str, open_end: int, hard_limit: int) -> tuple[str, int, bool]:
    """Depth-tracking scan for the CONTENT of a `<tag_name ...>...
    </tag_name>` block, given `open_end` (the position right after the
    already-matched OPENING tag) and a `hard_limit` (the requirement's
    own tail boundary, never crossed). Correctly handles nesting -- e.g.
    a `div.warning` wrapping an `aside.example` wrapping a further
    `div` (a real shape found under req-2-random-enough) -- which a
    naive non-greedy `<div ...>.*?</div>` regex would truncate at the
    FIRST nested closing tag, silently losing content. This is exactly
    the bug class PARSING_NOTES.md's two prior real parsing bugs were.
    Returns (inner_content, position_right_after_the_matching_closing_
    tag, was_truncated) -- `was_truncated=True` means no matching close
    was found before `hard_limit`; the caller must log a parsing_notes
    entry in that case, never silently truncate without one.
    """
    tag_re = re.compile(rf"</?{tag_name}\b[^>]*>", re.I)
    depth = 1
    for m in tag_re.finditer(html, open_end, hard_limit):
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return html[open_end : m.start()], m.end(), False
        else:
            depth += 1
    return html[open_end:hard_limit], hard_limit, True


def classify_informative_tail(html: str, tail_start: int, tail_end: int, req_id: str) -> tuple[list[dict], list[dict]]:
    """Walks the informative tail following a requirement's own primary
    normative sentence (from `tail_start` -- right after that sentence's
    closing </p> -- up to `tail_end`, the next requirement/heading
    boundary) and classifies every top-level block found: plain <p>
    (explanatory prose), <ul> (an enumerated list), <div>/<aside>
    carrying a `warning`/`note`/`example`/`illegal-example` class token
    (checked as an exact token, not a substring match, so e.g.
    "warning-title" never matches "warning"). Anything that doesn't fit
    a recognized shape is captured as `block_type: "unclassified"` and
    logged to `notes` -- never silently dropped. Returns
    (blocks, parsing_notes_entries), both in document order.
    """
    blocks: list[dict] = []
    notes: list[dict] = []
    pos = tail_start
    while pos < tail_end:
        m = TAIL_BLOCK_OPEN_RE.search(html, pos, tail_end)
        if not m:
            leftover = strip_tags(html[pos:tail_end])
            if leftover:
                notes.append(
                    {
                        "req_id": req_id,
                        "issue": "unclassified_informative_trailing_text",
                        "note": f"Non-empty text after the last recognized informative block: {leftover[:200]!r}",
                    }
                )
            break
        if m.start() > pos:
            between = strip_tags(html[pos : m.start()])
            if between:
                notes.append(
                    {
                        "req_id": req_id,
                        "issue": "unclassified_informative_text_before_block",
                        "note": f"Text found between two recognized informative blocks: {between[:200]!r}",
                    }
                )

        tag_name = m.group(1)
        attrs = m.group(2)
        block_id_m = ID_ATTR_RE.search(attrs)
        block_id = block_id_m.group(1) if block_id_m else None

        if tag_name == "p":
            close_idx = html.find("</p>", m.end())
            if close_idx == -1 or close_idx >= tail_end:
                notes.append(
                    {
                        "req_id": req_id,
                        "issue": "unbalanced_tag_in_informative_block",
                        "note": "A <p> in the informative tail has no closing </p> before the requirement boundary; truncated at the boundary.",
                    }
                )
                fragment, end_pos = html[m.end() : tail_end], tail_end
            else:
                fragment, end_pos = html[m.end() : close_idx], close_idx + len("</p>")
            blocks.append(
                {
                    "block_type": "paragraph", "block_id": block_id, "example_title": None,
                    "text": strip_tags(fragment), "code": None, "code_language_hint": None,
                    "raw_html": html[m.start() : end_pos],
                }
            )
            pos = end_pos
        elif tag_name == "ul":
            close_idx = html.find("</ul>", m.end())
            if close_idx == -1 or close_idx >= tail_end:
                notes.append(
                    {
                        "req_id": req_id,
                        "issue": "unbalanced_tag_in_informative_block",
                        "note": "A <ul> in the informative tail has no closing </ul> before the requirement boundary; truncated at the boundary.",
                    }
                )
                fragment, end_pos = html[m.end() : tail_end], tail_end
            else:
                fragment, end_pos = html[m.end() : close_idx], close_idx + len("</ul>")
            items = [strip_tags(li) for li in LI_RE.findall(fragment)]
            blocks.append(
                {
                    "block_type": "list", "block_id": block_id, "example_title": None,
                    "text": "\n".join(f"- {it}" for it in items if it), "code": None, "code_language_hint": None,
                    "raw_html": html[m.start() : end_pos],
                }
            )
            pos = end_pos
        elif tag_name == "dl":
            # A definition list of <dt>term</dt><dd>description</dd> pairs
            # (e.g. req-R-mutation-testing's "Mutation Operators" taxonomy)
            # -- a real, distinct shape from <ul>, found directly while
            # verifying this extraction against the raw HTML (not
            # anticipated by the original design). Each <dd> may itself
            # wrap a nested <ul>; that's flattened into the same rendered
            # text rather than dropped.
            fragment, end_pos, was_truncated = extract_balanced_tag(html, tag_name, m.end(), tail_end)
            if was_truncated:
                notes.append(
                    {
                        "req_id": req_id,
                        "issue": "unbalanced_tag_in_informative_block",
                        "note": "A <dl> in the informative tail has no matching closing tag before the requirement boundary; truncated at the boundary.",
                    }
                )
            lines = []
            for pair_m in DT_DD_PAIR_RE.finditer(fragment):
                term = strip_tags(pair_m.group(1))
                dd_html = pair_m.group(2)
                ul_m = UL_INNER_RE.search(dd_html)
                if ul_m:
                    intro = strip_tags(dd_html[: ul_m.start()])
                    items = [strip_tags(li) for li in LI_RE.findall(ul_m.group(1)) if strip_tags(li)]
                    dd_text = intro
                    if items:
                        dd_text += ("\n" if intro else "") + "\n".join(f"  - {it}" for it in items)
                else:
                    dd_text = strip_tags(dd_html)
                if term or dd_text:
                    lines.append(f"{term}: {dd_text}" if term else dd_text)
            blocks.append(
                {
                    "block_type": "definition_list", "block_id": block_id, "example_title": None,
                    "text": "\n".join(lines), "code": None, "code_language_hint": None,
                    "raw_html": html[m.start() : end_pos],
                }
            )
            pos = end_pos
        else:  # div or aside
            class_m = CLASS_ATTR_RE.search(attrs)
            classes = set(class_m.group(1).split()) if class_m else set()
            fragment, end_pos, was_truncated = extract_balanced_tag(html, tag_name, m.end(), tail_end)
            if was_truncated:
                notes.append(
                    {
                        "req_id": req_id,
                        "issue": "unbalanced_tag_in_informative_block",
                        "note": f"A <{tag_name}> in the informative tail has no matching closing tag before the requirement boundary; truncated at the boundary.",
                    }
                )
            if "warning" in classes:
                block_type = "warning"
            elif "note" in classes:
                block_type = "note"
            elif "illegal-example" in classes:
                block_type = "illegal_example"
            elif "example" in classes:
                block_type = "example"
            else:
                block_type = "unclassified"
                notes.append(
                    {
                        "req_id": req_id,
                        "issue": "unclassified_div_or_aside_class_in_informative_tail",
                        "note": f"<{tag_name}> with class(es) {sorted(classes)!r} did not match any recognized informative-block type.",
                    }
                )

            example_title = None
            code = None
            code_language_hint = None
            text_source = fragment
            if block_type in ("example", "illegal_example"):
                title_m = EXAMPLE_TITLE_RE.search(fragment)
                if title_m:
                    example_title = strip_tags(title_m.group(1))
                code_m = PRE_CODE_RE.search(fragment)
                if code_m:
                    code_attrs = code_m.group(1)
                    lang_m = CLASS_ATTR_RE.search(code_attrs)
                    code_language_hint = lang_m.group(1) if lang_m else None
                    code = strip_tags_preserve_whitespace(code_m.group(2))
                    text_source = fragment[: code_m.start()] + fragment[code_m.end() :]

            blocks.append(
                {
                    "block_type": block_type, "block_id": block_id, "example_title": example_title,
                    "text": strip_tags(text_source), "code": code, "code_language_hint": code_language_hint,
                    "raw_html": html[m.start() : end_pos],
                }
            )
            pos = end_pos
    return blocks, notes


def render_explanatory_text(blocks: list[dict]) -> str:
    """Flattens `explanatory_blocks` (in document order) into the single
    `explanatory_text` string `context_artifacts.generate_requirement_
    context_md`'s existing `explanatory_text` parameter expects.
    Warning/note/example blocks are prefixed so their kind survives
    even in the flattened form; empty blocks contribute nothing."""
    chunks = []
    for b in blocks:
        bt = b["block_type"]
        if bt == "warning":
            chunk = f"[Warning] {b['text']}" if b["text"] else ""
        elif bt == "note":
            chunk = f"[Note] {b['text']}" if b["text"] else ""
        elif bt in ("example", "illegal_example"):
            label = b["example_title"] or b["block_id"] or "?"
            chunk = f"[Example: {label}] {b['text']}" if b["text"] else f"[Example: {label}]"
            if b["code"]:
                chunk += f"\nCode:\n{b['code']}"
        else:
            chunk = b["text"]
        if chunk:
            chunks.append(chunk)
    return "\n\n".join(chunks)


def find_section_context(headings: list[tuple[int, str, str, str]], pos: int) -> dict | None:
    best = None
    for hoffset, hlevel, hsecno, htitle in headings:
        if hoffset < pos:
            best = {"level": hlevel, "secno": hsecno, "title": htitle}
        else:
            break
    return best


def classify_singular_override_relationships(primary_html: str) -> tuple[list[dict], list[tuple[int, int]]]:
    """Singular 'Overriding Requirement' -- target named inline via a #req- link
    shortly after the dfn mention. Returns (relationships, claimed_char_spans)."""
    rels = []
    claimed = []
    for dfn_m in OR_DFN_MENTION_RE.finditer(primary_html):
        lookbehind_text = strip_tags(primary_html[max(0, dfn_m.start() - 200) : dfn_m.start()]).lower()
        lookahead_raw = primary_html[dfn_m.end() : dfn_m.end() + 250]
        lookahead_text = strip_tags(lookahead_raw).lower()

        target_link = REQ_LINK_RE.search(lookahead_raw)
        if target_link is None:
            continue

        if lookahead_text.startswith("for"):
            relation = "this_requirement_overrides"
        elif "unless" in lookbehind_text[-60:]:
            relation = "this_requirement_is_excepted_by"
        else:
            relation = "overriding_requirement_mentioned_direction_unclear"

        rels.append(
            {
                "req_id": target_link.group(1),
                "relation": relation,
                "link_text": strip_tags(target_link.group(2)),
                "condition_text": None,
            }
        )
        claimed.append((dfn_m.end() + target_link.start(), dfn_m.end() + target_link.end()))
    return rels, claimed


def classify_set_of_overriding_requirements(primary_html: str, tail_after_primary: str) -> tuple[list[dict], bool]:
    """Plural 'Set of Overriding Requirements', both directions:
    (a) "... this MUST NOT ... unless it meets the Set of Overriding
        Requirements" -- THIS requirement is excepted by the set, whose
        members are listed in a <ul> immediately following the primary
        paragraph's closing </p>.
    (b) "This is part of the Set of Overriding Requirements for [X]" --
        THIS requirement is itself one member of a set that excepts X;
        the target is named inline, no adjacent <ul> to find.
    Returns (relationships, mention_found_without_resolvable_list) -- the
    second value is only meaningful for direction (a).
    """
    reverse_m = SET_OVERRIDES_FOR_RE.search(primary_html)
    if reverse_m:
        return (
            [
                {
                    "req_id": reverse_m.group(1),
                    "relation": "this_requirement_is_one_of_set_overriding",
                    "link_text": strip_tags(reverse_m.group(2)),
                    "condition_text": None,
                }
            ],
            False,
        )

    if not OR_SET_DFN_MENTION_RE.search(primary_html):
        return [], False

    ul_m = re.match(r"\s*<ul>(.*?)</ul>", tail_after_primary, re.S)
    if not ul_m:
        return [], True  # mentioned but no adjacent <ul> found -- flag for review

    rels = []
    for li_m in LI_RE.finditer(ul_m.group(1)):
        li_html = li_m.group(1)
        link_m = REQ_LINK_RE.search(li_html)
        if link_m:
            target_req_id = link_m.group(1)
            link_text = strip_tags(link_m.group(2))
            outside_link_text = strip_tags(li_html[: link_m.start()])
            rels.append(
                {
                    "req_id": target_req_id,
                    "relation": "this_requirement_is_excepted_by_one_of_set",
                    "link_text": link_text,
                    "condition_text": outside_link_text or None,
                }
            )
        else:
            # No internal #req- link -- typically a reference to a predecessor
            # (v1-only) requirement no longer in the current corpus. Record as
            # an unresolvable external predecessor reference rather than
            # silently dropping it.
            ext_m = EXTERNAL_HREF_RE.search(li_html)
            rels.append(
                {
                    "req_id": None,
                    "relation": "this_requirement_is_excepted_by_one_of_set_external_predecessor",
                    "link_text": strip_tags(li_html),
                    "condition_text": None,
                    "external_url": ext_m.group(1) if ext_m else None,
                }
            )
    return rels, False


_SENTENCE_TERMINAL_CHARS = (".", "!", "?")

# Bare connective words the spec sometimes places alone in a sibling <p> or
# <b> to join two normative clauses across block boundaries (e.g.
# req-2-compiler-060: "...as an Overriding Requirement,</p><p><b>AND</b></p>
# <p>Tested code MUST NOT..."). A clause ending in one of these, even with
# terminal-looking punctuation stripped away, is still mid-sentence. Checked
# case-insensitively against the LAST word only, not as a substring, so real
# words like "command" or "further" are never caught.
_DANGLING_CONNECTIVES = {"and", "or", "nor", "unless", "but", "provided"}


def _looks_incomplete(text: str) -> bool:
    """True if `text` doesn't yet read as a complete normative clause.
    Real cases found in the spec (AR-005, AR-027):
    (1) No RFC2119 keyword at all yet -- the original, narrower check.
    (2) A keyword is present but DANGLING -- essentially nothing follows it
        in this block (e.g. req-2-self-destruct's header ends "... MUST</p>"
        with the actual predicate only starting in a following <ul>).
    (3) The accumulated text does not end in real sentence-terminal
        punctuation ('.', '!', '?'). AR-027: the original version of this
        function instead tried to special-case "ends with ':'" (introduces
        a <ul>) and treated anything else with a keyword-plus-long-tail as
        complete. That silently mis-classified several genuinely incomplete
        clauses as complete, each confirmed by direct comparison against
        the raw spec HTML:
          - req-2-documented: extension stopped right after gluing on the
            enumerated <ul>, because the accumulated text (ending in
            "...pseudo-randomness,") already had a keyword with a long
            tail -- silently dropping two further MUST obligations that
            exist only in a later sibling <p> ("and MUST describe how the
            Tested Code protects against misuse...").
          - req-2-external-calls, req-2-protect-create2, req-2-self-destruct,
            req-2-malleable-signatures-for-replay: each ends with "...unless
            it meets the Set of Overriding Requirements" (or similar) with
            NO terminal punctuation at all, immediately followed by the
            actual enumerated Overriding-Requirement <ul> that completes
            the same sentence -- previously left off entirely.
        A real English sentence never legitimately ends on a bare comma,
        colon, dash, or connective word -- requiring real terminal
        punctuation is a strictly more correct generalization of the
        colon-specific check it replaces, not a narrower one: every case
        the old ':'-check caught is also caught here (a colon is not
        terminal punctuation either).
    (4) The accumulated text's last word (case-insensitive) is a bare
        dangling connective (see `_DANGLING_CONNECTIVES`) -- e.g.
        req-2-compiler-060's "...Overriding Requirement,</p><p><b>AND</b></p>":
        after rule (3) forces extension past the comma, the next sibling
        block is a standalone "AND", which itself has no terminal
        punctuation either, but a naive re-check could still mis-fire if a
        future spec revision ever puts terminal punctuation after a bare
        connective marker -- checking the connective explicitly, not just
        terminal punctuation, is the more robust of the two and catches
        this class directly regardless.
    """
    stripped = strip_tags(text).strip()
    if not stripped:
        return True
    last_word = re.findall(r"[A-Za-z]+", stripped)
    if last_word and last_word[-1].lower() in _DANGLING_CONNECTIVES:
        return True
    matches = list(RFC2119_RE.finditer(text))
    if not matches:
        return True
    # RFC2119_RE matches only the OPENING <em class="rfc2119" ...> tag --
    # text right after .end() is the keyword's own visible text (e.g.
    # "MUST"), not real predicate content. Measure the tail from after the
    # matching closing </em>, not from after the opening tag, or a bare
    # dangling keyword (the actual bug this function exists to catch) gets
    # miscounted as having "MUST" itself as three-plus characters of tail.
    close_idx = text.find("</em>", matches[-1].end())
    tail_start = close_idx + len("</em>") if close_idx != -1 else matches[-1].end()
    tail_plain = strip_tags(text[tail_start:]).strip()
    if len(tail_plain) < 3:
        return True
    if stripped[-1] not in _SENTENCE_TERMINAL_CHARS:
        return True
    return False


def extend_until_modality(html: str, start_pos: int, boundary_limit: int, initial_text: str, max_blocks: int = 4) -> tuple[str, int, bool]:
    """Some requirements split their normative clause across sibling blocks:
    the header <p> ends before any RFC2119 keyword (e.g. "Tested code
    that</p>"), or ends with a colon introducing a <ul>, or ends with a
    keyword itself dangling with nothing after it in this block -- in all
    three cases (see _looks_incomplete), the actual MUST/MUST NOT predicate
    continues inside a following <ul>'s <li> items or a subsequent sibling
    <p>. Glue immediately-following sibling <ul>/<p> blocks onto the text
    (only whitespace allowed between them) until it reads as complete,
    capped at `max_blocks` to avoid runaway. Returns (extended_text,
    new_end_pos, was_extended).
    """
    if not _looks_incomplete(initial_text):
        return initial_text, start_pos, False

    accumulated = initial_text
    cur_pos = start_pos
    extended = False
    for _ in range(max_blocks):
        if cur_pos >= boundary_limit:
            break
        m = SIBLING_BLOCK_RE.match(html, cur_pos)
        if not m or m.end() > boundary_limit:
            break
        block = m.group(1)
        accumulated += " " + block
        cur_pos = m.end()
        extended = True
        if not _looks_incomplete(accumulated):
            break
    return accumulated, cur_pos, extended


def extract_conditioned_scope_clause(primary_html: str, rfc2119_match: re.Match) -> dict:
    before = primary_html[: rfc2119_match.start()]
    clause_text = strip_tags(before)
    bare_subject_variants = {"tested code"}
    is_unconditioned = clause_text.strip().lower() in bare_subject_variants
    return {"raw_html": before.strip(), "text": clause_text, "is_unconditioned_subject": is_unconditioned}


def parse() -> dict:
    html = SPEC_HTML.read_text(encoding="utf-8", errors="replace")

    headings = []
    for m in HEADING_RE.finditer(html):
        level_digit, hid, inner = m.groups()
        secno_m = SECNO_RE.search(inner)
        secno = secno_m.group(1) if secno_m else None
        title_text = strip_tags(SECNO_RE.sub("", inner))
        headings.append((m.start(), level_digit, secno, title_text))

    # First pass: locate every requirement block start + its wrapper tag/id.
    block_starts = []
    for m in REQ_BLOCK_RE.finditer(html):
        req_id = m.group(1) or m.group(2)
        wrapper = "p" if m.group(1) else "div"
        block_starts.append((m.start(), m.end(), req_id, wrapper))

    heading_boundaries = [h[0] for h in headings]
    all_boundaries = sorted([b[0] for b in block_starts] + heading_boundaries)

    records = []
    parsing_notes = []
    seen_ids = set()

    for start, header_end, req_id, wrapper in block_starts:
        if req_id in seen_ids:
            parsing_notes.append({"req_id": req_id, "issue": "duplicate_block_start_skipped"})
            continue
        seen_ids.add(req_id)

        title_m = TITLE_RE.match(html, header_end)
        if not title_m:
            parsing_notes.append(
                {
                    "req_id": req_id,
                    "issue": "title_pattern_did_not_match_after_wrapper_start",
                    "note": "Requirement wrapper found but the expected "
                    "'<b>[LEVEL] Title<selflink></b>...</p>' pattern didn't "
                    "match immediately after it -- skipped, needs manual review.",
                }
            )
            continue

        level, title_html, primary_rest = title_m.groups()
        title = strip_tags(title_html)
        primary_paragraph_end = title_m.end()

        next_boundary_after_start = min(
            (b for b in all_boundaries if b > start), default=len(html)
        )
        primary_rest, primary_paragraph_end, was_extended = extend_until_modality(
            html, primary_paragraph_end, next_boundary_after_start, primary_rest
        )
        if was_extended:
            parsing_notes.append(
                {
                    "req_id": req_id,
                    "issue": "normative_clause_extended_into_sibling_blocks",
                    "note": "Header paragraph read as an incomplete normative "
                    "clause (AR-005: no RFC2119 keyword yet, OR header ends "
                    "with ':' introducing a list, OR a keyword is present but "
                    "dangling with no real predicate text after it in this "
                    "block); normative text was extended to include "
                    "immediately-following sibling <ul>/<p> block(s) until it "
                    "read as complete. Not an error -- logged so the extension "
                    "is auditable rather than silent.",
                }
            )

        rfc2119_matches = list(RFC2119_RE.finditer(primary_rest))
        modality = [mm.group(1) for mm in rfc2119_matches]

        if rfc2119_matches:
            scope = extract_conditioned_scope_clause(primary_rest, rfc2119_matches[0])
        else:
            scope = {"raw_html": None, "text": None, "is_unconditioned_subject": None}
            parsing_notes.append(
                {
                    "req_id": req_id,
                    "issue": "no_rfc2119_keyword_found_in_primary_paragraph",
                    "note": "Modality/scope-clause extraction skipped even after "
                    "sibling-block extension; requires manual review.",
                }
            )

        singular_rels, claimed_spans = classify_singular_override_relationships(primary_rest)

        tail_after_primary = html[primary_paragraph_end : primary_paragraph_end + 4000]
        set_rels, set_mentioned_unresolved = classify_set_of_overriding_requirements(
            primary_rest, tail_after_primary
        )
        if set_mentioned_unresolved:
            parsing_notes.append(
                {
                    "req_id": req_id,
                    "issue": "set_of_overriding_requirements_mentioned_but_no_adjacent_ul_found",
                    "note": "Requires manual review to locate the actual override targets.",
                }
            )

        override_rels = singular_rels + set_rels

        claimed_link_starts = {s for s, _ in claimed_spans}
        referenced_rels = []
        for m in REQ_LINK_RE.finditer(primary_rest):
            if m.start() in claimed_link_starts:
                continue
            referenced_rels.append(
                {"req_id": m.group(1), "relation": "referenced", "link_text": strip_tags(m.group(2))}
            )

        definitions = sorted({d for d, _ in DFN_LINK_RE.findall(primary_rest)})
        enumerated_terms = sorted({strip_tags(c) for c in CODE_RE.findall(primary_rest)})

        explanatory_blocks, tail_notes = classify_informative_tail(
            html, primary_paragraph_end, next_boundary_after_start, req_id
        )
        parsing_notes.extend(tail_notes)
        explanatory_text = render_explanatory_text(explanatory_blocks)
        informative_tail_referenced_requirements = [
            {"req_id": m.group(1), "link_text": strip_tags(m.group(2))}
            for m in REQ_LINK_RE.finditer(html[primary_paragraph_end:next_boundary_after_start])
        ]

        full_block = html[start:next_boundary_after_start]

        bibrefs = sorted({b for b, _ in BIBREF_RE.findall(full_block)})
        external_links = sorted(
            {(url, strip_tags(text)) for url, text in EXTERNAL_HREF_RE.findall(full_block)}
        )

        normative_text_plain = strip_tags(f"{title_html} {primary_rest}")
        section = find_section_context(headings, start)

        records.append(
            {
                "req_id": req_id,
                "level": level,
                "title": title,
                "wrapper_tag": wrapper,
                "section": section,
                "modality": modality,
                "normative_text": normative_text_plain,
                "conditioned_scope_clause": scope,
                "overriding_requirements": [
                    r for r in override_rels if r["relation"] != "referenced"
                ],
                "referenced_requirements": referenced_rels,
                "definitions_referenced": definitions,
                "exceptions_referenced": [
                    r
                    for r in override_rels
                    if r["relation"]
                    in (
                        "this_requirement_is_excepted_by",
                        "this_requirement_is_excepted_by_one_of_set",
                        "this_requirement_is_excepted_by_one_of_set_external_predecessor",
                    )
                ],
                "external_references": {
                    "bibliographic": bibrefs,
                    "external_links_in_full_block": [
                        {"url": u, "text": t} for u, t in external_links
                    ],
                },
                "enumerated_terms": enumerated_terms,
                "explanatory_text": explanatory_text,
                "explanatory_blocks": explanatory_blocks,
                "informative_tail_referenced_requirements": informative_tail_referenced_requirements,
                "maturity": "DRAFT_TRANSLATION",
            }
        )

    metadata = json.loads((SPEC_HTML.parent / "metadata.json").read_text())

    explanatory_tail_block_counts: dict[str, int] = {}
    for r in records:
        for b in r["explanatory_blocks"]:
            explanatory_tail_block_counts[b["block_type"]] = explanatory_tail_block_counts.get(b["block_type"], 0) + 1

    corpus = {
        "spec_version": metadata["spec_version"],
        "spec_source_hash": metadata["raw_snapshot_sha256"],
        "spec_retrieved_at": metadata["retrieved_at"],
        "parser_run_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parser_script": "rtf/l1_corpus/parse_spec.py",
        "total_requirements": len(records),
        "by_level": {
            lvl: sum(1 for r in records if r["level"] == lvl) for lvl in ["S", "M", "Q", "GP"]
        },
        "by_wrapper_tag": {
            "p": sum(1 for r in records if r["wrapper_tag"] == "p"),
            "div": sum(1 for r in records if r["wrapper_tag"] == "div"),
        },
        "explanatory_tail_block_counts": explanatory_tail_block_counts,
        "requirements": records,
        "parsing_notes": parsing_notes,
    }
    return corpus


def main() -> None:
    corpus = parse()
    OUT_JSON.write_text(json.dumps(corpus, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(OUT_JSON.read_bytes()).hexdigest()
    OUT_HASH.write_text(f"{digest}  {OUT_JSON.name}\n")
    print(f"Wrote {OUT_JSON} ({corpus['total_requirements']} requirements)")
    print(f"By level: {corpus['by_level']}")
    print(f"By wrapper tag: {corpus['by_wrapper_tag']}")
    print(f"sha256: {digest}")
    if corpus["parsing_notes"]:
        print(f"parsing_notes: {len(corpus['parsing_notes'])} item(s) flagged for manual review")
        for n in corpus["parsing_notes"]:
            print("  -", n)


if __name__ == "__main__":
    main()
