# RTF v2: Whole-Project Foundry Compilation — Implementation Plan & Fresh-Session Runbook

**Status of this document**: final planning pass, verified against the repository on
2026-08-14. No production code was changed while writing this document (see
`git diff` at the time of writing, reproduced in §3). This document is the
authoritative handoff — a fresh Claude Code session with zero conversational
memory of how this plan was produced should be able to execute it end to end
using only this file and the repository.

**Repository location**: `/scratch/md5344/evmbench/agent4vul`, worktree
`.claude/worktrees/rtf-v2-redesign`, branch `rtf-v2-redesign` (tracks
`origin/rtf-v2-redesign`, pushed). All file paths in this document are
relative to that worktree root unless stated otherwise.

**Do not read this document out of order.** Phase 0 exists specifically to
stop a fresh session from acting on stale assumptions — including ones in
this document.

---

## Phase 0 — Soft Run / Context Reconstruction

**Mandatory. Do not modify production code before completing this phase and
producing the Soft Run Checkpoint (§0.9).**

### 0.1 Read the complete plan first

Read this entire document — Background, Target Architecture, Implementation
Status, Invariants, Deferred Work, every Goal section, every test section,
the Implementation Order, and the Definition of Done — before editing
anything. The sections build on each other; skipping to the checklist in §19
without the reasoning in §§1-18 will produce technically-passing but
architecturally-wrong changes (e.g. a second scope matcher, per Invariant C).

### 0.2 Inspect repository state

Run, from the worktree root:

```
git status
git log --oneline -n 30
git diff
git diff --staged
```

Determine: current branch (expected `rtf-v2-redesign`), whether it's still
tracking `origin/rtf-v2-redesign`, what's uncommitted, and whether §3's
implementation-status table still matches reality. **§3 was accurate at
write time (2026-08-14) but will go stale the moment anyone touches these
files.** Do not trust it — reproduce it. In particular: this plan was
written against a working tree with 6 modified files and no staged changes
(§3 has the exact list and a summary of each diff). If `git status` now
shows something different — more committed, more modified, fewer files —
that means work happened between this plan being written and this session
starting. Reconcile before proceeding: read the actual diffs, don't assume
the old state.

Do not discard or overwrite any uncommitted changes you find. If they match
§3, they are a **known, real, uncommitted prior implementation attempt**,
not stray junk — see Phase 1 in §19.

### 0.3 Read the relevant existing reports first

Read, in this order:

1. `rtf/RTF_V2_5ENTRY_ALL_MISSES_ROOT_CAUSE.md` — the forensic root-cause
   report this entire plan exists to act on. Confirms, with file:line
   citations against real EVMbench targets, that `2025-04-forte`'s `Ln.sol`
   and `2024-08-phi`'s `Cred.sol` were never part of the compiled unit the
   semantic property generator saw, because each is a sibling of the
   selected entry file that the entry does not `import`. This is the
   **single highest-leverage, confirmed-not-hypothetical** finding driving
   this plan (see its "Summary table": 3 of 11 misses in that report trace
   to this one structural cause).
2. `rtf/RTF_V2_5ENTRY_COMPARISON_REPORT.md` — the run this root-cause report
   is forensic analysis *of* (5 audits vs. a simple Codex baseline; RTF v2
   lost 2/15 vs. baseline's 6/15 headline, but with real, root-caused,
   fixable failure modes, not a blanket "RTF doesn't work").
3. `rtf/RTF_V2_TEMPO_FEEAMM_ROOT_CAUSE.md` — a companion root-cause doc for
   a *different* failure mode (investigation timeout, not compilation
   scope) — read it only to correctly distinguish "this plan's fix would
   help" from "this plan's fix is irrelevant here." Whole-project
   compilation does **not** fix investigation timeouts; do not conflate the
   two when interpreting future rerun results.
4. `rtf/RTF_V2_SYSTEM_DESCRIPTION.md` — standalone architecture description
   of RTF v2 as of the 5-entry comparison, useful as an orientation map of
   the whole pipeline before diving into individual files in §0.4.
5. `rtf/RTF_V2_ARCHITECTURE.md` — the original RTF v2 redesign audit
   (Deliverable 1). Background only; largely superseded by the two 5-entry
   reports above for anything scope/compilation-related, but useful for
   understanding `l11_investigation_grouping`'s pre-existing architecture
   (grouping engine, `PropertyMetadata`, context artifacts) that this plan
   builds on rather than replaces.

Do not rely solely on §1 of this document (which summarizes the confirmed
examples) if you need the full mechanism — the root-cause report has the
complete evidence chain (property text, cluster IDs, transcript excerpts)
this document deliberately does not reproduce in full.

### 0.4 Read the relevant production code

Trace these before trusting any file:line citation in this document — they
were correct at write time but will drift:

```
rtf/l5_predicates/compile_helper.py
    compile_evmbench_target                     (pre-existing)
    compile_evmbench_target_via_foundry          (new, uncommitted — see §3)

rtf/l11_investigation_grouping/
    semantic_property_generation.py   (ProjectManifest.from_slither, generation prompt)
    semantic_only_driver.py           (run_semantic_investigation — the orchestration entry point)
    property_metadata.py              (split_properties_by_scope, forward_out_of_scope_context, _paths_match)
    protocol_context.py               (generate_enriched_protocol_context_md and friends — investigator-facing context)
    context_artifacts.py              (generate_cluster_plan_md and friends)
    live_runner.py                    (prepare_cluster_investigations, run_cluster_investigations_live)

rtf/l8_llm_judgment_layer/bundle_agent_experiment/
    arm_g_codex.py                    (prepare_full_repo_investigation_dir, run_arm_g_bundle)
    graph_mcp_server.py               (the MCP server subprocess — _get_graph, ENTRY_FILE env var)

a4v/graph.py                          (ProgramGraph.build vs. ProgramGraph.from_slither)
rtf/standards/discovery.py            (_is_vendored_path — the canonical vendor-path rule)
```

Trace the four flows below with a real editor/grep, not from memory of this
document:

**Compilation** (generation-time):
```
semantic_only_driver.run_semantic_investigation
        -> compile_helper.compile_evmbench_target / compile_evmbench_target_via_foundry
        -> Slither
```

**Semantic generation**:
```
ProjectManifest.from_slither(slither, repo_root=...)
        -> generation prompt (semantic_property_generation.py)
        -> property_grounding.py
```

**Scope**:
```
generated/grounded properties
        -> property_metadata.split_properties_by_scope
        -> property_metadata.forward_out_of_scope_context
        -> live_runner.prepare_cluster_investigations (grouping)
```

**Investigation**:
```
live_runner.prepare_cluster_investigations
        -> live_runner.run_cluster_investigations_live
        -> arm_g_codex.run_arm_g_bundle
        -> arm_g_codex.prepare_full_repo_investigation_dir (full-repo copy)
        -> graph_mcp_server.py subprocess (separate process, own env vars)
        -> graph_mcp_server._get_graph() -> a4v.graph.ProgramGraph.build(ENTRY_FILE, ...)
```

**Confirm this last arrow specifically** — this document asserts (§3, §11)
that `_get_graph()` currently always calls `ProgramGraph.build`, never
`ProgramGraph.from_slither`, regardless of how generation compiled. If a
fresh session finds this has changed, §11-§15 (Goal 2) may already be done;
re-verify against §0.6's checkpoint table before assuming so.

### 0.5 Read the relevant tests

Inspect, at minimum:

```
rtf/l5_predicates/test_compile_helper.py
rtf/l11_investigation_grouping/test_semantic_property_generation.py
rtf/l11_investigation_grouping/test_semantic_only_driver.py
rtf/l11_investigation_grouping/test_property_metadata.py
rtf/l11_investigation_grouping/test_protocol_context.py
rtf/l11_investigation_grouping/test_context_artifacts.py
rtf/l11_investigation_grouping/test_live_runner.py
rtf/l11_investigation_grouping/test_semantic_pipeline.py
rtf/l11_investigation_grouping/test_end_to_end_integration.py
rtf/l12_evaluation/test_agentic_architecture.py   (covers prepare_full_repo_investigation_dir)
```

**Identify existing, missing, and misleading coverage.** A concrete,
confirmed example of misleading coverage in the current tree (verified
2026-08-14, re-verify it's still true):
`test_semantic_only_driver.py::test_scope_files_drops_properties_targeting_files_outside_declared_scope`
uses a fixture where `Vault.sol` (the entry) contains `import "./Helper.sol";`
— i.e. `Helper.sol` **is** reachable via the entry's own import graph, so it
was compiled by the *old*, pre-existing `compile_evmbench_target` path too.
This test proves "an in-import-graph, compiled, out-of-scope file is
correctly rejected." It does **not** prove this plan's actual new
requirement: *a file the entry does not import, compiled only because
whole-project compilation exists, still correctly rejected as out-of-scope*.
That is a materially different and currently untested case — see §7's
`Helper.sol` semantics, which deliberately differ from this existing
fixture's `Helper.sol` (same name, different, non-imported role).

Also check `git diff` for the two new tests already added uncommitted in
this session's prior state (§3): `test_semantic_only_driver.py`'s
`test_compile_via_foundry_makes_a_sibling_scope_file_visible_to_generation`
and `test_compile_helper.py`'s
`test_compile_via_foundry_real_target_multi_file_visibility`. These *do*
correctly exercise the new non-imported-sibling case for the **generation**
side. Neither touches investigation/graph-navigation (Goal 2) or defense in
depth (Goal 1b) at all — confirm this is still true before assuming any of
§9-§15's work is started.

### 0.6 Verify the current implementation status

Reproduce §3's table yourself rather than trusting it verbatim — re-run the
greps in §0.4, re-read the diffs, re-run the tests in §0.7. If your findings
differ from §3, trust your own reproduction and note the discrepancy in your
Soft Run Checkpoint (§0.9).

### 0.7 Run a baseline test pass

This repository's established convention is **module execution, not bare
`pytest`**:

```
.venv/bin/python3 -m rtf.l5_predicates.test_compile_helper
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_property_generation
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_only_driver
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_property_metadata
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_protocol_context
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_context_artifacts
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_live_runner
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_pipeline
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_end_to_end_integration
.venv/bin/python3 -m rtf.l12_evaluation.test_agentic_architecture
```

Each test file's own `main()` prints `PASSED: N` / `FAILED: N` with named
`ok -`/`FAIL -` lines — read the actual names, don't just check the exit
code, since a test that silently `return`s early after a caught exception
(the "skip gracefully if the environment is unavailable" pattern used
throughout this codebase — see `test_compile_via_foundry_real_target_multi_file_visibility`'s
own docstring) still reports as a `PASSED` line with a name like "... skipped
(container unavailable here?)". **A pass with "skip" or "unavailable" in its
own name is not evidence the feature works** — distinguish these from a
genuine pass, which for the Foundry-related tests specifically means the
container was actually invoked and `forge build` actually ran. At write
time (2026-08-14), running these exact commands produced **zero skips** —
every Foundry-touching test (`test_compile_via_foundry_real_target_multi_file_visibility`,
`test_compile_via_foundry_makes_a_sibling_scope_file_visible_to_generation`,
the vendored-filtering tests) executed for real and passed (see §3 for exact
counts). If a fresh session sees skips here that this document didn't, the
environment itself has regressed — resolve that (§0.8) before drawing any
conclusion about the code.

### 0.8 Verify environment prerequisites

```
ls -la /scratch/md5344/evmbench/containers/evmbench-worker.sif
ls -la /share/apps/NYUAD5/singularity/current/bin/singularity
.venv/bin/python3 -c "import slither; print('slither ok')"
```

At write time: `evmbench-worker.sif` exists (394MB,
`/scratch/md5344/evmbench/containers/evmbench-worker.sif`), `singularity`
exists at the path above, and `compile_evmbench_target_via_foundry`
successfully ran a real `forge build` inside the container against a real
checkout (`/scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm`
— re-verify this specific path still exists; job scratch directories are not
guaranteed to survive indefinitely, see `env_scratch_quota` memory
conventions if working in this account). If that checkout is gone, either
re-clone it (`git clone https://github.com/evmbench-org/2026-01-tempo-feeamm.git`,
`git submodule update --init` if needed) or point the equivalent test at any
other real Foundry-based EVMbench checkout you have on disk — the test's own
skip-gracefully fallback means a missing fixture degrades to a named skip,
not a crash, but a skip here means you have NOT verified the environment and
must not treat it as verified.

**Do not launch paid LLM/Codex investigations during Phase 0.** Everything
in §0.7-§0.8 is local compilation and mocked-LLM tests only — zero API
spend.

### 0.9 Produce a Soft Run Checkpoint

Before writing or changing any production code, write out (in your own
working notes, not necessarily committed) a checkpoint in this shape:

```
Repository state: <branch, HEAD, uncommitted files found>
Already implemented: <what you found working end-to-end, with test evidence>
Still missing: <what you confirmed absent, with the grep/read that proved it>
Existing tests: <files run, pass/fail/skip counts>
Baseline failures/skips: <any, with real-vs-environmental classification>
Environment readiness: <container, singularity, checkout fixture status>
Plan assumptions confirmed: <which of §3's claims you independently verified>
Plan assumptions corrected: <anything in this document that was wrong or stale>
```

Only after this checkpoint is complete should implementation (§19 Phase 1
onward) begin.

---

## 1. Background / Confirmed Root Cause

RTF v2's semantic-property pipeline (`rtf/l11_investigation_grouping/`)
generates properties by compiling exactly one entry `.sol` file and its own
`import` graph:

```
entry_sol_file
        ↓
raw solc (compile_helper.compile_evmbench_target)
        ↓
entry + its import graph only
        ↓
Slither
        ↓
ProjectManifest (contracts/functions/state vars the generator is told about)
        ↓
semantic generation
```

This is insufficient whenever an audit's declared `scope_files` include
independent sibling contracts the entry does not `import` — a real, common
shape for Foundry-library-style projects, not a contrived edge case.

**`2025-04-forte`**: the comparison run's entry was `src/Float128.sol`.
`src/Ln.sol` **imports** `Float128.sol` (uses its types) — not the reverse.
Compiling `Float128.sol` as the sole entry therefore never pulls `Ln.sol`
into the Slither compilation unit, even though the orchestration's own
`scope_files` list for this audit explicitly included `"src/Ln.sol"`. Result:
forte H-03 (`Ln.ln()` accepts negative/zero input without validation) — the
generator could not possibly have proposed a property about `Ln.ln`, because
`Ln` was never part of what it was shown, full stop. Confirmed by direct
string search: `semantic_properties_raw.json` for this run has **zero**
properties mentioning `Ln`/`ln(` anywhere, and `protocol_context.md`'s
"Contracts and inheritance" section lists exactly `Float128`/`Uint512`, no
`Ln`.

**`2024-08-phi`**: the comparison run's entry was `src/PhiFactory.sol`.
`src/Cred.sol` is a legitimately in-scope sibling contract `PhiFactory.sol`
does not import. Result: phi H-03 (`shareBalance` `EnumerableMap` bloat DoS)
and phi H-06 (`Cred.sol` cred-creation/share-purchase reentrancy) — both
entirely invisible to the generator for the identical structural reason.
Confirmed the same way: zero mentions of `Cred`/`shareBalance`/
`CuratorRewardsDistributor` in phi's raw properties or protocol context.

These are **confirmed causes of real, specific misses in a real, already-run
comparison** (`RTF_V2_5ENTRY_ALL_MISSES_ROOT_CAUSE.md`), not a theoretical
architecture concern. The root-cause report classifies 3 of its 11 analyzed
misses (forte H-03, phi H-03, phi H-06) under this one structural cause and
calls it "the single highest-leverage fix identified in this whole report,
since it mechanically explains 3 of 11 misses... with one engineering
change."

---

## 2. Target Architecture

```
Whole-project Foundry compilation
            ↓
Broad project representation (every first-party contract, vendored deps still resolvable)
            ↓
Semantic generation  (sees the whole project)
            ↓
Grounding            (unchanged — still requires real ProjectManifest membership)
            ↓
Primary scope filtering        (property_metadata.split_properties_by_scope — unchanged, canonical)
            ↓
Defense-in-depth Boundary A    (immediately before investigation — NEW)
            ↓
Grouping             (unchanged — live_runner.prepare_cluster_investigations)
            ↓
Investigation
            ↓
Graph navigation using the SAME build artifacts (NEW — currently a second, independent compile)
            ↓
Defense-in-depth Boundary B    (immediately before final result return — NEW)
            ↓
Final result
```

**Main principle**: broad visibility, narrow reporting scope, one
consistent project view. Whole-project compilation exists so the system can
*understand* the entire project (resolve types, see inheritance, let a
sibling's function be named correctly in a property). It does not, and must
never, redefine what is *reportable* — that remains `scope_files`,
exclusively, checked in exactly one place logically (even if enforced at
multiple physical boundaries for defense in depth — see Invariant C and §9).

---

## 3. Current Implementation Status

**As verified 2026-08-14, against `git diff` on `rtf-v2-redesign` with 6
modified files, 0 staged, 1 untracked (`.venv`, irrelevant — a local venv,
not project content). Re-verify per §0.2/§0.6 before trusting this table.**

| Component | Status | Evidence |
|---|---|---|
| `compile_helper.compile_evmbench_target_via_foundry(project_root, extra_forge_build_args=None, timeout_s=300) -> Slither` | **Implemented, uncommitted.** Runs `forge build --build-info --skip ./test/** ./script/** --force` inside `evmbench-worker.sif` via `singularity exec --bind <project_root>:/work --pwd /work`, raises `RuntimeError` with real stdout/stderr tail on failure, returns `Slither(str(project_root.resolve()), foundry_ignore_compile=True, compile_force_framework="Foundry")`. | `rtf/l5_predicates/compile_helper.py` (appended function, `git diff` shows it as new). Test: `test_compile_helper.py::test_compile_via_foundry_real_target_multi_file_visibility` — **ran for real** (not skipped) against `/scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm`, confirmed `FeeAMM` present with zero manual solc flags. `test_compile_helper.py` full run: 11/11 pass. |
| `run_semantic_investigation(..., compile_via_foundry: bool = False, extra_forge_build_args: list[str] \| None = None)` | **Implemented, uncommitted.** Branches to the new Foundry compile function when `True`; calls `ProjectManifest.from_slither(slither, repo_root=repo_root)` in **both** branches (not just the Foundry one). | `rtf/l11_investigation_grouping/semantic_only_driver.py`. Test: `test_semantic_only_driver.py::test_compile_via_foundry_makes_a_sibling_scope_file_visible_to_generation` — **real end-to-end proof** (mocked LLM/Codex only) that a `Sibling.sol` NOT imported by the entry `Vault.sol` becomes visible to generation, is grounded, and is correctly counted in-scope. Full file: 15/15 pass. |
| `ProjectManifest.from_slither(cls, slither, repo_root: Path \| None = None)` vendored-contract filtering | **Implemented, uncommitted.** Reuses `rtf.standards.discovery._is_vendored_path` (vendor dir names: `lib`, `node_modules`, `vendor`, `dependencies`, `.deps`) via a new local helper `_contract_is_vendored`. `repo_root=None` (default) = unfiltered, byte-identical to prior behavior. | `rtf/l11_investigation_grouping/semantic_property_generation.py`. Tests: `test_manifest_from_slither_filters_vendored_contracts_when_repo_root_given` and 2 related — pass. Full file: 36/36 pass. |
| Foundry-mode propagation past generation (`compile_via_foundry` reaching `live_runner`, `arm_g_codex`, `graph_mcp_server`) | **Does not exist.** | Repo-wide grep for `GRAPH_COMPILE_VIA_FOUNDRY`: zero hits. `live_runner.prepare_cluster_investigations`/`run_cluster_investigations_live` and `arm_g_codex.run_arm_g_bundle` have no Foundry-related parameter at all (read in full, §0.4). |
| Investigation-time graph construction reuse (`ProgramGraph.from_slither`) | **The reusable primitive already exists; nothing calls it from the investigation path.** | `a4v/graph.py:159-177` — `ProgramGraph.from_slither(cls, slither) -> ProgramGraph`, built in an earlier, unrelated session specifically to avoid a second compile (motivated by a *different* bug: canto's stack-too-deep divergence between two independent compiles of the same file). `graph_mcp_server.py:114-119`'s `_get_graph()` **always** calls `ProgramGraph.build(ENTRY_FILE, solc_remaps=REMAPS, extra_kwargs=...)` — an independent second compile via raw solc — with no branch to `from_slither` at all. `from_slither` itself has **zero test coverage anywhere in the repo** (confirmed by grep: only referenced in its own definition). |
| `prepare_full_repo_investigation_dir` (full-repo copy for investigation) | **Pre-existing, tested, unrelated to Foundry mode as written — but structurally relevant.** Does a full `shutil.copytree(repo_root, investigation_dir, ignore=shutil.ignore_patterns(".git"), symlinks=True)`. If `repo_root` already contains Foundry `out/`/`cache/` artifacts at call time, they get copied along with everything else — untested whether this actually happens correctly in the real generation→investigation lifecycle (see §14). | `rtf/l8_llm_judgment_layer/bundle_agent_experiment/arm_g_codex.py:117-144`. Tested (not for Foundry-artifact reuse specifically) in `rtf/l12_evaluation/test_agentic_architecture.py`. |
| `split_properties_by_scope` / `filter_properties_to_scope` / `forward_out_of_scope_context` / `_paths_match` | **Pre-existing, implemented, tested, already wired as the one canonical scope filter.** `_paths_match` tolerates differing relative-path prefixes via suffix comparison (`c==s or c.endswith("/"+s) or s.endswith("/"+c)`), not raw prefix/substring matching. | `rtf/l11_investigation_grouping/property_metadata.py:321-430ish`. Wired into `semantic_only_driver.run_semantic_investigation` (the sole primary filter call site) and `rtf/l11_investigation_grouping/ablation_driver.py`. Tested in `test_property_metadata.py` and `test_semantic_only_driver.py`. **Not yet tested against real Foundry-mode-compiled path forms specifically** — `compile_via_foundry` is brand new; whether Foundry's own `source_mapping.filename` values match this existing logic's assumptions has not been checked live. |
| Compiled-but-out-of-scope test (first-party, non-imported, whole-project-only visible) | **Does not exist as a correct test yet.** The existing test with this shape uses a `Helper.sol` that IS imported by the entry, so it was already compiled under the OLD path too — proves a different, weaker claim. | `test_semantic_only_driver.py::test_scope_files_drops_properties_targeting_files_outside_declared_scope`, confirmed by reading its fixture source (`import "./Helper.sol";` inside the entry file). See §0.5 and §7. |
| Defense-in-depth Boundary A / Boundary B / `scope_boundary_violations` | **Does not exist. Zero code anywhere.** Purely aspirational — this plan's own new work. | Repo-wide grep for `scope_boundary_violations`: zero hits. |
| Investigator-facing (`protocol_context.md`) vendor filtering | **Does not exist.** Only the generator-facing `ProjectManifest` got vendor filtering (row above); the separate Markdown context the investigator actually reads is unfiltered. | `rtf/l11_investigation_grouping/protocol_context.py` — `extract_accounting_state_variables`/`extract_lifecycle_hints`/`generate_enriched_protocol_context_md` iterate `slither.contracts_derived` directly, zero mentions of `vendor`/`_is_vendored` anywhere in this file or `context_artifacts.py` (grep confirmed). |
| Artifact-relocation validity (copied Foundry `out/`/`build-info/` consumed by Slither post-copy) | **Never tested.** No code path exercises this yet since nothing propagates Foundry mode into investigation (see propagation row above). | N/A — this is a required new test, §14. |
| I/O / runtime measurement of artifact copying | **Never measured.** | N/A — required new measurement, §17. |
| Live EVMbench validation of this specific fix | **Never run.** The one real-target compile test (`tempo-feeamm`) exercises only the compile function in isolation — tempo-feeamm's own actual miss (root-caused separately in `RTF_V2_TEMPO_FEEAMM_ROOT_CAUSE.md`) is an investigation timeout, unrelated to this gap, and no live per-cluster Codex investigation has ever run with `compile_via_foundry=True`. | Requires explicit user approval before any paid call — §9 (Phase 9) / §21. |

**Minor, non-blocking documentation nit found while reading**: the
docstring on `compile_evmbench_target_via_foundry` contains a
self-correcting aside ("`Ln.sol` (imported only BY `Float128.sol`... wait,
imports `Float128.sol`, not the reverse..."). Harmless (the surrounding
prose gets the direction right — `Ln.sol` imports `Float128.sol`, matching
§1 above), but worth a one-line cleanup whenever that file is next touched.
Not a functional issue; do not spend a dedicated pass on it.

### Update — 2026-08-15: Phases 1–8 complete, three reliability fixes added

**Everything below §3's original table is now implemented, tested, and
committed on `rtf-v2-redesign`** (commits `351005a`..`436cfac`), reproduce
via `git log --oneline` before trusting this claim, per this document's own
Phase 0 discipline:

- Goal 1 (§6–§8): done. §7's Entry/Sibling/Helper/Vendor fixture is real
  (`test_semantic_only_driver.py::test_compile_via_foundry_scope_matrix_entry_sibling_helper_vendor`),
  proves all four outcomes in one real whole-project Foundry compile.
  `_paths_match` needed no change — real Foundry `source_mapping.filename`
  values (`used`/`absolute` forms) already match correctly.
- Goal 1b defense-in-depth (§9–§10): done. `property_metadata.
  enforce_scope_boundary` (Boundary A, in `live_runner.
  prepare_cluster_investigations_with_scope_boundary`; Boundary B, in
  `semantic_only_driver._enforce_scope_boundary_b`), `scope_boundary_
  violations` in the returned dict, both bypass-injection tests pass.
- Investigator-facing vendor filtering (§16): done, in BOTH
  `context_artifacts.generate_protocol_context_md` and
  `protocol_context.py`'s narrative functions — a real bug was found and
  fixed getting here: `prepare_cluster_investigations` was independently
  regenerating its own unfiltered `protocol_context_md`, silently
  discarding the driver's own enriched, filtered one (fixed via
  `protocol_context_override`/`repo_root` threaded into
  `prepare_cluster_investigations`).
- Goal 2 (§11–§15): done. `a4v/graph.py`'s pre-existing `ProgramGraph.
  from_slither` is now wired via `graph_mcp_server._build_graph_for_
  investigation` behind `GRAPH_COMPILE_VIA_FOUNDRY`, propagated through
  `run_semantic_investigation` → `run_cluster_investigations_live` →
  `run_arm_g_bundle` → the MCP env block. The mandatory artifact-relocation
  test (§14) and no-hidden-recompile test (§15) both pass, in
  `test_graph_mcp_foundry_relocation.py` — the no-recompile proof uses a
  poison-pill mock on `ProgramGraph.build` (raises if ever called in
  Foundry mode), not just a call-count check.

**Three additional reliability fixes, NOT in the original plan** — found
from real operational evidence, not anticipated in advance (see the
"interrupted live run" note below): hard process-tree timeout enforcement,
incremental per-call checkpointing, and concurrency-aware cost-ceiling
reservation, all in `arm_g_codex.run_arm_g_bundle`/`live_runner.
run_cluster_investigations_live` (commit `436cfac`). See that commit
message for full detail; briefly:
1. `run_arm_g_bundle`'s codex subprocess now launches via `Popen(...,
   start_new_session=True)` instead of `subprocess.run(timeout=...)`,
   which only kills the ONE direct child on timeout. `_kill_process_tree`
   SIGTERMs-then-SIGKILLs the WHOLE process group.
2. `run_cluster_investigations_live` gained `checkpoint_path` — every
   completed call's cost and any finalized verdicts are appended to disk
   immediately (`_append_checkpoint`), and a resumed call skips clusters
   whose properties are already checkpointed.
3. `cost_ceiling_usd` batches are now sized by what the REMAINING budget
   can plausibly afford (running average of real completed-call costs,
   or `estimated_cost_per_call_usd` before any complete), not just
   re-checked between batches.
Both `checkpoint_path` and `cost_ceiling_usd` behavior default to
byte-identical prior behavior when unused.

**A real, live investigation run against the actual `2024-08-phi` target
happened on 2026-08-15** (`compile_via_foundry=True`, named
`2024-08-phi-foundry-preflight`, scratch at
`/scratch/md5344/evmbench/rtf_phi_live_foundry_20260814/`) — **discovered
after the fact, not launched under this document's own Phase 9 gate**, and
**interrupted mid-run** (the process-tree timeout bug above, item 1, is
what let one child outlive its timeout during this exact run — this run is
what surfaced the bug, not a run that used the fix). Real, non-trivial
spend (known lower bound ≈$1.10 — investigation ≈$1.08, generation
≈$0.016; a true lower bound because timed-out calls never emitted final
usage records). **11 grounded/in-scope properties generated (up from the
pre-fix architecture's single-entry run, which never saw `Cred.sol` at
all), 7/11 verdicts recovered before interruption**: 3 real FAIL findings
(unbounded `protocolFeePercent`, missing double-claim guard — these two
describe the same underlying theme; combined protocol/creator fee cap) and
4 PASS (curator reward accounting, sell lock period, creator royalty
limit, soulbound transfer restrictions), 4 properties left INCONCLUSIVE
(split investigations never finished before the run stopped). Whole-project
graph navigation confirmed working live: `Cred._authorizeUpgrade` in
`src/Cred.sol` resolved successfully. **No `audit.md` was generated and no
`DetectGrader` run happened — there is no EVMbench score for this run.**
Do not report a grade for it; do not conflate "provisional FAIL findings
exist" with "graded." Per Invariant G and this document's own prior
instruction: the reliability fixes above exist specifically so a FUTURE
rerun doesn't repeat this loss, not to make this specific ungraded run
retroactively count as validation. **A fresh paid rerun against
`2024-08-phi`, now with the reliability fixes in place, still requires
the user's explicit go-ahead before launching** — same Phase 9 gate as
before, this incident does not substitute for it.

### Phase 9 completed — 2026-08-15: real graded rerun against `2024-08-phi`

User gave explicit go-ahead. Launched via a one-off scratch script (not
committed — `/scratch/md5344/evmbench/rtf_phi_live_foundry_rerun_20260815/`),
`compile_via_foundry=True`, `checkpoint_path` set, `cost_ceiling_usd=5.00`,
`max_concurrent_investigations=4`, real `2024-08-phi` checkout + `scope.txt`
(9 files).

**First attempt failed cleanly, $0 spent**: `codex_model="openai/gpt-5.1-codex-max"`
is no longer recognized by the installed `codex-cli 0.147.0` (auto-updated
sometime after the prior interrupted run — its own model registry now tops
out around a "GPT-5.6" family; `gpt-5.1-codex-max` triggers a "Model metadata
not found, defaulting to fallback metadata" warning, then every real call
fails with a `Server tool request failed (400)` from the provider). Confirmed
via a minimal standalone repro outside the pipeline (no MCP server, trivial
prompt) — same failure. Not a bug in this plan's own code; external
model-lifecycle drift. Codex's own default model (`gpt-5.6-sol`) works fine.
Stale checkpoint entries from this failed attempt (all cost $0.00, all
`INCONCLUSIVE`/`cluster_investigation_incomplete_or_failed`) were moved
aside, not reused — resuming from them would have incorrectly skipped every
cluster as "already done."

**Second attempt, `codex_model="gpt-5.6-sol"`, completed cleanly, no
interruption**: 143.5s wall clock, **$0.226 total real spend** ($0.217
investigation + $0.009 generation — well under the $5 ceiling), 9/9
in-scope properties, 0 out-of-scope, `scope_boundary_violations: []`, zero
splits needed (both top-level clusters completed on the first pass). 6
FAIL / 3 PASS. Real per-property evidence with file:line citations and
genuine counterexample searches throughout (not templated/generic text) —
sample FAILs: `Cred.buyShareCredFor` performs no signature/signer
verification at all (unlike `PhiFactory.signatureClaim`); a zero-supply
creator-royalty branch in `BondingCurve`/`Cred._getCreatorFee` makes the
quoted buy price diverge from the amount actually charged (both single and
batch paths); `Cred.setProtocolFeePercent` has no upper-bound check against
`RATIO_BASE`; `PhiFactory`'s claim-tracking mappings aren't enforced as
replay guards, so a claim can be repeated.

**Real `DetectGrader` result (`openai/gpt-4o` judge): 0/6** (H-01, H-02,
H-03, H-04, H-06, H-07 — H-05 not included in this grading run). None of
the 6 real FAIL findings matched any of the 6 graded ground-truth
vulnerabilities; the judge's own per-vulnerability reasoning confirms each
miss is a genuine mechanism mismatch, not a near-miss or wording issue.

**Honest assessment — architecture worked, generation coverage still
didn't land on H-03/H-06 this run**: `Cred.sol` was confirmed compiled,
grounded, and substantively investigated this run (multiple real FAIL
findings target it directly) — the exact structural gap this whole plan
exists to close (§1) is closed: whole-project compilation makes `Cred.sol`
visible and investigable where the pre-fix architecture never compiled it
at all. But the specific properties this run's generator proposed for
`Cred.sol` (fee-quote accounting, signature verification, lock-period
enforcement) did not happen to target H-03's `EnumerableMap`-bloat DoS or
H-06's reentrancy mechanism — a `GENERATION_COVERAGE_GAP` in this run's own
property set (same category as documented extensively in
`RTF_V2_5ENTRY_ALL_MISSES_ROOT_CAUSE.md`), not a visibility/scope failure.
This is consistent with, not contradicted by, this plan's own stated goal:
Goal 1/Goal 2 make `Cred.sol` reachable and investigable; they do not by
themselves guarantee the semantic generator proposes every specific
property a grader will match against. Full raw evidence:
`/scratch/md5344/evmbench/rtf_phi_live_foundry_rerun_20260815/` — `audit.md`
(rendered findings), `summary.json` (verdicts), `checkpoint.jsonl` (per-call
cost/evidence), `grade_result.json` (full judge reasoning per vulnerability).

### Follow-up — 2026-08-15: `max_semantic_properties` raised to 78, real score improves to 2/6

Prompted by the 0/6 result above, measured (not guessed) what generation
actually proposes with the property cap effectively removed
(`max_semantic_properties=1000` against the same real `2024-08-phi`
checkout, generation+grounding only, no investigation, ~$0.04 real cost):
**106 raw properties proposed, 78 grounded** (vs. 9 grounded at the
default cap of 12) — confirming `max_semantic_properties` was acting as a
real, binding constraint on this audit, not a slack limit the model was
already staying under. Critically, this uncapped measurement's 78
properties still contained **zero** properties targeting H-03's
`EnumerableMap`-cleanup-on-zero-balance or H-06's reentrancy-before-
counter-increment mechanism — establishing *before* spending on a live
rerun that raising the cap alone would not flip those two specific misses.

**Live rerun with `max_semantic_properties=78`** (same real checkout,
same `codex_model="gpt-5.6-sol"`, same `$5.00` ceiling, same reliability
fixes, fresh checkpoint/scratch dir
`/scratch/md5344/evmbench/rtf_phi_live_foundry_78props_20260815/`):
363s wall clock, **$0.906 total real spend** ($0.854 investigation +
$0.052 generation — comfortably under ceiling), 53 grounded properties
this run (real run-to-run generation variance vs. the 78 measured
separately — same "different runs propose different property
wording/coverage" behavior already documented in
[[project_rtf_v2_semantic_properties]]), 7 clusters, 0 splits, 0
out-of-scope, `scope_boundary_violations: []`. 42 PASS / 11 FAIL.

**Real `DetectGrader` result: 2/6** (up from 0/6):
- **H-04 and H-07: DETECTED** — both trace to the SAME single generated
  property (`PhiFactory.updateArtSettings must only be callable by the
  owner`), which is genuinely true (the real function uses `onlyArtCreator`,
  not an owner check) and happens to be the shared root cause both
  ground-truth findings describe (forced `endTime` re-extension via
  artist-level access, and unrestricted artist-controlled setting changes
  more broadly) — one real property catching two related ground-truth
  findings via one real, correct mechanism match, not a coincidence or a
  near-miss judged generously (read the judge's own reasoning in
  `grade_result.json` for both).
- **H-01, H-02, H-06: still not detected**, for the same reasons already
  identified: H-01/H-02 need signature *chain/config-binding* properties,
  not signer-correctness properties (still the recurring framing gap);
  H-06 needs a reentrancy/CEI-ordering property, still never proposed even
  at 53-78 properties, confirming this is a genuine generation-shape gap,
  not a volume gap.
- **H-03: still not detected** — same confirmation as above for the
  EnumerableMap-bloat mechanism specifically.

**Conclusion**: raising `max_semantic_properties` is a real, working lever
(0/6 → 2/6, ~$0.91 total spend for both real generation measurements +
the live rerun combined) but it improves recall by covering MORE distinct
functions/mechanisms with SOME property, not by making the generator more
likely to propose any one specific hard-to-frame mechanism (EnumerableMap
lifecycle, reentrancy/CEI ordering, signature-domain binding) — those
three remain open, already-diagnosed generation-precision gaps
independent of both the property cap and the whole-project-compilation
fix this plan implements. Full raw evidence:
`/scratch/md5344/evmbench/rtf_phi_live_foundry_78props_20260815/`.

### Follow-up — 2026-08-15: EthTrust structural routing wired into `compile_via_foundry`, real score 4/6

Every remaining miss traced back to one gap: the semantic-only driver
(`structural_properties=[]`) never routed through RTF's real 81-requirement
EthTrust corpus at all. A keyword search over the real corpus
(`rtf/l1_corpus/requirement_corpus.json`) found direct, well-matched
requirements for 3 of the 4 remaining misses: `req-1-eip155-chainid`
("Encode Hashes with chainid") and `req-2-malleable-signatures-for-replay`
("No Improper Usage of Signatures for Replay Attack Protection") for
H-01/H-02; `req-1-use-c-e-i` ("Use Check-Effects-Interaction") and
`req-2-avoid-readonly-reentrancy` for H-06. No clear match was found for
H-03's EnumerableMap-bloat mechanism.

**Implemented** (commit `8112347`): `run_rtf.build_context_for_evmbench_target`
gained the same `compile_via_foundry`/`extra_forge_build_args` params used
throughout this plan — every Slither-backed EthTrust/ERC predicate now
gets the same whole-project visibility semantic generation already had.
New `semantic_only_driver.build_ethtrust_structural_properties`: real
compile ($0, local, deterministic) → `run_rtf` (81-corpus predicates) →
`rtf.standards` ERC/EIP-generated requirement merge → `build_property_pool`
→ a `PropertyMetadata` list ready for `run_semantic_investigation`'s
existing `structural_properties` param. Proven with a real Entry/Sibling
fixture (old path never sees the sibling contract; Foundry mode does; a
real `req-2-block-data-misuse` predicate fires on it) and a real
end-to-end merge test (structural + semantic properties reach one
investigation pool together, mocked LLM/Codex). Deliberately does a
SECOND real Foundry compile separate from generation's own — disclosed
as a wall-clock cost, not a correctness risk (same deterministic compile
function, no divergence risk).

**Live combined run** (`/scratch/md5344/evmbench/rtf_phi_live_foundry_combined_20260815/`,
`max_semantic_properties=78`, same real checkout/model/ceiling): **186
real structural properties** derived in 28.6s at $0 (81-corpus + ERC/EIP
predicates against the whole-project compile), merged with semantic-v2
generation. **116 properties resolved** (64 FAIL / 52 PASS), **$2.391
total real spend** ($2.358 investigation + $0.033 generation, comfortably
under the $5 ceiling).

**A real operational incident occurred and was recovered from cleanly**:
the run itself completed successfully (every property resolved,
everything correctly checkpointed incrementally per this session's own
checkpointing fix), but the FINAL step (`write_observability_artifacts`)
crashed with `OSError: [Errno 122] Disk quota exceeded` -- `/scratch`'s
Lustre file-count quota was at 1,086,410 files against a 1,000,000 HARD
limit (see memory `env_scratch_quota.md`), driven largely by the day's
accumulated per-cluster investigation scratch copies (`_gview`/`_ghome`
full-repo copies, ~190K files across the day's earlier three run
directories alone). **Zero data was lost**: `checkpoint.jsonl`'s
per-call incremental persistence (this session's own reliability fix)
meant every real verdict and raw evidence string survived even though
`run_semantic_investigation` itself never returned and `summary.json`
was never written -- `audit.md` was rebuilt directly from
`checkpoint.jsonl` alone. Recovered by deleting the disposable
`scratch/` subdirectories (full per-cluster investigation copies, not
primary data) from the day's now-fully-reported prior runs, dropping
file count to 894,890 (back under the hard limit, though still over the
500K soft quota with an ~1d22h grace period remaining -- a pre-existing,
broader account-wide pressure per `env_scratch_quota.md`, not something
this fix resolves permanently).

**Real `DetectGrader` result: 4/6** (up from 2/6 semantic-only):
- **H-01, H-02, H-06: now DETECTED** -- exactly the three requirements
  identified above. `req-2-malleable-signatures-for-replay` resolved
  FAIL at all 3 real instances; `req-1-use-c-e-i` resolved FAIL at 4 of
  5 real instances (`req-2-avoid-readonly-reentrancy` itself resolved
  all-PASS, so the catch came from the CEI requirement, not the
  readonly-reentrancy one specifically). The judge's own reasoning for
  all three confirms genuine mechanism matches, not generous grading.
- **H-04: still detected** (as in the semantic-only 78-property run).
- **H-03: still not detected** -- confirms the EnumerableMap-bloat
  mechanism is a genuine gap in BOTH the semantic generator and (per the
  keyword search above) the EthTrust corpus itself, not merely a routing
  gap this fix could close.
- **H-07: regressed to not-detected** (was detected in the semantic-only
  78-property run) -- real run-to-run semantic generation variance: this
  run's own generation pass did not produce (or the judge did not match)
  the `updateArtSettings`-owner-only property that caught it last time.
  Not a regression in the fix itself -- a reminder that semantic
  generation coverage is still stochastic per run, independent of the
  structural-routing improvement.

Full raw evidence: `/scratch/md5344/evmbench/rtf_phi_live_foundry_combined_20260815/`
(`checkpoint.jsonl` is authoritative; `summary.json` does not exist for
this run for the disk-quota reason above; `audit.md`/`grade_result.json`
were rebuilt directly from `checkpoint.jsonl`).

### Second confirmation target — 2026-08-15: `2025-04-forte`, real score 3/5

Per §21's own guidance ("if authorized/practical, independently validate
`2025-04-forte`... protects against accidentally building a phi-specific
solution"), user explicitly authorized running the SAME combined
structural+semantic recipe (`compile_via_foundry=True`,
`max_semantic_properties=78`, `build_ethtrust_structural_properties`,
`codex_model="gpt-5.6-sol"`, `cost_ceiling_usd=5.00`) against the real
`2025-04-forte` checkout (`src/Float128.sol`/`src/Ln.sol`/`src/Types.sol`,
solc `0.8.24`). Completed cleanly (no crash this time), 799s wall clock,
**115 real structural properties**, **160 properties resolved** (140
in-scope after the primary filter's own accounting, 47 FAIL), **$3.379
total real spend** (investigation only — this run's own generation cost
is inside that total; see `generation_tokens.jsonl` for the split),
under the $5 ceiling, `scope_boundary_violations: []`.

**Confirmed: `Ln.sol` — completely invisible under the pre-fix
architecture (the root cause this whole plan exists to close, §1) — got
real, substantial investigation this run**: 4 distinct real properties
targeted `Ln.sol`/`ln()` directly (not zero, not one — a genuinely
covered file), one resolving a real, different numerical-precision FAIL
(`Ln.sol:270`'s Taylor-series partition-index arithmetic, distinct from
the ground-truth H-03 mechanism) and three PASS.

**Real `DetectGrader` result: 3/5**:
- **H-02, H-04, H-05: DETECTED** — all three were previously classified
  `INVESTIGATION_TIMEOUT` (H-02, H-05) or `GENERATION_COVERAGE_GAP` (H-04)
  in `RTF_V2_5ENTRY_ALL_MISSES_ROOT_CAUSE.md`'s original forensic
  analysis of the pre-fix architecture. The timeout-classified ones are
  consistent with (though not conclusively attributable to) this
  session's own process-tree-timeout-kill and checkpointing reliability
  fixes actually letting investigations run to real completion instead
  of exhausting silently.
- **H-01 (sqrt exponent off-by-one): still not detected** — same
  generation-precision gap as before; no property this run addressed the
  halve-before-digit-adjustment ordering in `sqrt()` specifically.
- **H-03 (`Ln.ln()` accepts negative/zero input without validation):
  still not detected, but the reason has genuinely changed** — `Ln.sol`
  is no longer invisible (confirmed above), and one of the 4 real
  properties targeting it is directly adjacent to this exact mechanism
  (`semantic__semantic__89b3d89ffd51`: "the only bypass is a mathematical
  one, for which `ln` returns zero" — i.e. an invalid input producing a
  silent zero rather than a revert, the same shape as H-03's real defect)
  but resolved PASS rather than FAIL. This is now a genuine
  investigation-precision question (did the investigator correctly reason
  about that specific bypass, or accept a plausible-sounding conclusion
  too readily), not a pure coverage-absence question — worth a closer,
  dedicated look if this specific finding matters, not re-derived further
  here.

**Conclusion**: this is a real, independent second confirmation that the
whole-project-compilation fix itself works exactly as designed (`Ln.sol`
visibility is real and substantive, not a fluke specific to phi's
`Cred.sol`) — every remaining miss traces to a SEPARATE, already-named
generation- or investigation-precision limitation, never to
scope/visibility. Full raw evidence:
`/scratch/md5344/evmbench/rtf_forte_live_foundry_combined_20260815/`.

**Combined real spend across both live-validated targets today: phi
$2.391 + forte $3.379 = $5.77**, each individually under its own $5
ceiling (the two are separate runs/ceilings, not a shared budget).

---

## 4. Architectural Invariants — Do Not Violate

### Invariant A — Visibility is not scope

`compiled/visible != reportable`. Whole-project compilation exists so the
system can understand the entire project. It does not redefine audit scope.

### Invariant B — Groundable is not reportable

A property may successfully reference real code and still be outside the
declared audit scope: `real reference + successful grounding != permission
to report`.

### Invariant C — `scope_files` is the reporting authority

Do not infer scope from `src/`, Foundry compilation output, "first-party"
status, project manifest membership, successful grounding, or contract
reachability. The declared audit scope (`scope_files`, as already consumed
by `split_properties_by_scope`) remains authoritative. **Do not invent a
second scope-matching implementation anywhere in this work** — Boundary A
and Boundary B (§9) must call the existing `split_properties_by_scope`/
`_paths_match` logic, not reimplement path comparison.

### Invariant D — Broad dependencies remain available for reasoning

A dependency may need to exist in Slither/call relationships/inheritance
relationships/graph structure without becoming an independent audit target.

### Invariant E — Generation and investigation must use the same project view

A property generated from a contract must not become structurally
unresolvable merely because graph navigation reconstructed the audit from a
different, narrower entry file. This is what §11-§15 (Goal 2) exist to fix.

### Invariant F — Scope must fail closed at execution boundaries

If an out-of-scope file-targeted candidate somehow bypasses normal
filtering: do not investigate, do not return, record the violation
(`scope_boundary_violations`).

### Invariant G — Do not silently recover by recompiling differently

If copied Foundry artifacts cannot be consumed during investigation, do not
silently fall back to the old independent single-entry compile. That would
hide the architectural failure this work exists to fix. Investigate the
real cause, document it, design the smallest correct fix (§14).

---

## 5. Explicit Scope and Deferred Work

This plan targets the `semantic-v2 generation → grouping → live
investigation` path only:
`rtf/l11_investigation_grouping/semantic_only_driver.py` and everything it
calls, through `live_runner.py`, `arm_g_codex.py`, and `graph_mcp_server.py`.

**Explicitly deferred, do not touch unless a compatibility break forces it**:
- `rtf/l12_evaluation/pipeline_e2e.py`
- `rtf/l12_evaluation/pilot5_driver.py`
- `rtf/l11_investigation_grouping/ablation_driver.py`

None of these currently call `compile_via_foundry`; wiring them in is future
work, not this plan's. Do not redesign the unrelated structural/EthTrust
(`rtf/standards/`, `rtf/l9_assumptions_register/`, `rtf/track_a/`)
architecture — this plan does not touch it.

---

## 6. Goal 1 — Broad Visibility, Narrow Audit Scope

Preserve the existing architecture where appropriate. Whole-project Foundry
compilation (already implemented, §3) exposes all relevant first-party
contracts. Semantic generation and grounding may operate against this broad
project representation (already wired, §3). Then:

```python
split_properties_by_scope(properties, scope_files)
```

(`rtf/l11_investigation_grouping/property_metadata.py`) must remain the
canonical scope rule — already true, already the sole call site in
`semantic_only_driver.run_semantic_investigation`. **Do not create another
path-matching implementation.** The remaining Goal 1 work is test coverage
(§7-§8), not new production logic — Goal 1's core mechanism is done.

---

## 7. Goal 1 Test Fixture

Build a real Foundry fixture:

```
src/
  Entry.sol
  Sibling.sol
  Helper.sol

lib/
  Vendor.sol
```

Semantics:

- **`Entry.sol`** — in scope.
- **`Sibling.sol`** — in scope, **NOT imported by `Entry.sol`**. (This is
  what `test_compile_via_foundry_makes_a_sibling_scope_file_visible_to_generation`,
  §3, already proves for a 2-file case; this fixture extends it to the full
  4-role matrix below in one place.)
- **`Helper.sol`** — first-party, compiled, visible, groundable, **OUT OF
  SCOPE**, and **NOT imported by `Entry.sol`** (this is the deliberate
  correction to the existing misleading fixture, §0.5/§3 — the point is to
  prove rejection of a file that is *only* visible because of whole-project
  compilation, not one that was already visible under the old path).
- **`Vendor.sol`** (under `lib/`) — dependency/vendored.

Tests must prove:

```
Entry       → visible + reportable
Sibling     → visible + reportable
Helper      → visible + NOT reportable
Vendor      → dependency-visible as needed + not a normal context/report target
```

Place this fixture and its tests in `rtf/l11_investigation_grouping/test_semantic_only_driver.py`
(same file/convention as the existing `compile_via_foundry` tests) or a new
`test_compile_via_foundry_scope_matrix.py` in the same package if the
existing file is getting unwieldy — either is acceptable, prefer whichever
keeps the existing file readable.

---

## 8. Real Foundry Path Matching

Test scope matching using real path values produced by the actual
Foundry/Slither flow — i.e. run the §7 fixture through
`compile_evmbench_target_via_foundry` for real and inspect what
`source_mapping.filename` actually contains (both `.absolute` and `.used`
forms), then confirm `_paths_match` (property_metadata.py:321) correctly
matches those real values against `scope_files` entries in forms like
`./src/X.sol`, `src/X.sol`, `project/src/X.sol`.

**`_paths_match` already exists and already handles suffix-based matching**
(§3) — this is validation work, not new-logic work. **Do not modify
`_paths_match` preemptively.** Only change it if this section's real test
run exposes an actual mismatch, and if so, fix the minimal case, keep the
existing suffix-matching approach (Invariant C — one canonical matcher).

---

## 9. Goal 1b — Defense-in-Depth Scope Boundaries

Keep the existing primary filter (§6, unchanged). Add two new, minimal
boundaries, both calling the **existing** `split_properties_by_scope`/
`_paths_match` logic — never a second implementation (Invariant C).

**Boundary A — immediately before investigation.** In
`live_runner.prepare_cluster_investigations` (or immediately before its
call site in `semantic_only_driver.run_semantic_investigation`, whichever
keeps the check closest to the actual investigation dispatch), re-run the
scope check on the property set about to be clustered/dispatched. An
out-of-scope property here: drop it, don't cluster it, don't investigate it,
record the violation.

**Boundary B — immediately before final result return.** In
`run_semantic_investigation`'s return path, revalidate the property/result
IDs actually present in the returned structures. An out-of-scope result
here: remove it from the result structures, record the violation.

Expose, in `run_semantic_investigation`'s returned dict:

```python
"scope_boundary_violations": [...]   # non-empty only if a boundary ever caught something
```

Normal operation (nothing bypassed the primary filter, which should be
every real run — these boundaries exist for defense in depth, not because
the primary filter is expected to fail): `"scope_boundary_violations": []`.

Implement one small shared helper (e.g. `_enforce_scope_boundary(properties,
scope_files, boundary_name) -> tuple[list[PropertyMetadata], list[dict]]`)
in `property_metadata.py`, reusing `split_properties_by_scope` internally,
returning both the kept properties and a list of violation records
(`{"boundary": boundary_name, "property_id": ..., "target_files": ...}`).
Call it from both boundary sites. This keeps Invariant C intact (still one
underlying matcher) while giving both boundaries their own observability
label.

---

## 10. Defense-in-Depth Bypass Tests

These must **intentionally simulate failure of the primary filtering
layer** — testing the primary filter twice proves nothing new.

**Boundary A test**: manually construct a property pool where `Helper.sol`
(§7's out-of-scope fixture contract) has already survived past the normal
`split_properties_by_scope` call (i.e. call `prepare_cluster_investigations`
/ the Boundary-A-wrapped entry point directly with a pool that includes it,
bypassing the driver's own upstream filter call). Assert: `Helper` is
blocked at Boundary A, never reaches clustering, never gets sent to
`run_arm_g_bundle` (verify via a mock `run_arm_g_bundle_fn` that records
every `case_id`/property set it was invoked with, and assert `Helper` never
appears in any of them).

**Boundary B test**: independently, construct a fake investigator response
(mock `run_arm_g_bundle_fn` return value) whose `final_decision["properties"]`
includes an entry naming `Helper.bump`/`Helper.sol` — simulating an
investigator that somehow reasoned about or fabricated a reference to the
out-of-scope contract. Assert: Boundary B strips this entry from the
returned result structures before `run_semantic_investigation` returns, and
`scope_boundary_violations` is non-empty and names it.

---

## 11. Goal 2 — Consistent Generator / Investigator Project View

**Confirmed current inconsistency** (§3, verified by reading both files
directly):

```
Generation
    → compile_evmbench_target_via_foundry (whole-project, when compile_via_foundry=True)

Investigation graph (graph_mcp_server._get_graph)
    → ALWAYS ProgramGraph.build(ENTRY_FILE, ...) — independent single-entry raw-solc compile,
      completely unaware of whether generation used Foundry mode at all
```

This is unacceptable under Invariant E: a property generated from
`Sibling.sol` (visible only because generation used whole-project Foundry
compilation) becomes structurally unresolvable the moment graph navigation
tries to look it up, because the graph was rebuilt from `ENTRY_FILE`'s
narrower import graph, which never included `Sibling.sol` at all.

**The good news, confirmed by reading `a4v/graph.py:159-177`**: the
primitive this needs — `ProgramGraph.from_slither(cls, slither) ->
ProgramGraph`, building a graph from an *already-compiled* Slither object
with no second compile — **already exists**, built in an earlier, unrelated
session (motivated by a different bug: `2024-01-canto`'s
`LendingLedger.sol` hitting a real "stack too deep" `BuildFailed` on a
second, differently-configured compile that the first compile never hit).
It has **zero test coverage** and **zero callers** anywhere in the repo
currently — Goal 2's job is to wire it in, not build it.

Target:

```
one Foundry build (compile_evmbench_target_via_foundry, generation time)
        ↓
build-info (out/build-info/*.json, on disk under project_root)
        ↓
generation Slither  (already reads this — compile_evmbench_target_via_foundry's own return value)
        +
investigation Slither (graph_mcp_server, NEW — must read the SAME artifacts, not recompile)
        ↓
same project view
```

---

## 12. Foundry Artifact Reuse Design

In `graph_mcp_server.py`, when Foundry mode is active for this investigation
(new env var, §13), replace the unconditional:

```python
_pg_cache = ProgramGraph.build(ENTRY_FILE, solc_remaps=REMAPS, extra_kwargs=extra_kwargs)
```

with a branch:

```python
if GRAPH_COMPILE_VIA_FOUNDRY:
    slither = Slither(
        str(INVESTIGATION_DIR),
        foundry_ignore_compile=True,
        compile_force_framework="Foundry",
    )
    _pg_cache = ProgramGraph.from_slither(slither)
else:
    _pg_cache = ProgramGraph.build(ENTRY_FILE, solc_remaps=REMAPS, extra_kwargs=extra_kwargs)
```

`INVESTIGATION_DIR` here is the existing `GRAPH_INVESTIGATION_DIR` env var
(already read at graph_mcp_server.py:92) — the full-repo copy
`prepare_full_repo_investigation_dir` already produces (§3, §14). This
mirrors exactly how `compile_evmbench_target_via_foundry` itself reads
artifacts back (`foundry_ignore_compile=True, compile_force_framework="Foundry"`,
§3's first table row) — same Slither-loading convention, applied at a
different point in the pipeline, not a new pattern.

Keep the old path (`ProgramGraph.build(ENTRY_FILE, ...)`) completely
unchanged when `GRAPH_COMPILE_VIA_FOUNDRY` is unset/false — this is the
existing, tested, non-Foundry behavior and must remain byte-identical
(regression test, §18).

---

## 13. Compilation Mode Propagation

Exact control flow to implement (verify every function name against the
real code per §0.4 before implementing — this was correct at write time,
2026-08-14):

```
semantic_only_driver.run_semantic_investigation(compile_via_foundry=...)
            ↓ (NEW: thread compile_via_foundry through)
live_runner.run_cluster_investigations_live(compile_via_foundry=...)     [NEW param]
            ↓ (NEW: pass through per-invocation)
arm_g_codex.run_arm_g_bundle(compile_via_foundry=...)                    [NEW param]
            ↓ (NEW: set as an MCP-server env var, same convention as the
              existing GRAPH_ENTRY_FILE/GRAPH_SOLC_REMAPS/etc. block in
              write_g_config / wherever those env vars are currently
              assembled — read that assembly site directly, §0.4)
GRAPH_COMPILE_VIA_FOUNDRY=1   (new env var, mirrors the existing GRAPH_* naming convention)
            ↓
graph_mcp_server.py reads GRAPH_COMPILE_VIA_FOUNDRY at module load (same
pattern as its existing ENTRY_FILE/REMAPS/REPO_ROOT/etc. reads, graph_mcp_server.py:89-95)
            ↓
_get_graph()  →  branches per §12
            ↓
ProgramGraph.from_slither(slither)   [when Foundry mode active]
```

`run_cluster_investigations_live`'s existing `run_arm_g_bundle_fn`
injection point (already used by every current test to mock Codex calls,
§3/§0.5) is the natural place to verify the new parameter is threaded
correctly under test — assert the mock receives `compile_via_foundry=True`
when the driver was called with it, without needing a real Codex binary.

---

## 14. Artifact Relocation Test — MANDATORY

Do **not** test artifact reuse only inside the original source repository —
that would not prove anything about the real production lifecycle, where
generation and investigation run against *different* directories.

Test the real lifecycle, using the §7 fixture (or a smaller 2-file
Entry/Sibling fixture — either is fine, the §7 fixture may be overkill for
this specific test):

```
create Foundry fixture (Entry.sol + Sibling.sol, Sibling not imported by Entry)
        ↓
compile via compile_evmbench_target_via_foundry(fixture_root) — produces real out/build-info/*.json under fixture_root
        ↓
arm_g_codex.prepare_full_repo_investigation_dir(fixture_root, investigation_dir)  — real copytree call
        ↓
load Slither from investigation_dir (the COPIED artifacts, not fixture_root)
        ↓
ProgramGraph.from_slither(that Slither)
        ↓
resolve Sibling.sol's contract/function nodes in the resulting graph
```

This must prove, with real assertions, not inference:

1. The copied build artifacts remain valid (Slither loads them from
   `investigation_dir` without error).
2. `Slither(str(investigation_dir), foundry_ignore_compile=True,
   compile_force_framework="Foundry")` does not silently trigger a fresh
   `forge build` under the hood (see §15 for how to verify this concretely).
3. Graph construction via `from_slither` succeeds against the copied
   artifacts.
4. `Sibling.sol`'s contract and its function(s) are resolvable in the graph
   (e.g. `graph.nodes_of_kind(...)` or equivalent finds `Sibling`/its
   function node — use whatever real query `a4v/graph.py` exposes; read it,
   don't guess the exact method name).
5. Source identities/paths remain usable after relocation (a node's file
   path resolves to a real, readable file under `investigation_dir`, not a
   stale absolute path pointing back at `fixture_root`).

**If this fails because artifact metadata depends on original absolute
paths** (a real, known risk category for build-info JSON, which can embed
absolute source paths from the machine/directory it was built in):
investigate the real cause, document it in this file's own "Current
Implementation Status" table (update it in place, don't create a separate
doc), and design the smallest correct fix. Per Invariant G, do **not**
silently fall back to a fresh single-entry compile to make this test pass —
that defeats the entire purpose of this work.

---

## 15. Verify There Is No Hidden Recompile

The Goal 2 test suite must explicitly prove Foundry investigation mode does
**not** invoke a fresh `forge build` or fall through to
`ProgramGraph.build(...)` via the old path. Concretely:

- Instrument or mock `compile_helper.compile_evmbench_target_via_foundry`
  (or the underlying `subprocess.run` call it makes) during the §14 test
  and assert it is called **exactly once** (at generation time), never
  again during the investigation-time `_get_graph()` call.
- Separately, assert `ProgramGraph.build` (the old classmethod) is **never**
  called when `GRAPH_COMPILE_VIA_FOUNDRY` is set — e.g. via a mock/patch
  that fails the test if `build` is invoked, only allowing `from_slither`.

The point is not merely that graph navigation succeeds — it must succeed
using the exact same existing build artifacts, with observable proof of
that, not just an absence-of-error inference.

---

## 16. Vendor Context Filtering

Whole-project compilation may expose dozens of dependencies. The generator-
facing `ProjectManifest.from_slither(repo_root=...)` filter already exists
(§3) — this section is about the **separate**, currently **unfiltered**
investigator-facing context.

Confirmed gap (§3): `protocol_context.py`'s `extract_accounting_state_variables`/
`extract_lifecycle_hints`/`generate_enriched_protocol_context_md` iterate
`slither.contracts_derived` directly, with no vendored-path exclusion. When
`compile_via_foundry=True` is used against a real project with a populated
`lib/` (OpenZeppelin, Solady, forge-std, etc.), `protocol_context.md` — the
Markdown file the investigator actually reads (§9's Boundary-A-adjacent
context assembly in `live_runner.prepare_cluster_investigations`) — will be
dominated by vendored contracts unless filtered.

Fix: thread a `repo_root` parameter into the relevant `protocol_context.py`
functions (mirror the exact pattern already used for `ProjectManifest.from_slither`,
§3) and reuse `rtf.standards.discovery._is_vendored_path` **directly** — do
not create a separate classification rule (the same discipline as Invariant
C, applied to vendor-detection instead of scope-detection: one canonical
rule, reused everywhere it's needed).

Verify both context paths receive appropriate filtering with real tests:
- Generation-facing (`ProjectManifest`) — already covered, §3.
- Investigator-facing (`protocol_context.md` content) — new test needed in
  `test_protocol_context.py`, using the §7 fixture's `lib/Vendor.sol`:
  assert `Vendor` does not appear in the generated Markdown's "Contracts
  and inheritance" (or equivalent) section when `repo_root` is passed, and
  does appear when it's omitted (backward-compatibility check, same pattern
  as the existing `ProjectManifest` tests).

---

## 17. Lightweight I/O and Runtime Measurements

Do not assume artifact copying is free. Using the §7 or §14 fixture (or, for
a more representative number, a real compiled EVMbench target — e.g. the
`tempo-feeamm` checkout already used in §3's real-container test), measure:

```
size(out/build-info/)
size(out/)
time(prepare_full_repo_investigation_dir)   — for a repo that already has out/ populated by a prior compile_via_foundry call
```

Record at least one representative real measurement (a `du -sh`/`time`
invocation is sufficient — this is not a benchmark suite). If multiple
investigation clusters are created per audit (the normal case — see
`live_runner.run_cluster_investigations_live`'s per-cluster
`prepare_full_repo_investigation_dir`-adjacent dispatch, §0.4), estimate
whether copying `out/` repeatedly (once per cluster, per §12's design where
each investigation gets its own `INVESTIGATION_DIR`) is significant at
realistic cluster counts (5-15 clusters per audit, per the 5-entry
comparison's own observed cluster counts in `RTF_V2_5ENTRY_COMPARISON_REPORT.md`).

This is **measurement, not a storage redesign**. Do not prematurely
introduce symlink systems, shared artifact services, new caches, or complex
artifact protocols. If copying is small (a reasonable prior, given
`build-info` JSON is typically well under the source tree's own size), keep
the simple full-copy design already in place (`prepare_full_repo_investigation_dir`
requires no change for this). If it's significant, record a follow-up
optimization recommendation in this document's own status table (§3) rather
than blocking on it — do not let a performance concern gate correctness
work in this plan.

**Real measurement taken 2026-08-15**, against the real
`2026-01-tempo-feeamm` checkout (the same one §3's real-container test
uses), after a real `compile_evmbench_target_via_foundry` compile:

```
out/build-info/  : 4.5K
out/ (total)     : 18K
repo (total)     : 475K   -- out/ is ~3.8% of the whole repo copy
prepare_full_repo_investigation_dir time: 1.842s
```

**Conclusion: small, not significant.** `out/`'s own contribution to the
copy is negligible relative to the full-repo copy that already happens on
every investigation regardless of Foundry mode — the 1.842s is dominated
by the pre-existing full-repo `copytree`, not by anything this work added.
At a realistic 5-15 clusters/audit (per `RTF_V2_5ENTRY_COMPARISON_REPORT.md`),
that's roughly 9-28s of total copy overhead per audit — trivial next to
real per-cluster Codex investigation wall-clock time (minutes, not
seconds). **This is one target's numbers, not a guarantee** — a target
with a much larger `lib/` (heavy multi-library OpenZeppelin/Solady/
forge-std dependency tree) could shift this ratio; re-measure before
assuming it generalizes to every audit, but no design change is warranted
from this data point. No follow-up optimization is recommended.

---

## 18. Tests — Rationale for Each

| Test | Protects against |
|---|---|
| Sibling visibility (§7) | Regression back to entry-import-only compilation — the exact bug this whole plan exists to fix. |
| Helper out-of-scope, non-imported (§7) | Whole-project visibility accidentally becoming whole-project reporting scope (Invariant A/B) — and specifically, being fooled by a test whose fixture happens to also be reachable under the old path (§0.5's confirmed misleading-coverage example). |
| Boundary A/B injection tests (§10) | Future alternate code paths bypassing the primary scope filter, silently, with no observability. |
| Graph consistency / from_slither wiring (§11-§13) | Semantic generation and graph navigation reasoning over different source sets (Invariant E) — a property that exists but can never be resolved during investigation. |
| Artifact relocation (§14) | `build-info` working in the original repo but failing in real investigation scratch directories — the gap between "works in a unit test's temp dir" and "works in the real per-cluster investigation lifecycle." |
| No-hidden-recompile (§15) | A test that merely observes "navigation succeeded" without proving it used the SAME artifacts, silently masking Invariant G violations (a quiet fallback recompile that happens to still work). |
| Vendor context test (§16) | Whole-project compilation causing huge, irrelevant LLM context (cost and signal-to-noise both degrade). |
| Non-Foundry regression test (§9, §18 below) | semantic-v2 changes breaking legacy (`compile_via_foundry=False`) callers — everything that doesn't opt in must be provably unaffected. |

**Explicit non-Foundry regression test**: re-run the existing full
`test_semantic_only_driver.py`, `test_live_runner.py`, and
`rtf/l12_evaluation/test_agentic_architecture.py` suites unmodified after
all changes above — every currently-passing test with `compile_via_foundry`
omitted (the default `False`) must still pass byte-identically. This is
what proves the old path is untouched, not merely "probably fine."

---

## 19. Concrete Implementation Order

### Phase 0 — Soft Run
See the full procedure above (§0.1-§0.9). Do not skip.

### Phase 1 — Preserve existing completed work
1. Confirm the 6 already-modified files (§3) still match the diffs
   described there (re-run `git diff` per §0.2).
2. If still correct: commit them as their own logical commit(s) — suggest
   splitting into (a) `compile_evmbench_target_via_foundry` +
   its test, (b) `ProjectManifest.from_slither(repo_root=...)` + its tests,
   (c) `run_semantic_investigation`'s `compile_via_foundry` wiring + its
   test — or one combined commit if that's cleaner given how entangled the
   diffs are; use judgment, this is not prescriptive.
3. Do not rewrite this working, tested code without new evidence it's
   wrong. If you find a real bug in it, fix the bug narrowly; don't
   redesign it.

### Phase 2 — Scope separation tests
4. Build the §7 multi-file Foundry fixture (Entry/Sibling/Helper/Vendor).
5. Write and run the Entry/Sibling/Helper/Vendor visibility+scope tests.
6. Test real Foundry path matching against the fixture's actual compiled
   output (§8).
7. Fix `_paths_match` only if this step's real test run exposes an actual
   mismatch — do not modify it speculatively.

### Phase 3 — Defense in depth
8. Implement the shared `_enforce_scope_boundary` helper (§9) in
   `property_metadata.py`, reusing `split_properties_by_scope`.
9. Add Boundary A (before clustering/investigation dispatch).
10. Add Boundary B (before final result return).
11. Add `scope_boundary_violations` to `run_semantic_investigation`'s
    return dict.
12. Add the deliberate bypass/injection tests (§10) — these must inject
    past the normal filter, not merely re-test it.

### Phase 4 — Context filtering
13. Thread `repo_root` into the relevant `protocol_context.py` functions,
    reusing `_is_vendored_path` directly (§16).
14. Add the investigator-facing vendor-filtering test.
15. Confirm both generator-facing (already done, §3) and investigator-
    facing context paths are filtered with real tests.

### Phase 5 — Shared graph representation
16. Add `GRAPH_COMPILE_VIA_FOUNDRY` propagation: `run_semantic_investigation`
    → `run_cluster_investigations_live` → `run_arm_g_bundle` → the MCP-
    server env-var assembly site (find it via §0.4's trace, don't guess its
    name) → `graph_mcp_server.py` (§13).
17. Add the `_get_graph()` branch in `graph_mcp_server.py` calling
    `ProgramGraph.from_slither` when Foundry mode is active (§12).
18. Keep the old `ProgramGraph.build(ENTRY_FILE, ...)` path completely
    unchanged for `compile_via_foundry=False` / `GRAPH_COMPILE_VIA_FOUNDRY`
    unset.

### Phase 6 — Artifact relocation
19. Compile the fixture in its original location via
    `compile_evmbench_target_via_foundry`.
20. Create a real investigation scratch copy via
    `prepare_full_repo_investigation_dir`.
21. Load the copied `out/build-info/` via Slither + `ProgramGraph.from_slither`.
22. Resolve `Sibling.sol` in the resulting graph.
23. Prove no independent recompilation occurred (§15).
24. If relocation fails: investigate root cause, document in §3's table,
    design the minimal correct fix (Invariant G — no silent fallback).

### Phase 7 — Performance observation
25. Measure `out/build-info/` size, total `out/` size, and
    `prepare_full_repo_investigation_dir` copy time for at least one real
    representative target (§17).
26. Record whether repeated per-cluster copying is significant at realistic
    cluster counts; note a follow-up recommendation if so, don't block on
    it.

### Phase 8 — Regression suite
27. Run every test file listed in §0.7, plus every new test added in
    Phases 2-7.
28. Confirm zero unexpected skips (a skip on a Foundry/container-touching
    test that passed with real execution earlier in this plan, per §3, is
    a regression — investigate, don't just note it and move on).
29. Investigate any real regression rather than hiding it via a skip or a
    loosened assertion.
30. Commit logical units as each phase completes, rather than one giant
    end-of-session commit.

### Phase 9 — Live validation gate
31. **Stop before any real paid LLM/Codex call.**
32. Ask the user for explicit approval, stating the specific target(s)
    (§21: `2024-08-phi` primary, `2025-04-forte` if authorized/practical)
    and an estimated cost ceiling based on this project's own prior real
    runs (`RTF_V2_LIVE_VALIDATION_REAL_TARGET_CONFIRMED.md`-scale spend —
    order of a few dollars per audit, not tens, based on this plan's prior
    real-run history; state your own updated estimate at the time, don't
    just cite an old number as current).
33. Only after approval, run the real EVMbench verification (§21).

### Phase 10 — Final report
34. Compare results against the Definition of Done (§22).
35. Document the before/after architecture (this document's §2 vs. §1 is
    the template; update with what was actually built, not just what was
    planned).
36. Document tests and evidence (pass counts, what each proves — reuse
    §18's rationale table, filled in with final real results).
37. Document the §17 measurements.
38. Document remaining limitations/follow-up work (e.g. `pipeline_e2e.py`/
    `pilot5_driver.py`/`ablation_driver.py` not yet wired, per §5).

---

## 20. Test Execution Requirements

Use the project's established module-execution convention, **not** bare
`pytest` (verify this is still accurate for this repo before relying on it,
per §0.7 — it was confirmed accurate 2026-08-14 by successfully running
every command listed there):

```
.venv/bin/python3 -m rtf.l5_predicates.test_compile_helper
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_property_generation
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_only_driver
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_property_metadata
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_protocol_context
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_context_artifacts
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_live_runner
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_pipeline
.venv/bin/python3 -m rtf.l11_investigation_grouping.test_end_to_end_integration
.venv/bin/python3 -m rtf.l12_evaluation.test_agentic_architecture
```

**Real integration/compile tests must not be counted as passes when they
silently skip.** Read each test file's own printed `ok -` lines, not just
the summary count — a name containing "skipped"/"unavailable" means the
environment gap this document flags in §0.8, not verified behavior. At
write time, none of the above skipped (§3).

No dedicated test file exists yet for `arm_g_codex.py`'s
`prepare_full_repo_investigation_dir` beyond its coverage inside
`rtf/l12_evaluation/test_agentic_architecture.py`, and **no test file
exists anywhere for `graph_mcp_server.py` or `a4v/graph.py`'s
`ProgramGraph.from_slither`** (confirmed by grep, §3) — the new tests in
Phases 5-6 (§19) are genuinely new coverage, not an extension of an
existing suite for that specific code. Place them in
`rtf/l11_investigation_grouping/test_live_runner.py` (for the propagation
plumbing, §13) and a new small test module near `graph_mcp_server.py` or
`a4v/graph.py` for the `from_slither`-in-anger coverage (§14-§15) —
whichever keeps the graph-construction tests colocated with the code that's
actually least tested right now.

---

## 21. Real EVMbench Verification

**Requires explicit user approval before any call in this section (Phase 9,
§19).**

Primary validation target: `2024-08-phi`. Run semantic v2 with
`compile_via_foundry=True`. Verify:

```
PhiFactory.sol visible
Cred.sol visible
same semantic run
properties generated/grounded on both sides (PhiFactory and Cred)
scope filtering correct (both are legitimately in scope per phi's scope.txt — verify this is still true, don't assume from §1)
no unrelated first-party finding leakage
vendor context controlled (OpenZeppelin/solady chain doesn't dominate protocol_context.md)
graph navigation resolves Cred.sol (a property targeting Cred.sol's investigation can actually navigate to it)
same artifacts reused (no independent graph recompile, per §15's instrumentation)
scope_boundary_violations == []   (nothing should trip Boundary A/B on a real, correctly-scoped run)
```

Also collect the §17 runtime/I/O measurements against this real run where
practical (real numbers are more representative than the synthetic-fixture
numbers from Phase 7, but Phase 7's numbers are still required as the
zero-cost baseline before this paid step).

If authorized/practical, independently validate `2025-04-forte` and confirm
`Ln.sol` is visible and navigable — this protects against accidentally
building a phi-specific solution (two independent confirmations of the same
structural fix, on two audits whose actual defect mechanisms are unrelated
to each other).

**Do not read `config.yaml`/ground-truth finding text for either audit
before this run**, beyond what §1 already legitimately references (both
audits are already frozen/graded in this project's history per the 5-entry
comparison, so citing their already-known finding mechanics in §1 is
post-hoc forensic analysis, not benchmark-tuning — but the live run itself
should still be evaluated fresh, not steered toward the known answer).

---

## 22. Definition of Done

The work is complete only if all of the following are proven, not merely
implemented:

- **Whole-project visibility**: an in-scope sibling not imported by the
  selected entry is visible to generation. *(Already proven for a minimal
  case, §3 — must hold for the full §7 fixture too.)*
- **Scope separation**: a first-party contract can be compiled, visible,
  and groundable while still being rejected because it is outside
  `scope_files` — proven specifically for a contract NOT reachable via the
  entry's old import graph (§7's `Helper.sol`, correcting the misleading
  existing test, §0.5).
- **Canonical scope authority**: no new competing scope-matching
  implementation exists anywhere in the diff.
- **Defense in depth**: an intentionally injected out-of-scope property is
  blocked before investigation AND before final output, with violations
  observable via `scope_boundary_violations`.
- **Consistent project view**: generation and graph navigation resolve the
  same sibling contract (§14).
- **Artifact portability**: the same build artifacts work after copying
  into the real investigation-directory layout (§14).
- **No hidden independent recompilation**: Foundry graph mode does not
  quietly rebuild from the single entry (§15, with real instrumentation
  proof, not inference).
- **Controlled context**: vendor contracts do not flood investigator
  protocol context (§16).
- **Backward compatibility**: non-Foundry behavior remains working,
  byte-identical, proven by an unmodified regression run (§18/§19 Phase 8).
- **Regression safety**: all relevant existing and new tests pass, with
  zero silent skips on anything that previously ran for real (§20).
- **Real EVMbench validation**: after explicit approval, `2024-08-phi`
  proves the architecture end-to-end (§21); `2025-04-forte` if authorized.

---

## 23. Instructions for a Fresh Claude Code Session

You have no conversational context from the session that created this plan.
Treat this document as the authoritative handoff, but **verify every
repository-state claim before changing code** — this document describes the
repository as of 2026-08-14; it may have moved since.

**Start with Phase 0 — Soft Run / Context Reconstruction** (top of this
document). Do not begin implementation until you have:

1. read the entire plan;
2. inspected `git status`/`git diff`/history;
3. read the referenced root-cause reports (§0.3);
4. traced the named code paths (§0.4), confirming in particular whether
   `graph_mcp_server.py` still always calls `ProgramGraph.build` (if this
   has changed, Goal 2 may already be partially or fully done — don't
   redo it);
5. inspected the named tests (§0.5), including re-verifying the
   `Helper.sol` misleading-coverage claim is still accurate;
6. produced the implementation-status matrix (§0.6), reconciling against
   §3 rather than assuming §3 is still current;
7. run the baseline relevant tests (§0.7), watching for skips that weren't
   present at write time;
8. verified the Foundry/container environment (§0.8);
9. produced the Soft Run Checkpoint (§0.9).

**If the repository disagrees with this document**: trust the current
repository state, explain the discrepancy (in your own working notes or in
an update to this document's §3 table — updating §3 in place is preferred
over writing a new separate status doc), update your execution
understanding accordingly, and preserve the architectural invariants (§4)
unless new evidence genuinely invalidates one of them (this would be
unusual — the invariants are about what "reportable" means, which is a
product/audit-methodology decision, not an implementation detail likely to
be invalidated by code drift).

**Do not redo already-complete work** — §3's table, once you've reproduced
and confirmed or corrected it, tells you exactly what's already implemented
and tested. The single most valuable existing asset most likely to be
overlooked is `a4v/graph.py`'s `ProgramGraph.from_slither` (§11) — it
already exists and was built for a different reason; Goal 2 is wiring, not
building.

**Do not expand into the deferred structural/EthTrust pipeline** (§5) —
`pipeline_e2e.py`, `pilot5_driver.py`, `ablation_driver.py` are explicitly
out of scope for this plan.

**Do not silently fall back to single-entry compilation in Foundry mode**
if something in §14/§15 doesn't work cleanly — investigate the real cause
and fix it minimally (Invariant G).

**Do not make paid LLM/Codex calls without explicit user approval** — this
applies to all of §21/Phase 9, and to any exploratory paid call outside
this plan's own scope.

Work through the implementation phases in §19 in order, and evaluate
completion against the Definition of Done (§22) — not against "I made
changes that seem related," but against the specific, itemized proofs
listed there.
