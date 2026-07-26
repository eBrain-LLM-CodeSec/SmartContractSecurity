"""A1 -- discovery & label-schema inspection (see plan A1).

Best-effort, format-agnostic scan of a Resource-2-shaped tree: directory
layout, per-contract file granularity, label granularity (node/function/
line/file) + the vuln-class vocabulary, a pragma histogram, and a
self-containment probe (dangling local-import rate).

This is deliberately heuristic. The plan is explicit that A1 is discovery: we
do not know Messi-Q's exact label schema until A0's download lands (gated on
explicit user go-ahead), so this module scans for common shapes -- JSON/CSV
records carrying some subset of contract/function/line/vulnerability-class
fields -- rather than hardcoding one assumed layout. Run it against the real
extraction once A0 completes and tighten the heuristics against whatever it
finds; `tests/unit/test_discover.py` exercises the mechanics against a
synthetic 5-file fixture tree in the meantime.

This is the plan's "hard stop": if `label_granularity` comes back "file", the
caller (A8, or a human) must treat node-ranking supervision as an open
feasibility question before any further Part-A work is sunk.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

_PRAGMA_RE = re.compile(r"pragma\s+solidity\s+([^;]+);")
_IMPORT_RE = re.compile(r"""import\s+(?:[^"'{}]*?from\s+)?["']([^"']+)["']""")

# Field names that plausibly carry each kind of label locator, in priority
# order (most specific first) -- used only to *infer* granularity, not to
# parse labels for real (that's A2's job, gated on the real format).
_LINE_FIELDS = ("line", "lines", "loc", "line_no", "lineno", "start_line")
_FUNCTION_FIELDS = ("function", "func", "func_name", "function_name", "method")
_CONTRACT_FIELDS = ("contract", "contract_name")
_FILE_FIELDS = ("file", "filename", "path", "source", "source_file")
_CLASS_FIELDS = (
    "vulnerability", "vuln", "vuln_type", "type", "category", "label",
    "class", "cwe", "bug_type",
)

_LABEL_NAME_HINTS = ("label", "vuln", "annotation", "ground_truth", "gt")


@dataclass
class DiscoveryReport:
    root: str
    sol_file_count: int
    label_file_count: int
    label_files: list[str]
    label_granularity: str  # "node" | "function" | "line" | "file" | "unknown" | "none"
    vuln_classes: list[str]
    pragma_histogram: dict[str, int]
    self_contained_rate: float
    dangling_import_count: int
    total_import_count: int
    readme_paths: list[str]
    instructions_paths: list[str]
    sample_sol_files: list[str]
    warnings: list[str] = field(default_factory=list)


def _find_readme_and_instructions(root: Path) -> tuple[list[Path], list[Path]]:
    readmes = sorted(p for p in root.rglob("*") if p.is_file() and p.name.lower().startswith("readme"))
    instr_dirs = [p for p in root.rglob("*") if p.is_dir() and p.name.lower() == "instructions"]
    instr_files: list[Path] = []
    for d in instr_dirs:
        instr_files.extend(sorted(f for f in d.rglob("*") if f.is_file()))
    return readmes, instr_files


def _pragma_histogram(sol_files: list[Path]) -> Counter:
    hist: Counter = Counter()
    for f in sol_files:
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        m = _PRAGMA_RE.search(text)
        hist[m.group(1).strip() if m else "<none>"] += 1
    return hist


def _resolve_import(sol_file: Path, import_path: str, root: Path) -> bool:
    """Best-effort: only resolves relative (./ or ../) local imports. A bare
    package-style import (no leading dot) is treated as *not* locally
    resolvable -- that's the definition of a non-self-contained unit for
    Part A's self-contained-only MVP.
    """
    if not import_path.startswith("."):
        return False
    candidate = (sol_file.parent / import_path).resolve()
    if candidate.exists():
        return True
    if candidate.suffix != ".sol" and candidate.with_suffix(".sol").exists():
        return True
    return False


def _self_containment_probe(sol_files: list[Path], root: Path) -> tuple[int, int]:
    """Returns (dangling_import_count, total_import_count) across sol_files."""
    dangling = 0
    total = 0
    for f in sol_files:
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        for m in _IMPORT_RE.finditer(text):
            total += 1
            import_path = m.group(1)
            if import_path.startswith("."):
                if not _resolve_import(f, import_path, root):
                    dangling += 1
            # non-relative imports (package-style) aren't counted as
            # "dangling" here -- they're a distinct non-self-contained
            # signal that A3/extract.py classifies separately.
    return dangling, total


def _looks_like_label_file(p: Path) -> bool:
    if p.suffix.lower() not in (".json", ".csv", ".jsonl", ".txt"):
        return False
    name = p.name.lower()
    return any(hint in name for hint in _LABEL_NAME_HINTS)


def _find_label_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file() and _looks_like_label_file(p))


def _iter_json_records(p: Path) -> list[dict]:
    try:
        if p.suffix.lower() == ".jsonl":
            records = []
            for line in p.read_text(errors="ignore").splitlines():
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                records.append(obj)
            return records
        raw = json.loads(p.read_text(errors="ignore"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(raw, list):
        return [r for r in raw if isinstance(r, dict)]
    if isinstance(raw, dict):
        # Could be {native_id: {...}} or {"records": [...]} shaped.
        if "records" in raw and isinstance(raw["records"], list):
            return [r for r in raw["records"] if isinstance(r, dict)]
        return [v for v in raw.values() if isinstance(v, dict)]
    return []


def _iter_csv_records(p: Path) -> list[dict]:
    import csv
    try:
        with p.open(newline="", errors="ignore") as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def _first_present(rec: dict, field_names: tuple[str, ...]) -> object | None:
    lower = {k.lower(): v for k, v in rec.items()}
    for name in field_names:
        if name in lower and lower[name] not in (None, "", []):
            return lower[name]
    return None


def _infer_label_granularity_and_classes(label_files: list[Path]) -> tuple[str, set[str]]:
    """Inspect a sample of records across all label files and infer the
    finest granularity actually present, plus the observed class vocabulary.
    Priority: line > function > file (node-level would show up as a line
    or function reference tied to a specific graph element -- this scanner
    can't tell "node" from "function" apart without the real graph, so it
    reports "function" and lets A2/map_labels.py do the exact node join).
    """
    classes: set[str] = set()
    has_line = has_function = has_file_only = False
    any_record = False

    for lf in label_files:
        records = _iter_json_records(lf) if lf.suffix.lower() != ".csv" else _iter_csv_records(lf)
        for rec in records:
            any_record = True
            cls = _first_present(rec, _CLASS_FIELDS)
            if isinstance(cls, str):
                classes.add(cls)
            elif isinstance(cls, list):
                classes.update(str(c) for c in cls)

            if _first_present(rec, _LINE_FIELDS) is not None:
                has_line = True
            elif _first_present(rec, _FUNCTION_FIELDS) is not None:
                has_function = True
            elif _first_present(rec, _FILE_FIELDS) is not None or _first_present(rec, _CONTRACT_FIELDS) is not None:
                has_file_only = True

    if not any_record:
        return "none", classes
    if has_line:
        return "line", classes
    if has_function:
        return "function", classes
    if has_file_only:
        return "file", classes
    return "unknown", classes


def discover(root: str | Path, sample_limit: int = 2000) -> DiscoveryReport:
    root = Path(root)
    warnings: list[str] = []

    sol_files = sorted(root.rglob("*.sol"))
    sample = sol_files[:sample_limit]

    readmes, instr_files = _find_readme_and_instructions(root)
    label_files = _find_label_files(root)
    if not label_files:
        warnings.append(
            "no label files matched heuristic name patterns "
            f"({_LABEL_NAME_HINTS}); label_granularity will be 'none' -- "
            "widen the heuristic once the real layout is known"
        )

    granularity, classes = _infer_label_granularity_and_classes(label_files)
    pragma_hist = _pragma_histogram(sample)
    dangling, total_imports = _self_containment_probe(sample, root)
    self_contained_rate = 1.0 if total_imports == 0 else 1.0 - (dangling / total_imports)

    return DiscoveryReport(
        root=str(root),
        sol_file_count=len(sol_files),
        label_file_count=len(label_files),
        label_files=[str(p.relative_to(root)) for p in label_files],
        label_granularity=granularity,
        vuln_classes=sorted(classes),
        pragma_histogram=dict(pragma_hist.most_common()),
        self_contained_rate=self_contained_rate,
        dangling_import_count=dangling,
        total_import_count=total_imports,
        readme_paths=[str(p.relative_to(root)) for p in readmes],
        instructions_paths=[str(p.relative_to(root)) for p in instr_files],
        sample_sol_files=[str(p.relative_to(root)) for p in sample[:20]],
        warnings=warnings,
    )


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="Root of the extracted dataset tree")
    ap.add_argument(
        "-o", "--out", type=Path,
        default=Path("data/gnn/index/discovery_report.json"),
    )
    args = ap.parse_args()

    report = discover(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(asdict(report), indent=2, sort_keys=True))
    print(json.dumps(asdict(report), indent=2, sort_keys=True))

    if report.label_granularity == "file":
        print(
            "\n*** HARD STOP: labels appear to be file-granularity only. "
            "Node-ranking supervision may not be trainable from this data "
            "alone -- surface this to the user before proceeding past A1. ***"
        )
    elif report.label_granularity in ("none", "unknown"):
        print(
            "\n*** WARNING: could not confidently determine label "
            "granularity -- widen discover.py's heuristics against the "
            "real layout before trusting this report. ***"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
