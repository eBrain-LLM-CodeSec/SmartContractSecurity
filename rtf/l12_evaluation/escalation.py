"""L12 escalation rule: decides whether a bounded L8 judgment result gets
handed to the graph-gated Codex investigation path (Arm G) instead of
being accepted as final.

Deliberately reuses L8's OWN existing decision/confidence signals rather
than introducing any new relevance/sufficiency classifier -- the pilot
spec this module implements explicitly forbids that. `ConformanceState`
is imported from `metrics.py`, not redefined; `confidence` is read
straight off the raw judgment dict L8 already returns
(`judgment_layer.build_judgment_prompt`'s schema: "HIGH"/"MEDIUM"/"LOW").
"""
from __future__ import annotations

from rtf.l12_evaluation.metrics import ConformanceState

_ESCALATE_ON_STATES = {ConformanceState.INSUFFICIENT_EVIDENCE, ConformanceState.INCONCLUSIVE}


def decide_escalation(conformance_state: ConformanceState | None, confidence: str | None) -> bool:
    """Escalate to Codex iff the bounded judgment's resolved
    `ConformanceState` is INSUFFICIENT_EVIDENCE or INCONCLUSIVE, OR its
    confidence is LOW. A HIGH/MEDIUM-confidence PASS or FAIL is accepted
    as final without escalation -- the bounded call already had enough to
    decide, and a real investigation Codex call costs real time/money
    (see the PoolTogether experiments: ~$0.14, ~6 minutes for one
    candidate) that shouldn't be spent on requirements L8 already
    resolved confidently.

    `conformance_state=None` (the requirement was never actually judged
    -- e.g. an operational failure, or a DETERMINISTIC_COMPLETE
    unconditioned PASS that never reached L8 at all) is not eligible for
    escalation: there is no bounded judgment to be dissatisfied with.
    """
    if conformance_state is None:
        return False
    if conformance_state in _ESCALATE_ON_STATES:
        return True
    return confidence == "LOW"
