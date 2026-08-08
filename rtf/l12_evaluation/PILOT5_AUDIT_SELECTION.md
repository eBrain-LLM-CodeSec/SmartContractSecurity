# 5-Audit End-to-End Pilot: Audit Selection Record

Frozen before any pipeline run, per the pilot's own rule (ground truth
findings may not be read before `audit.md`/traces are frozen for that
audit). This document records selection methodology and exposure only —
no requirement routing, evidence, or Codex investigation happens here.

## 1. Exposure ledger finding (pre-selection)

Before selecting, a full prior-exposure audit was run across all 40
EVMbench entries by inspecting this project's own artifacts (never
opening audit finding text for anything not already exposed). Result:

**0 of 40 audits have NONE exposure**, because the predecessor MGPR
system (`a4v/mgpr/`, this project's prior track) was built directly from
`data/mgpr/benchmark_registry.jsonl`, which contains every audit's
finding titles + descriptions across the full 40-entry corpus. That
registry was read in detail before any RTF work began (see
`rtf/l11_correspondence/EXPOSURE_DECLARATION.json`). This is a real,
structural limitation of doing RTF work in this codebase, not an
oversight specific to this pilot — logged here explicitly rather than
worked around by redefining "NONE" to mean something it doesn't.

Full breakdown: **25 SUBSTANTIAL** (quoted vulnerable code + explicit
exploit-mechanics correspondence judgments in
`rtf/l11_correspondence/correspondence_mapping.json`, or a full RTF run +
real DetectGrader scoring in `rtf/l12_evaluation/runs/RUNS_REGISTRY.json`
— `2023-07-pooltogether` and `2026-01-tempo-mpp-streams` specifically);
**15 LIMITED** (7 "floor-only" — registry title/description known, never
reasoned about further; 6 "family-reviewed" — vulnerability-family
classification reviewed in `data/mgpr/reviewed_family_labels.jsonl`, no
quoted exploit mechanics found; 2 build-blocked/no-source-ever-compiled).

**Incident during this selection**: while checking `config.yaml` layout
for non-finding repo metadata, `2023-12-ethereumcreditguild`'s H-01
title+description was read in full before recognizing that entry's
config embeds findings inline (unlike the directory-per-finding pattern
most other audits use). Caught immediately; no further findings text was
read for that or any other entry. `2023-12-ethereumcreditguild` is
excluded from this pilot's candidate pool as a result — LIMITED but not
floor-only, and freshly (not just historically) tainted.

## 2. Selection rule for this pilot (explicit user decision)

Per direct instruction: keep the original NONE/LIMITED/SUBSTANTIAL
definitions unchanged (no redefinition), record the 0-NONE finding
plainly (above), and **preferentially sample the 5 pilot audits from the
LIMITED tier, prioritizing the floor-only subset** (title/description
known via the historical registry, never reasoned about beyond that).
`2023-12-ethereumcreditguild` excluded per the incident above.

Floor-only candidate pool (7 minus the excluded entry = 6):
`2025-01-liquid-ron`, `2024-01-canto`, `2024-01-init-capital-invitational`,
`2024-03-neobase`, `2024-05-arbitrum-foundation`, `2024-06-vultisig`,
`2025-10-sequence`.

## 3. Diversity data (non-finding fields + shallow git clone only)

| entry | total size | own-scope `.sol` files (excl. `lib/`, `node_modules/`, `test/`, `out/`, `cache/`, `script/`) | build tooling | structural notes |
|---|---|---|---|---|
| `2025-01-liquid-ron` | 2.2M | 10 | foundry only | smallest own-code footprint of the pool |
| `2024-01-canto` | 3.0M | 4 | foundry + npm | tiny own-code amid large vendored dependency tree |
| `2024-01-init-capital-invitational` | 445K | 105 | foundry only | **known build-blocked** — `RTF_V1_RUN2_REPORT.md:21` documents source never successfully compiled in a prior RTF run |
| `2024-03-neobase` | 3.0M | 5 | foundry + npm | near-duplicate profile to `2024-01-canto` (tiny own-code, large vendored tree, same tooling) |
| `2024-05-arbitrum-foundation` | 1.2M | 142 | foundry + hardhat + Yul | largest own-scope code of the pool; includes raw Yul assembly files |
| `2024-06-vultisig` | 2.0M | 85 | foundry + hardhat | custom `hardhat-vultisig/` subdirectory, hybrid tooling |
| `2025-10-sequence` | 4.6M | 49 | foundry + pnpm workspace | largest total repo; multi-package monorepo layout (`pnpm-workspace.yaml`) |

None of the 7 candidates use git submodules (`.gitmodules` absent in
every shallow clone) — dependencies are vendored as plain committed
files under `lib/`, unlike `2023-07-pooltogether`'s true-submodule
pattern. This removes that specific historical infra gotcha (see
`CLAUDE.md`'s PoolTogether reproduction notes) as a concern for this
pool, though it does not rule out other build issues.

## 4. Final selection (frozen)

**Selected (5), all LIMITED/floor-only exposure:**

1. `2025-01-liquid-ron` — commit `b0df3cffce6e1a151c1c32dea8b17dd4f8932cf7`
2. `2024-01-canto` — commit `cec6952e832f05e836a96223d8e12aa7b0641c15`
3. `2024-05-arbitrum-foundation` — commit `1ede95fe9198887481aa5824fe58eb776ff763a3`
4. `2024-06-vultisig` — commit `607f320dd21ceaee567a937ab77847641f0614bf`
5. `2025-10-sequence` — commit `70fc6ba76d8088bdf07634d2bb9555b6c4fe3a96`

Commits are the default-branch HEAD of each `evmbench-org/<id>` GitHub
repo at the time of this selection (each audit's own `Dockerfile` clones
the default branch with no pinned checkout, so this is exactly what a
fresh container build would produce today) — frozen here for pilot
reproducibility, matching the project's established pattern
(`2023-07-pooltogether`'s pinned `4240445e...` commit in `CLAUDE.md`).

**Selection rationale**: `2024-03-neobase` was dropped from the 6-entry
floor-only pool as structurally redundant with `2024-01-canto` (near-
identical size, tooling, and own/vendored-code ratio) — keeping both
would not add real diversity. `2024-01-init-capital-invitational` was
dropped in favor of the other 5 due to its documented prior build
failure (a genuine, already-known infrastructure risk from a past RTF
run, not new information about this pilot's difficulty) — including it
would very likely consume one of five pilot slots on a foregone
`INFRASTRUCTURE_BLOCKED` outcome rather than new pipeline signal. Both
are retained as documented reserves, substitutable only if one of the 5
selected audits turns out infrastructure-blocked during this pilot's own
run (per the pilot's own rule against silently dropping blocked audits).

**Not selected, and not considered further**: no SUBSTANTIAL- or
non-floor-only-LIMITED-tier audit was drawn on, since the floor-only
pool alone supplied 5 usable, sufficiently diverse candidates without
needing to reach further.

## 5. Exposure declaration for this pilot (per audit)

| audit | exposure | what is known |
|---|---|---|
| `2025-01-liquid-ron` | LIMITED (floor-only) | finding title + one-line description, from `data/mgpr/benchmark_registry.jsonl`, never reasoned about beyond that |
| `2024-01-canto` | LIMITED (floor-only) | same |
| `2024-05-arbitrum-foundation` | LIMITED (floor-only) | same |
| `2024-06-vultisig` | LIMITED (floor-only) | same |
| `2025-10-sequence` | LIMITED (floor-only) | same |

No audit in this pilot is genuinely NONE-exposure, disclosed per SS1
above. No audit in this pilot is SUBSTANTIAL-exposure. This is uniform
across all 5 — nothing in this pilot mixes fresh and previously-studied
audits at different depths, so no per-audit exposure-tier distinction
needs separate reporting within the pilot itself (contrast with e.g. a
future pilot that deliberately included `2023-07-pooltogether`).
