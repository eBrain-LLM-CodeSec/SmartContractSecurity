# Security Audit Report: 2025-01-liquid-ron

Findings below were produced by the RTF (Requirement Translation Framework) pipeline: EthTrust requirement routing, deterministic evidence collection, bounded LLM judgment, and (where the bounded judgment was inconclusive, insufficient, or low-confidence) graph-gated Codex investigation.

## req-2-documented::./src/RonHelper.sol: req-2-documented::./src/RonHelper.sol

**Requirement:** 

**Location(s):** RonHelper._depositRONTo, RonHelper._withdrawRONTo

**Confidence:** MEDIUM

**Mechanism:** The function performs two external calls including a value transfer but provides no specific documentation explaining the necessity of these special operations, violating the requirement to document such uses.

**Supporting evidence:**
  - RonHelper._depositRONTo: makes an external call
  - RonHelper._depositRONTo: makes an external call
  - RonHelper._withdrawRONTo: makes an external call
  - RonHelper._withdrawRONTo: makes an external call

_Determined via graph-gated Codex investigation (0 graph queries, 131s)._

## req-3-annotate::./src/RonHelper.sol: req-3-annotate::./src/RonHelper.sol

**Requirement:** 

**Location(s):** IWRON.deposit, IWRON.transfer, IWRON.withdraw

**Confidence:** HIGH

**Mechanism:** The public interface IWRON exposes external functions including deposit without any NatSpec annotations for intent, parameters, or returns, violating the requirement that all public interfaces be documented with NatSpec.

**Supporting evidence:**
  - IWRON.deposit: public/external function has no NatSpec annotation
  - IWRON.withdraw: public/external function has no NatSpec annotation
  - IWRON.transfer: public/external function has no NatSpec annotation

_Determined via graph-gated Codex investigation (2 graph queries, 49s)._

## req-3-linted::./src/RonHelper.sol: req-3-linted::./src/RonHelper.sol

**Requirement:** 

**Location(s):** RonHelper._depositRONTo, RonHelper._withdrawRONTo

**Confidence:** HIGH

**Mechanism:** Lint requirement mandates explicit visibility for all variables; state variable wron lacks a visibility specifier, constituting noncompliance despite other lint aspects being met.

**Supporting evidence:**
  - RonHelper._withdrawRONTo: RonHelper._withdrawRONTo(address,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/RonHelper.sol#38-42) is never used and should be removed
  - RonHelper._depositRONTo: RonHelper._depositRONTo(address,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/RonHelper.sol#30-33) is never used and should be removed

_Determined via graph-gated Codex investigation (4 graph queries, 84s)._

## req-3-all-valid-inputs::./src/RonHelper.sol: req-3-all-valid-inputs::./src/RonHelper.sol

**Requirement:** 

**Location(s):** IWRON.transfer, IWRON.withdraw, RonHelper._depositRONTo, RonHelper._withdrawRONTo

**Confidence:** MEDIUM

**Mechanism:** The transfer path relies on `_depositRONTo`, which forwards recipient and amount directly to `IWRON.transfer` without checks. No graph-discovered callers provide upstream validation. Inputs can therefore be malformed (e.g., zero address or zero value) without being rejected, violating the requirement that all inputs be validated.

**Supporting evidence:**
  - IWRON.withdraw: none of this function's parameters (['']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - IWRON.transfer: none of this function's parameters (['', '']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - RonHelper._depositRONTo: none of this function's parameters (['amount', 'to']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - RonHelper._withdrawRONTo: none of this function's parameters (['amount', 'to']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling

_Determined via graph-gated Codex investigation (6 graph queries, 124s)._

## req-3-event-on-state-change::./src/Pausable.sol: req-3-event-on-state-change::./src/Pausable.sol

**Requirement:** 

**Location(s):** Pausable.pause, Pausable.unpause

**Confidence:** HIGH

**Mechanism:** Both pause and unpause modify the paused state without emitting any event, violating the requirement that all state-changing transactions emit events.

**Supporting evidence:**
  - Pausable.pause: writes state but emits no event
  - Pausable.unpause: writes state but emits no event

_Determined via graph-gated Codex investigation (17 graph queries, 268s)._

## req-3-annotate::./src/Pausable.sol: req-3-annotate::./src/Pausable.sol

**Requirement:** 

**Location(s):** Pausable.pause, Pausable.unpause

**Confidence:** HIGH

**Mechanism:** All ABI-exposed members (public variable and external functions) lack required NatSpec comments explaining intent, parameters, returns, and safe usage, violating the requirement.

**Supporting evidence:**
  - Pausable.pause: public/external function has no NatSpec annotation
  - Pausable.unpause: public/external function has no NatSpec annotation

_Determined via graph-gated Codex investigation (2 graph queries, 58s)._

## req-1-use-c-e-i::./src/LiquidRon.sol: req-1-use-c-e-i::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards

**Confidence:** HIGH

**Mechanism:** harvest invokes an external proxy call then updates internal fee accounting afterward without reentrancy guard or pre-call effects, so CEI pattern is not followed.

**Supporting evidence:**
  - LiquidRon.harvest: external call at node 1 followed by state write at node 2 (CFG-reachable)
  - LiquidRon.harvestAndDelegateRewards: external call at node 2 followed by state write at node 3 (CFG-reachable)

_Determined via graph-gated Codex investigation (13 graph queries, 179s)._

## req-2-external-calls::./src/LiquidRon.sol: req-2-external-calls::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards

**Confidence:** MEDIUM

**Mechanism:** External calls go to owner-deployed proxies within the tested set, but neither function applies checks-effects-interactions or any reentrancy guard around those calls, so required protection is absent.

**Supporting evidence:**
  - LiquidRon.harvest: external call at node 1 followed by state write at node 2 (CFG-reachable)
  - LiquidRon.harvestAndDelegateRewards: external call at node 2 followed by state write at node 3 (CFG-reachable)

_Determined via graph-gated Codex investigation (19 graph queries, 254s)._

## req-2-documented::./src/LiquidRon.sol: req-2-documented::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20._spendAllowance, ERC20._update, ERC4626._convertToAssets, ERC4626._convertToShares, ERC4626._deposit, ERC4626._tryGetAssetDecimals, ERC4626._withdraw, ERC4626.totalAssets, Escrow.constructor, Escrow.deposit, LiquidProxy.delegateAmount, LiquidProxy.harvest, LiquidProxy.harvestAndDelegateRewards, LiquidProxy.redelegateAmount, LiquidProxy.undelegateAmount, LiquidRon._checkUserCanReceiveRon, LiquidRon._convertToAssets, LiquidRon._getTotalRewardsInProxy, LiquidRon._getTotalStakedInProxy, LiquidRon._withdraw, LiquidRon.constructor, LiquidRon.delegateAmount, LiquidRon.deposit, LiquidRon.getAssetsInVault, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, LiquidRon.pruneValidatorList, LiquidRon.receive, LiquidRon.redeem, LiquidRon.redelegateAmount, LiquidRon.undelegateAmount, Math.ceilDiv, Math.invMod, Math.invModPrime, Math.log10, Math.log2, Math.log256, Math.modExp, Math.mulDiv, Math.sqrt, Math.ternary, Math.tryAdd, Math.tryModExp, Math.tryMul, Math.trySub, Panic.panic, RonHelper._depositRONTo, RonHelper._withdrawRONTo, SafeCast.toUint, SafeERC20._callOptionalReturn, SafeERC20._callOptionalReturnBool, SafeERC20.approveAndCallRelaxed, SafeERC20.safeDecreaseAllowance, SafeERC20.safeIncreaseAllowance, SafeERC20.transferAndCallRelaxed, SafeERC20.transferFromAndCallRelaxed

**Confidence:** HIGH

**Mechanism:** Constructor performs an external approve call, which qualifies as a special operation, but no comment or documentation explains its necessity, violating the documentation requirement.

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

_Determined via graph-gated Codex investigation (1 graph queries, 36s)._

## req-3-event-on-state-change::./src/LiquidRon.sol: req-3-event-on-state-change::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20.constructor, ERC4626.constructor, Escrow.constructor, LiquidProxy.constructor, LiquidRon.constructor, LiquidRon.deployStakingProxy, LiquidRon.fetchOperatorFee, LiquidRon.setOperatorFee, LiquidRon.slitherConstructorConstantVariables, LiquidRon.updateFeeRecipient, LiquidRon.updateOperator, Panic.slitherConstructorConstantVariables, Pausable.pause, Pausable.unpause, RonHelper.constructor, ValidatorTracker._removeValidator, ValidatorTracker._tryPushValidator

**Confidence:** HIGH

**Mechanism:** Constructor assigns the `_vault` state variable but does not emit any contract event reflecting this state change, violating the requirement that all state-changing transactions emit an event.

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

_Determined via graph-gated Codex investigation (3 graph queries, 76s)._

## req-3-annotate::./src/LiquidRon.sol: req-3-annotate::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ILiquidProxy.delegateAmount, ILiquidProxy.harvest, ILiquidProxy.harvestAndDelegateRewards, ILiquidProxy.redelegateAmount, ILiquidProxy.undelegateAmount, IRoninValidator.bulkUndelegate, IRoninValidator.claimRewards, IRoninValidator.delegate, IRoninValidator.delegateRewards, IRoninValidator.getManyStakingAmounts, IRoninValidator.getManyStakingTotals, IRoninValidator.getReward, IRoninValidator.getRewards, IRoninValidator.getStakingAmount, IRoninValidator.getStakingTotal, IRoninValidator.redelegate, IRoninValidator.undelegate, IVault.deposit, IWRON.deposit, IWRON.transfer, IWRON.withdraw, Pausable.pause, Pausable.unpause

**Confidence:** HIGH

**Mechanism:** The public/external function delegateAmount in ILiquidProxy is declared without any NatSpec comments; the interface contains no NatSpec annotations for its public interfaces, violating the requirement that all public interfaces be annotated.

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

_Determined via graph-gated Codex investigation (2 graph queries, 100s)._

## req-2-documented::./src/LiquidProxy.sol: req-2-documented::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** LiquidProxy.delegateAmount, LiquidProxy.harvest, LiquidProxy.harvestAndDelegateRewards, LiquidProxy.redelegateAmount, LiquidProxy.undelegateAmount, RonHelper._depositRONTo, RonHelper._withdrawRONTo

**Confidence:** MEDIUM

**Mechanism:** The function makes an external payable call to the staking contract but lacks an explicit justification or note about the necessity/risks of that external call as required for documenting special code use.

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

_Determined via graph-gated Codex investigation (3 graph queries, 83s)._

## req-3-event-on-state-change::./src/LiquidProxy.sol: req-3-event-on-state-change::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** LiquidProxy.constructor, RonHelper.constructor

**Confidence:** HIGH

**Mechanism:** Constructor transactions change storage (vault, roninStaking, wron) yet neither the constructor nor its base emits any event, so this state change is untracked, violating the requirement that all transactions causing state changes emit an event.

**Supporting evidence:**
  - LiquidProxy.constructor: writes state but emits no event
  - RonHelper.constructor: writes state but emits no event

_Determined via graph-gated Codex investigation (6 graph queries, 111s)._

## req-3-annotate::./src/LiquidProxy.sol: req-3-annotate::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** ILiquidProxy.delegateAmount, ILiquidProxy.harvest, ILiquidProxy.harvestAndDelegateRewards, ILiquidProxy.redelegateAmount, ILiquidProxy.undelegateAmount, IRoninValidator.bulkUndelegate, IRoninValidator.claimRewards, IRoninValidator.delegate, IRoninValidator.delegateRewards, IRoninValidator.getManyStakingAmounts, IRoninValidator.getManyStakingTotals, IRoninValidator.getReward, IRoninValidator.getRewards, IRoninValidator.getStakingAmount, IRoninValidator.getStakingTotal, IRoninValidator.redelegate, IRoninValidator.undelegate, IWRON.deposit, IWRON.transfer, IWRON.withdraw

**Confidence:** HIGH

**Mechanism:** The public interface function delegateAmount is part of the ABI but has no NatSpec comments describing intent, parameters, return values, or safety guidance, violating the requirement that all public interfaces be annotated.

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

_Determined via graph-gated Codex investigation (2 graph queries, 48s)._

## req-3-linted::./src/LiquidProxy.sol: req-3-linted::./src/LiquidProxy.sol

**Requirement:** 

**Location(s):** RonHelper._withdrawRONTo

**Confidence:** HIGH

**Mechanism:** The contract complies with pragma and naming constraints and has no unreachable code or unnecessary variables in the inspected area. However, the state variable `wron` and the constructor lack explicit visibility specifiers, violating the requirement that all functions and variables declare visibility.

**Supporting evidence:**
  - RonHelper._withdrawRONTo: RonHelper._withdrawRONTo(address,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/RonHelper.sol#38-42) is never used and should be removed

_Determined via graph-gated Codex investigation (1 graph queries, 46s)._

## req-2-documented::./src/Escrow.sol: req-2-documented::./src/Escrow.sol

**Requirement:** 

**Location(s):** Escrow.constructor, Escrow.deposit

**Confidence:** HIGH

**Mechanism:** Constructor performs an external call (IERC20.approve) but provides no documentation describing the necessity of this special operation, violating the requirement to document each instance.

**Supporting evidence:**
  - Escrow.constructor: makes an external call
  - Escrow.deposit: makes an external call

_Determined via graph-gated Codex investigation (1 graph queries, 35s)._

## req-3-event-on-state-change::./src/Escrow.sol: req-3-event-on-state-change::./src/Escrow.sol

**Requirement:** 

**Location(s):** Escrow.constructor

**Confidence:** MEDIUM

**Mechanism:** The constructor initializes `_vault`, a contract state variable, but the contract defines no events and emits none in the constructor. Since this state change occurs without an event, the requirement that all transactions causing state changes emit an event is violated.

**Supporting evidence:**
  - Escrow.constructor: writes state but emits no event

_Determined via graph-gated Codex investigation (7 graph queries, 99s)._

## req-3-annotate::./src/Escrow.sol: req-3-annotate::./src/Escrow.sol

**Requirement:** 

**Location(s):** IVault.deposit

**Confidence:** HIGH

**Mechanism:** The only public interface function IVault.deposit is defined without any NatSpec comments, so the code fails the requirement to document all public interfaces.

**Supporting evidence:**
  - IVault.deposit: public/external function has no NatSpec annotation

_Determined via graph-gated Codex investigation (2 graph queries, 88s)._
