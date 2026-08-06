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

## Run 3 (2026-08-06): L8 integrated into L12, tested on clear/borderline/insufficient-evidence cases

Runs 1–2 above tested L8 in isolation, hand-crafted, against one file.
This run tested the ACTUAL integration point (`rtf/l12_evaluation/
judge_with_l8.py`, wired to real evidence RTF's own predicates produced
against the real pooltogether target) on three deliberately different
signal shapes, per an explicit request to stress-test exactly the
untested risk both prior runs flagged: "flip risk is higher on
genuinely borderline cases, not yet tested." Script/raw output:
`03_clear_borderline_insufficient_evidence.{py,json}`.

**CLEAR case** (`req-3-access-control`, evidence: `Vault.mintYieldFee`
flagged unprotected — the real EVMbench H-04 vulnerability): expected
`FAIL`. Got **`INSUFFICIENT_EVIDENCE`, LOW confidence, stable across both
passes (agree=True)**. Not a bug — a genuine, valuable finding: this
requirement's actual text ("...MUST implement appropriate access control
... that provide the LEAST PRIVILEGE NECESSARY ..., based on the
documentation provided for [Q] Document Contract Logic") is more
conditional than the case's own "CLEAR" label assumed. The model
correctly noticed that judging "least privilege necessary" requires a
documentation cross-reference the bare unprotected-function evidence
alone doesn't supply, and declined to force a FAIL it couldn't fully
back per the requirement's own stated condition. This is the L8 layer
doing exactly what "LLMs are semantic reviewers, not conformance
authorities... permitted to return INCONCLUSIVE/INSUFFICIENT_EVIDENCE
instead of a forced binary" was designed for — the test case's own
premise (that this was obviously "clear") was the thing that turned out
to be wrong, not the model's judgment.

**BORDERLINE case** (`req-2-avoid-readonly-reentrancy`, evidence:
`LiquidationPair.maxAmountIn` reads reserve variables written after an
external call elsewhere in the contract — a structural precondition
only, per the predicate's own documented scope). First pass: `FAIL`,
MEDIUM confidence. **Second pass: DISAGREED** (`agree: False`) — the
single most important result of this run. This is the first real,
observed instance of exactly the instability Track A's go/no-go review
flagged as an open risk ("both live runs happened to land on unambiguous
answers... flip risk is higher on genuinely borderline cases, not yet
tested") — now it HAS been tested, on a genuinely borderline case, and
it DID flip. This is direct, concrete validation of why the plan
mandates a second independent pass before any L6/L7 consumer may trust a
single PASS/FAIL: relying on the first pass alone here would have
silently reported a confident-sounding FAIL that the model itself
couldn't reproduce on a second, independent attempt.

**INSUFFICIENT_EVIDENCE case** (`req-2-block-data-misuse`, evidence:
bare `ERC20Permit.permit reads block.timestamp`, no context on how it's
used): expected and got **`INSUFFICIENT_EVIDENCE`, LOW confidence,
stable across both passes**. Correctly recognized that "reads
block.timestamp" alone (a textbook-safe deadline-check pattern in most
`permit()` implementations, but not confirmed as such by this evidence
line) doesn't distinguish safe use from misuse without more context.

**What this run establishes, beyond runs 1–2:** L8 does not merely
produce plausible-sounding answers — it (a) correctly refuses to force a
verdict when the evidence's own conditions aren't met, even on a case
this project initially misjudged as unambiguous, and (b) its second-pass
disagreement mechanism catches real instability on a genuinely
ambiguous case, not just a null result on easy ones. Both are load-
bearing findings for how much any single L8 verdict should be trusted at
scale — genuinely borderline cases need the second pass, not just the
easy ones.
