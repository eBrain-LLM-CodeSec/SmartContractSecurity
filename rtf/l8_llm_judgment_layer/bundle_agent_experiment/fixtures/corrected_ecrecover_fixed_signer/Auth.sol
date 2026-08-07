// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Auth {
    address public immutable authorizedSigner;

    constructor(address _initialSigner) {
        require(_initialSigner != address(0), "signer cannot be zero");
        authorizedSigner = _initialSigner;
    }

    function verify(bytes32 _digest, uint8 _v, bytes32 _r, bytes32 _s) public view returns (bool) {
        address signer = ecrecover(_digest, _v, _r, _s);
        return signer == authorizedSigner;
    }
}
