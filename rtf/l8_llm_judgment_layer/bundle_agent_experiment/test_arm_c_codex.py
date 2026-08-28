"""Deterministic tests for run_arm_c_bundle's optional reasoning_effort
override (added for the GPT-5.2 "high" baseline comparison). No live
Codex calls -- subprocess.run is monkeypatched."""
from __future__ import annotations

from pathlib import Path

from rtf.l8_llm_judgment_layer.bundle_agent_experiment import arm_c_codex


def _run_with_captured_cmd(tmp_path: Path, monkeypatch, reasoning_effort):
    captured = {}

    def fake_run(cmd, **kwargs):
        # Other subprocess.run calls happen along the way (e.g. git
        # metadata lookups) -- only capture the actual codex invocation.
        if cmd and cmd[0] == "/usr/bin/true":
            captured["cmd"] = cmd
        class _Result:
            pass
        return _Result()

    def fake_login(codex_bin, home, api_key):
        pass

    monkeypatch.setattr(arm_c_codex.subprocess, "run", fake_run)
    monkeypatch.setattr(arm_c_codex, "codex_login", fake_login)

    investigation_dir = tmp_path / "investigation"
    investigation_dir.mkdir()
    arm_c_codex.run_arm_c_bundle(
        codex_bin=Path("/usr/bin/true"), api_key="unused", model="openai/gpt-5.2",
        case_id="test-case", repetition=1, investigation_dir=investigation_dir,
        prompt="do the audit", unresolved_facts=[], scratch_root=tmp_path,
        reasoning_effort=reasoning_effort,
    )
    return captured["cmd"]


def test_reasoning_effort_omitted_by_default(tmp_path, monkeypatch):
    cmd = _run_with_captured_cmd(tmp_path, monkeypatch, reasoning_effort=None)
    assert "-c" not in cmd
    assert not any("model_reasoning_effort" in part for part in cmd)


def test_reasoning_effort_high_forwarded_as_config_override(tmp_path, monkeypatch):
    cmd = _run_with_captured_cmd(tmp_path, monkeypatch, reasoning_effort="high")
    assert "-c" in cmd
    idx = cmd.index("-c")
    assert cmd[idx + 1] == "model_reasoning_effort=high"
