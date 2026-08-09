"""Generic, standards-driven requirement-generation mechanism for EthTrust's
`[GP] Follow Accepted ERC Standards` (req-R-follow-erc-standards).

Deliberately isolated from `rtf.l1_corpus`/`rtf.l12_evaluation.registry`'s
static 81-requirement corpus: standards registered here (`rtf/standards/erc/`)
and the atomic requirements `generator.py` derives from their clauses are a
logically separate, dynamically-sized pool that gets merged into a pipeline
run's routed-requirement set additively, never written into
`rtf/l1_corpus/requirement_corpus.json` itself. See
`rtf/l12_evaluation/ETH_TRUST_GP_IMPLEMENTATION_REPORT.md` (once written) for
the full architecture; `GP_ACCEPTED_ERC_DEFINITION.md` in this directory for
the "what counts as an accepted ERC" decision record.
"""
