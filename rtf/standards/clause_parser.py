"""Generic RFC2119 normative-clause extractor.

**Not used to produce any standard's production `clauses.json`** (see e.g.
`rtf/standards/erc/ERC-4626/clauses.json`'s own `extraction_method_note`) --
real spec prose (EIP-4626 included) is irregular enough that a fully
automatic pass is unreliable for a benchmark-facing artifact. Per the
implementation plan's own fallback instruction, production standards use a
manually reviewed/pinned clause representation instead.

This module exists to prove the extraction MECHANISM works generically, and
is exercised only by `test_clause_parser.py` against synthetic fixtures
covering the required cases (MUST/MUST NOT/SHOULD/SHOULD NOT/MAY, multiline
statements, multiple terms in one paragraph, conditions, exceptions, and
false positives from prose merely mentioning a lowercase keyword).

Deliberately conservative and honest about uncertainty:
  - Only ALL-CAPS keyword spellings are treated as normative, matching
    RFC2119's own convention -- "the implementation must have an address"
    (lowercase) is prose, not a requirement, and is never extracted.
  - One sentence containing more than one distinct RFC2119 keyword is
    split into multiple candidate clauses (on internal "; " or ", and "
    boundaries where present) rather than silently picking one keyword and
    discarding the other's obligation.
"""
from __future__ import annotations

import hashlib
import re

from .models import ClauseProvenance, NormativeClause, NormativeStrength

# Longest-first so "MUST NOT" matches before the bare "MUST" alternative
# would otherwise shadow it.
_KEYWORD_PATTERN = re.compile(
    r"\b(MUST NOT|MUST|SHALL NOT|SHALL|SHOULD NOT|SHOULD|MAY)\b"
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

_CONDITION_PREFIX = re.compile(r"^\s*If\s+(?P<condition>.+?),\s*(?P<rest>.+)$", re.IGNORECASE | re.DOTALL)
_EXCEPTION_SUFFIX = re.compile(r"^(?P<obligation>.+?)\s+unless\s+(?P<exception>.+?)\.?\s*$", re.IGNORECASE | re.DOTALL)

# Sentences containing two clauses joined by these connectors are split
# further so a second normative keyword in the same sentence is not
# silently dropped.
_MULTI_CLAUSE_SPLIT = re.compile(r";\s+|,\s+and\s+(?=\w+\s+(?:MUST|SHALL|SHOULD|MAY)\b)")


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _split_sentences(paragraph: str) -> list[str]:
    normalized = _normalize_whitespace(paragraph)
    if not normalized:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT.split(normalized) if s.strip()]


def _split_multi_clause(sentence: str) -> list[str]:
    parts = _MULTI_CLAUSE_SPLIT.split(sentence)
    return [p.strip() for p in parts if p.strip()]


def _extract_condition_and_exception(clause_text: str) -> tuple[str, list[str], list[str]]:
    """Returns (obligation_text_with_keyword_intact, conditions, exceptions).
    Deliberately does NOT strip the condition into the obligation text --
    "If X, implementation MUST Y" must not collapse into an unconditional
    "implementation MUST Y", per the plan's explicit warning.
    """
    conditions: list[str] = []
    exceptions: list[str] = []
    remaining = clause_text

    cond_match = _CONDITION_PREFIX.match(remaining)
    if cond_match:
        conditions.append(cond_match.group("condition").strip())
        remaining = cond_match.group("rest").strip()

    exc_match = _EXCEPTION_SUFFIX.match(remaining)
    if exc_match:
        exceptions.append(exc_match.group("exception").strip().rstrip("."))
        remaining = exc_match.group("obligation").strip()

    return remaining, conditions, exceptions


def extract_clauses(
    text: str,
    standard_id: str,
    section: str,
    source_file: str,
) -> list[NormativeClause]:
    """Extracts one `NormativeClause` per ALL-CAPS RFC2119 keyword found in
    `text`, split at sentence (and, within a sentence, multi-clause)
    boundaries. Returns an empty list for text with no capitalized
    keyword -- including text that merely mentions a lowercase spelling of
    one, which is the intended false-positive-avoidance behavior, not a
    bug.
    """
    clauses: list[NormativeClause] = []
    seq = 0

    for sentence in _split_sentences(text):
        for candidate in _split_multi_clause(sentence):
            match = _KEYWORD_PATTERN.search(candidate)
            if not match:
                continue
            strength = NormativeStrength.from_text(match.group(1))
            obligation_text, conditions, exceptions = _extract_condition_and_exception(candidate)

            seq += 1
            digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()[:10]
            clause_id = f"{standard_id.lower()}__{_slug(section)}__auto{seq:03d}__{digest}"

            clauses.append(
                NormativeClause(
                    clause_id=clause_id,
                    standard_id=standard_id,
                    section=section,
                    original_normative_strength=strength,
                    normalized_obligation=obligation_text,
                    affected_interface=(),
                    conditions=tuple(conditions),
                    exceptions=tuple(exceptions),
                    provenance=ClauseProvenance(
                        source_file=source_file,
                        source_section_heading=section,
                        quoted_text=candidate,
                    ),
                )
            )
    return clauses


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
