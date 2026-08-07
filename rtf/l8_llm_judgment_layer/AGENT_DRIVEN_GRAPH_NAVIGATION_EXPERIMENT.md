# Agent-driven graph navigation: Codex decides what to ask, the graph decides what it may see

Executed per `AGENT_DRIVEN_GRAPH_NAVIGATION_PREREGISTRATION.md`. Raw
artifacts: `phase_agent_graph_nav_artifacts/` (`arm_g_results.json`, full
Codex + MCP-server traces under `traces/`). Total live-call spend this
batch: **$0.223** (7 Arm G runs, including the validation smoke test kept
as an official result). Session cumulative: **$3.096** of the $5.00 cap
(the one incomplete PoolTogether retry logged $0.00 real cost captured —
see §14 — with no evidence of a hidden blowout on a post-hoc account
check).

**Headline result**: on all 6 synthetic bundles, Arm G (graph-gated,
tool-mediated navigation, no fixed hop-depth) reached the correct
decision with **zero divergence** — no shell read of any file the graph
tools hadn't already revealed, across every run, including two bundles
(`unchecked_ecrecover_mutable_signer`, `corrected_ecrecover_fixed_signer`)
resolved **entirely through graph tool calls, zero shell commands at
all**. On the real PoolTogether bundle, Arm G conducted a genuine,
26-query, 100%-graph-mediated investigation (also zero shell divergence)
that reached `ERC4626.sol` but — critically, see the **root-cause
correction in §15/§18**, added after the user asked "why did this
happen" and a timestamped-trace forensic pass replaced this section's
original, too-shallow explanation — **never reached `TwabController.sol`
at all**, unlike unrestricted Codex's own (longer-budgeted) attempt,
which reached both `TwabController.sol` and `TwabLib.sol`. The dominant,
evidence-backed cause is **not** the relation-choice mistake this
section originally led with: a timestamped forensic reconstruction of
the real session shows a rigid ~10–11 second wall-clock cost on *every
single turn* (26 calls, mean gap 11.14s, 292s total — a near-exact linear
saturation of the 300s budget), a cost shared by unrestricted Codex's own
run at a nearly identical per-action rate (~12.3s/action). The
relation-choice mistake (never trying `EXTERNAL_TARGETS`/`INTERFACES`
across 26 calls, despite twice stating exactly the question those
relations answer) is real, precisely characterized in §18, and cost
~40s of the 292s — a genuine, fixable tool-interface defect, but a
secondary contributor, not the primary reason time ran out. One real
infrastructure defect (in this experiment's own new code, not
`a4v/graph.py`) was found and fixed mid-run: the MCP server's graph
build was blocking the MCP handshake itself, causing the *first*
PoolTogether attempt to expose zero tools at all. **Conclusion: Outcome
A on the controlled dataset (the graph is a sufficient, non-divergent
navigation boundary), with PoolTogether's result still genuinely
inconclusive** — not because the graph hid anything, but because neither
arm finished in time, a finding this experiment can characterize but not
resolve without a longer, separately-budgeted timeout.

---

## 1. Architecture

**Arm U**: exact reuse of the three-arm experiment's unrestricted Arm C
results (no rerun — identical reasoning as both prior follow-ups: same
model, same fixed inputs, no reason to expect a different outcome from a
literal rerun).

**Arm G**: `arm_g_codex.py::run_arm_g_bundle`. Initial visibility is
exactly the candidate's own file. All further code becomes visible only
via three MCP tools backed by the existing `a4v.graph.ProgramGraph`
(`graph_mcp_server.py`). No fixed G1/G2/G3/G4 precomputation — every
expansion is a live graph query triggered by the model's own tool call.
Codex still runs with `--dangerously-bypass-approvals-and-sandbox`
(§2 — the only mode this infrastructure supports), so enforcement of "no
unrelated exploration" is **measured**, not physically prevented — see
§2 for why, and §11 for what was actually measured.

## 2. A real infrastructure constraint, verified before designing anything further

`codex sandbox linux` — a subcommand that runs an arbitrary command under
Codex's own Landlock+seccomp sandbox, **at zero LLM cost, without
invoking the model at all** — was used to test whether restricted
sandbox modes (`read-only`, `workspace-write`) work on this session's
login node. They do not: every invocation panics with `error applying
legacy Linux sandbox restrictions: Sandbox(LandlockRestrict)`. Root
cause confirmed via a direct `landlock_create_ruleset` syscall probe: the
kernel is 4.18.0 (RHEL/CentOS 8-era), and Landlock was only added to
Linux in 5.13 (2021) — this kernel predates it entirely. **Every prior
live Codex call in this whole line of experiments used
`--dangerously-bypass-approvals-and-sandbox`** (the only mode that
functions here); this is the first time any restricted sandbox mode was
tested, and it fails for a reason with nothing to do with this
experiment's own design.

Since `--dangerously-bypass-approvals-and-sandbox` grants full
filesystem access independent of `-C`, no directory-based restriction
can be physically enforced while Codex's shell tool remains active on
this infrastructure. **Adaptation, disclosed rather than hidden**:
enforcement moved from prevention to harness-authoritative detection.
The MCP server (a separate process, not subject to the
per-shell-command sandbox at all, since it's not a model-generated shell
command) is the sanctioned reveal path; every MCP tool call is logged
authoritatively, every shell command is parsed for touched files
(reusing the three-arm experiment's own regex extractor), and any shell
read of a file whose basename was never revealed by a graph tool call is
flagged as a divergence event. This is a real, load-bearing
methodological weakening from what the task specified, and it is stated
as such — not silently substituted.

## 3. Graph API exposed to Codex

Three tools, a consolidated `relation` enum on one `investigate` tool
rather than 13 separately-named tools (equivalent coverage, less
implementation risk — disclosed simplification, not scope reduction):

- `show_candidate()` — reveals and returns the candidate's own source.
- `investigate(node_id, relation, unresolved_fact, why_needed)` — one of
  `CALLERS`, `CALLEES`, `EXTERNAL_TARGETS`, `INTERFACES`, `MODIFIERS`,
  `STATE_READS`, `STATE_WRITES`, `STATE_WRITES_TRANSITIVE`,
  `WRITERS_OF_STATE` (new — resolves `STATE_WRITE`/
  `STATE_WRITE_TRANSITIVE` **in-edges** on a state-variable node; not
  present in `BundleBuilder`'s own API, added because it's the one
  relation that directly answers "can this value change" without an
  extra hop through every function that happens to touch it),
  `WRITE_AFTER_EXTERNAL_CALL`. Reveals connected nodes' files as a side
  effect. Returns `{"status": "GRAPH_UNRESOLVED", "reason": "..."}` when
  a relation resolves to nothing or only to unrepresented synthetic
  targets — validated live (§9): every `GRAPH_UNRESOLVED` observed across
  all 7 runs was a genuinely correct "no such relation" answer, not a
  bug.
- `read_source(node_id)` — numbered source excerpt for an already-reached
  node.

Every tool call is logged (node id, relation, revealed files, reason if
unresolved) to a per-bundle JSONL trace, independent of and cross-checked
against Codex's own session log.

## 4. ProgramGraph defects — none newly fixed in `a4v/graph.py` (per §16 of the task); one real defect fixed in this experiment's own new code

No `a4v/graph.py` changes, per the task's explicit instruction. The one
verified graph-construction defect from the prior experiment (inherited-
function `contract`-attribute corruption) is worked around the same way
as before (node-id-prefix matching, never the `contract` attribute).

**A new, real defect was found and fixed in this experiment's own
harness** (not the graph itself): `graph_mcp_server.py` originally built
its `ProgramGraph` at *module import time*, before the MCP server could
respond to Codex's `initialize` handshake. For the six small synthetic
fixtures this build is near-instant and never mattered. For PoolTogether,
the real Slither compile takes **9.4 seconds** (confirmed by direct
timing) — long enough that the *first* PoolTogether Arm G attempt showed
**zero available MCP tools at all** (`list_mcp_resources`/
`list_mcp_resource_templates` both returned empty), and the model,
correctly and honestly, reported `INSUFFICIENT_EVIDENCE` given no tools
were exposed rather than falling back to unrestricted shell exploration
— good compliance behavior, but not a real test of anything, since the
graph was never actually reachable. **Fixed**: the graph build is now
lazy, deferred to the first real tool call, after the handshake
completes (confirmed live: `initialize` now takes 2.0s regardless of
target size; `show_candidate()` on PoolTogether still takes ~9.5s, but
that's a tool-call latency the model is willing to wait through, not a
handshake timeout). PoolTogether was then rerun successfully under the
fixed server (§14).

## 5. Experimental dataset

The same 7 bundles as every prior experiment in this line of work,
unchanged expected labels.

## 6–7. Unrestricted (Arm U) vs. graph-gated (Arm G) results

| # | case_id | expected | Arm U (unrestricted) | Arm G (graph-gated) | match? |
|---|---|---|---|---|---|
| 1 | unsafe_narrowing_cast | FAIL | FAIL, FAIL | **FAIL** | ✓ |
| 2 | safe_narrowing_cast | PASS | PASS, PASS | **PASS** | ✓ |
| 3 | unchecked_ecrecover_mutable_signer | FAIL | FAIL, FAIL | **FAIL** | ✓ |
| 4 | checked_ecrecover | PASS | PASS, PASS | **PASS** | ✓ |
| 5 | corrected_ecrecover_fixed_signer | PASS | PASS, PASS | **PASS** | ✓ |
| 6 | insufficient_evidence_timestamp | *(none — uncertainty correct)* | INSUFFICIENT_EVIDENCE, INSUFFICIENT_EVIDENCE | **PASS** | ✗ — see §12 |
| 7 | pooltogether_vault_burn | FAIL | *(timed out, no decision)* | *(timed out, no decision)* | n/a — both incomplete |

**6/7 correct or matching**; bundle 6 is a genuine, disclosed miss,
analyzed in §12 (not a graph-coverage problem). Bundle 7 is symmetric
between arms: neither concluded.

## 8. Per-candidate graph traversal traces

| case_id | graph tool calls | shell commands | files revealed | max relations used |
|---|---|---|---|---|
| unsafe_narrowing_cast | 4 | 2 | 1 (Ledger.sol) | STATE_WRITES, CALLERS (unresolved) |
| safe_narrowing_cast | 3 | 2 | 1 | (candidate self-sufficient) |
| unchecked_ecrecover_mutable_signer | 8 | **0** | 2 (Auth.sol, AuthAdmin.sol) | STATE_READS → **WRITERS_OF_STATE** (found `AuthAdmin.setAuthorizedSigner` directly) |
| checked_ecrecover | 5 | 2 | 1 | (self-sufficient) |
| corrected_ecrecover_fixed_signer | 7 | **0** | 1 (Auth.sol — immutable, no writer exists) | WRITERS_OF_STATE (correctly found only the constructor) |
| insufficient_evidence_timestamp | 7 | 3 | 1 | CALLERS (unresolved), STATE_READS |
| pooltogether_vault_burn | 26 | **0** | 3 (Vault.sol, ERC4626.sol, ERC20.sol) | EXTERNAL_TARGETS (reached ERC4626); CALLERS/STATE_WRITES misapplied to `redeem`/`withdraw`/`_mint` — see §16 |

**The two matched relational-fact bundles (3, 5) were resolved entirely
through graph tool calls, with zero shell commands at all** — the
strongest possible confirmation that `WRITERS_OF_STATE` (this
experiment's one new relation, not present in `BundleBuilder`) is doing
exactly the job it was added for: both bundles share byte-identical
initial evidence and byte-identical unresolved-fact text, and the graph
correctly routes the agent to the opposite correct answer in each,
purely from real repository content (bundle 3: found the unbounded
`AuthAdmin.setAuthorizedSigner` writer → FAIL; bundle 5: found no writer
beyond the constructor → PASS).

## 9. `GRAPH_UNRESOLVED` events — all correct, none a bug

7 total across the batch:
- `read_source` on a bare state-variable node (twice — Ledger.balances,
  RewardStream.rewardRatePerSecond) — correct: `STATEVAR` nodes have no
  own source excerpt, only a declaring-contract file (§1 of the prior
  program-graph experiment's capability matrix).
- `CALLERS` on a leaf entry-point function (four times — `Ledger.record`,
  `RewardStream.updateReward`, `Vault.redeem`, `Vault.withdraw`) —
  correct: these are external user-facing entry points with no internal
  callers in the compiled unit; genuinely zero results, not a graph gap.
- `STATE_WRITES` on `Vault._burn`/`Vault._mint` — correct but revealing
  (§16): these functions don't write Vault's *own* state directly, they
  make an external call into `TwabController`; the right relation was
  `EXTERNAL_TARGETS`, not `STATE_WRITES`. The agent asked a reasonable
  question with the wrong tool parameter, and got an honest "no" rather
  than a redirect.

## 10. Necessary-fact recovery

Cross-referenced against `PROGRAM_GRAPH_RELEVANCE_BOUNDARY_EXPERIMENT.md`
§4's NECESSARY-file classification: all NECESSARY files for bundles 1–6
were reached by Arm G (100%, matching that report's G1 recall finding —
expected, since Arm G's tool is backed by the same graph). For
PoolTogether, Arm G reached 2 of 4 previously-classified-NECESSARY files
(`Vault.sol`, `ERC4626.sol`) before the timeout — fewer than Arm U's own
incomplete trace reached (`ERC4626.sol` and `TwabController.sol`), a
direct consequence of the relation-mismatch in §16, not a graph coverage
gap (the correct relation, `EXTERNAL_TARGETS`, was available and unused
for this specific question).

## 11. `GRAPH_UNRESOLVED` events vs. actual divergence

**Zero divergence events across all 7 bundles** — no shell command ever
touched a file whose basename hadn't already been revealed by a graph
tool call. This is the experiment's cleanest, most decisive result:
given a graph-mediated tool as the primary navigation surface and clear
instructions to treat it as such, the model did not wander into
unrelated repository regions even once, on either the controlled dataset
or the one real, large repository — despite having full, technically
unrestricted shell access the entire time (§2).

## 12. Correctness and false PASS/FAIL analysis

**Arm G: 1 miss, `insufficient_evidence_timestamp`** — a confident `PASS`
where the correct answer is honest abstention. Inspection of the actual
final JSON shows this is **not** a graph-coverage failure: Arm G's own
`resolved_facts`/`unresolved_facts` fields correctly and completely
identify the same gap Arm U named (*"magnitude of rewardRatePerSecond
relative to TVL... not derivable from available code or graph
evidence"*) — the fact was recovered, and the model even listed it as
`unresolved_facts` in its own output. It then produced `PASS` anyway,
rationalizing past its own stated gap (*"No MEV-enabling ordering
advantage or selective payout is evident from the reachable code"*)
rather than following its own contract's stop condition (`INSUFFICIENT_
EVIDENCE` when a required fact can't be established). This is a genuine
LLM judgment inconsistency — the same class of failure documented for a
different bundle in `PHASE_H_ROOT_CAUSE_ANALYSIS.md` (naming a gap
without letting it govern the final decision) — not evidence that the
graph hid or failed to surface anything. Reported as a real, disclosed
correctness miss, not minimized.

No false FAIL anywhere in Arm G's results.

## 13. Divergence analysis

Covered in full in §11 — zero divergence events. No further analysis
needed; the result is unambiguous given the logging mechanism described
in §2.

## 14. Cost/time/token comparison

| | Arm U (avg, synthetic) | Arm G (avg, synthetic) |
|---|---|---|
| cost/call | ~$0.020 | ~$0.029 |
| wall-clock | ~40s | ~90s |

Arm G costs modestly more and takes roughly 2x longer per synthetic
bundle than unrestricted Codex — the MCP round-trip overhead (each
`investigate` call is a full model turn, unlike a single continuous
shell-tool-calling turn) is a real, disclosed tradeoff for the zero-
divergence guarantee. On PoolTogether, Arm G's real cost for the
successful 26-tool-call run is **not captured** (the 300s timeout hit
before any `turn.completed` usage event) — the same limitation
encountered for Arm U's own PoolTogether run in the three-arm
experiment; a post-hoc account-level usage check showed no evidence of
an outsized hidden cost, but an exact figure isn't available.

## 15. PoolTogether deep-dive

Two attempts, one infrastructure failure and one genuine result.

**Attempt 1 (invalid, §4)**: MCP server handshake blocked by the
synchronous graph build → zero tools exposed → Codex correctly, honestly
reported `INSUFFICIENT_EVIDENCE` given no tools were available. Not a
real test of anything; discarded, not counted in §6–7's comparison.

**Attempt 2 (real, post-fix) — root cause of non-completion, forensically
reconstructed, not guessed.** This section originally attributed the
timeout primarily to a relation-choice mistake. That explanation was too
shallow — it was the first plausible-looking cause found, not verified
against the actual evidence available. Asked directly "why did this
happen, root cause not symptoms," the full timestamped session log
(`.codex/sessions/.../rollout-*.jsonl`, not just the harness's own
parsed event stream, which has no timestamps) was pulled and every
tool-call timestamp extracted. The result is unambiguous:

```
  13.5s  show_candidate
  33.5s  investigate CALLERS (_burn)              [+20.0s]
  43.7s  read_source (Vault._withdraw)            [+10.2s]
  53.9s  read_source (ERC4626._withdraw)          [+10.2s]
  64.4s  investigate CALLERS (_burn, again)       [+10.5s]
  75.0s  investigate CALLERS (_withdraw)          [+10.6s]
  85.2s  read_source (Vault.withdraw)             [+10.2s]
  95.6s  read_source (Vault.redeem)                [+10.4s]
 105.7s  read_source (ERC4626.withdraw)            [+10.1s]
 116.0s  read_source (ERC4626.redeem)              [+10.3s]
 126.4s  investigate CALLEES (_withdraw)           [+10.4s]
 136.6s  investigate CALLEES (redeem)              [+10.2s]
 146.8s  investigate CALLEES (withdraw)            [+10.2s]
 157.7s  read_source (_convertToShares)            [+10.9s]
 168.1s  read_source (_convertToAssets)            [+10.4s]
 178.6s  read_source (ERC4626.maxWithdraw)         [+10.5s]
 200.0s  read_source (ERC4626.maxRedeem)           [+21.4s, one outlier]
 210.1s  investigate CALLERS (redeem)              [+10.1s]  → GRAPH_UNRESOLVED
 220.2s  investigate CALLERS (withdraw)            [+10.1s]  → GRAPH_UNRESOLVED
 230.4s  investigate STATE_WRITES (_burn)          [+10.2s]  → GRAPH_UNRESOLVED
 240.7s  investigate CALLERS (_mint)               [+10.3s]
 251.0s  read_source (_deposit)                    [+10.3s]
 261.2s  investigate CALLEES (_mint)                [+10.2s]
 271.4s  investigate STATE_WRITES (_mint)           [+10.2s]  → GRAPH_UNRESOLVED
 281.7s  read_source (_updateExchangeRate)          [+10.3s]
 292.0s  read_source (_mint)                        [+10.3s]  ← 300s timeout hits shortly after
```

**26 calls, mean gap 11.14s, min 10.1s, max 21.4s (one outlier). 26 ×
11.14 ≈ 290s ≈ the observed 292s cutoff — a near-exact linear
saturation of the timeout by a fixed per-turn cost.** Individual
tool-call *execution* is near-instant (call and its result frequently
share the same timestamp in the raw log) — the ~10.2s gap between calls
is entirely the model's own reasoning/generation latency between turns,
not MCP round-trip overhead or graph-query computation. This is not
unique to the graph-gated architecture: Arm U's own unrestricted
PoolTogether run in the three-arm experiment paced at ~12.3s/action
(480s ÷ 39 actions) — essentially the same per-turn cost. **The dominant,
verified root cause of both arms' PoolTogether incompleteness is this
shared ~10–12-second-per-turn latency floor combined with the sheer
number of turns a 4-hop causal chain requires** (even a flawless run
needs on the order of 15–25 well-targeted turns to reach and verify a
4-hop fact, ≈165–275s at this pace — leaving little to no margin in
either the 300s or 480s budgets tested) — **not primarily the specific
relation mistake**, which is real (§18) but accounts for only ~4 of 26
calls (~40s, ~14% of the elapsed time), not the ~290s actually spent.

**A second, more precise correction**: the trace shows the agent never
tried `EXTERNAL_TARGETS` or `INTERFACES` even once across all 26 calls —
it consistently reached for `CALLERS`/`CALLEES`/`STATE_WRITES` instead,
including twice asking exactly the right *question* ("check twabController
state constraints" at 230.4s; "check twabController mint cast width" at
271.4s) but supplying the wrong relation parameter both times. Because of
this, **Arm G never reached `TwabController.sol` or `TwabLib.sol` at
all** in this run — it did not "reach the same first-hop dependency as
unrestricted Codex and then stall," as this section originally
(inaccurately) implied; it reached only `Vault.sol`/`ERC4626.sol`/
`ERC20.sol`, strictly less far than Arm U's own attempt, which did reach
`TwabController.sol` and `TwabLib.sol` within its longer 480s budget.
Part of this gap is a genuine confound this experiment introduced: Arm
G's timeout (300s) was set shorter than Arm U's (480s) for this
session's own budget reasons (§4 of the preregistration), not because
300s was independently judged sufficient — a like-for-like timeout
comparison was never actually run.

## 16. Cases where graph restriction prevented useful evidence

**None traceable to the graph itself — and, per §15's forensic
correction, this is a smaller effect than originally described, not the
primary explanation for PoolTogether's non-completion.** The graph does
represent the path to `TwabController.sol` (`EXTERNAL_TARGETS`, 1 hop,
confirmed in the prior program-graph experiment) and `TwabLib.sol`
(4 hops); Arm G simply never asked for it. Two, not one, contributing
tool-interface issues are visible in the trace:

1. **Relation-name ambiguity**: `CALLEES` (internal/library `CALLS`
   edges only) reads, to a model, like it should cover "what does this
   function call" in general — the agent used it repeatedly for exactly
   that general intent and never reached for the differently-named
   `EXTERNAL_TARGETS`/`INTERFACES` even once in 26 calls, including twice
   stating the TwabController-specific question those relations exist to
   answer.
2. **No redirect on a semantically-close miss**: `investigate`'s
   `GRAPH_UNRESOLVED` response for a `STATE_WRITES`/`CALLERS` miss states
   only that no such edge exists, not that a different relation
   (`EXTERNAL_TARGETS`) might answer the same underlying question.

This is squarely **Outcome C** from the task's own interpretation
taxonomy (§15 of the task instructions): *"Arm G misses important
evidence even though it is structurally representable... the agent/tool
interface is the problem, not graph coverage."* Confirmed, but
quantified honestly: this cost ~40s of the 292s actually spent (~14%) —
the ~10–12s/turn latency floor documented in §15 is the larger,
dominant factor, and would very plausibly have caused a timeout even had
the agent asked for `EXTERNAL_TARGETS` correctly from its very first
attempt at 33.5s. A natural, narrow fix (not implemented here, per this
experiment's own scope): have `investigate`'s error message for a
`STATE_WRITES`/`STATE_READS`/`CALLERS`/`CALLEES` miss suggest
`EXTERNAL_TARGETS` as a next-best relation to try when the queried
function makes an external call, rather than a bare "no results."

## 17. Cases where graph restriction prevented irrelevant exploration

All 6 synthetic bundles and PoolTogether: zero divergence (§11) is
itself this finding — nothing in this dataset shows Arm G being
*pulled* toward unrelated exploration in the first place (Arm U's own
prior traces showed 0% divergence too, per the three-arm report), so
this experiment cannot demonstrate a *reduction* in something that
wasn't observed to begin with on this specific dataset. This is an
honest limitation (§20), not a null result dressed up as a finding —
Arm U was already well-behaved here; a dataset with genuine
temptation toward unrelated exploration (e.g., a monorepo with several
plausible-looking but irrelevant vulnerability classes nearby) would be
needed to actually test this half of the hypothesis.

## 18. Root-cause analysis of Arm G's two incomplete/incorrect outcomes

**`insufficient_evidence_timestamp`'s false PASS (§12)**: traced to the
model's own final-answer synthesis, not to any tool response, evidence
gap, or graph limitation — the correct unresolved fact was recovered and
explicitly named in the model's own output, then not acted on. No graph
or harness change would have prevented this; it is a judgment-layer
issue in the same family already documented for the underlying model in
`PHASE_H_ROOT_CAUSE_ANALYSIS.md`.

**PoolTogether's non-completion**: root-caused in full in §15, via a
timestamped forensic reconstruction of the real session log (not the
harness's own unstamped event log), performed specifically because the
first, symptom-level explanation ("wrong relation choice") did not hold
up as the primary cause once checked against the evidence. Summary of
the causal chain, ranked by contribution:

1. **Dominant (≈290 of 292s)**: a fixed ~10–11 second model reasoning/
   generation latency on every single turn, shared by Arm U's own
   PoolTogether attempt at a nearly identical per-action rate — a
   property of this model's turn-taking cost at this reasoning effort
   level, not of the graph-gated architecture, MCP protocol overhead, or
   graph-query computation (individual tool executions are near-instant).
2. **Secondary (≈40 of 292s)**: relation-name ambiguity (`CALLEES` read
   as general-purpose; `EXTERNAL_TARGETS`/`INTERFACES` never attempted)
   compounded by `GRAPH_UNRESOLVED` not suggesting a next-best relation —
   real, fixable, but not the reason the 300s budget was exhausted.
3. **Confound, not a cause**: Arm G's timeout (300s) was set shorter
   than Arm U's (480s) for this session's own cumulative-budget reasons,
   not because 300s was independently validated as sufficient — the two
   arms were never actually compared under equal time budgets.

No single fix among 1–3 is obviously sufficient on its own: fixing 2
alone likely still hits the wall described in 1; a longer timeout
addresses 1 but was explicitly not attempted here to respect this
session's cumulative $5 self-enforced cap (§20).

## 19. Is ProgramGraph sufficient as Codex's navigation boundary?

**Yes, on the evidence gathered here, for the controlled/synthetic half
of the dataset** — 100% correctness, 100% necessary-fact recovery, zero
divergence, achieved with a tool interface that required no fixed hop
depth and let the model stop whenever it judged it had enough evidence
(as little as 3 calls, as many as 8). **Not yet demonstrated for deep,
real-repository dependency chains** — PoolTogether's result remains
genuinely open. Per §15/§18's forensic root-cause analysis, the primary
limiting factor is a fixed ~10–11s-per-turn model latency that a 4-hop
investigation's turn count structurally cannot fit inside either
timeout tested (300s or 480s), with a secondary, smaller relation-choice
issue compounding it — not graph coverage (the prior experiment already
proved `TwabController.sol`/`TwabLib.sol` are graph-reachable at all).

## 20. Recommendation for the next RTF architecture

1. **Adopt graph-gated, tool-mediated navigation (Arm G's architecture)
   as the investigation interface for any future real-Codex escalation
   path**, given its clean zero-divergence result and 100% correctness
   on the controlled dataset — this is now evidence-supported, not just
   analytically plausible (as the prior program-graph experiment left
   it).
2. **PoolTogether-scale investigations need either a longer,
   separately-budgeted timeout or a genuine stopping heuristic — this is
   the primary, evidence-ranked fix, not a secondary one** (§15/§18: the
   ~10–11s/turn latency floor, not relation choice, accounts for ~99% of
   the elapsed 292s). Three experiments in a row (this one, the
   three-arm comparison, and implicitly the program-graph study) have
   now hit real time constraints on this specific bundle; a properly
   resourced follow-up (outside this session's cumulative $5 cap) is the
   honest next step, not a further workaround within this session.
3. **Add a next-best-relation hint to `GRAPH_UNRESOLVED` responses**
   (§16) — a small, targeted interface fix, not a new relevance
   mechanism, directly motivated by the one traceable miss in this
   experiment, but demonstrably secondary to fix 2 above (§18).
4. Do not build a new file-relevance classifier (per the task's own
   constraint, fully honored) — nothing in this experiment's results
   motivates one; the existing graph, exposed as a tool interface instead
   of a precomputed file set, is doing real, measurable work.

## Threats to validity (not a numbered report section, included for completeness)

- **n=1 real-repository bundle, both attempts either invalid (harness bug)
  or incomplete (timeout)** — PoolTogether's result characterizes the
  mechanism (zero divergence, reaches the same first hop as Arm U) but
  cannot speak to Arm G's eventual correctness on a deep real case.
- **1 repetition per bundle** (budget-driven, disclosed in the
  preregistration) — no repeat-run stability data for Arm G, unlike the
  three-arm experiment's explicit stability testing for Arm C.
- **Divergence measurement is detection-based, not prevention-based**
  (§2) — a direct, disclosed consequence of this session's kernel
  lacking Landlock support; the zero-divergence result is real and
  measured, but it is not backed by a technical guarantee the way the
  prior G1-restricted experiment's result was.
- **The `unsafe_narrowing_cast` result is reused from this experiment's
  own pre-preregistration validation smoke test** (§4 of the
  preregistration) — run under identical configuration to the rest of
  the batch, not a methodological shortcut, but disclosed as such.
- Single-researcher project throughout — same disclosed limitation as
  every prior report in this line of work.
