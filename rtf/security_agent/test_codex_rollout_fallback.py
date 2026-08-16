import json

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import recover_codex_rollout
from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_c_codex import (
    _extract_last_fenced_json, _extract_touched_files,
)


def test_recovers_final_message_and_usage_from_latest_rollout(tmp_path):
    rollout = tmp_path / ".codex/sessions/2026/08/16/rollout-test.jsonl"
    rollout.parent.mkdir(parents=True)
    events = [
        {"type": "event_msg", "payload": {"type": "token_count", "info": {
            "total_token_usage": {"input_tokens": 12, "cached_input_tokens": 4, "output_tokens": 3}
        }}},
        {"type": "event_msg", "payload": {"type": "task_complete", "last_agent_message": "```json\n{\"ok\": true}\n```"}},
    ]
    rollout.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")

    assert recover_codex_rollout(tmp_path) == ("```json\n{\"ok\": true}\n```", 12, 4, 3)


def test_missing_rollout_is_empty(tmp_path):
    assert recover_codex_rollout(tmp_path) == ("", 0, 0, 0)


def test_extracts_final_json_after_explanatory_code_fence():
    text = 'Evidence:\n```solidity\nrequire(value > 0);\n```\nFinal:\n```json\n{"properties": []}\n```'
    assert _extract_last_fenced_json(text) == {"properties": []}


def test_head_limit_is_not_reported_as_a_file():
    assert _extract_touched_files("find . -type f | head -80") == []
