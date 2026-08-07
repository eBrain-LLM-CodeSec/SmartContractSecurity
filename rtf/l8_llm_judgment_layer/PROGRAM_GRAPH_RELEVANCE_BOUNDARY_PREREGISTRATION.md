# Preregistration: does the existing ProgramGraph bound Codex's file access without hiding evidence?

Frozen before any live restricted-Codex call in this batch. Written after
completing the free (zero-cost) analysis in
`PROGRAM_GRAPH_RELEVANCE_BOUNDARY_EXPERIMENT.md` §1–§4, which already
answers most of this experiment's core question analytically — this
preregistration covers only the remaining live-call portion (§5 of the
task instructions).

## 1. What the free analysis already established (not reproduced here, see the report)

- `a4v.graph.ProgramGraph` / `a4v.slice.BundleBuilder` exist and are
  fully functional, but **RTF itself never constructs or uses them
  today** — confirmed via a repo-wide grep. This experiment is the first
  thing that wires them to RTF's own candidates.
- A real bug was found and verified in `ProgramGraph.build()`: inherited-
  but-not-overridden function nodes have their `contract` attribute
  silently overwritten by the last contract that reprocesses them (no
  dedup guard around function-node creation) — not fixed here, per this
  experiment's own "audit, don't fix" scope; worked around in this
  experiment's own node-resolution code only.
- **G1 achieves exact-match (100% recall, 0% over-inclusion) against the
  files Arm C's real Codex investigation actually touched, on all 6
  synthetic bundles.**
- **On the one real-repository bundle (PoolTogether `Vault._burn`), G1/G2/
  adaptive-G3 all plateau at 3 of 4 necessary files (75% recall)** — the
  missing file, `TwabLib.sol`, is empirically confirmed (via direct
  `ProgramGraph.expand()` calls, hop-by-hop) to be reachable only at
  **4 hops**, not 3. This is a `GRAPH_DEPTH` limitation (the causal chain
  exists in the graph), not a missing relation or an unrepresentable
  construct.

## 2. What this live batch tests

Whether **G1-restriction** (the level shown sufficient by the free
analysis on the synthetic dataset) preserves Arm C's correct, unrestricted
judgments when Codex's filesystem access is *actually* limited to the G1
file set — not merely evidence that G1 *contains* the right files, but
that a real, harness-enforced restricted view doesn't otherwise change
Codex's behavior (e.g., via missing incidental context, a different
directory-listing experience, or triggering different search patterns).

## 3. Dataset and scope (budget-driven, logged before running)

**All 6 synthetic bundles, G1-restricted, 1 repetition each** (not 2 — see
budget below). **PoolTogether is NOT re-run live in this batch.** This is
a deliberate, budget-driven scope decision, not a silent omission: the
unrestricted PoolTogether Arm C run already consumed significant wall-
clock time and did not complete within its own budget; a second live
PoolTogether run (restricted or not) risks a repeat of that outcome for a
question (§2 above) that is already answered analytically and
deterministically for the *file-availability* half of the question
(TwabLib.sol is unreachable at G1/G2/G3 — this is a graph fact, not
something a live call can change or needs to confirm). The specific
question a live PoolTogether-restricted run *would* add — does Codex
notice the gap and honestly abstain, or does it produce a false-confident
answer without the missing evidence (§6 of the task instructions, "detect
false restriction") — is logged as **not executed, budget-constrained**,
not silently dropped; see the report's §17 (threats to validity) and
§20-equivalent limitations section.

## 4. Restricted-workspace mechanism

Filesystem-enforced, not prompt-enforced: for each of the 6 bundles, a
fresh scratch directory is populated with **only** the files in that
bundle's G1 set (already == 100% of the bundle's actual file count for
5 of 6 bundles, since those fixtures are 1-file repos; the
`unchecked_ecrecover_mutable_signer` bundle is the only 2-file case,
and G1 already includes both files, so this specific live batch is
expected to be behaviorally identical to the unrestricted Arm C run —
see §6 for why it's still run, not skipped). No build/config metadata is
added beyond what each fixture already has (none of these fixtures use
Foundry/Hardhat config). Codex is invoked with the exact same frozen
`CODEX_SYSTEM_PROMPT_v2_arm_c.md` contract and the exact same per-bundle
prompt content as the unrestricted Arm C run, `-C` pointed at the
restricted directory.

## 5. Metrics

Decision, confidence, tool-action count, files touched, wall-clock,
cost — directly comparable to the unrestricted Arm C `r0`/`r1` results
already on file. Primary question: does the decision match the
unrestricted run's decision (both being correct, per the frozen
`dataset.py` expected labels)?

## 6. Why run G1-restricted trials at all when G1 == the fixture's full file set for 5/6 bundles

This is itself the point for those 5 bundles: it is a **negative/sanity
control** confirming that harness-level filesystem restriction (a real,
new mechanism — copying only G1 files into an isolated directory) doesn't
itself change Codex's behavior for reasons unrelated to file content
(e.g., a different `ls` output, a smaller apparent codebase changing its
exploration heuristics). Only `unchecked_ecrecover_mutable_signer` tests
genuine restriction value (G1 excludes nothing there either, in this
specific bundle, since AuthAdmin.sol is already in G1 — so even this
bundle is a same-file-set control, not a true reduction case, for the
reason documented in the free-analysis report §1: the spurious duplicate
DECLARES edge already pulls it in at 1 hop). **This means this specific
live batch is a mechanism-sanity-check, not a test of whether restriction
*trades off* recall for reduction** — the dataset's only real
recall-vs-reduction tradeoff case (PoolTogether) is the one not rerun
live, per §3. This asymmetry is disclosed, not hidden.

## 7. Budget

Session spend before this batch: **$2.744** (prior two experiments).
Remaining before the $4.00 stop-new-calls threshold: **$1.256**. Six
single-file/two-file restricted Codex calls, each expected to cost
roughly the same as the unrestricted equivalents already on file
($0.013–$0.027/call observed) → estimated **$0.10–0.20** for this batch,
comfortably within margin. Checked before/after every call exactly as in
both prior batches.

## 8. Interpretation

Given §1's free analysis already provides strong, clean evidence for
Outcome A (G1 sufficient) on the synthetic half of the dataset and a
`GRAPH_DEPTH`-classified partial miss on the real-repository half, this
live batch's role is **confirmatory**, not discriminating between
outcomes — a mismatch between any restricted and unrestricted decision
here would be a surprising, important finding (logged and investigated,
not dismissed), but the batch is not designed to distinguish Outcome A
from B/C the way a PoolTogether-scale test would. The report's overall
conclusion (§16 of the required structure) is drawn from the *combination*
of the free analysis (primary evidence) and this live batch (confirmatory
check), stated honestly as such.
