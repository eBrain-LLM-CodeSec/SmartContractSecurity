// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Ledger {
    mapping(address => uint96) public balances;

    function record(address _account, uint256 _amount) external {
        require(_amount <= type(uint96).max, "too large");
        balances[_account] = uint96(_amount);
    }
}
