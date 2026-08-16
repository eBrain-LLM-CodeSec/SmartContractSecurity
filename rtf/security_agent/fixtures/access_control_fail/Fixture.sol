// Synthetic requirement-derived fixture: privileged state needs authorization.
pragma solidity ^0.8.20;

contract OracleConfiguration {
    address public oracle;
    function setOracle(address nextOracle) external {
        oracle = nextOracle;
    }
}
