# Track A step 3 — go/no-go review

Evaluated against the fixed, pre-registered thresholds from the plan's
Rev. 3 finalization patch. **Updated verdict: GO for the mechanism,
scoped explicitly to what's been exercised** — all 7 criteria are now
met, but two (5 and 6) rest on a small live sample and should not be read
as "proven at scale." See "Why this is a scoped GO, not an unqualified
one" below.

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | 100% of strategy components have a populated, non-empty derivation trace | **MET** | Every L4/L5/L6 component across all 6 requirements has a `derivation_trace` or equivalent `note` field explaining its reasoning — checked file-by-file, not sampled. |
| 2 | 100% of applicability decisions have a populated `derivation_log_entry` | **MET** | All 6 `rtf/track_a/l3_applicability/*.json` records have it populated, including the two AR-001 cases requiring manual re-read. |
| 3 | Zero unregistered assumptions found during independent review | **MET, via a genuinely independent (fresh, non-forked) subagent for L11, plus this session's own verification pass** | A self-review pass on the translation records (L1-L8) found and corrected one overreach (AR-002). Separately, L11's correspondence mapping was built by a fresh subagent with no exposure to this conversation's MGPR history (see `rtf/l11_correspondence/EXPOSURE_DECLARATION.json`), and this session then independently re-verified 17 of its 57 records against the real EVMbench finding files, finding and correcting one further misclassification (AR-003). Not a perfect guarantee (see AR-004, an open scope question left unresolved rather than forced), but real independent review did happen, not just self-review. |
| 4 | Every `EXACT_MATCH` claim passes source review + falsification tests, with pinned versions | **VACUOUSLY MET** | Zero `EXACT_MATCH` claims arose in this tranche (both compiler-bug S requirements landed at `PARTIAL_MATCH`, the third at `NO_MATCH`/`UNKNOWN`) — nothing to violate this criterion, which is a different thing from having positively demonstrated it works. |
| 5 | Evidence-citation validity ≥ 95% (reported as raw counts) | **MET: 11/11 (100%)** | Live run (`rtf/l8_llm_judgment_layer/live_validation/02_*`) against PoolTogether's real `Vault.sol`, 5 repeated calls (cache-bypassed, genuinely independent). Hand-verified, not just schema/existence-checked: the cited line ranges exactly match the real `_requireVaultCollateralized`/`_setYieldFeePercentage` functions. **Small sample — one file, one question, 11 citations. Demonstrates the mechanism works; does not establish 95%+ holds at scale.** |
| 6 | LLM decision-flip rate ≤ 10% (reported as raw counts) | **MET: 0/5 and 0/5 (two separate live runs, 10 repeated calls total)** | Same live runs as #5, plus a first run (`01_*`) that correctly and stably answered `INCONCLUSIVE` 5/5 times (a genuine negative result — Vault.sol has no exact-`==` balance check at all). **Both runs happened to land on a clear-cut answer; flip risk is higher on genuinely borderline cases, not yet tested.** |
| 7 | `INCONCLUSIVE`/`INSUFFICIENT_EVIDENCE`/untranslatable outcomes count as valid, not automatic no-go | **MET, AND EXERCISED** | `req-1-compiler-060` correctly resolved to a designed `INCONCLUSIVE` path rather than a guessed FAIL; `req-1-eip155-chainid` correctly resolved to `AMBIGUOUS_TEXT_GAP` rather than an invented predicate; the live run above added a third real example (`INCONCLUSIVE` on a genuinely absent trigger). All treated as valid findings, not failures. |

## Three real bugs found and fixed by actually running this live

Getting criteria 5–6 real data wasn't just "run it and read the numbers" —
doing so surfaced three genuine defects that unit tests alone had not
caught, all now fixed and covered by regression tests (`selftest.py`,
18/18 passing):
1. `a4v/llm.py`'s JSON extraction crashed on a real model response that
   had one extra stray closing brace after an otherwise complete, valid
   object.
2. The same function also mishandled a real response where the model
   opened a ` ```json ` fence and never closed it, parsing the fence
   markers themselves as if they were JSON.
3. `judge_stability`/`judge_with_second_pass` were silently defeated by
   `ChatClient`'s own caching — repeated "independent" calls with
   identical inputs at temperature 0 were just replaying the same cached
   response, meaning flip rate was trivially always 0 and second-pass
   disagreement could never be detected. Fixed by bypassing the cache for
   every repeat call.

Full writeup: `rtf/l8_llm_judgment_layer/live_validation/README.md`. Bug 1
and 2 are fixed in `a4v/llm.py`, which is *existing, shared production
infrastructure* (used by the Commentator/Auditor pipeline, not just RTF)
— this live-testing exercise found and fixed real bugs in code that
predates this session's work, a genuine side benefit beyond Track A
itself.

## Why this is a scoped GO, not an unqualified one

The mechanism has now been exercised end-to-end at least once, live,
against real code, with real citation verification and real repeated-call
independence — not just unit-tested in isolation. That's a meaningfully
stronger claim than the previous UNDETERMINED verdict. But the live
sample is small (one target file, two questions, 10 total repeated
calls), and both live runs happened to land on unambiguous answers
(clear absence, clear presence) rather than a genuinely borderline case
where a model is more likely to flip or hallucinate a citation. Declaring
this GO for Track A's mechanism is warranted; declaring the 95%/10%
thresholds "proven" at the scale Track B would need is not — that
requires a broader sweep across more requirements and targets, which is
Track B's job, not a retroactive claim this pass should make.

## What would strengthen this further (Track B, not blocking)

1. Run `judge_stability`/`judge_with_second_pass` against a genuinely
   borderline case (a target where the trigger condition is ambiguous or
   the code is partially-but-not-fully compliant) to stress-test
   citation validity and flip rate under harder conditions than this
   pass's two clear-cut examples.
2. Revisit AR-004 (the third-party-documentation scope question) with
   expert input before Track B relies on those `req-3-implement-as-
   documented` correspondence records at scale.

## Why this isn't NO-GO

Every criterion is met, and every gap encountered anywhere in Track A had
an honest, distinct classification (external-document dependency,
sound-but-unimplemented, genuine text-derivation limit, or corrected
on verification) — never a case where the mechanism was forced to
fabricate a result it couldn't support.
