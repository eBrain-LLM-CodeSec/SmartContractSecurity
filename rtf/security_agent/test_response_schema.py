"""Unit tests for rtf.security_agent.response_schema -- the strict-mode
JSON schema builder backing the kernel's live-verified structured-output
fix (RTF_SECURITY_AGENT_CONTEXT_MANAGEMENT_DESIGN.md section 6 /
2026-08-25 canto run finding). No LLM calls anywhere in this file --
uses the real `jsonschema` validator against real kernel action model
instances instead."""
from __future__ import annotations

import jsonschema

from rtf.security_agent.kernel import (
    ConcludeAction, RESPONSE_MODELS, ToolCallAction, UpdateInvestigationAction,
)
from rtf.security_agent.response_schema import build_strict_schema


def _payload():
    return build_strict_schema(RESPONSE_MODELS, "kernel_action")


def _walk_object_schemas(node):
    """Yields every object-with-properties sub-schema in the tree."""
    if isinstance(node, dict):
        if node.get("type") == "object" and "properties" in node:
            yield node
        for value in node.values():
            yield from _walk_object_schemas(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_object_schemas(item)


def test_payload_shape():
    payload = _payload()
    assert payload["type"] == "json_schema"
    assert payload["name"] == "kernel_action"
    assert payload["strict"] is True
    assert "schema" in payload


def test_every_object_with_fixed_properties_is_strict():
    payload = _payload()
    found = list(_walk_object_schemas(payload["schema"]))
    assert len(found) >= 6  # the 3 actions + EvidenceInput/HypothesisInput/etc.
    for obj in found:
        assert obj["additionalProperties"] is False, obj
        assert set(obj["required"]) == set(obj["properties"].keys()), obj


def test_open_ended_dict_field_keeps_additional_properties_true():
    """ToolCallAction.args is a genuinely open dict (arbitrary tool
    arguments) -- must NOT be collapsed to additionalProperties: false,
    which would make it accept only an empty object."""
    payload = _payload()
    args_schema = payload["schema"]["$defs"]["ToolCallAction"]["properties"]["args"]
    assert args_schema.get("additionalProperties") is True


def test_value_level_constraints_are_stripped():
    """minLength/minItems/pattern are stripped from the PROVIDER-facing
    schema (unreliable support across strict-mode implementations) --
    Pydantic's own post-hoc validation still enforces them on every
    parsed response regardless (model_client.py's decide())."""
    import json
    payload = _payload()
    dumped = json.dumps(payload)
    for keyword in ("minLength", "maxLength", "minItems", "maxItems", "pattern"):
        assert f'"{keyword}"' not in dumped, keyword


def test_discriminator_values_present_as_const():
    payload = _payload()
    defs = payload["schema"]["$defs"]
    assert defs["ToolCallAction"]["properties"]["action"]["const"] == "call_tool"
    assert defs["UpdateInvestigationAction"]["properties"]["action"]["const"] == "update_investigation"
    assert defs["ConcludeAction"]["properties"]["action"]["const"] == "conclude"


def test_real_tool_call_action_instance_validates_against_generated_schema():
    payload = _payload()
    instance = ToolCallAction(action="call_tool", tool="get_contract_source",
                              args={"contract": "Vault"}, reasoning="inspecting").model_dump(mode="json")
    jsonschema.validate(instance, payload["schema"])


def test_real_conclude_action_instance_validates_against_generated_schema():
    payload = _payload()
    instance = ConcludeAction(
        action="conclude",
        evidence=[{"id": "ev-1", "claim": "c", "source_file": "Vault.sol"}],
        hypotheses=[{"id": "hyp-1", "claim": "c", "originating_property_ids": ["p1"]}],
        properties=[{
            "property_id": "p1", "claim": "c", "evidence_ids": ["ev-1"],
            "hypothesis_ids": ["hyp-1"], "interpretation": "i", "verdict": "PASS",
        }],
    ).model_dump(mode="json")
    jsonschema.validate(instance, payload["schema"])


def test_real_update_investigation_action_instance_validates_against_generated_schema():
    payload = _payload()
    instance = UpdateInvestigationAction(
        action="update_investigation",
        hypotheses=[{"id": "hyp-1", "claim": "c", "originating_property_ids": ["p1"]}],
    ).model_dump(mode="json")
    jsonschema.validate(instance, payload["schema"])


def test_extra_unknown_field_is_rejected_by_strict_schema():
    """Proves additionalProperties: false is a real, load-bearing
    constraint, not cosmetic -- an instance with a typo'd/extra field
    must fail validation against the generated schema."""
    payload = _payload()
    instance = ToolCallAction(action="call_tool", tool="x", args={}).model_dump(mode="json")
    instance["unexpected_extra_field"] = "surprise"
    errors = list(jsonschema.Draft7Validator(payload["schema"]).iter_errors(instance))
    assert errors, "expected the extra field to be rejected"


def test_the_action_field_naming_a_tool_directly_is_rejected():
    """Regression for the exact live bug this fix targets (2026-08-25
    canto run): the model naming a tool directly as the top-level
    "action" (e.g. {"action": "read_evidence", ...}) instead of wrapping
    it in call_tool. No branch of the union has "read_evidence" as a
    valid `action` const, so this must fail validation."""
    payload = _payload()
    bad_instance = {"action": "read_evidence", "evidence_id": "tool-1"}
    errors = list(jsonschema.Draft7Validator(payload["schema"]).iter_errors(bad_instance))
    assert errors
