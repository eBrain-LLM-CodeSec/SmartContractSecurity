"""Phase 1 of the grouped-investigation-architecture plan: extract the
current (G0_UNGROUPED) execution baseline from EXISTING pilot5_driver.py
artifacts, at zero additional cost -- no new Codex calls.

`extract_entry_baseline` reads one `entry_XX_*_stage.json`-shaped dict
(the per-entry summary `pilot5_driver.run_one_audit` already writes) and
computes the metrics the plan's Phase 1 asks for. `extract_audit_baseline`
does the same for a whole `pilot_summary.json`.

**Honest limitation, stated up front**: these historical artifacts (from
runs that predate this module) do not persist per-investigation token
counts or per-PASS evidence -- only `fail_details` (FAIL findings) carry
full evidence; PASS/INCONCLUSIVE/INSUFFICIENT_EVIDENCE investigations are
only reflected in the aggregate `stage_metrics.final_decisions` counts.
Token/cost figures below are therefore audit-level (`codex_cost`,
`wall_s`), not per-investigation, for this historical data. Runs going
forward (with `run_metadata` now attached, see
`rtf.l11_investigation_grouping.run_metadata`) can be extended to persist
richer per-investigation detail in a later phase if the cluster-size
study needs it; not required for this baseline.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EntryBaseline:
    entry: str
    requirements_considered: int
    requirements_applicable: int
    evidence_bundles_generated: int
    investigations_escalated: int
    """Number of DISTINCT requirements that reached a Codex investigation
    -- equals `bundles_escalated_to_codex` in stage_metrics."""
    investigation_instances: int
    """Number of actual Codex CALLS made. For every historical run (pre-
    instance-expansion) and for any G0_UNGROUPED run without expansion
    enabled, this equals `investigations_escalated` (1:1). Differs once
    instance expansion or grouping is active."""
    avg_properties_per_call: float
    """`investigations_escalated / investigation_instances` under the
    plan's own definition of a "property" as (for this baseline) one
    escalated requirement -- see the module docstring's note that G0's
    own "1 property = 1 call" identity makes this trivially 1.0 for
    every historical run, a useful sanity value once real property-level
    counts exist in a later phase."""
    codex_cost_usd: float
    wall_clock_s: float
    pass_count: int
    fail_count: int
    inconclusive_count: int
    insufficient_evidence_count: int
    exploration_failed_count: int
    """Requirements whose `codex_outcome_reasons` or
    `escalation_skip_reasons` name a crash/timeout/no-decision outcome --
    a partial reconstruction of `coverage_telemetry.CoverageState.
    EXPLORATION_FAILED` from what historical artifacts retain (full
    reconstruction needs per-requirement evidence, not persisted for
    non-FAIL entries in these older runs)."""
    grouping_policy: str | None
    """None for historical artifacts predating `run_metadata` (honest --
    "we don't know" is not the same as "G0_UNGROUPED", even though that
    would in practice be the right guess for every run before this
    field existed)."""


def _count_exploration_failures(skip_reasons: dict, outcome_reasons: dict) -> int:
    failed = set()
    for req_id, reason in (skip_reasons or {}).items():
        if "codex_invocation_crashed" in reason:
            failed.add(req_id)
    for req_id, reason in (outcome_reasons or {}).items():
        if reason.startswith(("codex_timeout", "codex_no_decision", "codex_unknown_decision")):
            failed.add(req_id)
    return len(failed)


def extract_entry_baseline(entry_stage: dict) -> EntryBaseline:
    """`entry_stage` is one entry's saved dict -- either the top-level
    content of an `entry_XX_*_stage.json` file, or one element of
    `pilot_summary.json`'s `per_entry_summaries` list (same shape).
    """
    sm = entry_stage["stage_metrics"]
    final_decisions = sm.get("final_decisions", {})
    escalated = sm.get("bundles_escalated_to_codex", 0)

    run_metadata = entry_stage.get("run_metadata")
    num_instances = entry_stage.get("num_investigation_instances")
    if num_instances is None:
        # Historical artifact predating this field -- the only
        # consistent value available is the escalation count itself
        # (1:1 for every run before instance expansion/grouping existed).
        num_instances = escalated

    avg_props_per_call = (escalated / num_instances) if num_instances else 0.0

    return EntryBaseline(
        entry=entry_stage.get("entry", "<unknown>"),
        requirements_considered=sm.get("requirements_considered", 0),
        requirements_applicable=sm.get("requirements_applicable", 0),
        evidence_bundles_generated=sm.get("evidence_bundles_generated", 0),
        investigations_escalated=escalated,
        investigation_instances=num_instances,
        avg_properties_per_call=avg_props_per_call,
        codex_cost_usd=entry_stage.get("codex_cost", 0.0),
        wall_clock_s=entry_stage.get("wall_s", 0.0),
        pass_count=final_decisions.get("PASS", 0),
        fail_count=final_decisions.get("FAIL", 0),
        inconclusive_count=final_decisions.get("INCONCLUSIVE", 0),
        insufficient_evidence_count=final_decisions.get("INSUFFICIENT_EVIDENCE", 0),
        exploration_failed_count=_count_exploration_failures(
            entry_stage.get("escalation_skip_reasons", {}), entry_stage.get("codex_outcome_reasons", {}),
        ),
        grouping_policy=(run_metadata or {}).get("grouping_policy"),
    )


@dataclass(frozen=True)
class AuditBaseline:
    audit_id: str
    scope_entries: int
    total_codex_cost_usd: float
    total_wall_clock_s: float
    entries: list = field(default_factory=list)
    """list[EntryBaseline], one per scope entry."""

    @property
    def total_investigations_escalated(self) -> int:
        return sum(e.investigations_escalated for e in self.entries)

    @property
    def total_investigation_instances(self) -> int:
        return sum(e.investigation_instances for e in self.entries)

    @property
    def total_fail_count(self) -> int:
        return sum(e.fail_count for e in self.entries)


def extract_audit_baseline(pilot_summary: dict) -> AuditBaseline:
    """`pilot_summary` is the parsed content of a real `pilot_summary.json`
    (as written by `pilot5_driver.run_one_audit`)."""
    entries = [extract_entry_baseline(e) for e in pilot_summary.get("per_entry_summaries", [])]
    total_wall = sum(e.wall_clock_s for e in entries)
    return AuditBaseline(
        audit_id=pilot_summary.get("audit_id", "<unknown>"),
        scope_entries=pilot_summary.get("scope_entries", len(entries)),
        total_codex_cost_usd=pilot_summary.get("total_codex_cost_usd", 0.0),
        total_wall_clock_s=total_wall,
        entries=entries,
    )
