// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-2-block-data-misuse [M]
// SAFE variant: block.timestamp is still read (so the same structural
// predicate correctly stays APPLICABLE -- this is a genuine judgment
// case, not a routing/coverage case), but the value handed to the
// callee is a correctly-computed elapsed-seconds duration, matching the
// callee's own documented expectation.

interface IGauge {
    /// @notice expects an elapsed-seconds duration since the last update
    function writeWeight(address gauge, uint256 elapsedSeconds) external;
}

contract TimedRewardTracker {
    IGauge public gauge;
    mapping(address => uint256) public lastRewardTimestamp;

    constructor(address _gauge) { gauge = IGauge(_gauge); }

    function updateMarket(address market) public {
        uint256 elapsed = block.timestamp - lastRewardTimestamp[market];
        gauge.writeWeight(market, elapsed);
        lastRewardTimestamp[market] = block.timestamp;
    }
}
