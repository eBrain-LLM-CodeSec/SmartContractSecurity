import networkx as nx
import numpy as np

from a4v.gnn.etl.labels import Annotation, LabelRecord
from a4v.gnn.etl.map_labels import map_to_nodes


class FakeGraph:
    """Duck-types ProgramGraph's `.graph` attribute so map_labels can be
    unit-tested without a real Slither compile.
    """

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph


def _graph_with_nodes(nodes: dict) -> FakeGraph:
    g = nx.MultiDiGraph()
    for nid, attrs in nodes.items():
        g.add_node(nid, **attrs)
    return FakeGraph(g)


CLASS_NAMES = ["reentrancy", "unchecked_call", "access_control"]


def test_line_granularity_maps_only_matching_file_and_overlapping_lines():
    graph = _graph_with_nodes({
        "fn::A.f": {"kind": "function", "name": "f", "contract": "A", "file": "A.sol", "lines": [10, 11, 12]},
        "fn::A.g": {"kind": "function", "name": "g", "contract": "A", "file": "A.sol", "lines": [20, 21]},
        "fn::B.f": {"kind": "function", "name": "f", "contract": "B", "file": "B.sol", "lines": [10, 11, 12]},
    })
    record = LabelRecord(
        native_id="X", granularity="line",
        annotations=(Annotation(vuln_class="reentrancy", file="A.sol", lines=(11,)),),
    )
    result = map_to_nodes(record, graph, CLASS_NAMES)
    row = {nid: i for i, nid in enumerate(result.node_ids)}
    assert result.node_labels[row["fn::A.f"], 0] == 1
    assert result.node_labels[row["fn::A.g"], 0] == 0
    # Same line number, different file -- must NOT bleed across files.
    assert result.node_labels[row["fn::B.f"], 0] == 0


def test_line_granularity_nodes_missing_file_or_lines_are_unmappable():
    graph = _graph_with_nodes({
        "ext::<low-level-call>": {"kind": "function", "name": "<low-level-call>", "external": True},
        "fn::A.f": {"kind": "function", "name": "f", "contract": "A", "file": "A.sol", "lines": [1, 2]},
    })
    record = LabelRecord(
        native_id="X", granularity="line",
        annotations=(Annotation(vuln_class="reentrancy", file="A.sol", lines=(1,)),),
    )
    result = map_to_nodes(record, graph, CLASS_NAMES)
    row = {nid: i for i, nid in enumerate(result.node_ids)}
    assert result.node_labels[row["ext::<low-level-call>"], 0] == 0
    assert result.node_labels[row["fn::A.f"], 0] == 1
    assert result.unmappable_annotation_count == 0


def test_line_annotation_with_no_overlap_is_unmappable():
    graph = _graph_with_nodes({
        "fn::A.f": {"kind": "function", "name": "f", "contract": "A", "file": "A.sol", "lines": [1, 2]},
    })
    record = LabelRecord(
        native_id="X", granularity="line",
        annotations=(Annotation(vuln_class="reentrancy", file="A.sol", lines=(99,)),),
    )
    result = map_to_nodes(record, graph, CLASS_NAMES)
    assert result.node_labels.sum() == 0
    assert result.unmappable_annotation_count == 1


def test_function_granularity_keyed_by_contract_name_signature_avoids_overload_collision():
    graph = _graph_with_nodes({
        "fn::A.f#1": {"kind": "function", "name": "f", "contract": "A", "canonical_name": "A.f(uint256)"},
        "fn::A.f#2": {"kind": "function", "name": "f", "contract": "A", "canonical_name": "A.f(address)"},
    })
    record = LabelRecord(
        native_id="X", granularity="function",
        annotations=(Annotation(vuln_class="access_control", contract="A", function_name="f", signature="(address)"),),
    )
    result = map_to_nodes(record, graph, CLASS_NAMES)
    row = {nid: i for i, nid in enumerate(result.node_ids)}
    assert result.node_labels[row["fn::A.f#1"], 2] == 0
    assert result.node_labels[row["fn::A.f#2"], 2] == 1


def test_function_granularity_no_signature_ambiguous_overload_is_logged_not_guessed():
    graph = _graph_with_nodes({
        "fn::A.f#1": {"kind": "function", "name": "f", "contract": "A", "canonical_name": "A.f(uint256)"},
        "fn::A.f#2": {"kind": "function", "name": "f", "contract": "A", "canonical_name": "A.f(address)"},
    })
    record = LabelRecord(
        native_id="X", granularity="function",
        annotations=(Annotation(vuln_class="access_control", contract="A", function_name="f"),),
    )
    result = map_to_nodes(record, graph, CLASS_NAMES)
    assert result.node_labels.sum() == 0
    assert len(result.ambiguous) == 1
    assert set(result.ambiguous[0].candidate_node_ids) == {"fn::A.f#1", "fn::A.f#2"}


def test_function_granularity_no_signature_unambiguous_match_still_works():
    graph = _graph_with_nodes({
        "fn::A.f": {"kind": "function", "name": "f", "contract": "A", "canonical_name": "A.f(uint256)"},
        "fn::B.f": {"kind": "function", "name": "f", "contract": "B", "canonical_name": "B.f(uint256)"},
    })
    record = LabelRecord(
        native_id="X", granularity="function",
        annotations=(Annotation(vuln_class="access_control", contract="A", function_name="f"),),
    )
    result = map_to_nodes(record, graph, CLASS_NAMES)
    row = {nid: i for i, nid in enumerate(result.node_ids)}
    assert result.node_labels[row["fn::A.f"], 2] == 1
    assert result.node_labels[row["fn::B.f"], 2] == 0
    assert result.ambiguous == []


def test_function_granularity_base_derived_same_name_is_keyed_by_declaring_contract():
    # Base and derived contract both declare `withdraw` -- keying on
    # (contract, name, sig) means an annotation for the base doesn't light
    # up the derived override, and vice versa.
    graph = _graph_with_nodes({
        "fn::Base.withdraw": {"kind": "function", "name": "withdraw", "contract": "Base", "canonical_name": "Base.withdraw()"},
        "fn::Derived.withdraw": {"kind": "function", "name": "withdraw", "contract": "Derived", "canonical_name": "Derived.withdraw()"},
    })
    record = LabelRecord(
        native_id="X", granularity="function",
        annotations=(Annotation(vuln_class="reentrancy", contract="Derived", function_name="withdraw", signature="()"),),
    )
    result = map_to_nodes(record, graph, CLASS_NAMES)
    row = {nid: i for i, nid in enumerate(result.node_ids)}
    assert result.node_labels[row["fn::Derived.withdraw"], 0] == 1
    assert result.node_labels[row["fn::Base.withdraw"], 0] == 0


def test_file_granularity_sets_graph_labels_not_node_labels():
    graph = _graph_with_nodes({
        "fn::A.f": {"kind": "function", "name": "f", "contract": "A"},
    })
    record = LabelRecord(
        native_id="X", granularity="file",
        annotations=(Annotation(vuln_class="reentrancy"), Annotation(vuln_class="access_control")),
    )
    result = map_to_nodes(record, graph, CLASS_NAMES)
    assert result.node_labels is None
    assert isinstance(result.graph_labels, np.ndarray)
    assert result.graph_labels.tolist() == [1, 0, 1]
