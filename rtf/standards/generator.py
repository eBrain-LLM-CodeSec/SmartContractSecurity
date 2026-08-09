"""Translates a standard's normative clauses into atomic RTF requirements
(`GeneratedRequirement`), and determines clause-level applicability given a
standard-level `StandardDetectionResult`.

Source-driven only: every field on a `GeneratedRequirement` traces directly
to its originating `NormativeClause` (itself traced to a pinned spec
snapshot) -- nothing here injects vulnerability-taxonomy language, EVMbench
knowledge, or any audit-specific fact.
"""
from __future__ import annotations

import hashlib
import re

from .models import (
    ApplicabilityStatus,
    DerivationType,
    GeneratedRequirement,
    NormativeClause,
    RequirementApplicabilityResult,
    StandardDetectionResult,
    StandardRecord,
)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def generated_requirement_id(standard_id: str, clause_id: str) -> str:
    """Deterministic, stable across repeated runs -- a pure function of
    (standard_id, clause_id), never a timestamp or random suffix. Per the
    plan's own example shape (`gp-accepted-standard__erc4626__...`), but
    keeping the clause_id verbatim as the suffix rather than re-deriving a
    second slug from obligation text, so a requirement_id -> clause_id ->
    provenance chain is a direct, lossless lookup, not a re-parse."""
    return f"gp-accepted-standard__{_slug(standard_id)}__{clause_id}"


def generate_requirements_for_standard(
    record: StandardRecord,
    clauses: tuple[NormativeClause, ...],
) -> list[GeneratedRequirement]:
    """One GeneratedRequirement per NormativeClause -- DerivationType.
    STANDARD_CLAUSE_DIRECT, the only derivation this generator currently
    performs (a 1:1 clause -> requirement translation; no composite/
    cross-clause requirements are synthesized). Deterministic: calling this
    twice with the same (record, clauses) produces byte-identical output
    (see test_generator.py's determinism test) -- no wall-clock timestamps,
    no random IDs, no unordered-set iteration anywhere in this function.
    """
    out: list[GeneratedRequirement] = []
    for clause in clauses:
        req_id = generated_requirement_id(record.standard_id, clause.clause_id)
        source_text_hash = hashlib.sha256(clause.provenance.quoted_text.encode("utf-8")).hexdigest()
        out.append(
            GeneratedRequirement(
                requirement_id=req_id,
                source_family=record.source_family,
                source_id=record.standard_id,
                source_title=record.title,
                source_url_or_local_spec=record.canonical_source_reference,
                source_version=record.version,
                source_section=clause.section,
                normative_strength=clause.original_normative_strength,
                parent_requirement_id=record.parent_gp_requirement_id,
                derivation_type=DerivationType.STANDARD_CLAUSE_DIRECT,
                clause_id=clause.clause_id,
                obligation_text=clause.normalized_obligation,
                conditions=clause.conditions,
                exceptions=clause.exceptions,
                affected_interface=clause.affected_interface,
                source_text_hash=source_text_hash,
            )
        )
    return out


_STRUCTURAL_MARKER_PREFIXES = ("contract:", "event:")


def _contract_surface(slither, contract_name: str) -> set[str]:
    """All function AND event names visible on the named contract (its own
    plus inherited) -- a generated clause naming e.g. `totalAssets` is
    applicable if that name appears here, regardless of whether it's
    declared directly or inherited from a base (mirrors discovery.py's own
    transitive-inheritance handling, not a stricter check)."""
    for contract in getattr(slither, "contracts_derived", []):
        if contract.name == contract_name:
            names = {f.name for f in getattr(contract, "functions", [])}
            names |= {e.name for e in getattr(contract, "events", [])}
            return names
    return set()


def determine_clause_applicability(
    req: GeneratedRequirement,
    detection: StandardDetectionResult,
    slither,
) -> RequirementApplicabilityResult:
    """Two-level applicability per the plan's §11:
      1. STANDARD applicability (`detection.applicable`) gates everything --
         if the standard itself isn't APPLICABLE, no clause of it is either.
      2. CLAUSE applicability: does the specific function/event this clause
         names actually exist on the identified implementing contract(s)?
         A clause with a semantic activation CONDITION (e.g. "if the Vault
         is non-transferrable") that can't be mechanically evaluated from
         structure alone resolves to UNKNOWN, not silently APPLICABLE or
         silently dropped -- deferred to the agent investigation, which
         DOES receive the condition text (see routing.py's bundle
         renderer) and can resolve it from real repository content.
    Every branch returns an explicit reason -- no silent NOT_APPLICABLE.
    """
    from .models import DetectionConfidence  # local import: avoids a cycle with models re-exports elsewhere

    if detection.applicable != DetectionConfidence.APPLICABLE:
        return RequirementApplicabilityResult(
            requirement_id=req.requirement_id,
            status=ApplicabilityStatus.NOT_APPLICABLE,
            reason=(
                f"parent standard {req.source_id} was not determined APPLICABLE to this "
                f"repository ({detection.applicable.value}): {detection.reason}"
            ),
        )

    named_targets = [t for t in req.affected_interface if not t.startswith(_STRUCTURAL_MARKER_PREFIXES)]
    if named_targets:
        surface: set[str] = set()
        for contract_name in detection.contracts:
            surface |= _contract_surface(slither, contract_name)
        missing = [t for t in named_targets if t not in surface]
        if missing:
            return RequirementApplicabilityResult(
                requirement_id=req.requirement_id,
                status=ApplicabilityStatus.NOT_APPLICABLE,
                reason=(
                    f"named target(s) {missing} not found on any identified implementing "
                    f"contract {list(detection.contracts)} -- likely an optional standard "
                    f"feature this repository does not use"
                ),
            )

    if req.conditions:
        return RequirementApplicabilityResult(
            requirement_id=req.requirement_id,
            status=ApplicabilityStatus.UNKNOWN,
            reason=(
                f"clause has activation condition(s) {list(req.conditions)} that cannot be "
                f"mechanically evaluated from contract structure alone -- routed to agent "
                f"investigation to resolve from real repository content, not silently assumed "
                f"either way"
            ),
        )

    return RequirementApplicabilityResult(
        requirement_id=req.requirement_id,
        status=ApplicabilityStatus.APPLICABLE,
        reason=(
            f"parent standard {req.source_id} is applicable (contracts: {list(detection.contracts)}) "
            f"and this clause's target(s) {named_targets or '(contract-level)'} are present with no "
            f"unresolved activation condition"
        ),
    )
