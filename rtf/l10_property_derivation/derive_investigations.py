"""L10: Property/invariant derivation and investigation-instance expansion.

Built in response to the RTF-vs-EthTrust translation-fidelity re-audit
(`rtf/l12_evaluation/RTF_ETHTRUST_TRANSLATION_AUDIT.md`), which found two
distinct, generic architectural gaps -- not requirement-specific ones --
in how a requirement becomes an investigation:

1. A multi-clause normative requirement (multiple MUST/MUST NOT sentences
   in one `normative_text`, e.g. req-2-check-rounding's three obligations)
   was forwarded to the investigating agent as one flat, undifferentiated
   block of text, competing for attention rather than being investigated
   as the several distinct properties the requirement's own sentence
   structure names.
2. `pipeline_e2e.py`'s escalation loop collapsed every AGENT_REQUIRED
   requirement's ranked evidence down to exactly ONE top-ranked location
   (`candidate_location = ranked[0].item.location`), even when the
   predicate found many distinct violation sites -- so a requirement
   whose own scope is "every function" or "every block-data read" in
   practice only ever got one function/site actually investigated.

Both derivations below are PURELY STRUCTURAL: driven by (a) sentence
boundaries already present in a requirement's own `normative_text`
(itself EthTrust spec text, verbatim) and (b) the SHAPE of a
requirement's own predicate-produced evidence (how many distinct
locations it found), never by req_id, never by anything EVMbench-derived.
A requirement with one clause and one evidence location behaves exactly
as the pre-existing single-instance pipeline; the expansion only ever
activates for requirements whose OWN text or OWN evidence actually has
more than one thing to say.

This module is additive and NOT wired into the default pipeline path --
`pipeline_e2e.run_pipeline_e2e` still uses its original single-instance
behavior unless a caller explicitly opts in (see that module's
`instance_expansion` parameter), so no existing run's cost/behavior
changes unless deliberately requested. This mirrors how
`max_concurrent_investigations` was introduced as an opt-in parameter
rather than changed pipeline-wide.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from rtf.l12_evaluation.metrics import ConformanceState

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def derive_clauses(normative_text: str) -> list[str]:
    """Splits a requirement's normative_text into its constituent
    sentences -- each MUST/MUST NOT/SHOULD sentence in the spec's own
    prose becomes one derived clause/property. Purely mechanical (regex
    sentence-boundary split on real terminal punctuation, the same
    '.', '!', '?' set `rtf/l1_corpus/parse_spec.py`'s own completeness
    check now requires -- see AR-027), not NLP, not requirement-specific.

    A single-sentence requirement (the common case) returns a
    single-element list containing the whole text unchanged -- callers
    should treat `len(derive_clauses(text)) <= 1` as "this requirement is
    not multi-clause," not as an error or a degenerate case.

    Deliberately does NOT try to strip the leading title text some
    corpus records glue onto their first sentence (e.g. "Ensure Proper
    Rounding of Computations Affecting Value Tested code MUST
    identify...") -- that's exactly the text every existing single-clause
    prompt already receives unmodified, so leaving it in the first clause
    keeps this a strict refinement, not a change to what single-clause
    requirements see.
    """
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(normative_text.strip()) if s.strip()]
    return sentences or [normative_text.strip()]


@dataclass(frozen=True)
class InvestigationInstance:
    """One scoped (requirement-derived-property, candidate-location) pair
    to actually send to the investigating agent. `focused_clause` is
    `None` for a single-clause requirement (the agent sees the full
    normative text as before); otherwise it names the specific derived
    sentence this instance should focus on, in addition to (not instead
    of) the full requirement text and context bundle -- the agent should
    always still see the whole requirement for context, just told which
    part this particular instance is scoped to.
    """
    req_id: str
    instance_id: str
    candidate_location: str
    focused_clause: str | None
    clause_index: int
    location_index: int


def distinct_locations(locations_in_rank_order: list[str], max_locations: int) -> list[str]:
    """Dedupes a rank-ordered location list, preserving rank order (the
    first occurrence of a repeated location wins, matching the existing
    evidence-ranking output's own ordering guarantee), capped at
    `max_locations`. Empty/falsy locations are dropped (an evidence item
    the ranker couldn't place in the tree contributes nothing here).
    """
    seen: list[str] = []
    for loc in locations_in_rank_order:
        if not loc or loc in seen:
            continue
        seen.append(loc)
        if len(seen) >= max_locations:
            break
    return seen


def expand_investigation_instances(
    req_id: str,
    normative_text: str,
    locations_in_rank_order: list[str],
    max_locations: int = 5,
    max_total_instances: int = 6,
) -> list[InvestigationInstance]:
    """The combined derivation: how many scoped investigations should
    this one requirement actually produce, for this one repository.

    Combinatorial-explosion control (deliberately simple and
    deterministic, not a search/optimization problem): total instances
    are hard-capped at `max_total_instances` regardless of how many
    clauses or locations exist.

    - Single-clause requirement: one instance per distinct location, up
      to the cap -- directly fixes gap (2) above (every distinct
      violation site the predicate found gets its own investigation,
      not just the top-ranked one).
    - Multi-clause requirement: one instance per derived clause at the
      TOP-ranked location first (every distinct property the
      requirement's own text names is guaranteed at least one
      investigation) -- directly fixes gap (1). Any remaining budget
      (`max_total_instances - len(clauses)`) is then spent giving the
      FIRST (highest-priority) clause additional locations, rather than
      trying to cross every clause against every location (which would
      make the cap trivially binding for any requirement with >2 clauses
      and >2 locations, defeating the point of guaranteeing every clause
      at least one investigation).

    No location at all (`locations_in_rank_order` empty, e.g. a
    documentary-evidence-only requirement with nothing localizable):
    produces one instance per clause with `candidate_location=""`,
    exactly matching the pre-existing single-instance behavior's own
    `candidate_location = ranked[0].item.location if ranked else ""`
    fallback.
    """
    locations = distinct_locations(locations_in_rank_order, max_locations)
    clauses = derive_clauses(normative_text)
    instances: list[InvestigationInstance] = []

    if len(clauses) <= 1:
        clause_text = None
        effective_locations = locations or [""]
        for li, loc in enumerate(effective_locations):
            if len(instances) >= max_total_instances:
                break
            instances.append(InvestigationInstance(
                req_id=req_id, instance_id=f"{req_id}::loc{li}",
                candidate_location=loc, focused_clause=clause_text,
                clause_index=0, location_index=li,
            ))
        return instances

    top_location = locations[0] if locations else ""
    for ci, clause in enumerate(clauses):
        if len(instances) >= max_total_instances:
            return instances
        instances.append(InvestigationInstance(
            req_id=req_id, instance_id=f"{req_id}::clause{ci}",
            candidate_location=top_location, focused_clause=clause,
            clause_index=ci, location_index=0,
        ))

    remaining_budget = max_total_instances - len(instances)
    for li, loc in enumerate(locations[1:1 + remaining_budget], start=1):
        instances.append(InvestigationInstance(
            req_id=req_id, instance_id=f"{req_id}::clause0::loc{li}",
            candidate_location=loc, focused_clause=clauses[0],
            clause_index=0, location_index=li,
        ))
    return instances


def aggregate_instance_verdicts(states: list[ConformanceState]) -> ConformanceState:
    """Combines several instances' conformance verdicts (one per
    (clause, location) pair investigated for the SAME requirement) into
    the one final verdict that requirement gets. Reuses, verbatim, the
    exact same FAIL-wins / else-unresolved-wins / else-PASS precedence
    `pipeline_e2e.compute_aggregation_requirements`'s own `_aggregate`
    helper already uses for the DIFFERENT, pre-existing kind of
    aggregation (combining verdicts across MULTIPLE DISTINCT requirements
    for req-2-pass-l1/req-3-pass-l2) -- not a new, invented precedence:
    a requirement that instructs "process ALL inputs" or "document EVERY
    instance of X" is, by its own text, violated if ANY instance is
    violated, exactly the same semantics as an AND-aggregated corpus-level
    requirement.

    Raises ValueError on an empty list -- there is always at least one
    instance for any requirement that reached investigation
    (`expand_investigation_instances` never returns an empty list for a
    non-empty clause list), so an empty input here indicates a caller
    bug, not a legitimate "no evidence" case (that's
    `ConformanceState.INSUFFICIENT_EVIDENCE`, a real value in the list,
    not an empty list).
    """
    if not states:
        raise ValueError("aggregate_instance_verdicts requires at least one state")
    if any(s == ConformanceState.FAIL for s in states):
        return ConformanceState.FAIL
    if all(s == ConformanceState.PASS for s in states):
        return ConformanceState.PASS
    return ConformanceState.INCONCLUSIVE
