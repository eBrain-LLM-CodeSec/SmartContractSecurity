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
when an authoritative project setting itself conflicts (e.g. a Foundry
`[profile.default]` declaring both `solc` and `solc_version` to different
values) -- a project that genuinely declares, or is inferred via pragma
scanning to require, more than one compiler version (e.g. `2024-01-curves`'
Hardhat config, which lists both `0.8.7` and `0.5.15`; or `2024-06-size`,
whose `src/` pins `0.8.23` while a few test mocks pin `0.8.13`/`0.8.19`) is
not ambiguous -- it RESOLVES to multiple required versions, exactly
mirroring Foundry/Hardhat's own default per-file auto-detection behavior
when no single global `solc` pin exists.
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
        # three key spellings, real forms confirmed present across the 27
        # audits: `solc = "X.Y.Z"`, `solc_version = "X.Y.Z"`, and (older
        # Foundry convention, confirmed live in 2024-06-vultisig's own
        # foundry.toml) `solc-version = "X.Y.Z"` -- a bare TOML key may
        # contain hyphens, so tomllib parses it fine; the old two-key list
        # just never looked for it, which is why vultisig fell through to
        # a bare pragma scan and came back "ambiguous" even though its own
        # foundry.toml authoritatively pins 0.7.6.
        for key in ("solc", "solc_version", "solc-version"):
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
# A pragma constraint only pins a single required version if it is ONE
# version literal with at most one leading operator (^, ~, =, or bare) --
# `0.8.20`, `^0.8.20`, `=0.8.20`. A range (`>=0.6.2 <0.9.0`, `>=0.5.0`,
# `0.7 - 0.8`) declares compatibility with many versions, not a requirement
# for any one of them.
_EXACT_PIN_RE = re.compile(r"^[\^~=]?\s*(\d+\.\d+\.\d+)$")
# Directory-boundary markers for a vendored/independent project embedded
# directly in the checkout rather than under a conventional `lib`/
# `node_modules` name.
_NESTED_CONFIG_NAMES = ("foundry.toml", "hardhat.config.ts", "hardhat.config.js", "package.json")


def _extract_exact_pin(constraint: str) -> str | None:
    """Confirmed real bug this replaces: the old implementation extracted
    EVERY `\\d+\\.\\d+\\.\\d+`-shaped number out of a pragma constraint,
    including both bounds of a range -- so `pragma solidity >=0.6.2
    <0.9.0;` (routine in vendored library code, e.g. forge-std) was counted
    as declaring TWO separately 'required' exact versions (0.6.2 AND
    0.9.0), fabricating pragma diversity that was never actually a
    disagreement about which compiler to use. A range pragma provides no
    signal about which exact version is required -- any compiler in range
    satisfies it -- so it must not vote at all in the fallback below."""
    m = _EXACT_PIN_RE.match(constraint.strip())
    return m.group(1) if m else None


def _nested_vendor_dirs(subproject_root: Path) -> set[tuple[str, ...]]:
    """Directories (relative to subproject_root) that themselves contain
    their own build/package configuration -- a vendored/independent
    project embedded directly in the checkout (e.g. forge-std vendored
    under `test/forge-std/`, with its own `foundry.toml`, rather than
    under the conventional `lib/`), not the audited subproject's own
    source. Confirmed real: 2023-12-ethereumcreditguild vendors forge-std
    this way; its wide-range pragmas (see `_extract_exact_pin`) used to
    leak into the fallback pragma scan and make an otherwise-unanimous
    project (all of its own src/test code pins exactly 0.8.13) look
    falsely ambiguous."""
    dirs: set[tuple[str, ...]] = set()
    for name in _NESTED_CONFIG_NAMES:
        for p in subproject_root.rglob(name):
            parent = p.parent
            if parent == subproject_root:
                continue
            rel = parent.relative_to(subproject_root).parts
            if any(part in _VENDOR_DIR_NAMES for part in rel):
                continue  # already covered by the conventional-name exclusion
            dirs.add(rel)
    return dirs


def _scan_pragma_versions(subproject_root: Path) -> Counter[str]:
    nested_vendor_dirs = _nested_vendor_dirs(subproject_root)
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
        if any(relative_parts[:len(nd)] == nd for nd in nested_vendor_dirs):
            continue
        try:
            text = sol_file.read_text(errors="ignore")
        except OSError:
            continue
        for m in _PRAGMA_RE.finditer(text):
            v = _extract_exact_pin(m.group(1))
            if v is not None:
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
    # Multiple distinct exact-pinned versions with no authoritative
    # project setting is NOT an authoring conflict for Foundry (or
    # Hardhat, handled above): confirmed live -- absent an explicit
    # `solc`/`solc_version` pin, Foundry's own default behavior
    # (`auto_detect_solc`) is to compile EACH source file against whichever
    # locally-available compiler satisfies that file's own pragma,
    # transparently using different solc binaries for different files in
    # the same build. This is exactly the same "legitimate multi-compiler
    # project" situation as the Hardhat `other_candidates` branch above
    # (2024-01-curves' declared 0.8.7/0.5.15), just discovered via pragma
    # scanning instead of an explicit config list. `AMBIGUOUS_COMPILER_
    # CONFIGURATION` is reserved for a genuine authoring conflict -- e.g. a
    # `[profile.default]` itself setting `solc` and `solc_version` to two
    # different values (handled earlier in this function) -- never for
    # ordinary pragma diversity across files, which real Foundry builds
    # every day without any ambiguity at all. (Confirmed real for three
    # audits previously misclassified this way: 2024-06-size, 2025-06-
    # panoptic, 2024-07-basin -- each has one dominant version in its own
    # `src/` plus a handful of test-mock/script files pinned differently,
    # not a disagreement about what the project's own code requires.)
    cands = [
        CompilerCandidate(version=v, source="pragma_fallback", config_file="(scanned *.sol pragmas)",
                           detail=f"{n} file(s)")
        for v, n in pragma_counts.most_common()
    ]
    versions = sorted(pragma_counts)
    return CompilerResolution(
        status=CompilerResolutionStatus.RESOLVED, versions=versions, primary_version=None,
        candidates=cands, build_system=build_system,
        detail=f"no authoritative project setting; pragma fallback found {len(pragma_counts)} distinct exact "
               f"versions across files with no single-compiler config to force one globally -- treated as a "
               f"legitimate multi-version build (Foundry/Hardhat's own default per-file auto-detection "
               f"behavior), not an authoring conflict: {dict(pragma_counts)}",
    )
