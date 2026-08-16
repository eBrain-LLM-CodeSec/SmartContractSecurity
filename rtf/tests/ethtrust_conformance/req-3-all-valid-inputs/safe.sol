// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-3-all-valid-inputs [Q]
// SAFE variant: explicitly rejects domain-invalid input instead of
// silently producing a meaningless result for it.

contract Ln {
    function ln(int256 x) public pure returns (int256) {
        require(x > 0, "Ln: input must be positive");
        int256 result = 0;
        int256 t = x;
        while (t > 1) {
            t = t / 2;
            result += 1;
        }
        return result;
    }
}
