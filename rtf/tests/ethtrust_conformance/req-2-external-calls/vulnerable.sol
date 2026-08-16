// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-2-external-calls [M]
// ("Protect external calls")
// VIOLATION: withdraw() performs its external call BEFORE updating the
// caller's own balance -- a checks-effects-interactions ordering
// violation that leaves a reentrancy window open.

contract Vault {
    mapping(address => uint256) public balances;

    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "insufficient");
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "transfer failed");
        balances[msg.sender] -= amount;
    }
}
