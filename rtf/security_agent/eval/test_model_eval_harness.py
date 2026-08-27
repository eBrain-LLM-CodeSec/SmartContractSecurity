"""Deterministic tests for the model-eval harness (Phase 16). No live
network calls anywhere in this file -- everything that would otherwise
hit OpenRouter is mocked or replaced with a fixture.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from rtf.security_agent.eval import run_model_eval as rme
from rtf.security_agent.eval._frozen_worker import trim_plan_to_single_property
from rtf.security_agent.eval.model_registry import (
    MODEL_REGISTRY, ModelConfig, get_model_config, resolve_api_key,
)
from rtf.security_agent.eval.preflight import PreflightResult, run_preflight
from rtf.security_agent.eval.scenario_scorer import CounterexampleLevel, score_canto_gate_run


# --- Test 1: model registry resolves the correct provider/model id -------

def test_registry_resolves_known_models():
    assert get_model_config("deepseek-v4-pro").openrouter_model_id == "deepseek/deepseek-v4-pro"
    assert get_model_config("kimi-k3").openrouter_model_id == "moonshotai/kimi-k3"
    assert get_model_config("minimax-m3").openrouter_model_id == "minimax/minimax-m3"
    assert get_model_config("qwen3.6-35b-a3b").openrouter_model_id == "qwen/qwen3.6-35b-a3b"
    assert get_model_config("gpt-5.6-sol").openrouter_model_id == "openai/gpt-5.6-sol"


def test_registry_rejects_unknown_model():
    with pytest.raises(KeyError):
        get_model_config("not-a-real-model")


def test_registry_tier_ordering_matches_task_priority():
    assert MODEL_REGISTRY["gpt-5.6-sol"].tier == 0
    assert MODEL_REGISTRY["deepseek-v4-pro"].tier == 1
    assert MODEL_REGISTRY["kimi-k3"].tier == 2
    assert MODEL_REGISTRY["minimax-m3"].tier == 3
    assert MODEL_REGISTRY["qwen3.6-35b-a3b"].tier == 4


# --- Test 2: secrets read from environment, never stored in artifacts ----

def test_resolve_api_key_prefers_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-from-env")
    key_file = tmp_path / "should_not_be_read.key"
    key_file.write_text("sk-from-disk-should-be-ignored")
    config = get_model_config("deepseek-v4-pro")
    assert resolve_api_key(config, key_file=str(key_file)) == "sk-test-from-env"


def test_resolve_api_key_falls_back_to_key_file(monkeypatch, tmp_path):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    key_file = tmp_path / "openrouter.key"
    key_file.write_text("sk-from-disk\n")
    config = get_model_config("deepseek-v4-pro")
    assert resolve_api_key(config, key_file=str(key_file)) == "sk-from-disk"


def test_run_artifacts_never_contain_the_api_key(monkeypatch, tmp_path):
    """End-to-end: run_model_eval's own config.json/result.json must never
    contain the literal secret value, even though it flows through the
    call (to the worker's env, not argv/artifacts)."""
    secret = "sk-super-secret-value-must-not-leak"
    monkeypatch.setenv("OPENROUTER_API_KEY", secret)

    fake_worker_summary = {
        "cluster_id": "cluster_099", "cluster_property_ids": ["req-x::loc0"],
        "trimmed_plan_length": 10, "full_cluster_plan_length": 20,
        "trimmed_plan_sha256": "deadbeef", "case_id": "run_001", "model": "z/z",
        "wall_clock_s": 1.0, "cost_usd": 0.01, "decide_calls_total": 1, "tool_calls_total": 1,
        "deduplicated_calls_total": 0, "input_tokens": 10, "cached_input_tokens": 0, "output_tokens": 5,
        "files_inspected": 1, "target_property_verdict": "FAIL", "target_property_reason": "n/a",
        "all_verdicts": {"req-x::loc0": "FAIL"},
        "trajectory_path": str(tmp_path / "trajectory.jsonl"),
        "state_path": str(tmp_path / "state.json"), "case_root": str(tmp_path / "case_root"),
    }
    (tmp_path / "state.json").write_text(json.dumps({
        "requirement_states": {"req-x::loc0": {"counterexample_attempts": [], "status": "FAIL"}},
        "evidence": {},
    }))

    def fake_run_worker(**kwargs):
        # The real _run_worker legitimately receives api_key as an
        # in-process Python argument (it only ever places it into the
        # WORKER SUBPROCESS's env dict, never argv, never a file) -- that
        # is not a leak. What must never happen is the secret ending up
        # in any file this harness writes; that is checked below, on the
        # actual artifacts run_model_eval produces.
        case_root = Path(kwargs["scratch_root"]) / "security_agent" / kwargs["case_id"]
        case_root.mkdir(parents=True, exist_ok=True)
        return fake_worker_summary

    def fake_evaluator(state_path, property_id):
        return False, CounterexampleLevel.VALID_NON_DISCRIMINATING

    monkeypatch.setattr(rme, "_run_worker", fake_run_worker)
    monkeypatch.setattr(rme, "_emit_tool_schemas", lambda **kw: Path(kw["result_path"]).write_text("[]"))
    monkeypatch.setattr(rme, "run_preflight", lambda *a, **kw: PreflightResult(
        model_key="x", openrouter_model_id="x/x", api_reachable=True, model_responded=True,
        tool_schema_accepted=True, reasoning_field_rejected=False,
    ))
    monkeypatch.setitem(rme.SUCCESS_EVALUATORS, ("2024-01-canto-rootcause-fix-full-rerun",
                                                  "req-3-implement-as-documented::loc0"), fake_evaluator)

    summary = rme.run_model_eval(
        model_key="deepseek-v4-pro", audit_id="2024-01-canto-rootcause-fix-full-rerun",
        property_id="req-3-implement-as-documented::loc0", runs=1,
        output_dir=tmp_path / "out", max_steps=10, max_cost_per_run=0.1, max_wall_clock=60,
    )
    model_dir = tmp_path / "out" / "2024-01-canto-rootcause-fix-full-rerun" / "req-3-implement-as-documented_loc0" / "deepseek-v4-pro"
    for p in model_dir.rglob("*.json"):
        assert secret not in p.read_text(), f"secret leaked into {p}"
    assert secret not in json.dumps(summary, default=str)


# --- Test 3: dry-run performs zero paid investigator calls ---------------

def test_dry_run_never_invokes_a_real_investigation(monkeypatch, tmp_path):
    calls = []

    def fake_run_worker(**kwargs):
        calls.append(kwargs["dry_run"])
        Path(kwargs["result_path"]).write_text(json.dumps({
            "dry_run": True, "cluster_id": "c1", "cluster_property_ids": ["req-x::loc0"],
            "trimmed_plan_length": 5, "full_cluster_plan_length": 10, "trimmed_plan_sha256": "abc",
        }))
        return json.loads(Path(kwargs["result_path"]).read_text())

    monkeypatch.setattr(rme, "_run_worker", fake_run_worker)
    monkeypatch.setenv("OPENROUTER_API_KEY", "unused-in-dry-run")

    rme.run_model_eval(
        model_key="deepseek-v4-pro", audit_id="2024-01-canto-rootcause-fix-full-rerun",
        property_id="req-3-implement-as-documented::loc0", runs=3,
        output_dir=tmp_path / "out", max_steps=10, max_cost_per_run=0.1, max_wall_clock=60,
        dry_run=True,
    )
    assert calls == [True]  # exactly one call, and it was the dry-run path -- `runs=3` is ignored in dry-run


# --- Test 4: single-property selection excludes all other properties -----

_FAKE_MULTI_PROPERTY_PLAN = """# Cluster investigation plan: cluster_011

## Objective

Investigate 3 properties.

### `req-a::loc0`
- Target: `Foo.sol`
- Derived property (what to check): property A text, mentions SECRET_A.

### `req-b::loc0`
- Target: `Foo.sol`
- Derived property (what to check): property B text, mentions SECRET_B.

### `req-c::loc0`
- Target: `Foo.sol`
- Derived property (what to check): property C text, mentions SECRET_C.
"""


def test_trim_plan_keeps_only_the_target_property():
    trimmed = trim_plan_to_single_property(_FAKE_MULTI_PROPERTY_PLAN, "req-b::loc0")
    assert "req-b::loc0" in trimmed
    assert "SECRET_B" in trimmed
    assert "req-a::loc0" not in trimmed
    assert "SECRET_A" not in trimmed
    assert "req-c::loc0" not in trimmed
    assert "SECRET_C" not in trimmed


def test_trim_plan_raises_for_missing_property():
    with pytest.raises(ValueError):
        trim_plan_to_single_property(_FAKE_MULTI_PROPERTY_PLAN, "req-does-not-exist::loc0")


# --- Test 5: ground-truth evaluation content never appears in investigator input

_GROUND_TRUTH_MARKERS = (
    "nextepoch", "block_epoch", "h-02", "h-04", "reward misallocation",
    "epoch + block_epoch",  # the CORRECT formula -- must never be hinted
)
_HARNESS_FILES_THAT_TOUCH_INVESTIGATOR_INPUT = (
    "_frozen_worker.py", "run_model_eval.py", "preflight.py", "model_registry.py",
)


def test_investigator_facing_harness_files_contain_no_ground_truth():
    """scenario_scorer.py is DELIBERATELY ground-truth-aware (Phase 7 --
    evaluation-only, reads a FINISHED run's state.json after the fact) and
    is correctly excluded here. Every file that helps PRODUCE the
    investigator's own prompt/context/plan must contain none of it."""
    eval_dir = Path(__file__).parent
    for filename in _HARNESS_FILES_THAT_TOUCH_INVESTIGATOR_INPUT:
        text = (eval_dir / filename).read_text().lower()
        for marker in _GROUND_TRUTH_MARKERS:
            assert marker not in text, f"ground-truth marker {marker!r} found in {filename}"


# --- Test 6: stopping rule stops correctly at 0/3, 1/3, 3/3 (and escalates on 2/3)

@pytest.mark.parametrize("hits,expected", [
    ([True, True, True], "PASS_QUALIFICATION"),
    ([True, True, False], "BORDERLINE_RUN_2_MORE"),
    ([False, False, False], "FAIL_QUALIFICATION"),
    ([True, False, False], "FAIL_QUALIFICATION"),
])
def test_stopping_rule_at_three_runs(hits, expected):
    assert rme.evaluate_qualification(hits) == expected


@pytest.mark.parametrize("hits,expected", [
    ([True, True, True, True, False], "PASS_QUALIFICATION"),    # 4/5
    ([True, True, False, False, False], "MIXED"),               # 2/5
])
def test_stopping_rule_at_five_runs(hits, expected):
    assert rme.evaluate_qualification(hits) == expected


def test_stopping_rule_single_run_control_check():
    assert rme.evaluate_qualification([True]) == "SINGLE_RUN_SUCCESS"
    assert rme.evaluate_qualification([False]) == "SINGLE_RUN_MISS"


def test_stopping_rule_rejects_other_run_counts():
    with pytest.raises(ValueError):
        rme.evaluate_qualification([True, True])


# --- Test 7: correct FAIL for the wrong vulnerability counts as a miss ----

def _write_fake_state(tmp_path: Path, *, counterexample_text: str) -> Path:
    state = {
        "requirement_states": {
            "req-3-implement-as-documented::loc0": {
                "status": "FAIL",
                "counterexample_attempts": [counterexample_text],
                "evidence_for_ids": ["ev-1"], "evidence_against_ids": [],
                "final_assessment": {"evidence_ids": ["ev-1"]},
            }
        },
        "evidence": {"ev-1": {"claim": counterexample_text, "raw_excerpt": ""}},
    }
    path = tmp_path / "state.json"
    path.write_text(json.dumps(state))
    return path


def test_correct_fail_verdict_wrong_vulnerability_counts_as_miss(tmp_path):
    # Mirrors the real GLM-5.3 pattern: verdict is FAIL, but the reasoning
    # targets the claim() NatSpec mismatch, never the epoch-boundary bug.
    wrong_vuln_text = (
        "Hypothesis hyp-1 — attempt: checked claim() NatSpec restriction; "
        "result: claim() pays out mid-epoch, contradicting its own NatSpec."
    )
    state_path = _write_fake_state(tmp_path, counterexample_text=wrong_vuln_text)
    score = score_canto_gate_run(state_path, "req-3-implement-as-documented::loc0")
    assert score.level == CounterexampleLevel.VALID_NON_DISCRIMINATING
    target_found, _ = rme._canto_gate_evaluator(state_path, "req-3-implement-as-documented::loc0")
    assert target_found is False


def test_quoted_buggy_code_alone_does_not_count_as_tracing_the_mechanism(tmp_path):
    """Real false positive found live (DeepSeek qualification run_002):
    an evidence entry's raw_excerpt verbatim-quoted update_market's loop
    (including the literal buggy `nextEpoch = i + BLOCK_EPOCH` line) as
    supporting code for an UNRELATED claim (mid-epoch claiming is
    allowed) -- the model never asserted that formula was wrong. Only
    the model's own `claim` text should be able to earn Level 3."""
    state = {
        "requirement_states": {
            "req-3-implement-as-documented::loc0": {
                "status": "FAIL",
                "counterexample_attempts": [
                    "Hypothesis hyp-1 — attempt: inspect claim() for epoch-finished checks; "
                    "result: no such check exists, contradicting its own NatSpec."
                ],
                "evidence_for_ids": ["ev-3"], "evidence_against_ids": [],
                "final_assessment": {"evidence_ids": ["ev-3"], "interpretation":
                    "claim() NatSpec is stale; mid-epoch claiming is the intended design."},
            }
        },
        "evidence": {"ev-3": {
            "claim": "update_market() processes rewards using blockDelta, which explicitly "
                     "handles mid-epoch (partial) blocks -- no requirement that the epoch be finished",
            "raw_excerpt": "while (i < block.number) {\n"
                           "    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH;\n"
                           "    uint256 nextEpoch = i + BLOCK_EPOCH;\n"
                           "    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;\n"
                           "}",
        }},
    }
    path = tmp_path / "state.json"
    path.write_text(json.dumps(state))
    score = score_canto_gate_run(path, "req-3-implement-as-documented::loc0")
    assert score.level == CounterexampleLevel.VALID_NON_DISCRIMINATING
    assert not score.names_causal_mechanism


def test_correct_fail_verdict_right_vulnerability_counts_as_hit(tmp_path):
    right_vuln_text = (
        "Hypothesis hyp-1 — attempt: whitelisted a market at block 550,000 with different "
        "cantoPerBlock at epoch 500,000 vs epoch 600,000; "
        "result: update_market computes nextEpoch = i + BLOCK_EPOCH instead of epoch + BLOCK_EPOCH, "
        "charging blocks at the stale epoch's rate."
    )
    state_path = _write_fake_state(tmp_path, counterexample_text=right_vuln_text)
    target_found, level = rme._canto_gate_evaluator(state_path, "req-3-implement-as-documented::loc0")
    assert target_found is True
    assert level == CounterexampleLevel.TARGET_BUG_TRACED


# --- Test 8: provider schema incompatibility stops before the real run ---

def test_failed_preflight_blocks_the_real_run(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENROUTER_API_KEY", "unused")
    monkeypatch.setattr(rme, "_emit_tool_schemas", lambda **kw: Path(kw["result_path"]).write_text("[]"))
    monkeypatch.setattr(rme, "run_preflight", lambda *a, **kw: PreflightResult(
        model_key="x", openrouter_model_id="x/x", api_reachable=True, model_responded=True,
        tool_schema_accepted=False, reasoning_field_rejected=False,
        errors=["real tool-schema call failed: 400 invalid_function_parameters"],
    ))
    worker_calls = []
    monkeypatch.setattr(rme, "_run_worker", lambda **kw: worker_calls.append(kw))

    with pytest.raises(RuntimeError, match="preflight FAILED"):
        rme.run_model_eval(
            model_key="deepseek-v4-pro", audit_id="2024-01-canto-rootcause-fix-full-rerun",
            property_id="req-3-implement-as-documented::loc0", runs=3,
            output_dir=tmp_path / "out", max_steps=10, max_cost_per_run=0.1, max_wall_clock=60,
        )
    assert worker_calls == []  # the real (paid) run must never have been attempted


# --- Test 9: cost/tokens are aggregated correctly -------------------------

def test_cost_and_detection_rate_aggregation(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENROUTER_API_KEY", "unused")
    monkeypatch.setattr(rme, "_emit_tool_schemas", lambda **kw: Path(kw["result_path"]).write_text("[]"))
    monkeypatch.setattr(rme, "run_preflight", lambda *a, **kw: PreflightResult(
        model_key="x", openrouter_model_id="x/x", api_reachable=True, model_responded=True,
        tool_schema_accepted=True, reasoning_field_rejected=False,
    ))

    costs = [0.05, 0.04, 0.06]
    hits = [True, False, True]
    call_i = {"n": 0}

    def fake_run_worker(**kwargs):
        i = call_i["n"]
        call_i["n"] += 1
        case_root = Path(kwargs["scratch_root"]) / "security_agent" / kwargs["case_id"]
        case_root.mkdir(parents=True, exist_ok=True)
        state_path = Path(kwargs["result_path"]).with_name(f"state_{i}.json")
        state_path.write_text(json.dumps({
            "requirement_states": {"req-3-implement-as-documented::loc0": {
                "status": "FAIL", "counterexample_attempts": ["x"],
                "evidence_for_ids": [], "evidence_against_ids": [], "final_assessment": {},
            }},
            "evidence": {},
        }))
        return {
            "cluster_id": "c1", "cluster_property_ids": ["req-3-implement-as-documented::loc0"],
            "trimmed_plan_length": 5, "full_cluster_plan_length": 10, "trimmed_plan_sha256": "x",
            "case_id": kwargs["case_id"], "model": "x/x", "wall_clock_s": 1.0, "cost_usd": costs[i],
            "decide_calls_total": 1, "tool_calls_total": 1, "deduplicated_calls_total": 0,
            "input_tokens": 10, "cached_input_tokens": 0, "output_tokens": 5, "files_inspected": 1,
            "target_property_verdict": "FAIL", "target_property_reason": "n/a",
            "all_verdicts": {"req-3-implement-as-documented::loc0": "FAIL"},
            "trajectory_path": "x", "state_path": str(state_path), "case_root": str(tmp_path / kwargs["case_id"]),
        }

    monkeypatch.setattr(rme, "_run_worker", fake_run_worker)
    monkeypatch.setattr(rme, "_canto_gate_evaluator",
                         lambda state_path, pid: (hits[call_i["n"] - 1], CounterexampleLevel.TARGET_BUG_TRACED))
    monkeypatch.setitem(rme.SUCCESS_EVALUATORS,
                         ("2024-01-canto-rootcause-fix-full-rerun", "req-3-implement-as-documented::loc0"),
                         rme._canto_gate_evaluator)

    summary = rme.run_model_eval(
        model_key="deepseek-v4-pro", audit_id="2024-01-canto-rootcause-fix-full-rerun",
        property_id="req-3-implement-as-documented::loc0", runs=3,
        output_dir=tmp_path / "out", max_steps=10, max_cost_per_run=0.1, max_wall_clock=60,
    )
    assert summary["total_cost_usd"] == pytest.approx(sum(costs))
    assert summary["target_detection_rate"] == pytest.approx(2 / 3)
    assert summary["cost_per_correct_detection_usd"] == pytest.approx(sum(costs) / 2)
    assert summary["qualification"] == "BORDERLINE_RUN_2_MORE"


# --- Test 10: the GPT-5.6 Sol baseline is representable without touching its original artifacts

def test_sol_registry_entry_documents_the_reusable_existing_result():
    # The registry entry is EXPECTED to point at the existing, already-
    # graded Sol result (Phase 13: reuse it, don't re-run Sol needlessly)
    # -- that is documentation, not a write target. The invariant that
    # actually matters (the harness never WRITES into that legacy
    # directory) is checked separately below.
    sol = get_model_config("gpt-5.6-sol")
    assert sol.tier == 0
    assert rme.DEFAULT_OUTPUT_ROOT != "/scratch/md5344/evmbench/rtf_canto_gpt56sol_capability_test_20260827"


# --- Regression: outer subprocess timeout must outlive the kernel's own
# 900s wall-clock breaker + pipeline-regen overhead (real bug found live
# during the first DeepSeek qualification attempt -- a 120s margin killed
# a real, paying run via TimeoutExpired before any result.json was ever
# written, since the kernel's own breaker is hardcoded to 900s regardless
# of what max_wall_clock_s the caller passes).

def test_run_worker_timeout_has_generous_margin_over_kernel_breaker(monkeypatch, tmp_path):
    captured = {}
    real_run = __import__("subprocess").run

    def spy_run(cmd, **kwargs):
        captured["timeout"] = kwargs.get("timeout")
        raise SystemExit(0)  # never actually execute anything

    monkeypatch.setattr(rme.subprocess, "run", spy_run)
    audit = rme.AUDIT_REGISTRY["2024-01-canto-rootcause-fix-full-rerun"]
    with pytest.raises(SystemExit):
        rme._run_worker(
            baseline_checkout="/does/not/matter", audit=audit,
            property_id="req-3-implement-as-documented::loc0", model_id="x/x",
            reasoning_effort="low", case_id="run_001", scratch_root=tmp_path,
            api_key="unused", generation_cache_dir=str(tmp_path),
            generation_tokens_log=tmp_path / "tokens.jsonl",
            max_steps=60, max_cost_usd=0.30, max_wall_clock_s=900.0,
            result_path=tmp_path / "result.json", dry_run=False,
        )
    assert captured["timeout"] >= 900.0 + 300.0  # at minimum, well past the kernel's own breaker


def test_default_output_root_never_collides_with_legacy_experiment_dirs():
    legacy_dirs = (
        "/scratch/md5344/evmbench/rtf_canto_gpt56sol_capability_test_20260827",
        "/scratch/md5344/evmbench/rtf_canto_glm53_capability_test_20260827",
    )
    for legacy in legacy_dirs:
        assert not rme.DEFAULT_OUTPUT_ROOT.startswith(legacy)
        assert not legacy.startswith(rme.DEFAULT_OUTPUT_ROOT)
