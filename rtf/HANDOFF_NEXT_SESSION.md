# RTF + EVMbench: Handoff for a New Session

Written at the end of a session that built the RTF-to-Codex escalation
pipeline glue and ran a 5-audit end-to-end pilot partway through. Read
this first, then `rtf/PROJECT_SUMMARY.md` for full project history, then
`rtf/l9_assumptions_register/REGISTER.jsonl` for every logged deviation
(AR-001 through AR-026 as of this handoff).

## 1. What RTF is

RTF (Requirement Translation Framework) is a standards-driven (EthTrust)
replacement for the older MGPR system, on branch `worktree-mgpr-router2`
under `agent4vul/rtf/`. **RTF is evaluated against EVMbench, never
*designed* from it** — this is the single most important, repeatedly-
enforced rule in this project. No benchmark-specific predicates, no
hardcoded symbols/functions from EVMbench findings, no tuning after
seeing grading results (a permitted-reason list + `framework_version`
bump is required for any post-evaluation change).

Full architecture: 13 layers, L0 (spec ingestion) through L12 (evaluation
harness). Design doc + full revision history:
`/scratch/md5344/.claude/plans/ou-are-a-critical-purring-eich.md`. Current
verified state: **81 EthTrust requirements** (22 S / 24 M / 24 Q / 11 GP),
superseding an earlier provisional ~52 estimate — see
`standards/ethtrust/metadata.json`.

## 2. How to run the REAL, wired RTF pipeline end-to-end

Before this session, the deterministic pipeline (`run_rtf.py`) and the
graph-gated Codex escalation harness (built across several earlier
sessions) existed but were **completely disconnected** — confirmed via
repo-wide grep. This session built the missing glue (commit `03bc7ac`)
and it is now real, tested, wired code:

```python
from rtf.l12_evaluation.pipeline_e2e import run_pipeline_e2e
from rtf.l8_llm_judgment_layer.judgment_layer import LLMJudgmentLayer
from a4v.llm import ChatClient          # <-- MUST use this, see SS4 gotcha #1

chat_client = ChatClient(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY_FILE.read_text().strip(),
    model="openai/gpt-5.1-codex-max",
    cache_dir=Path(".../l8_cache"),
    token_log_path=Path(".../l8_cache/tokens.jsonl"),
)
judgment_layer = LLMJudgmentLayer(chat_client=chat_client, model_version="openai/gpt-5.1-codex-max")

artifacts = run_pipeline_e2e(
    audit_id="...", entry_sol_file=Path("..."), project_root=Path("..."),
    solc_version="0.8.20", judgment_layer=judgment_layer,
    codex_bin=Path(".../codex"), python_bin=Path(".../.venv/bin/python3"),
    mcp_server_script=Path("rtf/l8_llm_judgment_layer/bundle_agent_experiment/graph_mcp_server.py"),
    api_key=API_KEY, codex_model="openai/gpt-5.1-codex-max",
    solc_path_dir="...", scratch_root=Path("..."),
    escalation_enabled=True, codex_timeout_s=900, cost_ceiling_usd=4.0,
)
```

Pipeline stages this chains together, all real code, all under
`rtf/l12_evaluation/` unless noted:
1. `run_rtf.py` — deterministic predicate evidence collection
2. `judge_with_l8.py` — bounded LLM judgment (always runs first)
3. `escalation.py` — **frozen rule**: escalate to Codex iff the bounded
   judgment resolves to `INSUFFICIENT_EVIDENCE`/`INCONCLUSIVE`, or
   confidence is `LOW`. Reuses only signals L8 already produces — no new
   relevance classifier.
4. `rtf/l8_llm_judgment_layer/graph_navigation.py` (`resolve_seed_node`) —
   candidate location → `a4v.graph.ProgramGraph` node, raises explicitly
   on zero or >1 match (never guesses on overloads)
5. `codex_bridge.py` — builds the 5 Arm-G prompt inputs, reusing the
   *same* L2 context-bundle renderer L8's own prompt uses
   (`judgment_layer.render_context_bundle_text`) and maps `ArmGResult` →
   `ConformanceState`
6. `rtf/l8_llm_judgment_layer/bundle_agent_experiment/arm_g_codex.py`
   (`run_arm_g_bundle`) — the actual graph-gated Codex investigation
   (MCP tools `show_candidate`/`investigate`/`read_source`; relations
   `CALLERS`/`CALLEES`/`EXTERNAL_TARGETS`/`INTERFACES`/`MODIFIERS`/
   `STATE_READS`/`STATE_WRITES`/`STATE_WRITES_TRANSITIVE`/
   `WRITE_AFTER_EXTERNAL_CALL`/`WRITERS_OF_STATE`; no fixed hop-depth
   limit)
7. `report_generator.py` (`generate_audit_md`) — one section per FAIL
   requirement, freeform prose
8. `run_grader.py` (`run_grader`) — generic, parameterized real
   `DetectGrader` invocation (judge model `openai/gpt-4o` via OpenRouter)

## 3. Critical gotchas (all hit live this session — don't re-discover them)

1. **`chat_client` MUST be `a4v.llm.ChatClient`, not a raw
   `openai.OpenAI()` client.** `LLMJudgmentLayer` calls
   `self.chat_client._cache_key(...)`/`.complete_json(...)`, methods
   only `ChatClient` has. Passing a raw OpenAI client causes every
   judgment call to crash silently (caught by `judge_result`'s own
   per-requirement error isolation, degrading to `ENVIRONMENT_FAILURE`
   with `conformance_state=None`) — **zero real API calls happen, $0
   cost, and it looks like a clean run with zero escalations and zero
   FAIL findings.** This exact bug produced a fully invalid "0
   escalations across 5 audits" result early in this session before
   being caught and fixed. If you ever see suspiciously-clean all-PASS
   results with $0 spend, check this first.

2. **No Foundry on this node** (GLIBC < required version — AR-009).
   `compile_evmbench_target` (`rtf/l5_predicates/compile_helper.py`)
   compiles ONE entry `.sol` file directly via solc (with explicit
   absolute-path remappings + a neutral `cwd` to prevent crytic-compile's
   Foundry auto-detection from firing), not a whole-project Foundry
   build. **Real EVMbench audits often need MULTIPLE entry-file
   compilations** to cover their full scope (see `scope.txt` per audit —
   several have genuinely disconnected subsystems, e.g.
   `2024-05-arbitrum-foundation`'s 38 scope files span 4 unrelated
   subsystems). `pilot5_driver.py` (SS5 below) handles this by looping
   every `scope.txt` entry as its own compile target.

3. **`solc-select`'s active version is a machine-global mutable side
   effect**, not process-local. `compile_evmbench_target` calls
   `solc-select use <version>` before every compile. **Never run two
   audits (or two entry-file compiles needing different solc versions)
   concurrently** — they will race on this shared global state and one
   could silently compile against the wrong compiler version. Always run
   sequentially. (This is also why some hardhat-adjacent sub-projects
   inside one audit need a different solc version than the rest — e.g.
   `2024-06-vultisig`'s `hardhat-vultisig/` subdir needs 0.8.24 while its
   main `src/` needs exactly 0.7.6; check each audit's `foundry.toml`
   `solc`/`solc_version` field AND any `hardhat.config.ts` before
   assuming one version covers the whole repo.)

4. **`a4v/graph.py` was fixed this session** (commit `5ec39f0`):
   inherited-but-not-overridden functions used to corrupt the node's
   `contract` attribute and add a duplicate `DECLARES` edge. Fixed via
   `function.contract_declarer`-based resolution + a
   `processed_function_ids` guard. If you're on an older checkout without
   this commit, `resolve_seed_node`/graph queries on any contract with
   inheritance may silently misattribute functions to the wrong
   contract.

5. **Codex investigations genuinely take a long time.** Individual
   escalations run up to the 900s ceiling; a single scope-entry file can
   have *multiple* escalating requirements processed *sequentially*
   within one `run_pipeline_e2e()` call. Observed real per-entry
   durations this session: 480s to ~1800s+ when several requirements
   escalate. **A single audit with 20-45 scope entries can take multiple
   hours wall-clock.** Plan accordingly — this is not a quick pilot to
   run in one sitting per audit.

6. **Landlock is unavailable on this kernel** (4.18, predates Landlock's
   5.13 introduction) — Codex's own sandbox modes crash outright. Always
   use `--dangerously-bypass-approvals-and-sandbox`. See memory
   `project_jubail_landlock_limitation.md`.

7. **Known, disclosed architecture gaps** (documented in the frozen
   preregistration SS4.3, confirmed live during the pilot, not yet
   fixed):
   - **Requirement- vs. candidate-granularity mismatch**: the wired
     pipeline resolves evidence at requirement granularity; one
     requirement's evidence can span several distinct locations.
     `pipeline_e2e.py` uses only the single highest-ranked location as
     the graph-navigation seed.
   - **Non-function-shaped evidence locations have no graph-resolution
     path at all** — confirmed as the *dominant* real-world escalation
     blocker during the pilot. EthTrust's 22 compiler-version-check
     requirements report locations like `"compiler config"` or
     `"pragma solidity>=0.8.0"`, not `Contract.function` — `graph_
     navigation.resolve_seed_node` correctly has nothing to match and
     raises, so these requirements can *never* reach Codex even when the
     bounded judgment says they need to.
   - **Two inconsistent compilation paths**: `pipeline_e2e.py` rebuilds
     `ProgramGraph` via a second, separate `ProgramGraph.build()` call
     that doesn't apply the same optimizer/`--via-ir` settings
     `compile_evmbench_target` uses for deterministic evidence
     collection — confirmed live (canto's `LendingLedger.sol` hit a real
     "stack too deep" error on the second compile that the first never
     hit), blocking every escalation attempt for that audit.
   - **Cost-ceiling enforcement is per-completed-call**, not a live
     OpenRouter balance poll — a single very expensive in-flight
     investigation could push total spend somewhat past the nominal
     ceiling before the next check fires.

## 4. How EVMbench itself works (audit/finding structure)

- All 40 audit entries: `/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench/audits/<audit-id>/`
- Each has `config.yaml` (ground-truth `vulnerabilities:` — **do not
  read for any audit whose `audit.md` isn't already frozen and graded**,
  see SS6) and `Dockerfile` (`git clone --recurse
  https://github.com/evmbench-org/<audit-id>.git`, no pinned commit — so
  pin your own via `git rev-parse HEAD` at clone time and record it).
- `scope.txt` (in-scope file list) and `out_of_scope.txt` are safe,
  non-finding metadata.
- **`2023-12-ethereumcreditguild`'s `config.yaml` embeds finding text
  inline**, unlike most other audits' directory-per-finding pattern —
  a real incident this session where finding text was read by accident
  while checking non-finding fields. Be careful with any generic
  "extract just the metadata fields" script on this specific audit.
- Grading: `rtf/l12_evaluation/run_grader.py`, generic —
  `run_grader(audit_id, agent_output_path, judge_model="openai/gpt-4o")`.
  Reuses the exact OpenRouter/`preparedness_turn_completer` wiring the
  original task10-specific one-off script used (that harness's own model
  registry only recognizes bare OpenAI names, hence the
  `CONTEXT_WINDOW_LENGTHS.setdefault` patch).
- A real, fully-graded example from an earlier session:
  `/scratch/md5344/evmbench/run/task10_real_entry/` (PoolTogether,
  `2023-07-pooltogether`, H-02/H-04, scored 0/2 then, separately, a
  pipeline_lite multi-agent approach scored 1/2 — see top-level
  `/scratch/md5344/evmbench/CLAUDE.md` for that whole line of work,
  which is a **different system** — an LLM-agent auditor via
  SingularityBackend, unrelated to RTF's own static-predicate framework).

## 5. The 5-audit pilot: exactly where it stands

**Preregistration is frozen**: `rtf/l12_evaluation/RTF_5_AUDIT_END_TO_END_PREREGISTRATION.md`
(SHA-256 `2e7b04700eb07e141fdc034cd0b8d74bb8766ebed4565b7c017cd68bfcb610a7`
at freeze time). **Selection record**:
`rtf/l12_evaluation/PILOT5_AUDIT_SELECTION.md`. Both explain the
methodology in full — read them before touching anything below.

**Key preregistration finding (AR-025)**: 0 of EVMbench's 40 audits have
genuine NONE prior exposure (the predecessor MGPR system read every
audit's finding title+description building its benchmark registry). The
5 selected audits are LIMITED/floor-only exposure (title/description
known historically, never reasoned about further) — disclosed plainly,
not redefined to look like NONE.

**Selected 5 audits + exact frozen commits:**
1. `2025-01-liquid-ron` — `b0df3cffce6e1a151c1c32dea8b17dd4f8932cf7`, solc 0.8.20
2. `2024-01-canto` — `cec6952e832f05e836a96223d8e12aa7b0641c15`, solc 0.8.17
3. `2024-05-arbitrum-foundation` — `1ede95fe9198887481aa5824fe58eb776ff763a3`, solc 0.8.17
4. `2024-06-vultisig` — `607f320dd21ceaee567a937ab77847641f0614bf`, solc 0.7.6 (main), **0.8.24 for `hardhat-vultisig/` subtree**
5. `2025-10-sequence` — `70fc6ba76d8088bdf07634d2bb9555b6c4fe3a96`, solc 0.8.28

**Driver script**: `rtf/l12_evaluation/pilot5_driver.py` (copied into
the repo this session — was previously only in ephemeral job scratch).
This is **pilot scaffolding, not the frozen pipeline itself** — it loops
every `scope.txt` entry as its own `run_pipeline_e2e()` call (per gotcha
#2 above), tracks a per-audit Codex cost sub-ceiling, and merges FAIL
results into one `audit.md` per audit. It has a **resume capability**
(added mid-session after a harness restart killed an in-progress run):
if `entry_XX_*_stage.json` already exists in the artifacts dir for a
given scope entry, it re-hydrates that entry's results instead of
re-running (and re-spending) it. Usage:

```
python3 rtf/l12_evaluation/pilot5_driver.py \
  <audit_id> <repo_root> <scope.txt path> <artifacts_dir> \
  <per_audit_codex_ceiling_usd> <default_solc_version> '<path_prefix_overrides_json>'

# example (vultisig, resuming):
python3 rtf/l12_evaluation/pilot5_driver.py \
  2024-06-vultisig /path/to/cloned/2024-06-vultisig \
  /path/to/cloned/2024-06-vultisig/scope.txt \
  rtf/l12_evaluation/pilot5_artifacts/2024-06-vultisig \
  4.0 0.7.6 '{"hardhat-vultisig/": "0.8.24"}'
```

Repo clones aren't committed (large, and reproducible from the pinned
commits above) — re-clone with `git clone <url> <dir> && cd <dir> && git
checkout <commit>` from `https://github.com/evmbench-org/<audit-id>.git`.

**Real status per audit** (results preserved in
`rtf/l12_evaluation/pilot5_artifacts/<audit_id>/`):

| Audit | Status | Real cost | FAIL findings | Grade |
|---|---|---|---|---|
| `2024-01-canto` | **complete** | $0 | 0 | 0/2 |
| `2025-01-liquid-ron` | **complete** | $2.56 | 17 | 0/1 |
| `2024-06-vultisig` | **8/22 entries done**, interrupted mid-run by a harness restart (the pilot process itself died, confirmed via process table — not a pipeline crash) | ~$3.00 so far | 6 (in the 8 done) | not graded yet |
| `2024-05-arbitrum-foundation` | **stale, invalid** — only has the pre-fix ($0-cost, meaningless) result. Must be re-run from scratch with `pilot5_driver.py`. | — | — | — |
| `2025-10-sequence` | **stale, invalid** — same as above, must be re-run. | — | — | — |

**Known data gap**: vultisig's first 8 entries' `stage.json` files were
written *before* a mid-session fix added `fail_details` persistence (the
data needed to reconstruct FAIL findings on resume). Their aggregate
*counts* are accurate, but their specific FAIL-finding text (reasoning,
evidence citations) was not captured before the interruption — disclose
this plainly in the final report rather than silently omitting it or
re-running (re-running would re-spend the ~$2.7 already spent on those 8
entries). The raw Codex output files may still exist under
`/scratch/md5344/.claude/jobs/318205ae/tmp/pilot5_scratch/2024-06-vultisig/*_gout.txt`
if that job's scratch hasn't been cleaned up yet — worth checking before
assuming this is unrecoverable.

## 6. Interim failure-mode analysis (from canto + liquid-ron only — NOT the full 5-audit picture)

Two real, distinct failure categories seen so far, root-caused against
actual grader output (permitted — grading itself necessarily touches
ground truth for already-frozen-and-graded audits; this is not a
violation of the "don't read ground truth before freezing" rule):

- **Canto (0 FAIL findings)**: every escalation attempt failed at graph
  resolution (the two infra gaps in SS3 above), so nothing reached
  Codex. Separately, canto's actual ground-truth bug is a domain-specific
  economic logic error (block-number-vs-time epoch miscalculation) that
  none of EthTrust's standards-based requirements are aimed at catching
  — looks like a genuine `REQUIREMENT_COVERAGE_FAILURE`, independent of
  the infra issue.
- **Liquid-ron (17 real FAIL findings, still 0/1 graded)**: real,
  substantive findings (missing input validation, no NatSpec, missing
  events, unchecked ops, assembly use) — but liquid-ron's actual
  ground-truth bug is an incorrect `totalAssets()` calculation, which
  none of the 17 findings addresses. Also looks like
  `REQUIREMENT_COVERAGE_FAILURE`.

**Do not generalize from n=2.** The frozen preregistration's own rule is
to do full 14-category failure-taxonomy classification only after all 5
audits are frozen and graded (`rtf/l9_assumptions_register/REGISTER.jsonl`'s
failure-taxonomy categories, mirrored in the preregistration SS6).

## 7. Budget discipline this session

Started at a $5 self-imposed cap (carried over from earlier work), raised
to $10 soft / $20 hard for the pilot, then raised again to $40 hard after
a real per-bundle cost projection showed $20 was at risk from bounded-
judgment volume alone. **Always check real spend before assuming a
budget is safe** — `curl -s https://openrouter.ai/api/v1/auth/key -H
"Authorization: Bearer $(cat /scratch/md5344/evmbench/run/task5_secrets/openrouter.key)"`,
`usage_daily` field. As of this handoff, total spend for this pilot
(everything in SS5's table) is roughly **$5.60-6.00** — get an exact
current figure before continuing, don't trust this number as still
current.

## 8. What's genuinely NOT done yet

- Vultisig: 14 more scope entries (resume-capable, won't re-spend the
  first 8's cost)
- Arbitrum-foundation: full re-run (39 scope entries), never done with
  the fixed driver
- Sequence: full re-run (47 scope entries), never done with the fixed
  driver
- Full failure-taxonomy classification across all 5 (only started for 2)
- The final report itself, `rtf/l12_evaluation/RTF_5_AUDIT_END_TO_END_PILOT.md`
  (user spec's 23-section format) — not started
- Separately, still-untouched from before this pilot: Phase H items 8
  (second-pass verifier-vs-independent design comparison), 10 (freeze a
  formal RTF v3), 11-12 (ordered Tempo→PoolTogether rerun + final report)
  — these predate the 5-audit pilot and were never in scope for it.

## 9. Where to look for more

- `rtf/PROJECT_SUMMARY.md` — full project history, kept current after
  every major phase
- `rtf/l9_assumptions_register/REGISTER.jsonl` — every logged deviation,
  AR-001 through AR-026
- `/scratch/md5344/evmbench/CLAUDE.md` — the separate SingularityBackend/
  LLM-agent-auditor system (not RTF, don't confuse the two)
- Memory (persists across Claude Code sessions, not in git):
  `project_rtf_state.md`, `feedback_research_methodology.md`,
  `feedback_spend_discipline.md`, `project_jubail_landlock_limitation.md`
  under `/scratch/md5344/.claude/projects/-scratch-md5344-evmbench-agent4vul/memory/`
