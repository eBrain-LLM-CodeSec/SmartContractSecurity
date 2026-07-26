// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IOracle {
    function getPrice() external view returns (uint256);
}

abstract contract Ownable {
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }
}

contract Vault is Ownable {
    IOracle public oracle;
    mapping(address => uint256) public shares;
    uint256 public totalShares;

    constructor(address _oracle) {
        oracle = IOracle(_oracle);
    }

    function setOracle(address _oracle) external onlyOwner {
        oracle = IOracle(_oracle);
    }

    // VULNERABILITY (fixture): external call to msg.sender before state update.
    function withdraw(uint256 amount) external {
        uint256 price = oracle.getPrice();
        uint256 payout = amount * price;
        (bool ok, ) = msg.sender.call{value: payout}("");
        require(ok, "transfer failed");
        shares[msg.sender] -= amount;
        totalShares -= amount;
    }

    function deposit() external payable {
        shares[msg.sender] += msg.value;
        totalShares += msg.value;
    }

    function _internalHelper() internal view returns (uint256) {
        return totalShares;
    }

    function callHelper() external view returns (uint256) {
        return _internalHelper();
    }
}
