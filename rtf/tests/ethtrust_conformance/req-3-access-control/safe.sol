// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-3-access-control [Q]
// SAFE variant: the same privileged operation is gated by an
// appropriate access-control mechanism (onlyOwner).

contract Treasury {
    address public owner;
    uint256 public totalFunds;

    constructor() { owner = msg.sender; }

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    function withdraw(uint256 amount) public onlyOwner {
        totalFunds -= amount;
        payable(msg.sender).transfer(amount);
    }
}
