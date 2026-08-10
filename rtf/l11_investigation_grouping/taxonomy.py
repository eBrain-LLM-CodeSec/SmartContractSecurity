"""Phase 3 of the grouped-investigation architecture: semantic reasoning
categories derived from the EthTrust corpus itself.

See `RTF_INVESTIGATION_GROUPING_TAXONOMY.md` for the full rationale per
category (why it exists, what shared reasoning context its members have,
why joint investigation may help, unsafe combinations). This module is
the mechanical, testable half: a category enum, an explicit per-req_id
mapping covering all 81 static corpus requirements (built by reading
every requirement's own title/normative text -- see the taxonomy doc for
the reasoning behind each assignment, not re-derived here), and a
best-effort categorizer for GENERATED (GP/ERC-standard-derived)
requirements, which reuses the exact same category definitions applied
to the generated clause's own text -- no separate scheme for generated
vs. static requirements.

These categories were derived by reading EthTrust's own requirement
titles and normative text (`rtf/l1_corpus/requirement_corpus.json`) --
NOT from any EVMbench vulnerability taxonomy, finding, or label. Two
requirements land in the same category because EthTrust's own text
points at the same code sites and the same kind of reasoning, not
because they happen to correlate with any benchmark outcome.
"""
from __future__ import annotations

from enum import Enum


class ReasoningCategory(str, Enum):
    COMPILER_TOOLCHAIN_SAFETY = "COMPILER_TOOLCHAIN_SAFETY"
    LOW_LEVEL_CONSTRUCT_SAFETY = "LOW_LEVEL_CONSTRUCT_SAFETY"
    EXTERNAL_CALL_INTERACTION = "EXTERNAL_CALL_INTERACTION"
    ACCESS_PRIVILEGE_CONTROL = "ACCESS_PRIVILEGE_CONTROL"
    SIGNATURE_AUTH_REPLAY = "SIGNATURE_AUTH_REPLAY"
    ARITHMETIC_VALUE_CORRECTNESS = "ARITHMETIC_VALUE_CORRECTNESS"
    INPUT_DOMAIN_VALIDATION = "INPUT_DOMAIN_VALIDATION"
    SOURCE_TEXT_INTEGRITY = "SOURCE_TEXT_INTEGRITY"
    FUNCTIONAL_CORRECTNESS_DOCUMENTATION = "FUNCTIONAL_CORRECTNESS_DOCUMENTATION"
    TIME_BLOCK_MEV_ORDERING = "TIME_BLOCK_MEV_ORDERING"
    GAS_DOS_STATE_GROWTH = "GAS_DOS_STATE_GROWTH"
    ORACLE_EXTERNAL_DEPENDENCY = "ORACLE_EXTERNAL_DEPENDENCY"
    STATE_CHANGE_OBSERVABILITY = "STATE_CHANGE_OBSERVABILITY"
    PRIVACY_DATA_EXPOSURE = "PRIVACY_DATA_EXPOSURE"
    PROCESS_GOVERNANCE_PRACTICE = "PROCESS_GOVERNANCE_PRACTICE"
    AGGREGATION_META = "AGGREGATION_META"
    """Pure logical AND-aggregations over OTHER requirements
    (`registry.AGGREGATION_REQ_IDS`) -- never independently investigated
    (resolved by `compute_aggregation_requirements` from other
    requirements' own final verdicts), so never a candidate for grouping
    at all. Included in the mapping so `categorize_requirement` is total
    over the corpus, not so these ever reach the grouping engine."""


# Built by reading every one of the 81 corpus requirements' own title +
# normative_text (rtf/l1_corpus/requirement_corpus.json) -- see
# RTF_INVESTIGATION_GROUPING_TAXONOMY.md for the per-category rationale.
REQ_ID_TO_CATEGORY: dict[str, ReasoningCategory] = {
    # --- Compiler/toolchain safety (deterministic-heavy; version/known-bug checks) ---
    "req-1-compiler-060": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-compiler-SOL-2021-1": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-compiler-SOL-2021-2": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-compiler-sol-2021-4": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-compiler-SOL-2022-1": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-compiler-SOL-2022-2": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-compiler-SOL-2022-3": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-compiler-SOL-2022-5-push": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-compiler-SOL-2022-6": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-compiler-SOL-2023-3": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-1-no-ancient-compilers": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-2-compiler-060": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-2-compiler-SOL-2021-3": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-2-compiler-SOL-2022-4": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-2-compiler-SOL-2022-5-assembly": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-2-compiler-SOL-2022-7": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-2-compiler-SOL-2023-1": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-3-consistent-solidity-output": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,
    "req-R-use-latest-compiler": ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY,

    # --- Low-level/dangerous construct safety (assembly, delegatecall, selfdestruct, CREATE2) ---
    "req-1-no-assembly": ReasoningCategory.LOW_LEVEL_CONSTRUCT_SAFETY,
    "req-2-safe-assembly": ReasoningCategory.LOW_LEVEL_CONSTRUCT_SAFETY,
    "req-1-delegatecall": ReasoningCategory.LOW_LEVEL_CONSTRUCT_SAFETY,
    "req-1-self-destruct": ReasoningCategory.LOW_LEVEL_CONSTRUCT_SAFETY,
    "req-2-self-destruct": ReasoningCategory.LOW_LEVEL_CONSTRUCT_SAFETY,
    "req-1-no-create2": ReasoningCategory.LOW_LEVEL_CONSTRUCT_SAFETY,
    "req-2-protect-create2": ReasoningCategory.LOW_LEVEL_CONSTRUCT_SAFETY,
    "req-2-documented": ReasoningCategory.LOW_LEVEL_CONSTRUCT_SAFETY,

    # --- External call interaction / reentrancy / CEI ---
    "req-1-use-c-e-i": ReasoningCategory.EXTERNAL_CALL_INTERACTION,
    "req-1-check-return": ReasoningCategory.EXTERNAL_CALL_INTERACTION,
    "req-2-handle-return": ReasoningCategory.EXTERNAL_CALL_INTERACTION,
    "req-2-external-calls": ReasoningCategory.EXTERNAL_CALL_INTERACTION,
    "req-3-external-calls": ReasoningCategory.EXTERNAL_CALL_INTERACTION,
    "req-2-avoid-readonly-reentrancy": ReasoningCategory.EXTERNAL_CALL_INTERACTION,

    # --- Access/privilege control, governance, timelock ---
    "req-3-access-control": ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
    "req-3-no-single-admin-eoa": ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
    "req-3-revocable-permisions": ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
    "req-3-protect-governance": ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
    "req-3-timelock-for-privileged-actions": ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
    "req-R-multisig-threshold": ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,

    # --- Signature verification / authentication / replay ---
    "req-2-signature-verification": ReasoningCategory.SIGNATURE_AUTH_REPLAY,
    "req-2-malleable-signatures-for-replay": ReasoningCategory.SIGNATURE_AUTH_REPLAY,
    "req-3-intended-replay": ReasoningCategory.SIGNATURE_AUTH_REPLAY,
    "req-1-eip155-chainid": ReasoningCategory.SIGNATURE_AUTH_REPLAY,
    "req-1-no-tx.origin": ReasoningCategory.SIGNATURE_AUTH_REPLAY,
    "req-3-verify-tx.origin": ReasoningCategory.SIGNATURE_AUTH_REPLAY,

    # --- Arithmetic / value / rounding correctness ---
    "req-2-overflow-underflow": ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS,
    "req-2-check-rounding": ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS,
    "req-1-exact-balance-check": ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS,
    "req-2-verify-exact-balance-check": ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS,
    "req-2-enforce-eval-order": ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS,

    # --- Input/domain validation ---
    "req-3-all-valid-inputs": ReasoningCategory.INPUT_DOMAIN_VALIDATION,

    # --- Source-text integrity (unicode/homoglyph/encoding-ambiguity attacks) ---
    "req-1-unicode-bdo": ReasoningCategory.SOURCE_TEXT_INTEGRITY,
    "req-2-unicode-bdo": ReasoningCategory.SOURCE_TEXT_INTEGRITY,
    "req-2-no-homoglyph-attack": ReasoningCategory.SOURCE_TEXT_INTEGRITY,
    "req-1-no-hashing-consecutive-variable-length-args": ReasoningCategory.SOURCE_TEXT_INTEGRITY,

    # --- Functional correctness / documentation-vs-implementation ---
    "req-3-documented": ReasoningCategory.FUNCTIONAL_CORRECTNESS_DOCUMENTATION,
    "req-3-implement-as-documented": ReasoningCategory.FUNCTIONAL_CORRECTNESS_DOCUMENTATION,
    "req-3-document-system": ReasoningCategory.FUNCTIONAL_CORRECTNESS_DOCUMENTATION,
    "req-3-document-threats": ReasoningCategory.FUNCTIONAL_CORRECTNESS_DOCUMENTATION,
    "req-3-annotate": ReasoningCategory.FUNCTIONAL_CORRECTNESS_DOCUMENTATION,
    "req-3-linted": ReasoningCategory.FUNCTIONAL_CORRECTNESS_DOCUMENTATION,

    # --- Time/block/MEV/ordering semantics ---
    "req-2-block-data-misuse": ReasoningCategory.TIME_BLOCK_MEV_ORDERING,
    "req-2-random-enough": ReasoningCategory.TIME_BLOCK_MEV_ORDERING,
    "req-3-block-mev": ReasoningCategory.TIME_BLOCK_MEV_ORDERING,
    "req-3-block-front-running": ReasoningCategory.TIME_BLOCK_MEV_ORDERING,

    # --- Gas / DoS / state growth ---
    "req-3-enough-gas": ReasoningCategory.GAS_DOS_STATE_GROWTH,
    "req-3-protect-gas": ReasoningCategory.GAS_DOS_STATE_GROWTH,

    # --- Oracle / external dependency ---
    "req-3-check-oracles": ReasoningCategory.ORACLE_EXTERNAL_DEPENDENCY,

    # --- State-change observability ---
    "req-3-event-on-state-change": ReasoningCategory.STATE_CHANGE_OBSERVABILITY,

    # --- Privacy / data exposure ---
    "req-3-no-private-data": ReasoningCategory.PRIVACY_DATA_EXPOSURE,

    # --- Aggregation/meta (never independently investigated) ---
    "req-2-pass-l1": ReasoningCategory.AGGREGATION_META,
    "req-3-pass-l2": ReasoningCategory.AGGREGATION_META,
    "req-R-meet-all-possible": ReasoningCategory.AGGREGATION_META,

    # --- Process/governance practice (org-level, mostly deterministic/doc-evidence) ---
    "req-R-check-new-bugs": ReasoningCategory.PROCESS_GOVERNANCE_PRACTICE,
    "req-R-clean-code": ReasoningCategory.PROCESS_GOVERNANCE_PRACTICE,
    "req-R-define-license": ReasoningCategory.PROCESS_GOVERNANCE_PRACTICE,
    "req-R-follow-erc-standards": ReasoningCategory.PROCESS_GOVERNANCE_PRACTICE,
    "req-R-formal-verification": ReasoningCategory.PROCESS_GOVERNANCE_PRACTICE,
    "req-R-fuzzing-in-testing": ReasoningCategory.PROCESS_GOVERNANCE_PRACTICE,
    "req-R-mutation-testing": ReasoningCategory.PROCESS_GOVERNANCE_PRACTICE,
    "req-R-notify-news": ReasoningCategory.PROCESS_GOVERNANCE_PRACTICE,
}


# Category PAIRS that must never be grouped into one Codex investigation,
# even if two properties from these categories happen to share a
# location/file -- see RTF_INVESTIGATION_GROUPING_TAXONOMY.md for the
# per-pair rationale (incompatible reasoning shapes, not just "different
# topics"). Stored as frozenset pairs so lookup is direction-independent.
UNSAFE_CATEGORY_COMBINATIONS: frozenset[frozenset[ReasoningCategory]] = frozenset({
    frozenset({ReasoningCategory.AGGREGATION_META, c})
    for c in ReasoningCategory if c != ReasoningCategory.AGGREGATION_META
} | {
    frozenset({ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY, c})
    for c in ReasoningCategory if c != ReasoningCategory.COMPILER_TOOLCHAIN_SAFETY
} | {
    frozenset({ReasoningCategory.FUNCTIONAL_CORRECTNESS_DOCUMENTATION, ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS}),
    frozenset({ReasoningCategory.SIGNATURE_AUTH_REPLAY, ReasoningCategory.GAS_DOS_STATE_GROWTH}),
})
# Every stored combination has exactly 2 DISTINCT members -- a same-
# category "pair" would be meaningless (grouping properties from the
# SAME category is the normal, safe case every grouping policy relies
# on), and `is_unsafe_combination`'s pairwise loop never even constructs
# a length-1 frozenset to look up, so a stray one here would be silent
# dead weight, not a bug -- excluded anyway for clarity.
assert all(len(pair) == 2 for pair in UNSAFE_CATEGORY_COMBINATIONS)


def categorize_requirement(req_id: str) -> ReasoningCategory | None:
    """Static-corpus lookup. None for a req_id not in the 81-corpus
    (a generated GP/ERC requirement) -- use `categorize_generated_clause`
    for those instead, which applies the same category definitions to
    the clause's own text rather than a fixed table (a generated
    requirement's identity isn't known ahead of time)."""
    return REQ_ID_TO_CATEGORY.get(req_id)


# Keyword anchors for categorizing a GENERATED (GP/ERC-standard-derived)
# requirement's clause text -- applies the SAME category definitions
# above, not a separate scheme. Deliberately simple substring matching
# (not NLP): every ERC-4626/ERC-20 clause this session's generator
# produces is short, mechanically-templated normative prose (see
# rtf/standards/generator.py), so keyword presence is a reliable,
# auditable signal here, not a guess. Checked in order; first match
# wins -- ordered from most to least specific so a clause mentioning
# both "rounding" and "fees" (a real, common ERC-4626 pattern) lands on
# the more specific ARITHMETIC_VALUE_CORRECTNESS read.
_GENERATED_CLAUSE_KEYWORDS: tuple[tuple[ReasoningCategory, tuple[str, ...]], ...] = (
    (ReasoningCategory.ARITHMETIC_VALUE_CORRECTNESS,
     ("round", "fee", "convert", "share", "asset", "precision", "truncat", "overflow", "underflow")),
    (ReasoningCategory.EXTERNAL_CALL_INTERACTION,
     ("transfer", "reentran", "call", "hook")),
    (ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
     ("owner", "admin", "role", "permission", "privileg")),
    (ReasoningCategory.SIGNATURE_AUTH_REPLAY,
     ("signature", "permit", "nonce", "approve", "allowance")),
    (ReasoningCategory.INPUT_DOMAIN_VALIDATION,
     ("validate", "revert", "zero address", "input")),
)


def categorize_generated_clause(clause_text: str) -> ReasoningCategory | None:
    """Best-effort keyword categorization for a generated requirement's
    own normative clause text (e.g. an ERC-4626 clause). Returns None
    (not a guessed default) when no keyword matches -- an uncategorized
    generated property is a real, honestly-reported gap, not silently
    folded into an arbitrary bucket, matching this whole taxonomy's
    "explainable or nothing" standard.
    """
    lowered = clause_text.lower()
    for category, keywords in _GENERATED_CLAUSE_KEYWORDS:
        if any(kw in lowered for kw in keywords):
            return category
    return None


def is_unsafe_combination(categories: set[ReasoningCategory]) -> bool:
    """True if ANY pair within `categories` is a listed unsafe
    combination -- checked pairwise, not just "is the whole set a listed
    combination" (a 3+-category cluster is unsafe if any 2 of its
    members are)."""
    cats = list(categories)
    for i in range(len(cats)):
        for j in range(i + 1, len(cats)):
            if frozenset({cats[i], cats[j]}) in UNSAFE_CATEGORY_COMBINATIONS:
                return True
    return False
