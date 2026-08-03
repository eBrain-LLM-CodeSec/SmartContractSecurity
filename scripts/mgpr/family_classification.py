"""Deterministic, auditable P1/P2/P5 vulnerability-family classifier for the
MGPR feasibility study's dataset-construction labeling step (replaces
`run_feasibility_study.assign_expected_family`'s broad substring heuristic).

This is evaluation-methodology code, exactly like `citation_resolution.py` --
it decides which *label* a finding gets for the STUDY's own ground-truth
bookkeeping. It has no effect on MGPR's actual routing/gate/context behavior.

Why the old heuristic broke: `"reentran" in text.lower()` matches not only
genuine reentrancy prose but also the routine DEFENSIVE identifiers
`nonReentrant`, `noReentrant`, `reentrancyLock` -- these show up constantly
in pasted code excerpts, since audit writeups conventionally quote the
vulnerable function's full signature including its (irrelevant, defensive)
guard modifiers. Similarly `"cast" in text.lower()` matches "casting votes"
in governance-related findings that have nothing to do with type casts. A
hand audit (see the project's own root-cause validation) confirmed 8 of 9
apparent P2 "resolved but not fired" cases were mislabeled this way, plus
one confirmed P5 false positive from the "casting votes" collision.

Design, per the task's own required structure:

1. Text is cleaned before matching: fenced code blocks, inline code spans,
   URLs, and mitigation/remediation sections are stripped
   (`_clean_for_classification`). Known defensive identifiers
   (`nonReentrant`, `reentrancyLock`, etc.) and known false-positive phrases
   ("casting vote(s)") are separately stripped and RECORDED (not silently
   discarded) as `excluded_matches`, so a reviewer can see exactly what was
   filtered out and why.
2. Matching proceeds over ranked source fields -- title, then description,
   then the cleaned body (impact/mechanism prose folds into the cleaned
   body here: this implementation does not build a separate impact-section
   extractor beyond the mitigation-section cut described above, so "prose
   sections describing impact/mechanism" and "full writeup after excluding
   irrelevant sections" are the same cleaned text in this pass -- a
   documented simplification, not a missing feature silently dropped).
3. Only a curated set of STRONG, compound, low-ambiguity phrases can
   directly assign a family (e.g. "narrowing cast", "downcast",
   "reentrancy attack", "missing access control"). Single generic words
   ("authoriz", "call", "precision", "cast") never assign a family alone --
   they only ever contribute to a WEAK signal, which produces UNCERTAIN
   (not a forced family) when no strong evidence exists anywhere in the
   text.
4. Every classification records: source_field, matched_rule, matched_text,
   excluded_matches, and a confidence tier ("strong" | "weak" | "none").
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class FamilyOutcome(str, Enum):
    P1_AUTHORIZATION = "P1_AUTHORIZATION"
    P2_REENTRANCY = "P2_REENTRANCY"
    P5_ARITHMETIC_PRECISION = "P5_ARITHMETIC_PRECISION"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNCERTAIN = "UNCERTAIN"


_FAMILIES = (FamilyOutcome.P2_REENTRANCY, FamilyOutcome.P5_ARITHMETIC_PRECISION, FamilyOutcome.P1_AUTHORIZATION)


@dataclass(frozen=True)
class ExcludedMatch:
    rule: str
    text: str

    def as_dict(self) -> dict:
        return {"rule": self.rule, "text": self.text}


@dataclass(frozen=True)
class FamilyClassification:
    outcome: FamilyOutcome
    source_field: str | None        # "title" | "description" | "cleaned_body" | None
    matched_rule: str | None        # the specific phrase/pattern name that matched
    matched_text: str | None        # the literal substring that matched, with surrounding context
    excluded_matches: list[ExcludedMatch] = field(default_factory=list)
    confidence: str = "none"        # "strong" | "weak" | "none"

    def as_dict(self) -> dict:
        return {
            "outcome": self.outcome.value, "source_field": self.source_field,
            "matched_rule": self.matched_rule, "matched_text": self.matched_text,
            "excluded_matches": [m.as_dict() for m in self.excluded_matches],
            "confidence": self.confidence,
        }


# --- text cleaning -----------------------------------------------------------

_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_URL_RE = re.compile(r"https?://\S+")
# A "heading-like" line: a markdown ATX heading, a bold-only line, or a short
# plain-text line (no trailing period, under ~60 chars) matching a known
# section name -- covers both the `### Recommended Mitigation` style and the
# plain `Recommended Mitigation` style actually used across EVMbench
# findings (confirmed by direct sampling of real finding writeups).
_MITIGATION_HEADING_RE = re.compile(
    r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?\*{0,2}(recommended mitigation|mitigation|remediation|recommendation)s?\*{0,2}[ \t]*:?[ \t]*$"
)
_NEXT_HEADING_RE = re.compile(r"(?m)^[ \t]*(?:#{1,6}[ \t]+\S|\*\*[^\n*]+\*\*[ \t]*$|[A-Z][A-Za-z ]{2,40}[ \t]*:?[ \t]*$)")


def _strip_mitigation_section(text: str) -> str:
    """Cuts the text from the first mitigation/remediation heading to the
    next heading (or, if none follows, to the end of the text) -- mitigation
    sections conventionally appear near/at the end of a finding writeup, so
    "to the end" is the common case; a mitigation section followed by more
    unrelated prose is a known, documented residual risk, not silently
    claimed to be handled perfectly."""
    m = _MITIGATION_HEADING_RE.search(text)
    if m is None:
        return text
    rest = text[m.end():]
    nxt = _NEXT_HEADING_RE.search(rest)
    if nxt is None:
        return text[: m.start()]
    return text[: m.start()] + rest[nxt.start():]


def _strip_urls_and_code(text: str) -> str:
    text = _FENCED_CODE_RE.sub(" ", text)
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    return text


def clean_for_classification(text: str) -> str:
    """Full cleaning pipeline: fenced code, inline code, URLs, then the
    mitigation/remediation section. Order matters -- mitigation-section
    detection runs on text that may still contain code, since the heading
    regex only matches whole short lines and is unaffected by surrounding
    code blocks."""
    text = _strip_mitigation_section(text)
    text = _strip_urls_and_code(text)
    return text


# --- denylist stripping (recorded, not silently discarded) ------------------

# Defensive reentrancy-guard identifiers: matched WITHOUT a leading \b (since
# `nonReentrant`/`noReentrant` have no word-boundary between their `non`/`no`
# prefix and `Reentrant` -- both are word characters) but the alternation
# itself is anchored at both ends by \b so it only ever matches a real,
# complete identifier token, never a mid-word coincidence.
_P2_DENYLIST_RE = re.compile(
    r"\b(?:non-?[Rr]eentrant\w*|no-?[Rr]eentrant\w*|[Rr]eentranc?y-?[Ll]ock\w*|"
    r"[Rr]eentranc?y-?[Gg]uard\w*|whenNotReentered|notEntered|reentrancyStatus|reentrancy_?status)\b"
)

_P5_DENYLIST_RE = re.compile(
    r"\bcast(?:ing)?\s+(?:a\s+|an?\s+|their\s+|his\s+|her\s+|its\s+)?votes?\b|\bvotes?\s+cast(?:ing)?\b",
    re.IGNORECASE,
)


def _strip_denylist(text: str, pattern: re.Pattern, rule_name: str, excluded: list[ExcludedMatch]) -> str:
    def _record(m: re.Match) -> str:
        excluded.append(ExcludedMatch(rule=rule_name, text=m.group(0)))
        return " "
    return pattern.sub(_record, text)


# --- family phrase rules -----------------------------------------------------
# Each family has a STRONG list (compound, low-ambiguity phrases -- these
# alone can assign the family) and a WEAK list (single generic roots -- these
# only ever contribute to an UNCERTAIN outcome, per the task's explicit
# instruction not to let bare "authorization"/"call"/"precision" assign a
# family without evidence of the actual mechanism).

_P2_STRONG = [
    "reentrancy", "re-entrancy", "reentrant attack", "reentrant call", "reentering",
    "recursive call before", "cross-function reentrancy", "read-only reentrancy",
    "reenter", "re-enter",
]
_P2_WEAK: list[str] = []  # "reentran" root alone, post-denylist, is already specific enough to be strong

_P5_STRONG = [
    "downcast", "narrowing cast", "narrowing conversion", "unsafe cast", "type cast",
    "explicit cast", "truncat", "precision loss", "loses precision", "loss of precision",
    "rounding error", "rounding down", "rounding up", "integer overflow", "integer underflow",
    "silently truncat", "cast to uint", "cast from uint", "casting to uint", "casting from uint",
    # deliberately "convert from"/"convert to", NOT "convert from uint" --
    # confirmed live against a real finding (pooltogether/H-02: "convert
    # from `uint256` to `uint96`") that inline-code stripping removes the
    # backtick-wrapped type name entirely, breaking any compound phrase
    # that requires it to stay adjacent. "convert from"/"convert to" are
    # still specific enough in audit-report prose to stand alone.
    "convert from", "convert to", "downcasting", "overflow", "underflow",
]
_P5_WEAK = ["cast", "precision", "round"]

_P1_STRONG = [
    "access control", "missing authorization", "lacks authorization", "without authorization",
    "unauthorized", "any user can call", "anyone can call", "callable by anyone",
    "no permission check", "lacks a permission check", "missing permission check",
    "missing role check", "no role check", "missing onlyowner", "no ownership check",
    "no caller validation", "lacks caller validation", "unrestricted access",
    "privilege escalation", "spoof the lender", "spoofing the lender",  # domain-specific but still a compound signal
]
# NOTE: "call" is deliberately NOT included here even though the task cites
# it as an example generic word -- unlike "authoriz"/"permission"/
# "privilege"/"role" (topically tied to access control even in isolation),
# "call" is so common in smart-contract prose (any function invocation) that
# including it would surface UNCERTAIN for nearly every finding regardless
# of subject, defeating the point of a "no evidence -> weak/none" signal
# rather than strengthening it. The protection the task asks for --
# "call" alone must never assign P1 -- holds regardless, since "call" was
# never in the STRONG list either.
_P1_WEAK = ["authoriz", "permission", "privilege", "role"]

_RULES: dict[FamilyOutcome, tuple[list[str], list[str]]] = {
    FamilyOutcome.P2_REENTRANCY: (_P2_STRONG, _P2_WEAK),
    FamilyOutcome.P5_ARITHMETIC_PRECISION: (_P5_STRONG, _P5_WEAK),
    FamilyOutcome.P1_AUTHORIZATION: (_P1_STRONG, _P1_WEAK),
}


def _find_phrase(text: str, phrases: list[str]) -> tuple[str, str] | None:
    """Returns (phrase, matched_text_with_context) for the first phrase (in
    list order) found in `text`, case-insensitively, or None. Anchored at a
    leading word boundary (but not trailing, so prefix roots like "truncat"
    still match "truncated"/"truncating") -- a plain substring search
    (the original implementation) let "round" match inside "around" and
    "cast" match inside "broadcast"/"forecast", both confirmed live as real
    false-positive sources during this classifier's own validation pass."""
    lowered = text.lower()
    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase)
        m = re.search(pattern, lowered)
        if m is not None:
            idx = m.start()
            start = max(0, idx - 20)
            end = min(len(text), idx + len(phrase) + 20)
            return phrase, text[start:end].strip()
    return None


def classify_family(
    title: str | None, description: str | None, full_text: str | None,
) -> FamilyClassification:
    """Classifies one finding into a P1/P2/P5 family, NOT_APPLICABLE, or
    UNCERTAIN. `title`/`description` are matched as-is (already short,
    rarely contain code); `full_text` (the finding's own findings/*.md, when
    available) is run through the full cleaning pipeline first."""
    excluded: list[ExcludedMatch] = []

    fields: list[tuple[str, str]] = []
    if title:
        fields.append(("title", title))
    if description:
        fields.append(("description", description))
    if full_text:
        cleaned = clean_for_classification(full_text)
        cleaned = _strip_denylist(cleaned, _P2_DENYLIST_RE, "defensive_reentrancy_identifier", excluded)
        cleaned = _strip_denylist(cleaned, _P5_DENYLIST_RE, "casting_votes_governance_phrase", excluded)
        fields.append(("cleaned_body", cleaned))

    # also scan title/description for the same denylist phrases, in case a
    # short description itself says e.g. "even with nonReentrant in place" --
    # rare, but consistent with "excluded from primary classification"
    # applying everywhere, not only to the full writeup.
    scan_fields: list[tuple[str, str]] = []
    for name, text in fields:
        if name == "cleaned_body":
            scan_fields.append((name, text))
            continue
        stripped = _strip_denylist(text, _P2_DENYLIST_RE, "defensive_reentrancy_identifier", excluded)
        stripped = _strip_denylist(stripped, _P5_DENYLIST_RE, "casting_votes_governance_phrase", excluded)
        scan_fields.append((name, stripped))

    # pass 1: strong phrases, field-priority order (title -> description ->
    # cleaned_body), family-priority order within each field
    # (P2 -> P5 -> P1, matching the original heuristic's documented order).
    for field_name, text in scan_fields:
        for family in _FAMILIES:
            strong, _weak = _RULES[family]
            hit = _find_phrase(text, strong)
            if hit is not None:
                phrase, matched_text = hit
                return FamilyClassification(
                    outcome=family, source_field=field_name, matched_rule=phrase,
                    matched_text=matched_text, excluded_matches=excluded, confidence="strong",
                )

    # pass 2: weak phrases -- never assign a family, only surface UNCERTAIN
    # with the evidence recorded, per the task's explicit instruction.
    for field_name, text in scan_fields:
        for family in _FAMILIES:
            _strong, weak = _RULES[family]
            hit = _find_phrase(text, weak)
            if hit is not None:
                phrase, matched_text = hit
                return FamilyClassification(
                    outcome=FamilyOutcome.UNCERTAIN, source_field=field_name, matched_rule=f"{family.value}:{phrase}",
                    matched_text=matched_text, excluded_matches=excluded, confidence="weak",
                )

    return FamilyClassification(
        outcome=FamilyOutcome.NOT_APPLICABLE, source_field=None, matched_rule=None,
        matched_text=None, excluded_matches=excluded, confidence="none",
    )
