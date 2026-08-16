"""RTF_V3_REDESIGN_PLAN.md "Mutation testing" section: a small, real
proof of concept, not a full framework.

Question this answers, per the task brief verbatim: "Given a contract
known to satisfy EthTrust requirement X, if we deliberately violate X,
does RTF detect it?" -- independent evidence of requirement
implementation quality, distinct from hand-written vulnerable/safe
fixture pairs (`test_ethtrust_conformance.py`), since the mutated
contract is DERIVED from a real safe fixture by a single, mechanical,
requirement-shaped edit (remove an access-control modifier / remove a
domain-validation check / remove a pruning path), not independently
authored.

Each mutation below is one of the exact classes the task brief lists:
"remove access modifier", "remove validation", "remove pruning/removal
path". Applied via plain string surgery on the real `safe.sol` fixture
content (never touching the file on disk) -- deliberately NOT a general
AST-mutation engine; that's future work, explicitly out of scope for
this first proof of concept per the brief's own phasing instruction.

Run with:
    .venv/bin/python3 -m rtf.tests.ethtrust_conformance.test_mutation_testing_poc
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l12_evaluation.metrics import ApplicabilityState
from rtf.tests.ethtrust_conformance.conformance_harness import FIXTURES_DIR, run_tier1

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _run_mutated(req_id: str, mutated_source: str):
    """Same real routing pipeline `conformance_harness.run_tier1` uses,
    but against IN-MEMORY mutated source rather than a fixture path --
    `run_tier1` itself only accepts a path, so this is a thin, deliberate
    duplication of its own compile+route call, not a divergent
    mechanism."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        entry = tmp / "Entry.sol"
        entry.write_text(mutated_source, encoding="utf-8")
        from rtf.l12_evaluation.pipeline_e2e import CORPUS_PATH
        from rtf.l12_evaluation.run_rtf import build_context_for_evmbench_target, load_unconditioned_map, run_rtf
        ctx, compile_error = build_context_for_evmbench_target(entry, tmp, "0.8.20")
        assert ctx.slither is not None, f"mutated fixture failed to compile: {compile_error}"
        unconditioned_map = load_unconditioned_map(CORPUS_PATH)
        run, _raw = run_rtf(ctx, "mutation-poc", unconditioned_map)
        return run.routed[req_id]


# --- Mutation 1: remove access modifier (req-3-access-control) ---------

def test_removing_onlyowner_modifier_from_safe_fixture_is_detected():
    safe_source = (FIXTURES_DIR / "req-3-access-control" / "safe.sol").read_text(encoding="utf-8")
    check("precondition: safe fixture actually uses onlyOwner", "onlyOwner" in safe_source, safe_source)
    mutated = safe_source.replace("function withdraw(uint256 amount) public onlyOwner {", "function withdraw(uint256 amount) public {")
    check("mutation applied: onlyOwner no longer on withdraw", "public onlyOwner" not in mutated, mutated)

    baseline = run_tier1(FIXTURES_DIR / "req-3-access-control" / "safe.sol", "req-3-access-control")
    mutated_result = _run_mutated("req-3-access-control", mutated)

    check("mutated version still routes APPLICABLE (predicate still fires)", mutated_result.applicability_state == ApplicabilityState.APPLICABLE, mutated_result)
    check(
        "mutation is detectable: evidence for the mutated function now matches the KNOWN-vulnerable fixture's shape",
        any(e.location == "Treasury.withdraw" for e in mutated_result.evidence),
        mutated_result.evidence,
    )


# --- Mutation 2: remove validation (req-3-all-valid-inputs) -------------

def test_removing_domain_validation_from_safe_fixture_is_detected():
    safe_source = (FIXTURES_DIR / "req-3-all-valid-inputs" / "safe.sol").read_text(encoding="utf-8")
    check("precondition: safe fixture actually validates its input", "require(x > 0" in safe_source, safe_source)
    mutated = safe_source.replace('require(x > 0, "Ln: input must be positive");\n        ', "")
    check("mutation applied: require() no longer present", "require(x > 0" not in mutated, mutated)

    baseline = run_tier1(FIXTURES_DIR / "req-3-all-valid-inputs" / "safe.sol", "req-3-all-valid-inputs")
    check("baseline (real, unmutated safe fixture): zero evidence, resolves PASS", baseline.evidence_locations == (), baseline)

    mutated_result = _run_mutated("req-3-all-valid-inputs", mutated)
    mutated_locations = [e.location for e in mutated_result.evidence]
    check(
        "mutation is detectable: removing the validation makes the requirement APPLICABLE with evidence again",
        mutated_result.applicability_state == ApplicabilityState.APPLICABLE and len(mutated_locations) > 0,
        mutated_result,
    )
    check("mutated evidence targets Ln.ln, matching the known-vulnerable fixture", any("Ln.ln" in loc for loc in mutated_locations), mutated_locations)


# --- Mutation 3: remove pruning/removal path (req-3-enough-gas) --------

def test_removing_removal_path_from_safe_fixture_is_detected():
    safe_source = (FIXTURES_DIR / "req-3-enough-gas" / "safe.sol").read_text(encoding="utf-8")
    check("precondition: safe fixture has a removal path", "holderList.pop();" in safe_source, safe_source)
    # Remove the entire removeHolder function body's mutating statements,
    # leaving a no-op stub -- the removal PATH is gone even though the
    # function still exists (a real, minimal mutation: deleting a
    # capability without deleting the whole function signature).
    mutated = safe_source.replace(
        "    function removeHolder(uint256 idx) public {\n"
        "        holderList[idx] = holderList[holderList.length - 1];\n"
        "        holderList.pop();\n"
        "    }\n",
        "",
    )
    check("mutation applied: removeHolder's own pop() no longer present", "holderList.pop();" not in mutated, mutated)

    mutated_result = _run_mutated("req-3-enough-gas", mutated)
    mutated_locations = [e.location for e in mutated_result.evidence]
    check(
        "mutation is detectable: growth predicate now flags Holders.distributeRewards, matching the known-vulnerable fixture",
        any(loc == "Holders.distributeRewards" for loc in mutated_locations),
        mutated_locations,
    )


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
