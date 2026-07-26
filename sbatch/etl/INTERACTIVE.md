# Part A GNN ETL — interactive compute-node runs

Per the plan's execution ladder: 10-20 contracts first (all A-steps, records
well-formed, global-version untouched), then 50 via interactive `salloc`
(timeouts + subprocess isolation exercised on a real node), then 200 for the
feasibility deliverable. Never on the login node — `run_sample.py` refuses to
run unless `$SLURM_JOB_ID` is set.

## 1. Allocate an interactive node

```
salloc --partition=<partition> --time=02:00:00 --cpus-per-task=4 --mem=16G
```

Confirms you're on a compute node (not the login host) before anything else:

```
echo "SLURM_JOB_ID=$SLURM_JOB_ID"
hostname
```

## 2. Build the index + sample (cheap, login-node-safe, but fine here too)

```
cd /scratch/md5344/evmbench/agent4vul
.venv/bin/python -m scripts.etl.build_index data/gnn/raw \
    --labels-json <path-to-parsed-raw-labels.json> \
    --out-dir data/gnn/index \
    --sample-size 50   # 200 for the real deliverable run
```

## 3. Provision solc for the sample (login node only, needs internet)

Run this step on the **login node**, not inside the `salloc` allocation
(compute nodes may not have internet):

```
.venv/bin/python -m scripts.etl.provision_solc \
    data/gnn/index/sample_50.json data/gnn/index/full_index.jsonl \
    --out data/gnn/index/candidates.json
```

Review `candidates.json`'s `smoke_results` before proceeding -- a failed
smoke test for a major.minor band means every sampled contract on that band
will fail identically; see plan A4's two named contingencies (pinned older
Slither venv; older-glibc Apptainer image) rather than burning the whole
sample budget rediscovering the same failure 5-10 times.

## 4. Compile the sample (compute node, inside the `salloc` session)

```
.venv/bin/python -m scripts.etl.run_sample \
    data/gnn/index/sample_50.json data/gnn/index/full_index.jsonl \
    data/gnn/index/candidates.json \
    --out-dir data/gnn/processed \
    --attempts data/gnn/manifests/attempts.jsonl \
    --class-names reentrancy access_control unchecked_call ...
```

Watch for hangs at this stage specifically -- this is what the 50-contract
interactive step is *for*. If a contract hangs past its outer backstop
(default 600s), `run_sample.py`'s `subprocess.run(timeout=...)` kills it and
logs `CRASHED`; confirm this actually happens for at least one slow/legacy
contract before trusting the 200-contract unattended run.

## 5. Kill-and-resume check (required before trusting the 200-contract run)

Mid-run, from another shell on the same node (or `Ctrl-C` the job and
re-launch the same command):

```
kill -9 <run_sample.py pid>
# then re-run the exact same run_sample.py command
```

Verify:
- `data/gnn/manifests/attempts.jsonl` has one line per attempt, append-only,
  no corruption (a truncated trailing line from the kill is tolerated by
  `manifest.read_attempts`).
- The relaunch's first thing is a **fresh merge** over `attempts.jsonl` (not
  a stale `manifest.jsonl` read) -- already-`OK` contract_ids are skipped and
  logged as `SKIPPED_RESUME`, not silently re-attempted or re-claimed.
- No `SameRunDuplicateClaim` is raised on merge (would indicate a dispatch
  bug double-claiming a contract within one run_id).

## 6. Merge + report

```
.venv/bin/python -m scripts.etl.merge_manifests \
    --attempts data/gnn/manifests/attempts.jsonl \
    --manifest data/gnn/manifests/manifest.jsonl
```

The feasibility report (`a4v/gnn/etl/report.py`, wired into a driver script
once the 200-contract run exists) reads `manifest.jsonl` + the serialized
records in `data/gnn/processed/` + `full_index.jsonl` to produce
`data/gnn/reports/feasibility.json` -- reviewed with the user before any
Part B decision.
