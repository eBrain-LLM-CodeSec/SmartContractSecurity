# RTF v2 5-entry comparison: root cause of every miss

Forensic trace over artifacts already on disk from the completed 5-entry
comparison run (SLURM job `17215379`). No new LLM/Codex calls made. Ground
truth read from each audit's `findings/H-XX.md` and `config.yaml` (both
audits are already frozen/graded in this project's own record, so this is
post-hoc forensic analysis, not benchmark-tuning). Real vulnerable source
read directly to verify every mechanism independently, not taken from the
judge's paraphrase. Companion to `RTF_V2_TEMPO_FEEAMM_ROOT_CAUSE.md` (already
done) and `RTF_V2_5ENTRY_COMPARISON_REPORT.md` (liquid-ron, already done) —
this file covers the 11 remaining misses: canto H-02, forte H-01–H-05, phi
H-01/H-02/H-03/H-04/H-06.

---

## canto H-02

**Ground truth** (`findings/H-02.md`, confirmed live at
`src/LendingLedger.sol:65`): `update_market()`'s reward-accrual loop computes
`epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH` (the epoch `i` currently belongs
to) but then computes `nextEpoch = i + BLOCK_EPOCH` instead of
`epoch + BLOCK_EPOCH`. When `i` is not epoch-aligned (e.g. `market.
lastRewardBlock` sits mid-epoch), `blockDelta = min(nextEpoch, block.number)
- i` under-measures how many blocks remain in the *current* reward-rate
epoch before the boundary, causing the loop to apply the wrong
`cantoPerBlock[epoch]` rate to blocks that actually belong to the next
epoch — a reward-accounting error that can inflate `accCantoPerShare`.

**Evidence chain**: `semantic_properties_raw.json` for canto has exactly 12
properties (0 rejected at either generation or grounding — verified
directly). None targets `nextEpoch`/epoch-boundary loop arithmetic. The
closest is:
> `numerical: LendingLedger.marketInfo must track the last-claimed block
> epoch per market such that rewards are only accrued for blocks between
> the previous epoch and the current epoch, and must not allow rewards to
> be accrued for blocks before the last-claimed epoch.`

This asks about *double-accrual across separate `update_market()` calls*
(no re-accruing already-paid blocks), which the code does correctly.
H-02 is a *within-one-call* rate-misattribution bug at an epoch boundary —
a materially different, more specific arithmetic claim the generator never
proposed.

**Classification: GENERATION_COVERAGE_GAP.**

**Why, as a security expert**: this bug requires reasoning about a
*multi-variable interaction inside one loop body* — the relationship
between a loop's rate-lookup key (`epoch`) and its boundary-advance
variable (`nextEpoch`), and specifically that they must derive from the
*same* base value. `protocol_context.md`/`ProjectManifest` expose function
and state-variable *names*, not loop-body control flow or intra-function
variable-dependency structure — there's no signal in what the generator
sees that would prompt "check whether these two locally-scoped variables
that both reference `BLOCK_EPOCH` are derived consistently." This class of
bug (a loop-local off-by-a-derivation-source error) is invisible to a
generator working from a contract-level interface summary; it requires
function-body-level static analysis or a prompt that explicitly asks about
per-loop-iteration invariants, not just cross-call state consistency.

**Concrete fix**: extend `ProjectManifest`/`protocol_context.md` to surface,
per function, a lightweight structural summary of loop bodies containing
external-state-dependent computations (e.g. "this function contains a
`while`/`for` loop with N distinct locally-derived variables feeding an
external call") — enough to prompt the generator to ask "are these
loop-local values derived consistently across iterations," without
requiring full control-flow-graph reasoning.

---

## forte H-01 — sqrt exponent off-by-one (72-digit adjustment ordering)

**Ground truth** (`findings/H-01.md`, confirmed live at `src/Float128.sol`,
lines ~734–743 in the current checkout): in `sqrt()`'s large-mantissa path,
digit-count normalization (`if (rMan > MAX_L_DIGIT_NUMBER) { rMan /= BASE;
++rExp; }`) happens *before* halving (`rExp = rExp / 2`), but halving must
happen first — halving a pre-adjustment value and halving a
post-adjustment value are not equivalent when the adjustment itself changes
`rExp`'s parity/magnitude. Off-by-one in the result exponent, verified by
the finding's own PoC (`float / (result*result)` should be ≈1, is actually
>99).

**Evidence chain**: raw property proposed and grounded cleanly:
> `numerical: Float128.sqrt must produce a result r such that Float128.
> mul(r, r) is approximately equal to the input value, within the
> precision limits of the Float128 representation.` (`semantic__numerical__
> fd1d6c14310b::loc0`)

This property's *statement* is exactly the right shape to catch H-01 (a
correctly-executed round-trip check with a large-mantissa input would
surface the ~10x/2338-vs-2339-magnitude discrepancy the finding's own PoC
demonstrates). It was clustered into `cluster_000`, which split twice
(depth 2) down to leaf `cluster_000_a_a` — property `fd1d6c14310b` paired
with `semantic__semantic__0254d73a582d` (an unrelated `lt`/`gt` mutual-
exclusivity property). `2025-04-forte__Float128__cluster_000_a_a_gstream.
jsonl` shows real activity — `{'thread.started': 1, 'item.completed': 29,
'turn.started': 1, 'item.started': 25}` — 29 genuine tool-call events, but
**no `turn.completed` event**, and no matching `_gout.txt` exists anywhere
under `rtf_scratch/`. The investigation started, was actively exploring,
and never finished within `codex_timeout_s=600`.

**Classification: INVESTIGATION_TIMEOUT.** Identical failure signature to
`tempo-feeamm`'s already-documented root cause — a correctly-targeted
property, correctly grounded, never actually investigated.

**Fix**: same as documented for tempo-feeamm — raise `max_split_depth`
so a stubborn cluster reaches single-property leaves, or retry a timed-out
leaf once before falling back to `INCONCLUSIVE`.

---

## forte H-02 — sqrt(0) uses `stop()`, silently halting execution

**Ground truth** (`findings/H-02.md`): `sqrt()`'s assembly block does
`if iszero(a) { stop() }` — the EVM `STOP` opcode, which halts execution
of the *entire call* with success status and *no return value written*,
rather than returning `packedFloat.wrap(0)` or reverting. Any caller
expecting a normal return silently gets undefined/zeroed output with no
error signal.

**Evidence chain**: same property (`fd1d6c14310b`, "sqrt must produce r
such that mul(r,r)≈input") is the only one whose text plausibly reaches
this code path — a thorough investigation of "does sqrt behave correctly
for all inputs" would naturally include the boundary case `input=0`. Same
leaf cluster (`cluster_000_a_a`), same timeout, same missing
`turn.completed`.

**Classification: INVESTIGATION_TIMEOUT** (same underlying failure as
H-01 — one un-investigated cluster covers both).

---

## forte H-03 — `Ln.ln()` accepts negative/zero input without validation

**Ground truth** (`findings/H-03.md`, confirmed at `src/Ln.sol:63-77` per
the finding): `ln()` extracts `mantissa`/`exponent`/`inputL` from the
packed float via assembly but never checks the sign bit
(`MANTISSA_SIGN_MASK`) before proceeding — negative or zero inputs produce
`ln(|input|)`-shaped garbage instead of reverting.

**Evidence chain**: `semantic_properties_raw.json` has **zero** properties
mentioning `Ln` or `ln(` anywhere (verified by direct string search — 0
hits). This traces to a structural, not a reasoning, cause: the comparison
run's entry file for forte was `src/Float128.sol`; `protocol_context.md`'s
own "Contracts and inheritance" section (identical across every cluster's
copy, confirmed) lists exactly two contracts — `Float128` and `Uint512` —
**`Ln` is not present.** `Ln.sol` imports `Float128.sol` (uses its types),
not the reverse, so compiling `Float128.sol` as the sole entry never pulls
`Ln.sol` into the Slither compilation unit, even though the orchestration
script's own `scope_files` list for this audit explicitly included
`"src/Ln.sol"`. `ProjectManifest.from_slither` can only ever expose
contracts that are part of the *compiled* unit — scope filtering happens
*after* generation, on properties that already exist; it cannot inject
visibility the compilation never had.

**Classification: GENERATION_COVERAGE_GAP — entry-file compilation scope,
not a reasoning or prompt-quality issue.** The generator could not
possibly have proposed a `Ln.ln` property because `Ln` was never part of
what it was shown, full stop.

**Concrete fix (structural, not "improve the prompt")**: `semantic_only_
driver.run_semantic_investigation` currently accepts exactly one
`entry_sol_file`. For a multi-file scope where sibling files aren't
mutually imported (a real, common Foundry-library-project shape — this
exact same cause independently recurs for phi below), the driver needs to
either (a) compile each `scope_files` entry that isn't already reachable
from the primary entry as an *additional* compilation unit and merge their
`ProjectManifest`s before generation, or (b) run one generation pass per
disconnected scope-file cluster. This is the single most generalizable,
mechanical fix available from this trace — it independently explains 3 of
the 11 misses in this report (see phi H-03/H-06 below).

---

## forte H-04 — `eq()` mishandles `L_MANTISSA_FLAG` across mantissa sizes

**Ground truth** (`findings/H-04.md`, confirmed at `src/Float128.sol:1070-
1072`): `eq(a, b)` is implemented as raw `packedFloat.unwrap(a) ==
packedFloat.unwrap(b)` — a bitwise comparison of the packed representation.
Two packed floats that encode the *same mathematical value* but differ in
mantissa size (38-digit "M" vs. 72-digit "L", which sets/clears
`L_MANTISSA_FLAG`) have different bit patterns and are wrongly judged
unequal.

**Evidence chain**: one property was proposed adjacent to this exact
function:
> `semantic: Float128.eq must be reflexive: for any valid packed Float128
> value a, Float128.eq(a, a) must return true.` (`semantic__semantic__
> 4ff118b73ac5::loc0`)

This property's cluster (`cluster_000_b_a`) **did** complete —
`cluster_000_b_a_gout.txt` has a real `PASS` verdict. The investigator's
own transcript is unusually precise evidence here: it read
`Float128.sol:1070-1072` (the exact vulnerable lines), explicitly
enumerated edge cases including *"L-size values (MANTISSA_L_FLAG_MASK bit
set)"* in its counterexample search, and correctly concluded
`unwrap(a) == unwrap(a)` is tautologically true for *any* single value
`a` — which it is. **The investigator engaged with the correct code and
the correct flag, and reasoned soundly about the question it was actually
asked.** The question itself — reflexivity, `eq(a,a)` — is provably
unable to expose H-04, whose defect is specifically about `eq(a,b)` for
two *different* representations of one *equal* value. Reflexivity and
cross-representation-equality are logically independent claims about the
same function; satisfying one says nothing about the other.

**Classification: GENERATION_COVERAGE_GAP** (a precision/framing gap, not
a coverage-zero gap and explicitly not a reasoning failure — the one
completed investigation in this whole 11-miss set that most directly
demonstrates the difference between "the investigator got it wrong" and
"the investigator correctly answered a different, weaker question").

**Why, as a security expert**: `eq`-mishandling-multiple-representations
is a specific, well-known bug class in any system with more than one valid
encoding of the same logical value (here, size-variant packed floats;
elsewhere, e.g. non-canonical integer encodings, padded byte strings,
normalized-vs-unnormalized fractions). A generator that already knows a
type has *two mantissa sizes* (the codebase's own doc comment says so
explicitly, quoted in the finding) needs a specific nudge toward
"multiple representations of one value" as an equality-testing hazard —
`protocol_context.md` doesn't currently surface type-level encoding
variants (dual bit-widths, packed flags) as a distinct signal class the
way it surfaces, say, accounting- or lifecycle-relevant state variables.

**Concrete fix**: add a `protocol_context.md` section (or extend the
existing accounting-relevant-state-variables heuristic) that flags
type-level bit-packing/multi-representation patterns — e.g. any constant
or flag name matching `*_FLAG`/`*_MASK` alongside a documented "N-bit or
M-bit" comment — as a distinct "representation-variance" signal, since
equality/comparison functions over such types are a recurring, specific
audit target.

---

## forte H-05 — precision loss in `toPackedFloat`

**Ground truth** (`findings/H-05.md`, at `src/Float128.sol` near the
`toPackedFloat` mantissa-size-selection logic): result mantissa size
(M vs. L) is chosen from `exponent` alone, not the mantissa's actual digit
count; in the range `(MAX_M_DIGIT_NUMBER, MIN_L_DIGIT_NUMBER)` this
downcasts an L-sized mantissa into M format via division, silently
truncating up to ~33 digits of precision.

**Evidence chain**: the one property closest in spirit is:
> `semantic: Float128.decode must correctly extract the mantissa and
> exponent from a packed Float128 value such that the decoded value equals
> the original mathematical value encoded by Float128.toPackedFloat.`
> (`semantic__semantic__726d37a23700::loc0`)

An encode-then-decode round-trip check, if actually run against a mantissa
in the vulnerable range, would surface exactly this precision loss (decode
would return the truncated value, not the original). This property was
clustered into `cluster_000_b_b` (the sibling leaf of the completed
`cluster_000_b_a` above, both children of `cluster_000_b`).
`2025-04-forte__Float128__cluster_000_b_b_gstream.jsonl`:
`{'thread.started': 1, 'item.completed': 31, 'turn.started': 1,
'item.started': 23, 'item.updated': 2, 'error': 1}` — real exploration (31
tool calls) plus a logged `error` event, but again **no `turn.completed`**
and no `_gout.txt`.

**Classification: INVESTIGATION_TIMEOUT** — a third, independent instance
of the same failure mode within this one audit's run. Notably,
`cluster_001` (a 2-property cluster unrelated to any of the 5 graded bugs)
also split into two single-property leaves (`cluster_001_a`,
`cluster_001_b`) and **neither of those completed either** — 5 of this
run's ~9 real investigation attempts for forte never produced a
`turn.completed`. This is not one unlucky cluster; it's a systemic pattern
specific to this target, plausibly because verifying fixed-point
arithmetic/assembly-level bit manipulation genuinely requires more
investigator turns per property than a typical access-control or
event-emission check, making forte's clusters disproportionately likely to
exceed a fixed 600s budget regardless of cluster size.

---

## phi H-01 — cross-chain signature replay in `signatureClaim`

**Ground truth** (`findings/H-01.md`, confirmed at `src/PhiFactory.sol`
around the `signatureClaim` decode/verify block): `abi.decode(encodeData_,
(uint256, address, address, address, uint256, uint256, bytes32))` decodes
a `chainId` field (the middle `uint256`) that is then **never compared
against `block.chainid`** — the signature-validity check
(`_recoverSigner(...) != phiSignerAddress`) only confirms *who* signed,
not *for which chain*. A signature obtained on chain B is fully valid and
replayable verbatim on chain A.

**Evidence chain**: one property targets this exact function:
> `authorization: PhiFactory.signatureClaim must revert if the recovered
> signer from the provided signature does not equal PhiFactory.
> phiSignerAddress...` (`semantic__authorization__a9498ed56c34::loc0`)

This cluster (`cluster_001`) completed cleanly (no split, no timeout — the
whole phi run finished in 507s with zero timeouts, unlike forte). The
investigator's transcript is exact and correct: it read
`PhiFactory.sol:327-344` (the *exact* lines containing the vulnerable
`abi.decode` — i.e. it had the chainId-dropping code in its context
window) plus `ECDSA.sol`, verified the signer-comparison logic is sound,
explicitly checked whether `phiSignerAddress` could degrade to
`address(0)`, and correctly returned `PASS` — because the property only
asked "is the recovered signer correct," and the code genuinely does get
that part right. The property never asked whether the *signed payload*
itself is bound to the executing chain.

**Classification: GENERATION_COVERAGE_GAP** (precision/framing gap — the
investigator read the vulnerable line and reasoned correctly about a
narrower, adjacent, satisfied claim).

**Why, as a security expert**: replay-across-execution-contexts (chains,
in this case; elsewhere: replay across contract instances, across time
via missing nonces, across function selectors via missing domain
separators) is a *distinct* security question from "is the signature
cryptographically valid." A signature-verification property needs to ask
not just "was this signed by the right key" but "does the signed payload
uniquely commit to *this* execution context" — chain id, contract
address, a nonce/sequence number. The generator here treated signer
identity as the complete authorization question.

**Concrete fix**: this is a genuine, recurring, nameable pattern —
"signature verification without full replay-domain binding" — general
enough to warrant a dedicated prompt hint in `semantic_property_generation.
py`'s system prompt for any EIP-712/ECDSA-signature-consuming function
found in the manifest: explicitly ask the generator to also produce a
property about what the signed payload binds to (chain, contract, nonce,
specific caller) whenever a signature-recovery pattern is detected — a
targeted, mechanism-specific addition, not a blanket "be more thorough"
instruction.

---

## phi H-02 — signature replay / front-run in `createArt`

**Ground truth** (`findings/H-02.md`, at `src/PhiFactory.sol:196-213`):
`createArt()`'s signature check doesn't bind the signature to the specific
submitted `CreateConfig` (artist, royalties receiver, BPS, etc.) or to a
specific caller — an attacker can observe a pending `createArt` tx in the
mempool, front-run it reusing the *same* signature but supplying their own
`CreateConfig`, and become the royalties recipient/artist of record.

**Evidence chain**: the only property targeting `createArt` at all is:
> `accounting: PhiFactory.createArt must increment PhiFactory.artIdCounter
> exactly once per successful call and store the new art configuration in
> PhiFactory.arts under the new artId.` (`semantic__accounting__
> c558162872c2::loc0`)

Purely about counter bookkeeping — no mention of signature scope, config
binding, or front-running. `rejected_properties.json` for phi shows 0
rejections at either stage, confirming nothing relevant was even proposed
and discarded — this is a pure absence.

**Classification: GENERATION_COVERAGE_GAP.**

**Why**: same underlying pattern as H-01 (signature-binding-scope), but on
a *different* function the generator happened to characterize purely by
its bookkeeping side-effect (`artIdCounter++`) rather than by its
signature-gated entry-point nature. This reinforces H-01's proposed fix:
a signature-recovery-aware prompt hint would likely have produced a
relevant property here too, since `createArt` and `signatureClaim` share
the exact same missing-binding defect class.

---

## phi H-03 — `shareBalance` `EnumerableMap` bloat DoS (in `Cred.sol`)

**Ground truth** (`findings/H-03.md`, at `Cred.sol`'s
`_updateCuratorShareBalance`): selling all shares zeroes a curator's
balance but never removes their `EnumerableMap` entry; after ~4000
distinct historical holders, `CuratorRewardsDistributor`'s enumeration of
that map exceeds the block gas limit, permanently blocking reward
distribution for that cred.

**Evidence chain**: `semantic_properties_raw.json` for phi has **zero**
mentions of `Cred`, `shareBalance`, or `CuratorRewardsDistributor`
(verified by direct search). `protocol_context.md`'s "Contracts and
inheritance" section (identical across all phi clusters, confirmed) lists
only `PhiFactory` and its OpenZeppelin/solady dependency chain
(`Address`, `ContextUpgradeable`, `ECDSA`, `ERC1967Utils`, `IBeacon`,
`Initializable`, etc.) — **no `Cred`, no `CuratorRewardsDistributor`.**
The comparison run's phi entry file was `src/PhiFactory.sol`; `Cred.sol`
is a sibling contract PhiFactory does not import.

**Classification: GENERATION_COVERAGE_GAP — identical structural cause to
forte's H-03 (Ln.sol invisibility).** Not a reasoning or prompt-quality
issue; `Cred.sol` was never part of the compiled unit the generator saw.

**Fix**: identical to forte H-03's — multi-entry-compilation support in
`semantic_only_driver.py`. This is now confirmed as a *recurring* pattern
(2 of 2 audits in this comparison whose real scope spans multiple,
non-mutually-importing top-level contracts lost coverage on the
non-primary-entry contract entirely) — the single highest-leverage fix
identified in this whole report, since it mechanically explains 3 of 11
misses (forte H-03, phi H-03, phi H-06) with one engineering change.

---

## phi H-04 — forced `endTime` re-extension enables backrun minting

**Ground truth** (`findings/H-04.md`, at `src/PhiFactory.sol`'s
`updateArtSettings`, line ~242 per the finding): to change unrelated
settings (URI, `soulBounded`, royalties) after an art's claim window has
closed, the artist is *forced* by a validation check to also set
`endTime >= block.timestamp` — which reopens the minting window. An
attacker watching the mempool can backrun the artist's `updateArtSettings`
call with a `merkleClaim`/mint call that now passes the (attacker-
unintended) re-extended `endTime` check.

**Evidence chain**: the only property touching `updateArtSettings` is the
broad access-control one that (correctly) caught H-07:
> `authorization: ...updateArtSettings... must only be callable by the
> contract owner...`

Nothing addresses `updateArtSettings`'s time-window/`endTime` semantics
specifically, or the backrun-timing hazard. `semantic_properties_raw.json`
has no property mentioning `endTime`, `startTime`, or a minting-window
concept at all.

**Classification: GENERATION_COVERAGE_GAP.**

**Why, as a security expert**: this is a *temporal/ordering* hazard — a
side effect of one legitimate state-changing call (re-extending a
deadline as an unavoidable consequence of an unrelated update) creating a
window another transaction can exploit via transaction ordering
(front-run/back-run). This is a materially different reasoning shape from
either "is this value accounted for correctly" (accounting/numerical
properties, which the generator produces readily) or "is this caller
authorized" (the generator's other strong suit, evidenced by catching
H-07 correctly). Nothing in `protocol_context.md` currently flags
functions whose parameter validation has *side effects on unrelated
protocol state* (here: a "just update the URI" call forcibly mutating the
claim deadline) as a distinct, MEV/backrun-relevant hazard class.

**Concrete fix**: extend the accounting-relevant/lifecycle heuristics in
`protocol_context.py` to flag functions where a validation `require`/`if`
on one parameter has the *side effect* of changing a different, security-
relevant state variable's semantics (e.g. a time-window/deadline field)
as part of the same call — a narrow, mechanical pattern (validation logic
that writes to a field not explicitly requested by the caller) detectable
via the same kind of state-variable-touch analysis
`_graph_enrichment`/`_slither_enrichment` already do, just not yet applied
to this specific "forced side-effect" shape.

---

## phi H-06 — reentrancy in `Cred.sol` cred-creation/share-purchase refund flow

**Ground truth** (`findings/H-06.md`, at `Cred.sol`'s
`_createCredInternal`/`buyShareCred`): buying shares issues an ETH refund
for excess payment before the cred's `credIdCounter` is incremented,
giving an attacker's refund-receiving contract a reentrancy window to
re-enter cred creation/share trading and manipulate accounting before the
counter advances, ultimately draining the contract.

**Evidence chain**: same as H-03 — `Cred.sol` is entirely absent from the
compiled manifest phi's entry (`PhiFactory.sol`) produced. No property
could reference `_createCredInternal`, `buyShareCred`, or any Cred-side
refund logic because none of those symbols were ever visible to the
generator.

**Classification: GENERATION_COVERAGE_GAP — same structural cause as
H-03/forte-H-03.** Notably, RTF v2 *did* correctly generate and ground a
genuine reentrancy-shaped property elsewhere in this same comparison run
(liquid-ron's `state_consistency` property about `LendingLedger`
reentrancy-adjacent claim-transfer ordering, and tempo-feeamm's correctly-
targeted CEI-ordering property for `FeeAMM.burn`) — reentrancy reasoning
is not a blind spot for the generator in general; `Cred.sol` simply was
never in its field of view for this specific run.

---

## Summary table

| Finding | Classification | One-line root cause |
|---|---|---|
| canto H-02 | GENERATION_COVERAGE_GAP | No property tests loop-local `nextEpoch`-vs-`epoch` derivation consistency; existing property only covers cross-call double-accrual |
| forte H-01 (sqrt exponent off-by-one) | INVESTIGATION_TIMEOUT | Correct property generated+grounded; its leaf cluster (`cluster_000_a_a`) hit the 600s timeout at max split depth, no `turn.completed` |
| forte H-02 (sqrt(0) `stop()`) | INVESTIGATION_TIMEOUT | Same un-investigated cluster as H-01 |
| forte H-03 (ln domain validation) | GENERATION_COVERAGE_GAP | `Ln.sol` never compiled — entry was `Float128.sol`, which doesn't import `Ln.sol`; invisible to `ProjectManifest` |
| forte H-04 (eq L_MANTISSA_FLAG) | GENERATION_COVERAGE_GAP | Property tested reflexivity (`eq(a,a)`), not cross-representation equality (`eq(a,b)`, a≠b same value); investigator engaged correctly with the wrong-but-adjacent question |
| forte H-05 (toPackedFloat precision loss) | INVESTIGATION_TIMEOUT | Closest property (`decode` round-trip) in leaf `cluster_000_b_b`, timed out, no `turn.completed` |
| phi H-01 (cross-chain signature replay) | GENERATION_COVERAGE_GAP | Property tested signer validity only, not chain/domain binding of the signed payload; investigator read the vulnerable decode line and correctly answered the narrower question asked |
| phi H-02 (createArt signature replay) | GENERATION_COVERAGE_GAP | Only property on `createArt` is about counter bookkeeping; nothing about signature-to-config/caller binding |
| phi H-03 (shareBalance DoS) | GENERATION_COVERAGE_GAP | `Cred.sol` never compiled — entry was `PhiFactory.sol`, which doesn't import `Cred.sol`; invisible to `ProjectManifest` |
| phi H-04 (forced endTime extension) | GENERATION_COVERAGE_GAP | No property addresses `updateArtSettings`'s forced side-effect on the minting deadline; only its (correctly-used) access-control angle was tested |
| phi H-06 (Cred.sol reentrancy) | GENERATION_COVERAGE_GAP | Same as phi H-03 — `Cred.sol` never compiled/visible |

**8 GENERATION_COVERAGE_GAP, 3 INVESTIGATION_TIMEOUT, 0 REASONING_FAILURE,
0 GROUNDING_REJECTED, 0 CLUSTERING_OR_SCOPE_LOSS.**

Two of the 8 coverage gaps sub-classify further: **3 are pure entry-file
compilation-scope blindness** (forte H-03, phi H-03, phi H-06 — one
mechanical, high-leverage fix closes all three), and **5 are
property-framing precision gaps** where the relevant code (and, in 3
cases, the exact vulnerable line) was in the generator's or investigator's
context, but the proposed property tested a narrower, satisfied claim
adjacent to the real defect rather than the defect's own mechanism (canto
H-02, forte H-04, phi H-01/H-02/H-04). Three of those five cluster around
one nameable, generalizable pattern: **signature/authorization checks that
verify "is this valid" without verifying "is this bound to the intended
context"** (forte H-04's representation-binding, phi H-01's chain-binding,
phi H-02's config/caller-binding) — the single most actionable, specific
prompt-engineering target this trace surfaces.
