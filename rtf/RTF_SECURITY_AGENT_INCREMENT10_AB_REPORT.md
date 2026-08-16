# Security-agent Increment 10: controlled live A/B

Date: 2026-08-16. Both arms used `z-ai/glm-5.2` through OpenRouter with the
same prompt, context artifacts, timeout, compiler settings, and synthetic
`security_agent/fixtures/input_validation_ok/Fixture.sol` target. The frozen
input fingerprint was
`93040fb997c4e80e9b75a506cb6ed375c95c0984bd3ef4400492b596776553e4`.
No real EVMbench target source was sent.

## Result

Both the general Codex arm and the custom security-agent arm returned `PASS`
for `safe-input-domain`. Both explicitly tested the zero and negative-input
counterexamples and found the `require(value > 0)` guard. Thus verdict
agreement was 1/1 with no disagreement.

| Metric | Codex | Security agent |
|---|---:|---:|
| Input tokens | 49,449 | 4,807 |
| Cached input tokens | 22,205 | not reported separately |
| Output tokens | 1,150 | 911 |
| Tool calls | 5 shell | 1 typed inspection |
| Files inspected | 4 | 1 |
| Wall clock | 43.53 s | 11.61 s |
| Cost field | $0.048330625 | $0.001340064594 |

The custom arm used about 9.7% of Codex's input tokens and 26.7% of its wall
time on this case. The cost row must not be interpreted as a provider-cost
ratio: the custom value is OpenRouter-reported actual cost, while the Codex
value is an estimate produced by historical, frozen GPT-5.1 Codex pricing
constants. Codex CLI did not expose GLM's provider-reported cost.

## Live compatibility defects found and fixed

1. Codex CLI 0.147 completed but did not reliably flush the requested `-o`
   file or final stdout event before the wrapper parsed results. The wrapper
   now falls back to the newest canonical Codex rollout for the final agent
   message and cumulative token usage.
2. The legacy JSON extractor spanned from the first Markdown code fence to
   the last. An explanatory Solidity fence before the final JSON therefore
   yielded a false `None` decision. It now walks individual fences backward
   and returns the last valid JSON object.
3. A piped `head -80` option was incorrectly counted as a touched filename.
   File extraction now rejects option-shaped matches, and A/B metrics count
   Codex shell commands plus graph calls and the union of observed files.

Regression tests cover all three behaviors. The already-paid Codex session
was recovered from its artifacts; it was not rerun to repair the report.

## Interpretation and next gate

This one synthetic safe case demonstrates semantic agreement and a materially
smaller custom-agent execution footprint. It does not establish vulnerability
recall, robustness on large repositories, or statistical superiority. The
next meaningful increment is a preregistered frozen-RTF evaluation containing
both PASS and FAIL properties. That step sends real audit source and incurs a
new paid external run, so it remains a separate authorization gate.
