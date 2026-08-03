"""Tests for scripts.mgpr.family_classification -- the deterministic,
auditable replacement for the old broad-substring `assign_expected_family`
heuristic. Required test list items 1-10 (see task spec) plus supporting
coverage for the cleaning/denylist machinery."""
from scripts.mgpr.family_classification import FamilyOutcome, classify_family


# --- required test 1-3: defensive reentrancy-guard identifiers -------------


def test_nonreentrant_inside_code_does_not_classify_as_p2():
    full_text = (
        "The function is protected by the `nonReentrant` modifier but still "
        "loses funds due to an unrelated rounding bug in the fee split."
    )
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is not FamilyOutcome.P2_REENTRANCY


def test_noreentrant_does_not_classify_as_p2():
    full_text = "```solidity\nmodifier noReentrant() { ... }\n```\nThe fee accounting rounds down every call."
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is not FamilyOutcome.P2_REENTRANCY


def test_reentrancylock_does_not_classify_as_p2():
    full_text = (
        "```solidity\nmodifier reentrancyLock() { require(!locked); locked = true; _; locked = false; }\n```\n"
        "Signature replay allows an attacker to reuse an old claim message twice."
    )
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is not FamilyOutcome.P2_REENTRANCY


# --- required test 4: genuine reentrancy title -----------------------------


def test_genuine_reentrancy_title_classifies_as_p2():
    result = classify_family(
        title="Reentrancy in Vault.withdraw allows draining the pool", description=None, full_text=None,
    )
    assert result.outcome is FamilyOutcome.P2_REENTRANCY
    assert result.source_field == "title"
    assert result.confidence == "strong"


# --- required test 5: "casting votes" does not classify as P5 --------------


def test_casting_votes_does_not_classify_as_p5():
    full_text = (
        "A malicious delegate can gain influence over governance outcomes without actually "
        "casting votes, by exploiting the delegation-weight snapshot timing."
    )
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is not FamilyOutcome.P5_ARITHMETIC_PRECISION


# --- required test 6: genuine narrowing-cast finding classifies as P5 ------


def test_genuine_narrowing_cast_classifies_as_p5():
    full_text = "The vault performs a narrowing cast from uint256 to uint96 when burning shares, silently truncating large balances."
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is FamilyOutcome.P5_ARITHMETIC_PRECISION
    assert result.confidence == "strong"


# --- required test 7: genuine authorization issue classifies as P1 --------


def test_genuine_authorization_issue_classifies_as_p1():
    full_text = "sellCreditMarket() lacks authorization: any user can call it and steal another lender's credit."
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is FamilyOutcome.P1_AUTHORIZATION
    assert result.confidence == "strong"


# --- required test 8: unrelated finding becomes NOT_APPLICABLE ------------


def test_unrelated_finding_becomes_not_applicable():
    result = classify_family(
        title="Gas griefing via unbounded loop", description="Excess gas consumption in a loop over an unbounded array",
        full_text="No relevant keywords here at all, purely a denial-of-service-via-gas concern.",
    )
    assert result.outcome is FamilyOutcome.NOT_APPLICABLE
    assert result.confidence == "none"


# --- required test 9: an unclear finding becomes UNCERTAIN -----------------


def test_unclear_finding_becomes_uncertain_not_forced():
    # Only the generic, ambiguous word "authorization" appears, with no
    # compound evidence of an actual missing-check mechanism -- must not be
    # forced into P1.
    full_text = "The design around authorization in this module could be clearer, though nothing concrete was found."
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is FamilyOutcome.UNCERTAIN
    assert result.confidence == "weak"


def test_uncertain_generic_precision_word_alone_not_forced_into_p5():
    full_text = "The precision of the off-chain oracle feed is a general design concern worth revisiting."
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is FamilyOutcome.UNCERTAIN


def test_generic_call_word_alone_not_forced_into_p1():
    # "call" alone (no compound access-control phrase) must never assign
    # P1_AUTHORIZATION -- it is deliberately excluded even from the weak
    # list (see module comment), since it is far too generic in
    # smart-contract prose to carry any signal at all; the required
    # protection is simply that it never causes P1_AUTHORIZATION.
    full_text = "The external call graph of this module is complex and hard to audit."
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is not FamilyOutcome.P1_AUTHORIZATION


# --- required test 10: fenced code is excluded from classification --------


def test_fenced_code_excluded_from_classification():
    full_text = (
        "```solidity\n"
        "// this comment mentions reentrancy and downcast and unauthorized just to poison naive matching\n"
        "```\n"
        "The actual bug here is an unbounded loop causing gas griefing, nothing else."
    )
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is FamilyOutcome.NOT_APPLICABLE


def test_inline_code_excluded_from_classification():
    full_text = "The `nonReentrant` guard is present. Separately, `castVote()` is called during snapshotting."
    result = classify_family(title=None, description=None, full_text=full_text)
    # inline code stripped entirely -- neither the modifier name nor the
    # unrelated `castVote()` function name should surface as evidence at all
    assert result.outcome is FamilyOutcome.NOT_APPLICABLE


def test_mitigation_section_excluded_from_classification():
    full_text = (
        "The function has a subtle off-by-one in a loop bound, unrelated to any of the three families.\n\n"
        "Recommended Mitigation\n"
        "Add a nonReentrant modifier and validate authorization before the narrowing cast to uint96.\n"
    )
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is FamilyOutcome.NOT_APPLICABLE


# --- title/description priority ---------------------------------------------


def test_title_takes_priority_over_conflicting_body_evidence():
    result = classify_family(
        title="Reentrancy in Vault.withdraw",
        description=None,
        full_text="Also mentions a narrowing cast to uint96 elsewhere, unrelated to the title's issue.",
    )
    assert result.outcome is FamilyOutcome.P2_REENTRANCY
    assert result.source_field == "title"


# --- excluded_matches bookkeeping -------------------------------------------


def test_excluded_matches_recorded_for_denylisted_reentrancy_identifier():
    full_text = "Protected by `reentrancyLock` (irrelevant); the real issue is a missing role check letting anyone call pause()."
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is FamilyOutcome.P1_AUTHORIZATION
    # note: reentrancyLock is inside inline code here so it's stripped by
    # code-removal before the denylist even runs -- use a non-code mention
    # to actually exercise the denylist-recording path:
    full_text_2 = "The reentrancyLock variable is set but the real issue is a missing role check letting anyone call pause()."
    result2 = classify_family(title=None, description=None, full_text=full_text_2)
    assert result2.outcome is FamilyOutcome.P1_AUTHORIZATION
    assert any(m.rule == "defensive_reentrancy_identifier" for m in result2.excluded_matches)


def test_excluded_matches_recorded_for_casting_votes_phrase():
    full_text = "Without actually casting votes, a delegate can still swing the outcome -- a missing role check lets anyone call finalize()."
    result = classify_family(title=None, description=None, full_text=full_text)
    assert result.outcome is FamilyOutcome.P1_AUTHORIZATION
    assert any(m.rule == "casting_votes_governance_phrase" for m in result.excluded_matches)
