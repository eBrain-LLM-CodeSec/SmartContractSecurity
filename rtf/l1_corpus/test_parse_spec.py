"""Unit tests for rtf.l1_corpus.parse_spec -- the FIRST test coverage
this layer has ever had. Mix of real-spec-derived fixtures (quoted
directly from the live parse, cited by req_id so they can be re-checked
against the raw HTML) and fully synthetic fixtures for the pure helper
functions (invented HTML, nothing derived from EVMbench). Run with:
    .venv/bin/python3 -m rtf.l1_corpus.test_parse_spec
"""
from __future__ import annotations

import sys

from rtf.l1_corpus.parse_spec import (
    classify_informative_tail, extract_balanced_tag, parse,
    render_explanatory_text, strip_tags_preserve_whitespace,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


_CORPUS = parse()
_BY_ID = {r["req_id"]: r for r in _CORPUS["requirements"]}


# --- corpus-shape guards -------------------------------------------------

def test_total_requirements_still_81():
    check("corpus: still 81 requirements", _CORPUS["total_requirements"] == 81, _CORPUS["total_requirements"])


def test_by_level_breakdown_unchanged():
    check("corpus: by_level unchanged", _CORPUS["by_level"] == {"S": 22, "M": 24, "Q": 24, "GP": 11}, _CORPUS["by_level"])


def test_every_requirement_has_the_three_new_fields():
    missing = [
        r["req_id"] for r in _CORPUS["requirements"]
        if "explanatory_text" not in r or "explanatory_blocks" not in r
        or "informative_tail_referenced_requirements" not in r
    ]
    check("corpus: every requirement has explanatory_text/explanatory_blocks/informative_tail_referenced_requirements",
          not missing, missing)


# --- exact-content tests against real, hand-verified requirements --------
# (values below were read directly off requirement_corpus.json after a
# real parse and cross-checked against the raw HTML; see PARSING_NOTES.md)

def test_block_data_misuse_explanatory_text_contains_swc116_example():
    text = _BY_ID["req-2-block-data-misuse"]["explanatory_text"]
    check("block-data-misuse: mentions the SWC-116 block.number/14 example", "block.number / 14" in text, text[:300])


def test_block_data_misuse_captures_warning_box():
    blocks = _BY_ID["req-2-block-data-misuse"]["explanatory_blocks"]
    check("block-data-misuse: warning box captured with its real text",
          any(b["block_type"] == "warning" and "specific block period" in b["text"] for b in blocks), blocks)


def test_block_data_misuse_captures_related_requirements_links():
    links = {r["req_id"] for r in _BY_ID["req-2-block-data-misuse"]["informative_tail_referenced_requirements"]}
    expected = {"req-1-exact-balance-check", "req-2-random-enough", "req-3-block-mev"}
    check("block-data-misuse: Related Requirements links captured", expected <= links, links)


def test_all_valid_inputs_explanatory_text_mentions_swc123():
    text = _BY_ID["req-3-all-valid-inputs"]["explanatory_text"]
    check("all-valid-inputs: mentions SWC-123", "SWC-123" in text, text[:300])


def test_exact_balance_check_explanatory_text_and_links():
    r = _BY_ID["req-1-exact-balance-check"]
    check("exact-balance-check: mentions MEV attack risk", "MEV attack" in r["explanatory_text"], r["explanatory_text"][:300])
    links = {l["req_id"] for l in r["informative_tail_referenced_requirements"]}
    expected = {"req-2-random-enough", "req-2-block-data-misuse", "req-3-block-mev"}
    check("exact-balance-check: Related Requirements links captured", expected <= links, links)


def test_fuzzing_in_testing_captures_scribble_example_with_code():
    blocks = _BY_ID["req-R-fuzzing-in-testing"]["explanatory_blocks"]
    example = next((b for b in blocks if b["block_type"] == "example"), None)
    check("fuzzing: an example block was captured", example is not None, blocks)
    if example is not None:
        check("fuzzing: example_title mentions Scribble", "Scribble" in (example["example_title"] or ""), example["example_title"])
        check("fuzzing: code captured verbatim, includes #if_succeeds", "#if_succeeds" in (example["code"] or ""), example["code"])
        check("fuzzing: code captures the real assertion text", "x == old(x) + y" in (example["code"] or ""), example["code"])


def test_normative_text_byte_identical_for_all_four_requirements():
    # Pinned exactly as read off a real parse pre- and post- this change
    # -- if the classifier were ever accidentally wired into
    # normative_text derivation, these would go stale/fail immediately.
    expected = {
        "req-2-block-data-misuse": "Don't Misuse Block Data Block numbers and timestamps used in Tested Code "
                                    "MUST NOT introduce vulnerabilities to MEV or similar attacks.",
        "req-3-all-valid-inputs": "Process All Inputs Tested Code MUST validate inputs, and function correctly "
                                   "whether the input is as designed or malformed.",
        "req-1-exact-balance-check": "No Exact Balance Check Tested code MUST NOT test that the balance of an "
                                      "account is exactly equal to (i.e. ==) a specified amount or the value of "
                                      "a variable unless it meets the Overriding Requirement [M] Verify Exact "
                                      "Balance Checks.",
        "req-R-fuzzing-in-testing": "Use Fuzzing Fuzzing SHOULD be used to probe Tested Code for errors.",
    }
    for req_id, expected_text in expected.items():
        actual = _BY_ID[req_id]["normative_text"]
        check(f"normative_text unchanged: {req_id}", actual == expected_text, actual)


def test_mutation_testing_definition_list_captured():
    blocks = _BY_ID["req-R-mutation-testing"]["explanatory_blocks"]
    dl = next((b for b in blocks if b["block_type"] == "definition_list"), None)
    check("mutation-testing: a definition_list block was captured", dl is not None, [b["block_type"] for b in blocks])
    if dl is not None:
        check("mutation-testing: State Variable Mutations term captured", "State Variable Mutations" in dl["text"], dl["text"])
        check("mutation-testing: nested <ul> item captured", "Changing visibility modifiers" in dl["text"], dl["text"])


# --- pure unit tests for the helpers, synthetic fixtures ------------------

def test_extract_balanced_tag_handles_nested_divs():
    html = '<div class="warning">outer-start<aside class="example">inner<div>deepest</div>inner-end</aside>outer-end</div>AFTER'
    open_end = html.index(">") + 1
    fragment, end_pos, was_truncated = extract_balanced_tag(html, "div", open_end, len(html))
    check("extract_balanced_tag: not truncated at the first nested </div>", not was_truncated, was_truncated)
    check("extract_balanced_tag: includes innermost content", "deepest" in fragment, fragment)
    check("extract_balanced_tag: includes content after the nested aside closes", "outer-end" in fragment, fragment)
    check("extract_balanced_tag: end_pos lands right after the true closing </div>", html[end_pos:end_pos + 5] == "AFTER", html[end_pos:end_pos + 10])


def test_extract_balanced_tag_flags_unbalanced_as_truncated():
    html = '<div class="warning">no closing tag here, ever'
    open_end = html.index(">") + 1
    fragment, end_pos, was_truncated = extract_balanced_tag(html, "div", open_end, len(html))
    check("extract_balanced_tag: unbalanced tag correctly flagged truncated", was_truncated is True)
    check("extract_balanced_tag: truncated fragment still returns available content", "no closing tag" in fragment, fragment)


def test_classify_informative_tail_logs_unclassified_class():
    html = '<p id="req-x"><b>[S] X<a class="selflink"></a></b> Tested code MUST do X.</p><div class="totally-unknown">mystery content</div>'
    tail_start = html.index("</p>") + len("</p>")
    blocks, notes = classify_informative_tail(html, tail_start, len(html), "req-x")
    check("classify_informative_tail: unclassified div still captured as a block", any(b["block_type"] == "unclassified" for b in blocks), blocks)
    check("classify_informative_tail: unclassified div's content preserved", any("mystery content" in b["text"] for b in blocks), blocks)
    check("classify_informative_tail: unclassified class logged, not silent",
          any(n["issue"] == "unclassified_div_or_aside_class_in_informative_tail" for n in notes), notes)


def test_classify_informative_tail_captures_plain_paragraph():
    html = '<div id="req-y"><p><b>[M] Y<a class="selflink"></a></b> Tested code MUST NOT do Y.</p><p>Explanatory prose about Y.</p></div>'
    tail_start = html.index("Y.</p>") + len("Y.</p>")
    tail_end = html.rindex("</div>")
    blocks, notes = classify_informative_tail(html, tail_start, tail_end, "req-y")
    check("classify_informative_tail: plain paragraph captured", len(blocks) == 1 and blocks[0]["block_type"] == "paragraph", blocks)
    check("classify_informative_tail: paragraph text correct", blocks[0]["text"] == "Explanatory prose about Y.", blocks[0]["text"])
    check("classify_informative_tail: no notes needed for a clean single paragraph", notes == [], notes)


def test_classify_informative_tail_captures_warning_with_code_and_title():
    html = (
        '<p id="req-z"><b>[Q] Z<a class="selflink"></a></b> Tested code SHOULD do Z.</p>'
        '<aside class="example" id="ex-1"><span class="example-title">: A synthetic example</span>'
        '<pre><code class="solidity">uint256 x = 1;</code></pre></aside>'
    )
    tail_start = html.index("Z.</p>") + len("Z.</p>")
    blocks, notes = classify_informative_tail(html, tail_start, len(html), "req-z")
    check("classify_informative_tail: example block captured", len(blocks) == 1 and blocks[0]["block_type"] == "example", blocks)
    check("classify_informative_tail: example_title extracted", blocks[0]["example_title"] == "A synthetic example", blocks[0]["example_title"])
    check("classify_informative_tail: code captured verbatim", blocks[0]["code"] == "uint256 x = 1;", blocks[0]["code"])
    check("classify_informative_tail: code_language_hint captured", blocks[0]["code_language_hint"] == "solidity", blocks[0]["code_language_hint"])


def test_render_explanatory_text_prefixes_warning_and_note():
    blocks = [
        {"block_type": "warning", "text": "be careful", "block_id": None, "example_title": None, "code": None},
        {"block_type": "note", "text": "fyi", "block_id": None, "example_title": None, "code": None},
        {"block_type": "paragraph", "text": "plain prose", "block_id": None, "example_title": None, "code": None},
    ]
    rendered = render_explanatory_text(blocks)
    check("render_explanatory_text: warning gets [Warning] prefix", "[Warning] be careful" in rendered, rendered)
    check("render_explanatory_text: note gets [Note] prefix", "[Note] fyi" in rendered, rendered)
    check("render_explanatory_text: plain paragraph has no prefix", "plain prose" in rendered and "[Warning] plain prose" not in rendered, rendered)


def test_render_explanatory_text_empty_blocks_produce_empty_string():
    check("render_explanatory_text: empty list -> empty string", render_explanatory_text([]) == "", render_explanatory_text([]))


def test_strip_tags_preserve_whitespace_keeps_newlines_and_unescapes_entities():
    fragment = "line one\n<span class=\"hljs-x\">&lt;Foo&gt;</span> &amp; more\nline two"
    result = strip_tags_preserve_whitespace(fragment)
    check("strip_tags_preserve_whitespace: newlines preserved", "\n" in result, result)
    check("strip_tags_preserve_whitespace: entities unescaped", "<Foo>" in result and "&" in result, result)
    check("strip_tags_preserve_whitespace: tags removed", "<span" not in result, result)


# --- corpus-wide sanity ----------------------------------------------------

def test_every_explanatory_block_has_recognized_type():
    known = {"paragraph", "list", "definition_list", "warning", "note", "example", "illegal_example", "unclassified"}
    bad = [
        (r["req_id"], b["block_type"])
        for r in _CORPUS["requirements"] for b in r["explanatory_blocks"]
        if b["block_type"] not in known
    ]
    check("corpus: every block_type is a recognized value", not bad, bad)


def test_explanatory_tail_block_counts_matches_sum_over_records():
    recomputed: dict[str, int] = {}
    for r in _CORPUS["requirements"]:
        for b in r["explanatory_blocks"]:
            recomputed[b["block_type"]] = recomputed.get(b["block_type"], 0) + 1
    check("corpus: explanatory_tail_block_counts matches a fresh sum over all records",
          recomputed == _CORPUS["explanatory_tail_block_counts"], (recomputed, _CORPUS["explanatory_tail_block_counts"]))


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
