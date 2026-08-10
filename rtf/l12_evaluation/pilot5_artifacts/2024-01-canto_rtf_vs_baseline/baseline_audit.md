# Security Audit Report: 2024-01-canto

Findings below were produced by a single, autonomous, non-RTF Codex session using the production evmbench single-shot audit prompt (backend/worker_runner/detect.md) -- full repository access, no requirement routing, no structured tool scaffolding.

## 1. Gauge weight lookup uses block numbers instead of timestamps, zeroing all rewards (high)

**Summary:** LendingLedger passes block numbers to GaugeController.gauge_relative_weight_write, which expects Unix timestamps, causing every lookup to hit empty checkpoints and return zero weight so no CANTO rewards ever accrue.

**Location:** src/LendingLedger.sol:64-70

update_market computes `epoch` from the block number and calls `gauge_relative_weight_write(_market, epoch)`. GaugeController stores weights keyed by weekly timestamps, so using block numbers causes `points_sum[t].bias` to be zero and the relative weight to be zero.

**Impact:** All markets receive a zero relative weight, so `cantoReward` is always zero and `accCantoPerShare` never increases. Users can never accrue or claim the configured CANTO emissions, leaving funded rewards locked in the contract and causing a direct loss of expected assets.

**Proof of concept:** Fund LendingLedger with CANTO, whitelist a market, set non-zero rewards via setRewards, and perform deposits. Calls to claim will always return zero because update_market derives epoch from block numbers and gauge_relative_weight_write returns zero weight.

**Remediation:** Pass a timestamp (e.g., block.timestamp rounded to weeks) to `gauge_relative_weight_write` instead of the block number, or convert the block-based epoch to an equivalent timestamp so GaugeController retrieves the correct weight.
