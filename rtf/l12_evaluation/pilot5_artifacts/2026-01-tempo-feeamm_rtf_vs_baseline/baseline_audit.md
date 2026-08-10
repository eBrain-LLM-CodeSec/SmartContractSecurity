# Security Audit Report: 2026-01-tempo-feeamm

Findings below were produced by a single, autonomous, non-RTF Codex session using the production evmbench single-shot audit prompt (backend/worker_runner/detect.md) -- full repository access, no requirement routing, no structured tool scaffolding.

## 1. Burn is reentrancy-vulnerable allowing LPs to withdraw multiple times (high)

**Summary:** The burn routine performs external ERC20 transfers before updating liquidity balances or reserves and lacks any reentrancy guard, letting a malicious token reenter burn and redeem the same liquidity repeatedly to drain pool assets.

**Location:** contracts/FeeAMM.sol:226-269

During burn, the contract transfers `userToken` and `validatorToken` to the recipient at lines 252-253 before decreasing `liquidityBalances`, `totalSupply`, and pool reserves at lines 255-258. With no reentrancy guard, a malicious ERC20 can reenter `burn` in its `transfer` hook and redeem again while balances and reserves are still untouched.

**Impact:** A liquidity provider using a reentrant token can repeatedly invoke burn in a single transaction, withdrawing more tokens than their share and emptying the pool’s reserves of both userToken and validatorToken, causing direct loss of funds for other LPs and traders.

**Proof of concept:** Deploy a malicious ERC20 as `userToken` (or `validatorToken`) that calls `FeeAMM.burn` again in its `transfer` hook. Hold some LP tokens, call `burn`, the hook reenters `burn` before balances drop, repeating withdrawals until reserves are exhausted.

**Remediation:** Add a reentrancy guard (e.g., OpenZeppelin ReentrancyGuard) and update state before external token transfers in burn.

## 2. ERC20 transfer return values are ignored enabling free withdrawals and mints (high)

**Summary:** All ERC20 transfer/transferFrom calls ignore their boolean return value, so tokens that return false instead of reverting are treated as successful, allowing attackers to receive validator tokens or mint liquidity without sending funds.

**Location:** contracts/FeeAMM.sol:95-170

executeFeeSwap uses `IERC20(userToken).transferFrom` (line 113) and immediately decrements `reserveValidatorToken` and transfers validator tokens to the caller (line 118) without checking the return value; a token returning false results in validator tokens paid out with no input received.

**Location:** contracts/FeeAMM.sol:173-224

mint calls `IERC20(validatorToken).transferFrom` at line 205 without verifying success, yet mints liquidity and increments reserves at lines 211-214, allowing liquidity to be minted for free if transferFrom returns false.

**Location:** contracts/FeeAMM.sol:129-170

rebalanceSwap similarly ignores return values for validatorToken transferFrom (line 157) and userToken transfer (line 162), letting attackers drain reserves with a non-reverting false-return token.

**Impact:** Attackers can deploy or select ERC20 tokens that return false on transfer/transferFrom without reverting, then call executeFeeSwap to receive validatorToken payouts without providing userToken, or mint LP shares without depositing validatorToken, directly draining pool reserves and stealing liquidity value.

**Proof of concept:** Use a crafted ERC20 whose transfer/transferFrom returns false but does not revert. Approve FeeAMM, call `executeFeeSwap` with any `amountIn`; transferFrom returns false, but FeeAMM still reduces validator reserves and transfers validator tokens to the attacker, yielding free validator tokens.

**Remediation:** Use SafeERC20’s `safeTransfer`/`safeTransferFrom` (or require the returned boolean is true) for all token operations so calls revert on failure.
