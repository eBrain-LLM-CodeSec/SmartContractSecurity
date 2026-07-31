"""Fast, hermetic tests for build_manifests.py's SKIPPED/COMPILED/
COMPILE_FAILED branching -- mocks EnvRepair.build_until_success so the unit
suite doesn't depend on network/solc/forge availability. The real compile
path was validated separately against actual EVMbench audit checkouts
(2023-07-pooltogether, 2026-01-tempo-feeamm both COMPILED; 2025-04-forte
COMPILE_FAILED for a documented pre-existing solc-version-matching gap in
agent4vul/bin/forge's shim, unrelated to this script's own logic)."""
from pathlib import Path
from unittest.mock import MagicMock

import networkx as nx
import pytest

from a4v.graph import BuildFailed, ProgramGraph
from a4v.repair import BuildResult
from scripts.mgpr.build_manifests import _run_cmd_dir, build_manifest_for_audit


def _fake_graph() -> ProgramGraph:
    g = nx.MultiDiGraph()
    g.add_node("contract::C", kind="contract", name="C")
    g.add_node("fn::C.f()", kind="function", name="f", contract="C")
    g.add_edge("contract::C", "fn::C.f()", kind="declares")
    return ProgramGraph(g, slither=None)


def test_skipped_when_no_checkouts_dir(tmp_path):
    row, graph_row, graph = build_manifest_for_audit(
        "some-audit", evmbench_root=tmp_path, checkouts_dir=None, repair=MagicMock()
    )
    assert row["status"] == "SKIPPED"
    assert row["reason"] == "no local checkout available"
    assert graph_row["status"] == "SKIPPED"
    assert graph is None


def test_skipped_when_checkout_missing(tmp_path):
    checkouts_dir = tmp_path / "checkouts"
    checkouts_dir.mkdir()
    row, graph_row, graph = build_manifest_for_audit(
        "not-present-audit", evmbench_root=tmp_path, checkouts_dir=checkouts_dir, repair=MagicMock()
    )
    assert row["status"] == "SKIPPED"
    assert graph is None


def test_compiled_when_repair_succeeds(tmp_path):
    checkouts_dir = tmp_path / "checkouts"
    (checkouts_dir / "audit-1").mkdir(parents=True)
    repair = MagicMock()
    repair.build_until_success.return_value = BuildResult(graph=_fake_graph(), solc_version="0.8.20", attempts=[])

    row, graph_row, graph = build_manifest_for_audit(
        "audit-1", evmbench_root=tmp_path, checkouts_dir=checkouts_dir, repair=repair
    )
    assert row["status"] == "COMPILED"
    assert row["solc_version"] == "0.8.20"
    assert row["reason"] is None
    assert graph_row["status"] == "COMPILED"
    assert graph_row["node_counts"] == {"contract": 1, "function": 1}
    assert graph_row["edge_counts"] == {"declares": 1}
    assert graph is not None


def test_compile_failed_when_repair_raises(tmp_path):
    checkouts_dir = tmp_path / "checkouts"
    (checkouts_dir / "audit-1").mkdir(parents=True)
    repair = MagicMock()
    repair.build_until_success.side_effect = BuildFailed("exhausted repair budget")

    row, graph_row, graph = build_manifest_for_audit(
        "audit-1", evmbench_root=tmp_path, checkouts_dir=checkouts_dir, repair=repair
    )
    assert row["status"] == "COMPILE_FAILED"
    assert "exhausted repair budget" in row["reason"]
    assert graph_row["status"] == "COMPILE_FAILED"
    assert graph is None


def test_run_cmd_dir_defaults_to_dot_without_config(tmp_path):
    assert _run_cmd_dir(tmp_path, "no-such-audit") == "."


def test_run_cmd_dir_reads_config_yaml(tmp_path):
    audit_dir = tmp_path / "audits" / "pooltogether-like"
    audit_dir.mkdir(parents=True)
    (audit_dir / "config.yaml").write_text("framework: foundry-json\nrun_cmd_dir: vault\n")
    assert _run_cmd_dir(tmp_path, "pooltogether-like") == "vault"


def test_repair_target_uses_run_cmd_dir_subdirectory(tmp_path):
    """Confirms build_manifest_for_audit actually joins checkout_root with
    the audit's run_cmd_dir before calling repair -- not just reading the
    config value and ignoring it (the real pooltogether audit needs its
    `vault/` subdirectory compiled, not the checkout root)."""
    checkouts_dir = tmp_path / "checkouts"
    (checkouts_dir / "audit-1" / "vault").mkdir(parents=True)
    (tmp_path / "audits" / "audit-1").mkdir(parents=True)
    (tmp_path / "audits" / "audit-1" / "config.yaml").write_text("run_cmd_dir: vault\n")

    repair = MagicMock()
    repair.build_until_success.return_value = BuildResult(graph=_fake_graph(), solc_version="0.8.20", attempts=[])

    build_manifest_for_audit("audit-1", evmbench_root=tmp_path, checkouts_dir=checkouts_dir, repair=repair)
    called_target = repair.build_until_success.call_args[0][0]
    assert Path(called_target) == checkouts_dir / "audit-1" / "vault"
