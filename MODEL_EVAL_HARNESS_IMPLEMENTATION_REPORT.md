# Model Evaluation Harness — Implementation Report

**Date:** 2026-08-27
**Objective:** Build a reproducible, low-cost model-evaluation harness for testing whether cheaper/open-weight models can replace GPT-5.6 Sol as the primary RTF investigator, then run the first, cheapest test of that question (DeepSeek V4 Pro against the frozen Canto gate case).
**Harness location:** `rtf/security_agent/eval/` (this worktree)
**Experiment artifacts:** `/scratch/md5344/evmbench/experiments/model_eval/2024-01-canto-rootcause-fix-full-rerun/req-3-implement-as-documented_loc0/`

---

## 1. Architecture

```
run_model_eval.py (CLI + orchestration)
  ├─ model_registry.py    -- ModelConfig per candidate, resolve_api_key()
  ├─ preflight.py          -- mandatory compatibility gate before any paid run
  ├─ scenario_scorer.py     -- offline Level 0-3 counterexample-quality scorer (Canto-specific)
  └─ _frozen_worker.py      -- subprocess: the ONLY place that imports the
                               frozen a61d547 baseline checkout's investigator/
                               kernel/pipeline code
```

**Why a subprocess boundary for the frozen checkout.** Every prior GLM-5.3/GPT-5.6-Sol
result in this project was produced against a specific pinned kernel state
(commit a61d547 + the independent `rank_evidence` fix from 881eeb3, with the
anti-anchoring gate 73bf68c absent). For a new model's result to be
comparable to those numbers, it must run against the *identical* scaffold —
not this worktree's current HEAD, which may have diverged. `run_model_eval.py`
itself lives inside this worktree's own `rtf.security_agent.eval` package, so
a naive `sys.path.insert(0, baseline_checkout)` trick (which the original
one-off `glm53_capability_test_launch.py`/`gpt56sol_capability_test_launch.py`
scripts used successfully, since they were standalone top-level scripts with
no prior `rtf.*` import) would not work reliably here — `rtf.security_agent`
is already resolved from the worktree the moment this package is imported.
`_frozen_worker.py` is invoked as a fresh subprocess instead, which has its
own `sys.modules` and safely imports the frozen checkout's code with zero
collision risk. It has an `--emit-tool-schemas` mode (no pipeline regen, no
investigation) that lets `preflight.py` test the *exact* tool schema list a
real run will send, from the same pinned checkout — not this worktree's
possibly-different copy of `tools.py`/`kernel.py`.

**Artifact layout.** Adapted to fit `run_security_agent_bundle`'s own
`scratch_root/security_agent/<case_id>/` convention rather than forcing an
artificial extra nesting level: each run's `trajectory.jsonl`, `state.json`,
`tokens.jsonl`, `evidence/`, and `cache/` live together under
`experiments/model_eval/<audit>/<property_slug>/<model_key>/security_agent/run_NNN/`,
with a `config.json` (model/config/pinned-checkout provenance/prompt hash/
timestamp) and `result.json` (verdict/cost/tokens/scoring) written alongside.
A `summary.json` at the model level aggregates all runs and the stopping-rule
outcome.

## 2. Reused components

| Component | Reused from | Notes |
|---|---|---|
| `ResponsesChatClient` | `rtf/security_agent/responses_client.py` | Used directly by `preflight.py` for its two live calls — no new HTTP client written. |
| `run_security_agent_bundle` | `rtf/security_agent/investigator.py` (frozen checkout) | Unchanged; the actual investigation entry point, called once per run from `_frozen_worker.py`. |
| Pipeline regeneration (`build_ethtrust_structural_properties`, `compile_evmbench_target_via_foundry`, `ProjectManifest.from_slither`, `build_full_property_pool`, `prepare_cluster_investigations_with_scope_boundary`, `generate_cluster_plan_md`) | `rtf/l11_investigation_grouping/*`, `rtf/l5_predicates/compile_helper.py` (frozen checkout) | Byte-identical call sequence to `glm53_capability_test_launch.py`/`gpt56sol_capability_test_launch.py`; verified via dry-run producing the identical `cluster_011`, 1,032-char trimmed plan, matching both prior scripts exactly. |
| Single-property plan trimming | Generalized from both prior scripts' hand-rolled closures | Pulled to a module-level, unit-testable function (`trim_plan_to_single_property`) with its own local copy of the `### \`property_id\`` regex, rather than importing from the frozen checkout for a trivial text operation. |
| Provider-reported cost/token accounting | `ResponsesChatClient`/`ClusterInvestigationState.token_usage` | No new pricing table — this project already treats OpenRouter's `usage.cost` as authoritative; the harness does not hardcode per-token prices anywhere. |
| Cluster-by-property-membership lookup | The fix already discovered during the GLM-5.3 test (cluster numbering is not stable across regeneration paths) | Carried forward unchanged into `_frozen_worker.py`. |

**Newly built:** the model registry, the preflight gate, the offline scenario
scorer, the generic CLI runner, the subprocess worker, and the stopping-rule
function (`evaluate_qualification`) — none of these existed before this task.
The pre-existing `rtf/security_agent/eval/ab_runner.py`/`ab_metrics.py` were
inspected first (Phase 1) and found to solve a *different* problem (Codex vs.
security-agent two-arm comparison, not N-model comparison within the fixed
kernel) — not duplicated, but their `ArmMetrics` dataclass pattern and
`input_fingerprint` fairness-check idea informed this harness's own
`config.json` provenance record.

## 3. Provider compatibility

| Model | API reachable | Model resolution | Tool calling | Structured output | Reasoning field | Known issues |
|---|---|---|---|---|---|---|
| DeepSeek V4 Pro | Yes | Confirmed (`deepseek/deepseek-v4-pro`, live ping returned real content) | Yes — emitted a real `conclude` tool call on the preflight prompt | N/A (native tool-calling path only, no `text.format` used) | Accepted (not rejected) | None blocking. One **non-gating** diagnostic flag: the preflight's own placeholder args (`evidence_ids: []`, `hypothesis_ids: []`) failed `ConcludeAction`'s `min_length=1` validators — a flaw in the preflight test prompt itself, not a DeepSeek compatibility problem (documented in `preflight.py`, never gates `passed`). |
| Kimi K3, MiniMax M3, Qwen3.6-35B-A3B | Not yet tested | OpenRouter slugs confirmed live via `/api/v1/models` (`moonshotai/kimi-k3`, `minimax/minimax-m3`, `qwen/qwen3.6-35b-a3b`) | — | — | — | Per Phase 11/18: only test if DeepSeek qualifies, or (as here) once it fails, per the stated candidate-progression order. |
| GPT-5.6 Sol | Already validated (prior session) | `openai/gpt-5.6-sol` | Yes | N/A | Yes | The one real, already-documented incompatibility this whole project has found: OpenAI/Azure's strict schema validator requires every tool parameter in `required`; GLM tolerates omission. Fixed once, permanently, in the frozen baseline checkout's `tools.py` (a wire-contract fix, not a tool-behavior change) — confirmed this fix is *already present* in the checkout this harness uses. |

The mandatory preflight gate (Phase 4) fetches the frozen checkout's real
13-read-tool + native-action-tool schema list via `--emit-tool-schemas`,
then sends the single most complex schema (`conclude`, with nested
evidence/hypotheses/properties/counterexample arrays) as a live compatibility
probe — this is deliberately the exact schema shape that broke for GPT-5.6
Sol originally, so a preflight pass here is a real, not superficial,
guarantee.

## 4. Deterministic test results

`rtf/security_agent/eval/test_model_eval_harness.py` — **26/26 passed.**
Full existing suite (`pytest rtf/security_agent/ -q`) — **240/240 passed**
(214 pre-existing + 26 new; zero regressions, zero existing files modified).

| # | Test | Result |
|---|---|---|
| 1 | Model registry resolves correct provider/model id (all 5 candidates + unknown-key rejection + tier ordering) | PASS |
| 2 | Secrets read from environment, never stored in artifacts (env-var precedence, key-file fallback, full-run artifact scan for the literal secret) | PASS |
| 3 | Dry-run performs zero paid investigator calls (`runs=3` requested, exactly one dry-run worker call made) | PASS |
| 4 | Single-property selection excludes all sibling properties (`trim_plan_to_single_property`, both keep- and reject-paths) | PASS |
| 5 | Ground-truth evaluation content never appears in investigator-facing harness files (static scan for `nextEpoch`/`BLOCK_EPOCH`/`H-02`/etc., deliberately excluding the ground-truth-aware `scenario_scorer.py`) | PASS |
| 6 | Stopping rule correctly resolves 0/3, 1/3, 2/3→BORDERLINE, 3/3, plus the 5-run escalation and the single-run control-check variant | PASS |
| 7 | A correct FAIL verdict for the *wrong* vulnerability counts as a miss (synthetic fixture matching GLM-5.3's real pattern) — and the converse, a correctly-traced right-vulnerability fixture counts as a hit | PASS |
| 8 | Provider schema incompatibility (simulated) stops before the real run — zero worker calls attempted | PASS |
| 9 | Cost/token/detection-rate aggregation arithmetic, including the qualification-rule interaction | PASS |
| 10 | GPT-5.6 Sol is representable in the registry without the harness ever writing into its legacy experiment directory | PASS |
| — | (Added after a live bug) Outer subprocess timeout carries a generous margin over the kernel's hardcoded 900s breaker | PASS |
| — | (Added after a live false positive) A raw-code excerpt quoting the buggy line, without the model asserting it's wrong, must NOT score as bug-traced | PASS |

## 5. DeepSeek qualification result

**Property:** `2024-01-canto` / `req-3-implement-as-documented::loc0` / `LendingLedger.update_market`
**Preflight:** PASSED (reachable, tool schema accepted, tool call emitted, reasoning field accepted).

| Run | Target bug found | Counterexample level | Tool calls | Decide calls | Input / output tokens | Cost | Wall-clock |
|---|---|---|---|---|---|---|---|
| 1 | **No** | 1 — VALID_NON_DISCRIMINATING (claim() NatSpec mismatch, same pattern as GLM-5.3) | 40 | 22 | 403,341 / 34,158 | $0.2509 | 587s (743s incl. subprocess overhead) |
| 2 | **No** | 1 — VALID_NON_DISCRIMINATING | 36 (+28 deduplicated) | 26 | 493,711 / 51,374 | $0.2847 | 801s (984s) |
| 3 | **No** | 1 — VALID_NON_DISCRIMINATING | 44 | 24 | 483,912 / 41,344 | $0.3069 | 706s (893s) |

**Stopping rule:** 0/3 → **FAIL_QUALIFICATION** (stop testing DeepSeek on this property, per the task's own decision rule — no further prompt tuning).

**Notable behavioral observations, all directly from the trajectories:**
- All 3 runs converge on the *identical* miss pattern GLM-5.2/5.3 already showed: fixating on the `claim()` NatSpec-vs-README documentation mismatch (a real, but different, finding) instead of constructing the epoch-boundary/heterogeneous-configuration scenario that exposes the actual `update_market` reward-misattribution bug.
- Run 2 recorded **28 deduplicated tool calls** against 36 real ones — the model repeatedly re-requested information it already had, a genuine efficiency problem distinct from the accuracy miss.
- Run 3 never reached a natural `conclude` — it was salvaged by the kernel's own forced-conclusion breaker after exceeding the $0.30 per-run cost ceiling (`forced_conclusion_not_conclude:max_cost_exceeded`).
- A run_002 evidence entry's `raw_excerpt` happened to verbatim-quote `update_market`'s buggy line (`nextEpoch = i + BLOCK_EPOCH`) — but only as incidental supporting code for its (unrelated, wrong) claim() finding, never asserting that formula was itself wrong. This was caught live while scoring these results and led to a real scorer fix (§6/§4) before the qualification verdict was finalized — see the note below.

**A scorer correctness note, disclosed for transparency:** while scoring these
three runs, two real bugs were found and fixed in `scenario_scorer.py` (a
bare-word "revert" false match inside a search-plan sentence, and — more
significantly — matching a Level-3 "mechanism traced" signal against *quoted
source code* rather than the model's own asserted claim). Both fixes were
verified against all 7 known runs (3 GLM-5.3 + 1 Sol + these 3 DeepSeek) before
being trusted; the corrected scoring is what's reported above, and a
regression test now locks in each fix (`test_model_eval_harness.py`). Without
the second fix, run 2 would have been miscounted as a hit — this is exactly
why Phase 7 specifies an *external*, ground-truth-aware scorer rather than
self-reported success, and why it was calibrated against real data before
being trusted for a verdict with real weight.

## 6. Comparison to baselines

| Model | Scaffold | Target detection | Notes |
|---|---|---|---|
| GLM-5.3 | Custom kernel | 0/3 | Miss pattern: claim() NatSpec mismatch, valid but non-discriminating scenarios. |
| GPT-5.6 Sol | Custom kernel | **1/1** | Control — independently constructed the discriminating epoch-boundary counterexample and named the exact causal mechanism in its own words. |
| **DeepSeek V4 Pro** | Custom kernel | **0/3** | Same miss pattern and same level (VALID_NON_DISCRIMINATING) as all 3 GLM-5.3 runs — not merely a similar failure rate, but the *identical* failure mode. |

DeepSeek does not reproduce Sol's Canto result. It also does not distinguish
itself from GLM-5.3 in *kind* of failure — both models converge on the same
documentation-mismatch finding and never construct a scenario that varies
configuration across an epoch boundary.

## 7. Economic result

| | GLM-5.3 (avg of 3) | GPT-5.6 Sol (1 run) | **DeepSeek V4 Pro (avg of 3)** |
|---|---|---|---|
| Cost/run | $0.0511 | $0.0535 | **$0.2808** |
| Input tokens | 81,796 | 33,367 | **460,321** |
| Output tokens | 4,531 | 1,672 | **42,292** |
| Tool calls | 4 | 6 | **40** |
| Target detections | 0/3 | 1/1 | 0/3 |
| Cost per correct detection | undefined (0 hits) | $0.054 | **undefined (0 hits)** |

**Relative cost vs. Sol:** DeepSeek is **~5.2x more expensive per run** than
GPT-5.6 Sol, and ~5.5x more expensive than GLM-5.3 — despite entering this
test as the "cheap candidate." This inverts the economic premise this
experiment set out to test: DeepSeek is neither cheaper nor more accurate
than the existing options on this task. The reason is volume, not per-token
price: DeepSeek used roughly **14x the input tokens and 25x the output
tokens** of Sol's single successful run, driven by the same kind of
inefficient, repetitive tool use (28 deduplicated calls in run 2) that also
shows up in its miss pattern.

`cost_per_correct_detection_usd` is undefined for both GLM-5.3 and DeepSeek —
neither model produced a single correct detection to divide by, which is
itself the headline economic result: on this property, DeepSeek costs more
per run and delivers zero successes, the worst combination on both axes this
experiment was designed to measure.

## 8. Recommendation

**DEEPSEEK FAILS — TEST KIMI K3 NEXT**

Preflight passed cleanly, all 3 runs completed and were scored with a
verified (twice-corrected, cross-checked against all 7 known runs) offline
scorer, and the result is an unambiguous 0/3 with the *same* failure
signature GLM-5.3 already showed — not a borderline or ambiguous case, and
not a harness/provider artifact (the one real infra issue found during this
run, an undersized subprocess timeout, was caught, fixed, and the affected
run was cleanly re-executed from scratch before any result was trusted).

## 9. Next step

Per Phase 11's candidate-progression order, test **Kimi K3** next using the
identical qualification protocol — same property, same 3-run gate, same
preflight-first discipline, same frozen baseline checkout. The harness
requires zero new code to do this: `python3 rtf/security_agent/eval/run_model_eval.py
--model kimi-k3 --audit 2024-01-canto-rootcause-fix-full-rerun --property
req-3-implement-as-documented::loc0 --runs 3` is the entire command (after a
`--dry-run` sanity check first, per the same discipline used for DeepSeek).
Not recommended before this: retrying DeepSeek with prompt/scaffold changes
(explicitly out of scope — Phase 10: "do not prompt-engineer DeepSeek after
failure") or expanding to the broader 4-5 property micro-benchmark (Phase 12
explicitly gates this behind a qualifying candidate, which DeepSeek is not).
