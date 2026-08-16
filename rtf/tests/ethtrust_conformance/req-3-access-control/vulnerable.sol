// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-3-access-control [Q]
// ("Enforce Least Privilege")
// Normative text (verbatim): "Tested code that enables privileged
// access MUST implement appropriate access control mechanisms that
// provide the least privilege necessary for those interactions."
// VIOLATION: withdraw() mutates privileged state (totalFunds) and moves
// funds, but has no access-control mechanism at all -- any caller can
// invoke it.

contract Treasury {
    address public owner;
    uint256 public totalFunds;

    constructor() { owner = msg.sender; }

    function withdraw(uint256 amount) public {
        totalFunds -= amount;
        payable(msg.sender).transfer(amount);
    }
}
