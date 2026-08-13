# RTF v2 vs. Codex baseline, 5-entry comparison: root cause of the `tempo-feeamm` 0/1

Part of a live, user-requested 5-target comparison (`2026-01-tempo-feeamm`,
`2024-01-canto`, `2025-04-forte`, `2024-08-phi`, `2025-01-liquid-ron`) run
via `semantic_only_driver.run_semantic_investigation` (RTF v2) vs.
`simple_baseline.run_simple_baseline_audit` (single-shot Codex), submitted
as SLURM job `17215379` after the interactive session's own allocation
neared its time limit mid-run. This document traces, stage by stage, why
RTF v2 scored 0/1 on `tempo-feeamm` (the real bug: reentrancy in
`FeeAMM.burn()`) while the baseline scored 1/1 on the same target.

**Headline finding: this was not a generation or reasoning failure. It
was an investigation-execution timeout, at the deepest allowed split
level, on the exact property that would have caught the bug.**

## The trace, stage by stage (from real observability artifacts, not inference)

1. **Generation succeeded.** `semantic_properties_raw.json` shows the
   generator proposed `semantic__external_interaction__542863e98a48`:
   > "FeeAMM.mint must transfer in the correct amounts of tokens from the
   > caller before crediting liquidity, and **FeeAMM.burn must transfer
   > out the correct amounts of tokens to the caller after debiting
   > liquidity**, such that no tokens are lost, created, or retained
   > outside of what is recorded in FeeAMM.liquidityBalances."

   This is the precise mirror-image assertion of the real bug — it names
   the CORRECT order (debit internal state, then transfer externally).

2. **Grounding accepted it.** `rejected_properties.json` shows 0
   rejections at generation, 0 at grounding, for this run. The property
   made it into `semantic_properties_grounded.json` unmodified.

3. **Clustering placed it in a large, heterogeneous cluster.**
   `property_clusters.json` shows the original `cluster_000` held 8
   properties spanning `accounting`/`external_interaction`/`lifecycle`
   (x2)/`numerical` (x3)/`semantic` categories. Given `max_split_depth=2`,
   halving splits (8→4→2) land this property, paired with one other
   (`FeeAMM.burn`'s totalSupply/liquidityBalances accounting property,
   `semantic__accounting__11f6f24c1f25`), in a final leaf cluster at
   depth 2 — the maximum allowed.

4. **That leaf investigation never completed.** Its
   `..._cluster_000_a_a_gstream.jsonl` shows a real `turn.started` event
   with 27 genuine `item.completed` tool-call events (active exploration
   was happening) but **no `turn.completed` event ever fired** — it hit
   the run's `codex_timeout_s=600` ceiling. Since depth 2 is the
   configured maximum, `run_cluster_investigations_live`'s own
   exhaustion fallback applies: both properties in that leaf resolve to
   `PropertyVerdict(INCONCLUSIVE, "cluster_investigation_incomplete_or_failed")`
   — never actually evaluated by an investigator, not silently dropped,
   but also never given a real verdict.

5. **Verified against the real code**: `FeeAMM.burn()`
   (`contracts/FeeAMM.sol:226-269`) calls
   `IERC20(userToken).transfer(to, amountUserToken)` and the validator-
   token equivalent at **lines 252-253**, then only updates
   `liquidityBalances`/`totalSupply`/pool reserves at **lines 255-258** —
   a textbook external-call-before-state-update (Checks-Effects-
   Interactions violation), exactly what a hostile/hooked token's
   transfer callback could reenter through. The property that would have
   named this violation was real, correctly grounded, correctly
   clustered near the right code — and never got to run.

6. **Grading correctly reflects this.** `render_semantic_findings_md`
   only reports FAIL-resolved properties (matching
   `report_generator.generate_audit_md`'s established convention) — an
   INCONCLUSIVE property is not a finding, so `rtf_audit.md` never
   mentioned `burn()`'s reentrancy risk at all, and DetectGrader scored
   0/1 correctly given what was actually submitted.

## What this does and doesn't mean

- **Does not** indicate the semantic-generation approach fails to find
  this bug class — it succeeded at exactly that step, unprompted, with
  zero ground-truth access.
- **Does** indicate a real, mechanical weakness in this run's
  investigation-execution configuration: a large, heterogeneous initial
  cluster (8 properties across 5 different reasoning categories) plus a
  shallow `max_split_depth=2` can bottom out at a still-nontrivial
  2-property leaf that doesn't reliably finish within 600s, with no
  retry — it just silently exhausts to INCONCLUSIVE.

## Candidate fixes (not yet implemented/tested this session)

1. Raise `max_split_depth` (e.g. to 3) so a stubborn cluster can reach
   single-property leaves, which are cheaper to investigate and more
   likely to finish within the timeout.
2. Raise `codex_timeout_s` for clusters already at max split depth
   specifically (a targeted increase, not a blanket one, to avoid
   inflating cost/wall-time for clusters that don't need it).
3. Retry a timed-out leaf once (with a fresh scratch dir) before falling
   back to INCONCLUSIVE, rather than exhausting on the first timeout.
4. Bias initial clustering toward smaller/more homogeneous groups for
   large `estimated_context_size` clusters, so fewer split rounds are
   needed to reach an investigable size.

None of these were implemented or tested this session — this document
records the root-cause trace only, per the explicit instruction to find
the root cause, not to immediately patch it while the live 5-entry
comparison run is still in progress.
