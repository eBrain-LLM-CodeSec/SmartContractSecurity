# 2023-07-pooltogether Report



## [HIGH] Reentrancy in Vault

**Location:** `src/Vault.sol`, line(s) 566, 567, 568, 570, 573, 574, 581, 584

vault.liquidate computes the liquidatable yield once (lines 566‑568) then makes two external calls before updating supply/fee accounting (lines 570 and 581). If the prizePool (or yieldVault) is malicious, it can call back into the liquidationPair, which reenters liquidate while the first call is still active. Because no state has changed yet and there is no reentrancy guard, the second call sees the same available yield and mints another _amountOut. When the outer call resumes it also mints, so total shares minted exceed actual yield, driving the vault undercollateralized and letting the attacker extract unbacked shares.

**Suggested fix:** Add a reentrancy guard to liquidate (e.g., inherit ReentrancyGuard and wrap with nonReentrant) or move the state-updating effects (_increaseYieldFeeBalance and _mint) before any external calls, ensuring subsequent reentrant executions observe updated totals.

## [HIGH] Integer truncation / accounting mismatch in Vault

**Location:** `src/Vault.sol`, line(s) 1138, 1139, 1140, 1142

Vault._burn downcasts the caller‑provided `_shares` to uint96 before forwarding to `_twabController.burn`, so a withdraw/redeem with `_shares > 2**96-1` burns only `_shares mod 2**96` from the TWAB balances while assets are paid out for the full `_shares`. The user’s TWAB balance and totalSupply therefore drop by too little, letting them repeat withdrawals and drain assets without giving up corresponding shares.

**Suggested fix:** Validate the argument before casting, e.g. `require(_shares <= type(uint96).max, "burn too large");` or change TwabController to accept uint256 so full share amounts are burned.

## [HIGH] Reentrancy / broken cei in Vault

**Location:** `src/Vault.sol`, line(s) 931, 959, 960, 962

_deposit calls the external `_yieldVault.deposit(_assets, address(this))` at line 959 before updating its own share supply with `_mint` at line 960. A malicious or hook-enabled yield vault can reenter Vault (e.g., calling withdraw/redeem) while `totalAssets` already includes the just-deposited funds (used via `_yieldVault.maxWithdraw`), but `totalSupply` is still the old value, temporarily inflating the exchange rate. During this window an attacker holding pre-existing shares can withdraw more assets than their fair value, draining the vault.

**Suggested fix:** Apply a reentrancy guard to deposit/mint paths (e.g., inherit ReentrancyGuard and mark _deposit nonReentrant) or reorder effects before interactions by minting shares before calling `_yieldVault.deposit`, ensuring supply is updated before any external control is transferred.

## [MEDIUM] Integer truncation in Vault

**Location:** `src/Vault.sol`, line(s) 1114, 1127

Vault._mint() downcasts the uint256 _shares argument to uint96 before forwarding to the TWAB controller. When liquidate() mints _amountOut shares (no per-call cap) or mintYieldFee() mints accrued fees, _shares can exceed type(uint96).max once TVL/yield grow beyond 7.9e28 units. The downcast silently truncates the high bits, so TWAB totalSupply/balances increase by the truncated value while the Transfer event emits the full _shares and fee/Yield accounting uses the untruncated amount, leaving the caller shorted and vault accounting inconsistent.

**Suggested fix:** Before casting, revert if _shares > type(uint96).max (and similarly bound _amountOut/_shares inputs in liquidate and mintYieldFee), e.g. `if (_shares > type(uint96).max) revert SharesTooLarge(_shares); _twabController.mint(_receiver, uint96(_shares));`.

## [MEDIUM] Missing access control in Vault

**Location:** `src/Vault.sol`, line(s) 394, 395, 396, 398, 399

Accrued yield fees are tracked in `_yieldFeeTotalSupply`, but `mintYieldFee(uint256,address)` is callable by anyone and accepts any recipient. Any user can call it, decrement `_yieldFeeTotalSupply`, and mint those shares to themselves, stealing all accumulated yield fees that should belong to the configured fee recipient/treasury.

**Suggested fix:** Restrict minting of yield fees to the designated fee recipient or owner, e.g. `function mintYieldFee(uint256 _shares, address _recipient) external { require(msg.sender == _yieldFeeRecipient, CallerNotFeeRecipient()); require(_recipient == _yieldFeeRecipient); ... }` or remove the `_recipient` parameter and mint directly to `_yieldFeeRecipient`.

## [MEDIUM] Loss-of-funds in Vault

**Location:** `src/Vault.sol`, line(s) 406, 414, 864, 874

ERC4626 deposit mints shares using `_convertToShares(..., Math.Rounding.Down)` but never checks the result for zero. When the share price exceeds 1 (exchangeRate > _assetUnit), small deposits (assets < exchangeRate/_assetUnit) produce `_shares == 0`, yet `_deposit` still transfers `_assets` into the vault and deposits them into the yield vault. The user receives no shares, effectively donating their funds to existing holders.

**Suggested fix:** After computing `_shares` in `deposit`, revert if `_assets != 0 && _shares == 0` (and similarly in `depositWithPermit`/`_sponsor` if desired), matching the standard ERC4626 guard to prevent zero-share mints.



## Not investigated (budget ceiling reached)

- fn::Vault.targetOf(address)

- fn::Vault._convertToAssets(uint256,uint256,Math.Rounding)

- fn::Vault.balanceOf(address)

- fn::Vault._totalAssets()

- fn::Vault._totalSupply()

- fn::Vault._permit(IERC20Permit,address,address,uint256,uint256,uint8,bytes32,bytes32)
