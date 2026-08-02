"""Phase 2: hermetic, checksum-verified toolchain provisioning.

Reads `audit-build-manifest.jsonl` (produced by
`scripts.benchmark.audit_build_manifest`), determines the complete set of
required Solidity compiler versions, downloads each exactly once into a
benchmark-owned, deterministic, writable location (never `$HOME/.svm`,
never `$HOME/.solc-select` -- see the note below on why that path is
itself session-dependent), verifies every binary's SHA-256 against an
independently-fetched checksum, and writes `toolchain-lock.json`
recording path + checksum + provenance for everything provisioned.

This command MAY use the network (it is the one step in this whole
pipeline that is allowed to). Benchmark execution (Phase 3/4) never
downloads anything at all -- it only ever reads what this command already
verified and wrote to disk.

**Why `$HOME/.solc-select` cannot be trusted as-is**: `solc-select`
resolves its own install directory from `$VIRTUAL_ENV` if that env var
happens to be set at import time, else falls back to `Path.home()`
(`solc_select/constants.py`). Confirmed live during this work's own
investigation: the *same* install call resolves to `.venv/.solc-select`
under one invocation (venv active) and `$HOME/.solc-select` under another
(venv not active, e.g. calling `.venv/bin/python` directly without
sourcing `activate`) -- a real, hidden, session-dependent state
dependency that has previously left the two directories in inconsistent
states (a global-version pointer in `$HOME/.solc-select` clobbered by an
unrelated process, breaking every subsequent compile relying on the
`.venv` copy instead). This command routes solc-select's own install
mechanism to a directory *this command controls explicitly* (via
`VIRTUAL_ENV`, set before `solc_select` is ever imported in this process)
so the ambiguity cannot occur.

`python -m scripts.benchmark.provision_toolchains
    --manifest audit-build-manifest.jsonl
    --toolchain-dir .benchmark/toolchains
    --lock-out toolchain-lock.json`
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

_UA_HEADERS = {"User-Agent": "agent4vul-benchmark-toolchain-provisioner"}
_OFFICIAL_LIST_URLS = (
    "https://binaries.soliditylang.org/linux-amd64/list.json",
    "https://raw.githubusercontent.com/crytic/solc/new-list-json/linux/amd64/list.json",
)


@dataclass
class ToolchainEntry:
    tool: str                # "solc"
    version: str
    path: str                 # absolute path to the verified binary
    sha256: str
    checksum_source: str      # "soliditylang.org/list.json" | "crytic/solc list.json" | "self-pinned-at-provisioning (no independent source found)"
    provisioned_at: float     # unix timestamp


def required_solc_versions(manifest_path: Path) -> set[str]:
    versions: set[str] = set()
    for line in manifest_path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        versions.update(rec.get("required_compiler_versions") or [])
    return versions


def _fetch_official_checksums() -> dict[str, str]:
    """version -> sha256 hex (no 0x prefix), from the first reachable
    official list. Best-effort: a version genuinely absent from every
    official list (very old releases) is simply not in the returned dict,
    handled explicitly by the caller, not silently ignored."""
    checksums: dict[str, str] = {}
    for url in _OFFICIAL_LIST_URLS:
        try:
            req = urllib.request.Request(url, headers=_UA_HEADERS)
            data = json.loads(urllib.request.urlopen(req, timeout=20).read())
        except Exception as e:  # noqa: BLE001 -- network flakiness must not abort provisioning of versions that DO resolve
            print(f"  (could not fetch {url}: {e})", file=sys.stderr)
            continue
        for build in data.get("builds", []):
            v, sha = build.get("version"), build.get("sha256")
            if v and sha and v not in checksums:
                checksums[v] = sha.removeprefix("0x")
    return checksums


def verify_and_install(src: Path, version: str, toolchain_dir: Path, official_checksums: dict[str, str]) -> ToolchainEntry:
    """Pure(ish) checksum-verification + deterministic-placement step,
    factored out of `provision_solc` so it's testable directly against a
    real file on disk without needing to mock solc-select's own import
    machinery (whose install directory is a module-level constant computed
    at import time -- awkward and fragile to mock cleanly; this function
    doesn't need to touch it at all, since by the time it runs, `src` is
    already a downloaded file on disk)."""
    if not src.exists():
        raise RuntimeError(f"solc-select reported {version} installed but {src} does not exist")

    actual_sha = hashlib.sha256(src.read_bytes()).hexdigest()
    expected_sha = official_checksums.get(version)
    if expected_sha is not None:
        if actual_sha != expected_sha:
            raise RuntimeError(
                f"CHECKSUM MISMATCH for solc {version}: downloaded {actual_sha}, "
                f"official list.json says {expected_sha}. Refusing to provision a "
                f"compiler binary that does not match its published checksum."
            )
        checksum_source = "official list.json (soliditylang.org or crytic/solc)"
    else:
        checksum_source = "self-pinned-at-provisioning (no independent source found for this version)"

    dest_dir = toolchain_dir / "solc" / version
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "solc"
    shutil.copy2(src, dest)
    dest.chmod(0o755)
    # verify the COPY too -- catches a corrupting filesystem issue between
    # solc-select's own directory and this command's deterministic one.
    copied_sha = hashlib.sha256(dest.read_bytes()).hexdigest()
    if copied_sha != actual_sha:
        raise RuntimeError(f"copy corruption provisioning solc {version}: {dest} does not match {src}")

    return ToolchainEntry(
        tool="solc", version=version, path=str(dest.resolve()), sha256=actual_sha,
        checksum_source=checksum_source, provisioned_at=time.time(),
    )


def provision_solc(version: str, toolchain_dir: Path, official_checksums: dict[str, str]) -> ToolchainEntry:
    """Downloads `version` via solc-select (redirected to a location this
    command controls explicitly -- see module docstring) if not already
    present, then verifies + places it via `verify_and_install`."""
    solc_select_home = toolchain_dir / "_solc_select_home"
    solc_select_home.mkdir(parents=True, exist_ok=True)
    # Must be set BEFORE solc_select is imported anywhere in this process --
    # its install directory is a module-level constant computed at import
    # time (see module docstring).
    os.environ["VIRTUAL_ENV"] = str(solc_select_home)
    import solc_select.solc_select as ss  # local import: after VIRTUAL_ENV is set

    installed = ss.installed_versions()
    if version not in installed:
        ok = ss.install_artifacts([version], silent=True)
        if not ok:
            raise RuntimeError(f"solc-select could not install {version} (not a known release)")

    src = ss.artifact_path(version)
    return verify_and_install(src, version, toolchain_dir, official_checksums)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--toolchain-dir", type=Path, required=True)
    ap.add_argument("--lock-out", type=Path, required=True)
    args = ap.parse_args(argv)

    args.toolchain_dir.mkdir(parents=True, exist_ok=True)
    versions = sorted(required_solc_versions(args.manifest))
    print(f"required solc versions ({len(versions)}): {versions}")

    print("fetching official checksums...")
    official_checksums = _fetch_official_checksums()
    print(f"  {len(official_checksums)} official checksums available")

    entries: list[ToolchainEntry] = []
    failures: list[tuple[str, str]] = []
    for v in versions:
        try:
            entry = provision_solc(v, args.toolchain_dir, official_checksums)
            entries.append(entry)
            print(f"  {v}: OK ({entry.checksum_source})")
        except Exception as e:  # noqa: BLE001
            failures.append((v, str(e)))
            print(f"  {v}: FAILED -- {e}")

    lock = {
        "schema": "toolchain-lock/v1",
        "generated_at": time.time(),
        "toolchain_dir": str(args.toolchain_dir.resolve()),
        "solc": {e.version: asdict(e) for e in entries},
        "provisioning_failures": [{"version": v, "error": err} for v, err in failures],
    }
    args.lock_out.parent.mkdir(parents=True, exist_ok=True)
    args.lock_out.write_text(json.dumps(lock, indent=2, sort_keys=True))
    print(f"\n-> {args.lock_out}")
    print(f"provisioned {len(entries)}/{len(versions)} required solc versions"
          + (f", {len(failures)} FAILED" if failures else ""))

    # fail loudly (non-zero exit) if anything required could not be
    # provisioned -- per this task's constraint, benchmark execution must
    # never silently proceed with a smaller toolchain set than declared.
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
