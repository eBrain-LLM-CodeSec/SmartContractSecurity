# RTF Agentic Architecture -- redesign record

Per user directive: "revisit the RTF pipeline architecture before running
any further EVMbench audits... the current design is not aligned with the
intended agentic architecture." This document is the required "document
the resulting architecture clearly" deliverable, and the audit trail for
the 6 named defect classes.

## 1. The core architectural rule (as implemented)

```
EthTrust requirement
  -> applicability (run_rtf.py, unchanged -- L1 corpus's own
     conditioned_scope_clause / is_unconditioned_subject)
  -> routing (registry.py, decided AHEAD OF TIME, not per-run):
       DETERMINISTIC_COMPLETE_REQ_IDS (19 requirements)
         -> predicate evidence (or its absence) IS the final verdict.
            No LLM, no Codex, at all. (run_rtf.py)
       AGENT_REQUIRED_REQ_IDS (59 requirements: 38 "trigger-only"
       registered predicates + 21 with no predicate at all)
         -> ALWAYS a direct Codex/agent investigation when applicable
            and evidence-bearing. Bounded L8 is NOT a gate deciding
            whether this happens. (pipeline_e2e.py)
       AGGREGATION_REQ_IDS (3 requirements)
         -> computed post-hoc from every other requirement's own final
            result (pipeline_e2e.compute_aggregation_requirements,
            unchanged by this redesign)
  -> final PASS / FAIL / INCONCLUSIVE / INSUFFICIENT_EVIDENCE /
     NOT_APPLICABLE / UNSUPPORTED_ANALYZER (compute_terminal_status)
```

This replaces the PRIOR design (frozen at commit `0a3ba22`/`b4fdf8a`),
where bounded L8 ran first for every evidence-backed requirement and
Codex was only invoked if L8's own judgment was uncertain
(`escalation.decide_escalation`). That design is confirmed, by direct
forensic evidence (see section 6), to have contributed to a real missed
finding.

## 2. Deterministic-complete vs agent-required: exact classification

**Method** (mechanical, reproducible, not hand-tuned per requirement, not
benchmark-derived -- see `registry.py`'s own extensive inline
justification): derived from each REGISTERED requirement's own Track A
design-record `implementation_status.status` string
(`l5_level_s_strategy/`, `l6_level_m_extraction/`, `l7_level_q_evidence/`,
`l_gp_recommended_practice/`). A status counts as "genuinely complete"
only if it contains NONE of: `PENDING`, `UNRESOLVED`, `BLOCKED`,
`NOT_ATTEMPTED`, `TRIGGER`, `PARTIAL`, `CROSS_CHECK`, `CORRECTED`,
`LOOPHOLE`, `COMPONENT`, `SUB_CLAUSES`, `NOT_IMPLEMENTED` -- every one of
those substrings is that record's OWN acknowledgment of an incomplete or
needs-judgment component (e.g. `TRIGGER_COMPONENT_...SEMANTIC_CONDITION_
PENDING`, `VERSION_COMPONENT_...OVERRIDE_COMPONENT_STILL_BLOCKED`).

This is deliberately conservative in one direction only: it is SAFE to
route a requirement to the agent that a future, more detailed pass could
fully mechanize (e.g. the compiler-bug-pattern checks' override component
is always unresolvable given a FIXED, non-target-varying fact -- a real
future simplification, not implemented here to avoid inventing bespoke
per-requirement decision procedures beyond this pass's scope). It is NOT
safe to do the reverse (silently treating an acknowledged-incomplete
predicate as a complete verdict) -- that direction was never taken.

**DETERMINISTIC_COMPLETE_REQ_IDS (19)**: `req-1-compiler-sol-2021-4`,
`req-1-delegatecall`, `req-1-eip155-chainid`, `req-1-exact-balance-check`,
`req-1-no-ancient-compilers`, `req-1-no-create2`,
`req-1-no-hashing-consecutive-variable-length-args`, `req-1-no-tx.origin`,
`req-1-self-destruct`, `req-1-unicode-bdo`,
`req-2-verify-exact-balance-check`, `req-3-annotate`,
`req-3-consistent-solidity-output`, `req-3-event-on-state-change`,
`req-R-define-license`, `req-R-formal-verification`,
`req-R-fuzzing-in-testing`, `req-R-mutation-testing`,
`req-R-use-latest-compiler`.

**AGENT_REQUIRED_REQ_IDS (59)** = every other registered requirement (38,
mostly compiler-bug-pattern checks and "trigger found, semantic condition
pending" ones -- e.g. `req-1-use-c-e-i`, `req-2-overflow-underflow`,
`req-3-access-control`) + the 21 requirements with no predicate at all
that the prior session's runtime-coverage fix already wired to the
generic evidence collector (`req-3-documented`,
`req-3-implement-as-documented`, etc. -- see
`RTF_MISSING_REQUIREMENTS_GAP_ANALYSIS.md`).

Full per-requirement classification with each one's exact design-record
status string: `registry.py`'s own `DETERMINISTIC_COMPLETE_REQ_IDS`/
`AGENT_REQUIRED_REQ_IDS` definitions (both frozensets, with an assertion
that they exactly partition `REGISTRY.keys()`).

## 3. The agent investigation redesign

### 3.1 Full repository access (`arm_g_codex.run_arm_g_bundle`)

**Before**: `investigation_dir` started with ONLY the entry `.sol` file
copied in. All further code became visible only through the graph MCP
server's `investigate`/`read_source` tools, which resolved real
structural relations from the compiled program graph -- the PROMPT
(`ARM_G_PROMPT_v1.md`) explicitly forbade `grep -R`, `find`, or reading
any file the graph tools hadn't "revealed," even though nothing
technically prevented it (no working sandbox on this kernel -- see
`graph_mcp_server.py`'s docstring). This was a deliberate, disclosed
research design for an EARLIER question ("does graph-mediated navigation
alone suffice"), not the production architecture.

**After**: `run_arm_g_bundle` copies the FULL `repo_root` (minus `.git`)
into `investigation_dir` before the agent ever starts. The agent's shell
already has real `ls`/`find`/`grep`/`cat`/`sed` access to the complete
repository from turn one. Graph-navigation MCP tools remain available as
a supplementary structural-query capability (useful for real
caller/callee/state-read/state-write questions a text search answers
poorly), never the exclusive channel. `ARM_G_PROMPT_v2.md` replaces the
"you do not have unrestricted repository browsing" instruction with an
explicit "use your standard tools freely" one, and explicitly forbids
returning `INSUFFICIENT_EVIDENCE` without a genuine exploration attempt.

A full COPY (not the live `repo_root` itself) is still used, deliberately:
Codex runs with `--dangerously-bypass-approvals-and-sandbox` (the only
mode that works on this kernel) and could technically write/delete within
its own cwd; a disposable copy means an errant write can't corrupt the
actual cloned audit repo other entries/predicates still need to read.

### 3.2 No `candidate_location` precondition

**Before**: `pipeline_e2e.py` called `resolve_seed_node(pg,
candidate_location)` BEFORE invoking Codex at all. If this raised (zero
or ambiguous graph match -- the dominant real-world case for
non-function-shaped locations like "compiler config" or "project
documentation"), escalation was ABANDONED entirely
(`escalation_skip_reasons[req_id] = "graph_resolution_failed: ..."`) and
the requirement fell back to whatever the bounded L8 pass had already
concluded (typically `INSUFFICIENT_EVIDENCE`, since that same
non-function-shaped-location gap is exactly what caused L8-only
resolution in the first place).

**After**: seed resolution is still ATTEMPTED (for a nicer, pre-loaded
`show_candidate()` hint when it works), but a failure is purely
informational (`escalation_skip_reasons[req_id] =
"graph_seed_not_resolved (agent still investigates): ..."`,
`graph_seed_resolved[req_id] = False`) and never blocks the investigation.
`graph_mcp_server.py`'s `_get_seed()`/`show_candidate()` were changed to
degrade gracefully (`NO_CANDIDATE_HINT`, with guidance to explore via
normal file tools) instead of raising/crashing.

### 3.3 Deterministic evidence as hints, not restrictions

The generic `collect_documentary_and_implementation_evidence` predicate
(README/docs/NatSpec/entry-file-source) and every real "trigger-only"
predicate's findings are still collected exactly as before and still
included in the agent's prompt (`build_codex_prompt_inputs`) -- but they
are no longer the ONLY code the agent can see. This directly fixes the
`_MAX_SOURCE_EXCERPT_CHARS=8000` truncation bug found in the prior
session's forensic H-01 investigation: that cap still exists (it bounds
how much of the entry file's source becomes an explicit evidence
BULLET), but it no longer determines what the agent CAN see -- the full,
untruncated file (and every other file in the repository) is directly
readable via the agent's normal shell tools regardless of what the
evidence-collector excerpt included.

## 4. L8's redefined role

### 4.1 What `judge_with_l8.py` did before this redesign

- `judge_once`/`judge_with_second_pass`: a single bounded LLM call (no
  tools, no repository access) given only the requirement's L2 context
  bundle + a rendered evidence-bundle question, returning a
  PASS/FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE decision. The
  second-pass variant re-runs the identical call and downgrades to
  INCONCLUSIVE on disagreement (a real, valuable reproducibility check).
- `judge_run`/`judge_result`: per-requirement orchestration, isolating
  one requirement's judgment-layer failure (`ENVIRONMENT_FAILURE`) from
  every other requirement's, with error text preserved in the raw
  output.

### 4.2 What's now redundant

The core role this whole module played in the PRIOR architecture -- "the
first, cheap opinion that decides whether Codex is worth invoking" -- is
gone. `escalation.decide_escalation` is not called anywhere in
`pipeline_e2e.py`'s live loop. Both remain fully intact, importable, and
tested (`test_judge_with_l8.py` still passes unmodified) -- nothing was
deleted -- but neither participates in the live routing decision anymore.

### 4.3 What's still potentially valuable, and the decision made about it

The user's own instruction: *"If L8 remains useful, redefine it as an
optional verifier/critic or bounded second-pass judgment layer AFTER
agent investigation... Do not remove it blindly."*

**Decision made in this pass: L8 is NOT wired as a post-agent critic in
this implementation.** Reasoning:

- Building a genuine post-agent critic is NEW work, not a redefinition of
  existing code: `judge_with_l8.py` only ever judged from a rendered
  TEXT evidence bundle, never from a full agent transcript + its cited
  sources + its own confidence/reasoning. A real critic would need a new
  prompt, new schema-mapping logic, and its own validation -- a
  meaningfully different scope than "revisit the routing architecture."
- It has a real, non-trivial cost: one additional LLM call after EVERY
  agent investigation (59 requirements x however many are applicable
  per target), roughly doubling the already-large per-audit LLM call
  count this redesign already produces (see section 5's cost
  discussion).
- It is explicitly conditional in the user's own instructions ("if L8
  remains useful"), not mandated.

**What IS preserved and available, should a future pass want it:** the
second-pass agreement-check pattern (`judge_with_second_pass`) is
directly reusable as the SHAPE of a post-agent critic (run an
independent second opinion, downgrade to INCONCLUSIVE on disagreement)
-- it would need a new prompt that takes an agent's cited evidence and
conclusion as input rather than a bare evidence-bundle question. This is
flagged as a concrete, scoped follow-up, not implemented speculatively
here.

## 5. Defect audit (the 6 named classes)

1. **An LLM-required requirement could terminate without an agent
   investigation.** FOUND: `escalation.decide_escalation` gated Codex on
   bounded-L8 uncertainty; a confident (HIGH/MEDIUM) bounded verdict
   never escalated at all, even for AGENT_REQUIRED-shaped requirements.
   FIXED: removed as a gate; every AGENT_REQUIRED_REQ_IDS requirement
   with evidence goes straight to the agent.
2. **Static evidence truncation could hide relevant implementation.**
   FOUND: `_MAX_SOURCE_EXCERPT_CHARS=8000` in
   `collect_documentary_and_implementation_evidence`, confirmed live to
   have hidden H-01's exact vulnerable function on `LiquidRon.sol`
   (function starts at character 12,553). FIXED: full repository access
   (section 3.1) means the excerpt cap no longer bounds what the agent
   can see, only what one evidence bullet quotes verbatim.
3. **Agent invocation depended on a resolvable `candidate_location`.**
   FOUND: `resolve_seed_node` as a blocking precondition, aborting
   escalation on failure. FIXED: section 3.2.
4. **`INSUFFICIENT_EVIDENCE` could become terminal despite unexplored
   evidence.** FOUND: bounded L8 (no tools, no repo access) could return
   `INSUFFICIENT_EVIDENCE` as a FINAL answer for AGENT_REQUIRED-shaped
   requirements whenever it wasn't uncertain enough to trigger escalation
   OR whenever escalation itself failed to reach Codex (defects 1 and 3
   above). FIXED: bounded L8 no longer produces a terminal answer for
   these requirements at all; only the full-access agent does, and
   `ARM_G_PROMPT_v2.md` explicitly forbids returning
   `INSUFFICIENT_EVIDENCE` without a genuine exploration attempt.
5. **Repository/file access was unnecessarily restricted.** FOUND:
   `ARM_G_PROMPT_v1.md`'s explicit prohibition on `grep -R`/`find`/
   reading non-"revealed" files (section 3.1). FIXED: removed.
6. **Deterministic analysis was being used as a substitute for
   reasoning.** FOUND, in the OPPOSITE direction from the literal
   reading: LLM reasoning (bounded L8) was being used as a substitute
   for what several requirements' own design records already show is a
   COMPLETE deterministic answer (e.g. the 19
   `DETERMINISTIC_COMPLETE_REQ_IDS`, previously deferred to L8 anyway
   the instant their predicate found ANY evidence). FIXED: section 1 --
   these now resolve directly from predicate evidence, no LLM call at
   all.

## 6. Why this redesign, not a targeted Liquid-Ron patch

The prior session's forensic root-cause finding for H-01 (0/1 on
`2025-01-liquid-ron`, DetectGrader) was: `req-3-documented`/`req-3-
implement-as-documented`/`req-3-document-system` all executed correctly
on the `LiquidRon.sol` entry and honestly resolved `INSUFFICIENT_EVIDENCE`
-- but the evidence they received was structurally incapable of
containing `totalAssets()` (H-01's exact vulnerable function), because
`_MAX_SOURCE_EXCERPT_CHARS=8000` truncated the 20,462-character file
before reaching it (offset 12,553). Confirmed by grepping every cached
L8 response that run produced for "totalAssets"/"operatorFeeAmount":
zero matches anywhere.

That finding was scoped to ONE evidence collector's ONE constant. This
session's audit found the SAME underlying failure mode (a bounded,
non-exploring judgment layer terminating a requirement that genuinely
needed investigation) was structural, not confined to that one
predicate -- it applied to the bounded-L8-as-gate design for all 59
`AGENT_REQUIRED_REQ_IDS`, not just the 21 that happened to use the new
generic collector. Raising or removing `_MAX_SOURCE_EXCERPT_CHARS` alone
would not have fixed the `candidate_location`-gated escalation abandonment
(defect 3) or the graph-visibility restriction (defect 5), both of which
independently limit what a requirement's investigation can see even when
it DOES reach Codex. Fixing the architecture, not the one constant, is
what this document records.

## 7. Known cost/scope implication (disclosed, not hidden)

Every one of the 59 `AGENT_REQUIRED_REQ_IDS` requirements now becomes an
UNCONDITIONAL agent investigation whenever applicable and evidence-
bearing, rather than a MAYBE-escalation gated on bounded-L8 uncertainty.
The prior architecture's own real-run data (liquid-ron, commit `0a3ba22`)
showed roughly 65-72% requirement applicability per entry and only 31
total escalations across all 6 entries (bounded L8 resolved the rest
confidently on its own). Under this redesign, the same audit would be
expected to produce on the order of 35-45 agent investigations PER ENTRY
(not per audit) -- a large, disclosed increase in both wall-clock time
(each investigation takes minutes, and investigations run sequentially
due to the shared `solc-select` global-state constraint -- see
`HANDOFF_NEXT_SESSION.md` gotcha #3) and real spend. This is the direct,
expected consequence of "do not use bounded L8 as a gate" -- not an
oversight. See the companion validation report for the actual observed
numbers from the fresh, fully-supervised rerun, and for the cost check-in
with the user before that rerun was launched.
