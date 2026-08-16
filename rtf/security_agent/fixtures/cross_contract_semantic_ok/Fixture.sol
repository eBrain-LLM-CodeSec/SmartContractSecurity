// Synthetic requirement-derived fixture: cross-contract semantic consistency.
pragma solidity ^0.8.20;

contract EpochConsumer {
    uint256 public constant EPOCH = 100;
    function weightAt(uint256 epochStart) external pure returns (uint256) {
        return epochStart / EPOCH;
    }
}

contract AlignedCaller {
    EpochConsumer public consumer;
    constructor(EpochConsumer target) { consumer = target; }
    function currentWeight() external view returns (uint256) {
        uint256 epochStart = (block.number / 100) * 100;
        return consumer.weightAt(epochStart);
    }
}
