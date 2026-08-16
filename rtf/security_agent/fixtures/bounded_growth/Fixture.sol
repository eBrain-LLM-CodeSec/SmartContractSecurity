// Synthetic requirement-derived fixture: persistent growth and iteration cost.
pragma solidity ^0.8.20;

contract MemberRegistry {
    uint256 public constant MAX_MEMBERS = 16;
    address[] public members;
    function addMember(address member) external {
        require(members.length < MAX_MEMBERS, "bounded registry");
        members.push(member);
    }
    function removeLast() external {
        require(members.length != 0, "empty");
        members.pop();
    }
    function contains(address candidate) external view returns (bool) {
        for (uint256 i; i < members.length; ++i) {
            if (members[i] == candidate) return true;
        }
        return false;
    }
}
