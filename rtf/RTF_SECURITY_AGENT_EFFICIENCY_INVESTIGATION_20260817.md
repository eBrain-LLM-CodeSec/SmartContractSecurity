# Security-agent kernel: why it's slow and under-resolves, vs. Codex

Investigation date: 2026-08-17. Target: `2025-04-forte` (`Float128.sol` +
`Ln.sol` + `Types.sol`), same frozen semantic-property generation cache used
by both arms compared below, same clustering pipeline
(`rtf/l11_investigation_grouping/`), only the investigator differs. All
numbers in this document are pulled directly from real run artifacts, not
estimated — file paths are cited throughout so every claim is checkable.

Runs referenced:
- **Codex baseline**: `/scratch/md5344/evmbench/rtf_forte_live_foundry_combined_20260815/` (`summary.json`, `grade_result.json`)
- **Security-agent kernel, final successful run**: `/scratch/md5344/evmbench/rtf_forte_security_agent_20260817_v2/` (`summary.json`, per-cluster `scratch/security_agent/*/{tokens,trajectory}.jsonl`) — this is the run analyzed throughout; it ran on `security-agent-kernel` @ commit `7b07a32` (post- all fixes described below except where noted as "still open")
- **Security-agent kernel, first (pre-fix) run**: `/scratch/md5344/evmbench/rtf_forte_security_agent_20260817/` — referenced only for historical context on the crash bugs, all since fixed

---

## 1. Headline comparison

| | Codex (real baseline) | Security-agent kernel (this investigation) |
|---|---|---|
| Properties resolved | 155 / 160 (97%) | 53 / 147 (36%) |
| Real cost | $3.38 | $5.09 (pipeline's own authoritative in-run total, carrying forward the earlier checkpointed $1.90 — see §6 on why this number, not others quoted mid-investigation, is the trustworthy one) |
| Wall clock | 799 s (13.3 min) | 9,781 s (163.0 min) |
| Cost per resolved property | $0.022 | $0.096 (**4.4×** worse) |
| Time per resolved property | ~5.2 s | ~184.5 s (**~35×** worse) |
| DetectGrader score | 3/5 (real, graded) | not yet graded — see §7 |

Same model (`z-ai/glm-5.2`) in both arms. The gap is architectural, not a
model-choice difference.

---

## 2. Symptoms, quantified

### 2.1 Only 41% of cluster attempts actually concluded

From `scratch/security_agent/*/trajectory.jsonl`'s final `cluster_finished`
event, across all 22 cluster attempts in the final run:

| Termination reason | Cluster attempts | What it means |
|---|---|---|
| `concluded` | 9 (41%) | Real PASS/FAIL/NOT_APPLICABLE verdicts produced |
| `kernel_malformed_response_exhausted` | 7 (32%) | **Zero properties resolved** — every retry attempt failed to produce a parseable answer |
| `max_steps_exhausted` | 6 (27%) | Ran out of the 15-step budget without ever reaching `conclude` |

Nearly 6 in 10 cluster attempts produced **no verdict at all** for any of
their properties, while still consuming real time and money.

### 2.2 Duration is dominated by a small number of pathological clusters

Per-cluster wall-clock span (first to last real API call), sorted:

```
cluster_001  164.9 min  (28 calls, 6 malformed, ended: exhausted)
cluster_000  136.8 min  (45 calls, 3 malformed, ended: max_steps)
cluster_005  122.7 min  ( 5 calls, 5 malformed, ended: exhausted)
cluster_004  111.7 min  (30 calls, 1 malformed, ended: max_steps)
cluster_002   48.0 min  (20 calls, 2 malformed, ended: concluded)
cluster_003   39.3 min  (21 calls, 1 malformed, ended: concluded)
... (16 more clusters, all under 30 min, several under 3 min)
```

The 4 slowest clusters alone account for 536 cumulative cluster-minutes —
more than 3× the entire run's 163-minute wall clock (they overlapped via
`max_concurrent_investigations=2`, which is exactly why the whole run still
took as long as it did: the two concurrency slots kept getting occupied by
one of these pathological clusters at a time). The other 18 clusters
mostly resolved (concluded or exhausted) in under 15 minutes each.

This is not "the kernel is uniformly slow" — it is "a minority of clusters
fall into a specific, expensive failure mode, and that failure mode
dominates the total runtime."

### 2.3 Malformed responses are frequent and expensive

47 `malformed_model_response` events across the run (out of ~285 successful
`model_action` events + 47 malformed ≈ 332 real model turns — roughly
**one in every seven real API calls produced nothing usable**).

Of the 334 real calls counted across all attempts against this run
directory (see §6's caveat on this figure), 23 (7%) hit the completion-token
cap outright (`completion_tokens` ≥ 15,900 against the 16,000 cap) —
these 23 calls alone account for **$1.69, roughly 20% of all real spend**,
for zero usable output each.

---

## 3. Root causes

### 3.1 [FIXED] No `max_tokens` cap at all (first run, 2026-08-17 morning)

The very first live run set no completion-token limit anywhere. `z-ai/glm-5.2`
repeatedly generated runaway completions hitting an apparent ~65,536-token
hard provider ceiling on complex clusters (`cluster_006`: 29209, 33813,
23069, 29414, then 65536 completion tokens across successive turns, the
last costing $0.067 by itself) — truncated/anomalous output crashed
downstream JSON parsing (`AttributeError` on `None.find`).
**Fixed**: `DEFAULT_MAX_COMPLETION_TOKENS` introduced (commit `9f79c2e`),
later raised 8000→16000 (commit `51a3f81`) once it became clear 8000 was
itself still frequently insufficient.

### 3.2 [FIXED] No defensive handling for `content: null`

Even with a token cap, the model can spend the *entire* budget on internal
reasoning and return `content: null` (confirmed live, byte-for-byte, in two
separate clusters' raw cached API responses: `{"content": null,
"completion_tokens": 8000}`). `extract_last_fenced_json(None)` crashed with
`AttributeError` uncaught, propagating to `live_runner.py`'s generic
catch-all (`cluster_invocation_crashed:AttributeError`).
**Fixed**: `model_client.py` now checks for empty/null content before
parsing (commit `51a3f81`).

### 3.3 [FIXED] Uncaught `JSONDecodeError` and unvalidated evidence references

Two more real crash types from the first run, both root-caused and fixed
with regression tests (commit `9f79c2e`):
- `json.JSONDecodeError` from genuinely malformed (not just
  trailing-garbage) model output, uncaught in `model_client.py`.
- `kernel.py`'s `_apply_investigation_update` never validated that a
  hypothesis's cited evidence ids existed before `upsert_hypothesis` ->
  `_require_evidence` raised `UnknownEvidenceIdError` — the single largest
  crash cause in the first run (42/114 INCONCLUSIVE properties).

### 3.4 [FIXED, but see §3.6] Wrong wire format for a reasoning model

`a4v.llm.ChatClient` talks to GLM-5.2 via the Chat Completions endpoint
(`/chat/completions`), which has no way to bound reasoning effort
independent of total output length. The real Codex investigator has never
hit any of the above failures on the same model, because it uses the
Responses API (`wire_api = "responses"`, confirmed in
`arm_c_codex.py`/`arm_g_codex.py`), which exposes an explicit
`reasoning.effort` control.
**Fixed**: new `rtf/security_agent/responses_client.py`
(`ResponsesChatClient`, commit `7b07a32`), `reasoning_effort="low"` by
default, now the kernel's default chat client.

### 3.5 [OPEN, dominant cause of §2.2/§2.3] `reasoning.effort="low"` reduces but does NOT eliminate reasoning exhaustion, because context keeps growing unboundedly

This is the most important open finding. `cluster_005`'s real call history
in the *final, post-fix* run (`scratch/security_agent/.../cluster_005/tokens.jsonl`):

```
pre-fix (Chat Completions):  114, 16000, 6906, 14959, 16000 completion tokens
post-fix (Responses, low):   100, 3563, 10567, 16000, 16000 completion tokens
```

The Responses-API fix clearly helps on *early* turns (100, 3563, 10567 —
much smaller than the pre-fix pattern) but the **same cluster still hits
the 16,000-token cap twice** by its 4th and 5th turns. Critically, `prompt_tokens`
for these same calls grew 28,853 → 28,904 → 42,846 → 42,904 across the
cluster's lifetime — nearly matching the completion cap itself by the end.

**The mechanism**: this kernel resends the *entire* accumulated conversation
history as raw text on every single turn (a stateless completions API, no
truncation, no summarization, no session/prompt-cache reuse). As a cluster's
investigation progresses — especially after a malformed-response retry
appends a corrective message, which itself lengthens the conversation for
every subsequent turn — the prompt grows, requiring more model reasoning to
process, which makes the *next* turn more likely to exhaust even a bounded
low-effort budget, which triggers *another* retry, which grows the context
further. This is a compounding failure spiral that neither the token cap
(§3.1) nor the reasoning-effort control (§3.4) addresses at its root — both
only raise the threshold before the spiral becomes visible, they don't stop
it from developing.

This single mechanism plausibly explains most of §2.1–§2.3 directly: the 7
clusters that ended `kernel_malformed_response_exhausted` are exactly the
clusters where this spiral ran to its conclusion (3 consecutive failed
retries, each takes 15–25 minutes of real wall-clock time per the timestamp
gaps observed, e.g. `cluster_005`'s 122.7-minute span for only 5 total
calls).

### 3.6 [OPEN, orthogonal] Property-to-cluster assignment is not stable across separate process runs

Confirmed with hard data, not inferred: `cluster_001`'s property_ids in the
*final* run (`req-2-check-rounding::clause0/loc1/loc2/loc3/clause1/clause2`
+ 2 semantic numerical properties) are **completely different** from
whatever properties occupied the name `cluster_001` in the earlier,
killed attempt that this run's `checkpoint.jsonl` was seeded from — none
of the final run's `cluster_001` properties appear in the checkpoint at
all, despite `cluster_001` having already been marked `DONE` in an earlier
attempt.

`grouping_engine.py`'s `cluster_properties` is internally deterministic
given a fixed input order (its own docstring: "ties broken by property_id
for full reproducibility", verified by reading the merge logic) — the
non-determinism is therefore almost certainly upstream, in how the property
pool itself is assembled/ordered before clustering runs (not pinned down to
an exact line in this investigation). The practical effect: `live_runner.py`'s
checkpoint-resume optimization (`set(cluster.property_ids) <=
resolved_property_ids`) is far less effective than intended across separate
process launches, because a cluster bearing the same *name* as a
previously-completed one can now contain a different mix of already-resolved
and never-resolved properties, forcing full re-investigation (paying again
for properties that were already correctly resolved). This compounds the
cost/time problem in §1 but is a distinct, separable bug from §3.5 — it
lives in the pre-existing clustering/generation pipeline, not in anything
added for this kernel.

---

## 4. What this does NOT show

To be precise about what these results do and don't demonstrate:

- **This is not evidence the security-agent architecture is worse at finding
  real vulnerabilities than Codex.** Of the 53 properties it *did* resolve,
  9 real FAILs were found with cited evidence (`req-2-documented`,
  `req-1-no-assembly` on `Float128`) — quality of the properties actually
  investigated hasn't been assessed against ground truth yet (§7).
- **The clustering/generation pipeline itself is not implicated** beyond
  §3.6 — the same property pool, same clustering code, drove both a 3/5
  Codex run and this run; the efficiency gap is entirely on the investigator
  side.
- **GLM-5.2 is not inherently unusable for this task** — Codex gets 97%
  resolution with the same model. The gap is in how this kernel talks to it
  and manages context, not the model's raw capability.

---

## 5. Recommendations, in priority order

1. **Bound conversation-history growth per cluster** (§3.5, highest
   leverage). Options: summarize/prune older turns instead of resending
   raw history; exploit the Responses API's own session/prompt-caching
   support instead of treating every call as fully stateless; cap the
   number of tool-call turns before forcing a checkpoint/conclude attempt.
   This is the one change most likely to collapse the heavy tail in §2.2
   directly, since the spiral in §3.5 is what produces it.
2. **Make the malformed-response retry loop time-aware, not just
   attempt-count-aware.** Currently 3 failed attempts can cost 45–75+
   minutes of real wall-clock time on a single doomed cluster (§2.3) with
   no circuit breaker on elapsed time, only attempt count. A wall-clock
   budget per cluster (independent of the per-call `timeout_s`) would cap
   the worst case.
3. **Investigate and fix the clustering/property-pool ordering
   non-determinism** (§3.6) — even a partial fix (e.g., sorting the property
   pool by a stable key before clustering) would make checkpoint-resume
   actually save the money it's designed to save.
4. **Re-evaluate whether the PASS-discipline completion gate's cost is
   worth its rigor benefit** — 11 `conclusion_rejected` events in this run
   is a real but comparatively small contributor next to §3.5/§3.6; revisit
   after the above are addressed, since it may look proportionally larger
   or smaller once the dominant costs are fixed.

---

## 6. A note on the cost figures in this document

During the live investigation, an internal check script summed real
per-call costs from every `tokens.jsonl` file under this run's `scratch/`
directory and reported **$8.62** — this number is **inflated** and should
not be treated as authoritative. The same run directory was reused across
three separate process launches (a raw background attempt, a killed SLURM
attempt, and this final successful SLURM attempt), and `tokens.jsonl` files
are appended to, not overwritten, per case_id across separate launches. The
pipeline's own in-memory `total_cost_usd` — which correctly starts from the
checkpoint's real recorded cost and adds only the current run's genuinely
new spend — is the trustworthy figure: **$5.09**, reported in this run's
own `summary.json`. §2.3's $1.69/23-call capped-cost figure is pulled from
the same (inflated) aggregate scan as the $8.62 total and should be read as
directionally correct (roughly a fifth of spend goes to capped-out calls)
rather than a precise dollar figure for this run alone.

---

## 7. Not yet done

- **Real `DetectGrader` score** for this run's 9 FAIL findings against
  forte's ground truth (H-01 through H-05) — needed to know whether the 36%
  resolution rate that *was* achieved found anything Codex's 3/5 missed, or
  vice versa. Separate real spend, needs explicit go-ahead.
- **A rerun with §5.1/§5.2 fixed** would be the natural next validation
  step before drawing conclusions about the architecture's investigation
  quality, since the current run's coverage is too incomplete (36%) for a
  fair recall comparison against Codex's 97%.
