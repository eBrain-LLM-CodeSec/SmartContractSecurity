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
_reg("req-2-signature-verification", PredicateSpec(P.find_ecrecover_usage, ("slither",)))
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
_reg("req-3-all-valid-inputs", PredicateSpec(P.find_unvalidated_function_parameters, ("slither",)))

# --- GP --------------------------------------------------------------------

_reg("req-R-define-license", PredicateSpec(P.find_spdx_or_license_file, ("sol_source_paths", "repo_root"), passes_req_id=False))
_reg("req-R-follow-erc-standards", PredicateSpec(P.find_erc_interface_conformance, ("slither",)))
_reg("req-R-fuzzing-in-testing", PredicateSpec(P.find_fuzzing_evidence, ("repo_root", "sol_test_paths")))
_reg("req-R-mutation-testing", PredicateSpec(P.find_mutation_testing_evidence, ("repo_root",)))
_reg("req-R-formal-verification", PredicateSpec(P.find_formal_verification_evidence, ("repo_root", "sol_source_paths")))
# req-R-use-latest-compiler deliberately NOT registered with a hardcoded
# version -- see run_rtf.py's special-cased handling: it requires a
# run-time-supplied `latest_known_stable_solc_version` config value, and
# is marked ENVIRONMENT_FAILURE if that config is absent, rather than
# silently guessing or skipping.


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
