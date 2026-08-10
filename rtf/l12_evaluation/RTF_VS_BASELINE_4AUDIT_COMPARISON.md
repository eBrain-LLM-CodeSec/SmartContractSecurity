# RTF pipeline vs. simple single-shot baseline — 4-audit comparison

Real, paid, completed comparison across 4 small, diverse, previously-unseen
EVMbench audits (none ERC-4626/ERC-20 vaults, deliberately different from
`2025-01-liquid-ron`), each run through both the full RTF pipeline
(requirement routing, deterministic + agent-required evaluation,
concurrency enabled) and a simple, single-shot, non-RTF Codex baseline
(`rtf/l12_evaluation/simple_baseline.py`, using the exact production
single-shot audit prompt from `backend/worker_runner/detect.md`). Both
sides use the same model (`openai/gpt-5.1-codex-max`), the same real
checkout, the same real `DetectGrader`.

## Results

| Audit | Domain | RTF score | RTF cost | RTF wall time | Baseline score | Baseline cost | Baseline wall time |
|---|---|---|---|---|---|---|---|
| 2025-04-forte | Floating-point math library | 0/5 | $2.8364 | 27.6 min | 0/5 | $0.1368 | 3.7 min |
| 2024-08-phi | NFT / creator rewards / bonding curve | 1/6 | $3.7350 | 37.9 min | 1/6 | $0.5151 | 11.3 min |
| 2026-01-tempo-feeamm | AMM (reentrancy) | 1/1 | $2.5426 | 29.7 min | 1/1 | $0.1685 | 3.0 min |
| 2024-01-canto | Lending/reward ledger | **0/2** | $3.2354 | 34.0 min | **1/2** | $0.0957 | 2.9 min |
| **Total** | | | **$12.3494** | | | **$0.9161** | |

## Honest reading — no spin

**RTF did not outright win on any of these 4 audits.** Tied on 3 (forte,
phi, tempo-feeamm — same score both ways) and **lost outright on canto**
(baseline caught H-01, RTF's 37 real investigations did not, despite
multiple RTF findings touching the exact same `update_market()` function
per the judge's own reasoning). Cost was consistently **~15-30x higher**
for RTF across all 4, and wall time ~8-13x longer even with 5x
concurrency enabled.

This is a materially different picture from the earlier `2025-01-liquid-ron`
result (RTF: 1/1 detecting H-01 via a generated ERC-4626 requirement;
see `RTF_PIPELINE_AND_REQUIREMENTS_REFERENCE.md`), and the difference is
explainable, not contradictory:

- **None of these 4 targets are ERC-4626/ERC-20 vaults.** The GP/ERC-
  standards generator (`rtf/standards/`) — the specific new capability
  that produced LiquidRon's win — contributed few or no additional
  *applicable* requirements here (`requirements_applicable` ranged
  49-61 out of 172 considered, well below LiquidRon's 149, meaning most
  of the 91 generated requirements resolved `NOT_APPLICABLE` for these
  non-vault targets, exactly as intended -- see §1.3/§2.4 of the
  reference doc for what that state means). RTF's remaining edge on
  these 4 audits is purely the 81-EthTrust-requirement corpus's atomized,
  per-requirement decomposition (deterministic + ~30-42 agent
  investigations each) versus one continuous holistic session.
- **On this small sample, atomized decomposition did not reliably beat
  a single holistic pass**, and in canto's case, plausibly diluted
  attention: RTF's investigations found the *code region* (`update_market`)
  under several different requirement lenses (external-calls,
  state-writes, etc.) without any one of them being shaped to ask the
  *specific* time-vs-block-number epoch-calculation question H-01/H-02
  hinge on — the same "class C/E" pattern documented in the LiquidRon
  forensic analysis, just without a generated requirement this time to
  close the gap, because none of the 91 generated clauses are about
  lending-ledger epoch/reward-accounting semantics (only ERC-4626/ERC-20
  are registered standards so far).
- The **simple baseline's own real strength**: one continuous session
  that reads the whole (small) codebase once and reasons across all of
  it together, rather than fragmenting attention across dozens of
  narrowly-framed lenses. For a SMALL, single-file target, that
  continuity is a real advantage a decomposed approach doesn't
  automatically get back just by adding concurrency.

## What this does and doesn't imply

- It does **not** undermine the LiquidRon result — that win came
  specifically from the generated ERC-4626 requirement whose text
  independently matched H-01's mechanism, a mechanism this 4-audit
  sample structurally cannot exercise (no vault targets).
- It **does** suggest the atomized-decomposition-of-the-static-corpus
  part of RTF (independent of the GP generator) is not, by itself, a
  reliable improvement over a simple single continuous session on a
  small target — and costs meaningfully more to run either way.
- The natural next question -- whether registering MORE standards (not
  just ERC-4626/ERC-20) would recover RTF's edge on non-vault targets by
  giving the generator something applicable to fire on -- is a real,
  answerable follow-up, not attempted here.

## Infra notes (per the explicit request to monitor for issues)

Three real, previously-undiscovered infrastructure gaps were found and
fixed BEFORE any of these 4 runs were launched (zero-cost compile
verification first, per instruction) -- see `compile_helper.py` commit
`95f5f4f`: foundry.toml-only remappings (tempo-feeamm), an `--allow-paths`
too narrow for a relative import escaping its own directory (forte), and
a missing `--via-ir`/`--optimize` passthrough (canto, whose own
`foundry.toml` requires both). A fourth, live, standing infra corruption
was found and fixed mid-run: the shared, machine-global `solc-select`
artifact for `0.8.17` was mislabeled (reporting itself as `0.8.20`),
blocking canto's RTF launch; reinstalled and reverified before retrying.
All 8 runs (4 RTF + 4 baseline) completed cleanly after these fixes, zero
further infra failures, `integrity_valid=True` on all 4 RTF runs.
