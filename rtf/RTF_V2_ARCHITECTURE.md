# RTF v2 Architecture: Audit + Redesign

Written at the start of a new session (worktree `rtf-v2-redesign`, branched
from `worktree-mgpr-router2` @ `300c739`). This document is Deliverable #1
of the RTF v2 task: it (A) traces the CURRENT pipeline against real code
(not memory, not the task brief's assumptions), (B) identifies exactly what
the brief asked for that already exists vs. what is a genuine gap, and (C)
lays out the concrete, incremental plan this session implements.

**Headline finding**: RTF has moved substantially since the brief's model of
it. A full second architecture layer, `rtf/l11_investigation_grouping/`
("the grouped-investigation architecture", built across an 11-phase session
on 2026-08-10/13), already implements atomic property metadata, G0-G3
semantic-aware grouping, a semantic reasoning taxonomy, and reusable
Markdown context artifacts (protocol context / requirement context /
cluster plan) — most of what Section 5, 12, and 13 of the task brief ask
for. `rtf/standards/` already implements applicable-ERC discovery with
concrete per-clause obligation derivation — all of Section 7. **The one
genuinely missing piece is Section 8: a stage that proposes NEW candidate
properties from protocol semantics, independent of any pre-existing
EthTrust/ERC requirement text.** Every property in the system today,
without exception, traces back to a `requirement_id` in the 81-item static
EthTrust corpus or a generated ERC clause — confirmed at the exact code
line where this is enforced (see §A.5 below). This is the real "no
predicate/requirement match → no property" ceiling, and it is the sole
focus of RTF v2's new implementation work.

---

## A. Audit: Current Architecture (as of `300c739`)

### A.1 — Where standards are loaded

- **EthTrust static corpus (81 requirements)**: `rtf/l1_corpus/requirement_corpus.json`,
  produced by `rtf/l1_corpus/parse_spec.py` from the raw EthTrust v3 spec
  HTML. Each record: `req_id`, `level` (S/M/Q/GP), `title`,
  `normative_text`, `section` (`{secno, ...}`), `explanatory_text`.
- **ERC specs**: `rtf/standards/registry.py`'s `StandardsRegistry` loads
  pinned, hash-verified spec snapshots from `rtf/standards/erc/<ID>/`
  (`standard.json` + a `clauses.json`, currently ERC-4626 and ERC-20).
  `StandardRecord.local_source_hash` is checked against the on-disk file at
  load time — a tampered/updated snapshot fails loudly, never silently.

### A.2 — Where EthTrust requirements become routable objects

Both static-corpus and generated requirements resolve to the same
`RoutedRequirementResult` (`rtf/l12_evaluation/metrics.py:66`):
`req_id`, `applicability_state` (APPLICABLE/NOT_APPLICABLE/UNKNOWN),
`operational_status`, `conformance_state` (None until resolved),
`evidence: tuple[EvidenceItem, ...]`. Static requirements are routed by
`run_rtf.py`; generated ERC requirements are bridged into the same shape by
`rtf/standards/routing.py`'s `build_standards_routed_requirements` — this
bridge needed **zero changes** to `RoutedRequirementResult` or any of its
downstream consumers (confirmed generic by the original Phase-0 trace, per
memory of that session).

### A.3 — How GP/ERC requirements are represented

`GeneratedRequirement` (`rtf/standards/models.py:226`): one per
`NormativeClause`, `derivation_type=STANDARD_CLAUSE_DIRECT` (1:1
clause→requirement, no composite synthesis today). Full provenance:
`source_family/source_id/source_title/source_url_or_local_spec/
source_version/source_section/normative_strength/parent_requirement_id/
derivation_type/clause_id/obligation_text/conditions/exceptions/
affected_interface/source_text_hash`. Critically, `generator.py`
(`generate_requirements_for_standard`) does NOT stop at "implements
ERC-4626" — it translates each individual normative clause (e.g.
`totalAssets` semantics) into its own `obligation_text`, which is exactly
Section 7's requested behavior ("derive concrete obligations", not treat
standard-applicability itself as the property). This is how
`gp-accepted-standard__erc-4626__erc4626-totalassets-must-include-fees`
already exists as a real, spec-derived (not benchmark-derived) requirement.

### A.4 — How predicates are associated with requirements

Structural predicates (`rtf/l5_predicates/predicates.py`, e.g.
`find_block_data_usage`, `find_cross_boundary_block_data_argument`,
access-control / external-call checks) run over a compiled Slither object
and produce `EvidenceItem`s (`predicate`, `location`, `detail`, optional
`structured` dict). `run_rtf.py` collects these per requirement into
`RoutedRequirementResult.evidence`. A predicate never "creates" a property
directly — it only supplies evidence that a requirement is applicable and
where.

### A.5 — Exactly where "property" objects are created (THE KEY FINDING)

`PropertyMetadata` (`rtf/l11_investigation_grouping/property_metadata.py:48`),
built by `derive_property_metadata`, one per `InvestigationInstance`
(`rtf/l10_property_derivation/derive_investigations.py` — a single
requirement can expand into up to N instances: one per derived clause ×
distinct evidence location, FAIL-wins aggregated back at the end).

The pool of properties for one audit is assembled by
`build_property_pool` (`rtf/l11_investigation_grouping/live_runner.py:41`):

```python
for req_id, result in routed.items():
    if result.applicability_state != ApplicabilityState.APPLICABLE:
        continue
    if result.conformance_state is not None:
        continue
    if not result.evidence or result.operational_status.value != "OK":
        continue
    ...  # only here does a property get created
```

**This loop is the entire universe of property generation in RTF today.**
It iterates *only* over `routed` — i.e. every property traces to a
`req_id` already present in the static 81-corpus or the ERC generator's
output, AND requires non-empty `evidence` (i.e. some structural
predicate/evidence-collector already fired for it). There is no code path
anywhere in the repository that proposes a property NOT anchored to a
pre-existing requirement id. This is the literal, code-level form of the
brief's "no predicate → no property → no investigation" ceiling — it's not
only about structural predicates; it's about the *requirement corpus*
itself being the sole property-generation seed.

### A.6 — `PropertyMetadata`'s existing schema (full field list)

`property_id, requirement_id, requirement_level, requirement_semantic_intent,
property_text, target_contract, target_function, location,
candidate_locations, relevant_files, relevant_symbols,
relevant_state_variables, relevant_types, relevant_constants,
callgraph_neighbors, inheritance_context, reasoning_category,
estimated_complexity, source_provenance, requirement_explanatory_text,
related_out_of_scope_context`. Frozen dataclass; every enrichment field
(`_graph_enrichment`, `_slither_enrichment`) degrades to an empty tuple on
failure, never guesses.

### A.7 — Source locations/functions/files attachment

`parse_contract_function` splits a `"Contract.function"` (or bare
`"Contract"`) location string. `relevant_files` prefers Slither's real
`source_mapping` (`_slither_enrichment`); `_property_target_files` falls
back to the raw `location` string itself when it already looks like a file
path (e.g. `"README.md"`) that Slither never compiled.

### A.8 — Scope filtering

`split_properties_by_scope` / `filter_properties_to_scope`
(`property_metadata.py:281-325`): path-suffix comparison
(`_paths_match`) against the audit's declared `scope_files`. Properties
with no resolvable file target (compiler-config-level checks) are always
kept. `forward_out_of_scope_context` then forwards a dropped property's
`requirement_explanatory_text` to any KEPT property it's callgraph-adjacent
to (built specifically from the canto `LendingLedger`/`GaugeController`
case — see the docstring).

### A.9 — Callgraph representation

`a4v.graph.ProgramGraph`, queried via
`rtf.l8_llm_judgment_layer.graph_navigation.resolve_seed_node` +
`pg.neighbors_by_kind(node, CALLS/EXTERNAL_CALL/STATE_READ/STATE_WRITE, direction=...)`.
`_graph_enrichment` in `property_metadata.py` pulls one-hop
caller/callee/external-call neighbors and state read/write variables —
best-effort, empty on any resolution failure.

### A.10 — G0/G1/G2/G3 grouping

`rtf/l11_investigation_grouping/policies.py` parameterizes the single
generic engine in `grouping_engine.py`:
- **G0_UNGROUPED**: `min_score_to_group=inf` — structurally can never
  merge; reuses the same clustering code path (not a separate branch).
- **G1_CONSERVATIVE**: score threshold + a hard `hard_gate`
  (`g1_hard_gate`: same requirement AND same reasoning_category AND same
  contract — a strict AND the additive score alone can't express).
- **G2_CONTEXT_AWARE**: score-only, generous `max_cluster_size=8` cap.
- **G3_ADAPTIVE**: score-only, dynamic `max_context_size=20` budget
  instead of a fixed count cap.

`compatibility_score` (`grouping_engine.py:54`) is a fully-explainable,
additive score: strong positives (same requirement / same
reasoning_category / same contract / shared state vars / shared types /
shared constants / `shares_callgraph_region` / overlapping candidate
locations), weak positives (file proximity / shared inheritance / shared
symbols), one strong negative (different contracts + literally no shared
context), and a hard veto from `taxonomy.is_unsafe_combination`. **This
already is semantic-aware grouping, not pure callgraph adjacency** — the
brief's Section 12 request is largely satisfied by existing code.

### A.11 — Cluster plans

`generate_cluster_plan_md` (`context_artifacts.py:185`) already produces
almost exactly the brief's Section 13 artifact: objective, why-grouped
(`grouping_reason`), files/components involved, per-property detail
(target, derived property text, EthTrust basis / `source_provenance`,
candidate locations, dependencies, a link to that property's requirement
context file, any forwarded out-of-scope context), a fixed 7-step
investigation procedure, and a required per-property JSON output schema
(`property_id/verdict/evidence/files_read/counterexample_attempt/
counterexample_result/reasoning/vulnerable_location/confidence`). It
**structurally guarantees no expected-verdict leakage** — no code path in
the module reads or writes a PASS/FAIL conclusion. Missing relative to the
brief: an explicit "what would constitute a violation" section and an
explicit "evidence required before reporting" section (currently implicit
in the output schema's `counterexample_*` fields, not named as such).

### A.12 — Exact context reaching Codex

`live_runner.py`'s `_prepare` (per cluster) writes into the agent's
`extra_files`: `.rtf/context/protocol_context.md` (once per audit),
`.rtf/context/requirements/<req_id>.md` (once per distinct requirement in
the cluster), `.rtf/plans/<cluster_id>.md`. `build_cluster_investigation_prompt`
(`cluster_prompt.py`) is a short pointer prompt naming those three file
paths. `run_arm_g_bundle` (`arm_g_codex.py`) then gives the agent a full
repo copy plus graph-navigation MCP tools (`show_candidate`/`investigate`/
`read_source`) as supplementary, never-required aids.

### A.13 — `protocol_context.md`: exists, but structural-only

`generate_protocol_context_md` (`context_artifacts.py:41`) already
produces a real `protocol_context.md`: in-scope contract list, contracts +
inheritance, external entry points, critical state variables, and a
"trust boundaries" section (naming-heuristic only, explicitly caveated as
unverified). **All of it is Slither-derived structural fact — zero
narrative content.** It does NOT cover: protocol purpose, README/NatSpec
summary, roles-beyond-modifier-naming, accounting/fee model, deposit-
withdraw-mint-redeem relationships, lifecycle/state machine, external
protocols/oracles, governance, applicable-ERC-standards section, or
cross-contract relationships. This is the real gap in Section 6 — not
"build protocol_context.md from scratch" but "add the narrative/standards
layer on top of the existing structural layer."

### A.14 — Applicable-standard discovery

`rtf/standards/discovery.py`'s `discover_applicable_standards` is
**entirely data-driven** off each standard's own `detection_signals`
(inheritance / import / natspec / documentation_claim strong signals;
function_signatures / events / known_library_import supporting signals) —
zero standard-specific code. Two real bugs already fixed live (documented
in the module): interface-to-interface inheritance falsely counted as
"implements", and a bare doc claim auto-crediting an unrelated
single-contract compilation unit. This satisfies Section 7 in full,
including the explicit "don't treat 'implements ERC-4626' as the property"
requirement — `generator.py` derives one obligation per clause, not one
per standard.

### A.15 — Investigation outputs → findings

`cluster_response_validation.py`'s `validate_cluster_response` /
`resolve_property_verdicts` parse the cluster's JSON response into
`PropertyVerdict` per `property_id`. `cluster_splitting.py`'s
`detect_split_reason` triggers an automatic cluster split (depth-capped)
on validation failure or budget overrun. `aggregate_properties_to_requirements`
(`live_runner.py:332`) reuses `derive_investigations.aggregate_instance_verdicts`
(FAIL-wins) to roll properties back up to requirement-level verdicts.
`report_generator.py`'s `generate_audit_md` renders one section per FAIL
requirement.

### A.16 — Caching

The L8 bounded-judgment layer's `a4v.llm.ChatClient` already has a real
hash-keyed cache: `_cache_key(messages, temperature, top_p, max_tokens)` →
sha256 → `cache_dir/<key>.json`, plus a `token_log_path` spend log. The
grouped-investigation package's context-artifact generators
(`generate_protocol_context_md`/`generate_requirement_context_md`/
`generate_cluster_plan_md`) are pure, deterministic, cheap string-building
functions — deliberately kept out of the LLM/cache path entirely (no
caching needed; they're byte-identical on identical input by construction,
noted explicitly as required for future prompt-prefix caching).
`pilot5_driver.py` has whole-scope-entry resume via
`entry_XX_*_stage.json`. **There is no cache for anything semantic-LLM-based
in L11 today, because no semantic-LLM stage exists yet** — Phase 5 below
must build one, and the natural choice is to reuse `ChatClient` directly
rather than invent a parallel cache.

### A.17 — Production wiring status (an important caveat)

`rtf/l12_evaluation/pipeline_e2e.py` (the path `pilot5_driver.py` and the
5-audit pilot actually used) has its **own, older**, per-requirement
escalation loop and does **not** call into `rtf/l11_investigation_grouping/`
at all. Only `rtf/l11_investigation_grouping/ablation_driver.py` — a
research harness comparing **Configuration B** (properties left ungrouped,
G0, but using the new context/plan artifacts + cluster-shaped prompt) vs.
**Configuration D** (real grouping, G2_CONTEXT_AWARE, same artifacts) —
wires L11 in, reusing `run_rtf`/`build_standards_routed_requirements` for
the deterministic layer and `live_runner` instead of `pipeline_e2e`'s own
loop for escalation. **L11 is a fully-built, tested, but not-yet-promoted
alternative execution path.** This redesign builds RTF v2's new semantic
stage against the L11/`live_runner` path (the more capable one), not the
older `pipeline_e2e` loop — promoting L11 to the production default is a
separate, pre-existing open question this session does not resolve.

---

## B. What the task brief assumed didn't exist (status table)

| Brief's Section 5-20 request | Real status | Where |
|---|---|---|
| Candidate property schema w/ provenance | **MOSTLY DONE** — `PropertyMetadata` has most fields; missing `source_kind`/`generation_method`/`confidence`/`rationale` as explicit fields (currently folded into free-text `source_provenance`) | `property_metadata.py` |
| Protocol-context extraction (§6) | **PARTIAL** — structural facts done; narrative/standards/accounting/lifecycle layer missing | `context_artifacts.py` |
| Applicable-standard discovery (§7) | **DONE**, including per-clause obligation derivation | `standards/discovery.py`, `generator.py` |
| Semantic property generation (§8) | **NOT DONE** — the one real gap; every property today needs a pre-existing `requirement_id` | (nothing — new work) |
| Property grounding/validation (§9) | **NOT DONE** as a distinct stage (unneeded until §8 exists — existing properties are grounded by construction) | (nothing — new work) |
| Preserve structural predicates (§10) | **DONE**, untouched | `l5_predicates/` |
| Property dedup/consolidation (§11) | **NOT DONE** at the property level (clustering ≈ investigation-time consolidation, but no canonical-property merge) | (nothing — new work, needed once §8 exists) |
| Semantic-aware grouping (§12) | **MOSTLY DONE** — already beyond callgraph adjacency | `grouping_engine.py`, `taxonomy.py` |
| Cluster-plan compilation (§13) | **MOSTLY DONE** | `context_artifacts.py` |
| One Codex/cluster (§14) | **DONE** | `live_runner.py` |
| Property gen ≠ vuln detection (§15) | **DONE** structurally for the existing pipeline (no verdict field anywhere upstream of investigation) — must be preserved for the new §8 stage too | (design constraint for new work) |
| Provenance everywhere (§16) | **DONE** for existing properties; needed for new semantic ones | (extend) |
| Caching (§20) | **DONE** for LLM judgment (`ChatClient`); **NOT DONE** for anything semantic-LLM (doesn't exist yet) | `a4v/llm.py` |
| Observability artifacts (§19) | **PARTIAL** — `.rtf/context/`, `.rtf/plans/` are written; no `applicable_standards.json`/`structural_properties.json`/`semantic_properties_raw.json`/`rejected_properties.json`/`property_clusters.json` dump exists yet | (new work) |

---

## C. RTF v2: concrete, incremental plan for this session

Given how much of the brief is already satisfied, RTF v2's actual scope of
work is narrower than the brief's 11 phases suggest. This session
implements, in order, committing after each:

1. **Schema extension** (`property_metadata.py`): add
   `source_kind: str` (`"ethtrust" | "erc_gp" | "code_semantics"`,
   inferred for existing call sites so old data still round-trips),
   `generation_method: str` (`"structural_predicate" | "standard_clause" | "semantic_derivation"`),
   `confidence: float | None`, `rationale: str`, `grounding_evidence: tuple[str, ...]`.
   All new fields default such that every existing call site and test is
   unaffected (additive, per the frozen-dataclass convention already used
   for `reasoning_category`/`estimated_complexity`).
2. **Protocol-context narrative extraction**: a new deterministic
   (`$0` cost, no LLM) extractor that reads README/NatSpec/interfaces and
   the existing `discover_applicable_standards` output, adding sections
   (Protocol purpose excerpt, Applicable standards + their concrete
   obligations, Accounting-relevant state variables, lifecycle/init
   hints) to what `generate_protocol_context_md` already produces — every
   claim cited to its exact source (file/NatSpec tag/signal_id), never a
   free-form summary. An LLM narrative-synthesis pass is a natural later
   extension but is deliberately deferred (out of scope this session) to
   keep this stage free and reproducible first, matching the module's own
   "facts, never guessed" discipline.
3. **Semantic property generation** (new module): one bounded LLM call
   per audit, fed ONLY the (now-enriched) `protocol_context.md` +
   applicable-standard obligations + a structured contract/function/
   state-variable manifest. Prompted strictly for "what must remain
   true", never "find vulnerabilities" (enforced by prompt template +
   a runtime rejection of verdict-shaped language). Reuses
   `a4v.llm.ChatClient` verbatim for caching (no parallel cache).
4. **Grounding/validation** (new module, deterministic, no LLM): every
   raw semantic property must name contracts/functions/state variables
   that actually exist in the compiled project and cite a real standard
   clause or doc passage; genericity is rejected via a concrete-reference
   requirement (not a banned-phrase blocklist alone). Rejected properties
   are recorded with a reason, never silently dropped. Accepted
   properties become full `PropertyMetadata` objects (synthetic
   `requirement_id`, `requirement_level="SEMANTIC"`) so they flow through
   the *unchanged* grouping/cluster-plan/live_runner pipeline.
5. **Merge + dedup**: combine the existing structural/requirement-derived
   property pool with the new semantic pool before grouping; consolidate
   near-duplicate semantic properties (shared affected state
   variables/functions + property_type overlap) into one canonical
   property rather than one Codex call each.
6. **Observability**: persist `applicable_standards.json`,
   `semantic_properties_raw.json`, `semantic_properties_grounded.json`,
   `rejected_properties.json` per audit run, alongside the existing
   `.rtf/context/`/`.rtf/plans/` artifacts.
7. **Tests**: regression (existing suite must stay green), new unit tests
   for the extractor/generator/grounder (mocked LLM, matching this
   repo's own "mock-tested only, no live calls yet" convention for
   `live_runner`), and a synthetic end-to-end fixture (ERC-4626 vault +
   fee accumulator) verifying a property gets generated and grounded with
   no hand-written "bad totalAssets" predicate anywhere in the new code.

**Explicitly deferred, not attempted this session**: any live/paid Codex
run, and Section 18's re-evaluation of previously-missed EVMbench entries
(totalAssets/fee accounting, gauge accounting, Canto arithmetic) — these
require real spend and, per this project's established convention
(see prior session memory), an explicit user go-ahead before launching.

---

## D. Status: what this session actually implemented

Everything in section C's plan (1-7) was implemented, committed
incrementally, and is regression-tested (full `l11_investigation_grouping`
+ `standards` + `l5_predicates` suites green after every commit). Concrete
new modules, all under `rtf/l11_investigation_grouping/`:

- **`property_metadata.py`** (extended, not replaced): `PropertyMetadata`
  gained `source_kind`, `generation_method`, `confidence`, `rationale`,
  `grounding_evidence` — all additive, defaulted, inferred automatically
  for every existing EthTrust/ERC call site.
- **`protocol_context.py`** (new): deterministic, `$0`-cost narrative
  extraction — protocol purpose (cited README excerpt), applicable
  standards + their concrete per-clause obligations (wires
  `rtf.standards.discovery`/`generator`), accounting-relevant state
  variables, lifecycle/initialization signals. `generate_enriched_
  protocol_context_md` composes this with the existing structural artifact
  as a strict superset.
- **`semantic_taxonomy.py`** (new) + 3 new `taxonomy.ReasoningCategory`
  members (`STATE_CONSISTENCY`, `LIFECYCLE_INITIALIZATION`,
  `TOKEN_SEMANTICS_CONFORMANCE`): maps the task brief's 12-value
  `property_type` vocabulary onto the existing grouping-engine key, so
  semantic properties group through the unchanged engine.
- **`semantic_property_generation.py`** (new): the one genuinely new LLM
  stage — one bounded, cached (`a4v.llm.ChatClient`) call per audit,
  proposing "what must remain true" only. Any verdict-shaped key
  (`verdict`/`vulnerable`/`pass`/`fail`/`severity`/`exploit`/...) in a
  response entry is rejected outright, never stripped and kept.
- **`property_grounding.py`** (new): deterministic (no LLM) grounding —
  every affected contract/function/state-variable must exist in a real,
  Slither-derived `ProjectManifest`; the statement must concretely name
  one of them; generic statements (the brief's own 3 literal banned
  examples, tested verbatim) are rejected. Accepted properties become
  full `PropertyMetadata` (`source_kind="code_semantics"`) — the same
  object structural properties use. Also: `deduplicate_semantic_
  properties`/`merge_property_pools` (Phase 7 consolidation).
- **`semantic_pipeline.py`** (new): orchestration
  (`build_full_property_pool`) + Section 19 observability
  (`write_observability_artifacts` — `applicable_standards.json`,
  `structural_properties.json`, `semantic_properties_raw.json`,
  `semantic_properties_grounded.json`, `rejected_properties.json`,
  `property_clusters.json`).
- **`context_artifacts.py`** (extended): `generate_cluster_plan_md` gained
  "What would constitute a violation" and "Evidence required before
  reporting a finding" sections, placed *after* `## Required output
  schema` specifically so the pre-existing `test_cluster_plan_never_leaks_
  an_expected_verdict` structural guarantee still holds (verified, not
  just assumed).

**Test coverage added**: 96+ new tests across 6 new/extended test files —
real Slither compilation throughout (no mocked compilation), zero real
LLM calls (a fake `chat_client` matching `live_runner.py`'s own established
mock-first convention). Includes the brief's Section 17-G synthetic
end-to-end scenario verbatim: an ERC-4626-shaped vault with a fee
accumulator, no hand-written "bad totalAssets" predicate anywhere in the
new code, still produces a grounded `source_kind="code_semantics"`
property naming both `totalAssets`/`accruedFees`, and that property is
shown (via the real grouping engine, not asserted by fiat) to cluster
with a state-sharing structural property while staying separate from an
unrelated one.

**Deliberately NOT done this session** (see the task brief's own Section
21 phasing and Section 18's explicit sequencing — architecture and
synthetic tests first, benchmark evaluation only after, and only with
authorization given the real cost):
- Any live/paid LLM or Codex call — the semantic generator has never been
  invoked against a real OpenRouter endpoint; every test uses a fake
  `chat_client`. The prompt/schema is real and complete, but unvalidated
  against actual model output quality/parsing edge cases a live call
  might surface.
- Wiring `build_full_property_pool`/`semantic_pipeline` into
  `pilot5_driver.py`/`ablation_driver.py`'s actual driver scripts — this
  session built and tested the stage in isolation; connecting it to a
  real per-audit run (own cost, own ceiling, own explicit go-ahead) is a
  distinct next step.
- Section 18/11's re-evaluation of the previously-missed EVMbench entries
  (totalAssets/fee accounting on real liquid-ron, gauge accounting,
  Canto). Requires real spend; not attempted without explicit
  authorization, per this project's established convention.
- A live A/B comparison of grounding thresholds (the `0.3` dedup-Jaccard
  cutoff, the concrete-reference/banned-phrase grounding rules) against
  real LLM output — calibrated only against the hand-written test
  fixtures in this session, honestly disclosed as a starting default (same
  caveat `policies.py` already applies to its own cluster-size/context-
  budget defaults), not an experimentally-tuned value.
