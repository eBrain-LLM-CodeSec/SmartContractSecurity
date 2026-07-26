"""A5 -- self-contained-only compilation, subprocess entry point (see plan A5).

`python -m a4v.gnn.etl.compile_one <job_json_path> <result_json_path>`

Reads a job spec (target `.sol` path, ordered solc candidates, per-candidate
timeout, label + output info) and writes a result spec (status, chosen
solc_version if any, every candidate attempted with its own outcome) to
`result_json_path`. Never raises to the caller -- every failure mode becomes
a `status` value the orchestrator (`scripts/etl/run_sample.py`) can log
without special-casing exceptions; that script owns the *outer* backstop
timeout (`subprocess.run(timeout=...)`, containing genuine hangs/segfaults
of this whole process) and resume.

MVP compiles **plain, self-contained Solidity only** -- callers pass
`skip_non_self_contained: true` for anything A3/A1 flagged as needing a real
build system (Foundry/Hardhat/remappings), and this just records that
status rather than attempting one.

Per-candidate timeout (review point 11: a first candidate that hangs must
not consume the whole budget and mislabel a contract as TIMEOUT) is enforced
with `SIGALRM` around each `ProgramGraph.build` call, not a nested
subprocess per candidate -- this process is Linux-only (Jubail HPC compute
nodes) and single-threaded in its main loop, so `signal.alarm` is sufficient
and keeps the process tree exactly two levels deep
(`run_sample.py` -> `compile_one.py`), matching the plan's architecture.

Every candidate uses the **explicit-solc-path kwarg** verified in Part 0
(`extra_kwargs={"solc": <abs path>}`) -- never solc-select's global
switch -- so concurrent workers never share or race on `global-version`.
"""
from __future__ import annotations

import json
import signal
import sys
import time
from contextlib import contextmanager
from pathlib import Path

from a4v.graph import BuildFailed, ProgramGraph
from a4v.gnn.etl import labels as labels_mod
from a4v.gnn.etl.map_labels import map_to_nodes
from a4v.gnn.etl.serialize import build_record, write_record

STATUS_OK = "OK"
STATUS_COMPILE_FAILED = "COMPILE_FAILED"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_CRASHED = "CRASHED"
STATUS_SOLC_MISSING = "SOLC_MISSING"
STATUS_EMPTY_GRAPH = "EMPTY_GRAPH"
STATUS_UNRESOLVED_DEPS = "UNRESOLVED_DEPS"
STATUS_SKIPPED_NONSELFCONTAINED = "SKIPPED_NONSELFCONTAINED"
STATUS_WRITE_FAILED = "WRITE_FAILED"

DEFAULT_CANDIDATE_TIMEOUT_SECONDS = 180


class CandidateTimeout(Exception):
    pass


@contextmanager
def _alarm(seconds: int):
    if seconds <= 0:
        yield
        return

    def _handler(signum, frame):
        raise CandidateTimeout(f"candidate exceeded {seconds}s")

    previous = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def compile_with_candidates(
    target: Path,
    candidates: list[dict],
    candidate_timeout_seconds: int = DEFAULT_CANDIDATE_TIMEOUT_SECONDS,
    solc_kwarg: str = "solc",
):
    """`candidates`: [{"solc_version": str, "solc_path": str, "extra_kwargs":
    {...}}], tried **in order**; a hung/failed candidate never consumes more
    than its own `candidate_timeout_seconds`. Returns
    `(graph_or_None, chosen_version_or_None, status, attempts)`.
    """
    attempts: list[dict] = []
    if not candidates:
        return None, None, STATUS_UNRESOLVED_DEPS, attempts

    for cand in candidates:
        solc_path = cand["solc_path"]
        version = cand["solc_version"]
        extra_kwargs = dict(cand.get("extra_kwargs") or {})
        extra_kwargs[solc_kwarg] = solc_path

        if not Path(solc_path).exists():
            attempts.append({"version": version, "ok": False, "status": STATUS_SOLC_MISSING,
                              "error": f"{solc_path} not found"})
            continue

        start = time.monotonic()
        try:
            with _alarm(candidate_timeout_seconds):
                graph = ProgramGraph.build(target, extra_kwargs=extra_kwargs)
        except CandidateTimeout as e:
            attempts.append({"version": version, "ok": False, "status": STATUS_TIMEOUT,
                              "error": str(e), "seconds": time.monotonic() - start})
            continue
        except BuildFailed as e:
            attempts.append({"version": version, "ok": False, "status": STATUS_COMPILE_FAILED,
                              "error": str(e), "seconds": time.monotonic() - start})
            continue
        except Exception as e:  # noqa: BLE001 -- any other exception is this candidate's CRASHED, not fatal to the loop
            attempts.append({"version": version, "ok": False, "status": STATUS_CRASHED,
                              "error": str(e), "seconds": time.monotonic() - start})
            continue

        if len(graph.nodes_of_kind("function")) == 0:
            # Interface-only/abstract files compile but yield zero function
            # nodes -- record as a dataset-bias signal (A8), not a retry target.
            attempts.append({"version": version, "ok": False, "status": STATUS_EMPTY_GRAPH,
                              "seconds": time.monotonic() - start})
            continue

        attempts.append({"version": version, "ok": True, "status": STATUS_OK,
                          "seconds": time.monotonic() - start})
        return graph, version, STATUS_OK, attempts

    last_status = attempts[-1]["status"] if attempts else STATUS_COMPILE_FAILED
    return None, None, last_status, attempts


def run_job(job: dict) -> dict:
    if job.get("skip_non_self_contained"):
        return {"status": STATUS_SKIPPED_NONSELFCONTAINED, "solc_version": None, "solc_attempts": []}

    target = Path(job["target"])
    graph, version, status, attempts = compile_with_candidates(
        target, job["candidates"], job.get("candidate_timeout_seconds", DEFAULT_CANDIDATE_TIMEOUT_SECONDS),
    )
    if graph is None:
        return {"status": status, "solc_version": None, "solc_attempts": attempts}

    class_names = job["class_names"]
    label_record_raw = job.get("label_record")
    if label_record_raw is not None:
        lr = labels_mod.LabelRecord(
            native_id=label_record_raw["native_id"],
            granularity=label_record_raw["granularity"],
            annotations=tuple(labels_mod.Annotation(**a) for a in label_record_raw["annotations"]),
        )
        mapping = map_to_nodes(lr, graph, class_names)
        node_labels, graph_labels, granularity = mapping.node_labels, mapping.graph_labels, lr.granularity
    else:
        node_labels, graph_labels, granularity = None, None, "none"

    # `attempts` (this function's local var) carries wall-clock "seconds" --
    # volatile timing that must live only in the manifest attempt log, never
    # in the content-addressed record (see serialize.py's determinism
    # contract: JSON is ints/strings only, no floats).
    record_safe_attempts = [
        {k: v for k, v in a.items() if k != "seconds"} for a in attempts
    ]

    json_part, arrays_part = build_record(
        graph,
        contract_id=job["contract_id"],
        native_ids=job["native_ids"],
        source_relpath=job["source_relpath"],
        content_sha256=job["content_sha256"],
        label_granularity=granularity,
        class_names=class_names,
        node_labels=node_labels,
        graph_labels=graph_labels,
        solc_version=version,
        solc_attempts=record_safe_attempts,
        pragma_raw=job.get("pragma_raw", []),
        slither_version=job.get("slither_version", ""),
        crytic_compile_version=job.get("crytic_compile_version", ""),
        etl_git_rev=job.get("etl_git_rev", ""),
    )

    try:
        write_record(Path(job["out_dir"]), job["contract_id"], json_part, arrays_part)
    except OSError as e:
        return {"status": STATUS_WRITE_FAILED, "solc_version": version, "solc_attempts": attempts, "error": str(e)}

    return {"status": STATUS_OK, "solc_version": version, "solc_attempts": attempts}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    job_path, result_path = Path(argv[0]), Path(argv[1])
    job = json.loads(job_path.read_text())

    try:
        result = run_job(job)
    except Exception as e:  # noqa: BLE001 -- a result file must exist even on an unexpected crash
        result = {"status": STATUS_CRASHED, "solc_version": None, "solc_attempts": [], "error": str(e)}

    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, sort_keys=True))
    return 0 if result.get("status") == STATUS_OK else 1


if __name__ == "__main__":
    raise SystemExit(main())
