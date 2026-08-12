"""L12 <-> Arm G (graph-gated Codex investigation) bridge.

Two directions:
  - INPUT: given one requirement's evidence for one candidate, build the
    5 inputs `arm_g_codex.build_arm_g_prompt` needs, reusing the exact
    same L2 context-bundle renderer and evidence-bundle renderer the
    bounded L8 call already uses (`judgment_layer.render_context_bundle_
    text`, `evidence_ranking.*`) -- so Codex sees the identical
    requirement context and evidence L8 saw, not a second, possibly-
    drifted rendering.
  - OUTPUT: given an `ArmGResult`, resolve it onto the same
    `ConformanceState` enum `judge_with_l8.resolve_conformance_from_
    judgment` uses, so escalated and non-escalated requirements merge
    into one uniform result set downstream.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from rtf.l12_evaluation.evidence_ranking import (
    apply_evidence_budget, build_evidence_bundles, rank_evidence, render_bundles_for_prompt,
)
from rtf.l12_evaluation.metrics import ConformanceState, RoutedRequirementResult
from rtf.l8_llm_judgment_layer.bundle_agent_experiment.reasoning_rigor import counterexample_search_is_sufficient
from rtf.l8_llm_judgment_layer.judgment_layer import render_context_bundle_text

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLES_DIR = REPO_ROOT / "rtf" / "l2_context_bundles"
CORPUS_PATH = REPO_ROOT / "rtf" / "l1_corpus" / "requirement_corpus.json"


@lru_cache(maxsize=1)
def corpus_by_req_id() -> dict[str, dict]:
    data = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    return {r["req_id"]: r for r in data["requirements"]}


@dataclass(frozen=True)
class CodexPromptInputs:
    requirement_text: str
    context_bundle_text: str
    candidate_location: str
    evidence_bundle_text: str
    unresolved_facts: list[str]


def build_codex_prompt_inputs(
    req_id: str,
    candidate_location: str,
    result: RoutedRequirementResult,
    repo_root: Path | None,
    open_questions: list[str] | None = None,
    max_bundles: int = 30,
    bundle_record: dict | None = None,
) -> CodexPromptInputs:
    """Builds the agent's prompt inputs for one (req_id, candidate) pair.
    `open_questions`, when the caller has some (e.g. from an optional
    bounded-L8 pre-pass, if one is ever wired back in), populates
    `unresolved_facts` directly rather than inventing a new "what's
    missing" heuristic. As of the "revisit the RTF architecture" redesign,
    `pipeline_e2e.py`'s main loop no longer runs a bounded pass first, so
    this is normally `None` -- the agent is expected to discover its own
    open questions via full repository exploration, not inherit them from
    a prior bounded judgment.

    `context_bundle_text` comes from the requirement's real L2 bundle
    (`rtf/l2_context_bundles/<req_id>.json`) via the same renderer L8's
    own prompt uses (`judgment_layer.render_context_bundle_text`) -- this
    is real, wired data, not a gap: L2 bundles exist and are already
    loaded by `judge_with_l8.judge_result` for every requirement with a
    bundle file.

    `bundle_record`, when given, is used directly instead of reading
    `rtf/l2_context_bundles/<req_id>.json` from disk -- the seam
    `rtf.standards.routing.build_standards_routed_requirements` uses to
    feed a generated (ERC-standard-derived) requirement's in-memory,
    same-shaped bundle through unchanged, with no L2 bundle FILE ever
    needing to exist for a dynamically-generated req_id. Every existing
    call site omits this (defaults to `None`) and behaves exactly as
    before -- purely additive.

    Raises FileNotFoundError if no L2 bundle exists for req_id AND no
    `bundle_record` override was given (mirrors `judge_with_l8.judge_
    result`'s own `ENVIRONMENT_FAILURE` case -- callers should catch this
    the same way, not let it propagate as an unhandled crash for one
    candidate).
    """
    if bundle_record is None:
        bundle_path = BUNDLES_DIR / f"{req_id}.json"
        if not bundle_path.exists():
            raise FileNotFoundError(f"no L2 context bundle for {req_id!r} at {bundle_path}")
        bundle_record = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle = bundle_record["bundle"]

    # NOTE: the corpus now also carries `explanatory_text` (the spec's
    # informative prose following the normative sentence -- see
    # PARSING_NOTES.md's "Explanatory/informative content extraction"
    # section) at `corpus_by_req_id()[req_id]["explanatory_text"]`. Not
    # wired into this (old, non-grouped) prompt path yet -- deliberately
    # deferred, since this pipeline has no existing seam for it (unlike
    # `context_artifacts.generate_requirement_context_md`'s pre-built
    # `explanatory_text` param, already wired for the L11 grouped
    # pipeline via `live_runner.py`). Available for a future pass.
    requirement_text = corpus_by_req_id().get(req_id, {}).get("normative_text", bundle["self"])
    context_bundle_text = render_context_bundle_text(bundle)

    ranked = rank_evidence(list(result.evidence), repo_root)
    bundles = build_evidence_bundles(req_id, requirement_text, ranked)
    budget = apply_evidence_budget(bundles, max_bundles)
    evidence_bundle_text = render_bundles_for_prompt(budget.included, omitted_count=len(budget.excluded))

    return CodexPromptInputs(
        requirement_text=requirement_text,
        context_bundle_text=context_bundle_text,
        candidate_location=candidate_location,
        evidence_bundle_text=evidence_bundle_text,
        unresolved_facts=list(open_questions or []),
    )


# --- ArmGResult -> ConformanceState -----------------------------------------

_DECISION_TO_CONFORMANCE = {
    "PASS": ConformanceState.PASS,
    "FAIL": ConformanceState.FAIL,
    "INCONCLUSIVE": ConformanceState.INCONCLUSIVE,
    "INSUFFICIENT_EVIDENCE": ConformanceState.INSUFFICIENT_EVIDENCE,
}


@dataclass(frozen=True)
class CodexJudgmentOutcome:
    conformance_state: ConformanceState
    reason: str | None  # None for a real decision; a machine-readable code otherwise
    reasoning_summary: str | None


def resolve_conformance_from_arm_g(final_decision: dict | None, timed_out: bool) -> CodexJudgmentOutcome:
    """Maps an `ArmGResult` onto the same `ConformanceState` values
    `judge_with_l8.resolve_conformance_from_judgment` uses for the
    bounded path, so escalated and non-escalated requirements merge into
    one uniform result type downstream (report generation, metrics).

    A timeout or an unparseable/missing final decision both resolve to
    INCONCLUSIVE (a legitimate outcome per the plan, not a crash) with an
    explicit machine-readable `reason` ("codex_timeout" /
    "codex_no_decision") attached -- this must stay visible in stage
    metrics, never silently collapsed into a bare INCONCLUSIVE
    indistinguishable from a real one the model itself returned.

    A `decision: PASS` is additionally checked against
    `reasoning_rigor.counterexample_search_is_sufficient` (see
    ARM_G_PROMPT_v3.md) -- a PASS without a genuine, non-placeholder
    counterexample search is downgraded to INCONCLUSIVE with reason
    `insufficient_reasoning_rigor:<specific code>`, never silently
    trusted. FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE decisions are
    untouched by this check (the prompt's own schema note: the
    counterexample field is not required for those).
    """
    if timed_out:
        return CodexJudgmentOutcome(ConformanceState.INCONCLUSIVE, "codex_timeout", None)
    if not final_decision or "decision" not in final_decision:
        return CodexJudgmentOutcome(ConformanceState.INCONCLUSIVE, "codex_no_decision", None)
    decision = final_decision["decision"]
    state = _DECISION_TO_CONFORMANCE.get(decision)
    if state is None:
        return CodexJudgmentOutcome(ConformanceState.INCONCLUSIVE, f"codex_unknown_decision:{decision}", None)
    if state == ConformanceState.PASS:
        sufficient, rigor_reason = counterexample_search_is_sufficient(final_decision)
        if not sufficient:
            return CodexJudgmentOutcome(
                ConformanceState.INCONCLUSIVE, f"insufficient_reasoning_rigor:{rigor_reason}",
                final_decision.get("reasoning_summary"),
            )
    return CodexJudgmentOutcome(state, None, final_decision.get("reasoning_summary"))
