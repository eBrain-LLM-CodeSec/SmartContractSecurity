// Synthetic requirement-derived fixture: malformed inputs must be handled.
pragma solidity ^0.8.20;

contract DomainMath {
    function reciprocal(int256 value) external pure returns (int256) {
        require(value > 0, "outside reciprocal domain");
        return int256(1e18) / value;
    }
}
