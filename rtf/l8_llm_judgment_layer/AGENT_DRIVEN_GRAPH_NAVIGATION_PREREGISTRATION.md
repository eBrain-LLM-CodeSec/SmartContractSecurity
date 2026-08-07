# Preregistration: agent-driven graph navigation (Arm G) vs. unrestricted Codex (Arm U)

Frozen after building and validating the Arm G harness (design forced by
a real infrastructure constraint discovered during this process — see §1
— but the dataset, metrics, and success criteria below are fixed before
any bundle beyond the one validation smoke test, kept as an official data
point per §4, is run).

## 1. A real infrastructure constraint changed the enforcement mechanism — disclosed, not hidden

The task's own design assumed filesystem/harness-enforced restriction of
Codex's visible file scope. Verified live, at zero LLM cost, using
`codex sandbox linux` (which runs an arbitrary command under Codex's own
Landlock+seccomp sandbox without invoking the model at all): **this
session's login node runs kernel 4.18.0, which predates Landlock's
introduction in Linux 5.13** — every sandboxed invocation
(`read-only`, `workspace-write`) panics with `error applying legacy Linux
sandbox restrictions: Sandbox(LandlockRestrict)`. Confirmed further via
a direct `landlock_create_ruleset` syscall probe (invalid ABI). Every
prior live Codex call in this session used
`--dangerously-bypass-approvals-and-sandbox` — the only mode that works
here — meaning no experiment in this line of work has ever run Codex
under its own OS-level sandbox; this is the first time it was tested, and
it fails outright, independent of anything about this experiment's own
design.

**Consequence**: `--dangerously-bypass-approvals-and-sandbox` grants full
filesystem access regardless of `-C`, so a directory populated with only
the candidate's file (as done for the prior G1-restricted experiment,
where the *final* file set was precomputed once) does not, by itself,
prevent Codex's shell from reading elsewhere once invoked in this mode —
there is no way, on this infrastructure, to combine "shell tool available"
with "reads outside a given directory are physically blocked."

**Adaptation**: enforcement shifts from **prevention** to
**harness-authoritative detection**. A separate, unsandboxed MCP server
process (`graph_mcp_server.py`, launched by `codex mcp add`-equivalent
config, not subject to the model-generated-shell-command sandbox at all)
is the *sanctioned* path to new evidence: it resolves real
`ProgramGraph` relations and, as a side effect, copies the corresponding
source files into Codex's visible directory. The harness measures
compliance from the real, authoritative record (every MCP tool call is
logged; every shell command is parsed for touched files, exactly as in
the three-arm experiment) rather than assuming it: **any file read via
the shell whose basename was never revealed by a graph tool call is
logged as a divergence event** — a real, disclosed weakening from
"physically impossible" to "measured and reported," not silently
substituted for the stronger guarantee the task asked for.

## 2. Architecture (as implemented, matches the task's intent modulo §1)

**Arm U**: exact reuse of the three-arm experiment's unrestricted Arm C
results — no rerun (same reasoning as the prior two follow-up
experiments: identical inputs, nothing about Arm C's implementation
changed).

**Arm G**: `arm_g_codex.py::run_arm_g_bundle`. Initial visibility:
exactly the candidate's own file, copied into a fresh investigation
directory (nothing else). MCP server (`graph_mcp_server.py`) registered
per-bundle via a hand-written `config.toml` `[mcp_servers.rtf-graph-
navigation]` block (schema confirmed by running the real `codex mcp add`
once against a throwaway `$HOME` and inspecting its output — not
guessed), exposing three tools: `show_candidate()`, `investigate(node_id,
relation, unresolved_fact, why_needed)`, `read_source(node_id)`. No fixed
G1/G2/G3/G4 precomputation — every expansion is a live graph query
triggered by the model's own tool call, exactly per the task's core
architectural rule (§2 of the task instructions).

**Relations exposed** (a consolidated `relation` enum parameter on one
`investigate` tool, rather than 13 separately-named tools — a disclosed
implementation simplification with equivalent coverage, not a scope
reduction): `CALLERS`, `CALLEES`, `EXTERNAL_TARGETS`, `INTERFACES`,
`MODIFIERS`, `STATE_READS`, `STATE_WRITES`, `STATE_WRITES_TRANSITIVE`,
`WRITERS_OF_STATE` (new — not present in `BundleBuilder`'s own API;
added because it's the single relation genuinely needed to answer "can
this variable change" questions precisely, resolving `STATE_WRITE`/
`STATE_WRITE_TRANSITIVE` in-edges on a state-variable node), and
`WRITE_AFTER_EXTERNAL_CALL`. `GRAPH_UNRESOLVED` is returned, with a
reason, whenever a relation resolves to nothing, or only to
unrepresented synthetic targets (unresolved external interfaces,
collapsed low-level-call markers) — validated live in the smoke test
(§4): a genuine "no callers" case and a genuine "no source excerpt for a
bare state-variable node" case both correctly returned
`GRAPH_UNRESOLVED` with an accurate reason, not a crash or a silent
empty result.

## 3. Verified ProgramGraph defects — none newly fixed, prior workarounds reused

Per the task's §16, no new graph enhancements were introduced. The one
verified defect from the prior experiment (inherited-function `contract`
attribute corruption / duplicate `DECLARES` edges) is worked around the
same way as before: `graph_mcp_server.py`'s node resolution matches by
node-id prefix (`fn::Contract.function(`), never by the `contract` data
attribute. `STATEVAR` file resolution likewise parses the node id's own
`var::Owner.name` prefix. No other defects were found or needed fixing
for this experiment's tool surface.

## 4. Dataset and live-run scope (budget-driven, logged before running)

Session spend before this experiment: **$2.873**. Remaining before the
$4.00 stop-new-calls threshold: **$1.127**, already partly spent on this
experiment's own free-then-cheap validation (a $0.030 smoke test on
`unsafe_narrowing_cast`, kept as this bundle's official Arm G result —
no reason to discard and rerun a properly-configured call). All 6
synthetic bundles + PoolTogether are attempted, in this order:
`unsafe_narrowing_cast` (done, §above), `safe_narrowing_cast`,
`unchecked_ecrecover_mutable_signer`, `checked_ecrecover`,
`corrected_ecrecover_fixed_signer`, `insufficient_evidence_timestamp`,
then `pooltogether_vault_burn` last (highest cost/time risk, run only if
budget comfortably allows after the other 6 — matching the exact
budget-gating pattern already used successfully in both prior follow-up
experiments). **1 repetition per bundle** (not 2) — this experiment's
focus is traversal-path/divergence characterization, not repeat-run
stability, and budget does not comfortably support both.
`pooltogether_vault_burn`'s timeout is set to 300s (tighter than the
unrestricted run's 480s, given this session's cumulative time/cost
budget for this specific bundle across three experiments now) — if it
times out, that is reported as a valid, honest result (as it was for
Arm U), not retried.

## 5. Metrics

Per task §13: correctness, false PASS/FAIL, appropriate uncertainty;
necessary-fact/file recovery (cross-referenced against the same
NECESSARY classification already established in
`PROGRAM_GRAPH_RELEVANCE_BOUNDARY_EXPERIMENT.md` §4); investigation
completeness; traversal metrics (graph tool calls, unique files
revealed, relation types used, `GRAPH_UNRESOLVED` events); divergence
(shell reads of never-revealed files — the one metric this experiment
can measure exactly, per §1's adaptation); cost/time/tokens. Relevant vs.
divergent actions are reported separately, never a raw tool-call count
used as a negative signal, per the task's explicit instruction.

## 6. Success criteria / interpretation

Outcomes A–D adopted verbatim from the task's §15. Applied mechanically
to the actual results, not re-litigated after seeing them.
