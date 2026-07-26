"""A3.5 -- stratified sample of 200, drawn from the A3 index (see plan A3.5).

Uniform random sampling over 200 contracts is wrong for a feasibility
*report*: it underrepresents rare vuln classes and old pragma bands, resting
headline numbers on single-digit counts. This samples **from the
deduplicated, label-joined A3 index** (never the raw tree), stratified by
`merged_classes x pragma_major_minor` using the full-index cell counts.

**Multi-hot rule**: a contract belongs to every class cell it carries --
sampled per cell (proportional to that cell's size, with a floor per
non-empty cell), allowing overlap across cells, then deduped by
`contract_id` and topped up to the target count. **Unlabeled** contracts (no
`merged_classes`) get their own `"unlabeled"` cell so they're represented but
never crowd out labeled classes.

Deterministic given `seed`. Returns the full per-cell counts alongside the
sample so thin cells stay visible in the sample index / `feasibility.json`,
even ones the sample under- or over-represents.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

UNLABELED_CELL_CLASS = "unlabeled"


def _cell_keys(merged_classes: list[str], pragma_major_minor: str | None) -> list[tuple[str, str | None]]:
    classes = merged_classes if merged_classes else [UNLABELED_CELL_CLASS]
    return [(c, pragma_major_minor) for c in classes]


@dataclass
class SampleResult:
    contract_ids: list[str]
    cell_counts: dict[str, int]  # "class|pragma_major_minor" -> full-index count


def _cell_str(key: tuple[str, str | None]) -> str:
    cls, pmm = key
    return f"{cls}|{pmm}"


def stratified_sample(
    rows,  # list[extract.IndexRow] (duck-typed: .contract_id, .merged_classes, .pragma_major_minor)
    target_n: int = 200,
    seed: int = 0,
    floor_per_cell: int = 1,
) -> SampleResult:
    cells: dict[tuple, list[str]] = {}
    for row in rows:
        for key in _cell_keys(row.merged_classes, row.pragma_major_minor):
            cells.setdefault(key, []).append(row.contract_id)

    all_ids = sorted({row.contract_id for row in rows})
    cell_counts = {_cell_str(k): len(v) for k, v in cells.items()}

    if not all_ids:
        return SampleResult(contract_ids=[], cell_counts=cell_counts)

    target_n = min(target_n, len(all_ids))
    total_cell_weight = sum(len(v) for v in cells.values()) or 1

    rng = random.Random(seed)
    selected: set[str] = set()
    # Which cells a given id would satisfy the floor for, so we know which
    # ids are "critical" if we later need to trim.
    covers: dict[str, set[tuple]] = {}

    for key, ids in sorted(cells.items(), key=lambda kv: _cell_str(kv[0])):
        weight = len(ids) / total_cell_weight
        alloc = max(floor_per_cell, round(target_n * weight))
        alloc = min(alloc, len(ids))
        picked = rng.sample(sorted(ids), alloc)
        for cid in picked:
            selected.add(cid)
            covers.setdefault(cid, set()).add(key)

    # Top up if the floor+proportional pass undershot the target.
    if len(selected) < target_n:
        remaining = sorted(set(all_ids) - selected)
        rng.shuffle(remaining)
        for cid in remaining:
            if len(selected) >= target_n:
                break
            selected.add(cid)

    # Trim if floors across many cells overshot the target -- protect ids
    # that are the *sole* selected representative of some cell.
    if len(selected) > target_n:
        cell_representative_count: dict[tuple, int] = {}
        for cid in selected:
            for key in covers.get(cid, ()):
                cell_representative_count[key] = cell_representative_count.get(key, 0) + 1

        def is_critical(cid: str) -> bool:
            return any(cell_representative_count.get(key, 0) <= 1 for key in covers.get(cid, ()))

        removable = sorted(cid for cid in selected if not is_critical(cid))
        rng.shuffle(removable)
        excess = len(selected) - target_n
        for cid in removable[:excess]:
            selected.discard(cid)
            for key in covers.get(cid, ()):
                cell_representative_count[key] -= 1

        # If still over target (every id was critical), trim deterministically
        # from the full selected set as a last resort -- rare (many singleton
        # cells vs. a small target_n), and documented rather than silent.
        if len(selected) > target_n:
            extra_removable = sorted(selected)
            rng.shuffle(extra_removable)
            for cid in extra_removable:
                if len(selected) <= target_n:
                    break
                selected.discard(cid)

    return SampleResult(contract_ids=sorted(selected), cell_counts=cell_counts)
