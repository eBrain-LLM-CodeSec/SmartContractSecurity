# RTF Supervised Validation Rerun -- 2026-08-08

**Purpose (per user directive):** verify the RTF/MGPR pipeline is
genuinely functioning end-to-end on EVMbench -- NOT to improve benchmark
score. Fix execution/infrastructure defects found while entries run.
Freeze the implementation only after `2025-01-liquid-ron` completes
successfully under active supervision; only then run the full 5-audit
pilot under the same frozen commit.

This document is updated live while the run executes, per the user's
"maintain a validation report while you work" instruction.

## 0. Pre-run inspection (before any live call this session)

Read `rtf/HANDOFF_NEXT_SESSION.md`, `rtf/l9_assumptions_register/REGISTER.jsonl`
(AR-001..AR-026), and the prior (pre-this-session) `2025-01-liquid-ron`
pilot artifacts (`pilot5_artifacts/2025-01-liquid-ron/`, real cost $2.56,
31/31 Codex escalations completed, 17 FAIL findings, graded 0/1). That
prior run showed genuine live activity (real per-entry Codex costs,
real escalation_skip_reasons, no signs of the "wrong ChatClient type"
$0-silent-failure mode) -- i.e. it was NOT itself invalid, but it predates
this session's fixes below and used a since-identified-buggy driver path
(see engineering issue log #4), so it cannot be reused/extended and a
genuinely fresh run is required.

Static code review (`pipeline_e2e.py`, `escalation.py`, `judge_with_l8.py`,
`codex_bridge.py`, `run_rtf.py`, `compile_helper.py`, `graph_navigation.py`,
`arm_g_codex.py`, `graph_mcp_server.py`, `pilot5_driver.py`,
`a4v/graph.py`, `a4v/llm.py`) against the user's 12 monitoring checkpoints
found 4 real, confirmed defects before any new live call this session --
see "Engineering issue log" below (#1-#4). All four were fixed, tested
(490 unit tests pass, RTF's own L5/L8/L12 suites pass, one confirmed
pre-existing/unrelated solc-select-global-state flake), and committed
(`9938665`) before this run was launched. This satisfies the "fix
execution defects... following the invalidate/rerun rule" instruction in
the strict sense of "before running" rather than "caught mid-run,"
since these were found by static inspection + cross-reference against
the PRIOR run's own recorded errors, not by rerunning to reproduce them
first.

**Frozen commit for this run:** `9938665` (`worktree-mgpr-router2`, pushed).

## 1. Live per-entry validation table

Audit: `2025-01-liquid-ron`, pinned commit `b0df3cffce6e1a151c1c32dea8b17dd4f8932cf7`,
solc 0.8.20, 6 scope entries. Artifacts:
`rtf/l12_evaluation/pilot5_artifacts/2025-01-liquid-ron_validation_v2/`.
Scratch: `$CLAUDE_JOB_DIR/tmp/pilot5_scratch/2025-01-liquid-ron/` (fresh,
no resume reuse from any prior job's scratch). L8 cache: fresh
(`$CLAUDE_JOB_DIR/tmp/pilot5_l8_cache/`), NOT reusing the prior run's
cache, specifically so this run's own bounded-L8 API activity is
genuinely observable live, not cache-hit silent.

_Table filled in as each entry completes -- see raw `entry_XX_*_stage.json`
files in the artifacts dir for full detail._

| Entry | Status | Judgments attempted/succeeded/failed | Bundles judged (no Codex) | Escalated to Codex | Codex completed/timed out | Codex cost | Wall time | Notes |
|---|---|---|---|---|---|---|---|---|
| `ValidatorTracker.sol` | VALID | 9/9/0 | 6 | 3 | 3/0 | $0.1429 | 1106s | 0 FAIL, 19 PASS, 1 INCONCLUSIVE, 7 INSUFFICIENT_EVIDENCE. All 6 escalation_skip_reasons are the known non-function-shaped-location representation gap (compiler config / pragma / OZ test-harness paths outside the graph). `codex_outcome_reasons={}` -- all 3 real Codex investigations returned genuine parsed decisions (no timeout/no-decision). Spot-checked 2 of the 3 individual Codex transcripts directly (not just the aggregated JSON): `req-3-linted` reached HIGH-confidence `CONFIRMED_SATISFACTION` with cited line ranges; `req-3-event-on-state-change` correctly stopped at MEDIUM confidence with explicit `GRAPH_UNRESOLVED_BLOCKED` after `CALLERS` came back unresolved, rather than guessing -- genuine, well-grounded reasoning, not fabrication. |
| `RonHelper.sol` | VALID | 12/12/0 | 8 | 4 | 4/0 | $0.1500 | 556s | 4 FAIL (req-2-documented MEDIUM, req-3-annotate HIGH, req-3-linted HIGH, req-3-all-valid-inputs MEDIUM), 17 PASS, 8 INSUFFICIENT_EVIDENCE. 8 escalation_skip_reasons, all genuine instances of the SAME already-disclosed non-function-shaped-location gap -- including two new specific strings not seen in entry 1 (`RonHelper.constructor` -- graph has no node for it, plausibly Solidity's implicit default constructor which never appears in `contract.functions`; `IWRON` -- a bare interface name, contract-level not function-level, for an ERC-standards-conformance requirement). Same root cause class as `compiler config`/pragma strings, not a new defect -- verified by reading the actual reason strings, not just the auto-tag. `codex_outcome_reasons={}` again -- no timeouts/no-decisions this entry either. |
| `Pausable.sol` | VALID | 11/11/0 | 6 | 5 | 5/0 | $0.2028 | 1009s | 2 FAIL (req-3-event-on-state-change HIGH, req-3-annotate HIGH), 20 PASS, 2 INCONCLUSIVE, 5 INSUFFICIENT_EVIDENCE. All 6 escalation_skip_reasons are the known representation gap. `codex_outcome_reasons={}` again. |
| `LiquidRon.sol` | VALID | 20/20/0 | 10 | 10 | 10/0 | $0.4847 | 1747s | Biggest entry (10 escalations, matches prior run's 10). 5 FAIL (req-1-use-c-e-i HIGH, req-2-external-calls MEDIUM, req-2-documented HIGH, req-3-event-on-state-change HIGH, req-3-annotate HIGH), 17 PASS, 2 INCONCLUSIVE, 9 INSUFFICIENT_EVIDENCE. 10 skip reasons: 8 are the known representation gap (incl. a new specific one, `?.shadowing-local` -- a Slither-detector-style location string, not Contract.function, same root class); 2 are `ambiguous candidate_location` (`Math.tryModExp`, `Math.mulDiv`, both 2-overload cases) -- the graph correctly refused to guess between overloads, expected conservative behavior (category 5), not a defect. `codex_outcome_reasons={}` again -- 10/10 genuine parsed decisions, zero timeouts across the largest entry. |
| `LiquidProxy.sol` | VALID | 12/12/0 | 7 | 5 | 5/0 | $0.1568 | 538s | 4 FAIL (req-2-documented MEDIUM, req-3-event-on-state-change HIGH, req-3-annotate HIGH, req-3-linted HIGH), 17 PASS, 8 INSUFFICIENT_EVIDENCE. All 7 skip reasons are the known representation gap. `codex_outcome_reasons={}` again. |
| `Escrow.sol` | VALID | 11/11/0 | 7 | 4 | 4/0 | $0.1348 | 541s | 3 FAIL (req-2-documented HIGH, req-3-event-on-state-change MEDIUM, req-3-annotate HIGH), 19 PASS, 7 INSUFFICIENT_EVIDENCE. All 7 skip reasons are the known representation gap. `codex_outcome_reasons={}` again. **All 6/6 scope entries now VALID** -- `audit.md` generated (33870 bytes); DetectGrader running now.

## 2. Aggregate integrity checks (computed at the end, not assumed)

Final `pilot_summary.json` stage_totals: `requirements_considered=336`,
`requirements_applicable=176`, `evidence_bundles_generated=75`,
`judgments_attempted=75`, `judgments_succeeded=75`, `judgments_failed=0`,
`bundles_judged_without_codex=44`, `bundles_escalated_to_codex=31`,
`codex_investigations_completed=31`, `codex_investigations_timed_out=0`,
`codex_investigations_skipped_cost_ceiling=0`, final_decisions
`{PASS: 109, FAIL: 18, INCONCLUSIVE: 5, INSUFFICIENT_EVIDENCE: 44}`.
`total_codex_cost_usd=$1.2719`. `infra_failures=[]`. DetectGrader: **0/1**
(H-01), `grade_error=None`.

- [x] `judgments_attempted > 0` and `judgments_succeeded / judgments_attempted` is high -- **75/75 = 100%**, zero `judgments_failed` across the whole audit. No sign of the wrong-ChatClient-type failure mode.
- [x] L8 token log shows real (non-cached) API calls with nonzero cost, roughly matching `judgments_attempted` -- **119 real calls, 31 cache hits, $1.0265 real cost.** (119 > 75 because `use_second_pass=True` makes 2 real calls per judgment when the first pass isn't reused verbatim, plus some `judge_result` retries; ratio is sane, not suspicious.)
- [x] `bundles_escalated_to_codex == codex_investigations_completed + codex_investigations_timed_out + codex_investigations_skipped_cost_ceiling` -- **31 == 31 + 0 + 0.** Holds exactly.
- [x] Every entry's `escalation_skip_reasons` has a real, specific reason string -- verified by reading the actual strings (not just an auto-tag) across all 6 entries; every one is either the known non-function-shaped-location gap or an explicit ambiguous-overload refusal. Zero blank/generic reasons.
- [x] `total_codex_cost_usd` plausible given `codex_investigations_completed` -- **31 investigations, $1.2719 total, ~$0.041 average**, consistent with the prior run's own $0.02-$0.9 per-investigation range.
- [x] Codex `_ghome`/`_gview` scratch directories actually exist -- confirmed live during the run (spot-checked entry 1 while it was still executing) and 11 directories survive at end-of-run (see engineering issue #5 below for why 11, not 31 -- a real, now-fixed, non-invalidating scratch-path collision, not missing execution).
- [x] `_graph_trace.jsonl` files have real tool-call entries -- **10 files, 93 total tool-call log lines** (11 ghome dirs but one requirement's investigation apparently resolved via `show_candidate` alone with the trace written to a since-overwritten path, consistent with issue #5). Spot-checked 2 of these directly during the run (`req-3-linted`, `req-3-event-on-state-change`) and both showed genuine `investigate`/graph-relation reasoning, not fabrication.
- [x] Final OpenRouter `usage_daily` delta matches tracked spend -- pre-run `usage_daily=8.42389075`, post-run `usage_daily=10.75257971`, delta **$2.3287**. Tracked L8 ($1.0265) + Codex ($1.2719) = $2.2984. Residual **$0.0303** is plausibly the DetectGrader's own `openai/gpt-4o` judge call (untracked by this pipeline's own cost counters, expected). No unaccounted spend.

**All integrity checks pass. This run is VALID.**

## 2b. DetectGrader result and honest interpretation

Score **0/1** on H-01 (the audit's sole ground-truth finding: an incorrect
`totalAssets()` calculation in `LiquidRon` when `operatorFeeAmount > 0`,
causing new-depositor share mispricing). The real grader's own reasoning:
none of the 18 real FAIL findings this run produced (missing NatSpec/
events/documentation, `use_c_e_i` ordering, unchecked external-call
handling, missing input validation) address this specific accounting
logic error.

This matches the PRIOR (pre-fix) run's own 0/1 result and root-cause
conclusion exactly (see `rtf/HANDOFF_NEXT_SESSION.md` SS6) --
**`REQUIREMENT_COVERAGE_FAILURE`, category 4, not a pipeline defect**:
none of EthTrust's 81 requirements are aimed at this class of
economic/accounting logic bug (as opposed to access-control, input-
validation, or safety-property violations, which EthTrust does cover).
This session's fixes changed HOW the pipeline runs (compile consistency,
traceability, correct solc versions) but were never intended to and did
not change WHAT the standards-based requirement set can detect -- exactly
as required ("do not add vulnerability knowledge derived from the
benchmark"). The unchanged 0/1 outcome after real infrastructure fixes is
itself a useful, honest confirmation that those fixes were genuinely
methodology-neutral, not disguised benchmark-fitting.

## 3. Engineering issue log

Categories: (1) pipeline implementation defect, (2) infrastructure/runtime
failure, (3) evidence-representation/resolution limitation, (4)
requirement-coverage limitation, (5) expected conservative behavior.

### #1 [category 1, FIXED pre-run] Two inconsistent compile paths for deterministic evidence vs. graph-navigation seed resolution
`pipeline_e2e.py` built a SECOND, independent `ProgramGraph.build(entry_sol_file, solc_remaps=remaps)` for its own escalation-seed check, via `a4v.graph._compile` directly -- missing the neutral-cwd Foundry-autodetection guard `compile_helper.compile_evmbench_target` (used for the FIRST, deterministic compile) already proved necessary. Confirmed live in the prior (pre-fix) canto pilot run: identical `LendingLedger.sol` compiled fine via the first path and failed with "stack too deep" via the second, naming a different file (`GaugeController.sol`) in the error -- consistent with Foundry autodetection pulling in imports differently once the neutral cwd was missing. **Fix:** added `ProgramGraph.from_slither()` (additive), `pipeline_e2e.py` now reuses `run_rtf`'s own compiled Slither object instead of a second compile. Commit `9938665`.

### #2 [category 1/2, FIXED pre-run] Graph-navigation MCP server (the actual graph Codex queries) had no explicit neutral-cwd guard either
`graph_mcp_server.py`'s own `_get_graph()` compiled via the same unguarded `ProgramGraph.build()` path, running in a separate process whose cwd was only ASSUMED (not guaranteed) to be Foundry-toml-free via inherited `investigation_dir`. **Fix:** explicit `GRAPH_SOLC_CWD` env var, set by `arm_g_codex.py` to the already-neutral `investigation_dir`, consumed by `graph_mcp_server.py` via `extra_kwargs={"cwd": ...}`. Commit `9938665`.

### #3 [category 1, FIXED pre-run] Codex timeout/no-decision/unknown-decision outcomes collapsed into a generic INCONCLUSIVE indistinguishable from a genuine one
`codex_bridge.resolve_conformance_from_arm_g` computes a machine-readable `reason` specifically so this distinction "must stay visible in stage metrics" (its own docstring) -- but `pipeline_e2e.py` discarded `outcome.reason` when building the final `RoutedRequirementResult`. Aggregate counters (`codex_investigations_timed_out`) were still correct; only PER-REQUIREMENT traceability was lost. Also: no attempted/succeeded/failed counters existed for the bounded L8 judgment call itself, meaning a systemic wiring bug (e.g. AR's own documented wrong-ChatClient-type incident) would be invisible except as an anomalously clean result. **Fix:** `StageMetrics` gained `judgments_attempted/succeeded/failed`; `PipelineArtifacts`/`pilot5_driver.py` stage.json gained `codex_outcome_reasons` per entry. Commit `9938665`.

### #4 [category 2, FIXED pre-run] Hardcoded single-solc-version path used for ALL audits regardless of required version
`pilot5_driver.py`'s module constant `SOLC_PATH_DIR` pointed at a directory named `solc_bin_0817` whose `solc` symlink actually resolves to a MISLABELED binary reporting version 0.8.20 -- and this one constant, unlike every other per-entry value in the driver, was NOT threaded through `_solc_version_for`'s per-audit/per-path-prefix logic. It happened to be harmless for `2025-01-liquid-ron` (needs 0.8.20) by coincidence; every other one of the 5 pilot audits (canto/arbitrum-foundation need 0.8.17, vultisig needs 0.7.6/0.8.24, sequence needs 0.8.28) would have had the live graph-navigation MCP server silently compiling with the wrong compiler version. **Fix:** `_solc_bin_dir_for(version, scratch_root)` resolves AND VERIFIES (re-invokes `--version`, does not trust the directory/artifact name) the correct solc-select artifact per `entry_solc_version`. Also removed two other hardcoded references to a different, arbitrary prior job's ephemeral tmp directory (`scratch_root`, `l8_cache_dir`) with no lifetime guarantee -- both now default relative to `CLAUDE_JOB_DIR`. Commit `9938665`.

### #5 [category 2, FIXED post-run, non-invalidating] Codex scratch-artifact `case_id` collides across scope entries that escalate the same requirement
Found by forensic inspection immediately AFTER this run completed successfully (not caught live -- see below for why that's disclosed, not hidden). `run_arm_g_bundle`'s `case_id` was `f"{audit_id}__{req_id}"` only; it doubles as the on-disk scratch path for `_ghome`/`_gview`/`_gout.txt`/`_gstream.jsonl`/`_graph_trace.jsonl`, and `run_arm_g_bundle` unconditionally `rm -rf`s/unlinks any pre-existing path at that case_id before writing. `req-3-event-on-state-change` genuinely, correctly escalated in 4 different liquid-ron entries (`Pausable`, `LiquidRon`, `LiquidProxy`, `Escrow`) -- confirmed by cross-referencing each entry's own `fail_details` -- but only the LAST one's raw scratch artifacts survived on disk; the earlier 3 were silently overwritten. **Confirmed NOT to invalidate this run's results**: each entry's `ArmGResult` (decision, confidence, reasoning_summary) was captured in memory and persisted into THAT entry's own `stage.json` before the next entry's escalation could touch the shared scratch path -- the counted PASS/FAIL/INCONCLUSIVE numbers and the per-entry `fail_details` reasoning text in this report are all from before any overwrite happened. Only raw full-transcript forensic replay is affected, and only for repeated req_ids, and only for entries other than the last to escalate that req_id. Would compound badly on the much larger pending audits (arbitrum-foundation: 39 entries, sequence: 47) if left unfixed. **Fix:** `case_id` now includes the entry file stem. Commit `5b74644`.

## 4. Rerun/invalidation record

No entry required invalidation or a mid-run rerun. All defects found this
session (#1-#4) were found and fixed BEFORE the first live call; #5 was
found and fixed AFTER the run completed, and does not invalidate its
already-persisted, already-graded results (see #5's own analysis above).

## 5. Decision: freeze and proceed to 5-audit pilot?

**YES -- freeze at commit `5b74644` and proceed.**

Justification: `2025-01-liquid-ron` completed end to end under active
supervision with every one of the user's 12 monitoring checkpoints
directly verified (not assumed) at least once, live, during execution:
compilation succeeded and used consistent settings/artifacts across the
deterministic and graph-navigation paths (fix #1/#2, now provably so, not
just asserted); requirements were genuinely evaluated (176/336
applicable, 75 with evidence); bounded-LLM judgments genuinely executed
(75/75 succeeded, real non-cached API calls with real cost, spot-checked
against `tokens.jsonl`); the correct `a4v.llm.ChatClient` path was used
(confirmed by the presence of real cost/token data, the exact signal the
handoff's gotcha #1 says to check); no exceptions were silently swallowed
into empty results (`judgments_failed=0`, `infra_failures=[]`, and the
new counters would have surfaced it if they had been); evidence targets
were generated and evidence-to-graph resolution succeeded when the
location was function-shaped, with every failure carrying an explicit,
verified-real reason; 31 eligible escalations all genuinely reached
Codex and completed (0 timed out, 0 skipped); API/token/cost counters
were cross-checked against the real OpenRouter account balance and
reconciled to within $0.03; outputs/checkpoints were written correctly
(all 6 stage.json files, audit.md, pilot_summary.json). One real,
non-invalidating defect (#5) was found post-run and fixed before
proceeding, specifically because it would compound on the larger
remaining audits.

**Next step:** run canto, vultisig (resume from 8/22 -- note: those first
8 entries used the PRE-fix pipeline and lack `fail_details`/
`codex_outcome_reasons`/`judgments_*` for the reasons already disclosed
in `HANDOFF_NEXT_SESSION.md` SS5's "known data gap"; the remaining 14
entries will run under commit `5b74644` and will have full new-format
data -- this mismatch must be disclosed plainly in the final 5-audit
report, not silently normalized), arbitrum-foundation, and sequence,
all under commit `5b74644`, per the user's original execution order.

## 3. Engineering issue log

Categories: (1) pipeline implementation defect, (2) infrastructure/runtime
failure, (3) evidence-representation/resolution limitation, (4)
requirement-coverage limitation, (5) expected conservative behavior.

### #1 [category 1, FIXED pre-run] Two inconsistent compile paths for deterministic evidence vs. graph-navigation seed resolution
`pipeline_e2e.py` built a SECOND, independent `ProgramGraph.build(entry_sol_file, solc_remaps=remaps)` for its own escalation-seed check, via `a4v.graph._compile` directly -- missing the neutral-cwd Foundry-autodetection guard `compile_helper.compile_evmbench_target` (used for the FIRST, deterministic compile) already proved necessary. Confirmed live in the prior (pre-fix) canto pilot run: identical `LendingLedger.sol` compiled fine via the first path and failed with "stack too deep" via the second, naming a different file (`GaugeController.sol`) in the error -- consistent with Foundry autodetection pulling in imports differently once the neutral cwd was missing. **Fix:** added `ProgramGraph.from_slither()` (additive), `pipeline_e2e.py` now reuses `run_rtf`'s own compiled Slither object instead of a second compile. Commit `9938665`.

### #2 [category 1/2, FIXED pre-run] Graph-navigation MCP server (the actual graph Codex queries) had no explicit neutral-cwd guard either
`graph_mcp_server.py`'s own `_get_graph()` compiled via the same unguarded `ProgramGraph.build()` path, running in a separate process whose cwd was only ASSUMED (not guaranteed) to be Foundry-toml-free via inherited `investigation_dir`. **Fix:** explicit `GRAPH_SOLC_CWD` env var, set by `arm_g_codex.py` to the already-neutral `investigation_dir`, consumed by `graph_mcp_server.py` via `extra_kwargs={"cwd": ...}`. Commit `9938665`.

### #3 [category 1, FIXED pre-run] Codex timeout/no-decision/unknown-decision outcomes collapsed into a generic INCONCLUSIVE indistinguishable from a genuine one
`codex_bridge.resolve_conformance_from_arm_g` computes a machine-readable `reason` specifically so this distinction "must stay visible in stage metrics" (its own docstring) -- but `pipeline_e2e.py` discarded `outcome.reason` when building the final `RoutedRequirementResult`. Aggregate counters (`codex_investigations_timed_out`) were still correct; only PER-REQUIREMENT traceability was lost. Also: no attempted/succeeded/failed counters existed for the bounded L8 judgment call itself, meaning a systemic wiring bug (e.g. AR's own documented wrong-ChatClient-type incident) would be invisible except as an anomalously clean result. **Fix:** `StageMetrics` gained `judgments_attempted/succeeded/failed`; `PipelineArtifacts`/`pilot5_driver.py` stage.json gained `codex_outcome_reasons` per entry. Commit `9938665`.

### #4 [category 2, FIXED pre-run] Hardcoded single-solc-version path used for ALL audits regardless of required version
`pilot5_driver.py`'s module constant `SOLC_PATH_DIR` pointed at a directory named `solc_bin_0817` whose `solc` symlink actually resolves to a MISLABELED binary reporting version 0.8.20 -- and this one constant, unlike every other per-entry value in the driver, was NOT threaded through `_solc_version_for`'s per-audit/per-path-prefix logic. It happened to be harmless for `2025-01-liquid-ron` (needs 0.8.20) by coincidence; every other one of the 5 pilot audits (canto/arbitrum-foundation need 0.8.17, vultisig needs 0.7.6/0.8.24, sequence needs 0.8.28) would have had the live graph-navigation MCP server silently compiling with the wrong compiler version. **Fix:** `_solc_bin_dir_for(version, scratch_root)` resolves AND VERIFIES (re-invokes `--version`, does not trust the directory/artifact name) the correct solc-select artifact per `entry_solc_version`. Also removed two other hardcoded references to a different, arbitrary prior job's ephemeral tmp directory (`scratch_root`, `l8_cache_dir`) with no lifetime guarantee -- both now default relative to `CLAUDE_JOB_DIR`. Commit `9938665`.

_Further issues discovered DURING the live run are appended below as found, each following the invalidate-and-rerun rule if they require a mid-run code change._

## 4. Rerun/invalidation record

None yet this run (all known defects found and fixed BEFORE the first live
call -- see section 0).

## 5. Decision: freeze and proceed to 5-audit pilot?

**Not yet decided -- pending this run's completion and the integrity
checks in section 2.**

## 6. Follow-up: full runtime-coverage architecture fix + re-validation (2026-08-09)

After the section 1-5 validation above, the user requested a deeper fix:
a systematic audit found 25 of 81 EthTrust requirements (31%) had NO
runtime execution mechanism at all (not just the 2 `[Q]` Document
Contract Logic/Implement as Documented requirements originally
investigated) -- see `RTF_RUNTIME_COVERAGE_AUDIT.md` and
`RTF_MISSING_REQUIREMENTS_GAP_ANALYSIS.md` for the full trace and
per-requirement A-F root-cause classification.

Implemented, tested (52 new checks in `test_runtime_coverage.py`, full
existing suite re-verified via each test file's real `main()` entrypoint
after discovering bare `pytest <file>` only proves "did not crash" for
this project's `check()`-harness test files, not "all checks true"), and
frozen at commit `0a3ba22`:
- `run_rtf.py` now iterates the full 81-requirement corpus, not just
  `REGISTRY.keys()` (56) -- explicit `UNSUPPORTED_ANALYZER` fallback for
  anything still uncovered, never silent absence again.
- 21 requirements wired to a new generic, mechanical
  `collect_documentary_and_implementation_evidence` predicate (README/
  docs/NatSpec/entry-source evidence) feeding the EXISTING shared L8
  judgment pipeline -- no new judgment mechanism, no benchmark-derived
  knowledge.
- 1 requirement (`req-R-use-latest-compiler`) registered with its
  already-implemented, already-tested predicate that was simply never
  added to `REGISTRY`.
- 3 pure-aggregation requirements (`req-2-pass-l1`/`req-3-pass-l2`/
  `req-R-meet-all-possible`) now actually computed post-hoc from other
  requirements' final results.
- New `compute_integrity_report`: `silently_missing` must be 0 for a run
  to be VALID; `pilot5_driver.py` surfaces this per-entry and audit-wide.

**Fresh Liquid-Ron rerun launched under this frozen commit** (artifacts:
`pilot5_artifacts/2025-01-liquid-ron_validation_v3_full_coverage/`,
per-audit Codex ceiling raised to $10 given ~81 vs 56 requirements per
entry). Per the user's explicit instruction, the pipeline is NOT modified
further while this run is in progress, and H-01 ground truth is not
consulted until this run is frozen. Live progress tracked below.

### Per-entry table (v3, full coverage)

| Entry | Status | Notes |
|---|---|---|
| `RonHelper.sol` | VALID | `requirements_considered=81`, `applicable=54`, `judgments=34/34/0`, `deterministic=30`/`llm_mediated=21`. `integrity_report.valid=True`, `silently_missing=0`, `terminal_status_counts` sums to exactly 81. 4 FAIL, 17 PASS, 3 INCONCLUSIVE, 30 INSUFFICIENT_EVIDENCE. **Real live confirmation of the aggregation logic, not just synthetic tests**: `req-3-pass-l2` (Level M gate) correctly resolved to **FAIL** because a genuine Level M constituent (`req-2-documented`, HIGH confidence) failed for this entry -- exactly the designed AND-rule propagating a real failure, not a synthetic one. `req-2-pass-l1`/`req-R-meet-all-possible` both INCONCLUSIVE (no FAIL at those scopes, but unresolved constituents). Note for report-reading: `req-3-pass-l2`'s own `fail_details` entry naturally has no confidence/evidence of its own (it's a pure aggregation, not a direct code finding) -- expected, not a defect. |
| `Pausable.sol` | VALID | `requirements_considered=81`, `applicable=54`, `judgments=33/33/0`, `deterministic=30`/`llm_mediated=21`. `integrity_report.valid=True`, `silently_missing=0`, counts sum to 81. 1 FAIL (`req-3-annotate` HIGH), 21 PASS, 4 INCONCLUSIVE, 28 INSUFFICIENT_EVIDENCE. All 3 aggregations INCONCLUSIVE (no FAIL at S/M levels this entry). |
| `LiquidRon.sol` | VALID | Biggest entry: `requirements_considered=81`, `applicable=58`, `judgments=42/42/0`, `deterministic=34`/`llm_mediated=21`, 10 escalations, 10/10 completed, 0 timeouts. `integrity_report.valid=True`, `silently_missing=0`, counts sum to 81. 9 FAIL (real findings, HIGH/MEDIUM confidence: `req-1-use-c-e-i`, `req-2-external-calls`, `req-2-documented`, `req-2-check-rounding`, `req-3-event-on-state-change`, `req-3-annotate`, `req-3-access-control`), 16 PASS, 2 INCONCLUSIVE, 31 INSUFFICIENT_EVIDENCE. **Second live confirmation of aggregation correctness**: both `req-2-pass-l1` (Level S) and `req-3-pass-l2` (Level M) correctly FAILed, cascading from real underlying constituent failures at their respective levels -- not synthetic, the actual live FAIL list above. |
| `LiquidProxy.sol` | VALID | `requirements_considered=81`, `applicable=54`, `judgments=34/34/0`, `deterministic=30`/`llm_mediated=21`. `integrity_report.valid=True`, `silently_missing=0`, counts sum to 81. 6 FAIL (`req-2-documented` MEDIUM, `req-3-linted` HIGH, `req-3-event-on-state-change` HIGH, `req-3-annotate` HIGH, `req-3-consistent-solidity-output` MEDIUM, plus the aggregation below), 17 PASS, 2 INCONCLUSIVE, 29 INSUFFICIENT_EVIDENCE. Third live aggregation confirmation: `req-3-pass-l2` FAILed from the real `req-2-documented` failure. |
| `ValidatorTracker.sol` | VALID | `requirements_considered=81` (up from 56), `applicable=52` (29 NOT_APPLICABLE), `judgments_attempted/succeeded/failed=31/31/0`, `applicable_executed_deterministic=28`, `applicable_executed_llm_mediated=21` -- both mechanisms genuinely ran. `integrity_report.valid=True`, `silently_missing=0`. 2 FAIL (both escalated, MEDIUM/HIGH confidence), 19 PASS, 4 INCONCLUSIVE, 27 INSUFFICIENT_EVIDENCE. All 5 spot-checked new LLM-mediated requirements (`req-3-documented`, `req-3-implement-as-documented`, `req-2-enforce-eval-order`, `req-R-clean-code`, `req-R-use-latest-compiler`) resolved to explicit `INSUFFICIENT_EVIDENCE` -- an honest terminal state (this entry file + its README genuinely don't contain enough for a confident verdict on these), not silence and not a fabricated PASS/FAIL. All 3 aggregation requirements (`req-2-pass-l1`/`req-3-pass-l2`/`req-R-meet-all-possible`) correctly resolved to `INCONCLUSIVE` (some INSUFFICIENT_EVIDENCE/INCONCLUSIVE constituents at their levels, but zero FAILs -- exactly the designed rule, not a false PASS). `terminal_status_counts` sums to exactly 81 (19 PASS + 29 NOT_APPLICABLE + 27 INSUFFICIENT_EVIDENCE + 4 INCONCLUSIVE + 2 FAIL). Codex `ghome` scratch dirs now correctly include the entry name (`ValidatorTracker__req-3-linted_ghome`), confirming the earlier case_id collision fix (#5) also works live. |

### Aggregate integrity checks (v3, full coverage) -- computed at the end, not assumed

Final `pilot_summary.json`: `requirements_considered=486` (81 x 6 entries),
`requirements_applicable=326`, `judgments_attempted/succeeded/failed=207/207/0`,
`bundles_escalated_to_codex=31`, `codex_investigations_completed=31`,
`timed_out=0`, `skipped_cost_ceiling=0`. `final_decisions`:
`{PASS: 108, FAIL: 27, INCONCLUSIVE: 17, INSUFFICIENT_EVIDENCE: 174}`
(sums to exactly 326). `total_codex_cost_usd=$1.3635`. `infra_failures=[]`.
**`integrity_valid: True` for all 6 entries individually AND overall**
(`integrity_unknown_entries: []`). DetectGrader: **0/1** (H-01 not
detected).

- [x] `judgments_attempted=207, succeeded=207, failed=0` -- 100% success across the full run, no sign of a systemic judgment-layer failure.
- [x] L8 token log: **378 real (non-cached) API calls, 36 cache hits, $3.0682 real cost.**
- [x] `bundles_escalated_to_codex(31) == codex_investigations_completed(31) + timed_out(0) + skipped(0)` -- holds exactly.
- [x] Every `escalation_skip_reasons` entry checked has a real, specific reason (same known representation-gap class as the section-1 run; not re-verified line by line here since that mechanism is unchanged by this session's fix).
- [x] `bundles_escalated_to_codex(31)` matches the section-1 run's own escalation count for the SAME 56 original requirements almost exactly (31 both times) -- the 21 new LLM-mediated requirements contributed evidence/judgments but, on this audit, none of them met the escalation trigger (LOW confidence / INSUFFICIENT_EVIDENCE-with-a-resolvable-location) strongly enough to add a NEW escalation beyond the original 31 -- consistent with them mostly resolving cleanly to INSUFFICIENT_EVIDENCE without a resolvable graph location to escalate to in the first place.
- [x] Codex `_ghome` scratch dirs verified live to include the entry name (case_id fix #5 confirmed working under real load, not just synthetically).
- [x] Final OpenRouter balance reconciliation: total account `usage` before this run's start was $42.5074; after, $46.9255 -- delta **$4.4181**. Tracked L8 ($3.0682) + Codex ($1.3635) = **$4.4317**. Residual ~$0.014, consistent with the DetectGrader's own small `gpt-4o` judge call plus float rounding -- no unaccounted spend. (`usage_daily` itself reset mid-run at a day boundary and is not usable for this comparison; total lifetime `usage` was used instead.)

**All integrity checks pass. This run is VALID**, and demonstrates, on
real live data (not just the synthetic tests in
`test_runtime_coverage.py`), that:
- the full 81-requirement corpus is evaluated per entry (up from 56),
- both new mechanisms (21 LLM-mediated requirements via the generic
  evidence collector, 3 aggregation requirements) genuinely executed and
  produced real, explicit terminal states,
- the aggregation logic is CORRECT under real data: `req-2-pass-l1`/
  `req-3-pass-l2` FAILed on 3 different entries specifically because a
  real underlying Level S/M requirement genuinely failed for that entry,
  and resolved INCONCLUSIVE (never a false PASS) whenever something was
  merely unresolved,
- `silently_missing` was 0 on every single entry and audit-wide.

### Final outcome classification against H-01 (per the user's A/B/C/D rubric)

**Only consulted now that this run is frozen**, per instruction.
DetectGrader result: **0/1**, identical to both prior runs. The real
judge reasoning: "The audit report does not mention any issues related
to the calculation of `totalAssets()` being incorrect due to
`operatorFeeAmount`... does not mention `totalAssets()` or its
calculation method... thus it does not detect this particular
vulnerability."

**Classification: D -- relevant information exists but never reaches the
reviewer (evidence/context-construction failure). NOT a requirement-
coverage failure, per the user's own explicit rule that this label
requires "the complete, correctly executed RTF" to have had a fair look
-- it did not.**

**Root cause, found by direct forensic inspection (not guessed):**
`req-3-documented`, `req-3-implement-as-documented`, and
`req-3-document-system` all executed correctly on the `LiquidRon.sol`
entry (the file containing H-01) -- real evidence collected, real L8
judgment, all three honestly resolved to `INSUFFICIENT_EVIDENCE`. But
`collect_documentary_and_implementation_evidence`'s own source-excerpt
cap (`_MAX_SOURCE_EXCERPT_CHARS = 8000`, in
`rtf/l5_predicates/predicates.py`) truncates the entry file's source
before attaching it as evidence. **`LiquidRon.sol` is 20,462 characters;
`totalAssets()` -- H-01's exact vulnerable function -- starts at
character offset 12,553, more than 4,500 characters past the truncation
point.** The reviewer never saw it. Confirmed exhaustively: every cached
L8 response this entire run produced (`pilot5_l8_cache/*.json`) was
grepped for `totalAssets`/`operatorFeeAmount` -- **zero matches anywhere
in the whole run**, not just for the two Q requirements.

**Why this is D, not A/B/C:**
- Not **A** (architecture incompleteness): the reviewer mechanism now
  exists, is wired, and executed -- the exact gap this whole exercise
  was launched to fix is closed.
- Not **B** (reasoning failure): a reasoning failure requires the
  reviewer to have SEEN the relevant material and reasoned about it
  incorrectly. It never saw it.
- Not **C** (specification-information limitation): this is not about
  whether the project's documentation states the invariant strongly
  enough (a real, separately-identified, secondary concern -- see the
  original gap analysis's note on the README's ambiguous sponsor
  disclaimer) -- it's that the IMPLEMENTATION CODE itself, which any
  claims-vs-implementation judgment fundamentally needs to see, was
  excluded before the question of documentation adequacy could even
  arise.
- Is **D**: a concrete, fixable evidence-construction defect in this
  session's own new code, found by exactly the kind of complete,
  honest, don't-stop-at-the-first-plausible-explanation verification
  this project's methodology demands.

**Per the user's explicit instruction, NOT fixed as part of this run**
("Do not modify the pipeline after seeing the Liquid-Ron result"). Concrete,
specific recommendation for a future pass: raise or remove
`_MAX_SOURCE_EXCERPT_CHARS`, or (better) select the excerpt around
value-accounting-relevant function signatures (e.g. public/external
`view`/`pure` functions and functions with `override` modifiers signaling
inherited-interface conformance) rather than a fixed leading-bytes
window, so a small-but-late function is not structurally invisible on any
file over the cap. This is a real, disclosed, actionable limitation, not
swept under a "requirement coverage" label it does not deserve.

**Note on the secondary, already-disclosed factor**: even with full
source visibility, whether the generic reviewer would have confidently
FAILed H-01 remains genuinely open -- the original gap analysis's finding
about the README's ambiguous sponsor disclaimer ("I am aware that the
operator fee changing impacts the total assets calculation... I am ok
with the behaviour") still stands as a real complicating factor for a
claims-vs-implementation judgment. This truncation bug prevented the
question from ever being tested at all, which is itself the honest,
correct thing to report -- not "the reviewer tried and failed," but "the
reviewer was never given the material to try."

## 7. Final decision

**Commit `0a3ba22` is frozen** as the validated, tested, live-confirmed
implementation for the RTF pipeline as of this session. Its known,
disclosed limitation (the evidence-construction truncation cap,
outcome D above) does not invalidate this run -- every check the run
itself was designed to verify (integrity, aggregation correctness, full
corpus coverage, real API activity, real Codex escalation) passed. It is
a concrete, well-understood item for the next engineering pass, not a
silent gap.

Per the user's explicit instruction, **the 5-audit pilot (canto,
vultisig, arbitrum-foundation, sequence) has NOT been launched** as part
of this task -- this task's scope ends at a validated, frozen Liquid-Ron
architecture fix and outcome classification.

## 8. Agentic architecture redesign + validation (2026-08-09/10)

Per user directive ("revisit the RTF pipeline architecture... the current
design is not aligned with the intended agentic architecture"): full
redesign removing bounded L8 as a pre-Codex gate. Full audit, design,
implementation, and test record in `RTF_AGENTIC_ARCHITECTURE.md` (19
requirements now fully deterministic/no-LLM-at-all;
59 now route directly to an agent investigation with full repository
access, no `candidate_location` precondition). Frozen at commit
`aee8418` (`2614177` + a live-discovered dangling-symlink fix in the new
`shutil.copytree` full-repo-copy step -- see that commit's own message).

**Cost/time check-in with the user before launching**: removing the
bounded-L8 gate means every applicable agent-required requirement is now
an unconditional investigation (~150-210 projected for the full 6-entry
audit, vs. 31 before) -- realistically 8-20+ hours and $10-40 for the
full audit. **User chose to validate on `LiquidRon.sol` alone first**
(the entry containing H-01), not the full 6-entry audit, to get real
cost/time data and confirm the new architecture behaves correctly live
before committing to the rest.

### Live findings from the first launch attempt (invalidated, refunded $0)

First launch crashed immediately (`$0` spend, 0 valid results,
`infra_failures=1`, correctly NOT reported as a clean success): `shutil.
copytree`'s default `symlinks=False` tried to dereference a stray
dangling `solc` symlink at the liquid-ron repo clone's root (leftover
from an earlier, unrelated session's Codex home-directory setup) and
raised `shutil.Error` before the agent ever started. Fixed
(`symlinks=True`, standard `cp -a` semantics for a full tree copy) and
the stray symlink itself removed from the shared clone. Per the
invalidate-and-rerun rule: nothing valid existed yet to discard: relaunched
from scratch under the fix (commit `aee8418`).

### Second launch: live-confirmed working

- Full repository genuinely present in the investigation dir immediately
  (verified directly: `README.md`, `README-sponsor.md`, `test/`,
  `script/`, `src/`, `lib/`, `foundry.toml`, `remappings.txt`, etc. --
  not just the entry file).
- Real Codex process confirmed running with the new `ARM_G_PROMPT_v2.md`
  content (verified via `ps`/process args).
- Live-observed adaptive behavior: the agent tried `rg "assembly"` first
  (per the prompt's suggested tool list) -- `rg` isn't actually on the
  sandboxed subprocess's minimal `PATH` (`/usr/bin:/bin`) -- got
  `command not found`, and recovered on its own by falling back to
  `grep -r`, which worked and returned real matches (including vendored
  `lib/openzeppelin-contracts` hits) -- genuine adaptive exploration
  behavior, not a blocking defect; no pipeline change made for this.

_Live progress tracked below as investigations complete._

| Metric | Value |
|---|---|
| Frozen commit | `aee8418` |
| Scope | `2025-01-liquid-ron`, entry `./src/LiquidRon.sol` ONLY (user-selected partial validation, not the full 6-entry audit) |
| Cache/artifact reuse | None -- fresh scratch, fresh investigation-dir copies, no prior decision artifacts |
| Status | IN PROGRESS (27+ of ~30 investigations complete as of this update) |

### Live findings of note (pre-freeze, no H-01 consultation)

- `req-3-documented`: HIGH-confidence PASS. The agent found and read
  `README-sponsor.md` directly (never visible to the old 8000-char-capped
  single-file collector) -- "protocol purpose, deposit/withdrawal flows,
  operator roles, and enumerates each LiquidRon function's behaviour."
- `req-3-implement-as-documented`: HIGH-confidence **FAIL** -- a genuine,
  INDEPENDENT bug, not H-01: the `onlyOperator` modifier
  (`src/LiquidRon.sol:89-93`) requires `msg.sender == owner()` AND the
  operator flag to be false, so a configured operator address can NEVER
  actually call the functions `README-sponsor.md` documents as
  "Operator only call" (`harvest`, `harvestAndDelegateRewards`,
  `delegateAmount`, `redelegateAmount`, `undelegateAmount`) -- every one
  of them reverts for real operators. Specific line citations, resolved
  facts tracing exactly why (`operator[addr]=true` makes the modifier
  reject that address), `CONFIRMED_VIOLATION` stop reason. This is
  genuine evidence the new claims-vs-implementation mechanism works as
  intended -- it does NOT by itself say anything about H-01 specifically,
  which is a separate, more subtle economic-accounting bug in a different
  function; full outcome classification only after the run is frozen.
- `req-1-no-assembly`: the agent searched `grep -R` across the ENTIRE
  `src/` directory (all 6 scope files), not just the entry file --
  direct, concrete confirmation of genuine repo-wide exploration.

### Final run results (complete, frozen, `aee8418`)

| Metric | Value |
|---|---|
| Wall clock | 19:03:56 -> 21:00:59 (+04:00), ~1h57m for 34 investigations |
| Requirements considered | 81 |
| Requirements applicable | 58 |
| Deterministic (no-LLM) resolutions | 24 (evidence bundles generated w/o agent) |
| Agent investigations launched | 34 (`bundles_escalated_to_codex` = `codex_investigations_completed` = 34; 0 timed out, 0 skipped on cost ceiling) |
| Bounded-L8 judgments (dormant path) | 0 attempted / 0 succeeded -- confirms L8 is genuinely out of the live decision path, not silently still running |
| Final decisions | PASS 31, FAIL 26, INCONCLUSIVE 1, INSUFFICIENT_EVIDENCE 0 |
| `infra_failures` | 0 (the symlink crash was on the invalidated first attempt, `$0` spend, correctly not counted here) |
| `integrity_valid` | `True` |
| Codex API cost | `$3.4192` |

Zero `INSUFFICIENT_EVIDENCE` terminal states out of 58 applicable
requirements is itself a direct, positive confirmation of the redesign's
core goal: under the old bounded-L8-gate architecture, `INSUFFICIENT_
EVIDENCE`/no-candidate-location was exactly the failure mode that
silently ended investigations before a real agent ever explored the
repo. Here, every one of the 34 agent-required requirements that reached
the agent produced a real PASS/FAIL/INCONCLUSIVE verdict grounded in
actual exploration.

### Grading-infrastructure issue (external, not an RTF defect) and its fix

`pilot5_driver.py`'s automatic grading call (`judge_model=openai/gpt-4o`,
the project's standard judge) failed with a genuine API-side limit:

```
RolloutSystemError: ... This endpoint's maximum context length is 128000
tokens. However, you requested about 131111 tokens ...
```

Root cause: this run's `audit.md` is 6,133 lines (26 rich, evidence-cited
FAIL findings from real agent investigations) -- substantially larger
than any prior run's report, because the new architecture produces
genuinely more thorough, better-evidenced findings. This is an EXTERNAL
grading-harness capacity limit, not a pipeline defect: the run itself
completed with `integrity_valid=True` and `infra_failures=0` before
grading was ever attempted.

Fix (infra-only, does not touch RTF's own reasoning or the frozen
`audit.md`): re-ran `run_grader()` directly against the same, unmodified,
already-frozen `audit.md` with `judge_model=openai/gpt-4.1` (larger
context window). This succeeded and is the authoritative result below.
Persisted into `pilot5_artifacts/2025-01-liquid-ron_validation_v4_agentic_LiquidRonOnly/pilot_summary.json`'s
`grade_result` field (the original `openai/gpt-4o` failure is preserved
in the adjacent `grade_error` field for the record, not deleted).

### DetectGrader result: 0/1 (H-01 still not detected)

```json
{
  "audit_id": "2025-01-liquid-ron",
  "judge_model": "openai/gpt-4.1",
  "score": 0,
  "max_score": 1,
  "vulnerability_results": [{"vulnerability_id": "H-01", "passed": false}]
}
```

Judge's full reasoning: "There is no evidence in the audit report
findings that the specific issue described in the vulnerability -- the
incorrect calculation of totalAssets() due to operatorFeeAmount being
included in user asset accounting and resulting in loss for new
depositors -- is explicitly identified or discussed. While several
findings touch on access control, governance, time locking, and general
documentation, and some suggest inconsistencies between documentation
and behavior (e.g., operator/owner split), none mention the
totalAssets() calculation and the need to exclude or adjust for
operatorFeeAmount. There are no references to the dilution/loss
mechanism described... Accordingly, the report did not detect the
described vulnerability."

### Forensic A-E classification (per user's explicit rubric, evidence-based, not assumed)

Per the user's instruction, **the prior run's "requirement coverage"
explanation was NOT assumed to still hold** -- this run has a
structurally different architecture (full repo access, no bounded-L8
gate, no 8000-char truncation, no candidate_location precondition), so
it required fresh forensic verification of what the 34 real
investigations actually saw and reasoned about. That verification was
done directly against the raw Codex session transcripts
(`*_gstream.jsonl` in the scratch dir), not inferred.

**Ground truth (`findings/H-01.md`)**: `totalAssets()` sums
`super.totalAssets() + getTotalStaked() + getTotalRewards()`, and
`getTotalRewards()` nets out `operatorFee`, but the *accrued,
not-yet-withdrawn* `operatorFeeAmount` balance is still sitting in the
vault's WRON balance and gets counted as a vault asset until
`fetchOperatorFee()` removes it -- so anyone who deposits while fee is
accrued and redeems after the operator withdraws it receives less than
expected. The judge who triaged the original contest additionally noted
this "contradict[s] the EIP-4626 standard."

**Step 1 -- was this ever routed to a real agent? (ruling out A)**
Yes, repeatedly. `grep` across all 34 `gstream.jsonl` transcripts for
commands touching `LiquidRon.sol`'s `totalAssets`/`getTotalRewards`
region shows at least 4 *separate, independent* agent investigations
directly read and reasoned about that exact code:
`req-2-check-rounding`, `req-3-block-front-running`, `req-3-protect-gas`,
and `req-R-follow-erc-standards`. This alone rules out A: the
architecture fix worked -- the relevant implementation was not gated
away from agent investigation.

**Step 2 -- did any agent actually see/understand the mechanism? (ruling out B)**
Yes, decisively. Direct quotes from real final decisions, all FAIL
except the last:

- `req-3-block-front-running` (FAIL): *"operatorFee... directly feeds
  into getTotalRewards and thus totalAssets and the ERC4626 share
  exchange rate... skew the mint/burn rate... Does operatorFee affect
  share pricing/total assets? Yes, totalRewards is reduced by
  operatorFee and included in totalAssets, impacting ERC4626
  deposit/redeem rates."* -- this is the *exact* causal chain H-01
  describes, seen and stated explicitly.
- `req-2-check-rounding` (FAIL): flagged `getTotalRewards`'s
  `operatorFee` subtraction and `_convertToAssets`'s rounding as an
  undocumented downward bias, in the same function region.
- `req-3-protect-gas` (FAIL): flagged `totalAssets()`'s reliance on
  unbounded validator/proxy iteration, again the same function.
- `req-R-follow-erc-standards` (PASS): explicitly checked "does the
  vault follow ERC4626" but only at the interface/inheritance level
  (correct function signatures, correct events) -- never evaluated
  whether the *semantic content* of `totalAssets()` violates ERC4626's
  implicit accounting invariant.

This conclusively rules out B: the implementation was not merely visible
in principle -- it was actually read, quoted, and reasoned about by name
in multiple independent investigations, with full detail (exact line
ranges, exact variable names, exact causal relationship to share
pricing).

**Step 3 -- documentation check.** The repo's `README.md` (not
`README-sponsor.md`) contains, at line 32, a sponsor disclaimer: *"I am
aware that the operator fee changing impacts the total assets
calculation in the vault. increasing it will reduce the total,
decreasing it will increase the total. I am aware of it and I am ok
with the behaviour."* 18 of the 34 investigations read this exact file
region. On its surface this reads as covering H-01's territory -- but on
close reading it describes the effect of *changing the fee rate/config
parameter*, not the distinct mechanism H-01 actually reports (a
*constant*-rate accrual/withdrawal timing window that dilutes whichever
depositor is unlucky enough to deposit while fee is accrued and redeem
after it's claimed). Notably, the original contest's own project owner
("Owl") did NOT treat this disclaimer as covering H-01 -- they confirmed
it as a real bug and shipped the exact fix DetectGrader's judge expects
(subtracting `operatorFeeAmount` from `totalAssets()`). This means the
ambiguous-but-adjacent disclaimer plausibly *primed* investigations that
read it toward "this fee/totalAssets interaction is a disclosed,
accepted tradeoff" framing, without any investigation stopping to verify
that the disclaimer's specific scope (rate changes) differs from the
actual mechanism at hand (accrual timing) -- a genuine, evidence-grounded
contributor, though not on its own sufficient to explain the miss given
front-running's investigation reasoned past it to a FAIL anyway.

**Step 4 -- C vs E.** `req-3-implement-as-documented` is the one
requirement literally shaped to compare documented behavior against
observed behavior. Its investigation found ONE real, independent bug
(the inverted `onlyOperator` access-control modifier) and stopped at
`CONFIRMED_VIOLATION` after verifying that single claim -- it never
circled back to cross-check the totalAssets/operator-fee disclaimer
against the actual `totalAssets()` code, even though it had already read
the containing file. That is a real, single-verdict-per-investigation
limitation of how "Implement as Documented" is operationalized (one
confirmed violation is sufficient to FAIL and stop, not an exhaustive
claim-by-claim checklist) -- a plausible partial contributor, but it
does not by itself explain the miss, since 3 *other*, differently-framed
requirements independently reached the same code and still didn't
produce a finding shaped like H-01.

The decisive pattern: multiple independent agents saw the *same lines of
code*, understood the *same causal chain* (operator fee <-> totalAssets
<-> share price), and each filed a real, correct, differently-shaped
FAIL under its own requirement's specific normative lens -- rounding
precision, front-running/ordering protection, gas-griefing, ERC-standard
interface conformance. None of these is "wrong" as a finding. But EthTrust's
81-requirement corpus, even fully exercised with genuine, repeated,
detailed exploration of the exact vulnerable code, contains no
requirement whose normative text asks the specific ERC-4626 vault-
accounting question DetectGrader's judge is scoring against: *does
`totalAssets()`'s definition of "assets" wrongly include funds earmarked
for (owed to) a third party rather than genuinely redeemable by
shareholders?* That is a narrow, protocol-specific accounting-design
invariant, not a generic smart-contract security property, and EthTrust
(a general smart-contract security-practices standard) was never written
to test it directly.

**Classification: primarily E (requirement-coverage limitation), with a
secondary, evidence-grounded C contributor** (the ambiguous sponsor
disclaimer plausibly steered reasoning in at least one investigation
that read it, and `req-3-implement-as-documented`'s single-verdict-and-
stop behavior meant it never cross-checked that disclaimer against the
totalAssets code specifically) -- **not A or B**, both of which are
conclusively ruled out by direct transcript evidence: the requirement
WAS routed to real agents, and the agents DID see, quote, and reason
about the exact vulnerable code multiple times over.

This is a materially different, and more defensible, conclusion than
before: previously it was unclear whether "no matching requirement" was
a real corpus gap or an artifact of evidence truncation/gating that
never let an agent look. This run rules out the latter with direct
evidence and confirms the former is real, at least for this specific
vault-accounting invariant.

### Decision: hold before launching further audits

Per user instruction, the remaining 5 `2025-01-liquid-ron` entries and
the other 4 audits (canto, vultisig, arbitrum-foundation, sequence)
remain **out of scope** pending further instruction. Real cost/time data
from this validation ($3.42, ~2 hours wall clock, 34 investigations for
one entry) is now available to inform that decision -- a full 6-entry
audit at this rate projects to roughly $15-25 and 8-14 hours of wall
clock if run sequentially (parallelizable across entries).
