"""Stage-separated L12 evaluation metrics.

Every metric returns a `(numerator, denominator)` raw-count pair, never a
bare percentage -- the same discipline Track A's go/no-go review used for
its own citation-validity/flip-rate thresholds, for the same reason: a
percentage over a small evaluation corpus looks more precise than the
underlying sample size supports.

Stage separation is the point of this module, not an incidental detail:
a miss at "did RTF even fire on the right requirement" (routing) is a
structurally different failure from "RTF fired correctly but collected
no usable evidence" (evidence collection) or "evidence was collected
correctly but L8 judged it wrong" (semantic judgment). Conflating these
into one "did RTF find it" number is exactly what this module is built
to avoid -- each metric isolates one stage.

Every metric excludes results whose `operational_status` is not `OK`
(see `failure_taxonomy.py`) from its denominator entirely. An
infrastructure failure is not a routing miss; it is a case RTF never got
a fair chance to answer, and folding it into a routing-failure count
would make the framework look worse at ROUTING than it actually is.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .failure_taxonomy import OperationalStatus, is_eligible_for_routing_metrics


class ApplicabilityState(str, Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    APPLICABILITY_UNKNOWN = "APPLICABILITY_UNKNOWN"


class ConformanceState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True)
class EvidenceItem:
    predicate: str
    location: str  # "Contract.function", "Contract", or a file path
    detail: str = ""


@dataclass(frozen=True)
class RoutedRequirementResult:
    """One requirement's outcome for one EVMbench target."""
    req_id: str
    applicability_state: ApplicabilityState
    operational_status: OperationalStatus = OperationalStatus.OK
    conformance_state: ConformanceState | None = None  # None iff NOT_APPLICABLE or an operational failure blocked evaluation
    evidence: tuple[EvidenceItem, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GroundTruthFinding:
    """One EVMbench ground-truth finding for one audit, with its L11
    correspondence and (where available) its real code location, e.g.
    extracted from the finding's fix patch diff.
    """
    finding_id: str
    audit_id: str
    correspondences: tuple[tuple[str, str], ...]  # ((req_id, relationship), ...)
    ground_truth_locations: tuple[str, ...] = field(default_factory=tuple)  # e.g. "Vault.sol", "Vault._burn"


@dataclass(frozen=True)
class TargetRunResult:
    audit_id: str
    routed: dict[str, RoutedRequirementResult]  # req_id -> result, one entry per requirement RTF evaluated for this target


def direct_req_ids(findings: list[GroundTruthFinding]) -> set[str]:
    """req_ids with at least one DIRECT correspondence anywhere in this
    target's ground truth. Only DIRECT feeds recall-like metrics, per the
    plan's L11 design -- PARTIAL/CONTEXTUAL are informative but must not
    inflate recall.
    """
    return {req_id for f in findings for req_id, rel in f.correspondences if rel == "DIRECT"}


def _eligible(run: TargetRunResult, req_id: str) -> RoutedRequirementResult | None:
    r = run.routed.get(req_id)
    if r is None or not is_eligible_for_routing_metrics(r.operational_status):
        return None
    return r


def requirement_routing_recall(run: TargetRunResult, findings: list[GroundTruthFinding]) -> tuple[int, int]:
    """Of requirements with a DIRECT ground-truth mapping for this
    target, how many did RTF's L3 applicability layer correctly mark
    APPLICABLE (with no operational failure blocking the attempt)?

    A DIRECT correspondence means a real vulnerability matching this
    requirement genuinely exists in this target -- so the requirement
    MUST be applicable; NOT_APPLICABLE or APPLICABILITY_UNKNOWN here is a
    real routing miss, not just a difference of interpretation.
    """
    expected = direct_req_ids(findings)
    if not expected:
        return (0, 0)
    hit = 0
    for req_id in expected:
        r = _eligible(run, req_id)
        if r is not None and r.applicability_state == ApplicabilityState.APPLICABLE:
            hit += 1
    return (hit, len(expected))


def requirement_routing_precision(run: TargetRunResult, findings: list[GroundTruthFinding]) -> tuple[int, int]:
    """Of requirements RTF actually marked APPLICABLE for this target
    (with no operational failure), how many have a DIRECT ground-truth
    justification? The mirror of routing recall -- recall asks "did RTF
    catch every real case," precision asks "when RTF fired, was it
    right."
    """
    expected = direct_req_ids(findings)
    routed_applicable = [
        req_id for req_id, r in run.routed.items()
        if is_eligible_for_routing_metrics(r.operational_status)
        and r.applicability_state == ApplicabilityState.APPLICABLE
    ]
    if not routed_applicable:
        return (0, 0)
    justified = sum(1 for req_id in routed_applicable if req_id in expected)
    return (justified, len(routed_applicable))


def target_localization_accuracy(run: TargetRunResult, findings: list[GroundTruthFinding]) -> tuple[int, int]:
    """Of DIRECT ground-truth findings where RTF DID collect evidence for
    the corresponding requirement, how many of that evidence's locations
    actually overlap the finding's real ground-truth location (e.g. the
    finding's fix-patch diff path/contract/function)?

    Deliberately measured only among findings where evidence exists --
    this metric answers "when RTF pointed somewhere, did it point to the
    right place," not "did RTF find it at all" (that's evidence-
    collection recall, below). A finding with no collected evidence is
    excluded from this metric's denominator, not counted as a
    localization miss -- conflating the two would blame localization for
    an evidence-collection failure.

    Matches on the FULL location string ("Contract.function"), not just
    the contract name -- a real bug caught by this project's own first
    real evaluation run: an earlier version of this function compared
    only the substring before the first '.', which trivially "matched"
    any evidence anywhere in the same contract file as the ground truth,
    regardless of which function it was actually in. For a real target
    where every candidate location lives in one file (e.g. a single
    `Vault.sol`), that earlier version silently reported 100% accuracy
    even when the evidence pointed at a completely different function
    than the real bug -- exactly the false-confidence failure mode this
    metric exists to catch, not produce.
    """
    hit = 0
    total = 0
    for f in findings:
        direct_reqs = {req_id for req_id, rel in f.correspondences if rel == "DIRECT"}
        if not direct_reqs or not f.ground_truth_locations:
            continue
        for req_id in direct_reqs:
            r = _eligible(run, req_id)
            if r is None or not r.evidence:
                continue  # no evidence collected -- excluded, not a localization miss
            total += 1
            gt_locations = {loc.lower() for loc in f.ground_truth_locations}
            ev_locations = {e.location.lower() for e in r.evidence}
            if gt_locations & ev_locations:
                hit += 1
    return (hit, total)


def evidence_collection_recall(run: TargetRunResult, findings: list[GroundTruthFinding]) -> tuple[int, int]:
    """Of DIRECT ground-truth findings, how many correspond to a
    requirement where RTF's predicate produced AT LEAST ONE evidence
    item, regardless of what L8 ultimately judged? Isolates the evidence
    stage from the judgment stage -- a routing hit with zero evidence is
    an evidence-collection failure, not a semantic-judgment failure.
    """
    expected = direct_req_ids(findings)
    if not expected:
        return (0, 0)
    hit = 0
    for req_id in expected:
        r = _eligible(run, req_id)
        if r is not None and len(r.evidence) > 0:
            hit += 1
    return (hit, len(expected))


def final_finding_recall(run: TargetRunResult, findings: list[GroundTruthFinding]) -> tuple[int, int]:
    """Of DIRECT ground-truth findings, how many correspond to a
    requirement RTF's FULL pipeline (routing + evidence + L8 judgment)
    resolved all the way to `ConformanceState.FAIL`? This is the
    end-to-end metric -- the only one of this module's metrics that
    requires every stage to have worked, and the one most directly
    comparable to a traditional benchmark "recall" number. Every other
    metric here exists specifically so a low number here can be
    attributed to a SPECIFIC stage rather than reported as one opaque
    miss.
    """
    expected = direct_req_ids(findings)
    if not expected:
        return (0, 0)
    hit = 0
    for req_id in expected:
        r = _eligible(run, req_id)
        if r is not None and r.conformance_state == ConformanceState.FAIL:
            hit += 1
    return (hit, len(expected))


def false_alert_rate(run: TargetRunResult, findings: list[GroundTruthFinding]) -> tuple[int, int]:
    """Of requirements RTF resolved to `ConformanceState.FAIL` for this
    target, how many have NO correspondence record at all (not even
    PARTIAL/CONTEXTUAL) linking them to any real finding in this audit?
    Deliberately lenient about what counts as "justified" here (PARTIAL/
    CONTEXTUAL count, not just DIRECT) -- this metric is asking "is this
    alert noise," not "is this alert a perfect ground-truth match,"
    which is a different, stricter question `final_finding_recall`
    already answers.
    """
    all_correspondences = {(req_id, rel) for f in findings for req_id, rel in f.correspondences}
    justified_req_ids = {req_id for req_id, _rel in all_correspondences}
    fails = [
        req_id for req_id, r in run.routed.items()
        if is_eligible_for_routing_metrics(r.operational_status)
        and r.conformance_state == ConformanceState.FAIL
    ]
    if not fails:
        return (0, 0)
    unjustified = sum(1 for req_id in fails if req_id not in justified_req_ids)
    return (unjustified, len(fails))


def inconclusive_rate(run: TargetRunResult) -> tuple[int, int]:
    """Of all APPLICABLE, operationally-OK requirement results for this
    target, what fraction resolved to INCONCLUSIVE? Per the plan,
    INCONCLUSIVE is a legitimate, expected outcome, not a defect -- this
    metric exists to REPORT its rate honestly, not to be minimized.
    """
    applicable = [
        r for r in run.routed.values()
        if is_eligible_for_routing_metrics(r.operational_status)
        and r.applicability_state == ApplicabilityState.APPLICABLE
    ]
    if not applicable:
        return (0, 0)
    n = sum(1 for r in applicable if r.conformance_state == ConformanceState.INCONCLUSIVE)
    return (n, len(applicable))


def insufficient_evidence_rate(run: TargetRunResult) -> tuple[int, int]:
    """Of all APPLICABLE, operationally-OK requirement results for this
    target, what fraction resolved to INSUFFICIENT_EVIDENCE? Same
    "legitimate outcome, not a defect" framing as inconclusive_rate --
    directly analogous to L7's own `repo-only assessability rate`
    concept, generalized here to the whole corpus rather than just
    Q-level requirements.
    """
    applicable = [
        r for r in run.routed.values()
        if is_eligible_for_routing_metrics(r.operational_status)
        and r.applicability_state == ApplicabilityState.APPLICABLE
    ]
    if not applicable:
        return (0, 0)
    n = sum(1 for r in applicable if r.conformance_state == ConformanceState.INSUFFICIENT_EVIDENCE)
    return (n, len(applicable))


def applicability_recall_on_known_applicable(run: TargetRunResult, findings: list[GroundTruthFinding]) -> tuple[int, int]:
    """Of requirements KNOWN to be applicable to this target (because a
    DIRECT ground-truth finding proves the vulnerable construct is
    present), how many did RTF's L3 layer correctly mark APPLICABLE?

    Named deliberately narrowly, NOT `applicability_accuracy`: this is
    only the recall half. The precision half -- of requirements RTF
    marked NOT_APPLICABLE, how many were CORRECTLY inapplicable -- cannot
    be computed automatically from raw EVMbench data, because EVMbench
    findings only document what IS wrong, never certify that a given
    requirement definitely does NOT apply to a target. Establishing that
    would require a separate, manually-reviewed "confirmed inapplicable"
    label set that does not currently exist. Reported as an explicit,
    logged limitation (see AR register), not silently approximated by
    this function or hidden by a misleadingly complete-sounding name.
    """
    return requirement_routing_recall(run, findings)
