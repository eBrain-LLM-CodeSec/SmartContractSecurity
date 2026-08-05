# L8 live validation — first real model execution

Two small, deliberately cost-controlled live runs (5 repeated calls each,
`openai/gpt-5.1-codex-max` via OpenRouter) against PoolTogether's real
`Vault.sol` (1232 lines, unzipped from
`run/pipeline_validation/fixed_pooltogether_entry/upload.zip` in the
sibling evmbench deployment), to fill in the two go/no-go criteria that
couldn't be assessed from unit tests alone: evidence-citation validity and
LLM decision-flip rate. See `rtf/track_a/GO_NO_GO.md` for how these feed
into the go/no-go verdict.

## Two real bugs found and fixed by this exercise (not in this directory —
see `a4v/llm.py` and `rtf/l8_llm_judgment_layer/judgment_layer.py`)

1. **Extra stray closing brace.** `openai/gpt-5.1-codex-max` occasionally
   emits a complete, valid JSON object followed by one extra `}` --
   `json.loads` correctly rejects this as "Extra data" even though the
   actual object is well-formed. Fixed in `a4v/llm.py` by falling back to
   `json.JSONDecoder().raw_decode`, which parses the first complete value
   and ignores trailing garbage, specifically only for that error class (a
   genuinely truncated/broken response still raises, verified).
2. **Unclosed fence.** The model sometimes opens a ` ```json ` fence and
   never closes it. The original two-way branch in
   `extract_last_fenced_json` conflated "no fence at all" with "exactly
   one fence, unclosed", parsing the *entire* raw text (including the
   ` ```json ` prefix) in both cases -- wrong for the unclosed case. Fixed
   with a proper three-way branch.
3. **Cache defeated "independent" repeated calls.** `a4v.llm.ChatClient`
   caches by exact `(model, messages, temperature)`. `judge_stability` and
   `judge_with_second_pass` called with identical inputs at temperature 0
   were therefore just replaying the *same* cached response on every
   "independent" call -- flip rate was trivially always 0/N and
   second-pass disagreement could never be detected, silently defeating
   both mechanisms. Fixed by bypassing the cache (deleting the relevant
   entry before the call) for every repeat call beyond the first. All
   three fixes are covered by `rtf/l8_llm_judgment_layer/selftest.py`
   (18/18 passing, no network access).

## Run 1 — `01_balance_check_vs_vault.py`

Question: does Vault.sol contain an exact-equality balance check (the
`req-2-verify-exact-balance-check` trigger)? **Result: 5/5 runs answered
`INCONCLUSIVE`, zero evidence emitted, 0/5 flip rate.** This is a
*correct* negative result, not a failure — Vault.sol genuinely uses
`!=`/`>`/`>=` comparisons around balances, never a literal `==`, so the
requirement's own trigger condition is absent. Confirmed by the model's
own `reasoning_summary` in `01_result.json`. Because no evidence was
emitted, this run contributes nothing to the citation-validity metric
(0/0, undefined) but does contribute a genuine, stable 0/5 flip-rate data
point.

## Run 2 — `02_implement_as_documented_vs_vault.py`

Question: does Vault.sol's actual behavior match two specific NatSpec-
documented error conditions (`req-3-implement-as-documented`)? **Result:
5/5 runs answered `PASS`, 11/11 total evidence citations valid (files
exist, line ranges in bounds), 0/5 flip rate.** Independently spot-checked
by hand against the real file (not just schema/existence checked): the
cited line ranges (`Vault.sol:1198-1201`, `Vault.sol:1218-1223`) exactly
correspond to `_requireVaultCollateralized` and `_setYieldFeePercentage`,
matching what the model's evidence claims. This is a real, verified,
accurate result, not merely a schema-valid one.

## Feeding into go/no-go criteria 5–6

- **Citation validity**: 11/11 = 100%, well above the 95% threshold.
  Sample size is small (one run, one file, 11 citations) — this
  demonstrates the mechanism works correctly, not that 100% validity holds
  at scale across many files/requirements.
- **Decision-flip rate**: 0/5 and 0/5 across both runs (10 total repeated
  calls, all stable) — well under the 10% threshold. Same caveat: small
  sample, and both runs happened to land on an "easy" answer (clear
  absence, clear presence) rather than a genuinely borderline case where
  flips are more likely.
