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
}
