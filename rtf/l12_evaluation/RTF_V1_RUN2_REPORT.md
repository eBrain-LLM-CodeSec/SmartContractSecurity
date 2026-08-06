# RTF Version 1, Evaluation Run 2 — Report

**Scope of this run:** (1) fixed a real implementation defect (AR-011)
found by determining whether run 1's H-02 miss was a text-derivation
limit or a bug — it was a bug; (2) integrated L8 into the orchestrator
and stress-tested it on clear/borderline/insufficient-evidence cases;
(3) sampled 4 new audits via a frozen protocol (before any compatibility
check) — 3 were environmentally blocked on this HPC node, 1
(`2026-01-tempo-mpp-streams`) compiled and ran cleanly; (4) re-ran
`2023-07-pooltogether` with the AR-011 fix and L8 integrated. Full
per-artifact data: `rtf/l12_evaluation/run2_artifacts/`.

---

## 1. Audit-sampling outcome (frozen protocol, `AUDIT_SELECTION.json`)

| Audit | Framework | Result |
|---|---|---|
| `2025-02-thorwallet` | Hardhat/npm | **BLOCKED** — no Node.js/npm/bun runtime installed on this node at all; not a compatibility judgment, a missing runtime |
| `2024-03-taiko` | Foundry | **BLOCKED** — no vendored `lib/`, no `.gitmodules`; would need `forge install`, blocked by the same GLIBC issue as AR-009 |
| `2024-01-init-capital-invitational` | Foundry | **BLOCKED** — same as taiko, plus a non-git `contracts/.cache/` dependency with no documented provisioning step found |
| `2026-01-tempo-mpp-streams` | Foundry | **RAN** — `lib/` fully vendored (forge-std, openzeppelin-contracts), compiled cleanly via the same no-forge workaround as pooltogether |

Per this protocol's own frozen rule (mirroring Track A's), **none of the
3 blocked audits were substituted for easier ones.** This 3-of-4 block
rate is itself a real, disclosed finding: this HPC node's current
tooling (no Foundry, no Node.js) meaningfully limits which real EVMbench
audits are reachable at all, independent of anything about RTF's own
translation quality.

## 2. AR-011: H-02's miss was an implementation defect, not a text limit

Investigated using only `req-3-all-valid-inputs`'s original normative
text and definitions (before checking effect on any score). Verdict:
**defect.** The predicate's original public/external-only scope had no
basis anywhere in the requirement's text (`"Tested Code MUST validate
inputs"`, with `"Tested Code"` defined broadly, no visibility
restriction stated or implied). Fixed to scan all functions regardless
of visibility. Confirmed against real code: `Vault._burn`/`_mint`/
`_transfer` (H-02's actual fix location) now appear in the evidence.
Full writeup: AR-011 in `rtf/l9_assumptions_register/REGISTER.jsonl`.

## 3. L8 case-type testing

Three real evidence shapes tested (`rtf/l8_llm_judgment_layer/
live_validation/03_clear_borderline_insufficient_evidence.{py,json}`):

| Case | Expected | Got | Stable across 2nd pass? |
|---|---|---|---|
| "Clear" (H-04, unprotected `mintYieldFee`) | FAIL | **INSUFFICIENT_EVIDENCE** | Yes — correctly noticed the requirement's own text conditions on a documentation cross-check the evidence doesn't supply |
| Borderline (read-only-reentrancy candidate) | Uncertain | FAIL (1st pass) | **No — 2nd pass DISAGREED** |
| Insufficient-evidence (bare `block.timestamp` read) | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | Yes |

The borderline case's real, observed second-pass disagreement is the
first concrete evidence this project has for the flip-risk Track A's
go/no-go review flagged as untested. It directly validates the plan's
mandatory-second-pass rule — the first pass alone would have silently
reported a confident-sounding FAIL the model couldn't reproduce.

---

## 4. Three separated outcomes

Per your explicit instruction, these are reported separately and must
not be blended into one number — each answers a different question
about a different pipeline stage.

### (a) Routing / evidence performance (deterministic layer only — no L8, no external grader)

| Metric | pooltogether | tempo-mpp-streams |
|---|---|---|
| Requirement routing recall | 2/2 | 2/2 |
| Requirement routing precision | 2/38 (5%) | 2/34 (6%) |
| Target localization accuracy | **2/2 (100%, up from 1/2 in run 1)** | 2/2 (100%) |
| Evidence collection recall | 2/2 | 2/2 |

**Reading this:** RTF's deterministic layer (L1–L7 predicates) correctly
routes to and collects evidence at the exact real vulnerable location
for all 4 known findings across both audits. Precision looks low (5–6%)
but is not a false-positive rate — each audit has only 1–2 *graded*
findings while RTF's evidence-only predicates are deliberately
over-inclusive by design (most of the other ~35 `APPLICABLE`
requirements per target are unscored candidates, not confirmed false
positives).

### (b) Final RTF judgment performance (post-L8)

| Metric | pooltogether | tempo-mpp-streams |
|---|---|---|
| Final finding recall (L8 reaches FAIL) | 0/2 | 0/2 |
| L8 decision on both DIRECT requirements | INSUFFICIENT_EVIDENCE (both, stable) | INSUFFICIENT_EVIDENCE (both, stable) |

**Reading this — the most important, consistent finding of this run:**
in **both** audits, on **all four** ground-truth-mapped requirements, L8
reached the same verdict: the evidence correctly points at the real
vulnerable code, but its phrasing (e.g. *"parameter not referenced in
any require()/assert()"*) is too generic for the model to confidently
conclude a violation without more context (what the specific exploit
mechanism is, what "correct" behavior would look like). This is not
noise — it replicated identically across two structurally different
audits and vulnerability types (a truncating cast, a missing
zero-address check). **This is real, actionable signal that RTF's
current evidence format is the limiting factor for final judgment
quality, not L8's reasoning or the underlying localization.**

### (c) DetectGrader finding recall (external, real upstream grader)

| Audit | Score | Detail |
|---|---|---|
| pooltogether | **1/2** | H-04 detected (unchanged from run 1); H-02 still not detected, even with the AR-011 fix's corrected evidence present in the report — the grader's judge explicitly reasoned that the report's phrasing describes "unprotected/unvalidated" generically, not the specific `uint256→uint96` truncating-cast mechanism, so it doesn't count as detecting "the same vulnerability" under the grader's strict same-fix criterion. **This reframes run 1's finding: the gap is no longer "wrong location" (AR-011 fixed that), it is now specifically "evidence not specific enough to name the exploit mechanism."** |
| tempo-mpp-streams | **0/1** | H-03 not detected — same pattern: the judge confirmed the report's evidence is in the right functions but doesn't articulate the zero-address/ecrecover mechanism specifically enough |

**All three outcome categories tell a coherent, consistent story**:
routing and localization are strong (100% on every known case across
both audits); the bottleneck is entirely downstream, in how
under-specified RTF's current evidence text is once evidence exists.

---

## 5. Audit-level confidence, tracked separately by prior exposure

| Audit | Prior exposure | Basis | Confidence in DIRECT-based metrics for this audit |
|---|---|---|---|
| `2023-07-pooltogether` | **SUBSTANTIAL** (declared in `EXPOSURE_DECLARATION.json`) | This project's own earlier MGPR work analyzed this exact corpus's findings in detail, including H-02/H-04 by name and line number, before RTF existed | **DOWNGRADED**, per the plan's own mandate — correspondence built via a fresh-subagent mitigation, not true personnel separation (documented in `L11_PROCESS_NOTES.md`'s extension section). Localization/routing results here should be read as a *weaker* signal of RTF's real capability than the numbers alone suggest. |
| `2026-01-tempo-mpp-streams` | **NONE** (fresh) | Selected via the frozen sampling protocol; its finding text was read for the first time in this pass, by this same session, but only *after* every RTF translation artifact (predicates, requirement corpus, L2–L7 records) had already been completed and hash-locked at commits `d4f7ba6`/`95c4f88` — satisfying the plan's temporal/procedural blinding fallback for `PARTIAL`/`NONE` exposure | **Standard confidence, not downgraded** — this is currently the project's *strongest* piece of evidence for RTF's real, un-primed capability, precisely because it was never seen before this pass and the translation work strictly predates it. |

**This asymmetry is itself the headline finding of this section:**
`tempo-mpp-streams`' clean, fresh-exposure 2/2 routing and localization
result on a genuinely novel target is stronger evidence for RTF's real
generalization than pooltogether's matching numbers — precisely because
pooltogether's result could, in principle, be partly explained by this
project's own prior familiarity with that specific corpus, however
indirectly. Any future aggregate reporting across more audits **must**
keep this distinction (fresh vs. substantial-exposure) and never average
DIRECT-based recall across both tiers into one number.

---

## What remains open after this run

- **The evidence-specificity gap (finding 4b/4c) is now the clearest,
  most reproducible next problem** — appearing identically across 2
  unrelated audits and vulnerability mechanisms. A plausible fix
  direction: enrich predicate evidence with more of the surrounding
  code/exploit-relevant context (not just "parameter X unused in a
  require"), though this needs its own careful, text-grounded design
  pass, not a quick patch.
- Still only 2 of 40 real audits ever evaluated end-to-end; 3 more are
  environmentally blocked pending Foundry/Node.js availability on this
  node.
- L8 was scoped to only the DIRECT-correspondence requirements in this
  run (2 per audit) to bound cost — not run across all ~34–38
  `APPLICABLE` requirements per target, so `inconclusive_rate`/
  `insufficient_evidence_rate` above reflect only that narrow subset,
  not the full applicable set.
