# ERC-4626 (Tokenized Vaults) — pinned standard snapshot

Registered under EthTrust's `[GP] Follow Accepted ERC Standards`
(`req-R-follow-erc-standards`) as the first concrete `EXTERNAL_STANDARD_DERIVED`
standard implemented through the generic mechanism in `rtf/standards/`. See
`../GP_ACCEPTED_ERC_DEFINITION.md` for why ERC-4626 qualifies as "accepted"
(traced to EthTrust's own bibliography, not invented).

- `erc-4626.raw.md` — verbatim pinned snapshot of the ERC-4626 spec text,
  fetched by direct HTTPS GET (curl), not summarized by any model. Frontmatter
  states `status: Final`. **Do not edit.** If a new EIP-4626 revision is ever
  published, save it as a new file and add a new snapshot record to
  `metadata.json` rather than overwriting this one.
- `metadata.json` — provenance record: source URL, retrieval method/timestamp,
  content hash, license, and the explicit "accepted ERC" qualification note
  (traced to EthTrust's own bibliography, not invented).
- `standard.json` — the `StandardRecord`: standard identity, detection
  signals (strong/supporting), and parent GP linkage, consumed by
  `rtf/standards/registry.py`.
- `clauses.json` — 77 manually-authored, individually-provenanced normative
  clauses extracted from every function (`asset` through `redeem`), both
  events (`Deposit`/`Withdraw`), the top-level EIP-20-conformance
  requirements, and the one explicit cross-function invariant in Security
  Considerations. See `clauses.json`'s own `extraction_method_note` for why
  this is a reviewed/pinned representation rather than output of the generic
  `clause_parser.py` extractor, and `excluded_as_non_normative_note` for what
  was deliberately left out and why (lowercase "should", advisory prose,
  Rationale-section discussion).

**Deliberately covers every ERC-4626 method, not just `totalAssets`.** Per
the implementation plan's explicit instruction: this exists to demonstrate
that the `totalAssets` fee-accounting obligation
(`erc4626-totalassets-must-include-fees`) emerges from processing the real
ERC-4626 specification text as one clause among many, not from any knowledge
of a specific benchmark finding.
