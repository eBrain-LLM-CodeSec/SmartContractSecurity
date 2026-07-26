"""Phase 1: repair.py's bounded env-repair loop.

Fixable case: a fixture pinned to an old solc version (via `pragma solidity
^0.4.24`) while the global solc-select version is left at something newer --
repair.py must detect the version, install/switch solc, and succeed.

Unfixable case: a syntactically-broken fixture must exhaust the repair
budget, log repair.jsonl, and raise BuildFailed -- never produce a partial
graph.
"""
from pathlib import Path

import pytest

from a4v.graph import BuildFailed
from a4v.repair import EnvRepair

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
WRONG_SOLC = FIXTURES / "wrong_solc" / "OldStyle.sol"
UNBUILDABLE = FIXTURES / "unbuildable" / "Broken.sol"


@pytest.fixture(autouse=True)
def _clean_repair_logs():
    for f in (FIXTURES / "wrong_solc" / "repair.jsonl", FIXTURES / "unbuildable" / "repair.jsonl"):
        f.unlink(missing_ok=True)
    yield


def test_repair_fixes_wrong_solc_version():
    repair = EnvRepair(max_attempts=6, max_wall_clock_seconds=300)
    result = repair.build_until_success(WRONG_SOLC)
    assert result.solc_version == "0.4.24"
    assert "fn::OldStyle.setValue(uint256)" in result.graph.graph.nodes


def test_repair_exhausts_budget_on_unbuildable_fixture():
    repair = EnvRepair(max_attempts=6, max_wall_clock_seconds=60)
    log_path = UNBUILDABLE.parent / "repair.jsonl"

    with pytest.raises(BuildFailed):
        repair.build_until_success(UNBUILDABLE)

    assert log_path.exists()
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) >= 1
    assert all("ok" in line for line in lines)
