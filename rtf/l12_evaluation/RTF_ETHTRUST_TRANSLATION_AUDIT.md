# RTF vs. EthTrust v3: translation-fidelity audit (Phase 1)

**Status: analysis only. No code has been modified as part of this
document — per the explicit instruction, this is the hard gate that must
be reviewed before any implementation work begins.**

**Method:** every requirement below was re-read directly from the pinned
local EthTrust v3 spec source (`standards/ethtrust/ethtrust-sl.raw.html`),
independent of anything RTF currently stores about it, and independent of
EVMbench. Ground truth (EVMbench) was **not** consulted anywhere in this
document. Only after building each row's "proposed correction" did I
cross-check it against the existing `RTF_MISSED_FINDINGS_ROOT_CAUSE_REPORT.md`
E-classifications, noted separately at the bottom, never the other way
around.

For each requirement, "current RTF interpretation" traces the **actual
code path**, not the design intent recorded in `rtf/track_a/` (which is a
prototype/rubric layer that, per its own `SCHEMA.md`, was never executed
— the live pipeline's real prompt-construction path is
`rtf/l12_evaluation/codex_bridge.py::build_codex_prompt_inputs`, fed by
`rtf/l12_evaluation/registry.py`'s predicate registration and
`rtf/l5_predicates/predicates.py`'s actual trigger logic).

---

## 1. `[Q] Process All Inputs` (`req-3-all-valid-inputs`)

**Full normative + explanatory text (spec, not RTF's stored copy):**
> Tested Code MUST validate inputs, and function correctly whether the
> input is as designed or malformed. Code that fails to validate inputs
> runs the risk of being subverted through maliciously crafted input that
> can trigger a bug, or behaviour the authors did not anticipate. See
> also SWC-123 which notes that **it is important to consider whether
> input requirements are too strict, as well as too lax**, [CWE-573]
> Improper Following of Specification by Caller, and note there are
> several Related Requirements specific to particular Solidity compiler
> versions.

**Current RTF representation:**
- Corpus `normative_text` (`rtf/l1_corpus/requirement_corpus.json`):
  captures only the bare first sentence. Drops the "too strict as well as
  too lax" clause and the CWE-573 framing entirely — these never reach
  the L2 context bundle (`rtf/l2_context_bundles/req-3-all-valid-inputs.json`
  only carries `dfn-tested-code` + two bibliography stub lines, not this
  explanatory prose).
- Applicability (`rtf/track_a/l3_applicability/req-3-all-valid-inputs.json`):
  `target_grain: "contract"` — unconditionally applicable to any Tested
  Code, one applicability decision **per contract**, not per function or
  per parameter.
- Predicates registered (`registry.py:122-124`):
  `find_unvalidated_function_parameters` (flags functions with zero
  `require()`/`assert()` touching any parameter — a coarse presence
  check, explicitly documented in its own docstring as
  `DETERMINISTIC_EVIDENCE_ONLY`, "does not establish CORRECT/COMPLETE
  validation") and `find_unsafe_narrowing_cast` (flags unchecked
  `uintN(x)`/`intN(x)` narrowing casts). Both correctly produce
  **multiple** findings, one per function/site, each with its own
  `location`.
- **Instantiation collapse** (`pipeline_e2e.py:379`,
  `codex_bridge.build_codex_prompt_inputs`): `rank_evidence` ranks all
  those per-site findings, then `candidate_location = ranked[0].item.location`
  — only the single top-ranked location becomes the investigation seed.
  The prompt sent to Codex is the one-line truncated normative text plus
  evidence for that ONE location. **One requirement → one investigation
  → one function**, even though every other flagged function/site is
  never independently investigated at all — its predicate evidence exists
  in the evidence pool but is discarded past the top rank.

**Information lost:**
1. The "too strict as well as too lax" and CWE-573 explanatory text —
   never reaches the model, so the investigation has no textual grounding
   to look for *over*-restrictive validation (e.g. a function that
   reverts on legitimate edge-case inputs), only under-validation.
2. Multi-instance collapse: a codebase with 20 functions flagged by
   `find_unvalidated_function_parameters` gets exactly 1 investigated,
   the other 19 silently never get an agent's attention for this
   requirement, with no telemetry distinguishing "investigated and
   passed" from "never looked at."
3. No decomposition of "validate inputs" into the concrete boundary
   classes the spec's own cited CWE/SWC entries actually describe (zero
   values, max-uint values, zero addresses, empty arrays, array-length
   mismatches, reentrant re-entry mid-validation, decimal/precision
   mismatches for token amounts) — the requirement's single sentence is
   forwarded to Codex as-is and the model has to invent its own
   decomposition each time, inconsistently, with no systematic coverage
   guarantee.

**Proposed correction (justified from this text alone, not EVMbench):**
Add a property-derivation step between applicability and investigation
that, for a requirement whose scope is function/parameter-level (as this
one's own referenced CWE-573/SWC-123 texts imply — "Caller" following
"Specification" is inherently about the boundary of individual callable
entry points), enumerates the actual candidate set from the repo's own
structure (every externally-callable function with ≥1 parameter) rather
than one contract-level applicability decision, and expands each flagged
location into its own scoped investigation instance, subject to
combinatorial controls (Phase 3). Carry the full explanatory text (not
just the corpus's truncated `normative_text`) into the L2 bundle/prompt
so "too strict as well as too lax" is visible to the investigating agent.

---

## 2. `[Q] Document Contract Logic` (`req-3-documented`) and `[Q] Implement as Documented` (`req-3-implement-as-documented`)

**Full text, Document Contract Logic:**
> A specification of the business logic that the Tested code
> functionality is intended to implement MUST be available to anyone who
> can call the Tested Code. Contract Logic documented in a human-readable
> format and with enough detail that functional correctness and safety
> assumptions for special code use can be validated by auditors helps
> them assess complex code more efficiently... **It is important to
> document how the logic protects against potential attacks such as
> Flash Loan Attacks (especially on governance or price manipulation),
> MEV, and other complex attacks that take advantage of ecosystem
> features or tokenomics.**

**Full text, Implement as Documented:**
> The Tested code MUST behave as described in the documentation provided
> for [Q] Document Contract Logic, and [Q] Document System Architecture.
> ...it is also crucial that the Tested Code actually behaves as
> documented. **If it does not, it is possible that this reflects
> insufficient care and that the code is also vulnerable due to bugs
> that were missed in implementation.** It is also possible that the
> difference is an attempt to hide malicious code.

**Current RTF representation:**
- Both routed through the generic `_DOC_EVIDENCE_REQ_IDS` mechanism
  (`registry.py:174-199`): `collect_documentary_and_implementation_evidence`
  gathers README/NatSpec/docs text, no verdict, purely evidence
  collection.
- Track A's L7 rubric (`req-3-implement-as-documented.json`) frames the
  check as "compare documented claims to implementation," which is a
  correct reading of the requirement's literal text — but the rubric was
  **never executed**; the live pipeline doesn't build a
  `claims_vs_implementation` structure at all, it hands the raw
  normative sentence + generically-collected evidence straight to one
  Codex investigation, same one-candidate-location collapse as above.
- Corpus `normative_text` drops the explanatory sentence entirely — the
  key interpretive clue that a doc/code mismatch is a **proxy signal for
  a real implementation bug**, not an end in itself, never reaches the
  investigating agent.

**Information lost:**
This is the single most consequential loss in the whole set. The spec's
own text says the true target of "Implement as Documented" is *whether
the code has bugs that cause it to diverge from its own intended
protocol behavior* — documentation is the evidentiary anchor, not the
subject matter. A narrow "diff the README against the code" reading (the
literal rubric text) misses everything the explanatory sentence actually
points at: systematic verification that the contract's real state
machine matches its own documented/intended invariants — which, for an
undocumented or thinly-documented repo (the EVMbench norm), collapses
this requirement to near-uselessness, because "compare X to
documentation" has nothing to compare against once documentation is
thin. The spec's own words suggest the requirement should degrade
gracefully to "does the implementation match its own INTERNALLY
consistent, inferable design intent" (NatSpec `@dev`/`@notice` per
function, variable/function naming, the shape of access-control roles,
event emissions implying state invariants) rather than collapsing to
`INSUFFICIENT_EVIDENCE` whenever no prose doc exists.

**Proposed correction:** Treat "Document Contract Logic" +
"Implement as Documented" together as licensing a **derived
functional-correctness property per public/external function**: "does
this function's actual behavior match what its own signature, NatSpec,
event emissions, and surrounding code's naming/structure claim it does,"
generating one scoped investigation per function-with-nontrivial-state-effect
rather than one whole-repo doc-diff. This is directly justified by the
"insufficient care...bugs missed in implementation" sentence — the spec
itself says the real target is implementation bugs, evidenced through
(not limited to) documentation gaps.

---

## 3. `[M] Document Special Code Use` (`req-2-documented`)

**Full normative text (spec):**
> Tested Code MUST document the need for each instance of: CREATE2,
> assembly{}, selfdestruct()/suicide(), external calls, delegatecall(),
> code that can cause an overflow or underflow, block.number or
> block.timestamp, or use of oracles and pseudo-randomness, **and MUST
> describe how the Tested Code protects against misuse or errors in
> these cases, and the documentation MUST be available to anyone who can
> call the Tested Code.**

**Current RTF representation — a genuine extraction bug, not just a
narrowing:** the corpus's stored `normative_text` for `req-2-documented`
(`rtf/l1_corpus/requirement_corpus.json`) reads:

> "...or Use of oracles and pseudo-randomness,"

and **stops there, mid-sentence, on a trailing comma.** The two
downstream obligations — "MUST describe how the Tested Code protects
against misuse" and "documentation MUST be available to anyone who can
call the Tested Code" — are **not present anywhere in the stored
normative text**, not truncated-but-summarized, genuinely absent. This
is a parser/extraction defect in the original L1 corpus build
(`rtf/l1_corpus/parse_spec.py`), independent of any interpretation
choice downstream.
- Predicate (`find_documented_trigger_sites`, `predicates.py:678-704`):
  composes 7 existing trigger-presence predicates (CREATE2 usage,
  assembly usage, selfdestruct, external calls, delegatecall,
  unprotected arithmetic, block-data reads). This detects **use of the
  triggers themselves**, not documentation of them — a mechanism
  detector standing in for a documentation-completeness check, which the
  predicate's own docstring is honest about (it produces evidence for
  Codex to judge documentation against, not a documentation verdict
  itself).

**Information lost:** two full normative obligations (describe
protection measures; ensure documentation is caller-visible) are
missing from the corpus text a downstream investigation would ever see.
This is worth flagging distinctly from the "narrow instantiation"
pattern in the other rows — it's a straightforward text-fidelity bug in
L1 corpus extraction, independently fixable and independently
verifiable against the raw HTML without any EVMbench involvement.

**Proposed correction:** Re-run/patch the L1 extraction for this
req_id specifically (and audit `parse_spec.py` for whether other
requirements have the same truncation-on-enumeration-list pattern — any
requirement whose normative text ends in a bare comma after an
enumerated list is a candidate). This is a Phase-1-only, corpus-text-fidelity
fix; it does not by itself require the property-derivation architecture
change, though the resulting fuller text should also feed
the same property-derivation stage as other rows once built.

---

## 4. `[M] Don't Misuse Block Data` (`req-2-block-data-misuse`)

**Full text:**
> Block numbers and timestamps used in Tested Code MUST NOT introduce
> vulnerabilities to MEV or similar attacks. Block numbers are
> vulnerable to approximate prediction... block.timestamp is subject to
> manipulation... It is therefore important that these data are not
> trusted... to function as if they were highly reliable or random
> information. [cites SWC-116, gives concrete example:] using
> `block.number / 14` as a proxy for elapsed seconds, or relying on
> `block.timestamp` to indicate a precise time has passed. For
> probabilistic low-precision use ("about half an hour has passed") [an
> expression using block data may be acceptable].

**Current RTF representation:** `find_block_data_usage` — deliberately
over-inclusive per its own docstring: flags **any** read of
`block.timestamp`/`now`/`block.number`/`block.prevrandao`/`block.difficulty`,
regardless of how the value is used. Correctly notes the semantic
condition (is this specific usage precision-sensitive/security-critical
vs. a tolerant approximate use) is not attempted by the predicate,
deferred to the agent. One investigation collapses to the single
top-ranked read site.

**Information lost:** the spec gives a genuinely useful discriminating
test — "is this a precision-sensitive or probabilistic-tolerant use" —
directly in its own text (the `block.number / 14` example vs. the
"about half an hour" counter-example), but this discriminator never
reaches the prompt (corpus `normative_text` for this req_id is actually
reasonably complete, but the L2 bundle strips the elaboration/examples,
same pattern as row 1). With N block-data-read sites in a contract, only
the top-ranked one gets investigated.

**Proposed correction:** Same multi-instance-expansion treatment as row
1 (one investigation per distinct block-data-read site, not just the
top-ranked), plus carry the spec's own worked example
(`block.number / 14`) into the prompt as a concrete anchor for what
"vulnerable" precision-sensitive usage looks like.

---

## 5. `[M] Proper Signature Verification` (`req-2-signature-verification`)

**Full text:**
> Tested Code MUST properly verify signatures to ensure authenticity of
> messages that were signed off-chain... Using `ecrecover()` for
> signature verification, **it is important to validate the address
> returned against the expected outcome. In particular, a return value
> of `address(0)` represents a failure to provide a valid signature.**
> See also SWC-122. For code using `ecrecover()` and a Solidity compiler
> version older than 0.4.14, see [M] Use a Modern Compiler.

**Current RTF representation:** two predicates —
`find_ecrecover_usage` and `find_unchecked_ecrecover_result`
(`registry.py:98-100`) — these correctly, mechanically target the exact
concrete failure mode the spec's own text calls out (`address(0)` return
not checked). This is one of the **better**-instantiated M-level
requirements: the spec gives a specific mechanism, RTF has a specific
predicate for that exact mechanism, not a generic collapse. Still subject
to the same single-top-candidate collapse if multiple `ecrecover()` call
sites exist in one contract.

**Information lost:** minimal on substance; the only loss is the
same multi-instance collapse (row 1's pattern) if a contract has more
than one `ecrecover()` call site — SWC-122's own broader framing
(signature replay, missing nonce/domain separation) is cited but not
independently checked beyond the `address(0)` mechanism; `malleable-signatures-for-replay`
is a separate registered requirement covering some of that adjacent
ground, so this is not a pure gap, just worth noting as a boundary.

**Proposed correction:** Lower priority than rows 1-3; apply the
multi-instance-expansion fix generically (Phase 3) rather than as a
special case for this requirement.

---

## 6. `[M] Ensure Proper Rounding of Computations Affecting Value` (`req-2-check-rounding`)

**Full text:**
> Tested code MUST identify and protect against exploiting rounding
> errors: the possible range of error introduced by such rounding MUST
> be documented. Tested code MUST NOT unintentionally create or lose
> value through rounding. Tested code MUST apply rounding in a way that
> does not allow round-trips "creating" value to repeat causing
> unexpectedly large transfers. [explains: integer arithmetic over real
> numbers necessarily introduces rounding; if a round-trip creates a
> predictable, repeatable gain, that's exploitable.]

**Current RTF representation:** `find_division_in_value_context` — any
`DIVISION` binary IR op, deliberately broad, explicitly deferring the
semantic question ("is this specific division value-affecting and is its
rounding exploitable/repeatable") to the agent. This is actually a
**reasonably faithful narrow-but-correct** trigger — division is
genuinely the only operator introducing rounding — but the requirement's
THIRD obligation ("round-trips... causing unexpectedly large transfers")
names a specific, checkable **property class** (repeated
deposit/withdraw or mint/burn round-trips that compound a rounding
favor) that the single generic prompt never surfaces as a distinct
thing to look for — it's flattened into the same one-line normative
text as the other two obligations.

**Information lost:** the round-trip/repeatability sub-property (the
requirement's most concretely exploitable clause, and the one closest to
real-world rounding CVEs — e.g. repeated small deposits gaming a
share-price rounding direction) is present in the corpus text but not
elevated into its own investigation question; it competes for attention
with two more general obligations in one flat sentence.

**Proposed correction:** Split multi-clause MUST-statements (this
requirement has 3 distinct MUST/MUST NOT obligations in one normative
block) into separate derived properties at the property-derivation stage
(Phase 2), rather than treating "normative_text" as one atomic unit —
directly justified by the spec's own sentence structure, not invented.

---

## 7. `[Q] Use TimeLock Delays for Sensitive Operations` (`req-3-timelock-for-privileged-actions`)

**Full text:**
> Sensitive operations that affect all or a majority of users MUST use
> [TimeLock] delays. Sensitive operations, such as Smart Contract
> upgrades and [RBAC] changes, impact all or a majority of users in the
> protocol. A TimeLock delay allows users to exit the system if they
> disagree with the proposed change, and allows developers to react if
> they detect a suspicious change.

**Current RTF representation:** routed through the generic
`_DOC_EVIDENCE_REQ_IDS` documentary-evidence collector (same mechanism
as row 2), one whole-repo investigation. The requirement itself already
names its own two concrete example categories — upgrades, RBAC/role
changes — directly in its explanatory text.

**Information lost:** "sensitive operation" is never decomposed into
the concrete, repo-discoverable candidate set the spec's own examples
imply: `Ownable`/`AccessControl` role-grant functions, proxy
`upgradeTo`/`upgradeToAndCall` functions, and any function gated by an
admin/owner modifier that changes protocol-wide parameters (fee rates,
oracle addresses, pausability). One generic investigation, not one
scoped check per privileged/state-changing admin function found in the
repo's own access-control structure.

**Proposed correction:** Candidate generation should scan for exactly
the two named categories from the spec's own text (upgrade functions,
role/permission-changing functions) — this is directly grounded in the
requirement's explanatory prose, not invented from a benchmark case —
and generate one scoped investigation per discovered privileged
function, checking specifically for the presence/absence of a delay
mechanism gating that function's execution.

---

## 8. `[GP] Use Formal Verification` (`req-R-formal-verification`)

**Full text:** `SHOULD` undergo formal verification; broad framing
(liveness, protocol invariants, narrower specific properties); several
sentences on tooling and purpose.

**Current RTF representation:** `find_formal_verification_evidence`
(repo-root/source-path scan, presumably for tool config files —
Certora `.conf`, Halmos/Foundry invariant test naming conventions, etc.),
classified `DETERMINISTIC_COMPLETE` — i.e. **no agent investigation at
all**, purely a file-presence check.

**Information lost:** minimal, and arguably *correctly* scoped — `SHOULD`
(not `MUST`) plus "has this repo actually undergone formal verification"
is a genuinely binary, evidence-presence question the spec's own
phrasing supports treating deterministically (either FV artifacts exist
in-repo or they don't). Flagged here for completeness, not as a finding
requiring correction — this is an example of the *current* architecture
getting the grain right, useful as a positive control against
over-correcting everything to "needs property derivation."

---

## Cross-cutting pattern (established from the 8 requirements above, before any EVMbench comparison)

| Failure mode | Which rows exhibit it | Root architectural cause |
|---|---|---|
| Explanatory/interpretive text dropped between raw spec and L2 bundle/prompt | 1, 2, 4, 6, 7 | `codex_bridge.build_codex_prompt_inputs` uses corpus `normative_text` only; L2 bundle assembly (`rtf/l2_context_bundles/`) captures definitions/references/parent-section but not the requirement's own surrounding explanatory prose |
| Multi-clause normative text treated as one atomic property | 1, 3 (bug), 6 | No property-derivation step exists between "requirement" and "prompt" — `build_codex_prompt_inputs` forwards the whole `normative_text` string verbatim |
| Rich per-site predicate evidence collapsed to exactly one investigated location | 1, 4, 5, 7 (all AGENT_REQUIRED reqs) | `pipeline_e2e.py`'s escalation loop: `candidate_location = ranked[0].item.location if ranked else ""` — top-1 only, structurally, for every AGENT_REQUIRED requirement, regardless of how many distinct sites the predicate actually found |
| Requirement's own named example categories not used to drive candidate discovery | 7, partially 2 | Candidate discovery is generic evidence-ranking (analyzer-detector-driven), not requirement-text-driven; a requirement whose text names concrete example categories (upgrade functions, RBAC changes) has no mechanism to turn those named categories into a repo-structure scan |
| Genuine text-extraction bug (not an interpretation choice) | 3 | `rtf/l1_corpus/parse_spec.py` truncated a multi-clause sentence at an internal comma |

**Two structurally distinct problems are visible, and they need different
fixes:**
1. **A information-loss problem** (rows 1, 2, 4, 6, 7): the full
   requirement text and its own worked examples exist in the spec and
   are recoverable, but get flattened/dropped before reaching the
   investigating agent. Fix: carry fuller text through, and split
   multi-clause requirements into distinct derived properties (Phase 2).
2. **An instantiation/coverage problem** (rows 1, 4, 5, 7 — really,
   structurally, every AGENT_REQUIRED requirement): even with perfect
   text, one requirement currently produces exactly one investigation at
   exactly one location, when the requirement's own scope (every
   function, every block-data read site, every privileged function)
   implies many. Fix: requirement → many scoped investigation instances,
   with combinatorial controls (Phase 3).

Row 3 is a distinct, narrower, independently-fixable bug (L1 extraction
fidelity), not evidence for either architectural claim above.

**Preliminary answer to the user's closing question** (subject to the
Section 9 rule — this is provisional until the synthetic tests and
regression in later phases confirm it, not asserted as final here):
the evidence in this document supports **RTF_TRANSLATION_GAP /
RTF_INSTANTIATION_GAP** as the dominant pattern for the broad Level-Q
functional-correctness requirements specifically (rows 1, 2), not
**TRUE_ETH_TRUST_GAP** — EthTrust's own text is richer and more specific
than what currently reaches the investigating agent, and the
requirement→investigation cardinality is fixed at 1:1 by
`pipeline_e2e.py`'s escalation-loop structure regardless of how broad
the requirement's actual scope is.

---
*Produced entirely from `standards/ethtrust/ethtrust-sl.raw.html`,
`rtf/l1_corpus/requirement_corpus.json`, `rtf/l2_context_bundles/`,
`rtf/l12_evaluation/registry.py`, `rtf/l12_evaluation/codex_bridge.py`,
`rtf/l12_evaluation/pipeline_e2e.py`, and `rtf/l5_predicates/predicates.py`.
EVMbench was not read or referenced while building any row above.*
