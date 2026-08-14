"""Real-subprocess proof that `arm_g_codex.run_arm_g_bundle`'s timeout
handling kills the WHOLE process tree it spawns, not just the one direct
child. Motivated by a real, live incident (2026-08-14): a real
2024-08-phi investigation's nominal timeout fired but a grandchild
process kept running, because plain `subprocess.run(..., timeout=...)`
only kills the immediate child. Run with:
    .venv/bin/python3 -m rtf.l8_llm_judgment_layer.bundle_agent_experiment.test_arm_g_codex_process_tree_timeout
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import _kill_process_tree

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def test_kill_process_tree_kills_a_grandchild_not_just_the_direct_child():
    """Spawns a real shell that backgrounds a real `sleep 60` grandchild
    and waits -- exactly the shape `codex exec` (a wrapper process that
    can itself start further subprocesses, e.g. the graph MCP server)
    has. `subprocess.run(..., timeout=...)`'s own SIGKILL only ever
    reaches the direct child (the shell); this test proves
    `_kill_process_tree`, given that direct child's pid, kills the
    grandchild too -- the exact gap that let a real Codex process outlive
    its nominal timeout on 2026-08-14.
    """
    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "grandchild_pid"
        proc = subprocess.Popen(
            ["/bin/sh", "-c", f"sleep 60 & echo $! > {pid_file}; wait"],
            start_new_session=True,
        )
        deadline = time.monotonic() + 5
        while not pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.05)

        if not pid_file.exists():
            check("setup: grandchild pid file was written", False, "shell never wrote its pid file in time")
            proc.kill()
            proc.wait(timeout=5)
            return
        grandchild_pid = int(pid_file.read_text().strip())

    check("setup: grandchild is genuinely alive before any kill", _pid_alive(grandchild_pid), grandchild_pid)

    _kill_process_tree(proc.pid, grace_s=0.5)
    proc.wait(timeout=5)

    check("process-tree kill: the direct child (shell) is dead", not _pid_alive(proc.pid), proc.pid)
    check("process-tree kill: the GRANDCHILD (the real gap) is also dead, not orphaned",
          not _pid_alive(grandchild_pid), grandchild_pid)


def test_kill_process_tree_is_a_no_op_on_an_already_exited_pid():
    """Best-effort: must not raise if the process is already gone by the
    time it's called (a genuine race in the real timeout path -- the
    process could exit between TimeoutExpired firing and the kill call).
    """
    proc = subprocess.Popen(["/bin/true"], start_new_session=True)
    proc.wait(timeout=5)
    time.sleep(0.2)
    try:
        _kill_process_tree(proc.pid, grace_s=0.1)
        check("process-tree kill: no exception on an already-exited pid", True)
    except Exception as e:  # noqa: BLE001
        check("process-tree kill: no exception on an already-exited pid", False, f"{type(e).__name__}: {e}")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
