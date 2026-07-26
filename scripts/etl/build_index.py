"""A3 + A3.5 CLI: full-corpus index (content-hash, dedup, label-join) +
stratified 200-contract sample (see plan A3/A3.5). Login-node fine (cheap:
hashing + label joins, no compilation).

`python -m scripts.etl.build_index <corpus_root> --messiq
    [--out-dir data/gnn/index] [--sample-size 200] [--seed 0]`

**Two label-join modes:**
- `--messiq` (the real Resource 2 layout, confirmed against the actual
  download -- see `data/gnn/raw/MANIFEST.md`): 4 vuln-class directories,
  each with `sourcecode/<name>.sol` + parallel `final_<class>_name.txt` /
  `final_<class>_label.txt`. Only `<class>/sourcecode/*.sol` files are
  compilation units -- `bytecode/`, `binarycode/`, `source_graph_data/`,
  `binary_graph_data/`, `error_data/`, `tools/` are NOT scanned (the
  `source_graph_data`/`binary_graph_data` `.sol`-named files are Messi-Q's
  own non-Solidity graph format, not source code -- see MANIFEST.md).
  Per-class sample ids collide (`reentrancy/3.sol` !=
  `Integeroverflow/3.sol`, confirmed via sha256), so Resource 2 is
  effectively **4 independent single-label corpora**: `positive_classes`
  here is always `[]` or exactly one class, never a true multi-hot union,
  since the same contract essentially never appears labeled under two
  classes. A3.5's stratification cells reflect that reality rather than the
  plan's general multi-hot case.
- `--labels-json PATH` (generic fallback): a flat JSON list of raw label
  records in `labels.parse_labels`'s provisional per-record-dict shape,
  joined under the `native_id == source_relpath` assumption. Kept for any
  other dataset with that shape; not what Resource 2 actually looks like.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from a4v.gnn.etl.extract import build_index
from a4v.gnn.etl.labels import parse_labels, parse_messiq_name_label_pairs
from a4v.gnn.etl.sample import stratified_sample
from a4v.repair import _candidate_versions_from_pragma, _PRAGMA_RE

# tools/ holds the dataset's own preprocessing scripts, not vuln-class data.
_MESSIQ_NON_CLASS_DIRS = {"tools"}


def _pragma_major_minor_by_relpath(sol_files: list[Path], root: Path) -> dict[str, str | None]:
    """Cheap per-file pragma-major.minor detection for A3.5's stratification
    cells -- reuses repair.py's pure regex/candidate-extraction helpers (not
    pragma.py's full satisfiability resolver, which is A4's concern at
    compile time). Reads each file's own pragma directly rather than
    `repair.py`'s `_detect_pragma_versions` (which scans a whole directory
    recursively) since Resource 2 may put many unrelated contracts in one
    directory -- a per-directory scan would misattribute pragmas across them.
    """
    result: dict[str, str | None] = {}
    for sol_file in sol_files:
        try:
            text = sol_file.read_text(errors="ignore")
        except OSError:
            text = ""
        exprs = [m.group(1).strip() for m in _PRAGMA_RE.finditer(text)]
        versions = _candidate_versions_from_pragma(exprs)
        relpath = str(sol_file.resolve().relative_to(root.resolve()))
        result[relpath] = ".".join(versions[0].split(".")[:2]) if versions else None
    return result


def _label_refs_by_relpath(raw_labels: list[dict], root: Path) -> dict[str, dict]:
    records = parse_labels(raw_labels)
    refs: dict[str, dict] = {}
    for native_id, record in records.items():
        positive = sorted({a.vuln_class for a in record.annotations})
        refs[native_id] = {"native_id": native_id, "positive_classes": positive}
    return refs


def _messiq_class_dirs(root: Path) -> list[Path]:
    return sorted(
        d for d in root.iterdir()
        if d.is_dir() and d.name not in _MESSIQ_NON_CLASS_DIRS and not d.name.startswith(".")
    )


def messiq_sol_files_and_label_refs(root: Path) -> tuple[list[Path], dict[str, dict]]:
    """Real Resource 2 layout: returns (sourcecode .sol files to compile,
    {source_relpath: {"native_id", "positive_classes"}}), joined per
    vuln-class directory. Names in `final_<class>_name.txt` whose file was
    moved to that class's own `error_data/` (the dataset's own quality
    filter, ~9% for reentrancy) are simply not compilation units here --
    they're absent from `sourcecode/`, so they never enter `sol_files`.
    """
    sol_files: list[Path] = []
    label_refs: dict[str, dict] = {}
    for cls_dir in _messiq_class_dirs(root):
        cls = cls_dir.name
        name_file = cls_dir / f"final_{cls.lower()}_name.txt"
        label_file = cls_dir / f"final_{cls.lower()}_label.txt"
        sourcecode_dir = cls_dir / "sourcecode"
        if not (name_file.exists() and label_file.exists() and sourcecode_dir.is_dir()):
            print(f"WARNING: {cls_dir} missing expected name/label/sourcecode layout -- skipping")
            continue

        records = parse_messiq_name_label_pairs(name_file, label_file, cls)
        for native_id, record in records.items():
            name = native_id.split("/", 1)[1]
            sol_path = sourcecode_dir / name
            if not sol_path.exists():
                continue
            sol_files.append(sol_path)
            positive = [a.vuln_class for a in record.annotations]
            relpath = str(sol_path.resolve().relative_to(root.resolve()))
            label_refs[relpath] = {"native_id": native_id, "positive_classes": positive}

    return sorted(sol_files), label_refs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("corpus_root", type=Path)
    ap.add_argument("--messiq", action="store_true",
                     help="use the real Resource 2 layout (4 class dirs, name/label.txt pairs)")
    ap.add_argument("--labels-json", type=Path, default=None,
                     help="generic fallback: flat JSON list of raw label records (see labels.py)")
    ap.add_argument("--out-dir", type=Path, default=Path("data/gnn/index"))
    ap.add_argument("--sample-size", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    root = args.corpus_root

    if args.messiq:
        sol_files, label_refs = messiq_sol_files_and_label_refs(root)
    else:
        sol_files = sorted(root.rglob("*.sol"))
        label_refs = {}
        if args.labels_json:
            raw_labels = json.loads(args.labels_json.read_text())
            label_refs = _label_refs_by_relpath(raw_labels, root)

    pragma_by_relpath = _pragma_major_minor_by_relpath(sol_files, root)

    rows, non_self_contained = build_index(
        sol_files, root,
        label_refs_by_relpath=label_refs,
        pragma_major_minor_by_relpath=pragma_by_relpath,
    )

    if label_refs and not args.messiq:
        joined_relpaths = {r.source_relpath for r in rows if r.merged_classes}
        unjoined = set(label_refs) - joined_relpaths
        if unjoined:
            print(
                f"WARNING: {len(unjoined)}/{len(label_refs)} label native_ids never "
                "joined to a source file under the native_id==source_relpath "
                "assumption -- revisit build_index.py's join key against the "
                "real Messi-Q schema."
            )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    index_path = args.out_dir / "full_index.jsonl"
    with index_path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row.__dict__, sort_keys=True) + "\n")

    sample = stratified_sample(rows, target_n=args.sample_size, seed=args.seed)
    sample_path = args.out_dir / f"sample_{args.sample_size}.json"
    sample_path.write_text(json.dumps({
        "seed": args.seed,
        "target_n": args.sample_size,
        "contract_ids": sample.contract_ids,
        "cell_counts": sample.cell_counts,
    }, indent=2, sort_keys=True))

    print(f"indexed {len(rows)} compilation unit(s) ({non_self_contained} skipped, not self-contained)")
    print(f"-> {index_path}")
    print(f"sampled {len(sample.contract_ids)} contract(s) across {len(sample.cell_counts)} cell(s)")
    print(f"-> {sample_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
