// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Gap B, Revision 3 fix: a PURE LIBRARY function (no state variables at
// all -- not just "no state vars written", a library has none to have)
// whose only accounting vocabulary ("mantissa", "exponent") lives in its
// own PARAMETER names, doing the actual multiplication/division entirely
// inside an inline `assembly` block -- mirrors forte/H-05's
// Float128.toPackedFloat exactly. Both the parameter-name scope widening
// (accounting_identifier_signal) and the assembly-awareness branch
// (precision_sensitive_arithmetic_exists) are required together; neither
// alone would catch this.
library Float128 {
    function toPackedFloat(uint256 mantissa, uint256 exponent) internal pure returns (uint256 packed) {
        assembly {
            packed := add(mul(mantissa, exp(2, exponent)), div(mantissa, exp(2, exponent)))
        }
    }
}

contract Accounting {
    uint256 public totalShares;
    uint256 public reserve;
    address public oracle;

    // P5_ACCOUNTING_ARITHMETIC positive: accounting-vocabulary identifiers
    // (function name "convert" + "shares"/"amount") AND direct arithmetic
    // (multiplication) in the same function body.
    function convertToShares(uint256 amount) public view returns (uint256) {
        return amount * totalShares / (reserve + 1);
    }

    // P5_ACCOUNTING_ARITHMETIC positive via TRANSITIVE arithmetic: the seed
    // itself has no Binary op, but its internal helper does -- mirrors the
    // thorwallet/H-01 "quoteTitn" shape exactly (arithmetic lives one
    // internal call away).
    function quoteShares(uint256 tgtAmount) public view returns (uint256) {
        return _computeShareQuote(tgtAmount);
    }

    function _computeShareQuote(uint256 tgtAmount) internal view returns (uint256) {
        return (tgtAmount * totalShares) / (reserve + 1);
    }

    // P5_EXTERNAL_CALL_ACCOUNTING_WRITE positive: external call + write to
    // an accounting-vocabulary state var ("reserve"), mirroring benddao's
    // H-01 _stake shape (direct external call + direct write, no
    // transitivity needed).
    function syncReserveFromOracle() external {
        (bool ok, bytes memory data) = oracle.call(abi.encodeWithSignature("price()"));
        require(ok, "oracle call failed");
        reserve = abi.decode(data, (uint256));
    }

    // P5_ACCOUNTING_ENTRYPOINT positive: action-verb function name
    // ("withdraw"), a numeric parameter, public/external visibility, and a
    // state write -- no arithmetic or external call required for this gate.
    function withdrawShares(uint256 amount) external {
        totalShares -= amount;
    }

    // Negative control: accounting-vocabulary identifier present ("total")
    // but NO arithmetic, NO external call, and not an action-verb entry
    // point -- none of the three new P5 gates should fire.
    function reportTotal() external view returns (uint256) {
        return totalShares;
    }

    // Negative control: has arithmetic (multiplication) but NO accounting-
    // vocabulary identifiers anywhere (name/state-vars/params/locals/
    // returns) -- accounting_identifier_signal alone must block firing.
    // (Careful: no substring of "multiplyInputs"/"x"/"y" may itself be a
    // whole vocabulary token.)
    function multiplyInputs(uint256 x, uint256 y) public pure returns (uint256) {
        return x * y;
    }

    // Tokenization guard: "captureEvent" must NOT match vocabulary token
    // "cap" via substring matching -- accounting_identifier_signal must be
    // MISSING here (no whole-token match: "capture" != "cap", "event" not
    // in vocabulary).
    function captureEvent(uint256 eventId) external pure returns (uint256) {
        return eventId;
    }

}
