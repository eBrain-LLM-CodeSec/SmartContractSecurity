"""Known-vuln reference corpus for semantic-similarity scoring, with EVMbench
leakage prevention (see plan: "Leakage prevention (EVMbench-specific)").

External corpus (SWC / public writeups) is preferred and leakage-free by
construction. If EVMbench's own findings/*.md are used at all, this module
enforces leave-one-audit-out AND fork-family exclusion: some audits share a
codebase/fork, so excluding only the exact target audit_id still leaks --
the whole fork family must be excluded.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class LeakageError(Exception):
    """Raised when a corpus entry belonging to the target audit's fork family
    would otherwise be used during detection/ranking/embedding for that audit.
    """


@dataclass(frozen=True)
class CorpusEntry:
    source: str  # "external" | "evmbench"
    id: str
    text: str
    audit_id: str | None = None


class ExternalCorpus:
    """Loads the external known-vuln corpus (SWC registry / public C4/Solodit
    writeups) -- inherently leakage-free since it's not part of EVMbench.
    """

    @staticmethod
    def load(corpus_dir: Path) -> list[CorpusEntry]:
        corpus_dir = Path(corpus_dir)
        if not corpus_dir.exists():
            return []
        entries = []
        for f in sorted(corpus_dir.rglob("*.md")):
            entries.append(CorpusEntry(source="external", id=str(f.relative_to(corpus_dir)), text=f.read_text()))
        return entries


class ForkFamilyMap:
    """Maps an audit_id to the set of audit_ids (including itself) that share
    a codebase/fork and must all be excluded together under LOAO.
    """

    def __init__(self, families: dict[str, list[str]] | None = None):
        # normalize to a lookup: audit_id -> frozenset of the whole family
        self._by_member: dict[str, frozenset[str]] = {}
        for members in (families or {}).values():
            fam = frozenset(members)
            for m in members:
                self._by_member[m] = fam

    def family_of(self, audit_id: str) -> frozenset[str]:
        return self._by_member.get(audit_id, frozenset({audit_id}))

    @classmethod
    def from_yaml(cls, path: Path) -> "ForkFamilyMap":
        import yaml
        path = Path(path)
        if not path.exists():
            return cls({})
        data = yaml.safe_load(path.read_text()) or {}
        return cls(data.get("fork_families", {}))


class EVMbenchCorpus:
    """Optional EVMbench-derived corpus (other audits' findings/*.md), gated
    by leave-one-audit-out + fork-family exclusion. Prefer ExternalCorpus;
    only use this if the external corpus proves insufficient.
    """

    def __init__(self, audits_dir: Path, fork_map: ForkFamilyMap | None = None):
        self.audits_dir = Path(audits_dir)
        self.fork_map = fork_map or ForkFamilyMap()

    def load_excluding(self, target_audit_id: str) -> list[CorpusEntry]:
        excluded = self.fork_map.family_of(target_audit_id)
        entries: list[CorpusEntry] = []
        if not self.audits_dir.exists():
            return entries
        for audit_dir in sorted(self.audits_dir.iterdir()):
            if not audit_dir.is_dir():
                continue
            aid = audit_dir.name
            if aid in excluded:
                continue
            findings_dir = audit_dir / "findings"
            if not findings_dir.exists():
                continue
            for f in sorted(findings_dir.glob("*.md")):
                entries.append(CorpusEntry(source="evmbench", id=f"{aid}/{f.name}", text=f.read_text(), audit_id=aid))
        self.assert_no_leakage(target_audit_id, entries)
        return entries

    def assert_no_leakage(self, target_audit_id: str, entries: list[CorpusEntry]) -> None:
        excluded = self.fork_map.family_of(target_audit_id)
        for e in entries:
            if e.audit_id in excluded:
                raise LeakageError(
                    f"corpus entry {e.id!r} belongs to {e.audit_id!r}, in the excluded fork "
                    f"family {sorted(excluded)!r} for target audit {target_audit_id!r}"
                )
