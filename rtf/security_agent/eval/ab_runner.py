"""Controlled two-arm runner: identical cluster inputs, investigator only varies."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from rtf.security_agent.eval.ab_metrics import ABMetrics, compare_results


@dataclass(frozen=True)
class ABRunResult:
    input_fingerprint: str
    codex_result: object
    security_agent_result: object
    metrics: ABMetrics


_FAIRNESS_KEYS = (
    "model", "case_id", "entry_file", "repo_root", "candidate_location",
    "solc_path_dir", "solc_remaps", "prompt", "timeout_s", "extra_files",
    "compile_via_foundry",
)


def input_fingerprint(bundle_kwargs: dict) -> str:
    missing = [key for key in _FAIRNESS_KEYS if key not in bundle_kwargs]
    if missing:
        raise ValueError(f"A/B bundle inputs missing fairness keys: {missing}")
    payload = {key: bundle_kwargs[key] for key in _FAIRNESS_KEYS}
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def run_ab_comparison(
    *, bundle_kwargs: dict, codex_runner: Callable[..., object],
    security_agent_runner: Callable[..., object], report_path: Path | None = None,
) -> ABRunResult:
    """Run both arms sequentially with shallow copies of the same kwargs.

    Sequential execution avoids concurrency/provider-load as an accidental
    variable in the first comparison. Each runner receives identical values;
    the fingerprint makes that preregistered input auditable.
    """
    fingerprint = input_fingerprint(bundle_kwargs)
    codex_result = codex_runner(**dict(bundle_kwargs))
    security_result = security_agent_runner(**dict(bundle_kwargs))
    metrics = compare_results(codex_result, security_result)
    result = ABRunResult(fingerprint, codex_result, security_result, metrics)
    if report_path is not None:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(json.dumps({
            "input_fingerprint": fingerprint,
            "metrics": metrics.to_dict(),
        }, indent=2, sort_keys=True), encoding="utf-8")
    return result
