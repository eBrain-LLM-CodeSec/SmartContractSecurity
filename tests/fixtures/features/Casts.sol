// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Casts {
    function safeCast(uint8 x) public pure returns (uint256) {
        return uint256(x);
    }

    // VULNERABILITY (fixture): narrowing downcast, truncates silently.
    function unsafeCast(uint256 x) public pure returns (uint96) {
        return uint96(x);
    }

    function branchy(uint256 x) public pure returns (uint256) {
        if (x > 10) {
            if (x > 20) {
                return 1;
            } else {
                return 2;
            }
        } else {
            return 3;
        }
    }

    // arithmetic_op_count: multiplication + division present -- count == 2.
    function scaleAndDivide(uint256 x, uint256 y, uint256 z) public pure returns (uint256) {
        return (x * y) / z;
    }

    // arithmetic_op_count: MODULO only -- must NOT count (indexing/cycling/
    // interval use is common and not precision-relevant).
    function modOnly(uint256 x, uint256 y) public pure returns (uint256) {
        return x % y;
    }

    // arithmetic_op_count: POWER (10 ** decimals-style fixed-point scaling) -- count == 1.
    function powerOnly(uint256 base, uint256 exp) public pure returns (uint256) {
        return base ** exp;
    }
}
