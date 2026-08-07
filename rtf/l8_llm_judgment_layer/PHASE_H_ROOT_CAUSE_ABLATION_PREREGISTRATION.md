# Root-cause investigation: ablation pre-registration

Written and frozen BEFORE any ablation call in this batch is made. All
ablations are single-variable changes from an exact, already-observed
real baseline (the post-fix Phase H stability-experiment prompts/results,
`phase_h_stability_artifacts/results_post_fix.json`). Single-pass calls
only (`use_second_pass=False`) — this investigation is about the
input-to-first-decision relationship, not first/second-pass stability,
which was already measured separately in Phase H items 6-7. Model fixed
to `openai/gpt-5.1-codex-max` throughout (the model under investigation).
Every call logs exact prompt, config, response, cost, and an input hash.

## Free analysis performed before any new call (zero cost)

Reconstructing the exact prompts for cases 1/2/3/4/8 via
`build_ranked_judgment_question` (deterministic, no API cost) and reading
the saved `reasoning_summary`/`open_questions` for all 7 relevant cases
already surfaced concrete, textually-grounded candidate causes, not
vague ones:

- **Case 1 vs case 3 bundles are template-identical** (same fields, same
  hedge phrasing pattern: "Missing/uncertain protections", "Possible
  failure mechanism"). The divergence (case 1 → confident FAIL; case 3 →
  INSUFFICIENT_EVIDENCE) is NOT explained by evidence-rendering
  differences between these two cases specifically.
- **Case 2's stated blocker is explicit and specific**, not vague: "the
  requirement covers validation of ALL INPUTS ... there is no broader
  information about OTHER inputs or functions" — a stated
  requirement-scope-vs.-evidence-scope objection (candidate H8), not a
  request for more source code (candidate H1 not supported by the
  model's own words here).
- **Case 4's stated blocker is also specific**: "no information about
  HOW the recovered address is compared to an expected signer or
  whether the signed message is correctly constructed" — again H8/H7
  (the evidence proves one necessary sub-condition of "properly verify
  signatures," not all of them), not a generic hedge.
- **Case 8's stated blocker treats multiple candidate locations as an
  undifferentiated pool** ("the evidence is phrased as missing/uncertain
  protections and does not include code context") even though the
  identical `Vault._burn` claim, alone, was trusted for a confident FAIL
  in case 7.
- **The judgment prompt's closing instruction sentence is asymmetric**:
  it only tells the model how to treat "violations" ("your job is to
  judge whether each specific listed location is a GENUINE violation")
  — it never states an analogous instruction for concluding PASS from
  evidence that shows adequate protection. Candidate H5.
- **req-2-signature-verification's own normative text uses open-ended
  qualitative language** ("MUST **properly** verify signatures to
  **ensure authenticity**") vs. req-3-all-valid-inputs's flatter, more
  operationally crisp text ("MUST validate inputs"). Candidate
  requirement-wording sensitivity (H8-adjacent).
- Case 3's evidence ALREADY states the relevant domain fact ("a
  malformed/invalid signature makes ecrecover return address(0)")
  explicitly in its `risk` field — **H9 (model must supply its own
  domain knowledge) is therefore NOT applicable to case 3 and is ruled
  out by inspection**, not tested live.

## The 10 pre-registered ablations

Each row: exact single change from the real baseline prompt, the
hypothesis it discriminates, and the PREDICTED outcome under that
hypothesis (stated before running, so a null result is recorded as a
null result, not reinterpreted after the fact).

| # | Base case | Change (single variable) | Hypothesis tested | Predicted outcome if hypothesis TRUE |
|---|---|---|---|---|
| AB1 | 2 (safe cast) | Append an explicit PASS-permission sentence to the closing instruction: "If the evidence at a specific location shows the relevant construct is adequately protected, and no evidence in this bundle set suggests a problem there or elsewhere, you may treat that location as conforming for the aspects covered by this evidence." Nothing else changes. | H5 (prompt closing-instruction asymmetry blocks PASS specifically) | Flips to PASS |
| AB2 | 2 (safe cast) | Change ONLY the final question sentence from "does the Tested Code conform to the requirement?" to "does the input handling AT THIS SPECIFIC LOCATION (Ledger.record) conform to the requirement?" Original closing instruction unchanged. | H8 (codebase-wide question framing vs. evidence's inherently local scope) | Flips to PASS |
| AB3 | 4 (checked ecrecover) | Same PASS-permission sentence as AB1, appended. Nothing else changes. | H5, tested on a second, independent case | Flips to PASS |
| AB4 | 4 (checked ecrecover) | Add ONE new structured field to the SAME bundle: `"validation_found"` extended to state the recovered signer IS ALSO compared to an expected stored value ("... ; require(signer == authorizedSigner, \"unauthorized\") immediately follows"). This directly supplies the specific missing sub-condition case 4's own reasoning named. Original question/instructions unchanged. | H7 (evidence structurally cannot prove "properly verified" without this sub-condition — a genuine evidence-model gap, not model hedging) | Flips to PASS |
| AB5 | 3 (unchecked ecrecover) | Add a 4-line literal source excerpt matching the predicate's claim exactly (`function verify(...) { address signer = ecrecover(...); return signer == authorizedSigner; }` — no zero-check, consistent with the structured evidence). Nothing else changes. | H1 (model doesn't trust a bare structured claim for ecrecover specifically without seeing code) | Flips to FAIL |
| AB6 | 3 (unchecked ecrecover) | Replace ONLY the presented requirement text from the real, verbatim req-2 text ("MUST properly verify signatures to ensure authenticity") with a flatter, operationally-scoped restatement ("MUST check that a recovered ecrecover() result is not the zero address before using it as a signer"). Diagnostic-only substitution — NOT a change to the frozen L1 corpus. Evidence/instructions unchanged. | Requirement-wording sensitivity (H8-adjacent): open-ended qualitative language ("properly", "ensure authenticity") invites more caution than an operationally flat statement | Flips to FAIL |
| AB7 | 8 (PoolTogether, 30 bundles) | Same 30 bundles, budget reduced to top 3 (`Vault._burn`/`_mint`/`_transfer` — the real top-3-ranked real items). | H2 (evidence volume) | Records raw decision; no directional prediction stated (exploratory point on the volume curve) |
| AB8 | 8 | Same, budget reduced to top 5. | H2 | Same as AB7 |
| AB9 | 8 | Same, budget reduced to top 10. | H2 | Same as AB7 |
| AB10 | 8 (full 30 bundles, unmodified evidence) | Same PASS/FAIL-permission closing-instruction addition as AB1/AB3, reworded for the FAIL direction: "...if the evidence for a specific location shows the relevant construct is NOT protected, and no evidence in this bundle set suggests a compensating protection, you may treat that location as non-conforming for the aspects covered by this evidence." Evidence set (all 30 bundles) unchanged. | H5, tested on the dilution case specifically — does the SAME instruction fix also unlock case 8 back to FAIL, suggesting one unifying cause across cases 2/4/8? | Flips to FAIL |

## Explicitly NOT tested live in this pass (and why)

- **H3 (irrelevant vs. token-matched neutral padding), H4 (ordering)**:
  case 8 already places the relevant bundle FIRST (rank #1) among 30,
  so ordering alone cannot explain its hedge — deprioritized in favor of
  AB7-AB9's volume curve, which is more directly diagnostic given this
  fact. If AB7-AB9 show a clean volume threshold, H3/H4 become natural
  follow-ups; if they don't, H3/H4 are unlikely to be the story either
  (competing/positional effects would be expected to show up as part of
  the same volume curve).
- **H9 (domain-knowledge dependency)**: ruled out by inspection for case
  3 (the domain fact is already present in the evidence's `risk` field)
  without spending a live call.
- **H10 (second-pass design)**: explicitly deferred per the task's own
  instruction ("only after primary root causes are understood").
- **H6 (schema field-name wording) as an isolated single-field test**:
  not run as its own separate ablation in this batch — the closing-
  instruction ablations (AB1/AB3/AB10) are a more direct test of the
  "the prompt discourages confident conclusions" family of hypotheses,
  and are prioritized within the economical budget available. If those
  ablations show partial-but-incomplete effects, a dedicated field-
  rename test is the natural next step (documented under "Unresolved
  questions" in the final report if not run here).

## Budget

10 single-pass calls, `openai/gpt-5.1-codex-max`, similar prompt sizes
to the already-measured Phase H calls (~$0.006-0.012/call observed for
single calls of this size) → estimated $0.06-0.12 total. Checked against
the real, cumulative session log before/after every call via
`spend_guard.py` (cap $5.00, stop-new-calls threshold $4.00). Session
spend before this batch: $0.471.

## Phase 6 causal-minimization follow-ups (pre-registered after AB1-AB10, before running)

AB5/AB6 produced an unanticipated but important result: adding a literal
source excerpt to case 3 did NOT flip it to FAIL, and inspection of the
reasoning showed why -- the model raised a NEW, logically sound
objection: the missing-zero-check's actual impact is CONDITIONAL on
whether `authorizedSigner` (the value compared against) could itself
ever be the zero address. This exact conditional dependency was already
implicit in the original (pre-ablation) case 3 evidence's own hedged
`risk` text ("...could be compared equal to an actual authorizedSigner
of address(0)...") and in its original open_questions ("Is address(0)
ever considered an authorized signer in this contract?"). Two follow-up
ablations, single-variable, pre-registered before running:

| # | Base case | Change | Hypothesis | Predicted outcome if hypothesis TRUE |
|---|---|---|---|---|
| AB11 | 8 (PoolTogether, 30 bundles) | Budget = top 20 (bisecting the 10-30 boundary AB7-AB9 established: top-10 -> FAIL, top-30 -> INSUFFICIENT_EVIDENCE) | Narrows the volume threshold for the dilution effect (H2) | Exploratory -- no directional prediction; records which side of 20 the transition falls on |
| AB12 | 3 (unchecked ecrecover), starting from AB5's source-excerpt version | Add ONE explicit sentence supplying the specific missing fact AB5's own reasoning identified: "`authorizedSigner` is a stored address, set exactly once during construction to a known non-zero address, and is never reset to zero anywhere in the contract." | H7-refined: the TRUE minimal causal feature for case 3 is this specific conditional fact, not source code in general (which AB5 already showed is insufficient alone) | Flips to FAIL |

## Cross-case unification test (pre-registered after AB11/AB12, before running)

AB2/AB4 established that a location-scoped question (vs. target-wide
"does the Tested Code conform") flips cases 2/4 to correct decisions.
AB10 already falsified an INSTRUCTION-permission fix for case 8's
volume-based hedge. One further, decisive test distinguishes whether
case 8 shares cases 2/4's root cause (question-scope framing) or is
truly independent:

| # | Base case | Change | Hypothesis | Predicted outcome if hypothesis TRUE |
|---|---|---|---|---|
| AB13 | 8 (PoolTogether, full 30 bundles, unmodified evidence) | Change ONLY the final question sentence to location-scoped framing, mirroring AB2 exactly: "does the input handling AT THE Vault._burn LOCATION conform to the requirement?" instead of "does the Tested Code conform to the requirement?" Evidence set (all 30 bundles) unchanged. | Cases 2/4 and case 8 share ONE root cause (question-scope framing), not two independent ones | Flips to FAIL |

If this flips to FAIL: cases 2, 4, and 8 share one deepest root cause
(target-wide question framing vs. location-scoped evidence). If it does
NOT flip: case 8's volume effect is causally independent of cases 2/4's
scope-framing effect, and the report must keep them as separate root
causes (as the pre-registration above already treats them provisionally).
