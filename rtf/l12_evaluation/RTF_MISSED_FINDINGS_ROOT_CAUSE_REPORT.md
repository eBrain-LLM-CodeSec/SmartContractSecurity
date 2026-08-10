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
