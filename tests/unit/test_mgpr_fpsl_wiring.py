"""Tests for the additive fpsl.py/commentator.py changes that let a Route's
string prompt_id (e.g. "P2_REENTRANCY_v1") drive the Commentator call,
alongside the existing five int-keyed strategies (untouched)."""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from a4v import fpsl
from a4v.commentator import Commentator
from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.llm import ChatResult
from a4v.mgpr.context import build_context
from a4v.mgpr.router import route_all
from a4v.mgpr.spec import load_routing_spec

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
ROUTING_SPEC = Path(__file__).resolve().parents[2] / "routing_spec.yaml"


def test_existing_int_strategies_untouched():
    for i in range(1, 6):
        messages = fpsl.build_prompt(i, "function f() public {}")
        assert len(messages) == 2
        assert messages[0]["role"] == "system"


@pytest.mark.parametrize("prompt_id", ["P1_AUTHORIZATION_v1", "P2_REENTRANCY_v1", "P5_ARITHMETIC_PRECISION_v1"])
def test_mgpr_prompt_ids_build_valid_messages(prompt_id):
    messages = fpsl.build_prompt(prompt_id, "function f() public {}")
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    # every strategy still asks for the same output contract, so the
    # Commentator's parsing code needs no change for the new prompt ids
    assert '"suspicious"' in messages[1]["content"]


def test_unknown_prompt_id_still_raises():
    with pytest.raises(ValueError, match="unknown FPSL strategy"):
        fpsl.build_prompt("NOT_A_REAL_PROMPT_ID", "function f() public {}")


def _stub_client(reply: dict) -> MagicMock:
    client = MagicMock()
    content = "```json\n" + json.dumps(reply) + "\n```"
    client.complete_json.return_value = (
        reply, ChatResult(content=content, prompt_tokens=10, completion_tokens=5, cached=False)
    )
    return client


def test_comment_bundle_accepts_string_prompt_id_end_to_end():
    """A real MGPR-built ContextBundle, fed through Commentator.comment_bundle
    with a string prompt_id, must reach the LLM call with the P2-specific
    system prompt -- proving the router->context->fpsl->commentator chain
    is wired, with no Commentator/fpsl signature break for the existing
    int-keyed strategies."""
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    routes = route_all(pg, features, spec)
    route = next(
        r for r in routes
        if r.routing_unit == "fn::Vault.withdraw(uint256)"
        and r.family == "P2_REENTRANCY" and r.route_would_fire
    )
    bundle, record = build_context(pg, route)

    reply = {
        "suspicious": True, "vuln_class": "reentrancy", "severity": "high",
        "rationale": "external call before state write", "lines": [37, 38],
    }
    client = _stub_client(reply)
    commentator = Commentator(client)
    comment = commentator.comment_bundle(bundle, strategy=route.prompt_id)

    assert comment.suspicious is True
    assert comment.strategy == "P2_REENTRANCY_v1"
    sent_messages = client.complete_json.call_args[0][0]
    assert "reentran" in sent_messages[0]["content"].lower()
