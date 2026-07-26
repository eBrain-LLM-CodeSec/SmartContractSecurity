"""A4 -- compiler version resolution (pure logic; see plan A4).

Given a contract's pragma expression(s) and, if present, an exact version
from dataset metadata, resolves which solc version to attempt against a
supplied list of known-available versions -- and records every version this
considered, not just the winner.

Selection order, "conservative and deliberate" per the plan:
  1. exact compiler version from dataset metadata, if present;
  2. else the **lowest satisfying minor line, newest patch within it** --
     earliest patches of a minor carry known compiler bugs later patches
     fixed, while semantics rarely move within a patch series, so
     newest-satisfying-overall risks semantic drift and lowest-overall risks
     buggy early patches;
  3. **no arbitrary fallback ladder** for pragma-less contracts -- mark
     unresolved and let A8 measure the loss, rather than guessing.

This module is pure selection logic over a caller-supplied `available_versions`
list -- it does not fetch or install anything (that's
`scripts/etl/provision_solc.py`'s job, login-node only, since it needs
solc-select's network-backed version list). Reuses `repair.py`'s pure pragma
helpers (`_detect_pragma_versions`, `_candidate_versions_from_pragma`) only
where they're a superset of what's needed elsewhere -- this module's own
constraint solving (caret/range satisfiability) is a distinct, stricter
concern `repair.py` never needed (it just picks candidate versions to *try*,
it doesn't need to prove which versions of a large provisioned set satisfy a
range).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion, Version

_TOKEN_RE = re.compile(r"(\^|>=|<=|>|<|=)?\s*(\d+)\.(\d+)\.(\d+)")


class UnparsablePragma(ValueError):
    """Raised when a pragma expression contains no recognizable version token."""


def _caret_upper_bound(major: int, minor: int) -> str:
    # Solidity is pre-1.0, so every released version is 0.x.y; a caret pins
    # the minor as the breaking-change boundary (^0.8.0 == >=0.8.0,<0.9.0).
    return f"{major}.{minor + 1}.0"


def _group_to_specifier(group: str) -> SpecifierSet:
    """One AND-group (space-separated comparators, e.g. '>=0.4.22 <0.6.0',
    or a single '^0.8.0' / bare '0.8.4') -> a packaging SpecifierSet.
    """
    specs: list[str] = []
    matched = False
    for m in _TOKEN_RE.finditer(group):
        matched = True
        op, maj, minr, patch = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        version = f"{maj}.{minr}.{patch}"
        if op in (None, "="):
            specs.append(f"=={version}")
        elif op == "^":
            specs.append(f">={version}")
            specs.append(f"<{_caret_upper_bound(maj, minr)}")
        else:
            specs.append(f"{op}{version}")
    if not matched:
        raise UnparsablePragma(f"no version token found in {group!r}")
    return SpecifierSet(",".join(specs))


def pragma_to_specifiers(expr: str) -> list[SpecifierSet]:
    """A pragma expression -> list of AND-group SpecifierSets, OR'd together
    (Solidity pragmas may combine ranges with `||`; a version satisfies the
    expression iff it satisfies at least one group).
    """
    groups = [g.strip() for g in expr.split("||") if g.strip()]
    if not groups:
        raise UnparsablePragma(f"empty pragma expression {expr!r}")
    return [_group_to_specifier(g) for g in groups]


def satisfying_versions(pragma_exprs: list[str], available_versions: list[str]) -> list[str]:
    """Versions from `available_versions` that satisfy the intersection of
    ALL given pragma expressions (multiple pragma lines in one compilation
    unit are logically AND'd), each expression itself being an OR of its
    `||`-separated groups. Returns a version-sorted list (ascending).
    """
    if not pragma_exprs:
        return []
    try:
        per_expr_groups = [pragma_to_specifiers(e) for e in pragma_exprs]
    except UnparsablePragma:
        return []

    def satisfies_all_exprs(v: Version) -> bool:
        for groups in per_expr_groups:
            if not any(v in spec for spec in groups):
                return False
        return True

    parsed: list[Version] = []
    for v in available_versions:
        try:
            parsed.append(Version(v))
        except InvalidVersion:
            continue
    matches = sorted(v for v in parsed if satisfies_all_exprs(v))
    return [str(v) for v in matches]


def pick_lowest_minor_newest_patch(versions: list[str]) -> str | None:
    """From a list of candidate version strings, pick the version in the
    lowest (major, minor) band, and within that band the highest patch.
    """
    if not versions:
        return None
    parsed = sorted((Version(v) for v in versions))
    lowest_band = (parsed[0].major, parsed[0].minor)
    band_versions = [v for v in parsed if (v.major, v.minor) == lowest_band]
    return str(max(band_versions))


@dataclass
class VersionResolution:
    resolved_version: str | None
    unresolved: bool
    reason: str
    exact_version_used: bool
    candidates_considered: list[str] = field(default_factory=list)
    # The ordered list of versions `compile_one.py` should actually try, in
    # order, recording every attempt in `solc_attempts`. For the normal
    # exact/pragma-satisfying paths this is a single deterministic choice
    # (`[resolved_version]`) -- the plan is explicit that those paths are NOT
    # a ladder. It's only ever a longer list for the pragma-less fallback
    # path below, and only when the caller opts in with real evidence.
    candidates_to_try: list[str] = field(default_factory=list)


def resolve_solc_version(
    pragma_exprs: list[str],
    available_versions: list[str],
    exact_version: str | None = None,
    pragma_less_fallback: list[str] | None = None,
) -> VersionResolution:
    """Select a solc version (or ordered candidate list) to attempt for one
    compilation unit.

    `available_versions` is whatever the caller has decided is provisionable
    (e.g. solc-select's `get_installable_versions()` plus already-installed
    ones) -- this function never assumes network access.

    `pragma_less_fallback`: an **explicit, caller-supplied, evidence-based**
    ordered list of versions to try for pragma-less contracts (e.g.
    `["0.4.24", "0.8.17", "0.8.20"]`, justified for Resource 2 specifically
    by a real compile smoke test -- 20/20 contracts compiled on the very
    first candidate, 0.4.24 -- see `data/gnn/raw/MANIFEST.md`). This is
    **not** the "arbitrary fallback ladder" the plan rules out by default:
    it only activates when a caller deliberately passes one, scoped to a
    dataset where real evidence supports it. Leave it unset (the default)
    to keep the original "pragma-less -> unresolved, measure the loss"
    behavior for any dataset without that evidence.
    """
    if exact_version:
        return VersionResolution(
            resolved_version=exact_version,
            unresolved=False,
            reason="exact_version_from_metadata",
            exact_version_used=True,
            candidates_considered=[exact_version],
            candidates_to_try=[exact_version],
        )

    if not pragma_exprs:
        if pragma_less_fallback:
            available_fallback = [v for v in pragma_less_fallback if v in available_versions]
            if available_fallback:
                return VersionResolution(
                    resolved_version=available_fallback[0],
                    unresolved=False,
                    reason="pragma_less_evidence_based_fallback",
                    exact_version_used=False,
                    candidates_considered=available_fallback,
                    candidates_to_try=available_fallback,
                )
        return VersionResolution(
            resolved_version=None,
            unresolved=True,
            reason="no_pragma_no_fallback_ladder",
            exact_version_used=False,
            candidates_considered=[],
            candidates_to_try=[],
        )

    candidates = satisfying_versions(pragma_exprs, available_versions)
    if not candidates:
        return VersionResolution(
            resolved_version=None,
            unresolved=True,
            reason="no_available_version_satisfies_pragma",
            exact_version_used=False,
            candidates_considered=[],
            candidates_to_try=[],
        )

    chosen = pick_lowest_minor_newest_patch(candidates)
    return VersionResolution(
        resolved_version=chosen,
        unresolved=False,
        reason="lowest_satisfying_minor_newest_patch",
        exact_version_used=False,
        candidates_considered=candidates,
        candidates_to_try=[chosen],
    )
