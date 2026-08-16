// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-3-enough-gas [Q]
// Normative text (verbatim): "Sufficient Gas MUST be available to work
// with data structures in the Tested Code that grow over time."
// Explanatory text (verbatim): "Iterating over a structure whose size
// is not clear in advance... can result in significant increases in
// gas usage."
// VIOLATION: holderList only ever grows (addHolder pushes, nothing ever
// removes an entry) and is fully iterated by distributeRewards() -- as
// the holder count grows without bound, distributeRewards()'s gas cost
// grows with it, eventually exceeding the block gas limit.

contract Holders {
    address[] public holderList;
    mapping(address => uint256) public balances;

    function addHolder(address who, uint256 amount) public {
        if (balances[who] == 0) {
            holderList.push(who);
        }
        balances[who] += amount;
    }

    function distributeRewards() public {
        for (uint256 i = 0; i < holderList.length; i++) {
            balances[holderList[i]] += 1;
        }
    }
}
