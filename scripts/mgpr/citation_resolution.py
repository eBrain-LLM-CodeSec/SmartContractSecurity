"""Deterministic citation extraction and resolution for the MGPR feasibility
study (used by `build_registry.py` at extraction time and by
`run_feasibility_study.py` at resolution time).

This is evaluation-methodology code -- it decides which finding cites which
compiled function node for the STUDY's own ground-truth bookkeeping. It has
no effect on MGPR's actual routing/gate/context behavior
(`a4v/mgpr/*.py`), which reads compiled-graph structural signals only and
never looks at a finding's citation text.

Two citation formats are supported:

  - Full GitHub blob links: `https://github.com/<owner>/<repo>/blob/<ref>/
    <path>#L<start>(-L<end>)?`, where `<ref>` may be a commit SHA *or* a
    branch name (e.g. `main`, `master`, or anything else without a literal
    `/` in it -- refs containing `/`, like `release/1.0`, are not
    supported, since a generic regex cannot distinguish a slash-containing
    ref from the start of the file path without querying GitHub itself,
    which this deterministic parser deliberately does not do).
  - Relative Markdown "Code Location" links: `[text](relative/path.sol#L10
    -L20)`, used systematically by the `2026-01-tempo-*` audits instead of
    full GitHub URLs. Resolved relative to the audited checkout's own
    `checkout_root / run_cmd_dir`, with path-traversal outside that root
    rejected.

No semantic or function-name-inference matching is added: a finding that
only mentions a function in prose, with no citation matching either
pattern above, remains unresolved (`NO_CITATION` at the finding level, or
this module simply never produces a match for it during extraction).
"""
from __future__ import annotations

import re
import weakref
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from a4v.graph import FUNCTION, ProgramGraph

# --- extraction --------------------------------------------------------------

# owner/repo/ref/path all exclude whitespace and markdown-link delimiters
# (`)`/`]`) so a citation embedded in `[text](https://github.com/...)` is
# bounded correctly at the closing paren; `ref` is any non-slash token, not
# just a hex SHA -- this is the fix for root cause #1 (branch-name citations
# like `blob/main/...`/`blob/master/...` were previously rejected outright).
_GITHUB_BLOB_RE = re.compile(
    r"https://github\.com/(?P<owner>[^/\s\)\]]+)/(?P<repo>[^/\s\)\]]+)/blob/"
    r"(?P<ref>[^/\s\)\]]+)/(?P<path>[^\s\)\]#]+)#L(?P<start>\d+)(?:-L(?P<end>\d+))?"
)

# `[any text](relative/path.sol#L10-L20)` -- the path must not itself look
# like a URL (so this never double-matches a markdown-wrapped GitHub link)
# and must end in `.sol` before the line fragment. Not gated on appearing
# under a "Code Location" heading specifically: several audits use this
# link shape without that exact heading, and requiring it would just drop
# real citations for no resolution benefit.
_RELATIVE_CODE_LINK_RE = re.compile(
    r"\[[^\]]*\]\((?P<path>(?!https?://)[^\s\)#]+\.sol)#L(?P<start>\d+)(?:-L(?P<end>\d+))?\)"
)

_SHA_RE = re.compile(r"[0-9a-fA-F]{7,40}")  # git's minimum short-SHA length


def extract_citations(full_text: str) -> list[str]:
    """Every citation substring in `full_text` matching either supported
    format, deduplicated and sorted (matches the previous extractor's
    dedup/sort behavior in build_registry.py, now over a broader set of
    formats)."""
    matches = {m.group(0) for m in _GITHUB_BLOB_RE.finditer(full_text)}
    matches |= {m.group(0) for m in _RELATIVE_CODE_LINK_RE.finditer(full_text)}
    return sorted(matches)


# --- parsing -------------------------------------------------------------


@dataclass(frozen=True)
class ParsedCitation:
    raw: str
    format: str  # "github_blob" | "relative_markdown"
    owner: str | None
    repo: str | None
    ref: str | None
    ref_kind: str | None  # "sha" | "branch" | None (None for relative_markdown)
    path: str  # as written in the citation, not yet resolved to a local path
    start: int
    end: int


def _ref_kind(ref: str) -> str:
    return "sha" if _SHA_RE.fullmatch(ref) else "branch"


def parse_citation(raw: str) -> ParsedCitation | None:
    """Parses a single already-extracted citation string. Returns None if
    it matches neither supported format (a malformed/unsupported citation)."""
    m = _GITHUB_BLOB_RE.match(raw)
    if m:
        start = int(m.group("start"))
        end = int(m.group("end") or start)
        ref = m.group("ref")
        return ParsedCitation(
            raw=raw, format="github_blob", owner=m.group("owner"), repo=m.group("repo"),
            ref=ref, ref_kind=_ref_kind(ref), path=m.group("path"), start=start, end=end,
        )
    m = _RELATIVE_CODE_LINK_RE.match(raw)
    if m:
        start = int(m.group("start"))
        end = int(m.group("end") or start)
        return ParsedCitation(
            raw=raw, format="relative_markdown", owner=None, repo=None, ref=None, ref_kind=None,
            path=m.group("path"), start=start, end=end,
        )
    return None


# --- repository-identity validation --------------------------------------

_DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-")


def _project_slug(audit_id: str) -> str:
    return _DATE_PREFIX_RE.sub("", audit_id).lower()


def is_in_scope_repository(owner: str, repo: str, audit_id: str) -> bool:
    """Whether a cited GitHub repo is the audited project itself (or a
    reasonable naming variant of it), as opposed to an external dependency.

    `owner` is recorded on the result for debugging but not enforced here:
    EVMbench audits are sourced from more than one contest-hosting org, and
    this deployment's own compiled checkouts live under yet a third org
    (`evmbench-org/<audit_id>`) that never appears in any finding's own
    citation text -- comparing against the checkout's own git remote would
    therefore always mismatch and cannot be the signal.

    Matching is by project slug (`audit_id` with its `YYYY-MM-` date
    prefix stripped) as a substring of the normalized cited repo name.
    Verified against every real citation sampled during the prior
    root-cause investigation: self-citations for `noya`, `benddao`,
    `curves`, `thorwallet`, `thorchain` (exact-slug repo names) and
    `virtuals` (repo name `virtuals-protocol`, a superset) all match;
    external-dependency citations to `solady`, `pendle-core-v2-public`,
    `smart-contracts` (etherfi), and `lido-dao` all correctly do not.
    This is a documented heuristic, not exact string matching -- unlike
    the span-matching in `find_routing_units_for_citation`, which stays
    exact per this task's own constraint. Short slugs (<4 chars) require
    an exact match instead of substring containment, to avoid spurious
    hits on short, common tokens.
    """
    slug = _project_slug(audit_id)
    normalized_repo = repo.lower()
    if len(slug) < 4:
        return normalized_repo in (slug, audit_id.lower())
    return slug in normalized_repo


# --- path safety -----------------------------------------------------------


def _safe_resolve(checkout_root: Path, run_cmd_dir: str, relative_path: str) -> Path | None:
    """Resolves `relative_path` under `checkout_root/run_cmd_dir`, rejecting
    (returning None for) any path that normalizes outside that root --
    e.g. `../../../etc/passwd`-style traversal in a relative Markdown
    citation."""
    base = (checkout_root / run_cmd_dir).resolve()
    candidate = (base / relative_path).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    return candidate


# --- compiled-graph membership + span matching ------------------------------

# Slither synthesizes these bookkeeping functions on nearly every contract
# that declares state variables, regardless of whether they have inline
# initializers -- not real source-level functions, and their line-span
# attribution is broad enough to spuriously overlap unrelated citations
# (confirmed live: matched multiple, unrelated H-02 citations). Same
# exclusion already established in scripts/etl/build_feasibility_report.py
# for the same reason, applied here independently since that script is for
# the unrelated Messi-Q GNN corpus, not EVMbench audits.
_SLITHER_SYNTHETIC_FUNCTION_NAMES = {"slitherConstructorVariables", "slitherConstructorConstantVariables"}

# Keyed by the ProgramGraph object itself via a WeakKeyDictionary, NOT by
# id(pg): a long-running batch (e.g. run_full_study_batch.py, one process
# looping over 27 audits) rebinds its `pg` local var every iteration, which
# drops the only reference to the previous audit's ProgramGraph and makes
# it immediately eligible for GC under CPython's refcounting -- a plain
# `dict[id(pg), ...]` cache would then risk id() reuse for the NEXT
# audit's ProgramGraph, silently serving a stale, wrong-audit file set. A
# WeakKeyDictionary's entries are removed automatically when their key
# object is actually collected, which happens before that id() could be
# reused for anything else, so this can never cross-contaminate audits.
_compiled_file_cache: "weakref.WeakKeyDictionary[ProgramGraph, set[str]]" = weakref.WeakKeyDictionary()


def _compiled_files(pg: ProgramGraph) -> set[str]:
    cached = _compiled_file_cache.get(pg)
    if cached is not None:
        return cached
    files: set[str] = set()
    for _node_id, data in pg.graph.nodes(data=True):
        node_file = data.get("file")
        if not node_file:
            continue
        try:
            files.add(str(Path(node_file).resolve()))
        except OSError:
            continue
    _compiled_file_cache[pg] = files
    return files


def path_in_compiled_graph(pg: ProgramGraph, local_path: Path) -> bool:
    """Whether `local_path` is the `file` of at least one compiled graph
    node (of any kind) -- distinguishes "this file was never part of the
    build" (PATH_NOT_IN_COMPILED_GRAPH) from "this file compiled, but no
    function's span covers this exact location" (NO_FUNCTION_SPAN_COVERS_LOCATION,
    e.g. a citation pointing at a state-variable declaration)."""
    try:
        resolved = str(local_path.resolve())
    except OSError:
        return False
    return resolved in _compiled_files(pg)


def find_routing_units_for_citation(pg: ProgramGraph, local_path: Path, start: int, end: int) -> list[str]:
    """Function nodes whose own source span overlaps [start, end] in
    local_path. Multiple matches (nested/overlapping functions) or zero
    matches are both real, reportable outcomes, not resolved arbitrarily."""
    matches = []
    for node_id in pg.nodes_of_kind(FUNCTION):
        data = pg.graph.nodes[node_id]
        if data.get("name") in _SLITHER_SYNTHETIC_FUNCTION_NAMES:
            continue
        node_file = data.get("file")
        node_lines = data.get("lines") or []
        if not node_file or not node_lines:
            continue
        try:
            if Path(node_file).resolve() != local_path:
                continue
        except OSError:
            continue
        node_start, node_end = min(node_lines), max(node_lines)
        if node_start <= end and start <= node_end:
            matches.append((node_id, node_end - node_start))
    matches.sort(key=lambda pair: pair[1])  # smallest enclosing span first (most specific)
    return [node_id for node_id, _span in matches]


def location_covered_by_nodes(pg: ProgramGraph, local_path: Path, start: int, end: int,
                               node_ids: set[str]) -> bool:
    for node_id in node_ids:
        if node_id not in pg.graph:
            continue
        data = pg.graph.nodes[node_id]
        node_file, node_lines = data.get("file"), data.get("lines") or []
        if not node_file or not node_lines:
            continue
        try:
            if Path(node_file).resolve() != local_path:
                continue
        except OSError:
            continue
        node_start, node_end = min(node_lines), max(node_lines)
        if node_start <= end and start <= node_end:
            return True
    return False


# --- resolution outcome ---------------------------------------------------


class CitationOutcome(str, Enum):
    RESOLVED = "RESOLVED"
    NO_CITATION = "NO_CITATION"
    UNSUPPORTED_CITATION_FORMAT = "UNSUPPORTED_CITATION_FORMAT"
    EXTERNAL_REPOSITORY_CITATION = "EXTERNAL_REPOSITORY_CITATION"
    PATH_NOT_IN_COMPILED_GRAPH = "PATH_NOT_IN_COMPILED_GRAPH"
    NO_FUNCTION_SPAN_COVERS_LOCATION = "NO_FUNCTION_SPAN_COVERS_LOCATION"


@dataclass(frozen=True)
class CitationResolution:
    outcome: CitationOutcome
    raw: str | None
    parser_format: str | None = None       # "github_blob" | "relative_markdown" | None
    ref_kind: str | None = None            # "sha" | "branch" | None
    repo_identity: str | None = None       # "owner/repo" for github_blob citations, else None
    normalized_path: str | None = None
    start: int | None = None
    end: int | None = None
    routing_units: list[str] = field(default_factory=list)
    detail: str = ""

    def as_dict(self) -> dict:
        return {
            "outcome": self.outcome.value, "raw": self.raw, "parser_format": self.parser_format,
            "ref_kind": self.ref_kind, "repo_identity": self.repo_identity,
            "normalized_path": self.normalized_path, "start": self.start, "end": self.end,
            "routing_units": self.routing_units, "detail": self.detail,
        }


def resolve_citation_string(
    raw: str, *, audit_id: str, checkout_root: Path, run_cmd_dir: str, pg: ProgramGraph,
) -> CitationResolution:
    """Full pipeline for one already-extracted citation string: parse ->
    path-safety check -> compiled-graph membership check -> (only if NOT in
    the compiled graph) repository-identity check, as an explanation for
    *why* -> exact function-span match. Returns exactly one of the six
    CitationOutcome values, with enough detail on the result to debug why.

    Repository identity is deliberately checked AFTER, not before,
    compiled-graph membership: several real audits (e.g.
    `2023-07-pooltogether`) are multi-repo monorepos whose in-scope files
    are pulled in as git submodules from differently-named upstream repos
    (`GenerationSoftware/pt-v5-vault` for that audit's own `Vault.sol`,
    explicitly listed in the audit's own Scope table) -- a real, in-scope,
    genuinely-compiled self-citation whose repo name has no textual
    relation to the audit_id at all. Checking repo identity first would
    reject these as EXTERNAL_REPOSITORY_CITATION even though the cited
    file is sitting right there in the compiled graph -- confirmed live:
    this exact ordering bug caused `2023-07-pooltogether/H-02` and `H-04`
    to regress from resolved to unresolved during this fix's own
    validation rerun. Checking the compiled graph first means a citation
    is only ever explained as "external" when it *actually* isn't part of
    what was compiled, which is the property that actually matters --
    repo-name matching is used solely to pick the more informative of the
    two negative outcomes once non-membership is already established.
    """
    parsed = parse_citation(raw)
    if parsed is None:
        return CitationResolution(
            outcome=CitationOutcome.UNSUPPORTED_CITATION_FORMAT, raw=raw,
            detail="citation text matched neither the GitHub blob#L pattern nor the "
                   "relative Markdown code-location pattern",
        )

    repo_identity = f"{parsed.owner}/{parsed.repo}" if parsed.owner and parsed.repo else None

    local_path = _safe_resolve(checkout_root, run_cmd_dir, parsed.path)
    if local_path is None:
        return CitationResolution(
            outcome=CitationOutcome.UNSUPPORTED_CITATION_FORMAT, raw=raw,
            parser_format=parsed.format, ref_kind=parsed.ref_kind, repo_identity=repo_identity,
            start=parsed.start, end=parsed.end,
            detail=f"resolved path for {parsed.path!r} normalizes outside the audited repository root",
        )

    if not path_in_compiled_graph(pg, local_path):
        if parsed.format == "github_blob" and not is_in_scope_repository(parsed.owner, parsed.repo, audit_id):
            return CitationResolution(
                outcome=CitationOutcome.EXTERNAL_REPOSITORY_CITATION, raw=raw,
                parser_format=parsed.format, ref_kind=parsed.ref_kind, repo_identity=repo_identity,
                normalized_path=str(local_path), start=parsed.start, end=parsed.end,
                detail=f"citation repository {repo_identity!r} does not match audited project "
                       f"{audit_id!r}, and {local_path} is not the file of any compiled graph "
                       f"node -- not treated as an in-scope span miss",
            )
        return CitationResolution(
            outcome=CitationOutcome.PATH_NOT_IN_COMPILED_GRAPH, raw=raw,
            parser_format=parsed.format, ref_kind=parsed.ref_kind, repo_identity=repo_identity,
            normalized_path=str(local_path), start=parsed.start, end=parsed.end,
            detail=f"{local_path} is not the file of any compiled graph node",
        )

    units = find_routing_units_for_citation(pg, local_path, parsed.start, parsed.end)
    if not units:
        return CitationResolution(
            outcome=CitationOutcome.NO_FUNCTION_SPAN_COVERS_LOCATION, raw=raw,
            parser_format=parsed.format, ref_kind=parsed.ref_kind, repo_identity=repo_identity,
            normalized_path=str(local_path), start=parsed.start, end=parsed.end,
            detail=f"no compiled function node's source span covers {local_path}:{parsed.start}-{parsed.end}",
        )

    return CitationResolution(
        outcome=CitationOutcome.RESOLVED, raw=raw,
        parser_format=parsed.format, ref_kind=parsed.ref_kind, repo_identity=repo_identity,
        normalized_path=str(local_path), start=parsed.start, end=parsed.end, routing_units=units,
        detail=f"resolved to {len(units)} routing unit(s)",
    )


# --- backward-compatible thin parser (parse + path-join only) --------------


def resolve_citation(citation_url: str, checkout_root: Path, run_cmd_dir: str) -> tuple[Path, int, int] | None:
    """Legacy-shape helper: parses a GitHub blob citation (branch names now
    accepted, not just hex SHAs -- fixes root cause #1) and joins it to a
    local path, with NO repository-identity validation and NO support for
    relative-Markdown citations. Kept for simple callers/tests that only
    need parse+join; the full pipeline (`_evaluate_finding` et al.) uses
    `resolve_citation_string` instead, which adds both."""
    parsed = parse_citation(citation_url)
    if parsed is None or parsed.format != "github_blob":
        return None
    local_path = (checkout_root / run_cmd_dir / parsed.path).resolve()
    return local_path, parsed.start, parsed.end
