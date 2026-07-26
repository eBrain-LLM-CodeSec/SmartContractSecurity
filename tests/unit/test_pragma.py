import pytest

from a4v.gnn.etl.pragma import (
    UnparsablePragma,
    pick_lowest_minor_newest_patch,
    pragma_to_specifiers,
    resolve_solc_version,
    satisfying_versions,
)

AVAILABLE = [
    "0.4.24", "0.4.25", "0.4.26",
    "0.5.16", "0.5.17",
    "0.6.11", "0.6.12",
    "0.7.6",
    "0.8.4", "0.8.17", "0.8.19", "0.8.20", "0.8.21",
]


def test_caret_pragma_resolves_to_lowest_minor_newest_patch():
    res = resolve_solc_version(["^0.8.0"], AVAILABLE)
    assert not res.unresolved
    assert res.resolved_version == "0.8.21"  # only 0.8.x band satisfies ^0.8.0
    assert res.reason == "lowest_satisfying_minor_newest_patch"


def test_range_pragma_picks_lowest_band_not_lowest_overall():
    # satisfies 0.5.x, 0.6.x, 0.7.x -- must pick the *lowest band* (0.5.x)
    # newest patch (0.5.17), not the single oldest overall version (0.5.16).
    res = resolve_solc_version([">=0.5.0 <0.8.0"], AVAILABLE)
    assert res.resolved_version == "0.5.17"


def test_exact_version_from_metadata_overrides_pragma():
    res = resolve_solc_version(["^0.8.0"], AVAILABLE, exact_version="0.7.6")
    assert res.resolved_version == "0.7.6"
    assert res.exact_version_used
    assert res.reason == "exact_version_from_metadata"


def test_pragma_less_contract_is_unresolved_not_guessed():
    res = resolve_solc_version([], AVAILABLE)
    assert res.unresolved
    assert res.resolved_version is None
    assert res.reason == "no_pragma_no_fallback_ladder"


def test_unsatisfiable_pragma_is_unresolved():
    res = resolve_solc_version(["^0.3.0"], AVAILABLE)
    assert res.unresolved
    assert res.resolved_version is None
    assert res.reason == "no_available_version_satisfies_pragma"
    assert res.candidates_considered == []


def test_or_combined_pragma():
    versions = satisfying_versions([">=0.4.24 <0.5.0 || >=0.8.0 <0.9.0"], AVAILABLE)
    assert "0.4.24" in versions
    assert "0.8.21" in versions
    assert "0.6.11" not in versions


def test_multiple_pragma_exprs_are_and_combined():
    # one file constrains ^0.8.0, another (imported) constrains >=0.8.17 --
    # only versions satisfying both should show up.
    versions = satisfying_versions(["^0.8.0", ">=0.8.17"], AVAILABLE)
    assert versions == ["0.8.17", "0.8.19", "0.8.20", "0.8.21"]


def test_bare_version_is_exact_match():
    versions = satisfying_versions(["0.8.4"], AVAILABLE)
    assert versions == ["0.8.4"]


def test_pick_lowest_minor_newest_patch_helper():
    assert pick_lowest_minor_newest_patch(["0.8.17", "0.8.20", "0.7.6"]) == "0.7.6"
    assert pick_lowest_minor_newest_patch([]) is None


def test_unparsable_pragma_raises():
    with pytest.raises(UnparsablePragma):
        pragma_to_specifiers("not a version")


def test_pragma_less_without_fallback_is_still_unresolved_by_default():
    # No fallback passed -- original "no arbitrary ladder" behavior preserved.
    res = resolve_solc_version([], AVAILABLE)
    assert res.unresolved
    assert res.candidates_to_try == []


def test_pragma_less_evidence_based_fallback_is_opt_in():
    res = resolve_solc_version([], AVAILABLE, pragma_less_fallback=["0.4.24", "0.8.17", "0.8.20"])
    assert not res.unresolved
    assert res.resolved_version == "0.4.24"
    assert res.reason == "pragma_less_evidence_based_fallback"
    assert res.candidates_to_try == ["0.4.24", "0.8.17", "0.8.20"]


def test_pragma_less_fallback_filters_to_available_versions_only():
    res = resolve_solc_version([], AVAILABLE, pragma_less_fallback=["0.4.99", "0.4.24", "0.8.20"])
    assert res.candidates_to_try == ["0.4.24", "0.8.20"]


def test_pragma_less_fallback_with_no_available_match_still_unresolved():
    res = resolve_solc_version([], AVAILABLE, pragma_less_fallback=["0.3.1"])
    assert res.unresolved
    assert res.reason == "no_pragma_no_fallback_ladder"


def test_normal_paths_have_single_candidate_to_try_not_a_ladder():
    res_exact = resolve_solc_version(["^0.8.0"], AVAILABLE, exact_version="0.7.6")
    assert res_exact.candidates_to_try == ["0.7.6"]
    res_pragma = resolve_solc_version(["^0.8.0"], AVAILABLE)
    assert res_pragma.candidates_to_try == ["0.8.21"]
