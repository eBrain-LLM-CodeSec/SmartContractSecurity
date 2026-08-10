# Security Audit Report: 2024-08-phi

Findings below were produced by a single, autonomous, non-RTF Codex session using the production evmbench single-shot audit prompt (backend/worker_runner/detect.md) -- full repository access, no requirement routing, no structured tool scaffolding.

## 1. Single-share buy during cred creation allows arbitrary reentrancy and drains creator rewards (high)

**Summary:** Cred creation executes an external buy before initialization completes, without any reentrancy guard, letting a malicious bonding curve reenter and sell or buy shares multiple times to extract Ether and creator royalties.

**Location:** src/Cred.sol:532-559

createCred calls _createCredInternal, which immediately invokes buyShareCred(credIdCounter, 1, 0) before finishing cred setup; this external call happens without nonReentrant protection and before cred.latestActiveTimestamp/merkle root updates.

**Location:** src/Cred.sol:600-659

_handleTrade (used by buyShareCred/sellShareCred) sends Ether to protocolFeeDestination and IPhiRewards.deposit without nonReentrant, allowing reentry from malicious bonding curve callbacks or manipulated bonding curve implementation.

**Location:** src/Cred.sol:666-682

Share balances and supply are updated before external transfers; on reentry attacker can perform sells against inflated balances or repeat buys, draining protocol fees and creator royalties.

**Impact:** A malicious or compromised bonding curve contract can reenter during the initial buy in cred creation to mint/sell repeatedly, stealing Ether meant for protocol/creators and corrupting supply and balances, resulting in loss of funds from the protocol and other participants.

**Proof of concept:** Deploy a malicious bonding curve that, when getPriceData or when receiving Ether during _handleTrade, reenters buyShareCred/sellShareCred for the same cred before locked is reset. Call createCred with this bonding curve whitelisted; reentrancy lets the attacker drain funds and manipulate supply without limit.

**Remediation:** Add a nonReentrant guard to _handleTrade and to createCred/createCredInternal or restructure cred creation to set all state first and perform the initial buy after enabling reentrancy protection. Prefer pull-pattern for external payments or move payments after state-locking.

## 2. Batch buy/sell skips price settlement allowing free shares or unpaid payouts (high)

**Summary:** Batch trading only updates balances and supply but never transfers Ether for buys or pays proceeds for sells, enabling users to obtain shares for free or withdraw value without payment.

**Location:** src/Cred.sol:810-883

_validateAndCalculateBatch computes totalAmount but does not enforce msg.value for buys or record payouts for sells; no funds are moved here.

**Location:** src/Cred.sol:732-783

_executeBatchTrade updates balances and currentSupply, then sends protocolFeeDestination and creator fees, but never charges buyers or pays sellers the trade price. totalAmount is unused and buyer msg.value is never checked; seller proceeds are never sent.

**Impact:** Attackers can call batchBuyShareCred to mint arbitrary shares without paying the trade price (only creator/protocol fees go out), or call batchSellShareCred to reduce their balances and supply while never receiving payment, effectively creating or destroying value and draining protocol/creator fees with zero cost.

**Proof of concept:** Call batchBuyShareCred with valid credIds/amounts and maxPrices and send only minimal msg.value (even 0). Balances and supply increase, protocol/creator fees are paid from caller’s minimal value, but the core price is never charged. Similarly, batchSellShareCred reduces supply and user balances without paying the seller, letting attackers manipulate state and grief funds.

**Remediation:** In batch buys, enforce msg.value == totalAmount and deduct the full price per cred before updating balances; in batch sells, transfer price - fees to seller per cred. Mirror single-trade settlement logic inside _executeBatchTrade or settle per-item before state changes.

## 3. Cred buy/sell functions lack global reentrancy protection enabling balance/supply corruption and fee theft (high)

**Summary:** buyShareCred/sellShareCred and underlying _handleTrade are not protected by nonReentrant, yet they send Ether to user and external contracts, allowing reentry that can bypass share locks and drain fees.

**Location:** src/Cred.sol:580-659

_handleTrade executes external ETH transfers (refunds, seller payout, protocolFeeDestination.safeTransferETH, IPhiRewards.deposit) without nonReentrant guard; function modifier is absent.

**Location:** src/Cred.sol:532-546

Public entry points buyShareCred/sellShareCred/buyShareCredFor call _handleTrade directly with no reentrancy guard, permitting nested calls to manipulate lastTradeTimestamp and balances.

**Impact:** An attacker can reenter during payout/refund to perform multiple trades within one call, bypassing SHARE_LOCK_PERIOD, double-withdrawing seller proceeds, or inflating balances to later dump, causing direct loss of ETH from the contract and protocol fees.

**Proof of concept:** Implement a bonding curve whose getPriceData or fallback sends ETH back to Cred triggering buyShareCred again before locked resets; attacker loops to increase balance and withdraw proceeds multiple times within one transaction.

**Remediation:** Add nonReentrant to buy/sell entrypoints or _handleTrade, reorder state changes before external calls, and minimize external calls (use pull payments where possible).

## 4. Factory claim refund and curator deposits send all ETH to caller before distributing, enabling theft of user funds (high)

**Summary:** PhiFactory refunds `etherValue_ - mintFee` to msg.sender and CuratorRewardsDistributor refunds royalty/rounding excess to caller, letting malicious intermediaries claim on behalf of users and steal their payment or the reward pool.

**Location:** src/PhiFactory.sol:640-704

_processClaim computes mintFee and refunds `etherValue_ - mintFee` to _msgSender() (the caller), not the intended minter; callers can supply large etherValue_ and steal the refund when claiming for others.

**Location:** src/reward/CuratorRewardsDistributor.sol:98-130

distribute calculates royaltyfee and distributeAmount, then sends `royaltyfee + distributeAmount - actualDistributeAmount` (slippage/rounding surplus) to _msgSender(), allowing the caller to drain leftover funds from the reward pool.

**Impact:** In factory claims, a relayer can front users’ claims with excess msg.value and skim the difference, stealing users’ funds. In curator reward distribution, a malicious caller can engineer distributions with tiny shares so most of the pool is refunded to themselves, draining curator rewards.

**Proof of concept:** Factory: Call claim for a valid minter with 1 ETH while mintFee is minimal; the function refunds nearly all ETH to the caller, not the minter. CuratorRewards: Call distribute when balance is high but only a few wei are actually distributed (e.g., due to rounding); the caller receives nearly the entire balance via the refund.

**Remediation:** Send any refund to the actual payer/minter (or revert on excess) in _processClaim. In curator distribution, send surplus/royalty to a protocol-controlled address or proportionally distribute; never refund to arbitrary caller.
