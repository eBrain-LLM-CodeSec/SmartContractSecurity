"""Phase 5: harness-side enforcement that a PASS verdict was actually
backed by a genuine counterexample search, per ARM_G_PROMPT_v3.md's
`counterexample_search` schema field.

Prompt text alone is a request, not a guarantee -- a model can still
return `decision: PASS` with a missing or placeholder
`counterexample_search`. This module is the generic (not property-
specific, not per-req_id) check that catches that and downgrades the
verdict rather than silently trusting an unearned PASS, mirroring how
`codex_bridge.resolve_conformance_from_arm_g` already downgrades a
timeout or unparseable decision to INCONCLUSIVE with a machine-readable
reason instead of crashing or silently accepting a bad state.
"""
from __future__ import annotations

# A description this short cannot possibly convey a real, specific
# violation scenario or a real, specific check performed -- catches
# placeholder/lazy text ("none", "n/a", "ok", "-") without being so
# strict that a genuinely terse-but-real answer gets rejected. Chosen
# generically (a length heuristic, not keyword-matching on any
# requirement's own vocabulary), so this applies uniformly to every
# requirement, not tuned per property.
_MIN_MEANINGFUL_DESCRIPTION_LENGTH = 15


def counterexample_search_is_sufficient(final_decision: dict) -> tuple[bool, str | None]:
    """Returns (sufficient, failure_reason). `failure_reason` is None iff
    `sufficient` is True. Only meaningful for a PASS decision -- callers
    should not invoke this for FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE
    (ARM_G_PROMPT_v3.md's own schema note: counterexample_search is not
    required for those, since either the violation search already
    succeeded (FAIL) or no "is this satisfied" claim is being made at
    all).
    """
    search = final_decision.get("counterexample_search")
    if not isinstance(search, dict):
        return False, "counterexample_search_missing"
    if search.get("attempted") is not True:
        return False, "counterexample_search_not_attempted"

    scenario = search.get("violation_scenario_considered")
    checks = search.get("checks_performed")
    if not isinstance(scenario, str) or len(scenario.strip()) < _MIN_MEANINGFUL_DESCRIPTION_LENGTH:
        return False, "counterexample_search_scenario_too_thin"
    if not isinstance(checks, str) or len(checks.strip()) < _MIN_MEANINGFUL_DESCRIPTION_LENGTH:
        return False, "counterexample_search_checks_too_thin"

    if search.get("found_violation") is True:
        # A genuine internal inconsistency: the agent says it found a
        # violation but still returned an overall PASS. Never silently
        # trust the PASS in this case -- surfaced as its own reason so
        # it's distinguishable from "just didn't do the work" in metrics.
        return False, "counterexample_search_found_violation_but_decision_was_pass"

    return True, None
