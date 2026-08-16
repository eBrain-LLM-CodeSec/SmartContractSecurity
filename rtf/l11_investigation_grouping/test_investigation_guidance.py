"""Unit tests for rtf.l11_investigation_grouping.investigation_guidance
(RTF_V3_REDESIGN_PLAN.md Phase 6). Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_investigation_guidance
"""
from __future__ import annotations

import re
import sys

from rtf.l11_investigation_grouping.investigation_guidance import (
    GUIDANCE_BY_REQ_ID, guidance_for_property,
)
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _prop(**overrides) -> PropertyMetadata:
    base = dict(
        property_id="p1", requirement_id="req-a", requirement_level="Q",
        requirement_semantic_intent="Test", property_text="Tested code MUST do the thing.",
        target_contract="Vault", target_function="withdraw",
        source_provenance="req_id=req-a; spec_section=5.3",
    )
    base.update(overrides)
    return PropertyMetadata(**base)


# --- guidance_for_property: applicability -----------------------------

def test_own_req_id_match_returns_the_cross_boundary_guidance():
    g = guidance_for_property(_prop(requirement_id="req-2-block-data-misuse"))
    check("guidance returned", g is not None, g)
    check("mentions callee semantics", "CALLEE" in g, g)


def test_own_req_id_match_returns_input_validation_guidance():
    g = guidance_for_property(_prop(requirement_id="req-3-all-valid-inputs"))
    check("guidance returned", g is not None, g)
    check("distinguishes valid-input correctness from invalid-input rejection", "REJECTION OF INVALID INPUT" in g, g)


def test_own_req_id_match_returns_gas_growth_guidance():
    g = guidance_for_property(_prop(requirement_id="req-3-enough-gas"))
    check("guidance returned", g is not None, g)
    check("mentions pruning/removal path", "removal path" in g, g)
    g2 = guidance_for_property(_prop(requirement_id="req-3-protect-gas"))
    check("req-3-protect-gas gets the same guidance family", g2 == g, g2)


def test_parent_requirement_id_match_returns_guidance_for_a_semantic_property():
    """A semantic property (Phase 4) whose OWN requirement_id is a
    synthetic hash but whose parent_requirement_id links to a real
    guidance-bearing corpus requirement must still get the guidance --
    this is the whole point of anchoring semantic properties to a
    parent (Phase 4) feeding Phase 6."""
    g = guidance_for_property(_prop(
        requirement_id="semantic__accounting__abc123", requirement_level="SEMANTIC",
        parent_requirement_id="req-3-enough-gas",
    ))
    check("guidance returned via parent link", g is not None, g)
    check("is the gas-growth guidance", "removal path" in g, g)


def test_own_req_id_takes_priority_over_parent_when_both_would_match():
    g = guidance_for_property(_prop(
        requirement_id="req-2-block-data-misuse", parent_requirement_id="req-3-enough-gas",
    ))
    check("own req_id's guidance wins over the (nonsensical here) parent link", "CALLEE" in g, g)


# --- guidance_for_property: non-applicability (task brief requirement) -

def test_unrelated_requirement_gets_no_guidance():
    g = guidance_for_property(_prop(requirement_id="req-2-overflow-underflow"))
    check("no guidance for a requirement with no entry", g is None, g)


def test_no_parent_and_unmatched_own_id_gets_no_guidance():
    g = guidance_for_property(_prop(
        requirement_id="semantic__state_consistency__abc123", requirement_level="SEMANTIC",
        parent_requirement_id=None,
    ))
    check("no guidance when neither own id nor parent id matches", g is None, g)


def test_parent_requirement_id_with_no_matching_entry_gets_no_guidance():
    g = guidance_for_property(_prop(
        requirement_id="semantic__access__abc123", requirement_level="SEMANTIC",
        parent_requirement_id="req-2-avoid-readonly-reentrancy",
    ))
    check("no guidance when the parent link itself has no guidance entry", g is None, g)


# --- provenance / anti-benchmark-overfitting checks --------------------

_BANNED_BENCHMARK_IDENTIFIERS = (
    "canto", "forte", "phi", "cred.sol", "lendingledger", "gaugecontroller",
    "updatecuratorsharebalance", "ln.sol", "float128", "liquid-ron", "liquidron",
    "tempo-feeamm", "feeamm",
)


def test_guidance_text_never_names_a_benchmark_target():
    """Task brief constraint #1: every guidance block must trace to
    official EthTrust text / generic Solidity semantics, never to an
    EVMbench target/finding. Mechanical check, not just a claim."""
    for req_id, text in GUIDANCE_BY_REQ_ID.items():
        lowered = text.lower()
        for banned in _BANNED_BENCHMARK_IDENTIFIERS:
            check(f"{req_id} guidance does not name benchmark identifier {banned!r}", banned not in lowered, text)


def test_every_guidance_entry_key_is_a_real_agent_required_corpus_req_id():
    from rtf.l12_evaluation.registry import AGENT_REQUIRED_REQ_IDS, REGISTRY
    for req_id in GUIDANCE_BY_REQ_ID:
        check(f"{req_id} is a real registered requirement", req_id in REGISTRY, req_id)
        check(f"{req_id} is AGENT_REQUIRED (guidance is for the agent, not a deterministic-only req)", req_id in AGENT_REQUIRED_REQ_IDS, req_id)


def test_guidance_blocks_are_short_not_a_be_more_thorough_dump():
    """Task brief constraint #3: no blanket "be more thorough" prompt
    expansion. Each block should be compact -- a handful of bullet
    lines, not a page."""
    for req_id, text in GUIDANCE_BY_REQ_ID.items():
        line_count = len([ln for ln in text.splitlines() if ln.strip()])
        check(f"{req_id} guidance is compact (<=10 non-empty lines)", line_count <= 10, (req_id, line_count))


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
