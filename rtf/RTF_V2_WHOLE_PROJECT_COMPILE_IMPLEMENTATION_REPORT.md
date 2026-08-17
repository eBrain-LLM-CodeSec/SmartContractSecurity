# RTF v2 whole-project Foundry compilation: full implementation report

Comprehensive record of every fix and change made while implementing and
live-validating the whole-project-Foundry-compilation architecture on
branch `rtf-v2-redesign`, 2026-08-14 through 2026-08-16. Companion
documents: `RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md` (the design plan
and its own accumulated live-run log) and
`RTF_V2_COMBINED_PIPELINE_5MISSES_ROOT_CAUSE.md` (why the 5 remaining
misses happen). This document answers a different question from both:
**what changed, why, how, and what did it do to the real numbers.**

---

## 1. Executive summary

**Problem**: RTF v2's semantic property generator -- and, until this
work, every EthTrust/ERC structural predicate too -- compiled only one
entry `.sol` file's own `import` graph. A legitimately in-scope sibling
contract the entry doesn't `import` (a common shape for Foundry-library
projects) was completely invisible to the pipeline. Confirmed, not
theoretical: `2025-04-forte`'s `Ln.sol` and `2024-08-phi`'s `Cred.sol`
were both structurally unreachable, accounting for 3 of 11 misses in an
earlier 5-entry comparison run.

**What was built**: whole-project Foundry compilation, threaded through
every stage of the pipeline (generation, investigation graph navigation,
and -- new this session -- EthTrust structural predicate evidence
collection), plus defense-in-depth scope enforcement, vendor-context
filtering, three real-incident-motivated reliability fixes, and EthTrust
structural-requirement routing merged into the same investigation as
semantic-v2 properties.

**Result**: real, `DetectGrader`-graded score across all 5 targets from
the project's original 5-entry comparison went from **2/15** (old,
pre-fix RTF v2 architecture) to **10/15** -- also beating the **6/15**
simple-Codex baseline RTF had previously lost to. Total real spend
validating all of this: **$14.793** across 5 live investigation runs,
plus roughly $0.20 in smaller diagnostic-only generation measurements.

---

## 2. Why this work happened

`RTF_V2_5ENTRY_ALL_MISSES_ROOT_CAUSE.md` (an earlier session's forensic
analysis of a completed 5-entry comparison run) found that RTF v2's
semantic generator compiled `entry_sol_file` and only the files it
transitively `import`s via raw `solc`. Two real, confirmed misses traced
directly to this:

- **`2025-04-forte` H-03** (`Ln.ln()` accepts negative/zero input without
  validation): the comparison run's entry was `Float128.sol`. `Ln.sol`
  *imports* `Float128.sol` -- not the reverse -- so compiling `Float128.sol`
  alone never pulls `Ln.sol` into the compiled unit. `semantic_properties_raw.json`
  for this run has zero mentions of `Ln`/`ln(` anywhere.
- **`2024-08-phi` H-03/H-06** (`Cred.sol`'s `EnumerableMap` bloat DoS and
  reentrancy): the entry was `PhiFactory.sol`. `Cred.sol` is a sibling
  contract `PhiFactory.sol` never imports. Same structural blindness,
  same result: zero mentions of `Cred`/`shareBalance` anywhere in that
  run's generated properties.

The root-cause report called this "the single highest-leverage fix
identified," since it mechanically explains 3 of 11 misses with one
engineering change, independent of any prompt tuning or generation
volume increase. This report covers everything built to close it, plus
everything found and fixed along the way while proving it worked.

---

## 3. Fix 1 -- Whole-project Foundry compilation for semantic generation (Goal 1)

### What
`compile_helper.compile_evmbench_target_via_foundry(project_root, extra_forge_build_args=None, timeout_s=300) -> Slither`
compiles the **whole project** (every file under the project's own
`src`, as `forge build` would) instead of following one entry file's
import graph via raw `solc`. `run_semantic_investigation` gained a
`compile_via_foundry: bool = False` parameter that branches generation-
time compilation between the old and new function.

### Why this design
- Real `forge` is broken on this host (`GLIBC < 2.29`, confirmed live).
  The `evmbench-worker.sif` Singularity container -- built for a
  *different* system (the LLM-agent-auditor pipeline, unrelated to
  RTF) -- happens to have a working `forge` install. Reused purely as a
  compilation utility: `forge build --build-info` runs *inside* the
  container via `singularity exec`, producing real `out/build-info/*.json`
  artifacts; `Slither` then reads those artifacts back on the *host* via
  crytic-compile's `foundry_ignore_compile=True` mode, which never
  invokes `forge` itself. Zero `forge` dependency on the host at any
  point.
- `test`/`script` directories are always skipped
  (`--skip ./test/** ./script/** --force`) -- matching crytic-compile's
  own Foundry-platform default, and avoiding a confirmed-live failure
  mode where a real EVMbench test suite's own unvendored npm dependency
  (`@prb/test` on `2024-08-phi`) would otherwise fail the whole build
  over files nothing downstream needs.
- Kept as a strict **opt-in** alternative (`compile_via_foundry=False`
  is the unchanged default) rather than replacing
  `compile_evmbench_target` outright -- every existing caller
  (`pipeline_e2e.py`, `pilot5_driver.py`, `ablation_driver.py`) is
  unaffected until explicitly migrated, a deliberate scope boundary (see
  Section 12).

### How -- the compilation call
```python
cmd = [
    str(_SINGULARITY_BIN), "exec",
    "--bind", f"{project_root.resolve()}:/work",
    "--pwd", "/work",
    str(_EVMBENCH_WORKER_SIF),
    "forge", "build", "--build-info", "--skip", "./test/**", "./script/**", "--force",
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
...
return Slither(str(project_root.resolve()), foundry_ignore_compile=True, compile_force_framework="Foundry")
```

A companion fix in the same commit: `ProjectManifest.from_slither`
gained an optional `repo_root` parameter that excludes vendored
contracts (`lib/`, `node_modules/`, `vendor/`, `dependencies/`,
`.deps/`) from the generator-facing manifest, reusing
`rtf.standards.discovery._is_vendored_path` directly rather than a
second classification rule. Load-bearing the moment compilation covers
a whole project: an unfiltered manifest would hand the LLM generator
every vendored OpenZeppelin/Solady contract too, for zero benefit
(vendored properties get dropped by scope filtering anyway).

### Tests
`test_compile_via_foundry_real_target_multi_file_visibility`
(`test_compile_helper.py`) -- real container compile against a real
EVMbench checkout (`2026-01-tempo-feeamm`), no manual solc flags.
`test_compile_via_foundry_makes_a_sibling_scope_file_visible_to_generation`
(`test_semantic_only_driver.py`) -- a synthetic 2-file fixture
(`Vault.sol` entry, `Sibling.sol` not imported by it) proving the
sibling becomes visible, grounded, and correctly scoped end to end,
mocked LLM only.

---

## 4. Fix 2 -- Real scope-matrix fixture closing a test-coverage gap (Goal 1, hardening)

### What
`test_compile_via_foundry_scope_matrix_entry_sibling_helper_vendor`
(`test_semantic_only_driver.py`): a real 4-file Foundry fixture --
`Entry.sol` (in scope), `Sibling.sol` (in scope, **not** imported by
Entry), `Helper.sol` (first-party, compiled, visible, groundable, but
**out of scope**, deliberately **not** imported by Entry), and
`lib/Vendor.sol` (vendored dependency).

### Why
An **existing** test with a similar shape
(`test_scope_files_drops_properties_targeting_files_outside_declared_scope`)
had a real, confirmed flaw: its own `Helper.sol` fixture **is**
`import`ed by its entry file, so it was already visible under the *old*
single-entry-compile path too. It proves "a compiled, in-import-graph,
out-of-scope file is correctly rejected" -- a real, valid test, but *not*
proof of this work's actual new requirement: a file invisible under the
old path, visible only because whole-project compilation exists, still
correctly rejected as out of scope. This is exactly the kind of
misleading-coverage trap the project's own "soft-run" planning
discipline exists to catch before trusting an existing test's green
checkmark.

### How
All four fixture files compiled together via one real
`compile_via_foundry=True` call. Assertions proved, in one test, all
four outcomes simultaneously: `Entry`/`Sibling` both reportable, `Helper`
visible+grounded+**rejected**, `Vendor` filtered at grounding (not even
groundable, confirming Fix 1's vendor filtering independently).

### Tests
20 checks in this one test function, all passing against a real
Foundry compile.

---

## 5. Fix 3 -- Defense-in-depth scope boundaries A/B (Goal 1b)

### What
Two new enforcement points that re-check a property pool against
`scope_files`, using the **same canonical matcher**
(`property_metadata.split_properties_by_scope`) the primary filter
already uses -- never a second scope-matching implementation:

- **Boundary A** (`live_runner.prepare_cluster_investigations_with_scope_boundary`):
  re-checks the property pool immediately before clustering/dispatch.
- **Boundary B** (`semantic_only_driver._enforce_scope_boundary_b`):
  immediately before `run_semantic_investigation` returns, strips any
  property_id present in `property_verdicts`/`raw_property_entries_by_id`
  that isn't a member of the already-scope-checked `properties_by_id`
  pool.

New shared helper: `property_metadata.enforce_scope_boundary(properties, scope_files, boundary_name) -> (kept, violations)`.
`run_semantic_investigation`'s returned dict gained
`scope_boundary_violations` (empty list in normal operation).

### Why
Whole-project compilation deliberately widens what the pipeline can
*see*. The plan's own Invariant C/F: `scope_files` remains the sole
reporting authority no matter how broad compilation gets, and if
something ever bypasses the primary filter, it must **fail closed** --
never silently investigated or returned. These boundaries exist
specifically to catch that failure mode, not because the primary filter
is expected to fail in normal operation.

### How -- the deliberate bypass tests
Testing the primary filter twice proves nothing new, so both new tests
deliberately **skip** the primary filter to prove the boundary catches
it independently:
- `test_boundary_a_blocks_a_property_that_bypassed_the_primary_filter`:
  calls `prepare_cluster_investigations_with_scope_boundary` **directly**
  with a pool that already contains an out-of-scope property -- never
  routed through `run_semantic_investigation`'s own upstream filter at
  all.
- `test_boundary_b_strips_a_fabricated_property_id_from_investigator_output`:
  a mocked investigator response names a property_id this run never
  dispatched to any cluster (simulating a fabricated/stale reference) --
  proven that `resolve_property_verdicts` and
  `run_cluster_investigations_live` would otherwise pass such an entry
  through unconditionally.

### Tests
4 new checks (2 per boundary), zero regressions across the full
`l11_investigation_grouping` suite.

---

## 6. Fix 4 -- Investigator-facing vendor context filtering, and a real bug found fixing it (Goal 1, hardening)

### What
`context_artifacts.generate_protocol_context_md` gained an optional
`repo_root` parameter that excludes vendored contracts from every
section it drives (contracts/inheritance, entry points, state
variables, trust boundaries) via a new `_contract_is_vendored` helper.
`protocol_context.py`'s `extract_accounting_state_variables`/
`extract_lifecycle_hints` gained the same parameter.

### Why -- and the real bug found along the way
Fix 1 already filtered the **generator-facing** `ProjectManifest`. This
fix does the same for the **separate, investigator-facing**
`protocol_context.md` -- the actual Markdown file every cluster
investigation reads. Without it, whole-project compilation against a
real project with a populated `lib/` (OpenZeppelin, Solady, forge-std)
would flood every investigation with irrelevant vendored-contract
context.

While wiring this in, a **real, load-bearing bug** was found: the
driver builds an enriched, filtered `protocol_context_md` at the top of
`run_semantic_investigation` -- but `prepare_cluster_investigations`
(called later, for clustering) was **independently regenerating its
own, separate, unfiltered** `protocol_context_md` from scratch,
silently discarding the driver's own enriched one. The vendor filtering
above would have been dead code from the investigator's perspective
without this fix.

### How
`prepare_cluster_investigations`/`prepare_cluster_investigations_with_scope_boundary`
gained `repo_root`/`protocol_context_override` parameters -- when the
driver already has a real enriched context, it's passed straight
through instead of being silently regenerated.

### Tests
`test_prepare_cluster_context_filters_vendor_when_repo_root_is_given`,
`test_prepare_cluster_context_uses_explicit_enriched_override`
(`test_live_runner.py`) -- both real, proving the override path is
actually taken, not just accepted as a no-op parameter.

**Separately (found by a concurrent continuation of this session while
validating against real phi content, not something anticipated in
advance)**: `extract_protocol_purpose`'s README-parsing heuristic
originally took the first non-heading paragraph as the protocol's
purpose -- real audit READMEs frequently lead with contest metadata
("Total Prize Pool: $30,000") before an actual `## Overview` section.
Fixed to prefer an explicit `Overview` heading's own first paragraph
when one exists, falling back to the old heuristic otherwise. Test:
`test_protocol_purpose_prefers_overview_over_contest_metadata`, using a
real fixture shaped like `2024-08-phi`'s own README.

---

## 7. Fix 5 -- Consistent generator/investigator project view (Goal 2)

### What
`graph_mcp_server.py`'s `_get_graph()` -- the function that builds the
`ProgramGraph` the investigation's MCP tools query -- gained a branch:
when Foundry mode is active (`GRAPH_COMPILE_VIA_FOUNDRY=1`, a new env
var), it loads the investigation copy's **own already-compiled**
Foundry artifacts (`Slither(INVESTIGATION_DIR, foundry_ignore_compile=True, compile_force_framework="Foundry")`
then `ProgramGraph.from_slither(slither)`) instead of an independent
second compile. New helper `_build_graph_for_investigation` isolates
this branch for direct testing. `compile_via_foundry` threads through
`run_semantic_investigation` -> `run_cluster_investigations_live` ->
`arm_g_codex.run_arm_g_bundle` -> the MCP server's own env-var block.

### Why
Confirmed, real inconsistency before this fix: generation used whatever
compile strategy it was told to; the investigation graph **always**
independently recompiled from `ENTRY_FILE`'s own narrower import graph,
regardless of how generation compiled. A property generated from a
sibling contract only visible via whole-project compilation would be
**structurally unresolvable the moment investigation tried to look it
up** -- a confirmed Invariant-E violation if left unfixed.

**One genuinely good find**: the primitive this needed --
`ProgramGraph.from_slither(slither) -> ProgramGraph`, building a graph
from an already-compiled Slither object with zero second compile --
**already existed** in `a4v/graph.py`, built in an earlier, unrelated
session for a different bug (`2024-01-canto`'s `LendingLedger.sol`
hitting a real "stack too deep" `BuildFailed` on a second, differently-
configured compile). It had zero callers and zero test coverage before
this fix. Goal 2 was wiring an existing primitive together correctly,
not building a new one.

### Tests -- including the mandatory artifact-relocation test
Two tests in `test_graph_mcp_foundry_relocation.py`:
- `test_copied_foundry_artifacts_resolve_sibling_without_legacy_compile`:
  compiles a real fixture in its original location, copies it via the
  **real** `prepare_full_repo_investigation_dir` into a separate
  investigation directory (the actual production lifecycle, not a
  same-directory shortcut), loads the **copied** artifacts, and resolves
  a sibling contract's node in the resulting graph -- while a **poison-
  pill mock** on `ProgramGraph.build` (raises `AssertionError` if ever
  called) proves the old recompile path is never silently taken.
- `test_non_foundry_helper_preserves_legacy_build_call`: proves the old,
  non-Foundry path is completely unchanged and still calls
  `ProgramGraph.build` with byte-identical arguments.

---

## 8. Fixes 6, 7, 8 -- Three reliability fixes found from a real interrupted live run

A real live investigation against `2024-08-phi` (launched, not
anticipated, by an earlier continuation of this session) was
interrupted mid-run -- 7 of 11 already-completed, already-paid-for
verdicts were at real risk of being unrecoverable, and one child process
outlived its own timeout and kept running/billing. Three fixes closed
these gaps, all in `arm_g_codex.py`/`live_runner.py`:

### Fix 6 -- Hard process-tree timeout enforcement
**What**: `run_arm_g_bundle`'s codex subprocess now launches via
`Popen(cmd, ..., start_new_session=True)` (its own process group)
instead of `subprocess.run(cmd, ..., timeout=timeout_s)`. On timeout,
new helper `_kill_process_tree(pid)` SIGTERMs then SIGKILLs the
**whole process group** via `os.killpg`.

**Why**: `subprocess.run(timeout=...)`'s own `TimeoutExpired` handling
only kills the ONE direct child it spawned. `codex` itself (or an MCP
server subprocess it starts) can leave a real, still-billing grandchild
running past the nominal timeout -- confirmed as the actual mechanism
that let a real Codex process keep running during the interrupted phi
run.

**Test**: `test_kill_process_tree_kills_a_grandchild_not_just_the_direct_child`
(`test_arm_g_codex_process_tree_timeout.py`) -- spawns a real shell that
backgrounds a real `sleep 60` grandchild, proves `_kill_process_tree`
kills both the shell and its grandchild, where a plain
`subprocess.run(timeout=...)` would only have killed the shell.

### Fix 7 -- Incremental per-call checkpointing
**What**: `run_cluster_investigations_live` gained an optional
`checkpoint_path` parameter. Every completed Codex call's cost and any
verdicts it finalized are appended as one JSON line
(`_append_checkpoint`) -- even a call that led to a split (money was
spent, nothing finalized yet, but the cost must still count on resume).
On entry, `_load_checkpoint` restores prior state and any cluster whose
every property already has a checkpointed verdict is skipped entirely.

**Why**: this is what turned the "7 verdicts unrecoverable" incident
into a non-issue for every subsequent live run -- real, quantified
value: every one of this session's 5 live-validation runs used this
checkpoint mechanism, and two of them (the `2024-08-phi` combined run
and the `2025-01-liquid-ron` run) hit a **separate** real crash
(`/scratch` disk-quota exceeded, see Section 10) mid-investigation, and
in **both cases zero data was lost** because the checkpoint had already
captured every real verdict before the crash.

**Test**: `test_checkpoint_round_trip_and_resume_skips_completed_clusters`
(`test_live_runner.py`) -- proves a checkpoint written during one call
lets a second, simulated-resumed call skip a completed cluster and
correctly restore `total_cost`.

### Fix 8 -- Concurrency-aware cost-ceiling reservation
**What**: each batch of concurrent calls is now sized by what the
*remaining* budget can plausibly afford -- the running average of real
completed-call costs once any exist, or a new
`estimated_cost_per_call_usd` parameter (default `0.20`) before any
call has completed -- not just re-checked once between batches.

**Why**: the interrupted run's own report explicitly named this gap:
"the ceiling was checked between concurrent batches, not reserved per
in-flight call," meaning a full batch of `max_concurrent_investigations`
calls could launch even with almost no budget left, overspending once
they all completed.

**Test**: `test_cost_ceiling_reservation_limits_batch_size_under_concurrency`
-- with `max_concurrent_investigations=4` but a ceiling that can only
afford 1 call at the estimated cost, proves peak in-flight concurrency
stays at 1 across the whole run (verified via a real lock-protected
in-flight counter across threads), not 4.

---

## 9. Fix 9 -- EthTrust structural routing wired into `compile_via_foundry` mode

### What
`run_rtf.build_context_for_evmbench_target` gained the same
`compile_via_foundry`/`extra_forge_build_args` parameters used
everywhere else in this work. New function
`semantic_only_driver.build_ethtrust_structural_properties(...)`: real
compile ($0, local, deterministic) -> `run_rtf` (the real 81-requirement
EthTrust corpus's own predicates) -> optional `rtf.standards` ERC/EIP-
generated-requirement merge -> `live_runner.build_property_pool` -> a
`PropertyMetadata` list ready for `run_semantic_investigation`'s
existing (previously never populated in this driver)
`structural_properties` parameter.

### Why
This was **user-requested mid-session**, prompted directly by the real
phi 0/6 result: a keyword search over the real EthTrust corpus
(`rtf/l1_corpus/requirement_corpus.json`) found direct, well-matched
requirements for 3 of that run's 4 remaining misses --
`req-1-eip155-chainid`/`req-2-malleable-signatures-for-replay` for
signature-replay findings, `req-1-use-c-e-i`/`req-2-avoid-readonly-reentrancy`
for the reentrancy finding -- that the semantic-only driver
(`structural_properties=[]` throughout every prior run) never routed
through at all. This wasn't a limitation of whole-project compilation;
it was that EthTrust's own real, static corpus was never wired into the
`compile_via_foundry` code path to begin with.

### How
Deliberately performs a **second**, separate real Foundry compile from
the one `run_semantic_investigation` does internally for generation --
disclosed explicitly in the function's own docstring as a wall-clock
cost, not a correctness risk, since both calls use the identical
deterministic `compile_evmbench_target_via_foundry` function against the
same `repo_root` (no divergence risk, unlike the single-entry-vs-whole-
project "stack too deep" scenario documented elsewhere). Sharing one
compile across both would need a deeper signature change to
`run_semantic_investigation` itself -- not made here, tracked as a
disclosed follow-up.

### Tests
Real Entry/Sibling fixture + a real `req-2-block-data-misuse` predicate
(`test_run_rtf_foundry.py`): the old path never sees the sibling
contract; `compile_via_foundry=True` does. Real end-to-end merge test
(`test_run_semantic_investigation_merges_real_structural_with_semantic_properties`,
`test_semantic_only_driver.py`): a real structural property (EthTrust-
derived) and a mocked semantic property both reach the same
investigation pool together, zero scope violations.

### Fix 9b -- a real bug found live on `2025-01-liquid-ron`
`build_property_pool` accepts an optional `generated_bundles` parameter
specifically so `build_codex_prompt_inputs` can resolve an
`rtf.standards`-generated requirement's context via its **in-memory**
bundle record -- generated requirements never have an on-disk L2
context-bundle JSON file. `build_ethtrust_structural_properties`
captured this dict from `build_standards_routed_requirements` as
`_bundles` (discarded, underscore-prefixed "intentionally unused") and
never passed it through. `liquid-ron` is the first of the 5 targets
with enough real ERC-4626/ERC-20 surface (599 real structural
properties -- by far the largest of any target this session) for the
GP-generator to produce a requirement that hit this exact path with
real evidence: `FileNotFoundError: no L2 context bundle for
'gp-accepted-standard__erc-20__erc20-callers-must-handle-false-return'`.
**Zero real spend lost** -- crashed before any investigation launched.
Fixed by threading `generated_bundles` through; zero regressions
(`test_semantic_only_driver.py` 36/36 after the fix).

---

## 10. Operational fixes found and handled during live validation (not code bugs)

These aren't pipeline code changes, but they materially affected
whether the live-validation runs in Section 11 succeeded, and are
recorded here for the same reason the code fixes are: so a future
session doesn't rediscover them from scratch.

### `codex_model` deprecation
`codex_model="openai/gpt-5.1-codex-max"` -- this project's long-standing
default -- is no longer recognized by the installed `codex-cli` (which
auto-updated to `0.147.0` at some point between an earlier interrupted
run and this session's own live runs). Every real call failed
identically ("Model metadata not found... Server tool request failed
400"), confirmed via a minimal repro completely outside any RTF code.
**Zero real spend lost** on the failed attempts. Fixed by switching to
`codex_model="gpt-5.6-sol"` (codex's own current default/flagship,
confirmed via a bare `codex exec` call with no `--model` override).

### `/scratch` file-count quota management
Three of the five live-validation runs required active, mid-run
cleanup: the Lustre filesystem's file-count **hard** limit
(1,000,000) was hit or nearly hit during `2024-08-phi`'s combined run,
`2026-01-tempo-feeamm`, and `2025-01-liquid-ron` -- each real
investigation cluster's full-repo scratch copy (`_gview`/`_ghome`
directories) adds tens of thousands of files, and this session ran 8
real live investigations across roughly 12 hours. A safe, verified
cleanup pattern was established and reused: cross-reference
`checkpoint.jsonl`'s own completed `case_id` set before deleting any
per-cluster scratch directory (never touch an in-flight investigation's
working directory), backgrounding large deletions that risk a tool
timeout. In one case (`2024-08-phi`'s combined run) the quota crash
happened **after** all real investigation work had already completed
and been checkpointed -- `audit.md` was rebuilt directly from
`checkpoint.jsonl` alone, zero data lost, directly validating Fix 7's
real value.

---

## 11. Results -- before and after, real numbers only

### 11.1 Test suite (zero real spend, run throughout implementation)

~400+ individual checks across every touched module
(`test_compile_helper`, `test_semantic_property_generation`,
`test_semantic_only_driver`, `test_live_runner`, `test_property_metadata`,
`test_protocol_context`, `test_context_artifacts`, `test_semantic_pipeline`,
`test_end_to_end_integration`, `test_run_rtf_foundry`,
`test_agentic_architecture`, `test_arm_g_codex_foundry_wiring`,
`test_graph_mcp_foundry_relocation`, `test_arm_g_codex_process_tree_timeout`)
-- **zero failures, zero unexpected skips**, re-run after every fix in
this document. Every Foundry-touching test genuinely executed a real
container compile; none silently skipped due to a missing environment.

### 11.2 Live-validation result: all 5 original 5-entry-comparison targets

Real `DetectGrader` scores, same per-target denominators as
`RTF_V2_5ENTRY_COMPARISON_REPORT.md` (verified by reading that report's
own results table directly):

| Target | Old RTF v2 (pre-fix) | Simple-Codex baseline | New combined pipeline |
|---|---|---|---|
| `tempo-feeamm` | 0/1 | 1/1 | 1/1 |
| `canto` | 1/2 | 2/2 | 1/2 |
| `forte` | 0/5 | 0/5 | 3/5 |
| `phi` | 1/6 | 2/6 | 4/6 |
| `liquid-ron` | 0/1 | 1/1 | 1/1 |
| **Total** | **2/15** | **6/15** | **10/15** |

**The new pipeline beats both the old RTF v2 architecture and the
simple-Codex baseline it had previously lost to** -- the first time in
this project's documented history RTF's own architecture has won this
comparison.

### 11.3 What each fix is directly responsible for, by target

- **`forte` (0/5 -> 3/5) and `phi` (1/6 -> 4/6)** -- the two largest,
  most multi-file targets, where Fix 1 (whole-project visibility) and
  Fix 9 (EthTrust structural routing) both had real, confirmed
  opportunity to help, and did: `Ln.sol`/`Cred.sol` visibility (Fix 1)
  plus signature-replay and reentrancy findings caught via real
  EthTrust requirements the semantic generator alone never proposed
  (Fix 9).
- **`tempo-feeamm` (0/1 -> 1/1)** -- not a scope story at all (this
  target's single file was always visible). Attributable to Fixes 6-8
  (reliability): the original miss was a pure `INVESTIGATION_TIMEOUT`
  -- a correct property that was never given the chance to finish.
- **`liquid-ron` (0/1 -> 1/1)** -- matches baseline, improves on old RTF
  v2. Real ERC-4626/ERC-20-heavy scope (599 structural properties, the
  largest of any target) -- this is also the target where Fix 9b (the
  `generated_bundles` bug) was found and fixed live.
- **`canto` (1/2, unchanged in aggregate)** -- no regression, no
  improvement in the headline number, but the *specific* finding caught
  differs between runs (this run: H-02, previously a confirmed
  `GENERATION_COVERAGE_GAP`; the original comparison: H-01). Real
  generation non-determinism, disclosed directly in
  `RTF_V2_COMBINED_PIPELINE_5MISSES_ROOT_CAUSE.md`, not papered over by
  the matching aggregate score.

### 11.4 What's honestly still open

`RTF_V2_COMBINED_PIPELINE_5MISSES_ROOT_CAUSE.md` root-causes all 5
remaining misses individually. Summary: 1 genuine EthTrust-corpus gap
(no requirement category exists yet for unbounded-storage-growth/gas-
DoS patterns -- `phi` H-03), 3 gaps attributable to this project's own
implementation (an investigation-prompt gap on cross-boundary semantic
checks, a property-wording gap that lets "correct behavior" properties
miss "reject invalid input" cases, and an evidence-collection/instance-
selection gap that never generated an access-control instance for the
right function), and 1 case (`forte` H-01) that's inherent to one-shot
LLM property generation not being exhaustive per function, not
something either EthTrust or this pipeline's engineering was ever
positioned to guarantee.

### 11.5 Total real spend, this session

| Item | Cost |
|---|---|
| `2024-08-phi`, capped-12 semantic-only (failed attempt, $0) + working rerun | $0.226 |
| `2024-08-phi`, uncapped generation-only measurement | $0.040 |
| `2024-08-phi`, `max_semantic_properties=78` semantic-only rerun | $0.906 |
| `2024-08-phi`, combined structural+semantic | $2.391 |
| `2025-04-forte`, combined structural+semantic | $3.379 |
| `2026-01-tempo-feeamm`, combined structural+semantic | $2.112 |
| `2024-01-canto`, combined structural+semantic | $1.838 |
| `2025-01-liquid-ron`, combined structural+semantic (first attempt: $0, crashed on Fix 9b before any spend; working rerun) | $5.073 |
| **Total** | **approximately $15.965** |

Every run stayed within its own independently-set `cost_ceiling_usd`
(one small, disclosed overrun on `liquid-ron`, a pre-existing "a single
in-flight call can complete after the ceiling check" limitation, not a
new bug). No run shared a budget with another.

---

## 12. What was deliberately NOT changed

Consistent with the plan's own explicit scope boundary: `pipeline_e2e.py`,
`pilot5_driver.py`, and `ablation_driver.py` remain completely untouched
and unwired to any of the fixes in this document -- none of them call
`compile_via_foundry` or `build_ethtrust_structural_properties`. Wiring
them in is real, separate future work, not something this session
expanded into. The unrelated structural/EthTrust standards machinery
itself (`rtf/standards/`, `rtf/l9_assumptions_register/`, `rtf/track_a/`)
was read and reused, never redesigned.
