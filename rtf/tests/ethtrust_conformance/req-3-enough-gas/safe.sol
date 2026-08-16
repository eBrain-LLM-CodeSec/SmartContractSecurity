// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-3-enough-gas [Q]
// SAFE variant: same growth-capable structure, but a real pruning path
// (removeHolder) exists, so the structure's size is bounded by active
// participation rather than growing without limit.

contract Holders {
    address[] public holderList;
    mapping(address => uint256) public balances;

    function addHolder(address who, uint256 amount) public {
        if (balances[who] == 0) {
            holderList.push(who);
        }
        balances[who] += amount;
    }

    function removeHolder(uint256 idx) public {
        holderList[idx] = holderList[holderList.length - 1];
        holderList.pop();
    }

    function distributeRewards() public {
        for (uint256 i = 0; i < holderList.length; i++) {
            balances[holderList[i]] += 1;
        }
    }
}
