"""In-scope file extraction from an audit's README.md Scope table.

Restricting the Commentator/seed/Auditor passes to in-scope files matters
for cost, not just correctness: a real Foundry project's compiled graph
includes every vendored dependency (OpenZeppelin, prb-math, ...) alongside
the audit's own code -- often 10-50x more functions than are actually in
scope. Running the Commentator over the whole compiled graph would be
reckless; this module is what makes "gate Commentator to graph/4naly3er
pre-flagged nodes" (plan cost-control section) possible in the first place.
"""
from __future__ import annotations

import re
from pathlib import Path

# Matches a markdown table row whose first cell is a `[path](url)` link,
# e.g. "| [vault/src/Vault.sol](https://github.com/.../Vault.sol) | 540 | ... |"
_SCOPE_ROW_RE = re.compile(r"^\|\s*\[([^\]]+)\]\([^)]*\)\s*\|")


def parse_scope_files(readme_text: str) -> list[str]:
    """Returns the relative file paths listed in the README's Scope table,
    in the order they appear. Returns [] if no scope table is found."""
    files = []
    in_scope_section = False
    for line in readme_text.splitlines():
        stripped = line.strip()
        if re.match(r"^#+\s*scope\s*$", stripped, re.IGNORECASE):
            in_scope_section = True
            continue
        if in_scope_section and stripped.startswith("#"):
            break  # next section header ends the scope table
        if not in_scope_section:
            continue
        m = _SCOPE_ROW_RE.match(stripped)
        if m:
            files.append(m.group(1).strip())
    return files


def in_scope_files_for_subproject(readme_text: str, subproject_prefix: str) -> set[str]:
    """Scope entries are repo-root-relative (e.g. "vault/src/Vault.sol"), but
    a per-subproject compile (e.g. Slither run against just `vault/`) sees
    paths relative to that subproject (e.g. "src/Vault.sol"). Strips the
    given prefix and returns only the files that matched it.
    """
    prefix = subproject_prefix.rstrip("/") + "/"
    out = set()
    for f in parse_scope_files(readme_text):
        if f.startswith(prefix):
            out.add(f[len(prefix):])
    return out


def filter_function_nodes_by_scope(function_nodes: list[str], node_files: dict[str, str],
                                    checkout_root: Path, in_scope_relpaths: set[str]) -> list[str]:
    """Keeps only function nodes whose source file matches one of
    `in_scope_relpaths` (relative to `checkout_root`)."""
    checkout_root = checkout_root.resolve()
    kept = []
    for node in function_nodes:
        file_str = node_files.get(node)
        if not file_str:
            continue
        try:
            rel = Path(file_str).resolve().relative_to(checkout_root)
        except ValueError:
            continue
        if str(rel) in in_scope_relpaths:
            kept.append(node)
    return kept
