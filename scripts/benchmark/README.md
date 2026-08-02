# Hermetic benchmark toolchain provisioning

Makes the MGPR/EVMbench build environment's Solidity-compiler selection
explicit, checksum-verified, and independent of session-specific caches.
See `/scratch/md5344/.claude/jobs/b51e9657/tmp/infra_benchmark_final_report.md`
(or wherever this session's final report was delivered) for the full
before/after investigation and validation results.

## How to provision (uses the network)

```
python -m scripts.benchmark.audit_build_manifest \
    --work-dir .benchmark/artifacts/manifest_scratch \
    --out .benchmark/artifacts/audit-build-manifest.jsonl
# processes one audit checkout at a time (clone -> resolve -> delete),
# never all 27 on disk simultaneously.

python -m scripts.benchmark.provision_toolchains \
    --manifest .benchmark/artifacts/audit-build-manifest.jsonl \
    --toolchain-dir .benchmark/toolchains \
    --lock-out .benchmark/artifacts/toolchain-lock.json
# downloads + checksum-verifies every required solc version exactly once
# into .benchmark/toolchains/solc/<version>/solc -- safe to re-run, already-
# provisioned versions are skipped (only re-verified).
```

## How to run offline (no network)

```
export PATH="$(pwd)/bin:$(pwd)/.venv/bin:$PATH"   # or wherever your venv/bin lives
export BENCHMARK_TOOLCHAIN_DIR="$(pwd)/.benchmark/toolchains"
export BENCHMARK_WORK_DIR="$(pwd)/.benchmark/runs/<run-id>/checkouts"
export BENCHMARK_OUT_DIR="$(pwd)/.benchmark/runs/<run-id>/study_full"
export BENCHMARK_REGISTRY_PATH="$(pwd)/data/mgpr/benchmark_registry.jsonl"
export BENCHMARK_CONTAINER_HOME="$(pwd)/.benchmark/runs/<run-id>/container_home"
export BENCHMARK_CONTAINER_TMP="$(pwd)/.benchmark/runs/<run-id>/container_tmp"
export BENCHMARK_STRICT_OFFLINE=1   # hard-fail rather than fall back to auto-detection/download

python -m scripts.mgpr.run_full_study_batch
```

Note: `forge install`/`npm install` (fetching each audit's OWN
dependencies, as opposed to the Solidity *compiler*) still requires
network access -- that is a pre-existing, separate dependency this work
did not attempt to eliminate. `BENCHMARK_STRICT_OFFLINE` governs compiler
*selection* only: whether `bin/forge` is ever allowed to let
Forge/`svm` decide dynamically to download a compiler.

## How to add a new required compiler version

Nothing to do by hand: `scripts.benchmark.compiler_resolver.resolve_compiler`
determines required versions per audit automatically from each audit's own
`foundry.toml`/`hardhat.config.*`/`Dockerfile`/pragma statements. Re-run
`audit_build_manifest` + `provision_toolchains` after adding or updating an
audit; the new version is picked up and provisioned automatically.

## How to add a new audit

1. Add an `AuditSpec` entry to `scripts/benchmark/audit_registry.py`,
   naming its subproject(s) (usually one, `SubprojectSpec("default", <run_cmd_dir>)`
   matching `audits/<id>/config.yaml`'s own `run_cmd_dir`). Only add a
   `foundry_version_override`/`override_reason` if you've independently
   confirmed (the way `2023-12-ethereumcreditguild`/`2024-06-size` were)
   that the generally-pinned Foundry release genuinely cannot compile it
   for reasons unrelated to solc version selection -- document *why*.
2. Add the audit_id to `scripts/mgpr/run_full_study_batch.py`'s
   `GENERIC_AUDITS`/`BESPOKE_AUDITS` list and, if it needs a bespoke
   compile recipe, a `compile_<name>()` function (see existing ones for
   the pattern). If it's a plain Foundry or Hardhat project with no
   special handling, it very likely just works via `compile_generic`.
3. Run `audit_build_manifest` + `provision_toolchains` restricted to just
   that audit (`--audit <id>`) to confirm resolution before a full run.

## How to diagnose a failure

Every audit's status in `build_manifest.jsonl` is one of:

- `COMPILED` -- succeeded.
- `TOOLCHAIN_NOT_PROVISIONED` -- the resolved compiler version isn't in
  the provisioned toolchain bundle; run `provision_toolchains` again
  (network required), or (in `BENCHMARK_STRICT_OFFLINE=1` mode) this is
  also what you get when a compile recipe was never wired to call the
  resolver at all (see "known remaining gaps" below) -- check whether
  `BENCHMARK_SOLC_PATH`/`FORGE_FORCE_SOLC` were actually set for that
  audit's compile call before assuming the toolchain itself is missing.
- `AMBIGUOUS_COMPILER_CONFIGURATION` -- the audit's own source has
  multiple conflicting compiler-version signals (a `[profile.default]`
  with contradictory `solc`/`solc_version` keys, or a bare pragma scan
  with no single dominant version and no authoritative project setting).
  This is never silently guessed; read `compiler_resolution_status`'s
  paired `reason`/`detail` field in the gate/build record for the exact
  candidates found.
- `NO_CONFIGURATION_FOUND` -- no compiler version signal anywhere at all
  (no config, no Dockerfile directive, no parseable pragma).
- `DEPENDENCY_INSTALL_FAILED` -- the audit's own `npm install`/
  `forge install` failed (network, a genuinely broken lockfile, etc.) --
  unrelated to compiler selection.
- `INFRASTRUCTURE_FAILURE` -- a container/filesystem-level problem in
  this specific deployment (e.g. a message containing "Read-only file
  system", or the repair-loop's own budget exhaustion message).
- `SLITHER_UNSUPPORTED_LANGUAGE_FEATURE` -- Slither itself cannot
  IR-generate a real language construct in the audit's source.
- `SOURCE_COMPILE_FAILED` -- none of the above matched; a genuine solc/
  compile-level error in the audit's own source, read the full `reason`.

## Known remaining gaps (not fixed in this pass)

- **The three bespoke Foundry recipes** (`compile_ethereumcreditguild`,
  `compile_size` in `run_full_study_batch.py`; `compile_noya` is
  Hardhat+Foundry hybrid) were **not** wired to call
  `compiler_resolver.resolve_compiler`/`provision_toolchains.provision_solc`
  the way `compile_generic` now is. Under `BENCHMARK_STRICT_OFFLINE=1`
  they therefore correctly fail closed (`TOOLCHAIN_NOT_PROVISIONED`)
  rather than falling back to Forge's own auto-detection -- this is the
  intended safety behavior, not a bug, but it does mean these three
  audits do not currently compile under strict-offline mode.
  `audit_build_manifest.py` confirms `2024-04-noya`'s compiler version
  *is* resolvable (`0.8.20`, via pragma fallback) -- wiring it in would
  very likely recover it. `2023-12-ethereumcreditguild` and
  `2024-06-size` genuinely resolve to `NO_CONFIGURATION_FOUND` even with
  the full resolver, and would need either a Dockerfile-derived pin or
  acceptance of pragma-fallback ambiguity to resolve further.
- **Foundry TOOL-version provisioning** (as opposed to the Solidity
  *compiler* version, which this work fully covers) is unchanged: the two
  audits needing a non-default Foundry release still depend on whatever
  is pre-installed under `.venv/.foundry-versions/`, which is itself a
  session-persistent cache, not freshly provisioned/checksum-verified by
  this work's Phase 2.
- **Audit dependency fetching** (`forge install`/`npm install`) still
  requires network access every run -- only Solidity *compiler*
  acquisition was made offline-safe, per this task's own framing
  ("network access... during the actual benchmark run" in context of the
  compiler-download regression being fixed).
- **Three genuinely ambiguous audits** (`2025-06-panoptic`,
  `2024-06-vultisig`, `2024-07-basin`) do not compile under this work by
  design -- their own source has multiple conflicting pragma-declared
  compiler versions with no project-level setting to disambiguate, and
  this resolver deliberately never guesses among them.
