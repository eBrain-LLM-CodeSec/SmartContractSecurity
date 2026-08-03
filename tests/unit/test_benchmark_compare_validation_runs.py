"""Tests for scripts.benchmark.compare_validation_runs -- Phase 6's
cross-run comparison must flag every mismatch explicitly, never average or
silently drop one."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.benchmark.compare_validation_runs import compare, load_run


def _make_run(tmp_path, name, build_rows, graph_rows, route_count=3, gate_count=2,
               order=None, findings_reached=5):
    run_dir = tmp_path / name
    (run_dir / "study_full").mkdir(parents=True)
    (run_dir / "study_full" / "build_manifest.jsonl").write_text(
        "\n".join(json.dumps(r) for r in build_rows) + "\n")
    (run_dir / "study_full" / "graph_manifest.jsonl").write_text(
        "\n".join(json.dumps(r) for r in graph_rows) + "\n")
    (run_dir / "study_full" / "route_manifest.jsonl").write_text(
        "\n".join(json.dumps({"i": i}) for i in range(route_count)) + "\n")
    (run_dir / "study_full" / "gate_evaluation.jsonl").write_text(
        "\n".join(json.dumps({"i": i}) for i in range(gate_count)) + "\n")
    (run_dir / "study_full" / "feasibility_report.json").write_text(
        json.dumps({"findings_reached_compiled_audits": findings_reached}))
    (run_dir / "study_full" / "audit_order.json").write_text(
        json.dumps({"seed": name, "order": order or ["a", "b"]}))
    return run_dir


def test_identical_runs_produce_no_mismatches(tmp_path):
    build_rows = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": {"versions": ["0.8.20"]}}]
    graph_rows = [{"audit_id": "a", "node_counts": {"contract": 3}}]
    r1 = load_run(_make_run(tmp_path, "run1", build_rows, graph_rows, order=["a"]))
    r2 = load_run(_make_run(tmp_path, "run2", build_rows, graph_rows, order=["a"]))
    result = compare([r1, r2])
    assert result["mismatches"] == []
    assert result["identical_coverage_and_graph_counts"] is True


def test_build_status_mismatch_is_flagged(tmp_path):
    rows1 = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": None}]
    rows2 = [{"audit_id": "a", "status": "TOOLCHAIN_NOT_PROVISIONED", "compiler_selection": None}]
    r1 = load_run(_make_run(tmp_path, "run1", rows1, [{"audit_id": "a", "node_counts": {}}]))
    r2 = load_run(_make_run(tmp_path, "run2", rows2, []))
    result = compare([r1, r2])
    kinds = [m["kind"] for m in result["mismatches"]]
    assert "build_status" in kinds
    assert "compiled_audit_set" in kinds
    assert result["identical_coverage_and_graph_counts"] is False


def test_graph_node_count_mismatch_is_flagged_even_when_both_compiled(tmp_path):
    """A real reproducibility failure this must NOT hide: same audit
    compiles in both runs, but produces a different graph -- e.g. a
    non-deterministic build. Never averaged away."""
    build_rows = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": {"versions": ["0.8.20"]}}]
    r1 = load_run(_make_run(tmp_path, "run1", build_rows, [{"audit_id": "a", "node_counts": {"contract": 3}}]))
    r2 = load_run(_make_run(tmp_path, "run2", build_rows, [{"audit_id": "a", "node_counts": {"contract": 4}}]))
    result = compare([r1, r2])
    assert any(m["kind"] == "graph_node_counts" for m in result["mismatches"])
    assert result["identical_coverage_and_graph_counts"] is False


def test_compiler_selection_detail_path_difference_is_not_a_mismatch(tmp_path):
    """Regression guard for a real false positive found live comparing the
    actual sbatch job's three runs: `detail` legitimately embeds each
    run's own checkout path (fresh WORK_DIR per run, by design), so two
    runs that selected the identical version via the identical mechanism
    must NOT be flagged as mismatched just because their `detail` strings
    differ only in an embedded run-scoped path."""
    build_rows_1 = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": {
        "status": "RESOLVED", "versions": ["0.8.17"], "mode": "single_use_pin",
        "detail": "resolved from [profile.default] (/run1/checkouts/a/foundry.toml)",
    }}]
    build_rows_2 = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": {
        "status": "RESOLVED", "versions": ["0.8.17"], "mode": "single_use_pin",
        "detail": "resolved from [profile.default] (/run2/checkouts/a/foundry.toml)",
    }}]
    graph_rows = [{"audit_id": "a", "node_counts": {"contract": 3}}]
    r1 = load_run(_make_run(tmp_path, "run1", build_rows_1, graph_rows))
    r2 = load_run(_make_run(tmp_path, "run2", build_rows_2, graph_rows))
    result = compare([r1, r2])
    assert result["mismatches"] == []


def test_compiler_selection_mismatch_is_flagged(tmp_path):
    build_rows_1 = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": {"versions": ["0.8.20"]}}]
    build_rows_2 = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": {"versions": ["0.8.19"]}}]
    graph_rows = [{"audit_id": "a", "node_counts": {"contract": 3}}]
    r1 = load_run(_make_run(tmp_path, "run1", build_rows_1, graph_rows))
    r2 = load_run(_make_run(tmp_path, "run2", build_rows_2, graph_rows))
    result = compare([r1, r2])
    assert any(m["kind"] == "compiler_selection" for m in result["mismatches"])


def test_route_and_gate_row_counts_compared(tmp_path):
    build_rows = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": None}]
    graph_rows = [{"audit_id": "a", "node_counts": {"contract": 3}}]
    r1 = load_run(_make_run(tmp_path, "run1", build_rows, graph_rows, route_count=5, gate_count=2))
    r2 = load_run(_make_run(tmp_path, "run2", build_rows, graph_rows, route_count=4, gate_count=2))
    result = compare([r1, r2])
    kinds = [m["kind"] for m in result["mismatches"]]
    assert "route_manifest_row_count" in kinds


def test_findings_reached_mismatch_flagged(tmp_path):
    build_rows = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": None}]
    graph_rows = [{"audit_id": "a", "node_counts": {}}]
    r1 = load_run(_make_run(tmp_path, "run1", build_rows, graph_rows, findings_reached=10))
    r2 = load_run(_make_run(tmp_path, "run2", build_rows, graph_rows, findings_reached=9))
    result = compare([r1, r2])
    assert any(m["kind"] == "findings_reached_compiled_audits" for m in result["mismatches"])


def test_randomized_orders_detected_as_distinct(tmp_path):
    build_rows = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": None}]
    graph_rows = [{"audit_id": "a", "node_counts": {}}]
    r1 = load_run(_make_run(tmp_path, "run1", build_rows, graph_rows, order=["a", "b", "c"]))
    r2 = load_run(_make_run(tmp_path, "run2", build_rows, graph_rows, order=["c", "a", "b"]))
    r3 = load_run(_make_run(tmp_path, "run3", build_rows, graph_rows, order=["b", "c", "a"]))
    result = compare([r1, r2, r3])
    assert result["audit_orders_were_genuinely_randomized_and_distinct"] is True


def test_identical_orders_detected_as_not_randomized(tmp_path):
    build_rows = [{"audit_id": "a", "status": "COMPILED", "compiler_selection": None}]
    graph_rows = [{"audit_id": "a", "node_counts": {}}]
    r1 = load_run(_make_run(tmp_path, "run1", build_rows, graph_rows, order=["a", "b"]))
    r2 = load_run(_make_run(tmp_path, "run2", build_rows, graph_rows, order=["a", "b"]))
    result = compare([r1, r2])
    assert result["audit_orders_were_genuinely_randomized_and_distinct"] is False
