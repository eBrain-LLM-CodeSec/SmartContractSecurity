# RTF Static-Analysis Findings Report -- 2026-01-tempo-mpp-streams

Auto-generated from RTF's L1-L8 predicate + LLM-judgment evidence.

## Signature Verification (EthTrust req-2-signature-verification)

RTF conformance verdict: INSUFFICIENT_EVIDENCE

Evidence:
- `TempoStreamChannel._recoverSigner`: ecrecover() used directly

## Process All Inputs (EthTrust req-3-all-valid-inputs)

RTF conformance verdict: INSUFFICIENT_EVIDENCE

Evidence:
- `TempoStreamChannel._recoverSigner`: none of this function's parameters (['digest', 'signature']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.openChannel`: none of this function's parameters (['authorizedSigner', 'deadline', 'deposit', 'payee', 'token']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.addDeposit`: none of this function's parameters (['amount', 'channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.settle`: none of this function's parameters (['signature', 'voucher']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.initiateClose`: none of this function's parameters (['channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.finalize`: none of this function's parameters (['channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.close`: none of this function's parameters (['payerSignature', 'signature', 'voucher']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.getChannel`: none of this function's parameters (['channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `TempoStreamChannel.getAvailableBalance`: none of this function's parameters (['channelId']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.transferAndCall`: none of this function's parameters (['to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.transferAndCall`: none of this function's parameters (['data', 'to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.transferFromAndCall`: none of this function's parameters (['from', 'to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.transferFromAndCall`: none of this function's parameters (['data', 'from', 'to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.approveAndCall`: none of this function's parameters (['spender', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC1363.approveAndCall`: none of this function's parameters (['data', 'spender', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.balanceOf`: none of this function's parameters (['account']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.transfer`: none of this function's parameters (['to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.allowance`: none of this function's parameters (['owner', 'spender']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.approve`: none of this function's parameters (['spender', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `IERC20.transferFrom`: none of this function's parameters (['from', 'to', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
