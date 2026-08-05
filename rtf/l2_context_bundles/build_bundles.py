"""L2: Context Bundle Constructor.

Builds the "requirement + normative dependencies" translation unit per the
RTF plan: self text, referenced definitions, overriding/exception/
referenced requirements, external references, and (for requirements
directly under a top-level Security Level section rather than a numbered
subsection) the section's own introductory text.

Adaptive, capped expansion (Rev. 3): start at the requirement's own
directly-referenced items (hop 1). For each item pulled in, scan its own
raw HTML for #dfn-*/#req-* links not already in the bundle -- if found,
that's an "unresolved normative reference" and triggers one more hop.
Hard cap at 3 hops; anything still unresolved when the cap is hit is
logged as a bundle-insufficiency finding, not silently dropped or expanded
further.

Originally built and validated in Track A against six requirements; the
mechanism generalizes directly (no per-requirement code, purely data-
driven from the L1 corpus), so it was run unchanged across all 81
requirements for Track B once Track A's go/no-go passed -- see
BUNDLES_NOTES.md for that run's results (81/81, zero cap hits).
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_HTML = ROOT / "standards" / "ethtrust" / "ethtrust-sl.raw.html"
CORPUS_JSON = ROOT / "rtf" / "l1_corpus" / "requirement_corpus.json"
OUT_DIR = Path(__file__).resolve().parent

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
INTERNAL_LINK_RE = re.compile(r'<a href="#(dfn|req)-([A-Za-z0-9._-]+)"')
MAX_HOPS = 3


def strip_tags(html_fragment: str) -> str:
    return WS_RE.sub(" ", TAG_RE.sub("", html_fragment)).strip()


def extract_dfn_definition(html: str, dfn_id: str) -> tuple[str | None, str | None]:
    """Returns (raw_html, plain_text) of the <p> containing the <dfn id="dfn_id">."""
    pattern = re.compile(
        r'<p>((?:(?!</p>).)*?<dfn[^>]*\bid="' + re.escape(dfn_id) + r'"[^>]*>.*?</dfn>(?:(?!</p>).)*?)</p>',
        re.S,
    )
    m = pattern.search(html)
    if not m:
        return None, None
    return m.group(1), strip_tags(m.group(1))


def extract_bib_entry(html: str, bib_id: str) -> tuple[str | None, str | None]:
    pattern = re.compile(r'<dt id="' + re.escape(bib_id) + r'">(.*?)</dt>\s*<dd>(.*?)</dd>', re.S)
    m = pattern.search(html)
    if not m:
        return None, None
    raw = m.group(0)
    text = f"{strip_tags(m.group(1))} -- {strip_tags(m.group(2))}"
    return raw, text


def extract_section_intro(html: str, secno: str) -> str | None:
    """Text between a top-level section's own heading and its first child
    subsection heading or first requirement div/p -- the section's own
    introductory prose, if any (used as parent_section_context)."""
    heading_pattern = re.compile(
        r'<h[2-4][^>]*>\s*<bdi class="secno">\s*' + re.escape(secno) + r'\s*</bdi>.*?</h[2-4]>',
        re.S,
    )
    hm = heading_pattern.search(html)
    if not hm:
        return None
    tail = html[hm.end() : hm.end() + 3000]
    # Stop at the first requirement wrapper or the next heading.
    stop_m = re.search(r'<(?:p|div) id="req-|<h[2-4]', tail)
    intro_html = tail[: stop_m.start()] if stop_m else tail
    text = strip_tags(intro_html)
    return text or None


def find_unresolved_links(raw_html: str, already_included: set[str]) -> list[dict]:
    found = []
    for m in INTERNAL_LINK_RE.finditer(raw_html):
        kind, ident = m.group(1), m.group(2)
        full_id = f"{kind}-{ident}"
        if full_id in already_included:
            continue
        context = strip_tags(raw_html[max(0, m.start() - 60) : m.end() + 60])
        found.append({"kind": kind, "id": full_id, "context_quote": context})
    return found


def build_context_bundle(html: str, corpus_by_id: dict, req_id: str) -> dict:
    r = corpus_by_id[req_id]
    included_dfn: set[str] = set()
    included_req: set[str] = {req_id}
    included_bib: set[str] = set()

    bundle = {
        "self": r["normative_text"],
        "definitions": [],
        "parent_section_context": None,
        "referenced_requirements": [],
        "overriding_requirements": [],
        "exceptions": [],
        "external_references": [],
    }
    expansion_log = []

    section = r.get("section") or {}
    if section.get("secno") and section["secno"].count(".") == 1:
        # A bare top-level secno like "5.1" (one dot -- NOT "5.1.2", which has
        # two) -- this requirement sits directly under the Security Level
        # section, not a numbered subsection, so that section's own intro
        # text is relevant context.
        intro = extract_section_intro(html, section["secno"])
        if intro:
            bundle["parent_section_context"] = intro

    frontier_dfn = list(dict.fromkeys(r["definitions_referenced"]))
    frontier_req = list(
        dict.fromkeys(
            o["req_id"]
            for o in (r["overriding_requirements"] + r["referenced_requirements"])
            if o.get("req_id")
        )
    )
    frontier_bib = list(dict.fromkeys(r["external_references"]["bibliographic"]))

    override_target_ids = {
        o["req_id"] for o in r["overriding_requirements"] if o.get("req_id")
    }
    exception_target_ids = {
        o["req_id"] for o in r["exceptions_referenced"] if o.get("req_id")
    }

    hop = 1
    cap_hit = False
    while hop <= MAX_HOPS and (frontier_dfn or frontier_req or frontier_bib):
        next_dfn: list[str] = []
        next_req: list[str] = []

        for did in frontier_dfn:
            if did in included_dfn:
                continue
            included_dfn.add(did)
            raw, text = extract_dfn_definition(html, did)
            bundle["definitions"].append({"id": did, "text": text})
            expansion_log.append(
                {
                    "hop": hop,
                    "item_added": did,
                    "reason": "directly referenced" if hop == 1 else "unresolved normative reference",
                }
            )
            if raw:
                for link in find_unresolved_links(raw, included_dfn | included_req):
                    if link["kind"] == "dfn":
                        next_dfn.append(link["id"].removeprefix("dfn-"))
                    else:
                        next_req.append(link["id"].removeprefix("req-"))

        for rid in frontier_req:
            if rid in included_req:
                continue
            included_req.add(rid)
            rr = corpus_by_id.get(rid)
            entry = {"req_id": rid, "normative_text": rr["normative_text"] if rr else None}
            if rid in override_target_ids or rid in exception_target_ids:
                bundle["overriding_requirements"].append(entry)
                if rid in exception_target_ids:
                    bundle["exceptions"].append(entry)
            else:
                bundle["referenced_requirements"].append(entry)
            expansion_log.append(
                {
                    "hop": hop,
                    "item_added": rid,
                    "reason": "directly referenced" if hop == 1 else "unresolved normative reference",
                }
            )
            if rr:
                for d2 in rr["definitions_referenced"]:
                    if d2 not in included_dfn:
                        next_dfn.append(d2)
                for o2 in rr["overriding_requirements"] + rr["referenced_requirements"]:
                    r2id = o2.get("req_id")
                    if r2id and r2id not in included_req:
                        next_req.append(r2id)

        for bid in frontier_bib:
            if bid in included_bib:
                continue
            included_bib.add(bid)
            _, text = extract_bib_entry(html, bid)
            bundle["external_references"].append({"id": bid, "text": text})
            expansion_log.append({"hop": hop, "item_added": bid, "reason": "directly referenced"})

        frontier_dfn = list(dict.fromkeys(next_dfn))
        frontier_req = list(dict.fromkeys(next_req))
        frontier_bib = []
        hop += 1

    if hop > MAX_HOPS and (frontier_dfn or frontier_req):
        cap_hit = True
        expansion_log.append(
            {
                "hop": MAX_HOPS + 1,
                "item_added": None,
                "reason": f"bundle insufficiency, cap reached -- unresolved: "
                f"dfn={frontier_dfn} req={frontier_req}",
            }
        )

    return {
        "req_id": req_id,
        "bundle": bundle,
        "expansion_log": expansion_log,
        "traversal_depth_reached": min(hop - 1, MAX_HOPS),
        "expansion_cap_hit": cap_hit,
        "assembled_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main(req_ids: list[str]) -> None:
    html = SPEC_HTML.read_text(encoding="utf-8", errors="replace")
    corpus = json.loads(CORPUS_JSON.read_text())
    corpus_by_id = {r["req_id"]: r for r in corpus["requirements"]}
    OUT_DIR.mkdir(exist_ok=True)

    for req_id in req_ids:
        record = build_context_bundle(html, corpus_by_id, req_id)
        payload = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
        record["bundle_hash"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        payload = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
        out_file = OUT_DIR / f"{req_id}.json"
        out_file.write_text(payload, encoding="utf-8")
        print(f"{req_id}: depth={record['traversal_depth_reached']} cap_hit={record['expansion_cap_hit']} -> {out_file}")


if __name__ == "__main__":
    import sys

    if sys.argv[1:]:
        ids = sys.argv[1:]
    else:
        # No args: build bundles for every requirement in the L1 corpus
        # (Track B default, since this run at 81/81, zero cap hits). Pass
        # specific req_ids as argv to rebuild/inspect just a subset.
        ids = [r["req_id"] for r in json.loads(CORPUS_JSON.read_text())["requirements"]]
    main(ids)
