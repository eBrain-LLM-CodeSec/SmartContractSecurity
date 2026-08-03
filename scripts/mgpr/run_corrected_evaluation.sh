#!/usr/bin/env bash
# Runs the CORRECTED evaluation (Phase 2 classifier + Phase 2 reviewed
# labels + Phase 3 incorrect claims) across all 27 stable-compiling audits,
# using the same checksum-verified toolchain and strict-offline mode as
# the benchmark-infrastructure validation runs. One run is sufficient here
# (this task's decision rule is about evaluation-methodology correctness,
# not build reproducibility, which was already established with 3
# independent runs by the prior benchmark-infrastructure pass) -- reuses
# the exact same env-var contract as run_three_validations.sh for
# consistency, just once instead of three times.
#
# Usage: scripts/mgpr/run_corrected_evaluation.sh [run-id]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
REPO_ROOT="$(pwd)"

RUN_ID="${1:-$(date +%Y%m%dT%H%M%S)}"
RUN_DIR="${REPO_ROOT}/.benchmark/runs/corrected_eval_${RUN_ID}"
TOOLCHAIN_DIR="${REPO_ROOT}/.benchmark/toolchains"
export PATH="${REPO_ROOT}/bin:${REPO_ROOT}/.venv/bin:${PATH}"

mkdir -p "${RUN_DIR}"
echo "=== corrected evaluation run -> ${RUN_DIR} ==="

export BENCHMARK_WORK_DIR="${RUN_DIR}/checkouts"
export BENCHMARK_OUT_DIR="${RUN_DIR}/study_full"
export BENCHMARK_CONTAINER_HOME="${RUN_DIR}/container_home"
export BENCHMARK_CONTAINER_TMP="${RUN_DIR}/container_tmp"
export BENCHMARK_TOOLCHAIN_DIR="${TOOLCHAIN_DIR}"
export BENCHMARK_STRICT_OFFLINE=1
export BENCHMARK_REVIEWED_LABELS_PATH="${REPO_ROOT}/data/mgpr/reviewed_family_labels.jsonl"

mkdir -p "${BENCHMARK_WORK_DIR}" "${BENCHMARK_OUT_DIR}" "${BENCHMARK_CONTAINER_HOME}" "${BENCHMARK_CONTAINER_TMP}"

.venv/bin/python -m scripts.benchmark.generate_environment_manifest \
  --out "${RUN_DIR}/environment-manifest.json"

.venv/bin/python -m scripts.mgpr.run_full_study_batch \
  2>&1 | tee "${RUN_DIR}/run.log"

.venv/bin/python -m scripts.mgpr.generate_corrected_metrics \
  --study-dir "${BENCHMARK_OUT_DIR}" \
  --out "${RUN_DIR}/corrected_metrics_report.json"

echo "=== corrected evaluation run done -> ${RUN_DIR} ==="
