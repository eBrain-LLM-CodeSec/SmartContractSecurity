"""MGPR M6 CLI: builds benchmark_registry.jsonl from the pinned EVMbench
detect-split task list, joining task_info.csv (per-finding ground truth),
task_info_audits.csv (per-audit metadata), and each finding's full
findings/<VULN-ID>.md writeup (plan section 6.2).

Genuinely new (not an extension of scripts/etl/build_index.py or
build_feasibility_report.py -- those two build a registry over the
unrelated Messi-Q GNN training corpus, not EVMbench audits; confirmed by
direct read, not inferred from filenames).

`python -m scripts.mgpr.build_registry
    [--evmbench-root /scratch/md5344/evmbench/repo/frontier-evals/project/evmbench]
    [--out data/mgpr/benchmark_registry.jsonl]`

Registry size is never hard-coded: the audit count is whatever
`splits/detect-tasks.txt` contains at run time, and the finding count is
the number of task_info.csv rows whose audit is in that list -- read
directly, never derived by multiplying audit count (plan section 6.2's
explicit correction).
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from scripts.mgpr.citation_resolution import extract_citations

_DEFAULT_EVMBENCH_ROOT = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench")


def _read_pinned_audit_ids(evmbench_root: Path) -> list[str]:
    path = evmbench_root / "splits" / "detect-tasks.txt"
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def _read_csv_rows(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _findings_md_text(evmbench_root: Path, audit_id: str, vuln: str) -> str | None:
    path = evmbench_root / "audits" / audit_id / "findings" / f"{vuln}.md"
    if not path.exists():
        return None
    return path.read_text(errors="ignore")


def build_registry(evmbench_root: Path) -> list[dict]:
    pinned_ids = _read_pinned_audit_ids(evmbench_root)
    pinned_set = set(pinned_ids)

    audit_meta_rows = _read_csv_rows(evmbench_root / "audits" / "task_info_audits.csv")
    audit_meta_by_id = {r["audit"]: r for r in audit_meta_rows if r["audit"] in pinned_set}

    finding_rows = _read_csv_rows(evmbench_root / "audits" / "task_info.csv")
    findings_by_audit: dict[str, list[dict]] = {aid: [] for aid in pinned_ids}
    for row in finding_rows:
        audit_id = row["audit"]
        if audit_id not in pinned_set:
            continue
        vuln = row["vuln"]
        md_text = _findings_md_text(evmbench_root, audit_id, vuln)
        cited_locations = extract_citations(md_text) if md_text else []
        findings_by_audit[audit_id].append({
            "finding_id": f"{audit_id}/{vuln}",
            "vuln": vuln,
            "description": row["description"],
            "n_auditors_found": int(row["n_auditors_found"]) if row["n_auditors_found"] else None,
            "award": float(row["award"]) if row["award"] else None,
            "findings_md_path": str(
                (evmbench_root / "audits" / audit_id / "findings" / f"{vuln}.md").resolve()
            ) if md_text is not None else None,
            "github_cited_locations": cited_locations,
        })

    registry = []
    for audit_id in pinned_ids:
        meta = audit_meta_by_id.get(audit_id, {})
        registry.append({
            "audit_id": audit_id,
            "project_description": meta.get("project"),
            "codebase_sloc": int(meta["codebase_sloc"]) if meta.get("codebase_sloc") else None,
            "n_contracts": int(meta["n_contracts"]) if meta.get("n_contracts") else None,
            "findings": findings_by_audit[audit_id],
        })
    return registry


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--evmbench-root", type=Path, default=_DEFAULT_EVMBENCH_ROOT)
    ap.add_argument("--out", type=Path, default=Path("data/mgpr/benchmark_registry.jsonl"))
    args = ap.parse_args(argv)

    registry = build_registry(args.evmbench_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for row in registry:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    total_findings = sum(len(r["findings"]) for r in registry)
    print(f"registry: {len(registry)} audit(s) (pinned detect split), {total_findings} finding(s)")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
