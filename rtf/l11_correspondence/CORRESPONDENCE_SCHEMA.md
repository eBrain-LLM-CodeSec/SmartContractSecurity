# L11 EVMbench Correspondence Layer — schema and freeze tooling

**This file and `freeze.py` are exposure-neutral tooling only.** They
define *how* correspondence judgments are recorded and frozen; they
contain zero actual judgments about which EVMbench findings correspond
to which EthTrust requirements. See `EXPOSURE_DECLARATION.json` for why
those judgments are not populated by this session.

## Record schema (per the plan, verbatim)

```json
{
  "finding_id": "...",
  "req_id": "...",
  "relationship": "DIRECT | PARTIAL | CONTEXTUAL | NONE",
  "justification": "...",
  "supporting_evidence": [],
  "review_status": "...",
  "frozen_at_framework_version": "..."
}
```

- `DIRECT`: the finding clearly demonstrates violation of the requirement.
- `PARTIAL`: the finding covers only part of the requirement.
- `CONTEXTUAL`: relevant but cannot independently establish nonconformance.
- `NONE`: no justified relationship exists.
- Explicitly **many-to-many**: one finding may be `DIRECT` for several
  requirements; one requirement may have several `DIRECT` findings. Report
  per-requirement and per-finding recall views separately.
- Only `DIRECT` mappings feed recall-like metrics; `PARTIAL`/`CONTEXTUAL`
  are reported separately, never folded into the same denominator.

## Process for whoever builds the actual mapping (the separated reviewer)

1. Read `EXPOSURE_DECLARATION.json` first and fill in your own
   `benchmark_exposure` block honestly before starting -- if you also have
   `SUBSTANTIAL` exposure to this corpus, you are not a valid Person B
   either, and this decision escalates further (see that file's
   `consequence` field).
2. Work from the frozen L1 Requirement Corpus
   (`rtf/l1_corpus/requirement_corpus.json`, hash-checked against
   `requirement_corpus.sha256`) and the EVMbench finding writeups
   (`repo/frontier-evals/project/evmbench/audits/*/findings/*.md`)
   independently -- do not read `rtf/track_a/`'s L3-L7 translation records
   before finishing your correspondence judgments, to avoid the reverse
   leakage direction (translation choices shaping which correspondences
   look plausible).
3. Record each judgment using the schema above, run `freeze.py` to
   hash-lock the result with a timestamp, before any evaluation (L12) is
   executed.

## `freeze.py`

Mirrors `rtf/l1_corpus/parse_spec.py`'s freeze pattern: takes a
correspondence-mapping JSON file, validates every record against the
schema (relationship enum, required fields, many-to-many allowed), writes
a `.sha256` freeze hash + timestamp, and refuses to proceed if the input
file doesn't validate. It does not generate or suggest any judgments
itself.
