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
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
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


def strip_tags(html_fragment: str) -> str:
    return WS_RE.sub(" ", TAG_RE.sub("", html_fragment)).strip()


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


def _looks_incomplete(text: str) -> bool:
    """True if `text` doesn't yet read as a complete normative clause.
    Three real cases found in the spec (AR-005):
    (1) No RFC2119 keyword at all yet -- the original, narrower check.
    (2) Header ends with ':' -- introduces a <ul> needed to complete the
        sentence, even though a keyword already appears earlier in the
        header (e.g. req-2-documented: 'MUST document the need for each
        instance of:').
    (3) A keyword is present but DANGLING -- essentially nothing follows it
        in this block (e.g. req-2-self-destruct's header ends "... MUST</p>"
        with the actual predicate only starting in a following <ul>).
    """
    stripped = strip_tags(text).strip()
    if not stripped:
        return True
    if stripped.endswith(":"):
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
                "maturity": "DRAFT_TRANSLATION",
            }
        )

    metadata = json.loads((SPEC_HTML.parent / "metadata.json").read_text())

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
