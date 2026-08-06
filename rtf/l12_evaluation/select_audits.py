"""Frozen, non-cherry-pickable EVMbench audit sampling protocol for
L12's next evaluation extension.

Mirrors `rtf/track_a/select_candidates.py`'s exact discipline, applied to
audit selection instead of requirement selection: candidates are drawn
from the real, on-disk audit pool; ties are broken by DETERMINISTIC
random sampling seeded from an already-frozen artifact hash (never a
manually-adjustable value); the selection is frozen (hashed + timestamped)
BEFORE any compilation attempt, BEFORE checking whether a sampled audit
uses Foundry/has vendored dependencies/compiles cleanly, and BEFORE
looking at what its findings are. Per the plan's own rule (and this
project's explicit instruction for this phase): audits must not be
selected because they look compatible with RTF's implemented predicates
-- compatibility problems discovered AFTER selection are reported as
operational failures for that audit, not grounds for silently swapping
in an easier one. Substitution is permitted only for genuine pool-
construction errors (e.g. a "candidate" that turns out not to be a real
audit directory at all), never for difficulty, exactly Track A's own
substitution rule.

Usage:
    python3 -m rtf.l12_evaluation.select_audits <n> [seed_material_extra]
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDITS_DIR = Path("/scratch/md5344/evmbench/repo/frontier-evals/project/evmbench/audits")
CORPUS_HASH_FILE = REPO_ROOT / "rtf" / "l1_corpus" / "requirement_corpus.sha256"
OUTPUT_PATH = REPO_ROOT / "rtf" / "l12_evaluation" / "AUDIT_SELECTION.json"

# Excluded from the candidate pool, with an explicit, logged reason each --
# NOT selection-time cherry-picking (both exclusions are structural, not
# about compatibility or difficulty):
EXCLUDED = {
    "template": "not a real audit -- the repo's own scaffold/example directory",
    "2023-07-pooltogether": (
        "already used for RTF v1 run 1, and carries a declared SUBSTANTIAL "
        "prior-exposure caveat for this project (EXPOSURE_DECLARATION.json) "
        "-- excluding it from the FRESH sample keeps the new sample's "
        "exposure profile clean (NONE/PARTIAL, not SUBSTANTIAL), which is "
        "the entire point of drawing a new, frozen sample rather than just "
        "reusing pooltogether again"
    ),
}


def list_candidate_pool() -> list[str]:
    all_dirs = sorted(
        p.name for p in AUDITS_DIR.iterdir()
        if p.is_dir() and p.name not in EXCLUDED
    )
    return all_dirs


def select(n: int, seed_extra: str = "") -> dict:
    pool = list_candidate_pool()
    if n > len(pool):
        raise SystemExit(f"Requested {n} audits but only {len(pool)} candidates remain after exclusions.")

    corpus_hash = CORPUS_HASH_FILE.read_text(encoding="utf-8").strip()
    seed_material_base = f"{corpus_hash}::l12_audit_sampling::{seed_extra}"

    remaining = list(pool)
    selected = []
    for i in range(n):
        seed_material = f"{seed_material_base}::draw_{i}"
        seed_digest = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()
        index = int(seed_digest, 16) % len(remaining)
        chosen = remaining.pop(index)
        selected.append({
            "audit_id": chosen,
            "draw_index": i,
            "seed_material": seed_material,
            "seed_digest": seed_digest,
            "index_into_remaining_pool": index,
            "remaining_pool_size_at_draw": len(remaining) + 1,
        })

    return {
        "protocol": "See module docstring -- deterministic sha256-seeded sampling without replacement, mirroring rtf/track_a/select_candidates.py's exact discipline. Frozen before any compilation attempt or compatibility check.",
        "corpus_hash_used_as_seed_root": corpus_hash,
        "full_candidate_pool_size": len(pool) + n,  # pool size BEFORE any draws removed items
        "excluded": EXCLUDED,
        "n_requested": n,
        "selected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "selected_audit_ids": [s["audit_id"] for s in selected],
        "selection_detail": selected,
        "substitution_log": [],
        "substitution_rule": "Substitution permitted ONLY for genuine pool-construction errors (e.g. a selected 'audit' turns out not to be a real, gradeable audit directory), never for compilation difficulty or predicate incompatibility -- exactly Track A's own rule, applied here to audits instead of requirements.",
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python3 -m rtf.l12_evaluation.select_audits <n> [seed_extra]")
    n = int(sys.argv[1])
    seed_extra = sys.argv[2] if len(sys.argv) > 2 else ""

    if OUTPUT_PATH.exists():
        raise SystemExit(
            f"REFUSING TO RE-SELECT: {OUTPUT_PATH} already exists. Selection is frozen "
            f"once written. Delete it first if a genuine pool-construction error requires "
            f"re-selection (log the reason in substitution_log)."
        )

    result = select(n, seed_extra)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Selected {n} audit(s): {result['selected_audit_ids']}")
    print(f"Frozen -> {OUTPUT_PATH}")
