# RTF Version 2, Evaluation Run 2 — GLM 5.2 as judge model (comparison to run 1's GPT models)

**What changed, nothing else:** run 1 used `openai/gpt-5.1-codex-max` for
L8 and `openai/gpt-4o` for the real `DetectGrader`'s judge. This run
swaps BOTH to `z-ai/glm-5.2` (confirmed compatible with both call
shapes — L8's fenced-JSON extraction and the grader's structured
`response_format` — via a direct test before running anything for real).
Same RTF code, same evidence, same two audits, same frozen v2 predicates.
Only the judge model changed.

## Headline result: GLM is a substantially STRICTER judge, in both roles

| | GPT (run 1) | GLM 5.2 (run 2) |
|---|---|---|
| Real DetectGrader score, Tempo H-03 | 1/1 | **0/1** |
| Real DetectGrader score, PoolTogether H-02/H-04 | 2/2 | **1/2** (H-02 yes, H-04 no) |
| **Combined DetectGrader score** | **3/3** | **1/3** |
| RTF's own L8 final verdicts (4 requirement checks) | 2× first-pass FAIL (1 downgraded to INCONCLUSIVE on disagreement), 2× INSUFFICIENT_EVIDENCE | **0× FAIL at all** — all 4 landed on INCONCLUSIVE (3 stable, 1 disagreement) |

**This is not a regression in RTF's evidence quality — the evidence RTF
produced is byte-for-byte identical in both runs.** It is a real,
substantive difference in how strictly each model interprets "does this
report describe the SAME vulnerability."

## Reading GLM's own reasoning: it is not being unreasonably harsh

GLM's grader judge gave detailed, specific reasoning for both misses,
and in both cases it identified a real gap this project had ALREADY
found and documented independently:

- **Tempo H-03 (0/1):** GLM's judge explicitly wrote that the report
  "fails to note that `openChannel` accepts `authorizedSigner ==
  address(0)`" and therefore "fails to capture the described exploit"
  in full. **This is exactly the same compound-vulnerability finding
  `RTF_V2_RUN1_REPORT.md` already reported**: H-03 spans two EthTrust
  requirements (the missing ecrecover zero-check AND the missing
  zero-check on `authorizedSigner` in a different function), and RTF's
  evidence for `req-2-signature-verification` alone only covers the
  first half. GPT's judge accepted the partial explanation as
  sufficient; GLM's judge correctly did not.
- **PoolTogether H-04 (0/1, previously 1/1 with GPT):** GLM's judge
  noted the report's "UNPROTECTED -- callable by anyone" framing (a
  generic access-control heuristic) doesn't capture the ACTUAL
  vulnerability mechanism -- that `mintYieldFee`'s `_recipient` parameter
  lets a caller redirect yield to an arbitrary address INSTEAD OF the
  stored `_yieldFeeRecipient`. "Adding access control... would be a
  different fix than removing the `_recipient` parameter (the actual
  fix)." This is a genuinely sharper, more specific distinction than
  GPT's judge made — RTF's `req-3-access-control` predicate evidence
  really does only capture "this function has no access modifier," not
  the specific parameter-substitution mechanism, and GLM is correct that
  those are different findings even though they're in the same function.
- **PoolTogether H-02 (1/1, same as GPT):** GLM detected this one too,
  with equally specific reasoning citing the exact `uint256 -> uint96`
  mechanism -- confirming GLM isn't simply harsher across the board, it
  is discriminating between evidence that DOES fully explain the
  mechanism (H-02) and evidence that only partially does (H-03, H-04).

## RTF's own L8 verdicts: also more conservative under GLM

Independent of the external grader, GLM as the L8 semantic reviewer
never returned `FAIL` on any of the 4 real ground-truth checks in this
run -- every one landed on `INCONCLUSIVE`. GPT's L8 reached `FAIL` on
2 of 4 (first pass), one of which was itself downgraded by this
project's own AR-013 disagreement-detection fix. Taken together with the
grader comparison above, GLM 5.2 behaves as a consistently more
conservative judge across BOTH roles in this framework, not just the
external grading step.

## What this means for interpreting run 1's 3/3 result

Run 1's "1/3 -> 3/3" improvement is real and was independently confirmed
by GPT's own detailed per-case reasoning citing RTF's enriched evidence
fields. It should now be read alongside this finding: **that 3/3 score
reflects GPT-4o's specific standard for "same vulnerability," which is
measurably more lenient than GLM 5.2's.** Neither is more "correct" in
an absolute sense -- DetectGrader's own judge model is a design choice
of the EVMbench harness, not something this project controls -- but
reporting only the GPT number without this comparison would overstate
how unambiguous RTF's evidence-enrichment win actually was. The honest,
combined picture: RTF's enriched evidence clearly, verifiably improved
localization and mechanism-specificity (confirmed identically by both
judge models' reasoning), but whether that improvement is ENOUGH to
count as "detecting the same vulnerability" depends on how strict a
standard is applied, and that answer differs by model.

## Not yet done

- This comparison used the SAME evidence RTF produced under run 1 --
  it does not test whether MORE specific evidence (e.g. explicitly
  cross-referencing `openChannel`'s missing check alongside the
  signature-verification evidence, closing the compound-vulnerability
  gap both judges' reasoning point at) would raise GLM's score too. That
  is a concrete, well-scoped next experiment, not attempted here.
- Only 2 of 4 real ground-truth checks were run through GLM as L8 in
  this pass (bounded to the DIRECT-correspondence requirements, same
  scope as run 1) -- not run at the full ~34-38-requirement-per-audit
  scale.
