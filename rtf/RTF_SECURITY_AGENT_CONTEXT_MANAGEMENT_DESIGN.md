# Security-agent kernel: context-management redesign

Written before implementation, per this project's own established gate.
Extends `RTF_SECURITY_AGENT_EFFICIENCY_INVESTIGATION_20260817.md`'s
findings (read that first for the evidence this design responds to).
Primary research question this addresses: **is the kernel's low coverage
primarily an execution/context-management failure, and can a compacted,
state-driven investigation loop approach Codex-level completion reliability
without changing the underlying security reasoning task?**

---

## 1. Current architecture, traced (the "before")

Read directly from `rtf/security_agent/kernel.py`, `state.py`, `prompts.py`,
`model_client.py`, `responses_client.py` as they exist before this change.

### 1.1 Prompt construction (`kernel.py:155-159`)

```python
messages = [
    {"role": "system", "content": build_system_prompt()},          # tool list + response protocol
    {"role": "user", "content": build_initial_user_message(...)},   # protocol_context + ALL requirement
]                                                                    # contexts + cluster plan, inlined
```

`build_initial_user_message` (`prompts.py:91-126`) inlines the full
protocol context markdown, every distinct requirement's context markdown,
and the cluster plan directly into one message — for a cluster spanning
several distinct `requirement_id`s this is already substantial before a
single tool call happens.

### 1.2 How the transcript grows — every path only appends, never prunes

| Event | Kernel line | What gets appended | Ever removed? |
|---|---|---|---|
| Any real model turn | `kernel.py:181` | `json.dumps(turn.raw)` — the model's FULL raw parsed action (for `conclude`, this includes the entire evidence pool + hypotheses + all property assessments) | No |
| Tool call result | `kernel.py:230` | `f"Tool result for {action.tool}:\n{json.dumps(result)}"` — the RAW, full tool payload (e.g. `get_contract_source` returns the whole contract text) | No |
| Malformed response | `kernel.py:172-175` | the bad raw attempt + a corrective message | No |
| Completion-gate rejection | `kernel.py:203-206` | note: the REJECTED conclude's full raw JSON was already appended at line 181 (unconditionally, before the gate check), PLUS a rejection message | No |
| Internal action-application error | `kernel.py:240-243` | an error message (the raw response was already appended at line 181) | No |

There is no code path anywhere in `kernel.py` that removes, summarizes, or
truncates anything from `messages`. It is a strictly monotonically growing
list for the entire life of a cluster investigation.

### 1.3 Retry semantics (the malformed-response loop, `kernel.py:161-176`)

Each failed attempt adds 2 messages (bad attempt + corrective instruction)
and stays permanently. Three consecutive failures (the default
`max_malformed_retries=2` → 3 total attempts before giving up) therefore
adds up to 6 messages that are never removed, even though only the LAST
attempt's outcome (give up, or succeed) matters going forward.

### 1.4 Token usage: measured after the fact, used for nothing

`_record_token_usage` (`kernel.py:325-334`) only accumulates
`state.token_usage` from the real API response, post-hoc. Nothing in the
loop reads this value to make any decision — there is no proactive size
check anywhere before sending the next request.

### 1.5 Responses API: no session/caching features used

`responses_client.py`'s `ResponsesChatClient.complete()` sends a fresh,
fully-reconstructed `input` array from `messages` on every call. The
Responses API supports `previous_response_id` chaining (server-side
conversation continuation, avoiding client-side resend of full history) —
not used anywhere in this kernel.

### 1.6 State exists, but is not authoritative for context

`ClusterInvestigationState` (`state.py`) already tracks requirement
statuses, evidence, hypotheses, tool history, inspected files/contracts/
functions, and unresolved questions — genuinely close to what a
"structured investigation state" should be. But it is used only as a
**side-effect record** for final output (`to_property_verdict_entries()`)
and completion-gate checks (`completion.py`). Nothing rebuilds `messages`
from `state` — the two are updated independently, and `messages` is what
actually gets sent to the model every turn.

### 1.7 Consequence, confirmed empirically

From the efficiency investigation: `cluster_005`'s real prompt sizes across
its own lifetime: 6,062 → 28,860 → 28,918 → 42,870 → 43,527 tokens. This is
`messages` growing exactly as described above — nothing here is
speculative, it is the direct, mechanical consequence of §1.2.

---

## 2. Design principle

> The structured investigation state is authoritative. The raw
> conversation history sent to the model on any given turn is a
> **derived, reproducible view**, rebuilt from that state plus a bounded
> recent-turns window — never an ever-growing accumulation.

Every valid model action: (1) validate, (2) update state, (3) persist
state, (4) rebuild the next turn's context from state — not from blindly
appending to what was already sent.

---

## 3. Structured state: extend, don't replace

`state.py`'s existing `ClusterInvestigationState`/`RequirementState`/
`Hypothesis`/`Evidence` already cover most of what's needed. Mapping
against the requested shape, field by field:

| Requested | Existing equivalent | Action |
|---|---|---|
| `properties: list[PropertyState]` | `requirement_states: dict[str, RequirementState]` | keep as-is (dict keyed by property_id is strictly more useful than a bare list) |
| `PropertyState.status` incl. `INCONCLUSIVE` | `RequirementResolution` (4 states, no INCONCLUSIVE — "UNRESOLVED + reason" was the prior stand-in) | **extend**: add `INCONCLUSIVE` as a real 5th terminal status (see §7 — circuit breakers need to actively CONCLUDE "inconclusive", which is different from "never got there") |
| `hypotheses: list[HypothesisState]` | `hypotheses: dict[str, Hypothesis]` | keep as-is |
| `evidence: list[EvidenceRef]` | `evidence: dict[str, Evidence]` | **extend**: add a `summary` field (short, always-in-context) distinct from full content (externalized, see §4) |
| `inspected_files: list[str]` | `inspected_files: set[str]` (+ contracts/functions) | keep as-is |
| `unresolved_questions: list[str]` | already exists, both cluster- and requirement-level | keep as-is |
| `next_actions: list[str]` | does not exist | **add** to `ClusterInvestigationState` |
| `step_count: int` | already exists | keep as-is |

No new state module. These are small, additive changes to `state.py`.

---

## 4. Evidence externalization

The measured bloat source is **not** the `Evidence` Pydantic objects
themselves (already compact by prompt design: id/claim/source
location/short excerpt) — it is **raw tool results** appended verbatim at
`kernel.py:230` (§1.2). `get_contract_source` on `Float128.sol` alone
returns tens of thousands of tokens of source text, sent to the model
in full, every single time it appears anywhere in the (never-pruned)
transcript.

New `rtf/security_agent/evidence_store.py`:

```python
class EvidenceStore:
    def __init__(self, cluster_scratch_dir: Path): ...
    def store(self, tool_call_id: str, tool: str, result: dict) -> StoredEvidence:
        """Writes the full raw tool result to
        <cluster_scratch_dir>/evidence/<tool_call_id>.json, returns a
        StoredEvidence(evidence_id, summary, path) -- summary is a short,
        deterministic, non-LLM string (file/contract/function/line-range +
        a fixed-length head of any source text), NOT a re-summarization
        by the model itself (cheap, reproducible, no extra LLM call)."""
    def read(self, evidence_id: str) -> str:
        """Full raw content, for the read_evidence tool."""
```

`kernel.py`'s tool-result handling changes from "append the full JSON" to:
externalize via `EvidenceStore.store(...)`, append only the compact
summary + evidence_id to `messages`. A new tool, `read_evidence(evidence_id)`,
added to `SecurityAgentTools.TOOL_NAMES`, lets the model retrieve full
content on demand — expected to be rare, since the model already saw the
relevant excerpt once and can cite line numbers directly.

This directly targets the single largest measured contributor to context
growth without weakening evidence auditability — the FULL raw content is
still on disk, still traceable by evidence_id, just not resent by default.

---

## 5. Deterministic context compaction

New `rtf/security_agent/context_manager.py`. No LLM-based summarization —
compaction is a pure function of `ClusterInvestigationState` plus a small
window of recent raw turns, so it is reproducible and testable without a
model in the loop.

```python
SOFT_COMPACTION_TOKENS = 20_000   # see rationale below
HARD_COMPACTION_TOKENS = 60_000
RECENT_TURNS_KEPT = 4

def estimate_tokens(text: str) -> int:
    """len(text) // 4 -- a cheap, dependency-free heuristic (no tokenizer
    dependency added for this). Deliberately conservative: real token
    counts are logged post-hoc via ChatResult and can validate/recalibrate
    this constant later without changing the estimator's call sites."""

def build_context(
    state: ClusterInvestigationState, cluster_context: ClusterContext,
    recent_turns: list[dict],
) -> list[dict]:
    """Deterministically rebuilds the full `messages` list: system prompt
    + cluster context (protocol/requirement/plan, unchanged) + a
    STRUCTURED STATE SUMMARY (property statuses, hypotheses with status,
    an evidence INDEX -- id/claim/location only, not full excerpts --
    unresolved questions, next_actions) + only the last RECENT_TURNS_KEPT
    raw turns verbatim. Called once at cluster start (recent_turns=[]) and
    again whenever the soft threshold is crossed."""
```

**Threshold rationale** (not arbitrary, tied to the efficiency
investigation's own data): the pathological clusters' prompts were
consistently fine under ~29K tokens and consistently produced empty/capped
completions once they crossed ~42K. `SOFT_COMPACTION_TOKENS=20_000` leaves
real headroom before the danger zone the data shows; `HARD_COMPACTION_TOKENS=
60_000` sits just under the ~65K pathological ceiling observed pre-fix, as
a last-resort safety net. Both are named constants, explicitly not claimed
final — Part 12's own instrumentation (§10) will show the real post-fix
context-size distribution, which is the actual basis for tuning these
later, not a one-time guess.

What survives compaction unconditionally: system/security-agent
instructions, cluster objective/plan, parent EthTrust requirement context,
the properties being evaluated, structured property statuses, hypotheses,
evidence index, unresolved questions, next actions, the last N raw turns.
What gets dropped: old raw tool output (superseded by the evidence index +
`read_evidence`), superseded/malformed turns, old retry exchanges,
duplicate file content already summarized in the evidence index.

---

## 6. Retry semantics: branch from the last valid state, don't accumulate

Current (`kernel.py:161-176`): every failed attempt appends 2 permanent
messages. New behavior: track only the CURRENT retry's exchange; on a new
retry, replace (don't append to) the prior failed exchange, so `messages`
after N failed attempts is the same length as after 1 failed attempt —
only the final valid outcome (success, or exhaustion) contributes lasting
state.

**Structured output investigated and used where supported.** The Responses
API (already in use via `responses_client.py`, confirmed working live for
`reasoning.effort`) supports `text.format: {type: "json_schema", ...}`
for schema-constrained output. `ResponsesChatClient` gains an optional
`response_schema: dict | None` parameter (generated once from
`RESPONSE_MODELS`' Pydantic `.model_json_schema()` — a discriminated union
on `action`), sent when supported. **Not assumed to work** — this is a
genuinely open question for GLM-5.2 via OpenRouter's Responses proxy (only
`reasoning.effort` has been confirmed working live so far); implemented
with a hard fallback: if the API rejects the `text.format` parameter (a
4xx on first use), disable it for the rest of that client's lifetime and
fall back to the existing fenced-JSON prompt contract, logged once so it's
visible in results rather than silently degrading forever unnoticed.

---

## 7. Circuit breakers

`SecurityAgentKernel` gains `max_wall_clock_s: float | None` (default:
generous, e.g. 600s per cluster — tunable, not treated as final, same
"named constant, revisit with real data" discipline as §5's thresholds).
Checked each loop iteration alongside the existing `max_steps`/
`max_malformed_retries`.

On any circuit breaker tripping (wall-clock, steps, or malformed-retries
exhausted): instead of immediately marking every property
`mark_unresolved_reason(...)` and returning, issue **one final forced-
conclusion turn** using whatever evidence/hypotheses already exist:

```text
The investigation budget is nearly exhausted. Using only the evidence
already collected: resolve every property that can safely be resolved;
mark unsupported properties INCONCLUSIVE; cite evidence for PASS/FAIL;
do not perform further exploration.
```

If that forced turn produces a valid, schema-conformant response (even a
partial one, per-property), apply it normally through the same
`_apply_conclusion` path (still gated by the completion check for any
attempted PASS — a forced conclusion does not weaken PASS evidence
requirements, per this task's explicit constraint). Anything still
unresolved after the forced attempt (or if the forced attempt itself fails)
is marked the new `INCONCLUSIVE` status (§3), not silently left
`UNRESOLVED`. This directly targets the efficiency investigation's finding
that 7/22 clusters produced **zero** resolved properties — a forced
conclusion turn, using evidence that was often already substantially
gathered before the spiral, should recover partial coverage from at least
some of those.

---

## 8. Progress detection

`ClusterInvestigationState` gains a cheap, deterministic fingerprint
method:

```python
def progress_fingerprint(self) -> tuple:
    return (
        len(self.evidence), len(self.hypotheses),
        tuple(sorted((h.id, h.status.value) for h in self.hypotheses.values())),
        tuple(sorted((pid, rs.status.value) for pid, rs in self.requirement_states.items())),
        len(self.unresolved_questions),
    )
```

The kernel tracks the fingerprint after each valid step; `N` (configurable,
default 3) consecutive identical fingerprints trigger: force a conclusion
attempt (reusing §7's mechanism directly — same "wrap up with what you
have" prompt), or compact once and retry, then `INCONCLUSIVE` if still no
movement. Logged as a `no_progress_detected` trajectory event (§10) so
it's visible in results, not just inferred after the fact.

---

## 9. Clustering/property-pool reproducibility

Confirmed (not assumed): `grouping_engine.py`'s `cluster_properties` is
internally deterministic given a fixed input order (its own docstring:
"ties broken by property_id for full reproducibility"; verified by reading
the merge logic). The non-determinism is upstream, in how the property
pool is assembled before clustering runs.

[Root cause pending a parallel, dedicated investigation into the exact
upstream mechanism — to be finalized in this section, along with the exact
minimal fix, once that investigation reports back. The fix, whatever the
exact mechanism, is expected to be a stable-sort/ordering fix only (no
change to which properties end up compatible/incompatible), per the same
discipline applied everywhere else in this document: understand the real
mechanism before touching it.]

Regardless of the exact upstream fix, checkpoint/resume already keys on
property_ids, not cluster names (`live_runner.py`: `set(cluster.property_ids)
<= resolved_property_ids`) — the ask to "generate a stable fingerprint from
the actual property IDs" is largely already true at the resume-matching
layer; the bug is that WHICH properties end up in a same-named cluster
differs run to run, defeating that matching. Fixing the ordering fixes this
without needing to change the resume-matching logic itself.

---

## 10. Instrumentation

Extends the existing `TrajectoryWriter`/`event_sink` mechanism (`kernel.py`'s
`_emit`, already wired) — no new logging framework. New event types:
`context_compacted` (tokens before/after, trigger: soft/hard), `no_progress_detected`,
`forced_conclusion_attempted`, `circuit_breaker_tripped` (which one: wall_clock/
steps/malformed_retries/no_progress). Per-cluster summary (computed at
`cluster_finished` time from `state`/trajectory, written into
`investigator.py`'s `SecurityAgentResult`): property/PASS/FAIL/
NOT_APPLICABLE/INCONCLUSIVE counts, turns, malformed count, retry count,
tool calls, max context tokens seen, compaction count, wall clock, cost,
termination reason, forced-conclusion triggered (bool), no-progress event
count, checkpoint-resume status. Run-level aggregation (a small new script,
not a pipeline change) computes resolution %, cost/time per resolved
property, malformed-response rate, max-step rate, compaction stats, and
the heavy-tail cluster-duration distribution — the same shape of analysis
done by hand for the efficiency investigation, now mechanical.

---

## 11. Test plan (Part 11, before any live rerun)

- **Context**: simulate a long investigation (many turns, large synthetic
  tool outputs) with a fake tool client; assert context stays under the
  hard limit, compaction triggers at the right point, and every required
  element (parent requirement, every property, current statuses,
  hypotheses, evidence index, recent turns) survives a compaction while
  old raw output does not.
- **Retry**: inject malformed JSON, `content: None`, schema-invalid
  actions, truncated output; assert retries branch from the last valid
  state (message count does not grow with retry count), the retry budget
  is respected, and a valid retry updates state exactly once.
- **Evidence**: assert an evidence reference surviving compaction still
  resolves to the exact stored source via `read_evidence`; assert PASS/FAIL
  never cite an evidence id absent from the store.
- **No-progress**: construct a trajectory of equivalent repeated actions;
  assert the circuit breaker activates at the configured threshold, not
  before or after.
- **Determinism**: run clustering multiple times (identical order, shuffled
  order, separate subprocess invocations) on the same fixture property set;
  assert identical final cluster/property-set fingerprints every time.
- **Resume**: start → resolve a subset → terminate → restart → resume;
  assert already-resolved properties are never re-investigated and cluster
  renumbering cannot invalidate checkpoint state.
- **Full existing regression suite** stays green throughout — no
  exceptions.

---

## 12. Explicitly out of scope for this change

Per this task's own constraints: no change to semantic-property generation,
no change to clustering POLICY (only ordering/determinism), no weakening
of PASS evidence requirements, no benchmark-specific tuning. `INCONCLUSIVE`
being reachable more often via forced conclusions is an accepted, correct
outcome — it is explicitly not a failure mode this design tries to avoid;
converting "zero coverage" into "an honest INCONCLUSIVE with partial
evidence" is the actual goal of §7.
