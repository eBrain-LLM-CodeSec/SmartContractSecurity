"""Tests for scripts.benchmark.audit_registry -- the explicit, documented
table of the 27 audits + their subprojects and hand-verified compatibility
overrides, replacing control flow previously buried undocumented inside
run_full_study_batch.py's if/elif chain."""
from scripts.benchmark.audit_registry import AUDIT_IDS, AUDITS, BY_ID


def test_exactly_27_audits():
    assert len(AUDIT_IDS) == 27
    assert len(set(AUDIT_IDS)) == 27  # no duplicates


# --- item 3: multi-subproject audit (thorchain) ---------------------------


def test_thorchain_has_two_distinct_subprojects_with_distinct_roots():
    """Real situation: 2024-06-thorchain is a monorepo with two
    independently-compiled Hardhat projects (ethereum/, avalanche/)."""
    spec = BY_ID["2024-06-thorchain"]
    assert len(spec.subprojects) == 2
    ids = {s.subproject_id for s in spec.subprojects}
    roots = {s.relative_root for s in spec.subprojects}
    assert ids == {"ethereum", "avalanche"}
    assert roots == {"ethereum", "avalanche"}


def test_single_subproject_audits_use_default_id():
    spec = BY_ID["2023-07-pooltogether"]
    assert len(spec.subprojects) == 1
    assert spec.subprojects[0].subproject_id == "default"


# --- item 5/Phase 5: documented compatibility overrides --------------------


def test_foundry_version_overrides_are_isolated_and_documented():
    """Every override must name exactly the one audit it was verified
    against, and carry a non-empty reason -- never a bare, unexplained
    env-var assignment (the state this table replaces)."""
    overridden = [a for a in AUDITS if a.foundry_version_override is not None]
    assert {a.audit_id for a in overridden} == {"2023-12-ethereumcreditguild", "2024-06-size"}
    for a in overridden:
        assert a.override_reason, f"{a.audit_id} has an override with no documented reason"
        assert a.audit_id in a.override_reason or "audit" in a.override_reason.lower()


def test_most_audits_have_no_override():
    """Overrides must stay isolated to the specific audits they were
    verified against, not silently spread to others."""
    non_overridden = [a for a in AUDITS if a.foundry_version_override is None]
    assert len(non_overridden) == 25


# --- item 17: subproject root distinct from audit_id / repo name ----------


def test_subproject_relative_roots_differ_from_audit_id_where_real():
    """Real situations: pooltogether's Foundry project root is `vault/`,
    renft's is `smart-contracts/`, nextgen's is `hardhat/` -- none equal
    to the audit_id itself, confirmed against each audit's own
    audits/<id>/config.yaml `run_cmd_dir`."""
    assert BY_ID["2023-07-pooltogether"].subprojects[0].relative_root == "vault"
    assert BY_ID["2024-01-renft"].subprojects[0].relative_root == "smart-contracts"
    assert BY_ID["2023-10-nextgen"].subprojects[0].relative_root == "hardhat"
