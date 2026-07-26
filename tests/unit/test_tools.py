from pathlib import Path

import pytest

from a4v.graph import ProgramGraph
from a4v.tools import InvestigationTools, SandboxError

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"


def test_read_file_within_sandbox_works():
    pg = ProgramGraph.build(VAULT_SOL)
    tools = InvestigationTools(pg, checkout_dir=FIXTURES / "multi_contract")
    content = tools.read_file(str(VAULT_SOL), start_line=1, end_line=5)
    assert "pragma solidity" in content


def test_read_file_outside_sandbox_raises():
    pg = ProgramGraph.build(VAULT_SOL)
    tools = InvestigationTools(pg, checkout_dir=FIXTURES / "multi_contract")
    with pytest.raises(SandboxError):
        tools.read_file("/etc/passwd")


def test_grep_outside_sandbox_raises():
    pg = ProgramGraph.build(VAULT_SOL)
    tools = InvestigationTools(pg, checkout_dir=FIXTURES / "multi_contract")
    with pytest.raises(SandboxError):
        tools.grep("root", path="/etc")


def test_slither_detector_outside_sandbox_raises():
    pg = ProgramGraph.build(VAULT_SOL)
    tools = InvestigationTools(pg, checkout_dir=FIXTURES / "multi_contract")
    with pytest.raises(SandboxError):
        tools.slither_detector("reentrancy-eth", "/etc/passwd")


def test_graph_query_cache_avoids_recompute(tmp_path, monkeypatch):
    pg = ProgramGraph.build(VAULT_SOL)
    tools = InvestigationTools(pg, checkout_dir=FIXTURES / "multi_contract", cache_dir=tmp_path / "cache")

    call_count = {"n": 0}
    real = pg.neighbors_by_kind

    def counting(*args, **kwargs):
        call_count["n"] += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(pg, "neighbors_by_kind", counting)

    r1 = tools.graph_query("fn::Vault.withdraw(uint256)", "external_call")
    r2 = tools.graph_query("fn::Vault.withdraw(uint256)", "external_call")
    assert r1 == r2
    assert call_count["n"] == 1, "second call should hit the on-disk cache, not recompute"


def test_expand_bundle_cache_key_distinguishes_hops(tmp_path):
    pg = ProgramGraph.build(VAULT_SOL)
    tools = InvestigationTools(pg, checkout_dir=FIXTURES / "multi_contract", cache_dir=tmp_path / "cache")
    b1 = tools.expand_bundle("fn::Vault.withdraw(uint256)", hops=1)
    b2 = tools.expand_bundle("fn::Vault.withdraw(uint256)", hops=2)
    assert b1["seed"] == b2["seed"]
    # different hop counts must not collide in the cache
    cache_files = list((tmp_path / "cache" / "expand_bundle").glob("*.json"))
    assert len(cache_files) == 2
