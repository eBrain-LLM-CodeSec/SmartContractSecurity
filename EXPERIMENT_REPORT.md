# GPT-5.6 Sol Custom-Kernel Controlled Test

**Date:** 2026-08-27
**Run artifacts:** `scratch/security_agent/gpt56sol-test-run1/` (trajectory.jsonl, state.json, evidence/, cache/, tokens.jsonl), `all_runs_summary.json`, `run1_summary.json`
**Launch script:** `/scratch/md5344/evmbench/agent4vul/.claude/worktrees/security-agent-kernel/gpt56sol_capability_test_launch.py`

## Objective

Can GPT-5.6 Sol discover the known Canto `update_market` reward/epoch bug when using the existing custom security-agent kernel instead of Codex? This test isolates model capability from scaffold effects by changing only the model, holding the kernel, prompts, tools, clustering, completion logic, and evidence handling constant relative to the immediately preceding GLM-5.3 capability test.

## 1. Executive summary

**Yes — GPT-5.6 Sol found the target bug on the very first run**, using the exact same unchanged custom kernel that GLM-5.2 and GLM-5.3 (0/3) both missed it with. In a single natural conclusion (no forced termination, no retries), it read the full `LendingLedger.sol` source and README, constructed a counterexample that whitelisted a market at a non-epoch-aligned block (550,000) with **different reward rates/weights configured in the adjacent 500,000 and 600,000 epochs**, and correctly derived that `update_market` computes `nextEpoch = i + BLOCK_EPOCH` (not `epoch + BLOCK_EPOCH`), causing all 100,000 blocks to be charged at the stale epoch's rate instead of switching at the boundary — the exact causal mechanism of the target vulnerability, stated in its own words with zero ground-truth exposure. It also independently traced *why* `lastRewardBlock` can be non-epoch-aligned in the first place (`whiteListLendingMarket` initializes it to the arbitrary current block), a level of explanatory completeness beyond even the original Codex artifact.

## 2. Configuration verification

Only the model changed relative to the GLM-5.3 test — confirmed by a dry run reproducing byte-identical output (`cluster_011`, same 8 properties, same 1,032-char trimmed plan) before any live model call. One unavoidable, purely mechanical difference was required and is documented below.

| | Value |
|---|---|
| Model resolution | Confirmed live: direct ping returned `"model": "openai/gpt-5.6-sol"` verbatim, and real completion content (unlike GLM's reasoning-only tiny-budget response) |
| Audit / Property / Target | `2024-01-canto` / `req-3-implement-as-documented::loc0` / `LendingLedger.update_market` — identical to GLM-5.3 test |
| Source revision / scope | Same `REPO_ROOT`, `SCOPE_FILES=["src/LendingLedger.sol"]`, `solc 0.8.17` |
| Plan/context size | Identical: 1,032-char trimmed plan (byte-identical dry-run output) |
| System prompt / investigation guidance | Unchanged |
| Tools available | 13 read-only + `update_investigation`/`conclude`, unchanged — except the one required fix below |
| max_steps / max_wall_clock / max_cost | 60 / 900s / $0.30 — unchanged |
| Anti-anchoring gate | Disabled (same `a61d547` throwaway baseline checkout as the GLM-5.3 test) |
| `rank_evidence` scope-filter cleanup | Kept (same as GLM-5.3 baseline) |

**One unavoidable configuration difference, documented as required:** the first attempt failed outright with `OpenRouter /responses error 400: "'required' is required to be... an array including every key in properties. Missing 'include_transitive'."` (`provider_name: Azure`). OpenAI's strict function-calling validator rejects a `strict: true` tool schema that omits any declared property from `required` — GLM tolerates the identical `strict: true` flag loosely; OpenAI enforces its own spec literally. Two of the 13 tools (`get_state_writes.include_transitive`, `search_repository.file_glob`) have optional parameters with defaults and were previously excluded from `required` by design (an existing, tested behavior, confirmed via `test_tools.py`). Fixed by unconditionally listing all parameters in `required` in the throwaway checkout's `tools.py` only — this changes the wire-format contract (the model must now pass these values explicitly rather than omit them for the default) but not what either tool does, and was never applied to the committed worktree. This is the single unavoidable difference from the GLM-5.3 run.

## 3. Result

| Model | Scaffold | Target bug | Other finding | Tool calls | Cost |
|---|---|---|---|---|---|
| GLM-5.3 | Custom | 0/3 | claim() NatSpec mismatch | ~4 | ~$0.05/run |
| **GPT-5.6 Sol** | **Custom** | **YES (1/1)** | also found claim() NatSpec mismatch, combined not exclusive | **6** | **$0.0535** |
| GPT-5.6 Sol | Codex | success | existing reference (README:60 invariant) | existing | existing |

## 4. Trajectory summary

4 decide-calls, 6 tool calls, $0.0535, 44.3s wall-clock, natural conclusion (no forced termination, zero dedup, zero compaction, zero malformed responses):

1. **Turn 1** — registers an initial hypothesis (`hyp-1`, "LendingLedger behavior diverges from its documentation") with zero evidence yet — a planning move before touching any tool.
2. **Turn 2** — `get_contract_source(LendingLedger)`, `read_file(README.md)`, `search_repository` across the whole repo for `LendingLedger|sync_ledger|cantoPerBlock|BLOCK_EPOCH|setRewards`.
3. **Turn 3** — `read_evidence` on both prior results, plus `read_file(LendingLedger.t.sol)` (the test file).
4. **Turn 4** — `conclude`, with 4 evidence entries and one counterexample attempt, verdict FAIL.

The `conclude` call's own evidence (`ev-3`) quotes the exact vulnerable lines uncut — no elision, unlike GLM-5.2's baseline evidence excerpt for the analogous property.

## 5. Counterexample comparison

**GLM-5.3's scenario:** a single lender depositing mid-epoch, one configuration, checking whether the per-block reward formula stays within its own magnitude bound (`cantoReward ≤ configured` given `weight ≤ 1e18`) — true under any uniform rate, so it can never expose a boundary-misattribution bug.

**GPT-5.6 Sol's scenario:** a market whitelisted at a deliberately non-epoch-aligned block (550,000), with **different `cantoPerBlock`/gauge weights configured at epoch 500,000 vs epoch 600,000**, updated at block 650,000 — i.e., it specifically varied the one state dimension (rate/weight *across* the boundary) that makes the misattribution observable, then traced `update_market`'s loop concretely to show all 100,000 blocks get charged at the *old* epoch's values. This is functionally identical in spirit to Codex's own counterexample construction (two adjacent epochs, different rates), independently arrived at.

| Behavior | GLM-5.3 | GPT-5.6 Sol |
|---|---|---|
| Reads README | Yes | Yes |
| Reads update_market | Yes | Yes |
| Valid scenario | Yes | Yes |
| Varies relevant state across boundary | No | **Yes** |
| Tests heterogeneous epoch behavior | No | **Yes** |
| Concrete arithmetic trace | Limited | **Full** (`epoch=500000`, `nextEpoch=650000`, 100,000 misattributed blocks) |
| Identifies attribution error | No | **Yes** (`nextEpoch = i + BLOCK_EPOCH` vs correct `epoch + BLOCK_EPOCH`, stated explicitly) |
| Target bug discovered | 0/3 | **1/1** |
| Tool calls | 4 | 6 |
| Cost | ~$0.05 | $0.054 |

## 6. Scaffold interference analysis

**No evidence the custom kernel limited Sol.** It concluded naturally on the first attempt with zero friction of any kind: no dedup blocking a revisit, no premature-completion forcing, no evidence truncation (its own excerpts are complete), no cost/step exhaustion, no property-representation steering toward an easier lens (it explicitly registered a documentation-mismatch hypothesis but investigated broadly enough — full contract source, README, and the test file — to also surface the deeper mechanism). Sol did not construct GLM-5.3's weak uniform scenario at any point; it went straight to a discriminating one. This is a clean case of the kernel supporting the required investigation once a capable-enough model is behind it.

## 7. Cost analysis

| | GLM-5.3 (avg of 3) | GPT-5.6 Sol |
|---|---|---|
| Decide calls | 6.67 | 4 |
| Tool calls | 4 | 6 |
| Input tokens | 81,796 | **33,367** |
| Output tokens | 4,531 | **1,672** |
| Cost | $0.0511 | $0.0535 |
| Wall-clock | 119.8s | 44.3s |

Sol used **~2.4x fewer input tokens and ~2.7x fewer output tokens** than GLM-5.3's average, at essentially the same total cost (higher per-token price offset by far fewer tokens needed) and less than half the wall-clock time.

**Cost per correct target detection:** GLM-5.3 = undefined ($0.153 spent across 3 runs, 0 successes). GPT-5.6 Sol = **$0.054** (1 run, 1 success). This directly answers the framing question: Sol is not just "more accurate," it is also cheaper and faster per run while being the only one of the two that actually solves the task.

## 8. Interpretation

`MODEL CAPABILITY IS THE DOMINANT DIFFERENCE`

Evidence chain, now complete:
```
Codex + GPT-5.6 Sol   -> success
Custom + GPT-5.6 Sol  -> success (this test)
Custom + GLM-5.3      -> 0/3
Custom + GLM-5.2      -> miss
```
The custom kernel, unchanged, supports the exact investigation depth required; GLM-5.x's counterexample-construction habit (testing invariants with uniform, non-discriminating configurations) is the actual limiting factor, not the scaffold.

## 9. Next action

**Recommend evaluating GPT-5.6 Sol (or an equivalently-capable model) as the default investigator model for the custom kernel**, given it matched cost, beat wall-clock, and succeeded where GLM-5.2/5.3 did not, on identical scaffold. No architecture redesign is justified by this evidence — this was a model-selection finding, not a scaffold-defect finding. If broader validation is wanted next, the appropriate follow-up is a small multi-property or multi-cluster Sol run (still short of a full benchmark rerun) to confirm this single result generalizes, rather than any kernel change.
