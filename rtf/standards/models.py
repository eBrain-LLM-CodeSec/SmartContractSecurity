"""Data model for the standards-driven GP requirement-generation mechanism.

Every type here is a plain, frozen dataclass with an explicit `from_dict`/
`to_dict` pair (not a generic dataclass-to-json helper) so the on-disk JSON
shape is asserted explicitly at every load boundary -- a malformed
`clauses.json`/`standard.json` fails loudly with a clear `KeyError`/
`ValueError` at load time (see registry.py's tests), not silently downstream.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NormativeStrength(str, Enum):
    """RFC2119 terms, kept distinct rather than flattened to a single
    'is normative' boolean -- MUST and SHOULD carry materially different
    obligations (see the implementation plan's explicit instruction not to
    flatten these)."""

    MUST = "MUST"
    MUST_NOT = "MUST_NOT"
    SHALL = "SHALL"
    SHALL_NOT = "SHALL_NOT"
    SHOULD = "SHOULD"
    SHOULD_NOT = "SHOULD_NOT"
    MAY = "MAY"

    @classmethod
    def from_text(cls, text: str) -> "NormativeStrength":
        """Normalizes raw spec-prose keyword spellings (case-sensitive --
        RFC2119 normative terms are conventionally ALL CAPS; a lowercase
        'must' is prose, not a keyword, and must never reach here as if it
        were one -- see clause_parser.py's extraction logic, which enforces
        this before ever constructing a NormativeStrength).
        """
        normalized = " ".join(text.split()).upper()
        mapping = {
            "MUST": cls.MUST,
            "MUST NOT": cls.MUST_NOT,
            "MUST_NOT": cls.MUST_NOT,
            "SHALL": cls.SHALL,
            "SHALL NOT": cls.SHALL_NOT,
            "SHALL_NOT": cls.SHALL_NOT,
            "SHOULD": cls.SHOULD,
            "SHOULD NOT": cls.SHOULD_NOT,
            "SHOULD_NOT": cls.SHOULD_NOT,
            "MAY": cls.MAY,
            "REQUIRED": cls.MUST,
            "RECOMMENDED": cls.SHOULD,
            "OPTIONAL": cls.MAY,
        }
        if normalized not in mapping:
            raise ValueError(
                f"unsupported normative strength {text!r} -- not one of the "
                f"RFC2119 terms this module recognizes; fails explicitly "
                f"rather than silently coercing to a guessed value"
            )
        return mapping[normalized]


@dataclass(frozen=True)
class ClauseProvenance:
    source_file: str
    source_section_heading: str
    quoted_text: str

    @classmethod
    def from_dict(cls, d: dict) -> "ClauseProvenance":
        return cls(
            source_file=d["source_file"],
            source_section_heading=d["source_section_heading"],
            quoted_text=d["quoted_text"],
        )

    def to_dict(self) -> dict:
        return {
            "source_file": self.source_file,
            "source_section_heading": self.source_section_heading,
            "quoted_text": self.quoted_text,
        }


@dataclass(frozen=True)
class NormativeClause:
    """One atomic normative obligation extracted from a standard's spec
    text. Deliberately retains `conditions`/`exceptions` as separate lists
    rather than folding them into `normalized_obligation` prose -- so
    "If X, implementation MUST Y" stays distinguishable from an
    unconditional "implementation MUST Y" downstream (applicability.py and
    generator.py both depend on this distinction being real, not lost)."""

    clause_id: str
    standard_id: str
    section: str
    original_normative_strength: NormativeStrength
    normalized_obligation: str
    affected_interface: tuple[str, ...]
    conditions: tuple[str, ...]
    exceptions: tuple[str, ...]
    provenance: ClauseProvenance

    @classmethod
    def from_dict(cls, d: dict) -> "NormativeClause":
        return cls(
            clause_id=d["clause_id"],
            standard_id=d["standard_id"],
            section=d["section"],
            original_normative_strength=NormativeStrength.from_text(d["original_normative_strength"]),
            normalized_obligation=d["normalized_obligation"],
            affected_interface=tuple(d.get("affected_interface", ())),
            conditions=tuple(d.get("conditions", ())),
            exceptions=tuple(d.get("exceptions", ())),
            provenance=ClauseProvenance.from_dict(d["provenance"]),
        )

    def to_dict(self) -> dict:
        return {
            "clause_id": self.clause_id,
            "standard_id": self.standard_id,
            "section": self.section,
            "original_normative_strength": self.original_normative_strength.value,
            "normalized_obligation": self.normalized_obligation,
            "affected_interface": list(self.affected_interface),
            "conditions": list(self.conditions),
            "exceptions": list(self.exceptions),
            "provenance": self.provenance.to_dict(),
        }


@dataclass(frozen=True)
class DetectionSignal:
    signal_id: str
    signal_type: str
    pattern: tuple[str, ...]
    description: str

    @classmethod
    def from_dict(cls, d: dict) -> "DetectionSignal":
        return cls(
            signal_id=d["signal_id"],
            signal_type=d["signal_type"],
            pattern=tuple(d.get("pattern", ())),
            description=d["description"],
        )


@dataclass(frozen=True)
class StandardRecord:
    """One registered accepted standard (e.g. ERC-4626). `clauses` is
    loaded lazily by the registry from `clauses_path`, not embedded here --
    keeps StandardRecord cheap to enumerate (registry.all_ids() etc.)
    without parsing every clause file up front."""

    standard_id: str
    source_family: str
    title: str
    version: str
    status: str
    canonical_source_reference: str
    local_spec_path: str
    local_source_hash: str
    clauses_path: str
    parent_gp_requirement_id: str
    detection_signals_strong: tuple[DetectionSignal, ...]
    detection_signals_supporting: tuple[DetectionSignal, ...]

    @classmethod
    def from_dict(cls, d: dict) -> "StandardRecord":
        sigs = d["detection_signals"]
        return cls(
            standard_id=d["standard_id"],
            source_family=d["source_family"],
            title=d["title"],
            version=d["version"],
            status=d["status"],
            canonical_source_reference=d["canonical_source_reference"],
            local_spec_path=d["local_spec_path"],
            local_source_hash=d["local_source_hash"],
            clauses_path=d["clauses_path"],
            parent_gp_requirement_id=d["parent_gp_requirement_id"],
            detection_signals_strong=tuple(DetectionSignal.from_dict(s) for s in sigs["strong"]),
            detection_signals_supporting=tuple(DetectionSignal.from_dict(s) for s in sigs["supporting"]),
        )


class DetectionConfidence(str, Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNCERTAIN = "UNCERTAIN"


@dataclass(frozen=True)
class StandardDetectionResult:
    standard_id: str
    applicable: DetectionConfidence
    confidence: float
    evidence: tuple[str, ...]
    contracts: tuple[str, ...]
    interfaces: tuple[str, ...]
    reason: str


class ApplicabilityStatus(str, Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RequirementApplicabilityResult:
    requirement_id: str
    status: ApplicabilityStatus
    reason: str


class DerivationType(str, Enum):
    STANDARD_CLAUSE_DIRECT = "STANDARD_CLAUSE_DIRECT"
    """Requirement text is a direct, source-driven translation of exactly
    one NormativeClause -- the only derivation type Phase 3's generator
    currently produces; enum kept extensible (e.g. a future composite
    derivation) without needing a schema migration."""


@dataclass(frozen=True)
class GeneratedRequirement:
    """An atomic RTF requirement synthesized from one NormativeClause.
    Mirrors the provenance fields the plan requires explicitly (source_
    family/source_id/source_title/source_url_or_local_spec/source_version/
    source_section/normative_strength/parent_requirement_id/derivation_type)
    -- deliberately NOT encoding all of this into the requirement_id string,
    per the plan's explicit instruction."""

    requirement_id: str
    source_family: str
    source_id: str
    source_title: str
    source_url_or_local_spec: str
    source_version: str
    source_section: str
    normative_strength: NormativeStrength
    parent_requirement_id: str
    derivation_type: DerivationType
    clause_id: str
    obligation_text: str
    conditions: tuple[str, ...]
    exceptions: tuple[str, ...]
    affected_interface: tuple[str, ...]
    source_text_hash: str

    def to_dict(self) -> dict:
        return {
            "requirement_id": self.requirement_id,
            "source_family": self.source_family,
            "source_id": self.source_id,
            "source_title": self.source_title,
            "source_url_or_local_spec": self.source_url_or_local_spec,
            "source_version": self.source_version,
            "source_section": self.source_section,
            "normative_strength": self.normative_strength.value,
            "parent_requirement_id": self.parent_requirement_id,
            "derivation_type": self.derivation_type.value,
            "clause_id": self.clause_id,
            "obligation_text": self.obligation_text,
            "conditions": list(self.conditions),
            "exceptions": list(self.exceptions),
            "affected_interface": list(self.affected_interface),
            "source_text_hash": self.source_text_hash,
        }
