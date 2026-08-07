"""Frozen dataset for the Arm A (bounded LLM) vs. Arm B (Codex-style
investigation agent) experiment. See
BUNDLE_LLM_VS_CODEX_AGENT_PREREGISTRATION.md -- this module and that
document must stay in sync; any change to a bundle here after execution
has begun is a protocol violation for that run.

Every `expected_label` is justified purely from facts stated directly in
that bundle's own fixture files (never from EVMbench ground truth) --
see each dataclass's `label_justification` field. `expected_label = None`
is itself a valid, intentional dataset entry (case 6): genuine
insufficient-evidence is a correct outcome to test for, not a gap in the
dataset.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]  # .../agent4vul/.claude/worktrees/mgpr-router2
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
BUNDLES_DIR = REPO_ROOT / "rtf" / "l2_context_bundles"

# Ephemeral job-scratch checkout (see evmbench/CLAUDE.md's existing
# reproduction steps for 2023-07-pooltogether: git clone, checkout
# 4240445ed3b5145be1032cf1becc9c6866046bf7, `git submodule update --init`
# (NOT --recursive)). Not committed to this repo (not ours to redistribute,
# and 35MB+). If this path doesn't exist when the experiment runs, that is
# an intended, visible failure (see EvidenceBundle.__post_init__), not a
# silent skip.
POOLTOGETHER_REPO_ROOT_DEFAULT = Path("/scratch/md5344/.claude/jobs/318205ae/tmp/pooltogether_src/vault")


def render_context_bundle(bundle: dict) -> str:
    b = bundle["bundle"]
    parts = []
    if b.get("parent_section_context"):
        parts.append(f"Parent section context: {b['parent_section_context']}")
    if b.get("definitions"):
        parts.append("Definitions:\n" + "\n".join(f"  - {d}" for d in b["definitions"]))
    if b.get("referenced_requirements"):
        parts.append("Referenced requirements:\n" + "\n".join(
            f"  - {r.get('req_id', '?')}: {r.get('normative_text', r)}" for r in b["referenced_requirements"]))
    if b.get("overriding_requirements"):
        parts.append("Overriding requirements:\n" + "\n".join(
            f"  - {r.get('req_id', '?')}: {r.get('normative_text', r)}" for r in b["overriding_requirements"]))
    if b.get("exceptions"):
        parts.append("Exceptions:\n" + "\n".join(f"  - {e}" for e in b["exceptions"]))
    return "\n\n".join(parts) if parts else "(no additional context beyond the requirement's own text)"


def load_l2_bundle(req_id: str) -> dict:
    return __import__("json").loads((BUNDLES_DIR / f"{req_id}.json").read_text(encoding="utf-8"))


@dataclass
class Bundle:
    case_id: str
    req_id: str
    candidate_location: str          # "Contract.function" -- RTF's existing location convention
    candidate_file_rel: str          # path relative to repo_root, for Arm B's initial hint (not shown to Arm A)
    evidence_bundle_text: str        # the initial structured evidence, rendered as text -- identical for both arms
    known_limitations: list[str]     # -> Arm A's "known limitations" / Arm B's "explicitly unresolved facts"
    repo_root: Path
    expected_label: str | None       # "PASS" | "FAIL" | None (None = genuinely no fixed expected outcome)
    label_justification: str
    purpose: str                     # one-line note on what this bundle is designed to discriminate

    def requirement_text(self) -> str:
        return load_l2_bundle(self.req_id)["bundle"]["self"]

    def context_bundle_text(self) -> str:
        return render_context_bundle(load_l2_bundle(self.req_id))


def _repo_root_for(case_id: str) -> Path:
    root = FIXTURES_DIR / case_id
    if not root.is_dir():
        raise FileNotFoundError(f"fixture repo missing for case '{case_id}': {root}")
    return root


def build_dataset() -> list[Bundle]:
    bundles: list[Bundle] = []

    bundles.append(Bundle(
        case_id="unsafe_narrowing_cast",
        req_id="req-3-all-valid-inputs",
        candidate_location="Ledger.record",
        candidate_file_rel="Ledger.sol",
        evidence_bundle_text=(
            "predicate: find_unsafe_narrowing_cast (deterministic structural detector)\n"
            "location: Ledger.record\n"
            "operation: narrowing type conversion uint256 -> uint96\n"
            "input: _amount (uint256)\n"
            "validation_found: none\n"
            "risk: values above type(uint96).max are silently truncated by this cast rather than rejected"
        ),
        known_limitations=[],
        repo_root=_repo_root_for("unsafe_narrowing_cast"),
        expected_label="FAIL",
        label_justification=(
            "The cast truncates unconditionally: no comparison, min(), or require() bounds _amount anywhere "
            "in Ledger.record before the cast, and the fixture's only file/function is the candidate itself "
            "-- there is no other code in the repository that could supply a bound. Absence of a bound check "
            "is directly and unconditionally observable from the candidate location alone."
        ),
        purpose="Control: no additional repo evidence exists anywhere -- both arms should reach the same "
                "correct FAIL, ideally with Arm B needing few or zero extra tool actions.",
    ))

    bundles.append(Bundle(
        case_id="safe_narrowing_cast",
        req_id="req-3-all-valid-inputs",
        candidate_location="Ledger.record",
        candidate_file_rel="Ledger.sol",
        evidence_bundle_text=(
            "predicate: find_unsafe_narrowing_cast (deterministic structural detector)\n"
            "location: Ledger.record\n"
            "operation: narrowing type conversion uint256 -> uint96\n"
            "input: _amount (uint256)\n"
            "validation_found: require(_amount <= type(uint96).max, \"too large\") immediately precedes the cast\n"
            "risk: none identified -- the destination type's max value is enforced before the cast"
        ),
        known_limitations=[],
        repo_root=_repo_root_for("safe_narrowing_cast"),
        expected_label="PASS",
        label_justification=(
            "The require() immediately precedes and dominates the cast, checking exactly the value that is "
            "cast (_amount) against exactly the destination type's bound (type(uint96).max). No other path "
            "reaches the cast. This is the direct textual counterpart of the unsafe case above."
        ),
        purpose="Control: tests whether Arm B's location-scoped framing alone (not new evidence -- there is "
                "none to find) is enough to reach confident PASS where prior Phase H runs saw Arm-A-style "
                "hedging on an evidence-complete PASS case (root-cause report cases 2/4).",
    ))

    unresolved_signer_zero = (
        "Can authorizedSigner be, or become, the zero address anywhere in this repository?"
    )
    ecrecover_evidence = (
        "predicate: find_unchecked_ecrecover_result (deterministic structural detector)\n"
        "location: Auth.verify\n"
        "operation: ecrecover(...)\n"
        "validation_found: none\n"
        "missing_safety_condition: signer != address(0)\n"
        "risk: a malformed/invalid signature makes ecrecover return address(0); with no explicit check, "
        "this could be compared equal to an actual authorizedSigner of address(0)"
    )

    bundles.append(Bundle(
        case_id="unchecked_ecrecover_mutable_signer",
        req_id="req-2-signature-verification",
        candidate_location="Auth.verify",
        candidate_file_rel="Auth.sol",
        evidence_bundle_text=ecrecover_evidence,
        known_limitations=[unresolved_signer_zero],
        repo_root=_repo_root_for("unchecked_ecrecover_mutable_signer"),
        expected_label="FAIL",
        label_justification=(
            "AuthAdmin.sol (same repository) defines setAuthorizedSigner(address), callable by owner, with "
            "no zero-address check on the new value -- authorizedSigner can legitimately be set to "
            "address(0) (by mistake, or by a compromised owner key). At that point ecrecover's zero-address "
            "failure return for a malformed/invalid signature would satisfy `signer == authorizedSigner`, "
            "forging authentication. This is a concrete, repo-demonstrable path, not a hypothetical -- "
            "exactly the fact Arm A cannot see and Arm B must find via AuthAdmin.sol."
        ),
        purpose="Primary relational-evidence-gap test (FAIL direction): does repository search actually "
                "recover the specific fact (mutable, unbounded setter) that resolves the case?",
    ))

    bundles.append(Bundle(
        case_id="checked_ecrecover",
        req_id="req-2-signature-verification",
        candidate_location="Auth.verify",
        candidate_file_rel="Auth.sol",
        evidence_bundle_text=(
            "predicate: find_unchecked_ecrecover_result (deterministic structural detector)\n"
            "location: Auth.verify\n"
            "operation: ecrecover(...)\n"
            "validation_found: require(signer != address(0), \"invalid signature\") immediately follows the call\n"
            "risk: none identified -- the zero-address (malformed-signature) case is explicitly rejected "
            "before the result is used"
        ),
        known_limitations=[],
        repo_root=_repo_root_for("checked_ecrecover"),
        expected_label="PASS",
        label_justification=(
            "The explicit require(signer != address(0)) rejects exactly ecrecover's failure-mode output "
            "before the comparison against authorizedSigner ever runs -- this holds regardless of "
            "authorizedSigner's own value, so no further fact about authorizedSigner is needed."
        ),
        purpose="Control: complete, self-sufficient PASS evidence -- both arms should agree quickly.",
    ))

    bundles.append(Bundle(
        case_id="corrected_ecrecover_fixed_signer",
        req_id="req-2-signature-verification",
        candidate_location="Auth.verify",
        candidate_file_rel="Auth.sol",
        evidence_bundle_text=ecrecover_evidence,
        known_limitations=[unresolved_signer_zero],
        repo_root=_repo_root_for("corrected_ecrecover_fixed_signer"),
        expected_label="PASS",
        label_justification=(
            "authorizedSigner is declared `immutable` and assigned exactly once, in the constructor, which "
            "itself requires the assigned value be non-zero (require(_initialSigner != address(0), ...)); "
            "there is no setter anywhere in the file. Solidity's `immutable` guarantees no further "
            "assignment after construction, so authorizedSigner can never be address(0) at any point in "
            "this contract's lifetime -- ecrecover's zero-address failure mode can therefore never forge a "
            "match against it. This matches the root-cause investigation's own AB12 finding (originally "
            "discovered live, now made a first-class, pre-justified fixture instead)."
        ),
        purpose="Primary relational-evidence-gap test (PASS direction), and the direct counterpart of the "
                "FAIL-direction case above: SAME initial evidence text, SAME unresolved fact, opposite repo "
                "content and opposite correct answer. Tests whether Arm B's repository search resolves the "
                "fact correctly in both directions rather than defaulting to one direction under ambiguity.",
    ))

    bundles.append(Bundle(
        case_id="insufficient_evidence_timestamp",
        req_id="req-2-block-data-misuse",
        candidate_location="RewardStream.updateReward",
        candidate_file_rel="RewardStream.sol",
        evidence_bundle_text=(
            "predicate: find_block_timestamp_dependency (deterministic structural detector)\n"
            "location: RewardStream.updateReward\n"
            "operation: reward accrual scaled by elapsed block.timestamp (accRewardPerShare += elapsed * "
            "rewardRatePerSecond)\n"
            "validation_found: rewardRatePerSecond is admin-configurable via setRewardRate, no upper bound "
            "enforced\n"
            "risk: a block-producer-manipulable timestamp skew (on the order of seconds) could skew accrued "
            "rewards by an amount proportional to rewardRatePerSecond"
        ),
        known_limitations=[
            "What is the deployed/expected magnitude of rewardRatePerSecond relative to the protocol's "
            "total value -- i.e. whether a several-second timestamp skew is economically material enough "
            "to constitute an MEV-enabling vulnerability?"
        ],
        repo_root=_repo_root_for("insufficient_evidence_timestamp"),
        expected_label=None,
        label_justification=(
            "The repository fully specifies the mechanism (elapsed-time-scaled accrual, admin-configurable "
            "unbounded rate) but not the economic materiality needed to judge 'MUST NOT introduce "
            "vulnerabilities to MEV or similar attacks.' rewardRatePerSecond's actual/expected deployed "
            "value is an off-chain/deployment fact that no amount of further repository investigation can "
            "resolve -- a confident PASS or FAIL here would be unjustified from repo-visible evidence "
            "alone. INCONCLUSIVE/INSUFFICIENT_EVIDENCE is the correct answer for both arms."
        ),
        purpose="Genuine-uncertainty control: tests whether Arm B's repository access causes it to "
                "over-search for a resolution that doesn't exist in the repo, or to fabricate false "
                "confidence, versus honestly abstaining like a well-behaved Arm A.",
    ))

    bundles.append(Bundle(
        case_id="pooltogether_vault_burn",
        req_id="req-3-all-valid-inputs",
        candidate_location="Vault._burn",
        candidate_file_rel="src/Vault.sol",
        evidence_bundle_text=(
            "predicate: find_unsafe_narrowing_cast (deterministic structural detector)\n"
            "location: Vault._burn\n"
            "operation: narrowing type conversion uint256 -> uint96\n"
            "input: _shares (uint256)\n"
            "validation_found: none\n"
            "risk: values above type(uint96).max are silently truncated by this cast rather than rejected"
        ),
        known_limitations=[
            "Is _shares ever bound-checked to <= type(uint96).max before this cast -- earlier in _burn, in "
            "any caller, or via a prior mint that already enforced the same bound?"
        ],
        repo_root=POOLTOGETHER_REPO_ROOT_DEFAULT,
        expected_label="FAIL",
        label_justification=(
            "_burn casts its uint256 _shares parameter directly to uint96 via `uint96(_shares)` "
            "(vault/src/Vault.sol:1139 in the referenced checkout). Reading _burn's full body finds no "
            "require/assert bounding _shares to type(uint96).max (or any related bound) before this line. "
            "This is the identical unconditional-truncation pattern as the unsafe_narrowing_cast case above, "
            "demonstrated on real, unmodified project code -- derived purely from the cast/bound-check "
            "pattern itself, not from any EVMbench finding text or label."
        ),
        purpose="Real-repository generalization test: same category of question as the synthetic cases, but "
                "against a large real codebase where Arm B's search must actually navigate a nontrivial "
                "directory structure, not a 1-2-file fixture.",
    ))

    for b in bundles:
        if not b.repo_root.exists():
            raise FileNotFoundError(
                f"repo_root for case '{b.case_id}' does not exist: {b.repo_root}. "
                f"If this is the PoolTogether checkout, regenerate per evmbench/CLAUDE.md's existing "
                f"reproduction steps (git clone 2023-07-pooltogether, checkout "
                f"4240445ed3b5145be1032cf1becc9c6866046bf7, `git submodule update --init`)."
            )
    return bundles
