"""A3 -- canonical index over the full corpus (see plan A3).

Builds one row per compilation unit, keyed by a **content-hash id** (not
`sha1(relpath)`) so it survives re-download/move/reorg, identifies true
duplicates, and changes whenever any imported file changes.

Canonicalization is specified, not "normalized" (this is the *only*
normalization scheme -- no second one anywhere downstream):
1. Resolve the unit's files: the main file, plus (self-contained units only)
   every locally-reachable relative import, transitively.
2. Sort those files by relpath **relative to the unit's own root** (the main
   file's directory) -- *not* relative to the corpus root. This is what
   makes duplicate detection possible at all: the same project vendored at
   two different corpus locations has two different corpus-root-relative
   paths but the same *unit-local* layout, and must hash identically to be
   recognized as a true duplicate. (`IndexRow.source_relpath` /
   `extra_source_paths`, used for on-disk bookkeeping/label-joining, are
   separately kept corpus-root-relative -- only the hash input uses
   unit-local paths.)
3. For each file: normalize line endings to `\n`, strip per-line trailing
   whitespace, ensure a single trailing newline.
4. Join with a fixed `\0<relpath>\0` separator before each file's bytes, so
   file boundaries *and* names are part of the hash (two units with
   identical file contents under different filenames/layouts hash
   differently).
5. `contract_id = sha256(canonical_bytes).hexdigest()`.

Part A MVP is **self-contained-only**: a unit whose transitive local-import
closure hits a non-relative (package-style) import, or a relative import
that doesn't resolve inside the corpus root, is not self-contained --
`extract_index` skips it and counts it, rather than attempting a general
Solidity build system (Foundry/Hardhat/remappings). If A1 finds Resource 2 is
single-file only, every unit's `extra_source_paths` is empty by construction
and this degenerates to the "lightweight import scan classifying
self-contained vs not" the plan describes.

Duplicate-collision policy: two units sharing a `contract_id` (identical
canonical bytes) collapse to **one row** -- `native_ids` / `raw_label_refs`
become lists, `merged_classes` is the union, and if the merged per-class
labels *disagree* between the duplicates (positive in one, negative/absent
in the other) `label_conflict=True` is set and the row is kept for review,
never silently dropped or silently resolved.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path

_IMPORT_RE = __import__("re").compile(r"""import\s+(?:[^"'{}]*?from\s+)?["']([^"']+)["']""")


class NotSelfContained(Exception):
    """Raised internally when a unit's import closure escapes local resolution."""


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    normalized = "\n".join(lines)
    if not normalized.endswith("\n"):
        normalized += "\n"
    return normalized


def canonicalize_unit(files: dict[str, str]) -> bytes:
    """`files`: relpath -> raw text (already decoded). Returns the exact
    bytes that get sha256'd -- see module docstring for the spec.
    """
    parts: list[bytes] = []
    for relpath in sorted(files):
        header = f"\0{relpath}\0".encode("utf-8")
        body = _normalize_text(files[relpath]).encode("utf-8")
        parts.append(header + body)
    return b"".join(parts)


def content_sha256(files: dict[str, str]) -> str:
    return hashlib.sha256(canonicalize_unit(files)).hexdigest()


def _resolve_relative_import(sol_file: Path, import_path: str) -> Path | None:
    candidate = (sol_file.parent / import_path).resolve()
    if candidate.exists():
        return candidate
    if candidate.suffix != ".sol":
        alt = candidate.with_suffix(candidate.suffix + ".sol")
        if alt.exists():
            return alt
    return None


def _find_imports(text: str) -> list[str]:
    return [m.group(1) for m in _IMPORT_RE.finditer(text)]


@dataclass
class ResolvedUnit:
    main_path: Path
    extra_paths: list[Path]
    self_contained: bool


def resolve_unit_files(main_path: Path, root: Path) -> ResolvedUnit:
    """Transitively resolves `main_path`'s local (relative) imports within
    `root`. Any non-relative import, or a relative import that fails to
    resolve on disk, marks the unit not-self-contained (`extra_paths` then
    holds whatever was resolved before the failure was hit -- callers must
    check `self_contained` before trusting it, per the skip-and-count MVP
    policy).
    """
    root = root.resolve()
    seen: set[Path] = {main_path.resolve()}
    frontier = [main_path]
    extra: list[Path] = []
    self_contained = True

    while frontier:
        current = frontier.pop()
        try:
            text = current.read_text(errors="ignore")
        except OSError:
            self_contained = False
            continue
        for import_path in _find_imports(text):
            if not import_path.startswith("."):
                self_contained = False
                continue
            resolved = _resolve_relative_import(current, import_path)
            if resolved is None:
                self_contained = False
                continue
            try:
                resolved.relative_to(root)
            except ValueError:
                self_contained = False
                continue
            if resolved.resolve() not in seen:
                seen.add(resolved.resolve())
                extra.append(resolved)
                frontier.append(resolved)

    return ResolvedUnit(main_path=main_path, extra_paths=sorted(extra), self_contained=self_contained)


@dataclass
class IndexRow:
    contract_id: str
    native_ids: list[str] = field(default_factory=list)
    source_relpath: str = ""
    extra_source_paths: list[str] = field(default_factory=list)
    content_sha256: str = ""
    raw_label_refs: list[dict] = field(default_factory=list)
    merged_classes: list[str] = field(default_factory=list)
    label_conflict: bool = False
    pragma_major_minor: str | None = None


def _read_unit_files_for_hash(resolved: ResolvedUnit) -> dict[str, str]:
    """Keys are relative to the unit's own root (the main file's directory),
    NOT the corpus root -- see module docstring point 2. This is what makes
    the same project vendored at two different corpus paths hash identically.
    """
    unit_root = resolved.main_path.resolve().parent
    files: dict[str, str] = {}
    for p in [resolved.main_path, *resolved.extra_paths]:
        relpath = os.path.relpath(p.resolve(), start=unit_root)
        files[relpath] = p.read_text(errors="ignore")
    return files


def extract_one(main_path: Path, root: Path) -> tuple[IndexRow | None, bool]:
    """Returns (row_without_labels, self_contained). `row` is None if the
    unit isn't self-contained (Part A MVP skips + the caller counts it).
    """
    resolved = resolve_unit_files(main_path, root)
    if not resolved.self_contained:
        return None, False

    hash_files = _read_unit_files_for_hash(resolved)
    cid = content_sha256(hash_files)
    main_relpath = str(main_path.resolve().relative_to(root.resolve()))
    extra_relpaths = [str(p.resolve().relative_to(root.resolve())) for p in resolved.extra_paths]
    row = IndexRow(
        contract_id=cid,
        source_relpath=main_relpath,
        extra_source_paths=extra_relpaths,
        content_sha256=cid,
    )
    return row, True


def _merge_classes(rows: list[dict]) -> tuple[list[str], bool]:
    """Union of positive classes across duplicate rows' raw_label_refs;
    `label_conflict=True` if one duplicate marks a class positive that
    another explicitly marks negative (only meaningful when label_refs
    carry explicit positive/negative info -- callers with pure presence-only
    label lists will never see a conflict here, which is correct: presence
    lists can only ever agree-by-union).
    """
    positive: set[str] = set()
    negative: set[str] = set()
    for ref in rows:
        for c in ref.get("positive_classes", []):
            positive.add(c)
        for c in ref.get("negative_classes", []):
            negative.add(c)
    conflict = bool(positive & negative)
    return sorted(positive), conflict


def build_index(
    sol_files: list[Path],
    root: Path,
    label_refs_by_relpath: dict[str, dict] | None = None,
    pragma_major_minor_by_relpath: dict[str, str | None] | None = None,
) -> tuple[list[IndexRow], int]:
    """Extracts + dedups + label-joins across the whole corpus.

    `label_refs_by_relpath`: source_relpath -> raw label ref dict (at least
    a `native_id`; optionally `positive_classes`/`negative_classes` for
    conflict detection). Returns (deduped rows, non_self_contained_count).
    """
    label_refs_by_relpath = label_refs_by_relpath or {}
    pragma_major_minor_by_relpath = pragma_major_minor_by_relpath or {}

    by_id: dict[str, list[IndexRow]] = {}
    by_id_label_refs: dict[str, list[dict]] = {}
    non_self_contained = 0

    for sol_file in sol_files:
        row, self_contained = extract_one(sol_file, root)
        if not self_contained:
            non_self_contained += 1
            continue
        ref = label_refs_by_relpath.get(row.source_relpath, {})
        native_id = ref.get("native_id", row.source_relpath)
        row.native_ids = [native_id]
        row.pragma_major_minor = pragma_major_minor_by_relpath.get(row.source_relpath)
        by_id.setdefault(row.contract_id, []).append(row)
        by_id_label_refs.setdefault(row.contract_id, []).append(ref)

    deduped: list[IndexRow] = []
    for cid, rows in by_id.items():
        refs = by_id_label_refs[cid]
        merged_classes, conflict = _merge_classes(refs)
        base = rows[0]
        native_ids = sorted({nid for r in rows for nid in r.native_ids}, key=lambda n: (len(n), n))
        deduped.append(IndexRow(
            contract_id=cid,
            native_ids=native_ids,
            source_relpath=base.source_relpath,
            extra_source_paths=base.extra_source_paths,
            content_sha256=cid,
            raw_label_refs=refs,
            merged_classes=merged_classes,
            label_conflict=conflict,
            pragma_major_minor=base.pragma_major_minor,
        ))

    deduped.sort(key=lambda r: r.contract_id)
    return deduped, non_self_contained
