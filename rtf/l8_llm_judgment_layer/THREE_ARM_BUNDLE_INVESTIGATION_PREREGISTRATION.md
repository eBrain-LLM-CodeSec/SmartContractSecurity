# Preregistration: bounded LLM (A) vs. fake-ReAct harness (B) vs. real Codex CLI (C)

Frozen before any live Arm C call in this batch. This document, plus
`bundle_agent_experiment/dataset.py`, `CODEX_SYSTEM_PROMPT_v1.md` (Arm B,
unchanged), and `CODEX_SYSTEM_PROMPT_v2_arm_c.md` (Arm C, new) are the
frozen artifacts for this comparison.

## 1. Why this experiment exists

`BUNDLE_LLM_VS_CODEX_AGENT_EXPERIMENT.md` (the prior experiment) found
that a hand-built ReAct harness (Arm B) frequently skipped real tool use
and fabricated investigation-shaped output when it did. That result
could not distinguish "agentic repository investigation doesn't help"
from "this specific harness's protocol was unsafe." This experiment adds
**Arm C: the real Codex CLI**, to determine whether a properly
constrained *real* agent recovers missing repository evidence and makes
better bundle-level judgments than both Arm A and Arm B — without
assuming Arm C wins.

## 2. Arms A and B: reused, not rerun

Both `ChatClient` calls run at `temperature=0.0` with an on-disk cache
keyed on the exact request payload. Since Arm A's and Arm B's inputs
(dataset, prompts, system prompts, model, config) are byte-identical to
the prior experiment and nothing about either implementation is changing
here, rerunning them would produce byte-identical output at zero marginal
information gain (already demonstrated directly in the prior report:
cases 3 and 5's Arm A responses were a literal cache hit on
byte-identical prompts). **Arm A and Arm B results are reused verbatim
from `phase_bundle_agent_artifacts/results.json`, not rerun.** This
satisfies the instruction to preserve Arm B's implementation/behavior
exactly (identical artifacts, not just identical code) and frees the
full remaining session budget for Arm C, which is this experiment's
actual new work.

## 3. Arm C: real Codex CLI — architecture

**Binary:** `codex-cli 0.104.0`, the exact version pinned in this
project's own worker image (`backend/docker/base/Dockerfile`), musl
static build, downloaded directly from the official GitHub release and
run standalone on this login node (confirmed via live smoke test —
network egress to `github.com`/`release-assets.githubusercontent.com`
and to `openrouter.ai` both work from this node; no SLURM/Singularity
job needed). Not a hand-built imitation.

**Provider config:** adapted directly from this project's own production
mechanism (`docker/worker/init.py::_write_codex_proxy_config`,
`backend/worker_runner/common.py::build_codex_cmd`), not guessed:
`model_provider = "proxy"`, `base_url = "https://openrouter.ai/api/v1"`
(same endpoint `a4v.llm.ChatClient` uses — no local `oai_proxy` hop,
mirroring this deployment's own `proxy_static` mode, which already
points `OAI_PROXY_BASE_URL` straight at OpenRouter per `env/stack.env`),
`wire_api = "responses"` (this version's only supported wire format;
`"chat"` was removed in 0.104.0), `env_key = "OPENAI_API_KEY"` holding
the real key from `run/task5_secrets/openrouter.key` directly (documented
"direct mode" in the production script's own comments, as opposed to
"proxy-token mode" where the key is an opaque token for a local
decrypting proxy — not needed here since there's no local proxy).
**Model: `openai/gpt-5.1-codex-max`, identical to Arms A/B.**

**Invocation**, adapted from `build_codex_cmd` (verified against that
source, not reimplemented from memory):
```
codex exec --model openai/gpt-5.1-codex-max \
  --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check \
  -C <investigation_dir> -o <out_path> --json "<prompt>"
```
No `--output-schema` (production abandoned relying on it after the GLM
finding in `evmbench/CLAUDE.md`; this experiment matches that and uses
fenced-JSON extraction from the final response instead, same as Arms A/B
and same as production's own `extract_fenced_json`).

**Session isolation:** one fresh, throwaway `$HOME` (and thus
`~/.codex/{config.toml,auth.json,sessions/}`) per bundle × repetition —
stronger isolation than production's own pipeline (which shares one
`AGENT_DIR/.codex` across multiple stages of the *same* job); guarantees
zero cross-bundle memory beyond what a single `codex exec` call already
provides.

**Repository access boundary — a real, disclosed architectural
difference from Arm B.** `--dangerously-bypass-approvals-and-sandbox`
grants Codex full filesystem read/write and network access (confirmed
live: the session log's `<permissions instructions>` block states
`sandbox_mode` is `danger-full-access`, "Network access is enabled").
Unlike Arm B's `tools.py`, which hard-rejects any path outside
`repo_root`, **nothing technically stops Arm C from reading outside its
intended directory** — the anti-divergence rules in the frozen prompt
are the only restraint, and they are instructions, not an enforced
boundary. Two mitigations, both logged as what they are (risk reduction,
not elimination):
1. For the 6 synthetic fixtures, which live inside this experiment's own
   git worktree, each bundle's fixture is **copied into a fresh, non-git
   scratch directory** (`arm_c_codex.py::prepare_isolated_repo`) before
   invoking Codex — this removes the specific, checked risk of Codex's
   git-repo detection surfacing the wider RTF/evmbench codebase as an
   explorable parent repository (confirmed via the smoke test: the
   session log captured this repo's own `commit_hash`/`branch`/
   `repository_url` when run directly against a fixture subdirectory of
   this worktree, proving that ancestry *was* visible before the fix).
2. For the PoolTogether bundle, `repo_root` is already an independent
   checkout (job-scratch, no parent-repo bleed-through) — used as-is,
   matching Arms A/B's identical `repo_root`.
3. Actual behavior is checked after the fact from the authoritative
   session trace (§6) — any command touching a path outside the intended
   investigation directory is flagged in the report, not assumed absent.

**System-prompt constraint — a second real, disclosed architectural
difference.** Real Codex CLI has no flag to fully replace its own
built-in `base_instructions` (a large general-purpose coding-agent
persona, confirmed present verbatim in the session log — "You are a
coding agent running in the Codex CLI..."). This experiment's frozen
investigation contract (`CODEX_SYSTEM_PROMPT_v2_arm_c.md`) is delivered
as the leading content of the single user-role prompt argument, layered
**on top of**, not instead of, Codex's own persona. Unlike Arms A/B,
where the system prompt is the complete and only behavioral
specification, Arm C's actual operative instructions are a superset this
experiment does not fully control. This is reported as a limitation
(§17 of the eventual report), not concealed.

## 4. Dataset: reused unchanged

The exact same 7 bundles from the prior experiment
(`dataset.py::build_dataset()`), same `expected_label`s and
justifications. No fixture was found invalid — re-inspected before this
preregistration was written, per the task instruction to check first.
Arm C receives the same requirement/context/candidate/evidence/
unresolved-facts as Arms A/B, plus a repository directory to investigate
(the isolated fixture copy or, for bundle 7, the same `repo_root` used
in the prior experiment).

## 5. Repetition count (fixed before running)

**N=2 for bundles 1–6, N=1 for bundle 7 (PoolTogether)** — an explicit,
logged, budget-driven asymmetry, not a methodological preference: the
prior experiment's Arm B PoolTogether investigation cost $1.56 alone
(the single most expensive result in that report), and this session's
remaining budget before this batch is a hard $5.00 cap with **$2.51
already spent** (prior experiment $2.48 + this batch's two required
Codex-CLI feasibility smoke-test calls, $0.029, logged honestly as spend
even though they predate this freeze — see §8). A second PoolTogether
repetition is attempted only if remaining budget comfortably allows
after seeing bundles 1–6's real cost; if not, this is reported as a
budget-driven truncation, not silently dropped. **This condition is
fixed now, before any bundle-1–6 result is seen** — no repetition count
is adjusted after observing outcomes.

## 6. Harness-enforced evidence integrity (authoritative, not model-reported)

`arm_c_codex.py::run_arm_c_bundle` parses Codex's own `--json` event
stream (not the model's self-reported claims) for:
- every `command_execution` item → `actual_tool_calls`, `actual_commands`
  (the literal shell command line)
- best-effort file-path extraction from each command
  (`cat`/`head`/`tail`/`sed -n`/`rg`/`grep`/`wc` patterns) →
  `actual_files_touched` — documented as best-effort, not a perfect
  parser, in the eventual report
- `turn.completed`'s `usage` block → `input_tokens`/`cached_input_tokens`/
  `output_tokens`, converted to `cost_usd` via OpenRouter's published
  per-token pricing for this model (queried once, live, via the public
  `GET /api/v1/models` endpoint — not the laggy account-usage endpoint)
- `git rev-parse HEAD` in the investigation dir → `repository_commit`
  (only populated for the real PoolTogether checkout)

**Mandatory-investigation gate**: if a bundle's `unresolved_facts` list
is non-empty and `actual_tool_calls == 0`, the result is flagged
`protocol_violation` — reported explicitly, not silently accepted as a
valid final answer, mirroring the prior experiment's central finding
about Arm B.

**Citation-provenance check**: every `source` field in the final JSON's
`initial_evidence_verification`/`resolved_facts` is checked against
whether any actually-touched file's basename appears in it; a mismatch
is logged as a `citation_provenance_failure`, not silently trusted —
same principle as the prior experiment's finding about Arm B's fabricated
`Router.sol`/`Rewarder.sol` citations, now checked mechanically for Arm C
too.

## 7. Metrics (adopted from the task instructions §11–14 verbatim)

Correct judgment rate; false PASS rate; false FAIL rate; appropriate
abstention; missing-fact recovery (bundles 3/5 especially); new-evidence
quality (real, repository-backed, relevant, decision-relevant);
citation-provenance validity; search efficiency; divergence rate; cost;
latency; token use; tool-action count — computed identically across all
three arms wherever the metric applies (Arm A has no tool-use metrics by
construction).

## 8. Budget

Session spend before this preregistration: **$2.5093** ($2.4796 from the
prior experiment + $0.0137 + $0.0150 for the two Codex-CLI feasibility/
harness-validation smoke tests in this session, run *before* this freeze
to determine whether Arm C was executable at all — logged honestly as
real spend, not excluded on a technicality). Remaining before the $4.00
stop-new-calls threshold: **$1.49**. `spend_guard`-equivalent checking
(via the live-computed `cost_usd` from §6, summed across this batch) runs
before and after every single Arm C call, exactly as in the prior two
live-call batches this session. Execution halts immediately if projected
spend would cross $4.00, with whatever bundles/repetitions are already
complete reported as a partial, honestly-labeled result.

## 9. Interpretation rules (adopted verbatim from the task instructions §16)

- **Outcome A** (Arm C wins): materially improves correctness/missing-fact
  recovery without unacceptable false PASS, divergence, or cost → real
  restricted agentic investigation is justified as an RTF investigation
  stage.
- **Outcome B** (Arm A wins): Arm C adds cost/complexity, no evidence
  benefit → stay with bounded LLM judgment.
- **Outcome C** (Arm C helps only on unresolved-fact bundles): selective
  agent escalation, not agent-per-bundle.
- **Outcome D** (fake ReAct fails, real Codex succeeds): the prior
  negative result was predominantly a harness/protocol artifact.
- **Outcome E** (both agents fail similarly): repository tool access
  itself does not solve the identified evidence problem under the tested
  constraints.

Applied mechanically to the actual three-way results in the final
report — not re-litigated after seeing them.

## 10. Deliverables

Raw results + complete Codex session traces (`.codex/sessions/*.jsonl`
per bundle × repetition, preserved alongside the harness's own parsed
`--json` stream log) under
`phase_three_arm_artifacts/`. Final report:
`THREE_ARM_LLM_REACT_CODEX_COMPARISON.md`, structure per the task
instructions' 20-point list.
