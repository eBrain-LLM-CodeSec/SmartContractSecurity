from pathlib import Path

import networkx as nx

from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.mgpr.spec import load_routing_spec
from scripts.mgpr.run_feasibility_study import (
    assign_expected_family,
    build_route_and_context_manifests,
    find_routing_units_for_citation,
    resolve_citation,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
ROUTING_SPEC = Path(__file__).resolve().parents[2] / "routing_spec.yaml"


# --- assign_expected_family -------------------------------------------------


def test_short_description_alone_can_classify_reentrancy():
    assert assign_expected_family("Reentrancy in burn allows stablecoin pool drainage") == "P2_REENTRANCY"


def test_short_description_alone_insufficient_for_real_downcast_finding():
    """H-02's real task_info.csv description states impact, not mechanism --
    confirmed by direct inspection this must NOT classify without the full
    text (regression guard for the bug this heuristic was fixed for)."""
    assert assign_expected_family("A malicious user can steal other user's deposits from Vault.sol") is None


def test_full_text_recovers_correct_family_for_downcast_finding():
    full_text = (
        "Cast\n\nWhen Vault.withdraw() is called, ... "
        "convert from `uint256` to `uint96` when burning shares."
    )
    assert assign_expected_family(
        "A malicious user can steal other user's deposits from Vault.sol", full_text
    ) == "P5_ARITHMETIC_PRECISION"


def test_full_text_recovers_authorization_family():
    full_text = "Vault.mintYieldFee function can be called by anyone to mint Vault Shares to any recipient."
    assert assign_expected_family("Unrestricted minting", full_text) == "P1_AUTHORIZATION"


def test_no_keyword_match_returns_none_not_a_guess():
    assert assign_expected_family("Gas griefing via unbounded loop", "no relevant keywords here at all") is None


def test_reentrancy_checked_before_other_families_when_both_present():
    # order matters: a description mentioning both should hit the first
    # matching family in _FAMILY_KEYWORDS's list order (documented, not
    # incidental) -- reentrancy is checked first.
    assert assign_expected_family("Reentrancy causes an overflow in the accounting") == "P2_REENTRANCY"


# --- resolve_citation --------------------------------------------------------


def test_resolve_citation_parses_range():
    result = resolve_citation(
        "https://github.com/org/repo/blob/deadbeef/src/Vault.sol#L10-L20",
        checkout_root=Path("/checkouts/audit-1"), run_cmd_dir="vault",
    )
    assert result == (Path("/checkouts/audit-1/vault/src/Vault.sol"), 10, 20)


def test_resolve_citation_parses_single_line():
    result = resolve_citation(
        "https://github.com/org/repo/blob/deadbeef/src/Vault.sol#L42",
        checkout_root=Path("/checkouts/audit-1"), run_cmd_dir=".",
    )
    assert result == (Path("/checkouts/audit-1/src/Vault.sol"), 42, 42)


def test_resolve_citation_rejects_non_matching_url():
    assert resolve_citation("https://example.com/not-github", Path("/x"), ".") is None


# --- find_routing_units_for_citation ----------------------------------------


def _graph_with_functions(specs: list[tuple[str, str, list[int]]]) -> ProgramGraph:
    g = nx.MultiDiGraph()
    for node_id, file, lines in specs:
        g.add_node(node_id, kind="function", name=node_id.split("::")[-1], file=file, lines=lines)
    return ProgramGraph(g, slither=None)


def test_finds_overlapping_function(tmp_path):
    f = str(tmp_path / "Vault.sol")
    pg = _graph_with_functions([("fn::Vault.withdraw()", f, [100, 130])])
    assert find_routing_units_for_citation(pg, Path(f), 110, 120) == ["fn::Vault.withdraw()"]


def test_no_match_when_lines_dont_overlap(tmp_path):
    f = str(tmp_path / "Vault.sol")
    pg = _graph_with_functions([("fn::Vault.withdraw()", f, [100, 130])])
    assert find_routing_units_for_citation(pg, Path(f), 200, 210) == []


def test_no_match_when_different_file(tmp_path):
    f = str(tmp_path / "Vault.sol")
    other = str(tmp_path / "Other.sol")
    pg = _graph_with_functions([("fn::Vault.withdraw()", f, [100, 130])])
    assert find_routing_units_for_citation(pg, Path(other), 100, 130) == []


def test_most_specific_smallest_span_ranked_first(tmp_path):
    f = str(tmp_path / "Vault.sol")
    pg = _graph_with_functions([
        ("fn::Vault.outer()", f, [1, 500]),
        ("fn::Vault.inner()", f, [100, 110]),
    ])
    result = find_routing_units_for_citation(pg, Path(f), 105, 105)
    assert result == ["fn::Vault.inner()", "fn::Vault.outer()"]


def test_slither_synthetic_functions_excluded(tmp_path):
    f = str(tmp_path / "Vault.sol")
    g = nx.MultiDiGraph()
    g.add_node("fn::Vault.slitherConstructorConstantVariables()", kind="function",
               name="slitherConstructorConstantVariables", file=f, lines=[1, 1000])
    g.add_node("fn::Vault.real()", kind="function", name="real", file=f, lines=[50, 60])
    pg = ProgramGraph(g, slither=None)
    assert find_routing_units_for_citation(pg, Path(f), 55, 55) == ["fn::Vault.real()"]


# --- build_route_and_context_manifests (real Vault.sol graph) --------------


def _synthetic_finding(finding_id: str, line_range: str) -> dict:
    # points at the REAL fixture file via checkout_root/run_cmd_dir join in
    # the test below, not a live GitHub URL -- this is offline unit testing.
    # Repo name matches finding_id's audit slug ("fake-audit") deliberately,
    # so citation_resolution's repo-identity check treats this as an
    # in-scope self-citation rather than an external dependency.
    audit_id = finding_id.split("/")[0]
    return {
        "finding_id": finding_id,
        "description": "synthetic test finding",
        "github_cited_locations": [f"https://github.com/fake/{audit_id}/blob/deadbeef/Vault.sol#{line_range}"],
        "findings_md_path": None,
    }


def test_route_manifest_covers_whole_graph_not_just_findings():
    """route_manifest rows must cover every fired route in the compiled
    graph -- withdraw fires both P1 and P2, deposit fires P1 -- regardless
    of whether any finding cites them."""
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    checkout_root, run_cmd_dir = FIXTURES, "multi_contract"

    route_rows, _context_rows = build_route_and_context_manifests(
        "fake-audit", pg, features, spec, findings=[], checkout_root=checkout_root, run_cmd_dir=run_cmd_dir
    )
    pairs = {(r["routing_unit"], r["family"]) for r in route_rows}
    assert ("fn::Vault.withdraw(uint256)", "P1_AUTHORIZATION") in pairs
    assert ("fn::Vault.withdraw(uint256)", "P2_REENTRANCY") in pairs
    assert ("fn::Vault.deposit()", "P1_AUTHORIZATION") in pairs
    # setOracle is protected -- must not appear as a fired P1 route
    assert not any(r["routing_unit"] == "fn::Vault.setOracle(address)" for r in route_rows)


def test_context_manifest_records_ground_truth_match_when_finding_cites_the_unit():
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    checkout_root, run_cmd_dir = FIXTURES, "multi_contract"
    finding = _synthetic_finding("fake-audit/H-01", "L34-L43")  # covers withdraw()'s span

    _route_rows, context_rows = build_route_and_context_manifests(
        "fake-audit", pg, features, spec, findings=[finding], checkout_root=checkout_root, run_cmd_dir=run_cmd_dir
    )
    withdraw_p2 = next(
        r for r in context_rows if r["routing_unit"] == "fn::Vault.withdraw(uint256)" and r["family"] == "P2_REENTRANCY"
    )
    assert withdraw_p2["matching_finding_ids"] == ["fake-audit/H-01"]
    assert withdraw_p2["ground_truth_cited_locations"] == finding["github_cited_locations"]
    assert withdraw_p2["ground_truth_locations_in_included"] is True
    assert withdraw_p2["ground_truth_locations_in_excluded_or_unresolved"] is False


def test_context_manifest_leaves_ground_truth_fields_null_when_no_finding_cites_the_unit():
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    checkout_root, run_cmd_dir = FIXTURES, "multi_contract"

    _route_rows, context_rows = build_route_and_context_manifests(
        "fake-audit", pg, features, spec, findings=[], checkout_root=checkout_root, run_cmd_dir=run_cmd_dir
    )
    deposit_p1 = next(
        r for r in context_rows if r["routing_unit"] == "fn::Vault.deposit()" and r["family"] == "P1_AUTHORIZATION"
    )
    assert deposit_p1["matching_finding_ids"] == []
    assert deposit_p1["ground_truth_cited_locations"] == []
    assert deposit_p1["ground_truth_locations_in_included"] is None
    assert deposit_p1["ground_truth_locations_in_excluded_or_unresolved"] is None


def test_route_manifest_gates_fired_matches_router_gate_ids():
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    checkout_root, run_cmd_dir = FIXTURES, "multi_contract"

    route_rows, _ = build_route_and_context_manifests(
        "fake-audit", pg, features, spec, findings=[], checkout_root=checkout_root, run_cmd_dir=run_cmd_dir
    )
    withdraw_p2 = next(
        r for r in route_rows if r["routing_unit"] == "fn::Vault.withdraw(uint256)" and r["family"] == "P2_REENTRANCY"
    )
    assert withdraw_p2["gates_fired"] == ["P2_CALL_BEFORE_WRITE"]
    assert withdraw_p2["prompt_id"] == "P2_REENTRANCY_v1"
