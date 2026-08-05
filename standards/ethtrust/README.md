# EthTrust Security Levels Specification — verbatim snapshot

This directory is the RTF (Requirement Translation Framework) Phase 0
artifact: a frozen, verbatim, licensed snapshot of the EthTrust spec that
the rest of the framework treats as ground truth. See `metadata.json` for
retrieval provenance, hash, and license basis.

- `ethtrust-sl.raw.html` — the raw HTML of the published spec, fetched by
  direct HTTPS GET (not summarized by any model). This is the canonical
  verbatim source for all downstream parsing.
- `APACHE-2.0.LICENSE.txt` — the license the spec itself is published
  under (Apache License 2.0), included per that license's own
  redistribution terms.
- `metadata.json` — provenance record: source URL, spec version,
  copyright notice, content hash, retrieval timestamp/method, and the
  requirement-inventory count re-derived from this verbatim text.

**Do not edit `ethtrust-sl.raw.html`.** If the spec is refetched (e.g. a
new version is published), save it as a new file
(`ethtrust-sl.v<N>.raw.html`) and update `metadata.json` with a new
snapshot record rather than overwriting this one — the frozen snapshot a
given `framework_version` was built against must remain reproducible.

**Corrects two errors found during Phase 0/1:** research done before this
snapshot (via a summarizing WebFetch) reported a provisional requirement
count of ~52 (24 S / 17 M / 9 Q / 2 GP) and identified the spec as
"Version 1 or Version 2." The verbatim text says otherwise: this is
**Version 3**. A first verbatim-parsing pass then undercounted at 53
(10 S / 12 M / 20 Q / 11 GP) because it only matched requirements written
as `<p id="req-...">`, missing 27 more written as
`<div id="req-...">`. The true, fully-audited count is **81** currently-
normative requirements (**22 S / 24 M / 24 Q / 11 GP**). See
`metadata.json`'s `requirement_inventory_verified_from_verbatim_text` and
`../../rtf/l1_corpus/PARSING_NOTES.md` for the full accounting, including
the 47 `class="removed"` legacy requirement anchors (mostly per-year
compiler-bug entries later consolidated into a single current requirement)
that are intentionally excluded from the current corpus.
