# Reproducible evaluation environment — investigation and findings

**Trigger:** RTF v1 run 2 found 3 of 4 frozen-sampled audits blocked
(`2025-02-thorwallet`, `2024-03-taiko`, `2024-01-init-capital-invitational`)
because `forge` cannot run on this HPC node (GLIBC < 2.29, confirmed via
a real `foundryup` install attempt — AR-009) and no Node.js/npm runtime
is installed at all.

## Real, validated fix: Singularity containers

This node already has Singularity 3.6.4 available as a module
(`/share/apps/NYUAD5/singularity/current/bin/singularity` — the SAME
container technology this project's separate `SingularityBackend`
deployment already relies on, per the top-level `CLAUDE.md`). Singularity
containers bundle their own glibc, so running Foundry's binaries *inside*
one sidesteps the host's older glibc entirely — a fundamentally
different, and more general, fix than trying to build/patch a
glibc-compatible Foundry binary for this specific host.

**Confirmed working, both real pulls, both real executions** (not
assumed from documentation):

```
singularity pull foundry.sif docker://ghcr.io/foundry-rs/foundry:latest
singularity exec foundry.sif forge --version
  -> forge Version: 1.8.0-nightly  (real output, not simulated)

singularity pull node.sif docker://node:20
singularity exec node.sif node --version   -> v20.20.2
singularity exec node.sif npm --version    -> 10.8.2
```

Both pulls completed in well under a minute each (confirming outbound
network access to `ghcr.io`/Docker Hub works from this node, the same
access already used to `git clone` real EVMbench audit repos). Image
sizes: `foundry.sif` 205MB, `node.sif` 321MB — small enough to keep in
scratch space per-job, not something that needs bundling into this git
repo.

## What this actually unblocks, checked per audit, not assumed

| Audit | Blocker (run 2) | Fixed by the container alone? |
|---|---|---|
| `2024-03-taiko` | No vendored `lib/`, would need `forge install` | **Yes, in principle** — `forge install` now runs; not re-verified end-to-end in this pass due to time (taiko's `packages/protocol` is a large L2-rollup subtree; a full `forge install` + compile attempt was out of scope for this bounded investigation) |
| `2025-02-thorwallet` | No Node.js/npm runtime at all | **Yes, the runtime blocker is fixed** — `npm install` inside `node.sif` would now be able to run; not re-verified end-to-end (needs `npm install` to actually fetch Hardhat + OpenZeppelin, untested in this pass) |
| `2024-01-init-capital-invitational` | No vendored `lib/`, **plus** a non-git `contracts/.cache/OpenZeppelin/...` dependency | **Partially tested, real gap found**: ran `forge install` (bare) inside `foundry.sif` against the real repo — it completed with no errors, but `lib/` remained empty afterward, because this repo has **no `.gitmodules`/forge dependency declarations at all** for `forge install` to act on. The `contracts/.cache/` directory is populated by some OTHER, audit-specific bootstrap mechanism not yet identified (no `Makefile`/install script found in a quick check) — **this audit has a genuine, audit-specific provisioning gap that container availability alone does not solve.** |

**Honest summary**: the container approach is a real, general, validated
fix for the *forge-binary-availability* and *node-runtime-availability*
blockers specifically (2 of the 3 original root causes). It does **not**
automatically solve every audit's dependency-provisioning story — some
audits (like init-capital) rely on custom, non-standard bootstrap steps
that need their own, per-audit investigation regardless of what runtime
is available.

## What was NOT done in this pass (explicitly out of scope, not silently skipped)

- **No single "everything bundled" container was built.** A combined
  image (Foundry + Node/npm + Slither + solc-select + this project's own
  `.venv`) is a real, larger engineering task -- assembling a Dockerfile/
  Singularity definition file, testing the FULL compile pipeline inside
  it (not just `--version` checks), and deciding how RTF's own Python
  predicates call out to it. This investigation validated the two
  hardest, most uncertain pieces (does Foundry even run under this
  node's Singularity via a pulled Docker image; does Node.js) rather than
  spending remaining time on packaging work that depends on those
  answers being yes.
- **taiko and thorwallet were not re-run end-to-end** with the new
  containers in this pass -- the runtime-level blocker is confirmed
  fixed, but actually compiling either (large L2-rollup dependency tree
  for taiko; a full `npm install` for thorwallet's Hardhat/OpenZeppelin
  stack) is real, separate follow-up work, not re-attempted here to keep
  this investigation bounded.
- **No change was made to `compile_evmbench_target()`** (the existing
  no-forge Slither workaround) -- it remains the working path for
  self-contained, vendored-`lib/` targets (confirmed on both
  `2023-07-pooltogether` and `2026-01-tempo-mpp-streams`). The container
  approach is a complementary, not a replacement, path: for a target
  whose dependencies are NOT already vendored, `forge install` (now
  runnable via the container) would need to populate `lib/` *first*,
  after which the SAME existing Slither-based compile workaround should
  work unchanged (not verified end-to-end in this pass).

## Concrete next steps (not done here, logged for future work)

1. `forge install` + compile `2024-03-taiko` end-to-end inside the
   container, confirm `compile_evmbench_target()` still works afterward
   with no code changes.
2. `npm install` + compile `2025-02-thorwallet` (a Hardhat project --
   may need a different compilation bridge than
   `compile_evmbench_target()`, which assumes a Foundry-style
   `remappings.txt`-based project; Hardhat resolves imports via
   `node_modules` instead, a genuinely different mechanism not yet
   investigated).
3. Find and document `2024-01-init-capital-invitational`'s actual
   `contracts/.cache/` provisioning step (likely in a README/CI config
   not yet read closely).
4. Only once 1-3 are concretely resolved: assemble a single combined
   Singularity definition file bundling everything this project's own
   `.venv` + Foundry + Node.js need, so a future audit-sampling run
   doesn't need per-audit runtime archaeology at all.
