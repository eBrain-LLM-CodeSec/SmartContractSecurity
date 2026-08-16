// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-1-no-tx.origin [S]
// Normative text (verbatim): "Tested code MUST NOT contain a tx.origin
// instruction unless it meets the Overriding Requirement [Q] Verify
// tx.origin Usage."
// VIOLATION: transfer() uses tx.origin for an authorization check --
// phishable via a malicious intermediate contract the owner interacts
// with, with no documented override justifying the usage.

contract Wallet {
    address public owner;

    constructor() { owner = msg.sender; }

    function transfer(address payable to, uint256 amount) public {
        require(tx.origin == owner, "not owner");
        to.transfer(amount);
    }
}
