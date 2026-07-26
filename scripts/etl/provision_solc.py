"""A4 CLI: compiler resolution + provisioning for the sample (see plan A4).
**Login-node only** -- needs internet for solc-select's version list and to
download binaries; compute nodes may not have it.

`python -m scripts.etl.provision_solc <sample_json> <full_index_jsonl>
    [--out data/gnn/index/candidates.json]`

For each sampled contract, resolves a solc version via `pragma.py`'s
"exact metadata version, else lowest-satisfying-minor-newest-patch, else
unresolved" policy, installs whatever's missing, then **smoke-tests with a
real `Slither()` run** (not just `solc --version`) once per distinct
provisioned major.minor -- the real failure mode is a pinned Slither/
crytic-compile mis-parsing legacy AST, not the binary failing to launch.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from solc_select import solc_select as ss

from a4v.gnn.etl.pragma import resolve_solc_version
from a4v.graph import BuildFailed, ProgramGraph

# Version-appropriate smoke probes -- constructor/pragma syntax differs
# materially across 0.4 (same-name constructor, no `override`), 0.5+
# (explicit `constructor`), and 0.8 (checked arithmetic by default).
_PROBE_BY_MAJOR_MINOR = {
    "0.4": 'pragma solidity ^0.4.24;\ncontract Probe {\n    uint256 public v;\n    function Probe() public { v = 0; }\n}\n',
    "0.5": 'pragma solidity ^0.5.0;\ncontract Probe {\n    uint256 public v;\n    constructor() public { v = 0; }\n}\n',
    "0.6": 'pragma solidity ^0.6.0;\ncontract Probe {\n    uint256 public v;\n    constructor() public { v = 0; }\n}\n',
    "0.7": 'pragma solidity ^0.7.0;\ncontract Probe {\n    uint256 public v;\n    constructor() { v = 0; }\n}\n',
    "0.8": 'pragma solidity ^0.8.0;\ncontract Probe {\n    uint256 public v;\n    constructor() { v = 0; }\n}\n',
}


def _probe_source_for(major_minor: str) -> str:
    return _PROBE_BY_MAJOR_MINOR.get(major_minor, _PROBE_BY_MAJOR_MINOR["0.8"])


def smoke_test_version(version: str, solc_path: Path) -> tuple[bool, str]:
    major_minor = ".".join(version.split(".")[:2])
    probe_src = _probe_source_for(major_minor)
    with tempfile.TemporaryDirectory() as td:
        probe_file = Path(td) / "Probe.sol"
        probe_file.write_text(probe_src)
        try:
            ProgramGraph.build(probe_file, extra_kwargs={"solc": str(solc_path)})
            return True, "ok"
        except BuildFailed as e:
            return False, str(e)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sample_json", type=Path)
    ap.add_argument("full_index_jsonl", type=Path)
    ap.add_argument("--out", type=Path, default=Path("data/gnn/index/candidates.json"))
    ap.add_argument(
        "--pragma-less-fallback", nargs="*", default=None,
        help="evidence-based ordered solc versions for pragma-less contracts "
             "(e.g. --pragma-less-fallback 0.4.24 0.8.17 0.8.20 -- see MANIFEST.md's "
             "20/20 smoke-test result before setting this for a new dataset)",
    )
    args = ap.parse_args(argv)

    sample = json.loads(args.sample_json.read_text())
    sample_ids = set(sample["contract_ids"])

    rows_by_id = {}
    for line in args.full_index_jsonl.read_text().splitlines():
        row = json.loads(line)
        if row["contract_id"] in sample_ids:
            rows_by_id[row["contract_id"]] = row

    already_installed = ss.installed_versions()
    installable = ss.get_installable_versions()  # network call -- login node only
    available = sorted(set(already_installed) | set(installable))

    resolutions: dict[str, dict] = {}
    needed_versions: set[str] = set()
    for cid, row in rows_by_id.items():
        pragma_expr = [f"^{row['pragma_major_minor']}.0"] if row.get("pragma_major_minor") else []
        res = resolve_solc_version(
            pragma_expr, available, pragma_less_fallback=args.pragma_less_fallback,
        )
        resolutions[cid] = {
            "resolved_version": res.resolved_version,
            "unresolved": res.unresolved,
            "reason": res.reason,
            "candidates_to_try": res.candidates_to_try,
        }
        needed_versions.update(res.candidates_to_try)

    to_install = sorted(v for v in needed_versions if v not in already_installed)
    if to_install:
        print(f"installing {len(to_install)} solc version(s): {to_install}")
        ss.install_artifacts(to_install, silent=False)

    smoke_results: dict[str, dict] = {}
    probed_major_minors: set[str] = set()
    for version in sorted(needed_versions):
        major_minor = ".".join(version.split(".")[:2])
        if major_minor in probed_major_minors:
            continue
        probed_major_minors.add(major_minor)
        solc_path = Path(ss.artifact_path(version))
        ok, detail = smoke_test_version(version, solc_path)
        smoke_results[major_minor] = {"probed_version": version, "ok": ok, "detail": detail}
        print(f"smoke {major_minor} (via {version}): {'OK' if ok else 'FAILED: ' + detail}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({
        "resolutions": resolutions,
        "smoke_results": smoke_results,
    }, indent=2, sort_keys=True))
    print(f"-> {args.out}")

    unresolved_count = sum(1 for r in resolutions.values() if r["unresolved"])
    if unresolved_count:
        print(f"WARNING: {unresolved_count}/{len(resolutions)} sampled contracts have no resolvable solc version")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
