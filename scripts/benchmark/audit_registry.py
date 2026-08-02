"""Authoritative, explicit list of the 27 audits (+ subprojects) this
benchmark-infrastructure work targets, and the small set of hand-verified,
documented compatibility facts that cannot be derived from each audit's
own repository alone.

This is deliberately a plain, inspectable data table -- not control flow
buried inside an orchestration script's if/elif chain (that was
`run_full_study_batch.py`'s `FORGE_VERSION` overrides for
`2023-12-ethereumcreditguild`/`2024-06-size`, discovered live during this
work's own inspection phase: correct, but undocumented and unrecorded in
any manifest). Every override here is isolated to the one audit it
applies to, and every override's presence is written into
`audit-build-manifest.jsonl` (`compatibility_overrides` field) so it is
never silently reapplied to an audit it wasn't verified against.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SubprojectSpec:
    subproject_id: str
    relative_root: str  # path relative to the audit checkout root
    build_system_hint: str | None = None  # "foundry" | "hardhat" | None (auto-detect)


@dataclass(frozen=True)
class AuditSpec:
    audit_id: str
    subprojects: tuple[SubprojectSpec, ...]
    # Hand-verified compatibility facts that cannot be derived from the
    # audit's own repository content -- e.g. a specific Foundry *tool*
    # version (not a solc version) required to work around a real
    # incompatibility between this audit's own recipe and the Foundry
    # version otherwise in use. Every entry here was confirmed live in a
    # prior session (see run_full_study_batch.py's compile_ethereumcreditguild/
    # compile_size, which set these via direct os.environ assignment with
    # no documentation of *why* -- this table is that documentation).
    foundry_version_override: str | None = None
    override_reason: str | None = None
    npm_install_flags: tuple[str, ...] = ()
    network_required_for_dependency_install: bool = True  # nearly always true (npm/forge install)


# The 27 audits this deployment's build infrastructure has previously
# compiled successfully at least once (per Implementation.md /
# mgpr_evidence_analysis.md's 27-audit list), split by whether their own
# run_cmd_dir (from EVMbench's own audits/<id>/config.yaml) already names
# the single project root, or the audit is a genuine multi-subproject
# monorepo needing more than one entry.
AUDITS: tuple[AuditSpec, ...] = (
    AuditSpec("2023-07-pooltogether", (SubprojectSpec("default", "vault"),)),
    AuditSpec("2025-04-forte", (SubprojectSpec("default", "."),)),
    AuditSpec("2026-01-tempo-feeamm", (SubprojectSpec("default", "."),)),
    AuditSpec("2024-08-phi", (SubprojectSpec("default", "."),)),
    AuditSpec("2025-01-liquid-ron", (SubprojectSpec("default", "."),)),
    AuditSpec("2025-06-panoptic", (SubprojectSpec("default", "."),)),
    AuditSpec("2026-01-tempo-mpp-streams", (SubprojectSpec("default", "."),)),
    AuditSpec("2026-01-tempo-stablecoin-dex", (SubprojectSpec("default", "."),)),
    AuditSpec("2024-01-canto", (SubprojectSpec("default", "."),)),
    AuditSpec("2024-05-loop", (SubprojectSpec("default", "."),)),
    AuditSpec("2024-06-vultisig", (SubprojectSpec("default", "."),)),
    AuditSpec("2025-10-sequence", (SubprojectSpec("default", "."),)),
    AuditSpec("2024-07-basin", (SubprojectSpec("default", "."),)),
    AuditSpec("2024-07-benddao", (SubprojectSpec("default", "."),)),
    AuditSpec("2024-12-secondswap", (SubprojectSpec("default", "."),)),
    AuditSpec("2024-05-munchables", (SubprojectSpec("default", "."),)),
    AuditSpec("2024-01-renft", (SubprojectSpec("default", "smart-contracts"),)),
    AuditSpec("2025-02-thorwallet", (SubprojectSpec("default", ".", "hardhat"),)),
    AuditSpec("2023-10-nextgen", (SubprojectSpec("default", "hardhat", "hardhat"),
                                   # `hardhat/` is the run_cmd_dir per config.yaml; nextgen's
                                   # own Dockerfile also `npm up hardhat` before compiling --
                                   # not a compiler-version fact, so not modeled as an override
                                   # here, just as an npm_install_flags-adjacent note.
                                   )),
    AuditSpec("2024-01-curves", (SubprojectSpec("default", ".", "hardhat"),)),
    AuditSpec("2024-07-traitforge", (SubprojectSpec("default", ".", "hardhat"),)),
    AuditSpec("2025-04-virtuals", (SubprojectSpec("default", ".", "hardhat"),)),
    AuditSpec("2025-05-blackhole", (SubprojectSpec("default", ".", "hardhat"),)),
    AuditSpec(
        "2023-12-ethereumcreditguild", (SubprojectSpec("default", "."),),
        foundry_version_override="nightly-5b7e4cb3c882b28f3c32ba580de27ce7381f415a",
        override_reason="confirmed live (prior session): this audit's own forge-std/solmate pin requires "
                         "a specific Foundry nightly build; the generally-pinned Foundry release fails to "
                         "compile it for reasons unrelated to solc version selection.",
    ),
    AuditSpec(
        "2024-06-thorchain",
        (SubprojectSpec("ethereum", "ethereum", "hardhat"), SubprojectSpec("avalanche", "avalanche", "hardhat")),
    ),
    AuditSpec(
        "2024-06-size", (SubprojectSpec("default", "."),),
        foundry_version_override="v0.3.0",
        override_reason="confirmed live (prior session): this audit's own foundry.lock/remappings require "
                         "an older pinned Foundry release; the generally-pinned Foundry release fails to "
                         "compile it for reasons unrelated to solc version selection.",
    ),
    AuditSpec("2024-04-noya", (SubprojectSpec("default", "."),), npm_install_flags=("--force",)),
)

AUDIT_IDS: tuple[str, ...] = tuple(a.audit_id for a in AUDITS)
BY_ID: dict[str, AuditSpec] = {a.audit_id: a for a in AUDITS}

assert len(AUDIT_IDS) == 27, f"expected 27 audits, got {len(AUDIT_IDS)}"
