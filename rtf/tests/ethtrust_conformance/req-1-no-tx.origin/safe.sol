// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-1-no-tx.origin [S]
// SAFE variant: uses msg.sender instead of tx.origin -- no tx.origin
// instruction anywhere in the contract.

contract Wallet {
    address public owner;

    constructor() { owner = msg.sender; }

    function transfer(address payable to, uint256 amount) public {
        require(msg.sender == owner, "not owner");
        to.transfer(amount);
    }
}
