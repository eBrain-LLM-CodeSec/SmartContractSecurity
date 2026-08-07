// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract RewardStream {
    address public admin;
    uint256 public lastUpdate;
    uint256 public accRewardPerShare;
    uint256 public rewardRatePerSecond;

    constructor(address _admin) {
        admin = _admin;
        lastUpdate = block.timestamp;
    }

    function setRewardRate(uint256 _ratePerSecond) external {
        require(msg.sender == admin, "not admin");
        rewardRatePerSecond = _ratePerSecond;
    }

    function updateReward() external {
        uint256 elapsed = block.timestamp - lastUpdate;
        accRewardPerShare += elapsed * rewardRatePerSecond;
        lastUpdate = block.timestamp;
    }
}
