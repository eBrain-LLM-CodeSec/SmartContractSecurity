"""Investigation tools for the Agentic Auditor: thin, read-mostly wrappers
over the program graph and Slither, sandboxed to a single audit's checkout,
with per-audit on-disk caching so repeated calls (across candidates sharing
a contract/inheritance tree) are free.

`codex exec` is a full coding agent with its own shell/file tools already --
it doesn't need a read_file/grep wrapper to *access* the filesystem. These
wrappers exist because they expose things codex has no other way to get
(program-graph queries, bundle expansion, targeted Slither detectors) and
because wrapping them gives us caching + a loggable, sandboxed call surface
for the session trace. Each function is also reachable as a CLI subcommand
(`python -m a4v.tools <name> ...`) so a generated shell wrapper in the
audit's working directory can hand it to codex as an invocable tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from a4v.graph import ProgramGraph
from a4v.slice import BundleBuilder, numbered_source


class SandboxError(Exception):
    """Raised when a tool call would touch a path outside the audit's checkout."""


def _cache_path(cache_dir: Path, tool: str, args: tuple) -> Path:
    key = hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()
    d = cache_dir / tool
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{key}.json"


def _cached(cache_dir: Path | None, tool: str, args: tuple, compute):
    if cache_dir is None:
        return compute()
    path = _cache_path(cache_dir, tool, args)
    if path.exists():
        return json.loads(path.read_text())
    result = compute()
    path.write_text(json.dumps(result))
    return result


def _assert_within(path: Path, sandbox_root: Path) -> Path:
    resolved = path.resolve()
    root = sandbox_root.resolve()
    if root != resolved and root not in resolved.parents:
        raise SandboxError(f"{path} is outside sandbox root {sandbox_root}")
    return resolved


class InvestigationTools:
    """Bound to one audit's ProgramGraph + checkout dir; every method is
    sandboxed to `checkout_dir` and cached under `cache_dir` (if given).
    """

    def __init__(self, pg: ProgramGraph, checkout_dir: Path, cache_dir: Path | None = None):
        self.pg = pg
        self.checkout_dir = Path(checkout_dir)
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.bundle_builder = BundleBuilder(pg)

    def graph_query(self, node: str, relation: str, direction: str = "out") -> list[str]:
        def compute():
            return self.pg.neighbors_by_kind(node, relation, direction=direction)
        return _cached(self.cache_dir, "graph_query", (node, relation, direction), compute)

    def expand_bundle(self, node: str, hops: int = 1) -> dict:
        def compute():
            bundle = self.bundle_builder.expand(node, hops=hops)
            return {
                "seed": bundle.seed,
                "contract": bundle.contract,
                "contract_summary": bundle.contract_summary,
                "inherited_defs": bundle.inherited_defs,
                "modifiers": bundle.modifiers,
                "state_vars": bundle.state_vars,
                "callers": bundle.callers,
                "callees": bundle.callees,
                "external_interactions": bundle.external_interactions,
                "write_after_external_call_vars": bundle.write_after_external_call_vars,
                "source_excerpts": {
                    k: numbered_source(v, bundle.source_excerpt_start_lines.get(k, 1))
                    for k, v in bundle.source_excerpts.items()
                },
            }
        return _cached(self.cache_dir, "expand_bundle", (node, hops), compute)

    def read_file(self, path: str, start_line: int | None = None, end_line: int | None = None) -> str:
        target = _assert_within(Path(path), self.checkout_dir)

        def compute():
            lines = target.read_text(errors="ignore").splitlines()
            s = (start_line or 1) - 1
            e = end_line or len(lines)
            return "\n".join(lines[s:e])
        return _cached(self.cache_dir, "read_file", (str(target), start_line, end_line), compute)

    def grep(self, pattern: str, path: str | None = None) -> list[str]:
        search_root = _assert_within(Path(path), self.checkout_dir) if path else self.checkout_dir

        def compute():
            proc = subprocess.run(
                ["grep", "-rn", "--include=*.sol", pattern, str(search_root)],
                capture_output=True, text=True, timeout=30,
            )
            return proc.stdout.splitlines()
        return _cached(self.cache_dir, "grep", (pattern, str(search_root)), compute)

    def slither_detector(self, name: str, contract_path: str) -> dict:
        target = _assert_within(Path(contract_path), self.checkout_dir)

        def compute():
            proc = subprocess.run(
                ["slither", str(target), "--detect", name, "--json", "-"],
                capture_output=True, text=True, timeout=120,
            )
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError:
                return {"error": proc.stderr[-2000:], "returncode": proc.returncode}
        return _cached(self.cache_dir, "slither_detector", (name, str(target)), compute)


def _main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="tool", required=True)

    p = sub.add_parser("graph_query")
    p.add_argument("node")
    p.add_argument("relation")
    p.add_argument("--direction", default="out")

    p = sub.add_parser("expand_bundle")
    p.add_argument("node")
    p.add_argument("--hops", type=int, default=1)

    p = sub.add_parser("read_file")
    p.add_argument("path")
    p.add_argument("--start-line", type=int, default=None)
    p.add_argument("--end-line", type=int, default=None)

    p = sub.add_parser("grep")
    p.add_argument("pattern")
    p.add_argument("--path", default=None)

    p = sub.add_parser("slither_detector")
    p.add_argument("name")
    p.add_argument("contract_path")

    parser.add_argument("--graph", required=True, help="path to a pickled ProgramGraph (see auditor.py)")
    parser.add_argument("--checkout", required=True)
    parser.add_argument("--cache", default=None)

    args = parser.parse_args()
    import pickle
    with open(args.graph, "rb") as f:
        pg = pickle.load(f)
    tools = InvestigationTools(pg, Path(args.checkout), Path(args.cache) if args.cache else None)

    if args.tool == "graph_query":
        result = tools.graph_query(args.node, args.relation, direction=args.direction)
    elif args.tool == "expand_bundle":
        result = tools.expand_bundle(args.node, hops=args.hops)
    elif args.tool == "read_file":
        result = tools.read_file(args.path, args.start_line, args.end_line)
    elif args.tool == "grep":
        result = tools.grep(args.pattern, args.path)
    elif args.tool == "slither_detector":
        result = tools.slither_detector(args.name, args.contract_path)
    else:
        parser.error(f"unknown tool {args.tool}")
        return

    json.dump(result, sys.stdout, indent=2)


if __name__ == "__main__":
    _main()
