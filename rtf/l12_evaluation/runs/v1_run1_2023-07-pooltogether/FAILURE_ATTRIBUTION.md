# L12 Failure-Attribution Report — First Frozen Evaluation

**Run:** 2023-07-pooltogether Vault.sol, frozen at git commit `95c4f88`
(`FROZEN_MANIFEST.json`). Raw data: `FIRST_EVALUATION_RESULT.json`,
`FIRST_EVALUATION_DETECTGRADER_RESULT.json`. Per the plan's operational-
failure discipline (`failure_taxonomy.py`), this report separates *why*
each gap happened, not just *that* one happened — an infrastructure
limitation, a routing miss, and a genuine framework-quality gap are
different findings requiring different fixes, and conflating them would
misattribute blame.

## Headline numbers

- 56/56 requirements evaluated, **0 operational failures** (0 compile/
  environment/analyzer/parser crashes during the actual scored run).
- 2/2 real graded findings for this audit (H-02, H-04) — both had L11
  DIRECT correspondence, both were correctly routed.
- Real `DetectGrader` score: **1/2** (H-04 detected, H-02 not detected).

---

## 1. Routing failures

**None.** Both requirements with a DIRECT ground-truth mapping
(`req-3-access-control` for H-04, `req-3-all-valid-inputs` for H-02)
were correctly marked `APPLICABLE` by RTF's L3 layer
(`requirement_routing_recall: 2/2`). Zero unjustified `APPLICABLE`
routings could be checked against ground truth either, since this audit
has no known FALSE ground-truth-absent case in its 2-finding scope — see
§5 for why this can't be extended to a true false-positive rate yet.

## 2. Downstream analysis failures (evidence collected, but incomplete/wrong)

**One real, honestly-attributable case: H-02's localization miss.**
`req-3-all-valid-inputs` correctly fired with evidence
(`evidence_collection_recall: 2/2` — evidence WAS collected), but none
of that evidence named the real vulnerable location. H-02's actual fix
(`patch/H-02.diff`) touches `Vault._mint`, `Vault._burn`, and
`Vault._transfer` — all **internal** function overrides.
`find_unvalidated_function_parameters()` only scans **public/external**
functions (a documented scope choice in its own docstring, not a bug —
see `rtf/track_a/l7_level_q_evidence/req-3-all-valid-inputs.json`'s
`implementation_status`). The predicate correctly found the causal ENTRY
POINT (`Vault.withdraw`, which triggers the eventual truncation) but
never the internal function where the actual unsafe cast lives.

**This does not fit cleanly into any single `OperationalStatus` code**,
which is itself a real, worth-noting finding about the taxonomy: the
predicate did not crash, was not blocked by a tool limitation, and did
route correctly — it simply has a scope boundary (public/external only)
that this specific vulnerability falls outside of. This is closest in
character to `EVIDENCE_COLLECTION_FAILURE`'s spirit (partial evidence)
but is better described as a **predicate coverage/precision gap** — a
distinct fourth category the taxonomy does not currently name
explicitly. Recorded here rather than forced into an ill-fitting code.

## 3. Tooling/infrastructure failures

**Zero during the scored run itself** (`0 operational failures` across
all 56 requirements) — but two real infrastructure obstacles were
overcome to get here, both logged in the Assumptions Register and worth
restating in a failure-attribution context since they represent real
fragility in the current setup, not permanently resolved:

- **AR-009**: `forge`/Foundry cannot run on this HPC node (GLIBC
  mismatch, confirmed via a real install attempt). The entire compile
  path for real, multi-file EVMbench targets depends on the workaround
  in `compile_evmbench_target()` (explicit remapping collection + a
  Foundry-free `cwd`) — this is real, load-bearing infrastructure this
  evaluation depends on, not a one-off inconvenience already behind us.
- A Slither IR-generation limitation on `TierCalculationLib.getTierOdds`
  (`'NoneType' object has no attribute 'parameters'`) appeared on every
  compile of this specific target. It did not affect this run's scored
  requirements, but is a real per-target risk: a future target where a
  scored requirement's evidence collection walks through a function
  Slither cannot generate IR for would show up as a false
  `ANALYZER_CRASH` or silently-incomplete evidence, not clearly
  attributable to this specific known limitation unless checked for
  explicitly per-target (this run did not build that check).

## 4. Evidence limitations (structural, not defects)

**The single largest limitation in this run: L8 was never invoked.**
`run_rtf.py` deliberately stops at evidence collection — every
requirement with evidence has `conformance_state = None` ("judgment
pending"), by design (see `run_rtf.py`'s own module docstring). This
directly explains `final_finding_recall: 0/2` — it is **not** a
detection failure, it is an accurate reflection that this specific run
never asked the question L8 exists to answer. Any future run that wires
L8 in will change this number substantially, and it should not be
compared against `final_finding_recall` numbers from a run that DID
invoke L8, without accounting for this.

`inconclusive_rate` and `insufficient_evidence_rate` are both `0/38` for
the same underlying reason — these states are only reachable through
L8's judgment or a `DETERMINISTIC_COMPLETE` unconditioned-prohibition
resolution, neither of which produced an INCONCLUSIVE/INSUFFICIENT_
EVIDENCE result for this specific target's applicable requirements.

## 5. EthTrust coverage gaps

- Of 81 total requirements, only **56 (69%)** have any implemented
  predicate at all (see `rtf/l12_evaluation/registry.py` /
  `rtf/AUDIT_L0_L12.md`) — 25 requirements could not have fired
  regardless of what this target actually contains.
- Of those 56, **38 (68%)** fired as `APPLICABLE` for this specific
  target — the other 18 correctly resolved `NOT_APPLICABLE` (the
  relevant construct is genuinely absent, per each requirement's
  `is_unconditioned_subject` status) rather than being a coverage gap.
- **This audit has exactly 2 GRADED ground-truth findings.** PoolTogether's
  real audit surfaced many more LOW/informational issues (see
  `findings/incorrect/`, `low_hints.md`) that are not part of the
  scored vulnerability set — meaning `requirement_routing_precision:
  2/38 (5%)` cannot be read as "95% false positive rate": most of the
  36 other `APPLICABLE` requirements may correspond to real (if
  unscored) issues, real-but-benign code patterns, or genuine noise —
  this run has no way to distinguish those three without either L8
  judgment or a broader ground-truth set than this audit's 2 scored
  findings provide.

## 6. EVMbench findings with no justified EthTrust mapping

**None for THIS audit** — both of `2023-07-pooltogether`'s real graded
findings (H-02, H-04) have a DIRECT L11 correspondence record. This is
not because EthTrust happens to cover this audit unusually well; it's
because L11 correspondence work was specifically extended to cover
exactly these 2 findings in this session (see
`rtf/l11_correspondence/L11_PROCESS_NOTES.md`'s extension section).

**This is the report's most important scope caveat**: the EVMbench
corpus has **46 audit directories**. Every finding in the other **44
un-reviewed audits** currently has **zero** L11 correspondence records
at all — not because they were checked and found to have `NONE`
relationship, but because L11 correspondence work has never been
attempted for them. A future evaluation run against any of those audits
would show 0/0 for every DIRECT-based metric, which must be read as "not
yet assessed," never as "RTF found nothing relevant here."

---

## Summary table

| Category | Count | Read as |
|---|---|---|
| Routing failures | 0/2 | Both real findings correctly routed |
| Downstream analysis failures | 1/2 | H-02: evidence collected, wrong exact location (documented predicate scope boundary, not a crash) |
| Tooling/infrastructure failures (this run) | 0/56 | Clean run; 2 known infra risks exist but did not trigger here |
| Evidence limitations | Structural | L8 not invoked in this pass — final_finding_recall reflects that, not detection quality |
| EthTrust coverage gaps | 25/81 requirements | No predicate exists at all (honestly terminal-stated per-requirement, not silent) |
| Findings with no justified mapping | 0/2 (this audit) | 44/46 audits entirely unassessed — explicit scope boundary, not a clean bill of health |
