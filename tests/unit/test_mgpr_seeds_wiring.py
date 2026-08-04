"""Tests for the seeds.py MGPR wiring: mgpr_commentator_seeds and
generate(routing_spec=...) must call the Commentator once per FIRED route
(multi-label aware), not once per in-scope function -- replacing the old
`commentator_seeds`'s O(all functions) full scan for MGPR-routed callers,
while `generate()` called WITHOUT a routing_spec keeps its exact prior
behavior (backward compatible, no regression for any non-MGPR caller).
"""
import json
from pathlib import Path
from unittest.mock import MagicMock

from a4v.commentator import Commentator
from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.llm import ChatResult
from a4v.mgpr.spec import load_routing_spec
from a4v.seeds import SeedGenerator

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
RESTRICTED_SOL = FIXTURES / "modifier_source" / "Restricted.sol"
ROUTING_SPEC = Path(__file__).resolve().parents[2] / "routing_spec.yaml"


def _stub_client(suspicious: bool = True) -> MagicMock:
    client = MagicMock()

    def _reply(messages):
        reply = {
            "suspicious": suspicious, "vuln_class": "other", "severity": "medium",
            "rationale": "stub", "lines": [],
        }
        content = "```json\n" + json.dumps(reply) + "\n```"
        return reply, ChatResult(content=content, prompt_tokens=1, completion_tokens=1, cached=False)

    client.complete_json.side_effect = _reply
    return client


def test_mgpr_commentator_seeds_calls_once_per_fired_group_not_per_function():
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    client = _stub_client()
    gen = SeedGenerator(pg, commentator=Commentator(client))

    seeds, comments = gen.mgpr_commentator_seeds(features, spec)

    # Vault.sol's fired (routing_unit, family) groups: withdraw/P1,
    # withdraw/P2, withdraw/P5 (three P5 gates -- P5_ACCOUNTING_ARITHMETIC,
    # P5_ACCOUNTING_ENTRYPOINT, P5_EXTERNAL_CALL_ACCOUNTING_WRITE -- MERGED
    # into one call, not three), deposit/P1 = 4 groups -- NOT 7 (the total
    # function count) and NOT 6 (one call per fired gate), proving both the
    # O(all functions) full-scan replacement AND the merge-not-pick-one
    # cross-cutting fix.
    assert client.complete_json.call_count == 4
    assert set(comments.keys()) == {
        "fn::Vault.withdraw(uint256)::P1_AUTHORIZATION",
        "fn::Vault.withdraw(uint256)::P2_REENTRANCY",
        "fn::Vault.withdraw(uint256)::P5_ARITHMETIC_PRECISION",
        "fn::Vault.deposit()::P1_AUTHORIZATION",
    }


def test_mgpr_commentator_seeds_reasons_are_family_and_gate_specific():
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    gen = SeedGenerator(pg, commentator=Commentator(_stub_client()))

    seeds, _ = gen.mgpr_commentator_seeds(features, spec)
    # withdraw fires three DIFFERENT families -- three separate SeedNode
    # entries here (merged later by generate()'s existing dedup logic),
    # each with its own family-scoped reason list (one reason per gate that
    # fired within that family's single merged call), not one node
    # conflating all three families.
    withdraw_nodes = [s for s in seeds if s.node_id == "fn::Vault.withdraw(uint256)"]
    assert len(withdraw_nodes) == 3
    all_reasons = {r for s in withdraw_nodes for r in s.reasons}
    assert all_reasons == {
        "mgpr:P1_AUTHORIZATION:P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
        "mgpr:P2_REENTRANCY:P2_CALL_BEFORE_WRITE",
        "mgpr:P5_ARITHMETIC_PRECISION:P5_ACCOUNTING_ARITHMETIC",
        "mgpr:P5_ARITHMETIC_PRECISION:P5_ACCOUNTING_ENTRYPOINT",
        "mgpr:P5_ARITHMETIC_PRECISION:P5_EXTERNAL_CALL_ACCOUNTING_WRITE",
    }
    # the P5 group's SINGLE SeedNode carries all three gate reasons together
    # -- proof the merge produced one call/one seed, not three.
    p5_node = next(s for s in withdraw_nodes if any("P5_" in r for r in s.reasons))
    assert len(p5_node.reasons) == 3


def test_mgpr_commentator_seeds_not_suspicious_produces_no_seed():
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    gen = SeedGenerator(pg, commentator=Commentator(_stub_client(suspicious=False)))

    seeds, comments = gen.mgpr_commentator_seeds(features, spec)
    assert seeds == []
    assert len(comments) == 4  # still one Comment recorded per fired GROUP, just none suspicious


def test_generate_with_routing_spec_merges_multilabel_withdraw_into_one_seed_node():
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    gen = SeedGenerator(pg, commentator=Commentator(_stub_client()))

    seed_nodes, comments = gen.generate(features, routing_spec=spec)
    combined = {s.node_id: s for s in seed_nodes}
    # generate()'s existing merge-by-node_id logic (unchanged) collapses
    # withdraw's three fired-family SeedNodes into one, accumulating
    # reasons -- alongside static_rule_seeds's own independent
    # write_after_external_call flag on the same function (static rules run
    # regardless of MGPR routing, per generate()'s unchanged merge step).
    withdraw_reasons = set(combined["fn::Vault.withdraw(uint256)"].reasons)
    assert {
        "mgpr:P1_AUTHORIZATION:P1_STATE_CHANGE_NO_AUTH_DOMINATOR",
        "mgpr:P2_REENTRANCY:P2_CALL_BEFORE_WRITE",
        "mgpr:P5_ARITHMETIC_PRECISION:P5_ACCOUNTING_ARITHMETIC",
    } <= withdraw_reasons


def test_generate_without_routing_spec_keeps_old_full_scan_behavior():
    """No routing_spec passed -> generate() must call the Commentator once
    per in-scope function (the old commentator_seeds path), unchanged --
    MGPR routing is opt-in, not a silent behavior change for existing
    callers."""
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    client = _stub_client()
    gen = SeedGenerator(pg, commentator=Commentator(client))

    gen.generate(features)  # no routing_spec

    # the old commentator_seeds path (still exercised here, unmodified)
    # iterates every function-kind node from FeatureExtractor.compute with
    # no external-stub filtering at all -- that filtering is new,
    # MGPR-only behavior in router.py's route_all, not a change to the
    # pre-existing path.
    all_function_kind_nodes = len(pg.nodes_of_kind("function"))
    assert client.complete_json.call_count == all_function_kind_nodes


# --- Gap C, Workstream 2: mgpr_investigation_seeds --------------------------


def test_mgpr_investigation_seeds_calls_once_per_selected_unit():
    pg = ProgramGraph.build(RESTRICTED_SOL)
    # simulate the pre-fix bug's exact symptom (unreadable modifier source)
    # so `setValue`'s authorization_control_state search is genuinely
    # decision-blocking-unresolved, independent of graph.py's own fix.
    pg.graph.nodes["mod::Restricted.restricted()"]["file"] = None
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    client = _stub_client()
    gen = SeedGenerator(pg, commentator=Commentator(client))

    seeds, comments = gen.mgpr_investigation_seeds(features, spec)

    assert client.complete_json.call_count == 1
    assert set(comments.keys()) == {"fn::Restricted.setValue(uint256)::investigation"}
    sent_messages = client.complete_json.call_args[0][0]
    assert "not fully resolve" in sent_messages[0]["content"].lower()


def test_mgpr_investigation_seeds_reasons_list_blocked_families():
    pg = ProgramGraph.build(RESTRICTED_SOL)
    pg.graph.nodes["mod::Restricted.restricted()"]["file"] = None
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    gen = SeedGenerator(pg, commentator=Commentator(_stub_client()))

    seeds, _ = gen.mgpr_investigation_seeds(features, spec)
    assert len(seeds) == 1
    assert seeds[0].node_id == "fn::Restricted.setValue(uint256)"
    assert seeds[0].reasons == ["mgpr_investigation:P1_AUTHORIZATION"]


def test_mgpr_investigation_seeds_no_selected_units_produces_no_calls():
    """Vault.sol has no unreadable modifiers/helpers -- no decision-
    blocking-unresolved units, so no investigation calls at all."""
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    client = _stub_client()
    gen = SeedGenerator(pg, commentator=Commentator(client))

    seeds, comments = gen.mgpr_investigation_seeds(features, spec)
    assert seeds == []
    assert comments == {}
    assert client.complete_json.call_count == 0


def test_mgpr_investigation_seeds_separate_from_commentator_seeds_call_count():
    """Explicit opt-in, separately measurable cost -- mgpr_commentator_seeds
    must not include investigation calls, and vice versa."""
    pg = ProgramGraph.build(RESTRICTED_SOL)
    pg.graph.nodes["mod::Restricted.restricted()"]["file"] = None
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    client = _stub_client()
    gen = SeedGenerator(pg, commentator=Commentator(client))

    gen.mgpr_commentator_seeds(features, spec)
    normal_call_count = client.complete_json.call_count
    gen.mgpr_investigation_seeds(features, spec)
    total_call_count = client.complete_json.call_count

    assert total_call_count == normal_call_count + 1
