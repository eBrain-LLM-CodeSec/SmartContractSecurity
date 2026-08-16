// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// RTF EthTrust conformance fixture -- req-3-all-valid-inputs [Q]
// Normative text (verbatim): "Tested Code MUST validate inputs, and
// function correctly whether the input is as designed or malformed."
// VIOLATION: ln() never checks that its input is inside the
// mathematically-defined domain (a logarithm's argument MUST be
// positive) -- a negative or zero input silently produces a meaningless
// result instead of being rejected.

contract Ln {
    function ln(int256 x) public pure returns (int256) {
        int256 result = 0;
        int256 t = x;
        while (t > 1) {
            t = t / 2;
            result += 1;
        }
        return result;
    }
}
