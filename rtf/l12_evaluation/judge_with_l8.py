"""L12 <-> L8 bridge: takes a `TargetRunResult` produced by `run_rtf.py`'s
deterministic layer and, for every requirement that fired with evidence
but has no conformance verdict yet ("judgment pending" -- see
`run_rtf.py`'s own module docstring), calls the L8 LLM Judgment Layer to
reach a real PASS/FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE decision.

This is the piece that turns RTF's routing+evidence output into an
actual, gradeable final judgment. Before this module, every evaluation
run necessarily showed `final_finding_recall: 0/N` regardless of how
good the underlying evidence was -- not because RTF failed to detect
anything, but because nothing downstream of evidence collection was ever
asked to render a verdict.
"""
from __future__ import annotations

import json
import traceback
from dataclasses import replace
from pathlib import Path

from rtf.l8_llm_judgment_layer.judgment_layer import LLMJudgmentLayer
from rtf.l12_evaluation.failure_taxonomy import OperationalStatus
from rtf.l12_evaluation.metrics import ConformanceState, RoutedRequirementResult, TargetRunResult

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLES_DIR = REPO_ROOT / "rtf" / "l2_context_bundles"

_DECISION_TO_CONFORMANCE = {
    "PASS": ConformanceState.PASS,
    "FAIL": ConformanceState.FAIL,
    "INCONCLUSIVE": ConformanceState.INCONCLUSIVE,
    "INSUFFICIENT_EVIDENCE": ConformanceState.INSUFFICIENT_EVIDENCE,
}


def build_judgment_question(evidence: list, max_items: int = 30) -> str:
    """A generic question template usable across ANY requirement's
    evidence, deliberately NOT requirement-specific -- the requirement's
    own text/definitions/exceptions are already injected by
    `judgment_layer.build_judgment_prompt` from the context bundle; this
    function's only job is to hand over what RTF's deterministic layer
    actually found, without editorializing about what it means.

    Capped at `max_items` evidence lines to keep prompts bounded when a
    predicate (deliberately over-inclusive by design) produces dozens of
    findings for one requirement -- the cap itself, and how many were
    omitted, is stated in the question so the model knows the list may be
    partial, not exhaustive.
    """
    lines = [f"- {e.location}: {e.detail}" for e in evidence[:max_items]]
    omitted_note = ""
    if len(evidence) > max_items:
        omitted_note = f"\n(...and {len(evidence) - max_items} more similar items, omitted for length.)"
    evidence_block = "\n".join(lines) + omitted_note
    return (
        "A static-analysis tool collected the following evidence from the Tested Code, "
        "regarding this specific requirement:\n\n"
        f"{evidence_block}\n\n"
        "Based ONLY on the requirement text above and this evidence (do not assume "
        "anything about the code not stated in the evidence), does the Tested Code "
        "conform to the requirement? Note that the evidence is deliberately "
        "over-inclusive by design (it flags candidate locations, not confirmed "
        "violations) -- your job is to judge whether each specific listed location "
        "is a GENUINE violation given the requirement's actual text, not to assume "
        "every listed item is automatically a violation."
    )


def judge_result(
    judgment_layer: LLMJudgmentLayer,
    req_id: str,
    result: RoutedRequirementResult,
    repo_root: Path | None = None,
    use_second_pass: bool = True,
) -> tuple[RoutedRequirementResult, dict | None]:
    """Judge ONE requirement's already-collected evidence. Returns
    (updated_result, raw_l8_response_or_None). Never raises -- an L8
    call failure (network, schema validation, API error) degrades this
    ONE requirement to `OperationalStatus.ENVIRONMENT_FAILURE` with the
    original evidence preserved, exactly the same per-requirement
    isolation discipline `run_rtf.py` already applies to predicate
    crashes.
    """
    bundle_path = BUNDLES_DIR / f"{req_id}.json"
    if not bundle_path.exists():
        return replace(result, operational_status=OperationalStatus.ENVIRONMENT_FAILURE), None

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    question = build_judgment_question(list(result.evidence))

    try:
        if use_second_pass:
            outcome = judgment_layer.judge_with_second_pass(bundle, question, repo_root=repo_root)
            judgment = outcome["first_pass"]
            raw = outcome
        else:
            judgment = judgment_layer.judge_once(bundle, question, repo_root=repo_root)
            raw = judgment
    except Exception as e:  # noqa: BLE001 -- one requirement's L8 failure must not abort the whole run
        return replace(
            result,
            operational_status=OperationalStatus.ENVIRONMENT_FAILURE,
        ), {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()}

    conformance = _DECISION_TO_CONFORMANCE.get(judgment["decision"])
    updated = replace(result, conformance_state=conformance)
    return updated, raw


def judge_run(
    judgment_layer: LLMJudgmentLayer,
    run: TargetRunResult,
    repo_root: Path | None = None,
    use_second_pass: bool = True,
    only_req_ids: set[str] | None = None,
) -> tuple[TargetRunResult, dict]:
    """Judge every APPLICABLE, evidence-backed, still-pending requirement
    in `run`. `only_req_ids`, if given, restricts judgment to that subset
    (e.g. only the requirements with a real L11 ground-truth mapping, to
    bound API cost on a bulk run) -- requirements outside that set are
    left untouched (still `conformance_state=None`, "not judged in this
    pass", not silently marked anything else).
    """
    new_routed = dict(run.routed)
    raw_judgments: dict[str, dict] = {}

    for req_id, result in run.routed.items():
        if only_req_ids is not None and req_id not in only_req_ids:
            continue
        if result.applicability_state.value != "APPLICABLE":
            continue
        if result.conformance_state is not None:
            continue  # already resolved (e.g. DETERMINISTIC_COMPLETE unconditioned-PASS) -- L8 not needed
        if not result.evidence:
            continue  # nothing to judge
        if result.operational_status.value != "OK":
            continue  # don't attempt to judge a result that already failed operationally

        updated, raw = judge_result(judgment_layer, req_id, result, repo_root, use_second_pass)
        new_routed[req_id] = updated
        if raw is not None:
            raw_judgments[req_id] = raw

    return TargetRunResult(audit_id=run.audit_id, routed=new_routed), raw_judgments
