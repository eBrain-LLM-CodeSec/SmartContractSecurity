"""Increment 8: seven synthetic fixtures, real Slither tools, mocked LLM.

The fixture mechanisms come from generic requirement shapes, not EVMbench
contract/finding names. The model is scripted so this remains deterministic;
the assertions cover both verdict plumbing and required investigation moves.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from a4v.llm import ChatResult
from rtf.l11_investigation_grouping.taxonomy import ReasoningCategory
from rtf.security_agent.kernel import RESPONSE_MODELS, SecurityAgentKernel
from rtf.security_agent.model_client import ModelClient
from rtf.security_agent.state import RequirementResolution
from rtf.security_agent.tools import SecurityAgentTools

PASSES: list[str] = []
FAILURES: list[str] = []
ROOT = Path(__file__).resolve().parent / "fixtures"
SOLC = Path.home() / ".solc-select/artifacts/solc-0.8.20/solc-0.8.20"


@dataclass(frozen=True)
class Case:
    name: str
    contract: str
    function: str
    verdict: str
    category: ReasoningCategory
    tool_calls: tuple[tuple[str, dict], ...]
    required_result_fragments: tuple[str, ...]
    counterexample: str


CASES = (
    Case("cross_contract_semantic_mismatch", "MismatchedCaller", "currentWeight", "FAIL",
         ReasoningCategory.TIME_BLOCK_MEV_ORDERING,
         (("get_external_calls", {"contract": "MismatchedCaller", "function": "currentWeight"}),
          ("get_function_source", {"contract": "EpochConsumer", "function": "weightAt"})),
         ("weightAt", "epochStart"), "compare raw block input with the callee epoch-unit assumption"),
    Case("cross_contract_semantic_ok", "AlignedCaller", "currentWeight", "PASS",
         ReasoningCategory.TIME_BLOCK_MEV_ORDERING,
         (("get_external_calls", {"contract": "AlignedCaller", "function": "currentWeight"}),
          ("get_function_source", {"contract": "AlignedCaller", "function": "currentWeight"})),
         ("weightAt", "epochStart"), "try a non-aligned block and verify it is aligned before the call"),
    Case("missing_input_validation", "DomainMath", "reciprocal", "FAIL",
         ReasoningCategory.INPUT_DOMAIN_VALIDATION,
         (("get_function_source", {"contract": "DomainMath", "function": "reciprocal"}),),
         ("value == 0", "return 0"), "try invalid negative and zero boundary inputs"),
    Case("input_validation_ok", "DomainMath", "reciprocal", "PASS",
         ReasoningCategory.INPUT_DOMAIN_VALIDATION,
         (("get_function_source", {"contract": "DomainMath", "function": "reciprocal"}),),
         ("require", "value > 0"), "try invalid negative, zero, and boundary inputs against the require guard"),
    Case("unbounded_growth_iteration", "MemberRegistry", "contains", "FAIL",
         ReasoningCategory.GAS_DOS_STATE_GROWTH,
         (("get_function_source", {"contract": "MemberRegistry", "function": "addMember"}),
          ("get_function_source", {"contract": "MemberRegistry", "function": "contains"})),
         ("members.push", "members.length"), "grow storage without bound, find no pruning, then exercise full iteration loop"),
    Case("bounded_growth", "MemberRegistry", "contains", "PASS",
         ReasoningCategory.GAS_DOS_STATE_GROWTH,
         (("get_contract_source", {"contract": "MemberRegistry"}),),
         ("MAX_MEMBERS", "removeLast", "members.length"),
         "attempt growth to the bound, verify pruning removal, then inspect iteration loop cost"),
    Case("access_control_fail", "OracleConfiguration", "setOracle", "FAIL",
         ReasoningCategory.ACCESS_PRIVILEGE_CONTROL,
         (("get_modifiers", {"contract": "OracleConfiguration", "function": "setOracle"}),
          ("get_function_source", {"contract": "OracleConfiguration", "function": "setOracle"})),
         ("NOT_FOUND", "oracle = nextOracle"), "invoke setOracle as an unauthorized unprivileged caller"),
)


def check(name, condition, detail=""):
    (PASSES if condition else FAILURES).append(name if condition else f"{name}: {detail}")


def _select_solc() -> None:
    if not SOLC.exists():
        raise RuntimeError(f"missing solc fixture compiler: {SOLC}")
    bin_dir = Path(tempfile.mkdtemp(prefix="fixture_matrix_solc_"))
    (bin_dir / "solc").symlink_to(SOLC)
    os.environ["PATH"] = f"{bin_dir}:{os.environ.get('PATH', '')}"


class ScriptedClient:
    """ModelClient.decide() calls .complete() directly (not
    .complete_json()) -- see model_client.py's own docstring."""

    def __init__(self, responses):
        self.responses = responses
        self.index = 0

    def complete(self, messages, temperature=0.0, top_p=None, max_tokens=None):
        response = self.responses[self.index]
        self.index += 1
        content = "```json\n" + json.dumps(response) + "\n```"
        return ChatResult(content, 0, 0, False, None)


def _responses(case: Case):
    responses = [
        {"action": "call_tool", "tool": tool, "args": args,
         "reasoning": f"required investigation move for {case.name}"}
        for tool, args in case.tool_calls
    ]
    if case.verdict == "PASS":
        responses.append({"action": "update_investigation", "hypotheses": [{
            "id": "h1", "claim": "the property can be violated",
            "originating_property_ids": ["p1"], "status": "REFUTED",
        }], "counterexample_attempts": [{
            "property_id": "p1", "hypothesis_id": "h1",
            "attempt": case.counterexample, "result": "the inspected guard refutes the attempted violation",
        }]})
        hypothesis_status = "REFUTED"
        support, contradict = [], ["ev1"]
    else:
        hypothesis_status = "SUPPORTED"
        support, contradict = ["ev1"], []
    responses.append({"action": "conclude", "evidence": [{
        "id": "ev1", "claim": "fixture source establishes the mechanism",
        "source_file": "Fixture.sol", "source_contract": case.contract,
        "source_function": case.function, "source_lines": "1-80", "tool_call_id": "tool-1",
    }], "hypotheses": [{
        "id": "h1", "claim": "the property can be violated",
        "originating_property_ids": ["p1"], "status": hypothesis_status,
        "supporting_evidence_ids": support, "contradicting_evidence_ids": contradict,
    }], "properties": [{
        "property_id": "p1", "claim": "the requirement holds",
        "evidence_ids": ["ev1"], "hypothesis_ids": ["h1"],
        "interpretation": f"synthetic mechanism resolves {case.verdict}", "verdict": case.verdict,
    }]})
    return responses


def test_fixture_matrix():
    _select_solc()
    for case in CASES:
        fixture = ROOT / case.name / "Fixture.sol"
        tools = SecurityAgentTools.build(fixture.parent, fixture)
        kernel = SecurityAgentKernel(tools, ModelClient(ScriptedClient(_responses(case)), RESPONSE_MODELS))
        state = kernel.run_cluster(
            case.name, ["p1"], "synthetic protocol", {"p1": "generic requirement"},
            f"investigate {case.contract}.{case.function}",
            reasoning_categories_by_property={"p1": case.category.value},
        )
        result_text = " ".join(call.result_summary for call in state.tool_history)
        # Summaries intentionally omit source text, so inspect direct tool
        # results too when checking mechanism-specific fragments.
        direct_results = [tools.call(tool, args) for tool, args in case.tool_calls]
        direct_text = json.dumps(direct_results)
        check(f"{case.name}: expected verdict",
              state.requirement_states["p1"].status == RequirementResolution(case.verdict),
              state.requirement_states["p1"])
        check(f"{case.name}: required tool sequence",
              [call.tool for call in state.tool_history] == [tool for tool, _ in case.tool_calls],
              state.tool_history)
        check(f"{case.name}: mechanism visible",
              all(fragment in direct_text or fragment in result_text
                  for fragment in case.required_result_fragments), direct_text)
        if case.verdict == "PASS":
            check(f"{case.name}: counterexample behavior recorded",
                  bool(state.requirement_states["p1"].counterexample_attempts),
                  state.requirement_states["p1"])


def test_fixtures_do_not_contain_benchmark_identifiers():
    banned = ("canto", "forte", "phi", "cred.sol", "curatorrewardsdistributor")
    contents = "\n".join(path.read_text().lower() for path in ROOT.rglob("*.sol"))
    check("fixture matrix contains no benchmark identifiers",
          not any(identifier in contents for identifier in banned),
          [identifier for identifier in banned if identifier in contents])


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as exc:
                FAILURES.append(f"{name}: CRASHED -- {type(exc).__name__}: {exc}")
    print(f"PASSED: {len(PASSES)}")
    for item in PASSES:
        print(f"  ok - {item}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for item in FAILURES:
            print(f"  FAIL - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
