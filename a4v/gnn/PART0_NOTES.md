# Part 0 — API verification spike results

Run: `.venv/bin/python scripts/etl/verify_part0.py` (12/12 checks passed).

## ★ Explicit-solc kwarg

**Settled: use `extra_kwargs={"solc": "<abs path to solc binary>"}`.**

- `crytic_compile/platform/solc.py:_get_targets_json` reads `kwargs.get("solc",
  "solc")` and passes it straight through to `_run_solc` as the executable to
  invoke — it never touches solc-select's global-version file. Confirmed at
  runtime: compiling `tests/fixtures/features/Casts.sol` (pragma `^0.8.20`)
  and `tests/fixtures/wrong_solc/OldStyle.sol` (pragma `^0.4.24`) back-to-back
  with two *different* explicit solc paths left
  `~/.solc-select/global-version` absent both before and after (it doesn't
  exist on this host at all — `SOLC_SELECT_INSTALL_DIR` is unset, so the
  default `~/.solc-select` applies, and no repair/select code has ever run
  under this user).
- `solc_solcs_bin` (a map/list of literal paths) takes the same direct-path
  route via `_run_solcs_path` — an equally race-free fallback if `solc` is
  ever not honored for some crytic-compile platform other than plain solc.
- **Do not use `solc_solcs_select`** — it resolves through `_run_solcs_env`,
  which is solc-select's `switch`/`use` global-state path; this is exactly
  the shared mutable state the ETL must avoid under concurrent workers.
- Conclusion for A5/`compile_one.py`: always call
  `ProgramGraph.build(target, extra_kwargs={"solc": <abs solc path for the
  resolved version>})`. Never call `solc-select use`/`switch_global_version`
  from the ETL path (that's `repair.py`'s pattern for the *interactive* Phase
  1 pipeline, not for parallel batch compilation).

## `solc_force_legacy_json` (old-solc note for A4)

Against solc 0.4.24 and `OldStyle.sol` (old-style same-name constructor),
compilation **succeeded identically with and without**
`solc_force_legacy_json=True` — crytic-compile/Slither already auto-detects
legacy vs compact AST format from the solc version it invokes. No difference
observed at 0.4.24. **A4 should still try the flag as a fallback if a
specific old version's *auto-detection* misfires** (the plan flags the
legacy↔compact AST switch as a known breakpoint, historically around the
0.5.0 boundary) — it's a free, harmless kwarg to add when a version-specific
smoke probe fails without it.

## External-node representation

Confirmed on `tests/fixtures/multi_contract/Vault.sol` (has a low-level call):
external callees are **not** a distinct graph `kind`. They come back as
`kind="function"` nodes carrying `external=True` and (for calls crytic-compile
can't resolve to a concrete `Function`/`FunctionContract`) an `ext::` id
prefix, e.g. `ext::<low-level-call>` or `ext::<Contract>.<method>`. Any code
deriving an "is this an external/unresolved callee" flag (map_labels.py,
serialize.py, a future feature stage) must check `attrs.get("external")` or
`node_id.startswith("ext::")` — never `kind`.

## Line mappings / missing attrs

Not re-verified at runtime here (already confirmed by reading `graph.py`):
`_lines()` reads `source_mapping.lines`; `ext::` stub nodes and the
write-after-external-call fallback statevar node (graph.py:262, added when a
written var isn't already in the graph) both omit `lines`/`file` entirely.
`map_labels.py` must treat missing `file`/`lines` as unmappable, not raise.

## Edge kinds / node-level features

Not exercised here — deferred, matters only for Part B's `FeatureExtractor`
(`a4v/features.py`), which is out of scope for the Part A raw-graph
prototype.
