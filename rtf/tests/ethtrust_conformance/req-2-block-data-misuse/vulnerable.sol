// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-2-block-data-misuse [M]
// Normative text (verbatim from the EthTrust v3 corpus):
//   "Tested Code MUST use block.number, block.timestamp, or any other
//   variable data associated with a block or transaction consistently,
//   in accordance with the description(s) provided ... [e.g.] using
//   block.number / 14 as a proxy for elapsed seconds."
// This fixture is a VIOLATION: updateMarket() reads block.number and
// passes it, unchanged, to an external contract's function whose own
// documented parameter expects an ELAPSED-SECONDS duration -- the
// caller's own local usage is self-consistent, but the value crosses a
// function boundary into a callee with a DIFFERENT interpretation of
// what it represents. Independently derived from this requirement's own
// worked example, not from any external benchmark's ground truth.

interface IGauge {
    // Expects an elapsed-seconds duration, NOT a raw block count.
    function writeWeight(address gauge, uint256 elapsedSeconds) external;
}

contract TimedRewardTracker {
    IGauge public gauge;
    mapping(address => uint256) public lastRewardBlock;

    constructor(address _gauge) { gauge = IGauge(_gauge); }

    function updateMarket(address market) public {
        gauge.writeWeight(market, block.number);
        lastRewardBlock[market] = block.number;
    }
}
