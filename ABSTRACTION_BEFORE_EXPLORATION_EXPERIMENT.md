# Abstraction-Before-Exploration Experiment

**Date:** 2026-08-28
**Audit / Property / Target:** `2024-01-canto` / `req-3-implement-as-documented::loc0` / `LendingLedger.update_market`
**Run artifacts:** `/scratch/md5344/evmbench/rtf_canto_abstraction_before_exploration_glm53_20260828/`
**Launch script:** `abstraction_before_exploration_glm53_launch.py`
**Deterministic tests:** `rtf/security_agent/test_abstraction_before_exploration.py`

## 1. Hypothesis

A major reason cheaper/open models (GLM-5.3) underperform GPT-5.6 Sol on
this property is that they explore code before forming a sufficiently
discriminating test of the property — Sol forms an abstraction (relevant
state dimensions, a scenario where correct/incorrect behavior diverge)
*before* broad exploration; GLM-5.3 explores immediately and produces a
valid-but-non-discriminating scenario. Tested: does mandating a short,
generic abstraction-before-exploration methodology close this gap for
GLM-5.3, with the model and everything else held constant?

## 2. Minimal implementation

**One file touched for the actual investigation policy: `rtf/security_agent/prompts.py`** (mirrored into the frozen `a61d547` baseline checkout used for this experiment specifically — see §3). No changes to `kernel.py`, `state.py`, `response_schema.py`, `tools.py`, or the tool set.

Two edits, both pure prompt text:

1. **`SYSTEM_PROMPT_TEMPLATE`**: replaced the existing soft one-sentence
   hint ("Start with at least one plausible failure hypothesis per
   property") with a mandatory four-item methodology, mapped onto the
   **existing** `Hypothesis` fields — no new schema:
   - PROPERTY + VARIABLES + DISCRIMINATOR → written into `claim` (one
     structured paragraph: "(1) the exact behavior being verified, (2)
     which input/state dimensions could change whether it holds, and (3)
     a valid scenario where a correct and an incorrect implementation
     would behave observably differently").
   - MINIMAL PLAN → written into `next_evidence_needed` ("(4) the minimum
     code/evidence needed to evaluate that scenario").
   - One added sentence for the exploration-discipline rule (Step 4):
     "Prefer tool calls that directly test the current scenario — if a
     call would not help evaluate it or resolve a specific missing
     dependency, reconsider whether it is necessary before making it."
2. **`build_initial_user_message`**'s closing line: changed from "Begin
   your investigation. Use your tools to inspect the actual code before
   concluding anything about any property" to require the four-item
   abstraction via `update_investigation` before the first exploratory
   tool call.

**Incidental wording change, disclosed:** the adjacent sentence "record
the concrete adversarial or boundary scenario you tried" became "record
the concrete scenario you traced" — not a separate deliberate fix, but a
direct, unavoidable consequence of the paragraph immediately above it now
defining what a valid scenario is (a discriminator per the methodology,
not necessarily adversarial); keeping the old "adversarial" wording there
would have put two competing definitions in adjacent sentences.

**Step 5 (soft mid-investigation checkpoint) was deliberately skipped.**
Per Step 1's inspection: the kernel has no existing periodic/staged hook
to reuse (every tool is available from turn 1, no planning-phase
mechanism exists), so adding one would itself be "a new orchestration
stage" — the task's own explicit prohibition. Documented as a scoped-out
choice, not an oversight.

**No hard mechanical gate was added.** This is an instruction, not an
enforced precondition — consistent with Step 4's "do not hard-cap... we
want to observe whether the methodology itself reduces unnecessary
exploration," and with native tool-calling already allowing
`update_investigation` and exploration tools in the same turn.

## 3. Experimental controls

Only investigation methodology changed. Specifically verified, not assumed:

- **Model**: `z-ai/glm-5.3` in both — identical to the original 0/3 baseline.
- **Kernel/scaffold**: the methodology change was applied to the **frozen
  `a61d547` + `881eeb3` throwaway checkout** (`glm53_baseline_checkout`),
  the exact same pinned scaffold every prior GLM-5.3/Sol/DeepSeek/Kimi/
  MiniMax capability test in this session used — **not** this worktree's
  current HEAD, which also carries the anti-anchoring gate (`73bf68c`).
  Applying the methodology to the main worktree instead would have
  introduced a second, uncontrolled variable (a schema/completion-logic
  difference neither baseline used). Confirmed via direct diff against
  the checkout's pre-patch `completion.py`/`state.py`/`kernel.py`: zero
  changes outside `prompts.py`.
- **Source revision / scope / property / plan**: pipeline regeneration
  reproduced **byte-identical `cluster_011`, 1,032-char trimmed plan**
  (same SHA as every prior test on this property) before any live call —
  confirmed live, not assumed.
- **Tools, completion rules, cost/step limits, evidence handling,
  ground-truth isolation**: unchanged — see §4 for the specific
  regression tests that verify this directly rather than by inspection
  alone.

## 4. Deterministic tests

`rtf/security_agent/test_abstraction_before_exploration.py` — **5/5 passed.**
Full existing suite (`pytest rtf/security_agent/ -q`) — **245/245 passed**
(240 pre-existing + 5 new; zero regressions).

| Test | Result |
|---|---|
| A. Methodology present (checked via the real `build_system_prompt()`/`build_initial_user_message()` output, not raw source-text — see note below) | PASS |
| B. No Canto/ground-truth leakage (`nextEpoch`, `epoch boundary`, `500000`, `600000`, `reward misattribution`, `block_epoch`, `canto` — all absent) | PASS |
| C. Tool surface unchanged (13 read tools + `update_investigation`/`conclude`, exact name-set match) | PASS |
| D. Completion logic unchanged (PASS gate still rejects a property with zero counterexample_attempts, `pass_without_counterexample_attempt`) | PASS |
| E. Baseline configuration identical to the original GLM-5.3 experiment (`BASELINE_CHECKOUT`, `AUDIT_ID`, `TARGET_PROPERTY_ID`, `MODEL`, `MAX_STEPS`, `MAX_COST_USD` compared programmatically between the two launch scripts) | PASS |

**A real, if minor, bug found and fixed while writing Test A**: the new
prompt paragraph used Python triple-quoted-string line-continuation
(`\` immediately followed by a newline, the same convention the rest of
the file already uses) but two consecutive lines were missing the
trailing `\`, so the raw *source text* on disk contained a literal
mid-sentence newline ("the exact behavior\nbeing verified"). This had
**no effect on the actual rendered prompt** (Python's line-continuation
still joined it correctly at parse time — confirmed by direct evaluation
before and after the fix) but broke a naive raw-source-grep test; fixed
by adding the missing `\` characters in both the main worktree's and the
frozen checkout's copy, and the test itself was corrected to check the
real rendered string via the public API rather than raw source text.

## 5. Live results

| Run | Scenario level | Target bug | Tool calls | Input / output tokens | Cost | Time |
|---|---|---|---|---|---|---|
| 1 | 1 — VALID_NON_DISCRIMINATING | No | 4 | 75,633 / 3,492 | $0.0526 | 74.5s |
| 2 | 1 — VALID_NON_DISCRIMINATING | No | 4 | 60,814 / 3,954 | $0.0420 | 78.5s |
| 3 | 1 — VALID_NON_DISCRIMINATING | No | 4 | 60,922 / 4,097 | $0.0428 | 75.3s |

Scored via `rtf.security_agent.eval.scenario_scorer.score_canto_gate_run`
(the same ground-truth-aware Level 0-3 classifier built and calibrated
earlier this session against all 7 known Canto-gate runs) — **0/3 target
detection, all three Level 1.**

## 6. Baseline comparison

| Metric | Baseline GLM-5.3 (no methodology) | Methodology GLM-5.3 |
|---|---:|---:|
| Target detection | 0/3 | 0/3 |
| Level-2+ scenario | 0/3 | 0/3 |
| Target mechanism traced | 0/3 | 0/3 |
| Avg tool calls | 4 | 4 |
| Avg decide calls | 6.67 | 5.33 |
| Avg input tokens | 81,796 | 65,790 (−19.6%) |
| Avg output tokens | 4,531 | 3,848 (−15.1%) |
| Avg cost | $0.0511 | $0.0458 (−10.4%) |
| Avg wall-clock | 119.8s | 76.1s (−36.5%) |

## 7. Trajectory analysis

Every run's **very first model turn** called `update_investigation`
alongside its first exploration calls (`get_contract_source`/`read_file`),
producing a hypothesis whose `claim`/`next_evidence_needed` do follow the
four-item structure — the methodology was genuinely exercised, not
ignored:

- **Run 1** `claim`: *"LendingLedger's NatSpec/comments describe behavior
  ... that the code does not actually implement. A violation would be a
  documented statement contradicted by code ... Discriminating scenario:
  pick each documented claim in LendingLedger.sol and trace the
  corresponding function to see if behavior matches."*
- **Run 2** `claim`: *"LendingLedger.sol's NatSpec/comments describe
  behavior that differs from actual implementation ... a correct vs
  incorrect implementation differ observably in sync_ledger/claim/
  update_market behavior vs their comments."*
- **Run 3** `claim`: *"LendingLedger.sol's code deviates from its own
  documentation ... Discriminating scenario: pick a documented behavior
  ..., trace the code, and compare against the README/NatSpec
  description; a mismatch = FAIL."*

**Did the abstraction guide later tool calls?** Yes, consistently — all
three runs then read the contract source and README, and every
subsequent counterexample attempt directly followed through on exactly
the plan stated (compare each documented claim to code; all three landed
on the same claim()-NatSpec-vs-implementation mismatch). There is no
wandering, no dependency-descent into unrelated contracts, no abandoned
hypothesis — the *procedural* discipline the methodology asked for was
followed faithfully in every run.

**What the abstraction never contains, in any of the 3 runs:** a
DISCRIMINATOR that identifies a *specific state dimension to vary*
(e.g., "check what happens when configuration differs across two
instances of the same recurring interval boundary"). All three
"discriminating scenarios" are the same generic move one level up: "check
every documented claim against the code" — a real abstraction step, but
one that operationalizes the property as a *documentation-consistency
audit*, not as a *state-transition correctness check*. This is the
single, consistent pattern behind all three misses.

## 8. Cost/efficiency impact

The methodology **decreased** cost, tokens, decide-calls, and wall-clock
across the board (see §6) — it did not increase overhead. The mechanism
is visible directly in the trajectories: forcing the abstraction into the
very first turn (mixed with the first exploration calls, since native
tool-calling allows both in one turn) front-loaded planning that the
baseline runs otherwise spread across more, smaller round-trips. Tool
call count itself was unchanged (4 in every run, methodology or not) —
the efficiency gain is in round-trips and token volume, not investigation
breadth.

## 9. Interpretation

```
MODEL CANNOT RELIABLY IDENTIFY THE DISCRIMINATING DIMENSIONS
```

Per the task's own decision rule (0/3 → STOP, then classify Case A vs
Case B): every run is **Case B** — the model still produces LEVEL 1
scenarios, not LEVEL 2. It genuinely engaged with the methodology's
*procedure* (produced the four items, in the required fields, before
broad exploration, and stayed on-plan afterward) but the *content* of its
DISCRIMINATOR never rose above "audit documentation claims against code"
— a real abstraction, just not the one needed to expose a state-transition
bug. This indicates the remaining gap is model reasoning capability
(recognizing which state dimensions actually matter for THIS class of
property), not investigation policy — scaffolding cannot manufacture an
insight the model doesn't have available to state, even when explicitly
asked to state it before acting.

## 10. Next recommendation

**Do not add more prompt rules to this property/model pairing** — the
task's own guidance after a Case B result. The one recommended next
experiment: **test the same unmodified methodology against GPT-5.6 Sol on
this identical property**, to check whether the methodology is neutral
(as it was for GLM-5.3 — same accuracy, better efficiency) or actually
*helps* Sol construct its discriminating scenario faster/cheaper than it
already does unprompted (Sol's existing single-run baseline: $0.054, 6
tool calls, 44s). This directly tests whether "abstraction-before-
exploration" is a genuinely capability-agnostic efficiency lever (worth
keeping regardless of model) or coincidentally neutral only because
GLM-5.3's ceiling was already the limiting factor. Per the task's own
Step 12, DeepSeek is explicitly a separate, later experiment (testing
whether the methodology reduces DeepSeek's context-congestion/tool-search
explosion specifically) — not to be mixed into this one.
