// Synthetic requirement-derived fixture: malformed inputs must be handled.
pragma solidity ^0.8.20;

contract DomainMath {
    function reciprocal(int256 value) external pure returns (int256) {
        // Negative values are outside the intended domain but silently accepted.
        if (value == 0) return 0;
        return int256(1e18) / value;
    }
}
