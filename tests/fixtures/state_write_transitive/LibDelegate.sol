// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Delegator {
    mapping(address => uint256) public balances;
    uint256 public directCounter;

    // VULNERABILITY (fixture, Gap A): `deposit` never directly writes
    // `balances` -- the actual `balances[who] = value` assignment happens
    // entirely inside `_setBalance`'s own body, one internal call away. A
    // predicate scoped to only the direct STATE_WRITE edge would never see
    // this as a state-writing function -- exactly the "internal-call
    // delegation" shape the real targeted findings (2025-04-virtuals/H-01,
    // 2024-04-noya/H-08, 2024-07-benddao/H-07) share.
    function deposit(address who, uint256 value) external {
        _setBalance(who, value);
    }

    function _setBalance(address who, uint256 value) internal {
        balances[who] = value;
    }

    // Contrast case: directCounter IS written directly by this function's
    // own body -- STATE_WRITE, not STATE_WRITE_TRANSITIVE.
    function bumpDirect() external {
        directCounter += 1;
    }

    function pureRead(address who) external view returns (uint256) {
        return balances[who];
    }
}
