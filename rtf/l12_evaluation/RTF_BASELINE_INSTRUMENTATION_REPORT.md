# Grouped-investigation architecture: Phase 1 baseline

Records the CURRENT (pre-grouping) execution baseline — G0_UNGROUPED —
for every real audit run this session has zero-cost access to. Per the
plan: this configuration must never be removed; every later grouping
policy (G1/G2/G3, Phases 5+) is measured against it, not against itself.

**Method**: mined `pilot_summary.json`/`entry_XX_*_stage.json` from 5
real, already-completed, already-paid-for runs
(`rtf/l12_evaluation/baseline_extraction.py`) — **zero new Codex calls**,
zero new spend. No EVMbench ground truth was used to select or shape
this extraction; the same mechanical metrics are computed identically
for every audit.

New instrumentation added this phase (`rtf/l11_investigation_grouping/run_metadata.py`,
wired into `PipelineArtifacts`/`pilot5_driver.py`'s saved summaries):
`grouping_policy`, `cluster_size`, `planner_version`, `context_version`,
`investigation_prompt_version`, plus a per-entry `num_investigation_instances`
count distinguishing "requirements escalated" from "actual Codex calls
made" (identical today, will diverge once grouping is real). All 5 runs
below **predate this instrumentation** — their `grouping_policy` is
honestly recorded as unknown (`None`), not backfilled as an assumption,
though in every real case here it was in fact the 1-property-1-call
behavior that instrumentation would call `G0_UNGROUPED`.

## Baseline table

| Audit | Entries | Considered | Applicable | Escalated | Instances | Avg props/call | PASS | FAIL | INCONCLUSIVE | INSUFF_EVID | Explore-fail | Cost | Wall time |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `2025-04-forte` | 1 | 172 | 49 | 26 | 26 | 1.00 | 32 | 14 | 1 | 2 | 0 | $2.8364 | 27.6 min |
| `2024-08-phi` | 1 | 172 | 54 | 35 | 35 | 1.00 | 25 | 27 | 2 | 0 | 0 | $3.7350 | 37.9 min |
| `2024-01-canto` | 1 | 172 | 61 | 37 | 37 | 1.00 | 33 | 27 | 1 | 0 | 0 | $3.2354 | 34.0 min |
| `2026-01-tempo-feeamm` | 1 | 172 | 61 | 42 | 42 | 1.00 | 34 | 25 | 1 | 1 | 0 | $2.5426 | 29.7 min |
| `2025-01-liquid-ron` | 1 | 172 | 144 | 124 | 124 | 1.00 | 95 | 46 | 3 | 0 | 2 | $13.6056 | 88.7 min |

**Every row's `avg_properties_per_call` is exactly 1.00** — confirming
what the translation audit already established structurally: none of
these 5 real runs used instance expansion or any form of grouping, so
"escalated requirements" and "actual Codex calls" are identical. This
is the honest starting point the grouping architecture is measured
against — not a synthetic zero, a real one, from real paid runs.

## What this baseline does and doesn't establish

- **Establishes** real, per-audit reference points for cost, wall time,
  call count, and PASS/FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE
  distribution under strictly 1:1 (property = call) execution — the
  number every grouping policy must be compared against for calls saved,
  cost saved, and (critically) any recall/quality regression.
- **Does not yet establish** a true "properties" baseline in the plan's
  sense (Phase 2's atomic property metadata schema doesn't exist yet) —
  for these 5 historical runs, "escalated requirement" is used as the
  property proxy, which is accurate only because none of them had
  multi-clause-splitting or multi-location-expansion active. Once Phase
  2's property schema and Phase 5's G0 (now backed by real instance
  expansion, `rtf.l10_property_derivation`) are both active on a fresh
  run, `num_investigation_instances` will correctly exceed
  `investigations_escalated` for any multi-clause or multi-location
  requirement — a real forward-looking distinction this baseline
  correctly does NOT collapse.
- **Does not include per-investigation token counts.** These 5 runs
  predate any per-call token persistence beyond aggregate cost; only
  `fail_details` entries (FAIL findings) carry structured evidence.
  Token-level granularity (needed for the caching-analysis phase,
  Phase 12) will need to be captured going forward, not retrofitted
  onto this historical data.
- **`exploration_failed` is near-zero across the board** (0 for 4 of 5
  audits, 2 for liquid-ron) — consistent with the translation audit's
  own finding that the redesigned full-repo-access architecture rarely
  fails to complete an investigation; the interesting variance in this
  whole line of work is in what QUESTION got asked, not whether the
  agent could run at all.

## `G0_UNGROUPED` formalized

`rtf.l11_investigation_grouping.run_metadata.default_run_metadata()`
now names this exact behavior explicitly:

```python
RunMetadata(
    grouping_policy="G0_UNGROUPED", cluster_size=None,
    planner_version="none", context_version="none",
    investigation_prompt_version="ARM_G_PROMPT_v3",
)
```

Attached to every `PipelineArtifacts` a fresh `run_pipeline_e2e` call
produces (12 new tests, `test_run_metadata.py`); no existing caller's
behavior changed — this is pure, additive instrumentation.

## Next steps (Phase 2+)

Phase 2 builds the atomic property metadata schema this baseline's
"escalated requirement ≈ property" proxy will be replaced by. Phase 3
derives the semantic grouping taxonomy from EthTrust corpus text (not
from anything in this baseline). Neither phase should reference or be
shaped by the PASS/FAIL counts above — this table exists to be compared
against LATER, not to guide what gets built now.
