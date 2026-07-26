"""Commentator wiring, with a stub ChatClient so no real API call is made."""
import json
from pathlib import Path
from unittest.mock import MagicMock

from a4v.commentator import Commentator
from a4v.graph import ProgramGraph
from a4v.llm import ChatResult
from a4v.slice import BundleBuilder

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"


def _stub_client(reply: dict) -> MagicMock:
    client = MagicMock()
    content = "```json\n" + json.dumps(reply) + "\n```"
    client.complete_json.return_value = (reply, ChatResult(content=content, prompt_tokens=10, completion_tokens=5, cached=False))
    return client


def test_comment_bundle_uses_numbered_source_and_parses_reply():
    pg = ProgramGraph.build(VAULT_SOL)
    bundle = BundleBuilder(pg).expand("fn::Vault.withdraw(uint256)", hops=1)

    reply = {
        "suspicious": True, "vuln_class": "reentrancy", "severity": "high",
        "rationale": "external call before state write", "lines": [37, 38],
    }
    client = _stub_client(reply)
    commentator = Commentator(client, strategies=[5])
    comment = commentator.comment_bundle(bundle)

    assert comment.suspicious is True
    assert comment.vuln_class == "reentrancy"
    assert comment.lines == [37, 38]

    # the prompt actually sent to the LLM must carry absolute line numbers,
    # not snippet-relative ones, and mention the write-after-external-call vars
    sent_messages = client.complete_json.call_args[0][0]
    user_content = sent_messages[1]["content"]
    assert "left margin" in user_content or "line number" in user_content
    assert "shares" in user_content or "totalShares" in user_content


def test_comment_source_not_suspicious():
    reply = {"suspicious": False, "vuln_class": None, "severity": None, "rationale": "looks fine", "lines": []}
    client = _stub_client(reply)
    commentator = Commentator(client, strategies=[1])
    comment = commentator.comment_source("function f() public {}")
    assert comment.suspicious is False
    assert comment.lines == []
