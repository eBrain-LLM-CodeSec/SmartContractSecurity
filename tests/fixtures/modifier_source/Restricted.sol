// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Gap C, Workstream 1 regression fixture: the modifier's NAME itself
// ("restricted") does not match the auth-pattern regex (unlike Vault.sol's
// fixture, where "onlyOwner" appears in the function's own signature line
// and short-circuits the search at step 1 before ever reaching the
// modifier's own source text). The auth check text (`require(msg.sender ==
// owner...)`) lives ONLY inside the modifier's body -- so this fixture can
// only resolve to PRESENT if authorization_control_state's step-2 modifier-
// body scan can actually read the modifier's source, which requires
// graph.py's MODIFIER nodes to carry a `file` attribute (the exact bug
// gate_evaluation.jsonl already recorded: MODIFIER nodes were built without
// `file` at either construction site, unlike FUNCTION nodes).
contract Restricted {
    address public owner;
    uint256 public value;

    modifier restricted() {
        require(msg.sender == owner, "not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function setValue(uint256 newValue) external restricted {
        value = newValue;
    }

    function setValueUnprotected(uint256 newValue) external {
        value = newValue;
    }

    // No state write (view) -- used to test that `state_write_exists`
    // being definitively MISSING blocks `decision_blocking_unresolved`
    // even when the modifier scan is separately forced UNRESOLVED (by
    // test code stripping the modifier node's `file` attribute).
    function viewOnly() external view restricted returns (uint256) {
        return value;
    }
}
