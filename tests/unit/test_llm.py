"""Phase 2: last-fence JSON extraction must survive a nested fenced code
block inside a string field (e.g. a `rationale`/`fix` field that itself
contains a ```solidity example). See llm.py docstring: naive "nearest
previous fence" search finds the inner block's closing fence, not the outer
opening one, and truncates mid-string.
"""
import json

import pytest

from a4v.llm import extract_last_fenced_json


def test_plain_json_no_fence():
    assert extract_last_fenced_json('{"a": 1}') == {"a": 1}


def test_simple_fenced_json():
    text = '```json\n{"a": 1, "b": "two"}\n```'
    assert extract_last_fenced_json(text) == {"a": 1, "b": "two"}


def test_fenced_json_with_nested_fence_in_string_field():
    text = (
        'Here is my analysis.\n'
        '```json\n'
        '{"suspicious": true, "vuln_class": "reentrancy", '
        '"rationale": "fix like:\\n```solidity\\nrequire(x);\\n```\\nthen update state"}\n'
        '```\n'
    )
    result = extract_last_fenced_json(text)
    assert result["vuln_class"] == "reentrancy"
    assert "```solidity" in result["rationale"]


def test_glm_style_reply_without_leading_prose():
    text = '```json\n{"detected": false}\n```'
    assert extract_last_fenced_json(text) == {"detected": False}


def test_malformed_json_raises():
    with pytest.raises(json.JSONDecodeError):
        extract_last_fenced_json('```json\n{not valid json\n```')
