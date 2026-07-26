"""Part 0 API verification spike (see .claude/plans/humming-sprouting-lampson.md).

Cheap, no-dataset runtime checks that de-risk the GNN ETL approach before any
dataset work:

1. Confirm `extra_kwargs={"solc": <abs path>}` on `ProgramGraph.build` compiles
   without touching solc-select's global-version file (the linchpin of
   race-free parallel compilation across worker processes).
2. Record whether `solc_force_legacy_json` changes compilation outcome against
   an old (0.4.x) solc, for A4's provisioning notes.

Run with: `.venv/bin/python scripts/etl/verify_part0.py`. Not a pytest module
-- prints a pass/fail report and exits non-zero on any failed assertion.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from a4v.graph import ProgramGraph, BuildFailed  # noqa: E402

SOLC_820 = REPO_ROOT / ".venv/.solc-select/artifacts/solc-0.8.20/solc-0.8.20"
SOLC_424 = REPO_ROOT / ".venv/.solc-select/artifacts/solc-0.4.24/solc-0.4.24"
CASTS = REPO_ROOT / "tests/fixtures/features/Casts.sol"
OLD_STYLE = REPO_ROOT / "tests/fixtures/wrong_solc/OldStyle.sol"
VAULT = REPO_ROOT / "tests/fixtures/multi_contract/Vault.sol"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" -- {detail}" if detail else ""))


def global_version_path() -> Path:
    install_dir = os.environ.get("SOLC_SELECT_INSTALL_DIR")
    base = Path(install_dir) if install_dir else Path.home() / ".solc-select"
    return base / "global-version"


def main() -> int:
    for path in (SOLC_820, SOLC_424, CASTS, OLD_STYLE):
        check(f"fixture exists: {path.relative_to(REPO_ROOT)}", path.exists())

    gv_path = global_version_path()
    existed_before = gv_path.exists()
    content_before = gv_path.read_text() if existed_before else None
    check(
        "global-version location resolved",
        True,
        f"{gv_path} (exists_before={existed_before})",
    )

    # --- 1. explicit-solc kwarg: compiles + never touches global-version ---
    try:
        pg = ProgramGraph.build(CASTS, extra_kwargs={"solc": str(SOLC_820)})
        compiled_ok = len(pg.nodes_of_kind("function")) > 0
        check("explicit `solc` kwarg compiles Casts.sol", compiled_ok,
              f"{len(pg.graph.nodes)} nodes")
    except BuildFailed as e:
        check("explicit `solc` kwarg compiles Casts.sol", False, str(e))

    existed_after = gv_path.exists()
    content_after = gv_path.read_text() if existed_after else None
    if not existed_before:
        check("global-version absent-before => absent-after", not existed_after,
              f"exists_after={existed_after}")
    else:
        check("global-version content unchanged", content_after == content_before,
              f"before={content_before!r} after={content_after!r}")

    # Repeat with a *different* solc version to make sure the kwarg path
    # can't be accidentally satisfied by a global-version that already
    # happens to match.
    try:
        pg2 = ProgramGraph.build(OLD_STYLE, extra_kwargs={"solc": str(SOLC_424)})
        check("explicit `solc` kwarg compiles OldStyle.sol (0.4.24)",
              len(pg2.nodes_of_kind("function")) > 0)
    except BuildFailed as e:
        check("explicit `solc` kwarg compiles OldStyle.sol (0.4.24)", False, str(e))

    existed_after2 = gv_path.exists()
    content_after2 = gv_path.read_text() if existed_after2 else None
    if not existed_before:
        check("global-version still absent after 2nd (different-version) build",
              not existed_after2, f"exists_after={existed_after2}")
    else:
        check("global-version still unchanged after 2nd (different-version) build",
              content_after2 == content_before,
              f"before={content_before!r} after={content_after2!r}")

    # --- 2. solc_force_legacy_json against an old (0.4.x) solc ---
    try:
        pg3 = ProgramGraph.build(
            OLD_STYLE,
            extra_kwargs={"solc": str(SOLC_424), "solc_force_legacy_json": True},
        )
        check("solc_force_legacy_json=True compiles OldStyle.sol (0.4.24)",
              len(pg3.nodes_of_kind("function")) > 0)
        legacy_note = "compiled fine WITH solc_force_legacy_json=True"
    except BuildFailed as e:
        check("solc_force_legacy_json=True compiles OldStyle.sol (0.4.24)", False, str(e))
        legacy_note = f"FAILED with solc_force_legacy_json=True: {e}"

    try:
        pg4 = ProgramGraph.build(OLD_STYLE, extra_kwargs={"solc": str(SOLC_424)})
        check("default (no solc_force_legacy_json) compiles OldStyle.sol (0.4.24)",
              len(pg4.nodes_of_kind("function")) > 0)
        default_note = "compiled fine WITHOUT solc_force_legacy_json"
    except BuildFailed as e:
        check("default (no solc_force_legacy_json) compiles OldStyle.sol (0.4.24)", False, str(e))
        default_note = f"FAILED without solc_force_legacy_json: {e}"

    print()
    print("--- A4 note: solc_force_legacy_json vs solc 0.4.24 ---")
    print(f"  with flag:    {legacy_note}")
    print(f"  without flag: {default_note}")

    # --- 3. external-node representation (kind vs external flag) ---
    # Casts.sol has no external calls; use Vault.sol (has an IOracle call +
    # a low-level-call pattern) so this actually exercises the ext:: path.
    try:
        pg_vault = ProgramGraph.build(VAULT, extra_kwargs={"solc": str(SOLC_820)})
        ext_nodes = [
            (n, d) for n, d in pg_vault.graph.nodes(data=True)
            if d.get("external") or n.startswith("ext::")
        ]
        check(
            "external callees are kind='function' with external=True / ext:: prefix, not a distinct kind",
            len(ext_nodes) > 0 and all(d.get("kind") == "function" for _, d in ext_nodes),
            f"{ext_nodes}",
        )
    except BuildFailed as e:
        check("external callees are kind='function' with external=True / ext:: prefix", False, str(e))

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print()
    print(f"{len(results) - n_fail}/{len(results)} checks passed")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
