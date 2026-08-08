"""L12 predicate registry: maps each of the 57 requirements with real,
tested predicate code to the exact function(s)/parameters that implement
it, so `run_rtf.py` can invoke them generically against a real target
instead of hand-wiring 57 call sites.

**Source of truth, not a re-derivation.** Every entry here is transcribed
directly from that requirement's own `implementation_status.code` field
(in `rtf/track_a/l5_level_s_strategy/`, `l6_level_m_extraction/`,
`l7_level_q_evidence/`, `l_gp_recommended_practice/`) -- if this registry
and a JSON record ever disagree, the JSON record is authoritative and
this file has drifted and needs fixing, not the reverse.

Deliberately excludes the 24 requirements with no implemented predicate
(21 terminal `NO_PREDICATE_POSSIBLE`/`NOT_IMPLEMENTED` + 3 pure
aggregation) -- the orchestrator must not silently skip them without
comment; see `run_rtf.py`'s handling of requirements absent from this
registry.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from rtf.l5_predicates import predicates as P


@dataclass(frozen=True)
class PredicateSpec:
    func: Callable
    needs: tuple[str, ...] = ()  # subset of "slither", "sol_source_paths", "repo_root", "sol_test_paths"
    extra_kwargs: dict = field(default_factory=dict)
    passes_req_id: bool = True
    """False for the 3 predicates with NO req_id parameter at all
    (find_create2_usage, find_documented_trigger_sites,
    find_spdx_or_license_file -- each hardcodes its own req_id
    internally instead). Discovered by a real L12 orchestrator run
    crashing with `TypeError: got an unexpected keyword argument
    'req_id'` -- every OTHER predicate in this module takes req_id, so
    this was a real, easy-to-miss inconsistency, not something apparent
    from reading any single function's signature in isolation.
    """


# req_id -> list of PredicateSpec. Multiple specs means the requirement's
# strategy composes more than one predicate call (evidence from all specs
# is concatenated) -- e.g. req-1-compiler-sol-2021-4 needs BOTH the UDVT
# width check AND the exact-version check.
REGISTRY: dict[str, list[PredicateSpec]] = {}


def _reg(req_id: str, *specs: PredicateSpec) -> None:
    REGISTRY[req_id] = list(specs)


# --- S-level -----------------------------------------------------------

_reg("req-1-compiler-060", PredicateSpec(P.check_compiler_version_floor, ("slither",), {"floor": "0.8.0"}))
_reg("req-1-no-ancient-compilers", PredicateSpec(P.check_compiler_version_floor, ("slither",), {"floor": "0.3.0"}))
_reg("req-1-compiler-sol-2021-4",
     PredicateSpec(P.find_udvt_narrower_than_32_bytes, ("slither",)),
     PredicateSpec(P.check_compiler_version_exact, ("slither",), {"exact": "0.8.8"}))
_reg("req-1-compiler-SOL-2021-1", PredicateSpec(P.check_compiler_version_floor, ("slither",), {"floor": "0.8.3"}))
_reg("req-1-compiler-SOL-2021-2", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.4.16", "high": "0.8.3"}))
_reg("req-1-compiler-SOL-2022-1", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.8.11", "high": "0.8.12"}))
_reg("req-1-compiler-SOL-2022-2", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.6.9", "high": "0.8.12"}))
_reg("req-1-compiler-SOL-2022-3", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.6.9", "high": "0.8.12"}))
_reg("req-1-compiler-SOL-2022-5-push", PredicateSpec(P.check_compiler_version_floor, ("slither",), {"floor": "0.8.15"}))
_reg("req-1-compiler-SOL-2022-6", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.5.8", "high": "0.8.15"}))
_reg("req-1-compiler-SOL-2023-3", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.8.5", "high": "0.8.22"}))
_reg("req-1-eip155-chainid", PredicateSpec(P.find_keccak256_calls_chainid_dependency, ("slither",)))
_reg("req-1-exact-balance-check", PredicateSpec(P.find_exact_native_balance_check, ("slither",)))
_reg("req-1-no-create2", PredicateSpec(P.find_create2_usage, ("slither",), {}, passes_req_id=False))
_reg("req-1-self-destruct", PredicateSpec(P.find_selfdestruct_presence, ("slither",)))
_reg("req-1-delegatecall", PredicateSpec(P.find_delegatecall_presence, ("slither",)))
_reg("req-1-no-tx.origin", PredicateSpec(P.find_tx_origin_any_usage, ("slither",)))
_reg("req-1-no-hashing-consecutive-variable-length-args", PredicateSpec(P.find_encode_packed_untainted_collision, ("slither",)))
_reg("req-1-unicode-bdo", PredicateSpec(P.find_unicode_direction_control_chars, ("sol_source_paths",)))
_reg("req-1-use-c-e-i", PredicateSpec(P.find_state_write_after_external_call, ("slither",)))

_reg("req-1-no-assembly", PredicateSpec(P.run_reused_slither_detector, ("slither",), {"detector_classes": None}))  # populated below (needs Slither import)
_reg("req-1-check-return", PredicateSpec(P.run_reused_slither_detector, ("slither",), {"detector_classes": None}))
_reg("req-2-handle-return", PredicateSpec(P.run_reused_slither_detector, ("slither",), {"detector_classes": None}))

# --- M-level -------------------------------------------------------------

_reg("req-2-compiler-060", PredicateSpec(P.check_compiler_version_floor, ("slither",), {"floor": "0.8.0"}))
_reg("req-2-compiler-SOL-2021-3", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.6.5", "high": "0.8.8"}))
_reg("req-2-compiler-SOL-2022-4", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.8.13", "high": "0.8.14"}))
_reg("req-2-compiler-SOL-2022-5-assembly", PredicateSpec(P.check_compiler_version_floor, ("slither",), {"floor": "0.8.15"}))
_reg("req-2-compiler-SOL-2022-7", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.8.13", "high": "0.8.16"}))
_reg("req-2-compiler-SOL-2023-1", PredicateSpec(P.check_compiler_version_in_range, ("slither",), {"low": "0.6.2", "high": "0.8.20"}))
_reg("req-2-overflow-underflow", PredicateSpec(P.find_unprotected_arithmetic, ("slither",)))
_reg("req-2-external-calls", PredicateSpec(P.find_state_write_after_external_call, ("slither",)))
_reg("req-2-documented", PredicateSpec(P.find_documented_trigger_sites, ("slither",), {}, passes_req_id=False))
_reg("req-2-block-data-misuse", PredicateSpec(P.find_block_data_usage, ("slither",)))
_reg("req-2-random-enough", PredicateSpec(P.find_block_data_usage, ("slither",)))
_reg("req-2-check-rounding", PredicateSpec(P.find_division_in_value_context, ("slither",)))
_reg("req-2-signature-verification",
     PredicateSpec(P.find_ecrecover_usage, ("slither",)),
     PredicateSpec(P.find_unchecked_ecrecover_result, ("slither",)))
_reg("req-2-malleable-signatures-for-replay",
     PredicateSpec(P.find_ecrecover_usage, ("slither",)),
     PredicateSpec(P.find_oz_ecdsa_library_usage, ("slither",)))
_reg("req-2-unicode-bdo", PredicateSpec(P.find_unicode_direction_control_chars, ("sol_source_paths",)))
_reg("req-2-verify-exact-balance-check", PredicateSpec(P.find_exact_native_balance_check, ("slither",)))
_reg("req-2-protect-create2", PredicateSpec(P.find_create2_deployed_target_violations, ("slither",)))
_reg("req-2-safe-assembly", PredicateSpec(P.find_unsafe_assembly_variable_write, ("slither",)))
_reg("req-2-avoid-readonly-reentrancy", PredicateSpec(P.find_readonly_reentrancy_candidates, ("slither",)))
_reg("req-2-self-destruct", PredicateSpec(P.find_selfdestruct_protection_status, ("slither",)))

# --- Q-level -------------------------------------------------------------

_reg("req-3-event-on-state-change", PredicateSpec(P.find_state_write_without_event, ("slither",)))
_reg("req-3-annotate", PredicateSpec(P.find_public_interfaces_missing_natspec, ("slither",)))
_reg("req-3-consistent-solidity-output", PredicateSpec(P.find_non_exact_pragma, ("slither",)))
_reg("req-3-external-calls", PredicateSpec(P.find_state_write_after_external_call, ("slither",)))
_reg("req-3-verify-tx.origin", PredicateSpec(P.find_tx_origin_any_usage, ("slither",)))
_reg("req-3-linted",
     PredicateSpec(P.find_linting_violations_via_reused_detectors, ("slither",)),
     PredicateSpec(P.find_pragma_solidity_version_specified, ("sol_source_paths",)))
_reg("req-3-access-control", PredicateSpec(P.find_state_mutating_function_protection_status, ("slither",)))
_reg("req-3-all-valid-inputs",
     PredicateSpec(P.find_unvalidated_function_parameters, ("slither",)),
     PredicateSpec(P.find_unsafe_narrowing_cast, ("slither",)))

# --- GP --------------------------------------------------------------------

_reg("req-R-define-license", PredicateSpec(P.find_spdx_or_license_file, ("sol_source_paths", "repo_root"), passes_req_id=False))
_reg("req-R-follow-erc-standards", PredicateSpec(P.find_erc_interface_conformance, ("slither",)))
_reg("req-R-fuzzing-in-testing", PredicateSpec(P.find_fuzzing_evidence, ("repo_root", "sol_test_paths")))
_reg("req-R-mutation-testing", PredicateSpec(P.find_mutation_testing_evidence, ("repo_root",)))
_reg("req-R-formal-verification", PredicateSpec(P.find_formal_verification_evidence, ("repo_root", "sol_source_paths")))

# req-R-use-latest-compiler: `check_compiler_version_is_latest_stable` was
# implemented and tested (rtf/l5_predicates/test_predicates.py) but never
# actually added here -- a real, confirmed category-A gap found during
# the RTF runtime coverage audit (RTF_RUNTIME_COVERAGE_AUDIT.md): a
# working predicate existed and simply was not registered. The comment
# previously here claimed a "special-cased handling" in run_rtf.py that
# does not exist anywhere in the codebase -- also a documentation/code
# discrepancy, logged in RTF_MISSING_REQUIREMENTS_GAP_ANALYSIS.md.
#
# `latest_known_stable_version` is a genuinely external, time-anchored
# reference (see the predicate's own docstring) -- 0.8.36, per
# https://www.soliditylang.org/blog/ as of 2026-08-09 (this repository's
# solc-select only has up to 0.8.28 installed, which does not change the
# correctness of the comparison: no version comparison here requires
# actually compiling WITH 0.8.36, only comparing against it as a string).
# This value WILL go stale as new Solidity versions ship -- flagged
# in-line, not hidden, exactly as the predicate's own docstring requires.
_reg("req-R-use-latest-compiler",
     PredicateSpec(P.check_compiler_version_is_latest_stable, ("slither",),
                   {"latest_known_stable_version": "0.8.36"}))

# --- Generic documentary/implementation-comparison evidence ---------------
# req_ids below were ALL marked NO_PREDICATE_POSSIBLE / NOT_IMPLEMENTED in
# their own Track A design record because assessing them requires
# comparing DOCUMENTED claims against IMPLEMENTATION behavior, or
# reviewing broad semantic/economic properties with no nameable syntactic
# anchor -- inherently semantic, per those records' own reasoning (see
# RTF_MISSING_REQUIREMENTS_GAP_ANALYSIS.md for the full per-requirement
# classification). None of that reasoning is wrong: no DETERMINISTIC
# predicate is being added here. What was missing is that
# "NO_PREDICATE_POSSIBLE" was previously treated as equivalent to "never
# runs at all" -- these requirements never even reached the ALREADY-BUILT
# shared L8 LLM Judgment Layer, because nothing ever produced evidence to
# hand it. `collect_documentary_and_implementation_evidence` fixes
# exactly that gap, generically: it collects README/docs/NatSpec/
# implementation-source evidence (identical mechanism for every req_id
# below) and lets the EXISTING judge_with_l8 -> escalation -> Codex
# pipeline decide conformance from it, same as every other requirement in
# this registry -- no new judgment mechanism, no per-requirement
# heuristics, no benchmark-derived knowledge.
_DOC_EVIDENCE_REQ_IDS = (
    "req-2-enforce-eval-order",
    "req-2-no-homoglyph-attack",
    "req-3-block-front-running",
    "req-3-block-mev",
    "req-3-check-oracles",
    "req-3-document-system",
    "req-3-document-threats",
    "req-3-documented",
    "req-3-enough-gas",
    "req-3-implement-as-documented",
    "req-3-intended-replay",
    "req-3-no-private-data",
    "req-3-no-single-admin-eoa",
    "req-3-protect-gas",
    "req-3-protect-governance",
    "req-3-revocable-permisions",
    "req-3-timelock-for-privileged-actions",
    "req-R-check-new-bugs",
    "req-R-clean-code",
    "req-R-multisig-threshold",
    "req-R-notify-news",
)
for _rid in _DOC_EVIDENCE_REQ_IDS:
    _reg(_rid, PredicateSpec(P.collect_documentary_and_implementation_evidence,
                              ("entry_sol_file", "repo_root")))
del _rid

# Public alias: which registered req_ids reach a verdict only through the
# shared L8 LLM Judgment Layer's semantic reading of generically-collected
# documentary/implementation evidence, as opposed to a real deterministic
# analytical predicate. Used by `pipeline_e2e.compute_integrity_report`'s
# "applicable executed: deterministic / LLM-mediated" breakdown -- L8
# itself judges evidence from BOTH kinds of requirement alike (that part
# of the architecture was already unified before this change), so this
# distinction is about EVIDENCE PROVENANCE, not which requirements get an
# LLM call at all.
LLM_MEDIATED_REQ_IDS = frozenset(_DOC_EVIDENCE_REQ_IDS)

# Three requirements are pure AGGREGATIONS over other requirements'
# already-computed conformance_state (req-2-pass-l1: AND over every Level
# S requirement; req-3-pass-l2: AND over every Level M requirement;
# req-R-meet-all-possible: an advisory SHOULD-level completeness measure)
# -- per their own Track A design records, "implementing" them means
# composing an L12-evaluation-level result, not writing a predicate that
# takes evidence from ONE target in isolation. Deliberately NOT registered
# here; computed by `pipeline_e2e.compute_aggregation_requirements` after
# the main per-requirement loop, using this same set so run_rtf.py can
# distinguish "aggregation, handled separately" from "genuinely
# unsupported" when iterating the full corpus.
AGGREGATION_REQ_IDS = frozenset({"req-2-pass-l1", "req-3-pass-l2", "req-R-meet-all-possible"})


def _wire_reused_detector_specs() -> None:
    """`run_reused_slither_detector` needs real Slither detector CLASS
    objects as `detector_classes`, not something expressible as a
    literal in the `_reg(...)` calls above -- wired here, after import,
    to keep the detector imports colocated with their one use instead of
    scattered across this file's top-level imports.
    """
    from slither.detectors.statements.assembly import Assembly
    from slither.detectors.operations.unchecked_low_level_return_values import UncheckedLowLevel
    from slither.detectors.operations.unchecked_send_return_value import UncheckedSend

    REGISTRY["req-1-no-assembly"][0].extra_kwargs["detector_classes"] = [Assembly]
    REGISTRY["req-1-check-return"][0].extra_kwargs["detector_classes"] = [UncheckedLowLevel, UncheckedSend]
    REGISTRY["req-2-handle-return"][0].extra_kwargs["detector_classes"] = [UncheckedLowLevel, UncheckedSend]


_wire_reused_detector_specs()


IMPLEMENTED_REQ_IDS = frozenset(REGISTRY.keys())
