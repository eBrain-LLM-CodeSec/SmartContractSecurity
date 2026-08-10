# Security Audit Report: 2025-01-liquid-ron

Findings below were produced by the RTF (Requirement Translation Framework) pipeline: EthTrust requirement routing, deterministic evidence collection, bounded LLM judgment, and (where the bounded judgment was inconclusive, insufficient, or low-confidence) graph-gated Codex investigation.

## req-1-no-hashing-consecutive-variable-length-args::src/LiquidRon.sol: req-1-no-hashing-consecutive-variable-length-args::src/LiquidRon.sol

**Requirement:** 

**Location(s):** Math.tryModExp

**Confidence:** None

**Mechanism:** None

**Supporting evidence:**
  - Math.tryModExp: abi.encodePacked() with 2+ consecutive dynamic-type args (taint-independent)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-1-no-assembly::src/LiquidRon.sol: req-1-no-assembly::src/LiquidRon.sol

**Requirement:** 

**Location(s):** Math.mulDiv, Math.tryModExp, Panic.panic, SafeCast.toUint, SafeERC20._callOptionalReturn, SafeERC20._callOptionalReturnBool

**Confidence:** HIGH

**Mechanism:** Inline assembly is present in Math.mulDiv (and elsewhere in Math) within the tested codebase. The requirement prohibits assembly unless the set of overriding requirements is met; no such justification or documentation is provided. Therefore the requirement is not satisfied.

**Supporting evidence:**
  - SafeERC20._callOptionalReturn: SafeERC20._callOptionalReturn(IERC20,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#159-177) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#162-172)
  - Panic.panic: Panic.panic(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Panic.sol#50-56) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Panic.sol#51-55)
  - SafeERC20._callOptionalReturnBool: SafeERC20._callOptionalReturnBool(IERC20,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#187-197) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#191-195)
  - Math.tryModExp: Math.tryModExp(uint256,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#337-361) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#339-360)
  - Math.tryModExp: Math.tryModExp(bytes,bytes,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#377-399) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#389-398)
  - SafeCast.toUint: SafeCast.toUint(bool) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol#1157-1161) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol#1158-1160)
  - Math.mulDiv: Math.mulDiv(uint256,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#144-223) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#151-154)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#175-182)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#188-197)

_Determined via graph-gated Codex investigation (1 graph queries, 217s)._

## req-1-use-c-e-i::src/LiquidRon.sol: req-1-use-c-e-i::src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards

**Confidence:** HIGH

**Mechanism:** harvest/harvestAndDelegateRewards perform external calls to LiquidProxy before state updates and without reentrancy guards, allowing reentrancy to repeat harvesting/fees; CEI not followed.

**Supporting evidence:**
  - LiquidRon.harvest: external call at node 1 followed by state write at node 2 (CFG-reachable)
  - LiquidRon.harvestAndDelegateRewards: external call at node 2 followed by state write at node 3 (CFG-reachable)

_Determined via graph-gated Codex investigation (1 graph queries, 169s)._

## req-2-pass-l1::src/LiquidRon.sol: req-2-pass-l1::src/LiquidRon.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** None

**Mechanism:** None

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-documented::src/LiquidRon.sol: req-2-documented::src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20._spendAllowance, ERC20._update, ERC4626._convertToAssets, ERC4626._convertToShares, ERC4626._deposit, ERC4626._tryGetAssetDecimals, ERC4626._withdraw, ERC4626.totalAssets, Escrow.constructor, Escrow.deposit, LiquidProxy.delegateAmount, LiquidProxy.harvest, LiquidProxy.harvestAndDelegateRewards, LiquidProxy.redelegateAmount, LiquidProxy.undelegateAmount, LiquidRon._checkUserCanReceiveRon, LiquidRon._convertToAssets, LiquidRon._getTotalRewardsInProxy, LiquidRon._getTotalStakedInProxy, LiquidRon._withdraw, LiquidRon.constructor, LiquidRon.delegateAmount, LiquidRon.deposit, LiquidRon.getAssetsInVault, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, LiquidRon.pruneValidatorList, LiquidRon.receive, LiquidRon.redeem, LiquidRon.redelegateAmount, LiquidRon.undelegateAmount, Math.ceilDiv, Math.invMod, Math.invModPrime, Math.log10, Math.log2, Math.log256, Math.modExp, Math.mulDiv, Math.sqrt, Math.ternary, Math.tryAdd, Math.tryModExp, Math.tryMul, Math.trySub, Panic.panic, RonHelper._depositRONTo, RonHelper._withdrawRONTo, SafeCast.toUint, SafeERC20._callOptionalReturn, SafeERC20._callOptionalReturnBool, SafeERC20.approveAndCallRelaxed, SafeERC20.safeDecreaseAllowance, SafeERC20.safeIncreaseAllowance, SafeERC20.transferAndCallRelaxed, SafeERC20.transferFromAndCallRelaxed

**Confidence:** MEDIUM

**Mechanism:** The requirement mandates documentation of the need for each special operation, including external calls. The Escrow constructor performs an external approve without any accompanying explanation, and other external calls similarly lack explicit justification. Therefore the documentation requirement is not fulfilled.

**Supporting evidence:**
  - SafeERC20._callOptionalReturn: SafeERC20._callOptionalReturn(IERC20,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#159-177) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#162-172)
  - Panic.panic: Panic.panic(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Panic.sol#50-56) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Panic.sol#51-55)
  - SafeERC20._callOptionalReturnBool: SafeERC20._callOptionalReturnBool(IERC20,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#187-197) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol#191-195)
  - Math.tryModExp: Math.tryModExp(uint256,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#337-361) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#339-360)
  - Math.tryModExp: Math.tryModExp(bytes,bytes,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#377-399) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#389-398)
  - SafeCast.toUint: SafeCast.toUint(bool) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol#1157-1161) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol#1158-1160)
  - Math.mulDiv: Math.mulDiv(uint256,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#144-223) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#151-154)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#175-182)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#188-197)
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

_Determined via graph-gated Codex investigation (1 graph queries, 335s)._

## req-2-check-rounding::src/LiquidRon.sol: req-2-check-rounding::src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.getTotalRewards, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, Math.average, Math.ceilDiv, Math.invMod, Math.log10, Math.mulDiv, Math.sqrt, Math.tryDiv, Math.tryMul

**Confidence:** MEDIUM

**Mechanism:** Reward and fee calculations round down via integer division, and redemption uses floor rounding with heuristic offsets. No code comments or documentation identify rounding risks or quantify possible error, violating the requirement to document and protect against rounding-based value creation/loss.

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

_Determined via graph-gated Codex investigation (1 graph queries, 206s)._

## req-3-pass-l2::src/LiquidRon.sol: req-3-pass-l2::src/LiquidRon.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** None

**Mechanism:** None

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-timelock-for-privileged-actions::src/LiquidRon.sol: req-3-timelock-for-privileged-actions::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Sensitive owner-controlled operations (fee changes, operator assignment, proxy deployment, pause/unpause) execute immediately without any timelock. No timelock contract is integrated despite a comment acknowledging it could be used. Requirement for delayed execution of sensitive operations is not met.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 227s)._

## req-3-enough-gas::src/LiquidRon.sol: req-3-enough-gas::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** User-facing ERC4626 flows invoke totalAssets(), which loops over staking proxies and all validators. Validators are appended whenever operators touch a new consensus address and are only optionally pruned, so the loop cost grows unbounded. As the sets expand, deposits/withdrawals can exceed block gas with no mitigation or documented constraint, violating the requirement to ensure sufficient gas for growing structures.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 219s)._

## req-3-block-front-running::src/LiquidRon.sol: req-3-block-front-running::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** The vault’s user-facing deposit/withdraw/redeem paths execute immediately against the current price-per-share with no slippage or delay controls. Operators can change totalAssets via harvest/delegate/undelegate right before a user tx, enabling front-running to capture value. Withdrawal requests lock shares but asset amount is based on operator-finalized totals, still manipulable without user safeguards. No ordering-attack mitigation is present.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (0 graph queries, 210s)._

## req-3-block-mev::src/LiquidRon.sol: req-3-block-mev::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Across LiquidRon, no MEV-aware design (deadlines, slippage, sequencing locks) is implemented. Conversions for deposits/withdrawals and epoch redemption rely on mutable totals that block producers or operators can reorder around. Documentation notes fee manipulation risk but provides no mitigation. Requirement demands appropriate MEV protections for susceptible code; none are present.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (0 graph queries, 229s)._

## req-3-protect-governance::src/LiquidRon.sol: req-3-protect-governance::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Governance is entirely centralized in a single owner with no timelock or multisig, and the operator role is unusable due to the onlyOperator check, meaning all operational and parameter controls rest on one key. This design lacks protections against governance takeover or key compromise, violating the requirement.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 271s)._

## req-3-event-on-state-change::src/LiquidRon.sol: req-3-event-on-state-change::src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20.constructor, ERC4626.constructor, Escrow.constructor, LiquidProxy.constructor, LiquidRon.constructor, LiquidRon.deployStakingProxy, LiquidRon.fetchOperatorFee, LiquidRon.setOperatorFee, LiquidRon.slitherConstructorConstantVariables, LiquidRon.updateFeeRecipient, LiquidRon.updateOperator, Panic.slitherConstructorConstantVariables, Pausable.pause, Pausable.unpause, RonHelper.constructor, ValidatorTracker._removeValidator, ValidatorTracker._tryPushValidator

**Confidence:** None

**Mechanism:** None

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

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-document-system::src/LiquidRon.sol: req-3-document-system::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Repository documentation covers system design, roles, and usage, but lacks explicit security assumptions required by the EthTrust requirement.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 132s)._

## req-3-document-threats::src/LiquidRon.sol: req-3-document-threats::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Searched README.md and source files for threat/assumption/attack terms and reviewed README content; found no documented threat models detailing threats, security assumptions, expected responses, or outcomes, so the requirement is not met.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 211s)._

## req-3-annotate::src/LiquidRon.sol: req-3-annotate::src/LiquidRon.sol

**Requirement:** 

**Location(s):** ILiquidProxy.delegateAmount, ILiquidProxy.harvest, ILiquidProxy.harvestAndDelegateRewards, ILiquidProxy.redelegateAmount, ILiquidProxy.undelegateAmount, IRoninValidator.bulkUndelegate, IRoninValidator.claimRewards, IRoninValidator.delegate, IRoninValidator.delegateRewards, IRoninValidator.getManyStakingAmounts, IRoninValidator.getManyStakingTotals, IRoninValidator.getReward, IRoninValidator.getRewards, IRoninValidator.getStakingAmount, IRoninValidator.getStakingTotal, IRoninValidator.redelegate, IRoninValidator.undelegate, IVault.deposit, IWRON.deposit, IWRON.transfer, IWRON.withdraw, Pausable.pause, Pausable.unpause

**Confidence:** None

**Mechanism:** None

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

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-implement-as-documented::src/LiquidRon.sol: req-3-implement-as-documented::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Documentation promises operators can manage staking and finalize withdrawal epochs, but onlyOperator logic requires sender be owner and not marked operator, so all operator-only functions are owner-only. This contradicts documented behavior, violating implement-as-documented.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (0 graph queries, 162s)._

## req-3-access-control::src/LiquidRon.sol: req-3-access-control::src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20.approve, ERC20.transfer, ERC20.transferFrom, ERC4626.deposit, ERC4626.mint, ERC4626.redeem, ERC4626.withdraw, LiquidRon.delegateAmount, LiquidRon.deployStakingProxy, LiquidRon.deposit, LiquidRon.fetchOperatorFee, LiquidRon.finaliseRonRewardsForEpoch, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, LiquidRon.mint, LiquidRon.pruneValidatorList, LiquidRon.redeem, LiquidRon.redelegateAmount, LiquidRon.requestWithdrawal, LiquidRon.setOperatorFee, LiquidRon.updateFeeRecipient, LiquidRon.updateOperator, LiquidRon.withdraw, Ownable.renounceOwnership, Ownable.transferOwnership, Pausable.pause, Pausable.unpause

**Confidence:** HIGH

**Mechanism:** Documentation gives operators and owner staking-control privileges, but onlyOperator is misimplemented to revert for any operator, allowing only a non-operator owner. All staking-control functions are therefore inaccessible to designated operators, violating the documented least-privilege role separation.

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

_Determined via graph-gated Codex investigation (1 graph queries, 135s)._

## req-3-revocable-permisions::src/LiquidRon.sol: req-3-revocable-permisions::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** LiquidRon gates privileged functions with owner-only controls and an operator mapping, but the onlyOperator modifier is flawed and rejects operators, and there is no explicit revocation/transfer mechanism for operators beyond owner rewrites. Ownership transfer exists but operator role lacks a functional revocable/transferable design, so requirement is not met.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 202s)._

## req-3-no-single-admin-eoa::src/LiquidRon.sol: req-3-no-single-admin-eoa::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** All privileged operations are gated by a single Ownable `owner` address; operator functions are also effectively owner-only due to the `onlyOperator` condition. There is no multisig or higher-privileged multisig override, violating the requirement against single-admin EOAs for critical actions.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 249s)._

## req-3-external-calls::src/LiquidRon.sol: req-3-external-calls::src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards

**Confidence:** MEDIUM

**Mechanism:** External calls to proxies are documented as operator-only, but the implemented onlyOperator modifier rejects marked operators and only permits the owner, making the protection incompatible with the documented access assumptions. Requirement fails due to mismatch between documented claim and actual guard on external calls.

**Supporting evidence:**
  - LiquidRon.harvest: external call at node 1 followed by state write at node 2 (CFG-reachable)
  - LiquidRon.harvestAndDelegateRewards: external call at node 2 followed by state write at node 3 (CFG-reachable)

_Determined via graph-gated Codex investigation (1 graph queries, 188s)._

## req-3-consistent-solidity-output::src/LiquidRon.sol: req-3-consistent-solidity-output::src/LiquidRon.sol

**Requirement:** 

**Location(s):** pragma solidity^0.8.20

**Confidence:** None

**Mechanism:** None

**Supporting evidence:**
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-check-new-bugs::src/LiquidRon.sol: req-R-check-new-bugs::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Project still targets solc 0.8.20 and contains no documentation or mitigation addressing compiler security bugs disclosed after Nov 1, 2023; requirement explicitly calls for such a review, so it is not satisfied.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 183s)._

## req-R-use-latest-compiler::src/LiquidRon.sol: req-R-use-latest-compiler::src/LiquidRon.sol

**Requirement:** 

**Location(s):** compiler config

**Confidence:** None

**Mechanism:** None

**Supporting evidence:**
  - compiler config: solc 0.8.20 != caller-supplied latest known stable version 0.8.36 (external, time-anchored reference -- not derived from spec text)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-clean-code::src/LiquidRon.sol: req-R-clean-code::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Readability is reduced by mislabeled/incorrect `onlyOperator` logic that hides actual access behavior and by two differently behaving `redeem` functions sharing a name, making the code harder to understand and reason about.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 118s)._

## req-R-follow-erc-standards::src/LiquidRon.sol: req-R-follow-erc-standards::src/LiquidRon.sol

**Requirement:** 

**Location(s):** IERC1363, IWRON, LiquidRon

**Confidence:** MEDIUM

**Mechanism:** Although LiquidRon inherits ERC4626, its withdraw/redeem functions divert the asset transfer to the vault and pay out native RON instead of delivering the ERC4626 asset to the receiver, violating ERC4626 behavioral expectations. This breaks conformance with the accepted standard.

**Supporting evidence:**
  - IERC1363: resembles ERC20; signature_check_performed=True; interface_mismatches=[]
  - LiquidRon: resembles ERC20; signature_check_performed=True; interface_mismatches=[]
  - IWRON: resembles ERC20; signature_check_performed=True; interface_mismatches=['transfer(address,uint256)']

_Determined via graph-gated Codex investigation (1 graph queries, 355s)._

## req-R-notify-news::src/LiquidRon.sol: req-R-notify-news::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Requirement recommends providing a responsible-disclosure process. Searched primary documentation (README.md, README-sponsor.md) and contract files; no instructions or references to reporting vulnerabilities were found, so the project does not meet the recommendation.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 208s)._

## req-R-fuzzing-in-testing::src/LiquidRon.sol: req-R-fuzzing-in-testing::src/LiquidRon.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testApprove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailBurnInsufficientBalance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadDeadline, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadNonce, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitPastDeadline, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitReplay, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientAllowance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientBalance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferInsufficientBalance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testMetadata, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testPermit, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testTransfer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApprove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnAuthorized, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnMinted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailBurnUnMinted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailMintToZero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailOwnerOfUnminted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnDataWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnDataWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromNotOwner, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromToZero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromUnOwned, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromWrongFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testMetadata, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromApproveAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromSelf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testInvalidDescriptionForProposer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testValidDescriptionForProposer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteAvoidsETHStuck, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchAvoidsETHStuck, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchTamperedValues, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchTamperedValuesZeroReceiver, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteTamperedValues, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testVerifyTamperedValues, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testCloneDeterministicDirty, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testFetchCloneArgs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testPredictDeterministicAddressDirty, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testSymbolicPredictDeterministicAddressSpillage, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testSymbolicPredictDeterministicAddressWithImmutableArgsSpillage, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_start_consecutive_id, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Arrays.t.sol:testSort, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol:testEncode, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol:testEncodeURL, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Create2.t.sol:testSymbolicComputeAddressSpillage, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthShort, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthWithFallback, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRevertLong, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripShort, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripWithFallback, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveArray, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveMappingBytes, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveMappingString, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingAddress, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingAddressDirty, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBoolean, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBooleanDirty, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBytes32, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBytes4, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingInt256, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingInt32, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingUint256, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingUint32, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParse, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseChecksumHex, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseHex, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseSigned, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testTryParseAddressExtendedEnd, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testTryParseHexUintExtendedEnd, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol:testRecover, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol:testVerify, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testCeilDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod17, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod65537, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvModP256, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog10, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog256, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testModExp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testModExpMemory, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDivDomain, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSqrt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSymbolicMinMax, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSymbolicTernary, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testTryModExp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testTryModExpMemory, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testAverage1, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testAverage2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicAbs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMax, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMinMax, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicTernary, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol:testFuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol:testFuzzGt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_fetch_operator_fee, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_deploy_staking_proxy, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_set_operator, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_set_operator_fee, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_fee_recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_operator, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_operator_fee, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_admin_pause, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_escrow_not_vault, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_fee_recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_fetch_fee_non_receiver, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_proxies_not_vault, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_delegate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest_and_delegate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest_duration, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_redelegate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_3days_redelegate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_delegate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_delegate_bad_proxy, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_insufficient_delegate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_redelegate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_undelegate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_undelegate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.t.sol:test_deposit, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.t.sol:test_deposit_no_func_call, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.t.sol:test_withdraw_init

**Confidence:** None

**Mechanism:** None

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testMetadata: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testTransfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testPermit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailBurnInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientAllowance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadNonce: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadDeadline: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitPastDeadline: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitReplay: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testMetadata: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromSelf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailMintToZero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailBurnUnMinted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnMinted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnAuthorized: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromUnOwned: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromWrongFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromToZero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromNotOwner: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnDataWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnDataWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailOwnerOfUnminted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testValidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testInvalidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteAvoidsETHStuck: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchAvoidsETHStuck: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testVerifyTamperedValues: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteTamperedValues: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchTamperedValuesZeroReceiver: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchTamperedValues: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testSymbolicPredictDeterministicAddressSpillage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testSymbolicPredictDeterministicAddressWithImmutableArgsSpillage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testCloneDeterministicDirty: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testPredictDeterministicAddressDirty: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testFetchCloneArgs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_start_consecutive_id: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Arrays.t.sol:testSort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol:testEncode: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol:testEncodeURL: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Create2.t.sol:testSymbolicComputeAddressSpillage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRevertLong: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveArray: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingAddress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBoolean: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBytes32: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBytes4: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingUint256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingUint32: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingInt256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingInt32: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveMappingString: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveMappingBytes: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBooleanDirty: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingAddressDirty: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParse: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseSigned: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseHex: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseChecksumHex: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testTryParseHexUintExtendedEnd: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testTryParseAddressExtendedEnd: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol:testVerify: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol:testRecover: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSymbolicTernary: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSymbolicMinMax: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testCeilDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSqrt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod17: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod65537: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvModP256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog10: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDivDomain: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testModExp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testTryModExp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testModExpMemory: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testTryModExpMemory: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicTernary: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMinMax: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMax: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testAverage1: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testAverage2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicAbs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol:testFuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol:testFuzzGt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_admin_pause: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_fee_recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_operator: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_set_operator: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_operator_fee: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_set_operator_fee: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_deploy_staking_proxy: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_fetch_operator_fee: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_fetch_fee_non_receiver: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_escrow_not_vault: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_proxies_not_vault: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_fee_recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_delegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_delegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_delegate_bad_proxy: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_insufficient_delegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest_duration: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest_and_delegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_3days_redelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_redelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_redelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_undelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_undelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.t.sol:test_deposit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.t.sol:test_deposit_no_func_call: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron/test/LiquidRon.t.sol:test_withdraw_init: Foundry-convention parameterized test function (fuzzed by forge test)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-multisig-threshold::src/LiquidRon.sol: req-R-multisig-threshold::src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** All admin and pause functions rely on OpenZeppelin Ownable single-owner gating; no multisig or threshold is implemented, making privileged actions effectively 1-of-1, contrary to the requirement.

**Supporting evidence:**
  - README.md: # Liquid Ron audit details

- Total Prize Pool: $40,000 in USDC
  - HM awards: $27,900 in USDC
  - QA awards: $1,200 in USDC
  - Judge awards: $3,200 in USDC
  - Validator awards: $2,200 USDC
  - Scout awards: $500 in USDC
  - Mitigation Review: $5,000 USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 28, 2025 20:00 UTC
- Ends February 4, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments:

- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/4naly3er-report.md).

Slither's output can be found [here](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/slither.txt).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

From the Sponsor:
> I am aware that the operator fee changing impacts the total assets calculation in the vault. increasing it will reduce the total, decreasing it will increase the total. I am aware of it and I am ok with the behaviour.
> I am also aware that the operators have a lot of power in how the ron is delegated on the validators. The worst scenario is manipulation of where to put the funds but once again, the behaviour will be to maximise apr and not worry for staking lobbying.

# Overview

**Liquid Ron is a Ronin staking protocol that automates user staking actions.**

Deposit RON, get liquid RON, a token representing your stake in the validation process of the Ronin Network.

Liquid RON stakes and harvests rewards automatically, auto compounding your rewards and ensuring the best yield possible.

## Links

- **Previous audits:** None
- **Documentation:** <https://github.com/OwlOfMoistness/liquid_ron/blob/main/README.md>
- **X/Twitter:** <https://x.com/OwlOfMoistness>
- **Code walk-through:** <https://youtu.be/S7d21f7jTNQ>

---

# Scope

_See [scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/scope.txt)_

### Files in scope

| File   | Logic Contracts | Interfaces | nSLOC | Purpose | Libraries used |
| ------ | --------------- | ---------- | ----- | -----   | ------------ |
| /src/ValidatorTracker.sol | 1| **** | 31 | ||
| /src/RonHelper.sol | 1| 1 | 18 | ||
| /src/Pausable.sol | 1| **** | 16 | |@openzeppelin/access/Ownable.sol|
| /src/LiquidRon.sol | 1| **** | 258 | |@openzeppelin/token/ERC20/extensions/ERC4626.sol<br>@openzeppelin/token/ERC20/IERC20.sol<br>@openzeppelin/utils/math/Math.sol<br>@openzeppelin/access/Ownable.sol|
| /src/LiquidProxy.sol | 1| **** | 48 | ||
| /src/Escrow.sol | 1| 1 | 15 | |@openzeppelin/token/ERC20/IERC20.sol|
| **Totals** | **6** | **2** | **386** | | |

### Files out of scope

_See [out_of_scope.txt](https://github.com/code-423n4/2025-01-liquid-ron/blob/main/out_of_scope.txt)_

| File         |
| ------------ |
| ./script/LiquidRon_saigon.s.sol |
| ./src/interfaces/ILiquidProxy.sol |
| ./src/interfaces/IRoninValidators.sol |
| ./src/mock/MockRonStaking.sol |
| ./src/mock/WrappedRon.sol |
| ./test/LiquidRon.admin.t.sol |
| ./test/LiquidRon.operator.t.sol |
| ./test/LiquidRon.t.sol |
| Totals: 8 |

## Scoping Q &amp; A

### General questions

| Question                                | Answer                       |
| --------------------------------------- | ---------------------------- |
| ERC20 used by the protocol              |       Wrapped RON, a wrapper for the ron native token             |
| Test coverage                           | 98%                      |
| ERC721 used  by the protocol            |          None        |
| ERC777 used by the protocol             |          None         |
| ERC1155 used by the protocol            |          None        |
| Chains the protocol will be deployed on | Other, Ronin chain  |

### External integrations (e.g., Uniswap) behavior in scope

| Question                                                  | Answer |
| --------------------------------------------------------- | ------ |
| Enabling/disabling fees (e.g. Blur disables/enables fees) | No   |
| Pausability (e.g. Uniswap pool gets paused)               |  No   |
| Upgradeability (e.g. Uniswap gets upgraded)               |   No  |

### EIP compliance checklist

N/A

# Additional context

## Main invariants

1. User should only be able to interact with the protocol via standard erc-4626 functions, on top of the custom deposit function, requestWithdrawal and custom redeem function
2. Operators can only direct the flow of assets from and to the proxies and proxies to the staking protocol.
3. Only the owner can deploy new liquid proxies
4. Anyone can prune validator list

## Attack ideas (where to focus for bugs)

The flow of funds is fairly simple.
User <=> vault <=> proxies <=> staking protocol

The flow can never jump from one to another directly.

Concern is making sure funds aren't stuck, that a user cannot withdraw more than intended, and that a user or operators is able to withdraw funds outside of expected flow.

## All trusted roles in the protocol

| Role                                | Description                       |
| --------------------------------------- | ---------------------------- |
| Owner                          | Can set specific parameters in the protocol (update fee recipient, operator fee, update operators)             |
| Operators (and owner)                             | Can manage where the assets will be staked via the set of staking functions provided. They can also finalise a withdrawal request.                     |

## Describe any novel or u
  - LiquidRon.sol (NatSpec): /// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
  - LiquidRon.sol (NatSpec): /// @dev Modifier to restrict access of a function to an operator or owner
  - LiquidRon.sol (NatSpec): /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
  - LiquidRon.sol (NatSpec): /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
  - LiquidRon.sol (NatSpec): /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
  - LiquidRon.sol (NatSpec): /// @dev Deploys a new staking proxy contract to granulate stake amounts
  - LiquidRon.sol (NatSpec): /// @dev Withdraws the operator fee to the fee recipient
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
  - LiquidRon.sol (NatSpec): /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
  - LiquidRon.sol (NatSpec): /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
  - LiquidRon.sol (NatSpec): /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
  - LiquidRon.sol (NatSpec): /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /// @param _proxyIndex The index of the staking proxy to undelegate from
    /// @param _amounts The amounts of RON tokens to undelegate
    /// @param _consensusAddrs The consensus addresses to undelegate from
  - LiquidRon.sol (NatSpec): /// @dev Prunes the validator list by removing validators with no rewards and no staking amounts
    /// To remove redundant reads if a consensus address is not used anymore or has renounced
  - LiquidRon.sol (NatSpec): ////////////////////////////////////
    /// WITHDRAWAL PROCESS FUNCTIONS ///
    ////////////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Finalises the RON rewards for the current epoch
    ///		 This function is called when users have called the requestWithdrawal, usually when the amount
    ///      of assets in the contract is not enough to cover all the withdrawals
  - LiquidRon.sol (NatSpec): //////////////////////
    /// VIEW FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of RON tokens staked in each staking proxy for each consensus address within them
    ///	     It is worth mentionning that the return value of this call may change based on the operator fee.
    ///      It could be possible to put the operator fee update behind a timelock to prevent manipulation of the amount returned
    ///      But the problem still persists even to a lesser degree. Overall users do not suffer much from this.
    ///		 Clear communication on when the fee will change will allow people plenty of time to decide whether to exit or not
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets in the contract
  - LiquidRon.sol (NatSpec): /// @dev Gets the total amount of assets the vault controls
  - LiquidRon.sol (NatSpec): //////////////////////
    /// USER FUNCTIONS ///
    //////////////////////
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 withdraw function
  - LiquidRon.sol (NatSpec): /// @dev We override to prevent wrong event emission and send native ron back to user
    ///		 Acts as the ERC4626 redeem function
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @dev We override to add the pause check
  - LiquidRon.sol (NatSpec): /// @notice Deposits RON tokens into the contract
    ///			We send the native token to the escrow to prevent wrong share minting amounts
  - LiquidRon.sol (NatSpec): /// @notice Requests a withdrawal of RON tokens
    ///         Called ideally if the amount of assets exceeds the vault's balance
    ///			Users should favour using withdraw or redeem functions to avoid the need of this function
    /// @param _shares The amount of shares (LRON) to burn
  - LiquidRon.sol (NatSpec): /// @notice Redeems RON tokens for assets for a specific withdrawal epoch
    ///			Callable only once per epoch
    /// @param _epoch The epoch to redeem the RON tokens for
  - LiquidRon.sol (NatSpec): ///////////////////////////////
    /// INTERNAL VIEW FUNCTIONS ///
    ///////////////////////////////
  - LiquidRon.sol (NatSpec): /// @dev Gets the total rewards in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get rewards from
    /// @return The total rewards in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Gets the total staked amount in a staking proxy
    /// @param _proxyIndex The index of the staking proxy
    /// @param _consensusAddrs The consensus addresses to get staked amounts from
    /// @return The total staked amount in the staking proxy
  - LiquidRon.sol (NatSpec): /// @dev Converts shares to assets. Function used on redemption of LRON tokens based on submitted price per share
    /// @param _shares The amount of shares to convert
    /// @param _totalAssets The total assets in the contract at time of epoch finalisation
    /// @param _totalShares The total shares in the contract at time of epoch finalisation
    /// @return The amount of assets the shares are worth
  - LiquidRon.sol (NatSpec): /// @dev Checks if a user can receive RON tokens
    /// @param _user The user to check
  - LiquidRon.sol (NatSpec): /// @dev We override to remove the event emission to prevent wrong data emission and use `asset()` since _asset is private
    ///      The receiver would be the vault with the new withdrawal flow. The Withdraw event has been moved in the withdraw and redeem functions
  - LiquidRon.sol (NatSpec): /// @dev Allows users to send RON tokens directly to the contract as if calling the deposit function
    ///      Lets the transfer go though if sender is wrapped RON
  - LiquidRon.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import {IRoninValidator} from "./interfaces/IRoninValidators.sol";
import {ILiquidProxy} from "./interfaces/ILiquidProxy.sol";
import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/utils/math/Math.sol";
import {Ownable} from "@openzeppelin/access/Ownable.sol";
import {Pausable} from "./Pausable.sol";
import {RonHelper} from "./RonHelper.sol";
import {Escrow} from "./Escrow.sol";
import {LiquidProxy} from "./LiquidProxy.sol";
import {ValidatorTracker} from "./ValidatorTracker.sol";

enum WithdrawalStatus {
    STANDBY,
    FINALISED
}

/// @title A contract to manage the staking and withdrawal of RON tokens in exchange of an interest bearing token
/// @author OwlOfMoistness
contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker {
    using Math for uint256;

    error ErrRequestFulfilled();
    error ErrWithdrawalProcessNotFinalised();
    error ErrInvalidOperator();
    error ErrBadProxy();
    error ErrCannotReceiveRon();
    error ErrNotZero();
    error ErrNotFeeRecipient();

    struct WithdrawalRequest {
        bool fulfilled;
        uint256 shares;
    }

    struct LockedPricePerShare {
        uint256 shareSupply;
        uint256 assetSupply;
    }

    uint256 public constant BIPS = 10_000;

    mapping(address => bool) public operator;
    mapping(uint256 => LockedPricePerShare) public lockedPricePerSharePerEpoch;
    mapping(uint256 => mapping(address => WithdrawalRequest)) public withdrawalRequestsPerEpoch;
    mapping(uint256 => uint256) public lockedSharesPerEpoch;
    mapping(uint256 => WithdrawalStatus) public statusPerEpoch;

    mapping(uint256 => address) public stakingProxies;
    uint256 public stakingProxyCount;

    address public escrow;
    address public roninStaking;
    address public feeRecipient;

    uint256 public withdrawalEpoch;
    uint256 public operatorFee;
    uint256 public operatorFeeAmount;

    event WithdrawalRequested(address indexed requester, uint256 indexed epoch, uint256 shareAmount);
    event WithdrawalClaimed(address indexed claimer, uint256 indexed epoch, uint256 shareAmount, uint256 assetAmount);
    event WithdrawalProcessFinalised(uint256 indexed epoch, uint256 shares, uint256 assets);
    event Harvest(uint256 indexed proxyIndex, uint256 amount);

    constructor(
        address _roninStaking,
        address _wron,
        uint256 _operatorFee,
        address _feeRecipient,
        string memory _name,
        string memory _symbol
    ) ERC4626(IERC20(_wron)) ERC20(_name, _symbol) RonHelper(_wron) Ownable(msg.sender) {
        roninStaking = _roninStaking;
        escrow = address(new Escrow(_wron));
        operatorFee = _operatorFee;
        feeRecipient = _feeRecipient;
        IERC20(_wron).approve(address(this), type(uint256).max);
    }

    /// @dev Modifier to restrict access of a function to an operator or owner
    modifier onlyOperator() {
        if (msg.sender != owner() || operator[msg.sender]) revert ErrInvalidOperator();
        _;
    }

    /// @dev Updates the fee recipient address
    /// @param _feeRecipient The new fee recipient address
    function updateFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }

    /// @dev Updates the operator status of an address
    /// @param _operator The address to update the operator status of
    /// @param _value The new operator status of the address
    function updateOperator(address _operator, bool _value) external onlyOwner {
        operator[_operator] = _value;
    }

    /// @dev Sets the operator fee for the contract
    /// @param _fee The new operator fee
    function setOperatorFee(uint256 _fee) external onlyOwner {
        require(_fee < 1000, "LiquidRon: Invalid fee");
        operatorFee = _fee;
    }

    /// @dev Deploys a new staking proxy contract to granulate stake amounts
    function deployStakingProxy() external onlyOwner {
        stakingProxies[stakingProxyCount++] = address(new LiquidProxy(roninStaking, asset(), address(this)));
    }

    /// @dev Withdraws the operator fee to the fee recipient
    function fetchOperatorFee() external {
        if (msg.sender != feeRecipient) revert ErrNotFeeRecipient();
        uint256 amount = operatorFeeAmount;
        operatorFeeAmount = 0;
        _withdrawRONTo(feeRecipient, amount);
    }

    ///////////////////////////////
    /// STAKING PROXY FUNCTIONS ///
    ///////////////////////////////

    /// @dev Harvests rewards from a staking proxy
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    function harvest(uint256 _proxyIndex, address[] calldata _consensusAddrs) external onlyOperator whenNotPaused {
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvest(_consensusAddrs);
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Harvests rewards from a staking proxy and delegates them to a new consensus address
    /// @param _proxyIndex The index of the staking proxy to harvest from
    /// @param _consensusAddrs The consensus addresses to claim tokens from
    /// @param _consensusAddrDst The consensus address to delegate the rewards to
    function harvestAndDelegateRewards(
        uint256 _proxyIndex,
        address[] calldata _consensusAddrs,
        address _consensusAddrDst
    ) external onlyOperator whenNotPaused {
        _tryPushValidator(_consensusAddrDst);
        uint256 harvestedAmount = ILiquidProxy(stakingProxies[_proxyIndex]).harvestAndDelegateRewards(
            _consensusAddrs,
            _consensusAddrDst
        );
        operatorFeeAmount += (harvestedAmount * operatorFee) / BIPS;
        emit Harvest(_proxyIndex, harvestedAmount);
    }

    /// @dev Delegates specific amounts of RON tokens to specific consensus addresses
    /// @param _proxyIndex The index of the staking proxy to delegate from
    /// @param _amounts The amounts of RON tokens to delegate
    /// @param _consensusAddrs The consensus addresses to delegate to
    function delegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrs
    ) external onlyOperator whenNotPaused {
        address stakingProxy = stakingProxies[_proxyIndex];
        uint256 total;

        if (stakingProxy == address(0)) revert ErrBadProxy();
        for (uint256 i = 0; i < _amounts.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrs[i]);
            total += _amounts[i];
        }
        _withdrawRONTo(stakingProxy, total);
        ILiquidProxy(stakingProxy).delegateAmount(_amounts, _consensusAddrs);
    }

    /// @dev Redelegates specific amounts of RON tokens from consensus addresses to others
    /// @param _proxyIndex The index of the staking proxy to redelegate from
    /// @param _amounts The amounts of RON tokens to redelegate
    /// @param _consensusAddrsSrc The consensus addresses to redelegate from
    /// @param _consensusAddrsDst The consensus addresses to redelegate to
    function redelegateAmount(
        uint256 _proxyIndex,
        uint256[] calldata _amounts,
        address[] calldata _consensusAddrsSrc,
        address[] calldata _consensusAddrsDst
    ) external onlyOperator whenNotPaused {
        ILiquidProxy(stakingProxies[_proxyIndex]).redelegateAmount(_amounts, _consensusAddrsSrc, _consensusAddrsDst);

        for (uint256 i = 0; i < _consensusAddrsSrc.length; i++) {
            if (_amounts[i] == 0) revert ErrNotZero();
            _tryPushValidator(_consensusAddrsDst[i]);
        }
    }

    /// @dev Undelegates specific amounts of RON tokens from consensus addresses
    /
  - 2025-01-liquid-ron: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 254s)._

## gp-accepted-standard__erc-20__erc20-callers-must-handle-false-return::src/LiquidRon.sol: gp-accepted-standard__erc-20__erc20-callers-must-handle-false-return::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-20 (Token Standard), version Final (eip-20), section Methods (notes).
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: Callers of transfer/transferFrom/approve MUST handle a `false` returned from `returns (bool success)` rather than assuming success.
Affected interface/function(s): transfer, transferFrom, approve
Source: https://eips.ethereum.org/EIPS/eip-20 (local pinned snapshot, hash c33aae40a9d54b0d...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** ERC20 methods are invoked via IERC20 without using SafeERC20 or checking returned bool for approve and transferFrom, violating the requirement to handle false returns.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-20 clause erc20-callers-must-handle-false-return (MUST): Callers of transfer/transferFrom/approve MUST handle a `false` returned from `returns (bool success)` rather than assuming success. | Applicability: parent standard ERC-20 is applicable (contracts: ['LiquidRon']) and this clause's target(s) ['transfer', 'transferFrom', 'approve'] are present with no unresolved activation condition

_Determined via graph-gated Codex investigation (1 graph queries, 349s)._

## gp-accepted-standard__erc-20__erc20-callers-must-not-assume-false-never-returned::src/LiquidRon.sol: gp-accepted-standard__erc-20__erc20-callers-must-not-assume-false-never-returned::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-20 (Token Standard), version Final (eip-20), section Methods (notes).
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST_NOT.
Obligation: Callers MUST NOT assume that `false` is never returned by transfer/transferFrom/approve.
Affected interface/function(s): transfer, transferFrom, approve
Source: https://eips.ethereum.org/EIPS/eip-20 (local pinned snapshot, hash 747fef9c54ce7ca9...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** ERC20 methods in LiquidRon and Escrow are invoked without checking their boolean return values, directly assuming success; this violates the ERC-20 note that callers must not assume these functions never return false.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-20 clause erc20-callers-must-not-assume-false-never-returned (MUST_NOT): Callers MUST NOT assume that `false` is never returned by transfer/transferFrom/approve. | Applicability: parent standard ERC-20 is applicable (contracts: ['LiquidRon']) and this clause's target(s) ['transfer', 'transferFrom', 'approve'] are present with no unresolved activation condition

_Determined via graph-gated Codex investigation (1 graph queries, 247s)._

## gp-accepted-standard__erc-4626__erc4626-totalassets-must-include-fees::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-totalassets-must-include-fees::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:totalAssets.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: totalAssets() MUST be inclusive of any fees that are charged against assets in the Vault -- amounts owed to a third party (e.g. an accrued operator/management fee) that are still held in the Vault's asset balance are still part of totalAssets() until actually paid out.
Affected interface/function(s): totalAssets
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash 0e230f9bb1bb4ab3...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** totalAssets relies on getTotalRewards which subtracts operator fees before adding rewards to the total, causing unpaid fees still in vault custody to be omitted and violating ERC-4626’s requirement to include such fees until paid.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-totalassets-must-include-fees (MUST): totalAssets() MUST be inclusive of any fees that are charged against assets in the Vault -- amounts owed to a third party (e.g. an accrued operator/management fee) that are still held in the Vault's asset balance are still part of totalAssets() until actually paid out. | Applicability: parent standard ERC-4626 is applicable (contracts: ['LiquidRon']) and this clause's target(s) ['totalAssets'] are present with no unresolved activation condition

_Determined via graph-gated Codex investigation (1 graph queries, 204s)._

## gp-accepted-standard__erc-4626__erc4626-totalassets-must-not-revert::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-totalassets-must-not-revert::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:totalAssets.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST_NOT.
Obligation: totalAssets() MUST NOT revert.
Affected interface/function(s): totalAssets
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash b5f6aa3d1060450a...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** LiquidRon.totalAssets aggregates staking proxies and rewards by calling external staking contract view functions without safeguards; any revert bubbles up, violating ERC-4626 requirement that totalAssets must not revert.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-totalassets-must-not-revert (MUST_NOT): totalAssets() MUST NOT revert. | Applicability: parent standard ERC-4626 is applicable (contracts: ['LiquidRon']) and this clause's target(s) ['totalAssets'] are present with no unresolved activation condition

_Determined via graph-gated Codex investigation (1 graph queries, 318s)._

## gp-accepted-standard__erc-4626__erc4626-converttoshares-must-not-include-fees::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-converttoshares-must-not-include-fees::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:convertToShares.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST_NOT.
Obligation: convertToShares() MUST NOT be inclusive of any fees that are charged against assets in the Vault.
Affected interface/function(s): convertToShares
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash bcbc1ae58baac7fd...)

**Location(s):** LiquidRon

**Confidence:** MEDIUM

**Mechanism:** convertToShares relies on totalAssets, which LiquidRon overrides to exclude operator fees via getTotalRewards subtraction. This makes convertToShares’ result inclusive of fees charged against assets, violating the MUST_NOT clause.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-converttoshares-must-not-include-fees (MUST_NOT): convertToShares() MUST NOT be inclusive of any fees that are charged against assets in the Vault. | Applicability: parent standard ERC-4626 is applicable (contracts: ['LiquidRon']) and this clause's target(s) ['convertToShares'] are present with no unresolved activation condition

_Determined via graph-gated Codex investigation (1 graph queries, 203s)._

## gp-accepted-standard__erc-4626__erc4626-converttoshares-must-not-revert-unless-overflow::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-converttoshares-must-not-revert-unless-overflow::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:convertToShares.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST_NOT.
Obligation: convertToShares() MUST NOT revert.
Exceptions (this obligation does NOT apply when): integer overflow caused by an unreasonably large input
Affected interface/function(s): convertToShares
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash 302558cb27b21301...)

**Location(s):** LiquidRon

**Confidence:** MEDIUM

**Mechanism:** convertToShares is inherited from OpenZeppelin ERC4626. In LiquidRon, it relies on a totalAssets override that performs external Ronin validator calls. Any failure in those external view calls will revert convertToShares, introducing revert cases unrelated to overflow, violating the MUST NOT revert requirement.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-converttoshares-must-not-revert-unless-overflow (MUST_NOT): convertToShares() MUST NOT revert. | Applicability: parent standard ERC-4626 is applicable (contracts: ['LiquidRon']) and this clause's target(s) ['convertToShares'] are present with no unresolved activation condition

_Determined via graph-gated Codex investigation (1 graph queries, 303s)._

## gp-accepted-standard__erc-4626__erc4626-converttoassets-must-not-include-fees::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-converttoassets-must-not-include-fees::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:convertToAssets.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST_NOT.
Obligation: convertToAssets() MUST NOT be inclusive of any fees that are charged against assets in the Vault.
Affected interface/function(s): convertToAssets
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash bcbc1ae58baac7fd...)

**Location(s):** LiquidRon

**Confidence:** MEDIUM

**Mechanism:** LiquidRon inherits OZ convertToAssets, which uses totalAssets. LiquidRon overrides totalAssets to subtract operator fees from rewards (getTotalRewards returns rewards minus fee). Thus convertToAssets uses a fee-reduced asset total, making it inclusive of the operator fee, violating the requirement that convertToAssets must exclude any fees.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-converttoassets-must-not-include-fees (MUST_NOT): convertToAssets() MUST NOT be inclusive of any fees that are charged against assets in the Vault. | Applicability: parent standard ERC-4626 is applicable (contracts: ['LiquidRon']) and this clause's target(s) ['convertToAssets'] are present with no unresolved activation condition

_Determined via graph-gated Codex investigation (1 graph queries, 308s)._

## gp-accepted-standard__erc-4626__erc4626-maxdeposit-must-not-overestimate::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-maxdeposit-must-not-overestimate::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:maxDeposit.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: maxDeposit() MUST return the maximum amount that the corresponding action would allow (not higher than the actual accepted maximum; MUST underestimate rather than overestimate) and MUST NOT rely on the caller's own balance of the underlying asset.
Conditions (this obligation applies ONLY when these hold, per the source spec -- verify against the real repository, do not assume): assumes the user has infinite assets
Affected interface/function(s): maxDeposit
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash f951e1835d3683ea...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** Because LiquidRon does not override maxDeposit, it always returns an unlimited value. However, deposits are blocked when paused, making the actual permissible deposit 0 in that state. maxDeposit therefore overestimates the true limit, violating the ERC-4626 requirement to not overestimate the maximum amount.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-maxdeposit-must-not-overestimate (MUST): maxDeposit() MUST return the maximum amount that the corresponding action would allow (not higher than the actual accepted maximum; MUST underestimate rather than overestimate) and MUST NOT rely on the caller's own balance of the underlying asset. | Applicability: clause has activation condition(s) ['assumes the user has infinite assets'] that cannot be mechanically evaluated from contract structure alone -- routed to agent investigation to resolve from real repository content, not silently assumed either way

_Determined via graph-gated Codex investigation (1 graph queries, 227s)._

## gp-accepted-standard__erc-4626__erc4626-maxdeposit-must-factor-in-limits::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-maxdeposit-must-factor-in-limits::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:maxDeposit.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: maxDeposit() MUST factor in both global and user-specific limits; MUST return 0 if the corresponding action is entirely disabled (even temporarily).
Conditions (this obligation applies ONLY when these hold, per the source spec -- verify against the real repository, do not assume): the corresponding action (deposits) is entirely disabled, even temporarily
Affected interface/function(s): maxDeposit
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash f2a676602619cbf4...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** LiquidRon is an ERC4626 vault that pauses deposits via the whenNotPaused modifier, disabling deposits when paused. However, it does not override maxDeposit, so the inherited ERC4626 implementation always returns the maximum uint256 and does not account for the paused state or any user/global limits. Consequently, when deposits are disabled, maxDeposit does not return 0 as required.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-maxdeposit-must-factor-in-limits (MUST): maxDeposit() MUST factor in both global and user-specific limits; MUST return 0 if the corresponding action is entirely disabled (even temporarily). | Applicability: clause has activation condition(s) ['the corresponding action (deposits) is entirely disabled, even temporarily'] that cannot be mechanically evaluated from contract structure alone -- routed to agent investigation to resolve from real repository content, not silently assumed either way

_Determined via graph-gated Codex investigation (1 graph queries, 246s)._

## gp-accepted-standard__erc-4626__erc4626-maxmint-must-not-overestimate::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-maxmint-must-not-overestimate::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:maxMint.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: maxMint() MUST return the maximum amount that the corresponding action would allow (not higher than the actual accepted maximum; MUST underestimate rather than overestimate) and MUST NOT rely on the caller's own balance of the underlying asset.
Conditions (this obligation applies ONLY when these hold, per the source spec -- verify against the real repository, do not assume): assumes the user has infinite assets
Affected interface/function(s): maxMint
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash f951e1835d3683ea...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** LiquidRon inherits OZ ERC4626 maxMint which always returns the maximum uint256. Minting is gated by whenNotPaused, so when the vault is paused maxMint overestimates the actual allowable mint amount (should be zero). This violates ERC-4626’s requirement to not overestimate the action’s maximum.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-maxmint-must-not-overestimate (MUST): maxMint() MUST return the maximum amount that the corresponding action would allow (not higher than the actual accepted maximum; MUST underestimate rather than overestimate) and MUST NOT rely on the caller's own balance of the underlying asset. | Applicability: clause has activation condition(s) ['assumes the user has infinite assets'] that cannot be mechanically evaluated from contract structure alone -- routed to agent investigation to resolve from real repository content, not silently assumed either way

_Determined via graph-gated Codex investigation (1 graph queries, 346s)._

## gp-accepted-standard__erc-4626__erc4626-maxmint-must-factor-in-limits::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-maxmint-must-factor-in-limits::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:maxMint.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: maxMint() MUST factor in both global and user-specific limits; MUST return 0 if the corresponding action is entirely disabled (even temporarily).
Conditions (this obligation applies ONLY when these hold, per the source spec -- verify against the real repository, do not assume): the corresponding action (mints) is entirely disabled, even temporarily
Affected interface/function(s): maxMint
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash f2a676602619cbf4...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** LiquidRon inherits ERC4626.maxMint which always returns uint256.max. The contract pauses mint/deposit via whenNotPaused, disabling minting, but maxMint remains unlimited and does not return 0 or reflect any limits. Therefore maxMint fails to account for disabled state and user/global limits.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-maxmint-must-factor-in-limits (MUST): maxMint() MUST factor in both global and user-specific limits; MUST return 0 if the corresponding action is entirely disabled (even temporarily). | Applicability: clause has activation condition(s) ['the corresponding action (mints) is entirely disabled, even temporarily'] that cannot be mechanically evaluated from contract structure alone -- routed to agent investigation to resolve from real repository content, not silently assumed either way

_Determined via graph-gated Codex investigation (1 graph queries, 233s)._

## gp-accepted-standard__erc-4626__erc4626-maxwithdraw-must-factor-in-limits::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-maxwithdraw-must-factor-in-limits::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:maxWithdraw.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: maxWithdraw() MUST factor in both global and user-specific limits; MUST return 0 if the corresponding action is entirely disabled (even temporarily).
Conditions (this obligation applies ONLY when these hold, per the source spec -- verify against the real repository, do not assume): the corresponding action (withdrawals) is entirely disabled, even temporarily
Affected interface/function(s): maxWithdraw
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash f2a676602619cbf4...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** LiquidRon relies on Pausable to block withdrawals, but maxWithdraw is inherited from OZ and ignores pause or other limits, returning full convertible assets even when withdrawals are disabled. Requirement demands maxWithdraw factor in global/user limits and return 0 when action is disabled. This behavior violates the obligation.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-maxwithdraw-must-factor-in-limits (MUST): maxWithdraw() MUST factor in both global and user-specific limits; MUST return 0 if the corresponding action is entirely disabled (even temporarily). | Applicability: clause has activation condition(s) ['the corresponding action (withdrawals) is entirely disabled, even temporarily'] that cannot be mechanically evaluated from contract structure alone -- routed to agent investigation to resolve from real repository content, not silently assumed either way

_Determined via graph-gated Codex investigation (0 graph queries, 436s)._

## gp-accepted-standard__erc-4626__erc4626-maxredeem-must-not-overestimate::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-maxredeem-must-not-overestimate::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:maxRedeem.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: maxRedeem() MUST return the maximum amount that the corresponding action would allow (not higher than the actual accepted maximum; MUST underestimate rather than overestimate) and MUST NOT rely on the caller's own balance of the underlying asset.
Conditions (this obligation applies ONLY when these hold, per the source spec -- verify against the real repository, do not assume): assumes the user has infinite assets
Affected interface/function(s): maxRedeem
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash f951e1835d3683ea...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** The contract is pausable; when paused, redeems/withdraws revert, so the maximum permitted redemption is zero. LiquidRon does not override ERC4626’s maxRedeem, which always returns the caller’s share balance and ignores pause state, thus overestimating the allowed amount and violating ERC-4626’s requirement that maxRedeem must not exceed the actual accepted maximum.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-maxredeem-must-not-overestimate (MUST): maxRedeem() MUST return the maximum amount that the corresponding action would allow (not higher than the actual accepted maximum; MUST underestimate rather than overestimate) and MUST NOT rely on the caller's own balance of the underlying asset. | Applicability: clause has activation condition(s) ['assumes the user has infinite assets'] that cannot be mechanically evaluated from contract structure alone -- routed to agent investigation to resolve from real repository content, not silently assumed either way

_Determined via graph-gated Codex investigation (1 graph queries, 229s)._

## gp-accepted-standard__erc-4626__erc4626-maxredeem-must-factor-in-limits::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-maxredeem-must-factor-in-limits::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:maxRedeem.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: maxRedeem() MUST factor in both global and user-specific limits; MUST return 0 if the corresponding action is entirely disabled (even temporarily).
Conditions (this obligation applies ONLY when these hold, per the source spec -- verify against the real repository, do not assume): the corresponding action (redemption) is entirely disabled, even temporarily
Affected interface/function(s): maxRedeem
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash f2a676602619cbf4...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** LiquidRon inherits ERC4626 without overriding maxRedeem, so the function always returns the caller’s share balance. The contract disables redemption via whenNotPaused on withdraw/redeem, but maxRedeem does not factor this global disablement and would return a nonzero value during pauses. This violates the requirement that maxRedeem must return 0 when redemption is disabled and account for global limits.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-maxredeem-must-factor-in-limits (MUST): maxRedeem() MUST factor in both global and user-specific limits; MUST return 0 if the corresponding action is entirely disabled (even temporarily). | Applicability: clause has activation condition(s) ['the corresponding action (redemption) is entirely disabled, even temporarily'] that cannot be mechanically evaluated from contract structure alone -- routed to agent investigation to resolve from real repository content, not silently assumed either way

_Determined via graph-gated Codex investigation (1 graph queries, 203s)._

## gp-accepted-standard__erc-4626__erc4626-previewdeposit-must-include-fees::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-previewdeposit-must-include-fees::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:previewDeposit.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: previewDeposit() MUST be inclusive of deposit fees.
Affected interface/function(s): previewDeposit
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash 82de479addb213b7...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** LiquidRon relies on OpenZeppelin ERC4626.previewDeposit with no overrides or deposit-fee adjustments. The contract has no deposit fee mechanism; only operator fees on rewards. Thus previewDeposit cannot include deposit fees, violating the requirement that previewDeposit be fee-inclusive.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-previewdeposit-must-include-fees (MUST): previewDeposit() MUST be inclusive of deposit fees. | Applicability: parent standard ERC-4626 is applicable (contracts: ['LiquidRon']) and this clause's target(s) ['previewDeposit'] are present with no unresolved activation condition

_Determined via graph-gated Codex investigation (1 graph queries, 325s)._

## gp-accepted-standard__erc-4626__erc4626-previewwithdraw-must-include-fees::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-previewwithdraw-must-include-fees::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:previewWithdraw.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MUST.
Obligation: previewWithdraw() MUST be inclusive of withdrawal fees.
Affected interface/function(s): previewWithdraw
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash e467fbcc774c1eb6...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** LiquidRon inherits ERC4626 and does not override previewWithdraw; the inherited function performs a simple asset-to-share conversion without fee handling. The contract implements only an operator fee on rewards, with no withdrawal fee mechanism. Therefore previewWithdraw is not inclusive of withdrawal fees, violating the ERC-4626 requirement.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-previewwithdraw-must-include-fees (MUST): previewWithdraw() MUST be inclusive of withdrawal fees. | Applicability: parent standard ERC-4626 is applicable (contracts: ['LiquidRon']) and this clause's target(s) ['previewWithdraw'] are present with no unresolved activation condition

_Determined via graph-gated Codex investigation (1 graph queries, 256s)._

## gp-accepted-standard__erc-4626__erc4626-redeem-may-support-preexisting-shares-flow::src/LiquidRon.sol: gp-accepted-standard__erc-4626__erc4626-redeem-may-support-preexisting-shares-flow::src/LiquidRon.sol

**Requirement:** [EXTERNAL_STANDARD_DERIVED] ERC ERC-4626 (Tokenized Vaults), version Final (eip-4626, requires EIP-20 + optionally EIP-2612), section Methods:redeem.
Parent EthTrust requirement: req-R-follow-erc-standards ([GP] Follow Accepted ERC Standards).
Normative strength: MAY.
Obligation: redeem() MAY support an additional flow where shares are already transferred to the Vault before execution and accounted for during redeem.
Conditions (this obligation applies ONLY when these hold, per the source spec -- verify against the real repository, do not assume): shares are transferred to the Vault contract before execution
Affected interface/function(s): redeem
Source: https://eips.ethereum.org/EIPS/eip-4626 (local pinned snapshot, hash d1d7b4918bed60e9...)

**Location(s):** LiquidRon

**Confidence:** HIGH

**Mechanism:** The ERC-4626 redeem override delegates to OpenZeppelin’s redeem which enforces share ownership/allowance and burns shares in-call, assuming shares are moved during execution. There is no alternate logic to recognize shares pre-sent to the vault. Thus the optional pre-transferred-share redeem flow is not supported.

**Supporting evidence:**
  - LiquidRon: Generated from ERC-4626 clause erc4626-redeem-may-support-preexisting-shares-flow (MAY): redeem() MAY support an additional flow where shares are already transferred to the Vault before execution and accounted for during redeem. | Applicability: clause has activation condition(s) ['shares are transferred to the Vault contract before execution'] that cannot be mechanically evaluated from contract structure alone -- routed to agent investigation to resolve from real repository content, not silently assumed either way

_Determined via graph-gated Codex investigation (1 graph queries, 217s)._
