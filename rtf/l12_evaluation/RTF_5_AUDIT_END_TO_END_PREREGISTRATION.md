# RTF + Graph-Gated Codex: 5-Audit End-to-End Pilot — Preregistration

**Status at time of writing: DRAFT, not yet frozen.** Section 4 (pre-pilot
integration fixes) is confirmed for the parts completed and tested so
far; section 3's escalation-bridge/`audit.md`-generator/grader-script
build is in progress in a background construction pass at the time this
draft was started, and this document will be updated with its confirmed
file paths, exact escalation-rule code, and smoke-test result before the
freeze hash is taken. **Do not treat this document as frozen until the
"FROZEN" marker and hash appear at the bottom.**

## 0. Research question

> Across 5 real EVMbench audits, can the current RTF pipeline route
> applicable EthTrust requirements, generate useful candidate evidence,
> escalate unresolved candidates to graph-gated Codex investigation, and
> produce findings that the real DetectGrader recognizes?

This is a system-level pilot. It is explicitly **not** optimized for a
good score — its purpose is to find where the frozen pipeline actually
breaks, end to end, on real repositories it has not been tuned against.

## 1. Frozen architecture

```
EthTrust requirements
        |
RTF applicability / deterministic strategies   (L1-L6, rtf/l5_predicates/, rtf/l12_evaluation/run_rtf.py)
        |
candidate locations                             (EvidenceItem.location, "Contract.function")
        |
one evidence bundle per candidate                (rtf/l12_evaluation/evidence_ranking.py)
        |
is evidence sufficient?                          (bounded L8 judgment run first, always)
        |
bounded judgment OR Codex escalation              (escalation rule, SS3 below)
        |
graph-gated Codex investigation                   (a4v.graph.ProgramGraph + MCP tools, arm_g_codex.py)
        |
candidate-level decision                          (ConformanceState, shared with the bounded path)
        |
finding generation / consolidation                (report_generator.py)
        |
audit.md
        |
real EVMbench DetectGrader                        (run_grader.py, openai/gpt-4o judge)
```

Investigation path (no fixed graph-depth or tool-call limit):

```
candidate
    |
Codex asks what fact it needs
    |
ProgramGraph relation query (MCP tool call)
    |
relevant connected code exposed
    |
Codex continues as deeply as needed
    |
stop when evidence is sufficient
```

## 2. Freeze items

### 2.1 RTF version / framework_version

`0.2.0-evidence-enrichment` — the current tagged state of
`rtf/l9_assumptions_register/REGISTER.jsonl` entries as of this pilot
(AR-001 through AR-025). **RTF v3 (Phase H items 8/10 — a second-pass
verifier-vs-independent design comparison and a formal version freeze)
was never completed** (`rtf/PROJECT_SUMMARY.md` / memory `project_rtf_state.md`
confirm these Phase H items remain open) — this pilot runs under the
current, already-tagged `0.2.0-evidence-enrichment` state, not a
hypothetical v3. Stated here explicitly rather than implied.

### 2.2 EthTrust snapshot

- Spec: EEA EthTrust Security Levels Specification, Version 3
- Retrieved: 2026-08-05T18:30:36Z (`standards/ethtrust/metadata.json`)
- Snapshot SHA-256: `7b2cea3b2f19945a463dbf7ad2861494f5a4ab55c5a586e8703547afbcaf60a7`
- Verified requirement inventory: **81 total** — 22 S / 24 M / 24 Q / 11 GP
  (supersedes the provisional ~52-requirement planning estimate)

### 2.3 Predicates / applicability rules

`rtf/l5_predicates/predicates.py` (1322 lines, unit-tested in
`tests/unit/test_mgpr_predicates.py` and predicate-specific test files —
490 passed / 7 skipped as of the pre-pilot test run, SS4.1). No predicate
logic is modified for this pilot.

### 2.4 Evidence schema

`EvidenceItem` (deterministic predicate output) — bare `"Contract.function"`
`location` field, `applicability_state`, evidence detail per predicate.
Ranked/bundled into LLM-readable text by `rtf/l12_evaluation/evidence_ranking.py`
(existing, pre-pilot code, unmodified).

### 2.5 Escalation rule (frozen, new for this pilot)

Run the bounded L8 judgment (`rtf/l12_evaluation/judge_with_l8.py`,
model `openai/gpt-5.1-codex-max`) on every applicable requirement's
evidence bundle first — always, no upfront sufficiency heuristic that
would skip it. **Escalate that specific candidate to graph-gated Codex
investigation if and only if** the bounded judgment's resolved
`ConformanceState` is `INSUFFICIENT_EVIDENCE` or `INCONCLUSIVE`, **or**
its `confidence` field is `LOW`. Otherwise the bounded judgment's
decision is accepted directly, with no Codex call.

This rule deliberately reuses only signals the L8 judgment schema
already produces (`decision`, `confidence`) — **no new relevance or
evidence-sufficiency classifier is introduced**, per explicit user
instruction. Exact implementation: see SS4.2 (pending fork confirmation).

### 2.6 Bounded-LLM judgment layer

- Model: `openai/gpt-5.1-codex-max` (matches the pinned model from the
  most recent real RTF v2 run, `rtf/l12_evaluation/runs/v2_run1_tempo-mpp-streams-pooltogether/artifacts/*_l8_raw.json`)
- Schema: decision (PASS/FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE) /
  requirement_citations / evidence / reasoning_summary / open_questions /
  confidence (HIGH/MEDIUM/LOW) / model_version / prompt_version / run_id /
  second_pass_agreement (`rtf/l8_llm_judgment_layer/judgment_layer.py`)
- Second-pass disagreement handling: `resolve_conformance_from_judgment()`
  downgrades a disagreeing second pass to `INCONCLUSIVE`
  (`rtf/l12_evaluation/judge_with_l8.py:233-250`)

### 2.7 Codex escalation path

- CLI: `codex-cli 0.104.0` (musl static build), model
  `openai/gpt-5.1-codex-max`, via OpenRouter (`wire_api="responses"`),
  `--dangerously-bypass-approvals-and-sandbox` (the only working mode on
  this cluster's kernel — Landlock unavailable, see memory
  `project_jubail_landlock_limitation.md`)
- System/task prompt: `rtf/l8_llm_judgment_layer/bundle_agent_experiment/ARM_G_PROMPT_v1.md`,
  built per-candidate via `build_arm_g_prompt()`
- Graph API: `a4v.graph.ProgramGraph` (inherited-function bug fixed this
  session, commit `5ec39f0`, 490 tests passing)
- Graph relations exposed via MCP tools (`show_candidate` /
  `investigate` / `read_source`): `CALLERS`, `CALLEES`,
  `EXTERNAL_TARGETS`, `INTERFACES`, `MODIFIERS`, `STATE_READS`,
  `STATE_WRITES`, `STATE_WRITES_TRANSITIVE`, `WRITE_AFTER_EXTERNAL_CALL`,
  `WRITERS_OF_STATE`
- Candidate -> graph node resolution: `resolve_seed_node()` (prefix-match
  on `canonical_name`, raises explicitly on zero or >1 match — never
  guesses on overloads), promoted out of the experiment folder per SS4.2
- **No fixed graph-hop or tool-call limit.** Codex investigates until it
  judges evidence sufficient or the timeout is reached.

### 2.8 Timeout

**900 seconds per Codex investigation** — a safety ceiling, not a
target, sized from the observed ~11s/turn latency floor confirmed across
three independent PoolTogether attempts (AR-022/023/024). Codex may stop
much earlier; PoolTogether's successful AR-024 run completed in 381.4s.

### 2.9 Cost ceiling

Per explicit user instruction this session: **soft cap $10** (the user
must be informed on crossing this), **hard cap $20** (all new spend
stops). Monitored live via OpenRouter's per-call `usage.cost` and
account-level `usage_daily`, same technique validated in AR-024. The
orchestrator (`pipeline_e2e.py`, SS4.2) refuses to launch a new Codex
escalation once the ceiling would be exceeded, marking any remaining
candidates `INCONCLUSIVE` with reason `cost_ceiling_reached` rather than
silently dropping them (user spec SS19).

### 2.10 Final report format

`rtf/l12_evaluation/RTF_5_AUDIT_END_TO_END_PILOT.md`, 23 sections per the
user's spec section 20, plus machine-readable artifacts (stage metrics,
candidate list, bundles, Codex traces, graph traversal traces, decisions,
`audit.md` outputs, grader outputs, failure classifications, cost/token/
time records) under `rtf/l12_evaluation/pilot5_artifacts/`.

## 3. Selected audits

See `rtf/l12_evaluation/PILOT5_AUDIT_SELECTION.md` for the full selection
methodology and exposure ledger. Summary:

| # | audit | exposure | commit | own-code `.sol` files | notes |
|---|---|---|---|---|---|
| 1 | `2025-01-liquid-ron` | LIMITED (floor-only) | `b0df3cffce6e1a151c1c32dea8b17dd4f8932cf7` | 10 | smallest own-code footprint |
| 2 | `2024-01-canto` | LIMITED (floor-only) | `cec6952e832f05e836a96223d8e12aa7b0641c15` | 4 | tiny own-code amid large vendored tree |
| 3 | `2024-05-arbitrum-foundation` | LIMITED (floor-only) | `1ede95fe9198887481aa5824fe58eb776ff763a3` | 142 | largest own-code, includes Yul assembly |
| 4 | `2024-06-vultisig` | LIMITED (floor-only) | `607f320dd21ceaee567a937ab77847641f0614bf` | 85 | foundry+hardhat hybrid |
| 5 | `2025-10-sequence` | LIMITED (floor-only) | `70fc6ba76d8088bdf07634d2bb9555b6c4fe3a96` | 49 | pnpm monorepo workspace |

**Exposure declaration**: all 5 are LIMITED/floor-only (title/description
known via a historical benchmark registry built for the predecessor
MGPR system, never reasoned about beyond that) — **not NONE**. A full
exposure audit found 0 of the 40 EVMbench entries have genuine NONE
exposure; see AR-025 and SS1 of `PILOT5_AUDIT_SELECTION.md` for the full
finding. This is disclosed plainly rather than worked around.

Ground-truth finding text for these 5 audits has **not** been read by
anyone working on this pilot as of this document's freeze. It may only
be opened, per audit, after that audit's `audit.md` + traces are frozen
and DetectGrader has scored it (user spec section 13).

## 4. Pre-pilot integration readiness (SS4.1 confirmed, SS4.2 pending confirmation at freeze time)

### 4.1 Confirmed fixes (completed, tested, committed before this pilot)

- **`a4v/graph.py` inherited-function bug** (function-node `contract`
  attribute corruption + duplicate `DECLARES` edges for inherited-but-
  not-overridden functions): fixed via `function.contract_declarer`-based
  resolution + a `processed_function_ids` guard (not a naive `fid in g`
  guard, which regressed 2 existing tests by also skipping legitimate
  reprocessing of call-site stub nodes — caught and corrected before
  commit). 3 new regression tests added
  (`tests/unit/test_graph.py`, fixture `tests/fixtures/inherited_function/`).
  Full suite: 490 passed, 7 skipped (was 487 passed pre-fix). Commit
  `5ec39f0`.
- **Graph node identity for overloaded functions**: audited, found
  already correct — `resolve_seed_node()` raises explicitly on zero or
  >1 matching node, never guesses. No fix needed.
- **MCP lazy graph-build**: confirmed intact
  (`graph_mcp_server.py:76-83,103,116,151,170-171,196,240`).
- **Codex session isolation / trace persistence / cost-token logging /
  timeout handling**: confirmed intact in `arm_g_codex.py`, validated
  live across AR-022/023/024.

### 4.2 Escalation-bridge / report-generator / grader-script build

*[PENDING — this section will be filled in with exact file paths, the
literal escalation-rule function, the `context_bundle_text` wiring
finding, and the smoke-test result once the in-progress construction
pass reports back. The document is not frozen until this section is
complete.]*

## 5. Evaluation metrics (per user spec section 14)

**Requirement/routing layer**: applicable requirement count, DIRECT
requirement correspondence recall, candidate localization recall.
**Evidence layer**: evidence collection recall, bundles per audit,
escalation rate. **Codex investigation**: completion rate, timeout rate,
correct candidate judgments, false PASS, false FAIL, appropriate
uncertainty, graph relations used, max traversal depth, divergence rate,
average time, average cost. **End-to-end**: DetectGrader finding recall,
findings found / total ground-truth findings, per-audit score, aggregate
score. Fresh-exposure vs. previously-exposed audits reported separately
(moot for this specific pilot — all 5 are uniformly LIMITED/floor-only,
per SS3).

## 6. Failure taxonomy (frozen, verbatim from user spec section 12)

`REQUIREMENT_COVERAGE_FAILURE`, `APPLICABILITY_FAILURE`,
`ROUTING_FAILURE`, `LOCALIZATION_FAILURE`, `PREDICATE_EVIDENCE_FAILURE`,
`ESCALATION_FAILURE`, `GRAPH_NAVIGATION_FAILURE`,
`GRAPH_COVERAGE_FAILURE`, `AGENT_REASONING_FAILURE`, `AGENT_TIMEOUT`,
`JUDGMENT_SYNTHESIS_FAILURE`, `REPORT_GENERATION_FAILURE`,
`GRADER_MISMATCH`, `INFRASTRUCTURE_FAILURE`. Multiple contributing causes
allowed; deepest/root cause identified per miss. Every missed
ground-truth finding gets exactly this classification, applied only
after that audit's DetectGrader run is complete (SS3).

## 7. No-tuning rule (frozen, verbatim from user spec section 17)

Once this document is marked FROZEN: no predicate changes, no prompt
changes, no graph relation additions, no model changes, no special
cases, no audit-specific timeout changes, no manual candidate injection,
across all 5 audits. Defects found during the run are logged, not fixed
mid-run — fixes belong to the next version.

---

**FREEZE STATUS: NOT YET FROZEN.** Awaiting SS4.2. No pipeline run
against any of the 5 selected audits may begin until this document is
updated, reviewed, and a freeze hash recorded below.
