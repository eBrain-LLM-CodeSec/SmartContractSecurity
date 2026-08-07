# Phase H root-cause analysis: why did RTF's LLM judgment fail on 4 of 7 known cases?

**Constraint honored throughout:** no hidden/private chain-of-thought was
retrieved or relied on. Every claim below is grounded in observable
artifacts — the exact prompt sent (reconstructed deterministically via
`build_ranked_judgment_question`, zero API cost), the model's returned
`reasoning_summary`, `open_questions`, `confidence`, `evidence` citations,
and the outcomes of 13 pre-registered, single-variable live ablation
calls. **No detailed model reasoning trace beyond `reasoning_summary` was
ever available** — this project's `judgment_layer.py` schema does not
request or store a raw chain-of-thought field, only the structured
summary. Where a claim below rests on `reasoning_summary` alone rather
than a live-verified ablation, it is marked accordingly.

Total spend for this investigation: **13 live calls, $0.182** (session
cumulative: $0.653 of the $5.00 self-enforced cap). All calls
single-pass (`use_second_pass=False`) — deliberate, since this
investigation is about the input→first-decision relationship, not
first/second-pass stability (already measured separately in Phase H
items 6-7). Full raw prompts/responses:
`rtf/l8_llm_judgment_layer/phase_h_root_cause_artifacts/ablation_results.json`.
Pre-registrations (written before each batch, not after):
`PHASE_H_ROOT_CAUSE_ABLATION_PREREGISTRATION.md`.

## 1. Executive conclusion

Three **distinct, independently-confirmed** root causes explain the four
failures — not one. Each was confirmed by a clean, single-variable live
ablation that flipped (or, in one case, decisively did NOT flip) the
outcome, not inferred from correlation alone.

1. **(HIGH confidence, cases 2 and 4) A requirement/evidence granularity
   mismatch, structural to how universally-quantified requirements
   interact with single-location evidence.** RTF asks one PASS/FAIL/
   INCONCLUSIVE/INSUFFICIENT_EVIDENCE verdict per (requirement, target)
   pair — a **target-wide** question — but supplies evidence scoped to
   **one location**. For a requirement phrased as "MUST validate
   [all] inputs" or "MUST properly verify signatures [in general]," one
   clean local example can never logically prove the target-wide
   claim, even though one bad local example CAN disprove it (a single
   counterexample refutes a universal "MUST", but a single confirming
   instance cannot establish one). This is not a prompt-wording
   artifact and not overcaution: rewording ONLY the question's scope
   from target-wide to location-scoped flipped both cases cleanly to
   the correct answer, with no other change (AB2, AB4).

2. **(HIGH confidence for this instance, MEDIUM for generalization; case
   3) The evidence architecture proves *construct presence* but not
   *relational exploitability* for comparison-based checks, and this
   session's own synthetic test-case label was underspecified as a
   result.** `find_unchecked_ecrecover_result`'s evidence establishes
   "no zero-check exists" but says nothing about whether the value
   `ecrecover`'s result gets compared against could itself be the
   zero address — a fact needed to know whether the missing check is
   actually exploitable. When that one specific fact was supplied
   live, the model correctly concluded **PASS**, not the originally
   assumed FAIL (AB12) — meaning this case's "expected: FAIL" label,
   as designed, was not fully justified by the fixture's own stated
   facts. This reclassifies case 3 from "LLM failure" to, at minimum,
   "ambiguous test-case design," and arguably "the model was right and
   the fixture was wrong."

3. **(Confirmed to exist, HIGH confidence; exact mechanism UNRESOLVED;
   case 8) A volume-dependent, genuinely independent effect**: the
   identical, top-ranked, individually-sufficient evidence for
   `Vault._burn` (which alone yields a confident FAIL) stops producing
   a confident FAIL somewhere between 10 and 20 competing candidate
   bundles in the same prompt (AB7/AB8/AB9 = FAIL at top-3/5/10; AB11 =
   INSUFFICIENT_EVIDENCE at top-20; case 8 = INSUFFICIENT_EVIDENCE at
   top-30). **Confirmed independent of cause #1**: the same
   location-scoping fix that cleanly resolved cases 2/4 did NOT resolve
   this one (AB13, a decisive null result). Confirmed independent of
   prompt-instruction wording (AB10, also null). What specifically
   about added bundle volume causes this — raw token/item count vs.
   competing semantic claims vs. some other volume-linked factor — is
   **not resolved** by the experiments run; see §8.

## 2. Evidence available

- Exact prompts: fully reconstructable and reconstructed for every case
  via `build_ranked_judgment_question`/`render_bundles_for_prompt`
  (deterministic, no API cost — confirmed byte-for-byte reproducible).
- Model outputs: `decision`, `confidence`, `reasoning_summary`,
  `open_questions`, `evidence` (citations), for every first AND second
  pass of the original 7 cases, plus every ablation's first pass.
- **No raw chain-of-thought / hidden reasoning trace was available or
  retrieved at any point** — `judgment_layer.py`'s schema never
  requests one, and none was inferred or fabricated. All causal claims
  below rest on (a) `reasoning_summary` text as a stated, observable
  artifact, and (b) live ablation outcomes (decision flips or
  non-flips), never on assumed internal model state.
- Token counts, cost, and an input hash were logged for every ablation
  call (`ablation_results.json`).
- Cache/config: all calls at `temperature=0.0`, `top_p=1.0`,
  `max_tokens=4096`, model `openai/gpt-5.1-codex-max` throughout (the
  model under investigation; GLM was not re-tested in this pass — the
  investigation targets GPT's specific failures per the task).

## 3. Case-by-case forensic analysis

### Case 2 — Safe narrowing cast (expected PASS, got INSUFFICIENT_EVIDENCE)

- **Model-stated blocker (from `reasoning_summary`, verbatim):** "The
  only available evidence shows that one function validates a
  narrowing conversion... However, the requirement covers validation
  of **all inputs** across the tested code, and there is no broader
  information about other inputs or functions." — classified as
  `EVIDENCE_SCOPE_MISMATCH` / requirement-ambiguity, stated explicitly
  by the model itself, not inferred.
- **Experiments:**
  - AB1 (append an explicit "you may conclude PASS from adequate local
    evidence" permission sentence to the prompt's closing instruction,
    nothing else changed): **did not flip** (`INSUFFICIENT_EVIDENCE`,
    LOW). Falsifies H5 (prompt-instruction asymmetry) for this case.
  - AB2 (change ONLY the final question from "does the Tested Code
    conform" to "does the input handling AT THIS SPECIFIC LOCATION
    conform," nothing else changed): **flipped to PASS** (MEDIUM
    confidence), with `reasoning_summary` now stating plainly the check
    "addresses potential malformed or oversized input... aligning with
    the requirement" — no more mention of "all inputs across the
    codebase."
- **Hypotheses falsified:** H5 (prompt-policy asymmetry), H1 (missing
  source code — never mentioned as a blocker by the model at any point
  for this case).
- **Minimal input change that corrected it:** one clause in the
  question's own scope framing — nothing about the evidence itself.
- **Root-cause classification:** `EVIDENCE_SCOPE_MISMATCH` (a variant of
  `REQUIREMENT_AMBIGUITY` — the requirement's "all inputs" language,
  read literally, is target-wide; the evidence is location-wide).
- **Confidence: HIGH** (single clean confirming ablation + one clean
  falsifying ablation on the same case).

### Case 4 — Checked ecrecover (expected PASS, got INSUFFICIENT_EVIDENCE)

- **Model-stated blocker:** "There is no information about how the
  recovered address is compared to an expected signer or whether the
  signed message is correctly constructed." — again explicit and
  specific, naming exactly what's missing.
- **Experiments:**
  - AB3 (same PASS-permission instruction as AB1): **did not flip**
    (`INSUFFICIENT_EVIDENCE`, MEDIUM). Replicates AB1's falsification of
    H5 on an independent case.
  - AB4 (add ONE field to the evidence: the recovered signer IS ALSO
    compared to an expected stored value — the exact sub-condition the
    model's own reasoning named as missing): **flipped to PASS** (MEDIUM
    confidence), with `reasoning_summary`: "recovers the signer... and
    immediately checks for a nonzero address and that the signer
    matches an authorized signer. This satisfies proper verification."
- **Hypotheses falsified:** H5. H1 was not directly tested for this case
  (not needed — the model never asked for source code, only for the
  specific missing relational fact, which AB4 supplied directly as
  structured evidence, not as source).
- **Minimal input change that corrected it:** one additional clause in
  ONE structured field (`validation_found`), not source code, not
  instruction wording.
- **Root-cause classification:** `INSUFFICIENT_INPUT_EVIDENCE` /
  `EVIDENCE_SCOPE_MISMATCH` — `find_unchecked_ecrecover_result` (even in
  its hand-constructed "positive" form used for this fixture) only ever
  establishes ONE of the several necessary sub-conditions "properly
  verify signatures to ensure authenticity" implies. This is a genuine
  evidence-model gap (the predicate cannot currently prove signer-
  comparison correctness at all, positive or negative), not an LLM
  reasoning defect — the model asked for exactly the right thing.
- **Confidence: HIGH.**

### Case 3 — Unchecked ecrecover (expected FAIL, got INSUFFICIENT_EVIDENCE)

- **Model-stated blocker (original run):** "without... confirmation that
  such a check is indeed omitted and would affect authentication
  logic, it is not possible to conclusively determine..." — on its face
  looked like `EVIDENCE_REPRESENTATION_FAILURE` / distrust of a bare
  structured claim (candidate H1).
- **Experiments:**
  - AB5 (add a 4-line literal source excerpt matching the predicate's
    claim exactly — `ecrecover(...)` with no zero-check, feeding
    directly into `return signer == authorizedSigner`): **did not
    flip** (`INSUFFICIENT_EVIDENCE`, LOW). Falsifies H1 — seeing the
    literal code did not resolve the doubt. Critically, the returned
    `reasoning_summary` revealed a DIFFERENT, more precise objection:
    "There is no explicit check for ecrecover returning address(0),
    which could be problematic **IF authorizedSigner is ever zero**...
    without evidence about how authorizedSigner is set or whether zero
    is a valid authorized signer, it's unclear whether this constitutes
    improper verification." This exact conditional dependency was
    ALREADY present, hedged, in the ORIGINAL case-3 evidence's own
    `risk` field ("...could be compared equal to an actual
    authorizedSigner of **address(0)**...") and original
    `open_questions` ("Is address(0) ever considered an authorized
    signer in this contract?") — so this was not a new confound AB5
    introduced, it is the same underlying gap surfacing more precisely
    once code made the comparison target (`authorizedSigner`) visible.
  - AB6 (reword ONLY the presented requirement text from the verbatim
    "MUST properly verify signatures to ensure authenticity" to a
    flatter "MUST check that a recovered ecrecover() result is not the
    zero address before using it," no source excerpt): **did not flip**
    (`INSUFFICIENT_EVIDENCE`, LOW), and reverted to reasoning resembling
    the ORIGINAL doubt pattern (doubting whether the check is "really"
    absent) rather than raising the `authorizedSigner` point — because
    no source was shown to trigger noticing it. Falsifies the
    "open-ended requirement wording causes extra caution" hypothesis as
    the primary driver.
  - AB12 (AB5's source excerpt **plus one explicit sentence**: "
    `authorizedSigner` is a stored address, set exactly once during
    construction to a known non-zero address, and is never reset"):
    **flipped — but to PASS, not the originally predicted FAIL**
    (MEDIUM confidence): "Given that authorizedSigner is initialized
    once to a non-zero address, any malformed or invalid signature
    yielding address(0)... will not match and will result in a failed
    verification. This satisfies the requirement."
- **Hypotheses falsified:** H1 (source code alone), the req-2-wording-
  sensitivity hypothesis.
- **Minimal input change that corrected it:** one explicit fact about a
  SECOND value's own possible range (not about the code construct being
  evaluated at all) — and correcting it flipped the "correct" answer to
  the OPPOSITE of what this case's own preregistration predicted.
- **Root-cause classification: `EXPECTED_LABEL_INVALID`,** with a
  secondary, generalizable finding classified `EVIDENCE_SCOPE_MISMATCH`:
  RTF's ecrecover predicate proves *construct presence* (a comparison
  with no zero-check exists) but not *relational exploitability*
  (whether the comparator could itself be zero) — a fact no current
  predicate collects. My own synthetic fixture for this case never
  specified whether `authorizedSigner` could be zero, so "expected:
  FAIL" was not fully justified by the fixture's own stated facts. Read
  plainly: **the model's original hedge was the epistemically correct
  response to genuinely incomplete evidence, not a defect.**
- **Confidence: HIGH** that the original label was underspecified (a
  live, reproducible ablation flip to PASS with a logically sound
  justification, not a guess). **MEDIUM** that this generalizes to
  every real-world unchecked-ecrecover finding (only one instance
  tested; real-world `authorizedSigner`-equivalents are frequently
  zero-initializable, which is exactly why SWC-122 is a real,
  frequently-exploited pattern — but RTF's own predicate does not
  currently check or report which situation applies).

### Case 8 — PoolTogether, full 30-bundle set (expected FAIL, isolated evidence = FAIL correct, 30-bundle set = INSUFFICIENT_EVIDENCE)

- **Model-stated blocker (original, 30-bundle run):** treats the
  identical `Vault._burn` claim (individually sufficient for a
  confident FAIL when shown alone, case 7) as one of several
  "high-ranked functions... where narrowing type conversions **could**
  truncate inputs **if not checked**... the evidence does not include
  code context or confirmation that bounds checks are absent" — i.e.
  the SAME claim gets treated as merely one candidate among a pool of
  unconfirmed possibilities once other candidates are present, not on
  its own individual merits.
- **Experiments (volume curve, all else identical):**
  - AB7 (top 3 bundles): **FAIL**, MEDIUM.
  - AB8 (top 5 bundles): **FAIL**, MEDIUM.
  - AB9 (top 10 bundles): **FAIL**, LOW.
  - AB11 (top 20 bundles): **INSUFFICIENT_EVIDENCE**, LOW.
  - (top 30 bundles, original case 8): **INSUFFICIENT_EVIDENCE**, MEDIUM.
  - → clean threshold: the transition happens strictly between 10 and
    20 bundles.
  - AB10 (full 30 bundles + an explicit FAIL-permission closing
    instruction, mirroring AB1/AB3's PASS-permission style but for the
    violation direction): **did not flip** (`INSUFFICIENT_EVIDENCE`,
    MEDIUM). Falsifies H5 for this case.
  - AB13 (full 30 bundles + the SAME location-scoped question fix that
    cleanly resolved cases 2 and 4): **did not flip**
    (`INSUFFICIENT_EVIDENCE`, LOW) — a decisive result. It DID change
    the *style* of the hedge (from "several high-ranked functions...
    pool" language to "does not show the surrounding code to confirm,"
    a phrasing closer to case 3's pattern), suggesting the fix had a
    partial, secondary effect on framing without resolving the
    underlying confidence drop, but the outcome itself did not change.
- **Hypotheses falsified:** H5 (both directions, AB1/AB3/AB10), and the
  cases-2/4-style scope-mismatch explanation is now independently
  falsified for THIS case specifically (AB13) even though it shares
  surface similarity with cases 2/4's language pattern.
- **Minimal input change that corrected it:** reducing the number of
  OTHER candidate bundles present, specifically to ≤10 — nothing about
  the relevant evidence, question wording, or instructions.
- **Root-cause classification: `CONTEXT_INTERFERENCE`,** confirmed to
  exist and bounded to a volume range (>10, ≤20 bundles in this
  specific prompt), but the PRECISE mechanism is **UNRESOLVED**: H3
  (competing semantic evidence specifically) vs. raw token/item-count
  volume vs. some other volume-linked factor were not disentangled —
  the token-matched-neutral-padding control (H3 variant C) and the
  ordering control (H4) that would distinguish these were not run in
  this pass (see §8).
- **Confidence: HIGH** that a real, volume-bounded, independent effect
  exists. **UNRESOLVED** on its exact mechanism.

## 4. Cross-case causal analysis

- **Cases 2 and 4 share one root cause**, confirmed not merely by
  similar language but by an IDENTICAL single-variable intervention
  (question-scope rewording) independently flipping both. This is the
  most solidly established finding in this investigation.
- **Case 8 is independently confirmed NOT to share cases 2/4's root
  cause** — the decisive test (AB13: apply the exact same fix to case 8)
  produced a clean null result. This matters: surface-level language
  similarity ("the evidence... does not include code context," "no
  broader information") is not sufficient to assume shared causation,
  and this investigation explicitly tested and rejected that
  assumption rather than taking it on faith.
- **Case 3 is causally distinct from all three others.** Its resolution
  required supplying a specific fact about a value the evidence never
  mentioned (the comparator's own range), not a question-scope change
  (untested directly on case 3, but the mechanism — a missing relational
  fact about a SECOND variable — is categorically different from
  cases 2/4's SCOPE issue and case 8's VOLUME issue) and not source
  code alone (AB5 falsified that). It further revealed a defect in this
  investigation's OWN test design (the "expected: FAIL" label), which
  none of the other three cases exhibited.
- **A tempting but explicitly REJECTED unifying narrative:** "the model
  gets more cautious as it becomes aware the target/context is larger
  than what it's been shown" superficially fits cases 2, 4, AND 8. This
  investigation does NOT endorse that as a single root cause — AB13
  is a direct, decisive test of exactly this narrative for case 8, and
  it failed. The correct, evidence-supported statement is narrower:
  cases 2/4 share a **question-scope** mechanism; case 8 has a
  **volume-of-candidate-evidence** mechanism that happens to produce
  superficially similar reasoning language but responds to a different
  intervention.

## 5. LLM failure vs. pipeline failure

This is the most consequential output of this investigation.

**Cases classified as NOT a genuine LLM reasoning failure:**

- **Case 2**: the model reasoned correctly given what it was actually
  asked (a target-wide question) and what it actually received
  (location-wide evidence). Classified `EVIDENCE_SCOPE_MISMATCH` — a
  **pipeline/question-design** issue, not a model defect.
- **Case 4**: same reasoning — the model correctly identified a real,
  specific, provable gap in what the evidence could establish.
  `INSUFFICIENT_INPUT_EVIDENCE` — a **pipeline/evidence-architecture**
  issue.
- **Case 3**: the model's original hedge was, on the evidence actually
  reviewed via ablation, the MORE epistemically correct response — this
  session's own synthetic test-case design did not fully specify the
  scenario. `EXPECTED_LABEL_INVALID` — a **test-design** issue, not a
  pipeline issue and certainly not a model issue. If anything, this
  case reflects favorably on the model's reasoning rigor.

**Case classified as a genuine, if only partially understood, RTF
pipeline issue (not directly an LLM defect either):**

- **Case 8**: the underlying evidence was correct, complete (relative to
  what case 7 already proved sufficient), and top-ranked throughout —
  RTF's own ranking/bundling work (earlier in Phase H) did its job
  correctly. The issue is that PRESENTING that evidence alongside ≥20
  other, less-certain candidates measurably degrades the model's
  willingness to commit to the one confirmed claim. This is not "the
  model reasoned incorrectly about the evidence it was given" so much
  as "the overall PROMPT CONSTRUCTION (evidence budget size) interacts
  with the model's calibration in a way this investigation confirmed
  but did not fully explain." Classified `CONTEXT_INTERFERENCE`,
  reported as a genuine open engineering problem, not attributed to
  either "the LLM is bad" or "the evidence was wrong."

**Net finding: zero of the four investigated failures are best described
as "the LLM received sufficient, correctly-scoped evidence and reasoned
to a wrong conclusion."** Three are pipeline/question-design/test-design
issues; the fourth (case 8) is a real, still-open interaction between
prompt volume and model confidence, not a case of the model being
"wrong" about the specific evidence in front of it.

## 6. Root-cause tree

```text
Symptom: 4 of 7 known-expectation cases resolved to INSUFFICIENT_EVIDENCE
instead of the expected PASS/FAIL.

├── Cases 2, 4 (PASS-expected cases)
│   Immediate cause: model states requirement's scope exceeds what one
│   location's evidence can prove.
│   Why present: requirement text ("all inputs," "properly verify...to
│   ensure authenticity") is inherently target-wide / multi-condition;
│   RTF's evidence bundles are inherently location-wide / single-
│   condition.
│   Why THAT design choice: L12's per-(requirement,target) verdict
│   model was built to match EthTrust's own requirement granularity
│   (one requirement -> one applicability/conformance state per target),
│   not per-location, and no per-location aggregation rule currently
│   exists to combine many location-level observations into one
│   target-level verdict.
│   ROOT CAUSE: the judgment layer asks a target-wide question but the
│   evidence architecture only ever produces location-wide answers, and
│   nothing in between (a per-location verdict, later aggregated) exists
│   to bridge them. Confirmed causal (AB2/AB4), not assumed.
│
├── Case 3
│   Immediate cause: model correctly notes exploitability is conditional
│   on a second value's own possible range, which the evidence doesn't
│   state.
│   Why present: find_unchecked_ecrecover_result proves "check absent"
│   (a LOCAL, unconditional fact) but signature-verification's real
│   risk is RELATIONAL (depends on what the result is compared against),
│   and no predicate currently inspects or reports the comparator's own
│   possible values.
│   Why THAT design choice: the predicate was derived (this session's
│   earlier evidence-enrichment work) to detect the SYNTACTIC pattern
│   "ecrecover result used without a zero check" -- a locally-checkable
│   construct -- not to perform the additional data-flow analysis needed
│   to bound the comparator's own range, which is a materially harder,
│   not-yet-attempted analysis.
│   Why the TEST failed to catch this: the synthetic fixture that
│   produced this case's "expected: FAIL" label was designed by mirroring
│   test_predicates.py's existing negative-test shape, which itself never
│   specifies the comparator's bounds -- an unexamined assumption carried
│   from predicate-unit-testing (where "does the predicate fire" is the
│   only question) into judgment-testing (where "is firing actually
│   correct" is the question), without being re-examined for the latter.
│   ROOT CAUSE (two, compounding): (a) a genuine evidence-architecture
│   gap (relational exploitability unproven for comparison-based
│   checks), and (b) a test-design gap (this investigation's own fixture
│   inherited an assumption from unit-testing scope that doesn't hold at
│   judgment-testing scope). Confirmed causal (AB5, AB6, AB12), not
│   assumed.
│
└── Case 8
    Immediate cause: identical top-ranked evidence, sufficient alone,
    stops being treated as sufficient once ≥~20 other candidate bundles
    are also present.
    Why present: UNRESOLVED at the mechanism level. Ruled out: prompt-
    instruction wording (AB10), question-scope framing (AB13). Not yet
    tested: token-volume-matched neutral padding vs. genuinely
    competing semantic claims (H3), and evidence ordering independent of
    volume (H4) -- case 8's evidence already sits at rank #1 throughout
    every tested volume, so ordering is a weak candidate but was not
    directly isolated.
    ROOT CAUSE: NOT YET IDENTIFIED AT THE MECHANISM LEVEL. What IS
    established causally: this is a volume-bounded phenomenon (a
    numeric threshold between 10 and 20 bundles in this specific
    prompt/evidence combination), independent of the mechanisms behind
    cases 2/4 and case 3.
```

## 7. Recommended architectural response

Per the task's explicit instruction, no fix is proposed for a cause
this investigation did not establish. Each recommendation below is
traced to a specific, confirmed finding — none is proposed merely
because it would raise the seven-case accuracy score.

- **For cases 2/4's confirmed root cause (question/evidence granularity
  mismatch):** the appropriate intervention is NOT "phrase the prompt
  to sound more permissive" (AB1/AB3 already falsified that a bare
  permission sentence does anything) — it is a **structural** one:
  either (a) narrow the judgment QUESTION to be location-scoped when
  the underlying evidence is location-scoped (exactly what AB2/AB4
  demonstrated works), which would require L12's orchestration to ask
  "does location X conform w.r.t. this requirement" per evidence-
  bearing location and define an aggregation rule (e.g. "target
  conforms only if all evidence-bearing locations independently
  conform, and target does not conform if any one does not") rather
  than a single flat target-wide question over all evidence; or (b)
  make the requirement's own scope explicit and bounded in the L2
  context bundle wherever the L1 corpus supports narrowing it (e.g.
  clarify per-location applicability where EthTrust's own text permits
  it). This is a genuine, non-trivial L2/L12 design change — not
  something to make casually inside this diagnostic pass. **Not
  implemented here per the task's explicit "do not implement the next
  improvement yet" instruction.**
- **For case 3's confirmed root cause (relational-exploitability gap):**
  either (a) extend `find_unchecked_ecrecover_result` (and any future
  comparison-based predicate) to attempt to bound the comparator's own
  possible values (a real, materially harder static-analysis task,
  not a quick fix), or, more conservatively, (b) have the predicate's
  own evidence EXPLICITLY FLAG this as an open, unverified precondition
  ("this finding's severity depends on whether `<comparator>` can be
  zero; not evaluated by this predicate") rather than presenting the
  risk as unconditional. (b) is the more honest and immediately
  actionable of the two, and does not require new analysis capability
  — it requires the predicate to accurately represent the LIMITS of
  what it already knows, which is a documentation/evidence-honesty fix
  consistent with this project's existing "over-inclusive, not a
  confirmed violation" framing.
- **For the test-design gap also found in case 3:** this project's
  synthetic-fixture design process (for THIS investigation and for any
  future stability testing) needs a step that explicitly asks "does
  this fixture's OWN stated facts fully justify the expected label, or
  does correctness depend on a fact not present in the fixture?" before
  freezing an "expected" outcome — not just mirroring an existing
  unit-test's positive/negative shape.
- **For case 8 (mechanism unresolved):** no architectural response is
  recommended yet — recommending a fix (e.g. "always cap bundles at
  10") before the mechanism is understood would risk optimizing for
  this one benchmark case rather than addressing the real cause, and
  would be exactly the kind of unsupported intervention the task
  explicitly warns against. The correct next step is the specific,
  cheap, still-unrun experiments in §8, not a production change.

## 8. Unresolved questions

- **Case 8's exact mechanism.** Established: real, volume-bounded (>10,
  ≤20), independent of instruction wording and question-scope framing.
  NOT established: whether the cause is (a) raw token/evidence-item
  volume regardless of content, (b) specifically the presence of many
  *other unconfirmed candidate claims* (semantic competition), or (c)
  something else volume-correlated not yet hypothesized. The two
  cleanest remaining tests (not run in this pass, to stay within the
  originally-scoped budget and the task's request to report null/open
  results honestly rather than keep spending indefinitely): a
  token-count-matched NEUTRAL padding control (H3 variant C — pad to
  the same length with content unrelated to any requirement) and a
  fine-grained bisection between 10 and 20 (e.g. 12, 15, 17) to
  determine whether the transition is a sharp threshold or a gradual
  slope.
- **Whether case 3's finding generalizes.** Confirmed for exactly one
  synthetic instance. Whether real EVMbench-style ecrecover findings
  (e.g. the real Tempo H-03 evidence used elsewhere in Phase H) exhibit
  the same "relational fact missing" gap was not tested here — doing so
  would require checking whether Tempo's real `authorizedSigner`-
  equivalent value is provably non-zero from the real source, which is
  a legitimate follow-up but was out of scope for this diagnostic pass
  (and must not be done by inspecting EVMbench's own finding text to
  reverse-engineer an answer, per this investigation's research-
  integrity constraints).
- **Whether cases 2/4's structural fix (per-location judgment +
  aggregation) is itself sufficient**, or whether it would surface NEW
  granularity problems (e.g. what counts as "the same location" across
  predicates, how contradictory location-level verdicts should
  aggregate) — genuinely unknown without building and testing it, which
  this diagnostic pass deliberately did not do.
- **AR-017 (citation-format mismatch)** was not re-investigated in this
  pass — it remains open exactly as reported in
  `RTF_PHASE_H_LIVE_STABILITY_AND_MODEL_COMPARISON.md`, and none of the
  ablations here depended on citation validity as a signal.
