#!/bin/bash
#SBATCH --job-name=gnn-smoke
#SBATCH --partition=preempt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH -o /scratch/md5344/evmbench/agent4vul/logs_gnn_smoke.%J.out
#SBATCH -e /scratch/md5344/evmbench/agent4vul/logs_gnn_smoke.%J.err
# **** all #SBATCH lines above this ****

cd /scratch/md5344/evmbench/agent4vul
.venv/bin/python -m scripts.etl.smoke_real_sample --n-per-class 5
