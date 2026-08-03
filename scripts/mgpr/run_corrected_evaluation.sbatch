#!/bin/bash
#SBATCH -p compute
#SBATCH -t 04:00:00
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -o /scratch/md5344/.claude/jobs/b51e9657/tmp/corrected_eval_sbatch_%j.out
#SBATCH -e /scratch/md5344/.claude/jobs/b51e9657/tmp/corrected_eval_sbatch_%j.err
# Submitted as a proper sbatch job rather than run interactively -- this
# session's own interactive allocation is capped at a 4h walltime (QOS
# non-extendable, confirmed live in the prior benchmark-infrastructure
# pass), and a single full 27-audit compile+evaluate run has historically
# taken ~100 minutes, which is cutting it close against other interactive
# work in the same session. sbatch removes that risk entirely.
set -uo pipefail
# Pinned explicitly to 3.6.4, matching every toolchain fixture/behavior
# validated in the prior benchmark-infrastructure pass -- a bare
# `module load singularity` silently resolves to a different default on
# this cluster (confirmed live previously: 4.2.0).
module purge; module load singularity/3.6.4
cd /scratch/md5344/evmbench/agent4vul/.claude/worktrees/mgpr-router2
bash scripts/mgpr/run_corrected_evaluation.sh "${1:-corrected_eval_${SLURM_JOB_ID}}"
