#!/usr/bin/env python3
"""Generic, reusable CLI runner for the model-evaluation harness.

    python3 rtf/security_agent/eval/run_model_eval.py \\
        --model deepseek-v4-pro \\
        --audit 2024-01-canto-rootcause-fix-full-rerun \\
        --property req-3-implement-as-documented::loc0 \\
        --runs 3

Selecting a new candidate model requires ONE new entry in
`model_registry.MODEL_REGISTRY` -- never a new one-off script, the
explicit requirement this generalizes away from the pattern
`glm53_capability_test_launch.py`/`gpt56sol_capability_test_launch.py`
each hand-rolled once.

Everything that must import from the FROZEN baseline checkout (a61d547 +
the independent rank_evidence fix, 881eeb3 -- the exact scaffold GLM-5.3
and GPT-5.6 Sol were already tested against, so every future model stays
comparable to those existing results) happens in a separate subprocess,
`_frozen_worker.py`, never in this process -- see that module's docstring
for why an in-process import would be unsafe here.

Secrets: the API key is resolved once here (env var or the shared key
file, via `model_registry.resolve_api_key`) and passed to the worker
subprocess only via the `MODEL_EVAL_API_KEY` environment variable, never
on argv and never written into config.json/result.json/summary.json.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_WORKER_SCRIPT = _THIS_DIR / "_frozen_worker.py"

sys.path.insert(0, str(_THIS_DIR.parent.parent.parent))  # repo root, for `rtf.security_agent.eval.*` imports
from rtf.security_agent.eval.model_registry import MODEL_REGISTRY, get_model_config, resolve_api_key
from rtf.security_agent.eval.preflight import run_preflight
from rtf.security_agent.eval.scenario_scorer import CounterexampleLevel, score_canto_gate_run

DEFAULT_BASELINE_CHECKOUT = "/scratch/md5344/.claude/jobs/c1eeff9d/tmp/glm53_baseline_checkout"
DEFAULT_GENERATION_CACHE_DIR = "/scratch/md5344/evmbench/rtf_canto_live_foundry_combined_20260815/llm_cache"
DEFAULT_OUTPUT_ROOT = "/scratch/md5344/evmbench/experiments/model_eval"

_BASELINE_CHECKOUT_NOTES = (
    "Pinned at commit a61d547 (\"security_agent: fix 3 confirmed root causes of zero "
    "natural-conclusion clusters\") with rtf/l11_investigation_grouping/evidence_ranking.py "
    "copied in from 881eeb3 (an independent, non-overlapping rank_evidence scope-filter "
    "fix) via plain file copy, NOT a git operation. The anti-anchoring PASS gate (73bf68c) "
    "is intentionally absent -- a61d547 predates it. rtf/security_agent/tools.py's "
    "build_tool_schemas() is patched (in this checkout only) to always list every tool "
    "parameter in `required`, fixing a real OpenAI/Azure strict-schema incompatibility "
    "(GLM-family providers tolerate an omitted-with-default parameter; OpenAI's own "
    "validator rejects it outright) discovered live during the GPT-5.6 Sol test -- a "
    "wire-contract fix, not a tool-behavior change. This exact checkout is what every "
    "prior GLM-5.3/GPT-5.6-Sol capability-test result in this project was produced "
    "against; kept fixed here so every new model result stays directly comparable."
)


@dataclass(frozen=True)
class AuditConfig:
    audit_id: str
    repo_root: str
    scope_files: list[str]
    solc_version: str
    entry_file_relative: str


# Deliberately just the one frozen Canto gate case (Phase 6/12: build
# support for a broader suite later, do not populate it yet).
AUDIT_REGISTRY: dict[str, AuditConfig] = {
    "2024-01-canto-rootcause-fix-full-rerun": AuditConfig(
        audit_id="2024-01-canto-rootcause-fix-full-rerun",
        repo_root="/scratch/md5344/.claude/jobs/a22997fe/tmp/checkouts/2024-01-canto",
        scope_files=["src/LendingLedger.sol"],
        solc_version="0.8.17",
        entry_file_relative="src/LendingLedger.sol",
    ),
}

# Per (audit_id, property_id): a function (state_path, property_id) ->
# (target_bug_found: bool, level: CounterexampleLevel). Registering a
# property here is a DELIBERATE, explicit step -- an audit/property with
# no evaluator refuses to run live (see `_evaluate_target` below) rather
# than silently falling back to "verdict == FAIL", which the task spec
# explicitly warns is not sufficient (a correct FAIL for the WRONG
# vulnerability must count as a miss).
def _canto_gate_evaluator(state_path: Path, property_id: str) -> tuple[bool, CounterexampleLevel]:
    score = score_canto_gate_run(state_path, property_id)
    return score.level == CounterexampleLevel.TARGET_BUG_TRACED, score.level


SUCCESS_EVALUATORS = {
    ("2024-01-canto-rootcause-fix-full-rerun", "req-3-implement-as-documented::loc0"): _canto_gate_evaluator,
    # Added 2026-08-28: the property Sol's own full-audit run actually
    # traced the target bug through (req-3-all-valid-inputs::loc0), NOT
    # the one every single-property capability test above used --
    # registered so a candidate model can be gated against the
    # better-fitting property directly, separating "wrong property
    # framing" from "model can't do this reasoning at all."
    # `_canto_gate_evaluator` already takes `property_id` as a parameter
    # with no hardcoding, so no new function is needed.
    ("2024-01-canto-rootcause-fix-full-rerun", "req-3-all-valid-inputs::loc0"): _canto_gate_evaluator,
}


def evaluate_qualification(target_hits: list[bool]) -> str:
    """Phase 6/10 stopping rule, as a pure function so it is independently
    testable without any live call (Phase 16 Test 6/7). Operates on an
    ACCUMULATING list -- call again with 2 more entries appended after a
    BORDERLINE result to get the up-to-5 decision."""
    n = len(target_hits)
    hits = sum(1 for h in target_hits if h)
    if n == 3:
        if hits == 3:
            return "PASS_QUALIFICATION"
        if hits == 2:
            return "BORDERLINE_RUN_2_MORE"
        return "FAIL_QUALIFICATION"
    if n == 5:
        return "PASS_QUALIFICATION" if hits >= 4 else "MIXED"
    if n == 1:
        # Sol-style single-run control check (Phase 13): not a full
        # qualification verdict, just a direct pass/fail on that one run.
        return "SINGLE_RUN_SUCCESS" if hits == 1 else "SINGLE_RUN_MISS"
    raise ValueError(f"evaluate_qualification called with {n} results -- expected 1, 3, or 5")


def _slug(property_id: str) -> str:
    return property_id.replace("::", "_").replace("/", "_")


def _emit_tool_schemas(*, baseline_checkout: str, result_path: Path) -> None:
    """One cheap subprocess call to get the FROZEN checkout's real tool
    schema list (no pipeline regen, no investigation) -- see
    `_frozen_worker.py --emit-tool-schemas` and `preflight.py`'s module
    docstring for why preflight must test this exact list, not the
    worktree's own possibly-different copy."""
    cmd = [sys.executable, str(_WORKER_SCRIPT), "--baseline-checkout", baseline_checkout,
           "--emit-tool-schemas", "--result-path", str(result_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"--emit-tool-schemas failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")


def _run_worker(*, baseline_checkout: str, audit: AuditConfig, property_id: str, model_id: str,
                 reasoning_effort: str, case_id: str, scratch_root: Path, api_key: str,
                 generation_cache_dir: str, generation_tokens_log: Path,
                 max_steps: int, max_cost_usd: float, max_wall_clock_s: float,
                 result_path: Path, dry_run: bool) -> dict:
    cmd = [
        sys.executable, str(_WORKER_SCRIPT),
        "--baseline-checkout", baseline_checkout,
        "--audit-id", audit.audit_id,
        "--repo-root", audit.repo_root,
        "--scope-files", json.dumps(audit.scope_files),
        "--solc-version", audit.solc_version,
        "--entry-file-relative", audit.entry_file_relative,
        "--property-id", property_id,
        "--model", model_id,
        "--reasoning-effort", reasoning_effort,
        "--case-id", case_id,
        "--scratch-root", str(scratch_root),
        "--generation-cache-dir", generation_cache_dir,
        "--generation-tokens-log", str(generation_tokens_log),
        "--max-steps", str(max_steps),
        "--max-cost-usd", str(max_cost_usd),
        "--max-wall-clock-s", str(max_wall_clock_s),
        "--result-path", str(result_path),
    ]
    if dry_run:
        cmd.append("--dry-run")
    env = dict(os.environ)
    env["MODEL_EVAL_API_KEY"] = api_key
    # Real bug found live (2026-08-27, first DeepSeek qualification
    # attempt): this outer subprocess timeout was `max_wall_clock_s + 120`
    # -- far too tight. `run_security_agent_bundle`'s own internal
    # circuit breaker (`SecurityAgentKernel`'s wall-clock check) is
    # ALWAYS `DEFAULT_MAX_CLUSTER_WALL_CLOCK_S=900.0` regardless of what
    # `timeout_s`/`max_wall_clock_s` is passed in (investigator.py
    # hardcodes it, confirmed by reading the source -- the passed-through
    # value only affects the Codex-specific `timeout_s` path, unused
    # here). Pipeline regeneration (foundry compile + slither + semantic
    # pool rebuild) ALSO happens inside this same subprocess call, before
    # the kernel's breaker clock even starts, adding several more minutes.
    # A 120s margin killed a real, paying run via `TimeoutExpired` before
    # the kernel's own forced-conclusion salvage could finish and write
    # any result.json at all -- real API spend, zero captured data. Fixed
    # with a much more generous margin; `max_wall_clock_s` itself is left
    # alone (it still bounds cost via decide-call cadence, just not via
    # this outer timeout).
    outer_timeout_s = max(max_wall_clock_s, 900.0) + 900.0
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=outer_timeout_s)
    if proc.returncode != 0:
        raise RuntimeError(
            f"worker subprocess failed (exit {proc.returncode}):\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return json.loads(Path(result_path).read_text())


def run_model_eval(*, model_key: str, audit_id: str, property_id: str, runs: int,
                    output_dir: Path, max_steps: int, max_cost_per_run: float, max_wall_clock: float,
                    baseline_checkout: str = DEFAULT_BASELINE_CHECKOUT,
                    key_file: str | None = None, dry_run: bool = False,
                    start_run_index: int = 1, skip_preflight: bool = False) -> dict:
    model_config = get_model_config(model_key)
    audit = AUDIT_REGISTRY[audit_id]
    api_key = resolve_api_key(model_config, key_file) if key_file else resolve_api_key(model_config)

    model_dir = output_dir / audit_id / _slug(property_id) / model_key
    model_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        result_path = model_dir / "dry_run_result.json"
        info = _run_worker(
            baseline_checkout=baseline_checkout, audit=audit, property_id=property_id,
            model_id=model_config.openrouter_model_id, reasoning_effort=model_config.reasoning_effort,
            case_id="dry-run", scratch_root=model_dir / "dry_run_scratch", api_key=api_key,
            generation_cache_dir=DEFAULT_GENERATION_CACHE_DIR,
            generation_tokens_log=model_dir / "dry_run_generation_tokens.jsonl",
            max_steps=max_steps, max_cost_usd=max_cost_per_run, max_wall_clock_s=max_wall_clock,
            result_path=result_path, dry_run=True,
        )
        return {"dry_run": True, **info}

    if not skip_preflight:
        schemas_path = model_dir / "frozen_tool_schemas.json"
        _emit_tool_schemas(baseline_checkout=baseline_checkout, result_path=schemas_path)
        real_tool_schemas = json.loads(schemas_path.read_text())
        preflight = run_preflight(model_config, api_key, tool_schemas=real_tool_schemas)
        preflight_path = model_dir / "preflight_result.json"
        preflight_path.write_text(json.dumps(preflight.__dict__, indent=2, default=str), encoding="utf-8")
        if not preflight.passed:
            raise RuntimeError(
                f"preflight FAILED for {model_key} -- refusing to start the paid RTF run. "
                f"See {preflight_path}. Errors: {preflight.errors}"
            )

    evaluator = SUCCESS_EVALUATORS.get((audit_id, property_id))
    if evaluator is None:
        raise ValueError(
            f"no registered success evaluator for (audit={audit_id!r}, property={property_id!r}) -- "
            "add one to SUCCESS_EVALUATORS before running this combination live "
            "(a correct-verdict-wrong-vulnerability miss must never silently count as a pass)"
        )

    run_records = []
    for i in range(start_run_index, start_run_index + runs):
        case_id = f"run_{i:03d}"
        case_root = model_dir / "security_agent" / case_id
        result_path = case_root.parent / f"{case_id}_result.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        started = time.time()
        worker_summary = _run_worker(
            baseline_checkout=baseline_checkout, audit=audit, property_id=property_id,
            model_id=model_config.openrouter_model_id, reasoning_effort=model_config.reasoning_effort,
            case_id=case_id, scratch_root=model_dir, api_key=api_key,
            generation_cache_dir=DEFAULT_GENERATION_CACHE_DIR,
            generation_tokens_log=model_dir / "generation_tokens.jsonl",
            max_steps=max_steps, max_cost_usd=max_cost_per_run, max_wall_clock_s=max_wall_clock,
            result_path=result_path, dry_run=False,
        )
        state_path = Path(worker_summary["state_path"])
        target_found, level = evaluator(state_path, property_id)

        config_record = {
            "model_key": model_key, "openrouter_model_id": model_config.openrouter_model_id,
            "reasoning_effort": model_config.reasoning_effort,
            "audit_id": audit_id, "property_id": property_id, "case_id": case_id,
            "max_steps": max_steps, "max_cost_usd": max_cost_per_run, "max_wall_clock_s": max_wall_clock,
            "baseline_checkout": baseline_checkout, "baseline_checkout_notes": _BASELINE_CHECKOUT_NOTES,
            "trimmed_plan_sha256": worker_summary.get("trimmed_plan_sha256"),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        (case_root / "config.json").write_text(json.dumps(config_record, indent=2), encoding="utf-8")

        result_record = {
            **worker_summary, "target_bug_found": target_found,
            "counterexample_level": level.name, "counterexample_level_value": int(level),
            "wall_clock_s_including_subprocess_overhead": time.time() - started,
        }
        (case_root / "result.json").write_text(json.dumps(result_record, indent=2, default=str), encoding="utf-8")
        run_records.append(result_record)

    qualification = evaluate_qualification([r["target_bug_found"] for r in run_records]) if runs in (1, 3, 5) else None
    summary = {
        "model_key": model_key, "audit_id": audit_id, "property_id": property_id,
        "runs": run_records, "qualification": qualification,
        "target_detection_rate": sum(1 for r in run_records if r["target_bug_found"]) / len(run_records),
        "total_cost_usd": sum(r["cost_usd"] for r in run_records),
        "cost_per_correct_detection_usd": (
            sum(r["cost_usd"] for r in run_records) / sum(1 for r in run_records if r["target_bug_found"])
            if any(r["target_bug_found"] for r in run_records) else None
        ),
    }
    summary_path = model_dir / "summary.json"
    if summary_path.exists() and start_run_index > 1:
        prior = json.loads(summary_path.read_text())
        merged_runs = prior["runs"] + run_records
        summary["runs"] = merged_runs
        summary["qualification"] = evaluate_qualification([r["target_bug_found"] for r in merged_runs]) \
            if len(merged_runs) in (1, 3, 5) else None
        summary["target_detection_rate"] = sum(1 for r in merged_runs if r["target_bug_found"]) / len(merged_runs)
        summary["total_cost_usd"] = sum(r["cost_usd"] for r in merged_runs)
        summary["cost_per_correct_detection_usd"] = (
            sum(r["cost_usd"] for r in merged_runs) / sum(1 for r in merged_runs if r["target_bug_found"])
            if any(r["target_bug_found"] for r in merged_runs) else None
        )
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


def _cli() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True, choices=sorted(MODEL_REGISTRY))
    p.add_argument("--audit", required=True, dest="audit_id", choices=sorted(AUDIT_REGISTRY))
    p.add_argument("--property", required=True, dest="property_id")
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--start-run-index", type=int, default=1)
    p.add_argument("--max-cost-per-run", type=float, default=0.30)
    p.add_argument("--max-steps", type=int, default=60)
    p.add_argument("--max-wall-clock", type=float, default=900.0)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_ROOT)
    p.add_argument("--baseline-checkout", default=DEFAULT_BASELINE_CHECKOUT)
    p.add_argument("--key-file", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-preflight", action="store_true", help="Escape hatch only -- never use for a real run.")
    args = p.parse_args()

    summary = run_model_eval(
        model_key=args.model, audit_id=args.audit_id, property_id=args.property_id, runs=args.runs,
        output_dir=Path(args.output_dir), max_steps=args.max_steps, max_cost_per_run=args.max_cost_per_run,
        max_wall_clock=args.max_wall_clock, baseline_checkout=args.baseline_checkout,
        key_file=args.key_file, dry_run=args.dry_run, start_run_index=args.start_run_index,
        skip_preflight=args.skip_preflight,
    )
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    _cli()
