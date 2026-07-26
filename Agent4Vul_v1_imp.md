# Agent4Vul v1 — Session Handoff / Continuation Prompt

Paste this whole file as the opening prompt for the next session. It's written
to be self-contained for a fresh Claude Code session with zero prior context.

---

## What this project is

`/scratch/md5344/evmbench/agent4vul/` is an Agent4Vul-inspired vulnerability
detection pipeline, adapted for EVMbench's `detect` split (real historical,
professionally-audited smart contract codebases), NOT a reproduction of the
original paper's trained GAT + LightGBM classifier — EVMbench lacks aligned
per-vuln-type labels at the scale a trained classifier needs (~40 audits,
≤120 total positive findings).

**Full original design plan** (phased, very detailed):
`/scratch/md5344/.claude/plans/adaptive-wobbling-marble.md` — read this first
for the complete architecture rationale (why no trained GAT/classifier, the
multimodal fusion design, budget/leakage/repair requirements, all phase
pass/fail criteria).

**Project memory** (auto-loaded context from past sessions):
`/scratch/md5344/.claude/projects/-scratch-md5344/memory/project_agent4vul_pipeline.md`

---

## What has been built and validated (Phases 0–3, all done)

Self-contained `uv` project at `agent4vul/`. Module layout under `a4v/`:
`graph.py` (Slither-based typed program graph: calls/inheritance/modifiers/
state r-w/external-calls/write-after-external-call), `features.py`, `repair.py`
(bounded env-repair, no degraded fallback), `slice.py` (context bundles),
`llm.py` (OpenRouter client, caching, last-fence JSON extraction), `fpsl.py`
(the paper's actual 5 prompt strategies — verified against the PDF),
`commentator.py`, `embed.py` (see SecureBERT note below), `corpus.py`
(leakage-guarded external/EVMbench corpus loader — **not yet populated**),
`seeds.py`, `score.py` (untrained dynamic-threshold ranker + strong-signal
keep-list — see note below on what "untrained" means), `scope.py` (README
scope-table parsing — critical cost control), `tools.py` (sandboxed,
cached investigation tools), `codex_runtime.py` (direct `singularity exec`
invocation of the real worker container's `codex` CLI), `auditor.py` (the
Agentic Auditor), `consolidate.py`, `report.py`. Plus `scripts/grade.py`,
`scripts/run_one.py`, `bin/forge` (a shim, see below), full `tests/unit/` +
`tests/integration/` suites (63+ tests passing).

### Real, end-to-end validated result

Ran the **complete real pipeline** against the real historical audit
`2023-07-pooltogether` (not a toy fixture) and graded it with EVMbench's
actual upstream `DetectGrader`:

- **Score: 2/2** (both H-02 the uint96 downcast, and H-04 the missing
  access-control on `mintYieldFee`, detected) — beats both existing
  baselines in this repo (`pipeline_lite`: 1/2, SmartAuditFlow: 1/2).
- Full report at `agent4vul/out/2023-07-pooltogether/audit.md`, grade at
  `.../grade.json`, session trace at `.../investigations/session.jsonl`,
  Commentator output at `.../commentary/comments.json`.
- Real cost for that whole run (Commentator over 68 in-scope functions +
  Auditor investigating 22 ranked candidates, 16 actually investigated
  before the token ceiling stopped it cleanly): **~$1.93** total (verified
  via the OpenRouter account's own `usage_daily` delta, NOT naive
  prompt-token × price math — that overestimates ~2.5x because this
  model's prompt caching discount isn't accounted for in a naive calc).
- 833 compiled functions in the full Vault Foundry project were cut down to
  68 actually-in-scope ones via `scope.py`'s README-table parsing BEFORE any
  LLM spend — this cost control matters a lot at real-audit scale.

### Infrastructure gotchas learned the hard way (do not rediscover these)

All confirmed live on this specific Jubail HPC / Singularity 3.6.4 setup:

1. **`SINGULARITYENV_HOME` is rejected outright** by this Singularity build
   ("Overriding HOME ... is not permitted"). `--no-home` does NOT reset
   `$HOME` to the image's baked-in default either — it resolves to the
   *host* user's real home dir, which doesn't exist inside the container.
2. Fix: use `-H src:dest` (a real singularity flag, not an env var) — but
   **the dest must NOT be `/home/agent`**, because that's exactly where the
   image bakes its own `forge`/`foundry` binaries (`-H` shadows it).
3. **`singularity exec` does not default the container's cwd to the bind
   path** — you MUST pass `--pwd <path>` explicitly or the invoked binary
   runs from `/` and silently does nothing (this caused a `forge build`
   "Nothing to compile" false negative that took real debugging to catch).
4. Codex's proxy provider config (pointing it at OpenRouter instead of
   `api.openai.com`) must be injected via `codex exec -c key=value` CLI
   overrides, **not** a `~/.codex/config.toml` file — since `$HOME`
   resolution is broken per (1)/(2), a config file approach silently never
   gets read (confirmed: codex fell back to hitting `api.openai.com`
   directly with a 401 before this was fixed).
5. **`--ephemeral`** is required on `codex exec` — without it, codex tries
   to persist skills/session state to a read-only path outside the bind
   mount and exits nonzero even though the actual turn completed
   successfully and the `-o` output file was written correctly. Because of
   this, **check success via the output file's existence/non-emptiness**,
   not the exit code (same pattern `run_codex_detect.sh` already used).
6. `forge`'s own solc-version-manager (svm) has the same home-directory
   resolution problem at a lower level (bypasses `$HOME` via an OS-level
   lookup) — sidestepped entirely by pointing `forge --use <path>` at an
   already-downloaded `solc-select` binary instead of letting svm manage it.
7. `graph.py`'s `_compile()` must NOT force the `solc` framework for
   directory targets — real Foundry projects need crytic-compile's
   auto-detection so it shells out to `forge` correctly; only single-file
   fixtures should force plain `solc`.
8. `FunctionTopLevel` (Solidity file-level free functions) has no
   `.contract` attribute — `graph.py`'s internal-call edge builder must
   guard this with `getattr(..., "contract", None)`.
9. `codex exec` has **no session-resume mechanism** (confirmed via
   `backend/worker_runner/common.py`'s own comment: "a retry launches a
   BRAND-NEW codex session from scratch"). So `auditor.py`'s "one shared
   session per audit" is implemented as one fresh `codex exec` process per
   candidate, with "shared memory" carried via an in-process/on-disk working
   memory object fed into each new prompt — not a literal persistent process.
10. Last-fence JSON extraction (`llm.py`) must use **first-fence-open,
    last-fence-close** — a naive "nearest previous fence" search breaks when
    a model's own rationale text embeds a nested fenced code example.

Cost-gated tests: `RUN_LLM_TESTS=1` gates tests that spend real OpenRouter
money; `RUN_MODEL_DOWNLOAD_TESTS=1` gates tests that download real model
weights. Both default to skipped so plain `pytest` stays free and offline.

### SecureBERT 2.0 swap (done, verified)

`a4v/embed.py`'s local embedding fallback (used when no Voyage API key is
present, which is the case on this host) now uses Cisco's
`cisco-ai/SecureBERT2.0-biencoder` (confirmed real on HF: Apache-2.0,
natively `sentence-transformers`-compatible, ModernBERT architecture,
768-dim, cybersecurity-domain-tuned) instead of generic
`all-MiniLM-L6-v2`. Verified: real download (~572MB), real embeddings
produced, non-degenerate cosine similarity, full test suite green.
`pyproject.toml` has an explicit `transformers>=4.48.0` floor (needed for
ModernBERT support). Note: this HPC login node needs
`OPENBLAS_NUM_THREADS`/`OMP_NUM_THREADS` capped (e.g. `=4`) or bare
sentence-transformers/sklearn imports crash on thread creation — pre-existing
host constraint, unrelated to the model choice.

---

## Open items — what to do next

### 1. Memorization / contamination check (raised by the user, unresolved)

`2023-07-pooltogether` is a real, publicly-documented Code4rena-style
contest. Its two vulnerabilities (H-02 uint96 downcast, H-04 missing
access control on `mintYieldFee`) are searchable public knowledge — a 2/2
score is real, but weaker evidence of genuine code analysis than a score on
a private/novel codebase would be, because the model may have memorized
this specific famous contest's write-ups during training.

**The test that settles it, not yet run:** locally patch both
vulnerabilities in the checkout (the same fixes PoolTogether actually
shipped — a `SafeCast`/bounds-check on the `uint96` downcast, and an
owner-check on `mintYieldFee`), then re-run just those two candidate
investigations through the real `AgenticAuditor`. If it still confirms
vulnerabilities that no longer exist in the patched code, that's evidence of
memorization/recitation rather than genuine grounding. If it correctly
reports the patched code as safe, that's evidence of real reasoning.
Estimated cost: ~$0.20–0.40 (2 targeted investigations at observed
per-candidate rates).

**Important limitation to fix first:** the current `auditor.py` +
`codex_runtime.py` uses `--ephemeral`, which discards codex's full
tool-call/reasoning trace — only my own coarse `investigate_start`/
`investigate_done` markers get saved, not what files the model actually
read. Before or alongside running the ablation, consider also capturing
the raw `stdout` JSONL event stream to disk per candidate (it streams
tool-call/exec events regardless of `--ephemeral` — that flag only affects
session *persistence*, not the live event stream) so future runs are
actually auditable for grounding, not just their final verdict.

### 2. GAT / graph transfer-learning (the user's specific ask — do this)

Confirmed: the paper's GAT training hyperparameters are **not disclosed
anywhere** (no learning rate, epoch count, or optimizer for the GAT
specifically — only LightGBM's hyperparameters are given in the paper's
Table 1). The only public code reproduction (`github.com/ashwanikumar9/
Agent4Vul`) has a GAT config that is that repo author's own invented
defaults, not sourced from the paper — do not treat it as authoritative.

**Where to get real training data** (traced this session): the paper's
actual dataset is reference [21] — Qian, Liu, Yin, He, "Cross-Modality
Mutual Learning for Enhancing Smart Contract Vulnerability Detection on
Bytecode," ACM Web Conference (WWW) 2023, pp. 2220–2229. Publicly released
by the same author (Peng Qian, GitHub handle `Messi-Q`) at:

**`https://github.com/Messi-Q/Smart-Contract-Dataset`** — use "Resource 2"
specifically (matches the paper exactly: 4 vuln types — reentrancy,
timestamp dependency, integer overflow, dangerous delegatecall — with
labeling instructions in the repo's `instructions/` dir). Download link is
a Google Drive share (`https://drive.google.com/file/d/
1UhHHevE9iDmvSB_k_lhyI58KAj7hnB1o/view`) — not git-clonable, needs manual
download or a `gdown`-style fetch. **No license file on that repo** —
check citation/reuse terms before committing to using it for anything
beyond research.

**Recommended approach, in order of cost/value:**
1. **Cheapest, do this first if short on time**: add classic graph
   centrality features (PageRank on the call graph, betweenness on state
   variables, k-core decomposition) to `a4v/features.py`'s existing
   untrained feature set. No training, no external data, immediate value.
2. **Best real option — transfer learning**: train a real GAT (or simpler
   GNN — GCN/GraphSAGE would be a reasonable, cheaper starting point) on
   the Messi-Q dataset above as a genuinely supervised structural encoder,
   using **our own source-level Slither graph representation**
   (`a4v/graph.py`) rather than the paper's bytecode-CFG approach (more
   consistent with what's already built, likely more informative since it
   preserves contract/inheritance/modifier structure). Then **freeze it**
   and apply it to EVMbench candidates purely as a feature extractor — its
   output embedding becomes one more input to `a4v/score.py`'s
   `SuspicionRanker`, same role embeddings already play, just backed by a
   real learned structural signal instead of hand-picked counts. This
   sidesteps EVMbench's label scarcity entirely (training data isn't
   EVMbench, so no leakage risk) and keeps the architecture intact — the
   Agentic Auditor stays the final decision-maker.
   - Real caveats: only covers 4 vuln classes (misses `access_control` —
     which is exactly where H-04 lived in our one real result —
     `oracle_price`, and `accounting`); needs GPU training (Jubail has an
     `nvidia` partition, see the `hpc-jubail` skill); will hit real
     compile-failure rates building 40K graphs (expect to need `repair.py`-
     style handling, possibly at lower rigor than the per-audit repair
     budget used for real EVMbench audits); several-GB dataset download.
3. **Self-supervised fallback** if the labeled-transfer route stalls:
   node2vec/graph2vec embeddings trained directly on each audit's own
   graph, no external data needed, but weaker signal since it's not
   anchored to known-vulnerable patterns.

Whichever is chosen, wire the result into `SuspicionRanker` as an
additional weighted term (mirroring how `embedding_similarity` is already
plumbed in, just currently unused — see item 3) — never as a replacement
for the Agentic Auditor's final call.

### 3. Populate the external embedding corpus (currently a no-op)

`a4v/corpus.py`'s `ExternalCorpus`/`EVMbenchCorpus` (with leakage guards:
leave-one-audit-out + fork-family exclusion) are built and tested, but
`scripts/build_corpus.py` (mentioned in the original plan's module layout)
was never built, so `embedding_similarity` was `None` for every candidate in
the one real run so far — it contributed nothing to ranking. Populate this
from the SWC Registry (permissively licensed, matches the vuln taxonomy
better than a toy demo set) and/or the Messi-Q dataset above.

### 4. Not started at all

- Phase 3a: diverse dev-set validation across 5–8 audits (reentrancy,
  arithmetic/downcasting, access control, accounting, oracle/price,
  cross-contract) before freezing config, per the original plan.
- Phase 4: full 40-audit sweep with frozen config, SLURM-batched.
- Phase 5 (optional): dev-set LOAO re-ranker, or the GAT work above.

### Known adjacent context, not ours to touch

A separate, more mature agentic system called "SmartAuditFlow" already
exists in this same repo (`backend/worker_runner/agentic/
orchestrate_audit.py`, plan doc `evmbench/SmartAuditFlow_Adaptation_Plan.md`),
with its own real graded runs (1/2 on the same audit). User's explicit
decision: keep `agent4vul` fully independent — do not import or reuse its
code, even though `auditor.py`'s `codex exec` invocation pattern deliberately
mirrors its proven approach (no session resume; shared memory via on-disk
state fed into fresh per-candidate calls).

---

## Quick-reference paths

- Project root: `/scratch/md5344/evmbench/agent4vul/`
- Original plan: `/scratch/md5344/.claude/plans/adaptive-wobbling-marble.md`
- Real audit output: `agent4vul/out/2023-07-pooltogether/` (`audit.md`,
  `grade.json`, `commentary/comments.json`, `investigations/session.jsonl`,
  `tokens.json`)
- OpenRouter key: `/scratch/md5344/evmbench/run/task5_secrets/openrouter.key`
  (check account balance/usage via `GET https://openrouter.ai/api/v1/auth/key`
  before any real run — use its `usage_daily` delta as ground truth for cost,
  not naive token math)
- Worker container (has `codex` + `forge` baked in):
  `/scratch/md5344/evmbench/containers/evmbench-worker.sif`
- `forge` shim (routes compilation through the container):
  `agent4vul/bin/forge`
- Prebuilt, already-fixed pooltogether checkout (submodules initialized):
  `/scratch/md5344/evmbench/run/pipeline_validation/fixed_pooltogether_entry/upload.zip`
- GAT training dataset (not yet downloaded): `https://github.com/Messi-Q/
  Smart-Contract-Dataset` (Resource 2)

## Suggested opening move for the next session

Ask the user which of the open items to prioritize (memorization check vs.
GAT transfer-learning vs. corpus population vs. Phase 3a/4) rather than
assuming — they're independent workstreams with very different cost/time
profiles, and this project's owner has consistently wanted to be consulted
before any step that spends real money or takes on a new multi-hour
engineering scope.
