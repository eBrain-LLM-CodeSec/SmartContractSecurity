# RTF Layer Audit (L0–L12) — 2026-08-06

Direct repository inspection, not a re-read of prior summaries. Status
values: **COMPLETE** (the layer's stated purpose is fully implemented
and verified for the full corpus), **PARTIAL** (implemented for a
subset, or the mechanism exists but a stated sub-scope is missing),
**MISSING** (no implementation exists at all), **BLOCKED** (implementation
exists but cannot proceed further without an external dependency).

| Layer | Status | Scope achieved | Exact files |
|---|---|---|---|
| **L0** Spec Ingestion | COMPLETE | Verbatim EthTrust V3 snapshot, hashed, dated, license-confirmed (Apache 2.0) | `standards/ethtrust/ethtrust-sl.raw.html`, `metadata.json`, `README.md`, `APACHE-2.0.LICENSE.txt` |
| **L1** Requirement Corpus | COMPLETE | 81/81 requirements mechanically parsed (22 S / 24 M / 24 Q / 11 GP), zero dangling cross-refs, 2 real parser bug-fix rounds | `rtf/l1_corpus/parse_spec.py`, `requirement_corpus.json` (+`.sha256`), `PARSING_NOTES.md` |
| **L2** Context Bundles | COMPLETE | 81/81, adaptive-expansion, zero cap hits | `rtf/l2_context_bundles/build_bundles.py`, 81×`.json`, `BUNDLES_NOTES.md` |
| **L3** Applicability | COMPLETE | 81/81 applicability records with `derivation_log_entry` populated on every one | `rtf/track_a/l3_applicability/*.json` (81 files) |
| **L4** Analyzer Matching | COMPLETE for S | 22/22 S-level requirements: 0 `EXACT_MATCH`, 18 `PARTIAL_MATCH`, 4 `NO_MATCH`, real Slither source inspection throughout. **No L4-equivalent pass exists for M/Q** — those layers route straight to L6/L7 classification without a separate analyzer-matching stage (this matches the plan's own architecture: L4 is scoped to "primary Level-S mechanism") | `rtf/track_a/l4_analyzer_mappings/*.json` (22), `L4_NOTES.md`, `S_LEVEL_TRACK_B_SUMMARY.md` |
| **L5** Level S Strategy Compiler | PARTIAL | 22/22 S-requirements have a strategy record; **22/22 also now have real, tested predicate code** for at least their trigger component (this session's predicate work) | `rtf/track_a/l5_level_s_strategy/*.json` (22), `rtf/l5_predicates/predicates.py` (1322 lines), `test_predicates.py` (1033 lines) |
| **L6** Level M Extractor | PARTIAL | 24/24 M-requirements classified (15 `DETERMINISTIC_TRIGGER_SEMANTIC_CONDITION` / 7 `FULLY_DETERMINISTIC` / 2 `FULL_SEMANTIC_REVIEW` / 0 untranslatable); **21/24 have real tested code**, 2 terminal (no predicate possible), 1 pure aggregation | `rtf/track_a/l6_level_m_extraction/*.json` (24), `M_LEVEL_TRACK_B_SUMMARY.md` |
| **L7** Level Q Evidence Assessor | PARTIAL | 24/24 Q-requirements have a rubric record; **8/24 have real tested predicate code** (mostly evidence-collector components), 15 terminal (genuinely need L8 or external evidence), 1 aggregation. **Zero Q requirements have actually been executed against a live repository** — every rubric is `RUBRIC_SPECIFIED_NOT_EXECUTED` | `rtf/track_a/l7_level_q_evidence/*.json` (24), `SCHEMA.md`, `Q_LEVEL_TRACK_B_SUMMARY.md` |
| **L8** LLM Judgment Layer | PARTIAL | Fully built and unit-tested (18/18 `selftest.py`), schema validation, citation-existence checking, second-pass disagreement, stability testing, caching. **Live-validated exactly twice**, against one file (PoolTogether `Vault.sol`), both clear-cut cases (0/5, 0/5 flip rate; 11/11 citation validity) — **never run at scale, never stress-tested on a borderline case** | `rtf/l8_llm_judgment_layer/{schema,citation_check,stability,judgment_layer,selftest}.py`, `live_validation/` |
| **L9** Assumptions Register | PARTIAL | 8 entries logged (4 `OPEN`, 4 `SUPERSEDED`), real deviations captured honestly throughout Track A/B and the predicate-implementation session. **No formal "completeness audit pass" has been run** — entries were logged as found, not swept for systematically |
| **L10** Maturity & Versioning | MISSING | Every one of the 81 requirement records carries a `maturity` field, but **all 81 are uniformly `DRAFT_TRANSLATION`** — no promotion to `RESEARCH_VALIDATED`/`EXPERT_VALIDATED` has ever happened, no `framework_version` field exists on requirement records, and no post-evaluation change-reason enforcement exists as code (only as prose in the plan) | none — no `rtf/l10_*` directory exists |
| **L11** EVMbench Correspondence | PARTIAL | Schema, freeze/hash tooling, and exposure declaration built. **Correspondence mapping covers only the original Track A 6 requirements** (57 records: 33 `DIRECT`/19 `PARTIAL`/5 `CONTEXTUAL`) — 75 of 81 requirements have zero correspondence records | `rtf/l11_correspondence/{CORRESPONDENCE_SCHEMA.md,EXPOSURE_DECLARATION.json,freeze.py,correspondence_mapping.json(+.sha256),L11_PROCESS_NOTES.md}` |
| **L12** Evaluation Harness | PARTIAL *(update: built and run once since this audit was written — see below)* | Orchestrator (`run_rtf.py`), 9 stage-separated metrics, 10-code operational failure taxonomy, executable freeze gate + manifest, and a real first frozen evaluation (2023-07-pooltogether, real DetectGrader score 1/2) all now exist and are tested. **Scope still narrow**: only 56/81 requirements are registry-eligible; only 1 of 46 real EVMbench audits has been run at all; L8 is not wired into the orchestrator yet (every evidence-backed requirement stops at "judgment pending," never reaches a final PASS/FAIL). | `rtf/l12_evaluation/{registry,run_rtf,metrics,failure_taxonomy,freeze_gate,freeze_manifest}.py`, `FROZEN_MANIFEST.json`, `FIRST_EVALUATION_RESULT.json`, `FIRST_EVALUATION_DETECTGRADER_RESULT.json`, `FAILURE_ATTRIBUTION_REPORT.md` |

## Cross-cutting findings from this audit

1. **The single biggest gap is L12, not L11.** Even with a complete L11
   correspondence mapping, there is currently no code that runs RTF's
   predicates against a real EVMbench target end-to-end and produces a
   gradeable output — that machinery does not exist anywhere in this
   repository. Building it is the actual critical-path blocker to a
   first frozen evaluation, not the correspondence mapping.
2. **L4's "no EXACT_MATCH" finding is a real, load-bearing constraint on
   L12's design.** Per the plan's own rule, the absence of `EXACT_MATCH`
   must never be treated as a routing failure when a composed/derived
   strategy exists — and 57/81 requirements do have one. The evaluation
   harness must credit these as valid strategies, not penalize them for
   not being a pure analyzer pass-through.
3. **L8's live validation sample (n=2, both clear-cut) is too small to
   trust for a real evaluation run.** Any frozen run that depends on L8
   for semantic judgment should treat L8's own decisions as provisional
   evidence requiring separate confidence tracking, not ground truth —
   this is exactly the "confidence never substitutes for evidence" rule
   the plan already states, but it has not yet been tested against a
   genuinely ambiguous case.
4. **L11's 6-requirement scope was appropriate for Track A but is now
   the limiting input to L12.** Any metric computed today would only be
   meaningful for those 6 requirements; extending L11 (task #14 below)
   is a genuine prerequisite for a corpus-representative evaluation, not
   optional polish.
5. **The EVMbench infrastructure needed for L12 does NOT require the
   Jubail SLURM/Singularity worker stack.** That stack runs a *different*
   system (the LLM-agent auditor pipeline documented in this project's
   top-level `CLAUDE.md`). What L12 actually needs — real audited
   contracts with ground-truth findings, and the real `DetectGrader` —
   already exists locally and is directly usable:
   `/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench/audits/`
   (40+ real audits) and its own working `.venv` with the grading
   harness's dependencies. `run/task10_real_entry/run_real_grader.py`
   already demonstrates the OpenRouter-backed judge-model wiring this
   project needs to reuse, not reinvent.
