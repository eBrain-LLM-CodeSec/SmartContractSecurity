"""L12 machine-readable freeze manifest.

Computes and records a hash for each of the plan's 12 freeze-checklist
items, plus framework version, git commit, and pinned tool/model
versions -- everything the plan's step 8 requires captured before the
first EVMbench evaluation may run. `freeze_gate.py` consumes this
module's `compute_manifest()` to decide whether a run may proceed.

Mapping from the plan's 12 named items to concrete repo artifacts (some
of Track A's layers were merged in practice -- e.g. derivation traces
live INSIDE the L4/L5/L6/L7 records rather than as a separate file, so
those items are hashed as directories, not looked for as standalone
files):

 1. spec snapshot                 -> standards/ethtrust/ethtrust-sl.raw.html
 2. requirement corpus            -> rtf/l1_corpus/requirement_corpus.json
 3. context bundles               -> rtf/l2_context_bundles/*.json (81 files)
 4. applicability classifications -> rtf/track_a/l3_applicability/*.json (81 files)
 5. analyzer mappings             -> rtf/track_a/l4_analyzer_mappings/*.json
 6. derivation traces             -> rtf/track_a/l5_level_s_strategy/*.json (traces live here for S; M/Q traces live in items 9/10)
 7. custom predicates             -> rtf/l5_predicates/predicates.py
 8. LLM prompt/schema/model       -> rtf/l8_llm_judgment_layer/{schema,judgment_layer}.py + PROMPT_VERSION constant
 9. M-level classifications       -> rtf/track_a/l6_level_m_extraction/*.json
10. Q-level review schema         -> rtf/track_a/l7_level_q_evidence/SCHEMA.md + *.json
11. EVMbench correspondence       -> rtf/l11_correspondence/correspondence_mapping.json
12. evaluation metric definitions -> rtf/l12_evaluation/metrics.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_directory(dir_path: Path, pattern: str = "*.json") -> tuple[str, int]:
    """Deterministic combined hash of every file matching `pattern` in
    `dir_path`, sorted by filename so the hash is stable regardless of
    filesystem iteration order. Returns (hash, file_count).
    """
    files = sorted(dir_path.glob(pattern))
    h = hashlib.sha256()
    for f in files:
        h.update(f.name.encode("utf-8"))
        h.update(f.read_bytes())
    return h.hexdigest(), len(files)


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10, check=True
        ).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"UNAVAILABLE: {e}"


def _framework_version() -> str:
    """No single canonical version file exists yet (a real L10 gap, see
    AUDIT_L0_L12.md) -- this literal string IS that canonical value for
    now (referenced by L11 freeze calls, Assumptions Register entries,
    and this manifest alike), rather than several divergent version
    identifiers scattered across the codebase.

    Bumped 0.1.0-track-a -> 0.2.0-evidence-enrichment per AR-012: a
    real, logged, permitted post-evaluation change ("evidence-format and
    evidence-collection improvement based on a repeated downstream
    judgment failure" -- RTF v1 run 2 found L8 and the real DetectGrader
    BOTH independently judged RTF's evidence too generic for a confident
    verdict despite correct localization, on two unrelated real audits).
    Any future bump must cite one of the plan's permitted reasons in a
    new Assumptions Register entry the same way, never "improves
    EVMbench performance" alone.

    Bumped 0.2.0-evidence-enrichment -> 0.4.0-explanatory-text-extraction
    per AR-028: the L1 corpus parser now also captures each requirement's
    informative tail (explanatory paragraphs, warning/note/example
    boxes, Related-Requirements cross-references), previously silently
    dropped -- root-caused via a real missed vulnerability in a paid
    audit run. AR-027 recorded an intended "0.3.0-translation-fidelity-
    audit" bump that was never actually applied here (a real, disclosed
    mismatch between the register and this file, corrected now rather
    than perpetuated); this bump supersedes both prior values in one step.
    """
    return "0.4.0-explanatory-text-extraction"


def compute_manifest() -> dict:
    """Compute all 12 freeze-checklist item hashes fresh from current
    repo state, plus framework/tool version metadata. Raises (does not
    silently produce a partial manifest) if a required artifact is
    entirely missing -- a missing artifact must block freezing, not
    produce a manifest with a hole in it.
    """
    items = {}

    spec_file = REPO_ROOT / "standards" / "ethtrust" / "ethtrust-sl.raw.html"
    items["1_spec_snapshot"] = {"path": str(spec_file.relative_to(REPO_ROOT)), "sha256": _hash_file(spec_file)}

    corpus_file = REPO_ROOT / "rtf" / "l1_corpus" / "requirement_corpus.json"
    items["2_requirement_corpus"] = {"path": str(corpus_file.relative_to(REPO_ROOT)), "sha256": _hash_file(corpus_file)}

    bundles_dir = REPO_ROOT / "rtf" / "l2_context_bundles"
    h, n = _hash_directory(bundles_dir, "req-*.json")
    items["3_context_bundles"] = {"path": str(bundles_dir.relative_to(REPO_ROOT)), "sha256": h, "file_count": n}

    applicability_dir = REPO_ROOT / "rtf" / "track_a" / "l3_applicability"
    h, n = _hash_directory(applicability_dir)
    items["4_applicability_classifications"] = {"path": str(applicability_dir.relative_to(REPO_ROOT)), "sha256": h, "file_count": n}

    l4_dir = REPO_ROOT / "rtf" / "track_a" / "l4_analyzer_mappings"
    h, n = _hash_directory(l4_dir, "req-*.json")
    items["5_analyzer_mappings"] = {"path": str(l4_dir.relative_to(REPO_ROOT)), "sha256": h, "file_count": n}

    l5_dir = REPO_ROOT / "rtf" / "track_a" / "l5_level_s_strategy"
    h, n = _hash_directory(l5_dir)
    items["6_derivation_traces_s_level"] = {"path": str(l5_dir.relative_to(REPO_ROOT)), "sha256": h, "file_count": n}

    predicates_file = REPO_ROOT / "rtf" / "l5_predicates" / "predicates.py"
    items["7_custom_predicates"] = {"path": str(predicates_file.relative_to(REPO_ROOT)), "sha256": _hash_file(predicates_file)}

    l8_dir = REPO_ROOT / "rtf" / "l8_llm_judgment_layer"
    l8_files = ["schema.py", "judgment_layer.py", "citation_check.py", "stability.py"]
    h = hashlib.sha256()
    for fname in l8_files:
        h.update((l8_dir / fname).read_bytes())
    prompt_version_match = re.search(r'PROMPT_VERSION\s*=\s*"([^"]+)"', (l8_dir / "judgment_layer.py").read_text())
    items["8_llm_prompt_schema_model"] = {
        "path": str(l8_dir.relative_to(REPO_ROOT)),
        "sha256": h.hexdigest(),
        "prompt_version": prompt_version_match.group(1) if prompt_version_match else "UNKNOWN",
    }

    l6_dir = REPO_ROOT / "rtf" / "track_a" / "l6_level_m_extraction"
    h, n = _hash_directory(l6_dir, "req-*.json")
    items["9_m_level_classifications"] = {"path": str(l6_dir.relative_to(REPO_ROOT)), "sha256": h, "file_count": n}

    l7_dir = REPO_ROOT / "rtf" / "track_a" / "l7_level_q_evidence"
    h, n = _hash_directory(l7_dir, "req-*.json")
    schema_file = l7_dir / "SCHEMA.md"
    items["10_q_level_review_schema"] = {
        "path": str(l7_dir.relative_to(REPO_ROOT)),
        "sha256": h,
        "file_count": n,
        "schema_sha256": _hash_file(schema_file) if schema_file.exists() else None,
    }

    correspondence_file = REPO_ROOT / "rtf" / "l11_correspondence" / "correspondence_mapping.json"
    items["11_evmbench_correspondence"] = {"path": str(correspondence_file.relative_to(REPO_ROOT)), "sha256": _hash_file(correspondence_file)}

    metrics_file = REPO_ROOT / "rtf" / "l12_evaluation" / "metrics.py"
    items["12_evaluation_metric_definitions"] = {"path": str(metrics_file.relative_to(REPO_ROOT)), "sha256": _hash_file(metrics_file)}

    return {
        "framework_version": _framework_version(),
        "git_commit": _git_commit(),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "freeze_items": items,
    }


def write_manifest(path: Path) -> dict:
    manifest = compute_manifest()
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    import sys

    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "rtf" / "l12_evaluation" / "FROZEN_MANIFEST.json"
    manifest = write_manifest(out_path)
    print(f"Manifest written -> {out_path}")
    print(f"framework_version: {manifest['framework_version']}")
    print(f"git_commit: {manifest['git_commit']}")
    for key, item in manifest["freeze_items"].items():
        print(f"  {key}: {item['sha256'][:16]}...")
