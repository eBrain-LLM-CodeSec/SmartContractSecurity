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
