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
from rtf.l12_evaluation.evidence_ranking import apply_evidence_budget, build_evidence_bundles, rank_evidence, render_bundles_for_prompt
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


def _render_evidence_line(e) -> str:
    """One evidence item as prompt text. Prefers the STRUCTURED fields
    (operation/input/types/validation_found/missing_safety_condition/
    risk) when a predicate provides them, over the older bare `detail`
    string -- added in direct response to a real, reproduced finding
    (RTF_V1_RUN2_REPORT.md): both L8 and the real DetectGrader
    independently judged bare 'parameter not validated'-style phrasing
    too generic for a confident verdict, even when correctly localized.
    Falls back to `detail` for predicates that don't (yet) produce
    structured evidence, so this stays a strict superset, not a breaking
    change for the other ~30 predicates.
    """
    if not e.structured:
        return f"- {e.location}: {e.detail}"
    se = e.structured
    parts = [f"- {e.location}:"]
    if se.get("operation"):
        parts.append(f"  Operation: {se['operation']}")
    if se.get("input"):
        inp = se["input"]
        parts.append(f"  Input: {inp.get('name')}, type {inp.get('type')}")
    if se.get("source_type") and se.get("destination_type"):
        parts.append(f"  Type conversion: {se['source_type']} -> {se['destination_type']}")
    if se.get("possible_result"):
        parts.append(f"  Possible result: {se['possible_result']}")
    if "validation_found" in se:
        parts.append(f"  Validation found: {se['validation_found']}")
    if se.get("missing_safety_condition"):
        parts.append(f"  Missing safety condition: {se['missing_safety_condition']}")
    if se.get("risk"):
        parts.append(f"  Risk: {se['risk']}")
    if se.get("affected_functions"):
        parts.append(f"  Affected functions: {', '.join(se['affected_functions'])}")
    return "\n".join(parts)


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
    lines = [_render_evidence_line(e) for e in evidence[:max_items]]
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


def build_ranked_judgment_question(
    req_id: str,
    requirement_text: str,
    evidence: list,
    repo_root: Path | None,
    max_bundles: int = 30,
) -> tuple[str, dict]:
    """The default (non-baseline) question builder: rank evidence
    (deterministic, requirement/code-derived signals only -- see
    evidence_ranking.py), merge same-location findings into coherent
    bundles, then apply a requirement-aware budget over whole bundles
    instead of the old flat `evidence[:max_items]` cutoff. Returns
    (question_text, ranking_metadata) -- the metadata is what work item 5
    asks to record (bundle counts, prompt char estimate as a token-count
    proxy, excluded location list).
    """
    ranked = rank_evidence(list(evidence), repo_root)
    bundles = build_evidence_bundles(req_id, requirement_text, ranked)
    budget = apply_evidence_budget(bundles, max_bundles)
    evidence_block = render_bundles_for_prompt(budget.included, omitted_count=len(budget.excluded))
    question = (
        "A static-analysis tool collected the following ranked evidence bundles from the Tested Code, "
        "regarding this specific requirement (higher ranking_score = more specific and more likely to be "
        "in the audited project's own code, not a vendored dependency):\n\n"
        f"{evidence_block}\n\n"
        "Based ONLY on the requirement text above and this evidence (do not assume "
        "anything about the code not stated in the evidence), does the Tested Code "
        "conform to the requirement? Note that the evidence is deliberately "
        "over-inclusive by design (it flags candidate locations, not confirmed "
        "violations) -- your job is to judge whether each specific listed location "
        "is a GENUINE violation given the requirement's actual text, not to assume "
        "every listed item is automatically a violation."
    )
    metadata = {
        "ranking_enabled": True,
        "raw_evidence_count": len(evidence),
        "deduped_evidence_count": len(ranked),
        "bundle_count": len(bundles),
        "bundles_included": len(budget.included),
        "bundles_excluded": len(budget.excluded),
        "excluded_locations": [b["target"]["source_location"] for b in budget.excluded],
        "prompt_char_estimate": budget.prompt_char_estimate,
        "max_bundles": max_bundles,
    }
    return question, metadata


def judge_result(
    judgment_layer: LLMJudgmentLayer,
    req_id: str,
    result: RoutedRequirementResult,
    repo_root: Path | None = None,
    use_second_pass: bool = True,
    use_ranking: bool = True,
) -> tuple[RoutedRequirementResult, dict | None]:
    """Judge ONE requirement's already-collected evidence. Returns
    (updated_result, raw_l8_response_or_None). Never raises -- an L8
    call failure (network, schema validation, API error) degrades this
    ONE requirement to `OperationalStatus.ENVIRONMENT_FAILURE` with the
    original evidence preserved, exactly the same per-requirement
    isolation discipline `run_rtf.py` already applies to predicate
    crashes.

    `use_ranking` (default True) selects the requirement-aware ranked-
    bundle question builder (`build_ranked_judgment_question`), which
    replaces the old fixed "first 30 flat items" behavior -- see
    evidence_ranking.py's module docstring for the concrete real-data bug
    this fixes (PoolTogether's Vault._burn narrowing-cast evidence was
    excluded outright by the old cutoff). `use_ranking=False` keeps the
    OLD flat-list builder available on purpose, not as dead code: work
    item 5 requires comparing ranked-bundle behavior against "current
    flat-list behavior... as a baseline," which needs the old path to
    still exist and still be callable.
    """
    bundle_path = BUNDLES_DIR / f"{req_id}.json"
    if not bundle_path.exists():
        return replace(result, operational_status=OperationalStatus.ENVIRONMENT_FAILURE), None

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    evidence_item_limit = 30  # keep in sync with build_judgment_question's own default -- passed explicitly below so it's one source of truth, not two

    if use_ranking:
        requirement_text = bundle["bundle"]["self"]
        question, ranking_meta = build_ranked_judgment_question(
            req_id, requirement_text, list(result.evidence), repo_root, max_bundles=evidence_item_limit
        )
    else:
        question = build_judgment_question(list(result.evidence), max_items=evidence_item_limit)
        ranking_meta = None

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

    # Evidence-truncation/ranking bookkeeping (Phase H work item 1:
    # "evidence-item limit/truncation behavior" must be recorded on every
    # judgment artifact; work item 5: "record ... excluded evidence").
    # Attached at the L12 orchestration level, not inside L8 itself,
    # because evidence bundling/budgeting is an L12-owned bridging
    # decision, not something judgment_layer.py knows about.
    if use_ranking:
        truncation_meta = ranking_meta
    else:
        truncation_meta = {
            "ranking_enabled": False,
            "evidence_item_limit": evidence_item_limit,
            "evidence_items_available": len(result.evidence),
            "evidence_items_included": min(len(result.evidence), evidence_item_limit),
            "evidence_items_omitted": max(0, len(result.evidence) - evidence_item_limit),
        }
    raw["evidence_truncation"] = truncation_meta

    conformance = resolve_conformance_from_judgment(judgment["decision"], raw.get("agree") if use_second_pass else None)
    updated = replace(result, conformance_state=conformance)
    return updated, raw


def resolve_conformance_from_judgment(decision: str, second_pass_agree: bool | None) -> ConformanceState | None:
    """Pure decision logic, extracted so it's unit-testable without a live
    LLM call. Real gap found by running RTF v2 run 1 live (tempo-mpp-
    streams' req-2-signature-verification): a PASS/FAIL was previously
    reported as final EVEN WHEN the second pass disagreed with it --
    silently ignoring exactly the signal the plan's own mandatory-second-
    pass rule exists to surface. If `second_pass_agree` is explicitly
    `False`, the decision is downgraded to `INCONCLUSIVE` (a legitimate,
    expected outcome per the plan, not a failure) regardless of what the
    first pass said -- a verdict the model itself couldn't reproduce on a
    second, independent attempt must not be reported at the same
    confidence as a stable one. `second_pass_agree=None` (single-pass
    mode, or second pass genuinely not run) leaves the first pass's own
    decision untouched -- there is nothing to compare it against.
    """
    if second_pass_agree is False:
        return ConformanceState.INCONCLUSIVE
    return _DECISION_TO_CONFORMANCE.get(decision)


def judge_run(
    judgment_layer: LLMJudgmentLayer,
    run: TargetRunResult,
    repo_root: Path | None = None,
    use_second_pass: bool = True,
    only_req_ids: set[str] | None = None,
    use_ranking: bool = True,
) -> tuple[TargetRunResult, dict]:
    """Judge every APPLICABLE, evidence-backed, still-pending requirement
    in `run`. `only_req_ids`, if given, restricts judgment to that subset
    (e.g. only the requirements with a real L11 ground-truth mapping, to
    bound API cost on a bulk run) -- requirements outside that set are
    left untouched (still `conformance_state=None`, "not judged in this
    pass", not silently marked anything else). `use_ranking` is forwarded
    to `judge_result` per-requirement -- see its docstring.
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

        updated, raw = judge_result(judgment_layer, req_id, result, repo_root, use_second_pass, use_ranking)
        new_routed[req_id] = updated
        if raw is not None:
            raw_judgments[req_id] = raw

    return TargetRunResult(audit_id=run.audit_id, routed=new_routed), raw_judgments
