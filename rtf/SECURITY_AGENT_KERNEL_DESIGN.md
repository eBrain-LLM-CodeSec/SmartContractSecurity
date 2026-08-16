# Custom security-agent kernel: architecture trace + proposed design

Written before any implementation, per the task brief's own gate ("produce
[deliverables 1-5] ... then implement the approved architecture"). Branch
`security-agent-kernel`, forked from `rtf-v2-redesign` @ `1e579dd` ("RTF v3:
Phase 6 -- requirement-specific investigation guidance"). That commit is
pinned as this work's baseline deliberately (see "Relationship to RTF v3"
below) — do not silently rebase onto a later `rtf-v2-redesign` tip without
re-checking this doc's file:line citations still hold.

Goal of this document: (1) trace exactly how RTF v2's clustering reaches
Codex today, (2) propose a minimal custom investigation-agent kernel that
plugs into the *same* clustering/context pipeline as a swappable
investigator, (3) justify each proposed dependency, (4) lay out small
vertical implementation increments, (5) lay out the test plan. Nothing below
has been implemented yet except where explicitly marked.

---

## 0. Relationship to RTF v3 (read this first)

`rtf-v2-redesign` currently has an **in-flight, separate** redesign
("RTF v3", `rtf/RTF_V3_REDESIGN_PLAN.md`, commits through "Phase 6") landing
concurrently on the same branch. RTF v3 fixes *requirement fidelity*:
restoring dropped `exceptions_referenced`/`overriding_requirements` text,
anchoring semantic properties to a parent EthTrust requirement, adding a
growth/iteration structural predicate, and adding requirement-shape-aware
investigation guidance. **It does not touch the investigator** — every fix
lands in context-assembly (`context_artifacts.py`), predicates
(`l5_predicates/predicates.py`), and semantic generation
(`semantic_property_generation.py`); Codex is still invoked exactly as
before via `arm_g_codex.run_arm_g_bundle`.

This is good news for the task brief's own experimental discipline ("Keep
RTF + cluster generation fixed and change only the investigator" — brief
§"Important experimental principle"): RTF v3 *is* "the parallel RTF fidelity
work" the brief's Phase 8 says to align with, and it is orthogonal by
construction. Consequences for this design:

- The security-agent kernel is built as a **drop-in alternative
  investigator**, never touching `grouping_engine.py`, `context_artifacts.py`,
  or the predicate/generation layers.
- First A/B comparisons (brief Phase 16) should pin a single commit of
  `rtf-v2-redesign` (this doc pins `1e579dd`) as the shared input-generation
  baseline for *both* arms, so a difference in score is attributable to the
  investigator alone, not to RTF v3 landing mid-comparison.
- Once RTF v3 finishes and is validated on its own, the kernel can be
  re-pointed at its tip for a later, second comparison — but that is a new,
  explicitly separate experiment, not silently folded into this one.

---

## 1. Existing architecture trace (Phase 1)

Traced read-only against `rtf-v2-redesign` @ `1e579dd` (worktree
`/scratch/md5344/evmbench/agent4vul/.claude/worktrees/rtf-v2-redesign`).

### 1.1 Grouping / clustering

`rtf/l11_investigation_grouping/grouping_engine.py` (298 lines). Deterministic,
**not LLM-based** clustering:

- `compatibility_score(a, b)` (`:54`) — pairwise additive score between two
  `PropertyMetadata`. Hard veto (`-inf`) for identical IDs or an "unsafe
  category combination". Strong positive (+3.0): same `requirement_id`, same
  `reasoning_category`, same `target_contract`, shared state vars/types/
  constants/callgraph region, overlapping candidate locations. Weak positive
  (+1.0): same file, same inheritance hierarchy, shared symbols. Strong
  negative (-4.0): different known contracts sharing nothing.
- `cluster_properties(...)` (`:168`) — greedy agglomerative merge; cross-
  cluster score = **minimum** pairwise score across every member pair
  (`pairwise_min_score`); blocked by a hard veto anywhere in the merge, a
  `max_cluster_size`/`max_context_size` cap, or an optional `hard_gate`.
- Named presets in `policies.py`: `G0_UNGROUPED` (no grouping),
  `G1_CONSERVATIVE` (strict hard gate: same req_id AND category AND
  contract), `G2_CONTEXT_AWARE` (**live default**, cap 8, no hard gate),
  `G3_ADAPTIVE` (cap by estimated context size instead of count).

**Heuristic in one line**: not "1 cluster = 1 contract"; a multi-signal
semantic score dominated by shared code context, with same-requirement/
same-category as strong-but-not-exclusive signals and an explicit veto for
unrelated contracts sharing nothing.

### 1.2 Cluster schema

`Cluster` (`grouping_engine.py:116-145`) — frozen `@dataclass` (this
codebase uses **zero Pydantic** anywhere; every structured object is a plain
`@dataclass`):

```python
@dataclass(frozen=True)
class Cluster:
    cluster_id: str
    property_ids: tuple[str, ...]
    grouping_reason: tuple[str, ...]
    shared_context: dict   # union of contracts/functions/files/state_vars/...
    estimated_context_size: int
    estimated_complexity: float | None = None
```

Member `PropertyMetadata` (`property_metadata.py`, also frozen dataclass,
~30 fields) carries `property_id`, `requirement_id`, `parent_requirement_id`,
`requirement_semantic_intent`, `property_text`, `target_contract`/
`target_function`, `candidate_locations`, `relevant_files`/`symbols`/
`state_variables`/`types`/`constants`, `callgraph_neighbors`,
`inheritance_context`, `reasoning_category`, `source_kind`
(`"ethtrust"`/`"erc_gp"`/`"code_semantics"`), `confidence`, `rationale`,
`grounding_evidence`.

### 1.3 Membership

Not 1-cluster-per-file/contract. A property joins because it scores above
threshold against *every* existing member (min-of-pairwise rule); two
properties in different files can cluster via shared state or callgraph
adjacency, and two properties in the same contract can fail to cluster if
they share nothing else.

### 1.4 Context assembly

`context_artifacts.py` (471 lines), three deterministic Markdown artifacts:

1. **Protocol context** (once/audit) — in-scope contracts, inheritance,
   entry points, critical state, naming-heuristic trust boundaries
   (caveated as unverified). Never contains a vulnerability conclusion.
2. **Requirement context** (once/req_id, `generate_requirement_context_md`)
   — verbatim EthTrust text + explanatory text (RTF v3 is currently
   extending this to also render exceptions/overriding/referenced text).
3. **Cluster plan** (`generate_cluster_plan_md`) — objective, grouping
   rationale, per-property detail, fixed investigation procedure, required
   output JSON schema. Structurally guaranteed to never leak an expected
   verdict (there's an explicit regression test for this).

Assembly entry point: `prepare_cluster_investigations`/
`prepare_cluster_investigations_with_scope_boundary`
(`live_runner.py:121-214`), fed by `build_context_for_evmbench_target`
(`l12_evaluation/run_rtf.py:282-341`, the compile-and-build-`RunContext`
step). Whole-project compile (`compile_via_foundry=True`) runs a real
`forge build` inside `evmbench-worker.sif` (`l5_predicates/compile_helper.py:
232-298`), then Slither loads the artifacts on the host.

At investigation time these three files are written into the investigator's
own scratch repo copy at `.rtf/context/protocol_context.md`,
`.rtf/context/requirements/<req_id>.md`, `.rtf/plans/<cluster_id>.md`
(`live_runner.py:414-433`) and referenced by **path**, not inlined — the
prompt (`cluster_prompt.py`) just points at the three files plus the frozen
`ARM_G_CLUSTER_PROMPT_v1.md` system text.

### 1.5 Investigation "plan"

No separate planning LLM call — the cluster-plan Markdown *is* the plan,
100% deterministic string formatting over `Cluster`/`PropertyMetadata`.

### 1.6 Codex invocation — **the actual integration seam**

`run_cluster_investigations_live(...)` (`live_runner.py:297-558`) is the
top-level loop. Its `_invoke` closure (`:445-454`) calls a swappable
parameter:

```python
def run_cluster_investigations_live(
    clusters, properties_by_id, protocol_context_md, requirement_context_by_req_id, *,
    audit_id, entry_sol_file, project_root, codex_bin, python_bin, mcp_server_script,
    api_key, codex_model, solc_path_dir, solc_remaps, scratch_root,
    codex_timeout_s=900, cost_ceiling_usd=None, max_split_depth=2, budget=None,
    run_arm_g_bundle_fn=None,   # <-- ALREADY a dependency-injection seam, used today for test mocks
    max_concurrent_investigations=1, run_variant=None, compile_via_foundry=False,
    checkpoint_path=None, estimated_cost_per_call_usd=0.20,
) -> tuple[dict[str, PropertyVerdict], dict[str, object], float, dict[str, dict]]:
    ...
    if run_arm_g_bundle_fn is None:
        from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import run_arm_g_bundle
        run_arm_g_bundle_fn = run_arm_g_bundle
    ...
    def _invoke(item):
        return run_arm_g_bundle_fn(
            codex_bin=..., python_bin=..., mcp_server_script=..., api_key=..., model=codex_model,
            case_id=item["case_id"], entry_file=entry_sol_file, repo_root=project_root,
            candidate_location=item["candidate_location"], solc_path_dir=..., solc_remaps=...,
            prompt=item["prompt"], scratch_root=..., timeout_s=codex_timeout_s,
            extra_files=item["extra_files"], compile_via_foundry=compile_via_foundry,
        )
```

`item["extra_files"]` is exactly the dict of the three `.rtf/*.md` artifacts
above, keyed by relative path; `item["prompt"]` is the frozen cluster
prompt. **This means the security-agent kernel needs no changes anywhere in
grouping/context/prompt code** — it only needs a function with this same
call signature that returns an object exposing (at minimum) `.final_decision`
and `.cost_usd` (confirmed below, §1.9).

Real Codex mechanics for comparison: `arm_g_codex.run_arm_g_bundle`
(`l8_llm_judgment_layer/bundle_agent_experiment/arm_g_codex.py:197-404`)
copies the full repo into a disposable investigation dir, writes a per-call
`~/.codex/config.toml` routing through OpenRouter (`model_provider =
"proxy"`, `base_url = openrouter.ai/api/v1`) plus an MCP server entry for
`graph_mcp_server.py`, then runs:

```python
cmd = [codex_bin, "exec", "--model", model,
       "--dangerously-bypass-approvals-and-sandbox", "--skip-git-repo-check",
       "-C", investigation_dir, "-o", out_path, "--json", prompt]
```

Bare-metal on the login node (sandbox bypass needed — Landlock isn't
available on this kernel), fresh process/session every call, no resumption.
`model` is a plain caller parameter with no committed hardcoded default in
this live path (the 10/15 run's exact `codex_model` string was not found
committed anywhere — flagged as a real gap, not to be assumed).

### 1.7 Prompt Codex receives

`ARM_G_CLUSTER_PROMPT_v1.md` (frozen, 117 lines) + a short generated body
naming the three artifact paths (`cluster_prompt.py:34-56`):

> "You are an EthTrust-guided smart-contract investigation agent. You are
> investigating a CLUSTER of related properties in one session ... You have
> full, normal access to the repository at your current working directory.
> ... Do not skip these or try to re-derive their content by re-reading the
> whole repository from scratch."

Required output: one fenced JSON block, key `"properties"`, exactly one
entry per cluster property. Codex's own `base_instructions` are always
present underneath.

### 1.8 Response parsing

`-o out.json --json` (streaming JSONL turn/item events) →
`_extract_last_fenced_json` (`arm_c_codex.py:145-162`): first fence-open,
**last** fence-close (survives a nested ` ```solidity ` block inside a
finding's own text) → `json.loads` with a `raw_decode` fallback. **No
`--output-schema` enforcement** (documented as unreliable across models in
this project's own history) and **no retry-on-malformed-output at the call
level** — a bad/missing JSON response is treated as incomplete and triggers
automatic cluster **splitting**, not a same-cluster retry.

### 1.9 Findings → requirement mapping

`cluster_response_validation.py` (226 lines):

- `validate_cluster_response` (`:58-118`) — exact expected property_id set
  check (no missing/duplicate/unrecognized).
- `resolve_property_verdicts` (`:188-226`) — maps each verdict string to
  `ConformanceState` (`PASS`/`FAIL`/`INCONCLUSIVE`/`INSUFFICIENT_EVIDENCE`,
  `l12_evaluation/metrics.py:37`). A `PASS` is **downgraded to
  INCONCLUSIVE** unless it passes `property_counterexample_is_sufficient`
  (non-trivial counterexample text required) and, if a `parent_requirement_id`
  exists, `parent_obligation_check_is_sufficient`. Result:
  `PropertyVerdict(conformance_state, reason)` — never implicit free text.
- `live_runner._process_result` (`:456-494`) — confirmed by direct grep:
  the harness only ever reads `getattr(result, "cost_usd", 0.0)` and
  `getattr(result, "final_decision", None)` off whatever
  `run_arm_g_bundle_fn` returns. **This is the entire compatibility
  contract our kernel's return value must satisfy** — nothing else on the
  real `ArmGResult` object is read by the core loop.
- Any property left unresolved after split-depth exhaustion finalizes
  `PropertyVerdict(INCONCLUSIVE, "cluster_investigation_incomplete_or_failed")`
  — never silently dropped.
- Requirement-level aggregation: `aggregate_properties_to_requirements`
  (`:546-559`), FAIL-wins.

### 1.10 Caching

No sqlite anywhere. `a4v/llm.py`'s `ChatClient` (203 lines) — on-disk JSON
cache keyed by `sha256({model, messages, temperature, ...})`, `tenacity`
retries, real `usage.cost` logging. Investigation-level: `checkpoint_path`/
`_append_checkpoint`/`_load_checkpoint` (`live_runner.py:230-294`) — one
JSON line per completed call, resumable, motivated by a real interrupted run
that lost 7 paid-for verdicts. Foundry artifacts: fresh `forge build` per
call by default; `compile_via_foundry` mode reuses one build's `out/
build-info/` for the graph MCP server instead of a third independent
compile.

### 1.11 Cost/token/runtime recording

`ArmGResult` (`arm_g_codex.py:94-114`): `input_tokens`, `cached_input_tokens`,
`output_tokens`, `cost_usd`, `wall_clock_s`, `timed_out`, plus tool
telemetry (`graph_tool_calls`, `revealed_files`, `divergent_files`,
`actual_shell_commands`). `cost_usd` for Codex calls uses **manually pinned
per-token prices for one specific model**, hardcoded — a real fragility if a
different `codex_model` is used without updating the constant. All JSON/
JSONL on disk, no sqlite, no markdown cost-report generator.

### 1.12 Reusable infrastructure (the important part for this design)

- **`a4v/graph.py`'s `ProgramGraph.from_slither`** (367 lines) — real,
  untrained graph over Slither's IR (CALLERS/CALLEES/EXTERNAL_TARGETS/
  STATE_READS/STATE_WRITES/inheritance/etc.). **Dual role today**: (a)
  feeds `PropertyMetadata.callgraph_neighbors`/`relevant_state_variables`
  at clustering time, and (b) exposed live to Codex as MCP tools via
  `graph_mcp_server.py` (367 lines) — `show_candidate()`, `investigate(node_id,
  relation)`, `read_source(node_id)`. For our own kernel we do **not** need
  to speak MCP/JSON-RPC at all (that protocol exists only because Codex is a
  separate process) — we can call the same underlying query functions as
  plain Python, in-process.
- **Foundry/Forge** (`compile_helper.py`) — solid, but pre-investigation
  only today; not callable as a live tool mid-session. `out/build-info/`
  reuse via `GRAPH_COMPILE_VIA_FOUNDRY=1` is the one investigation-time
  reachability, and only indirectly (through the graph tools).
  Running `forge test`/generating a PoC mid-investigation does not exist
  anywhere in this codebase yet.
- **`a4v/llm.py`'s `ChatClient`** — clean, cacheable, cost-logging HTTP
  client against OpenRouter. Reusable as-is for our kernel's model calls.
- **Model abstraction**: none. Two hardcoded-OpenRouter paths side by side
  (`ChatClient`, and Codex CLI via `config.toml`'s `model_provider =
  "proxy"`) — no shared abstraction layer.
- **Pydantic**: zero hits anywhere in the repo.

---

## 2. Proposed minimal architecture (Phase 2)

New package, **`rtf/security_agent/`**, sitting alongside
`l8_llm_judgment_layer/bundle_agent_experiment/` (where the Codex glue
lives) rather than inside the numbered `l#` pipeline-stage packages —
it's an alternative *investigator*, not a new pipeline stage.

```
rtf/security_agent/
    __init__.py
    state.py          # Pydantic: ClusterInvestigationState, RequirementState,
                       # Hypothesis, Evidence, ToolCall/ToolResult, CompletionCheck
    tools.py           # typed tool functions over a4v.graph.ProgramGraph + Slither +
                       # filesystem — in-process, no MCP/subprocess
    model_client.py    # thin wrapper around a4v.llm.ChatClient for tool-calling turns
    prompts.py         # system prompt + per-step assembly (hypothesis-first,
                       # counterexample-driven reasoning shapes; NOT benchmark-specific)
    completion.py      # PASS-discipline / completion-criteria checker
    trajectory.py       # observability: one JSONL event per model/tool call + per-cluster summary
    kernel.py           # SecurityAgentKernel: the decide/execute/update loop (Phase 2's loop)
    investigator.py      # run_security_agent_bundle(...) -- signature-compatible with
                          # run_arm_g_bundle_fn, the actual plug point into live_runner.py
    eval/
        ab_runner.py      # runs one cluster through BOTH investigators, same inputs
        ab_metrics.py      # recall/precision/tokens/cost/tool-calls/files-inspected diff
    tests/
        test_state.py
        test_tools.py
        test_completion.py
        test_kernel_mocked.py    # deterministic, fake model_client — no network
        fixtures/                 # new synthetic Solidity fixtures (Phase 14), NOT EVMbench-derived
            cross_contract_semantic_mismatch/
            cross_contract_semantic_ok/
            missing_input_validation/
            input_validation_ok/
            unbounded_growth_iteration/
            bounded_growth/
            access_control_fail/
```

### 2.1 State (Phase 3) — `state.py`, Pydantic

```python
class ToolCallRecord(BaseModel):
    tool: str
    args: dict
    result_summary: str
    timestamp: float

class Evidence(BaseModel):
    id: str
    claim: str                    # what this evidence establishes
    source_file: str
    source_contract: str | None
    source_function: str | None
    source_lines: str | None      # "120-134"
    tool_call_id: str | None      # which ToolCallRecord produced it
    raw_excerpt: str | None

class Hypothesis(BaseModel):
    id: str
    claim: str
    originating_property_ids: list[str]   # can span multiple properties in the cluster
    status: Literal["OPEN", "SUPPORTED", "REFUTED", "INCONCLUSIVE"]
    supporting_evidence_ids: list[str] = []
    contradicting_evidence_ids: list[str] = []
    next_evidence_needed: str | None = None

class RequirementState(BaseModel):
    property_id: str
    parent_requirement_id: str | None
    status: Literal["UNRESOLVED", "PASS", "FAIL", "NOT_APPLICABLE"]
    hypothesis_ids: list[str] = []
    evidence_for_ids: list[str] = []
    evidence_against_ids: list[str] = []
    unresolved_questions: list[str] = []
    counterexample_attempts: list[str] = []   # what was tried, not just whether

class ClusterInvestigationState(BaseModel):
    cluster_id: str
    property_ids: list[str]
    requirement_states: dict[str, RequirementState]   # keyed by property_id
    hypotheses: dict[str, Hypothesis]
    evidence: dict[str, Evidence]                      # shared pool, referenced by id
    inspected_files: set[str] = set()
    inspected_contracts: set[str] = set()
    inspected_functions: set[str] = set()
    tool_history: list[ToolCallRecord] = []
    unresolved_questions: list[str] = []
    token_usage: TokenUsage
    step_count: int = 0
```

Evidence lives **once**, in `ClusterInvestigationState.evidence`, referenced
by id from both `Hypothesis` and `RequirementState` — satisfies the brief's
"avoid duplicating shared evidence" requirement directly (a dict + id
references, not copies).

### 2.2 Tools (Phase 6) — `tools.py`

Thin, typed wrappers, each a plain Python function taking a Pydantic input
model and returning a Pydantic output model, built directly on
`a4v.graph.ProgramGraph`/Slither — reusing the exact same query logic
`graph_mcp_server.py` already has, called in-process instead of over MCP:

```
get_function_source(contract, function) -> FunctionSourceResult
get_contract_source(contract) -> ContractSourceResult
get_callers(contract, function) -> list[FunctionRef]
get_callees(contract, function) -> list[FunctionRef]
get_external_calls(contract, function) -> list[ExternalCallRef]
get_state_reads(contract, function) -> list[StateVarRef]
get_state_writes(contract, function) -> list[StateVarRef]
get_modifiers(contract, function) -> list[ModifierRef]
get_inheritance(contract) -> InheritanceInfo
get_related_functions(contract, function) -> list[FunctionRef]   # one-hop union of the above
read_file(path) -> str
search_repository(pattern) -> list[SearchHit]
```

V0 excludes `run_command`, `run_foundry_test`, `generate_temporary_poc` —
per the brief's Phase 18, the first version is a **read-only investigator**.
`run_foundry_test`/PoC generation is a later milestone, added only once
static investigation alone is proven and only against an isolated temp
workspace, never production source.

### 2.3 Model client — `model_client.py`

Reuses `a4v.llm.ChatClient` directly (existing OpenRouter HTTP client:
caching, `tenacity` retries, real `usage.cost` logging) for the agent's
tool-calling turns. Tool schemas are generated from the Pydantic input
models (`Model.model_json_schema()`) and passed as standard OpenAI-style
`tools=[...]` — most OpenRouter-routed models support this natively, which
sidesteps the fenced-JSON-extraction fragility documented in §1.8/§1.9 for
final-answer parsing (final verdicts are still validated with a Pydantic
model on receipt, with a fenced-JSON fallback extractor for models that
don't honor tool-calling reliably, mirroring the existing
`_extract_last_fenced_json` approach as a safety net, not the primary path).

### 2.4 Kernel loop (Phase 2) — `kernel.py`

```python
class SecurityAgentKernel:
    def run_cluster(self, cluster_context: ClusterContext) -> ClusterInvestigationState:
        state = ClusterInvestigationState.initial(cluster_context)
        while not self._completion_met(state, cluster_context):
            action = self.model_client.decide_next_action(cluster_context, state)
            result = self._execute(action, cluster_context)
            state = self._update(state, action, result)
            if state.step_count >= self.max_steps:
                break
        return state
```

Understandable by reading `kernel.py` + `state.py` + `completion.py` in one
sitting — no separate planner/critic/multi-agent roles in V0, matching the
brief's explicit "do not over-engineer this" instruction.

### 2.5 Completion / PASS discipline (Phase 9) — `completion.py`

Per-requirement, not global:

```python
def is_requirement_resolvable(req_state: RequirementState, req_kind: RequirementShape) -> bool:
    # e.g. for INPUT_DOMAIN_VALIDATION-shaped requirements: at least one
    # counterexample attempt targeting boundary/invalid-domain input recorded;
    # for ACCESS_PRIVILEGE_CONTROL-shaped: least-privileged-caller hypothesis
    # explicitly tested; for GAS_DOS_STATE_GROWTH-shaped: growth + pruning +
    # iteration-site all explicitly checked (present/absent recorded either way).
    ...

def cluster_can_conclude(state: ClusterInvestigationState, cluster_context) -> tuple[bool, list[str]]:
    # returns (ready, blocking_reasons) -- every property addressed,
    # mandatory counterexample attempts made per its reasoning-shape,
    # no unresolved high-severity question remains
```

The per-shape resolvability rules deliberately reuse the *existing*
`ReasoningCategory` taxonomy (`l11_investigation_grouping/taxonomy.py`,
already 16 categories derived from the EthTrust corpus) rather than
inventing a parallel one — this is the same taxonomy RTF v3's Phase 6
guidance table keys off, so the two efforts stay conceptually aligned
without sharing code.

### 2.6 Investigator entry point — `investigator.py`

```python
def run_security_agent_bundle(
    *, codex_bin, python_bin, mcp_server_script,   # accepted, unused -- signature compatibility
    api_key, model, case_id, entry_file, repo_root, candidate_location,
    solc_path_dir, solc_remaps, prompt, scratch_root, timeout_s, extra_files,
    compile_via_foundry,
) -> SecurityAgentResult:
    """Drop-in replacement for arm_g_codex.run_arm_g_bundle, passed as
    run_arm_g_bundle_fn to live_runner.run_cluster_investigations_live.
    `extra_files` IS the three .rtf/*.md context artifacts (same content
    Codex would get); `prompt` is the same frozen cluster prompt. Loads a
    ProgramGraph over `repo_root` (reusing compile_helper's already-built
    Foundry artifacts when compile_via_foundry, exactly like the graph MCP
    server does today), runs SecurityAgentKernel.run_cluster once per
    cluster, and maps its resolved ClusterInvestigationState back into the
    same {"properties": [...]} JSON shape cluster_response_validation.py
    already expects.
    """

@dataclass
class SecurityAgentResult:
    case_id: str
    final_decision: dict | None     # {"properties": [...]}, SAME shape Codex produces
    cost_usd: float                 # the only two fields live_runner.py's core loop reads
    # everything below is additive, for our own eval/observability:
    investigation_state: ClusterInvestigationState
    trajectory_path: str
    wall_clock_s: float
    input_tokens: int
    output_tokens: int
    tool_calls: int
    files_inspected: int
    hypotheses_generated: int
    counterexamples_attempted: int
```

Because `final_decision`/`cost_usd` are the *only* two fields the existing
harness reads (confirmed at `live_runner.py:459,462`), this function can be
passed straight into `run_cluster_investigations_live(..., run_arm_g_bundle_fn=
run_security_agent_bundle)` with **zero changes** to `live_runner.py`,
`cluster_response_validation.py`, `context_artifacts.py`, or
`grouping_engine.py`.

---

## 3. Dependency decisions (Phase "Dependency decision")

| Library | Why needed | Replaces/reuses | Essential for V0? |
|---|---|---|---|
| **Pydantic** | Structured, validated `ClusterInvestigationState`/`Hypothesis`/`Evidence`/tool I/O; JSON-schema generation for LLM tool-calling, replacing the fragile fenced-JSON extraction documented in §1.8 | Nothing — this codebase has zero Pydantic **usage** today, all plain dataclasses, though `pydantic==2.13.4` is already resolved in `uv.lock` as a transitive dep (verified live: `.venv/bin/python -c "import pydantic; print(pydantic.VERSION)"` → `2.13.4`) — so this isn't even a new dependency-resolution risk, just new first-party usage | **Yes.** Core to Phases 3/4/6/10's structured-state requirement; isolated to `rtf/security_agent/`, zero risk to existing dataclass-based code elsewhere |
| **LiteLLM** | Task brief suggests it for model-independence | `a4v.llm.ChatClient` already gives this in practice — it's an OpenRouter HTTP client with caching + real cost logging, and OpenRouter itself already fronts every model family we'd want to try (GPT, Claude, GLM, etc.) under one API | **No, not for V0.** Adding LiteLLM on top of an already-working, already-cached, already-cost-logging OpenRouter client is redundant. Revisit only if a specific need arises that OpenRouter/`ChatClient` can't serve (e.g. native provider-side prompt caching control, a local/self-hosted model, or a provider OpenRouter doesn't front) |
| **Tree-sitter** | Task brief names it as optional | Existing source access is a full repo copy + `read_file`/`search_repository`; graph/Slither infra already gives structural navigation once compiled | **No.** No demonstrated gap yet (fast syntax-level nav *without* compilation). Add only if a real investigation need surfaces one — e.g. navigating an uncompilable file |
| **Foundry/Forge** (existing) | Whole-project compilation, real ground truth for the graph | `compile_helper.compile_evmbench_target_via_foundry`, already built and validated | **Reused as-is, essential.** V0 treats it as pre-investigation-only (matches brief Phase 18 — no dynamic verification tool yet) |
| **Slither / `a4v.graph.ProgramGraph`** (existing) | Call graph, state read/write, inheritance — exactly the brief's "do not reimplement" instruction | `a4v/graph.py`, already built, already used both for context-building and (via `graph_mcp_server.py`) as live Codex tools | **Reused as-is, essential.** Our tools call the same underlying functions in-process, skipping the MCP/subprocess layer since we're not a separate process from our own controller |
| **`tenacity`** (existing, transitive via `a4v.llm`) | Retry logic for `ChatClient` HTTP calls | Already a dependency | Reused, no new decision needed |
| Observability (Langfuse/OTel) | Brief suggests as a later target | Project already uses JSON/JSONL logs (`ChatClient._log_tokens`, `live_runner._append_checkpoint`) | **No new dependency for V0.** Design `trajectory.py`'s JSONL schema so it *could* feed an OTel/Langfuse exporter later (one event per model/tool call, structured fields, no free text required to parse it) without committing to either now |

---

## 4. Implementation phases (small vertical increments)

Each increment is independently testable and, except where marked, **$0
real spend**.

0. **State skeleton.** Pydantic models in `state.py` only. Unit tests for
   state transitions (`UNRESOLVED → PASS/FAIL`), shared-evidence-by-id
   access from multiple `RequirementState`s. No LLM, no tools.
1. **Tool layer.** `tools.py` wrapping the existing `ProgramGraph`/Slither,
   tested against the *existing* fixtures already in `agent4vul/tests/
   fixtures/` (`VulnerableBank.sol`, `multi_contract/Vault.sol`) plus new
   Phase-14 synthetic fixtures. No LLM.
2. **Bare-minimum loop.** `kernel.py` wired to `model_client.py`
   (real `a4v.llm.ChatClient`, tiny/cheap model first): read code, decide,
   cite evidence, return PASS/FAIL — no hypotheses/counterexamples yet.
   First point real $ is spent, on a single synthetic fixture, small.
3. **Structured evidence + Claim/Evidence/Interpretation/Verdict
   separation** (brief Phase 10) wired into the loop's final-answer step.
4. **Hypotheses first-class** (Phase 4) + **counterexample-driven
   prompting** (Phase 5) — mostly prompt/loop changes on top of existing
   infra, not new modules.
5. **PASS discipline** (`completion.py`, Phase 9) gating the loop's exit.
6. **`investigator.py`**: wire as `run_arm_g_bundle_fn` into
   `run_cluster_investigations_live` against ONE real cluster from an
   existing `rtf-v2-redesign` run (brief Phase 12's vertical slice) —
   isolates the investigator as the sole experimental variable.
7. **Observability** (`trajectory.py`) — per-cluster JSONL trajectory,
   matching the existing checkpoint/cost-log conventions.
8. **Deterministic + synthetic fixture tests** (brief Phases 13/14) —
   the 7 fixture pairs listed in §2, each asserting the expected verdict
   AND the expected *behavior* (counterexample attempted, cross-contract
   traversal happened), not just the final PASS/FAIL.
9. **Live single-cluster integration test** (brief Phase 15) — small,
   explicit-go-ahead-required real spend, repeated a few times for
   variance, before any larger run.
10. **Codex A/B harness** (`eval/ab_runner.py`, brief Phase 16) — same
    cluster, same context, both investigators, real spend, explicit
    go-ahead required.
11. **Frozen RTF regression** (brief Phase 17) — canto/forte/phi, only
    after 0-10 above show real signal; explicit go-ahead required (these
    are $2-5+ each per the `RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md`
    cost history).

Increments 0-1 (and most of 2-8's code, sans final live tests) are $0 and
can proceed without further check-ins. Increments 9-11 involve real spend
and, per this project's own established convention (every memory of a live
run says "explicit go-ahead needed"), should be confirmed before launching.

---

## 5. Test plan (Phases 13-17, consolidated)

- **Deterministic (Phase 13)**: state transitions, shared-evidence
  reachability across requirements in one cluster, tool schema/error-
  handling/source-location correctness, completion-logic refusal to PASS
  with a mandatory question unresolved, cluster-not-split-into-independent-
  sessions invariant, result-to-property-id mapping correctness. All $0,
  mocked model client (matching this project's own established
  mock-first convention in `live_runner.py`'s own test suite).
- **Synthetic security fixtures (Phase 14)**: the 7 pairs in §2 — cross-
  contract semantic mismatch (fail/ok), missing/present input validation,
  unbounded-growth-with-iteration vs bounded/pruned, access-control
  failure. Provenance-checked the same way RTF v3's own Phase 7 fixtures
  are (grep for banned EVMbench-only identifiers) so nothing here is
  accidentally benchmark-derived.
- **Live-agent (Phase 15)**: small, variance-aware (repeat runs), real
  spend, explicit go-ahead.
- **Codex A/B (Phase 16)**: same cluster/context/repo/model where
  technically possible; compare recall, false-PASS rate, tokens, cost,
  runtime, files/functions inspected, boundary traversals, counterexamples
  attempted, tool calls.
- **Frozen RTF regression (Phase 17)**: canto H-01, forte H-03, phi H-03
  as regression tests only — the kernel's completion/reasoning-shape logic
  is built from generic taxonomy categories (§2.5), never an
  `if canto`/`if H-03` branch. Also re-run known-caught findings to confirm
  no recall regression.

---

## 6. Open questions before implementation proceeds

1. Confirm the `rtf/security_agent/` package location/naming (vs. e.g.
   placing it inside `l8_llm_judgment_layer/` next to the Codex glue it
   parallels).
2. Confirm no objection to adding Pydantic as a new dependency (isolated
   to this package).
3. Confirm which model to use for increments 2+'s first real (cheap) spend
   — this project's convention has been GLM/OpenRouter-routed models for
   cheap iteration, reserving larger spend for later comparison runs.
4. Confirm go-ahead is still required before any increment 9+ real spend
   (assumed yes, per this project's consistent prior convention).
