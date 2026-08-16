# RTF v3: preserving the full EthTrust obligation end-to-end

Branch `rtf-v2-redesign` @ `69e70c1` (base for this work). This document is
Phase 1's required trace + the Deliverables-A-H plan, written BEFORE any code
change in this effort, per the task brief's explicit gate. All file:line
citations were read directly from this branch's code this session (two
parallel read-only audits, cross-checked with direct greps — not carried over
from stale memory).

Extends/does not replace: `RTF_V2_ARCHITECTURE.md`, `RTF_V2_WHOLE_PROJECT_
COMPILATION_PLAN.md`, `RTF_V2_COMBINED_PIPELINE_5MISSES_ROOT_CAUSE.md`
("the 5-misses report" below).

---

## A. Current-state architecture (Phase 1 trace)

Two live-reachable pipelines exist today, both real, both still imported:

```
1) LEGACY / single-property path (still imported, still used by
   pilot5_driver.py and standards/routing.py's bundle wiring):

   requirement_corpus.json --normative_text only--> codex_bridge.
   build_codex_prompt_inputs --> pipeline_e2e.py main loop -->
   ARM_G Codex investigation --> resolve_conformance_from_arm_g --> verdict

2) LIVE / grouped RTF-v2 path (used by semantic_only_driver.py /
   run_rtf.py's compile_via_foundry mode -- the one that scored 10/15,
   beating both the old RTF and the simple-Codex baseline):

   requirement_corpus.json (rich: normative_text + explanatory_text +
   exceptions_referenced + overriding_requirements + referenced_requirements
   + enumerated_terms, all parsed by l1_corpus/parse_spec.py:724-761)
       |
       v
   l12_evaluation/registry.py REGISTRY  (per-req_id PredicateSpec list;
   DETERMINISTIC_COMPLETE_REQ_IDS (19) vs AGENT_REQUIRED_REQ_IDS (rest),
   exact-partition-asserted, registry.py:259-292)
       |
       v
   l5_predicates/predicates.py structural predicates (generic Slither-based
   signals, zero EVMbench-target hardcoding -- verified by direct grep)
       |                                    \
       v                                     \  standards/ (GP/ERC generator:
   PropertyMetadata (source_kind="ethtrust")   \  registry.py/discovery.py/
   [l11_investigation_grouping/property_          generator.py --> Generated
   metadata.py:274-297]                           Requirement, models.py:225-
       |                                          249, carries conditions/
       |    <-------- both converge -------->     exceptions as first-class
       v                                          fields)
   live_runner.build_property_pool()
   [l11_investigation_grouping/live_runner.py:41-118]
       |  - clause-splitting (derive_investigations.expand_investigation_
       |    instances) runs UNCONDITIONALLY here (no opt-in flag, unlike
       |    pipeline_e2e.py's instance_expansion_enabled=False default)
       |  - property_metadata.py:279: property_text = focused_clause OR
       |    normative_text (FULL) -- focused_clause is None unless instance
       |    expansion is on, so in the live default config every structural
       |    property carries the FULL requirement text, not a narrowed clause
       v
   [separately, semantic-v2:] semantic_property_generation.py proposes
   properties from protocol_context.md + applicable-standard clauses ONLY --
   NOT anchored to any requirement_id at all (module docstring, system
   prompt lines 49-90 never reference normative_text/explanatory_text).
   property_grounding.py:143 sets property_text=raw.statement,
   source_kind="code_semantics", no parent requirement attached.
       |
       v
   prepare_cluster_investigations() [live_runner.py:121-161]
       |  requirement_context_by_req_id[req_id] = generate_requirement_
       |  context_md(record, explanatory_text=record.get("explanatory_text"))
       |  [context_artifacts.py:179-222]
       v
   generate_requirement_context_md()  <-- THE SINGLE BIGGEST FIDELITY CHOKE
   POINT (finding 1 below): reads only req_id/level/title/normative_text/
   section.secno + optional explanatory_text. No code path for
   exceptions_referenced / overriding_requirements / referenced_requirements
   / enumerated_terms, even though parse_spec.py already extracted all four
   and they sit unused in the same requirement_record dict.
       |
       v
   generate_cluster_plan_md() [context_artifacts.py:225-349]
       |  per property: inlines property_text + source_provenance + a FILE
       |  POINTER to the requirement-context markdown (line 279-281) -- NOT
       |  the full requirement text inlined a second time. Generic (non-
       |  category-specific) "Investigation procedure"/"What would
       |  constitute a violation"/"Evidence required" sections, IDENTICAL
       |  wording regardless of reasoning_category (lines 286-347).
       v
   cluster_prompt.build_cluster_investigation_prompt() -->
   ARM_G_CLUSTER_PROMPT_v1.md (frozen) + 3 file-path pointers. Deliberately
   does NOT restate requirement text inline (by design, to avoid duplicating
   a long spec paragraph per property) -- correctness depends on Codex
   actually opening the referenced file; nothing in the response schema
   requires it to prove it did.
       |
       v
   [Codex investigation, full repo + tool access]
       |
       v
   per-property JSON verdict --> cluster_response_validation.py / codex_
   bridge.resolve_conformance_from_arm_g: gated on counterexample-search
   SUFFICIENCY (reasoning_rigor.py), never on whether the model's reasoning
   actually engaged the full parent requirement text vs. only the narrow
   property/generated-statement it was handed.
```

### Numbered findings (can security meaning be lost at this arrow?)

1. **CONFIRMED, biggest gap.** `generate_requirement_context_md`
   (`context_artifacts.py:179-222`) silently drops `exceptions_referenced`,
   `overriding_requirements`, `referenced_requirements`, `enumerated_terms`
   — all already parsed and present in `requirement_record`. EthTrust's
   "Overriding Requirement" is a first-class spec concept
   (`dfn-overriding-requirement`); an applicable exception is currently
   invisible to every investigator on the live path.

2. **CONFIRMED, two-path fidelity split.** The legacy `codex_bridge.
   build_codex_prompt_inputs` (`codex_bridge.py:41-121`) forwards bare
   `normative_text` only — its own comment (line 98-106) admits
   `explanatory_text` was "deliberately deferred." Still imported by
   `pilot5_driver.py`'s main loop. The live grouped path is richer but
   capped by finding 1.

3. **CONFIRMED, standards/routing.py's `render_generated_requirement_bundle`
   (`routing.py:50-94`) is RICHER than the corpus path** — it explicitly
   renders `conditions`/`exceptions` as their own labeled lines (lines
   71-74). But this function feeds `codex_bridge.build_codex_prompt_inputs`'s
   `bundle_record` param (the LEGACY path, per its own docstring at
   `routing.py:170`), not the live grouped `generate_requirement_context_md`
   path. GP/ERC-generated requirements that flow through
   `semantic_only_driver.build_ethtrust_structural_properties` (the live
   10/15-scoring combined pipeline) get flattened into the same
   `requirement_record` shape as corpus requirements and hit the SAME
   finding-1 choke point — so the richer rendering in `routing.py` is real
   but only reaches the legacy path, not the live one.

4. **CONFIRMED — this is the exact Phi-H-03 root cause, sharpened.**
   `req-3-enough-gas` ("Manage Gas Use Increases... MUST be available to
   work with data structures... that grow over time") is a REAL, PARSED,
   ROUTABLE (`AGENT_REQUIRED`, not deterministic) requirement in the live
   81-req corpus (`registry.py:185`, verified this session). It is NOT
   missing from EthTrust. Its only registered predicate is
   `collect_documentary_and_implementation_evidence`
   (`l5_predicates/predicates.py:52-`) — a generic README/NatSpec-vs-
   implementation DOCUMENTARY evidence collector with **zero code-pattern
   detection for growing persistent structures** (no EnumerableMap/
   EnumerableSet/dynamic-array/queue signal at all). If a target's docs
   never mention gas or growth, this predicate can produce no evidence and
   the requirement is never routed to `_updateCuratorShareBalance` in the
   first place. The 5-misses report's own `REQUIREMENT_TAXONOMY_GAP`
   classification for phi H-03 is therefore **not accurate as stated** — it
   is an `RTF_APPLICABILITY_GAP` (no predicate represents the relevant code
   pattern for an EXISTING, correctly-scoped requirement), exactly the
   failure mode the task brief predicted and explicitly told us not to
   assume without tracing. Fixed in Phase 5 below.

5. **CONFIRMED — Canto H-01 root cause, sharpened.** `req-2-block-data-
   misuse` already has TWO predicates registered
   (`registry.py:95-97`): `find_block_data_usage` AND
   `find_cross_boundary_block_data_argument` — i.e. RTF's own predicate
   layer already anticipated the cross-boundary case and routes on it. The
   5-misses report's own evidence confirms the requirement WAS applied 3x
   to the right function. The miss is purely that the generic investigation
   guidance (`context_artifacts.py:286-347`) never poses the specific
   two-hop question ("does the callee interpret this argument the same
   way") — it asks the same undifferentiated "investigate whether this
   property holds" question for every requirement regardless of shape.
   This is a pure `RTF_TRANSLATION_GAP` / missing requirement-specific
   guidance, fixed in Phase 6, NOT a predicate or applicability problem.

6. **CONFIRMED — Forte H-03 root cause, sharpened.** Semantic-v2 properties
   are NOT anchored to a parent requirement at all (finding above). Forte
   H-03's property almost certainly came from this generator (a
   "correctness" framing, not a "must-reject-invalid-input" framing) with
   no attached EthTrust obligation to check the verdict against. This
   matches the task brief's stated concern exactly, but the mechanism is
   "no parent obligation was ever attached," not "a narrow derived clause
   replaced a rich one" (structural clause-narrowing is present in the code
   as a capability but is OFF by default and not implicated here). Fixed in
   Phase 4 below (anchor every semantic property to a parent EthTrust
   requirement + dual PASS gate) plus Phase 6 (domain-validation-specific
   guidance, generalizing the 5-misses report's own targeted-fix
   recommendation).

7. **No requirement-category-specific investigation guidance exists
   anywhere** (`context_artifacts.py:208-221`, `286-347` — identical text
   regardless of `reasoning_category`). Confirms the brief's Phase 6
   premise directly; root cause for finding 5 and a contributor to finding
   6.

8. **Verdict resolution never checks that the model's reasoning actually
   engaged the parent requirement text vs. only the narrow property**
   (`codex_bridge.py:141-178`, `reasoning_rigor.py`). Structurally, nothing
   currently REQUIRES dual satisfaction (property AND parent obligation).

9. **Negative results, verified, not touched by this plan**: zero EVMbench-
   target-specific hardcoding in `l5_predicates/predicates.py` or
   `l1_corpus/parse_spec.py`. `DETERMINISTIC_COMPLETE_REQ_IDS`/
   `AGENT_REQUIRED_REQ_IDS` partition still exact and current. Grouping
   (`grouping_engine.py`) does not drop or merge requirement identity —
   `Cluster` stores IDs only, full `PropertyMetadata` looked up separately
   downstream, no lossy transform.

---

## B. Root architectural failures (summary)

Three distinct, separable failure classes — matching the task brief's own
taxonomy, now each backed by a specific code citation rather than assumed:

- **B1. Context-assembly under-preservation** (findings 1-3): the corpus
  parser already captures the full EthTrust obligation (explanatory text,
  exceptions, overriding requirements, referenced requirements) but the
  function that renders investigator-facing text drops most of it. This is
  a genuine implementation gap in an EXISTING function, not a missing
  abstraction layer.
- **B2. Applicability/predicate under-coverage for a real class of
  requirements** (finding 4): requirements whose own EthTrust text concerns
  a *pattern over code structure* (growth, bounded lifetime, iteration cost)
  get routed through a generic documentary-evidence collector instead of a
  structural predicate, so applicability silently depends on whether the
  target happens to document the issue.
- **B3. Missing requirement-shape-aware investigation guidance** (findings
  5-8): every requirement, regardless of its normative shape (cross-
  boundary semantic contract, domain validation, resource-growth-over-time,
  access control, ...), receives the same generic "investigate whether this
  holds" instruction. Semantic properties in particular can reach the
  investigator with NO parent obligation attached at all.

None of these three requires a new intermediate requirement language. All
three are fixes to existing functions (`generate_requirement_context_md`,
the predicate registry, `generate_cluster_plan_md`, `semantic_property_
generation.py`) — consistent with the brief's explicit architectural
constraint.

---

## C. Proposed minimal changes

**C1 (Phase 3 — closes B1).** Extend `generate_requirement_context_md` to
render `exceptions_referenced`, `overriding_requirements`,
`referenced_requirements` when present in `requirement_record`, clearly
labeled and visually distinguished from the normative text (so RTF-added
framing is never confused with official EthTrust text — the task's Phase 3
"clearly distinguishable" requirement). Also thread `explanatory_text`/the
same extended fields into the legacy `codex_bridge.build_codex_prompt_
inputs` path (finding 2) since it is still live-reachable via
`pilot5_driver.py`. No schema change needed — `parse_spec.py`'s output
already has everything; this is purely "read more of what's already there."

**C2 (Phase 4 — closes B3 for semantic properties).** Two changes to
`semantic_property_generation.py`/`property_grounding.py`:
(a) every generated semantic property must carry a `parent_requirement_id`
(chosen from applicable-standard clauses it was grounded in, or — new —
allowed to cite a matching corpus `req_id` when the property's own subject
matter maps onto one, e.g. "input domain validation" -> the relevant
Q-level requirement) so it is never fully parentless; (b) when a semantic
property DOES have a parent requirement (structural, or newly-attached per
(a)), `generate_cluster_plan_md`'s per-property block states explicitly:
"PASS requires BOTH (i) this property holds AND (ii) the parent
requirement's full obligation (see linked context file) is not violated by
a narrower framing of the same code" — and `cluster_response_validation.py`
gains a check that a PASS verdict's own stated reasoning references the
parent requirement's normative concern, not only the derived property text
(downgrade to INCONCLUSIVE otherwise, mirroring the existing counterexample-
search-sufficiency downgrade pattern — same mechanism, new check).

**C3 (Phase 5 — closes B2).** Add ONE new generic structural predicate,
`find_unbounded_growth_with_downstream_iteration` (name TBD in code), to
`l5_predicates/predicates.py`: detects (via Slither, generically) a
persistent state variable of a growth-capable container type (dynamic
array, mapping, `EnumerableSet`/`EnumerableMap`, or any user struct wrapping
one) that has a reachable insertion/append path but no corresponding
removal/pruning path reachable from the same or a related function, AND is
read by a loop/enumeration site (a `for`/iterate-all pattern, or a
Slither-detectable full-enumeration call) elsewhere in the same contract or
a contract that imports/inherits it. Register it under `req-3-enough-gas`
AND `req-3-protect-gas` (both already-parsed, already-`AGENT_REQUIRED`
corpus requirements whose text plausibly covers this — verified against
their real `normative_text`, not assumed) as an ADDITIONAL predicate
alongside the existing documentary-evidence one (both continue to run;
either producing evidence is sufficient for applicability — pure recall
increase, no removal of the existing signal).

**C4 (Phase 6 — closes B3 for guidance).** Add a small, requirement-shape
keyed guidance table (not per-benchmark, not per-EVMbench-finding) consulted
by `generate_cluster_plan_md` when rendering the "Investigation procedure"
section, keyed off a NEW derived tag on `PropertyMetadata`/requirement
records (`investigation_shape: Literal["cross_boundary_semantics",
"domain_validation", "resource_growth", "generic"]`), computed from the
requirement's own `reasoning_category` (already exists, see `taxonomy.py`)
plus a small keyword/pattern check against its `normative_text` (e.g.
"external call" + "block.number|block.timestamp" -> cross_boundary_
semantics; "MUST reject|invalid input|out of range|domain" ->
domain_validation; "grow|increase over time|data structures" ->
resource_growth). Each shape gets ~5-8 lines of GENERIC guidance text
(matching the brief's Phase 6 examples verbatim in spirit — block-data
cross-boundary callee-semantics check, domain-invalid-input rejection
check, growth/pruning/iteration-cost check) — no per-benchmark playbook,
no hardcoded contract names.

---

## D. Requirement-conformance design

New `rtf/tests/ethtrust_conformance/` (Phase 7): for each requirement in
the Phase 2 "representative slice" (§ below), one minimal Solidity fixture
pair (`*_vulnerable.sol` / `*_safe.sol`) plus a small deterministic-mode
harness (`run_conformance_check.py`) that runs the SAME `registry.py`
predicates + (mocked LLM) investigation path used in production against
both fixtures and asserts `FAIL` on the vulnerable one, `PASS` (or
correctly `NOT_APPLICABLE` where appropriate) on the safe one. A `--live`
flag allows running the same harness against a real Codex call, kept
separate from CI (per the brief's explicit instruction). Fixtures are
derived from the official requirement text only (documented provenance
comment at the top of each fixture file citing the `req_id` and the exact
clause it targets), never from EVMbench ground truth — this is checked
mechanically by a test that greps fixtures for banned EVMbench-only
identifiers (contract/finding names from any `findings/H-*.md` in the
EVMbench corpus) and fails the suite if any appear.

---

## E. Migration strategy

Phase 2's audit script (`rtf/l12_evaluation/requirement_fidelity_audit.py`,
built after this plan) walks `REGISTRY` + the GP/ERC-generated requirement
families and classifies every requirement into the brief's 4 states
(`UNIMPLEMENTED`/`PARTIAL`/`IMPLEMENTED_UNTESTED`/`CONFORMANCE_PASS`)
mechanically: source-preservation and applicability/routing are checked
against the real registry+corpus (no LLM needed); test existence is
checked by presence of a matching fixture pair + a green conformance run.
Nothing is upgraded to `CONFORMANCE_PASS` without an actual green
end-to-end (possibly mocked) test. This produces the ground truth for
which of the 81+ requirements are genuinely done vs. only "parsed."
Requirements outside the Phase-2 representative slice remain honestly
`PARTIAL`/`IMPLEMENTED_UNTESTED` after this effort — full-corpus fixture
coverage is future work, disclosed as such (§H).

---

## F. Test strategy

- Unit: `generate_requirement_context_md` renders exceptions/overriding/
  referenced text when present (new); legacy `codex_bridge` path parity
  test; semantic property parent-attachment test; dual-PASS-gate downgrade
  test (mocked verdict citing only the narrow property -> downgraded);
  new growth-predicate unit tests (positive: EnumerableMap-append-no-remove
  + iteration; negative: same container WITH pruning; negative: growth
  container never iterated).
- Integration: full `build_property_pool` -> `generate_cluster_plan_md`
  snapshot test asserting the investigation-shape-specific guidance text
  appears only for matching requirement shapes and not others (non-
  applicability check, per the brief's explicit requirement).
- Conformance (Phase 7): synthetic Solidity fixture pairs, deterministic
  mock-LLM mode in CI, `--live` opt-in for real Codex.
- Regression (Phase 9): re-run the EXISTING ~400+ test suite (must stay
  green) plus a code-level (non-live, no paid rerun without explicit
  authorization) walkthrough of whether the Canto H-01 / Forte H-03 / Phi
  H-03 root causes identified in §A are structurally closed by C1-C4 —
  documented honestly, not claimed as a re-graded score without an actual
  rerun.

---

## G. Cost/performance impact

- C1 (context rendering): zero LLM cost change — pure string assembly, runs
  once per req_id (already the case), negligible size increase (exceptions/
  overriding text is typically 1-3 sentences per requirement, only present
  on a minority of the 81 requirements).
- C2 (semantic parent-attachment + dual gate): zero additional LLM calls —
  attachment is a deterministic lookup/keyword match, and the dual-gate
  check is a text-pattern check on the EXISTING verdict response, not a
  second LLM call.
- C3 (new growth predicate): zero LLM cost — pure Slither-based structural
  analysis, same cost class as every existing predicate. May increase
  APPLICABLE-property count (and therefore investigation count/cost) on
  targets with growth-shaped state, which is the intended recall increase;
  bounded by the existing `max_semantic_properties`/cost-ceiling machinery
  already in place, no new unbounded-cost path introduced.
- C4 (guidance text): a few extra lines per cluster-plan markdown, only for
  clusters whose requirement shape matches — negligible prompt-size growth,
  explicitly NOT a global "be more thorough" expansion (brief constraint
  #3).
- Phase 7 conformance suite: $0 in CI (mocked); real cost only under
  explicit `--live` opt-in, never run automatically.

---

## H. Risks

- **Routing explosion**: C3's new predicate is scoped to a specific,
  nameable pattern (growth + no-removal + downstream iteration) and only
  feeds two specific already-corpus requirements — not a blanket "flag all
  EnumerableMap usage" rule. Mitigated by requiring BOTH the no-removal AND
  the downstream-iteration signal (not either alone) before producing
  evidence.
- **False-positive explosion**: the growth predicate can misfire on
  intentionally-unbounded-but-safe patterns (e.g. an admin-only, rarely-
  called enumeration with no gas-limit exposure). This is an applicability/
  recall signal only (feeds "could this requirement matter here"), not a
  verdict — the investigator still has to confirm an actual gas-DoS path
  exists, consistent with the brief's Phase 5 instruction that routing
  should not try to conclusively prove the vulnerability.
- **Prompt-size growth**: bounded by design (C1/C4 both add small, capped
  text blocks; C4 explicitly requirement-shape-gated, not global).
- **Requirement-specific overfitting**: C4's shape table is derived from
  generic Solidity/EthTrust-text patterns (documented provenance per
  guidance block), not from the 5 known misses' specific contract/function
  names — verified by the same banned-identifier check used for Phase 7
  fixtures, applied to the guidance-table source file too.
- **Non-determinism** (Phase 9, phi H-07's own evidence): explicitly out of
  this plan's critical path — documented as a separate, already-known
  reliability question (multi-sample generation + dedup), not conflated
  with the fidelity fixes above.
- **Duplicated structural/semantic investigation**: C2's parent-attachment
  could, in principle, cause a semantic property and its now-linked
  structural sibling to be independently re-investigated for the same
  underlying question. Mitigated by leaving `grouping_engine.py` untouched
  (it already clusters properties sharing a `requirement_id`/state/
  callgraph — parent-attachment makes MORE semantic properties eligible for
  this existing clustering, which is a cost-neutral consolidation, not a
  new duplication source).

---

## Representative first slice (Phase 2 target) — FINAL, as implemented

Phase 2's audit script surfaced `req-3-all-valid-inputs` ("Process All
Inputs" — "Tested Code MUST validate inputs, and function correctly
whether the input is as designed or malformed") as the real corpus
requirement for category 2, better than this document's original
placeholder guess (`req-2-check-rounding`). Final slice, all 6 now
implemented + conformance-tested (Phase 7) — see
`RTF_V3_IMPLEMENTATION_STATUS_REPORT.md` for full results:

1. Block data / semantic-value cross-boundary: `req-2-block-data-misuse`
2. Processing/validating inputs: `req-3-all-valid-inputs`
3. Gas usage with growing data structures: `req-3-enough-gas`
4. Access control: `req-3-access-control` ("Enforce Least Privilege")
5. External calls: `req-2-external-calls`
6. One straightforward static requirement: `req-1-no-tx.origin`
   (`DETERMINISTIC_COMPLETE`, zero-LLM, simplest possible conformance case)
