from pathlib import Path

import pytest

from a4v.mgpr.spec import SpecError, load_routing_spec

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING_SPEC = REPO_ROOT / "routing_spec.yaml"


def test_loads_real_routing_spec():
    spec = load_routing_spec(ROUTING_SPEC)
    assert spec.version == 1
    names = {f.name for f in spec.specified_families()}
    assert names == {"P1_AUTHORIZATION", "P2_REENTRANCY", "P5_ARITHMETIC_PRECISION"}
    assert len(spec.families) == 16  # full P0-P15 taxonomy, most stubbed


def test_not_yet_specified_families_have_no_gates():
    spec = load_routing_spec(ROUTING_SPEC)
    stubs = [f for f in spec.families.values() if f.status == "NOT_YET_SPECIFIED"]
    assert len(stubs) == 13
    for f in stubs:
        assert f.gates == []
        assert f.seed_types == []
        assert f.prompt_id is None


def test_p1_gate_predicate_uses_equals_not_boolean_none(tmp_path):
    spec = load_routing_spec(ROUTING_SPEC)
    p1 = spec.families["P1_AUTHORIZATION"]
    gate = p1.gates[0]
    items = gate.predicate["all"]
    equals_items = [i for i in items if isinstance(i, dict)]
    assert len(equals_items) == 1
    assert equals_items[0] == {"equals": {"authorization_control_state": "ABSENT"}}


def test_p1_has_bounded_helper_search_depth_param():
    spec = load_routing_spec(ROUTING_SPEC)
    p1 = spec.families["P1_AUTHORIZATION"]
    assert "authorization_search_max_helper_depth" in p1.params
    assert isinstance(p1.params["authorization_search_max_helper_depth"], int)


def test_p5_has_bounded_arithmetic_search_depth_param():
    spec = load_routing_spec(ROUTING_SPEC)
    p5 = spec.families["P5_ARITHMETIC_PRECISION"]
    assert "p5_arithmetic_search_max_helper_depth" in p5.params
    assert isinstance(p5.params["p5_arithmetic_search_max_helper_depth"], int)


def test_routing_spec_has_top_level_investigation_cap_param():
    spec = load_routing_spec(ROUTING_SPEC)
    assert "unresolved_investigation_max_per_audit" in spec.params
    assert isinstance(spec.params["unresolved_investigation_max_per_audit"], int)


def test_p2_has_callback_reachable_write_gate():
    spec = load_routing_spec(ROUTING_SPEC)
    p2 = spec.families["P2_REENTRANCY"]
    gate_ids = {g.id for g in p2.gates}
    assert "P2_CALL_BEFORE_WRITE" in gate_ids
    assert "P2_CALLBACK_REACHABLE_WRITE" in gate_ids


def test_p5_has_three_new_gates_alongside_narrowing_cast():
    spec = load_routing_spec(ROUTING_SPEC)
    p5 = spec.families["P5_ARITHMETIC_PRECISION"]
    gate_ids = {g.id for g in p5.gates}
    assert gate_ids == {
        "P5_NARROWING_CAST", "P5_ACCOUNTING_ARITHMETIC",
        "P5_EXTERNAL_CALL_ACCOUNTING_WRITE", "P5_ACCOUNTING_ENTRYPOINT",
    }


def test_p5_accounting_entrypoint_requires_all_four_predicates():
    spec = load_routing_spec(ROUTING_SPEC)
    p5 = spec.families["P5_ARITHMETIC_PRECISION"]
    entrypoint_gate = next(g for g in p5.gates if g.id == "P5_ACCOUNTING_ENTRYPOINT")
    assert set(entrypoint_gate.predicate["all"]) == {
        "visibility_is_public_or_external", "accounting_action_identifier_signal",
        "numeric_user_input_exists", "state_write_exists",
    }


def test_known_predicates_validation_rejects_typo(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        """
version: 1
families:
  P2_REENTRANCY:
    status: SPECIFIED
    seed_types: [function]
    gates:
      - id: P2_CALL_BEFORE_WRITE
        predicate: {all: [external_call_exsits]}
    prompt_id: P2_REENTRANCY_v1
"""
    )
    with pytest.raises(SpecError, match="external_call_exsits"):
        load_routing_spec(bad, known_predicates={"external_call_exists"})


def test_known_predicates_validation_accepts_correct_names(tmp_path):
    ok = tmp_path / "ok.yaml"
    ok.write_text(
        """
version: 1
families:
  P2_REENTRANCY:
    status: SPECIFIED
    seed_types: [function]
    gates:
      - id: P2_CALL_BEFORE_WRITE
        predicate: {all: [external_call_exists]}
    prompt_id: P2_REENTRANCY_v1
"""
    )
    spec = load_routing_spec(ok, known_predicates={"external_call_exists"})
    assert spec.families["P2_REENTRANCY"].status == "SPECIFIED"


def test_specified_family_without_gates_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        """
version: 1
families:
  P2_REENTRANCY:
    status: SPECIFIED
    seed_types: [function]
    gates: []
    prompt_id: P2_REENTRANCY_v1
"""
    )
    with pytest.raises(SpecError, match="at least one gate"):
        load_routing_spec(bad)


def test_stub_family_with_extra_keys_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        """
version: 1
families:
  P0_DETERMINISTIC_SYNTACTIC:
    status: NOT_YET_SPECIFIED
    seed_types: [function]
"""
    )
    with pytest.raises(SpecError, match="extra keys"):
        load_routing_spec(bad)


def test_unknown_seed_type_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        """
version: 1
families:
  P2_REENTRANCY:
    status: SPECIFIED
    seed_types: [nonexistent_unit_type]
    gates:
      - id: P2_CALL_BEFORE_WRITE
        predicate: {all: [external_call_exists]}
    prompt_id: P2_REENTRANCY_v1
"""
    )
    with pytest.raises(SpecError, match="unknown seed_type"):
        load_routing_spec(bad)
