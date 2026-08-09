"""Routes generated ERC requirements into the pipeline's existing
`RoutedRequirementResult` shape (`rtf.l12_evaluation.metrics`), and renders
the agent-prompt bundle for a generated requirement.

This is the ONLY module in `rtf/standards/` that imports from
`rtf.l12_evaluation` -- deliberately: everything upstream of this file
(models/registry/clause_parser/discovery/generator) has zero dependency on
the pipeline package and could be reused standalone; this module exists
specifically to bridge into it.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path

from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState, EvidenceItem, OperationalStatus, RoutedRequirementResult

from .discovery import discover_applicable_standards
from .generator import determine_clause_applicability, generate_requirements_for_standard
from .models import ApplicabilityStatus, DetectionConfidence, GeneratedRequirement, StandardDetectionResult
from .registry import StandardsRegistry


class RoutingDecision(str, Enum):
    DETERMINISTIC_COMPLETE = "DETERMINISTIC_COMPLETE"
    AGENT_REQUIRED = "AGENT_REQUIRED"


def classify_requirement(req: GeneratedRequirement) -> RoutingDecision:
    """Every currently-generated requirement (DerivationType.
    STANDARD_CLAUSE_DIRECT, translated from one ERC-4626/ERC-20 clause) is
    AGENT_REQUIRED, unconditionally. Per the plan's own conservative-
    default discipline (mirroring `rtf.l12_evaluation.registry`'s
    DETERMINISTIC_COMPLETE_REQ_IDS, whose 19-of-78 membership is the
    exception, not the rule): none of these obligations are the kind a
    predicate can verify COMPLETELY and RELIABLY without semantic
    reasoning -- accounting correctness (does totalAssets() over/under-
    count a specific balance component?), exact behavioral relationships
    between two DIFFERENT functions in the same transaction (previewDeposit
    vs deposit), and rounding-direction correctness are not mechanically
    decidable from structure alone. A future, narrower deterministic path
    (e.g. a pure interface-shape check with no semantic component) would
    need its own explicit, individually-justified carve-out here -- this
    function deliberately does not invent one preemptively.
    """
    return RoutingDecision.AGENT_REQUIRED


def render_generated_requirement_bundle(req: GeneratedRequirement, detection: StandardDetectionResult) -> dict:
    """Builds an in-memory L2-context-bundle-shaped dict for a generated
    requirement, matching the exact schema `judgment_layer.
    render_context_bundle_text` and `codex_bridge.build_codex_prompt_
    inputs` already expect (see `l2_context_bundles/*.json`'s real shape)
    -- so no rendering-side code needs to change to handle a generated
    requirement, only the bundle SOURCE (file read vs this in-memory dict).

    Carries every field §10 of the plan requires the agent to receive:
    standard identity, exact obligation, normative strength, conditions/
    exceptions, provenance/source section, and why the standard was
    determined applicable (from the real `StandardDetectionResult`, not
    asserted).
    """
    lines = [
        f"[EXTERNAL_STANDARD_DERIVED] {req.source_family} {req.source_id} ({req.source_title}), "
        f"version {req.source_version}, section {req.source_section}.",
        f"Parent EthTrust requirement: {req.parent_requirement_id} ([GP] Follow Accepted ERC Standards).",
        f"Normative strength: {req.normative_strength.value}.",
        f"Obligation: {req.obligation_text}",
    ]
    if req.conditions:
        lines.append("Conditions (this obligation applies ONLY when these hold, per the source spec -- verify against the real repository, do not assume): " + "; ".join(req.conditions))
    if req.exceptions:
        lines.append("Exceptions (this obligation does NOT apply when): " + "; ".join(req.exceptions))
    if req.affected_interface:
        lines.append("Affected interface/function(s): " + ", ".join(req.affected_interface))
    lines.append(f"Source: {req.source_url_or_local_spec} (local pinned snapshot, hash {req.source_text_hash[:16]}...)")

    why_applicable = (
        f"{req.source_id} was determined applicable to this repository. "
        f"Detector verdict: {detection.applicable.value} (confidence {detection.confidence}). "
        f"Reason: {detection.reason} "
        f"Evidence: {'; '.join(detection.evidence) if detection.evidence else '(none recorded)'}"
    )

    return {
        "req_id": req.requirement_id,
        "bundle": {
            "self": "\n".join(lines),
            "definitions": [],
            "parent_section_context": why_applicable,
            "referenced_requirements": [],
            "overriding_requirements": [],
            "exceptions": [],
            "external_references": [
                {"id": req.source_id, "text": f"{req.source_title} -- {req.source_url_or_local_spec}"}
            ],
        },
    }


@dataclass
class StandardsIntegrityReport:
    """Additive counters per the plan's §12 -- deliberately a SEPARATE
    report object, not new fields bolted onto `pipeline_e2e.IntegrityReport`
    (which stays byte-for-byte unchanged for the frozen 81-requirement
    path; existing consumers of its exact shape are not put at risk).
    `compute_integrity_report` (unmodified) still runs over the FULL merged
    `routed` dict (81-corpus + generated) at the pipeline_e2e.py call site,
    so the "no silent disappearance" invariant genuinely covers generated
    requirements too -- this report adds the standards-specific breakdown
    on top, it doesn't replace that check.
    """

    standards_considered: int = 0
    standards_discovered_applicable: int = 0
    standards_discovered_uncertain: int = 0
    standards_discovered_not_applicable: int = 0
    clauses_loaded: int = 0
    requirements_generated: int = 0
    requirements_applicable: int = 0
    requirements_not_applicable: int = 0
    requirements_routed_deterministic: int = 0
    requirements_routed_agent: int = 0
    unsupported: int = 0
    silently_missing: int = 0
    silently_missing_requirement_ids: list = field(default_factory=list)
    valid: bool = True
    invalid_reason: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _evidence_for_requirement(req: GeneratedRequirement, applicability_reason: str, detection: StandardDetectionResult) -> tuple[EvidenceItem, ...]:
    location = detection.contracts[0] if detection.contracts else req.source_id
    detail = (
        f"Generated from {req.source_id} clause {req.clause_id} ({req.normative_strength.value}): "
        f"{req.obligation_text} | Applicability: {applicability_reason}"
    )
    return (
        EvidenceItem(
            predicate="rtf.standards.generator.generate_requirements_for_standard",
            location=location,
            detail=detail,
            structured={
                "requirement_id": req.requirement_id,
                "standard_id": req.source_id,
                "clause_id": req.clause_id,
                "source_section": req.source_section,
            },
        ),
    )


def build_standards_routed_requirements(
    repo_root: Path,
    entry_sol_file: Path,
    slither,
    registry: StandardsRegistry | None = None,
) -> tuple[dict[str, RoutedRequirementResult], StandardsIntegrityReport, dict[str, dict]]:
    """The main Phase 3 entry point: discovers applicable standards,
    generates their atomic requirements, determines clause-level
    applicability, and returns:
      1. `routed` -- req_id -> RoutedRequirementResult, ready to be merged
         additively into an existing `run.routed` dict (same shape the
         81-corpus's own `run_rtf.py` produces).
      2. a `StandardsIntegrityReport` with the §12 breakdown counters.
      3. `bundles` -- req_id -> in-memory L2-bundle-shaped dict, for
         `codex_bridge.build_codex_prompt_inputs`'s new `bundle_record`
         override parameter (no `l2_context_bundles/*.json` file needed).

    Every generated requirement reaches EXACTLY one terminal routing
    status here (APPLICABLE+evidence -> agent-pending, or NOT_APPLICABLE)
    -- `report.silently_missing` asserts this directly, independent of
    `pipeline_e2e.compute_integrity_report`'s own (unmodified) check on
    the merged dict.
    """
    registry = registry if registry is not None else StandardsRegistry()
    detections = discover_applicable_standards(repo_root, entry_sol_file, slither, registry)

    routed: dict[str, RoutedRequirementResult] = {}
    bundles: dict[str, dict] = {}
    report = StandardsIntegrityReport(standards_considered=len(detections))
    all_requirement_ids: list[str] = []
    accounted_ids: set[str] = set()

    for detection in detections:
        if detection.applicable == DetectionConfidence.APPLICABLE:
            report.standards_discovered_applicable += 1
        elif detection.applicable == DetectionConfidence.UNCERTAIN:
            report.standards_discovered_uncertain += 1
        else:
            report.standards_discovered_not_applicable += 1

        record = registry.load(detection.standard_id)
        clauses = registry.load_clauses(detection.standard_id)
        report.clauses_loaded += len(clauses)

        requirements = generate_requirements_for_standard(record, clauses)
        report.requirements_generated += len(requirements)

        for req in requirements:
            all_requirement_ids.append(req.requirement_id)
            applicability = determine_clause_applicability(req, detection, slither)

            if applicability.status == ApplicabilityStatus.NOT_APPLICABLE:
                accounted_ids.add(req.requirement_id)
                report.requirements_not_applicable += 1
                routed[req.requirement_id] = RoutedRequirementResult(
                    req_id=req.requirement_id,
                    applicability_state=ApplicabilityState.NOT_APPLICABLE,
                    operational_status=OperationalStatus.OK,
                    conformance_state=None,
                    evidence=(),
                )
                continue

            # APPLICABLE and UNKNOWN (clause-level) both route to the agent
            # -- UNKNOWN means "condition can't be mechanically resolved,"
            # which is precisely what an agent investigation is for (see
            # generator.determine_clause_applicability's docstring and the
            # plan's §17: "an unresolved graph location does NOT prevent
            # agent invocation" -- the same discipline applies here to an
            # unresolved CLAUSE condition).
            accounted_ids.add(req.requirement_id)
            report.requirements_applicable += 1
            decision = classify_requirement(req)
            evidence = _evidence_for_requirement(req, applicability.reason, detection)
            bundles[req.requirement_id] = render_generated_requirement_bundle(req, detection)

            if decision == RoutingDecision.DETERMINISTIC_COMPLETE:
                report.requirements_routed_deterministic += 1
                # Not currently reachable (classify_requirement always
                # returns AGENT_REQUIRED) -- branch kept so a future
                # narrower deterministic carve-out has a defined landing
                # spot instead of needing new plumbing.
                routed[req.requirement_id] = RoutedRequirementResult(
                    req_id=req.requirement_id,
                    applicability_state=ApplicabilityState.APPLICABLE,
                    operational_status=OperationalStatus.OK,
                    conformance_state=ConformanceState.FAIL,
                    evidence=evidence,
                )
            else:
                report.requirements_routed_agent += 1
                routed[req.requirement_id] = RoutedRequirementResult(
                    req_id=req.requirement_id,
                    applicability_state=ApplicabilityState.APPLICABLE,
                    operational_status=OperationalStatus.OK,
                    conformance_state=None,  # pending agent investigation, same convention AGENT_REQUIRED_REQ_IDS uses
                    evidence=evidence,
                )

    missing_ids = sorted(set(all_requirement_ids) - accounted_ids)
    report.silently_missing = len(missing_ids)
    report.silently_missing_requirement_ids = missing_ids
    routed_total = report.requirements_routed_deterministic + report.requirements_routed_agent
    report.valid = report.silently_missing == 0 and routed_total == report.requirements_applicable
    if not report.valid and report.invalid_reason is None:
        report.invalid_reason = (
            f"{report.silently_missing} generated requirement(s) unaccounted for, or "
            f"routed_total ({routed_total}) != requirements_applicable ({report.requirements_applicable})"
        )

    return routed, report, bundles
