# Evidence flow trace (Phase H work item 2)

Traced from real code (`run_rtf.py`, `registry.py`, `judge_with_l8.py`)
and confirmed against real, already-collected data
(`v2_run1_artifacts/pooltogether_routed.json`) -- not inferred from
reading the modules alone.

## Path, end to end

1. **`registry.py`**: `REGISTRY: dict[str, list[PredicateSpec]]`, keyed by
   `req_id`, built by sequential `_reg(...)` calls at module load time. A
   Python dict preserves insertion order, and the `_reg` calls are fixed
   source code, so registry iteration order is deterministic run to run
   -- but that order reflects nothing about relevance, only the order
   requirements happen to appear in the source file.
2. **`run_rtf.py::run_rtf()`**: for each `req_id`, for each `PredicateSpec`
   in that requirement's list (in registration order), calls the
   predicate function once (`_run_predicate_spec`). Each predicate
   returns a `list[dict]` of findings in WHATEVER order its own internal
   loop visits Slither's compiled contracts/functions -- effectively
   Slither's own AST/compilation-unit enumeration order, which is itself
   an accident of file/import order, not a relevance ranking.
3. Findings are appended into one `all_evidence: list[EvidenceItem]` per
   requirement, in exactly this order: (predicate registration order) x
   (that predicate's own internal enumeration order). No sorting,
   deduplication, or filtering happens anywhere in this path.
4. `RoutedRequirementResult.evidence = tuple(all_evidence)` -- order
   preserved into the archived/serialized artifact.
5. **`judge_with_l8.py` (pre-Phase-H)**: `build_judgment_question(evidence,
   max_items=30)` took `evidence[:30]` -- literally the first 30 items in
   step 3's order -- and appended "(...and N more, omitted)" for the
   rest. **Ordering was deterministic. Relevance was not considered at
   any point in this path.**

## Why PoolTogether produced 739 items for `req-3-all-valid-inputs`, concretely

Loaded the real archived artifact and counted directly (not estimated):

```
739 raw evidence items = 681 from find_unvalidated_function_parameters
                        +  58 from find_unsafe_narrowing_cast
```

`find_unvalidated_function_parameters` scans **every function in every
compiled contract, all visibilities** (a deliberate, requirement-text-
justified design choice -- see AR-011: the requirement's own "Tested
Code" definition has no visibility restriction). PoolTogether's real
compiled target pulls in `console2` (forge-std's debug-logging shim,
vendored transitively under `lib/forge-std/`) alongside the project's own
~15 real contracts. Grouping the 739 items by contract:

```
console2: 383   (52% of all evidence -- forge-std debug shim, zero audit relevance)
Vault: 43
PrizePool: 36
TwabController: 34
... (33 more contracts, real project code + vendored OpenZeppelin/prb-math/etc.)
```

`console2` sorts FIRST in Slither's own contract enumeration for this
target, so its 383 irrelevant findings occupy indices 0-382 of the flat
list -- more than the entire 30-item cutoff on their own. The evidence
this project's own `RTF_V2_RUN1_REPORT.md` identified as the one that
flips PoolTogether's H-02 to a stable FAIL in isolated testing --
`Vault._burn`'s `find_unsafe_narrowing_cast` finding -- sits at raw
index **737 of 739**. It was not merely "diluted" among the top 30; it
was **excluded from the prompt outright, every single run**, by a cutoff
that has nothing to do with relevance.

## Fix implemented (work items 3-5): `rtf/l12_evaluation/evidence_ranking.py`

- `rank_evidence()`: scores each item on four requirement/code-derived
  signals only (priority-contract membership, structured-evidence
  specificity/completeness, explicit protection-status assessment,
  named concrete operation) -- see that module's docstrings for each
  signal's derivation. Deduplicates exact repeats.
- `build_evidence_bundles()`: merges same-location findings (e.g.
  `Vault._burn`'s generic `find_unvalidated_function_parameters` finding
  and its specific `find_unsafe_narrowing_cast` finding, previously two
  separate flat items at indices 674 and 737) into ONE coherent bundle
  per the schema Phase H work item 4 specifies.
- `apply_evidence_budget()`: takes the top-N BUNDLES (not flat items),
  so a cutoff can never split one location's evidence the way the old
  flat cutoff could and did.

**Concrete, real-data-verified result** (see
`test_evidence_ranking.py::test_real_pooltogether_narrowing_cast_survives_budget_that_previously_excluded_it`,
run against the actual archived 739-item artifact, no new LLM calls):
under the new ranked-bundle pipeline with the SAME budget size (30),
`Vault._burn`, `Vault._mint`, and `Vault._transfer` rank **#1-3** (score
0.9833 each) -- the three exact functions named in EVMbench's own H-02
fix diff. Zero `console2` items survive into the 30-bundle budget.

## Wiring (`judge_with_l8.py`)

`judge_result(..., use_ranking: bool = True)`: the ranked-bundle path is
now the default live behavior. The OLD flat-list builder
(`build_judgment_question`) is deliberately kept, not deleted -- work
item 5 requires comparing the new approach against "current flat-list
behavior... as a baseline," which needs the old path to remain callable
via `use_ranking=False`.

## Still open (not yet run -- requires live LLM calls)

The top-1/top-3/top-5-bundle vs. flat-list vs. no-ranking-baseline
COMPARISON EXPERIMENT itself (work item 5's second half: measuring how
each configuration affects L8's actual final judgment, not just which
evidence reaches the prompt) has not been executed yet -- the
deterministic ranking/bundling/budget machinery is built and proven
against real archived evidence, but running it through live L8 calls
under each configuration is separate, costed work, tracked as the next
step (work items 6+).
