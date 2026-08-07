// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Auth {
    address public authorizedSigner;
    address public owner;

    constructor(address _owner, address _initialSigner) {
        owner = _owner;
        authorizedSigner = _initialSigner;
    }

    function verify(bytes32 _digest, uint8 _v, bytes32 _r, bytes32 _s) public view returns (bool) {
        address signer = ecrecover(_digest, _v, _r, _s);
        return signer == authorizedSigner;
    }
}
