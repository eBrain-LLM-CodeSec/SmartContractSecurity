# Track A step 1 — selection rationale and a finding worth flagging early

Full protocol and category definitions are in `select_candidates.py`'s
module docstring; this file covers rationale plus one structural finding
surfaced while sanity-checking the frozen selection (per the plan's own
Track A step 1(e): review is allowed, reselection for difficulty is not).

## Frozen selection

| Category | req_id | Level | Title |
|---|---|---|---|
| 1. VERSION_ONLY compiler (S) | `req-1-compiler-060` | S | Use a Modern Compiler |
| 2. Unconditioned pure-syntactic (S) | `req-1-eip155-chainid` | S | Encode Hashes with `chainid` |
| 3. Conditioned/PATTERN_AND_VERSION (S) | `req-1-compiler-sol-2021-4` | S | Compiler Bug SOL-2021-4 |
| 4. M deterministic-trigger candidate | `req-2-verify-exact-balance-check` | M | Verify Exact Balance Checks |
| 5. M full-semantic-review candidate | `req-2-overflow-underflow` | M | Safe Overflow/Underflow |
| 6. Q (any) | `req-3-implement-as-documented` | Q | Implement as Documented |

Category population sizes before sampling: 2 / 9 / 9 / 3 / 12 / 24 — every
category had at least 2 candidates except category 1 (2, still allowed
real sampling) and category 4 (3). None were singletons requiring the
"no sampling needed" fallback, so the deterministic-seed tie-break was
exercised in every category — good, since an untested tie-break rule is a
weaker freeze guarantee than one actually exercised by the run.

## A genuine structural finding, not a miscategorization

`req-2-overflow-underflow`'s exception clause ("...MUST NOT contain
calculations that can overflow or underflow **unless** ...") is followed
by a plain-prose `<ul>` ("there is a demonstrated need... and there are
guards... to ensure behavior consistent with the claims of the contract
author") with **no cross-reference to another requirement ID at all** --
a third exception pattern distinct from both the singular
`#dfn-overriding-requirement` link and the plural `#dfn-sets-of-
overriding-requirements` link the L1 parser already handles. The L1
`overriding_requirements`/`exceptions_referenced` fields are correctly
empty for this requirement (there is genuinely no target requirement to
link to), so this is **not a parser bug** -- but it does mean this
requirement's real exception condition ("demonstrated need" + "guards...
consistent with author's claims") lives only in prose, entirely outside
the fields L1 currently structures. This needs to be pulled into this
requirement's context bundle (L2) as inline text, not just via
cross-references, when Track A step 2 processes it.

This *reinforces* rather than undermines the category-4/5 selection: it's
a clean, real example of exactly the "abstract, judgment-requiring
condition with no concrete syntactic anchor" that the
`FULL_SEMANTIC_REVIEW` category exists to test -- if anything, it's a
sharper test case than a synthetic one would have been, since per
selection rule 1(e) this stays in the tranche rather than being swapped
out for looking hard.

## Freeze artifacts

- `selected_requirements.json` -- the frozen record (six req_ids +
  category, selection-detail with sampling seed/index per category,
  timestamp, corpus hash it was derived from).
- `selected_requirements.sha256` -- freeze hash of that file.

Both are committed to git immediately after generation, before any
analyzer-coverage check or EVMbench correspondence work begins on these
six requirements (Track A step 2).
