#!/usr/bin/env bash
# Phase 5: three independent cold-start validations of the full 27-audit
# benchmark, each with its own fresh WORK_DIR/OUT_DIR/CONTAINER_HOME/tmp
# (only the immutable, checksum-verified toolchain bundle under
# .benchmark/toolchains is shared across runs -- it is provisioned
# separately, once, and never touched by this script), a distinct
# randomized audit-execution order, and BENCHMARK_STRICT_OFFLINE=1 so any
# implicit compiler download would hard-fail rather than silently succeed.
#
# Usage: scripts/benchmark/run_three_validations.sh [run-group-id]
# (run-group-id defaults to a timestamp, so re-invoking never collides
# with a previous group's runs)
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
REPO_ROOT="$(pwd)"

GROUP="${1:-$(date +%Y%m%dT%H%M%S)}"
TOOLCHAIN_DIR="${REPO_ROOT}/.benchmark/toolchains"
export PATH="${REPO_ROOT}/bin:${REPO_ROOT}/.venv/bin:${PATH}"

for RUN_ID in 1 2 3; do
  RUN_DIR="${REPO_ROOT}/.benchmark/runs/validation_${GROUP}_run${RUN_ID}"
  mkdir -p "${RUN_DIR}"
  echo "=== validation run ${RUN_ID} (group ${GROUP}) -> ${RUN_DIR} ==="

  export BENCHMARK_WORK_DIR="${RUN_DIR}/checkouts"
  export BENCHMARK_OUT_DIR="${RUN_DIR}/study_full"
  export BENCHMARK_CONTAINER_HOME="${RUN_DIR}/container_home"
  export BENCHMARK_CONTAINER_TMP="${RUN_DIR}/container_tmp"
  export BENCHMARK_TOOLCHAIN_DIR="${TOOLCHAIN_DIR}"
  export BENCHMARK_STRICT_OFFLINE=1
  # A distinct, but individually reproducible, seed per run -- see
  # run_full_study_batch.audit_order()'s own docstring for why this
  # matters (surfaces order-dependent state leaks as a mismatch instead of
  # masking them by always running the fixed ALL_27 order).
  export BENCHMARK_AUDIT_ORDER_SEED="$((RUN_ID * 104729))"

  mkdir -p "${BENCHMARK_WORK_DIR}" "${BENCHMARK_OUT_DIR}" "${BENCHMARK_CONTAINER_HOME}" "${BENCHMARK_CONTAINER_TMP}"

  .venv/bin/python -m scripts.benchmark.generate_environment_manifest \
    --out "${RUN_DIR}/environment-manifest.json"

  .venv/bin/python -m scripts.mgpr.run_full_study_batch \
    2>&1 | tee "${RUN_DIR}/run.log"

  echo "=== validation run ${RUN_ID} done ==="
done

echo "GROUP=${GROUP}"
