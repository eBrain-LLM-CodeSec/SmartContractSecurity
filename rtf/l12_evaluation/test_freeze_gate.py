"""Unit tests for the freeze gate's drift-detection logic. Uses
synthetic manifests (not the real repo's) so these tests don't depend on
whether the real FROZEN_MANIFEST.json exists yet.
Run with:
    .venv/bin/python3 -m rtf.l12_evaluation.test_freeze_gate
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from .freeze_gate import check_gate

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _write(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest), encoding="utf-8")


def test_missing_frozen_manifest_fails_gate():
    with tempfile.TemporaryDirectory() as tmp:
        result = check_gate(Path(tmp) / "does_not_exist.json")
        check("gate: fails when no frozen manifest exists at all", not result.passed, result.issues)
        check("gate: failure message explains freezing was never done", any("never performed" in i for i in result.issues), result.issues)


def test_gate_passes_when_frozen_matches_current():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "frozen.json"
        # Freeze against the REAL current repo state, then immediately re-check --
        # nothing changed in between, so this must pass.
        from .freeze_manifest import compute_manifest
        manifest = compute_manifest()
        _write(path, manifest)
        result = check_gate(path)
        check("gate: passes when current state exactly matches the frozen manifest", result.passed, result.issues)


def test_gate_fails_on_changed_item_hash():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "frozen.json"
        from .freeze_manifest import compute_manifest
        manifest = compute_manifest()
        # Tamper with one item's hash to simulate a real post-freeze change.
        manifest["freeze_items"]["7_custom_predicates"]["sha256"] = "0" * 64
        _write(path, manifest)
        result = check_gate(path)
        check("gate: fails when one item's hash was tampered/changed since freeze", not result.passed, result.issues)
        check("gate: the specific changed item is named in the issue list", any("7_custom_predicates" in i for i in result.issues), result.issues)


def test_gate_fails_on_missing_item():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "frozen.json"
        from .freeze_manifest import compute_manifest
        manifest = compute_manifest()
        del manifest["freeze_items"]["11_evmbench_correspondence"]
        _write(path, manifest)
        result = check_gate(path)
        check("gate: fails when an item present in current state is entirely absent from the frozen manifest", not result.passed, result.issues)


def test_gate_fails_on_unhashed_item():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "frozen.json"
        from .freeze_manifest import compute_manifest
        manifest = compute_manifest()
        manifest["freeze_items"]["2_requirement_corpus"]["sha256"] = ""
        _write(path, manifest)
        result = check_gate(path)
        check("gate: fails when a frozen item has no sha256 recorded (unhashed)", not result.passed, result.issues)


def test_gate_fails_on_framework_version_mismatch():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "frozen.json"
        from .freeze_manifest import compute_manifest
        manifest = compute_manifest()
        manifest["framework_version"] = "0.0.1-stale"
        _write(path, manifest)
        result = check_gate(path)
        check("gate: fails when framework_version differs between frozen and current", not result.passed, result.issues)


def main() -> int:
    tests = [
        test_missing_frozen_manifest_fails_gate,
        test_gate_passes_when_frozen_matches_current,
        test_gate_fails_on_changed_item_hash,
        test_gate_fails_on_missing_item,
        test_gate_fails_on_unhashed_item,
        test_gate_fails_on_framework_version_mismatch,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
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
