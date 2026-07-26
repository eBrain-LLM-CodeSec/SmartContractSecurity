pragma solidity ^0.4.24;

contract OldStyle {
    uint256 public value;

    function OldStyle() public {
        value = 0;
    }

    function setValue(uint256 v) public {
        value = v;
    }
}
