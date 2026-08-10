"""Repo-structure-derived discovery of which .sol files should each become
their own first-class RTF investigation entry (`pilot5_driver.py`'s
`scope_files`).

Built in response to a concrete, real finding while investigating the
"multi-file/multi-contract audit scoping" question raised in
`RTF_ETHTRUST_TRANSLATION_AUDIT.md`'s follow-on work: the 4-audit
comparison run's `2024-08-phi` entry list
(`rtf/l12_evaluation/pilot5_artifacts/2024-08-phi_rtf_vs_baseline/`)
contains exactly ONE entry (`entry_00_Cred_stage.json`), yet phi's own
README ("Files in scope" table) and its `scope.txt` both declare **9**
top-level in-scope contracts, including `/src/PhiFactory.sol` --
`PhiFactory.sol` never became its own entry at all, so nothing in it was
ever investigated under ANY requirement. This was traced to how that
run's `scope_files` list was constructed (a small, manually-curated
subset, for cost control during an exploratory comparison), not to any
limitation in `pipeline_e2e.py`/`registry.py` itself.

Two discovery strategies, tried in order, both driven entirely by the
repository's OWN structure/documentation -- never by EVMbench ground
truth:

1. **`scope.txt`** at the repo root: the audit's own self-declared,
   authoritative in-scope file list -- a real, standard convention this
   session found present verbatim (one relative path per line, already
   in EXACTLY the format `pilot5_driver.py`'s own `--scope-file` CLI
   argument already expects) in every real checkout this session had
   access to (`2024-08-phi`, `2025-01-liquid-ron`, `2025-04-forte`,
   `2024-01-canto`). When present, this is the highest-confidence signal
   available: it is the audit's own documentation of what a human
   auditor was asked to review, not an inference.
2. **Heuristic repo scan** (fallback, when no `scope.txt` exists):
   walk the repo for `.sol` files outside conventional non-source
   directories (test/script/mock/vendored-lib/build-artifact dirs), and
   keep only files containing at least one non-interface, non-pure-
   library top-level declaration (a file consisting ONLY of `interface`/
   `library` declarations is a supporting/vendored dependency, not
   itself something a security review targets as a first-class unit --
   confirmed against phi's own README, which explicitly separates
   `interfaces/` and `lib/`-only files into "Files out of scope" even
   though they're real .sol files in the repo).
"""
from __future__ import annotations

import re
from pathlib import Path

# Directory name components that conventionally hold non-audit-target
# code: tests, deploy/upgrade scripts, mocks, vendored third-party
# dependencies, and build output. Matched against any path SEGMENT
# (case-insensitive), not just the immediate parent, so both
# `test/Foo.sol` and `src/test/Foo.sol` are excluded alike.
_EXCLUDED_DIR_SEGMENTS = {
    "test", "tests", "script", "scripts", "mock", "mocks",
    "node_modules", "lib", "libs", "out", "artifacts", "cache",
    ".git", "forge-artifacts", "broadcast",
}

# A file whose only top-level type declarations are these keywords is a
# pure interface/library/abstract-marker file -- NOT itself a first-class
# audit-scope unit (confirmed against phi's README: its `src/interfaces/`
# and `src/lib/` directories are both explicitly "Files out of scope"
# despite being real, non-test, non-vendored .sol source).
_TOP_LEVEL_DECL_RE = re.compile(
    r"^\s*(abstract\s+contract|contract|interface|library)\s+\w+", re.MULTILINE,
)


def _is_excluded_path(rel_path: Path) -> bool:
    return any(part.lower() in _EXCLUDED_DIR_SEGMENTS for part in rel_path.parts[:-1])


def _has_non_interface_declaration(source: str) -> bool:
    """True if `source` declares at least one `contract` or
    `abstract contract` (a real logic unit) -- False if every top-level
    declaration found is `interface`/`library` only, or none at all.
    """
    kinds: set[str] = set()
    for m in _TOP_LEVEL_DECL_RE.finditer(source):
        decl = m.group(1)
        kinds.add("contract" if decl.startswith("abstract") else decl)
    if not kinds:
        return False
    return bool(kinds - {"interface", "library"})


def discover_scope_files_from_scope_txt(repo_root: Path) -> list[str] | None:
    """Reads `<repo_root>/scope.txt` if present -- the audit's own
    self-declared scope, one relative path per line (blank lines
    dropped, surrounding whitespace stripped, `./` prefix preserved
    as-is since `pilot5_driver.py`'s own resolution already strips it).
    Returns None (not an empty list) when the file doesn't exist, so
    callers can distinguish "no scope.txt, try the heuristic fallback"
    from "scope.txt exists but is empty" (which returns `[]`, a real,
    if unusual, answer).
    """
    scope_txt = repo_root / "scope.txt"
    if not scope_txt.exists():
        return None
    return [line.strip() for line in scope_txt.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()]


def discover_scope_files_heuristic(repo_root: Path) -> list[str]:
    """Fallback repo scan for when no `scope.txt` exists: every `.sol`
    file outside a conventional non-source directory that declares at
    least one real `contract`/`abstract contract` (not interface/library
    only). Returns paths relative to `repo_root`, sorted for determinism.
    """
    found: list[str] = []
    for path in sorted(repo_root.rglob("*.sol")):
        rel = path.relative_to(repo_root)
        if _is_excluded_path(rel):
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if _has_non_interface_declaration(source):
            found.append(str(rel))
    return found


def discover_scope_files(repo_root: Path) -> list[str]:
    """The combined entry point: prefer the audit's own `scope.txt` when
    present, else fall back to the heuristic repo scan. Never returns
    None -- an absent `scope.txt` always falls through to the scan
    (which may itself legitimately return `[]` for a repo with no
    matching files, e.g. a pure-library package).
    """
    from_scope_txt = discover_scope_files_from_scope_txt(repo_root)
    if from_scope_txt is not None:
        return from_scope_txt
    return discover_scope_files_heuristic(repo_root)
