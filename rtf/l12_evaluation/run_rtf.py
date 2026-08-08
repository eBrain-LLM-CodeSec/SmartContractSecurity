"""L12 RTF execution orchestrator.

Runs every registered predicate (`rtf.l12_evaluation.registry`) against a
real, compiled EVMbench target and produces both a `TargetRunResult`
(consumable directly by `rtf.l12_evaluation.metrics`) and a full raw
JSON artifact preserving everything the plan's step 6 requires kept:
routed requirement IDs, applicability decisions, predicate evidence,
tool/compiler versions, and execution errors. L8 semantic judgment is
NOT invoked by this module -- see "What this orchestrator does NOT do"
below.

Per requirement, three outcomes are possible:

1. Evidence collected (>=1 predicate finding): `applicability_state =
   APPLICABLE`, `conformance_state = None`. This is deliberate, not a
   bug: this orchestrator does not itself decide PASS/FAIL/INCONCLUSIVE
   for evidence-backed requirements -- per the plan, only L8 (a
   SEPARATE, not-yet-wired-in-here layer) may make that call, and
   `None` here means "judgment pending," not "no judgment needed" or
   any of the 4 canonical `ConformanceState` values. Inventing a 5th
   state to mean "pending" would violate the plan's own fixed schema.
2. No evidence, and the requirement's L1 `conditioned_scope_clause` is
   `is_unconditioned_subject: true` (an unconditioned "MUST NOT contain
   X" with no override): `applicability_state = APPLICABLE`,
   `conformance_state = PASS` -- for this shape ONLY, absence of the
   prohibited construct genuinely IS the complete conformance answer,
   no semantic judgment needed (matches the plan's own
   `DETERMINISTIC_COMPLETE` category).
3. No evidence, and the requirement IS conditioned (has a
   `conditioned_scope_clause` naming a subject the trigger didn't
   match): `applicability_state = NOT_APPLICABLE`, `conformance_state
   = None`.
4. Pure aggregation requirements (`req-2-pass-l1`, `req-3-pass-l2`,
   `req-R-meet-all-possible` -- see `registry.AGGREGATION_REQ_IDS`):
   `applicability_state = APPLICABLE`, `conformance_state = None`,
   `evidence = ()`. These cannot be resolved here -- they are a function
   of OTHER requirements' FINAL conformance states, which this
   deterministic-only layer does not yet have (L8 judgment/escalation run
   later, in `pipeline_e2e.py`). Resolved post-hoc by
   `pipeline_e2e.compute_aggregation_requirements` after that loop
   completes, using this exact placeholder as its signal to fill in.
5. Genuinely unsupported (no registered predicate, no aggregation rule --
   should be empirically EMPTY after the runtime-coverage-audit fixes,
   but the code path always exists): `applicability_state = APPLICABLE`,
   `operational_status = OperationalStatus.UNSUPPORTED_ANALYZER`. This is
   the fix for a real, confirmed prior bug: this orchestrator used to
   iterate ONLY `REGISTRY.keys()` (56 of 81 requirements), so any
   requirement without a registered predicate never appeared in `routed`
   AT ALL -- not as NOT_APPLICABLE, not as any operational-failure code,
   completely absent from every downstream artifact. See
   `RTF_RUNTIME_COVERAGE_AUDIT.md`/`RTF_MISSING_REQUIREMENTS_GAP_ANALYSIS.md`
   for the full investigation. This orchestrator now iterates the FULL
   requirement corpus (every key in `unconditioned_map`, which is built
   from the complete L1 corpus, not `REGISTRY.keys()`) so the invariant
   "applicable requirements = executed + explicitly unsupported, silently
   missing == 0" holds structurally, not just empirically.

Any predicate call that raises is caught and converted to
`OperationalStatus.ANALYZER_CRASH` for that ONE requirement -- a crash
on one requirement's predicate must never take down evaluation of every
other requirement in the same run (the plan's own operational-failure
discipline, `failure_taxonomy.py`).

**What this orchestrator does NOT do:** call L8, resolve L11
correspondence, or compute metrics -- those are separate, later steps
(`judgment_layer.py`, the frozen `correspondence_mapping.json`,
`metrics.py` respectively). This module's job ends at "here is what RTF's
deterministic layer concluded, evidence and all."
"""
from __future__ import annotations

import json
import subprocess
import sys
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path

from rtf.l5_predicates.compile_helper import compile_evmbench_target
from rtf.l12_evaluation.failure_taxonomy import OperationalStatus
from rtf.l12_evaluation.metrics import (
    ApplicabilityState,
    ConformanceState,
    EvidenceItem,
    RoutedRequirementResult,
    TargetRunResult,
)
from rtf.l12_evaluation.registry import AGGREGATION_REQ_IDS, REGISTRY


@dataclass
class RunContext:
    """Every input a registered predicate might need, gathered once per
    target run. `slither` may be None if compilation failed entirely --
    every SLITHER-needing predicate then reports COMPILATION_FAILURE
    rather than crashing on `None`.
    """
    slither: object | None
    sol_source_paths: list[Path] = field(default_factory=list)
    repo_root: Path | None = None
    sol_test_paths: list[Path] = field(default_factory=list)
    entry_sol_file: Path | None = None
    """The single entry file this run targets -- distinct from
    `sol_source_paths` (every .sol file in the whole project, including
    vendored dependencies under lib/). Added for
    `collect_documentary_and_implementation_evidence`, which needs "the
    Tested Code's own file," not the whole repository's source tree."""


def load_unconditioned_map(corpus_path: Path) -> dict[str, bool]:
    """req_id -> is_unconditioned_subject, read directly from the frozen
    L1 corpus (never re-derived/guessed) -- see outcome (2)/(3) above.
    """
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    out = {}
    for r in data["requirements"]:
        csc = r.get("conditioned_scope_clause") or {}
        out[r["req_id"]] = bool(csc.get("is_unconditioned_subject", False))
    return out


def load_requirement_levels(corpus_path: Path) -> dict[str, str]:
    """req_id -> EthTrust level ('S'/'M'/'Q'/'GP'), read directly from the
    frozen L1 corpus. Used by `pipeline_e2e.compute_aggregation_requirements`
    to group requirements by level for req-2-pass-l1 (AND over Level S)
    and req-3-pass-l2 (AND over Level M) -- see `registry.AGGREGATION_REQ_IDS`.
    """
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    return {r["req_id"]: r["level"] for r in data["requirements"]}


def _run_predicate_spec(spec, req_id: str, ctx: RunContext):
    """Invoke one PredicateSpec. Returns (findings, OperationalStatus, error_detail)."""
    for need in spec.needs:
        if getattr(ctx, need, None) in (None, []):
            missing_detail = f"required input '{need}' not available for this run"
            if need == "slither":
                return [], OperationalStatus.COMPILATION_FAILURE, missing_detail
            return [], OperationalStatus.ENVIRONMENT_FAILURE, missing_detail
    kwargs = dict(spec.extra_kwargs)
    if spec.passes_req_id:
        kwargs["req_id"] = req_id
    for need in spec.needs:
        kwargs[need] = getattr(ctx, need)
    try:
        return spec.func(**kwargs), OperationalStatus.OK, None
    except Exception as e:  # noqa: BLE001 -- deliberately broad: any predicate exception must degrade to ANALYZER_CRASH for THIS req_id only, never propagate
        return [], OperationalStatus.ANALYZER_CRASH, f"{type(e).__name__}: {e}\n{traceback.format_exc()}"


def run_rtf(
    ctx: RunContext,
    audit_id: str,
    unconditioned_map: dict[str, bool],
    known_limitations: dict[str, str] | None = None,
) -> tuple[TargetRunResult, dict]:
    """Run every registered predicate against `ctx`.

    `known_limitations`: req_id -> human-readable reason, for
    requirements known IN ADVANCE to hit a documented tool limitation for
    this specific target (e.g. AR-008's Slither Yul-parser crash) --
    marked `PARSER_LIMITATION` directly rather than letting the crash
    happen and get misclassified as a generic `ANALYZER_CRASH`.

    Returns (TargetRunResult for metrics.py, full raw JSON-able dict for
    archival).
    """
    known_limitations = known_limitations or {}
    routed: dict[str, RoutedRequirementResult] = {}
    raw: dict[str, dict] = {}

    # The FULL requirement corpus, not `REGISTRY.keys()` -- see module
    # docstring outcomes (4)/(5). `unconditioned_map` is built directly
    # from the complete L1 corpus (`load_unconditioned_map` iterates
    # every entry in `requirement_corpus.json`), so its key set already
    # IS the full 81-requirement universe with no separate corpus load
    # needed here.
    for req_id in unconditioned_map:
        if req_id in AGGREGATION_REQ_IDS:
            routed[req_id] = RoutedRequirementResult(
                req_id=req_id, applicability_state=ApplicabilityState.APPLICABLE,
                operational_status=OperationalStatus.OK, conformance_state=None, evidence=(),
            )
            raw[req_id] = {
                "applicability_state": "APPLICABLE", "operational_status": "OK",
                "conformance_state": None, "evidence": [], "errors": [],
                "note": "pure aggregation requirement -- resolved post-hoc by "
                        "pipeline_e2e.compute_aggregation_requirements, not here",
            }
            continue

        specs = REGISTRY.get(req_id)
        if specs is None:
            # No predicate, no aggregation rule -- genuinely unsupported.
            # Fail loudly rather than silently omit: see module docstring
            # outcome (5). After the runtime-coverage-audit fixes this
            # branch should not currently trigger for any of the 81
            # corpus requirements -- it exists so a FUTURE requirement
            # added to the corpus without a registered mechanism is
            # caught immediately instead of silently repeating this exact
            # gap.
            routed[req_id] = RoutedRequirementResult(
                req_id=req_id, applicability_state=ApplicabilityState.APPLICABLE,
                operational_status=OperationalStatus.UNSUPPORTED_ANALYZER, conformance_state=None, evidence=(),
            )
            raw[req_id] = {
                "applicability_state": "APPLICABLE", "operational_status": "UNSUPPORTED_ANALYZER",
                "conformance_state": None, "evidence": [],
                "errors": [f"no predicate, documentary-evidence collector, or aggregation rule "
                           f"registered for {req_id!r}"],
            }
            continue

        all_evidence: list[EvidenceItem] = []
        op_status = OperationalStatus.OK
        errors: list[str] = []

        if req_id in known_limitations:
            op_status = OperationalStatus.PARSER_LIMITATION
            errors.append(known_limitations[req_id])
        else:
            for spec in specs:
                findings, status, err = _run_predicate_spec(spec, req_id, ctx)
                if status != OperationalStatus.OK:
                    op_status = status
                    errors.append(err)
                    continue
                for f in findings:
                    all_evidence.append(EvidenceItem(
                        predicate=getattr(spec.func, "__name__", str(spec.func)),
                        location=f.get("location", "?"),
                        detail=f.get("detail", ""),
                        structured=f.get("structured_evidence"),
                    ))

        conformance: ConformanceState | None = None
        if op_status == OperationalStatus.OK:
            unconditioned = unconditioned_map.get(req_id, False)
            if all_evidence:
                applicability = ApplicabilityState.APPLICABLE
                # conformance stays None -- judgment deferred to L8, see module docstring outcome (1)
            elif unconditioned:
                applicability = ApplicabilityState.APPLICABLE
                conformance = ConformanceState.PASS
            else:
                applicability = ApplicabilityState.NOT_APPLICABLE
        else:
            applicability = ApplicabilityState.APPLICABILITY_UNKNOWN

        routed[req_id] = RoutedRequirementResult(
            req_id=req_id,
            applicability_state=applicability,
            operational_status=op_status,
            conformance_state=conformance,
            evidence=tuple(all_evidence),
        )
        raw[req_id] = {
            "applicability_state": applicability.value,
            "operational_status": op_status.value,
            "conformance_state": conformance.value if conformance else None,
            "evidence": [asdict(e) for e in all_evidence],
            "errors": errors,
        }

    return TargetRunResult(audit_id=audit_id, routed=routed), raw


def build_context_for_evmbench_target(
    entry_sol_file: Path,
    project_root: Path,
    solc_version: str,
    sol_source_paths: list[Path] | None = None,
    sol_test_paths: list[Path] | None = None,
) -> tuple[RunContext, str | None]:
    """Compile a real EVMbench target and build its RunContext. Returns
    (ctx, compilation_error_or_None) -- compilation failure does not
    raise, it returns a ctx with `slither=None` plus the error string, so
    callers can still run source-text-only predicates
    (`sol_source_paths`-only ones) even when Slither compilation itself
    fails, rather than losing the whole run to one failure.
    """
    try:
        slither = compile_evmbench_target(entry_sol_file, project_root, solc_version)
        error = None
    except Exception as e:  # noqa: BLE001
        slither = None
        error = f"{type(e).__name__}: {e}"

    if sol_source_paths is None:
        sol_source_paths = sorted(project_root.rglob("*.sol"))
    if sol_test_paths is None:
        sol_test_paths = [p for p in sol_source_paths if "test" in p.parts]

    ctx = RunContext(
        slither=slither,
        sol_source_paths=sol_source_paths,
        repo_root=project_root,
        sol_test_paths=sol_test_paths,
        entry_sol_file=entry_sol_file,
    )
    return ctx, error


def collect_tool_versions() -> dict:
    """Tool/compiler/library versions for this run -- required by the
    plan's step 6 ("preserve ... tool/compiler/model versions").
    """
    def _v(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception as e:  # noqa: BLE001
            return f"UNAVAILABLE: {e}"

    import slither as _slither_pkg

    return {
        "python": sys.version,
        "slither_version": getattr(_slither_pkg, "__version__", "unknown"),
        "solc_select_versions": _v(["solc-select", "versions"]),
    }
