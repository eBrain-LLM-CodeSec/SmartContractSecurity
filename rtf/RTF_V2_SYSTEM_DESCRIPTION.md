# RTF v2: System Description

A standalone reference for how RTF v2 works and how it's put together —
complements `RTF_V2_ARCHITECTURE.md` (which is the audit-plus-phased-
implementation-log) and the `RTF_V2_LIVE_VALIDATION_*.md`/
`RTF_V2_5ENTRY_COMPARISON_REPORT.md` docs (which report real run
results). This document describes the system itself: what it does, how
its pieces fit together, and where it currently ends.

---

## 1. What RTF v2 is, in one paragraph

RTF (Requirement Translation Framework) audits one Solidity entry file
at a time and produces investigated, evidence-backed security findings.
The original architecture only ever investigated a property if some
EthTrust/ERC requirement's own text already anticipated the question AND
a deterministic structural predicate had fired evidence for it — a hard
recall ceiling for anything the standards corpus wasn't written to ask
about (accounting invariants, cross-function state consistency,
protocol-specific business logic). RTF v2 adds a second, independent
property source — semantic property generation grounded in the
protocol's own code and documentation, with no dependency on any
predicate matching — and merges it into the same downstream
grouping/investigation/grading pipeline the original architecture
already had, so nothing else has to change to consume it.

---

## 2. Two generations of scaffolding coexist in the repo

The very first RTF design used a numbered L0–L12 layer scheme
(`AUDIT_L0_L12.md`, now a stale snapshot), built around translating each
of 81 EthTrust requirements through an analyzer-matching/strategy-
compiler pipeline under `rtf/track_a/`. **That scheme is legacy — not on
the live execution path.** Two later redesigns (an "agentic architecture"
pass, then a "grouped-investigation architecture") replaced it. RTF v2
(this session's work) extends the grouped-investigation architecture; it
does not touch `track_a/` at all.

| Directory | Role today |
|---|---|
| `rtf/l1_corpus/` | **Live.** EthTrust spec → 81-requirement corpus |
| `rtf/l2_context_bundles/` | Legacy — bundle-building for the old per-requirement L8 judgment path |
| `rtf/track_a/` (L3/L4/L6/L7) | **Dead.** Superseded prototype, kept for history |
| `rtf/l5_predicates/` | **Live.** Deterministic structural predicates + `compile_helper.py` |
| `rtf/l8_llm_judgment_layer/` | **Live, repurposed.** No longer a bounded pre-Codex gate (removed in the agentic-architecture redesign) — now houses `graph_navigation.py` and the real Codex runners (`arm_g_codex.py` for cluster investigations, `arm_c_codex.py` for the single-shot baseline) |
| `rtf/l9_assumptions_register/` | Running deviation log |
| `rtf/standards/` | **Live.** Not numbered — the generic GP/ERC requirement generator, added after the original L-scheme |
| `rtf/l10_property_derivation/` | **Live.** Per-requirement instance expansion |
| `rtf/l11_correspondence/` | Legacy — EVMbench correspondence mapping, only covers 6 of 81 original requirements |
| `rtf/l11_investigation_grouping/` | **Live, and where all of RTF v2 lives.** The grouped-investigation architecture plus every new module this session added |
| `rtf/l12_evaluation/` | **Live.** Orchestration, grading, reporting |

---

## 3. The core idea: two property sources, one shared pipeline

```
EthTrust corpus (81 reqs)          Protocol code + docs (README, NatSpec,
        +                          interfaces, compiled contracts)
ERC/EIP clauses (rtf/standards/)              │
        │                                     ▼
        ▼                          protocol_context.md (deterministic,
 structural predicate fires         $0 cost) + ProjectManifest (real
 (rtf/l5_predicates)                 contract/function/state-var names)
        │                                     │
        ▼                                     ▼
 derive_property_metadata          semantic_property_generation.py
 (existing, unchanged)             (ONE bounded LLM call, cached)
        │                                     │
        │                                     ▼
        │                          property_grounding.py
        │                          (deterministic, no LLM: reject
        │                           hallucinated refs, generic
        │                           statements, unjustified claims)
        │                                     │
        └──────────────┬──────────────────────┘
                        ▼
              PropertyMetadata (same type, both sources)
                        │
              merge_property_pools + deduplicate_semantic_properties
                        │
              split_properties_by_scope (audit's declared scope.txt)
                        │
              grouping_engine.py (G0-G3 policies, unchanged)
                        │
              context_artifacts.py (protocol_context.md /
              requirement_context.md / cluster_plan.md, unchanged
              generator, new content)
                        │
              ONE real Codex investigation per cluster
              (arm_g_codex.py, unchanged)
                        │
              cluster_response_validation.py + auto-split-on-failure
              (unchanged)
                        │
              PropertyVerdict per property
                        │
              render_semantic_findings_md → audit.md → DetectGrader
```

The single most important architectural property: **a semantic
property and a structural property are the exact same Python type**
(`PropertyMetadata`), differing only in two new fields
(`source_kind="code_semantics"`, `generation_method="semantic_derivation"`)
and a synthetic `requirement_id`. Every downstream stage — grouping,
context generation, investigation, verdict resolution — needed **zero**
changes to accept semantic properties. This was a deliberate design
choice (extend the existing schema, don't build a parallel one) and it's
why RTF v2 could be built incrementally without destabilizing the
existing structural pipeline.

---

## 4. Stage-by-stage detail

### 4.1 Protocol-context extraction — `rtf/l11_investigation_grouping/protocol_context.py`

Deterministic, $0 cost, no LLM. Compiles the entry file with Slither,
then extends the pre-existing `generate_protocol_context_md` (structural
facts: in-scope contracts, inheritance, entry points, state variables,
a naming-heuristic "trust boundaries" section) with new narrative
sections:

- **Protocol purpose** — the first real descriptive paragraph of the
  project's own README (skipping headings/badges), quoted verbatim with
  a citation, or an explicit "not available" if none exists. Never
  synthesized.
- **Applicable external standards + their concrete obligations** — wires
  `rtf/standards/discovery.py`'s detection plus `generator.py`'s
  clause-level translation, so this section names *specific* obligations
  (e.g. the exact ERC-4626 `totalAssets`-must-include-fees clause text),
  not just "implements ERC-4626."
- **Accounting-relevant state variables** — a naming heuristic (`fee`,
  `asset`, `share`, `balance`, `supply`, `debt`, ...), explicitly
  caveated as not a correctness claim.
- **Lifecycle/initialization signals** — naming/inheritance heuristics
  (`Initializable`, `Pausable`, `initializer` modifier), same caveat.

Known limitation, found live: `ProjectManifest.from_slither` (used both
here and for generation) reads Slither's `functions_declared`/
`state_variables_declared`, which are a contract's own *directly
declared* members only. A pure base contract used only via inheritance
(or an inherited-but-never-overridden method) is invisible under the
derived contract's name. Confirmed this doesn't cause incorrect
grounding in practice (the generator/grounder still succeed via a
different real reference the property also names), but it does mean the
generator can't itself *propose* a property naming only an
inherited-only method.

### 4.2 Semantic property generation — `semantic_property_generation.py`

One bounded LLM call per audit. Input: the enriched `protocol_context.md`
plus a `ProjectManifest` (every real contract/function/state-variable
name). Output: up to N `RawSemanticProperty` objects (`statement`,
`property_type`, `rationale`, `affected_contracts/functions/
state_variables`, `source_refs`, `confidence`).

**The one non-negotiable discipline, enforced structurally, not just by
prompt wording**: the model is asked *only* "what must remain true" —
never "find vulnerabilities." Any response entry carrying a verdict-
shaped key (`verdict`, `pass`, `fail`, `vulnerable`, `severity`,
`exploit`, `confirmed`, ...) is rejected outright at parse time, before
grounding ever sees it — a generator that tries to render a finding
instead of a property produces zero usable output, not a
stripped-down one.

Caching: reuses `a4v.llm.ChatClient`'s own hash-keyed cache
(sha256 of model + messages + temperature) — no parallel cache built.
Identical `protocol_context.md` content (same `audit_id`, same scope)
produces a cache hit on rerun; a different `audit_id` or scope changes
the first line of `protocol_context.md` and therefore the cache key,
so it's a fresh, real call — this is by design, confirmed live (a
second liquid-ron generation call with a different `audit_id` label
produced a genuinely independent sample rather than replaying the
cached one).

### 4.3 Grounding — `property_grounding.py`

Deterministic, no LLM — a proposed property is rejected here for
concrete, greppable reasons, never a bare "rejected":

- `ungrounded_reference:...` — an affected contract/function/state-
  variable name isn't in the real `ProjectManifest`.
- `no_concrete_target_named` — nothing affected was named at all.
- `generic_banned_statement:...` — matches one of a small set of
  literal banned patterns ("should not lose money", "should be secure",
  "accounting should be correct", and close variants) as defense in
  depth.
- `statement_not_concretely_grounded` — every referenced name is real,
  but the statement's own prose never names any of them (technically
  real targets, generic text).
- `insufficient_grounding_evidence` — no rationale and no source
  citation at all.

Accepted properties become full `PropertyMetadata`
(`source_kind="code_semantics"`), with `grounding_evidence` recording
exactly what justified acceptance (source refs + which affected
function/state-variable references were verified).

### 4.4 Deduplication and merge — `property_grounding.py` + `semantic_pipeline.py`

`deduplicate_semantic_properties` consolidates near-duplicate semantic
properties — same `reasoning_category`, at least one shared affected
state variable, and word-Jaccard similarity ≥0.3 on the statement text
(calibrated against realistic paraphrases of the same underlying
concern, not against a synthetic worst case) — into one canonical
property, folding the others' phrasing into
`requirement_explanatory_text` rather than discarding them.
`merge_property_pools` then concatenates the (unchanged) structural pool
with the deduplicated semantic pool into one list — this is the entire
merge; nothing else needs to happen because both are the same type.

### 4.5 Scope filtering — `property_metadata.py` (existing, reused)

`split_properties_by_scope` drops properties whose only resolvable file
target falls outside the audit's declared `scope_files` (its real
`scope.txt`, not a heuristic) — the exact same function/mechanism the
structural pipeline's `ablation_driver.run_config_entry` already used,
now driven from `semantic_only_driver.run_semantic_investigation`'s own
`scope_files` parameter (added this session; defaults to just the entry
file if omitted, reproducing prior behavior exactly).
`forward_out_of_scope_context` still forwards a dropped property's
explanatory text to any kept property it's callgraph-adjacent to.

### 4.6 Grouping — `grouping_engine.py` + `taxonomy.py` (existing, extended)

Unchanged clustering mechanism: `compatibility_score` is an additive,
fully-explainable pairwise score (same requirement / same
`reasoning_category` / same contract / shared state variables / shared
types / shared constants / shared callgraph region / overlapping
candidate locations as strong positives; file proximity / shared
inheritance / shared symbols as weak positives; unrelated contracts with
zero shared context as a negative), with a hard veto for unsafe category
pairs. `cluster_properties` does deterministic greedy agglomerative
merging. Four named policies (G0 ungrouped / G1 conservative hard-gate /
G2 context-aware / G3 adaptive budget) parameterize the same engine.

Extension this session: three new `ReasoningCategory` values
(`STATE_CONSISTENCY`, `LIFECYCLE_INITIALIZATION`,
`TOKEN_SEMANTICS_CONFORMANCE`) for property shapes the 81-requirement
corpus has no clause for, plus `semantic_taxonomy.py`'s mapping from the
generator's 12-value `property_type` vocabulary onto this same enum (9
direct mappings, 3 deliberately under-specified types fall back to the
existing keyword categorizer applied to the property's own text). A
semantic property clustering correctly with a structural one that shares
real state is verified by a real integration test (not just asserted) —
confirmed live on the real liquid-ron target too, where 8-10 generated
properties per run consistently clustered into 1-2 substantive groups
for genuine, inspectable reasons (shared state variables, same contract,
same category), not by accident.

### 4.7 Context artifacts — `context_artifacts.py` (existing, one extension)

Three Markdown artifacts, unchanged generation mechanism:
`protocol_context.md` (once per audit), `requirement_context.md` (once
per distinct requirement/property source in a cluster — for a semantic
property this renders the synthetic `"SEMANTIC"`-level "requirement" from
the property's own `property_type`/statement, via the same fallback path
already used for GP-generated requirements without a static corpus
record), `cluster_plan.md` (per cluster: objective, why grouped, files/
components, per-property detail, a fixed 7-step investigation procedure,
the required JSON output schema).

Extension this session: `cluster_plan.md` gained "What would constitute
a violation" and "Evidence required before reporting a finding"
sections — added *after* the output schema specifically, because the
existing `test_cluster_plan_never_leaks_an_expected_verdict` guard
forbids PASS/FAIL tokens anywhere before that section, and the new text
legitimately needs to name the schema's own verdict values.

### 4.8 Investigation — `arm_g_codex.py` + `live_runner.py` (existing, unchanged)

One real Codex subprocess per cluster: a full disposable copy of the
repo, `--dangerously-bypass-approvals-and-sandbox` (the only mode that
works on this kernel), graph-navigation MCP tools available as
supplementary aids, never a precondition. `run_cluster_investigations_
live` handles concurrency (`max_concurrent_investigations`), a cost
ceiling, and automatic splitting: if a cluster's response fails
validation or the investigation times out, the cluster is halved and
each half is re-enqueued (up to `max_split_depth`, default 2). A
property still unresolved after the split budget is exhausted resolves
to `INCONCLUSIVE` with an explicit reason — never silently dropped, but
also never actually investigated. This exact mechanism is what caused
one confirmed real miss (below).

### 4.9 Verdict resolution and reporting

`cluster_response_validation.py` parses the cluster's JSON response into
one `PropertyVerdict` per property. `semantic_pipeline.
render_semantic_findings_md` (new this session) renders every
FAIL-resolved property into `audit.md`-shaped Markdown — one section per
FAIL, using only the investigator's own evidence/reasoning/
vulnerable-location text, PASS/INCONCLUSIVE properties omitted (matching
the existing structural pipeline's `report_generator.generate_audit_md`
convention) — ready for the real `DetectGrader`.

### 4.10 Observability — `semantic_pipeline.write_observability_artifacts` (new)

Every stage's output is a real artifact: `applicable_standards.json`,
`structural_properties.json`, `semantic_properties_raw.json` (everything
proposed, before grounding), `rejected_properties.json` (split into
`rejected_generation` — basic shape/discipline failures — and
`rejected_grounding` — shape-valid but ungrounded, each with a reason
string), `semantic_properties_grounded.json`, `property_clusters.json`.
This isn't decorative — it's what made it possible to trace two real
misses (in a live 5-target comparison) to their exact failure stage
(an investigation timeout vs. a compound/ambiguous property statement)
rather than reporting an undifferentiated "RTF missed it."

---

## 5. Entry points

- `rtf/l12_evaluation/pilot5_driver.py` / `pipeline_e2e.py` — the
  **older**, structural-only production path. Never updated to call the
  semantic layer.
- `rtf/l11_investigation_grouping/ablation_driver.py` — the B-vs-D
  research harness (grouped vs. ungrouped), structural-only, predates
  RTF v2.
- `rtf/l11_investigation_grouping/semantic_only_driver.py` —
  **`run_semantic_investigation`, built this session**: the first driver
  that actually runs generation → grounding → clustering → real
  investigation end to end. Semantic-only by default; accepts an
  externally-computed `structural_properties` list to merge in, but no
  driver currently computes that list and calls this one in the same
  run — **a true combined structural+semantic production driver does
  not exist yet.** This is the largest remaining integration gap.

---

## 6. What's been validated live, and what hasn't

**Validated, with real evidence, not just architecture review:**

- Generation + grounding alone: $0.004–$0.01 per call, consistently 0
  rejections on well-formed real model output across multiple runs.
- Full pipeline including a real Codex investigation, on a synthetic
  fixture: 4 correct FAIL / 3 correct PASS, each with genuine
  counterexample reasoning, $0.20 total.
- Full pipeline against the real `2025-01-liquid-ron` target: an
  independently-generated property whose FAIL verdict traces to the
  exact mechanism historically described as H-01 (operator-fee
  accrual not excluded from `totalAssets()`), $1.64, no ground-truth
  access during generation.
- A 5-target comparison against a single-shot Codex baseline
  (`2026-01-tempo-feeamm`/`2024-01-canto`/`2025-04-forte`/
  `2024-08-phi`/`2025-01-liquid-ron`): baseline won in aggregate
  (6/15 vs. 2/15), but RTF v2 independently caught `canto`'s H-01 — the
  exact bug class the **pre-v2** architecture scored 0/2 on historically
  due to a documented EthTrust-corpus coverage gap. Two real misses were
  root-caused to specific, fixable causes: an investigation timeout at
  max split depth (not a coverage/reasoning gap — the correct property
  was generated and grounded, its cluster just never finished within the
  timeout), and a compound/ambiguous property statement on a rerun of
  liquid-ron that diluted an otherwise-correct investigation into a
  real-but-non-graded finding.

**Not yet validated:**

- Whether a combined structural+semantic run (not yet wired into any
  driver) changes the aggregate picture.
- Generalization beyond these small targets to larger, noisier real
  audits.
- Whether the grounding/dedup thresholds (0.3 Jaccard, the concrete-
  reference rule) hold up against a broader distribution of live model
  output across more targets/models than tested so far.

---

## 7. Deliberate non-goals (per this project's own standing rules)

- Never derive a property, predicate, or threshold from an EVMbench
  ground-truth finding — grading happens strictly after generation, to
  measure, never to justify a design choice.
- Never let the property-generation stage itself render a verdict —
  enforced structurally (verdict-shaped keys rejected at parse time),
  not just requested in the prompt.
- Never treat "a property was generated" as evidence of a
  vulnerability — grounding and investigation are separate, required
  steps; a generated property is a question, not a finding.
