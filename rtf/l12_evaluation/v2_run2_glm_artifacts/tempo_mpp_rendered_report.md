# RTF Static-Analysis Findings Report -- 2026-01-tempo-mpp-streams (RTF v2, GLM 5.2 judgment)

Auto-generated from RTF's L1-L8 predicate + LLM-judgment evidence.

## Signature Verification (req-2-signature-verification)

RTF conformance verdict: INCONCLUSIVE

Evidence: 5 in the audited contract itself, 0 in imported libraries/interfaces (showing all of the former, first 15 of the latter):
- `TempoStreamChannel._recoverSigner`:
    ecrecover() used directly
- `TempoStreamChannel._recoverSigner`:
    operation: ecrecover(...)
    validation_found: UNKNOWN -- result not assigned to a traceable named variable
    risk: cannot be determined by this predicate; requires manual/semantic review
- `TempoStreamChannel.settle`:
    operation: ecrecover(...) (via local wrapper function '_recoverSigner')
    input: {'name': 'signer', 'type': 'address'}
    validation_found: none
    missing_safety_condition: signer != address(0)
    risk: an invalid signature recovers to address(0) and, if address(0) is ever treated as authorized (e.g. an unset/default signer field), an invalid signature would be accepted as authentic
    affected_functions: ['TempoStreamChannel.settle']
- `TempoStreamChannel.close`:
    operation: ecrecover(...) (via local wrapper function '_recoverSigner')
    input: {'name': 'signer', 'type': 'address'}
    validation_found: none
    missing_safety_condition: signer != address(0)
    risk: an invalid signature recovers to address(0) and, if address(0) is ever treated as authorized (e.g. an unset/default signer field), an invalid signature would be accepted as authentic
    affected_functions: ['TempoStreamChannel.close']
- `TempoStreamChannel.close`:
    operation: ecrecover(...) (via local wrapper function '_recoverSigner')
    input: {'name': 'payerSigner', 'type': 'address'}
    validation_found: none
    missing_safety_condition: payerSigner != address(0)
    risk: an invalid signature recovers to address(0) and, if address(0) is ever treated as authorized (e.g. an unset/default signer field), an invalid signature would be accepted as authentic
    affected_functions: ['TempoStreamChannel.close']

## Process All Inputs (req-3-all-valid-inputs)

RTF conformance verdict: INCONCLUSIVE

Evidence: 9 in the audited contract itself, 238 in imported libraries/interfaces (showing all of the former, first 15 of the latter):
- `TempoStreamChannel._recoverSigner`:
    none of this function's parameters (['digest', 'signature']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.openChannel`:
    none of this function's parameters (['authorizedSigner', 'deadline', 'deposit', 'payee', 'token']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.addDeposit`:
    none of this function's parameters (['amount', 'channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.settle`:
    none of this function's parameters (['signature', 'voucher']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.initiateClose`:
    none of this function's parameters (['channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.finalize`:
    none of this function's parameters (['channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.close`:
    none of this function's parameters (['payerSignature', 'signature', 'voucher']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.getChannel`:
    none of this function's parameters (['channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.getAvailableBalance`:
    none of this function's parameters (['channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.transferAndCall`:
    none of this function's parameters (['to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.transferAndCall`:
    none of this function's parameters (['data', 'to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.transferFromAndCall`:
    none of this function's parameters (['from', 'to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.transferFromAndCall`:
    none of this function's parameters (['data', 'from', 'to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.approveAndCall`:
    none of this function's parameters (['spender', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.approveAndCall`:
    none of this function's parameters (['data', 'spender', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.balanceOf`:
    none of this function's parameters (['account']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.transfer`:
    none of this function's parameters (['to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.allowance`:
    none of this function's parameters (['owner', 'spender']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.approve`:
    none of this function's parameters (['spender', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.transferFrom`:
    none of this function's parameters (['from', 'to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `SafeERC20.safeTransfer`:
    none of this function's parameters (['to', 'token', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `SafeERC20.safeTransferFrom`:
    none of this function's parameters (['from', 'to', 'token', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `SafeERC20.trySafeTransfer`:
    none of this function's parameters (['to', 'token', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `SafeERC20.trySafeTransferFrom`:
    none of this function's parameters (['from', 'to', 'token', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
