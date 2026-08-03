from pathlib import Path

import networkx as nx

from a4v.features import FeatureExtractor
from a4v.graph import ProgramGraph
from a4v.mgpr.spec import load_routing_spec
from scripts.mgpr.run_feasibility_study import (
    _evaluate_finding,
    _evaluate_incorrect_claim,
    build_route_and_context_manifests,
    find_routing_units_for_citation,
    load_reviewed_labels,
    resolve_citation,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"
ROUTING_SPEC = Path(__file__).resolve().parents[2] / "routing_spec.yaml"

# NOTE: the old broad-substring `assign_expected_family` heuristic and its
# tests were removed in favor of `scripts.mgpr.family_classification`
# (see tests/unit/test_mgpr_family_classification.py for the required
# collision/classification test coverage). `_evaluate_finding` now calls
# that classifier internally -- covered below via the reviewed-label
# override path, which is specific to `_evaluate_finding` itself.


def _finding(finding_id: str, title: str | None = None, description: str = "", full_text: str | None = None,
             citations: list[str] | None = None) -> dict:
    audit_id = finding_id.split("/")[0]
    return {
        "finding_id": finding_id, "title": title, "description": description,
        "github_cited_locations": citations or [f"https://github.com/fake/{audit_id}/blob/deadbeef/Vault.sol#L34-L43"],
        "findings_md_path": None,
    }


def test_evaluate_finding_uses_raw_classifier_when_no_review_given():
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    finding = _finding("fake-audit/H-01", title="Reentrancy in Vault.withdraw")
    rows = _evaluate_finding(finding, pg, features, spec, FIXTURES, "multi_contract")
    assert rows[0]["expected_primary_family"] == "P2_REENTRANCY"
    assert rows[0]["reviewed"] is False


def test_evaluate_finding_review_overrides_raw_classifier():
    """A finding the raw classifier would call P2_REENTRANCY (title says
    "Reentrancy") but that a human reviewer corrected to NOT_APPLICABLE
    (e.g. the `nonReentrant`-in-quoted-code false-positive pattern) must
    use the REVIEWED label, not the raw one -- "the manually reviewed
    labels become the evaluation labels for this study."""
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    finding = _finding("fake-audit/H-01", title="Reentrancy in Vault.withdraw")
    reviewed = {"fake-audit/H-01": {
        "finding_id": "fake-audit/H-01", "final_family": "NOT_APPLICABLE", "reviewer_status": "CORRECTED",
    }}
    rows = _evaluate_finding(finding, pg, features, spec, FIXTURES, "multi_contract", reviewed)
    assert rows[0]["expected_primary_family"] is None
    assert rows[0]["family_outcome"] == "NOT_APPLICABLE"
    assert rows[0]["reviewed"] is True
    assert rows[0]["reviewer_status"] == "CORRECTED"
    # the raw (pre-review) classification is still recorded, for audit trail
    assert rows[0]["raw_classification"]["outcome"] == "P2_REENTRANCY"


def test_load_reviewed_labels_missing_file_returns_empty(tmp_path):
    assert load_reviewed_labels(tmp_path / "does_not_exist.jsonl") == {}


def test_load_reviewed_labels_missing_path_returns_empty():
    assert load_reviewed_labels(None) == {}


def test_load_reviewed_labels_keyed_by_finding_id(tmp_path):
    path = tmp_path / "reviewed.jsonl"
    path.write_text(
        '{"finding_id": "a/H-01", "final_family": "P1_AUTHORIZATION", "reviewer_status": "CONFIRMED"}\n'
        '{"finding_id": "a/H-02", "final_family": "NOT_APPLICABLE", "reviewer_status": "CORRECTED"}\n'
    )
    labels = load_reviewed_labels(path)
    assert set(labels) == {"a/H-01", "a/H-02"}
    assert labels["a/H-01"]["reviewer_status"] == "CONFIRMED"


# --- required test 18: reviewed labels serialize deterministically --------


def test_reviewed_labels_serialize_deterministically(tmp_path):
    import json
    row = {
        "finding_id": "a/H-01", "audit_id": "a", "title": "T", "raw_classifier_family": "P1_AUTHORIZATION",
        "final_family": "P1_AUTHORIZATION", "vulnerability_mechanism": "m", "classification_evidence": "e",
        "reviewer_status": "CONFIRMED", "previous_family_assignment": "P1_AUTHORIZATION", "reason_for_change": None,
    }
    serialized_1 = json.dumps(row, sort_keys=True)
    serialized_2 = json.dumps(dict(reversed(list(row.items()))), sort_keys=True)
    assert serialized_1 == serialized_2  # key order in the source dict must not affect output

    path = tmp_path / "reviewed.jsonl"
    path.write_text(serialized_1 + "\n")
    reloaded = load_reviewed_labels(path)
    assert reloaded["a/H-01"] == row


# --- required test 13: incorrect claims use the same citation resolver ----


def test_evaluate_incorrect_claim_uses_same_citation_resolver():
    """Points an incorrect claim's citation at Vault.withdraw()'s real span
    in the fixture graph -- must resolve via the identical
    resolve_citation_string pipeline `_evaluate_finding` uses, producing a
    RESOLVED gate row with the correct routing unit."""
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    claim = {
        "incorrect_finding_id": "fake-audit/incorrect/high/H-01", "audit_id": "fake-audit", "severity": "high",
        "title": "Reentrancy claim in withdraw (rejected)",
        "github_cited_locations": ["https://github.com/fake/fake-audit/blob/deadbeef/Vault.sol#L34-L43"],
        "source_path": None,
    }
    rows = _evaluate_incorrect_claim(claim, pg, features, spec, FIXTURES, "multi_contract")
    assert rows[0]["citation_outcome"] == "RESOLVED"
    assert rows[0]["routing_unit"] == "fn::Vault.withdraw(uint256)"
    assert rows[0]["expected_primary_family"] == "P2_REENTRANCY"


def test_evaluate_incorrect_claim_retains_severity_and_no_review_applied():
    pg = ProgramGraph.build(VAULT_SOL)
    features = FeatureExtractor.compute(pg)
    spec = load_routing_spec(ROUTING_SPEC)
    claim = {
        "incorrect_finding_id": "fake-audit/incorrect/low/H-02", "audit_id": "fake-audit", "severity": "low",
        "title": "Unrelated gas griefing claim", "github_cited_locations": [], "source_path": None,
    }
    rows = _evaluate_incorrect_claim(claim, pg, features, spec, FIXTURES, "multi_contract")
    assert rows[0]["severity"] == "low"
    assert rows[0]["reviewed"] is False


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
