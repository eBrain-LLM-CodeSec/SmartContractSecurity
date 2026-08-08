// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./Auth.sol";

contract AuthAdmin is Auth {
    constructor(address _owner, address _initialSigner) Auth(_owner, _initialSigner) {}

    function setAuthorizedSigner(address _newSigner) external {
        require(msg.sender == owner, "not owner");
        authorizedSigner = _newSigner;
    }
}
