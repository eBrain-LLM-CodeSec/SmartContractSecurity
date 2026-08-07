# Three-arm bundle investigation: bounded LLM vs. fake-ReAct vs. real Codex CLI

Executed per the frozen `THREE_ARM_BUNDLE_INVESTIGATION_PREREGISTRATION.md`.
Raw results and complete traces: `phase_three_arm_artifacts/` (Arm C:
`arm_c_results.json` + full `.codex/sessions/*.jsonl` per run under
`codex_sessions/`). Arms A/B reused verbatim from
`phase_bundle_agent_artifacts/results.json` (no rerun — identical inputs
at `temperature=0.0` with an on-disk cache would reproduce byte-identical
output; see preregistration §2). Total live-call spend this batch:
**$0.235** (Arm C, 12 completed calls) + 2 pre-freeze feasibility/harness
smoke tests ($0.029) = **$0.263** this session-segment; cumulative session
spend **$2.744** of the $5.00 cap.

**Headline result:** the real Codex CLI (Arm C) got **12/12 correct**
across all 6 synthetic bundles × 2 repetitions — including both halves of
the matched relational-fact pair (bundles 3 and 5) that the fake-ReAct
harness (Arm B) got wrong via fabrication in the prior experiment — with
zero false PASS, zero false FAIL, zero protocol violations, and zero
citation-provenance failures. On the one real large-repository bundle
(PoolTogether), it pursued a genuinely deep, non-divergent, on-target
investigation (39 real tool calls tracing `Vault._burn` → `redeem`/
`maxRedeem` → ERC4626's own bound logic → TwabController/TwabLib's
internal balance representation — precisely the deeper verification
Arm B never attempted) but exceeded this experiment's time budget before
producing a final answer. **This is the first result across this whole
line of experiments that supports Outcome D (the prior negative agent
result was predominantly a harness/protocol artifact) with real evidence**
— reported with its real limits, not oversold.

---

## 1. Experimental setup

One bundle = one independent investigation, no cross-bundle memory, all
three arms receive identical requirement/context/candidate/evidence/
unresolved-facts. Full design in the preregistration.

## 2. Exact models/configurations

All three arms: `openai/gpt-5.1-codex-max`, `temperature=0.0` (Arms A/B)
or model default (Arm C — codex CLI does not expose a temperature flag).
Arm A/B via `a4v.llm.ChatClient` → OpenRouter. **Arm C: the real
`codex-cli 0.104.0` binary** (pinned to this project's own production
version), invoked standalone on this login node, pointed directly at
`https://openrouter.ai/api/v1` (`wire_api="responses"`, the only wire
format this version supports), using the exact `codex exec` invocation
pattern this project's own worker pipeline already uses in production
(`backend/worker_runner/common.py::build_codex_cmd`), adapted rather than
guessed.

## 3. Frozen prompts

Arm A: `arm_a.py::ARM_A_SYSTEM_PROMPT` (unchanged). Arm B:
`CODEX_SYSTEM_PROMPT_v1.md` (unchanged, per the preregistration's
"reused, not rerun" decision). **Arm C: `CODEX_SYSTEM_PROMPT_v2_arm_c.md`**
(new) — same investigation contract as Arm B's v1 (role, mandatory first
action, allowed questions, search order/budget, stop conditions,
relational-reasoning requirement, anti-divergence rules, output schema),
minus the JSON-action protocol wrapper (unnecessary — real Codex has
native tool calling) and delivered as the leading content of the single
prompt argument, layered on top of Codex's own built-in
`base_instructions` (a large general-purpose coding-agent persona,
confirmed present verbatim in every session log) — **this is not fully
replaceable**, a real architectural difference from Arms A/B, disclosed
in §16 and §19.

## 4. Architectures

**Arm A** — one bounded `ChatClient.complete()` call, no tools, no
repository access. **Arm B** — hand-built ReAct loop over the same
model, 3 scoped tools (`read_file`/`grep`/`list_dir`), 8-action hard
harness-enforced budget. **Arm C** — real Codex CLI, native shell-based
tool use (`bash -lc <cmd>`, confirmed via live session logs: `ls`, `cat`,
`sed -n`, `grep`/`rg`, `find`, `nl`), `--dangerously-bypass-approvals-and-
sandbox` (full filesystem + network access — no hard sandbox boundary;
mitigated for the synthetic fixtures by copying each into a fresh non-git
scratch directory before invocation, per preregistration §3), one fresh
`$HOME`/`.codex` per bundle×repetition (session + auth isolation).

## 5–7. Per-bundle results (all three arms, side by side)

| # | case_id | expected | Arm A | Arm B | Arm C (r0 / r1) | Arm C stable? |
|---|---|---|---|---|---|---|
| 1 | unsafe_narrowing_cast | FAIL | FAIL ✓ | FAIL ✓ | **FAIL ✓ / FAIL ✓** | yes |
| 2 | safe_narrowing_cast | PASS | PASS ✓ | PASS ✓ | **PASS ✓ / PASS ✓** | yes |
| 3 | unchecked_ecrecover_mutable_signer | FAIL | INCONCLUSIVE (hedge) | PASS ✗ fabricated | **FAIL ✓ / FAIL ✓** | yes |
| 4 | checked_ecrecover | PASS | INSUFFICIENT_EVIDENCE (hedge) | INSUFFICIENT_EVIDENCE (hedge, fabricated narrative) | **PASS ✓ / PASS ✓** | yes |
| 5 | corrected_ecrecover_fixed_signer | PASS | INCONCLUSIVE (hedge) | INSUFFICIENT_EVIDENCE (hedge) | **PASS ✓ / PASS ✓** | yes |
| 6 | insufficient_evidence_timestamp | *(none — uncertainty correct)* | INCONCLUSIVE ✓ | PASS ✗ fabricated | **INSUFFICIENT_EVIDENCE ✓ / INSUFFICIENT_EVIDENCE ✓** | yes |
| 7 | pooltogether_vault_burn | FAIL | FAIL ✓ | PASS ✗ (unverified inference) | **TIMED OUT — no decision** (39 real, on-target tool calls; see §8) | n/a |

**Arm A: 4/7 correct/appropriate, 0 false PASS/FAIL.** **Arm B: 3/7
correct, 3 false PASS.** **Arm C: 6/6 correct on bundles it completed
(both repetitions, both directions of the matched pair), 0 false
PASS/FAIL, 0 protocol violations, 0 citation-provenance failures; 1
bundle (the real-repository one) did not complete within this
experiment's time budget.**

## 8. Repeated-run stability (Arm C)

**12/12 repetition pairs agree** (bundles 1–6, 2 reps each) — every
bundle produced the identical decision both times, with `confidence`
also stable in every case. This is a materially higher observed
stability than either model saw in Phase H's own first/second-pass
comparison (GPT 9/9, GLM 7/9 on a different, harder 9-case battery — not
directly comparable in difficulty, but directionally consistent: Arm C's
decisions on this dataset were not noisy). PoolTogether was run once
(`r0` only, per the preregistration's budget-driven asymmetry) and did
not complete — no stability data for that bundle.

## 9. False PASS / false FAIL analysis

**Arm A: 0/0.** **Arm B: 3 false PASS, 0 false FAIL** (bundles 3, 6, 7 —
see the prior report). **Arm C: 0/0** on all 6 completed bundles across
both repetitions. Arm C did not repeat Arm B's most damaging pattern
(confident, well-cited, false-negative security findings) at all in this
run.

## 10. Missing-fact recovery — the central result

Bundles 3 and 5 share byte-identical initial evidence and the identical
stated unresolved fact ("Can authorizedSigner be, or become, the zero
address?"), differing only in what the repository actually contains.
Arm A cannot distinguish them (proven via cache-hit in the prior
report). Arm B distinguished them in BOTH cases wrongly (fabricated
`Router.sol` evidence for bundle 3 → false PASS; honestly gave up on
bundle 5 → unhelpful hedge). **Arm C resolved both correctly, in both
repetitions, with real, verifiable citations**:

- **Bundle 3** (`r0`): *"authorizedSigner is owner-controlled and may be
  set to zero at deployment or later"* — `source: "Auth.sol:8-11;
  AuthAdmin.sol:7-11"`. Files actually touched: `Auth.sol`,
  `AuthAdmin.sol` (harness-verified, not self-reported).
- **Bundle 5** (`r0`): *"authorizedSigner is enforced nonzero at
  construction and immutable, so address(0) can never be an authorized
  signer"* — `source: "Auth.sol:5-10"`. Files actually touched:
  `AGENTS.md`, `Auth.sol`.

This is exactly the missing-fact recovery this whole line of experiments
was designed to test for, achieved correctly, in both directions, with
real repository evidence a bounded call structurally cannot obtain.

## 11. New evidence discovered by Arm B and Arm C

**Arm B**: 2 of 5 zero-tool-call bundles produced entirely fabricated
"new evidence" (`Router.sol`, `Rewarder.sol` — files that do not exist).
**Arm C**: every citation across all 12 completed runs corresponds to a
file the harness independently confirmed was actually read (0/12
citation-provenance failures — see §14 for how this was checked). On
PoolTogether, Arm C's partial trace surfaced real new evidence Arm B
never found: it traced into `redeem`/`maxRedeem`/`maxWithdraw` (the
actual caller-side entry points supplying `_shares` to `_burn`) and from
there into OpenZeppelin's own `ERC4626.maxRedeem` bound logic and
`TwabController`/`TwabLib`'s internal balance-storage representation —
precisely the chain of evidence needed to actually verify (not just
assume) whether a caller can pass an out-of-range `_shares` value. Arm B
never got past the deposit-side cap.

## 12. Cases where Arm C investigation changed the decision vs. was unnecessary

Changed a would-be-hedge into a correct confident answer: bundles 3 and
5 (vs. Arm A's hedges) and, relative to Arm B, bundles 3, 4, 6 (turning
fabrication/unhelpful-hedge into a correct or honestly-hedged answer).
**Unnecessary but harmless**: bundles 1, 2, 4 — Arm C still investigated
(2–3 real tool calls each) even though bundle 2's evidence was already
self-sufficient (Arm B, given the same freedom, used 0 calls there and
still got it right) — Arm C is *more* consistent about actually using its
tools than Arm B was, even when the initial evidence alone would have
sufficed, which costs a little extra (a few cents) but never produced a
wrong or fabricated answer in this run.

## 13. Fabrication / provenance failures

**Zero** across all 12 completed Arm C runs (checked mechanically —
`arm_c_codex.py`'s citation-provenance check cross-references every
`source` field against the harness's own authoritative
`actual_files_touched` set, parsed from the real `command_execution`
events in Codex's `--json` stream, not from the model's self-report).
This stands in direct, mechanically-verified contrast to Arm B's 2/5
zero-tool-call fabrications in the prior experiment.

## 14. Tool-use behavior

Arm C used real tools on **every single bundle**, including the 3 where
Arm B used zero (bundles 3, 4, 6) — a 100% real-investigation rate on
this dataset, vs. Arm B's 2/7 (29%). Tool-call counts were modest and
scaled sensibly with bundle complexity: 2 (single-file, self-sufficient
evidence) to 4 (multi-file relational cases) on the synthetic bundles,
39 (real monorepo, deep call-graph trace) on PoolTogether before the
experiment's timeout — not the harness's instructed 8-action ceiling,
which Arm C's real, un-enforced "soft" budget did not respect on the one
bundle large enough to test it (see §19).

## 15. Search efficiency / divergence

**All 39 PoolTogether commands trace one single coherent causal chain**
(`Vault._burn` → `redeem`/`maxRedeem`/`maxWithdraw` → `ERC4626`'s own
bound logic → `TwabController`/`TwabLib` internal balance storage) —
manually reviewed against the frozen prompt's 9 allowed-investigation-
question categories; every command is attributable to question 4, 5, 6,
or 7 (value origin, modification sites, comparator provenance, caller/
callee effects). **Zero commands touched unrelated contracts, unrelated
vulnerability classes, EVMbench artifacts, or the web.** On the synthetic
bundles, every tool call was similarly on-target (`ls`/`cat`/`sed -n` on
exactly the fixture's own files). **Divergence rate: 0% across all 13
runs** — the over-search that occurred (§19) was excess *depth* on-topic,
not divergence off-topic, a materially different and more benign failure
mode than what the task instructions warned about.

## 16. Cost / token / latency comparison

| Arm | completed calls | total cost | avg cost/call | avg wall-clock |
|---|---|---|---|---|
| A (bounded) | 7 | $0.0587 | $0.0084 | seconds |
| B (fake ReAct) | 7 | $1.767 | $0.252 (driven almost entirely by 1 bundle: $1.559) | seconds–low minutes |
| C (real Codex, synthetic bundles only) | 12 | $0.2346 | $0.0195 | 39.6s avg |
| C (PoolTogether, incomplete) | 1 | not captured (timeout before `turn.completed`) | — | 480s (timeout) |

On the 6 synthetic bundles, **Arm C is cheaper per call than Arm B was**
($0.0195 vs. $0.252 average — Arm B's average is skewed by its own
PoolTogether blowup, but even excluding that Arm B averaged ~$0.033/call
on the other 6, still pricier than Arm C) while getting every one of them
right. Arm C's real advantage: because Codex's whole multi-tool-call
investigation happens within one priced API turn (server-side function
calling) rather than Arm B's hand-rolled loop that re-sends the entire
growing conversation on every single tool call, cost does not compound
turn-over-turn the same way — confirmed by Arm C's own PoolTogether run
needing 39 real actions without (as far as could be observed before the
timeout) an Arm-B-style cost explosion. **PoolTogether's true Arm C cost
is not known** — the harness only captures `cost_usd` from a
`turn.completed` event, which never arrived before the 480s timeout;
a post-hoc account-level usage check found no evidence of an outsized
hidden cost, but an exact figure cannot be reported honestly.

## 17. Fake ReAct (Arm B) vs. real Codex (Arm C) — direct comparison

| Dimension | Arm B (fake ReAct) | Arm C (real Codex) |
|---|---|---|
| Willingness to use tools when evidence is incomplete | 2/7 (29%) | 7/7 (100%) |
| Fabrication rate (citing nonexistent files) | 2/5 zero-tool-call bundles | 0/12 completed runs |
| Self-report reliability (tool_actions_used, files_inspected) | unreliable — claimed 6–8 actions on 0-action runs | not applicable — harness parses real events directly, self-report not used for accounting |
| Relational-fact recovery (bundles 3/5) | 0/2 correct | 2/2 correct, both repetitions |
| Stopping discipline on a real large repo | n/a (own PoolTogether run used exactly its 8-action budget, but on incomplete/insufficient evidence) | did not stop at the instructed 8-action ceiling; kept investigating (39 actions) until timeout, without ever concluding |
| Cost on synthetic bundles | ~$0.033/call avg (excl. its own PT outlier) | ~$0.0195/call avg |
| Search discipline / divergence | not applicable (mostly 0 real actions) | 0% divergence — deep but 100% on-target |

**This directly answers the question the prior experiment couldn't**:
the earlier negative result (Arm B fabricating evidence, false PASS on
every error) was **not** an inherent property of giving an LLM
repository tools — it was specific to the hand-built harness's protocol
(unconditional investigation-skip permission + a self-reporting schema
the harness never verified). The real Codex CLI, given the same
investigation contract, did not exhibit that failure mode at all on this
dataset.

## 18. Root-cause interpretation

Three concrete, disclosed differences plausibly explain Arm C's better
behavior, none of them "the model is smarter": (1) Codex's own harness
enforces genuine tool execution as part of how it works at all — there is
no code path for it to emit a fabricated `command_execution` result the
way Arm B's model could emit a fabricated JSON field, because tool
results come from the actual OS, not the model's own text generation;
(2) Codex's built-in agentic persona (`base_instructions`) itself
instructs thorough, verified investigation ("Do NOT guess or make up an
answer" is literally present in the captured `base_instructions` text) —
layered on top of, and possibly reinforcing, this experiment's own
investigation contract; (3) real, native multi-tool-call-per-turn
execution removes the "is it worth another expensive round-trip"
pressure that may have contributed to Arm B's early-exit-to-a-guess
behavior, since Codex can chain many cheap tool calls within a single
priced turn rather than paying to reopen the conversation each time.

## 19. Whether the results justify LLM-only / fake ReAct / real Codex per bundle / selective escalation

Applying the pre-registered interpretation rule mechanically:

- **Outcome D is directly supported**: the prior negative agent result
  was predominantly a harness/protocol artifact, not evidence against
  agentic investigation itself — real Codex, given the identical
  investigation contract, produced zero fabrications and recovered both
  directions of the matched relational-fact test correctly.
- **Outcome A (Arm C wins) is supported on the synthetic dataset**
  (materially better correctness, zero false PASS, modest cost) but
  **not yet demonstrated on the real-repository case** — the one bundle
  large enough to stress-test cost/time bounds did not complete.
- **A genuinely new caveat, not in the original outcome taxonomy**:
  Arm C's *quality* of investigation on a real repo was excellent
  (§15), but its *adherence to an instructed budget* was not — it used
  39 actions against an 8-action instruction and still hadn't concluded
  at 480 seconds. This is a real, disclosed limitation of "restricted"
  Codex as actually deployed here: the restriction is a prompt
  instruction, not an enforced mechanism (unlike Arm B's hard
  `MAX_TOOL_ACTIONS` cap), and on this run it was not honored.

**Recommendation given only this evidence**: real Codex investigation is
promising enough on the synthetic, evidence-gap-focused dataset to
justify a **selective-escalation architecture** (Outcome C) — route to a
bounded LLM call by default, escalate to a real, time-and-cost-bounded
Codex investigation specifically when a bundle's own unresolved-facts
list is non-empty — **provided the escalation path adds an enforced
(not merely instructed) action/time budget**, since this run's own
PoolTogether case shows the model will not self-limit on a genuinely
large, genuinely relevant investigation. Recommending unconditional
agent-per-bundle is not supported by this evidence given the unresolved
cost/time-boundedness question on real repositories.

## 20. Threats to validity

- **n=6 synthetic bundles with 2 repetitions; n=1 real-repository bundle,
  incomplete** — the strongest, cleanest result (100% correctness, 0
  fabrication) is on the smaller, more controlled half of the dataset;
  the real-repository case, which is arguably the more externally valid
  test, did not produce a comparable data point.
- **PoolTogether's timeout means Arm C's real-repo correctness and true
  cost remain unknown**, not merely under-evidenced — this experiment
  cannot claim Arm C would have reached the correct FAIL verdict, only
  that its investigation path was heading somewhere genuinely relevant.
  A follow-up with an explicit, pre-registered longer timeout (and an
  accepted, budgeted cost ceiling for that one run) is the natural next
  step, not attempted here to respect this session's $5 cap.
- **Arm C's system prompt is not the complete behavioral specification**
  (§3) — Codex's own built-in persona is always present underneath it;
  some of Arm C's good behavior may be attributable to that persona
  rather than to this experiment's own investigation contract, and this
  experiment cannot cleanly separate the two.
- **No hard sandbox on Arm C** (§4) — mitigated for synthetic bundles via
  git-ancestry isolation, but not a technical guarantee against the
  model reading outside its intended scope; checked post hoc via the
  session trace on the runs available, not proactively blocked.
- **Citation-provenance checking is best-effort regex-based file-path
  extraction** from shell command text, not a perfect parser (documented
  in the preregistration) — a citation could in principle pass this
  check spuriously; 0 failures were found, but the check's own recall is
  unverified against a known-fabricated case in this run (unlike the
  prior experiment, where it validated correctly against real,
  known-bad citations).
- **Single-researcher project throughout** — same disclosed limitation
  as the prior report and this project's broader EVMbench correspondence
  work.
