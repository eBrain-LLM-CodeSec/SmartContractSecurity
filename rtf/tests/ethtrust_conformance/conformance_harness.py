"""RTF_V3_REDESIGN_PLAN.md Phase 7: reusable harness for the EthTrust
conformance suite.

Two tiers, both real code paths -- nothing here is a second, parallel
implementation of routing/resolution:

**Tier 1 (fully real, $0, no mocking at all)**: compiles a fixture and
runs the REAL `run_rtf.run_rtf` routing pipeline. For a requirement
whose predicate cleanly distinguishes vulnerable from safe (or whose own
DETERMINISTIC_COMPLETE/"unconditioned" classification resolves a verdict
without any agent step), this alone gives a genuine FAIL/PASS/
NOT_APPLICABLE result -- see `run_tier1`.

**Tier 2 (mocked-agent verdict resolution)**: for a requirement that
stays APPLICABLE with `conformance_state=None` (genuinely pending a real
Codex investigation, per `run_rtf.py`'s own documented semantics), this
runs the REAL `live_runner.build_property_pool` (so Phase 3/4/5/6's
context/parent-linking/guidance machinery is all genuinely exercised)
to get the real `PropertyMetadata` for the fixture, then resolves a
SCRIPTED verdict response through the REAL `cluster_response_validation.
resolve_property_verdicts` -- the same function a live Codex response
would flow through. Only the "what would the agent conclude" step is
faked; every structural/context-assembly/verdict-resolution step is
real. This is the "deterministic/mock LLM behavior... for CI" the task
brief explicitly calls for -- a `--live` mode that replaces the mock
with a real Codex call is future work, not built here (also per the
brief: keep live-agent tests separate).
"""
from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from rtf.l11_investigation_grouping.cluster_response_validation import resolve_property_verdicts
from rtf.l11_investigation_grouping.live_runner import build_property_pool
from rtf.l12_evaluation.metrics import ApplicabilityState, ConformanceState
from rtf.l12_evaluation.pipeline_e2e import CORPUS_PATH
from rtf.l12_evaluation.run_rtf import build_context_for_evmbench_target, load_unconditioned_map, run_rtf

FIXTURES_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Tier1Result:
    applicability_state: ApplicabilityState
    conformance_state: ConformanceState | None
    evidence_locations: tuple[str, ...]
    properties: tuple  # tuple[PropertyMetadata, ...] -- only populated when APPLICABLE + pending


def run_tier1(fixture_path: Path, req_id: str, solc_version: str = "0.8.20") -> Tier1Result:
    """Compiles `fixture_path` standalone and runs it through the REAL
    routing pipeline (`run_rtf.run_rtf`), returning that requirement's
    real, un-mocked result. If the result is APPLICABLE with
    `conformance_state is None` (pending investigation), also runs the
    REAL `build_property_pool` so Tier 2 has genuine `PropertyMetadata`
    to resolve a mocked verdict against.
    """
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        entry = tmp / "Entry.sol"
        entry.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")
        ctx, compile_error = build_context_for_evmbench_target(entry, tmp, solc_version)
        if ctx.slither is None:
            raise RuntimeError(f"fixture failed to compile: {fixture_path} -- {compile_error}")
        unconditioned_map = load_unconditioned_map(CORPUS_PATH)
        run, _raw = run_rtf(ctx, "ethtrust-conformance", unconditioned_map)
        result = run.routed[req_id]

        properties: tuple = ()
        if result.applicability_state == ApplicabilityState.APPLICABLE and result.conformance_state is None:
            properties = tuple(
                p for p in build_property_pool(run.routed, tmp, pg=None, slither=ctx.slither)
                if p.requirement_id == req_id
            )

        return Tier1Result(
            applicability_state=result.applicability_state,
            conformance_state=result.conformance_state,
            evidence_locations=tuple(e.location for e in result.evidence),
            properties=properties,
        )


def mock_verdict_response(property_id: str, verdict: str, *, parent_obligation_check: str | None = None) -> dict:
    """A well-formed, schema-complete mocked verdict entry -- passes
    both the counterexample-search-sufficiency gate AND (when a
    property has a linked parent requirement) the Phase 4 parent-
    obligation-check gate, so the ONLY thing under test is whether the
    resolver correctly turns a genuine PASS/FAIL opinion into the
    matching `ConformanceState` -- not an artifact of a thin/placeholder
    mocked response tripping a rigor downgrade for the wrong reason.
    """
    entry = {
        "property_id": property_id,
        "verdict": verdict,
        "evidence": f"(mocked, deterministic CI fixture) real code inspection supports {verdict}",
        "files_read": ["Entry.sol"],
        "counterexample_attempt": (
            "Considered whether an adversarial caller/input could make the stated "
            "property fail despite the code's apparent structure."
        ),
        "counterexample_result": (
            "Confirmed the property holds under that scenario." if verdict == "PASS"
            else "Confirmed the property fails under that scenario, with a concrete trigger."
        ),
        "reasoning": f"(mocked, deterministic CI fixture) scripted {verdict} verdict for conformance testing.",
        "vulnerable_location": None if verdict == "PASS" else "Entry.sol",
        "confidence": "HIGH",
    }
    if parent_obligation_check is not None:
        entry["parent_obligation_check"] = parent_obligation_check
    return entry


def run_tier2(tier1: Tier1Result, verdict: str) -> ConformanceState:
    """Resolves a SCRIPTED `verdict` ("PASS"/"FAIL") for the single
    property `tier1.properties` names, through the REAL
    `resolve_property_verdicts` (the same function the live cluster
    pipeline uses). Requires exactly one property -- callers pick which
    one via `tier1.properties` filtering before calling this, matching
    the real per-property independence the architecture guarantees.
    """
    if len(tier1.properties) != 1:
        raise ValueError(f"run_tier2 expects exactly one property, got {len(tier1.properties)}: {tier1.properties}")
    prop = tier1.properties[0]
    parent_check = None
    if prop.parent_requirement_id:
        parent_check = f"Parent requirement {prop.parent_requirement_id}'s obligation was also evaluated and is consistent with this verdict."
    response = {"properties": [mock_verdict_response(prop.property_id, verdict, parent_obligation_check=parent_check)]}
    resolved = resolve_property_verdicts(response, {prop.property_id: prop})
    return resolved[prop.property_id].conformance_state
