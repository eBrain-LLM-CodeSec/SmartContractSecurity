# Feasibility study: does the existing ProgramGraph bound Codex's file access without hiding evidence?

Executed per `PROGRAM_GRAPH_RELEVANCE_BOUNDARY_PREREGISTRATION.md`. Raw
artifacts: `phase_graph_relevance_artifacts/` (`graph_file_sets.json`,
`restricted_codex_results.json`, full Codex session traces under
`codex_sessions/`). Total live-call spend this batch: **$0.129** (7 real
Codex calls — 6 bundles + 1 retry of a formatting fluke). Session
cumulative: **$2.873** of the $5.00 cap.

**Headline result**: the existing, already-in-the-codebase
`ProgramGraph`/`BundleBuilder` — currently used by zero lines of RTF code
before this experiment — achieves **exact-match, 100% necessary-file
recall at 1 hop (G1) on all 6 controlled synthetic bundles**, confirmed
both analytically (against Arm C's previously-recorded unrestricted
trace) and live (a fresh, filesystem-enforced G1-restricted Codex run
reproduced every correct decision, 6/6). On the one real-repository
bundle, **G1/G2, and this experiment's own adaptive-G3 heuristic all
plateau at 75% necessary-file recall** (3 of 4 files) with **>99%
repository-size reduction** — the missing file is confirmed, by direct
graph traversal, to sit at exactly **4 hops**, a `GRAPH_DEPTH` limit, not
a missing relation or an unrepresentable construct. **Conclusion: the
existing graph is sufficient as a relevance boundary for controlled/
localized candidates and structurally promising but insufficiently deep
(at the G0–G3 levels tested here) for deep real-repository dependency
chains — do not build a new relevance classifier; extend hop depth /
targeted deeper expansion first.**

---

## 1. Existing graph capability audit

**RTF does not use this infrastructure today.** A repo-wide grep
(`grep -rln "a4v.graph\|a4v.slice\|ProgramGraph\|BundleBuilder" rtf/`)
returns nothing. `a4v/graph.py`'s `ProgramGraph` and `a4v/slice.py`'s
`BundleBuilder` are real, tested, working code — but they belong to the
sibling MGPR/Auditor system (`a4v/auditor.py`, `a4v/seeds.py`,
`a4v/tools.py` all import them; RTF's own `l5_predicates/predicates.py`
takes a bare `Slither` object and never touches this module). This
experiment is the first thing that wires the two together for RTF's own
candidates (`bundle_agent_experiment/graph_relevance.py`).

**Integration gap found and bridged, not silently assumed away**: RTF's
predicate `location` field is `f"{contract.name}.{func.name}"` (bare, no
parameter types — the exact string documented as AR-017's root cause).
The graph's function-node ids are
`f"fn::{f.canonical_name}"` = `"fn::Contract.function(paramtypes)"`.
`graph_relevance.py::resolve_seed_node` bridges these via a node-id
prefix match (not the node's `contract` data attribute — see the bug
below for why), raising on zero or multiple matches (an overload RTF's
bare location format can't disambiguate) rather than silently guessing.

**A real, previously-undocumented bug found and verified in
`ProgramGraph.build()`**: function-node creation has no `if fid not in
g` dedup guard (unlike modifier/statevar/callee creation, which all have
one). When a function is *inherited but not overridden* by a derived
contract, Slither's `contract.functions` includes it again during the
derived contract's own iteration, and `g.add_node(fid, ...,
contract=contract.name, ...)` **silently overwrites the node's
`contract` attribute to the last-processed (most-derived) contract's
name**, even though the node id itself (`canonical_name`-derived) still
correctly encodes the true declaring contract. Confirmed empirically on
the `unchecked_ecrecover_mutable_signer` fixture:
`fn::Auth.verify(bytes32,uint8,bytes32,bytes32)`'s `contract` attribute
reads `"AuthAdmin"`, not `"Auth"`, once `AuthAdmin` (which inherits
`verify` without overriding it) is processed. **Side effect, also
confirmed**: this same unguarded reprocessing adds a *spurious duplicate*
`DECLARES` edge from every inheriting contract straight to the shared
function node (`contract::AuthAdmin -> fn::Auth.verify(...) declares`,
in addition to the correct `contract::Auth -> ... declares` edge) — this
is the actual mechanism (not a deliberate inheritance-aware relation)
that pulled `AuthAdmin.sol` into G1 in §3 below. **Not fixed here**, per
this experiment's explicit "audit, don't fix" scope — worked around only
in this experiment's own node-resolution code (matches by node-id
prefix, immune to the attribute bug) and in `_node_file`'s state-variable
file resolution (parses the node id's own `"var::Owner.name"` prefix
rather than trusting the analogous, first-write-wins-but-still-fragile
`contract` attribute on `STATEVAR` nodes).

**Graph incompleteness observed live**: compiling the real PoolTogether
checkout produced one Slither-internal IR-generation error —
`Impossible to generate IR for TierCalculationLib.getTierOdds: 'NoneType'
object has no attribute 'parameters'` — meaning that specific function's
own `CALLS`/`STATE_READ`/`STATE_WRITE` edges are incomplete/absent in
the resulting graph. It was not on this experiment's causal path, so it
did not affect these results, but it is a real, general risk for graph
completeness on some real codebases, logged per task instructions §10.

### Capability matrix

| Relation | Implemented? | Reliable? | Gives file path? |
|---|---|---|---|
| candidate → containing file | Yes (`file` attr on `FUNCTION` node) | Yes | Direct |
| caller (fn ← fn) | Yes (`CALLS` + `EXTERNAL_CALL` in-edges) | Partial — `BundleBuilder.callers` unions both edge kinds via raw `predecessors()`, not separately queryable as internal-only vs external-only without extra filtering | Direct |
| callee (fn → fn), internal | Yes (`CALLS`) | Reliable | Direct |
| callee, external/high-level | Yes (`EXTERNAL_CALL`) | Reliable when Slither resolves the target; unresolved targets become a generic `"ext::Contract.func"` node with no file | Direct only when resolved |
| callee, low-level (`.call`/`.delegatecall`/`.staticcall`) | Partial | **All three collapse into one generic `"ext::<low-level-call>"` marker** — zero distinguishing target information, no way to tell a plain `.call` from a `.delegatecall` from the graph alone | No |
| modifier | Yes (`USES_MODIFIER`) | Reliable | Direct |
| inheritance (contract → base) | Yes (`INHERITS`) | Reliable at the contract level | Direct |
| state read | Yes (`STATE_READ`) | Reliable | **Indirect only** — `STATEVAR` nodes never get a `file` attribute directly; resolved via the owning contract's node (see the robustness note above about *which* attribute to trust for that lookup) |
| state write | Yes (`STATE_WRITE`, + disjoint `STATE_WRITE_TRANSITIVE` for writes via internal/library call chains) | Reliable | Indirect (same as state read) |
| write-after-external-call | Yes (`WRITE_AFTER_EXTERNAL_CALL`, real CFG reachability via `.sons`) | Reliable | Indirect |
| constructor/init | Partial | **Internal constructors are explicitly skipped and never enter the graph at all** (`if function.is_constructor and function.visibility == "internal": continue`) | N/A when skipped |
| declares (contract → fn/mod/statevar) | Yes | **Bug found**: no dedup guard — inherited-but-not-overridden functions get reprocessed, corrupting the `contract` attribute and adding a spurious duplicate edge (see above) | N/A |
| definitions/declarations of referenced symbols | Yes, via `DECLARES` | Reliable for direct declarations; subject to the same inherited-function caveat above | Direct |

## 2. G0/G1/G2/G3 definitions (as implemented, `graph_relevance.py`)

- **G0** — the candidate's own containing file only.
- **G1** — `BundleBuilder.expand(seed, hops=1)`'s node neighborhood
  (existing code, unmodified), converted to a file set via each node's
  `file` attribute (or, for `STATEVAR` nodes, the owning contract's file
  — see §1).
- **G2** — identical mechanism, `hops=2`.
- **G3 (adaptive)** — starts at G1; for each unresolved fact, checks
  whether any node one hop further than the current set has a `name`
  that appears as a substring in the fact's text, and if so pulls in that
  node's file, recording the trigger symbol/relation/file in an
  expansion-step log. **This is a keyword-substring heuristic over
  existing graph node names, not a new classifier over source text** —
  it only works because this experiment's own unresolved-fact strings
  were hand-written by the same project that names its graph nodes
  consistently; it would not generalize to free-text unresolved-fact
  phrasing without a real text-matching step, which is explicitly out of
  this experiment's scope (§13 of the task instructions).

## 3. File sets generated per candidate

| case_id | G0 | G1 | G2 | G3 (adaptive) |
|---|---|---|---|---|
| unsafe_narrowing_cast | 1 (Ledger.sol) | 1 | 1 | 1 |
| safe_narrowing_cast | 1 | 1 | 1 | 1 |
| unchecked_ecrecover_mutable_signer | 1 (Auth.sol) | **2** (+ AuthAdmin.sol) | 2 | 2 |
| checked_ecrecover | 1 | 1 | 1 | 1 |
| corrected_ecrecover_fixed_signer | 1 | 1 | 1 | 1 |
| insufficient_evidence_timestamp | 1 | 1 | 1 | 1 |
| pooltogether_vault_burn | 1 (Vault.sol) | **3** (+ ERC4626.sol, TwabController.sol) | **15** | **5** |

PoolTogether's real graph: 1095 nodes, 3716 edges, built from
`src/Vault.sol` with the project's own existing solc remaps (no new
compilation-framework work — reused `all_remaps.txt` from this session's
earlier work). G3's two triggered expansions (`_burn` → `ERC20.sol`,
`mint` → `IERC4626.sol`) are logged in
`graph_file_sets.json`'s `g3_expansion_steps`.

## 4. NECESSARY/SUPPORTING/UNNECESSARY classification of historical Codex-read files

Ground truth: Arm C's already-recorded, harness-authoritative
`actual_files_touched` from `THREE_ARM_LLM_REACT_CODEX_COMPARISON.md`
(not re-derived — reused exactly as instructed by task §3). `AGENTS.md`
(a non-Solidity metadata file some Codex runs opportunistically `cat`,
an artifact of this experiment's best-effort shell-command regex
extractor, not a source file the graph reasons about at all) is excluded
from this table.

| case_id | files touched (Arm C, unrestricted) | classification |
|---|---|---|
| unsafe_narrowing_cast | Ledger.sol | NECESSARY |
| safe_narrowing_cast | Ledger.sol | NECESSARY |
| unchecked_ecrecover_mutable_signer | Auth.sol, AuthAdmin.sol | both NECESSARY — cited directly in `resolved_facts.source: "Auth.sol:8-11; AuthAdmin.sol:7-11"` |
| checked_ecrecover | Auth.sol | NECESSARY |
| corrected_ecrecover_fixed_signer | Auth.sol | NECESSARY |
| insufficient_evidence_timestamp | RewardStream.sol | NECESSARY |
| pooltogether_vault_burn (incomplete, 39-command trace) | Vault.sol | NECESSARY (candidate) |
| | ERC4626.sol (OpenZeppelin) | NECESSARY — actively queried for `maxRedeem`'s own bound logic, the specific caller-side check the trace was pursuing |
| | TwabController.sol | NECESSARY — read multiple times, tracing `increaseBalances`/`_delegate` |
| | TwabLib.sol | **NECESSARY-by-trajectory** — the investigation was actively reading `AccountDetails`/`increaseBalances`'s internal representation (the deepest possible verification of the uint96 bound question) when the 480s timeout cut it off; classified necessary based on the model's own search trajectory, not a completed citation (none exists — the run never reached a final decision), an explicit methodological caveat per task §4 |
| | `lib/v5-twab-controller/TwabController.sol` (a wrong path guess, `ERROR: not a file`) | **not applicable** — a failed read attempt, not an inspected file; excluded from recall accounting |

Every touched-and-successfully-read file across all 7 candidates was
classified NECESSARY — no SUPPORTING or UNNECESSARY files were found in
this dataset's traces (consistent with §15 of the prior three-arm
report's own finding of 0% divergence in Arm C's investigation
behavior on this specific dataset).

## 5–6. Necessary-file recall / repository reduction

| case_id | G0 recall | G1 recall | G2 recall | G3 recall | repo reduction (G1, of total .sol files) |
|---|---|---|---|---|---|
| unsafe_narrowing_cast | 1/1 (100%) | 1/1 | 1/1 | 1/1 | 0% (1-file repo) |
| safe_narrowing_cast | 1/1 | 1/1 | 1/1 | 1/1 | 0% |
| unchecked_ecrecover_mutable_signer | 1/2 (50%) | **2/2 (100%)** | 2/2 | 2/2 | 0% (2-file repo) |
| checked_ecrecover | 1/1 | 1/1 | 1/1 | 1/1 | 0% |
| corrected_ecrecover_fixed_signer | 1/1 | 1/1 | 1/1 | 1/1 | 0% |
| insufficient_evidence_timestamp | 1/1 | 1/1 | 1/1 | 1/1 | 0% |
| pooltogether_vault_burn | 1/4 (25%) | **3/4 (75%)** | 3/4 (75%) | 3/4 (75%) | **99.86%** (3 of 2162 files) |

The synthetic bundles' 0% reduction figure is expected and not a
negative result — those fixtures are 1–2 file repositories by design
(controlled cases), so there is nothing to reduce; their purpose was to
test recall precision (G1 = exactly the necessary set, no more, no less)
and mechanism soundness (§9 below), not repository-size reduction.
PoolTogether is the only bundle in this dataset large enough to test the
reduction half of the hypothesis, and it does so decisively: **>99%
reduction while retaining 3 of 4 necessary files** at G1.

## 7–8. Restricted Codex results / unrestricted vs. restricted comparison

Live, filesystem-enforced G1-restricted runs on all 6 synthetic bundles
(PoolTogether not rerun live — budget-driven, logged in the
preregistration §3, not silently skipped):

| case_id | unrestricted Arm C (both reps) | G1-restricted (live) | match? |
|---|---|---|---|
| unsafe_narrowing_cast | FAIL, FAIL | FAIL | ✓ |
| safe_narrowing_cast | PASS, PASS | PASS | ✓ |
| unchecked_ecrecover_mutable_signer | FAIL, FAIL | *(null-JSON formatting fluke on attempt 1 — retried once, see below)* → FAIL | ✓ |
| checked_ecrecover | PASS, PASS | PASS | ✓ |
| corrected_ecrecover_fixed_signer | PASS, PASS | PASS | ✓ |
| insufficient_evidence_timestamp | INSUFFICIENT_EVIDENCE, INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | ✓ |

**6/6 correct, 6/6 match unrestricted.** One data-quality note, not a
graph-relevance finding: `unchecked_ecrecover_mutable_signer`'s first
restricted attempt produced `final_decision: null` — inspection of the
raw session trace showed the model *did* read both correct files
(`Auth.sol`, `AuthAdmin.sol`, exactly G1) and its own trailing
`agent_message` text ends *"...determined violation; so FAIL... Now
final JSON."* — it reached the correct conclusion but failed to emit the
properly fenced JSON block that turn (a one-off generation/formatting
issue, not an evidence-availability failure). A single retry (same
restricted view, same prompt) produced a clean `FAIL` with 3 tool calls.
Logged transparently rather than silently substituting the retry's
result for the original attempt's raw record (both are preserved in
`restricted_codex_results.json`'s git history / this report).

Since G1 == the fixture's full file count on all 6 synthetic bundles (a
consequence of §3's finding, not a design flaw in this batch), this
comparison is a **mechanism-sanity check** — does harness-level
filesystem restriction itself change Codex's behavior for reasons
unrelated to file content (a smaller apparent codebase, a different `ls`
output) — rather than a genuine recall-vs-reduction tradeoff test. It
answers that sanity question cleanly (no): tool-call counts, costs, and
decisions are all consistent with the unrestricted runs.

## 9. Adaptive expansion (G3) results

On the synthetic dataset, G3 never differs from G1 (no unresolved fact
ever named a symbol reachable only beyond 1 hop in these fixtures — the
2-file case's second file was already inside G1 via the duplicate-
`DECLARES`-edge mechanism in §1). On PoolTogether, G3's two triggered
expansions (`_burn`, `mint`) pulled in `ERC20.sol` and `IERC4626.sol` —
plausible, on-topic files given those symbols — but did **not** reach
`TwabLib.sol`, because no unresolved-fact string in this experiment's
hand-written dataset happens to literally name a symbol on that specific
4-hop path. This is an honest limitation of the substring-heuristic
implementation, not evidence about the *graph's* reachability (§10 below
shows the graph itself does connect to `TwabLib.sol`, just 4 hops out).

## 10–11. Cases where necessary evidence was excluded; responsible graph relations

**One confirmed exclusion, fully characterized**: `TwabLib.sol`, needed
(by trajectory) for the PoolTogether candidate, is excluded from G0, G1,
G2, and this experiment's adaptive G3. Direct `ProgramGraph.expand()`
calls at increasing hop counts pinpoint exactly why:

```
hops=1: 8 nodes    -- TwabLib NOT reached
hops=2: 187 nodes  -- TwabLib NOT reached
hops=3: 276 nodes  -- TwabLib NOT reached
hops=4: 340 nodes  -- TwabLib reached (libraries/TwabLib.sol)
```

**Classification: `GRAPH_DEPTH`, not `GRAPH_MISSING_EDGE` or
`NOT_GRAPH_REPRESENTABLE`.** The causal chain the graph would need to
traverse — `Vault._burn` → `_twabController.burn` (`EXTERNAL_CALL`,
1 hop) → `TwabController`'s own internal balance-mutation functions
(`CALLS`/declares-adjacent, further hops) → those functions' own calls
into the `TwabLib` library (`CALLS`, library-call resolution) — is a real
edge sequence the graph does capture; it simply requires more hops than
G0–G3 (as defined in this experiment) expose. This is exactly the "most
important negative result" the task instructions asked this experiment
to surface, reported without attempting a fix.

```json
{
  "candidate": "Vault._burn",
  "graph_mode": "G1/G2/G3(adaptive)",
  "decision": "N/A -- unrestricted run timed out before a final decision; restricted rerun not executed (budget)",
  "missing_fact": "the exact internal representation/bound of TwabController's per-account balance storage (AccountDetails.balance), the deepest verification of whether _shares can exceed uint96.max",
  "needed_symbol": "TwabLib (library used internally by TwabController's increaseBalances/decreaseBalances)",
  "needed_file": "lib/pt-v5-prize-pool/lib/pt-v5-twab-controller/src/libraries/TwabLib.sol",
  "was_file_in_allowed_set": false,
  "graph_relation_that_should_have_reached_it": "Vault._burn --EXTERNAL_CALL--> TwabController function --CALLS--> TwabLib function (verified to exist at hop 4 via direct ProgramGraph.expand())",
  "failure_type": "GRAPH_DEPTH"
}
```

## 12. PoolTogether investigation analysis

Already covered in depth in `THREE_ARM_LLM_REACT_CODEX_COMPARISON.md`
§15 (0% divergence — all 39 commands trace one coherent causal chain).
This experiment adds the graph-structural half of that finding: the
chain Codex pursued in practice (`Vault._burn` → `redeem`/`maxRedeem` →
`ERC4626` → `TwabController`/`TwabLib`) corresponds almost exactly to
increasing graph hop-distance from the candidate (`ERC4626`/
`TwabController` at 1 hop, `TwabLib` at 4 hops) — the agent's own,
independently-arrived-at investigation order and the graph's own
structural distance ordering agree, a notable convergent-validity
signal for the graph's relevance ranking even where its tested depth
(G0–G3) falls short of full coverage.

## 13. Cost/time/action/file-count comparison

| | unrestricted Arm C (synthetic avg) | G1-restricted (synthetic avg) |
|---|---|---|
| cost/call | ~$0.020 | ~$0.018 |
| tool actions | ~2.5 | ~2.8 |
| decision correctness | 6/6 (both reps) | 6/6 |

No meaningful efficiency difference on this dataset — expected, given
§8's finding that G1 == the full fixture file set here. The efficiency
half of the original hypothesis (restriction reduces wandering without
losing evidence) remains **untested at the scale where it would matter**
(a real repository with genuinely excludable irrelevant files) — logged
as an open follow-up, not claimed.

## 14. Threats to validity

- **The restricted-Codex live comparison is a sanity check, not a
  recall-vs-reduction stress test** (§8) — G1 happened to equal the full
  file set on every synthetic bundle tested live; the one bundle where
  restriction would have meant something (PoolTogether) was not rerun
  live, for disclosed budget reasons.
- **NECESSARY classification for `TwabLib.sol` is trajectory-based, not
  citation-based** — the PoolTogether investigation never completed, so
  there is no final `resolved_facts` entry to confirm the file's content
  was decisive, only that the model chose to keep reading it when the
  timeout hit.
- **The G3 adaptive-expansion heuristic is a simple substring match**,
  acknowledged as non-generalizing beyond this experiment's own
  hand-written unresolved-fact strings (§2, §9) — a real relevance
  mechanism would need a genuine text-to-symbol matching step, out of
  this experiment's explicit scope.
- **A real, verified graph-construction bug (§1) was worked around, not
  fixed** — any other code relying on a function node's `contract`
  attribute (rather than parsing its node id) for an inherited-but-not-
  overridden function will get the wrong answer until `a4v/graph.py`
  itself is patched, which this experiment deliberately did not do.
- **n=1 real-repository bundle** — the `GRAPH_DEPTH` finding for
  PoolTogether is a single, if well-characterized, data point; whether
  4-hop-deep dependency chains are typical or unusual across the kinds
  of candidates RTF would actually route is not established here.
- **Single-researcher project throughout** — same disclosed limitation as
  prior reports in this line of work.

## 15. Conclusion

**The existing graph is sufficient as a relevance boundary for
controlled, localized candidates** (Outcome A, cleanly supported: 100%
necessary-file recall at G1 on all 6 synthetic bundles, both
analytically and via a live filesystem-enforced restricted rerun).
**It is not yet sufficient, at the hop depths tested here (G0–G3), for
deep real-repository dependency chains** — PoolTogether's one confirmed
miss is a `GRAPH_DEPTH` limitation (4 hops needed, 3 tested), not a
missing relation or a fundamentally unrepresentable construct, and not
grounds for inventing a new relevance mechanism (per the task's own
constraint, §13). **Recommended next step, if this line of work
continues**: test whether a deeper but still-existing-relations-only
expansion (a literal G4, or an adaptive expansion with a real budget
instead of this experiment's simple substring heuristic) closes the
PoolTogether gap without a comparable loss of repository reduction —
this is a natural, narrow follow-up question this experiment's own
results point to directly, not attempted here to respect this session's
cumulative $5 self-enforced spend cap (final: $2.873).
