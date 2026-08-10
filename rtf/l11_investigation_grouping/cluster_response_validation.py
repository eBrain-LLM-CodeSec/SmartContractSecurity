"""Phase 9 of the grouped-investigation architecture: harness-side
validation of a clustered Codex response against
`ARM_G_CLUSTER_PROMPT_v1.md`'s own schema contract.

Prompt text is a request, never a guarantee (the same principle Phase 5's
`reasoning_rigor.py` already established for single-property PASS
verdicts) -- this module is the mechanical, harness-side enforcement
that a clustered response actually satisfies:

1. **Completeness**: exactly the expected `property_id` set, no missing,
   no duplicates, no unrecognized ids.
2. **No cluster-wide PASS**: structurally impossible to satisfy (1) with
   anything other than one real per-property entry -- but this module
   additionally flags byte-identical `reasoning` text repeated across
   multiple properties as a real, mechanical (not semantic-judgment)
   signal of undifferentiated, copy-pasted reasoning, i.e. implicit
   verdict inheritance.
3. **Counterexample-before-PASS, per property**: the same discipline
   Phase 5 enforces for single-property investigations, applied
   independently to EVERY property in the cluster -- a PASS on property
   A never exempts property B from its own counterexample requirement.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from rtf.l12_evaluation.metrics import ConformanceState

_MIN_MEANINGFUL_LENGTH = 15
"""Same threshold `reasoning_rigor.py` uses for the single-property
contract -- kept consistent across both schemas rather than picking a
different number for no reason."""

_DECISION_TO_CONFORMANCE = {
    "PASS": ConformanceState.PASS, "FAIL": ConformanceState.FAIL,
    "INCONCLUSIVE": ConformanceState.INCONCLUSIVE, "INSUFFICIENT_EVIDENCE": ConformanceState.INSUFFICIENT_EVIDENCE,
}


@dataclass(frozen=True)
class ClusterValidationResult:
    complete: bool
    missing_property_ids: tuple[str, ...]
    duplicate_property_ids: tuple[str, ...]
    unrecognized_property_ids: tuple[str, ...]
    entries_missing_property_id_field: int
    duplicated_reasoning_groups: tuple[tuple[str, ...], ...]
    """Groups of property_ids (each group size >=2) whose `reasoning`
    text is byte-identical -- a real, mechanical, no-judgment-call signal
    of undifferentiated/copy-pasted reasoning across properties.
    Non-empty groups do NOT make `complete=False` on their own (this is
    a quality WARNING, not a structural incompleteness) -- surfaced
    separately so a caller can decide how to treat it."""
    issues: tuple[str, ...]


def validate_cluster_response(expected_property_ids: list[str], response: dict | None) -> ClusterValidationResult:
    """Structural completeness check ONLY -- does not itself resolve
    per-property verdicts (see `resolve_property_verdicts` for that).
    """
    expected_set = set(expected_property_ids)

    if not isinstance(response, dict) or not isinstance(response.get("properties"), list):
        return ClusterValidationResult(
            complete=False, missing_property_ids=tuple(sorted(expected_set)),
            duplicate_property_ids=(), unrecognized_property_ids=(),
            entries_missing_property_id_field=0, duplicated_reasoning_groups=(),
            issues=("response_missing_or_malformed",),
        )

    entries = response["properties"]
    returned_ids: list[str | None] = []
    missing_id_field_count = 0
    for entry in entries:
        pid = entry.get("property_id") if isinstance(entry, dict) else None
        if pid is None:
            missing_id_field_count += 1
        returned_ids.append(pid)

    counts = Counter(pid for pid in returned_ids if pid is not None)
    duplicates = tuple(sorted(pid for pid, n in counts.items() if n > 1))
    returned_set = set(pid for pid in returned_ids if pid is not None)
    missing = tuple(sorted(expected_set - returned_set))
    unrecognized = tuple(sorted(returned_set - expected_set))

    # Byte-identical reasoning text across >=2 DISTINCT, recognized
    # properties -- grouped by exact text match.
    reasoning_groups: dict[str, list[str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        pid = entry.get("property_id")
        reasoning = entry.get("reasoning")
        if pid is None or not isinstance(reasoning, str) or not reasoning.strip():
            continue
        reasoning_groups.setdefault(reasoning, []).append(pid)
    duplicated_reasoning = tuple(
        tuple(sorted(pids)) for pids in reasoning_groups.values() if len(pids) >= 2
    )

    issues: list[str] = []
    if missing:
        issues.append(f"missing_property_ids:{missing}")
    if duplicates:
        issues.append(f"duplicate_property_ids:{duplicates}")
    if unrecognized:
        issues.append(f"unrecognized_property_ids:{unrecognized}")
    if missing_id_field_count:
        issues.append(f"entries_missing_property_id_field:{missing_id_field_count}")

    complete = not missing and not duplicates and not unrecognized and missing_id_field_count == 0

    return ClusterValidationResult(
        complete=complete, missing_property_ids=missing, duplicate_property_ids=duplicates,
        unrecognized_property_ids=unrecognized, entries_missing_property_id_field=missing_id_field_count,
        duplicated_reasoning_groups=duplicated_reasoning, issues=tuple(issues),
    )


def property_counterexample_is_sufficient(property_result: dict) -> tuple[bool, str | None]:
    """Per-property counterexample-before-PASS enforcement, applied to
    ARM_G_CLUSTER_PROMPT_v1.md's own schema fields
    (`counterexample_attempt`/`counterexample_result`) -- a distinct
    schema from the single-property `counterexample_search` object
    (`reasoning_rigor.py`), by the plan's own explicit field list, not
    accidentally different. Same non-placeholder-length discipline
    either way. Only meaningful when `verdict == "PASS"`; always
    (True, None) otherwise, mirroring `reasoning_rigor.py`'s own
    "not required for FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE" rule.
    """
    if property_result.get("verdict") != "PASS":
        return True, None
    attempt = property_result.get("counterexample_attempt")
    result = property_result.get("counterexample_result")
    if not isinstance(attempt, str) or len(attempt.strip()) < _MIN_MEANINGFUL_LENGTH:
        return False, "counterexample_attempt_too_thin"
    if not isinstance(result, str) or len(result.strip()) < _MIN_MEANINGFUL_LENGTH:
        return False, "counterexample_result_too_thin"
    return True, None


@dataclass(frozen=True)
class PropertyVerdict:
    conformance_state: ConformanceState
    reason: str | None
    """None for a genuine, sufficiently-rigorous decision; a machine-
    readable code otherwise -- same convention
    `codex_bridge.resolve_conformance_from_arm_g` already uses."""


def resolve_property_verdicts(response: dict) -> dict[str, PropertyVerdict]:
    """Resolves EVERY property entry present in `response["properties"]`
    to a `PropertyVerdict`, applying counterexample-before-PASS
    enforcement per property. Callers should check
    `validate_cluster_response`'s `complete` flag FIRST -- this function
    only resolves what's present, it does not itself detect missing
    property_ids (a missing property simply has no entry here at all,
    which is exactly what `validate_cluster_response` is for).
    """
    resolved: dict[str, PropertyVerdict] = {}
    for entry in response.get("properties", []):
        if not isinstance(entry, dict):
            continue
        pid = entry.get("property_id")
        if pid is None:
            continue
        verdict = entry.get("verdict")
        state = _DECISION_TO_CONFORMANCE.get(verdict)
        if state is None:
            resolved[pid] = PropertyVerdict(ConformanceState.INCONCLUSIVE, f"unknown_verdict:{verdict}")
            continue
        if state == ConformanceState.PASS:
            sufficient, reason = property_counterexample_is_sufficient(entry)
            if not sufficient:
                resolved[pid] = PropertyVerdict(ConformanceState.INCONCLUSIVE, f"insufficient_reasoning_rigor:{reason}")
                continue
        resolved[pid] = PropertyVerdict(state, None)
    return resolved
