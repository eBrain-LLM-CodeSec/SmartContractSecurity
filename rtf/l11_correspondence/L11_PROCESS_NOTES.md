# L11 execution notes — a messy process, an honestly-verified result

## What was asked for vs. what happened

The plan (and `EXPOSURE_DECLARATION.json`) required a genuinely independent
reviewer to build the correspondence mapping, since this session has
substantial prior MGPR exposure to this exact corpus. A fresh subagent
(no conversation memory, so no exposure) was spawned with explicit,
written exclusions: no `rtf/track_a/`, no `a4v/mgpr/`/`scripts/mgpr/`/
`data/mgpr/`, no `routing_spec.yaml`, nothing MGPR-named.

**That subagent, on its own initiative, recursively spawned further
sub-forks** to parallelize across audit directories — not something it was
instructed to do. This produced a fragmented, hard-to-track execution:
- An early consolidation attempt wrote 11 records to
  `_own_batch.json` and separately to `correspondence_mapping.json`
  after being told (by the orchestrating session) to stop forking further
  and consolidate what existed.
- A *different* branch of the same fork tree (labeled "batch 5, noya" in
  its own report) was, unknown to the orchestrating session at the time,
  still running a broader sweep across 39 audits, using its own further
  sub-forks. It finished later and **overwrote**
  `correspondence_mapping.json` with 57 records, clobbering the
  11-record file without any coordination between the two branches.
- One of *that* branch's own sub-forks (covering the `2024-04-noya`
  audit) reportedly returned early having processed only 8 of 20
  findings; the branch caught this itself, re-ran the missed work, and
  personally re-checked all skipped findings before merging — a genuine
  self-catch, though it only came to light because the branch's own
  final report disclosed it.

**Lesson, logged rather than glossed over:** letting a subagent choose
its own recursive-forking strategy for a task like this trades a real
efficiency gain (39 audits in parallel) for real coordination risk (races
on a shared output file, no visibility into partial failures until self-
reported). A safer pattern for next time is to either forbid sub-forking
explicitly in the task instructions, or to have each fork write to a
uniquely-named file and require an explicit, single, final merge step
performed by the orchestrating session — not by the subagent itself.

## Why the result was verified before being accepted anyway

Regardless of *how* the mapping was produced, "independent" is not a
synonym for "correct" — the whole point of this framework is not to trust
any single stage's output without checking it. The orchestrating session
independently re-read the actual EVMbench finding files
(`/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench/audits/`)
for a meaningful subset before accepting anything:

- **All 10** `req-2-overflow-underflow` records: full source verification.
  Found **1 genuine misclassification**
  (`2023-07-pooltogether/H-02` — a narrowing type-cast truncation
  mislabeled as an arithmetic overflow; the real fix was "Added SafeCast",
  not overflow protection). The other 9 were confirmed well-grounded,
  including one (`2024-03-gitcoin/H-01`) the orchestrating session
  initially suspected was also a stretch, then confirmed as legitimate
  after reading the full justification (it cites a genuine
  `ARITHMETIC_UNDER_OR_OVERFLOW` runtime panic, not just colloquial
  language). See `rtf/l9_assumptions_register/REGISTER.jsonl` AR-003.
- **All 4** `req-2-verify-exact-balance-check` and **all 3**
  `req-1-eip155-chainid` records: reviewed, one spot-checked against the
  actual finding text (`2024-08-phi/H-01`) and confirmed accurate. All 7
  were appropriately hedged (PARTIAL where the match wasn't a literal
  `==` check) rather than overclaimed.
- **The 40** `req-3-implement-as-documented` records: reviewed at the
  justification-pattern level (not full source verification on all 40,
  given time) — consistently followed the intended methodology (quote a
  specific documented claim, show a concrete code-level contradiction),
  with appropriate `CONTEXTUAL` downgrades where the documentation itself
  was disputed (`2024-07-traitforge/H-02`). One scope question was
  surfaced and logged as open, not resolved: several records cite
  *third-party* protocol documentation (Balancer, Synthetix, Pendle) the
  audited code integrates with, rather than the audited project's own
  documentation — a defensible but unsettled reading of the requirement's
  scope (AR-004).

## Final state

`correspondence_mapping.json`: 57 records (33 DIRECT, 19 PARTIAL, 5
CONTEXTUAL, 0 NONE-by-design), frozen with a hash
(`correspondence_mapping.json.sha256`) after the one correction above.
Coverage: 24 of the corpus's real 39 audit directories (not 27 — see
below) produced at least one match against these six requirements; zero
matches for `req-1-compiler-060` and `req-1-compiler-sol-2021-4` across
the entire reviewed corpus, an expected and legitimate negative result
(every observed audit targets Solidity ≥0.8.x, and none combine
user-defined value types with solc 0.8.8 exactly).

**Another stale-number correction, consistent with this project's pattern
this session** (EthTrust's real requirement count, its real version):
the plan's original "27-audit corpus" figure is itself outdated — the
actual corpus at `/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench/audits/`
currently has **46** audit directories (the independent reviewer's own
count of "39" reviewable ones excludes some without a usable `findings/`
structure — not independently re-verified here, logged as a further open
detail for Track B).

## Extension: 2023-07-pooltogether re-screened against the full 81-requirement corpus (2026-08-06)

The original pass above checked findings against only Track A's original
6 selected requirements. This extension re-checked pooltogether's SAME 2
real, graded findings (H-02, H-04) against the FULL 81-requirement
corpus, using the identical mitigation pattern as the original pass: a
fresh, non-forked subagent with no memory of this conversation (hence no
exposure to this session's prior MGPR work OR to this session's own RTF
translation choices in `rtf/track_a/`), instructed to read the finding
writeups and all 81 requirements' `normative_text` in full before
producing any judgment, and to only read `rtf/track_a/` afterward (for
req_id spelling verification only).

**Result: 2 new DIRECT records**, both manually spot-verified by this
orchestrating session against the real finding files
(`findings/H-02.md`, `findings/H-04.md`) before merging — every quoted
excerpt in both new records was confirmed to appear verbatim in the real
finding text:
- `2023-07-pooltogether/H-02` → `req-3-all-valid-inputs` (DIRECT) —
  flagged by the reviewer itself as the more borderline of the two calls
  (a reasonable reviewer could argue PARTIAL instead, since "process all
  inputs" is broad and the finding demonstrates one specific boundary
  case rather than exhaustive input-validation failure); accepted as
  DIRECT per the reviewer's own reasoning (a single clear counterexample
  is sufficient to establish nonconformance with a MUST-level
  requirement) but logged here as a genuine, not fully resolved judgment
  call, not a clean-cut case.
- `2023-07-pooltogether/H-04` → `req-3-access-control` (DIRECT) — a
  clean match; the finding states outright that the vulnerable function
  "can be called by anyone since there is no access control."

The reviewer also explicitly considered and rejected several
superficially-plausible matches (`req-2-overflow-underflow` and the
overflow/underflow clause of `req-2-documented` for H-02 — correctly
distinguishing a truncating-downcast bug from an arithmetic overflow/
underflow bug, per this project's own AR-003 gotcha; `req-2-check-
rounding` for H-02; `req-3-revocable-permisions`/`req-3-no-single-admin-
eoa` as CONTEXTUAL for H-04, both explicitly conditioned on access
control existing, which is precisely what's absent here) — a positive
signal about review discipline, not just a summary of what it did match.

**`correspondence_mapping.json` re-frozen**: now 59 records (35 DIRECT,
19 PARTIAL, 5 CONTEXTUAL, 0 NONE-by-design), new hash in
`correspondence_mapping.json.sha256`.

**Confidence-downgrade caveat, per the plan's own mandate for
`SUBSTANTIAL` exposure** (`EXPOSURE_DECLARATION.json`): a fresh,
non-forked subagent is a real, meaningful mitigation against the
specific cognitive-leakage risk this layer is designed to guard against
(a translator's own prior exposure shaping which correspondences look
plausible) — but it is **not** the plan's own stated standard of "true
personnel separation" (a genuinely different human reviewer, in a
different organizational role, with no shared instance/session lineage
with the translator). Both this extension and the original 6-requirement
pass rely on the SAME mitigation, at the SAME (weaker-than-ideal)
strength. Per the plan's explicit fallback rule: **any recall-like
metric computed from this mapping's `DIRECT` records should be reported
with an explicit confidence downgrade**, not presented at face value
alongside a metric that carries no such risk. This downgrade applies to
all 35 DIRECT records currently in `correspondence_mapping.json`, not
just the 2 added in this extension.

**Scope, stated plainly**: this extension covers exactly ONE audit
(2023-07-pooltogether) re-screened against the full corpus — it is NOT a
full 81-requirement × full-EVMbench-corpus correspondence pass. The
EVMbench corpus has 46 audit directories; extending this same treatment
to the rest remains a real, separate, larger undertaking, tracked
honestly as future work rather than implied complete by this extension.
