# RTF v2 combined pipeline (whole-project Foundry compile + EthTrust structural routing + semantic-v2): root cause of every miss

Forensic trace over artifacts already on disk from the 5-target re-run
completed 2026-08-15/16 (`RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md` §24).
No new LLM/Codex calls made — every property, verdict, and piece of
investigator reasoning quoted below is read verbatim from that run's own
`checkpoint.jsonl` (real, already-paid-for evidence) or from
`grade_result.json` (the real `DetectGrader` judge's own reasoning).
Ground truth read from each audit's `findings/H-XX.md`. This is post-hoc
forensic analysis of already-frozen-and-graded runs, not benchmark
tuning.

**Score**: 10/15 across tempo-feeamm (1/1), canto (1/2), forte (3/5), phi
(4/6), liquid-ron (1/1). This report covers the 5 misses: canto H-01,
forte H-01, forte H-03, phi H-03, phi H-07.

---

## canto H-01 — block-number used where GaugeController expects elapsed time

**Ground truth** (`findings/H-01.md`, `src/LendingLedger.sol:69`):
`update_market()` calls `gaugeController.gauge_relative_weight_write(gauge,
block.number)` — but `GaugeController`'s own weight-checkpoint logic
expects a **time** argument, not a raw block count. Canto's block time is
not fixed, so `block.number` silently drifts from real elapsed time,
corrupting the weight calculation the external call performs.

**Evidence chain — this is NOT a coverage gap.** The exact right EthTrust
requirement, `req-2-block-data-misuse`, was applied to `update_market()`
**three separate times** (`loc0`, `loc1`, `loc2`), each a real,
independent investigation:

> `req-2-block-data-misuse::loc2` → **PASS**: "update_market uses
> block.number to measure discrete emission intervals, partitions them by
> the explicitly block-denominated BLOCK_EPOCH, and monotonically
> advances lastRewardBlock... Rewards are configured per block by
> setRewards."

The investigator correctly confirmed `block.number` is used
**self-consistently** within `LendingLedger` itself (every local
computation treats it as a block count, never conflated with a
timestamp inside this contract). What it did not do — in any of the
three independent attempts — is check whether the **value being handed
to the external call** matches what the **callee** (`GaugeController`)
itself expects. `req-3-enough-gas::loc0` and `req-2-external-calls::loc0`
both independently *read* `gauge_relative_weight_write`'s real signature
and even `GaugeControll[er]`'s own checkpoint-loop implementation while
investigating unrelated angles (gas cost, controller-address validation)
— the information needed to catch this bug was in front of the
investigator multiple times — but no investigation attempt asked "does
the callee's own definition of this parameter match what block.number
actually represents."

**Classification: `INVESTIGATION_REASONING_GAP` — a cross-boundary
semantic/unit mismatch, not a coverage or generation gap.** The
requirement, the function, and (per two adjacent investigations) even
the callee's source code were all in view. This is a genuinely different
failure shape from every "GENERATION_COVERAGE_GAP" finding in this
project's prior root-cause reports: the miss is not "nobody looked,"
it's "everybody who looked checked the wrong invariant" — internal
self-consistency of a value, not the value's semantic contract with an
external component it's handed to.

**Why, as a security expert**: "is `block.number` used consistently as
a block count" is a natural, bounded question an LLM investigator can
answer purely by reading the caller. "Does the external contract this
value gets passed to interpret it the same way" requires the
investigator to treat an external call's argument as a genuine interface
boundary — deliberately re-deriving the callee's own expectations from
its interface/implementation, not just confirming the caller's own
internal arithmetic is self-consistent. This is a harder, two-hop
reasoning step, and it's the exact class of miss `req-2-block-data-misuse`
was *also* missed on in an earlier session for a materially similar
reason (see `rtf/l9_assumptions_register/REGISTER.jsonl` AR-028's own
citation of this exact requirement/target/mechanism from a prior corpus-
parsing investigation).

**Concrete fix**: extend the counterexample-search instruction in
`ARM_G_PROMPT_v3.md`/the cluster investigation prompt to explicitly
require, whenever an external call's argument derives from
`block.number`/`block.timestamp`, checking the callee's own parameter
semantics (via its interface or source, if available) as a **distinct,
mandatory sub-question** from "is this value used consistently within
the caller" — a targeted, mechanism-specific prompt addition (matching
this project's existing convention of adding narrow, evidenced prompt
hints rather than a blanket "be more thorough" instruction).

---

## forte H-01 — sqrt exponent off-by-one (halve-before-digit-adjustment ordering)

**Ground truth** (`findings/H-01.md`, `src/Float128.sol` sqrt's
large-mantissa path): digit-count normalization happens *before* halving
the exponent, but halving must happen first — an off-by-one in the
result exponent.

**Evidence chain**: this run's generator did NOT sit idle on `sqrt` —
it produced two **different, real, correctly-diagnosed** numerical
defects in the same function:

> `semantic__numerical__a187ef56acbe` → **FAIL**: a specific
> `lt(a,b)`-ordering counterexample in sqrt's odd-exponent scaling
> branch (`Float128.sol:826`).
>
> `semantic__numerical__3e1ee69bde02` → **FAIL**: sqrt's downward
> rounding combined with `mul`'s truncation means non-perfect squares
> don't round-trip through `eq` (`Float128.sol:818`).

Neither property names the specific halve-before-digit-adjustment
ordering defect H-01 describes — they are adjacent, real,
independently-valid bugs in the same function, not the same bug
reworded.

**Classification: `GENERATION_COVERAGE_GAP` — a "precision-competing"
variant.** This is not pure absence (`sqrt` clearly got real, repeated
generator attention) and not investigation timeout (both properties
resolved cleanly). The generator's limited per-function property budget
landed on two other genuine defects instead of this one — the same
function can hide multiple independent numerical bugs, and one-shot
generation does not reliably enumerate all of them.

**Why, as a security expert**: fixed-point/floating-point libraries are
exactly the kind of code where a single function legitimately has
*several* independent, unrelated correctness properties (rounding
direction, exponent-arithmetic ordering, representation-boundary
handling) — a generator that proposes "the round-trip must hold" and
"comparisons must be ordering-consistent" is reasoning soundly about
real risk, it's just not guaranteed to also propose "the two
normalization steps must be sequenced correctly," a narrower,
implementation-detail-shaped claim that requires noticing the specific
order of two adjacent lines, not a general numerical-correctness
instinct.

**Concrete fix**: none specific to this bug — this is the same
"generation is not exhaustive per function" limitation already
documented for `max_semantic_properties`
(`RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md`'s own follow-up section:
raising the cap increases the odds of covering more DISTINCT mechanisms,
it doesn't guarantee covering every one). A generic mitigation (multiple
independent generation samples merged, not just a higher single-call
cap) would help here more than a single larger cap would, since the
issue is diversity of proposed mechanisms per function, not total count.

---

## forte H-03 — `Ln.ln()` accepts negative/zero input without validation

**Ground truth** (`findings/H-03.md`, `src/Ln.sol:63-77`): `ln()` never
checks the sign bit before proceeding — negative or zero input produces
garbage instead of reverting.

**Evidence chain — `Ln.sol` is fully visible and substantively
investigated this run** (the structural fix this whole plan implements
worked correctly): 4 distinct real properties target `Ln.sol`/`ln()`
directly. The closest is:

> `semantic__semantic__89b3d89ffd51` → **PASS**: "After decoding input,
> `Ln.ln` returns `ln_helper(mantissa, exponent, inputL)` directly at
> `src/Ln.sol:63-76`. The only bypass is a mathematical one, for which
> `ln` returns zero; tracing `ln_helper` with the decod[ed values
> confirms...]"

The investigator's own words name the *exact* real defect — an input
that bypasses `ln`'s intended domain and produces a silent zero instead
of a revert — and still resolved PASS.

**Classification: hybrid — property-obligation wording is too weak,
compounded by an investigation that traced the mechanism correctly but
didn't treat "silently returns zero" as a violation.** The property's
own statement (reconstructable from its `PASS` framing) most likely
asked something like "ln must return `ln_helper`'s result" or "must not
revert unexpectedly" — a claim a silent-zero-return technically
satisfies. It did NOT ask "must revert for negative or zero input,"
which is H-03's actual normative claim. This is different from forte
H-01 (pure absence of the right mechanism) and different from canto H-01
(right property, callee-boundary reasoning gap): here, the *investigator
found the real bug in its own reasoning trace* and still didn't flag it,
because the property being checked wasn't actually H-03's claim, just
adjacent to it.

**Why, as a security expert**: this is the sharpest version of a
recurring theme in this project's prior root-cause reports — a
property phrased around "correct behavior for valid inputs" instead of
"explicit rejection of invalid inputs" lets exactly this kind of silent-
degradation bug hide in plain sight, even when the investigator's own
counterexample search surfaces the precise mechanism. The gap isn't
visibility or reasoning depth here — it's that the object being
verified (the property's own text) wasn't the security-relevant claim.

**Concrete fix**: a targeted `semantic_property_generation.py` system-
prompt addition for any function taking a numeric input to a
domain-restricted mathematical operation (log, sqrt, division, etc.):
explicitly prompt for a **companion domain-validation property**
("`X` must revert for inputs outside its valid domain") whenever a
"produces the correct result" property is proposed for the same
function — so the presence of a correctness property doesn't crowd out
its own validation counterpart. Complements (does not duplicate) H-01
phi's existing "signature-domain-binding" prompt-hint recommendation
from the prior root-cause report — this is the same "the model reasons
about the presence of a check, not its absence" shape.

---

## phi H-03 — `Cred.sol` `shareBalance` `EnumerableMap` bloat DoS

**Ground truth** (`findings/H-03.md`, `Cred.sol`'s
`_updateCuratorShareBalance`): a curator's entry is never removed from
the `EnumerableMap` when their balance returns to zero; after ~4000
distinct historical holders, `CuratorRewardsDistributor`'s enumeration
of that map exceeds the block gas limit, permanently blocking reward
distribution.

**Evidence chain — the single most confirmed, structural gap in this
entire report.** `_updateCuratorShareBalance` — the *exact* function
H-03 names — received **three independent real investigations this
run alone**, via three different EthTrust structural requirements:

> `req-1-use-c-e-i::loc1` → **PASS**: "`Cred._updateCuratorShareBalance`
> at `src/Cred.sol:666-682` only reads and updates Cred storage through
> internal EnumerableMap operations and internal bookkeeping functions.
> It makes no external call."
>
> `req-2-external-calls::loc1` → **PASS**: "`_updateCuratorShareBalance`
> ... invokes no external address or contract; all operations are
> internal storage bookkeeping."
>
> `req-3-external-calls::loc1` → **PASS**: "`_updateCuratorShareBalance`
> ... only reads and writes local mappings and EnumerableMap storage.
> ... neither performs an external message ca[ll]"

Every one of these three verdicts is **factually correct** — the
function genuinely makes no external call and has no reentrancy
exposure. The requirements applied to it (checks-effects-interactions,
external-call safety) are simply the **wrong shape of question** for a
storage-growth/gas-limit-DoS defect. This is not unique to today's
run: neither the earlier semantic-only-12-property run, the
semantic-only-78-property run, nor this combined run (three
independent, differently-configured attempts across the whole session)
ever produced a property asking "does this `EnumerableMap` entry ever
get removed" or "can unbounded growth here exceed gas limits elsewhere."

**Classification: `REQUIREMENT_TAXONOMY_GAP` — confirmed, reproducible,
present in BOTH sub-systems.** This is qualitatively different from
every other miss in this report: it is not that generation didn't
sample the right property this run (forte H-01/phi H-07's pattern), and
it's not an investigation-reasoning gap on an otherwise-correct property
(canto H-01/forte H-03's pattern). Every EthTrust requirement category
that got ROUTED to this function is genuinely inapplicable to this bug
class, and the semantic generator — across three independent attempts
at three different property budgets — has never once proposed the
"unbounded resource growth" property shape at all, for this function or
any other, in this entire session's evidence.

**Why, as a security expert**: "does this external call/reentrancy
pattern hold" and "does this state mutation stay bounded over the
protocol's operational lifetime" are fundamentally different classes of
claim — the first is checkable by reading one function in isolation,
the second requires reasoning about the function's behavior *integrated
over many calls across the contract's lifetime* (does this map only
ever grow? is there a caller-facing enumeration elsewhere that would
choke on that growth?). Neither RTF's static 81-requirement EthTrust
corpus (at least the categories with real evidence/applicability on this
target) nor a single-pass LLM property generator naturally produces this
shape of claim without being specifically prompted for it.

**Concrete fix**: this needs a genuinely new capability, not a tuning
fix to the existing generator or a different requirement routing —
either (a) a new EthTrust-corpus-adjacent requirement/predicate category
specifically for "unbounded on-chain data structure growth reachable
from user-triggered code, enumerated or iterated elsewhere in the
protocol" (a real, nameable, recurring Solidity bug class independent of
this specific audit), or (b) a targeted semantic-generation prompt hint
for any `EnumerableSet`/`EnumerableMap`/array-append pattern: "is there
a corresponding removal path for every insertion path, and if not, is
the resulting structure ever iterated by a function with a bounded gas
budget." This is the single highest-leverage remaining gap identified
in this report — it's the only one confirmed absent across every
variant of the pipeline tried this session.

---

## phi H-07 — `updateArtSettings` lets artists freely change URI/royalties/soulbound status

**Ground truth** (`findings/H-07.md`, `PhiFactory.updateArtSettings`):
callable by the art's creator (not just the contract owner) with no
restriction on which settings can be changed post-creation, letting an
artist unilaterally alter royalty recipients or soulbound status after
holders already own the NFT.

**Evidence chain**: exactly one property this run even mentions
`updateArtSettings`:

> `req-1-use-c-e-i::loc3` → **FAIL**: "`PhiFactory._createNewNFTContract`
> writes `arts[newArtId].artAddress`... calls `newArt.initialize`...
> and only afterward writes `credNFTContracts`... `createArt` is
> `nonReentrant`, but `updateArtSettings` is not and can operate on the
> partially initialized art."

This is a real, correct finding — and it's what caught H-04 this run
(a CEI/reentrancy-shaped explanation of a defect touching the same
function). It has **nothing to do** with H-07's actual claim (who is
authorized to call this function, and should they be able to change
these specific settings). No property this run asks the access-control
question about `updateArtSettings` at all.

**Classification: `GENERATION_COVERAGE_GAP`, confirmed as pure
sampling non-determinism, not a capability gap.** This is the clearest
non-determinism evidence in the whole report: the EARLIER semantic-
only 78-property run (same target, same day, different independent
generation sample) DID produce exactly the missing property —
`"PhiFactory.updateArtSettings must only be callable by the owner"` —
and that one property correctly caught BOTH H-04 and H-07 together
(`RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md`'s own §"Follow-up" section,
2026-08-15). In this run's own independent generation sample, that
specific property was never proposed; H-04 got caught anyway, via an
unrelated structural CEI finding that happens to touch the same
function region — a coincidence of code proximity, not a substitute for
the missing access-control property.

**Why, as a security expert**: this is a textbook "obvious to a human
auditor, but not guaranteed by a single LLM sample" case — "who can call
this state-mutating function, and is that appropriate" is one of the
most standard access-control questions in any Solidity review, and this
project's own generator has already proven (in a different run) that it
CAN produce this exact property reliably enough to be found once. The
miss here is entirely about run-to-run generation variance, not about
whether this class of property is within the generator's reach.

**Concrete fix**: none specific to this bug beyond the general fix for
Pattern 1 below (multiple independent generation samples per function/
per audit, deduplicated and merged, rather than trusting a single
generation call's coverage) — this is the cleanest possible evidence
that such an investment would pay off, since the missing property is
already proven producible.

---

## Patterns across all 5 misses

| Miss | Right requirement/function investigated? | Right verdict question asked? | Classification |
|---|---|---|---|
| canto H-01 | Yes, 3x (`req-2-block-data-misuse`) | No — checked internal consistency, not the callee's own semantics | `INVESTIGATION_REASONING_GAP` |
| forte H-01 | Function yes, this specific bug no | N/A — never proposed | `GENERATION_COVERAGE_GAP` (precision-competing) |
| forte H-03 | Yes — investigator named the exact mechanism | No — property's own wording didn't require rejecting the bypass | Hybrid: weak obligation wording + reasoning |
| phi H-03 | Function yes, 3x — but wrong requirement categories entirely | No — CEI/external-call questions are the wrong shape | `REQUIREMENT_TAXONOMY_GAP` |
| phi H-07 | No — absent this run, present in an earlier run | N/A — never proposed | `GENERATION_COVERAGE_GAP` (pure non-determinism) |

**Pattern 1 — Non-deterministic single-sample generation is a real,
quantified source of variance, independent of the pipeline's
capability.** phi H-07 is direct, controlled evidence: the exact
property needed was produced by this same generator, on this same
target, in a *different* run earlier the same day. canto H-01's own
history (caught in the ORIGINAL 5-entry comparison, missed here) is the
same phenomenon from the opposite direction. This is not a defect to
fix so much as a property of one-shot LLM sampling that this project's
own aggregate numbers already partially average out across 5 targets —
but it means any SINGLE run's specific miss list should not be read as
"the pipeline cannot find X," only as "this specific sample didn't."

**Pattern 2 — Investigation reasoning defaults to intra-function/
intra-contract self-consistency checks, and under-weights cross-
component semantic contracts at external-call boundaries.** canto H-01
is the clean example: the right question ("is this value used
consistently") got asked and answered honestly; the harder, correct
question ("does the thing I'm calling interpret this value the same
way I do") did not. This is a reasoning-depth gap, not a coverage gap,
and is the kind of miss that persists even as generation and
compilation-scope both improve — a distinct, separate lever from
everything else fixed this session.

**Pattern 3 — A property's own wording can be technically satisfied by
a real security defect, when it's framed around "correct behavior" but
not "explicit rejection of invalid states."** forte H-03 shows this
starkly: the investigator's own prose describes the exact real bug and
still resolves PASS, because the property never asked the rejection
question. This is a generation-prompt-shape issue (properties need a
"must reject invalid X" companion, not just "must correctly compute Y
for valid X"), fixable with a targeted, evidenced prompt addition — not
a reasoning failure at the investigation stage.

**Pattern 4 — Some real bug classes have no matching requirement SHAPE
anywhere in the system yet, and this is confirmed, not merely
suspected.** phi H-03 is the standout: three independent real
investigations, correct in their own narrow terms, all miss because
NOTHING in either the static EthTrust corpus categories applied to this
function or the semantic generator's own repertoire (checked across
three separate runs this session) asks about unbounded-growth/gas-DoS.
This is the one miss in this report that cannot be explained by
sampling variance or investigation depth — it needs a genuinely new
requirement or prompt category to close, not a rerun.

**What these patterns together imply, prioritized by leverage**: (1)
phi H-03's requirement-taxonomy gap is the highest-value, most
tractable next fix — a single new prompt/requirement category for
unbounded-state-growth patterns would plausibly generalize well beyond
this one finding, since it's a common, nameable Solidity bug class, not
audit-specific. (2) forte H-03's "reject invalid input" companion-
property prompt hint is similarly targeted and cheap. (3) canto H-01's
cross-boundary-semantics reasoning gap is real but harder to fix
generically — it may need a dedicated counterexample-search sub-step
in the investigation prompt, with real risk of adding cost/noise to
every investigation for a benefit that's specific to external-call-
parameter-semantics bugs. (4) Pattern 1 (non-determinism) is not a bug
to fix at all — it's a property of the architecture that argues for
ensembling/multiple-sample generation as a future investment, not a
targeted patch.
