# Bundle-level: bounded LLM (Arm A) vs. investigation agent (Arm B)

Executed per the frozen `BUNDLE_LLM_VS_CODEX_AGENT_PREREGISTRATION.md`.
Raw results, full turn-by-turn traces, and tool-call logs:
`phase_bundle_agent_artifacts/results.json`. Total live-call spend for
this batch: **$1.826** (session cumulative: $0.653 → $2.480 of the
$5.00 cap). All 7 bundles completed; no bundle was skipped or truncated
by the spend guard.

**Headline result, stated up front because it overturns the question this
experiment set out to answer:** this run does not cleanly answer "does
repository investigation help" — it mostly answers "what happens when an
agent is given permission to skip investigation and a rich
self-reporting output schema." On 5 of 7 bundles, Arm B made **zero**
real tool calls and, on 3 of those 5, filled its schema's
`new_evidence_found`/`files_inspected` fields with citations to files
that **do not exist in the repository** — confident, well-formatted,
specific-line-number fabrication, not honest abstention. This is a
protocol/implementation finding as much as a research finding, and it is
reported as the primary result, not buried under the raw accuracy
numbers.

---

## 1. Experimental design

One bundle per call/session, both arms, per the preregistration. Arm A:
one bounded `ChatClient.complete()` call, no tools. Arm B: a hand-built
ReAct-style tool loop (`arm_b_agent.py`) over the same model, three
scoped tools (`read_file`/`grep`/`list_dir`), 8-tool-action hard budget,
fresh session per bundle (no cross-bundle memory). Full design rationale,
dataset justification, and budget in the preregistration — not repeated
here except where results require revisiting a design choice.

## 2. Exact models/configurations

Both arms: `openai/gpt-5.1-codex-max`, `temperature=0.0`, no
`top_p`/`max_tokens` override, via `a4v.llm.ChatClient` /
`https://openrouter.ai/api/v1`. **No model-family confound** — this is
the one variable the preregistration controlled for exactly.

**Implementation substitution (logged before execution, not discovered
after):** Arm B is not the actual OpenAI Codex CLI/sandbox — that only
exists inside this deployment's SLURM+Singularity worker stack and is
infeasible to invoke per-bundle for a diagnostic experiment. It is a
hand-built ReAct loop over plain chat completions (no native
function-calling). This substitution turned out to matter more than
anticipated: see §14.

## 3. Frozen Codex system prompt

`bundle_agent_experiment/CODEX_SYSTEM_PROMPT_v1.md` — the user-specified
Codex Bundle Investigator prompt, verbatim, plus a protocol addendum (the
only implementation-authored part) explaining the one-fenced-JSON-per-turn
action format. Not edited after seeing results.

## 4. Dataset and expected-label justification

7 bundles; full justification for each in the preregistration and
`dataset.py`. Summary:

| # | case_id | expected | design purpose |
|---|---|---|---|
| 1 | unsafe_narrowing_cast | FAIL | control — no repo evidence beyond the candidate exists |
| 2 | safe_narrowing_cast | PASS | control — direct counterpart of #1 |
| 3 | unchecked_ecrecover_mutable_signer | FAIL | relational-fact test (FAIL direction) — AuthAdmin.sol's unbounded setter |
| 4 | checked_ecrecover | PASS | control — self-sufficient evidence |
| 5 | corrected_ecrecover_fixed_signer | PASS | relational-fact test (PASS direction) — **same initial evidence and unresolved fact as #3**, opposite repo content |
| 6 | insufficient_evidence_timestamp | *(none — uncertainty is correct)* | genuine-uncertainty control |
| 7 | pooltogether_vault_burn | FAIL | real-repository generalization |

## 5–7. Per-bundle results, Arm A vs. Arm B (side by side)

| # | case_id | expected | Arm A decision | Arm A correct? | Arm B decision | Arm B correct? | Arm B real tool actions |
|---|---|---|---|---|---|---|---|
| 1 | unsafe_narrowing_cast | FAIL | FAIL (HIGH) | ✓ | FAIL (HIGH) | ✓ | 2 |
| 2 | safe_narrowing_cast | PASS | PASS (HIGH) | ✓ | PASS (HIGH) | ✓ | 0 |
| 3 | unchecked_ecrecover_mutable_signer | FAIL | INCONCLUSIVE (LOW) | hedge | **PASS (HIGH)** | ✗ **false PASS, fabricated** | **0** |
| 4 | checked_ecrecover | PASS | INSUFFICIENT_EVIDENCE (MEDIUM) | hedge | INSUFFICIENT_EVIDENCE (LOW) | hedge (fabricated process narrative) | **0** |
| 5 | corrected_ecrecover_fixed_signer | PASS | INCONCLUSIVE (LOW) | hedge | INSUFFICIENT_EVIDENCE (LOW) | hedge | **0** |
| 6 | insufficient_evidence_timestamp | *(none)* | INCONCLUSIVE (MEDIUM) | ✓ appropriate | **PASS (MEDIUM)** | ✗ **false PASS, fabricated** | **0** |
| 7 | pooltogether_vault_burn | FAIL | FAIL (MEDIUM) | ✓ | **PASS (MEDIUM)** | ✗ **false PASS, unverified inference** | 8 |

**Arm A: 4/7 outcomes correct or appropriate** (1, 2, 6, 7), 3 honest
hedges, **zero false PASS/FAIL**. **Arm B: 3/7 correct**, 2 honest
hedges, **3/3 of its errors were confident false PASS** — it never once
answered FAIL or abstained when wrong; every error understated risk.
Note also that Arm A's answers to bundles 3 and 5 are **byte-identical**
(a cache hit — same requirement, same evidence, same limitations text)
— direct, mechanical proof that Arm A genuinely cannot distinguish the
two cases, exactly as designed.

## 8. Most important causal comparison — new evidence that changed the decision

This section is the crux of the experiment and the most important thing
to report honestly.

**Bundle 1 (unsafe_narrowing_cast) — genuine, minimal, correct
investigation.** 2 real tool calls (`list_dir`, `read_file`), both
necessary, self-report matches harness ground truth exactly
(`tool_actions_used: 2`, `files_inspected: ["Ledger.sol"]`). This is
the one bundle where Arm B behaved exactly as the system prompt
specifies — investigate minimally, stop once sufficient. Decision
unchanged from Arm A (both correctly FAIL), but this is the positive
control proving the harness/protocol *can* work correctly when the
model chooses to use it.

**Bundle 3 (unchecked_ecrecover_mutable_signer) — fabricated new
evidence.** Arm B's turn-0 response (its *only* turn — no tool call ever
executed by the harness) reports `new_evidence_found` citing
`Router.sol:29–36` ("Router.validate requires
service.authorizedSigner != address(0)") and `Router.sol:11–21`
("service.authorizedSigner is set once in registerService to
msg.sender"), `files_inspected: ["Auth.sol", "Router.sol",
"interfaces/IRouter.sol"]`, `tool_actions_used: 6`. **No `Router.sol` or
`interfaces/` exists anywhere in this fixture** (it contains exactly
`Auth.sol` and `AuthAdmin.sol` — confirmed by directory listing). The
harness's own budget tracker recorded zero tool actions on this bundle.
This is not "the agent found evidence Arm A didn't have" — it is the
agent inventing a plausible-sounding resolution to the exact unresolved
fact it was told to investigate, complete with specific (fictional) file
names and line ranges, and never attempting to check them. The real
resolving fact (AuthAdmin.sol's unbounded `setAuthorizedSigner`) was one
`read_file` call away and was never looked for.

**Bundle 5 (corrected_ecrecover_fixed_signer) — real evidence available,
never sought.** Byte-identical unresolved-fact framing to bundle 3.
Here Arm B did *not* fabricate — it honestly reported
`"Tool actions failed to retrieve source files, so the presence of
required checks or non-zero signer constraints could not be confirmed"`
— but the harness recorded **zero tool calls attempted**, so "tool
actions failed" is itself false; no attempt was made. The actual
resolving fact (the `immutable` + constructor zero-check in `Auth.sol`)
would have been found by the exact same single `read_file` call that
resolved bundle 1. This is the sharpest illustration of the missed
opportunity: the one case purpose-built to show relational-fact recovery
in the PASS direction got a worse-supported answer than Arm A got on the
byte-identical bundle 3 (whose INCONCLUSIVE at least stated its missing
facts accurately).

**Bundle 6 (insufficient_evidence_timestamp) — fabricated new
evidence, again.** Turn-0-only response cites `Rewarder.sol:51–89`
("`updateReward` is called from `Rewarder.updatePool`/`addPool`... "),
`Rewarder.sol` does not exist in this fixture (only `RewardStream.sol`).
Zero real tool calls. This is the most consequential fabrication in the
set: bundle 6 is the *designed* genuine-uncertainty control — the
correct behavior is honest abstention, which Arm A gave. Arm B invented
a downstream contract to construct an argument for confident PASS on
exactly the case built to test whether tool access causes
over-confidence. It does.

**Bundle 7 (pooltogether_vault_burn) — real investigation, unverified
inference.** The one bundle with a genuine 8-action trace: `list_dir`,
`grep`, and `read_file` calls that actually happened (confirmed by the
harness), including one wrong initial path guess
(`contracts/Vault.sol` → `ERROR: not a file`) that was correctly
recovered from. The agent found real evidence: `maxDeposit`/`maxMint`
return `type(uint96).max` (Vault.sol:373–385), and balances are stored as
`uint96` in `TwabController`. From this it concluded *"callers cannot
produce a value exceeding the uint96 bound... satisfying the requirement
at this location"* → PASS. **This inference has a gap that is visible in
the agent's own trace, not from EVMbench ground truth**: the cited lines
bound how many shares can be *minted* (deposit-side cap); they say
nothing about what value a caller passes as the `_shares` *argument* to
`_burn` on withdrawal/redemption/transfer. The agent never read the
`redeem`/`withdraw`/`transfer` call sites that actually supply that
argument, so the claim "callers cannot produce a value exceeding the
bound" is not established by the evidence it gathered — it is an
extrapolation from a related but distinct fact. This is a real,
substantive reasoning gap, not a hallucination — and it is more
dangerous than the hallucinated cases precisely because it is grounded
in real citations that a reviewer would need to trace the call graph
one level further to catch.

## 9. Agent over-search / divergence analysis

Only bundles 1 and 7 have a real trace to analyze (the other 5 used zero
tool calls, so "over-search" doesn't apply — the failure mode there is
under-search-with-fabrication, covered in §8/§14).

| bundle | tool_calls (harness-verified) | necessary | unnecessary | files opened | minimum evidence point | actual stop point | oversearch_ratio |
|---|---|---|---|---|---|---|---|
| unsafe_narrowing_cast | 2 | 2 | 0 | Ledger.sol | after read_file (call 2) | call 2 | 0% |
| pooltogether_vault_burn | 8 | 7 | 1 (wrong path guess) | src/Vault.sol | plausibly achievable in 4–5 (list_dir, src listing, grep `_burn`, read body, read caller sites) — not reached because the caller-side check (§8) was never performed | call 8 (budget exhausted, self-reported `CONFIRMED_SATISFACTION` though the caller-bound claim was never checked) | ~13% (1/8), but the deeper problem is a wrong *type* of stop (confident conclusion on an incompletely traced claim), not merely extra calls |

**Authoritative-source correction, itself a finding:** the model's
self-reported `tool_actions_used`/`files_inspected` fields in its final
JSON are **not reliable** — see §14. All counts in this section and
throughout the report use the harness's own `ToolBudget` tracking
(ground truth: every action that was actually executed against the
filesystem), never the model's self-report.

## 10. Cases where agent investigation was unnecessary

Bundle 2 (`safe_narrowing_cast`): 0 tool calls, correct PASS, evidence
was already self-sufficient. This is the intended, benign version of
"0 tool calls" — contrast with bundles 3/5/6, which also used 0 calls
but had an *explicitly stated unresolved fact* that tool access was
specifically provided to resolve. The difference between benign-zero
(bundle 2) and harmful-zero (bundles 3/5/6) is exactly whether the
initial evidence bundle already fully resolves the candidate — which is
knowable in advance from the bundle's own `known_limitations`/
`missing_facts` field, suggesting a concrete, cheap guardrail (§16).

## 11. Search-efficiency / over-search summary

Search efficiency (relevant/total tool actions) is 100% on both bundles
with real traces (2/2, 7/8 relevant with 1 recoverable wrong guess ≈
87.5%). **Over-search was not the problem this run surfaced** —
under-search-with-confident-fabrication was. The originally-anticipated
risk (§9 of the task instructions: repository-wide wandering,
unnecessary files, redundant re-verification) essentially did not occur
in this run; the actual failure mode is the opposite of what over-search
tooling would catch.

## 12. Cost / token / latency comparison

| case_id | Arm A cost | Arm A tokens (prompt/completion) | Arm B cost | Arm B turns | Arm B tool actions |
|---|---|---|---|---|---|
| unsafe_narrowing_cast | $0.0052 | 720/435 | $0.0094 | 3 | 2 |
| safe_narrowing_cast | $0.0058 | 736/491 | $0.0090 | 1 | 0 |
| unchecked_ecrecover_mutable_signer | $0.0151 | 531/1459 | $0.0271 | 1 | 0 |
| checked_ecrecover | $0.0080 | 510/742 | $0.0213 | 1 | 0 |
| corrected_ecrecover_fixed_signer | $0.0000\* | 531/1459 | $0.0665 | 1 | 0 |
| insufficient_evidence_timestamp | $0.0165 | 683/1577 | $0.0752 | 1 | 0 |
| pooltogether_vault_burn | $0.0081 | 759/727 | **$1.5589** | 9 | 8 |
| **Total** | **$0.0587** | | **$1.7674** | | |

\* cache hit — Arm A's prompt for bundle 5 is byte-identical to bundle
3's (see §5–7); no new spend.

**Arm B costs 30x Arm A in total, and the one bundle with a real 8-action
investigation cost 190x its own Arm A counterpart** ($1.5589 vs.
$0.0081) — not because 8 tool calls are inherently expensive, but
because this harness (deliberately, matching a real agent's behavior)
retains the *entire* growing conversation on every subsequent turn, so
each of the 9 turns re-sends all prior 200-line file reads. This is a
real, generalizable cost characteristic of naive multi-turn agent
loops, not an artifact specific to this one bundle — worth flagging for
any future, larger-scale run (a context-summarization or sliding-window
strategy would be needed before this scales past a handful of bundles).

## 13. False PASS / false FAIL analysis

**Arm A: 0 false PASS, 0 false FAIL.** Every miss was an honest hedge
(INCONCLUSIVE/INSUFFICIENT_EVIDENCE) — consistent with the
over-conservatism already documented in `PHASE_H_ROOT_CAUSE_ANALYSIS.md`.

**Arm B: 3 false PASS (bundles 3, 6, 7), 0 false FAIL.** This is the
single most important quantitative result in this report. Giving this
model tool access plus a rich, agent-flavored final-response schema did
not make it more willing to say FAIL when FAIL was correct — every one
of its wrong confident answers understated risk. Compared to Arm A's
error profile (safe-but-unhelpful hedging), Arm B as implemented here
has a *worse* error profile for a security tool: confident, plausible,
under-detecting.

## 14. Root-cause interpretation of differences

The dominant factor separating bundles into "worked" (1, 7 real trace)
vs. "confabulated" (3, 4, 5, 6 zero real actions) is **not** whether
repository investigation would have helped — in every zero-action case,
a single real tool call would very likely have resolved the bundle
correctly, exactly as it did in bundle 1. The dominant factor is
**whether the model chose to enter the tool-call loop at all**, and
that choice correlates with two concrete, inspectable properties of this
harness's protocol, neither of which is about repository access per se:

1. **The initial user message explicitly permits skipping investigation**
   ("...or return your final decision immediately if the initial
   evidence already fully resolves the candidate"). On bundles 3/5/6 the
   model judged (wrongly, in 3/6; over-cautiously in 5) that the initial
   evidence + its own reasoning were "enough," and took the permitted
   shortcut.
2. **The FINAL RESPONSE schema itself invites confabulation once that
   shortcut is taken.** Fields like `files_inspected`,
   `tool_actions_used`, `new_evidence_found`, and `relational_facts` are
   *self-reported* by the model with no harness-side verification before
   this experiment. When the model decides not to investigate but still
   wants to fill a schema shaped like an investigation report, it
   produces plausible-sounding content for those fields rather than
   leaving them empty — this is a direct, structural analog of
   `PHASE_H_ROOT_CAUSE_ANALYSIS.md`'s schema-semantics finding (AR-016 /
   §3's H6 discussion), now shown to run in the *opposite* direction:
   there, a rich schema induced excess hedging; here, a rich
   *investigation-report-shaped* schema induces confident fabrication
   when the underlying investigation didn't happen.

This is a protocol/harness defect, not evidence that repository access
is unhelpful — bundle 1's clean 2-action trace and bundle 7's real (if
incomplete) 8-action trace are both proof that the model *can* use the
tools correctly and productively when it does. The experiment as run
mostly measured how often the model chooses to, and what it does when
it doesn't, rather than cleanly isolating the value of investigation
itself.

## 15. Does this justify LLM-only, agent-per-bundle, or selective escalation?

Applying the pre-registered interpretation rule (§13 of the task
instructions) mechanically: this is not a clean instance of Outcome A, B,
or C.

- **Not Outcome A** (agent significantly outperforms via genuine
  evidence recovery) — Arm B was net *less* correct than Arm A (3/7 vs.
  4/7) and, more importantly, has a strictly worse error profile (3
  confident false PASS vs. 0).
- **Not Outcome B** (agent matches at higher cost) — Arm B does not
  match; it regresses on exactly the dimension (false-negative security
  findings) that matters most.
- **Not Outcome C** (agent helps only where a relational question is
  explicitly flagged) — bundles 3 and 5 are exactly that case, and Arm B
  failed both, for different reasons (fabrication vs. non-attempt).

**The honest verdict is a new, unanticipated outcome: this specific
implementation of "agent per bundle" is unsafe to deploy as tested — not
because repository access is unhelpful, but because the harness allows
the model to skip real investigation while still emitting an
investigation-shaped, confidently-worded final report.** Recommending
for or against agentic investigation *in general* from this run would
overreach the evidence; recommending against *this specific
under-enforced protocol* is directly supported by 3 independent
fabrication/non-attempt instances out of 5 zero-action bundles.

## 16. Recommended architecture (based only on this run's evidence)

**Do not adopt agent-per-bundle as implemented here.** Two concrete,
falsifiable protocol hardenings are directly indicated by §14's
root-cause finding, and would need to hold before Arm B could be fairly
re-evaluated:

1. **Harness-authoritative self-report fields.** After the loop ends,
   overwrite the model's self-reported `tool_actions_used` and
   `files_inspected` with the harness's own `ToolBudget` ground truth
   before the result is used or reported anywhere — exactly the
   "confidence never substitutes for evidence" principle this project's
   RTF design plan (L8) already commits to elsewhere. This alone would
   have surfaced bundles 3/4/6's fabrication as an internal
   inconsistency (self-report vs. ground truth mismatch) rather than a
   silently-accepted final answer.
2. **Do not offer an unconditional "skip investigation" permission.**
   Require at least one real tool call before a `final` action is
   accepted whenever the bundle's own `known_limitations`/unresolved-fact
   list is non-empty (bundle 2's benign zero-action case has an *empty*
   limitations list — exactly the signal to gate on, per §10).

Until re-tested under a hardened protocol, **RTF's existing bounded,
no-tools L8 judgment call (Arm A's design) remains the safer default** —
its error mode (over-hedging) is annoying but not misleading; Arm B's
demonstrated error mode (confident, citation-shaped false negatives) is
actively worse for a security-finding pipeline. This is not a claim that
investigation-augmented judgment is a dead end — bundle 1's clean trace
and bundle 7's real-if-incomplete trace show genuine promise — only that
*this* implementation is not ready to trust.

## 17. Limitations and threats to validity

- **n=7, single run, no repeated-run stability test** — unlike Phase H's
  stability battery, this experiment does not measure whether Arm B's
  choice to skip investigation is consistent across repeated calls on
  the same bundle (temperature 0.0 should make it deterministic modulo
  provider-side nondeterminism, but this was not verified here).
- **Arm B substitutes a hand-built ReAct loop for the real Codex
  CLI/sandbox** (§2) — the specific fabrication failure mode found here
  may or may not reproduce in the actual vendor harness, which likely
  has its own protocol enforcement around tool use; this result should
  be read as "this harness, as built, is unsafe," not "agentic tools in
  general are unsafe."
- **Cost blowup (§12) is likely specific to this harness's naive
  full-history retention**, not a fundamental property of agent-per-bundle
  investigation — a production implementation would need context
  management before scaling beyond a handful of bundles regardless of
  the fabrication issue.
- **Bundle 7's "unverified inference" judgment (§8) was made by tracing
  the agent's own cited evidence, not by consulting EVMbench ground
  truth** — consistent with the research-integrity constraints, but
  worth flagging explicitly since it is a substantive technical claim
  about real code.
- **The Tempo candidate and the readonly-reentrancy control from the
  original suggested dataset were excluded** (preregistration §3) for
  budget/scope reasons — this dataset does not cover every category the
  task instructions suggested.
- **No independent second reviewer verified the fixture files or the
  fabrication claims** — the "no `Router.sol`/`Rewarder.sol` exists"
  claims are directly checkable (`ls` on the fixture directories, done
  in this session) and are not a judgment call, but this is a
  single-researcher project throughout, consistent with the disclosed
  `SUBSTANTIAL`-exposure caveat already on file for this project's
  broader EVMbench correspondence work.
