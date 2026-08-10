# Security Audit Report: 2024-01-canto

Findings below were produced by the RTF (Requirement Translation Framework) pipeline: EthTrust requirement routing, deterministic evidence collection, bounded LLM judgment, and (where the bounded judgment was inconclusive, insufficient, or low-confidence) graph-gated Codex investigation.

## req-1-no-assembly::src/LendingLedger.sol: req-1-no-assembly::src/LendingLedger.sol

**Requirement:** 

**Location(s):** Address._revert, Math.mulDiv

**Confidence:** HIGH

**Mechanism:** Inline assembly is present in imported OpenZeppelin libraries (e.g., Address._revert, Math.mulDiv) used by the project, with no documentation or overriding-requirement justification. Thus the requirement prohibiting assembly is not satisfied.

**Supporting evidence:**
  - Math.mulDiv: Math.mulDiv(uint256,uint256,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#55-134) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#62-66)
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#85-92)
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#99-108)
  - Address._revert: Address._revert(bytes,string) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Address.sol#231-243) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Address.sol#236-239)

_Determined via graph-gated Codex investigation (1 graph queries, 213s)._

## req-1-delegatecall::src/LendingLedger.sol: req-1-delegatecall::src/LendingLedger.sol

**Requirement:** 

**Location(s):** Address.functionDelegateCall

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - Address.functionDelegateCall: delegatecall present

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-pass-l1::src/LendingLedger.sol: req-2-pass-l1::src/LendingLedger.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-external-calls::src/LendingLedger.sol: req-2-external-calls::src/LendingLedger.sol

**Requirement:** 

**Location(s):** GaugeController.vote_for_gauge_weights, LendingLedger.update_market

**Confidence:** HIGH

**Mechanism:** Requirement demands all external calls target only the tested contract set under the same control and maintain CEI-level reentrancy protection. LendingLedger.claim issues a value-bearing external call to `msg.sender`, an arbitrary address outside the tested contracts, violating the restriction on external call targets; although state is updated before the call, the target control requirement is not met.

**Supporting evidence:**
  - GaugeController.vote_for_gauge_weights: external call at node 5 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 8 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 28 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 29 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 31 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 32 followed by state write at node 46 (CFG-reachable)
  - LendingLedger.update_market: external call at node 11 followed by state write at node 13 (CFG-reachable)
  - LendingLedger.update_market: external call at node 12 followed by state write at node 13 (CFG-reachable)

_Determined via graph-gated Codex investigation (0 graph queries, 161s)._

## req-2-documented::src/LendingLedger.sol: req-2-documented::src/LendingLedger.sol

**Requirement:** 

**Location(s):** Address._revert, Address.functionCallWithValue, Address.functionDelegateCall, Address.functionStaticCall, Address.sendValue, GaugeController._change_gauge_weight, GaugeController._get_sum, GaugeController._get_weight, GaugeController._remove_gauge_weight, GaugeController.constructor, GaugeController.vote_for_gauge_weights, LendingLedger.claim, LendingLedger.update_market, LendingLedger.whiteListLendingMarket, Math.log10, Math.log2, Math.log256, Math.mulDiv, Math.sqrt, SafeERC20._callOptionalReturn, SafeERC20._callOptionalReturnBool, SafeERC20.safeApprove, SafeERC20.safeDecreaseAllowance, SafeERC20.safeIncreaseAllowance, SafeERC20.safePermit, VotingEscrow._checkpoint, VotingEscrow.balanceOf, VotingEscrow.balanceOfAt, VotingEscrow.constructor, VotingEscrow.createLock, VotingEscrow.increaseAmount, VotingEscrow.totalSupply, VotingEscrow.totalSupplyAt, VotingEscrow.withdraw

**Confidence:** HIGH

**Mechanism:** Requirement mandates documenting the need for each instance of special constructs like block.timestamp/number. _change_gauge_weight computes next_time using block.timestamp with no accompanying explanation, and project documentation provides no justification. Thus documentation is missing for this special code use.

**Supporting evidence:**
  - Math.mulDiv: Math.mulDiv(uint256,uint256,uint256) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#55-134) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#62-66)
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#85-92)
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol#99-108)
  - Address._revert: Address._revert(bytes,string) (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Address.sol#231-243) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Address.sol#236-239)
  - SafeERC20.safeApprove: makes an external call
  - SafeERC20.safeIncreaseAllowance: makes an external call
  - SafeERC20.safeDecreaseAllowance: makes an external call
  - SafeERC20.safePermit: makes an external call
  - SafeERC20.safePermit: makes an external call
  - SafeERC20.safePermit: makes an external call
  - SafeERC20._callOptionalReturn: makes an external call
  - SafeERC20._callOptionalReturnBool: makes an external call
  - SafeERC20._callOptionalReturnBool: makes an external call
  - Address.sendValue: makes an external call
  - Address.functionCallWithValue: makes an external call
  - Address.functionStaticCall: makes an external call
  - Address.functionDelegateCall: makes an external call
  - GaugeController.vote_for_gauge_weights: makes an external call
  - GaugeController.vote_for_gauge_weights: makes an external call
  - GaugeController.vote_for_gauge_weights: makes an external call
  - GaugeController.vote_for_gauge_weights: makes an external call
  - GaugeController.vote_for_gauge_weights: makes an external call
  - GaugeController.vote_for_gauge_weights: makes an external call
  - LendingLedger.update_market: makes an external call
  - LendingLedger.update_market: makes an external call
  - LendingLedger.claim: makes an external call
  - VotingEscrow.withdraw: makes an external call
  - Address.functionDelegateCall: delegatecall present
  - SafeERC20.safeDecreaseAllowance: - operation, inside unchecked{} block
  - Address._revert: + operation, inside unchecked{} block
  - Math.mulDiv: * operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: - operation, inside unchecked{} block
  - Math.mulDiv: + operation, inside unchecked{} block
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
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: * operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.sqrt: + operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
  - Math.log2: + operation, inside unchecked{} block
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
  - Math.log10: + operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - Math.log256: + operation, inside unchecked{} block
  - GaugeController.constructor: reads block.timestamp
  - GaugeController._get_sum: reads block.timestamp
  - GaugeController._get_sum: reads block.timestamp
  - GaugeController._get_weight: reads block.timestamp
  - GaugeController._get_weight: reads block.timestamp
  - GaugeController._change_gauge_weight: reads block.timestamp
  - GaugeController._remove_gauge_weight: reads block.timestamp
  - GaugeController.vote_for_gauge_weights: reads block.timestamp
  - GaugeController.vote_for_gauge_weights: reads block.timestamp
  - GaugeController.vote_for_gauge_weights: reads block.timestamp
  - LendingLedger.update_market: reads block.number
  - LendingLedger.update_market: reads block.number
  - LendingLedger.update_market: reads block.number
  - LendingLedger.update_market: reads block.number
  - LendingLedger.whiteListLendingMarket: reads block.number
  - VotingEscrow.constructor: reads block.number
  - VotingEscrow.constructor: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.number
  - VotingEscrow._checkpoint: reads block.number
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.number
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.number
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow._checkpoint: reads block.timestamp
  - VotingEscrow.createLock: reads block.timestamp
  - VotingEscrow.createLock: reads block.timestamp
  - VotingEscrow.increaseAmount: reads block.timestamp
  - VotingEscrow.increaseAmount: reads block.timestamp
  - VotingEscrow.increaseAmount: reads block.timestamp
  - VotingEscrow.increaseAmount: reads block.timestamp
  - VotingEscrow.increaseAmount: reads block.timestamp
  - VotingEscrow.withdraw: reads block.timestamp
  - VotingEscrow.withdraw: reads block.timestamp
  - VotingEscrow.balanceOf: reads block.timestamp
  - VotingEscrow.balanceOfAt: reads block.number
  - VotingEscrow.balanceOfAt: reads block.number
  - VotingEscrow.balanceOfAt: reads block.timestamp
  - VotingEscrow.totalSupply: reads block.timestamp
  - VotingEscrow.totalSupplyAt: reads block.number
  - VotingEscrow.totalSupplyAt: reads block.number
  - VotingEscrow.totalSupplyAt: reads block.number
  - VotingEscrow.totalSupplyAt: reads block.timestamp

_Determined via graph-gated Codex investigation (0 graph queries, 133s)._

## req-2-check-rounding::src/LendingLedger.sol: req-2-check-rounding::src/LendingLedger.sol

**Requirement:** 

**Location(s):** GaugeController._change_gauge_weight, GaugeController._gauge_relative_weight, GaugeController._remove_gauge_weight, GaugeController.constructor, GaugeController.vote_for_gauge_weights, LendingLedger.claim, LendingLedger.sync_ledger, LendingLedger.update_market, Math.average, Math.ceilDiv, Math.log10, Math.mulDiv, Math.sqrt, VotingEscrow._checkpoint, VotingEscrow._findBlockEpoch, VotingEscrow._findUserBlockEpoch, VotingEscrow._floorToWeek, VotingEscrow.balanceOfAt, VotingEscrow.totalSupplyAt

**Confidence:** MEDIUM

**Mechanism:** Reward calculations floor multiple times without documenting error bounds or reclaiming dust, allowing cumulative unclaimed value; EthTrust requires documenting and preventing value loss/creation from rounding.

**Supporting evidence:**
  - Math.average: division operation (potential rounding)
  - Math.ceilDiv: division operation (potential rounding)
  - Math.mulDiv: division operation (potential rounding)
  - Math.mulDiv: division operation (potential rounding)
  - Math.mulDiv: division operation (potential rounding)
  - Math.mulDiv: division operation (potential rounding)
  - Math.sqrt: division operation (potential rounding)
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
  - GaugeController.constructor: division operation (potential rounding)
  - GaugeController._gauge_relative_weight: division operation (potential rounding)
  - GaugeController._gauge_relative_weight: division operation (potential rounding)
  - GaugeController._change_gauge_weight: division operation (potential rounding)
  - GaugeController._remove_gauge_weight: division operation (potential rounding)
  - GaugeController.vote_for_gauge_weights: division operation (potential rounding)
  - GaugeController.vote_for_gauge_weights: division operation (potential rounding)
  - LendingLedger.update_market: division operation (potential rounding)
  - LendingLedger.update_market: division operation (potential rounding)
  - LendingLedger.update_market: division operation (potential rounding)
  - LendingLedger.update_market: division operation (potential rounding)
  - LendingLedger.sync_ledger: division operation (potential rounding)
  - LendingLedger.sync_ledger: division operation (potential rounding)
  - LendingLedger.sync_ledger: division operation (potential rounding)
  - LendingLedger.sync_ledger: division operation (potential rounding)
  - LendingLedger.claim: division operation (potential rounding)
  - VotingEscrow._checkpoint: division operation (potential rounding)
  - VotingEscrow._checkpoint: division operation (potential rounding)
  - VotingEscrow._checkpoint: division operation (potential rounding)
  - VotingEscrow._checkpoint: division operation (potential rounding)
  - VotingEscrow._floorToWeek: division operation (potential rounding)
  - VotingEscrow._findBlockEpoch: division operation (potential rounding)
  - VotingEscrow._findUserBlockEpoch: division operation (potential rounding)
  - VotingEscrow.balanceOfAt: division operation (potential rounding)
  - VotingEscrow.totalSupplyAt: division operation (potential rounding)
  - VotingEscrow.totalSupplyAt: division operation (potential rounding)

_Determined via graph-gated Codex investigation (1 graph queries, 227s)._

## req-3-pass-l2::src/LendingLedger.sol: req-3-pass-l2::src/LendingLedger.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-timelock-for-privileged-actions::src/LendingLedger.sol: req-3-timelock-for-privileged-actions::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Governance can directly change reward rates and market whitelisting without any timelock or delay, violating the requirement that sensitive operations use TimeLock delays.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 127s)._

## req-3-linted::src/LendingLedger.sol: req-3-linted::src/LendingLedger.sol

**Requirement:** 

**Location(s):** ReentrancyGuard._reentrancyGuardEntered

**Confidence:** MEDIUM

**Mechanism:** Requirement demands explicit visibility on all functions; ReentrancyGuard constructor omits visibility, violating the linting rule despite _reentrancyGuardEntered itself being compliant.

**Supporting evidence:**
  - ReentrancyGuard._reentrancyGuardEntered: ReentrancyGuard._reentrancyGuardEntered() (../../../../../.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/security/ReentrancyGuard.sol#74-76) is never used and should be removed

_Determined via graph-gated Codex investigation (0 graph queries, 79s)._

## req-3-protect-governance::src/LendingLedger.sol: req-3-protect-governance::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Privileged functions rely solely on a single governance address check and can update governance itself, set rewards, or whitelist markets without delay or checks. No timelock, multisig, caps, or circuit breakers exist, and documentation explicitly assumes governance is trusted. This leaves the system unprotected against governance takeover, violating the requirement.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 181s)._

## req-3-all-valid-inputs::src/LendingLedger.sol: req-3-all-valid-inputs::src/LendingLedger.sol

**Requirement:** 

**Location(s):** Address._revert, Address.functionCall, Address.functionCallWithValue, Address.functionDelegateCall, Address.functionStaticCall, Address.isContract, Address.verifyCallResult, GaugeController._change_gauge_weight, GaugeController._gauge_relative_weight, GaugeController._get_weight, GaugeController._remove_gauge_weight, GaugeController.checkpoint_gauge, GaugeController.gauge_relative_weight, GaugeController.gauge_relative_weight_write, GaugeController.get_gauge_weight, GaugeController.remove_gauge_weight, GaugeController.setGovernance, IERC20.allowance, IERC20.approve, IERC20.balanceOf, IERC20.transfer, IERC20.transferFrom, IERC20Permit.nonces, IERC20Permit.permit, LendingLedger.claim, LendingLedger.setGovernance, LendingLedger.sync_ledger, LendingLedger.update_market, LendingLedger.whiteListLendingMarket, Math.average, Math.ceilDiv, Math.log10, Math.log2, Math.log256, Math.max, Math.min, Math.mulDiv, Math.sqrt, SafeERC20._callOptionalReturn, SafeERC20._callOptionalReturnBool, SafeERC20.forceApprove, SafeERC20.safeIncreaseAllowance, SafeERC20.safePermit, SafeERC20.safeTransfer, SafeERC20.safeTransferFrom, VotingEscrow._checkpoint, VotingEscrow._copyLock, VotingEscrow._findBlockEpoch, VotingEscrow._findUserBlockEpoch, VotingEscrow._floorToWeek, VotingEscrow._supplyAt, VotingEscrow.balanceOf, VotingEscrow.balanceOfAt, VotingEscrow.constructor, VotingEscrow.createLock, VotingEscrow.getLastUserPoint, VotingEscrow.increaseAmount, VotingEscrow.lockEnd, VotingEscrow.withdraw

**Confidence:** MEDIUM

**Mechanism:** Reward and block timestamp computations are narrowed to smaller integer types without validation. Oversized inputs (e.g., large `cantoPerBlock` set by governance) can produce values exceeding uint128, leading to silent truncation rather than a checked failure, violating the requirement to validate inputs and handle malformed values safely.

**Supporting evidence:**
  - IERC20.balanceOf: none of this function's parameters (['account']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - IERC20.transfer: none of this function's parameters (['amount', 'to']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - IERC20.allowance: none of this function's parameters (['owner', 'spender']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - IERC20.approve: none of this function's parameters (['amount', 'spender']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - IERC20.transferFrom: none of this function's parameters (['amount', 'from', 'to']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - IERC20Permit.permit: none of this function's parameters (['deadline', 'owner', 'r', 's', 'spender', 'v', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - IERC20Permit.nonces: none of this function's parameters (['owner']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - SafeERC20.safeTransfer: none of this function's parameters (['to', 'token', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - SafeERC20.safeTransferFrom: none of this function's parameters (['from', 'to', 'token', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - SafeERC20.safeIncreaseAllowance: none of this function's parameters (['spender', 'token', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - SafeERC20.forceApprove: none of this function's parameters (['spender', 'token', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - SafeERC20.safePermit: none of this function's parameters (['deadline', 'owner', 'r', 's', 'spender', 'token', 'v', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - SafeERC20._callOptionalReturn: none of this function's parameters (['data', 'token']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - SafeERC20._callOptionalReturnBool: none of this function's parameters (['data', 'token']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address.isContract: none of this function's parameters (['account']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address.functionCall: none of this function's parameters (['data', 'target']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address.functionCall: none of this function's parameters (['data', 'errorMessage', 'target']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address.functionCallWithValue: none of this function's parameters (['data', 'target', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address.functionStaticCall: none of this function's parameters (['data', 'target']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address.functionStaticCall: none of this function's parameters (['data', 'errorMessage', 'target']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address.functionDelegateCall: none of this function's parameters (['data', 'target']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address.functionDelegateCall: none of this function's parameters (['data', 'errorMessage', 'target']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address.verifyCallResult: none of this function's parameters (['errorMessage', 'returndata', 'success']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Address._revert: none of this function's parameters (['errorMessage', 'returndata']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.max: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.min: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.average: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.ceilDiv: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.mulDiv: none of this function's parameters (['denominator', 'rounding', 'x', 'y']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.sqrt: none of this function's parameters (['a']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.sqrt: none of this function's parameters (['a', 'rounding']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.log2: none of this function's parameters (['value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.log2: none of this function's parameters (['rounding', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.log10: none of this function's parameters (['value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.log10: none of this function's parameters (['rounding', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.log256: none of this function's parameters (['value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Math.log256: none of this function's parameters (['rounding', 'value']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController.setGovernance: none of this function's parameters (['_governance']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController._get_weight: none of this function's parameters (['_gauge_addr']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController.checkpoint_gauge: none of this function's parameters (['_gauge']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController._gauge_relative_weight: none of this function's parameters (['_gauge', '_time']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController.gauge_relative_weight: none of this function's parameters (['_gauge', '_time']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController.gauge_relative_weight_write: none of this function's parameters (['_gauge', '_time']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController._change_gauge_weight: none of this function's parameters (['_gauge', '_weight']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController._remove_gauge_weight: none of this function's parameters (['_gauge']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController.remove_gauge_weight: none of this function's parameters (['_gauge']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - GaugeController.get_gauge_weight: none of this function's parameters (['_gauge']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - LendingLedger.setGovernance: none of this function's parameters (['_governance']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - LendingLedger.sync_ledger: none of this function's parameters (['_delta', '_lender']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - LendingLedger.claim: none of this function's parameters (['_market']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - VotingEscrow.lockEnd: none of this function's parameters (['_addr']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - VotingEscrow.getLastUserPoint: none of this function's parameters (['_addr']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - VotingEscrow._checkpoint: none of this function's parameters (['_addr', '_newLocked', '_oldLocked']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - VotingEscrow._copyLock: none of this function's parameters (['_locked']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - VotingEscrow._floorToWeek: none of this function's parameters (['_t']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - VotingEscrow._findBlockEpoch: none of this function's parameters (['_block', '_maxEpoch']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - VotingEscrow._findUserBlockEpoch: none of this function's parameters (['_addr', '_block']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - VotingEscrow.balanceOf: none of this function's parameters (['_owner']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - VotingEscrow._supplyAt: none of this function's parameters (['_point', '_t']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - LendingLedger.update_market: unchecked narrowing cast: TMP_363 (uint256) -> uint128, no bound check found for this parameter against the destination type's max value
  - LendingLedger.update_market: unchecked narrowing cast: TMP_366 (uint256) -> uint128, no bound check found for this parameter against the destination type's max value
  - LendingLedger.update_market: unchecked narrowing cast: block.number (uint256) -> uint64, no bound check found for this parameter against the destination type's max value
  - LendingLedger.whiteListLendingMarket: unchecked narrowing cast: block.number (uint256) -> uint64, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.constructor: unchecked narrowing cast: 0 (uint256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.constructor: unchecked narrowing cast: 0 (uint256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow._checkpoint: unchecked narrowing cast: TMP_432 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow._checkpoint: unchecked narrowing cast: TMP_436 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow._checkpoint: unchecked narrowing cast: TMP_442 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow._checkpoint: unchecked narrowing cast: TMP_446 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow._checkpoint: unchecked narrowing cast: TMP_468 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.createLock: unchecked narrowing cast: TMP_509 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.createLock: unchecked narrowing cast: TMP_511 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.increaseAmount: unchecked narrowing cast: TMP_527 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.increaseAmount: unchecked narrowing cast: TMP_532 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.increaseAmount: unchecked narrowing cast: TMP_541 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.withdraw: unchecked narrowing cast: TMP_556 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.balanceOf: unchecked narrowing cast: TMP_584 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow.balanceOfAt: unchecked narrowing cast: TMP_608 (int256) -> int128, no bound check found for this parameter against the destination type's max value
  - VotingEscrow._supplyAt: unchecked narrowing cast: TMP_641 (int256) -> int128, no bound check found for this parameter against the destination type's max value

_Determined via graph-gated Codex investigation (1 graph queries, 233s)._

## req-3-event-on-state-change::src/LendingLedger.sol: req-3-event-on-state-change::src/LendingLedger.sol

**Requirement:** 

**Location(s):** GaugeController._change_gauge_weight, GaugeController._get_sum, GaugeController._get_weight, GaugeController._remove_gauge_weight, GaugeController.constructor, GaugeController.setGovernance, GaugeController.slitherConstructorConstantVariables, GaugeController.vote_for_gauge_weights, LendingLedger.claim, LendingLedger.constructor, LendingLedger.setGovernance, LendingLedger.setRewards, LendingLedger.slitherConstructorConstantVariables, LendingLedger.sync_ledger, LendingLedger.update_market, LendingLedger.whiteListLendingMarket, ReentrancyGuard._nonReentrantAfter, ReentrancyGuard._nonReentrantBefore, ReentrancyGuard.constructor, ReentrancyGuard.slitherConstructorConstantVariables, VotingEscrow._checkpoint, VotingEscrow.constructor, VotingEscrow.slitherConstructorConstantVariables, VotingEscrow.slitherConstructorVariables

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - ReentrancyGuard.constructor: writes state but emits no event
  - ReentrancyGuard._nonReentrantBefore: writes state but emits no event
  - ReentrancyGuard._nonReentrantAfter: writes state but emits no event
  - ReentrancyGuard.slitherConstructorConstantVariables: writes state but emits no event
  - GaugeController.constructor: writes state but emits no event
  - GaugeController.setGovernance: writes state but emits no event
  - GaugeController._get_sum: writes state but emits no event
  - GaugeController._get_weight: writes state but emits no event
  - GaugeController._change_gauge_weight: writes state but emits no event
  - GaugeController._remove_gauge_weight: writes state but emits no event
  - GaugeController.vote_for_gauge_weights: writes state but emits no event
  - GaugeController.slitherConstructorConstantVariables: writes state but emits no event
  - LendingLedger.constructor: writes state but emits no event
  - LendingLedger.setGovernance: writes state but emits no event
  - LendingLedger.update_market: writes state but emits no event
  - LendingLedger.sync_ledger: writes state but emits no event
  - LendingLedger.claim: writes state but emits no event
  - LendingLedger.setRewards: writes state but emits no event
  - LendingLedger.whiteListLendingMarket: writes state but emits no event
  - LendingLedger.slitherConstructorConstantVariables: writes state but emits no event
  - VotingEscrow.constructor: writes state but emits no event
  - VotingEscrow._checkpoint: writes state but emits no event
  - VotingEscrow.slitherConstructorVariables: writes state but emits no event
  - VotingEscrow.slitherConstructorConstantVariables: writes state but emits no event

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-documented::src/LendingLedger.sol: req-3-documented::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Review of README and LendingLedger.sol found only brief descriptions and inline comments, without any accessible, detailed specification of the contract’s business logic. Callers cannot reference a documented specification, violating the requirement.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 139s)._

## req-3-document-system::src/LendingLedger.sol: req-3-document-system::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Search across repository found only a generic README with contest info and a short LendingLedger purpose; no system architecture, security assumptions, or usage documentation exists, so the mandatory documentation requirement is not met.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 221s)._

## req-3-document-threats::src/LendingLedger.sol: req-3-document-threats::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Repository lacks any document describing threat models, security assumptions, or expected responses/outcomes for the tested code. README and source files contain no such documentation, so the requirement is unmet.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 137s)._

## req-3-annotate::src/LendingLedger.sol: req-3-annotate::src/LendingLedger.sol

**Requirement:** 

**Location(s):** LendingLedger.receive, LendingLedger.update_market, VotingEscrow.balanceOfAt, VotingEscrow.createLock, VotingEscrow.increaseAmount, VotingEscrow.totalSupply, VotingEscrow.totalSupplyAt, VotingEscrow.withdraw

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - LendingLedger.update_market: public/external function has no NatSpec annotation
  - LendingLedger.receive: public/external function has no NatSpec annotation
  - VotingEscrow.createLock: public/external function has no NatSpec annotation
  - VotingEscrow.increaseAmount: public/external function has no NatSpec annotation
  - VotingEscrow.withdraw: public/external function has no NatSpec annotation
  - VotingEscrow.balanceOfAt: public/external function has no NatSpec annotation
  - VotingEscrow.totalSupply: public/external function has no NatSpec annotation
  - VotingEscrow.totalSupplyAt: public/external function has no NatSpec annotation

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-implement-as-documented::src/LendingLedger.sol: req-3-implement-as-documented::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Documentation/NatSpec says claims are limited to prior epochs, but the code accrues rewards up to the current block and allows claiming them immediately, so behavior does not match documented logic.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 259s)._

## req-3-no-single-admin-eoa::src/LendingLedger.sol: req-3-no-single-admin-eoa::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Governance is a single address and controls critical functions without multisig or higher-privilege override; thus privileged actions can be executed by a single EOA, violating the requirement.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 211s)._

## req-3-external-calls::src/LendingLedger.sol: req-3-external-calls::src/LendingLedger.sol

**Requirement:** 

**Location(s):** GaugeController.vote_for_gauge_weights, LendingLedger.update_market

**Confidence:** MEDIUM

**Mechanism:** The requirement mandates documenting external calls and protecting them consistent with contract claims. vote_for_gauge_weights has no external call. update_market calls an external contract per-iteration but lacks NatSpec/README documentation of this dependency or protections; README merely counts external calls. Governance controls the target address but no explicit protection rationale is provided, so documentation/protection requirement is unmet.

**Supporting evidence:**
  - GaugeController.vote_for_gauge_weights: external call at node 5 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 8 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 28 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 29 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 31 followed by state write at node 46 (CFG-reachable)
  - GaugeController.vote_for_gauge_weights: external call at node 32 followed by state write at node 46 (CFG-reachable)
  - LendingLedger.update_market: external call at node 11 followed by state write at node 13 (CFG-reachable)
  - LendingLedger.update_market: external call at node 12 followed by state write at node 13 (CFG-reachable)

_Determined via graph-gated Codex investigation (1 graph queries, 297s)._

## req-3-consistent-solidity-output::src/LendingLedger.sol: req-3-consistent-solidity-output::src/LendingLedger.sol

**Requirement:** 

**Location(s):** pragma solidity^0.8.0, pragma solidity^0.8.1, pragma solidity^0.8.16

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - pragma solidity^0.8.0: pragma '^0.8.0' is a range, not an exact pin
  - pragma solidity^0.8.0: pragma '^0.8.0' is a range, not an exact pin
  - pragma solidity^0.8.0: pragma '^0.8.0' is a range, not an exact pin
  - pragma solidity^0.8.0: pragma '^0.8.0' is a range, not an exact pin
  - pragma solidity^0.8.1: pragma '^0.8.1' is a range, not an exact pin
  - pragma solidity^0.8.0: pragma '^0.8.0' is a range, not an exact pin
  - pragma solidity^0.8.16: pragma '^0.8.16' is a range, not an exact pin
  - pragma solidity^0.8.16: pragma '^0.8.16' is a range, not an exact pin
  - pragma solidity^0.8.16: pragma '^0.8.16' is a range, not an exact pin

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-check-new-bugs::src/LendingLedger.sol: req-R-check-new-bugs::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** The codebase pins solc 0.8.17 with via-IR. This version is affected by SOL-2023-3 (announced after Nov 1 2023) and other compiler bugs. No evidence of checks, documentation, or mitigations exists, nor is the compiler upgraded. Thus the requirement to check for and address new security bugs is not met.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 368s)._

## req-R-use-latest-compiler::src/LendingLedger.sol: req-R-use-latest-compiler::src/LendingLedger.sol

**Requirement:** 

**Location(s):** compiler config

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - compiler config: solc 0.8.17 != caller-supplied latest known stable version 0.8.36 (external, time-anchored reference -- not derived from spec text)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-define-license::src/LendingLedger.sol: req-R-define-license::src/LendingLedger.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/interface/Turnstile.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/ds-test/demo/demo.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/ds-test/src/test.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/ds-test/src/test.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/lib/ds-test/demo/demo.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/lib/ds-test/src/test.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/lib/ds-test/src/test.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/Base.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/Script.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdAssertions.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdChains.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdCheats.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdError.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdInvariant.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdJson.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdMath.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdStorage.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdStyle.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdUtils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/Test.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/Vm.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/console.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/console2.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC1155.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC165.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC4626.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IMulticall3.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdChains.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdCheats.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdError.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdStorage.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdStyle.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/compilation/CompilationScript.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/compilation/CompilationScriptBase.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/compilation/CompilationTest.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/compilation/CompilationTestBase.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/AccessControlDefaultAdminRulesHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/AccessControlHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/DoubleEndedQueueHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC20FlashMintHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC20PermitHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC20WrapperHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC3156FlashBorrowerHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC721Harness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC721ReceiverHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/EnumerableMapHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/EnumerableSetHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/InitializableHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/Ownable2StepHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/OwnableHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/PausableHarness.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/AccessControl.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/AccessControlCrossChain.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/AccessControlDefaultAdminRules.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/AccessControlEnumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/IAccessControl.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/IAccessControlDefaultAdminRules.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/IAccessControlEnumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/Ownable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/Ownable2Step.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/CrossChainEnabled.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/amb/CrossChainEnabledAMB.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/amb/LibAMB.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/arbitrum/CrossChainEnabledArbitrumL1.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/arbitrum/CrossChainEnabledArbitrumL2.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/arbitrum/LibArbitrumL1.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/arbitrum/LibArbitrumL2.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/errors.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/optimism/CrossChainEnabledOptimism.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/optimism/LibOptimism.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/polygon/CrossChainEnabledPolygonChild.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/finance/PaymentSplitter.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/finance/VestingWallet.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/Governor.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/IGovernor.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/TimelockController.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/compatibility/GovernorCompatibilityBravo.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/compatibility/IGovernorCompatibilityBravo.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorCountingSimple.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorPreventLateQuorum.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorProposalThreshold.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorSettings.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockCompound.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockControl.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotesComp.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotesQuorumFraction.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/IGovernorTimelock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/utils/IVotes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/utils/Votes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1155.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1155MetadataURI.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1155Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1271.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1363.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1363Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1363Spender.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC165.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1820Implementer.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1820Registry.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1967.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC20Metadata.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC2309.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC2612.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC2981.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC3156.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC3156FlashBorrower.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC3156FlashLender.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC4626.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC4906.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC5267.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC5313.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC5805.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC6372.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC721Enumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC721Metadata.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC721Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC777.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC777Recipient.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC777Sender.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC1822.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC2612.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/metatx/ERC2771Context.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/metatx/MinimalForwarder.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/AccessControlCrossChainMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ArraysMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/CallReceiverMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ConditionalEscrowMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ContextMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/DummyImplementation.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/EIP712Verifier.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC1271WalletMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165MaliciousData.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165MissingData.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165NotSupported.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165ReturnBomb.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC20Mock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC20Reentrant.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC2771ContextMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC3156FlashBorrowerMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC4626Mock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/EtherReceiverMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/InitializableMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/MulticallTest.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/MultipleInheritanceInitializableMocks.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/PausableMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/PullPaymentMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ReentrancyAttack.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ReentrancyMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/RegressionImplementation.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/SafeMathMemoryCheck.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/SingleInheritanceInitializableMocks.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/StorageSlotMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/TimelockReentrant.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/TimersBlockNumberImpl.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/TimersTimestampImpl.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/VotesMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/compound/CompTimelock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/crosschain/bridges.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/crosschain/receivers.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/ERC4626Fees.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/governance/MyGovernor.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/governance/MyToken.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/governance/MyTokenTimestampBased.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/governance/MyTokenWrapped.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorCompMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorCompatibilityBravoMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorPreventLateQuorumMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockCompoundMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockControlMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorVoteMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorWithParamsMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/proxy/BadBeacon.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/proxy/ClashingImplementation.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/proxy/UUPSLegacy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/proxy/UUPSUpgradeableMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC1155ReceiverMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20DecimalsMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ExcessDecimalsMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20FlashMintMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ForceApproveMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20MulticallMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20NoReturnMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20PermitNoRevertMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ReturnFalseMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20VotesLegacyMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC4626OffsetMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC4646FeesMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ConsecutiveEnumerableMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ConsecutiveMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ReceiverMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC721URIStorageMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC777Mock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC777SenderRecipientMock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/VotesTimestamp.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/wizard/MyGovernor1.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/wizard/MyGovernor2.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/wizard/MyGovernor3.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/Clones.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Upgrade.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/Proxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/beacon/BeaconProxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/beacon/IBeacon.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/beacon/UpgradeableBeacon.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/transparent/ProxyAdmin.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/transparent/TransparentUpgradeableProxy.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/utils/Initializable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/utils/UUPSUpgradeable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/security/Pausable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/security/PullPayment.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/security/ReentrancyGuard.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/ERC1155.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/IERC1155.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/IERC1155Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Burnable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Pausable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Supply.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155URIStorage.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/IERC1155MetadataURI.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/presets/ERC1155PresetMinterPauser.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Capped.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20FlashMint.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Pausable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Permit.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Snapshot.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Votes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20VotesComp.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Wrapper.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC4626.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Permit.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/draft-ERC20Permit.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/draft-IERC20Permit.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/presets/ERC20PresetFixedSupply.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/presets/ERC20PresetMinterPauser.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/utils/TokenTimelock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/ERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/IERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/IERC721Receiver.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Burnable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Consecutive.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Enumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Pausable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Royalty.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721URIStorage.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Votes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Wrapper.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/IERC721Enumerable.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/IERC721Metadata.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/draft-ERC721Votes.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/presets/ERC721PresetMinterPauserAutoId.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/utils/ERC721Holder.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/ERC777.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/IERC777.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/IERC777Recipient.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/IERC777Sender.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/presets/ERC777PresetFixedSupply.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/common/ERC2981.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Address.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Arrays.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Base64.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Checkpoints.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Context.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Counters.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Create2.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Multicall.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/ShortStrings.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Strings.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Timers.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/ECDSA.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/EIP712.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/MerkleProof.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/SignatureChecker.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/draft-EIP712.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/escrow/ConditionalEscrow.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/escrow/Escrow.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/escrow/RefundEscrow.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165Checker.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165Storage.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/ERC1820Implementer.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/IERC165.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/IERC1820Implementer.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/IERC1820Registry.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/SafeMath.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/SignedMath.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/SignedSafeMath.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/structs/BitMaps.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/structs/DoubleEndedQueue.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/amb/IAMB.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IArbSys.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IBridge.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IDelayedMessageProvider.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IInbox.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IOutbox.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/compound/ICompoundTimelock.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/optimism/ICrossDomainMessenger.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/polygon/IFxMessageProcessor.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/erc4626-tests/ERC4626.prop.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/erc4626-tests/ERC4626.test.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/lib/ds-test/demo/demo.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/lib/ds-test/src/test.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/lib/ds-test/src/test.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/Base.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/Script.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdAssertions.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdChains.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdCheats.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdError.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdInvariant.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdJson.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdMath.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdStorage.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdStyle.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdUtils.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/Test.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/Vm.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/console.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/console2.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC1155.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC165.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC20.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC4626.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC721.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IMulticall3.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdChains.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdError.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdStyle.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationScript.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationScriptBase.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationTest.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationTestBase.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/governance/Governor.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/GaugeController.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/LendingLedger.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/VotingEscrow.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/GaugeController.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/LendingLedger.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/VotingEscrow.t.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/utils/Console.sol, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/utils/Utilities.sol

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/interface/Turnstile.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/ds-test/demo/demo.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/ds-test/src/test.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/ds-test/src/test.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/lib/ds-test/demo/demo.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/lib/ds-test/src/test.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/lib/ds-test/src/test.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/Base.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/Script.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdAssertions.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdChains.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdCheats.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdError.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdInvariant.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdJson.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdMath.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdStorage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdStyle.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/StdUtils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/Test.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/Vm.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/console.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/console2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC4626.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/src/interfaces/IMulticall3.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdChains.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdCheats.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdError.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdStorage.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdStyle.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/compilation/CompilationScript.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/compilation/CompilationScriptBase.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/compilation/CompilationTest.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/compilation/CompilationTestBase.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/AccessControlDefaultAdminRulesHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/AccessControlHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/DoubleEndedQueueHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC20FlashMintHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC20PermitHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC20WrapperHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC3156FlashBorrowerHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC721Harness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/ERC721ReceiverHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/EnumerableMapHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/EnumerableSetHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/InitializableHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/Ownable2StepHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/OwnableHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/harnesses/PausableHarness.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/AccessControl.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/AccessControlCrossChain.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/AccessControlDefaultAdminRules.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/AccessControlEnumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/IAccessControl.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/IAccessControlDefaultAdminRules.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/IAccessControlEnumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/Ownable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/access/Ownable2Step.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/CrossChainEnabled.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/amb/CrossChainEnabledAMB.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/amb/LibAMB.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/arbitrum/CrossChainEnabledArbitrumL1.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/arbitrum/CrossChainEnabledArbitrumL2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/arbitrum/LibArbitrumL1.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/arbitrum/LibArbitrumL2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/errors.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/optimism/CrossChainEnabledOptimism.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/optimism/LibOptimism.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/crosschain/polygon/CrossChainEnabledPolygonChild.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/finance/PaymentSplitter.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/finance/VestingWallet.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/Governor.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/IGovernor.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/TimelockController.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/compatibility/GovernorCompatibilityBravo.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/compatibility/IGovernorCompatibilityBravo.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorCountingSimple.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorPreventLateQuorum.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorProposalThreshold.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorSettings.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockCompound.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorTimelockControl.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotesComp.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/GovernorVotesQuorumFraction.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/extensions/IGovernorTimelock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/utils/IVotes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/governance/utils/Votes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1155MetadataURI.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1155Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1271.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1363.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1363Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1363Spender.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1820Implementer.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1820Registry.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC1967.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC20Metadata.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC2309.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC2612.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC2981.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC3156.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC3156FlashBorrower.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC3156FlashLender.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC4626.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC4906.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC5267.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC5313.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC5805.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC6372.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC721Enumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC721Metadata.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC721Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC777.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC777Recipient.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/IERC777Sender.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC1822.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/interfaces/draft-IERC2612.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/metatx/ERC2771Context.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/metatx/MinimalForwarder.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/AccessControlCrossChainMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ArraysMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/CallReceiverMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ConditionalEscrowMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ContextMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/DummyImplementation.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/EIP712Verifier.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC1271WalletMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165MaliciousData.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165MissingData.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165NotSupported.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC165/ERC165ReturnBomb.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC20Mock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC20Reentrant.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC2771ContextMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC3156FlashBorrowerMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ERC4626Mock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/EtherReceiverMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/InitializableMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/MulticallTest.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/MultipleInheritanceInitializableMocks.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/PausableMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/PullPaymentMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ReentrancyAttack.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/ReentrancyMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/RegressionImplementation.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/SafeMathMemoryCheck.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/SingleInheritanceInitializableMocks.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/StorageSlotMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/TimelockReentrant.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/TimersBlockNumberImpl.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/TimersTimestampImpl.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/VotesMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/compound/CompTimelock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/crosschain/bridges.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/crosschain/receivers.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/ERC4626Fees.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/governance/MyGovernor.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/governance/MyToken.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/governance/MyTokenTimestampBased.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/docs/governance/MyTokenWrapped.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorCompMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorCompatibilityBravoMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorPreventLateQuorumMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockCompoundMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorTimelockControlMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorVoteMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/governance/GovernorWithParamsMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/proxy/BadBeacon.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/proxy/ClashingImplementation.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/proxy/UUPSLegacy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/proxy/UUPSUpgradeableMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC1155ReceiverMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20DecimalsMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ExcessDecimalsMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20FlashMintMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ForceApproveMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20MulticallMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20NoReturnMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20PermitNoRevertMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20ReturnFalseMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC20VotesLegacyMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC4626OffsetMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC4646FeesMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ConsecutiveEnumerableMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ConsecutiveMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC721ReceiverMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC721URIStorageMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC777Mock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/ERC777SenderRecipientMock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/token/VotesTimestamp.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/wizard/MyGovernor1.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/wizard/MyGovernor2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/mocks/wizard/MyGovernor3.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/Clones.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Upgrade.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/Proxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/beacon/BeaconProxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/beacon/IBeacon.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/beacon/UpgradeableBeacon.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/transparent/ProxyAdmin.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/transparent/TransparentUpgradeableProxy.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/utils/Initializable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/proxy/utils/UUPSUpgradeable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/security/Pausable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/security/PullPayment.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/security/ReentrancyGuard.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/ERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/IERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/IERC1155Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Burnable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Pausable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Supply.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155URIStorage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/extensions/IERC1155MetadataURI.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/presets/ERC1155PresetMinterPauser.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Capped.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20FlashMint.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Pausable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Permit.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Snapshot.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Votes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20VotesComp.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Wrapper.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC4626.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Permit.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/draft-ERC20Permit.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/draft-IERC20Permit.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/presets/ERC20PresetFixedSupply.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/presets/ERC20PresetMinterPauser.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC20/utils/TokenTimelock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/ERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/IERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/IERC721Receiver.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Burnable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Consecutive.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Enumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Pausable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Royalty.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721URIStorage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Votes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Wrapper.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/IERC721Enumerable.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/IERC721Metadata.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/extensions/draft-ERC721Votes.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/presets/ERC721PresetMinterPauserAutoId.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC721/utils/ERC721Holder.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/ERC777.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/IERC777.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/IERC777Recipient.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/IERC777Sender.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/ERC777/presets/ERC777PresetFixedSupply.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/token/common/ERC2981.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Address.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Arrays.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Base64.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Checkpoints.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Context.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Counters.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Create2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Multicall.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/ShortStrings.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Strings.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/Timers.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/ECDSA.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/EIP712.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/MerkleProof.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/SignatureChecker.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/cryptography/draft-EIP712.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/escrow/ConditionalEscrow.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/escrow/Escrow.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/escrow/RefundEscrow.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165Checker.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/ERC165Storage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/ERC1820Implementer.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/IERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/IERC1820Implementer.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/introspection/IERC1820Registry.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/Math.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/SafeMath.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/SignedMath.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/math/SignedSafeMath.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/structs/BitMaps.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/structs/DoubleEndedQueue.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/amb/IAMB.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IArbSys.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IBridge.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IDelayedMessageProvider.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IInbox.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/arbitrum/IOutbox.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/compound/ICompoundTimelock.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/optimism/ICrossDomainMessenger.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/contracts/vendor/polygon/IFxMessageProcessor.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/erc4626-tests/ERC4626.prop.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/erc4626-tests/ERC4626.test.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/lib/ds-test/demo/demo.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/lib/ds-test/src/test.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/lib/ds-test/src/test.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/Base.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/Script.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdAssertions.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdChains.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdCheats.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdError.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdInvariant.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdJson.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdMath.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdStorage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdStyle.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/StdUtils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/Test.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/Vm.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/console.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/console2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC4626.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/src/interfaces/IMulticall3.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdChains.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdError.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdStorage.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdStyle.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationScript.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationScriptBase.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationTest.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/compilation/CompilationTestBase.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/governance/Governor.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/GaugeController.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/LendingLedger.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/VotingEscrow.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/GaugeController.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/LendingLedger.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/VotingEscrow.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/utils/Console.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/src/test/utils/Utilities.sol: SPDX-License-Identifier found

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-notify-news::src/LendingLedger.sol: req-R-notify-news::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** Reviewed README and scoped files; no responsible disclosure guidance exists for reporting vulnerabilities to a working group. Vendor dependency SECURITY.md does not cover this project, so the requirement is unmet.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 149s)._

## req-R-fuzzing-in-testing::src/LendingLedger.sol: req-R-fuzzing-in-testing::src/LendingLedger.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdChains.t.sol:testRpc, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdCheats.t.sol:testAssumeNoPrecompiles, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdCheats.t.sol:testAssumePayable, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testBound, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testBoundInt, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdChains.t.sol:testRpc, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testAssumeNoPrecompiles, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testAssumePayable, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBound, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBoundInt, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testInvalidDescriptionForProposer, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testValidDescriptionForProposer, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol:testLookup, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol:testPush, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthShort, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthWithFallback, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRevertLong, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripShort, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripWithFallback, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testCeilDiv, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog10, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog2, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog256, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDiv, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDivDomain, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSqrt

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdChains.t.sol:testRpc: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdCheats.t.sol:testAssumeNoPrecompiles: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdCheats.t.sol:testAssumePayable: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testBound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testBoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdChains.t.sol:testRpc: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testAssumeNoPrecompiles: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testAssumePayable: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testValidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testInvalidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRevertLong: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testCeilDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSqrt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog10: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDivDomain: Foundry-convention parameterized test function (fuzzed by forge test)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-formal-verification::src/LendingLedger.sol: req-R-formal-verification::src/LendingLedger.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/AccessControl.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/AccessControlDefaultAdminRules.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/DoubleEndedQueue.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/ERC20.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/ERC20FlashMint.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/ERC20Wrapper.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/ERC721.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/EnumerableMap.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/EnumerableSet.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/Initializable.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/Ownable.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/Ownable2Step.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/Pausable.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/TimelockController.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/helpers/helpers.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IAccessControl.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IAccessControlDefaultAdminRules.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC20.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC2612.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC3156.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC5313.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC721.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IOwnable.spec, /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IOwnable2Step.spec

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/AccessControl.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/Pausable.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/ERC20Wrapper.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/ERC20.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/Ownable2Step.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/Ownable.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/Initializable.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/DoubleEndedQueue.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/TimelockController.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/ERC20FlashMint.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/EnumerableMap.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/EnumerableSet.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/AccessControlDefaultAdminRules.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/ERC721.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/helpers/helpers.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC2612.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC5313.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IOwnable.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC3156.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC20.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IAccessControlDefaultAdminRules.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IAccessControl.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IERC721.spec: Certora spec file present
  - /scratch/md5344/.claude/jobs/318205ae/tmp/audit_diversity/2024-01-canto/lib/openzeppelin-contracts/certora/specs/methods/IOwnable2Step.spec: Certora spec file present

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-multisig-threshold::src/LendingLedger.sol: req-R-multisig-threshold::src/LendingLedger.sol

**Requirement:** 

**Location(s):** 2024-01-canto, LendingLedger.sol, LendingLedger.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Privileged actions (set governance, rewards, whitelist markets, add/remove gauges) are restricted only by `msg.sender == governance`, a single address. There is no multisignature or threshold mechanism anywhere, and docs assume trusted governance. Requirement recommends avoiding 1-of-N or single-signer control; current design uses single-signer, so it fails the recommendation.

**Supporting evidence:**
  - README.md: # Canto Invitational audit details

- Total Prize Pool: $16,425 
  - HM awards: $12,285 
  - Analysis awards: $683 
  - QA awards: $341 
  - Gas awards: $341 
  - Judge awards: $2,275 
  - Scout awards: $500 
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2024-01-canto-invitational/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts January 25, 2024 20:00 UTC
- Ends January 29,2024 20:00 UTC
- ❗️Awarding Note for Wardens, Judges, and Lookouts: If you want to claim your awards in $ worth of CANTO, you must follow the steps outlined in this [thread](https://discord.com/channels/810916927919620096/1199083429174718464/1199722579259310100); otherwise you'll be paid out in USDC.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-01-canto/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

Risks deemed acceptable:

- Everything related to governance / centralization abuse: We assume that governance is non-malicious.

# Overview

## Links

- **Previous audits:** <https://code4rena.com/audits/2023-08-verwa>
- **Documentation:** <https://code4rena.com/audits/2023-08-verwa> and below

# Scope

*See [scope.txt](https://github.com/code-423n4/2024-01-canto/blob/main/scope.txt)*

| Contract | SLOC | Purpose | Libraries used |  
| ----------- | ----------- | ----------- | ----------- |
| [src/LendingLedger.sol](https://github.com/code-423n4/2024-01-canto/blob/main/src/LendingLedger.sol) | 106 | Implements the bookkeeping for the rewards and is used for claiming. Moreover, provides data for third-party contracts that want to use this information for secondary rewards | [`@openzeppelin/*`](https://openzeppelin.com/contracts/) |

## Out of scope

All other contracts and interfaces, namely `src/GaugeController.sol`, `src/VotingEscrow.sol`, `interface/Turnstile.sol`, and all tests (`src/test/`).

# Additional Context

Since the previous audit, the `LendingLedger` logic was completely rewritten. We now use an approach that is very similar to [MasterChef / Synthetix](https://www.rareskills.io/post/staking-algorithm). The main motivation for doing that was to enable users to claim accrued rewards whenever they want (instead of only after a week / epoch has passed). Moreover, we also introduced the field `secRewardDebt`. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The code will only be deployed to CANTO.

The only trusted role is the governance address. Only this address can set the rewards per block.

## Attack ideas (Where to look for bugs)

Miscalculations / significant rounding errors

## Main invariants

The total rewards that are sent for one block should never be higher than the rewards that were configured for this block.

## Scoping Details

```
- If you have a public code repo, please share it here:  
- How many contracts are in scope?:   1
- Total SLoC for these contracts?:  107
- How many external imports are there?: 4 
- How many separate interfaces and struct definitions are there for the contracts within scope?:  2
- Does most of your code generally use composition or inheritance?:   Composition
- How many external calls?:   1
- What is the overall line coverage percentage provided by your tests?: 94
- Is this an upgrade of an existing system?: True - LendingLedger of the already audited veRWA (https://code4rena.com/audits/2023-08-verwa) was rewritten. It now supports per-block claiming (vs. per-epoch previously) and we expose data in the contract that enables secondary rewards (i.e. for other systems to incentivize deposits with their own tokens)
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): 
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:   True
- Please describe required context:  The changes since the last audit only affect one contract and are isolated, but it can be helpful for context to look at the overall system, which was described in the previous audit (https://code4rena.com/audits/2023-08-verwa) 
- Does it use an oracle?:  No
- Describe any novel or unique curve logic or mathematical models your code uses: The staking logic is adapted from Sushi / Synthetix: https://www.rareskills.io/post/staking-algorithm
- Is this either a fork of or an alternate implementation of another project?:   True
- Does it use a side-chain?: 
- Describe any specific areas you would like addressed:
```

# Setup and test instructions

```bash
# Cloning with recurse
git clone --recurse https://github.com/code-423n4/2024-01-canto.git
# Going into the contest directory
cd 2024-01-canto
# Installing npm dependencies
npm install
# Installing forge dependencies in case --recurse was forgotten when cloning
forge install
# Compiling
forge build
# Testing
forge test
# Generating gas report
forge test --gas-report
# Running coverage with minimum-IR (Stack too deep otherwise)
forge coverage --ir-minimum
# Generating lcov report file (keep in mind that the result will be a bit off when displaying the result such as with the Coverage Gutters extension on VSCode due to --ir-minimum).
forge coverage --ir-minimum --report lcov
# Running slither (alternatively, see the provided "slither.txt" file)
slither .
```

## Miscellaneous

Canto contributors that were involved in the creation of Neofinance Coordinator and their family members are ineligible to participate in this audit.

  - LendingLedger.sol (NatSpec): /// @dev Info for each user.
  - LendingLedger.sol (NatSpec): /// @dev Info of each lending market.
  - LendingLedger.sol (NatSpec): /// @dev Lending Market => Epoch => Balance
  - LendingLedger.sol (NatSpec): /// @notice Set governance address
    /// @param _governance New governance address
  - LendingLedger.sol (NatSpec): /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
  - LendingLedger.sol (NatSpec): /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
  - LendingLedger.sol (NatSpec): /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
  - LendingLedger.sol: // SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.16;

import {VotingEscrow} from "./VotingEscrow.sol";
import {GaugeController} from "./GaugeController.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LendingLedger {
    // Constants
    uint256 public constant BLOCK_EPOCH = 100_000; // 100000 blocks, roughly 1 week

    // State
    address public governance;
    GaugeController public gaugeController;
    mapping(address => bool) public lendingMarketWhitelist;

    /// @dev Info for each user.
    struct UserInfo {
        uint256 amount; // Amount of cNOTE that the user has provided.
        int256 rewardDebt; // Amount of CANTO entitled to the user.
        int256 secRewardDebt; // Amount of secondary rewards entitled to the user.
    }

    /// @dev Info of each lending market.
    struct MarketInfo {
        uint128 accCantoPerShare;
        uint128 secRewardsPerShare;
        uint64 lastRewardBlock;
    }

    mapping(address => mapping(address => UserInfo)) public userInfo; // Info of each user for the different lending markets
    mapping(address => MarketInfo) public marketInfo; // Info of each lending market

    mapping(uint256 => uint256) public cantoPerBlock; // CANTO per block for each epoch

    /// @dev Lending Market => Epoch => Balance
    mapping(address => uint256) public lendingMarketTotalBalance; // Total balance locked within the market

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    constructor(address _gaugeController, address _governance) {
        gaugeController = GaugeController(_gaugeController);
        governance = _governance;
    }

    /// @notice Set governance address
    /// @param _governance New governance address
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function update_market(address _market) public {
        require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = i + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    uint256 cantoReward = (blockDelta *
                        cantoPerBlock[epoch] *
                        gaugeController.gauge_relative_weight_write(_market, epoch)) / 1e18;
                    market.accCantoPerShare += uint128((cantoReward * 1e18) / marketSupply);
                    market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply); // TODO: Scaling
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }

    /// @notice Function that is called by the lending market on cNOTE deposits / withdrawals
    /// @param _lender The address of the lender
    /// @param _delta The amount of cNote deposited (positive) or withdrawn (negative)
    function sync_ledger(address _lender, int256 _delta) external {
        address lendingMarket = msg.sender;
        update_market(lendingMarket); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[lendingMarket];
        UserInfo storage user = userInfo[lendingMarket][_lender];

        if (_delta >= 0) {
            user.amount += uint256(_delta);
            user.rewardDebt += int256((uint256(_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt += int256((uint256(_delta) * market.secRewardsPerShare) / 1e18);
        } else {
            user.amount -= uint256(-_delta);
            user.rewardDebt -= int256((uint256(-_delta) * market.accCantoPerShare) / 1e18);
            user.secRewardDebt -= int256((uint256(-_delta) * market.secRewardsPerShare) / 1e18);
        }
        int256 updatedMarketBalance = int256(lendingMarketTotalBalance[lendingMarket]) + _delta;
        require(updatedMarketBalance >= 0, "Market balance underflow"); // Sanity check performed here, but the market should ensure that this never happens
        lendingMarketTotalBalance[lendingMarket] = uint256(updatedMarketBalance);
    }

    /// @notice Claim the CANTO for a given market. Can only be performed for prior (i.e. finished) epochs, not the current one
    /// @param _market Address of the market
    function claim(address _market) external {
        update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }

    /// @notice Used by governance to set the overall CANTO rewards per epoch
    /// @param _fromEpoch From which epoch (provided as block number) to set the rewards from
    /// @param _toEpoch Until which epoch (provided as block number) to set the rewards to
    /// @param _amountPerBlock The amount per block
    function setRewards(
        uint256 _fromEpoch,
        uint256 _toEpoch,
        uint256 _amountPerBlock
    ) external onlyGovernance {
        require(_fromEpoch % BLOCK_EPOCH == 0 && _toEpoch % BLOCK_EPOCH == 0, "Invalid block number");
        for (uint256 i = _fromEpoch; i <= _toEpoch; i += BLOCK_EPOCH) {
            cantoPerBlock[i] = _amountPerBlock;
        }
    }

    /// @notice Used by governance to whitelist a lending market
    /// @param _market Address of the market to whitelist
    /// @param _isWhiteListed Whether the market is whitelisted or not
    function whiteListLendingMarket(address _market, bool _isWhiteListed) external onlyGovernance {
        require(lendingMarketWhitelist[_market] != _isWhiteListed, "No change");
        lendingMarketWhitelist[_market] = _isWhiteListed;
        if (_isWhiteListed) {
            marketInfo[_market].lastRewardBlock = uint64(block.number);
        }
    }

    receive() external payable {}
}

  - 2024-01-canto: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 157s)._
