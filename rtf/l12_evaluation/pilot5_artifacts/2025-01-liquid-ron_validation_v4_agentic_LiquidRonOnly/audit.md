# Security Audit Report: 2025-01-liquid-ron

Findings below were produced by the RTF (Requirement Translation Framework) pipeline: EthTrust requirement routing, deterministic evidence collection, bounded LLM judgment, and (where the bounded judgment was inconclusive, insufficient, or low-confidence) graph-gated Codex investigation.

## req-1-no-hashing-consecutive-variable-length-args::./src/LiquidRon.sol: req-1-no-hashing-consecutive-variable-length-args::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** Math.tryModExp

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - Math.tryModExp: abi.encodePacked() with 2+ consecutive dynamic-type args (taint-independent)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-pass-l1::./src/LiquidRon.sol: req-2-pass-l1::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-external-calls::./src/LiquidRon.sol: req-2-external-calls::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards

**Confidence:** HIGH

**Mechanism:** Harvest functions invoke staking proxies whose logic calls external Ronin staking and WRON token contracts not part of the tested set; calls are not restricted to in-repo code nor protected with CEI-equivalent reentrancy safeguards, violating the requirement.

**Supporting evidence:**
  - LiquidRon.harvest: external call at node 1 followed by state write at node 2 (CFG-reachable)
  - LiquidRon.harvestAndDelegateRewards: external call at node 2 followed by state write at node 3 (CFG-reachable)

_Determined via graph-gated Codex investigation (1 graph queries, 131s)._

## req-2-documented::./src/LiquidRon.sol: req-2-documented::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20._spendAllowance, ERC20._update, ERC4626._convertToAssets, ERC4626._convertToShares, ERC4626._deposit, ERC4626._tryGetAssetDecimals, ERC4626._withdraw, ERC4626.totalAssets, Escrow.constructor, Escrow.deposit, LiquidProxy.delegateAmount, LiquidProxy.harvest, LiquidProxy.harvestAndDelegateRewards, LiquidProxy.redelegateAmount, LiquidProxy.undelegateAmount, LiquidRon._checkUserCanReceiveRon, LiquidRon._convertToAssets, LiquidRon._getTotalRewardsInProxy, LiquidRon._getTotalStakedInProxy, LiquidRon._withdraw, LiquidRon.constructor, LiquidRon.delegateAmount, LiquidRon.deposit, LiquidRon.getAssetsInVault, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, LiquidRon.pruneValidatorList, LiquidRon.receive, LiquidRon.redeem, LiquidRon.redelegateAmount, LiquidRon.undelegateAmount, Math.ceilDiv, Math.invMod, Math.invModPrime, Math.log10, Math.log2, Math.log256, Math.modExp, Math.mulDiv, Math.sqrt, Math.ternary, Math.tryAdd, Math.tryModExp, Math.tryMul, Math.trySub, Panic.panic, RonHelper._depositRONTo, RonHelper._withdrawRONTo, SafeCast.toUint, SafeERC20._callOptionalReturn, SafeERC20._callOptionalReturnBool, SafeERC20.approveAndCallRelaxed, SafeERC20.safeDecreaseAllowance, SafeERC20.safeIncreaseAllowance, SafeERC20.transferAndCallRelaxed, SafeERC20.transferFromAndCallRelaxed

**Confidence:** MEDIUM

**Mechanism:** Requirement demands documentation of the need for each special construct, including external calls. In Escrow.constructor the code approves an external ERC20 spender but provides no comment or NatSpec explaining why. Other external calls (e.g., LiquidProxy.harvest to the staking contract) likewise lack justification beyond generic function descriptions. Absence of explicit documentation for these external interactions violates the requirement.

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

_Determined via graph-gated Codex investigation (1 graph queries, 309s)._

## req-2-check-rounding::./src/LiquidRon.sol: req-2-check-rounding::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.getTotalRewards, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, Math.average, Math.ceilDiv, Math.invMod, Math.log10, Math.mulDiv, Math.sqrt, Math.tryDiv, Math.tryMul

**Confidence:** MEDIUM

**Mechanism:** Reward and conversion calculations rely on integer division with implicit floor bias; potential lost remainder and biased conversion are not documented or bounded, and there is no mitigation against exploitation through repeated operations. Requirement demands explicit identification/documentation and protection against rounding-induced value changes, which are absent.

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

_Determined via graph-gated Codex investigation (1 graph queries, 254s)._

## req-3-pass-l2::./src/LiquidRon.sol: req-3-pass-l2::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-timelock-for-privileged-actions::./src/LiquidRon.sol: req-3-timelock-for-privileged-actions::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Sensitive owner-controlled operations (fee updates, operator assignment, staking proxy deployment, pause control) execute immediately with `onlyOwner`/`onlyOperator` checks and no time delay. The codebase contains no timelock mechanism; a comment even notes timelocking the operator fee as a potential improvement. Therefore the requirement to use TimeLock delays for sensitive operations is not met.

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

_Determined via graph-gated Codex investigation (1 graph queries, 162s)._

## req-3-enough-gas::./src/LiquidRon.sol: req-3-enough-gas::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Validator and proxy lists grow without bound via `_tryPushValidator`. Core accounting (`totalAssets`) iterates over every validator across all proxies on each deposit/withdrawal, with no batching or caps, so gas cost scales with growth and can exceed block limits, breaking user flows. No documentation or mitigation exists to ensure sufficient gas for these growing structures, violating the requirement.

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

_Determined via graph-gated Codex investigation (1 graph queries, 275s)._

## req-3-protect-gas::./src/LiquidRon.sol: req-3-protect-gas::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** User deposit/mint rely on totalAssets, which performs unbounded, operator-controlled external-call loops over validators and proxies. Without caps or batching, a malicious operator can expand these lists to force excessive gas use or OOG, wasting or effectively stealing gas. No mitigation exists, so requirement is violated.

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

_Determined via graph-gated Codex investigation (1 graph queries, 193s)._

## req-3-block-front-running::./src/LiquidRon.sol: req-3-block-front-running::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Owner can change operatorFee at will; totalAssets and share conversion rely on this value, so fee changes immediately skew deposit/redeem pricing. No timelock or sequencing guard prevents fee changes from being front-run or used to manipulate ordering-dependent outcomes, violating the requirement to manage information to protect against ordering attacks.

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

_Determined via graph-gated Codex investigation (1 graph queries, 265s)._

## req-3-protect-governance::./src/LiquidRon.sol: req-3-protect-governance::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Access control for governance/operator actions is critically broken: the onlyOperator modifier reverts for owner or operators and allows any external caller, leaving high-impact staking and withdrawal management functions unrestricted. Combined with centralized owner authority and no time delays or multi-sig, the governance design is exposed to immediate takeover and misuse. Thus requirement to protect against governance takeovers is not met.

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

## req-3-event-on-state-change::./src/LiquidRon.sol: req-3-event-on-state-change::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20.constructor, ERC4626.constructor, Escrow.constructor, LiquidProxy.constructor, LiquidRon.constructor, LiquidRon.deployStakingProxy, LiquidRon.fetchOperatorFee, LiquidRon.setOperatorFee, LiquidRon.slitherConstructorConstantVariables, LiquidRon.updateFeeRecipient, LiquidRon.updateOperator, Panic.slitherConstructorConstantVariables, Pausable.pause, Pausable.unpause, RonHelper.constructor, ValidatorTracker._removeValidator, ValidatorTracker._tryPushValidator

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

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

## req-3-document-threats::./src/LiquidRon.sol: req-3-document-threats::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Requirement needs threat model documentation covering threats, assumptions, responses, and outcomes. Repository documentation (README.md, README-sponsor.md) lacks any such content, and searches across markdown files reveal no threat-model material. Therefore the requirement is unmet.

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

_Determined via graph-gated Codex investigation (1 graph queries, 197s)._

## req-3-annotate::./src/LiquidRon.sol: req-3-annotate::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ILiquidProxy.delegateAmount, ILiquidProxy.harvest, ILiquidProxy.harvestAndDelegateRewards, ILiquidProxy.redelegateAmount, ILiquidProxy.undelegateAmount, IRoninValidator.bulkUndelegate, IRoninValidator.claimRewards, IRoninValidator.delegate, IRoninValidator.delegateRewards, IRoninValidator.getManyStakingAmounts, IRoninValidator.getManyStakingTotals, IRoninValidator.getReward, IRoninValidator.getRewards, IRoninValidator.getStakingAmount, IRoninValidator.getStakingTotal, IRoninValidator.redelegate, IRoninValidator.undelegate, IVault.deposit, IWRON.deposit, IWRON.transfer, IWRON.withdraw, Pausable.pause, Pausable.unpause

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

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

## req-3-implement-as-documented::./src/LiquidRon.sol: req-3-implement-as-documented::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Documentation promises operators can invoke proxy/staking functions, but the `onlyOperator` modifier gates them to the owner only and explicitly rejects operator-marked addresses. This contradiction means the tested code does not behave as documented.

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

_Determined via graph-gated Codex investigation (1 graph queries, 185s)._

## req-3-access-control::./src/LiquidRon.sol: req-3-access-control::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** ERC20.approve, ERC20.transfer, ERC20.transferFrom, ERC4626.deposit, ERC4626.mint, ERC4626.redeem, ERC4626.withdraw, LiquidRon.delegateAmount, LiquidRon.deployStakingProxy, LiquidRon.deposit, LiquidRon.fetchOperatorFee, LiquidRon.finaliseRonRewardsForEpoch, LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards, LiquidRon.mint, LiquidRon.pruneValidatorList, LiquidRon.redeem, LiquidRon.redelegateAmount, LiquidRon.requestWithdrawal, LiquidRon.setOperatorFee, LiquidRon.updateFeeRecipient, LiquidRon.updateOperator, LiquidRon.withdraw, Ownable.renounceOwnership, Ownable.transferOwnership, Pausable.pause, Pausable.unpause

**Confidence:** HIGH

**Mechanism:** The documented least-privilege design allows operators (and the owner) to perform staking management. However, the onlyOperator modifier reverts for any caller that is not the owner or that has the operator flag set, so all functions using it—including delegateAmount—are effectively callable only by an owner that is not marked as operator. This blocks the intended operator role and misaligns privileged access with the documented logic, violating the least-privilege access control requirement.

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

_Determined via graph-gated Codex investigation (1 graph queries, 252s)._

## req-3-no-single-admin-eoa::./src/LiquidRon.sol: req-3-no-single-admin-eoa::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Privileged functions all require onlyOwner, and due to the onlyOperator modifier logic only the owner can invoke operator flows. Owner is initialized to the deployer and no multisig or revoker is implemented, so critical administrative tasks can be executed by a single EOA.

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

_Determined via graph-gated Codex investigation (1 graph queries, 164s)._

## req-3-external-calls::./src/LiquidRon.sol: req-3-external-calls::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** LiquidRon.harvest, LiquidRon.harvestAndDelegateRewards

**Confidence:** MEDIUM

**Mechanism:** Harvest functions make external calls but omit proxy validation and any documented need or protective measures; documentation does not describe the external dependency or safeguards, so requirement to document and protect external calls is not met.

**Supporting evidence:**
  - LiquidRon.harvest: external call at node 1 followed by state write at node 2 (CFG-reachable)
  - LiquidRon.harvestAndDelegateRewards: external call at node 2 followed by state write at node 3 (CFG-reachable)

_Determined via graph-gated Codex investigation (1 graph queries, 237s)._

## req-3-consistent-solidity-output::./src/LiquidRon.sol: req-3-consistent-solidity-output::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** pragma solidity^0.8.20

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

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

## req-R-use-latest-compiler::./src/LiquidRon.sol: req-R-use-latest-compiler::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** compiler config

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - compiler config: solc 0.8.20 != caller-supplied latest known stable version 0.8.36 (external, time-anchored reference -- not derived from spec text)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-clean-code::./src/LiquidRon.sol: req-R-clean-code::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Access-control logic contradicts its documentation, obscuring who may call operator-only functions. Additionally, two unrelated public flows share the same name `redeem`, reducing readability and making behavior hard to follow. These issues show the tested code is not written for easy understanding.

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

_Determined via graph-gated Codex investigation (1 graph queries, 149s)._

## req-R-define-license::./src/LiquidRon.sol: req-R-define-license::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/AccessControlDefaultAdminRulesHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/AccessControlHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/AccessManagedHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/AccessManagerHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/DoubleEndedQueueHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC20FlashMintHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC20PermitHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC20WrapperHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC3156FlashBorrowerHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC721Harness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC721ReceiverHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/EnumerableMapHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/EnumerableSetHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/InitializableHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/NoncesHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/Ownable2StepHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/OwnableHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/PausableHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/TimelockControllerHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/AccessControl.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/IAccessControl.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/Ownable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/Ownable2Step.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/extensions/AccessControlDefaultAdminRules.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/extensions/AccessControlEnumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/extensions/IAccessControlDefaultAdminRules.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/extensions/IAccessControlEnumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/AccessManaged.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/AccessManager.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/AuthorityUtils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/IAccessManaged.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/IAccessManager.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/IAuthority.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/account/utils/draft-ERC4337Utils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/account/utils/draft-ERC7579Utils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/finance/VestingWallet.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/finance/VestingWalletCliff.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/Governor.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/IGovernor.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/TimelockController.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorCountingFractional.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorCountingOverridable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorCountingSimple.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorPreventLateQuorum.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorSettings.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorStorage.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockAccess.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockCompound.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockControl.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotesQuorumFraction.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/utils/IVotes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/utils/Votes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/utils/VotesExtended.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1155.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1155MetadataURI.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1155Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1271.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1363.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1363Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1363Spender.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC165.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1820Implementer.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1820Registry.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1967.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC20Metadata.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC2309.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC2612.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC2981.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC3156.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC3156FlashBorrower.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC3156FlashLender.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC4626.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC4906.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC5267.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC5313.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC5805.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC6372.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC721Enumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC721Metadata.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC721Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC777.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC777Recipient.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC777Sender.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC1822.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC4337.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC6093.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC7579.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC7674.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/metatx/ERC2771Context.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/metatx/ERC2771Forwarder.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/AccessManagedTarget.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/AccessManagerMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ArraysMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/AuthorityMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/Base64Dirty.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/BatchCaller.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/CallReceiverMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ConstructorMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ContextMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/DummyImplementation.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/EIP712Verifier.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC1271WalletMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165InterfacesSupported.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165MaliciousData.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165MissingData.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165NotSupported.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165ReturnBomb.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC2771ContextMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC3156FlashBorrowerMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/EtherReceiverMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/InitializableMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/MerkleProofCustomHashMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/MerkleTreeMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/MulticallHelper.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/MultipleInheritanceInitializableMocks.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/PausableMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ReentrancyAttack.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ReentrancyMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ReentrancyTransientMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/RegressionImplementation.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/SingleInheritanceInitializableMocks.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/Stateless.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/StorageSlotMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/TimelockReentrant.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/TransientSlotMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/UpgradeableBeaconMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/VotesExtendedMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/VotesMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/account/utils/ERC7579UtilsMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/compound/CompTimelock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorCountingOverridableMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorFractionalMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorPreventLateQuorumMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorStorageMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockAccessMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockCompoundMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockControlMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorVoteMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorWithParamsMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/proxy/BadBeacon.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/proxy/ClashingImplementation.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/proxy/UUPSUpgradeableMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1155ReceiverMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363ForceApproveMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363NoReturnMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363ReceiverMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363ReturnFalseMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363SpenderMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ApprovalMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20DecimalsMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ExcessDecimalsMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20FlashMintMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ForceApproveMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20GetterHelper.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20Mock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20MulticallMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20NoReturnMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20Reentrant.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ReturnFalseMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20VotesAdditionalCheckpointsMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20VotesLegacyMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20VotesTimestampMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC4626LimitsMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC4626Mock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC4626OffsetMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC4646FeesMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ConsecutiveEnumerableMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ConsecutiveMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ReceiverMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC721URIStorageMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/Clones.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Utils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/Proxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/beacon/BeaconProxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/beacon/IBeacon.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/beacon/UpgradeableBeacon.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/transparent/ProxyAdmin.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/transparent/TransparentUpgradeableProxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/utils/Initializable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/utils/UUPSUpgradeable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/ERC1155.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/IERC1155.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/IERC1155Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Burnable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Pausable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Supply.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155URIStorage.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/IERC1155MetadataURI.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Utils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC1363.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Capped.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20FlashMint.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Pausable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Permit.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Votes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Wrapper.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC4626.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Permit.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/draft-ERC20TemporaryApproval.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/ERC1363Utils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/ERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/IERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/IERC721Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Burnable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Consecutive.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Enumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Pausable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Royalty.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721URIStorage.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Votes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Wrapper.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/IERC721Enumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/IERC721Metadata.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/utils/ERC721Holder.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/utils/ERC721Utils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/common/ERC2981.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Address.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Arrays.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Base64.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Bytes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/CAIP10.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/CAIP2.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Comparators.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Context.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Create2.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Errors.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Multicall.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Nonces.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/NoncesKeyed.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Packing.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Panic.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Pausable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/ReentrancyGuard.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/ReentrancyGuardTransient.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/ShortStrings.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/SlotDerivation.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Strings.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/TransientSlot.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/ECDSA.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/EIP712.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/Hashes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/MerkleProof.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/MessageHashUtils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/P256.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/RSA.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/SignatureChecker.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165Checker.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/introspection/IERC165.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SignedMath.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/BitMaps.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/Checkpoints.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/CircularBuffer.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/DoubleEndedQueue.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/Heap.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/MerkleTree.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/types/Time.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/vendor/compound/ICompoundTimelock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/erc4626-tests/ERC4626.prop.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/erc4626-tests/ERC4626.test.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/Base.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/Script.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdAssertions.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdChains.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdCheats.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdError.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdInvariant.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdJson.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdMath.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdStorage.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdStyle.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdToml.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdUtils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/Test.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/Vm.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/console.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/console2.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC1155.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC165.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC4626.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IMulticall3.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/mocks/MockERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/mocks/MockERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/safeconsole.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdChains.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdError.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdJson.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStyle.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdToml.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/Vm.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationScript.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationScriptBase.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationTest.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationTestBase.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/halmos-cheatcodes/src/SVM.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/halmos-cheatcodes/src/SymTest.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/account/utils/draft-ERC7579Utils.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Arrays.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Create2.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/script/LiquidRon_saigon.s.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/Escrow.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/LiquidProxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/LiquidRon.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/Pausable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/RonHelper.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/ValidatorTracker.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/interfaces/ILiquidProxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/interfaces/IRoninValidators.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/mock/MockRonStaking.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/mock/WrappedRon.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.t.sol

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/AccessControlDefaultAdminRulesHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/AccessControlHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/AccessManagedHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/AccessManagerHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/DoubleEndedQueueHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC20FlashMintHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC20PermitHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC20WrapperHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC3156FlashBorrowerHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC721Harness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/ERC721ReceiverHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/EnumerableMapHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/EnumerableSetHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/InitializableHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/NoncesHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/Ownable2StepHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/OwnableHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/PausableHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/harnesses/TimelockControllerHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/AccessControl.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/IAccessControl.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/Ownable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/Ownable2Step.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/extensions/AccessControlDefaultAdminRules.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/extensions/AccessControlEnumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/extensions/IAccessControlDefaultAdminRules.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/extensions/IAccessControlEnumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/AccessManaged.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/AccessManager.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/AuthorityUtils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/IAccessManaged.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/IAccessManager.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/access/manager/IAuthority.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/account/utils/draft-ERC4337Utils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/account/utils/draft-ERC7579Utils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/finance/VestingWallet.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/finance/VestingWalletCliff.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/Governor.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/IGovernor.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/TimelockController.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorCountingFractional.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorCountingOverridable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorCountingSimple.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorPreventLateQuorum.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorSettings.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorStorage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockAccess.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockCompound.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockControl.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotesQuorumFraction.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/utils/IVotes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/utils/Votes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/governance/utils/VotesExtended.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1155MetadataURI.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1155Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1271.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1363.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1363Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1363Spender.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1820Implementer.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1820Registry.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC1967.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC20Metadata.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC2309.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC2612.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC2981.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC3156.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC3156FlashBorrower.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC3156FlashLender.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC4626.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC4906.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC5267.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC5313.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC5805.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC6372.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC721Enumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC721Metadata.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC721Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC777.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC777Recipient.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/IERC777Sender.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC1822.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC4337.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC6093.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC7579.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC7674.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/metatx/ERC2771Context.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/metatx/ERC2771Forwarder.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/AccessManagedTarget.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/AccessManagerMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ArraysMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/AuthorityMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/Base64Dirty.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/BatchCaller.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/CallReceiverMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ConstructorMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ContextMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/DummyImplementation.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/EIP712Verifier.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC1271WalletMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165InterfacesSupported.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165MaliciousData.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165MissingData.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165NotSupported.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165ReturnBomb.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC2771ContextMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ERC3156FlashBorrowerMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/EtherReceiverMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/InitializableMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/MerkleProofCustomHashMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/MerkleTreeMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/MulticallHelper.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/MultipleInheritanceInitializableMocks.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/PausableMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ReentrancyAttack.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ReentrancyMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/ReentrancyTransientMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/RegressionImplementation.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/SingleInheritanceInitializableMocks.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/Stateless.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/StorageSlotMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/TimelockReentrant.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/TransientSlotMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/UpgradeableBeaconMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/VotesExtendedMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/VotesMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/account/utils/ERC7579UtilsMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/compound/CompTimelock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorCountingOverridableMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorFractionalMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorPreventLateQuorumMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorStorageMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockAccessMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockCompoundMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockControlMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorVoteMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorWithParamsMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/proxy/BadBeacon.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/proxy/ClashingImplementation.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/proxy/UUPSUpgradeableMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1155ReceiverMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363ForceApproveMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363NoReturnMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363ReceiverMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363ReturnFalseMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC1363SpenderMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ApprovalMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20DecimalsMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ExcessDecimalsMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20FlashMintMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ForceApproveMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20GetterHelper.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20Mock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20MulticallMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20NoReturnMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20Reentrant.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ReturnFalseMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20VotesAdditionalCheckpointsMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20VotesLegacyMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC20VotesTimestampMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC4626LimitsMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC4626Mock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC4626OffsetMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC4646FeesMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ConsecutiveEnumerableMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ConsecutiveMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ReceiverMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/mocks/token/ERC721URIStorageMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/Clones.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Utils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/Proxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/beacon/BeaconProxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/beacon/IBeacon.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/beacon/UpgradeableBeacon.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/transparent/ProxyAdmin.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/transparent/TransparentUpgradeableProxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/utils/Initializable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/proxy/utils/UUPSUpgradeable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/ERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/IERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/IERC1155Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Burnable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Pausable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Supply.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155URIStorage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/IERC1155MetadataURI.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Utils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC1363.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Capped.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20FlashMint.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Pausable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Permit.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Votes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Wrapper.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC4626.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Permit.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/draft-ERC20TemporaryApproval.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/ERC1363Utils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/ERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/IERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/IERC721Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Burnable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Consecutive.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Enumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Pausable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Royalty.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721URIStorage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Votes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Wrapper.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/IERC721Enumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/IERC721Metadata.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/utils/ERC721Holder.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/ERC721/utils/ERC721Utils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/token/common/ERC2981.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Address.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Arrays.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Base64.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Bytes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/CAIP10.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/CAIP2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Comparators.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Context.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Create2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Errors.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Multicall.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Nonces.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/NoncesKeyed.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Packing.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Panic.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Pausable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/ReentrancyGuard.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/ReentrancyGuardTransient.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/ShortStrings.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/SlotDerivation.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/Strings.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/TransientSlot.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/ECDSA.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/EIP712.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/Hashes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/MerkleProof.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/MessageHashUtils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/P256.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/RSA.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/cryptography/SignatureChecker.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165Checker.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/introspection/IERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/Math.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/math/SignedMath.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/BitMaps.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/Checkpoints.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/CircularBuffer.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/DoubleEndedQueue.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/Heap.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/structs/MerkleTree.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/utils/types/Time.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/contracts/vendor/compound/ICompoundTimelock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/erc4626-tests/ERC4626.prop.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/erc4626-tests/ERC4626.test.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/Base.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/Script.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdAssertions.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdChains.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdCheats.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdError.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdInvariant.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdJson.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdMath.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdStorage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdStyle.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdToml.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/StdUtils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/Test.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/Vm.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/console.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/console2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC4626.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IMulticall3.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/mocks/MockERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/mocks/MockERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/src/safeconsole.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdChains.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdError.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdJson.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStyle.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdToml.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/Vm.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationScript.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationScriptBase.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationTest.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationTestBase.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/halmos-cheatcodes/src/SVM.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/halmos-cheatcodes/src/SymTest.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/account/utils/draft-ERC7579Utils.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Arrays.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Create2.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/script/LiquidRon_saigon.s.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/Escrow.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/LiquidProxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/LiquidRon.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/Pausable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/RonHelper.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/ValidatorTracker.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/interfaces/ILiquidProxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/interfaces/IRoninValidators.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/mock/MockRonStaking.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/src/mock/WrappedRon.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.t.sol: SPDX-License-Identifier found

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-notify-news::./src/LiquidRon.sol: req-R-notify-news::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Reviewed top-level documentation (README.md, README-sponsor.md) and contract NatSpec (LiquidRon.sol). No mention of responsible disclosure channels or guidance. Therefore the requirement to responsibly disclose new vulnerabilities is not addressed.

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

## req-R-fuzzing-in-testing::./src/LiquidRon.sol: req-R-fuzzing-in-testing::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed2, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound_DistributionIsEven, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundMaxLessThanMin, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testApprove, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testBurn, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailBurnInsufficientBalance, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadDeadline, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadNonce, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitPastDeadline, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitReplay, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientAllowance, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientBalance, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferInsufficientBalance, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testMetadata, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testMint, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testPermit, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testTransfer, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApprove, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveAll, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveBurn, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testBurn, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnAuthorized, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnMinted, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailBurnUnMinted, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleBurn, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleMint, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailMintToZero, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailOwnerOfUnminted, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnDataWithData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721Recipient, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721RecipientWithData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721Recipient, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721RecipientWithData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnDataWithData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721Recipient, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721RecipientWithData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721Recipient, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721RecipientWithData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromNotOwner, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromToZero, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromUnOwned, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromWrongFrom, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testMetadata, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testMint, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToEOA, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721Recipient, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721RecipientWithData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToEOA, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721Recipient, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721RecipientWithData, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromApproveAll, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromSelf, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testInvalidDescriptionForProposer, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testValidDescriptionForProposer, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteAvoidsETHStuck, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchAvoidsETHStuck, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchTamperedValues, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchTamperedValuesZeroReceiver, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteTamperedValues, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testVerifyTamperedValues, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testCloneDeterministicDirty, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testFetchCloneArgs, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testPredictDeterministicAddressDirty, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testSymbolicPredictDeterministicAddressSpillage, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testSymbolicPredictDeterministicAddressWithImmutableArgsSpillage, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_start_consecutive_id, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Arrays.t.sol:testSort, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol:testEncode, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol:testEncodeURL, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Create2.t.sol:testSymbolicComputeAddressSpillage, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthShort, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthWithFallback, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRevertLong, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripShort, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripWithFallback, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveArray, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveMappingBytes, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveMappingString, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingAddress, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingAddressDirty, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBoolean, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBooleanDirty, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBytes32, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBytes4, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingInt256, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingInt32, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingUint256, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingUint32, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParse, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseChecksumHex, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseHex, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseSigned, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testTryParseAddressExtendedEnd, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testTryParseHexUintExtendedEnd, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol:testRecover, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol:testVerify, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testCeilDiv, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod17, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod2, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod65537, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvModP256, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog10, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog2, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog256, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testModExp, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testModExpMemory, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDiv, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDivDomain, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSqrt, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSymbolicMinMax, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSymbolicTernary, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testTryModExp, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testTryModExpMemory, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testAverage1, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testAverage2, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicAbs, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMax, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMin, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMinMax, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicTernary, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol:testFuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol:testFuzzGt, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_fetch_operator_fee, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_deploy_staking_proxy, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_set_operator, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_set_operator_fee, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_fee_recipient, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_operator, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_operator_fee, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_admin_pause, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_escrow_not_vault, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_fee_recipient, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_fetch_fee_non_receiver, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_proxies_not_vault, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_delegate, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest_and_delegate, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest_duration, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_redelegate, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_3days_redelegate, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_delegate, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_delegate_bad_proxy, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_insufficient_delegate, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_redelegate, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_undelegate, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_undelegate, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.t.sol:test_deposit, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.t.sol:test_deposit_no_func_call, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.t.sol:test_withdraw_init

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testMetadata: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testTransfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testPermit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailBurnInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientAllowance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadNonce: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadDeadline: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitPastDeadline: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitReplay: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testMetadata: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromSelf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailMintToZero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailBurnUnMinted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnMinted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnAuthorized: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromUnOwned: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromWrongFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromToZero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromNotOwner: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnDataWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnDataWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/lib/forge-std/test/mocks/MockERC721.t.sol:testFailOwnerOfUnminted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testValidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testInvalidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteAvoidsETHStuck: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchAvoidsETHStuck: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testVerifyTamperedValues: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteTamperedValues: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchTamperedValuesZeroReceiver: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchTamperedValues: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testSymbolicPredictDeterministicAddressSpillage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testSymbolicPredictDeterministicAddressWithImmutableArgsSpillage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testCloneDeterministicDirty: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testPredictDeterministicAddressDirty: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/proxy/Clones.t.sol:testFetchCloneArgs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_start_consecutive_id: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Arrays.t.sol:testSort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol:testEncode: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Base64.t.sol:testEncodeURL: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Create2.t.sol:testSymbolicComputeAddressSpillage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testPack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Packing.t.sol:testReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRevertLong: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveArray: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingAddress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBoolean: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBytes32: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBytes4: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingUint256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingUint32: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingInt256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingInt32: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveMappingString: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testDeriveMappingBytes: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingBooleanDirty: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/SlotDerivation.t.sol:testSymbolicDeriveMappingAddressDirty: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParse: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseSigned: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseHex: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testParseChecksumHex: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testTryParseHexUintExtendedEnd: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/Strings.t.sol:testTryParseAddressExtendedEnd: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol:testVerify: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/cryptography/P256.t.sol:testRecover: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSymbolicTernary: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSymbolicMinMax: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testCeilDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSqrt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod17: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvMod65537: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testInvModP256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog10: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDivDomain: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testModExp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testTryModExp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testModExpMemory: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testTryModExpMemory: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicTernary: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMinMax: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicMax: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testAverage1: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testAverage2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/math/SignedMath.t.sol:testSymbolicAbs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol:testFuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/test/utils/structs/Heap.t.sol:testFuzzGt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_admin_pause: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_fee_recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_operator: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_set_operator: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_set_operator_fee: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_set_operator_fee: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_revert_deploy_staking_proxy: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_admin_fetch_operator_fee: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_fetch_fee_non_receiver: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_escrow_not_vault: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_proxies_not_vault: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.admin.t.sol:test_revert_fee_recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_delegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_delegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_delegate_bad_proxy: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_insufficient_delegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest_duration: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_harvest_and_delegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_3days_redelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_redelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_redelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_revert_undelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.operator.t.sol:test_undelegate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.t.sol:test_deposit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.t.sol:test_deposit_no_func_call: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/test/LiquidRon.t.sol:test_withdraw_init: Foundry-convention parameterized test function (fuzzed by forge test)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-formal-verification::./src/LiquidRon.sol: req-R-formal-verification::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/AccessControl.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/AccessControlDefaultAdminRules.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/AccessManaged.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/AccessManager.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/DoubleEndedQueue.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/ERC20.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/ERC20FlashMint.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/ERC20Wrapper.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/ERC721.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/EnumerableMap.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/EnumerableSet.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Initializable.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Nonces.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Ownable.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Ownable2Step.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Pausable.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/TimelockController.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/helpers/helpers.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IAccessControl.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IAccessControlDefaultAdminRules.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IAccessManaged.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IAccessManager.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC20.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC2612.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC3156FlashBorrower.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC3156FlashLender.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC5313.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC721.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC721Receiver.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IOwnable.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IOwnable2Step.spec

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/AccessControlDefaultAdminRules.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/AccessManaged.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/EnumerableMap.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/EnumerableSet.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Initializable.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/ERC20Wrapper.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Ownable2Step.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Pausable.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Nonces.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/AccessControl.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/ERC20FlashMint.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/TimelockController.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/AccessManager.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/DoubleEndedQueue.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/ERC20.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/Ownable.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/ERC721.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IAccessManager.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IAccessManaged.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC2612.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC721Receiver.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC20.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IAccessControlDefaultAdminRules.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC5313.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC721.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IOwnable.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC3156FlashLender.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IOwnable2Step.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IERC3156FlashBorrower.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/methods/IAccessControl.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2025-01-liquid-ron/lib/openzeppelin-contracts/certora/specs/helpers/helpers.spec: Certora spec file present

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-multisig-threshold::./src/LiquidRon.sol: req-R-multisig-threshold::./src/LiquidRon.sol

**Requirement:** 

**Location(s):** 2025-01-liquid-ron, LiquidRon.sol, LiquidRon.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Privileged controls are held by a single Ownable owner (and operators designated by that owner), with no multisig or threshold guard. Requirement recommends avoiding 1-of-N and all-signature setups and using sufficient signer thresholds. The protocol uses 1-of-1 control, so it fails the recommended threshold guidance.

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

_Determined via graph-gated Codex investigation (1 graph queries, 213s)._
