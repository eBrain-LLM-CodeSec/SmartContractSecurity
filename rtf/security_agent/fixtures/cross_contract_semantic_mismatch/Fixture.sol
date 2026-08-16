// Synthetic requirement-derived fixture: cross-contract semantic consistency.
pragma solidity ^0.8.20;

contract EpochConsumer {
    uint256 public constant EPOCH = 100;
    function weightAt(uint256 epochStart) external pure returns (uint256) {
        return epochStart / EPOCH;
    }
}

contract MismatchedCaller {
    EpochConsumer public consumer;
    constructor(EpochConsumer target) { consumer = target; }
    function currentWeight() external view returns (uint256) {
        // Consumer expects an epoch-aligned value, but caller passes a raw block.
        return consumer.weightAt(block.number);
    }
}
