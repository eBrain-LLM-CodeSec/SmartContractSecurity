import gc
from pathlib import Path

import networkx as nx

from a4v.graph import ProgramGraph
from scripts.mgpr.citation_resolution import (
    CitationOutcome,
    extract_citations,
    is_in_scope_repository,
    parse_citation,
    path_in_compiled_graph,
    resolve_citation,
    resolve_citation_string,
)


def _graph_with_function(node_id: str, file: str, lines: list[int]) -> ProgramGraph:
    g = nx.MultiDiGraph()
    g.add_node(node_id, kind="function", name=node_id.split("::")[-1], file=file, lines=lines)
    return ProgramGraph(g, slither=None)


# --- extraction --------------------------------------------------------------


def test_extract_citations_finds_github_blob_and_relative_markdown():
    text = (
        "See https://github.com/org/repo/blob/main/src/Vault.sol#L10-L20 "
        "and also [FeeAMM.sol - burn()](contracts/FeeAMM.sol#L188-L220)."
    )
    citations = extract_citations(text)
    assert "https://github.com/org/repo/blob/main/src/Vault.sol#L10-L20" in citations
    assert "[FeeAMM.sol - burn()](contracts/FeeAMM.sol#L188-L220)" in citations
    assert len(citations) == 2


def test_extract_citations_deduplicates_and_sorts():
    text = "dup: https://github.com/org/repo/blob/deadbeef/src/A.sol#L1 " * 2
    assert extract_citations(text) == ["https://github.com/org/repo/blob/deadbeef/src/A.sol#L1"]


def test_citation_free_finding_extracts_nothing():
    """Requirement #11: a genuinely citation-free finding must not produce
    an invented match."""
    text = "The mint() function has no access control check. No links here."
    assert extract_citations(text) == []


# --- parse_citation ------------------------------------------------------


def test_parse_citation_sha_url_is_ref_kind_sha():
    parsed = parse_citation("https://github.com/org/repo/blob/deadbeef1234/src/Vault.sol#L10-L20")
    assert parsed.format == "github_blob"
    assert parsed.owner == "org" and parsed.repo == "repo"
    assert parsed.ref == "deadbeef1234" and parsed.ref_kind == "sha"
    assert parsed.path == "src/Vault.sol" and parsed.start == 10 and parsed.end == 20


def test_parse_citation_main_branch_url_is_ref_kind_branch():
    """Requirement: root cause #1 fix -- `blob/main/...` must resolve, not
    be silently rejected because `main` isn't hex."""
    parsed = parse_citation("https://github.com/code-423n4/2024-04-noya/blob/main/contracts/A.sol#L428")
    assert parsed.format == "github_blob"
    assert parsed.ref == "main" and parsed.ref_kind == "branch"


def test_parse_citation_master_branch_url_is_ref_kind_branch():
    parsed = parse_citation("https://github.com/etherfi-protocol/smart-contracts/blob/master/src/LiquidityPool.sol#L529")
    assert parsed.format == "github_blob"
    assert parsed.ref == "master" and parsed.ref_kind == "branch"


def test_parse_citation_nonstandard_branch_name():
    """Do not assume branch names are limited to main/master."""
    parsed = parse_citation("https://github.com/org/repo/blob/release-2.0/src/Vault.sol#L5")
    assert parsed.format == "github_blob"
    assert parsed.ref == "release-2.0" and parsed.ref_kind == "branch"


def test_parse_citation_relative_markdown_single_line():
    parsed = parse_citation("[StablecoinDEX.sol - cancel()](contracts/StablecoinDEX.sol#L234)")
    assert parsed.format == "relative_markdown"
    assert parsed.owner is None and parsed.repo is None
    assert parsed.path == "contracts/StablecoinDEX.sol"
    assert parsed.start == 234 and parsed.end == 234


def test_parse_citation_relative_markdown_line_range():
    parsed = parse_citation("[FeeAMM.sol - burn() function](contracts/FeeAMM.sol#L188-L220)")
    assert parsed.format == "relative_markdown"
    assert parsed.path == "contracts/FeeAMM.sol"
    assert parsed.start == 188 and parsed.end == 220


def test_parse_citation_malformed_returns_none():
    assert parse_citation("this is not a citation at all") is None
    assert parse_citation("https://example.com/not-github#L1") is None


# --- is_in_scope_repository ------------------------------------------------


def test_in_scope_repository_exact_slug_match():
    assert is_in_scope_repository("code-423n4", "2024-07-benddao", "2024-07-benddao") is True


def test_in_scope_repository_slug_is_substring_of_longer_repo_name():
    """Real example: 2025-04-virtuals audits self-cite
    `code-423n4/2025-04-virtuals-protocol`, not the exact audit_id."""
    assert is_in_scope_repository("code-423n4", "2025-04-virtuals-protocol", "2025-04-virtuals") is True


def test_external_dependency_repository_is_out_of_scope():
    """Real examples: 2024-01-curves citing Vectorized/solady,
    2024-04-noya citing pendle-finance/pendle-core-v2-public."""
    assert is_in_scope_repository("Vectorized", "solady", "2024-01-curves") is False
    assert is_in_scope_repository("pendle-finance", "pendle-core-v2-public", "2024-04-noya") is False


# --- resolve_citation_string: full pipeline, one test per outcome ----------


def test_resolves_sha_url_to_covering_function(tmp_path):
    audit_id = "2024-01-example"
    checkout_root, run_cmd_dir = tmp_path, "."
    f = str((tmp_path / "src" / "Vault.sol"))
    Path(f).parent.mkdir(parents=True)
    Path(f).write_text("placeholder\n" * 50)
    pg = _graph_with_function("fn::Vault.withdraw()", f, [10, 20])

    res = resolve_citation_string(
        "https://github.com/org/2024-01-example/blob/deadbeef1234/src/Vault.sol#L10-L20",
        audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
    )
    assert res.outcome is CitationOutcome.RESOLVED
    assert res.routing_units == ["fn::Vault.withdraw()"]
    assert res.parser_format == "github_blob" and res.ref_kind == "sha"


def test_resolves_main_branch_url_to_covering_function(tmp_path):
    """Requirement: previously-rejected branch-name citations must now
    resolve end-to-end, not just parse."""
    audit_id = "2024-04-noya"
    checkout_root, run_cmd_dir = tmp_path, "."
    f = str(tmp_path / "contracts" / "A.sol")
    Path(f).parent.mkdir(parents=True)
    Path(f).write_text("placeholder\n" * 500)
    pg = _graph_with_function("fn::AccountingManager.executeWithdraw()", f, [420, 440])

    res = resolve_citation_string(
        "https://github.com/code-423n4/2024-04-noya/blob/main/contracts/A.sol#L428",
        audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
    )
    assert res.outcome is CitationOutcome.RESOLVED
    assert res.routing_units == ["fn::AccountingManager.executeWithdraw()"]
    assert res.ref_kind == "branch"


def test_resolves_relative_markdown_single_line(tmp_path):
    audit_id = "2026-01-tempo-feeamm"
    checkout_root, run_cmd_dir = tmp_path, "."
    f = str(tmp_path / "contracts" / "FeeAMM.sol")
    Path(f).parent.mkdir(parents=True)
    Path(f).write_text("placeholder\n" * 300)
    pg = _graph_with_function("fn::FeeAMM.burn()", f, [188, 220])

    res = resolve_citation_string(
        "[FeeAMM.sol - burn() function](contracts/FeeAMM.sol#L200)",
        audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
    )
    assert res.outcome is CitationOutcome.RESOLVED
    assert res.parser_format == "relative_markdown"
    assert res.repo_identity is None  # no owner/repo in a relative link
    assert res.routing_units == ["fn::FeeAMM.burn()"]


def test_resolves_relative_markdown_line_range(tmp_path):
    audit_id = "2026-01-tempo-feeamm"
    checkout_root, run_cmd_dir = tmp_path, "."
    f = str(tmp_path / "contracts" / "FeeAMM.sol")
    Path(f).parent.mkdir(parents=True)
    Path(f).write_text("placeholder\n" * 300)
    pg = _graph_with_function("fn::FeeAMM.burn()", f, [188, 220])

    res = resolve_citation_string(
        "[FeeAMM.sol - burn() function](contracts/FeeAMM.sol#L188-L220)",
        audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
    )
    assert res.outcome is CitationOutcome.RESOLVED
    assert res.start == 188 and res.end == 220
    assert res.routing_units == ["fn::FeeAMM.burn()"]


def test_external_repository_citation_is_not_treated_as_span_miss(tmp_path):
    """Root cause #3: a citation to an out-of-scope dependency repo must be
    classified EXTERNAL_REPOSITORY_CITATION, not (misleadingly)
    NO_FUNCTION_SPAN_COVERS_LOCATION."""
    audit_id = "2024-01-curves"
    checkout_root, run_cmd_dir = tmp_path, "."
    pg = _graph_with_function("fn::Curves.buy()", str(tmp_path / "contracts" / "Curves.sol"), [1, 10])

    res = resolve_citation_string(
        "https://github.com/Vectorized/solady/blob/61612f187debb7affbe109543556666ef716ef69/src/utils/SafeTransferLib.sol#L117",
        audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
    )
    assert res.outcome is CitationOutcome.EXTERNAL_REPOSITORY_CITATION
    assert res.repo_identity == "Vectorized/solady"
    assert res.routing_units == []


def test_self_citation_to_differently_named_submodule_repo_still_resolves(tmp_path):
    """Regression guard: 2023-07-pooltogether's own Scope table lists
    `Vault.sol` as in-scope, but its real upstream repo is
    `GenerationSoftware/pt-v5-vault` (a git submodule pulled into the
    audited monorepo) -- nothing about that repo name relates to the
    audit_id string at all. Compiled-graph membership must win over the
    repo-identity heuristic: since the file genuinely compiled, this must
    resolve normally, not be misclassified EXTERNAL_REPOSITORY_CITATION.
    (Confirmed live: an earlier ordering of these two checks caused this
    exact finding to regress from resolved to unresolved.)"""
    audit_id = "2023-07-pooltogether"
    checkout_root, run_cmd_dir = tmp_path, "."
    f = str(tmp_path / "src" / "Vault.sol")
    Path(f).parent.mkdir(parents=True)
    Path(f).write_text("placeholder\n" * 1200)
    pg = _graph_with_function("fn::Vault.mintYieldFee(uint256,address)", f, [394, 402])

    res = resolve_citation_string(
        "https://github.com/GenerationSoftware/pt-v5-vault/blob/"
        "b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L394-L402",
        audit_id=audit_id, checkout_root=checkout_root, run_cmd_dir=run_cmd_dir, pg=pg,
    )
    assert res.outcome is CitationOutcome.RESOLVED
    assert res.routing_units == ["fn::Vault.mintYieldFee(uint256,address)"]


def test_malformed_citation_is_unsupported_format(tmp_path):
    pg = _graph_with_function("fn::A.f()", str(tmp_path / "A.sol"), [1, 10])
    res = resolve_citation_string(
        "not a citation at all", audit_id="2024-01-example",
        checkout_root=tmp_path, run_cmd_dir=".", pg=pg,
    )
    assert res.outcome is CitationOutcome.UNSUPPORTED_CITATION_FORMAT
    assert res.parser_format is None


def test_path_traversal_outside_audited_repo_is_rejected(tmp_path):
    """Requirement: reject unsafe path traversal outside the audited repo."""
    pg = _graph_with_function("fn::A.f()", str(tmp_path / "A.sol"), [1, 10])
    res = resolve_citation_string(
        "[evil](../../../../etc/malicious.sol#L1)", audit_id="2024-01-example",
        checkout_root=tmp_path, run_cmd_dir="src", pg=pg,
    )
    assert res.outcome is CitationOutcome.UNSUPPORTED_CITATION_FORMAT
    assert "outside the audited repository" in res.detail


def test_path_not_in_compiled_graph(tmp_path):
    """An in-scope citation whose file was never compiled at all (e.g.
    build-excluded, or a submodule that wasn't initialized) -- distinct
    from a file that compiled but whose specific span isn't a function."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "NotCompiled.sol").write_text("placeholder\n" * 20)
    pg = _graph_with_function("fn::Other.f()", str(tmp_path / "src" / "Other.sol"), [1, 10])

    res = resolve_citation_string(
        "https://github.com/org/2024-01-example/blob/main/src/NotCompiled.sol#L5",
        audit_id="2024-01-example", checkout_root=tmp_path, run_cmd_dir=".", pg=pg,
    )
    assert res.outcome is CitationOutcome.PATH_NOT_IN_COMPILED_GRAPH


def test_valid_citation_path_exists_but_no_function_span_covers_it(tmp_path):
    """The file IS part of the compiled graph, but the cited line range
    falls outside every function's span (e.g. a state-variable
    declaration)."""
    f = str(tmp_path / "src" / "Vault.sol")
    Path(f).parent.mkdir(parents=True)
    Path(f).write_text("placeholder\n" * 50)
    pg = _graph_with_function("fn::Vault.withdraw()", f, [30, 40])

    res = resolve_citation_string(
        "https://github.com/org/2024-01-example/blob/main/src/Vault.sol#L1-L2",
        audit_id="2024-01-example", checkout_root=tmp_path, run_cmd_dir=".", pg=pg,
    )
    assert res.outcome is CitationOutcome.NO_FUNCTION_SPAN_COVERS_LOCATION
    assert res.normalized_path == f


# --- backward-compatible resolve_citation() shim ---------------------------


def test_legacy_resolve_citation_now_accepts_branch_names():
    """The old thin parse+join helper is kept for simple callers, and is
    itself fixed by the same underlying regex broadening."""
    result = resolve_citation(
        "https://github.com/org/repo/blob/main/src/Vault.sol#L10-L20",
        checkout_root=Path("/checkouts/audit-1"), run_cmd_dir="vault",
    )
    assert result == (Path("/checkouts/audit-1/vault/src/Vault.sol"), 10, 20)


def test_legacy_resolve_citation_still_rejects_non_matching_url():
    assert resolve_citation("https://example.com/not-github", Path("/x"), ".") is None


def test_legacy_resolve_citation_does_not_handle_relative_markdown():
    """Documented limitation of the backward-compat shim -- only the full
    resolve_citation_string() pipeline handles relative Markdown links."""
    assert resolve_citation(
        "[FeeAMM.sol - burn()](contracts/FeeAMM.sol#L188-L220)", Path("/x"), ".",
    ) is None


# --- compiled-file cache does not leak across audits -----------------------


def test_compiled_file_cache_does_not_cross_contaminate_distinct_graphs(tmp_path):
    """Regression guard: a long-running batch (e.g. run_full_study_batch.py)
    rebinds its `pg` local every loop iteration, making the previous
    audit's ProgramGraph immediately GC-eligible under CPython's
    refcounting -- a plain id(pg)-keyed cache risks id() reuse silently
    serving a stale, wrong-audit file set to the next audit. The cache
    must be scoped per live object (a WeakKeyDictionary), not per id()."""
    only_in_one = str(tmp_path / "OnlyInGraphOne.sol")
    only_in_two = str(tmp_path / "OnlyInGraphTwo.sol")
    Path(only_in_one).write_text("x\n")
    Path(only_in_two).write_text("x\n")

    pg_one = _graph_with_function("fn::A.f()", only_in_one, [1, 5])
    pg_two = _graph_with_function("fn::B.g()", only_in_two, [1, 5])

    assert path_in_compiled_graph(pg_one, Path(only_in_one)) is True
    assert path_in_compiled_graph(pg_one, Path(only_in_two)) is False
    assert path_in_compiled_graph(pg_two, Path(only_in_two)) is True
    assert path_in_compiled_graph(pg_two, Path(only_in_one)) is False


def test_compiled_file_cache_entry_is_released_after_graph_is_collected(tmp_path):
    f = str(tmp_path / "Vault.sol")
    Path(f).write_text("x\n")
    pg = _graph_with_function("fn::Vault.f()", f, [1, 5])
    path_in_compiled_graph(pg, Path(f))  # populate the cache

    from scripts.mgpr.citation_resolution import _compiled_file_cache
    assert len(_compiled_file_cache) >= 1
    del pg
    gc.collect()
    assert len(_compiled_file_cache) == 0
