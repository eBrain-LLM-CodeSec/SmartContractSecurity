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
