"""L8: repeated-run stability testing.

Per the plan: run the same judgment component N times on a representative
subset, measure decision-flip rate, report before trusting any single-run
result elsewhere. This module only aggregates a list of already-produced
judgment dicts -- it doesn't call any model itself, so it's testable with
synthetic data independent of live LLM access (see selftest.py).
"""
from __future__ import annotations

from collections import Counter


def compute_stability(judgments: list[dict]) -> dict:
    """`judgments`: repeated-run outputs for the SAME input, each already
    schema-validated. Returns flip rate as raw counts (plan finalization-
    patch rule: never report a bare percentage without numerator/denominator)
    plus the modal decision and its share."""
    if len(judgments) < 2:
        raise ValueError("stability testing requires at least 2 runs to be meaningful")

    decisions = [j["decision"] for j in judgments]
    counts = Counter(decisions)
    modal_decision, modal_count = counts.most_common(1)[0]
    n = len(decisions)
    flips = n - modal_count

    return {
        "n_runs": n,
        "decision_counts": dict(counts),
        "modal_decision": modal_decision,
        "modal_count": modal_count,
        "flip_count": flips,
        "flip_rate_fraction": flips / n,
        "flip_rate_display": f"{flips}/{n}",
    }
