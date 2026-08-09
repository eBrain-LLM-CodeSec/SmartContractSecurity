"""Generic applicable-standard discovery: `discover_applicable_standards`
determines which registered standards (`rtf/standards/registry.py`) a given
repository appears to use, from real evidence -- inheritance, imports,
NatSpec, documentation claims, and (supporting-only) signature/event shape --
never from any audit_id/benchmark-specific branch.

Entirely data-driven off each standard's own `standard.json` `detection_
signals` (strong/supporting, per `models.DetectionSignal`) -- this module
contains ZERO ERC-4626-specific (or any other standard-specific) code. Add a
new standard by registering a new `standard.json`, not by editing this file.

**Vendored-dependency handling**: a project's own contract inheriting from a
vendored OpenZeppelin/Solmate `ERC4626.sol` under `lib/` is exactly the
common, expected way real projects implement the standard -- that MUST be
detected (the base contract's *definition* legitimately lives in a vendored
path). What must NOT happen is misclassifying the vendored library's own
internal contract (e.g. OZ's own `ERC4626 is ERC20, IERC4626 { ... }`
definition) as if the AUDITED PROJECT implements the standard merely because
that definition technically inherits `IERC4626` too. `_is_vendored_path`
distinguishes "which contract is the candidate implementer" (must not itself
live under a vendor directory) from "which base class it may legitimately
inherit from" (may live anywhere, including vendored paths).
"""
from __future__ import annotations

import re
from pathlib import Path

from .models import DetectionConfidence, DetectionSignal, StandardDetectionResult, StandardRecord
from .registry import StandardsRegistry

_VENDOR_DIR_NAMES = frozenset({"lib", "node_modules", "vendor", "dependencies", ".deps"})

_README_NAMES = ("README.md", "README.MD", "readme.md", "README", "README.rst", "README.txt")
_DOC_SUFFIXES = (".md", ".txt", ".rst")

# Below this many matched canonical function names, a function-signature
# supporting signal doesn't fire at all -- avoids classifying a standard as
# even *uncertain*ly applicable off one common function name (e.g. a lone
# `totalAssets()` getter on an unrelated accounting contract). Chosen as
# half of ERC-4626's 16-method surface; a generic, standard-size-relative
# threshold (ceil(len(pattern)/2)) is computed per-call, not hardcoded to 16,
# so this stays meaningful for a future, differently-sized standard.
_MIN_SIGNATURE_MATCH_FRACTION = 0.5

_FUNCTION_NAME_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\(")


def _is_vendored_path(path: Path, repo_root: Path) -> bool:
    try:
        rel_parts = path.resolve().relative_to(repo_root.resolve()).parts
    except ValueError:
        rel_parts = path.parts
    return any(part in _VENDOR_DIR_NAMES for part in rel_parts)


def _iter_project_sol_files(repo_root: Path) -> list[Path]:
    return sorted(
        p for p in repo_root.rglob("*.sol")
        if p.is_file() and not _is_vendored_path(p, repo_root)
    )


def _iter_doc_texts(repo_root: Path) -> list[tuple[str, str]]:
    """Returns (text, location_label) pairs: README* at repo root, then
    bounded docs/ tree, mirroring the exact source set
    `predicates.collect_documentary_and_implementation_evidence` already
    treats as "the project's documentation" for other GP/Q-level checks --
    same discipline applied here, not a new convention."""
    out: list[tuple[str, str]] = []
    for name in _README_NAMES:
        p = repo_root / name
        if p.exists() and p.is_file():
            out.append((p.read_text(encoding="utf-8", errors="replace"), name))
            break
    docs_dir = repo_root / "docs"
    if docs_dir.is_dir():
        for f in sorted(docs_dir.rglob("*"))[:20]:
            if f.is_file() and f.suffix.lower() in _DOC_SUFFIXES and not _is_vendored_path(f, repo_root):
                out.append((f.read_text(encoding="utf-8", errors="replace"), str(f.relative_to(repo_root))))
    return out


def _contract_source_path(contract, repo_root: Path) -> Path | None:
    sm = getattr(contract, "source_mapping", None)
    if sm is None or sm.filename is None:
        return None
    return Path(sm.filename.absolute)


def _canonical_function_names(patterns: tuple[str, ...]) -> set[str]:
    names = set()
    for p in patterns:
        m = _FUNCTION_NAME_RE.match(p.strip())
        if m:
            names.add(m.group(1))
    return names


def _is_interface(contract) -> bool:
    """True for a pure `interface` declaration (e.g. `interface IERC4626 is
    IERC20 {...}`). An interface extending another interface is NOT an
    "implementation" of anything -- it has no function bodies at all -- so
    it must never be counted as a candidate implementing contract, even
    though Slither's `contracts_derived` includes interfaces alongside real
    contracts and `.inheritance` reports IERC20 as an ancestor of IERC4626
    just as readily as it would for a concrete vault contract. Found live:
    without this check, `IERC4626 is IERC20` alone caused ERC-20 to be
    falsely reported as "implemented by contract IERC4626" for every repo
    that merely imports the interface file."""
    return getattr(contract, "contract_kind", None) == "interface"


def _detect_inheritance(sig: DetectionSignal, slither, repo_root: Path) -> tuple[list[str], set[str], set[str]]:
    """Returns (evidence_lines, implementing_contract_names, interfaces_seen)."""
    evidence: list[str] = []
    implementing: set[str] = set()
    interfaces_seen: set[str] = set()
    for contract in getattr(slither, "contracts_derived", []):
        if _is_interface(contract):
            continue
        src = _contract_source_path(contract, repo_root)
        if src is not None and _is_vendored_path(src, repo_root):
            continue  # the vendored library's own internal definitions are not the audited project's implementation
        base_names = {b.name for b in getattr(contract, "inheritance", [])}
        for pat in sig.pattern:
            if pat in base_names:
                implementing.add(contract.name)
                interfaces_seen.add(pat)
                evidence.append(f"{sig.signal_id}: contract {contract.name!r} inherits {pat!r}")
    return evidence, implementing, interfaces_seen


def _detect_import(sig: DetectionSignal, repo_root: Path) -> list[str]:
    evidence: list[str] = []
    for sol_file in _iter_project_sol_files(repo_root):
        text = sol_file.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("import"):
                continue
            for pat in sig.pattern:
                if pat in stripped:
                    evidence.append(f"{sig.signal_id}: {sol_file.name} imports {pat!r} ({stripped[:120]})")
    return evidence


def _detect_natspec(sig: DetectionSignal, slither, repo_root: Path) -> tuple[list[str], set[str]]:
    evidence: list[str] = []
    implementing: set[str] = set()
    contracts_by_file: dict[Path, list] = {}
    for contract in getattr(slither, "contracts_derived", []):
        if _is_interface(contract):
            continue
        src = _contract_source_path(contract, repo_root)
        if src is not None and not _is_vendored_path(src, repo_root):
            contracts_by_file.setdefault(src, []).append(contract)

    for sol_file in _iter_project_sol_files(repo_root):
        text = sol_file.read_text(encoding="utf-8", errors="replace")
        for pat in sig.pattern:
            if pat in text:
                evidence.append(f"{sig.signal_id}: {sol_file.name} contains {pat!r}")
                # Best-effort attribution: any project (non-vendored) contract
                # defined in the same file is credited -- NatSpec tags are not
                # trivially traceable to one specific function/contract from
                # raw text alone, so this stays an honest approximation, not
                # a precise binding.
                for c in contracts_by_file.get(sol_file, []):
                    implementing.add(c.name)
    return evidence, implementing


def _detect_documentation_claim(sig: DetectionSignal, repo_root: Path) -> list[str]:
    evidence: list[str] = []
    for text, loc in _iter_doc_texts(repo_root):
        lowered = text.lower()
        for pat in sig.pattern:
            if pat.lower() in lowered:
                evidence.append(f"{sig.signal_id}: {loc} mentions {pat!r}")
    return evidence


def _detect_function_signatures(sig: DetectionSignal, slither, repo_root: Path) -> list[str]:
    evidence: list[str] = []
    wanted = _canonical_function_names(sig.pattern)
    if not wanted:
        return evidence
    threshold = max(1, round(len(wanted) * _MIN_SIGNATURE_MATCH_FRACTION))
    for contract in getattr(slither, "contracts_derived", []):
        if _is_interface(contract):
            continue
        src = _contract_source_path(contract, repo_root)
        if src is not None and _is_vendored_path(src, repo_root):
            continue
        have = {f.name for f in getattr(contract, "functions", [])}
        matched = wanted & have
        if len(matched) >= threshold:
            evidence.append(
                f"{sig.signal_id}: contract {contract.name!r} matches {len(matched)}/{len(wanted)} "
                f"canonical function names ({sorted(matched)})"
            )
    return evidence


def _detect_events(sig: DetectionSignal, slither, repo_root: Path) -> list[str]:
    evidence: list[str] = []
    wanted_names = {p.split("(")[0].strip() for p in sig.pattern}
    for contract in getattr(slither, "contracts_derived", []):
        if _is_interface(contract):
            continue
        src = _contract_source_path(contract, repo_root)
        if src is not None and _is_vendored_path(src, repo_root):
            continue
        have = {e.name for e in getattr(contract, "events", [])}
        matched = wanted_names & have
        if matched:
            evidence.append(f"{sig.signal_id}: contract {contract.name!r} declares event(s) {sorted(matched)}")
    return evidence


def _detect_known_library_import(sig: DetectionSignal, repo_root: Path) -> list[str]:
    evidence: list[str] = []
    for sol_file in repo_root.rglob("*.sol"):  # includes vendored files: we're checking the IMPORT SITE, which may itself be vendored or project code
        if not sol_file.is_file():
            continue
        text = sol_file.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("import"):
                continue
            for pat in sig.pattern:
                if pat in stripped:
                    rel = sol_file.relative_to(repo_root) if sol_file.is_relative_to(repo_root) else sol_file
                    evidence.append(f"{sig.signal_id}: {rel} imports known library path {pat!r}")
    return evidence


def _detect_standard(record: StandardRecord, repo_root: Path, entry_sol_file: Path, slither) -> StandardDetectionResult:
    evidence: list[str] = []
    implementing: set[str] = set()
    interfaces_seen: set[str] = set()
    strong_fired: list[str] = []
    supporting_fired: list[str] = []

    for sig in record.detection_signals_strong:
        if sig.signal_type == "inheritance":
            ev, impl, ifaces = _detect_inheritance(sig, slither, repo_root)
            if ev:
                evidence += ev
                implementing |= impl
                interfaces_seen |= ifaces
                strong_fired.append(sig.signal_id)
        elif sig.signal_type == "import":
            ev = _detect_import(sig, repo_root)
            if ev:
                evidence += ev
                strong_fired.append(sig.signal_id)
                # Import alone does NOT establish implementation -- see
                # fixture 5 (interface-only reference). Contributes evidence
                # and can raise the verdict to UNCERTAIN, never APPLICABLE
                # on its own.
        elif sig.signal_type == "natspec":
            ev, impl = _detect_natspec(sig, slither, repo_root)
            if ev:
                evidence += ev
                implementing |= impl
                strong_fired.append(sig.signal_id)
        elif sig.signal_type == "documentation_claim":
            ev = _detect_documentation_claim(sig, repo_root)
            if ev:
                evidence += ev
                strong_fired.append(sig.signal_id)
                # Deliberately does NOT auto-credit any specific contract
                # as "implementing" the standard from a bare documentation
                # claim alone -- `_iter_doc_texts` scans project-level
                # README/docs, which are NOT scoped to the specific
                # entry_sol_file being analyzed. A repo-wide README saying
                # "this project implements ERC-4626" is true of the real
                # vault contract but says nothing about an unrelated
                # helper/mixin contract that happens to be compiled from
                # the same repo. Found LIVE on a real EVMbench target
                # (2025-01-liquid-ron): compiling Pausable.sol (an
                # unrelated pause-mixin, no ERC-4626/ERC-20 relationship
                # whatsoever) in isolation yields exactly one non-vendored
                # contract in that compilation unit (itself, since it has
                # no imports) -- an earlier version of this code took
                # "exactly one candidate contract exists" as license to
                # credit it, which is wrong: single-contract-in-compilation-
                # unit is an artifact of how EVMbench scope files get
                # compiled one at a time, not evidence that contract
                # implements anything. A documentation claim with no
                # corroborating code-level signal (inheritance/import/
                # natspec) now correctly stays UNCERTAIN via the fallback
                # branch below, never auto-promoted to APPLICABLE.

    for sig in record.detection_signals_supporting:
        if sig.signal_type == "function_signatures":
            ev = _detect_function_signatures(sig, slither, repo_root)
        elif sig.signal_type == "events":
            ev = _detect_events(sig, slither, repo_root)
        elif sig.signal_type == "known_library_import":
            ev = _detect_known_library_import(sig, repo_root)
        else:
            ev = []
        if ev:
            evidence += ev
            supporting_fired.append(sig.signal_id)

    if implementing:
        applicable = DetectionConfidence.APPLICABLE
        confidence = 0.95 if len(strong_fired) > 1 else 0.85
        reason = (
            f"strong signal(s) {sorted(set(strong_fired))} identify contract(s) "
            f"{sorted(implementing)} as implementing {record.standard_id}"
        )
    elif strong_fired or supporting_fired:
        applicable = DetectionConfidence.UNCERTAIN
        confidence = 0.4 if strong_fired else 0.15
        reason = (
            f"signal(s) {sorted(set(strong_fired + supporting_fired))} reference "
            f"{record.standard_id} but no specific contract was confirmed to implement it "
            f"(e.g. interface imported/mentioned, or only a minority-overlap function-name "
            f"match, without any contract actually inheriting the standard's interface)"
        )
    else:
        applicable = DetectionConfidence.NOT_APPLICABLE
        confidence = 0.0
        reason = f"no detection signal for {record.standard_id} found in this repository"

    return StandardDetectionResult(
        standard_id=record.standard_id,
        applicable=applicable,
        confidence=confidence,
        evidence=tuple(evidence),
        contracts=tuple(sorted(implementing)),
        interfaces=tuple(sorted(interfaces_seen)),
        reason=reason,
    )


def discover_applicable_standards(
    repo_root: Path,
    entry_sol_file: Path,
    slither,
    registry: StandardsRegistry | None = None,
) -> list[StandardDetectionResult]:
    """Runs standard-agnostic detection for every registered standard
    against this repository. `slither` is a compiled `Slither` object (the
    same one every other L5 predicate already receives) -- required, since
    inheritance/function/event signals need real compiled contract data,
    not just text search.
    """
    registry = registry if registry is not None else StandardsRegistry()
    results = []
    for standard_id in registry.all_ids():
        record = registry.load(standard_id)
        results.append(_detect_standard(record, repo_root, entry_sol_file, slither))
    return results
