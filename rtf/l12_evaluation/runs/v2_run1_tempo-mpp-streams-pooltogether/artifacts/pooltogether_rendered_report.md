# RTF Static-Analysis Findings Report -- 2023-07-pooltogether (RTF v2, evidence-enrichment)

Auto-generated from RTF's L1-L8 predicate + LLM-judgment evidence.

## Enforce Least Privilege (req-3-access-control)

RTF conformance verdict: INSUFFICIENT_EVIDENCE

Evidence: 15 in the audited contract itself, 23 in imported libraries/interfaces (showing all of the former, first 15 of the latter):
- `Vault.mintYieldFee`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.deposit`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.depositWithPermit`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.mint`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.mintWithPermit`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.sponsor`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.sponsorWithPermit`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.withdraw`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.redeem`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.liquidate`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.setClaimer`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.setHooks`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.setLiquidationPair`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.setYieldFeePercentage`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Vault.setYieldFeeRecipient`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC20.transfer`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC20.approve`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC20.transferFrom`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC20.increaseAllowance`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC20.decreaseAllowance`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC20Permit.permit`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC4626.deposit`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC4626.mint`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC4626.withdraw`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `ERC4626.redeem`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Ownable.renounceOwnership`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Ownable.transferOwnership`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `Ownable.claimOwnership`:
    state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `LiquidationPair.swapExactAmountIn`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
- `LiquidationPair.swapExactAmountOut`:
    state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here

## Process All Inputs (req-3-all-valid-inputs)

RTF conformance verdict: INSUFFICIENT_EVIDENCE

Evidence: 43 in the audited contract itself, 696 in imported libraries/interfaces (showing all of the former, first 15 of the latter):
- `Vault.balanceOf`:
    none of this function's parameters (['_account']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.maxDeposit`:
    none of this function's parameters (['']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.maxMint`:
    none of this function's parameters (['']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.mintYieldFee`:
    none of this function's parameters (['_recipient', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.deposit`:
    none of this function's parameters (['_assets', '_receiver']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.depositWithPermit`:
    none of this function's parameters (['_assets', '_deadline', '_r', '_receiver', '_s', '_v']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.mint`:
    none of this function's parameters (['_receiver', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.mintWithPermit`:
    none of this function's parameters (['_deadline', '_r', '_receiver', '_s', '_shares', '_v']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.sponsor`:
    none of this function's parameters (['_assets', '_receiver']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.sponsorWithPermit`:
    none of this function's parameters (['_assets', '_deadline', '_r', '_receiver', '_s', '_v']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.withdraw`:
    none of this function's parameters (['_assets', '_owner', '_receiver']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.redeem`:
    none of this function's parameters (['_owner', '_receiver', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.liquidatableBalanceOf`:
    none of this function's parameters (['_token']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.liquidate`:
    none of this function's parameters (['_account', '_amountIn', '_amountOut', '_tokenIn', '_tokenOut']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.targetOf`:
    none of this function's parameters (['_token']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.claimPrizes`:
    none of this function's parameters (['_feePerClaim', '_feeRecipient', '_prizeIndices', '_tier', '_winners']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.setClaimer`:
    none of this function's parameters (['claimer_']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.setHooks`:
    none of this function's parameters (['hooks']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.setLiquidationPair`:
    none of this function's parameters (['liquidationPair_']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.setYieldFeePercentage`:
    none of this function's parameters (['yieldFeePercentage_']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.setYieldFeeRecipient`:
    none of this function's parameters (['yieldFeeRecipient_']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault.getHooks`:
    none of this function's parameters (['_account']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._liquidatableBalanceOf`:
    none of this function's parameters (['_token']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._availableYieldFeeBalance`:
    none of this function's parameters (['_availableYield']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._increaseYieldFeeBalance`:
    none of this function's parameters (['_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._convertToShares`:
    none of this function's parameters (['_assets', '_rounding']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._convertToAssets`:
    none of this function's parameters (['_rounding', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._convertToAssets`:
    none of this function's parameters (['_exchangeRate', '_rounding', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._deposit`:
    none of this function's parameters (['_assets', '_caller', '_receiver', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._beforeMint`:
    none of this function's parameters (['_receiver', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._sponsor`:
    none of this function's parameters (['_assets', '_receiver']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._withdraw`:
    none of this function's parameters (['_assets', '_caller', '_owner', '_receiver', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._claimPrize`:
    none of this function's parameters (['_fee', '_feeRecipient', '_prizeIndex', '_tier', '_winner']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._permit`:
    none of this function's parameters (['_asset', '_assets', '_deadline', '_owner', '_r', '_s', '_spender', '_v']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._mint`:
    none of this function's parameters (['_receiver', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._burn`:
    none of this function's parameters (['_owner', '_shares']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._transfer`:
    none of this function's parameters (['_from', '_shares', '_to']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._setClaimer`:
    none of this function's parameters (['claimer_']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._setYieldFeePercentage`:
    none of this function's parameters (['yieldFeePercentage_']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._setYieldFeeRecipient`:
    none of this function's parameters (['yieldFeeRecipient_']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `Vault._mint`:
    operation: narrowing type conversion uint256 -> uint96
    input: {'name': '_shares', 'type': 'uint256'}
    validation_found: none
    missing_safety_condition: _shares <= type(uint96).max
    risk: values of _shares above uint96's maximum representable value (79228162514264337593543950335) are silently truncated by this cast rather than rejected
    affected_functions: ['Vault._mint']
- `Vault._burn`:
    operation: narrowing type conversion uint256 -> uint96
    input: {'name': '_shares', 'type': 'uint256'}
    validation_found: none
    missing_safety_condition: _shares <= type(uint96).max
    risk: values of _shares above uint96's maximum representable value (79228162514264337593543950335) are silently truncated by this cast rather than rejected
    affected_functions: ['Vault._burn']
- `Vault._transfer`:
    operation: narrowing type conversion uint256 -> uint96
    input: {'name': '_shares', 'type': 'uint256'}
    validation_found: none
    missing_safety_condition: _shares <= type(uint96).max
    risk: values of _shares above uint96's maximum representable value (79228162514264337593543950335) are silently truncated by this cast rather than rejected
    affected_functions: ['Vault._transfer']
- `console2._castLogPayloadViewToPure`:
    none of this function's parameters (['fnIn']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2._sendLogPayload`:
    none of this function's parameters (['payload']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2._sendLogPayloadView`:
    none of this function's parameters (['payload']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logInt`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logUint`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logString`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logBool`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logAddress`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logBytes`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logBytes1`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logBytes2`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logBytes3`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logBytes4`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logBytes5`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
- `console2.logBytes6`:
    none of this function's parameters (['p0']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
