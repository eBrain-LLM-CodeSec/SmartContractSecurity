"""Synthetic-repo tests for rtf.standards.discovery, per the implementation
plan's §13C (standard-discovery), §14 (ERC-4626 fixtures 1-6), and §15
(multi-standard fixtures). Every fixture is a real, temp-directory Solidity
repository compiled with a real Slither object (via
`rtf.l5_predicates.compile_helper.compile_evmbench_target`), not mocked.
Run with:
    python3 -m rtf.standards.test_discovery
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l5_predicates.compile_helper import compile_evmbench_target

from .discovery import discover_applicable_standards
from .models import DetectionConfidence
from .registry import StandardsRegistry

PASSES = []
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


IERC4626_INTERFACE = """// SPDX-License-Identifier: MIT
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
    function totalAssets() external pure returns (uint256) { return 0; }
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


def _write_interfaces(repo: Path) -> None:
    (repo / "interfaces").mkdir(parents=True, exist_ok=True)
    (repo / "interfaces" / "IERC4626.sol").write_text(IERC4626_INTERFACE, encoding="utf-8")


def _compile(repo: Path, entry_relpath: str):
    return compile_evmbench_target(repo / entry_relpath, repo, solc_version="0.8.20")


def _registry() -> StandardsRegistry:
    return StandardsRegistry()


# --- Fixture 1: correct/complete ERC-4626 implementation -----------------

def test_fixture1_correct_implementation():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_interfaces(repo)
        source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

contract MyVault is IERC4626 {{
{_ERC20_METHOD_BODIES}
{_ERC4626_METHOD_BODIES}
}}
"""
        (repo / "MyVault.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "MyVault.sol")
        results = discover_applicable_standards(repo, repo / "MyVault.sol", slither, _registry())
        erc4626 = next(r for r in results if r.standard_id == "ERC-4626")
        check("fixture1: ERC-4626 discovered as APPLICABLE", erc4626.applicable == DetectionConfidence.APPLICABLE, erc4626)
        check("fixture1: MyVault identified as the implementing contract", "MyVault" in erc4626.contracts, erc4626.contracts)


# --- Fixture 2: relevant logic appears after >8000 chars ------------------

def test_fixture2_late_file_implementation():
    padding = "// filler comment line to push real content past 8000 chars\n" * 200  # ~62 chars * 200 = ~12,400 chars
    assert len(padding) > 8000, "fixture2 padding must exceed 8000 chars to actually test the regression"
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_interfaces(repo)
        source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

{padding}

contract LateVault is IERC4626 {{
{_ERC20_METHOD_BODIES}
{_ERC4626_METHOD_BODIES}
}}
"""
        (repo / "LateVault.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "LateVault.sol")
        results = discover_applicable_standards(repo, repo / "LateVault.sol", slither, _registry())
        erc4626 = next(r for r in results if r.standard_id == "ERC-4626")
        check(
            "fixture2: ERC-4626 still discovered when the implementing contract appears >8000 chars into the file",
            erc4626.applicable == DetectionConfidence.APPLICABLE and "LateVault" in erc4626.contracts,
            erc4626,
        )


# --- Fixture 3: inherited implementation (totalAssets in a parent) --------

def test_fixture3_inherited_implementation():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_interfaces(repo)
        source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

abstract contract BaseVault is IERC4626 {{
{_ERC20_METHOD_BODIES}
{_ERC4626_METHOD_BODIES}
}}

contract ChildVault is BaseVault {{
}}
"""
        (repo / "ChildVault.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "ChildVault.sol")
        results = discover_applicable_standards(repo, repo / "ChildVault.sol", slither, _registry())
        erc4626 = next(r for r in results if r.standard_id == "ERC-4626")
        check(
            "fixture3: ERC-4626 discovered via transitive inheritance (ChildVault -> BaseVault -> IERC4626)",
            erc4626.applicable == DetectionConfidence.APPLICABLE,
            erc4626,
        )
        check(
            "fixture3: the concrete child contract is identified, not just the abstract base",
            "ChildVault" in erc4626.contracts,
            erc4626.contracts,
        )


# --- Fixture 4: cross-function accounting (logic spread across functions) -

def test_fixture4_cross_function_accounting():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_interfaces(repo)
        source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

contract FeeVault is IERC4626 {{
{_ERC20_METHOD_BODIES}
    uint256 public operatorFeeAmount;
    function _getTotalRewards() internal pure returns (uint256) {{ return 0; }}
    function totalAssets() external view returns (uint256) {{ return _getTotalRewards() + operatorFeeAmount; }}
    function convertToShares(uint256 assets) external pure returns (uint256) {{ return assets; }}
    function convertToAssets(uint256 shares) external pure returns (uint256) {{ return shares; }}
    function asset() external pure returns (address) {{ return address(0); }}
    function maxDeposit(address) external pure returns (uint256) {{ return 0; }}
    function previewDeposit(uint256 assets) external pure returns (uint256) {{ return assets; }}
    function deposit(uint256 assets, address) external returns (uint256) {{ return assets; }}
    function maxMint(address) external pure returns (uint256) {{ return 0; }}
    function previewMint(uint256 shares) external pure returns (uint256) {{ return shares; }}
    function mint(uint256 shares, address) external returns (uint256) {{ return shares; }}
    function maxWithdraw(address) external pure returns (uint256) {{ return 0; }}
    function previewWithdraw(uint256 assets) external pure returns (uint256) {{ return assets; }}
    function withdraw(uint256 assets, address, address) external returns (uint256) {{ return assets; }}
    function maxRedeem(address) external pure returns (uint256) {{ return 0; }}
    function previewRedeem(uint256 shares) external pure returns (uint256) {{ return shares; }}
    function redeem(uint256 shares, address, address) external returns (uint256) {{ return shares; }}
}}
"""
        (repo / "FeeVault.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "FeeVault.sol")
        results = discover_applicable_standards(repo, repo / "FeeVault.sol", slither, _registry())
        erc4626 = next(r for r in results if r.standard_id == "ERC-4626")
        check(
            "fixture4: ERC-4626 discovered on a contract whose accounting spans multiple helper functions/state vars "
            "(detection is structural/inheritance-based, not dependent on any one function's body content)",
            erc4626.applicable == DetectionConfidence.APPLICABLE and "FeeVault" in erc4626.contracts,
            erc4626,
        )


# --- Fixture 5: interface referenced but NOT implemented -------------------

def test_fixture5_interface_only_not_implemented():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_interfaces(repo)
        source = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

// A router that merely CALLS an external ERC-4626 vault -- does not implement the interface itself.
contract VaultRouter {
    function routeDeposit(IERC4626 vault, uint256 assets, address receiver) external returns (uint256) {
        return vault.deposit(assets, receiver);
    }
}
"""
        (repo / "VaultRouter.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "VaultRouter.sol")
        results = discover_applicable_standards(repo, repo / "VaultRouter.sol", slither, _registry())
        erc4626 = next(r for r in results if r.standard_id == "ERC-4626")
        check(
            "fixture5: importing/referencing IERC4626 without inheriting it does NOT produce a false 'implements ERC-4626' verdict",
            erc4626.applicable != DetectionConfidence.APPLICABLE,
            erc4626,
        )
        check("fixture5: no contract is falsely classified as implementing ERC-4626", erc4626.contracts == (), erc4626.contracts)


# --- Fixture 6: partial/nonconforming implementation ------------------------

def test_fixture6_partial_nonconforming_still_detected():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_interfaces(repo)
        # Claims ERC-4626 conformance via inheritance but has an obviously
        # nonconforming totalAssets() body (returns a hardcoded, non-fee-
        # aware constant) -- conformance judgment is NOT this module's job,
        # only detection is. Detection must still fire.
        source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

contract BrokenVault is IERC4626 {{
{_ERC20_METHOD_BODIES}
    function totalAssets() external pure returns (uint256) {{ return 42; }}  // nonconforming: ignores real balances/fees entirely
    function asset() external pure returns (address) {{ return address(0); }}
    function convertToShares(uint256 assets) external pure returns (uint256) {{ return assets; }}
    function convertToAssets(uint256 shares) external pure returns (uint256) {{ return shares; }}
    function maxDeposit(address) external pure returns (uint256) {{ return 0; }}
    function previewDeposit(uint256 assets) external pure returns (uint256) {{ return assets; }}
    function deposit(uint256 assets, address) external returns (uint256) {{ return assets; }}
    function maxMint(address) external pure returns (uint256) {{ return 0; }}
    function previewMint(uint256 shares) external pure returns (uint256) {{ return shares; }}
    function mint(uint256 shares, address) external returns (uint256) {{ return shares; }}
    function maxWithdraw(address) external pure returns (uint256) {{ return 0; }}
    function previewWithdraw(uint256 assets) external pure returns (uint256) {{ return assets; }}
    function withdraw(uint256 assets, address, address) external returns (uint256) {{ return assets; }}
    function maxRedeem(address) external pure returns (uint256) {{ return 0; }}
    function previewRedeem(uint256 shares) external pure returns (uint256) {{ return shares; }}
    function redeem(uint256 shares, address, address) external returns (uint256) {{ return shares; }}
}}
"""
        (repo / "BrokenVault.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "BrokenVault.sol")
        results = discover_applicable_standards(repo, repo / "BrokenVault.sol", slither, _registry())
        erc4626 = next(r for r in results if r.standard_id == "ERC-4626")
        check(
            "fixture6: a claimed-but-nonconforming implementation is STILL detected as applicable "
            "(claimed conformance is itself relevant per the plan; conformance judgment is a downstream concern, not discovery's)",
            erc4626.applicable == DetectionConfidence.APPLICABLE and "BrokenVault" in erc4626.contracts,
            erc4626,
        )


# --- §13C negative cases (not fixtures 1-6, but explicitly required) -------

def test_negative_totalassets_alone_is_not_erc4626():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        source = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SimpleAccounting {
    uint256 private _total;
    function totalAssets() external view returns (uint256) { return _total; }
}
"""
        (repo / "SimpleAccounting.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "SimpleAccounting.sol")
        results = discover_applicable_standards(repo, repo / "SimpleAccounting.sol", slither, _registry())
        erc4626 = next(r for r in results if r.standard_id == "ERC-4626")
        check(
            "negative: a contract with only totalAssets() is NOT classified as ERC-4626 (one function name is not enough)",
            erc4626.applicable == DetectionConfidence.NOT_APPLICABLE,
            erc4626,
        )


def test_negative_deposit_alone_is_not_erc4626():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        source = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SimpleStaking {
    mapping(address => uint256) public staked;
    function deposit() external payable { staked[msg.sender] += msg.value; }
    function withdraw(uint256 amount) external { staked[msg.sender] -= amount; }
}
"""
        (repo / "SimpleStaking.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "SimpleStaking.sol")
        results = discover_applicable_standards(repo, repo / "SimpleStaking.sol", slither, _registry())
        erc4626 = next(r for r in results if r.standard_id == "ERC-4626")
        check(
            "negative: a plain staking contract with deposit()/withdraw() (wrong signatures, no other overlap) is NOT ERC-4626",
            erc4626.applicable == DetectionConfidence.NOT_APPLICABLE,
            erc4626,
        )


def test_negative_erc20_imported_as_dependency_not_implemented():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_interfaces(repo)
        source = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

// Uses IERC20 purely as a dependency to call an external token -- does not implement ERC-20 itself.
contract TokenSweeper {
    function sweep(IERC20 token, address to, uint256 amount) external {
        token.transfer(to, amount);
    }
}
"""
        (repo / "TokenSweeper.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "TokenSweeper.sol")
        results = discover_applicable_standards(repo, repo / "TokenSweeper.sol", slither, _registry())
        erc20 = next(r for r in results if r.standard_id == "ERC-20")
        check(
            "negative: importing IERC20 purely as an external dependency does not falsely classify TokenSweeper as an ERC-20 implementer",
            erc20.applicable != DetectionConfidence.APPLICABLE and erc20.contracts == (),
            erc20,
        )


def test_negative_bare_comment_mention_does_not_trigger():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        source = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Unlike some competitor vaults, this contract does NOT implement ERC-4626 -- see design doc.
contract PlainVault {
    uint256 public balance;
    function deposit() external payable { balance += msg.value; }
}
"""
        (repo / "PlainVault.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "PlainVault.sol")
        results = discover_applicable_standards(repo, repo / "PlainVault.sol", slither, _registry())
        erc4626 = next(r for r in results if r.standard_id == "ERC-4626")
        check(
            "negative: a bare in-code comment mentioning 'ERC-4626' (not README/docs, not an @inheritdoc tag) does not trigger detection",
            erc4626.applicable == DetectionConfidence.NOT_APPLICABLE,
            erc4626,
        )


# --- §15: multi-standard fixture (ERC-4626 vault is inherently also ERC-20)

def test_multi_standard_erc4626_and_erc20_both_discovered_independently():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _write_interfaces(repo)
        source = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./interfaces/IERC4626.sol";

contract DualStandardVault is IERC4626 {{
{_ERC20_METHOD_BODIES}
{_ERC4626_METHOD_BODIES}
}}
"""
        (repo / "DualStandardVault.sol").write_text(source, encoding="utf-8")
        slither = _compile(repo, "DualStandardVault.sol")
        results = discover_applicable_standards(repo, repo / "DualStandardVault.sol", slither, _registry())
        by_id = {r.standard_id: r for r in results}

        check("multi-standard: both ERC-4626 and ERC-20 are registered/checked", {"ERC-4626", "ERC-20"} <= set(by_id), by_id.keys())
        check("multi-standard: ERC-4626 discovered as APPLICABLE", by_id["ERC-4626"].applicable == DetectionConfidence.APPLICABLE, by_id["ERC-4626"])
        check(
            "multi-standard: ERC-20 ALSO independently discovered as APPLICABLE on the same contract "
            "(a vault is inherently a token too -- both fire, neither suppresses the other)",
            by_id["ERC-20"].applicable == DetectionConfidence.APPLICABLE,
            by_id["ERC-20"],
        )
        check(
            "multi-standard: provenance stays separate -- each result's evidence only references its own standard_id's signal_ids",
            all("erc4626" in e.lower() for e in by_id["ERC-4626"].evidence)
            and all("erc20" in e.lower() for e in by_id["ERC-20"].evidence),
            (by_id["ERC-4626"].evidence, by_id["ERC-20"].evidence),
        )
        check("multi-standard: both identify the same contract as implementer", "DualStandardVault" in by_id["ERC-4626"].contracts and "DualStandardVault" in by_id["ERC-20"].contracts)


def main() -> int:
    tests = [
        test_fixture1_correct_implementation,
        test_fixture2_late_file_implementation,
        test_fixture3_inherited_implementation,
        test_fixture4_cross_function_accounting,
        test_fixture5_interface_only_not_implemented,
        test_fixture6_partial_nonconforming_still_detected,
        test_negative_totalassets_alone_is_not_erc4626,
        test_negative_deposit_alone_is_not_erc4626,
        test_negative_erc20_imported_as_dependency_not_implemented,
        test_negative_bare_comment_mention_does_not_trigger,
        test_multi_standard_erc4626_and_erc20_both_discovered_independently,
    ]
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
