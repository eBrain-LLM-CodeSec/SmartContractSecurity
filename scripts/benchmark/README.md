# Hermetic benchmark toolchain provisioning

Makes the MGPR/EVMbench build environment's Solidity-compiler selection
explicit, checksum-verified, and independent of session-specific caches.
Built across two passes: the first pass (Phase 1-4, `.benchmark/artifacts/`
committed at commit `8970f30`) established the resolver/provisioning/
strict-offline architecture and reached 21/27 compiling audits; the second
pass (this one) fixed the resolver bugs and wired the remaining bespoke
recipes that were blocking the other 6 (see "Fixed in a later pass" below),
plus ran the full Phase 5/6 cross-run reproducibility validation. See each
pass's own delivered final report for the complete before/after
investigation (paths given in the closing summary of each session; not
repeated here since job-scratch paths don't survive across sessions).

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
- `AMBIGUOUS_COMPILER_CONFIGURATION` -- an authoritative project setting
  itself conflicts (e.g. a `[profile.default]` declaring both `solc` and
  `solc_version` to different values). Plain diversity across files with
  no authoritative config to force one globally is NOT this status --
  see "Genuinely multi-version builds" above; it RESOLVES instead. This
  status is never silently guessed around; read `compiler_resolution_
  status`'s paired `reason`/`detail` field in the gate/build record for
  the exact conflicting candidates found.
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

## Genuinely multi-version builds (no `--use`, `--offline` + `~/.svm` instead)

A subproject can RESOLVE to more than one required compiler version with no
authoring conflict at all -- e.g. `2024-06-size`'s own `src/` pins `0.8.23`
while a few `test/`/`script/` files pin `0.8.13`/`0.8.19`/`0.8.0`; this is
exactly what Foundry's own default `auto_detect_solc` handles natively when
no single `solc` key is set (a different compiler per file, in the same
build). `_select_compiler` (`run_full_study_batch.py`) detects this case
(`len(resolution.versions) > 1`) and, instead of a single `--use <path>`
pin, populates the run's `CONTAINER_HOME` with a real
`~/.svm/<version>/solc-<version>` entry for every required version
(`scripts.benchmark.provision_toolchains.populate_svm_cache`) and sets
`BENCHMARK_FORGE_OFFLINE_AUTODETECT=1`, so `bin/forge` passes `--offline`
and lets Foundry's own per-file auto-detection resolve against that
provisioned set -- confirmed live: zero network access, and a version not
pre-populated fails closed with `No solc version installed that matches...`,
never a silent download.

Caret/range pragma constraints (`^0.8.0`) are extracted using their literal
lower-bound version for provisioning purposes -- a conservative superset,
not necessarily bit-identical to whatever a real online `forge` run might
have auto-selected among several range-compatible installed versions, but
fully deterministic and reproducible across runs, which is what this work's
Phase 5/6 requirements about identical cross-run coverage actually need.

## Fixed in a later pass (previously listed here as open gaps)

- **All three previously-unwired bespoke Foundry recipes**
  (`compile_ethereumcreditguild`, `compile_size`, `compile_noya`) are now
  wired to `_select_compiler`, the same resolver/provisioning path
  `compile_generic` uses (including the multi-version branch above where
  needed). All three now compile cleanly under `BENCHMARK_STRICT_OFFLINE=1`.
- **`2023-12-ethereumcreditguild`'s false `AMBIGUOUS_COMPILER_CONFIGURATION`**
  was two compounding resolver bugs, not a genuine conflict: (1) its
  vendored `forge-std` copy lives under `test/forge-std/` (its own nested
  `foundry.toml`), a location the old vendor-dir exclusion (name-based,
  `lib`/`node_modules`/etc.) never covered; (2) a naive `findall` over every
  `\d+.\d+.\d+`-shaped substring in a pragma constraint counted BOTH bounds
  of a range pragma (`>=0.6.2 <0.9.0`, routine in forge-std) as two
  separately "required" exact versions. Combined, these fabricated 7
  spurious version candidates out of forge-std's own wide-range pragmas;
  the project's actual own src/test code unanimously pins `0.8.13`. Fixed
  by `compiler_resolver._nested_vendor_dirs` (excludes any directory that
  itself contains its own `foundry.toml`/`hardhat.config.*`/`package.json`)
  and `_extract_exact_pin` (only a single-version-literal constraint votes;
  a range contributes nothing).
- **`2024-06-vultisig`'s false `AMBIGUOUS_COMPILER_CONFIGURATION`** was a
  missed config key: its own `foundry.toml` authoritatively pins
  `solc-version = "0.7.6"` (the older hyphenated Foundry key spelling,
  distinct from `solc_version`), which the resolver's two-key list never
  checked. Fixed by adding `"solc-version"` to `_parse_foundry_toml`.
- **`2025-06-panoptic`/`2024-07-basin`'s false `AMBIGUOUS_COMPILER_
  CONFIGURATION`**: both are genuine multi-version builds (see section
  above), previously misclassified because the old pragma-fallback branch
  treated ANY diversity among files as an authoring conflict rather than
  Foundry's normal per-file auto-detection behavior. Fixed by changing
  that branch's semantics -- see `compiler_resolver`'s own module
  docstring for the full reasoning.
- **A real concurrency bug in `provision_toolchains.verify_and_install`**:
  overwriting an already-provisioned solc binary in place
  (`shutil.copy2`) while another concurrent provisioning call was
  currently executing that exact binary raised `[Errno 26] Text file
  busy` -- found live running the six audits above in parallel. Fixed
  with an idempotent already-correct short-circuit plus a write-to-temp
  + atomic `os.replace()` for any real rewrite, so a concurrent reader/
  executor of the old inode is never disturbed.
- **`bin/forge`/`bin/npm`/`bin/npx` hardcoded `CONTAINER_HOME`**: direct
  `forge build`/`forge test` calls (Slither's own `subprocess.run(["forge",
  ...])`) always used one shared, cross-run-persistent directory regardless
  of which run's env vars were set, even though `run_dockerfile_recipes.py`'s
  `sh()`-routed npm/forge-install calls already respected a
  `BENCHMARK_CONTAINER_HOME` override -- a real gap for Phase 5's
  "fresh CONTAINER_HOME per run" requirement. Fixed by adding the same
  override to all three shims.

## Known remaining gaps (not fixed in this pass)

- **Foundry TOOL-version provisioning** (as opposed to the Solidity
  *compiler* version, which this work fully covers) is unchanged: audits
  needing a non-default Foundry release still depend on whatever is
  pre-installed under `.venv/.foundry-versions/`, which is itself a
  session-persistent cache, not freshly provisioned/checksum-verified by
  this work's Phase 2.
- **Audit dependency fetching** (`forge install`/`npm install`) still
  requires network access every run -- only Solidity *compiler*
  acquisition was made offline-safe, per this task's own framing
  ("network access... during the actual benchmark run" in context of the
  compiler-download regression being fixed).
