"""Track A step 1: frozen, non-cherry-pickable six-requirement selection.

Per the RTF plan's Rev. 3 finalization patch: candidates are derived purely
from the already-parsed, hash-locked L1 Requirement Corpus, using only
mechanical fields the corpus parser already computed from spec text
(conditioned_scope_clause.is_unconditioned_subject, enumerated_terms,
overriding_requirements, and each requirement's own section number for
compiler-bug identification) -- never from analyzer coverage or EVMbench
correspondence, which are not consulted anywhere in this script.

Category definitions (mechanical, computed BEFORE selection, not tuned
after seeing which candidates look easy):

  1. VERSION_ONLY compiler requirement (S):
     level == S, under the Compiler Bugs subsection (secno 5.1.3), and
     conditioned_scope_clause.is_unconditioned_subject == True -- the bug
     applies to any Tested Code compiled with the affected version, no
     additional pattern trigger.
  2. Unconditioned pure-syntactic S requirement:
     level == S, is_unconditioned_subject == True, >=1 enumerated_terms,
     NOT a compiler-bug requirement.
  3. Conditioned / PATTERN_AND_VERSION S requirement:
     level == S, under Compiler Bugs (secno 5.1.3), and
     is_unconditioned_subject == False -- needs both a pattern trigger and
     a version check.
  4. M pair -- deterministic-trigger candidate:
     level == M, NOT a compiler-bug requirement, has >=1
     overriding_requirements (a concrete override/exception anchor).
  5. M pair -- full-semantic-review candidate:
     level == M, NOT a compiler-bug requirement, zero
     overriding_requirements AND zero enumerated_terms (abstract,
     business-logic language with no concrete anchor).
  6. Any Q requirement (small population, no further sub-filter needed).

Within a category with more than one candidate, the tie-break is
deterministic random sampling seeded from the frozen L1 corpus hash (never
a manually-adjustable value): index = int(sha256(corpus_hash + category
name), 16) % len(sorted_candidates), applied to the alphabetically-sorted
candidate list.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS_JSON = ROOT / "rtf" / "l1_corpus" / "requirement_corpus.json"
CORPUS_HASH_FILE = ROOT / "rtf" / "l1_corpus" / "requirement_corpus.sha256"
OUT_DIR = Path(__file__).resolve().parent
OUT_JSON = OUT_DIR / "selected_requirements.json"


def is_compiler_bug_section(req: dict) -> bool:
    sec = req.get("section") or {}
    return sec.get("secno") in ("5.1.3", "5.2.5")


def deterministic_pick(candidates: list[str], seed_material: str) -> tuple[str, dict]:
    sorted_candidates = sorted(candidates)
    digest = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(sorted_candidates)
    picked = sorted_candidates[index]
    return picked, {
        "sorted_candidate_pool": sorted_candidates,
        "seed_material": seed_material,
        "seed_digest": digest,
        "index_formula": "int(sha256(seed_material), 16) % len(sorted_candidate_pool)",
        "index": index,
    }


def build_categories(reqs: list[dict]) -> dict[str, list[str]]:
    by_id = {r["req_id"]: r for r in reqs}

    def unconditioned(r):
        return r["conditioned_scope_clause"]["is_unconditioned_subject"] is True

    def has_terms(r):
        return len(r["enumerated_terms"]) > 0

    def has_override(r):
        return len(r["overriding_requirements"]) > 0

    cat1 = [
        r["req_id"]
        for r in reqs
        if r["level"] == "S" and is_compiler_bug_section(r) and unconditioned(r)
    ]
    cat2 = [
        r["req_id"]
        for r in reqs
        if r["level"] == "S"
        and unconditioned(r)
        and has_terms(r)
        and not is_compiler_bug_section(r)
    ]
    cat3 = [
        r["req_id"]
        for r in reqs
        if r["level"] == "S" and is_compiler_bug_section(r) and not unconditioned(r)
    ]
    cat4_deterministic_trigger = [
        r["req_id"]
        for r in reqs
        if r["level"] == "M" and not is_compiler_bug_section(r) and has_override(r)
    ]
    cat5_full_semantic = [
        r["req_id"]
        for r in reqs
        if r["level"] == "M"
        and not is_compiler_bug_section(r)
        and not has_override(r)
        and not has_terms(r)
    ]
    cat6_q_any = [r["req_id"] for r in reqs if r["level"] == "Q"]

    return {
        "1_version_only_compiler_S": cat1,
        "2_unconditioned_pure_syntactic_S": cat2,
        "3_conditioned_pattern_and_version_S": cat3,
        "4_M_deterministic_trigger_candidate": cat4_deterministic_trigger,
        "5_M_full_semantic_review_candidate": cat5_full_semantic,
        "6_Q_any": cat6_q_any,
    }


def main() -> None:
    corpus = json.loads(CORPUS_JSON.read_text())
    corpus_hash = CORPUS_HASH_FILE.read_text().split()[0]
    reqs = corpus["requirements"]

    categories = build_categories(reqs)

    selection = {}
    for cat_name, candidates in categories.items():
        if not candidates:
            raise RuntimeError(f"Category '{cat_name}' has zero candidates -- selection protocol cannot proceed.")
        if len(candidates) == 1:
            picked = candidates[0]
            detail = {
                "sorted_candidate_pool": candidates,
                "seed_material": None,
                "seed_digest": None,
                "index_formula": "single candidate, no sampling needed",
                "index": 0,
            }
        else:
            seed_material = f"{corpus_hash}::{cat_name}"
            picked, detail = deterministic_pick(candidates, seed_material)
        selection[cat_name] = {"selected_req_id": picked, "selection_detail": detail}

    by_id = {r["req_id"]: r for r in reqs}
    selected_ids = [v["selected_req_id"] for v in selection.values()]

    freeze_record = {
        "selection_frozen_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "corpus_hash_selection_was_derived_from": corpus_hash,
        "protocol": "See module docstring in rtf/track_a/select_candidates.py -- "
        "category rules are computed from L1 mechanical fields only, before "
        "any analyzer-coverage check or EVMbench correspondence lookup.",
        "categories": selection,
        "selected_req_ids": selected_ids,
        "selected_requirement_summaries": [
            {
                "req_id": rid,
                "level": by_id[rid]["level"],
                "title": by_id[rid]["title"],
                "section": by_id[rid]["section"],
            }
            for rid in selected_ids
        ],
        "substitution_log": [],
        "note": "Substitution is permitted ONLY for genuine miscategorization "
        "discovered under full L3/L4 review, never for a requirement turning "
        "out to be difficult or lacking analyzer candidates -- see the RTF "
        "plan's Rev. 3 finalization patch, item 2.",
    }

    OUT_JSON.write_text(json.dumps(freeze_record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    freeze_hash = hashlib.sha256(OUT_JSON.read_bytes()).hexdigest()
    (OUT_DIR / "selected_requirements.sha256").write_text(f"{freeze_hash}  {OUT_JSON.name}\n")

    print("Category populations:")
    for cat_name, candidates in categories.items():
        print(f"  {cat_name}: {len(candidates)} candidate(s)")
    print()
    print("Selected (frozen):")
    for rid in selected_ids:
        print(f"  {rid}  [{by_id[rid]['level']}]  {by_id[rid]['title']}")
    print()
    print(f"Freeze file: {OUT_JSON}")
    print(f"Freeze hash: {freeze_hash}")


if __name__ == "__main__":
    main()
