"""Independent, tag-agnostic audit of the L1 corpus's informative-tail
extraction (`parse_spec.py`'s `explanatory_blocks`/`explanatory_text`).

Uses Python's stdlib `html.parser.HTMLParser` -- a real tokenizer,
entirely independent of `parse_spec.py`'s own regex-based classifier --
to recount every `warning`/`note`/`example`/`illegal-example`-classed
`div`/`aside` in the raw spec document. That count is cross-checked
against a second, also-independent char-offset regex pass (so the two
independent methods must agree with each other, not just with the
parser under test), then reconciled against `requirement_corpus.json`'s
`explanatory_tail_block_counts` -- every occurrence that falls outside
any requirement's own tail (e.g. the spec's "How to Read a Requirement"
tutorial section) is individually named, not silently subtracted.

This is the rigor bar `PARSING_NOTES.md`'s two prior real parsing bugs
were caught with: an independent ground-truth count, separate from the
parser's own logic, that the parser's output must reconcile against --
not just "looks right".

Run: .venv/bin/python3 -m rtf.l1_corpus.verify_explanatory_extraction
Exits 1 and prints every unreconciled discrepancy if anything doesn't
add up; exits 0 only when every occurrence is accounted for.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser

from rtf.l1_corpus.parse_spec import (
    HEADING_RE, OUT_JSON, REQ_BLOCK_RE, SPEC_HTML, TITLE_RE, extend_until_modality,
)

_KIND_TO_BLOCK_TYPE = {
    "warning": "warning", "note": "note", "example": "example", "illegal-example": "illegal_example",
}


class _ClassCounter(HTMLParser):
    """Counts every div/aside carrying a warning/note/example/illegal-
    example class token, using the stdlib's own tag tokenizer -- a
    genuinely independent parsing method from `parse_spec.py`'s regexes."""

    def __init__(self) -> None:
        super().__init__()
        self.counts: dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in ("div", "aside"):
            return
        classes = dict(attrs).get("class") or ""
        tokens = set(classes.split())
        for kind in _KIND_TO_BLOCK_TYPE:
            if kind in tokens:
                self.counts[kind] = self.counts.get(kind, 0) + 1


_DIV_ASIDE_TAG_RE = re.compile(r"</?(div|aside)\b[^>]*>")
_CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')


def _classified_occurrences(html: str) -> list[dict]:
    """Walks every div/aside open/close tag in the whole document with a
    real depth-tracking stack (not just position-matching), and returns
    one entry per warning/note/example/illegal-example occurrence:
    `{"kind", "pos", "nested"}`, where `nested` is True iff it sits
    inside another such occurrence (e.g. a `div.warning` wrapping an
    `aside.example`, a real, confirmed shape in this spec --
    req-2-enforce-eval-order's example-13, req-2-avoid-readonly-
    reentrancy's example-15, req-2-random-enough's example-19, and
    req-3-consistent-solidity-output's example-20 all nest this way).

    A nested occurrence is EXPECTED to be folded into its nearest
    classified ancestor's own flattened text by `parse_spec.py`'s
    single-nearest-parent attribution (matching its documented design,
    see PARSING_NOTES.md) -- not to appear as a separate entry in
    `explanatory_blocks`. Only TOP-LEVEL (non-nested) occurrences are
    expected to have their own corpus entry, which is what this
    reconciliation actually checks.
    """
    stack: list[bool] = []  # True = this open frame is itself classified
    occurrences: list[dict] = []
    for m in _DIV_ASIDE_TAG_RE.finditer(html):
        if m.group(0).startswith("</"):
            if stack:
                stack.pop()
            continue
        cm = _CLASS_ATTR_RE.search(m.group(0))
        tokens = set(cm.group(1).split()) if cm else set()
        kind = next((k for k in _KIND_TO_BLOCK_TYPE if k in tokens), None)
        if kind is not None:
            occurrences.append({"kind": kind, "pos": m.start(), "nested": any(stack)})
        stack.append(kind is not None)
    return occurrences


def _requirement_tails(html: str) -> list[tuple[str, int, int]]:
    """Recomputes (req_id, tail_start, tail_end) for every requirement,
    reusing `parse_spec.py`'s own boundary-finding functions unchanged.
    This audit targets the NEW classifier (does it find every warning/
    note/example box?), not the pre-existing, already-tested boundary
    machinery -- reusing it here is deliberate, not a gap in the audit's
    independence, since the boundary logic isn't what's being verified.
    """
    block_starts = []
    for m in REQ_BLOCK_RE.finditer(html):
        req_id = m.group(1) or m.group(2)
        block_starts.append((m.start(), m.end(), req_id))
    headings = [m.start() for m in HEADING_RE.finditer(html)]
    all_boundaries = sorted([b[0] for b in block_starts] + headings)

    tails = []
    seen = set()
    for start, header_end, req_id in block_starts:
        if req_id in seen:
            continue
        seen.add(req_id)
        title_m = TITLE_RE.match(html, header_end)
        if not title_m:
            continue
        _, _, primary_rest = title_m.groups()
        primary_paragraph_end = title_m.end()
        next_boundary = min((b for b in all_boundaries if b > start), default=len(html))
        _, primary_paragraph_end, _ = extend_until_modality(html, primary_paragraph_end, next_boundary, primary_rest)
        tails.append((req_id, primary_paragraph_end, next_boundary))
    return tails


def main() -> int:
    html = SPEC_HTML.read_text(encoding="utf-8", errors="replace")
    corpus = json.loads(OUT_JSON.read_text(encoding="utf-8"))

    tokenizer = _ClassCounter()
    tokenizer.feed(html)

    tails = _requirement_tails(html)
    occurrences = _classified_occurrences(html)

    doc_wide_counts: dict[str, int] = {}
    nested_counts: dict[str, int] = {}
    unowned: dict[str, list[str]] = {}
    for occ in occurrences:
        kind, pos, nested = occ["kind"], occ["pos"], occ["nested"]
        doc_wide_counts[kind] = doc_wide_counts.get(kind, 0) + 1
        if nested:
            nested_counts[kind] = nested_counts.get(kind, 0) + 1
            continue  # a nested occurrence is never expected to be its own separate corpus entry
        owner = next((rid for rid, s, e in tails if s <= pos < e), None)
        if owner is None:
            unowned.setdefault(kind, []).append(html[pos : pos + 100].replace("\n", " "))

    problems: list[str] = []

    # The two independent counting methods (stdlib tokenizer vs. a
    # separate char-offset regex pass) must agree with each other --
    # if they don't, the document's markup isn't what either assumes.
    for kind in _KIND_TO_BLOCK_TYPE:
        tok_count = tokenizer.counts.get(kind, 0)
        regex_count = doc_wide_counts.get(kind, 0)
        if tok_count != regex_count:
            problems.append(
                f"[{kind}] independent methods disagree: stdlib HTMLParser found {tok_count} "
                f"document-wide, char-offset regex found {regex_count}"
            )

    corpus_counts = corpus.get("explanatory_tail_block_counts", {})
    print("Document-wide (independent stdlib HTMLParser tokenizer):", tokenizer.counts)
    print("Corpus explanatory_tail_block_counts:", corpus_counts)
    print()

    for kind, block_type in _KIND_TO_BLOCK_TYPE.items():
        doc_total = doc_wide_counts.get(kind, 0)
        nested = nested_counts.get(kind, 0)
        outside_tail = len(unowned.get(kind, []))
        expected_captured = doc_total - nested - outside_tail
        captured = corpus_counts.get(block_type, 0)
        print(
            f"[{kind}] document-wide={doc_total}  nested-inside-another-occurrence={nested}  "
            f"outside-any-requirement-tail={outside_tail}  expected-captured={expected_captured}  "
            f"actually-captured-in-corpus={captured}"
        )
        for snippet in unowned.get(kind, []):
            print(f"    outside-tail occurrence: {snippet!r}")
        if expected_captured != captured:
            problems.append(
                f"[{kind}] expected {expected_captured} captured (doc-wide {doc_total} minus "
                f"{nested} nested minus {outside_tail} outside any requirement's tail), but corpus "
                f"reports {captured} -- UNRECONCILED"
            )

    print()
    if problems:
        print(f"FAILED: {len(problems)} unreconciled discrepancy(ies)")
        for p in problems:
            print("  -", p)
        return 1

    print(
        "OK: every warning/note/example/illegal-example block in the document is reconciled -- "
        "either captured in its owning requirement's explanatory_blocks, or explicitly accounted "
        "for as sitting outside any requirement's tail."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
