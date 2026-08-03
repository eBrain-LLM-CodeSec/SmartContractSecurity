#!/bin/bash
#SBATCH -p compute
#SBATCH -t 12:00:00
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -o /scratch/md5344/.claude/jobs/b51e9657/tmp/phase5_sbatch_%j.out
#SBATCH -e /scratch/md5344/.claude/jobs/b51e9657/tmp/phase5_sbatch_%j.err
# Phase 5, submitted as a real batch job instead of running interactively:
# the interactive session this was first launched from is capped at a
# 4-hour walltime (QOS=small) and cannot be extended (confirmed live:
# `scontrol update ... TimeLimit=...` returns "Access/permission denied"
# for a non-admin user) -- three full 27-audit runs take roughly 5+ hours
# total based on run 1's own measured ~100 minutes, so an interactive
# session would be killed mid-run-2 or mid-run-3 by SLURM regardless of
# anything this script does. sbatch's own 7-day partition ceiling (same
# convention as sbatch/run_stack.sbatch) removes that ceiling entirely.
set -uo pipefail
module purge; module load singularity
cd /scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2
bash scripts/benchmark/run_three_validations.sh "${1:-phase5_sbatch_${SLURM_JOB_ID}}"
