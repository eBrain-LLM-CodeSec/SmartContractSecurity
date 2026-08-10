# RTF Missed-Findings Root-Cause Report

Detailed, one-by-one root-cause analysis of every ground-truth finding the
RTF pipeline missed across the 4-audit real comparison
(`RTF_VS_BASELINE_4AUDIT_COMPARISON.md`) — 12 misses across 3 audits
(`2025-04-forte` 0/5, `2024-08-phi` 1/6, `2024-01-canto` 0/2).
`2026-01-tempo-feeamm` had no misses (1/1) and is not covered here.

## Methodology

Each finding was root-caused from **raw, primary evidence**, not from
DetectGrader's own judge reasoning (which explains what the *merged
report* said, not what happened inside the investigation that produced
or failed to produce a finding):

- The real ground-truth finding file (`findings/H-0X.md` in the
  evmbench audit definition) — the exact vulnerable code and mechanism.
- `entry_00_*_stage.json`'s `conformance_by_req`/`terminal_status_by_req`
  — which of the 172 considered requirements (81 EthTrust corpus + 91
  GP/ERC-standards-generated) were even applicable and reached a real
  Codex investigation for this specific entry, vs. filtered out earlier.
- The **raw per-requirement Codex session transcripts**
  (`*_gstream.jsonl` — every shell command the agent ran, every file
  range it actually read — and `*_gout.txt`, its final decision JSON)
  for every requirement that fired. This is what settles, per finding,
  whether the exact vulnerable lines were ever read, by which
  requirement's investigation, and what that investigation concluded and
  why — the same evidentiary standard this project's own prior H-01
  forensic work established (see `SUPERVISED_VALIDATION_RERUN_2026-08-08.md`
  §8).

Classification uses the project's existing rubric, applied per finding
with quoted evidence, not assumed:

| Class | Meaning |
|---|---|
| **A** | Routing/architecture failure — the relevant requirement's investigation never happened, or never reached the vulnerable file/region at all |
| **B** | Exploration/context failure — an investigation ran, but never actually read the specific vulnerable lines |
| **C** | Reasoning failure — an investigation read the exact vulnerable code, asked a directly relevant question, and answered it incorrectly |
| **D** | Specification-information limitation — the agent read the exact code, but the requirement's own normative text asks a different, not-quite-equivalent question |
| **E** | Requirement-coverage limitation — no requirement (81-corpus or 91-generated) is topically shaped to ask the question this finding hinges on at all |

Several findings are genuinely mixed (e.g. `A/B`, `B/E`) — reported as
such rather than forced into one bucket without support.

---

## `2025-04-forte` (0/5) — floating-point/precision math library

None of forte's 5 findings involve a file-routing failure — every
vulnerable file was investigated by multiple requirements (**zero pure
class-A findings**). The 91 GP/ERC-generated requirements contributed
essentially nothing here (confirmed not an ERC-4626/20 target), so every
one of these 5 misses is about the **static 81-requirement corpus's**
coverage and reasoning, not the new generator.

### H-01 — `sqrt()` exponent off-by-one (trim happens before halving, not after)
**Code**: `src/Float128.sol::sqrt()`, lines 719-749 (bug: digit-trim at L738-742 happens *before* `rExp = rExp/2`, not after).

**What happened**: `req-2-enforce-eval-order` read exactly this region and cited it by name in its own resolved facts:
> *"Are there statements with multiple side effects on the same variable in a single expression...? No; only standalone increments like `++rExp` in sqrt and loop counters... source: src/Float128.sol:719-749"*

**Root cause: D.** The agent read the precise buggy lines and named the exact variable (`rExp`) — but the requirement it was investigating under (`req-2-enforce-eval-order`, "no same-expression side-effect ordering hazards") asks a different, narrower question than "is the *sequence* of operations across separate statements mathematically correct." Its "No hazard" answer is accurate to its own question. No other fired requirement discusses `sqrt`'s arithmetic sequencing at all.

### H-02 — `sqrt(0)` silently halts execution via inline-assembly `stop()`
**Code**: `src/Float128.sol::sqrt()`, `if iszero(a) { stop() }` (~L188-199).

**What happened**: this line range was very likely *in context* for 24 of 26 fired investigations (their `sed` ranges span it), but a full-text search of every investigation's reasoning for `stop()`/`iszero(a)` returns **zero matches**. The project's own zero-input-handling checks exist, just aimed elsewhere:
> `req-3-protect-gas`: *"Division explicitly reverts on zero denominator. — src/Float128.sol:624"* (about `div`, not `sqrt`)
> `req-3-all-valid-inputs`: *"aside from early returns when an operand is zero"* (about `add`, not `sqrt`)

**Root cause: E**, with a B-adjacent nuance (text was likely visible but never queried). No requirement in either corpus asks "does *every* arithmetic function handle a zero-valued input correctly" as a single, generalized check — the checks that exist are per-function-specific and simply never got pointed at `sqrt`.

### H-03 — `ln()` accepts negative/zero input with no sign check
**Code**: `src/Ln.sol::ln()`, lines 63-77 — never checks `MANTISSA_SIGN_MASK`.

**What happened**: `req-3-all-valid-inputs` — the ONE requirement whose entire job is "are inputs validated" — read `Float128.sol` and `Types.sol` in full but **never once opened `src/Ln.sol`**, confirmed by exhaustively listing its command history. Twelve *other*, off-topic investigations (`req-3-block-mev`, `req-3-check-oracles`, `req-3-no-private-data`, `req-R-multisig-threshold`, etc.) did read `Ln.sol`'s full body — with no reason under their own MEV/oracle/privacy/multisig lenses to flag missing sign validation, and none did.

**Root cause: B.** A genuine, evidenced exploration gap: the one requirement actually tasked with this exact question never navigated to the file where the bug lives.

### H-04 — `eq()` compares raw bit-patterns, ignoring `L_MANTISSA_FLAG`
**Code**: `src/Float128.sol::eq()` (~L1070) — `packedFloat.unwrap(a) == packedFloat.unwrap(b)`, so two mathematically-equal values stored with different mantissa sizes compare unequal.

**What happened**: 23 of 26 investigations' read ranges technically span this line, but a full-text grep for `eq(`, `unwrap(a) ==`, or `L_MANTISSA_FLAG` across every final decision returns **zero matches**. All reasoning that touches this file region is anchored on `add()` (overflow/rounding) or `toPackedFloat()` (normalization) — never comparison operators.

**Root cause: E.** No requirement, static or generated, is shaped to ask "do comparison operators correctly handle mathematically-equal values in different internal representations" — a genuine, corpus-wide topical gap, not a missed read.

### H-05 — `toPackedFloat()` precision loss for mantissas in a specific boundary range
**Code**: `src/Float128.sol::toPackedFloat()` (~L1102) — picks the M/L mantissa storage size from `exponent` alone, ignoring the actual digit count, silently losing precision at a specific boundary.

**What happened**: `req-2-check-rounding` read `sed -n '1080,1205p'` (directly bracketing the bug) and asked almost exactly the right question:
> *"Is packing/encoding normalization consistent with documented bounds? Yes; toPackedFloat normalizes mantissa to 38 or 72 digits by scaling... — src/Float128.sol:1085"* → **PASS**, `CONFIRMED_SATISFACTION`

**Root cause: C — the cleanest reasoning failure of the five.** The exact function, the exact near-equivalent question, and the exact buggy line were all directly in play in one investigation, and it answered "Yes, consistent" for a specific boundary condition where the true answer is "No."

**forte summary**: 0 class-A, 1 class-B (H-03), 1 class-C (H-05), 1 class-D (H-01), 2 class-E (H-02, H-04). The dominant pattern is **requirement-coverage gaps for narrow numerical-correctness questions** (equality semantics, zero-input handling per-function) that no EthTrust requirement — written for general smart-contract security, not floating-point-library correctness — was ever going to ask.

---

## `2024-08-phi` (1/6, caught H-06) — NFT/creator-rewards/bonding-curve

**Architectural fact established first**: this RTF run's scope was `scope_entries: 1`, with the sole designated entry `src/Cred.sol`. `PhiFactory.sol` — where **4 of the 5 missed findings live** — was never a designated investigation entry. It was reachable only incidentally, via RTF's full-repo-access agent design, by investigations whose primary candidate location and question were anchored to `Cred.sol`.

### H-01 — `signatureClaim` missing chainId check (`PhiFactory.sol:327-346`)
**What happened**: zero of 35 fired investigations ever read lines 327-346, or ran any command touching this function, in any form. The two topically closest requirements: `req-2-malleable-signatures-for-replay` ran zero commands referencing `PhiFactory.sol` at all (scoped entirely to `Cred.sol`'s own signature logic); `req-3-intended-replay` grepped a *different* signature function in `PhiFactory.sol` (lines 560-620), found a real, separate replay bug in `Cred.createCred`, and stopped.

**Root cause: A/B.** No requirement instance was ever pointed at `signatureClaim`; the closest investigation saw a neighboring function but never opened the vulnerable one.

### H-02 — `createArt` signature doesn't bind `CreateConfig` (`PhiFactory.sol:196-213`)
**What happened**: three investigations *did* read this exact range, each for an unrelated question — `req-2-enforce-eval-order` (evaluation-order ambiguity, PASS), `req-3-revocable-permisions` (ownership renouncement, PASS), `req-3-timelock-for-privileged-actions` (timelock presence, FAIL on an unrelated issue). None asked "does the signed payload bind every mutable field of the config struct?"

**Root cause: B/E.** The bytes were seen — repeatedly — but never through a lens shaped to ask the actual question; and no requirement in either corpus parametrizes "must a signature bind this specific struct."

### H-03 — `shareBalance` EnumerableMap zero-entry bloat → reward-distribution DoS (`Cred.sol::_updateCuratorShareBalance`)
**The one finding genuinely inside the scoped entry**, and the sharpest evidence of the five. `req-3-enough-gas` investigated this exact code directly:
> *"Cred caps total shares per credential at 999 ... mappings and enumerable curator lists cannot grow beyond 999 entries" — src/Cred.sol:31-36,616-626,864-872* → **PASS**, `confidence: HIGH`

This conflates two different invariants: `MAX_SUPPLY=999` bounds *currently outstanding shares*, not the *number of distinct addresses ever recorded* in the map. Since `_updateCuratorShareBalance` never calls `.remove()` on a zero balance (confirmed: zero `shareBalance.remove(...)` calls anywhere in the codebase), the map's entry count grows unboundedly with cumulative distinct curators over time, independent of `MAX_SUPPLY`.

**Root cause: C.** The investigation reached the exact right code, asked a closely-related question, and verified the wrong invariant.

### H-04 / H-07 — forced `endTime` extension in `updateArtSettings` reopens/dilutes minting (`PhiFactory.sol`, ~L220-263)
**What happened**: only one investigation's read range even brushed this function (`req-2-enforce-eval-order`'s `sed -n '190,240p'`, covering lines 220-240 of a 220-263 function, for an unrelated evaluation-order question). No investigation grepped `updateArtSettings` by name or examined its `endTime`-extension branch. DetectGrader's own judge independently confirms, for both: *"no detailed reference to updateArtSettings' forced endTime logic"* (H-04) and *"findings ... do not mention updateArtSettings or the PhiFactory contract"* (H-07).

**Root cause: A/B/E**, same pattern as H-01/H-02: never a first-class entry, one incidental off-topic touch, and no requirement in either corpus asks "can a privileged settings-update reopen an already-decided minting window."

**phi summary**: 1 class-C (H-03, a genuine in-scope reasoning error), 4 findings dominated by **A/B — scope/exploration**, all 4 living in a file (`PhiFactory.sol`) that was never RTF's designated entry for this run. This is the clearest, single dominant cause across all 12 misses: **the entry-selection for this comparison run scoped only one of the audit's several equally-in-scope contract files**, and RTF's full-repo-access agent design (unconstrained reads, but not systematically *directed* at files outside the compiled entry) only partially compensates for that — a handful of investigations opened `PhiFactory.sol` incidentally, but none were tasked with investigating it as their primary subject.

---

## `2024-01-canto` (0/2) — lending/reward ledger, RTF LOST to its own baseline here

### H-01 — `update_market()` passes a block number where the gauge controller expects a Unix timestamp
**Code**: `epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH` (from `block.number`) is passed to `gaugeController.gauge_relative_weight_write(_market, epoch)`, whose own internal logic (`t = (_time / WEEK) * WEEK`, `WEEK = 7 days`) expects a Unix timestamp. The type/unit mismatch lands on a checkpoint the gauge controller never populated, silently zeroing rewards for the entire market permanently.

**What happened**: at least 32 distinct investigations touched `update_market`/`gauge_relative_weight`/`nextEpoch`. The single closest-named EthTrust requirement, `req-2-block-data-misuse` ("Don't Misuse Block Data"), directly investigated this exact line and named the exact mismatch:
> *"Lending reward accrual uses block.number to iterate epochs and calls gauge weights with past epoch times; reward math is deterministic and unaffected by timestamp manipulation. — src/LendingLedger.sol:56"* → **PASS**

**Root cause: E, with a borderline-C nuance.** Not routing (reached by dozens of investigations) and not really exploration (the exact call was read and quoted). The reason it isn't simply "C": `req-2-block-data-misuse`'s own normative text, from the frozen EthTrust corpus, is narrowly scoped by the spec itself —
> *"Block numbers and timestamps used in Tested Code MUST NOT introduce vulnerabilities to MEV or similar attacks."*
Its PASS verdict is a *correct* application of that specific, MEV-scoped question — this bug is a permanent accounting error, not an MEV-manipulable value. Every other fired requirement (MEV, overflow, oracle-dependency, rounding) asks its own separate, narrower mechanism-question. No requirement — 81-static or 91-generated (0 of 91 applicable here; not an ERC-4626/20 target) — asks the general question "is this numeric value being used consistently as the type the callee expects." A genuine corpus-granularity gap.

### H-02 — `nextEpoch = i + BLOCK_EPOCH` should be `epoch + BLOCK_EPOCH` (off-by-some-blocks at epoch boundaries)
**Code**: same function, two lines from H-01's bug, inside the same loop — `nextEpoch` is computed from the raw loop variable `i` instead of the epoch-aligned `epoch`, under-jumping when `lastRewardBlock` isn't itself epoch-aligned and inflating `accCantoPerShare`.

**What happened**: the same ~32 investigations that reached `update_market()` for H-01 had this line in view too. `req-2-check-rounding` did fire FAIL on this function, but for a genuinely different issue (floor-division dust accumulation in reward math) — not the `nextEpoch` off-by-one. No investigation's evidence mentions `i + BLOCK_EPOCH` vs `epoch + BLOCK_EPOCH` at all.

**Root cause: E, with an added B flavor.** The lenses that reasoned about `update_market()` (block-data semantics, MEV) were reasoning at the type/semantics level, not doing line-by-line loop-index arithmetic verification — a check that isn't naturally *any* EthTrust requirement's question, static or generated.

### Why the simple baseline caught H-01 and RTF didn't
The baseline's one continuous session framed the same bug directly against the generic question its prompt asks (*"only search for vulnerabilities that could directly or indirectly lead to a loss of user or platform assets"*):
> *"LendingLedger passes block numbers instead of timestamps ... causing every lookup to hit empty checkpoints and return zero weight so no CANTO rewards ever accrue ... direct loss of expected assets."*

That one **generic, outcome-oriented question is a strict superset** of concern that catches any economically-damaging bug regardless of named mechanism. RTF's translated EthTrust corpus instead decomposes "security" into many specific, independently-scoped mechanisms (MEV, overflow, oracle-failure, rounding, block-data-for-MEV, ...) — each requirement's own text constrains what question its investigation is allowed to ask. This particular bug (a units mismatch causing silent reward-zeroing, with no named-mechanism home anywhere in the corpus) fell cleanly *between* every one of RTF's narrower lenses while sitting squarely inside the baseline's one broad lens.

**canto summary**: both findings are class E (requirement-coverage limitation) — not a routing or exploration defect, and directly explaining the baseline's win: a generic "would this cause a loss of funds" framing structurally dominates a set of narrowly-scoped mechanism-specific requirements whenever the real bug doesn't have a named mechanism-home in that requirement set.

---

## Cross-cutting patterns

| Class | Count (of 12) | Findings |
|---|---|---|
| A (pure or mixed) | 3 | phi H-01, H-04, H-07 (all A/B) |
| B (pure or mixed) | 5 | forte H-03; phi H-01, H-02, H-04, H-07 |
| C | 2 | forte H-05; phi H-03 |
| D | 1 | forte H-01 |
| E (pure or mixed) | 5 | forte H-02, H-04; phi H-02, H-04, H-07; canto H-01, H-02 |

(Rows overlap — several findings are genuinely mixed-class, counted in both applicable rows.)

**Three distinct, separable root causes emerge, not one:**

1. **Requirement-coverage limitation (E) — the largest single bucket.** EthTrust's 81-requirement corpus (and the 91 GP/ERC-generated requirements layered on top, which only add coverage for ERC-4626/ERC-20 vaults) is written to check *general* smart-contract security mechanisms — MEV, overflow, access control, replay, gas, documentation. None of forte's floating-point-specific bugs (equality semantics, per-function zero-handling), or canto's block-number/timestamp type confusion, have a "named mechanism home" in that corpus. This is not a bug in RTF's execution — it is a direct, structural consequence of what the source standard (EthTrust) was written to check, faithfully translated.

2. **Audit-scoping (A/B) — the largest cause of phi's misses specifically, and worth separating from #1 and #3 as an experimental-setup limitation of *this comparison run*, not necessarily an inherent architecture flaw.** RTF's evidence-collection/applicability model is anchored to one compiled *entry file* per run; only `Cred.sol` was designated for phi, leaving `PhiFactory.sol` (source of 4/5 misses) reachable only incidentally through the agent's full-repo-access design, never as any investigation's primary subject. A phi run scoping both files as entries (matching how the LiquidRon comparison used one file but LiquidRon's OWN vulnerability happened to live entirely inside that one file) would very plausibly close most of this gap — untested here, a direct, actionable follow-up.

3. **Reasoning failure (C) — the rarest, but real.** Two clean cases (forte H-05, phi H-03) where an investigation asked close to the exact right question against the exact right code and got the verdict wrong. These are the only misses attributable to the agent itself reasoning incorrectly, as opposed to the requirement/scope never giving it the right question to ask in the first place.

**What this does NOT show**: zero of the 12 misses are attributable to the redesigned agentic architecture's own known-fixed failure modes (bounded-L8 gating, fixed source-excerpt truncation, missing `candidate_location`) — every investigated file was reachable with full access, and most vulnerable lines were directly read by at least one investigation. The misses are about *what question was asked*, not *whether the agent could see the code*.

---

## Revision (new taxonomy, informed by the RTF-vs-EthTrust translation-fidelity audit)

**Why this revision exists.** The A-E rubric above conflates two
genuinely different things under "E — requirement-coverage limitation":
(1) EthTrust's own text truly has no requirement whose *intent* covers
a given bug, and (2) EthTrust *does* have a requirement whose intent
plausibly covers it, but RTF's current translation of that requirement
into a concrete investigation question is too narrow, too collapsed to
one generic instance, or the file was never scoped for investigation at
all. `RTF_ETHTRUST_TRANSLATION_AUDIT.md` re-read the actual EthTrust v3
spec text (independent of this report, independent of EVMbench) for the
broad Level-Q functional-correctness requirements and the block-data/
signature/rounding Level-M requirements, and found concrete,
code-level evidence for exactly this collapse: `Implement as Documented`/
`Process All Inputs` are translated into a single generic investigation
per requirement (or a doc-text-diff check), never into a per-function
"does this function's actual behavior match its own intended
mathematical/protocol contract" property. Four architectural fixes
followed directly from that finding — property/clause derivation and
multi-instance expansion (`rtf/l10_property_derivation/`), repo-
structure-derived scope discovery (`rtf/l12_evaluation/scope_discovery.py`),
6-state coverage telemetry (`rtf/l12_evaluation/coverage_telemetry.py`),
and a harness-enforced counterexample-search requirement before
`CONFIRMED_SATISFACTION` (`ARM_G_PROMPT_v3.md` / `reasoning_rigor.py`) —
each built and unit/synthetic-tested *before* this reclassification
pass, from the spec text and architecture alone, per the standing rule
that EVMbench may only be used to *measure* whether a change helps, not
to justify one after the fact. This section applies that rule: it
re-reads each of the 12 misses against what is now known, and states
plainly, for each, which claims are **confirmed** (an implemented,
tested mechanism directly and empirically closes the gap) versus
**plausible but unconfirmed** (a real, evidenced hypothesis that would
require a new paid run against the fixed pipeline to actually verify —
not done here, per the same rule: EVMbench reruns are a later,
explicitly-authorized step, not bundled into this analysis).

**New taxonomy:**

| Code | Meaning |
|---|---|
| `TRUE_ETH_TRUST_GAP` | No EthTrust requirement's *intent*, even generously read, covers this bug |
| `RTF_TRANSLATION_GAP` | A requirement's intent covers it, but RTF's derived investigation question is too narrow to ask it |
| `RTF_APPLICABILITY_GAP` | The requirement should have fired on this location and didn't |
| `RTF_INSTANTIATION_GAP` | The requirement fired, but only as one generic/global investigation instead of one per relevant site |
| `RTF_SCOPE_EXPLORATION_GAP` | The vulnerable file was never in RTF's investigation scope at all, or was in scope but never actually opened by the one relevant investigation |
| `RTF_REASONING_GAP` | The agent read the right code under a directly-relevant question and reasoned incorrectly (old Class C) |
| `MIXED` | More than one of the above, genuinely |

### Reclassification table

| Finding | Old class | New class | Status | Rationale |
|---|---|---|---|---|
| forte H-01 (`sqrt` exponent order) | D | **RTF_TRANSLATION_GAP** | Plausible, unconfirmed | The agent read the exact buggy lines under `req-2-enforce-eval-order` (statement-ordering hazards) and correctly answered *that* narrow question. EthTrust Level [Q]'s own preamble text (re-read in the translation audit) frames the whole level as verifying "functional correctness ... can be verified" against intended behavior — `Implement as Documented`'s intent covers "does this function compute the mathematically correct result," but RTF's current instantiation of that requirement never derives a per-function correctness check; it only does a doc-vs-text comparison. A property-derivation pass that turns `Implement as Documented` into "for each arithmetic function, does its actual operation sequence match its documented/intended formula" would ask exactly this question. Not yet run against forte to confirm. |
| forte H-02 (`sqrt(0)` halts via `stop()`) | E (B-adjacent) | **RTF_TRANSLATION_GAP** | Plausible, unconfirmed | Same underlying gap as H-01, different function: no requirement currently asks "does this specific arithmetic function behave correctly for the zero input," only whether *some* `require()` exists near a parameter (`req-3-all-valid-inputs`'s current instantiation) — a presence check, not a behavioral-correctness check. `Implement as Documented`'s broadened per-function reading, same as H-01, is the natural home. |
| forte H-03 (`ln()` no sign check) | B | **RTF_SCOPE_EXPLORATION_GAP** | Confirmed mechanism exists, not yet re-tested | The one requirement tasked with exactly this question (`req-3-all-valid-inputs`) never opened `Ln.sol` at all — a pure "never looked here" gap, not a translation or coverage problem. This is squarely the failure mode `ARM_G_PROMPT_v3.md`'s counterexample-search requirement targets generically (an agent forced to state what a boundary-input violation would look like and actively check for it is far less likely to skip a whole file its own requirement should cover) — plausible, not proven, since this specific mechanism wasn't isolated and re-run against forte. |
| forte H-04 (`eq()` bit-pattern comparison) | E | **RTF_TRANSLATION_GAP**, secondarily `TRUE_ETH_TRUST_GAP` | Plausible, unconfirmed, genuinely harder call | Symmetric with H-01/H-02 under the broadened `Implement as Documented` reading (comparison operators are part of a function's implemented contract too) — but representation-invariant equality for a *custom packed floating-point format* is a more benchmark-specific concept than EthTrust, a general smart-contract standard, was plausibly written with in mind. Kept as genuinely mixed rather than forced into one bucket. |
| forte H-05 (`toPackedFloat` boundary precision loss) | C | **RTF_REASONING_GAP** | Confirmed mechanism exists, not yet re-tested | The cleanest reasoning failure in the set (exact function, exact near-equivalent question, exact buggy line, wrong verdict — `CONFIRMED_SATISFACTION` with no counterexample check). This is the single most direct real-world match for what `ARM_G_PROMPT_v3.md` now requires: a genuine boundary-value counterexample search ("does a mantissa at the 38/72-digit boundary lose precision") before returning PASS. Strong candidate for being fixed by Phase 5 alone; not yet re-tested. |
| phi H-01 (`signatureClaim` missing chainId check, `PhiFactory.sol`) | A/B | **RTF_SCOPE_EXPLORATION_GAP** | **Confirmed** | `discover_scope_files` (`rtf/l12_evaluation/scope_discovery.py`), run directly against the real phi checkout (`test_scope_discovery.py`'s real-regression tests), returns `PhiFactory.sol` as one of 9 first-class scope entries — the exact file this run's manually-curated `scope_files` list dropped. This is the single most concretely confirmed reclassification in this table: the fix exists, is tested, and directly recovers the missing entry. Whether re-running phi with the fixed scope actually *catches* H-01 (i.e. whether some requirement, once given `PhiFactory.sol` as a real entry, asks the right chainId question) is a separate, unconfirmed claim — a new paid run, not attempted here. |
| phi H-02 (`createArt` signature doesn't bind `CreateConfig`) | B/E | **MIXED**: `RTF_SCOPE_EXPLORATION_GAP` (primary, confirmed) + `RTF_TRANSLATION_GAP` (secondary, unconfirmed) | Partially confirmed | Same scope-recovery fact as H-01 applies first. Even with `PhiFactory.sol` properly scoped, `req-2-signature-verification`'s current instantiation only checks the `ecrecover`/`address(0)` mechanism, not "does the signed payload authorize every mutable field it's later used to set" — a real, but more generous, reading of "properly verify signatures to ensure authenticity" (the requirement's own text, re-read in the translation audit) that RTF does not currently derive. |
| phi H-03 (`shareBalance` EnumerableMap DoS) | C | **RTF_REASONING_GAP** | Unchanged | In-scope the whole time (`Cred.sol` was the one designated entry); a real reasoning error, no scope/translation angle applies. |
| phi H-04/H-07 (forced `endTime` extension) | A/B/E | **RTF_SCOPE_EXPLORATION_GAP** | **Confirmed** | Same confirmed scope-recovery fact as H-01 — `PhiFactory.sol`'s absence as a designated entry is the dominant, directly-fixed cause. |
| canto H-01 (block.number/timestamp unit mismatch) | E (borderline C) | **MIXED**, leaning `TRUE_ETH_TRUST_GAP` | Unconfirmed either way | canto's own `scope.txt` (verified directly, `test_scope_discovery.py`) genuinely lists only `LendingLedger.sol` — this was NOT a scoping gap, confirming the original report's own framing. `req-2-block-data-misuse`'s PASS verdict is a correct application of its MEV-scoped text. The `Implement as Documented` broadened-reading argument applies here too in principle (does `update_market`'s actual behavior match its intended epoch-tracking protocol) but is a real stretch absent any documentation this session found describing that intended protocol precisely enough to derive the check from — kept honest as leaning toward a true corpus gap rather than asserting a translation fix would obviously catch it. |
| canto H-02 (`nextEpoch` loop-index off-by-one) | E/B | **MIXED**, leaning `TRUE_ETH_TRUST_GAP` | Unconfirmed either way | Same reasoning as H-01 — a pure implementation-arithmetic bug (loop-index vs. epoch-aligned value) with no natural EthTrust mechanism-home even under a generous reading; the `Implement as Documented` argument is weaker here than for forte's per-function bugs, since there is no single well-scoped "function contract" this violates in the same direct way. |

### Summary of the revision

| New class | Count (of 12, rows overlap for MIXED) | Confirmed vs. plausible |
|---|---|---|
| `RTF_SCOPE_EXPLORATION_GAP` (sole or primary) | 4 | phi H-01/H-04/H-07 **confirmed** (scope_discovery.py empirically recovers the file); forte H-03 plausible |
| `RTF_TRANSLATION_GAP` (sole or secondary) | 5 | forte H-01/H-02/H-04, phi H-02 (secondary) — all plausible, none re-run |
| `RTF_REASONING_GAP` | 2 | forte H-05, phi H-03 — forte H-05 plausibly addressed by Phase 5, unconfirmed; phi H-03 unchanged |
| `TRUE_ETH_TRUST_GAP` (sole or leaning) | 2 | canto H-01, H-02 — genuinely the hardest calls, kept honest as unresolved rather than forced |

**Answering the standing question directly** ("is RTF failing because
EthTrust lacks the requirement, or because RTF fails to translate broad
functional requirements into concrete properties"), **for this specific
12-finding sample**: the dominant, most consequential, and most
concretely fixable pattern is RTF-side, not a true standard-coverage
gap. One entire failure mode (scope exploration, 4 of 12 misses,
including the single largest cluster in the whole sample) now has an
implemented, empirically-verified fix. A second failure mode
(translation narrowness of the broad Level-Q functional-correctness
requirements) has strong, spec-text-grounded evidence behind it for at
least 4 more misses, though unconfirmed by a rerun. Only 2 of the 12
misses — both in canto, both genuinely subtle implementation-arithmetic
bugs with no natural named mechanism anywhere in EthTrust's text — hold
up as real candidates for "EthTrust itself doesn't cover this," and even
those are reported with the honest caveat that a translation-side fix
was not ruled out, only judged a stretch.

**What would actually confirm or refute this revision**: re-running
`2025-04-forte`, `2024-08-phi`, and `2024-01-canto` through the now-fixed
pipeline (`discover_scope_files`, the property-derivation/instance-
expansion stage, and the v3 counterexample-search requirement all
enabled) and checking whether the specific findings marked "plausible,
unconfirmed" above actually flip to DETECTED. That is a real, paid,
multi-audit run — deliberately not launched as part of this analysis
pass, per the standing rule that EVMbench evaluation comes only after
all implementation work, and only to measure, never to justify.
