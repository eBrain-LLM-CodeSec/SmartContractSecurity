"""L12 freeze-checklist executable validation gate.

Turns the plan's 12-item pre-evaluation freeze checklist into code that
actually blocks a run, not a checklist a human might forget to consult.
Two operations:

- `freeze(path)`: compute the current manifest and write it as the
  CANONICAL frozen manifest at `path`. This is the ONE-TIME "I am now
  freezing the framework" action -- run it once, right before the first
  evaluation, never casually re-run to "update" a frozen manifest (that
  would defeat the point; see the plan's post-evaluation change policy).

- `check_gate(frozen_path)`: recompute the CURRENT state of all 12 items
  fresh, compare every hash against the FROZEN manifest at `frozen_path`,
  and return a `GateResult`. `run_rtf.py`/any evaluation entry point
  MUST call this and check `.passed` before executing a single
  predicate against a real EVMbench target -- if it's not True, the run
  does not proceed. This is what makes the gate "executable" rather than
  a document nobody checks.

Usage (CLI):
    python3 -m rtf.l12_evaluation.freeze_gate freeze [path]
    python3 -m rtf.l12_evaluation.freeze_gate check [path]
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .freeze_manifest import REPO_ROOT, compute_manifest

DEFAULT_FROZEN_PATH = REPO_ROOT / "rtf" / "l12_evaluation" / "FROZEN_MANIFEST.json"


@dataclass
class GateResult:
    passed: bool
    issues: list[str] = field(default_factory=list)
    frozen_manifest: dict | None = None
    current_manifest: dict | None = None

    def report(self) -> str:
        lines = [f"Freeze gate: {'PASS' if self.passed else 'FAIL'}"]
        if self.issues:
            lines.append(f"{len(self.issues)} issue(s):")
            for i in self.issues:
                lines.append(f"  - {i}")
        return "\n".join(lines)


def freeze(path: Path = DEFAULT_FROZEN_PATH) -> dict:
    """Compute and write the canonical frozen manifest. Refuses to
    overwrite an existing frozen manifest silently -- freezing twice
    without an explicit, deliberate reason is exactly the kind of
    silent-reinterpretation risk the plan's post-evaluation change
    policy exists to prevent. Callers that genuinely need to re-freeze
    (e.g. after a logged, permitted correction) must delete the old
    file first, an intentional extra step, not a default.
    """
    if path.exists():
        raise SystemExit(
            f"REFUSING TO FREEZE: {path} already exists. Freezing is a one-time "
            f"action before the first evaluation. If a fix genuinely requires "
            f"re-freezing, delete this file first with a logged reason "
            f"(spec parsing error / incorrect requirement interpretation / "
            f"implementation defect / incorrect analyzer mapping / new expert "
            f"feedback / source spec update -- per the plan's post-evaluation "
            f"change policy). 'Improves EVMbench performance' is never a valid reason."
        )
    manifest = compute_manifest()
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def check_gate(frozen_path: Path = DEFAULT_FROZEN_PATH) -> GateResult:
    """The actual executable gate. Blocks (returns passed=False) if:
    - the frozen manifest doesn't exist at all (freezing was never done),
    - any of the 12 items is missing from either manifest,
    - any of the 12 items' hash differs between frozen and current
      (something changed after the freeze point -- exactly what this
      gate exists to catch),
    - framework_version differs (a version bump without a corresponding
      re-freeze is itself a signal something changed unaccounted-for).
    """
    if not frozen_path.exists():
        return GateResult(
            passed=False,
            issues=[f"No frozen manifest at {frozen_path} -- freezing was never performed. Run `freeze()` first."],
        )

    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    try:
        current = compute_manifest()
    except FileNotFoundError as e:
        return GateResult(passed=False, issues=[f"A required artifact is missing entirely: {e}"], frozen_manifest=frozen)

    issues: list[str] = []

    if frozen.get("framework_version") != current.get("framework_version"):
        issues.append(
            f"framework_version changed since freeze: frozen={frozen.get('framework_version')!r} "
            f"current={current.get('framework_version')!r} -- a version bump without a corresponding "
            f"re-freeze means something changed and was not accounted for."
        )

    frozen_items = frozen.get("freeze_items", {})
    current_items = current.get("freeze_items", {})
    all_keys = set(frozen_items) | set(current_items)
    for key in sorted(all_keys):
        f_item = frozen_items.get(key)
        c_item = current_items.get(key)
        if f_item is None:
            issues.append(f"[{key}] present in CURRENT state but was not in the frozen manifest -- freeze is stale, re-freeze required.")
            continue
        if c_item is None:
            issues.append(f"[{key}] was frozen but is now MISSING entirely -- an artifact was deleted/moved after freezing.")
            continue
        if not f_item.get("sha256"):
            issues.append(f"[{key}] frozen manifest has no sha256 recorded -- unhashed at freeze time, gate cannot trust it.")
            continue
        if f_item["sha256"] != c_item.get("sha256"):
            issues.append(
                f"[{key}] CHANGED since freeze: frozen sha256={f_item['sha256'][:16]}... "
                f"current sha256={c_item.get('sha256', '?')[:16]}... (path: {f_item.get('path')})"
            )

    return GateResult(passed=(len(issues) == 0), issues=issues, frozen_manifest=frozen, current_manifest=current)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("freeze", "check"):
        raise SystemExit("usage: python3 -m rtf.l12_evaluation.freeze_gate {freeze|check} [path]")
    path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_FROZEN_PATH
    if sys.argv[1] == "freeze":
        manifest = freeze(path)
        print(f"Frozen -> {path}")
        print(f"framework_version: {manifest['framework_version']}  git_commit: {manifest['git_commit']}")
    else:
        result = check_gate(path)
        print(result.report())
        sys.exit(0 if result.passed else 1)
