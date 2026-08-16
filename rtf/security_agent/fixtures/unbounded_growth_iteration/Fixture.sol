// Synthetic requirement-derived fixture: persistent growth and iteration cost.
pragma solidity ^0.8.20;

contract MemberRegistry {
    address[] public members;
    function addMember(address member) external { members.push(member); }
    function contains(address candidate) external view returns (bool) {
        for (uint256 i; i < members.length; ++i) {
            if (members[i] == candidate) return true;
        }
        return false;
    }
}
