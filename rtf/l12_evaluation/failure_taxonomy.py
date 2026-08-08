"""Operational failure taxonomy (L12).

Purpose: distinguish failures in TOOLING/INFRASTRUCTURE from genuine RTF
ROUTING/JUDGMENT failures, so `metrics.py` never silently blames a
routing miss on what was actually a compile crash, a Slither timeout, or
a known parser limitation. Every `RoutedRequirementResult` (see
`metrics.py`) carries an `operational_status` field populated from one of
the codes below; only `OK` results are eligible to count toward
routing/precision/recall metrics. Every non-`OK` code is tallied
separately by `failure_attribution.py` after a run, never folded into a
"the framework got this wrong" statistic.

Ten codes total (nine failure categories the plan's step 4 names, split
where a category names two distinct things -- e.g. "compilation/
environment failure" becomes two codes -- plus `OK`).
"""
from __future__ import annotations

from enum import Enum


class OperationalStatus(str, Enum):
    OK = "OK"
    """No operational failure. Eligible for routing/precision/recall metrics."""

    COMPILATION_FAILURE = "COMPILATION_FAILURE"
    """The target's Solidity source failed to compile (missing deps,
    wrong solc version pinned, malformed source) -- RTF's own logic never
    ran at all for this target."""

    ENVIRONMENT_FAILURE = "ENVIRONMENT_FAILURE"
    """An infrastructure issue unrelated to the target's own code (disk
    space, PATH misconfiguration, a missing tool binary, network failure
    reaching an LLM API) prevented execution."""

    ANALYZER_TIMEOUT = "ANALYZER_TIMEOUT"
    """Slither (or another analyzer component) exceeded its time budget
    before completing analysis of this target."""

    ANALYZER_CRASH = "ANALYZER_CRASH"
    """Slither itself raised an unhandled exception on a target that DID
    compile -- a genuine, unexpected tool crash, not a known limitation
    (see PARSER_LIMITATION for the known-limitation case)."""

    PARSER_LIMITATION = "PARSER_LIMITATION"
    """A KNOWN, already-documented Slither/tool limitation prevented
    analysis of a specific construct -- e.g. AR-008's confirmed Yul-parser
    crash on `.selector`/`.address` assignment to a local external
    function-pointer variable in assembly. Distinct from ANALYZER_CRASH:
    this is an expected, logged gap, not a surprise discovered during the
    run."""

    ROUTING_FAILURE = "ROUTING_FAILURE"
    """RTF's own L3 applicability logic ran to completion successfully,
    but reached the wrong applicability decision (fired when it
    shouldn't have, or didn't fire when it should have) for this
    requirement/target pair."""

    EVIDENCE_COLLECTION_FAILURE = "EVIDENCE_COLLECTION_FAILURE"
    """Applicability was correct and the requirement's trigger fired, but
    the predicate itself failed to produce usable evidence (crashed
    mid-collection on this specific input, or has a real bug on this
    input shape) -- distinct from ROUTING_FAILURE: routing got the
    ballpark right, the evidence stage is what broke."""

    SEMANTIC_JUDGMENT_FAILURE = "SEMANTIC_JUDGMENT_FAILURE"
    """Evidence was collected correctly and handed to L8, but L8's
    judgment reached the wrong conformance verdict given that evidence."""

    MISSING_EXTERNAL_EVIDENCE = "MISSING_EXTERNAL_EVIDENCE"
    """The requirement structurally needs evidence outside repository
    scope (deployment state, team process, off-chain services) -- not a
    defect. The correct, expected outcome here is
    `ConformanceState.INSUFFICIENT_EVIDENCE`, not a failure to fix."""

    NO_JUSTIFIED_CORRESPONDENCE = "NO_JUSTIFIED_CORRESPONDENCE"
    """RTF resolved a requirement to FAIL for this target, but no L11
    correspondence record (DIRECT, PARTIAL, or CONTEXTUAL) links any real
    EVMbench finding in this audit to this requirement -- reported
    explicitly as unjustified, not silently dropped from the report."""

    SUCCESSFUL_EXECUTION_WRONG_RESULT = "SUCCESSFUL_EXECUTION_WRONG_RESULT"
    """Nothing crashed, routing was correct, evidence collection
    succeeded, judgment ran to completion -- but the FINAL verdict was
    simply incorrect against ground truth. The ONLY category in this
    taxonomy that reflects a genuine framework-quality gap rather than an
    infrastructure/tooling/scope gap; every other non-OK code must be
    ruled out before a result is attributed here."""

    UNSUPPORTED_ANALYZER = "UNSUPPORTED_ANALYZER"
    """The requirement is APPLICABLE, but no deterministic predicate,
    documentary-evidence collector, aggregation rule, or any other
    executable mechanism is currently registered for it AT ALL -- a
    framework-COMPLETENESS gap (something was never built), distinct from
    every other code here, all of which describe something going wrong
    with a mechanism that DOES exist. Added specifically so an applicable
    requirement can never silently vanish from a run's output the way
    25 of 81 requirements (including req-3-documented/req-3-implement-
    as-documented) previously did -- see
    RTF_RUNTIME_COVERAGE_AUDIT.md/RTF_MISSING_REQUIREMENTS_GAP_ANALYSIS.md.
    `run_rtf.py`'s main loop now iterates the FULL requirement corpus, not
    just `registry.REGISTRY`'s keys, and assigns this code explicitly to
    any applicable requirement neither `REGISTRY` nor the aggregation
    step covers -- after the fixes in this same change, this should be
    empirically empty, but the code path exists and is tested regardless
    of whether it is currently ever hit, precisely so a FUTURE new
    requirement added to the corpus without a registered mechanism fails
    loudly instead of silently repeating this exact gap."""


# Codes that represent tooling/infrastructure problems, not a judgment RTF
# itself made. metrics.py excludes results carrying any of these from
# routing/precision/recall denominators entirely -- they are not "RTF got
# it wrong," they are "RTF never got a fair chance to answer."
INFRASTRUCTURE_CODES = frozenset({
    OperationalStatus.COMPILATION_FAILURE,
    OperationalStatus.ENVIRONMENT_FAILURE,
    OperationalStatus.ANALYZER_TIMEOUT,
    OperationalStatus.ANALYZER_CRASH,
    OperationalStatus.PARSER_LIMITATION,
})

# Codes that represent a genuine RTF-decision failure (the framework ran
# and reached an answer, the answer was wrong) -- eligible for
# quality-of-framework metrics, never conflated with INFRASTRUCTURE_CODES.
FRAMEWORK_DECISION_FAILURE_CODES = frozenset({
    OperationalStatus.ROUTING_FAILURE,
    OperationalStatus.EVIDENCE_COLLECTION_FAILURE,
    OperationalStatus.SEMANTIC_JUDGMENT_FAILURE,
    OperationalStatus.SUCCESSFUL_EXECUTION_WRONG_RESULT,
})

# Codes that represent an expected, non-defect outcome -- the requirement
# was correctly identified as unassessable from what's available, not a
# failure of the framework at all.
EXPECTED_LIMITATION_CODES = frozenset({
    OperationalStatus.MISSING_EXTERNAL_EVIDENCE,
    OperationalStatus.NO_JUSTIFIED_CORRESPONDENCE,
})

# Codes that represent a framework-COMPLETENESS gap -- a requirement this
# project has not yet built any executable mechanism for at all. Distinct
# from INFRASTRUCTURE_CODES (something built broke at runtime) and from
# EXPECTED_LIMITATION_CODES (correctly identified as unassessable from
# available evidence, not a "haven't built it yet" gap). Requirements
# carrying this code are exactly the ones a future implementation pass
# should target next.
IMPLEMENTATION_GAP_CODES = frozenset({
    OperationalStatus.UNSUPPORTED_ANALYZER,
})


def is_eligible_for_routing_metrics(status: OperationalStatus) -> bool:
    """Only OK results may be counted in requirement_routing_recall/
    precision, target_localization_accuracy, etc. (metrics.py) -- an
    infrastructure failure must reduce the metric's DENOMINATOR (the
    case is excluded, not silently treated as "RTF got it wrong"), never
    count as a routing miss.
    """
    return status == OperationalStatus.OK


def classify_bucket(status: OperationalStatus) -> str:
    """Which of the four top-level buckets (infrastructure / framework
    decision / expected limitation / implementation gap) a given code
    belongs to, for the post-run failure-attribution report. OK is its
    own bucket, not classified into any of the four.
    """
    if status == OperationalStatus.OK:
        return "OK"
    if status in INFRASTRUCTURE_CODES:
        return "INFRASTRUCTURE"
    if status in FRAMEWORK_DECISION_FAILURE_CODES:
        return "FRAMEWORK_DECISION_FAILURE"
    if status in EXPECTED_LIMITATION_CODES:
        return "EXPECTED_LIMITATION"
    if status in IMPLEMENTATION_GAP_CODES:
        return "IMPLEMENTATION_GAP"
    raise ValueError(f"unclassified OperationalStatus: {status!r}")
