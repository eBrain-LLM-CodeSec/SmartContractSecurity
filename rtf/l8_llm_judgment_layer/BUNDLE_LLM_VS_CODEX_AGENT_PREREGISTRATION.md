# Preregistration: bounded LLM vs. Codex-style investigation agent, per bundle

Frozen before any live call in this experiment batch. This document, plus
`bundle_agent_experiment/dataset.py` and
`bundle_agent_experiment/CODEX_SYSTEM_PROMPT_v1.md`, are the frozen
artifacts — no change to any of the three after execution begins without
a new version and a logged reason (research-integrity constraint,
identical in spirit to the Phase H root-cause investigation's own
ablation preregistration).

## 1. Experimental question

Given the same EthTrust requirement and the same initial evidence bundle,
does a repository-aware investigation agent (Arm B) produce more correct,
complete, and well-supported bundle-level judgments than a bounded LLM
call that cannot search the repository (Arm A) — and, where it does,
is the improvement traceable to specific repository evidence the bounded
call never received (rather than to a different model/prompt)?

**Model-family confound: none.** Both arms run the exact same model,
`openai/gpt-5.1-codex-max`, via the same `a4v.llm.ChatClient` /
OpenRouter path, `temperature=0.0`, no `top_p`/`max_tokens` override.
Arm B differs only in: (a) a different system prompt (the frozen Codex
Bundle Investigator prompt vs. Arm A's short bounded-reviewer prompt),
and (b) access to three scoped repository tools plus the resulting
multi-turn conversation. This is the only prompt/architecture confound,
and it is exactly what the experiment is designed to isolate.

**Implementation substitution, logged (see `CODEX_SYSTEM_PROMPT_v1.md`'s
header for the full explanation):** the real OpenAI Codex CLI/sandbox is
not available outside this deployment's SLURM+Singularity worker stack.
Arm B is a hand-built ReAct-style tool loop
(`bundle_agent_experiment/arm_b_agent.py`) over the same chat-completions
API, not the production Codex CLI. This keeps the model-family variable
controlled while testing the thing actually in question — repository
tool access — rather than a specific vendor agent product.

## 2. Unit of judgment

One bundle per call/session. No model or agent invocation receives more
than one candidate's evidence at a time — this deliberately removes the
context-interference/dilution effect identified in the Phase H
root-cause investigation's case 8 (`PHASE_H_ROOT_CAUSE_ANALYSIS.md` §3,
§6) from this experiment; that effect is a separate, already-documented
phenomenon and is not being re-tested here.

## 3. Dataset (frozen; see `dataset.py::build_dataset()` for the executable form)

7 bundles, chosen to span: (a) evidence-complete controls in both
directions, to test whether Arm B's location-scoped framing alone
changes anything absent new evidence; (b) a matched FAIL/PASS pair
sharing byte-identical initial evidence and the same stated unresolved
fact, differing only in which way the repository actually resolves that
fact — the closest thing to a controlled experiment on relational-fact
recovery; (c) a genuine insufficient-evidence control, to test for
over-confidence/hallucinated resolution under repo access; (d) one real,
large repository (2023-07-pooltogether) to test generalization beyond
small synthetic fixtures.

| # | case_id | requirement | candidate | expected | why (see `dataset.py` for full text) |
|---|---|---|---|---|---|
| 1 | `unsafe_narrowing_cast` | req-3-all-valid-inputs | Ledger.record | FAIL | unconditional truncation, single-file repo, nothing more to find |
| 2 | `safe_narrowing_cast` | req-3-all-valid-inputs | Ledger.record | PASS | require() dominates the cast; direct counterpart of #1 |
| 3 | `unchecked_ecrecover_mutable_signer` | req-2-signature-verification | Auth.verify | FAIL | AuthAdmin.sol's unbounded setter proves authorizedSigner can become zero |
| 4 | `checked_ecrecover` | req-2-signature-verification | Auth.verify | PASS | explicit zero-check dominates, independent of authorizedSigner's value |
| 5 | `corrected_ecrecover_fixed_signer` | req-2-signature-verification | Auth.verify | PASS | authorizedSigner is `immutable` + constructor-non-zero-checked, no setter — can never be zero. **Same initial evidence text and same unresolved fact as #3; opposite repo content, opposite correct answer.** |
| 6 | `insufficient_evidence_timestamp` | req-2-block-data-misuse | RewardStream.updateReward | *(none — INSUFFICIENT_EVIDENCE/INCONCLUSIVE is correct)* | mechanism is fully repo-visible; economic materiality is not, and no further search can supply it |
| 7 | `pooltogether_vault_burn` | req-3-all-valid-inputs | Vault._burn | FAIL | real code, same unconditional-truncation pattern as #1, verified by reading `_burn`'s body and callers — not derived from EVMbench finding text |

**Excluded from this pass (logged, not silently dropped):** the Tempo
candidate and the borderline readonly-reentrancy control from the user's
suggested dataset (RTF task instructions §6) are not included here, to
keep this first run inside a tight, already-partially-spent $5 session
cap (see §11) and because neither adds a new *type* of contrast beyond
what bundles 1–7 already cover (Tempo would need its own temporal-
blinding review before use; the reentrancy control would be a second
genuine-uncertainty case, redundant with #6 for this pass's purposes).
Both are legitimate follow-ups for a larger run, not omitted for
convenience.

Every `expected_label` is justified strictly from facts stated in that
bundle's own fixture source files (see `dataset.py`'s
`label_justification` fields) — never from EVMbench ground truth, per
the research-integrity constraints.

## 4. Arm A — bounded LLM call

One `ChatClient.complete()` call per bundle. System prompt: a short,
purpose-built bounded-reviewer prompt (`arm_a.py::ARM_A_SYSTEM_PROMPT`)
explicitly stating no repository access and location-only scope. User
message: requirement text (from the existing frozen L1/L2 corpus,
unmodified) + L2 context bundle (definitions/parent section/referenced
requirements) + candidate location + the bundle's evidence text + known
limitations, ending in the exact output schema from the task
instructions (`decision`/`reasoning_summary`/`supporting_facts`/
`missing_facts`/`requirement_citations`/`code_citations`/`confidence`).
No tools, no ability to request more evidence, `temperature=0.0`.

## 5. Arm B — investigation agent

`bundle_agent_experiment/arm_b_agent.py::run_arm_b()`. Frozen system
prompt: `CODEX_SYSTEM_PROMPT_v1.md` (the user-specified Codex Bundle
Investigator prompt, verbatim, plus a protocol addendum for the
non-native-function-calling JSON action format — see that file's header
for exactly which part is user-specified vs. implementation-only).
Same requirement/context/candidate/evidence/unresolved-facts as Arm A,
plus the bundle's `repo_root` and an explicit action-budget statement.
Three tools (`bundle_agent_experiment/tools.py`): `read_file(path,
start_line?, end_line?)`, `grep(pattern, glob?)`, `list_dir(path?)`, all
hard-scoped to `repo_root` (path escape raises `ValueError`), reads
truncated to 200 lines, grep capped at 30 matches. **Hard mechanical
budget: 8 tool actions per bundle** (`MAX_TOOL_ACTIONS`); on exhaustion
the agent is told once to return a final decision immediately (using
`INSUFFICIENT_EVIDENCE`/`INCONCLUSIVE` with `stop_reason:
"BUDGET_EXHAUSTED"` if unresolved), and if it still doesn't comply, a
synthesized `INSUFFICIENT_EVIDENCE` fallback is recorded — not a silent
retry loop. Absolute hard cap of 14 API calls per bundle regardless
(guards against a model that never emits parseable JSON). Fresh
`messages` list per bundle — no cross-bundle memory. `temperature=0.0`.

**Operational definitions logged, not left implicit:** "expansion hop" =
one more distinct file opened via `read_file` beyond the candidate's own
file (`tools.py::ToolBudget.expansion_hops`) — a proxy for the
instructions' "hops away from the candidate," not a semantic
import-graph distance. This is a measurement/reporting convention only;
it does not gate anything mechanically (the 8-action cap is the only
hard mechanical stop, consistent with the system prompt's own "budget is
a ceiling, not a target" framing).

## 6. Output schema reconciliation

The task instructions give Arm A a short 7-field schema (§3) but then
say Arm B "returns the SAME judgment schema as Arm A so results are
directly comparable" (§3) while the frozen Codex system prompt (§4)
specifies a much richer, different final-response schema. These two
statements are in tension in the source instructions. Resolution adopted
here: **each arm keeps its own natively-specified schema** (Arm A's
7-field schema; Arm B's full Codex-investigator schema, since it is
explicitly "part of the experiment," frozen, and versioned) — invented
after the fact would be exactly the kind of unlogged judgment call this
project's discipline exists to avoid. Comparability is achieved instead
by a `comparable_view` normalization computed post hoc from each arm's
raw output for the side-by-side tables in the report: `decision`,
`confidence`, `reasoning_summary`, and a merged `citations` list
(Arm A's `requirement_citations` + `code_citations`; Arm B's
`verified_initial_evidence` + `new_evidence_found` locations). This
normalization is reporting-only — it does not feed back into either
arm's actual output.

## 7. Metrics (see task instructions §7–9 for full definitions; adopted as specified)

Judgment correctness against `expected_label` (where not `None`); false
PASS; false FAIL; appropriate-uncertainty rate on the `None`-label case;
relational-fact recovery (bundles 3/5 specifically); citation validity
(qualitative — read against the actual fixture files, since AR-017's
location-format mismatch makes the existing automated
`verify_evidence_citations()` checker unusable for the `Contract.function`
convention this project already uses); cost/latency/tokens per bundle;
Arm-B-only: tool actions used, files opened, expansion hops,
search-efficiency (relevant/total tool actions, classified by hand
against the bundle's own stated unresolved facts); abstention rate.

## 8. Most important causal comparison (task instructions §8)

For every bundle where Arm A and Arm B disagree, the report identifies
the exact new evidence (if any) Arm B found and traces whether it, not
a prompting difference, caused the different outcome — bundles 3 and 5
are pre-designed specifically to make this traceable (matched initial
evidence, opposite repo content).

## 9. Success criteria (task instructions §12, adopted verbatim as the acceptance frame)

Not treated as "agent wins if it gets more right." The report evaluates
all ten of the task instructions' §12 criteria explicitly, including
false-FAIL rate, honest handling of the genuine-uncertainty case,
tool-budget adherence, and over-search rate — a net win on raw
correctness alone is not sufficient for the report to recommend
agent-per-bundle or selective-escalation over LLM-only.

## 10. Comparison / interpretation rule (task instructions §13, frozen)

Outcome A (agent significantly outperforms via new evidence) → RTF needs
an investigation stage. Outcome B (agent matches Arm A at higher cost) →
agentic investigation is unnecessary for most bundles. Outcome C (agent
helps only where the bundle explicitly names an unresolved relational
question) → selective escalation is justified. This rule is applied
mechanically to the actual per-bundle results in the final report, not
re-litigated after seeing them.

## 11. Budget

Session cumulative spend before this batch: **$0.653435** of the
self-enforced $5.00 cap (`spend_guard.py`, checked before/after every
bundle exactly as in the Phase H root-cause batch). Estimated cost for
this batch: Arm A ≈ 7 calls × ~$0.01–0.02 ≈ $0.10; Arm B ≈ 7 bundles ×
up to ~9 API calls each (1 initial + ≤8 tool-triggering turns, growing
message history per turn) — real per-call cost for smaller,
single-candidate contexts should be lower than the 30-bundle Phase H
calls (~$0.006–0.015/call observed there), but the *cumulative* per-
bundle cost across ~5–9 turns could reach ~$0.03–0.08/bundle → est.
$0.20–0.55 total for Arm B. Combined estimate **$0.30–0.65**, well within
the remaining ~$3.35 margin before the $4.00 stop-new-calls threshold.
Execution halts immediately (mid-batch if necessary) if `spend_guard`
reports spend ≥ $4.00, with whatever bundles are already complete
reported as a partial result rather than blocked entirely.

## 12. Deliverables

Raw results + complete traces (`phase_bundle_agent_artifacts/` under
this directory): per-bundle Arm A raw response + parsed decision;
per-bundle Arm B full turn-by-turn trace (every tool call, observation,
and the final decision) + tool-action/token/cost accounting. Final
report: `BUNDLE_LLM_VS_CODEX_AGENT_EXPERIMENT.md`, structure per task
instructions §15.
