"""Deterministic, requirement/code-derived evidence ranking and bundling
(Phase H work items 2-5).

## Why this module exists

`judge_with_l8.py`'s original `build_judgment_question()` sent L8 the
FIRST `max_items` (default 30) evidence items in whatever order
`run_rtf.py` happened to produce them -- registry.py's predicate
registration order, then Slither's own internal contract/function
enumeration order within each predicate. That ordering is fully
DETERMINISTIC (same code + same compiled target always produces the same
order) but is otherwise ACCIDENTAL: it carries no relevance signal at
all.

Traced concretely against the real, already-collected
`2023-07-pooltogether` v2 run 1 evidence
(`v2_run1_artifacts/pooltogether_routed.json`), not assumed:
`req-3-all-valid-inputs` produced 739 raw evidence items. 383 of them
(52%) are `find_unvalidated_function_parameters` findings against
`console2` -- forge-std's debug/logging shim, vendored under
`lib/forge-std/src/console2.sol`, pulled in transitively by nearly every
Foundry project and containing zero code relevant to any audit. Those
383 items sort FIRST (Slither's own contract-enumeration order put
`console2` before every real project contract). The evidence that
RTF_V2_RUN1_REPORT.md identified as the one that flips PoolTogether's
H-02 to a stable FAIL in isolated testing -- `Vault._burn`'s
`find_unsafe_narrowing_cast` finding -- sits at raw index 737 of 739,
i.e. literally does not survive `evidence[:30]`. This is not "dilution"
in the sense of the signal being present-but-crowded; the flat top-30
cutoff excludes it entirely, deterministically, on every run.

This module fixes that by scoring and grouping evidence using ONLY
requirement-derived and code-derived signals -- never EVMbench finding
text, finding IDs, expected vulnerable functions, grader feedback, or
any Tempo/PoolTogether-specific name or mechanism. See each function's
docstring for the specific engineering justification of the signal it
computes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .metrics import EvidenceItem

# --- Priority-contract membership --------------------------------------
#
# Signal: is this evidence located in a file that is plausibly the
# audited project's OWN source, or a vendored dependency / build
# artifact / test-tooling file pulled in transitively?
#
# All markers below are generic Foundry/Solidity project-layout and
# tooling conventions (not specific to any EVMbench audit's contracts,
# functions, or findings): a `lib/` subtree is exactly what `forge
# install`/git submodules populate with third-party dependencies (the
# same distinction this project's own CLAUDE.md documents making for
# what counts as "in scope" when constructing evaluation targets --
# vendored, independently-audited library code is conventionally out of
# audit scope); `node_modules/` is npm's dependency directory; `out/`
# and `cache/` are Foundry's own build-artifact directories (frequently
# containing STALE or DUPLICATE copies of every compiled file, including
# the project's own contracts -- these must be excluded too, or a real
# project contract would get counted twice under two different paths);
# `console2.sol`/`console.sol` are forge-std's specific debug-logging
# shims, present in essentially every Foundry project's `lib/forge-std/`
# regardless of what's being audited; `.t.sol` is Foundry's own test-file
# naming convention.
_VENDORED_PATH_SEGMENTS = {"lib", "node_modules", "out", "cache", "artifacts", "script", "scripts"}
_VENDORED_BASENAMES = {"console2.sol", "console.sol"}


def _is_vendored_or_noncode_path(path: Path, repo_root: Path) -> bool:
    """Checks path segments RELATIVE TO `repo_root` only -- never the
    absolute path. A real bug caught by this module's own real-data
    regression test (test_evidence_ranking.py): this project's own
    checkout happens to live under a directory literally named `out/`
    (`agent4vul/out/2023-07-pooltogether/checkout/vault/...`), which has
    nothing to do with Foundry's `out/` build-artifacts convention --
    checking the FULL absolute path's segments made every single file in
    the checkout match the `out` vendored-marker and score as "not
    priority", silently defeating the whole signal. Only segments inside
    the project tree itself are meaningful here.
    """
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        rel = path  # path isn't under repo_root at all -- fall back to checking it directly
    parts = {p.lower() for p in rel.parts}
    if parts & _VENDORED_PATH_SEGMENTS:
        return True
    if path.name.lower() in _VENDORED_BASENAMES:
        return True
    if path.name.lower().endswith(".t.sol"):
        return True
    return False


_CONTRACT_DECL_RE_CACHE: dict[Path, dict[str, list[Path]]] = {}


def _index_contract_declarations(repo_root: Path) -> dict[str, list[Path]]:
    """One pass over every `.sol` file under `repo_root`, mapping each
    declared contract/library/interface name to every file path that
    declares it (a name can legitimately be declared more than once --
    e.g. a real contract and an unrelated same-named test mock in a
    different subtree). Cached per `repo_root` since this module may be
    asked to rank evidence for many requirements against the same target
    in one run -- re-scanning the whole tree per requirement would be
    wasteful and is not needed, the tree doesn't change mid-run.
    """
    if repo_root in _CONTRACT_DECL_RE_CACHE:
        return _CONTRACT_DECL_RE_CACHE[repo_root]

    decl_re = re.compile(r"\b(?:contract|library|interface)\s+([A-Za-z_][A-Za-z0-9_]*)")
    index: dict[str, list[Path]] = {}
    for sol_file in repo_root.rglob("*.sol"):
        if not sol_file.is_file():
            continue  # Foundry's out/ can contain a DIRECTORY named e.g. "Vault.sol" holding build-info JSON, not source
        try:
            text = sol_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for name in decl_re.findall(text):
            index.setdefault(name, []).append(sol_file)

    _CONTRACT_DECL_RE_CACHE[repo_root] = index
    return index


def is_priority_contract(location: str, repo_root: Path | None) -> bool | None:
    """True if `location`'s contract (the part before the first `.`, or
    the whole string if there's no `.`) is declared in at least one file
    that is NOT a vendored dependency / build artifact / test file.
    False if it is declared ONLY in such files. None (unknown, treated
    as neutral by the scorer, not penalized) if `repo_root` is
    unavailable or the contract name can't be found in the tree at all
    (e.g. a name-only location string with no matching source file --
    this must not silently score as "definitely not priority", since
    that would be a false negative caused by a lookup gap, not a real
    signal).
    """
    if repo_root is None:
        return None
    contract_name = location.split(".", 1)[0]
    index = _index_contract_declarations(repo_root)
    paths = index.get(contract_name)
    if not paths:
        return None
    return any(not _is_vendored_or_noncode_path(p, repo_root) for p in paths)


# --- Structured-evidence specificity/completeness -----------------------
#
# Signal: does this evidence item's OWN predicate output name a concrete
# operation, a concrete input, and an explicit protection-status
# assessment -- i.e. is it the richer `structured` shape (added in RTF
# v2, see EvidenceItem.structured's own docstring), or the older bare
# `detail`-only shape? This is a property of the evidence RTF itself
# already produced, not of the underlying code or the requirement text --
# included because work item 3 explicitly asks for "specificity" and
# "completeness" as ranking features, and this is the direct, own-output
# measurement of both, with zero benchmark-derived input.
_INFORMATIVE_STRUCTURED_KEYS = (
    "operation", "input", "source_type", "destination_type", "validation_found",
    "missing_safety_condition", "risk", "possible_result", "affected_functions",
)


def structured_specificity_score(item: EvidenceItem) -> float:
    if not item.structured:
        return 0.0
    populated = sum(1 for k in _INFORMATIVE_STRUCTURED_KEYS if item.structured.get(k))
    completeness = populated / len(_INFORMATIVE_STRUCTURED_KEYS)
    return 0.5 + 0.5 * completeness  # has-structured floor (0.5) + completeness bonus


def protection_status_identified(item: EvidenceItem) -> bool:
    """True if the predicate explicitly assessed (present OR absent) a
    protection/validation condition for this finding, rather than
    omitting the question entirely. Derived straight from the
    predicate's own structured output (`validation_found`/
    `missing_safety_condition`) -- a predicate-authored field, not
    anything about the specific audit."""
    if not item.structured:
        return False
    return bool(item.structured.get("missing_safety_condition")) or "validation_found" in item.structured


def concrete_operation_named(item: EvidenceItem) -> bool:
    """True if a specific operation is named (a cast, a call, a signature
    recovery, a state write, a check) rather than a generic 'this
    function has no matching require()' style claim with no named
    mechanism. Uses only the evidence's own text/structured fields."""
    if item.structured and item.structured.get("operation"):
        return True
    # generic fallback keyword check for predicates that don't (yet)
    # produce structured evidence -- names of Solidity CONSTRUCTS, not
    # any audit-specific vocabulary
    keywords = ("cast", "ecrecover", "call(", "delegatecall", "staticcall",
                "assembly", "selfdestruct", "create2", "signature")
    return any(k in item.detail.lower() for k in keywords)


# --- Ranking ------------------------------------------------------------

RANKING_WEIGHTS = {
    "priority_contract": 0.35,
    "structured_specificity": 0.30,
    "protection_status_identified": 0.20,
    "concrete_operation_named": 0.15,
}
assert abs(sum(RANKING_WEIGHTS.values()) - 1.0) < 1e-9


@dataclass(frozen=True)
class RankedEvidence:
    item: EvidenceItem
    score: float
    breakdown: dict = field(default_factory=dict)


def score_evidence_item(item: EvidenceItem, repo_root: Path | None) -> RankedEvidence:
    priority = is_priority_contract(item.location, repo_root)
    # Unknown priority status contributes its weight's midpoint (0.5), not
    # 0 and not full credit -- an evidence item RTF can't place in the
    # tree at all is neither rewarded nor punished by a signal that
    # simply couldn't be computed for it.
    priority_component = 1.0 if priority is True else (0.0 if priority is False else 0.5)
    specificity_component = structured_specificity_score(item)
    protection_component = 1.0 if protection_status_identified(item) else 0.0
    operation_component = 1.0 if concrete_operation_named(item) else 0.0

    breakdown = {
        "priority_contract": {"value": priority, "component_score": priority_component, "weight": RANKING_WEIGHTS["priority_contract"]},
        "structured_specificity": {"value": round(specificity_component, 3), "component_score": specificity_component, "weight": RANKING_WEIGHTS["structured_specificity"]},
        "protection_status_identified": {"value": protection_component == 1.0, "component_score": protection_component, "weight": RANKING_WEIGHTS["protection_status_identified"]},
        "concrete_operation_named": {"value": operation_component == 1.0, "component_score": operation_component, "weight": RANKING_WEIGHTS["concrete_operation_named"]},
    }
    score = (
        priority_component * RANKING_WEIGHTS["priority_contract"]
        + specificity_component * RANKING_WEIGHTS["structured_specificity"]
        + protection_component * RANKING_WEIGHTS["protection_status_identified"]
        + operation_component * RANKING_WEIGHTS["concrete_operation_named"]
    )
    return RankedEvidence(item=item, score=score, breakdown=breakdown)


def _dedupe_key(item: EvidenceItem) -> tuple:
    return (item.predicate, item.location, item.detail)


def rank_evidence(evidence: list[EvidenceItem], repo_root: Path | None) -> list[RankedEvidence]:
    """Score every item, drop exact duplicates (same predicate + location
    + detail -- zero marginal information over the first occurrence,
    a mechanical dedup, not a relevance judgment), and sort by score
    descending. Stable sort with location as the tiebreak key, so output
    order is fully reproducible across runs given identical input, not
    just "deterministic in principle."
    """
    seen: set[tuple] = set()
    ranked: list[RankedEvidence] = []
    for item in evidence:
        key = _dedupe_key(item)
        if key in seen:
            continue
        seen.add(key)
        ranked.append(score_evidence_item(item, repo_root))
    ranked.sort(key=lambda r: (-r.score, r.item.location))
    return ranked


# --- Evidence bundles -----------------------------------------------------

def _merge_structured_lists(items: list[EvidenceItem], field_name: str) -> list[str]:
    out: list[str] = []
    for it in items:
        if it.structured and it.structured.get(field_name):
            v = it.structured[field_name]
            vals = v if isinstance(v, list) else [v]
            for x in vals:
                if x not in out:
                    out.append(str(x))
    return out


def build_evidence_bundles(
    req_id: str,
    requirement_text: str,
    ranked: list[RankedEvidence],
) -> list[dict]:
    """Groups ranked evidence by location into ONE coherent bundle per
    location (schema per Phase H work item 4), rather than the previous
    flat per-predicate-finding list. Real, concrete motivation: the real
    PoolTogether run had TWO separate flat items for `Vault._burn` --
    one from `find_unvalidated_function_parameters` (generic, "no
    require() references this parameter") and one from
    `find_unsafe_narrowing_cast` (specific, names the exact truncating
    cast) -- at raw indices 674 and 737 respectively, far enough apart
    that a flat top-30 cutoff could keep one and drop the other even if
    both survived ranking. Bundling by location guarantees whichever
    signals exist for one location are presented to L8 together, as one
    coherent picture, never split across the prompt.

    Bundle order follows the HIGHEST-scoring member evidence item per
    location (ties broken alphabetically by location, matching
    `rank_evidence`'s own tiebreak) -- so bundle-level ranking is
    consistent with item-level ranking, not a separate re-derivation.
    """
    by_location: dict[str, list[RankedEvidence]] = {}
    for r in ranked:
        by_location.setdefault(r.item.location, []).append(r)

    bundles: list[dict] = []
    for location, group in by_location.items():
        items = [g.item for g in group]
        bundle_score = max(g.score for g in group)
        # Merge every group member's breakdown under its own predicate
        # name -- keeps per-signal auditability even after merging.
        merged_breakdown = {g.item.predicate: g.breakdown for g in group}

        contract, _, function = location.partition(".")
        target = {"contract": contract, "function": function or None, "source_location": location}

        observed_ops = [it.structured["operation"] for it in items if it.structured and it.structured.get("operation")]
        input_sources = [
            f"{it.structured['input'].get('name')}: {it.structured['input'].get('type')}"
            for it in items if it.structured and it.structured.get("input")
        ]
        existing_protections = [
            it.structured["validation_found"] for it in items
            if it.structured and it.structured.get("validation_found") and it.structured["validation_found"].lower() != "none"
        ]
        missing_protections = _merge_structured_lists(items, "missing_safety_condition")
        risks = _merge_structured_lists(items, "risk")

        limitations: list[str] = []
        if not observed_ops:
            limitations.append("no predicate for this location named a concrete operation -- evidence is limited to a generic 'input/construct not validated' signal")
        if not existing_protections and not missing_protections:
            limitations.append("protection status not explicitly assessed by any contributing predicate for this location")

        # possible_failure_mechanism: prefer the contributing predicate's OWN
        # risk text (concrete -- e.g. "values above X are silently truncated
        # by this cast rather than rejected") over a generic templated
        # sentence. Real bug found and fixed here (Phase H live stability
        # experiment, see PHASE_H_STABILITY_EXPERIMENT_PREREGISTRATION.md /
        # the session's AR log): an earlier version of this function put the
        # predicate's risk text under `limitations` with a
        # "(not an exploit claim)" hedge prefix instead, which measurably
        # made L8 MORE uncertain (INSUFFICIENT_EVIDENCE, LOW confidence)
        # than the exact same information rendered as a plain "Risk:" line
        # in an isolated A/B comparison against identical evidence (FAIL,
        # MEDIUM confidence) -- confirmed by direct side-by-side testing,
        # not assumed. A predicate's own risk assessment is evidence, not a
        # limitation/caveat about the evidence, and must not be framed as
        # one. Still hedged ("may proceed", not "will cause") only in the
        # template FALLBACK, used when no predicate provides its own risk
        # text -- work item 4's "must not claim exploit impact the code
        # evidence can't support" constraint applies to what THIS module
        # invents, not to a predicate's own, already-appropriately-hedged
        # factual claim (e.g. "silently truncated" is a mechanical fact
        # about the cast, not an exploit-impact claim).
        if risks:
            possible_failure_mechanism = "; ".join(risks)
        elif missing_protections:
            possible_failure_mechanism = f"if {missing_protections[0]} is not otherwise enforced, the observed operation may proceed on out-of-range or unvalidated input"
        else:
            possible_failure_mechanism = None

        bundles.append({
            "req_id": req_id,
            "target": target,
            "requirement_text": requirement_text,
            "applicability_reason": f"matched by predicate(s): {', '.join(sorted({it.predicate for it in items}))}",
            "observed_operation": "; ".join(observed_ops) if observed_ops else None,
            "input_or_value_source": "; ".join(input_sources) if input_sources else None,
            "data_flow": [],  # not currently derivable without interprocedural tracing beyond this module's scope -- left empty, not fabricated
            "existing_protections": existing_protections,
            "missing_or_uncertain_protections": missing_protections,
            "possible_failure_mechanism": possible_failure_mechanism,
            "code_excerpts": [],  # source excerpts are attached by judge_with_l8.py's citation_check step, not duplicated here
            "supporting_evidence_ids": [f"{it.predicate}::{it.location}" for it in items],
            "limitations": limitations,
            "ranking_score": round(bundle_score, 4),
            "ranking_breakdown": merged_breakdown,
        })

    bundles.sort(key=lambda b: (-b["ranking_score"], b["target"]["source_location"]))
    return bundles


# --- Evidence budget ------------------------------------------------------

@dataclass(frozen=True)
class EvidenceBudgetResult:
    included: list[dict]
    excluded: list[dict]
    prompt_char_estimate: int  # proxy for token count -- see docstring


def apply_evidence_budget(bundles: list[dict], max_bundles: int) -> EvidenceBudgetResult:
    """Replaces the old fixed 'top 30 FLAT ITEMS' cutoff with a
    requirement-aware budget over whole BUNDLES (already ranking-sorted
    by `build_evidence_bundles`) -- so a cutoff can never split one
    location's evidence across the included/excluded boundary the way
    the flat-list cutoff could and, in the real PoolTogether run, did.

    `prompt_char_estimate` is a character-count proxy for prompt size,
    not a real tokenizer count (no tokenizer dependency is wired into
    this project) -- reported alongside the bundle counts per work item
    5's "record prompt token counts" requirement, with this
    approximation limitation stated explicitly rather than silently
    presented as an exact token count.
    """
    included = bundles[:max_bundles]
    excluded = bundles[max_bundles:]
    chars = sum(len(_render_bundle_text(b)) for b in included)
    return EvidenceBudgetResult(included=included, excluded=excluded, prompt_char_estimate=chars)


def _render_bundle_text(b: dict) -> str:
    lines = [f"- {b['target']['source_location']} (ranking_score={b['ranking_score']}):"]
    if b["observed_operation"]:
        lines.append(f"  Operation: {b['observed_operation']}")
    if b["input_or_value_source"]:
        lines.append(f"  Input: {b['input_or_value_source']}")
    if b["existing_protections"]:
        lines.append(f"  Existing protections: {'; '.join(b['existing_protections'])}")
    if b["missing_or_uncertain_protections"]:
        lines.append(f"  Missing/uncertain protections: {'; '.join(b['missing_or_uncertain_protections'])}")
    if b["possible_failure_mechanism"]:
        lines.append(f"  Possible failure mechanism: {b['possible_failure_mechanism']}")
    if b["limitations"]:
        lines.append(f"  Limitations: {'; '.join(b['limitations'])}")
    return "\n".join(lines)


def render_bundles_for_prompt(bundles: list[dict], omitted_count: int = 0) -> str:
    text = "\n".join(_render_bundle_text(b) for b in bundles)
    if omitted_count:
        text += f"\n(...and {omitted_count} more lower-ranked location(s), omitted for length.)"
    return text
