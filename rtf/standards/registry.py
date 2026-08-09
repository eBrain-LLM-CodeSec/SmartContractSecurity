"""Accepted-standards registry: loads pinned, local standard snapshots
(currently `rtf/standards/erc/<STANDARD-ID>/`) into `StandardRecord` +
`NormativeClause` objects.

Deliberately separate from `rtf.l12_evaluation.registry` (the 81-requirement
predicate registry) -- this registry's universe is dynamically sized and
grows as new standards are registered under a family root, never touching
the frozen L1 corpus.

No network access, ever: every load reads local files under this package's
own directory tree only. See `test_registry.py::test_registry_load_never_
touches_network` for a real enforcement test, not just a docstring claim.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .models import NormativeClause, StandardRecord

# Per GP_ACCEPTED_ERC_DEFINITION.md: EthTrust's own citation for "[ERC]" in
# req-R-follow-erc-standards resolves to "ERC Final" -- the EIP-1 process's
# terminal `Final` status. `Living` is included for completeness (EIP-1's
# other terminal status, for continuously-amended process documents) though
# no currently-registered standard uses it.
ACCEPTED_STATUSES = frozenset({"Final", "Living"})

# source_family -> directory containing one subdirectory per standard_id.
# Extensible: a future family (e.g. a non-ERC EIP, or a different standards
# body entirely) adds one more entry here, not a structural change.
_PACKAGE_ROOT = Path(__file__).resolve().parent
FAMILY_ROOTS: dict[str, Path] = {
    "ERC": _PACKAGE_ROOT / "erc",
}


class StandardsRegistryError(ValueError):
    """Raised for any malformed/inconsistent standard -- deliberately a
    distinct type from a bare ValueError/KeyError so callers (and tests)
    can assert on it specifically without also catching unrelated bugs."""


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class _StandardEntry:
    record: StandardRecord
    directory: Path


class StandardsRegistry:
    """Discovers and loads every `standard.json` under `FAMILY_ROOTS`,
    validating each at load time. Construction eagerly indexes standard_id
    -> directory (cheap: just JSON metadata, not full clause parsing);
    `load_clauses` parses a standard's `clauses.json` lazily and caches it.
    """

    def __init__(self, family_roots: dict[str, Path] | None = None) -> None:
        self._family_roots = family_roots if family_roots is not None else FAMILY_ROOTS
        self._entries: dict[str, _StandardEntry] = {}
        self._clauses_cache: dict[str, tuple[NormativeClause, ...]] = {}
        self._discover()

    def _discover(self) -> None:
        for family, root in self._family_roots.items():
            if not root.exists():
                continue
            for child in sorted(root.iterdir()):
                if not child.is_dir():
                    continue
                standard_json = child / "standard.json"
                if not standard_json.exists():
                    continue
                self._load_one(family, child, standard_json)

    def _load_one(self, family: str, directory: Path, standard_json: Path) -> None:
        try:
            raw = json.loads(standard_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise StandardsRegistryError(f"malformed standard.json at {standard_json}: {e}") from e

        try:
            record = StandardRecord.from_dict(raw)
        except KeyError as e:
            raise StandardsRegistryError(f"standard.json at {standard_json} missing required field {e}") from e

        if record.source_family != family:
            raise StandardsRegistryError(
                f"{standard_json}: source_family {record.source_family!r} does not match "
                f"its registered family root {family!r}"
            )

        if record.standard_id in self._entries:
            other = self._entries[record.standard_id].directory
            raise StandardsRegistryError(
                f"duplicate standard_id {record.standard_id!r}: registered at both "
                f"{other} and {directory}"
            )

        if record.status not in ACCEPTED_STATUSES:
            raise StandardsRegistryError(
                f"{record.standard_id}: status {record.status!r} is not an accepted "
                f"status ({sorted(ACCEPTED_STATUSES)}) per req-R-follow-erc-standards's "
                f"'finalized' requirement -- see GP_ACCEPTED_ERC_DEFINITION.md"
            )

        spec_path = directory / record.local_spec_path
        if not spec_path.exists():
            raise StandardsRegistryError(
                f"{record.standard_id}: local_spec_path {record.local_spec_path!r} "
                f"not found under {directory}"
            )
        actual_hash = _sha256_file(spec_path)
        if actual_hash != record.local_source_hash:
            raise StandardsRegistryError(
                f"{record.standard_id}: local_source_hash mismatch for {spec_path} -- "
                f"recorded {record.local_source_hash}, actual {actual_hash}. The pinned "
                f"snapshot has drifted from its provenance record; re-pin deliberately, "
                f"do not silently accept a changed spec file."
            )

        clauses_path = directory / record.clauses_path
        if not clauses_path.exists():
            raise StandardsRegistryError(
                f"{record.standard_id}: clauses_path {record.clauses_path!r} not found "
                f"under {directory}"
            )

        self._entries[record.standard_id] = _StandardEntry(record=record, directory=directory)

    def all_ids(self) -> list[str]:
        return sorted(self._entries)

    def load(self, standard_id: str) -> StandardRecord:
        entry = self._entries.get(standard_id)
        if entry is None:
            raise StandardsRegistryError(
                f"no standard registered under id {standard_id!r}; registered: {self.all_ids()}"
            )
        return entry.record

    def load_clauses(self, standard_id: str) -> tuple[NormativeClause, ...]:
        if standard_id in self._clauses_cache:
            return self._clauses_cache[standard_id]

        entry = self._entries.get(standard_id)
        if entry is None:
            raise StandardsRegistryError(
                f"no standard registered under id {standard_id!r}; registered: {self.all_ids()}"
            )

        clauses_path = entry.directory / entry.record.clauses_path
        try:
            raw = json.loads(clauses_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise StandardsRegistryError(f"malformed clauses.json at {clauses_path}: {e}") from e

        clauses: list[NormativeClause] = []
        seen_ids: set[str] = set()
        for raw_clause in raw.get("clauses", []):
            try:
                clause = NormativeClause.from_dict(raw_clause)
            except (KeyError, ValueError) as e:
                raise StandardsRegistryError(
                    f"malformed clause in {clauses_path} (clause_id="
                    f"{raw_clause.get('clause_id', '<missing>')!r}): {e}"
                ) from e

            if clause.standard_id != standard_id:
                raise StandardsRegistryError(
                    f"{clauses_path}: clause {clause.clause_id!r} has standard_id "
                    f"{clause.standard_id!r}, does not match parent standard {standard_id!r}"
                )
            if clause.clause_id in seen_ids:
                raise StandardsRegistryError(
                    f"{clauses_path}: duplicate clause_id {clause.clause_id!r}"
                )
            seen_ids.add(clause.clause_id)
            clauses.append(clause)

        result = tuple(clauses)
        self._clauses_cache[standard_id] = result
        return result
