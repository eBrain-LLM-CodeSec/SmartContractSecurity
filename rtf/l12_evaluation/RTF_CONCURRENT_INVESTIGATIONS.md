# Concurrent Codex investigations

`run_pipeline_e2e(..., max_concurrent_investigations=N)` runs up to `N`
Codex investigations at once for one entry, instead of one at a time.
Default is `1` (unchanged, original serial behavior — every existing test
still exercises exactly that code path, byte-for-byte unmodified).

## Why

Wall-clock time, not cost. The standards-driven GP generator (`rtf/
standards/`) adds up to ~91 additional agent-required requirements per
entry on top of the 81-corpus's own AGENT_REQUIRED set — a real run
against `2025-01-liquid-ron`'s `LiquidRon.sol` needed ~125 total
investigations at ~3.5 min each, serially, which is a multi-hour run.
Real per-investigation cost is unaffected by concurrency (same total
tokens/API calls either way) — this only changes how many run at once.

## Design

Two phases (`_run_escalations_concurrent` in `pipeline_e2e.py`):

1. **Sequential, cheap, local** — for every requirement needing
   escalation: resolve `candidate_location` (`rank_evidence`), attempt
   graph-seed resolution against the ONE shared `ProgramGraph` (built
   lazily once), build the full prompt. Stays single-threaded because it
   touches shared mutable state (`pg`) and is fast/local — no benefit to
   parallelizing it.
2. **Concurrent, I/O-bound** — only the actual `run_arm_g_bundle`
   subprocess calls, batched via a `ThreadPoolExecutor(max_workers=N)`.
   Threads (not processes): each call is I/O-bound (subprocess + network
   wait), not CPU-bound. Safe because every investigation already writes
   to its own isolated scratch path keyed by `case_id`
   (`arm_g_codex.run_arm_g_bundle` unconditionally rm-trees/unlinks any
   pre-existing path for that `case_id` — distinct req_ids never
   collide). All bookkeeping (`metrics`, `codex_results`, `new_routed`,
   etc.) happens in the MAIN thread only, as futures resolve via
   `as_completed` — worker threads only call `run_arm_g_bundle` and
   return, they never touch shared state directly.

## Cost-ceiling tradeoff

Enforced once per BATCH (before submitting it), using only cost from
FULLY completed batches — a call's real cost is only known after it
returns. Under concurrency, up to `max_workers - 1` extra investigations
may already be in flight when the ceiling is crossed mid-batch. This is a
wider, but still bounded and explicitly documented, version of the
serial path's own existing limitation (documented in `run_pipeline_e2e`'s
own docstring: "the finest-grained enforcement possible without a live,
separately-polled OpenRouter balance check"). Verified directly:
`test_cost_ceiling_enforced_at_batch_granularity` confirms a 4-item,
batch-size-2, $2/call run against a $3 ceiling lets the first batch ($4)
complete but blocks the second batch entirely.

## Verification

`test_concurrent_escalation.py`, 19 tests, no live Codex calls:
- **Proof of genuine overlap, not just "still works"**:
  `test_investigations_actually_run_concurrently` uses a
  `threading.Barrier(N)` — each mocked call blocks until exactly N calls
  are simultaneously in flight. If the pipeline were still serial, this
  would deadlock (call #1 blocks forever waiting for #2/#3, which never
  start until #1 returns). Completion within the test's timeout IS the
  proof, not a wall-clock speed measurement that could be explained other
  ways.
- Correct per-req_id result attribution under concurrency (no cross-talk
  between simultaneously-resolving futures).
- Every existing routing property re-verified under concurrency:
  deterministic-complete requirements still never invoke the agent,
  agent-required requirements still invoke exactly once, a crashing
  investigation resolves to `INCONCLUSIVE` with a recorded reason instead
  of killing the batch or the run.
- Full existing regression suite (168 tests across 6 `l12_evaluation`
  files + 144 across `rtf/standards/`) re-run and confirmed unchanged —
  the default (`max_concurrent_investigations=1`) path is untouched code,
  not just untested-differently.

## Choosing N for a real run

Not yet empirically tuned against real OpenRouter rate limits for
`openai/gpt-5.1-codex-max` — start conservative (e.g. 5-8) on the next
real run and watch for 429s/throttling in the codex session logs before
increasing. Each concurrent investigation also spawns its own MCP server
subprocess (`graph_mcp_server.py`), so local resource usage (memory, file
descriptors) scales with N too, not just network concurrency.
