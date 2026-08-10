# Security Audit Report: 2026-01-tempo-feeamm

Findings below were produced by the RTF (Requirement Translation Framework) pipeline: EthTrust requirement routing, deterministic evidence collection, bounded LLM judgment, and (where the bounded judgment was inconclusive, insufficient, or low-confidence) graph-gated Codex investigation.

## req-1-eip155-chainid::contracts/FeeAMM.sol: req-1-eip155-chainid::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM.getPoolId

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - FeeAMM.getPoolId: keccak256() call at node 1: block.chainid is NOT read in the same expression -- whether this is a transaction/signature-authorization hash at all is NOT determined here (blocked applicability component, see this requirement's own L5 record)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-1-use-c-e-i::contracts/FeeAMM.sol: req-1-use-c-e-i::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM.burn, FeeAMM.executeFeeSwap, FeeAMM.mint

**Confidence:** HIGH

**Mechanism:** Multiple functions (burn, executeFeeSwap, mint) perform external ERC20 transfers before updating contract state, lacking CEI and any reentrancy guard; thus the requirement to use Checks-Effects-Interactions for external calls is not met.

**Supporting evidence:**
  - FeeAMM.executeFeeSwap: external call at node 7 followed by state write at node 8 (CFG-reachable)
  - FeeAMM.mint: external call at node 20 followed by state write at node 23 (CFG-reachable)
  - FeeAMM.burn: external call at node 11 followed by state write at node 13 (CFG-reachable)
  - FeeAMM.burn: external call at node 12 followed by state write at node 13 (CFG-reachable)

_Determined via graph-gated Codex investigation (1 graph queries, 75s)._

## req-1-compiler-060::contracts/FeeAMM.sol: req-1-compiler-060::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** compiler config

**Confidence:** HIGH

**Mechanism:** Build config and contract pragma both target Solidity 0.7.6 (<0.8.0). No evidence of satisfying all overriding EthTrust requirements for older compilers, so the modern compiler requirement is not met.

**Supporting evidence:**
  - compiler config: solc 0.7.6 < required floor 0.8.0

_Determined via graph-gated Codex investigation (0 graph queries, 77s)._

## req-2-pass-l1::contracts/FeeAMM.sol: req-2-pass-l1::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-external-calls::contracts/FeeAMM.sol: req-2-external-calls::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM.burn, FeeAMM.executeFeeSwap, FeeAMM.mint

**Confidence:** HIGH

**Mechanism:** FeeAMM calls arbitrary ERC20 addresses supplied by users, violating the requirement that all external calls target tested contracts under common control. Functions lack CEI-equivalent protection: burn performs interactions before internal state changes and no reentrancy guard is used, creating reentrancy exposure from malicious tokens. Thus external call protection requirement is not met.

**Supporting evidence:**
  - FeeAMM.executeFeeSwap: external call at node 7 followed by state write at node 8 (CFG-reachable)
  - FeeAMM.mint: external call at node 20 followed by state write at node 23 (CFG-reachable)
  - FeeAMM.burn: external call at node 11 followed by state write at node 13 (CFG-reachable)
  - FeeAMM.burn: external call at node 12 followed by state write at node 13 (CFG-reachable)

_Determined via graph-gated Codex investigation (0 graph queries, 68s)._

## req-2-documented::contracts/FeeAMM.sol: req-2-documented::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM._calculateBurnAmounts, FeeAMM.burn, FeeAMM.checkSufficientLiquidity, FeeAMM.executeFeeSwap, FeeAMM.mint, FeeAMM.rebalanceSwap

**Confidence:** HIGH

**Mechanism:** Requirement demands documentation for external calls and potential overflow/underflow areas. FeeAMM uses multiple ERC20 external calls and unchecked arithmetic in Solidity 0.7.6, but the contract and repository contain no comments or documentation justifying these uses, so the requirement is not met.

**Supporting evidence:**
  - FeeAMM.executeFeeSwap: makes an external call
  - FeeAMM.executeFeeSwap: makes an external call
  - FeeAMM.rebalanceSwap: makes an external call
  - FeeAMM.rebalanceSwap: makes an external call
  - FeeAMM.mint: makes an external call
  - FeeAMM.burn: makes an external call
  - FeeAMM.burn: makes an external call
  - FeeAMM.checkSufficientLiquidity: * operation, inside unchecked{} block
  - FeeAMM.executeFeeSwap: * operation, inside unchecked{} block
  - FeeAMM.executeFeeSwap: + operation, inside unchecked{} block
  - FeeAMM.executeFeeSwap: - operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: * operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: + operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: + operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: + operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: - operation, inside unchecked{} block
  - FeeAMM.mint: - operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.mint: * operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.mint: * operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.burn: - operation, inside unchecked{} block
  - FeeAMM.burn: - operation, inside unchecked{} block
  - FeeAMM.burn: - operation, inside unchecked{} block
  - FeeAMM.burn: - operation, inside unchecked{} block
  - FeeAMM._calculateBurnAmounts: * operation, inside unchecked{} block
  - FeeAMM._calculateBurnAmounts: * operation, inside unchecked{} block

_Determined via graph-gated Codex investigation (1 graph queries, 147s)._

## req-2-check-rounding::contracts/FeeAMM.sol: req-2-check-rounding::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM._calculateBurnAmounts, FeeAMM.checkSufficientLiquidity, FeeAMM.executeFeeSwap, FeeAMM.mint, FeeAMM.rebalanceSwap

**Confidence:** MEDIUM

**Mechanism:** Core operations floor divisions without documenting error bounds; dust can accumulate and shift value, violating the requirement for documented and protected rounding behavior.

**Supporting evidence:**
  - FeeAMM.checkSufficientLiquidity: division operation (potential rounding)
  - FeeAMM.executeFeeSwap: division operation (potential rounding)
  - FeeAMM.rebalanceSwap: division operation (potential rounding)
  - FeeAMM.mint: division operation (potential rounding)
  - FeeAMM.mint: division operation (potential rounding)
  - FeeAMM.mint: division operation (potential rounding)
  - FeeAMM.mint: division operation (potential rounding)
  - FeeAMM._calculateBurnAmounts: division operation (potential rounding)
  - FeeAMM._calculateBurnAmounts: division operation (potential rounding)

_Determined via graph-gated Codex investigation (1 graph queries, 244s)._

## req-2-overflow-underflow::contracts/FeeAMM.sol: req-2-overflow-underflow::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM._calculateBurnAmounts, FeeAMM.burn, FeeAMM.checkSufficientLiquidity, FeeAMM.executeFeeSwap, FeeAMM.mint, FeeAMM.rebalanceSwap

**Confidence:** MEDIUM

**Mechanism:** The contract uses Solidity 0.7.6 with no overflow checks. In _calculateBurnAmounts, user-controlled liquidity is multiplied by pool reserves (uint128) and divided by totalSupply, with no bounds to ensure the product fits in uint256, and totalSupply/liquidity can grow unchecked via mint. Therefore overflow is possible, violating the requirement.

**Supporting evidence:**
  - FeeAMM.checkSufficientLiquidity: * operation, inside unchecked{} block
  - FeeAMM.executeFeeSwap: * operation, inside unchecked{} block
  - FeeAMM.executeFeeSwap: + operation, inside unchecked{} block
  - FeeAMM.executeFeeSwap: - operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: * operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: + operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: + operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: + operation, inside unchecked{} block
  - FeeAMM.rebalanceSwap: - operation, inside unchecked{} block
  - FeeAMM.mint: - operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.mint: * operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.mint: * operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.mint: + operation, inside unchecked{} block
  - FeeAMM.burn: - operation, inside unchecked{} block
  - FeeAMM.burn: - operation, inside unchecked{} block
  - FeeAMM.burn: - operation, inside unchecked{} block
  - FeeAMM.burn: - operation, inside unchecked{} block
  - FeeAMM._calculateBurnAmounts: * operation, inside unchecked{} block
  - FeeAMM._calculateBurnAmounts: * operation, inside unchecked{} block

_Determined via graph-gated Codex investigation (1 graph queries, 120s)._

## req-2-compiler-060::contracts/FeeAMM.sol: req-2-compiler-060::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** compiler config

**Confidence:** HIGH

**Mechanism:** The only tested contract, FeeAMM, declares pragma >=0.7.6 <0.8.0 and the Foundry configuration pins solc 0.7.6, which is older than 0.8.0. No evidence of satisfying the overriding requirement (Compiler Bug Check Constructor Payment) is present. Therefore the tested code violates the modern compiler requirement.

**Supporting evidence:**
  - compiler config: solc 0.7.6 < required floor 0.8.0

_Determined via graph-gated Codex investigation (1 graph queries, 97s)._

## req-3-pass-l2::contracts/FeeAMM.sol: req-3-pass-l2::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-block-front-running::contracts/FeeAMM.sol: req-3-block-front-running::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** 2026-01-tempo-feeamm, FeeAMM.sol, FeeAMM.sol (NatSpec)

**Confidence:** MEDIUM

**Mechanism:** All AMM operations rely on mutable reserves and expose no anti-ordering controls (deadlines, slippage/min-out, commit-reveal). Transaction ordering can change reserves before execution, enabling front-running/sandwiching to alter outcomes or cause reverts, so requirement is not met.

**Supporting evidence:**
  - FeeAMM.sol (NatSpec): /**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
  - FeeAMM.sol: // SPDX-License-Identifier: MIT OR Apache-2.0
pragma solidity >=0.7.6 <0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
contract FeeAMM {
    uint256 public constant M = 9970;
    uint256 public constant N = 9985;
    uint256 public constant SCALE = 10_000;
    uint256 public constant MIN_LIQUIDITY = 1000;

    struct Pool {
        uint128 reserveUserToken;
        uint128 reserveValidatorToken;
    }

    event Mint(
        address indexed sender,
        address indexed to,
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        uint256 liquidity
    );

    event Burn(
        address indexed sender,
        address userToken,
        address validatorToken,
        uint256 amountUserToken,
        uint256 amountValidatorToken,
        uint256 liquidity,
        address indexed to
    );

    event RebalanceSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    event FeeSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => uint256) public totalSupply;
    mapping(bytes32 => mapping(address => uint256)) public liquidityBalances;

    function _requireU128(uint256 x) internal pure {
        require(x <= type(uint128).max, "INVALID_AMOUNT");
    }

    function getPoolId(
        address userToken,
        address validatorToken
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(userToken, validatorToken));
    }

    function getPool(
        address userToken,
        address validatorToken
    ) external view returns (Pool memory) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        return pools[poolId];
    }

    function checkSufficientLiquidity(
        address userToken,
        address validatorToken,
        uint256 maxAmount
    ) external view {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        uint256 amountOutNeeded = (maxAmount * M) / SCALE;
        require(
            pools[poolId].reserveValidatorToken >= amountOutNeeded,
            "INSUFFICIENT_LIQUIDITY"
        );
    }

    function executeFeeSwap(
        address userToken,
        address validatorToken,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        Pool storage pool = pools[poolId];

        amountOut = (amountIn * M) / SCALE;

        _requireU128(amountIn);
        _requireU128(amountOut);

        require(
            pool.reserveValidatorToken >= amountOut,
            "INSUFFICIENT_LIQUIDITY"
        );

        IERC20(userToken).transferFrom(msg.sender, address(this), amountIn);

        pool.reserveUserToken += uint128(amountIn);
        pool.reserveValidatorToken -= uint128(amountOut);

        IERC20(validatorToken).transfer(msg.sender, amountOut);

        emit FeeSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function rebalanceSwap(
        address userToken,
        address validatorToken,
        uint256 amountOut,
        address to
    ) external returns (uint256 amountIn) {
        require(amountOut != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        amountIn = (amountOut * N) / SCALE + 1;

        Pool storage pool = pools[poolId];

        _requireU128(amountOut);
        _requireU128(amountIn);

        if (
            uint256(pool.reserveValidatorToken) + amountIn > type(uint128).max
        ) {
            revert("INSUFFICIENT_RESERVES");
        }

        require(pool.reserveUserToken >= amountOut, "INVALID_AMOUNT");

        pool.reserveValidatorToken += uint128(amountIn);
        pool.reserveUserToken -= uint128(amountOut);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountIn
        );
        IERC20(userToken).transfer(to, amountOut);

        emit RebalanceSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function mint(
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        address to
    ) external returns (uint256 liquidity) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(amountValidatorToken != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];
        uint256 _totalSupply = totalSupply[poolId];

        if (pool.reserveUserToken == 0 && pool.reserveValidatorToken == 0) {
            if (amountValidatorToken / 2 <= MIN_LIQUIDITY) {
                revert("INSUFFICIENT_LIQUIDITY");
            }
            liquidity = amountValidatorToken / 2 - MIN_LIQUIDITY;
            totalSupply[poolId] += MIN_LIQUIDITY;
        } else {
            uint256 product = (N * uint256(pool.reserveUserToken)) / SCALE;
            uint256 denom = uint256(pool.reserveValidatorToken) + product;
            liquidity = (amountValidatorToken * _totalSupply) / denom;
        }

        if (liquidity == 0) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        _requireU128(amountValidatorToken);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountValidatorToken
        );

        pool.reserveValidatorToken += uint128(amountValidatorToken);

        totalSupply[poolId] += liquidity;
        liquidityBalances[poolId][to] += liquidity;

        emit Mint(
            msg.sender,
            to,
            userToken,
            validatorToken,
            amountValidatorToken,
            liquidity
        );
    }

    function burn(
        address userToken,
        address validatorToken,
        uint256 liquidity,
        address to
    ) external returns (uint256 amountUserToken, uint256 amountValidatorToken) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(liquidity != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];

        if (liquidityBalances[poolId][msg.sender] < liquidity) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        (amountUserToken, amountValidatorToken) = _calculateBurnAmounts(
            pool,
            poolId,
            liquidity
        );

        _requireU128(amountUserToken);
        _requireU128(amountValidatorToken);

        IERC20(userToken).transfer(to, amountUserToken);
        IERC20(validatorToken).transfer(to, amountValidatorToken);

        liquidityBalances[poolId][msg.sender] -= liquidity;
        totalSupply[poolId] -= liquidity;
        pool.reserveUserToken -= uint128(amountUserToken);
        pool.reserveValidatorToken -= uint128(amountValidatorToken);

        emit Burn(
            msg.sender,
            userToken,
            validatorToken,
            amountUserToken,
            amountValidatorToken,
            liquidity,
            to
        );
    }

    function _calculateBurnAmounts(
        Pool storage pool,
        bytes32 poolId,
        uint256 liquidity
    )
        private
        view
        returns (uint256 amountUserToken, uint256 amountValidatorToken)
    {
        uint256 _totalSupply = totalSupply[poolId];
  - 2026-01-tempo-feeamm: No README file was found at the repository root.
  - 2026-01-tempo-feeamm: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 124s)._

## req-3-block-mev::contracts/FeeAMM.sol: req-3-block-mev::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** 2026-01-tempo-feeamm, FeeAMM.sol, FeeAMM.sol (NatSpec)

**Confidence:** MEDIUM

**Mechanism:** FeeAMM exposes public swap entry points that are inherently ordering-sensitive yet omit standard MEV mitigations such as slippage constraints or deadlines; any reordering can change reserve availability and cause unexpected failure or extraction with no protective checks, so the requirement to protect against MEV is not satisfied.

**Supporting evidence:**
  - FeeAMM.sol (NatSpec): /**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
  - FeeAMM.sol: // SPDX-License-Identifier: MIT OR Apache-2.0
pragma solidity >=0.7.6 <0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
contract FeeAMM {
    uint256 public constant M = 9970;
    uint256 public constant N = 9985;
    uint256 public constant SCALE = 10_000;
    uint256 public constant MIN_LIQUIDITY = 1000;

    struct Pool {
        uint128 reserveUserToken;
        uint128 reserveValidatorToken;
    }

    event Mint(
        address indexed sender,
        address indexed to,
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        uint256 liquidity
    );

    event Burn(
        address indexed sender,
        address userToken,
        address validatorToken,
        uint256 amountUserToken,
        uint256 amountValidatorToken,
        uint256 liquidity,
        address indexed to
    );

    event RebalanceSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    event FeeSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => uint256) public totalSupply;
    mapping(bytes32 => mapping(address => uint256)) public liquidityBalances;

    function _requireU128(uint256 x) internal pure {
        require(x <= type(uint128).max, "INVALID_AMOUNT");
    }

    function getPoolId(
        address userToken,
        address validatorToken
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(userToken, validatorToken));
    }

    function getPool(
        address userToken,
        address validatorToken
    ) external view returns (Pool memory) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        return pools[poolId];
    }

    function checkSufficientLiquidity(
        address userToken,
        address validatorToken,
        uint256 maxAmount
    ) external view {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        uint256 amountOutNeeded = (maxAmount * M) / SCALE;
        require(
            pools[poolId].reserveValidatorToken >= amountOutNeeded,
            "INSUFFICIENT_LIQUIDITY"
        );
    }

    function executeFeeSwap(
        address userToken,
        address validatorToken,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        Pool storage pool = pools[poolId];

        amountOut = (amountIn * M) / SCALE;

        _requireU128(amountIn);
        _requireU128(amountOut);

        require(
            pool.reserveValidatorToken >= amountOut,
            "INSUFFICIENT_LIQUIDITY"
        );

        IERC20(userToken).transferFrom(msg.sender, address(this), amountIn);

        pool.reserveUserToken += uint128(amountIn);
        pool.reserveValidatorToken -= uint128(amountOut);

        IERC20(validatorToken).transfer(msg.sender, amountOut);

        emit FeeSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function rebalanceSwap(
        address userToken,
        address validatorToken,
        uint256 amountOut,
        address to
    ) external returns (uint256 amountIn) {
        require(amountOut != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        amountIn = (amountOut * N) / SCALE + 1;

        Pool storage pool = pools[poolId];

        _requireU128(amountOut);
        _requireU128(amountIn);

        if (
            uint256(pool.reserveValidatorToken) + amountIn > type(uint128).max
        ) {
            revert("INSUFFICIENT_RESERVES");
        }

        require(pool.reserveUserToken >= amountOut, "INVALID_AMOUNT");

        pool.reserveValidatorToken += uint128(amountIn);
        pool.reserveUserToken -= uint128(amountOut);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountIn
        );
        IERC20(userToken).transfer(to, amountOut);

        emit RebalanceSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function mint(
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        address to
    ) external returns (uint256 liquidity) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(amountValidatorToken != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];
        uint256 _totalSupply = totalSupply[poolId];

        if (pool.reserveUserToken == 0 && pool.reserveValidatorToken == 0) {
            if (amountValidatorToken / 2 <= MIN_LIQUIDITY) {
                revert("INSUFFICIENT_LIQUIDITY");
            }
            liquidity = amountValidatorToken / 2 - MIN_LIQUIDITY;
            totalSupply[poolId] += MIN_LIQUIDITY;
        } else {
            uint256 product = (N * uint256(pool.reserveUserToken)) / SCALE;
            uint256 denom = uint256(pool.reserveValidatorToken) + product;
            liquidity = (amountValidatorToken * _totalSupply) / denom;
        }

        if (liquidity == 0) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        _requireU128(amountValidatorToken);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountValidatorToken
        );

        pool.reserveValidatorToken += uint128(amountValidatorToken);

        totalSupply[poolId] += liquidity;
        liquidityBalances[poolId][to] += liquidity;

        emit Mint(
            msg.sender,
            to,
            userToken,
            validatorToken,
            amountValidatorToken,
            liquidity
        );
    }

    function burn(
        address userToken,
        address validatorToken,
        uint256 liquidity,
        address to
    ) external returns (uint256 amountUserToken, uint256 amountValidatorToken) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(liquidity != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];

        if (liquidityBalances[poolId][msg.sender] < liquidity) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        (amountUserToken, amountValidatorToken) = _calculateBurnAmounts(
            pool,
            poolId,
            liquidity
        );

        _requireU128(amountUserToken);
        _requireU128(amountValidatorToken);

        IERC20(userToken).transfer(to, amountUserToken);
        IERC20(validatorToken).transfer(to, amountValidatorToken);

        liquidityBalances[poolId][msg.sender] -= liquidity;
        totalSupply[poolId] -= liquidity;
        pool.reserveUserToken -= uint128(amountUserToken);
        pool.reserveValidatorToken -= uint128(amountValidatorToken);

        emit Burn(
            msg.sender,
            userToken,
            validatorToken,
            amountUserToken,
            amountValidatorToken,
            liquidity,
            to
        );
    }

    function _calculateBurnAmounts(
        Pool storage pool,
        bytes32 poolId,
        uint256 liquidity
    )
        private
        view
        returns (uint256 amountUserToken, uint256 amountValidatorToken)
    {
        uint256 _totalSupply = totalSupply[poolId];
  - 2026-01-tempo-feeamm: No README file was found at the repository root.
  - 2026-01-tempo-feeamm: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 184s)._

## req-3-event-on-state-change::contracts/FeeAMM.sol: req-3-event-on-state-change::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM.slitherConstructorConstantVariables

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - FeeAMM.slitherConstructorConstantVariables: writes state but emits no event

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-documented::contracts/FeeAMM.sol: req-3-documented::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** 2026-01-tempo-feeamm, FeeAMM.sol, FeeAMM.sol (NatSpec)

**Confidence:** MEDIUM

**Mechanism:** Requirement needs a specification of intended contract logic available to callers. Only a brief header exists, with no function-level documentation or external README/docs outlining the business logic, so the specification is not provided.

**Supporting evidence:**
  - FeeAMM.sol (NatSpec): /**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
  - FeeAMM.sol: // SPDX-License-Identifier: MIT OR Apache-2.0
pragma solidity >=0.7.6 <0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
contract FeeAMM {
    uint256 public constant M = 9970;
    uint256 public constant N = 9985;
    uint256 public constant SCALE = 10_000;
    uint256 public constant MIN_LIQUIDITY = 1000;

    struct Pool {
        uint128 reserveUserToken;
        uint128 reserveValidatorToken;
    }

    event Mint(
        address indexed sender,
        address indexed to,
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        uint256 liquidity
    );

    event Burn(
        address indexed sender,
        address userToken,
        address validatorToken,
        uint256 amountUserToken,
        uint256 amountValidatorToken,
        uint256 liquidity,
        address indexed to
    );

    event RebalanceSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    event FeeSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => uint256) public totalSupply;
    mapping(bytes32 => mapping(address => uint256)) public liquidityBalances;

    function _requireU128(uint256 x) internal pure {
        require(x <= type(uint128).max, "INVALID_AMOUNT");
    }

    function getPoolId(
        address userToken,
        address validatorToken
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(userToken, validatorToken));
    }

    function getPool(
        address userToken,
        address validatorToken
    ) external view returns (Pool memory) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        return pools[poolId];
    }

    function checkSufficientLiquidity(
        address userToken,
        address validatorToken,
        uint256 maxAmount
    ) external view {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        uint256 amountOutNeeded = (maxAmount * M) / SCALE;
        require(
            pools[poolId].reserveValidatorToken >= amountOutNeeded,
            "INSUFFICIENT_LIQUIDITY"
        );
    }

    function executeFeeSwap(
        address userToken,
        address validatorToken,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        Pool storage pool = pools[poolId];

        amountOut = (amountIn * M) / SCALE;

        _requireU128(amountIn);
        _requireU128(amountOut);

        require(
            pool.reserveValidatorToken >= amountOut,
            "INSUFFICIENT_LIQUIDITY"
        );

        IERC20(userToken).transferFrom(msg.sender, address(this), amountIn);

        pool.reserveUserToken += uint128(amountIn);
        pool.reserveValidatorToken -= uint128(amountOut);

        IERC20(validatorToken).transfer(msg.sender, amountOut);

        emit FeeSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function rebalanceSwap(
        address userToken,
        address validatorToken,
        uint256 amountOut,
        address to
    ) external returns (uint256 amountIn) {
        require(amountOut != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        amountIn = (amountOut * N) / SCALE + 1;

        Pool storage pool = pools[poolId];

        _requireU128(amountOut);
        _requireU128(amountIn);

        if (
            uint256(pool.reserveValidatorToken) + amountIn > type(uint128).max
        ) {
            revert("INSUFFICIENT_RESERVES");
        }

        require(pool.reserveUserToken >= amountOut, "INVALID_AMOUNT");

        pool.reserveValidatorToken += uint128(amountIn);
        pool.reserveUserToken -= uint128(amountOut);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountIn
        );
        IERC20(userToken).transfer(to, amountOut);

        emit RebalanceSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function mint(
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        address to
    ) external returns (uint256 liquidity) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(amountValidatorToken != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];
        uint256 _totalSupply = totalSupply[poolId];

        if (pool.reserveUserToken == 0 && pool.reserveValidatorToken == 0) {
            if (amountValidatorToken / 2 <= MIN_LIQUIDITY) {
                revert("INSUFFICIENT_LIQUIDITY");
            }
            liquidity = amountValidatorToken / 2 - MIN_LIQUIDITY;
            totalSupply[poolId] += MIN_LIQUIDITY;
        } else {
            uint256 product = (N * uint256(pool.reserveUserToken)) / SCALE;
            uint256 denom = uint256(pool.reserveValidatorToken) + product;
            liquidity = (amountValidatorToken * _totalSupply) / denom;
        }

        if (liquidity == 0) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        _requireU128(amountValidatorToken);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountValidatorToken
        );

        pool.reserveValidatorToken += uint128(amountValidatorToken);

        totalSupply[poolId] += liquidity;
        liquidityBalances[poolId][to] += liquidity;

        emit Mint(
            msg.sender,
            to,
            userToken,
            validatorToken,
            amountValidatorToken,
            liquidity
        );
    }

    function burn(
        address userToken,
        address validatorToken,
        uint256 liquidity,
        address to
    ) external returns (uint256 amountUserToken, uint256 amountValidatorToken) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(liquidity != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];

        if (liquidityBalances[poolId][msg.sender] < liquidity) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        (amountUserToken, amountValidatorToken) = _calculateBurnAmounts(
            pool,
            poolId,
            liquidity
        );

        _requireU128(amountUserToken);
        _requireU128(amountValidatorToken);

        IERC20(userToken).transfer(to, amountUserToken);
        IERC20(validatorToken).transfer(to, amountValidatorToken);

        liquidityBalances[poolId][msg.sender] -= liquidity;
        totalSupply[poolId] -= liquidity;
        pool.reserveUserToken -= uint128(amountUserToken);
        pool.reserveValidatorToken -= uint128(amountValidatorToken);

        emit Burn(
            msg.sender,
            userToken,
            validatorToken,
            amountUserToken,
            amountValidatorToken,
            liquidity,
            to
        );
    }

    function _calculateBurnAmounts(
        Pool storage pool,
        bytes32 poolId,
        uint256 liquidity
    )
        private
        view
        returns (uint256 amountUserToken, uint256 amountValidatorToken)
    {
        uint256 _totalSupply = totalSupply[poolId];
  - 2026-01-tempo-feeamm: No README file was found at the repository root.
  - 2026-01-tempo-feeamm: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (0 graph queries, 208s)._

## req-3-document-system::contracts/FeeAMM.sol: req-3-document-system::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** 2026-01-tempo-feeamm, FeeAMM.sol, FeeAMM.sol (NatSpec)

**Confidence:** HIGH

**Mechanism:** Repository lacks any system architecture documentation; only a brief NatSpec header exists and does not cover required elements, so requirement is not satisfied.

**Supporting evidence:**
  - FeeAMM.sol (NatSpec): /**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
  - FeeAMM.sol: // SPDX-License-Identifier: MIT OR Apache-2.0
pragma solidity >=0.7.6 <0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
contract FeeAMM {
    uint256 public constant M = 9970;
    uint256 public constant N = 9985;
    uint256 public constant SCALE = 10_000;
    uint256 public constant MIN_LIQUIDITY = 1000;

    struct Pool {
        uint128 reserveUserToken;
        uint128 reserveValidatorToken;
    }

    event Mint(
        address indexed sender,
        address indexed to,
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        uint256 liquidity
    );

    event Burn(
        address indexed sender,
        address userToken,
        address validatorToken,
        uint256 amountUserToken,
        uint256 amountValidatorToken,
        uint256 liquidity,
        address indexed to
    );

    event RebalanceSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    event FeeSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => uint256) public totalSupply;
    mapping(bytes32 => mapping(address => uint256)) public liquidityBalances;

    function _requireU128(uint256 x) internal pure {
        require(x <= type(uint128).max, "INVALID_AMOUNT");
    }

    function getPoolId(
        address userToken,
        address validatorToken
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(userToken, validatorToken));
    }

    function getPool(
        address userToken,
        address validatorToken
    ) external view returns (Pool memory) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        return pools[poolId];
    }

    function checkSufficientLiquidity(
        address userToken,
        address validatorToken,
        uint256 maxAmount
    ) external view {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        uint256 amountOutNeeded = (maxAmount * M) / SCALE;
        require(
            pools[poolId].reserveValidatorToken >= amountOutNeeded,
            "INSUFFICIENT_LIQUIDITY"
        );
    }

    function executeFeeSwap(
        address userToken,
        address validatorToken,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        Pool storage pool = pools[poolId];

        amountOut = (amountIn * M) / SCALE;

        _requireU128(amountIn);
        _requireU128(amountOut);

        require(
            pool.reserveValidatorToken >= amountOut,
            "INSUFFICIENT_LIQUIDITY"
        );

        IERC20(userToken).transferFrom(msg.sender, address(this), amountIn);

        pool.reserveUserToken += uint128(amountIn);
        pool.reserveValidatorToken -= uint128(amountOut);

        IERC20(validatorToken).transfer(msg.sender, amountOut);

        emit FeeSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function rebalanceSwap(
        address userToken,
        address validatorToken,
        uint256 amountOut,
        address to
    ) external returns (uint256 amountIn) {
        require(amountOut != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        amountIn = (amountOut * N) / SCALE + 1;

        Pool storage pool = pools[poolId];

        _requireU128(amountOut);
        _requireU128(amountIn);

        if (
            uint256(pool.reserveValidatorToken) + amountIn > type(uint128).max
        ) {
            revert("INSUFFICIENT_RESERVES");
        }

        require(pool.reserveUserToken >= amountOut, "INVALID_AMOUNT");

        pool.reserveValidatorToken += uint128(amountIn);
        pool.reserveUserToken -= uint128(amountOut);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountIn
        );
        IERC20(userToken).transfer(to, amountOut);

        emit RebalanceSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function mint(
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        address to
    ) external returns (uint256 liquidity) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(amountValidatorToken != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];
        uint256 _totalSupply = totalSupply[poolId];

        if (pool.reserveUserToken == 0 && pool.reserveValidatorToken == 0) {
            if (amountValidatorToken / 2 <= MIN_LIQUIDITY) {
                revert("INSUFFICIENT_LIQUIDITY");
            }
            liquidity = amountValidatorToken / 2 - MIN_LIQUIDITY;
            totalSupply[poolId] += MIN_LIQUIDITY;
        } else {
            uint256 product = (N * uint256(pool.reserveUserToken)) / SCALE;
            uint256 denom = uint256(pool.reserveValidatorToken) + product;
            liquidity = (amountValidatorToken * _totalSupply) / denom;
        }

        if (liquidity == 0) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        _requireU128(amountValidatorToken);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountValidatorToken
        );

        pool.reserveValidatorToken += uint128(amountValidatorToken);

        totalSupply[poolId] += liquidity;
        liquidityBalances[poolId][to] += liquidity;

        emit Mint(
            msg.sender,
            to,
            userToken,
            validatorToken,
            amountValidatorToken,
            liquidity
        );
    }

    function burn(
        address userToken,
        address validatorToken,
        uint256 liquidity,
        address to
    ) external returns (uint256 amountUserToken, uint256 amountValidatorToken) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(liquidity != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];

        if (liquidityBalances[poolId][msg.sender] < liquidity) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        (amountUserToken, amountValidatorToken) = _calculateBurnAmounts(
            pool,
            poolId,
            liquidity
        );

        _requireU128(amountUserToken);
        _requireU128(amountValidatorToken);

        IERC20(userToken).transfer(to, amountUserToken);
        IERC20(validatorToken).transfer(to, amountValidatorToken);

        liquidityBalances[poolId][msg.sender] -= liquidity;
        totalSupply[poolId] -= liquidity;
        pool.reserveUserToken -= uint128(amountUserToken);
        pool.reserveValidatorToken -= uint128(amountValidatorToken);

        emit Burn(
            msg.sender,
            userToken,
            validatorToken,
            amountUserToken,
            amountValidatorToken,
            liquidity,
            to
        );
    }

    function _calculateBurnAmounts(
        Pool storage pool,
        bytes32 poolId,
        uint256 liquidity
    )
        private
        view
        returns (uint256 amountUserToken, uint256 amountValidatorToken)
    {
        uint256 _totalSupply = totalSupply[poolId];
  - 2026-01-tempo-feeamm: No README file was found at the repository root.
  - 2026-01-tempo-feeamm: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 118s)._

## req-3-document-threats::contracts/FeeAMM.sol: req-3-document-threats::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** 2026-01-tempo-feeamm, FeeAMM.sol, FeeAMM.sol (NatSpec)

**Confidence:** HIGH

**Mechanism:** Searched the repository and reviewed FeeAMM.sol; found no README/docs or any text describing threats, assumptions, responses, or outcomes. Only vendor markdown exists, so the required threat model is absent.

**Supporting evidence:**
  - FeeAMM.sol (NatSpec): /**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
  - FeeAMM.sol: // SPDX-License-Identifier: MIT OR Apache-2.0
pragma solidity >=0.7.6 <0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
contract FeeAMM {
    uint256 public constant M = 9970;
    uint256 public constant N = 9985;
    uint256 public constant SCALE = 10_000;
    uint256 public constant MIN_LIQUIDITY = 1000;

    struct Pool {
        uint128 reserveUserToken;
        uint128 reserveValidatorToken;
    }

    event Mint(
        address indexed sender,
        address indexed to,
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        uint256 liquidity
    );

    event Burn(
        address indexed sender,
        address userToken,
        address validatorToken,
        uint256 amountUserToken,
        uint256 amountValidatorToken,
        uint256 liquidity,
        address indexed to
    );

    event RebalanceSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    event FeeSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => uint256) public totalSupply;
    mapping(bytes32 => mapping(address => uint256)) public liquidityBalances;

    function _requireU128(uint256 x) internal pure {
        require(x <= type(uint128).max, "INVALID_AMOUNT");
    }

    function getPoolId(
        address userToken,
        address validatorToken
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(userToken, validatorToken));
    }

    function getPool(
        address userToken,
        address validatorToken
    ) external view returns (Pool memory) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        return pools[poolId];
    }

    function checkSufficientLiquidity(
        address userToken,
        address validatorToken,
        uint256 maxAmount
    ) external view {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        uint256 amountOutNeeded = (maxAmount * M) / SCALE;
        require(
            pools[poolId].reserveValidatorToken >= amountOutNeeded,
            "INSUFFICIENT_LIQUIDITY"
        );
    }

    function executeFeeSwap(
        address userToken,
        address validatorToken,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        Pool storage pool = pools[poolId];

        amountOut = (amountIn * M) / SCALE;

        _requireU128(amountIn);
        _requireU128(amountOut);

        require(
            pool.reserveValidatorToken >= amountOut,
            "INSUFFICIENT_LIQUIDITY"
        );

        IERC20(userToken).transferFrom(msg.sender, address(this), amountIn);

        pool.reserveUserToken += uint128(amountIn);
        pool.reserveValidatorToken -= uint128(amountOut);

        IERC20(validatorToken).transfer(msg.sender, amountOut);

        emit FeeSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function rebalanceSwap(
        address userToken,
        address validatorToken,
        uint256 amountOut,
        address to
    ) external returns (uint256 amountIn) {
        require(amountOut != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        amountIn = (amountOut * N) / SCALE + 1;

        Pool storage pool = pools[poolId];

        _requireU128(amountOut);
        _requireU128(amountIn);

        if (
            uint256(pool.reserveValidatorToken) + amountIn > type(uint128).max
        ) {
            revert("INSUFFICIENT_RESERVES");
        }

        require(pool.reserveUserToken >= amountOut, "INVALID_AMOUNT");

        pool.reserveValidatorToken += uint128(amountIn);
        pool.reserveUserToken -= uint128(amountOut);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountIn
        );
        IERC20(userToken).transfer(to, amountOut);

        emit RebalanceSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function mint(
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        address to
    ) external returns (uint256 liquidity) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(amountValidatorToken != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];
        uint256 _totalSupply = totalSupply[poolId];

        if (pool.reserveUserToken == 0 && pool.reserveValidatorToken == 0) {
            if (amountValidatorToken / 2 <= MIN_LIQUIDITY) {
                revert("INSUFFICIENT_LIQUIDITY");
            }
            liquidity = amountValidatorToken / 2 - MIN_LIQUIDITY;
            totalSupply[poolId] += MIN_LIQUIDITY;
        } else {
            uint256 product = (N * uint256(pool.reserveUserToken)) / SCALE;
            uint256 denom = uint256(pool.reserveValidatorToken) + product;
            liquidity = (amountValidatorToken * _totalSupply) / denom;
        }

        if (liquidity == 0) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        _requireU128(amountValidatorToken);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountValidatorToken
        );

        pool.reserveValidatorToken += uint128(amountValidatorToken);

        totalSupply[poolId] += liquidity;
        liquidityBalances[poolId][to] += liquidity;

        emit Mint(
            msg.sender,
            to,
            userToken,
            validatorToken,
            amountValidatorToken,
            liquidity
        );
    }

    function burn(
        address userToken,
        address validatorToken,
        uint256 liquidity,
        address to
    ) external returns (uint256 amountUserToken, uint256 amountValidatorToken) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(liquidity != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];

        if (liquidityBalances[poolId][msg.sender] < liquidity) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        (amountUserToken, amountValidatorToken) = _calculateBurnAmounts(
            pool,
            poolId,
            liquidity
        );

        _requireU128(amountUserToken);
        _requireU128(amountValidatorToken);

        IERC20(userToken).transfer(to, amountUserToken);
        IERC20(validatorToken).transfer(to, amountValidatorToken);

        liquidityBalances[poolId][msg.sender] -= liquidity;
        totalSupply[poolId] -= liquidity;
        pool.reserveUserToken -= uint128(amountUserToken);
        pool.reserveValidatorToken -= uint128(amountValidatorToken);

        emit Burn(
            msg.sender,
            userToken,
            validatorToken,
            amountUserToken,
            amountValidatorToken,
            liquidity,
            to
        );
    }

    function _calculateBurnAmounts(
        Pool storage pool,
        bytes32 poolId,
        uint256 liquidity
    )
        private
        view
        returns (uint256 amountUserToken, uint256 amountValidatorToken)
    {
        uint256 _totalSupply = totalSupply[poolId];
  - 2026-01-tempo-feeamm: No README file was found at the repository root.
  - 2026-01-tempo-feeamm: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 198s)._

## req-3-annotate::contracts/FeeAMM.sol: req-3-annotate::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM.burn, FeeAMM.checkSufficientLiquidity, FeeAMM.executeFeeSwap, FeeAMM.getPool, FeeAMM.getPoolId, FeeAMM.mint, FeeAMM.rebalanceSwap

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - FeeAMM.getPoolId: public/external function has no NatSpec annotation
  - FeeAMM.getPool: public/external function has no NatSpec annotation
  - FeeAMM.checkSufficientLiquidity: public/external function has no NatSpec annotation
  - FeeAMM.executeFeeSwap: public/external function has no NatSpec annotation
  - FeeAMM.rebalanceSwap: public/external function has no NatSpec annotation
  - FeeAMM.mint: public/external function has no NatSpec annotation
  - FeeAMM.burn: public/external function has no NatSpec annotation

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-access-control::contracts/FeeAMM.sol: req-3-access-control::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM.burn, FeeAMM.executeFeeSwap, FeeAMM.mint, FeeAMM.rebalanceSwap

**Confidence:** HIGH

**Mechanism:** FeeAMM exposes liquidity-minting, burning, and swap functions to all callers without any access control or role checks. No documentation defines authorized parties. This fails least-privilege enforcement for privileged interactions.

**Supporting evidence:**
  - FeeAMM.executeFeeSwap: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - FeeAMM.rebalanceSwap: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - FeeAMM.mint: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - FeeAMM.burn: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here

_Determined via graph-gated Codex investigation (1 graph queries, 238s)._

## req-3-revocable-permisions::contracts/FeeAMM.sol: req-3-revocable-permisions::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** 2026-01-tempo-feeamm, FeeAMM.sol, FeeAMM.sol (NatSpec)

**Confidence:** HIGH

**Mechanism:** The contract lacks any access-control mechanism, so there is no way to revoke or transfer permissions; requirement is unmet.

**Supporting evidence:**
  - FeeAMM.sol (NatSpec): /**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
  - FeeAMM.sol: // SPDX-License-Identifier: MIT OR Apache-2.0
pragma solidity >=0.7.6 <0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
contract FeeAMM {
    uint256 public constant M = 9970;
    uint256 public constant N = 9985;
    uint256 public constant SCALE = 10_000;
    uint256 public constant MIN_LIQUIDITY = 1000;

    struct Pool {
        uint128 reserveUserToken;
        uint128 reserveValidatorToken;
    }

    event Mint(
        address indexed sender,
        address indexed to,
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        uint256 liquidity
    );

    event Burn(
        address indexed sender,
        address userToken,
        address validatorToken,
        uint256 amountUserToken,
        uint256 amountValidatorToken,
        uint256 liquidity,
        address indexed to
    );

    event RebalanceSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    event FeeSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => uint256) public totalSupply;
    mapping(bytes32 => mapping(address => uint256)) public liquidityBalances;

    function _requireU128(uint256 x) internal pure {
        require(x <= type(uint128).max, "INVALID_AMOUNT");
    }

    function getPoolId(
        address userToken,
        address validatorToken
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(userToken, validatorToken));
    }

    function getPool(
        address userToken,
        address validatorToken
    ) external view returns (Pool memory) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        return pools[poolId];
    }

    function checkSufficientLiquidity(
        address userToken,
        address validatorToken,
        uint256 maxAmount
    ) external view {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        uint256 amountOutNeeded = (maxAmount * M) / SCALE;
        require(
            pools[poolId].reserveValidatorToken >= amountOutNeeded,
            "INSUFFICIENT_LIQUIDITY"
        );
    }

    function executeFeeSwap(
        address userToken,
        address validatorToken,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        Pool storage pool = pools[poolId];

        amountOut = (amountIn * M) / SCALE;

        _requireU128(amountIn);
        _requireU128(amountOut);

        require(
            pool.reserveValidatorToken >= amountOut,
            "INSUFFICIENT_LIQUIDITY"
        );

        IERC20(userToken).transferFrom(msg.sender, address(this), amountIn);

        pool.reserveUserToken += uint128(amountIn);
        pool.reserveValidatorToken -= uint128(amountOut);

        IERC20(validatorToken).transfer(msg.sender, amountOut);

        emit FeeSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function rebalanceSwap(
        address userToken,
        address validatorToken,
        uint256 amountOut,
        address to
    ) external returns (uint256 amountIn) {
        require(amountOut != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        amountIn = (amountOut * N) / SCALE + 1;

        Pool storage pool = pools[poolId];

        _requireU128(amountOut);
        _requireU128(amountIn);

        if (
            uint256(pool.reserveValidatorToken) + amountIn > type(uint128).max
        ) {
            revert("INSUFFICIENT_RESERVES");
        }

        require(pool.reserveUserToken >= amountOut, "INVALID_AMOUNT");

        pool.reserveValidatorToken += uint128(amountIn);
        pool.reserveUserToken -= uint128(amountOut);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountIn
        );
        IERC20(userToken).transfer(to, amountOut);

        emit RebalanceSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function mint(
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        address to
    ) external returns (uint256 liquidity) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(amountValidatorToken != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];
        uint256 _totalSupply = totalSupply[poolId];

        if (pool.reserveUserToken == 0 && pool.reserveValidatorToken == 0) {
            if (amountValidatorToken / 2 <= MIN_LIQUIDITY) {
                revert("INSUFFICIENT_LIQUIDITY");
            }
            liquidity = amountValidatorToken / 2 - MIN_LIQUIDITY;
            totalSupply[poolId] += MIN_LIQUIDITY;
        } else {
            uint256 product = (N * uint256(pool.reserveUserToken)) / SCALE;
            uint256 denom = uint256(pool.reserveValidatorToken) + product;
            liquidity = (amountValidatorToken * _totalSupply) / denom;
        }

        if (liquidity == 0) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        _requireU128(amountValidatorToken);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountValidatorToken
        );

        pool.reserveValidatorToken += uint128(amountValidatorToken);

        totalSupply[poolId] += liquidity;
        liquidityBalances[poolId][to] += liquidity;

        emit Mint(
            msg.sender,
            to,
            userToken,
            validatorToken,
            amountValidatorToken,
            liquidity
        );
    }

    function burn(
        address userToken,
        address validatorToken,
        uint256 liquidity,
        address to
    ) external returns (uint256 amountUserToken, uint256 amountValidatorToken) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(liquidity != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];

        if (liquidityBalances[poolId][msg.sender] < liquidity) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        (amountUserToken, amountValidatorToken) = _calculateBurnAmounts(
            pool,
            poolId,
            liquidity
        );

        _requireU128(amountUserToken);
        _requireU128(amountValidatorToken);

        IERC20(userToken).transfer(to, amountUserToken);
        IERC20(validatorToken).transfer(to, amountValidatorToken);

        liquidityBalances[poolId][msg.sender] -= liquidity;
        totalSupply[poolId] -= liquidity;
        pool.reserveUserToken -= uint128(amountUserToken);
        pool.reserveValidatorToken -= uint128(amountValidatorToken);

        emit Burn(
            msg.sender,
            userToken,
            validatorToken,
            amountUserToken,
            amountValidatorToken,
            liquidity,
            to
        );
    }

    function _calculateBurnAmounts(
        Pool storage pool,
        bytes32 poolId,
        uint256 liquidity
    )
        private
        view
        returns (uint256 amountUserToken, uint256 amountValidatorToken)
    {
        uint256 _totalSupply = totalSupply[poolId];
  - 2026-01-tempo-feeamm: No README file was found at the repository root.
  - 2026-01-tempo-feeamm: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 148s)._

## req-3-external-calls::contracts/FeeAMM.sol: req-3-external-calls::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** FeeAMM.burn, FeeAMM.executeFeeSwap, FeeAMM.mint

**Confidence:** HIGH

**Mechanism:** burn makes external ERC20 transfers but does not check return values, lacks reentrancy safeguards, updates state after the external calls, and provides no documentation of protections or rationale, violating the requirement for documented and compatible external-call protection.

**Supporting evidence:**
  - FeeAMM.executeFeeSwap: external call at node 7 followed by state write at node 8 (CFG-reachable)
  - FeeAMM.mint: external call at node 20 followed by state write at node 23 (CFG-reachable)
  - FeeAMM.burn: external call at node 11 followed by state write at node 13 (CFG-reachable)
  - FeeAMM.burn: external call at node 12 followed by state write at node 13 (CFG-reachable)

_Determined via graph-gated Codex investigation (1 graph queries, 131s)._

## req-3-consistent-solidity-output::contracts/FeeAMM.sol: req-3-consistent-solidity-output::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** pragma solidity>=0.6.0<0.8.0, pragma solidity>=0.7.6<0.8.0

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - pragma solidity>=0.7.6<0.8.0: pragma '>=0.7.6<0.8.0' is a range, not an exact pin
  - pragma solidity>=0.6.0<0.8.0: pragma '>=0.6.0<0.8.0' is a range, not an exact pin

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-use-latest-compiler::contracts/FeeAMM.sol: req-R-use-latest-compiler::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** compiler config

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - compiler config: solc 0.7.6 != caller-supplied latest known stable version 0.8.36 (external, time-anchored reference -- not derived from spec text)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-clean-code::contracts/FeeAMM.sol: req-R-clean-code::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** 2026-01-tempo-feeamm, FeeAMM.sol, FeeAMM.sol (NatSpec)

**Confidence:** MEDIUM

**Mechanism:** The FeeAMM contract provides only a brief header comment; all functions and core constants are undocumented and use terse names, leaving formulas and assumptions unclear. Lack of NatSpec and descriptive comments reduces ease of understanding, so the code does not meet the clarity good-practice requirement.

**Supporting evidence:**
  - FeeAMM.sol (NatSpec): /**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
  - FeeAMM.sol: // SPDX-License-Identifier: MIT OR Apache-2.0
pragma solidity >=0.7.6 <0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
contract FeeAMM {
    uint256 public constant M = 9970;
    uint256 public constant N = 9985;
    uint256 public constant SCALE = 10_000;
    uint256 public constant MIN_LIQUIDITY = 1000;

    struct Pool {
        uint128 reserveUserToken;
        uint128 reserveValidatorToken;
    }

    event Mint(
        address indexed sender,
        address indexed to,
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        uint256 liquidity
    );

    event Burn(
        address indexed sender,
        address userToken,
        address validatorToken,
        uint256 amountUserToken,
        uint256 amountValidatorToken,
        uint256 liquidity,
        address indexed to
    );

    event RebalanceSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    event FeeSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => uint256) public totalSupply;
    mapping(bytes32 => mapping(address => uint256)) public liquidityBalances;

    function _requireU128(uint256 x) internal pure {
        require(x <= type(uint128).max, "INVALID_AMOUNT");
    }

    function getPoolId(
        address userToken,
        address validatorToken
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(userToken, validatorToken));
    }

    function getPool(
        address userToken,
        address validatorToken
    ) external view returns (Pool memory) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        return pools[poolId];
    }

    function checkSufficientLiquidity(
        address userToken,
        address validatorToken,
        uint256 maxAmount
    ) external view {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        uint256 amountOutNeeded = (maxAmount * M) / SCALE;
        require(
            pools[poolId].reserveValidatorToken >= amountOutNeeded,
            "INSUFFICIENT_LIQUIDITY"
        );
    }

    function executeFeeSwap(
        address userToken,
        address validatorToken,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        Pool storage pool = pools[poolId];

        amountOut = (amountIn * M) / SCALE;

        _requireU128(amountIn);
        _requireU128(amountOut);

        require(
            pool.reserveValidatorToken >= amountOut,
            "INSUFFICIENT_LIQUIDITY"
        );

        IERC20(userToken).transferFrom(msg.sender, address(this), amountIn);

        pool.reserveUserToken += uint128(amountIn);
        pool.reserveValidatorToken -= uint128(amountOut);

        IERC20(validatorToken).transfer(msg.sender, amountOut);

        emit FeeSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function rebalanceSwap(
        address userToken,
        address validatorToken,
        uint256 amountOut,
        address to
    ) external returns (uint256 amountIn) {
        require(amountOut != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        amountIn = (amountOut * N) / SCALE + 1;

        Pool storage pool = pools[poolId];

        _requireU128(amountOut);
        _requireU128(amountIn);

        if (
            uint256(pool.reserveValidatorToken) + amountIn > type(uint128).max
        ) {
            revert("INSUFFICIENT_RESERVES");
        }

        require(pool.reserveUserToken >= amountOut, "INVALID_AMOUNT");

        pool.reserveValidatorToken += uint128(amountIn);
        pool.reserveUserToken -= uint128(amountOut);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountIn
        );
        IERC20(userToken).transfer(to, amountOut);

        emit RebalanceSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function mint(
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        address to
    ) external returns (uint256 liquidity) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(amountValidatorToken != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];
        uint256 _totalSupply = totalSupply[poolId];

        if (pool.reserveUserToken == 0 && pool.reserveValidatorToken == 0) {
            if (amountValidatorToken / 2 <= MIN_LIQUIDITY) {
                revert("INSUFFICIENT_LIQUIDITY");
            }
            liquidity = amountValidatorToken / 2 - MIN_LIQUIDITY;
            totalSupply[poolId] += MIN_LIQUIDITY;
        } else {
            uint256 product = (N * uint256(pool.reserveUserToken)) / SCALE;
            uint256 denom = uint256(pool.reserveValidatorToken) + product;
            liquidity = (amountValidatorToken * _totalSupply) / denom;
        }

        if (liquidity == 0) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        _requireU128(amountValidatorToken);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountValidatorToken
        );

        pool.reserveValidatorToken += uint128(amountValidatorToken);

        totalSupply[poolId] += liquidity;
        liquidityBalances[poolId][to] += liquidity;

        emit Mint(
            msg.sender,
            to,
            userToken,
            validatorToken,
            amountValidatorToken,
            liquidity
        );
    }

    function burn(
        address userToken,
        address validatorToken,
        uint256 liquidity,
        address to
    ) external returns (uint256 amountUserToken, uint256 amountValidatorToken) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(liquidity != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];

        if (liquidityBalances[poolId][msg.sender] < liquidity) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        (amountUserToken, amountValidatorToken) = _calculateBurnAmounts(
            pool,
            poolId,
            liquidity
        );

        _requireU128(amountUserToken);
        _requireU128(amountValidatorToken);

        IERC20(userToken).transfer(to, amountUserToken);
        IERC20(validatorToken).transfer(to, amountValidatorToken);

        liquidityBalances[poolId][msg.sender] -= liquidity;
        totalSupply[poolId] -= liquidity;
        pool.reserveUserToken -= uint128(amountUserToken);
        pool.reserveValidatorToken -= uint128(amountValidatorToken);

        emit Burn(
            msg.sender,
            userToken,
            validatorToken,
            amountUserToken,
            amountValidatorToken,
            liquidity,
            to
        );
    }

    function _calculateBurnAmounts(
        Pool storage pool,
        bytes32 poolId,
        uint256 liquidity
    )
        private
        view
        returns (uint256 amountUserToken, uint256 amountValidatorToken)
    {
        uint256 _totalSupply = totalSupply[poolId];
  - 2026-01-tempo-feeamm: No README file was found at the repository root.
  - 2026-01-tempo-feeamm: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 97s)._

## req-R-notify-news::contracts/FeeAMM.sol: req-R-notify-news::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** 2026-01-tempo-feeamm, FeeAMM.sol, FeeAMM.sol (NatSpec)

**Confidence:** MEDIUM

**Mechanism:** Searched the repository for SECURITY/README or any disclosure instructions and found none; FeeAMM.sol documentation likewise contains no guidance on reporting new vulnerabilities, so the project does not provide a responsible disclosure channel as required.

**Supporting evidence:**
  - FeeAMM.sol (NatSpec): /**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
  - FeeAMM.sol: // SPDX-License-Identifier: MIT OR Apache-2.0
pragma solidity >=0.7.6 <0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title FeeAMM
 * @notice Automated Market Maker for fee swaps between TIP-20 USD stablecoins
 * @dev Enables validators who run payment flows on Tempo to exchange fee tokens collected from users for their preferred
 *      stablecoin denomination.
 */
contract FeeAMM {
    uint256 public constant M = 9970;
    uint256 public constant N = 9985;
    uint256 public constant SCALE = 10_000;
    uint256 public constant MIN_LIQUIDITY = 1000;

    struct Pool {
        uint128 reserveUserToken;
        uint128 reserveValidatorToken;
    }

    event Mint(
        address indexed sender,
        address indexed to,
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        uint256 liquidity
    );

    event Burn(
        address indexed sender,
        address userToken,
        address validatorToken,
        uint256 amountUserToken,
        uint256 amountValidatorToken,
        uint256 liquidity,
        address indexed to
    );

    event RebalanceSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    event FeeSwap(
        address indexed userToken,
        address indexed validatorToken,
        address indexed sender,
        uint256 amountIn,
        uint256 amountOut
    );

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => uint256) public totalSupply;
    mapping(bytes32 => mapping(address => uint256)) public liquidityBalances;

    function _requireU128(uint256 x) internal pure {
        require(x <= type(uint128).max, "INVALID_AMOUNT");
    }

    function getPoolId(
        address userToken,
        address validatorToken
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(userToken, validatorToken));
    }

    function getPool(
        address userToken,
        address validatorToken
    ) external view returns (Pool memory) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        return pools[poolId];
    }

    function checkSufficientLiquidity(
        address userToken,
        address validatorToken,
        uint256 maxAmount
    ) external view {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        uint256 amountOutNeeded = (maxAmount * M) / SCALE;
        require(
            pools[poolId].reserveValidatorToken >= amountOutNeeded,
            "INSUFFICIENT_LIQUIDITY"
        );
    }

    function executeFeeSwap(
        address userToken,
        address validatorToken,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(userToken, validatorToken);
        Pool storage pool = pools[poolId];

        amountOut = (amountIn * M) / SCALE;

        _requireU128(amountIn);
        _requireU128(amountOut);

        require(
            pool.reserveValidatorToken >= amountOut,
            "INSUFFICIENT_LIQUIDITY"
        );

        IERC20(userToken).transferFrom(msg.sender, address(this), amountIn);

        pool.reserveUserToken += uint128(amountIn);
        pool.reserveValidatorToken -= uint128(amountOut);

        IERC20(validatorToken).transfer(msg.sender, amountOut);

        emit FeeSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function rebalanceSwap(
        address userToken,
        address validatorToken,
        uint256 amountOut,
        address to
    ) external returns (uint256 amountIn) {
        require(amountOut != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        amountIn = (amountOut * N) / SCALE + 1;

        Pool storage pool = pools[poolId];

        _requireU128(amountOut);
        _requireU128(amountIn);

        if (
            uint256(pool.reserveValidatorToken) + amountIn > type(uint128).max
        ) {
            revert("INSUFFICIENT_RESERVES");
        }

        require(pool.reserveUserToken >= amountOut, "INVALID_AMOUNT");

        pool.reserveValidatorToken += uint128(amountIn);
        pool.reserveUserToken -= uint128(amountOut);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountIn
        );
        IERC20(userToken).transfer(to, amountOut);

        emit RebalanceSwap(
            userToken,
            validatorToken,
            msg.sender,
            amountIn,
            amountOut
        );
    }

    function mint(
        address userToken,
        address validatorToken,
        uint256 amountValidatorToken,
        address to
    ) external returns (uint256 liquidity) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(amountValidatorToken != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];
        uint256 _totalSupply = totalSupply[poolId];

        if (pool.reserveUserToken == 0 && pool.reserveValidatorToken == 0) {
            if (amountValidatorToken / 2 <= MIN_LIQUIDITY) {
                revert("INSUFFICIENT_LIQUIDITY");
            }
            liquidity = amountValidatorToken / 2 - MIN_LIQUIDITY;
            totalSupply[poolId] += MIN_LIQUIDITY;
        } else {
            uint256 product = (N * uint256(pool.reserveUserToken)) / SCALE;
            uint256 denom = uint256(pool.reserveValidatorToken) + product;
            liquidity = (amountValidatorToken * _totalSupply) / denom;
        }

        if (liquidity == 0) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        _requireU128(amountValidatorToken);

        IERC20(validatorToken).transferFrom(
            msg.sender,
            address(this),
            amountValidatorToken
        );

        pool.reserveValidatorToken += uint128(amountValidatorToken);

        totalSupply[poolId] += liquidity;
        liquidityBalances[poolId][to] += liquidity;

        emit Mint(
            msg.sender,
            to,
            userToken,
            validatorToken,
            amountValidatorToken,
            liquidity
        );
    }

    function burn(
        address userToken,
        address validatorToken,
        uint256 liquidity,
        address to
    ) external returns (uint256 amountUserToken, uint256 amountValidatorToken) {
        require(userToken != validatorToken, "IDENTICAL_ADDRESSES");
        require(liquidity != 0, "INVALID_AMOUNT");

        bytes32 poolId = getPoolId(userToken, validatorToken);

        Pool storage pool = pools[poolId];

        if (liquidityBalances[poolId][msg.sender] < liquidity) {
            revert("INSUFFICIENT_LIQUIDITY");
        }

        (amountUserToken, amountValidatorToken) = _calculateBurnAmounts(
            pool,
            poolId,
            liquidity
        );

        _requireU128(amountUserToken);
        _requireU128(amountValidatorToken);

        IERC20(userToken).transfer(to, amountUserToken);
        IERC20(validatorToken).transfer(to, amountValidatorToken);

        liquidityBalances[poolId][msg.sender] -= liquidity;
        totalSupply[poolId] -= liquidity;
        pool.reserveUserToken -= uint128(amountUserToken);
        pool.reserveValidatorToken -= uint128(amountValidatorToken);

        emit Burn(
            msg.sender,
            userToken,
            validatorToken,
            amountUserToken,
            amountValidatorToken,
            liquidity,
            to
        );
    }

    function _calculateBurnAmounts(
        Pool storage pool,
        bytes32 poolId,
        uint256 liquidity
    )
        private
        view
        returns (uint256 amountUserToken, uint256 amountValidatorToken)
    {
        uint256 _totalSupply = totalSupply[poolId];
  - 2026-01-tempo-feeamm: No README file was found at the repository root.
  - 2026-01-tempo-feeamm: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (0 graph queries, 138s)._

## req-R-fuzzing-in-testing::contracts/FeeAMM.sol: req-R-fuzzing-in-testing::contracts/FeeAMM.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAsserNottEq_BytesErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertNotEq_BytesErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertNotEq_Bytes_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertNotEq_Bytes_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdChains.t.sol:testRpc, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeAddressIsNot, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeNotBlacklisted_TokenWithoutBlacklist, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeNotBlacklisted_USDC, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeNotBlacklisted_USDT, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeNotPrecompile, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testBound, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testBoundInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbsDecimal_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Return_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Revert_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertEqCall_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertNotEq_Bytes_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertNotEq_Bytes_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAssertNotEq_BytesErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdAssertions.t.sol:testAsserNottEq_BytesErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdChains.t.sol:testRpc: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeAddressIsNot: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeNotPrecompile: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeNotBlacklisted_TokenWithoutBlacklist: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeNotBlacklisted_USDC: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdCheats.t.sol:testAssumeNotBlacklisted_USDT: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testBound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testBoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2026-01-tempo-feeamm/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)

_Determined via bounded LLM judgment on deterministically-collected evidence._
