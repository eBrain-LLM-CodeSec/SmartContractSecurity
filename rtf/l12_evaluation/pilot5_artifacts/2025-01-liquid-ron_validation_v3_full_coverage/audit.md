# Security Audit Report: 2025-01-liquid-ron

Findings below were produced by the RTF (Requirement Translation Framework) pipeline: EthTrust requirement routing, deterministic evidence collection, bounded LLM judgment, and (where the bounded judgment was inconclusive, insufficient, or low-confidence) graph-gated Codex investigation.

## req-3-all-valid-inputs::./src/ValidatorTracker.sol: req-3-all-valid-inputs::./src/ValidatorTracker.sol

**Requirement:** 

**Location(s):** ValidatorTracker._removeValidator, ValidatorTracker._tryPushValidator

**Confidence:** MEDIUM

**Mechanism:** Both internal helpers accept any address without sanity checks (e.g., zero address) and rely solely on an active-flag guard, leaving malformed inputs unvalidated. This violates the requirement that inputs be validated even though caller context is unknown.

**Supporting evidence:**
  - ValidatorTracker._tryPushValidator: none of this function's parameters (['_validator']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - ValidatorTracker._removeValidator: none of this function's parameters (['_validator']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling

_Determined via graph-gated Codex investigation (8 graph queries, 121s)._

## req-3-event-on-state-change::./src/ValidatorTracker.sol: req-3-event-on-state-change::./src/ValidatorTracker.sol

**Requirement:** 

**Location(s):** ValidatorTracker._removeValidator, ValidatorTracker._tryPushValidator

**Confidence:** HIGH

**Mechanism:** _removeValidator updates multiple state variables and performs array/index swaps but emits no event; no events are defined in ValidatorTracker for validator additions/removals. Graph showed no callers, so evidence is limited to the contract itself, but the lack of event emission on state changes violates the requirement.

**Supporting evidence:**
  - ValidatorTracker._tryPushValidator: writes state but emits no event
  - ValidatorTracker._removeValidator: writes state but emits no event

_Determined via graph-gated Codex investigation (10 graph queries, 126s)._

## req-2-documented::./src/RonHelper.sol: req-2-documented::./src/RonHelper.sol

**Requirement:** 

**Location(s):** RonHelper._depositRONTo, RonHelper._withdrawRONTo

**Confidence:** HIGH

**Mechanism:** External calls in _depositRONTo lack justification documentation required by the standard; no other special constructs are present.

**Supporting evidence:**
  - RonHelper._depositRONTo: makes an external call
  - RonHelper._depositRONTo: makes an external call
  - RonHelper._withdrawRONTo: makes an external call
  - RonHelper._withdrawRONTo: makes an external call

_Determined via graph-gated Codex investigation (3 graph queries, 55s)._

## req-3-pass-l2::./src/RonHelper.sol: req-3-pass-l2::./src/RonHelper.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-linted::./src/RonHelper.sol: req-3-linted::./src/RonHelper.sol

**Requirement:** 

**Location(s):** RonHelper._depositRONTo, RonHelper._withdrawRONTo

**Confidence:** HIGH

**Mechanism:** The linting requirement mandates explicit visibility on all variables. Contract `RonHelper` declares `address wron;` without a visibility specifier, breaching the rule; other checks (pragma, function visibility) pass, but the missing visibility on `wron` is sufficient to fail.

**Supporting evidence:**
  - RonHelper._withdrawRONTo: RonHelper._withdrawRONTo(address,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/RonHelper.sol#38-42) is never used and should be removed
  - RonHelper._depositRONTo: RonHelper._depositRONTo(address,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/RonHelper.sol#30-33) is never used and should be removed

_Determined via graph-gated Codex investigation (2 graph queries, 56s)._

## req-3-all-valid-inputs::./src/RonHelper.sol: req-3-all-valid-inputs::./src/RonHelper.sol

**Requirement:** 

**Location(s):** IWRON.transfer, IWRON.withdraw, RonHelper._depositRONTo, RonHelper._withdrawRONTo

**Confidence:** MEDIUM

**Mechanism:** The candidate transfer is an unguarded interface declaration, and its only observed use in _depositRONTo forwards arbitrary caller-supplied address and amount without validation or consistency checks. This fails the requirement to validate and correctly handle malformed inputs.

**Supporting evidence:**
  - IWRON.withdraw: none of this function's parameters (['']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - IWRON.transfer: none of this function's parameters (['', '']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - RonHelper._depositRONTo: none of this function's parameters (['amount', 'to']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - RonHelper._withdrawRONTo: none of this function's parameters (['amount', 'to']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling

_Determined via graph-gated Codex investigation (7 graph queries, 108s)._

## req-3-annotate::./src/Pausable.sol: req-3-annotate::./src/Pausable.sol

**Requirement:** 

**Location(s):** Pausable.pause, Pausable.unpause

**Confidence:** HIGH

**Mechanism:** Both public functions pause and unpause expose ABI-visible interfaces without any NatSpec annotations, violating the requirement that all public interfaces be documented.

**Supporting evidence:**
  - Pausable.pause: public/external function has no NatSpec annotation
  - Pausable.unpause: public/external function has no NatSpec annotation

_Determined via graph-gated Codex investigation (3 graph queries, 63s)._

## req-1-use-c-e-i::./src/LiquidRon.sol: req-1-use-c-e-i::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards

**Confidence:** HIGH

**Mechanism:** harvest makes an external call to a proxy before modifying state and lacks any reentrancy guard; this violates the Checks-Effects-Interactions pattern required for external calls.

**Supporting evidence:**
  - LiquidRon.harvest: external call at node 1 followed by state write at node 2 (CFG-reachable)
  - LiquidRon.harvestAndDelegateRewards: external call at node 2 followed by state write at node 3 (CFG-reachable)

_Determined via graph-gated Codex investigation (10 graph queries, 194s)._

## req-2-pass-l1::./src/LiquidRon.sol: req-2-pass-l1::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-external-calls::./src/LiquidRon.sol: req-2-external-calls::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards

**Confidence:** MEDIUM

**Mechanism:** External calls target LiquidProxy instances controlled by the owner, so addresses stay within the tested set. However, both functions perform state writes after external interactions and lack any nonReentrant or Checks-Effects-Interactions safeguard, leaving reentrancy exposure, so the requirement is not met.

**Supporting evidence:**
  - LiquidRon.harvest: external call at node 1 followed by state write at node 2 (CFG-reachable)
  - LiquidRon.harvestAndDelegateRewards: external call at node 2 followed by state write at node 3 (CFG-reachable)

_Determined via graph-gated Codex investigation (17 graph queries, 219s)._

## req-2-documented::./src/LiquidRon.sol: req-2-documented::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20._spendAllowance, ERC20._update, ERC4626._convertToAssets, ERC4626._convertToShares, ERC4626._deposit, ERC4626._tryGetAssetDecimals, ERC4626._withdraw, ERC4626.totalAssets, Escrow.constructor, Escrow.deposit, LiquidProxy.delegateAmount, LiquidProxy.harvest, LiquidProxy.harvestAndDelegateRewards, LiquidProxy.redelegateAmount, LiquidProxy.undelegateAmount, LiquidRon._checkUserCanReceiveRon, LiquidRon._convertToAssets, LiquidRon._getTotalRewardsInProxy, LiquidRon._getTotalStakedInProxy, LiquidRon._withdraw, LiquidRon.constructor, LiquidRon.delegateAmount, LiquidRon.deposit, LiquidRon.getAssetsInVault, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, LiquidRon.pruneValidatorList, LiquidRon.receive, LiquidRon.redeem, LiquidRon.redelegateAmount, LiquidRon.undelegateAmount, Math.ceilDiv, Math.invMod, Math.invModPrime, Math.log10, Math.log2, Math.log256, Math.modExp, Math.mulDiv, Math.sqrt, Math.ternary, Math.tryAdd, Math.tryModExp, Math.tryMul, Math.trySub, Panic.panic, RonHelper._depositRONTo, RonHelper._withdrawRONTo, SafeCast.toUint, SafeERC20._callOptionalReturn, SafeERC20._callOptionalReturnBool, SafeERC20.approveAndCallRelaxed, SafeERC20.safeDecreaseAllowance, SafeERC20.safeIncreaseAllowance, SafeERC20.transferAndCallRelaxed, SafeERC20.transferFromAndCallRelaxed

**Confidence:** HIGH

**Mechanism:** The constructor performs an external ERC20 approval with unlimited allowance but provides no documentation explaining why this external call is required, violating the requirement to document special code use.

**Supporting evidence:**
  - SafeCast.toUint: SafeCast.toUint(bool) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol#1157-1161) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol#1158-1160)
  - SafeERC20._callOptionalReturnBool: SafeERC20._callOptionalReturnBool(IERC20,bytes) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#187-197) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#191-195)
  - Math.mulDiv: Math.mulDiv(uint256,uint256,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#144-223) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#151-154)
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#175-182)
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#188-197)
  - Math.tryModExp: Math.tryModExp(uint256,uint256,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#337-361) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#339-360)
  - SafeERC20._callOptionalReturn: SafeERC20._callOptionalReturn(IERC20,bytes) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#159-177) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#162-172)
  - Math.tryModExp: Math.tryModExp(bytes,bytes,bytes) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#377-399) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#389-398)
  - Panic.panic: Panic.panic(uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Panic.sol#50-56) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Panic.sol#51-55)
  - ERC4626._tryGetAssetDecimals: makes an external call
  - ERC4626.totalAssets: makes an external call
  - ERC4626._convertToShares: makes an external call
  - ERC4626._convertToAssets: makes an external call
  - ERC4626._deposit: makes an external call
  - ERC4626._withdraw: makes an external call
  - SafeERC20.safeIncreaseAllowance: makes an external call
  - SafeERC20.safeDecreaseAllowance: makes an external call
  - SafeERC20.transferAndCallRelaxed: makes an external call
  - SafeERC20.transferFromAndCallRelaxed: makes an external call
  - SafeERC20.approveAndCallRelaxed: makes an external call
  - Math.ternary: makes an external call
  - Math.ceilDiv: makes an external call
  - Math.ceilDiv: makes an external call
  - Math.mulDiv: makes an external call
  - Math.mulDiv: makes an external call
  - Math.modExp: makes an external call
  - Math.modExp: makes an external call
  - Math.sqrt: makes an external call
  - Math.sqrt: makes an external call
  - Math.log2: makes an external call
  - Math.log2: makes an external call
  - Math.log2: makes an external call
  - Math.log2: makes an external call
  - Math.log2: makes an external call
  - Math.log2: makes an external call
  - Math.log2: makes an external call
  - Math.log2: makes an external call
  - Math.log2: makes an external call
  - Math.log10: makes an external call
  - Math.log256: makes an external call
  - Math.log256: makes an external call
  - Math.log256: makes an external call
  - Math.log256: makes an external call
  - Math.log256: makes an external call
  - Math.log256: makes an external call
  - Escrow.constructor: makes an external call
  - Escrow.deposit: makes an external call
  - LiquidProxy.harvest: makes an external call
  - LiquidProxy.harvestAndDelegateRewards: makes an external call
  - LiquidProxy.delegateAmount: makes an external call
  - LiquidProxy.redelegateAmount: makes an external call
  - LiquidProxy.undelegateAmount: makes an external call
  - LiquidRon.constructor: makes an external call
  - LiquidRon.harvest: makes an external call
  - LiquidRon.harvestAndDelegateRewards: makes an external call
  - LiquidRon.delegateAmount: makes an external call
  - LiquidRon.redelegateAmount: makes an external call
  - LiquidRon.undelegateAmount: makes an external call
  - LiquidRon.pruneValidatorList: makes an external call
  - LiquidRon.pruneValidatorList: makes an external call
  - LiquidRon.getAssetsInVault: makes an external call
  - LiquidRon.deposit: makes an external call
  - LiquidRon.redeem: makes an external call
  - LiquidRon._getTotalRewardsInProxy: makes an external call
  - LiquidRon._getTotalStakedInProxy: makes an external call
  - LiquidRon._convertToAssets: makes an external call
  - LiquidRon._checkUserCanReceiveRon: makes an external call
  - LiquidRon._withdraw: makes an external call
  - LiquidRon.receive: makes an external call
  - RonHelper._depositRONTo: makes an external call
  - RonHelper._depositRONTo: makes an external call
  - RonHelper._withdrawRONTo: makes an external call
  - RonHelper._withdrawRONTo: makes an external call
  - ERC20._update: - operation, inside unchecked{} block
  - ERC20._update: - operation, inside unchecked{} block
  - ERC20._update: + operation, inside unchecked{} block
  - ERC20._spendAllowance: - operation, inside unchecked{} block
  - SafeERC20.safeDecreaseAllowance: - operation, inside unchecked{} block
  - SafeERC20._callOptionalReturn: + operation, inside unchecked{} block
  - SafeERC20._callOptionalReturnBool: + operation, inside unchecked{} block
  - Math.tryAdd: + operation, inside unchecked{} block
  - Math.trySub: - operation, inside unchecked{} block
  - Math.tryMul: * operation, inside unchecked{} block
  - Math.ternary: * operation, inside unchecked{} block
  - Math.ceilDiv: - operation, inside unchecked{} block
  - Math.ceilDiv: + operation, inside unchecked{} block
  - Math.ceilDiv: * operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: + operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.invMod: * operation, inside unchecked{} block
  - Math.invMod: - operation, inside unchecked{} block
  - Math.invMod: * operation, inside unchecked{} block
  - Math.invMod: - operation, inside unchecked{} block
  - Math.invMod: - operation, inside unchecked{} block
  - Math.invMod: - operation, inside unchecked{} block
  - Math.invModPrime: - operation, inside unchecked{} block
  - Math.tryModExp: + operation, inside unchecked{} block
  - Math.tryModExp: + operation, inside unchecked{} block
  - Math.tryModExp: + operation, inside unchecked{} block
  - Math.tryModExp: + operation, inside unchecked{} block
  - Math.tryModExp: + operation, inside unchecked{} block
  - Math.tryModExp: + operation, inside unchecked{} block
  - Math.tryModExp: + operation, inside unchecked{} block
  - Math.sqrt: * operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: - operation, inside unchecked{} block
  - Math.sqrt: * operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.log2: - operation, inside unchecked{} block
  - Math.log2: * operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: - operation, inside unchecked{} block
  - Math.log2: * operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: - operation, inside unchecked{} block
  - Math.log2: * operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: - operation, inside unchecked{} block
  - Math.log2: * operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: - operation, inside unchecked{} block
  - Math.log2: * operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: - operation, inside unchecked{} block
  - Math.log2: * operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: - operation, inside unchecked{} block
  - Math.log2: * operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: + operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: + operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: + operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: + operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: + operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: + operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: + operation, inside unchecked{} block
  - Math.log10: ** operation, inside unchecked{} block
  - Math.log10: + operation, inside unchecked{} block
  - Math.log256: - operation, inside unchecked{} block
  - Math.log256: * operation, inside unchecked{} block
  - Math.log256: * operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: - operation, inside unchecked{} block
  - Math.log256: * operation, inside unchecked{} block
  - Math.log256: * operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: - operation, inside unchecked{} block
  - Math.log256: * operation, inside unchecked{} block
  - Math.log256: * operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: - operation, inside unchecked{} block
  - Math.log256: * operation, inside unchecked{} block
  - Math.log256: * operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: - operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block

_Determined via graph-gated Codex investigation (2 graph queries, 61s)._

## req-2-check-rounding::./src/LiquidRon.sol: req-2-check-rounding::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.getTotalRewards, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, Math.average, Math.ceilDiv, Math.invMod, Math.log10, Math.mulDiv, Math.sqrt, Math.tryDiv, Math.tryMul

**Confidence:** HIGH

**Mechanism:** getTotalRewards and harvest functions apply operator fee via integer division, truncating fractional fees and potentially accumulating undistributed wei. The code lacks documentation of rounding error bounds or safeguards, violating the requirement to identify and protect against rounding effects.

**Supporting evidence:**
  - Math.tryMul: division operation (potential rounding)
  - Math.tryDiv: division operation (potential rounding)
  - Math.average: division operation (potential rounding)
  - Math.ceilDiv: division operation (potential rounding)
  - Math.mulDiv: division operation (potential rounding)
  - Math.mulDiv: division operation (potential rounding)
  - Math.mulDiv: division operation (potential rounding)
  - Math.mulDiv: division operation (potential rounding)
  - Math.invMod: division operation (potential rounding)
  - Math.sqrt: division operation (potential rounding)
  - Math.sqrt: division operation (potential rounding)
  - Math.sqrt: division operation (potential rounding)
  - Math.sqrt: division operation (potential rounding)
  - Math.sqrt: division operation (potential rounding)
  - Math.sqrt: division operation (potential rounding)
  - Math.sqrt: division operation (potential rounding)
  - Math.log10: division operation (potential rounding)
  - Math.log10: division operation (potential rounding)
  - Math.log10: division operation (potential rounding)
  - Math.log10: division operation (potential rounding)
  - Math.log10: division operation (potential rounding)
  - Math.log10: division operation (potential rounding)
  - LiquidRon.harvest: division operation (potential rounding)
  - LiquidRon.harvestAndDelegateRewards: division operation (potential rounding)
  - LiquidRon.getTotalRewards: division operation (potential rounding)

_Determined via graph-gated Codex investigation (18 graph queries, 222s)._

## req-3-pass-l2::./src/LiquidRon.sol: req-3-pass-l2::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-event-on-state-change::./src/LiquidRon.sol: req-3-event-on-state-change::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20.constructor, ERC4626.constructor, Escrow.constructor, LiquidProxy.constructor, LiquidRon.constructor, LiquidRon.deployStakingProxy, LiquidRon.fetchOperatorFee, LiquidRon.setOperatorFee, LiquidRon.slitherConstructorConstantVariables, LiquidRon.updateFeeRecipient, LiquidRon.updateOperator, Panic.slitherConstructorConstantVariables, Pausable.pause, Pausable.unpause, RonHelper.constructor, ValidatorTracker._removeValidator, ValidatorTracker._tryPushValidator

**Confidence:** HIGH

**Mechanism:** Constructor changes state by setting _vault but contains no emit and has no callees; thus the state-changing transaction lacks an event.

**Supporting evidence:**
  - ERC20.constructor: writes state but emits no event
  - ERC4626.constructor: writes state but emits no event
  - Panic.slitherConstructorConstantVariables: writes state but emits no event
  - Escrow.constructor: writes state but emits no event
  - LiquidProxy.constructor: writes state but emits no event
  - LiquidRon.constructor: writes state but emits no event
  - LiquidRon.updateFeeRecipient: writes state but emits no event
  - LiquidRon.updateOperator: writes state but emits no event
  - LiquidRon.setOperatorFee: writes state but emits no event
  - LiquidRon.deployStakingProxy: writes state but emits no event
  - LiquidRon.fetchOperatorFee: writes state but emits no event
  - LiquidRon.slitherConstructorConstantVariables: writes state but emits no event
  - Pausable.pause: writes state but emits no event
  - Pausable.unpause: writes state but emits no event
  - RonHelper.constructor: writes state but emits no event
  - ValidatorTracker._tryPushValidator: writes state but emits no event
  - ValidatorTracker._removeValidator: writes state but emits no event

_Determined via graph-gated Codex investigation (6 graph queries, 76s)._

## req-3-annotate::./src/LiquidRon.sol: req-3-annotate::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ILiquidProxy.delegateAmount, ILiquidProxy.harvest, ILiquidProxy.harvestAndDelegateRewards, ILiquidProxy.redelegateAmount, ILiquidProxy.undelegateAmount, IRoninValidator.bulkUndelegate, IRoninValidator.claimRewards, IRoninValidator.delegate, IRoninValidator.delegateRewards, IRoninValidator.getManyStakingAmounts, IRoninValidator.getManyStakingTotals, IRoninValidator.getReward, IRoninValidator.getRewards, IRoninValidator.getStakingAmount, IRoninValidator.getStakingTotal, IRoninValidator.redelegate, IRoninValidator.undelegate, IVault.deposit, IWRON.deposit, IWRON.transfer, IWRON.withdraw, Pausable.pause, Pausable.unpause

**Confidence:** HIGH

**Mechanism:** The public interface function delegateAmount appears without any NatSpec inline documentation, violating the requirement that all public interfaces be annotated.

**Supporting evidence:**
  - IVault.deposit: public/external function has no NatSpec annotation
  - Pausable.pause: public/external function has no NatSpec annotation
  - Pausable.unpause: public/external function has no NatSpec annotation
  - IWRON.deposit: public/external function has no NatSpec annotation
  - IWRON.withdraw: public/external function has no NatSpec annotation
  - IWRON.transfer: public/external function has no NatSpec annotation
  - ILiquidProxy.harvest: public/external function has no NatSpec annotation
  - ILiquidProxy.harvestAndDelegateRewards: public/external function has no NatSpec annotation
  - ILiquidProxy.delegateAmount: public/external function has no NatSpec annotation
  - ILiquidProxy.redelegateAmount: public/external function has no NatSpec annotation
  - ILiquidProxy.undelegateAmount: public/external function has no NatSpec annotation
  - IRoninValidator.delegate: public/external function has no NatSpec annotation
  - IRoninValidator.undelegate: public/external function has no NatSpec annotation
  - IRoninValidator.redelegate: public/external function has no NatSpec annotation
  - IRoninValidator.bulkUndelegate: public/external function has no NatSpec annotation
  - IRoninValidator.claimRewards: public/external function has no NatSpec annotation
  - IRoninValidator.delegateRewards: public/external function has no NatSpec annotation
  - IRoninValidator.getRewards: public/external function has no NatSpec annotation
  - IRoninValidator.getReward: public/external function has no NatSpec annotation
  - IRoninValidator.getStakingTotal: public/external function has no NatSpec annotation
  - IRoninValidator.getManyStakingTotals: public/external function has no NatSpec annotation
  - IRoninValidator.getStakingAmount: public/external function has no NatSpec annotation
  - IRoninValidator.getManyStakingAmounts: public/external function has no NatSpec annotation

_Determined via graph-gated Codex investigation (2 graph queries, 35s)._

## req-3-access-control::./src/LiquidRon.sol: req-3-access-control::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20.approve, ERC20.transfer, ERC20.transferFrom, ERC4626.deposit, ERC4626.mint, ERC4626.redeem, ERC4626.withdraw, LiquidRon.delegateAmount, LiquidRon.deployStakingProxy, LiquidRon.deposit, LiquidRon.fetchOperatorFee, LiquidRon.finaliseRonRewardsForEpoch, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, LiquidRon.mint, LiquidRon.pruneValidatorList, LiquidRon.redeem, LiquidRon.redelegateAmount, LiquidRon.requestWithdrawal, LiquidRon.setOperatorFee, LiquidRon.updateFeeRecipient, LiquidRon.updateOperator, LiquidRon.withdraw, Ownable.renounceOwnership, Ownable.transferOwnership, Pausable.pause, Pausable.unpause

**Confidence:** MEDIUM

**Mechanism:** delegateAmount moves vault funds and is intended for operators, but onlyOperator is written with an OR condition that blocks all designated operators and leaves only the owner able to perform delegation. This does not implement the documented operator role and concentrates privileged actions under the broader owner privilege rather than least-privilege operator access.

**Supporting evidence:**
  - Ownable.renounceOwnership: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Ownable.transferOwnership: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - ERC20.transfer: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - ERC20.approve: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - ERC20.transferFrom: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - ERC4626.deposit: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - ERC4626.mint: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - ERC4626.withdraw: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - ERC4626.redeem: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.updateFeeRecipient: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.updateOperator: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.setOperatorFee: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.deployStakingProxy: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.fetchOperatorFee: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.harvest: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.harvestAndDelegateRewards: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.delegateAmount: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.redelegateAmount: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.pruneValidatorList: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.finaliseRonRewardsForEpoch: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.withdraw: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.redeem: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.deposit: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.mint: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.requestWithdrawal: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - LiquidRon.redeem: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Pausable.pause: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Pausable.unpause: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here

_Determined via graph-gated Codex investigation (20 graph queries, 355s)._

## req-2-documented::./src/LiquidProxy.sol: req-2-documented::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** LiquidProxy.delegateAmount, LiquidProxy.harvest, LiquidProxy.harvestAndDelegateRewards, LiquidProxy.redelegateAmount, LiquidProxy.undelegateAmount, RonHelper._depositRONTo, RonHelper._withdrawRONTo

**Confidence:** MEDIUM

**Mechanism:** delegateAmount performs an external call with value to the staking contract. EthTrust requires documenting the necessity of each special construct such as external calls. The accompanying documentation only describes inputs and actions, not the rationale for this external interaction, leaving the requirement unmet.

**Supporting evidence:**
  - LiquidProxy.harvest: makes an external call
  - LiquidProxy.harvestAndDelegateRewards: makes an external call
  - LiquidProxy.delegateAmount: makes an external call
  - LiquidProxy.redelegateAmount: makes an external call
  - LiquidProxy.undelegateAmount: makes an external call
  - RonHelper._depositRONTo: makes an external call
  - RonHelper._depositRONTo: makes an external call
  - RonHelper._withdrawRONTo: makes an external call
  - RonHelper._withdrawRONTo: makes an external call

_Determined via graph-gated Codex investigation (5 graph queries, 109s)._

## req-3-pass-l2::./src/LiquidProxy.sol: req-3-pass-l2::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-linted::./src/LiquidProxy.sol: req-3-linted::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** RonHelper._withdrawRONTo

**Confidence:** HIGH

**Mechanism:** Pragma and function visibility are explicitly set, with no asserts or unreachable code and no constructor-name conflicts. However, the state variable wron omits an explicit visibility modifier, violating the explicit visibility requirement; therefore the candidate fails the linting requirement.

**Supporting evidence:**
  - RonHelper._withdrawRONTo: RonHelper._withdrawRONTo(address,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/RonHelper.sol#38-42) is never used and should be removed

_Determined via graph-gated Codex investigation (1 graph queries, 47s)._

## req-3-event-on-state-change::./src/LiquidProxy.sol: req-3-event-on-state-change::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** LiquidProxy.constructor, RonHelper.constructor

**Confidence:** HIGH

**Mechanism:** The constructor updates vault and roninStaking without emitting any event, and these are the only writes, violating the requirement that every state-changing transaction emit an event.

**Supporting evidence:**
  - LiquidProxy.constructor: writes state but emits no event
  - RonHelper.constructor: writes state but emits no event

_Determined via graph-gated Codex investigation (8 graph queries, 94s)._

## req-3-annotate::./src/LiquidProxy.sol: req-3-annotate::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** ILiquidProxy.delegateAmount, ILiquidProxy.harvest, ILiquidProxy.harvestAndDelegateRewards, ILiquidProxy.redelegateAmount, ILiquidProxy.undelegateAmount, IRoninValidator.bulkUndelegate, IRoninValidator.claimRewards, IRoninValidator.delegate, IRoninValidator.delegateRewards, IRoninValidator.getManyStakingAmounts, IRoninValidator.getManyStakingTotals, IRoninValidator.getReward, IRoninValidator.getRewards, IRoninValidator.getStakingAmount, IRoninValidator.getStakingTotal, IRoninValidator.redelegate, IRoninValidator.undelegate, IWRON.deposit, IWRON.transfer, IWRON.withdraw

**Confidence:** HIGH

**Mechanism:** The public interface function delegateAmount has no NatSpec annotations describing its intent, parameters, or returns, violating the requirement that all public interfaces be annotated.

**Supporting evidence:**
  - IWRON.deposit: public/external function has no NatSpec annotation
  - IWRON.withdraw: public/external function has no NatSpec annotation
  - IWRON.transfer: public/external function has no NatSpec annotation
  - ILiquidProxy.harvest: public/external function has no NatSpec annotation
  - ILiquidProxy.harvestAndDelegateRewards: public/external function has no NatSpec annotation
  - ILiquidProxy.delegateAmount: public/external function has no NatSpec annotation
  - ILiquidProxy.redelegateAmount: public/external function has no NatSpec annotation
  - ILiquidProxy.undelegateAmount: public/external function has no NatSpec annotation
  - IRoninValidator.delegate: public/external function has no NatSpec annotation
  - IRoninValidator.undelegate: public/external function has no NatSpec annotation
  - IRoninValidator.redelegate: public/external function has no NatSpec annotation
  - IRoninValidator.bulkUndelegate: public/external function has no NatSpec annotation
  - IRoninValidator.claimRewards: public/external function has no NatSpec annotation
  - IRoninValidator.delegateRewards: public/external function has no NatSpec annotation
  - IRoninValidator.getRewards: public/external function has no NatSpec annotation
  - IRoninValidator.getReward: public/external function has no NatSpec annotation
  - IRoninValidator.getStakingTotal: public/external function has no NatSpec annotation
  - IRoninValidator.getManyStakingTotals: public/external function has no NatSpec annotation
  - IRoninValidator.getStakingAmount: public/external function has no NatSpec annotation
  - IRoninValidator.getManyStakingAmounts: public/external function has no NatSpec annotation

_Determined via graph-gated Codex investigation (2 graph queries, 43s)._

## req-3-consistent-solidity-output::./src/LiquidProxy.sol: req-3-consistent-solidity-output::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** pragma solidity^0.8.20

**Confidence:** MEDIUM

**Mechanism:** The code declares a caret Solidity version (^0.8.20), which permits compilation with multiple compiler versions. Patch and minor compiler updates can change generated bytecode, so this wide range does not ensure the same bytecode across all allowed versions as required.

**Supporting evidence:**
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-documented::./src/Escrow.sol: req-2-documented::./src/Escrow.sol

**Requirement:** 

**Location(s):** Escrow.constructor, Escrow.deposit

**Confidence:** HIGH

**Mechanism:** The constructor performs an external token approval but lacks any documentation explaining its necessity, violating the requirement to document special code use such as external calls.

**Supporting evidence:**
  - Escrow.constructor: makes an external call
  - Escrow.deposit: makes an external call

_Determined via graph-gated Codex investigation (3 graph queries, 54s)._

## req-3-pass-l2::./src/Escrow.sol: req-3-pass-l2::./src/Escrow.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-event-on-state-change::./src/Escrow.sol: req-3-event-on-state-change::./src/Escrow.sol

**Requirement:** 

**Location(s):** Escrow.constructor

**Confidence:** HIGH

**Mechanism:** The constructor writes to state variable `_vault` without emitting any event, and the contract defines no events at all. Since a transaction causes a state change without an accompanying event, the requirement is violated.

**Supporting evidence:**
  - Escrow.constructor: writes state but emits no event

_Determined via graph-gated Codex investigation (8 graph queries, 106s)._

## req-3-annotate::./src/Escrow.sol: req-3-annotate::./src/Escrow.sol

**Requirement:** 

**Location(s):** IVault.deposit

**Confidence:** HIGH

**Mechanism:** The public interface function deposit in IVault lacks any NatSpec annotation explaining intent or parameters, so the code does not meet the requirement that all public interfaces be annotated.

**Supporting evidence:**
  - IVault.deposit: public/external function has no NatSpec annotation

_Determined via graph-gated Codex investigation (2 graph queries, 53s)._

## req-3-consistent-solidity-output::./src/Escrow.sol: req-3-consistent-solidity-output::./src/Escrow.sol

**Requirement:** 

**Location(s):** pragma solidity^0.8.20

**Confidence:** MEDIUM

**Mechanism:** The only observed pragma uses a caret range ^0.8.20, which permits multiple compiler versions. Minor and patch releases in this range can change code generation, so the specified range is unlikely to guarantee identical bytecode across all allowed compilers, violating the requirement to constrain the pragma to versions producing the same bytecode.

**Supporting evidence:**
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin

_Determined via bounded LLM judgment on deterministically-collected evidence._
