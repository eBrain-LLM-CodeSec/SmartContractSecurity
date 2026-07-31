"""Synthetic-graph tests for authorization_control_state's four-state search
chain -- covers cases that are hard or impossible to trigger via a real
Slither compile (an unreadable modifier source, a match only reachable
through a bounded-depth internal-helper chain). See
tests/unit/test_mgpr_predicates.py for the real-fixture (Vault.sol/
VulnerableBank.sol) coverage of the common PRESENT/ABSENT paths.
"""
from __future__ import annotations

import networkx as nx
import pytest

from a4v.graph import CALLS, DECLARES, FUNCTION, INHERITS, USES_MODIFIER, MODIFIER, CONTRACT, ProgramGraph
from a4v.mgpr.resolution import NegativeFeatureState, authorization_control_state


def _write(tmp_path, name: str, text: str) -> str:
    p = tmp_path / name
    p.write_text(text)
    return str(p)


def _add_function(g, node_id, *, file=None, lines=None, contract="C"):
    g.add_node(node_id, kind=FUNCTION, name=node_id.split("::")[-1], contract=contract, file=file, lines=lines)


def test_absent_when_body_and_modifiers_and_helpers_all_clean(tmp_path):
    src = _write(tmp_path, "f.sol", "function foo() public { doSomethingUnrelated(); }")
    g = nx.MultiDiGraph()
    _add_function(g, "fn::C.foo()", file=src, lines=[1, 1])
    pg = ProgramGraph(g, slither=None)

    result = authorization_control_state(pg, "fn::C.foo()")
    assert result.state == NegativeFeatureState.ABSENT


def test_present_via_modifier_body_when_not_in_function_source(tmp_path):
    fn_src = _write(tmp_path, "f.sol", "function foo() public onlyAdmin { doStuff(); }".replace("onlyAdmin", "guard"))
    mod_src = _write(tmp_path, "m.sol", "modifier guard() { require(msg.sender == admin); _; }")
    g = nx.MultiDiGraph()
    _add_function(g, "fn::C.foo()", file=fn_src, lines=[1, 1])
    g.add_node("mod::C.guard()", kind=MODIFIER, name="guard", contract="C", file=mod_src, lines=[1, 1])
    g.add_edge("fn::C.foo()", "mod::C.guard()", kind=USES_MODIFIER)
    pg = ProgramGraph(g, slither=None)

    result = authorization_control_state(pg, "fn::C.foo()")
    assert result.state == NegativeFeatureState.PRESENT
    assert any("modifier" in e for e in result.evidence)


def test_unresolved_when_modifier_source_unreadable():
    g = nx.MultiDiGraph()
    _add_function(g, "fn::C.foo()", file=None, lines=None)  # function source itself unreadable too
    g.add_node("mod::C.guard()", kind=MODIFIER, name="guard", contract="C", file=None, lines=None)
    g.add_edge("fn::C.foo()", "mod::C.guard()", kind=USES_MODIFIER)
    pg = ProgramGraph(g, slither=None)

    result = authorization_control_state(pg, "fn::C.foo()")
    assert result.state == NegativeFeatureState.UNRESOLVED_BY_EXTRACTION
    assert not any("PRESENT" in n for n in result.notes)  # sanity: notes record gaps, not false positives


def test_unresolved_takes_priority_over_absent_even_with_one_clean_path(tmp_path):
    """A function whose own body resolves cleanly (no match) but whose one
    applied modifier is unreadable must be UNRESOLVED_BY_EXTRACTION, not
    ABSENT -- an unresolved search path is never silently treated as
    evidence the control is missing."""
    fn_src = _write(tmp_path, "f.sol", "function foo() public onlyGuard { doStuff(); }")
    g = nx.MultiDiGraph()
    _add_function(g, "fn::C.foo()", file=fn_src, lines=[1, 1])
    g.add_node("mod::C.onlyGuard()", kind=MODIFIER, name="onlyGuard", contract="C", file=None, lines=None)
    g.add_edge("fn::C.foo()", "mod::C.onlyGuard()", kind=USES_MODIFIER)
    pg = ProgramGraph(g, slither=None)

    result = authorization_control_state(pg, "fn::C.foo()")
    assert result.state == NegativeFeatureState.UNRESOLVED_BY_EXTRACTION


def test_helper_chain_found_within_depth(tmp_path):
    fn_src = _write(tmp_path, "f.sol", "function foo() public { helper1(); }")
    h1_src = _write(tmp_path, "h1.sol", "function helper1() internal { helper2(); }")
    h2_src = _write(tmp_path, "h2.sol", "function helper2() internal { require(msg.sender == admin); }")
    g = nx.MultiDiGraph()
    _add_function(g, "fn::C.foo()", file=fn_src, lines=[1, 1])
    _add_function(g, "fn::C.helper1()", file=h1_src, lines=[1, 1])
    _add_function(g, "fn::C.helper2()", file=h2_src, lines=[1, 1])
    g.add_edge("fn::C.foo()", "fn::C.helper1()", kind=CALLS)
    g.add_edge("fn::C.helper1()", "fn::C.helper2()", kind=CALLS)
    pg = ProgramGraph(g, slither=None)

    result = authorization_control_state(pg, "fn::C.foo()", max_helper_depth=2)
    assert result.state == NegativeFeatureState.PRESENT
    assert any("helper" in e for e in result.evidence)


def test_helper_chain_beyond_depth_not_found(tmp_path):
    fn_src = _write(tmp_path, "f.sol", "function foo() public { helper1(); }")
    h1_src = _write(tmp_path, "h1.sol", "function helper1() internal { helper2(); }")
    h2_src = _write(tmp_path, "h2.sol", "function helper2() internal { require(msg.sender == admin); }")
    g = nx.MultiDiGraph()
    _add_function(g, "fn::C.foo()", file=fn_src, lines=[1, 1])
    _add_function(g, "fn::C.helper1()", file=h1_src, lines=[1, 1])
    _add_function(g, "fn::C.helper2()", file=h2_src, lines=[1, 1])
    g.add_edge("fn::C.foo()", "fn::C.helper1()", kind=CALLS)
    g.add_edge("fn::C.helper1()", "fn::C.helper2()", kind=CALLS)
    pg = ProgramGraph(g, slither=None)

    # max_helper_depth=1: BFS only reaches helper1 (depth 1), never helper2
    # (depth 2) where the auth pattern actually lives -- must not find it,
    # and since every visited node resolved cleanly (all have readable
    # source), the honest result is ABSENT, not UNRESOLVED.
    result = authorization_control_state(pg, "fn::C.foo()", max_helper_depth=1)
    assert result.state == NegativeFeatureState.ABSENT


def test_unresolved_base_contract_not_in_compile_unit(tmp_path):
    fn_src = _write(tmp_path, "f.sol", "function foo() public { doStuff(); }")
    g = nx.MultiDiGraph()
    _add_function(g, "fn::Derived.foo()", file=fn_src, lines=[1, 1], contract="Derived")
    g.add_node("contract::Derived", kind=CONTRACT, name="Derived")
    g.add_edge("fn::Derived.foo()", "fn::Derived.foo()", kind=CALLS)  # no-op edge, keep graph well-formed
    g.remove_edge("fn::Derived.foo()", "fn::Derived.foo()")
    g.add_edge("contract::Derived", "contract::Base", kind=INHERITS)  # Base intentionally never added as a node
    pg = ProgramGraph(g, slither=None)

    result = authorization_control_state(pg, "fn::Derived.foo()")
    assert result.state == NegativeFeatureState.UNRESOLVED_BY_EXTRACTION
    assert any("Base" in n for n in result.notes)
