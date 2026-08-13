# RTF v2: first live end-to-end run (generation → grounding → clustering → real Codex investigation)

Follows `RTF_V2_LIVE_VALIDATION_SEMANTIC_GENERATOR.md` (which validated
generation+grounding alone, no investigation). This run adds the
remaining stages via the new `semantic_only_driver.run_semantic_investigation`
(committed this session, mock-tested first — `test_semantic_only_driver.py`
— before this real invocation): real clustering with the existing engine,
then a **real Codex investigation subprocess** on the resulting cluster
(`run_arm_g_bundle`, same mechanism every other RTF investigation uses —
full repo copy, `--dangerously-bypass-approvals-and-sandbox`, graph MCP
tools available as supplementary aids).

Not a permanent test — run via a throwaway script
(`/scratch/md5344/.claude/jobs/a22997fe/tmp/live_e2e_investigation.py`,
not committed). This document is the durable record.

## Setup

- Same synthetic fixture family as the generation-only run: a
  `Vault` contract with `totalAssetsHeld`/`accruedFees`/`treasury`, a
  README describing it as a fee-charging asset vault. This run used a
  different `audit_id` label than the first live-generation check, which
  (correctly, by cache-key design — `audit_id` is the first line of
  `protocol_context.md`) produced a genuinely independent, uncached
  generation call rather than replaying the first run's cached response —
  useful here, since it gives two independent real samples rather than
  one repeated one.
- Generation: `z-ai/glm-5.2`, same as before. Investigation: same model,
  via the real `codex` CLI binary (`codex-cli 0.104.0`) exactly as every
  other RTF investigation in this project uses it.
- `cost_ceiling_usd=2.0`, `codex_timeout_s=480` — both comfortably above
  what this small, single-file fixture needed.

## Result

**Generation**: 7 properties proposed, all 7 accepted at generation, all
7 accepted at grounding (0 rejections either stage — consistent with the
first live-generation run's 0/8 rejection rate). **Cost: $0.00434.**

**Grouping**: all 7 properties fell into **one cluster**
(`cluster_000`), for real, substantive reasons —
`overlapping_candidate_locations`, `same_contract`, `same_reasoning_category`,
`shared_state_variables`, `source_proximity_same_file` — not a default/
fallback. This is Section 12's grouping goal working on real generated
properties, not just the hand-written grouping-engine unit tests.

**Investigation**: one real Codex call investigated all 7 properties
together. **Cost: $0.19924.** Total pipeline cost for this entire
generation→grounding→clustering→investigation run: **$0.204**.

| Property | Verdict | Real reasoning quality |
|---|---|---|
| `accrueFee` fee amount must derive from `totalAssetsHeld` + a rate, never decrease `totalAssetsHeld` | **FAIL** | Correct: the fixture's `accrueFee(uint256 amount)` takes a caller-supplied `amount` with no rate computation or access control — a genuine, independently-discovered bug, not one I specifically wrote the fixture to exhibit for THIS property's wording |
| `withdrawFees` must transfer to `treasury` and reduce `accruedFees` accordingly | **FAIL**, concrete counterexample | Correct: the fixture's `withdrawFees` decrements `accruedFees` but contains no transfer at all — a real gap the investigator caught by checking for the transfer call and finding none |
| `accruedFees` must never exceed `totalAssetsHeld` | **FAIL**, concrete counterexample (`accrueFee(100)` while `totalAssetsHeld=0`) | Correct and matches the exact bug class this whole redesign targets (an accounting invariant with no EthTrust/ERC clause shaped to ask this specific question) |
| `accrueFee` must not transfer tokens out of the vault | **PASS** | Correct: verified via both source read and graph-navigation `EXTERNAL_TARGETS` query — `accrueFee` really does only touch state, no external call exists to find |
| `withdrawFees` must only transfer to `treasury`, never elsewhere | **PASS** | Correct (if slightly ironic given the FAIL above): since `withdrawFees` transfers to NO address at all, it vacuously never transfers to a WRONG address either — the investigator explicitly noted this distinction rather than conflating it with the separate FAIL above |
| `totalAssets` must return a value "consistent with" `totalAssetsHeld` | **PASS** | Correct given this run's own (weaker) property wording — `totalAssets` does literally return `totalAssetsHeld` verbatim; this generation run phrased the property more loosely than the first run's "must equal totalAssetsHeld MINUS accruedFees" (see below) |
| `deposit` must not alter `accruedFees` | **PASS** | Correct: confirmed via source read and graph `STATE_WRITES` that `deposit` only touches `totalAssetsHeld` |

Every PASS carries an explicit `counterexample_attempt`/`counterexample_result`
pair explaining what was searched for and why it wasn't found — not a bare
"looks fine". Every FAIL carries a specific line reference
(`Vault.sol:13-15`, etc.) and a concrete, executable counterexample
sequence.

## An honest, useful discrepancy from the first live-generation run

This run's own generated wording for the `totalAssets` property
("must return a value consistent with `totalAssetsHeld`") is weaker than
the FIRST live-generation run's wording ("must return `totalAssetsHeld`
MINUS `accruedFees`") — and the investigator correctly PASSed the weaker
property, since the code trivially satisfies it. **This is not a
contradiction; it's the expected, correct behavior of property generation
being non-deterministic prose over the same underlying facts.** It also
surfaces a real, honest limitation worth recording rather than glossing
over: **a semantic property is only as strong as its own generated
wording** — this run's investigation would NOT have caught the specific
"doesn't subtract fees" framing of the bug, because this run's generator
never produced a property demanding that specific relationship. The other
FAIL findings (arbitrary fee amount, missing transfer, insolvency
invariant) are all genuine, real bugs in the fixture and were still
caught — but this is a concrete illustration of Section 11's dedup
concern from the other direction: independent generation runs produce
DIFFERENT (not just differently-phrased) coverage of the same underlying
protocol, and a single run's negative result on one specific framing
doesn't mean the property space is exhausted. Worth keeping in mind before
treating one live run as a full recall guarantee.

## What this validates

- The full pipeline runs end to end against a real Codex investigation,
  not just the generation/grounding half.
- Real generated properties cluster together for substantive, inspectable
  reasons, and one Codex call handles all 7 — the "one Codex session per
  coherent cluster" design goal (Section 14) holds on real data, not just
  synthetic `PropertyMetadata` fixtures.
- The investigation is genuinely rigorous both directions: it found real
  bugs with concrete counterexamples AND correctly passed genuinely
  correct behavior, including one property that could easily have been
  confused with an adjacent FAIL (`withdrawFees`'s two related but
  distinct properties) — it kept them straight.
- Total cost for one full synthetic-fixture run: **$0.204** — cheap
  enough that a handful of these runs (different fixtures, different
  models, checking calibration) is a reasonable next step before any real
  EVMbench spend.

## Still not validated (unchanged from the generation-only doc)

Real EVMbench targets are larger and noisier than this fixture; the
dedup/grounding thresholds remain calibrated only against hand-written
tests plus these two small live samples; no comparison yet against what a
structural-predicate-only pipeline would or wouldn't have caught on this
same fixture (out of scope for this run — this fixture has no EthTrust
routing set up at all, semantic-only by construction).
