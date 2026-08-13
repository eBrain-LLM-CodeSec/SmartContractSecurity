"""Unit tests for rtf.l11_investigation_grouping.protocol_context (RTF v2
Phase 3). Real Slither compilation, real StandardsRegistry (no mocks) --
same discipline as rtf.standards.test_discovery, whose IERC4626 fixture
this file reuses. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_protocol_context
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l5_predicates.compile_helper import compile_evmbench_target
from rtf.l11_investigation_grouping.protocol_context import (
    extract_accounting_state_variables, extract_applicable_standards_obligations,
    extract_lifecycle_hints, extract_protocol_purpose, generate_enriched_protocol_context_md,
    generate_protocol_context_narrative_md,
)
from rtf.standards.registry import StandardsRegistry

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


_PLAIN_CONTRACT = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Plain {
    uint256 public counter;
    function bump() external { counter += 1; }
}
"""

_IERC4626_INTERFACE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

interface IERC4626 is IERC20 {
    function asset() external view returns (address);
    function totalAssets() external view returns (uint256);
    function convertToShares(uint256 assets) external view returns (uint256);
    function convertToAssets(uint256 shares) external view returns (uint256);
    function maxDeposit(address receiver) external view returns (uint256);
    function previewDeposit(uint256 assets) external view returns (uint256);
    function deposit(uint256 assets, address receiver) external returns (uint256);
    function maxMint(address receiver) external view returns (uint256);
    function previewMint(uint256 shares) external view returns (uint256);
    function mint(uint256 shares, address receiver) external returns (uint256);
    function maxWithdraw(address owner) external view returns (uint256);
    function previewWithdraw(uint256 assets) external view returns (uint256);
    function withdraw(uint256 assets, address receiver, address owner) external returns (uint256);
    function maxRedeem(address owner) external view returns (uint256);
    function previewRedeem(uint256 shares) external view returns (uint256);
    function redeem(uint256 shares, address receiver, address owner) external returns (uint256);

    event Deposit(address indexed sender, address indexed owner, uint256 assets, uint256 shares);
    event Withdraw(address indexed sender, address indexed receiver, address indexed owner, uint256 assets, uint256 shares);
}
"""

_ERC20_METHOD_BODIES = """
    mapping(address => uint256) public balanceOf_;
    function totalSupply() external pure returns (uint256) { return 0; }
    function balanceOf(address account) external view returns (uint256) { return balanceOf_[account]; }
    function transfer(address, uint256) external returns (bool) { return true; }
    function allowance(address, address) external pure returns (uint256) { return 0; }
    function approve(address, uint256) external returns (bool) { return true; }
    function transferFrom(address, address, uint256) external returns (bool) { return true; }
"""

_ERC4626_METHOD_BODIES = """
    function asset() external pure returns (address) { return address(0); }
    function totalAssets() external view returns (uint256) { return _totalAssets - managementFee; }
    function convertToShares(uint256 assets) external pure returns (uint256) { return assets; }
    function convertToAssets(uint256 shares) external pure returns (uint256) { return shares; }
    function maxDeposit(address) external pure returns (uint256) { return 0; }
    function previewDeposit(uint256 assets) external pure returns (uint256) { return assets; }
    function deposit(uint256 assets, address) external returns (uint256) { return assets; }
    function maxMint(address) external pure returns (uint256) { return 0; }
    function previewMint(uint256 shares) external pure returns (uint256) { return shares; }
    function mint(uint256 shares, address) external returns (uint256) { return shares; }
    function maxWithdraw(address) external pure returns (uint256) { return 0; }
    function previewWithdraw(uint256 assets) external pure returns (uint256) { return assets; }
    function withdraw(uint256 assets, address, address) external returns (uint256) { return assets; }
    function maxRedeem(address) external pure returns (uint256) { return 0; }
    function previewRedeem(uint256 shares) external pure returns (uint256) { return shares; }
    function redeem(uint256 shares, address, address) external returns (uint256) { return shares; }
"""

_VAULT_WITH_LIFECYCLE = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

contract Initializable {{
    bool private _initialized;
    modifier initializer() {{
        require(!_initialized, "already initialized");
        _initialized = true;
        _;
    }}
}}

contract MyVault is IERC4626, Initializable {{
    uint256 public managementFee;
    uint256 public _totalAssets;
    address public treasury;

    function init() external initializer {{
        treasury = msg.sender;
    }}

{_ERC20_METHOD_BODIES}
{_ERC4626_METHOD_BODIES}
}}
"""


def _write_interfaces(repo: Path) -> None:
    (repo / "interfaces").mkdir(parents=True, exist_ok=True)
    (repo / "interfaces" / "IERC4626.sol").write_text(_IERC4626_INTERFACE, encoding="utf-8")


def _compile_vault(repo: Path):
    _write_interfaces(repo)
    (repo / "MyVault.sol").write_text(_VAULT_WITH_LIFECYCLE, encoding="utf-8")
    return compile_evmbench_target(repo / "MyVault.sol", repo, solc_version="0.8.20")


def _compile_plain(repo: Path):
    (repo / "Plain.sol").write_text(_PLAIN_CONTRACT, encoding="utf-8")
    return compile_evmbench_target(repo / "Plain.sol", repo, solc_version="0.8.20")


# --- extract_protocol_purpose ---------------------------------------------

def test_extract_protocol_purpose_from_readme():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        readme = (
            "# MyVault\n\n"
            "[![Build](https://img.shields.io/badge/build-passing-green)]()\n\n"
            "MyVault is a yield-bearing ERC-4626 vault that charges a management fee "
            "on assets under management.\n\n"
            "## Usage\n\nSee the docs.\n"
        )
        (repo / "README.md").write_text(readme, encoding="utf-8")
        result = extract_protocol_purpose(repo)
        check("purpose: found a real excerpt", result is not None, result)
        excerpt, citation = result
        check("purpose: skips heading/badge lines, finds the real paragraph",
              "yield-bearing ERC-4626 vault" in excerpt, excerpt)
        check("purpose: cites README.md", citation == "README.md", citation)


def test_extract_protocol_purpose_none_without_readme():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        result = extract_protocol_purpose(repo)
        check("purpose: None (not fabricated) when no README exists", result is None, result)


def test_extract_protocol_purpose_none_when_only_headings_and_badges():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "README.md").write_text("# Title\n\n[![CI](url)]()\n\n![logo](url)\n", encoding="utf-8")
        result = extract_protocol_purpose(repo)
        check("purpose: None when README has no real descriptive paragraph", result is None, result)


# --- extract_applicable_standards_obligations -----------------------------

def test_extract_applicable_standards_obligations_derives_concrete_clauses():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        slither = _compile_vault(repo)
        obligations = extract_applicable_standards_obligations(repo, repo / "MyVault.sol", slither, StandardsRegistry())
        erc4626 = next((o for o in obligations if o["standard_id"] == "ERC-4626"), None)
        check("obligations: ERC-4626 detected as applicable", erc4626 is not None, obligations)
        check("obligations: MyVault named as the implementing contract",
              erc4626 is not None and "MyVault" in erc4626["contracts"], erc4626)
        check("obligations: NOT just the bare applicability fact -- real clause obligations present",
              erc4626 is not None and len(erc4626["obligations"]) > 10, erc4626 and len(erc4626["obligations"]))
        totalassets_clause = erc4626 and next(
            (ob for ob in erc4626["obligations"] if ob["clause_id"] == "erc4626-totalassets-must-include-fees"), None,
        )
        check("obligations: the totalAssets/fees clause is present with its real obligation text",
              totalassets_clause is not None and "fee" in totalassets_clause["obligation_text"].lower(),
              totalassets_clause)


def test_extract_applicable_standards_obligations_empty_for_unrelated_contract():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        slither = _compile_plain(repo)
        obligations = extract_applicable_standards_obligations(repo, repo / "Plain.sol", slither, StandardsRegistry())
        check("obligations: no standard applicable to an unrelated plain contract", obligations == [], obligations)


# --- extract_accounting_state_variables -----------------------------------

def test_extract_accounting_state_variables_finds_fee_and_treasury_style_names():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        slither = _compile_vault(repo)
        found = extract_accounting_state_variables(slither)
        names = {(c, v) for c, v, _kw in found}
        check("accounting vars: managementFee found", ("MyVault", "managementFee") in names, found)
        check("accounting vars: _totalAssets found (matches 'asset')", ("MyVault", "_totalAssets") in names, found)
        check("accounting vars: matched keyword is a real substring of the var name",
              all(kw in v.lower() for _c, v, kw in found), found)


def test_extract_accounting_state_variables_empty_for_unrelated_contract():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        slither = _compile_plain(repo)
        found = extract_accounting_state_variables(slither)
        check("accounting vars: none found for a plain counter contract", found == [], found)


# --- extract_lifecycle_hints -----------------------------------------------

def test_extract_lifecycle_hints_detects_initializable_inheritance_and_modifier():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        slither = _compile_vault(repo)
        hints = extract_lifecycle_hints(slither)
        joined = " ".join(hints)
        check("lifecycle: MyVault's Initializable inheritance detected", "Initializable" in joined, hints)
        check("lifecycle: init()'s initializer modifier detected", "initializer" in joined.lower(), hints)


def test_extract_lifecycle_hints_empty_for_plain_contract():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        slither = _compile_plain(repo)
        hints = extract_lifecycle_hints(slither)
        check("lifecycle: no signals for a plain contract", hints == [], hints)


# --- generate_protocol_context_narrative_md / generate_enriched_... -------

def test_narrative_md_has_fallbacks_when_nothing_grounded():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        slither = _compile_plain(repo)
        md = generate_protocol_context_narrative_md(repo, repo / "Plain.sol", slither)
        check("narrative: purpose section present", "## Protocol purpose" in md, md)
        check("narrative: purpose fallback, not fabricated", "not available" in md, md)
        check("narrative: standards section present", "## Applicable external standards" in md, md)
        check("narrative: standards fallback when none applicable",
              "no external standard confirmed applicable" in md, md)
        check("narrative: accounting section present", "## Accounting-relevant state variables" in md, md)
        check("narrative: lifecycle section present", "## Lifecycle" in md, md)


def test_narrative_md_grounds_every_claim_for_the_vault_fixture():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        slither = _compile_vault(repo)
        (repo / "README.md").write_text(
            "# MyVault\n\nMyVault is an ERC-4626 vault with a management fee.\n", encoding="utf-8",
        )
        md = generate_protocol_context_narrative_md(repo, repo / "MyVault.sol", slither)
        check("narrative: README purpose excerpt present, cited", "verbatim excerpt from `README.md`" in md, md)
        check("narrative: ERC-4626 obligations section present", "ERC-4626" in md and "erc4626-totalassets-must-include-fees" in md, md)
        check("narrative: managementFee flagged as accounting-relevant", "managementFee" in md, md)
        check("narrative: Initializable lifecycle hint present", "Initializable" in md, md)


def test_enriched_protocol_context_md_is_superset_of_base():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        slither = _compile_vault(repo)
        enriched = generate_enriched_protocol_context_md(
            "test-audit", repo, repo / "MyVault.sol", slither, scope_files=["MyVault.sol"],
        )
        check("enriched: base structural header present", "# Protocol context: test-audit" in enriched, enriched[:200])
        check("enriched: base 'In-scope contracts' section present", "## In-scope contracts" in enriched, enriched)
        check("enriched: new narrative section present", "## Protocol purpose" in enriched, enriched)
        check("enriched: base section still appears BEFORE the narrative sections",
              enriched.index("## In-scope contracts") < enriched.index("## Protocol purpose"))


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
