"""Deterministic, multi-format Solidity compiler-version resolution for one
audit subproject's checkout.

This replaces `bin/forge`'s previous approach (a single bash regex,
`solc[[:space:]]*=[[:space:]]*["']${v}["']`, matched only against a
top-level `foundry.toml`), which is the confirmed root cause of most of
the audit-compile failures this module exists to fix: real audits declare
their compiler version in several different, textually unrelated forms --
`solc = "X.Y.Z"`, `solc_version = "X.Y.Z"` (a different key the old regex
never matched, even when the exact binary was already cached -- confirmed
live against `2024-01-canto`, `2024-05-loop`, `2024-07-benddao`,
`2024-12-secondswap`'s real `foundry.toml` files), Hardhat's
`solidity.compilers[].version` (a JS/TS object, not TOML), a Dockerfile's
own solc-select invocation, or -- for 7 of the 27 audits -- no explicit
version at all in any project file, meaning Foundry's own
`auto_detect_solc` would otherwise silently take over and attempt its own
download (the exact path that fails under this deployment's read-only
Singularity container view).

Every result is one of three explicit statuses -- RESOLVED,
AMBIGUOUS_COMPILER_CONFIGURATION, or NO_CONFIGURATION_FOUND -- never a
silently-guessed version. `AMBIGUOUS_COMPILER_CONFIGURATION` occurs only
when multiple *conflicting* candidates exist with no authoritative signal
to prefer one (e.g. a Foundry `[profile.default]` disagreeing with another
profile, or a bare pragma scan finding more than one exact version with no
project file settling it) -- a project that genuinely declares more than
one *required* compiler version (e.g. `2024-01-curves`' Hardhat config,
which lists both `0.8.7` and `0.5.15`) is not ambiguous; it RESOLVES to
multiple required versions.
"""
from __future__ import annotations

import re
import tomllib
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Directories that hold vendored/generated code, never the audited
# project's own compiler configuration or the pragma statements that
# should drive fallback resolution.
_VENDOR_DIR_NAMES = {
    "lib", "node_modules", "out", "cache", "cache_forge", "artifacts",
    ".git", "broadcast", "typechain", "typechain-types",
}


class BuildSystem(str, Enum):
    FOUNDRY = "FOUNDRY"
    HARDHAT = "HARDHAT"
    TRUFFLE = "TRUFFLE"
    UNKNOWN = "UNKNOWN"


class CompilerResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS_COMPILER_CONFIGURATION = "AMBIGUOUS_COMPILER_CONFIGURATION"
    NO_CONFIGURATION_FOUND = "NO_CONFIGURATION_FOUND"


@dataclass(frozen=True)
class CompilerCandidate:
    version: str
    source: str          # "foundry_toml_solc" | "foundry_toml_solc_version" | "hardhat_config" | "dockerfile" | "pragma_fallback"
    config_file: str      # path the candidate was found in (or a description, for pragma fallback)
    detail: str           # e.g. "[profile.default].solc", "solidity.compilers[].version", "14 file(s) agree"
    profile: str | None = None  # the Foundry profile name this candidate came from, if source is foundry_toml_*
    # (a structured field, not re-derived by string-matching `detail` --
    # confirmed live that substring-matching a self-formatted display
    # string is exactly the kind of bug this field exists to avoid: an
    # earlier version of this resolver checked `".default." in detail`
    # against `detail=f"[profile.{name}].{key}"`, which for name="default"
    # produces "[profile.default].solc" -- the character after "default"
    # is "]", not ".", so the check silently never matched anything and
    # every Foundry audit resolved to NO_CONFIGURATION_FOUND.)

    def as_dict(self) -> dict:
        return {"version": self.version, "source": self.source, "config_file": self.config_file,
                "detail": self.detail, "profile": self.profile}


@dataclass(frozen=True)
class CompilerResolution:
    status: CompilerResolutionStatus
    versions: list[str]              # every required version (len > 1 for genuine multi-compiler projects)
    primary_version: str | None      # the version to pass to --use; None unless status is RESOLVED
    candidates: list[CompilerCandidate] = field(default_factory=list)
    build_system: BuildSystem = BuildSystem.UNKNOWN
    detail: str = ""

    def as_dict(self) -> dict:
        return {
            "status": self.status.value, "versions": self.versions,
            "primary_version": self.primary_version,
            "candidates": [c.as_dict() for c in self.candidates],
            "build_system": self.build_system.value, "detail": self.detail,
        }


# --- Foundry (TOML) ---------------------------------------------------------

def _parse_foundry_toml(path: Path) -> list[CompilerCandidate]:
    try:
        data = tomllib.loads(path.read_text(errors="ignore"))
    except (tomllib.TOMLDecodeError, OSError):
        return []
    candidates: list[CompilerCandidate] = []
    profiles = data.get("profile")
    if not isinstance(profiles, dict):
        return []
    for profile_name, profile_data in profiles.items():
        if not isinstance(profile_data, dict):
            continue
        # both key spellings, real forms confirmed present across the 27
        # audits: `solc = "X.Y.Z"` and `solc_version = "X.Y.Z"`
        for key in ("solc", "solc_version"):
            v = profile_data.get(key)
            if isinstance(v, str) and re.fullmatch(r"\d+\.\d+\.\d+", v.strip()):
                candidates.append(CompilerCandidate(
                    version=v.strip(), source=f"foundry_toml_{key}", config_file=str(path),
                    detail=f"[profile.{profile_name}].{key}", profile=profile_name,
                ))
    return candidates


# --- Hardhat (JS/TS) ---------------------------------------------------------

# Hardhat configs are JS/TS, not a clean data format -- this is a bounded,
# documented heuristic (consistent with this codebase's existing small
# regex-based extractors, e.g. features.py's cast-type scan), not a real
# parser. Scoped to text following the `solidity` key to avoid matching an
# unrelated `version:` field (a dependency pin, etc.) elsewhere in the
# file; a spurious extra match downstream only ever produces an extra
# candidate, which the caller's ambiguity logic surfaces explicitly rather
# than silently mis-resolving.
_HARDHAT_SOLIDITY_BLOCK_RE = re.compile(r"solidity\s*:\s*(\{.*)", re.DOTALL)
_HARDHAT_VERSION_RE = re.compile(r'version\s*:\s*["\'](\d+\.\d+\.\d+)["\']')


def _parse_hardhat_config(path: Path) -> list[CompilerCandidate]:
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return []
    m = _HARDHAT_SOLIDITY_BLOCK_RE.search(text)
    scope = m.group(1) if m else text
    versions = sorted(set(_HARDHAT_VERSION_RE.findall(scope)))
    return [
        CompilerCandidate(version=v, source="hardhat_config", config_file=str(path),
                           detail="solidity.compilers[].version")
        for v in versions
    ]


# --- Dockerfile ---------------------------------------------------------

_DOCKERFILE_SOLC_RE = re.compile(r"solc-select\s+(?:install|use)\s+(\d+\.\d+\.\d+)")


def _parse_dockerfile(path: Path) -> list[CompilerCandidate]:
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return []
    versions = sorted(set(_DOCKERFILE_SOLC_RE.findall(text)))
    return [
        CompilerCandidate(version=v, source="dockerfile", config_file=str(path),
                           detail="solc-select install/use")
        for v in versions
    ]


# --- pragma fallback (only when no authoritative project setting exists) ----

_PRAGMA_RE = re.compile(r"pragma\s+solidity\s+([^;]+);")
_EXACT_VERSION_RE = re.compile(r"(\d+\.\d+\.\d+)")


def _scan_pragma_versions(subproject_root: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for sol_file in subproject_root.rglob("*.sol"):
        # Vendor-dir exclusion must only look at path components WITHIN
        # the project (relative to subproject_root), never the caller's
        # own ancestor directories -- confirmed live: scanning a checkout
        # under a scratch path that happened to contain a literal
        # "artifacts" segment (this module's own default output directory
        # convention) caused every .sol file in the entire project to be
        # wrongly excluded, since `sol_file.parts` includes every
        # component of the full path, not just the ones inside the repo.
        # This made every pragma-fallback-dependent audit resolve to
        # NO_CONFIGURATION_FOUND regardless of its real source content.
        relative_parts = sol_file.relative_to(subproject_root).parts
        if any(part in _VENDOR_DIR_NAMES for part in relative_parts):
            continue
        try:
            text = sol_file.read_text(errors="ignore")
        except OSError:
            continue
        for m in _PRAGMA_RE.finditer(text):
            for v in _EXACT_VERSION_RE.findall(m.group(1)):
                counts[v] += 1
    return counts


# --- build-system detection + top-level resolution --------------------------

def detect_build_system(subproject_root: Path) -> BuildSystem:
    if (subproject_root / "foundry.toml").exists():
        return BuildSystem.FOUNDRY
    if (subproject_root / "hardhat.config.ts").exists() or (subproject_root / "hardhat.config.js").exists():
        return BuildSystem.HARDHAT
    if (subproject_root / "truffle-config.js").exists():
        return BuildSystem.TRUFFLE
    return BuildSystem.UNKNOWN


def resolve_compiler(subproject_root: Path) -> CompilerResolution:
    """Resolves the required Solidity compiler version(s) for one
    subproject root, trying (in priority order): Foundry's `foundry.toml`
    (any profile, `solc`/`solc_version` keys), Hardhat's
    `hardhat.config.{js,ts}`, a `Dockerfile`'s own solc-select directive,
    and only if none of those declare anything, a bare `pragma solidity`
    scan across the subproject's own `.sol` files (excluding vendored
    dependency trees). Never silently picks among genuinely conflicting
    candidates -- returns AMBIGUOUS_COMPILER_CONFIGURATION instead.
    """
    build_system = detect_build_system(subproject_root)
    candidates: list[CompilerCandidate] = []

    foundry_toml = subproject_root / "foundry.toml"
    if foundry_toml.exists():
        candidates.extend(_parse_foundry_toml(foundry_toml))

    for name in ("hardhat.config.ts", "hardhat.config.js"):
        p = subproject_root / name
        if p.exists():
            candidates.extend(_parse_hardhat_config(p))

    dockerfile = subproject_root / "Dockerfile"
    if dockerfile.exists():
        candidates.extend(_parse_dockerfile(dockerfile))

    if candidates:
        foundry_candidates = [c for c in candidates if c.source.startswith("foundry_toml_")]
        other_candidates = [c for c in candidates if not c.source.startswith("foundry_toml_")]

        if foundry_candidates:
            # Foundry has one active profile at a time (`default`, absent an
            # explicit FOUNDRY_PROFILE override this deployment never sets) --
            # only [profile.default]'s own solc/solc_version keys are
            # authoritative for what forge actually compiles with. Other
            # profiles' pins are recorded for visibility but never chosen
            # from, since picking one would be exactly the kind of silent
            # guess this resolver must not make.
            default_candidates = [c for c in foundry_candidates if c.profile == "default"]
            default_versions = sorted(set(c.version for c in default_candidates))

            if len(default_versions) == 1:
                return CompilerResolution(
                    status=CompilerResolutionStatus.RESOLVED, versions=default_versions,
                    primary_version=default_versions[0], candidates=candidates, build_system=build_system,
                    detail=f"resolved from [profile.default] ({default_candidates[0].config_file})",
                )
            if len(default_versions) > 1:
                # e.g. [profile.default] sets both `solc` and `solc_version`
                # to different values -- a genuine authoring conflict.
                return CompilerResolution(
                    status=CompilerResolutionStatus.AMBIGUOUS_COMPILER_CONFIGURATION,
                    versions=default_versions, primary_version=None, candidates=candidates,
                    build_system=build_system,
                    detail=f"[profile.default] itself declares conflicting versions: {default_versions}",
                )
            # [profile.default] declares no version at all -- other profiles'
            # pins don't apply by default, so this is treated the same as
            # "no config found" and falls through to pragma fallback below,
            # not silently borrowed from a non-default profile.

        elif other_candidates:
            # Hardhat (and, if ever present, a Dockerfile solc directive)
            # has no single-active-profile concept the way Foundry does --
            # Hardhat natively resolves each source file against whichever
            # of its declared `compilers` entries fits that file's pragma.
            # Multiple distinct versions here is a legitimate, supported
            # multi-compiler project (confirmed real: 2024-01-curves
            # declares both 0.8.7 and 0.5.15), not an authoring conflict --
            # every distinct version is simply required, and provisioning
            # must supply all of them.
            versions = sorted(set(c.version for c in other_candidates))
            return CompilerResolution(
                status=CompilerResolutionStatus.RESOLVED, versions=versions,
                primary_version=versions[0] if len(versions) == 1 else None,
                candidates=candidates, build_system=build_system,
                detail=(f"resolved from {other_candidates[0].source} ({other_candidates[0].config_file})"
                        if len(versions) == 1 else
                        f"multiple compiler versions natively declared by {build_system.value.lower()}: {versions}"),
            )

    pragma_counts = _scan_pragma_versions(subproject_root)
    if not pragma_counts:
        return CompilerResolution(
            status=CompilerResolutionStatus.NO_CONFIGURATION_FOUND, versions=[], primary_version=None,
            candidates=[], build_system=build_system,
            detail="no foundry.toml/hardhat-config compiler version, no Dockerfile solc directive, and no "
                   "parseable `pragma solidity` statements found under this subproject root",
        )
    if len(pragma_counts) == 1:
        v = next(iter(pragma_counts))
        cand = CompilerCandidate(version=v, source="pragma_fallback", config_file="(scanned *.sol pragmas)",
                                  detail=f"{pragma_counts[v]} file(s) agree")
        return CompilerResolution(
            status=CompilerResolutionStatus.RESOLVED, versions=[v], primary_version=v, candidates=[cand],
            build_system=build_system,
            detail=f"no authoritative project setting; pragma fallback ({pragma_counts[v]} file(s) agree on {v})",
        )
    cands = [
        CompilerCandidate(version=v, source="pragma_fallback", config_file="(scanned *.sol pragmas)",
                           detail=f"{n} file(s)")
        for v, n in pragma_counts.most_common()
    ]
    return CompilerResolution(
        status=CompilerResolutionStatus.AMBIGUOUS_COMPILER_CONFIGURATION, versions=sorted(pragma_counts),
        primary_version=None, candidates=cands, build_system=build_system,
        detail=f"no authoritative project setting, and a pragma scan found {len(pragma_counts)} conflicting "
               f"exact versions with no dominant candidate: {dict(pragma_counts)}",
    )
