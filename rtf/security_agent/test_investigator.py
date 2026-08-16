"""Deterministic Increment-6 adapter tests; no network or real model."""
from __future__ import annotations

import sys
import tempfile
import json
from pathlib import Path

from a4v.llm import ChatResult
from rtf.l11_investigation_grouping.cluster_response_validation import validate_cluster_response
from rtf.security_agent.investigator import (
    _extract_context, _property_metadata_from_plan, run_security_agent_bundle,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name, condition, detail=""):
    (PASSES if condition else FAILURES).append(name if condition else f"{name}: {detail}")


PLAN = """# Cluster investigation plan: c1
## Properties
### `p1`
- Target: `Vault.withdraw`
- **Parent EthTrust obligation**: `req-parent` (full official text: `.rtf/context/requirements/req-parent.md`)
## Investigation procedure
"""


class FakeChatClient:
    def __init__(self, *args, **kwargs):
        self.turn = 0

    def complete_json(self, messages, temperature=0.0, **kwargs):
        self.turn += 1
        usage = ChatResult("", 10, 5, False, 0.001)
        if self.turn == 1:
            return ({"action": "call_tool", "tool": "get_function_source",
                     "args": {"contract": "Vault", "function": "withdraw"},
                     "reasoning": "inspect ordering"}, usage)
        return ({"action": "conclude", "evidence": [{
            "id": "ev1", "claim": "call precedes state update", "source_file": "Vault.sol",
            "source_contract": "Vault", "source_function": "withdraw", "source_lines": "38-41",
            "tool_call_id": "tool-1",
        }], "hypotheses": [{
            "id": "h1", "claim": "withdraw is reentrant", "originating_property_ids": ["p1"],
            "status": "SUPPORTED", "supporting_evidence_ids": ["ev1"],
        }], "properties": [{
            "property_id": "p1", "claim": "withdraw follows safe ordering",
            "evidence_ids": ["ev1"], "hypothesis_ids": ["h1"],
            "interpretation": "external interaction precedes effects", "verdict": "FAIL",
        }]}, usage)


class FakeTools:
    def call(self, name, args):
        return {"status": "OK", "file": "Vault.sol", "contract": "Vault",
                "name": "withdraw", "source": "38: call(); 40: shares -= amount;"}


def test_context_and_parent_parsing():
    extra = {".rtf/context/protocol_context.md": "protocol",
             ".rtf/context/requirements/req-parent.md": "requirement",
             ".rtf/plans/c1.md": PLAN}
    protocol, requirements, plan = _extract_context(extra)
    ids, parents = _property_metadata_from_plan(plan)
    check("protocol extracted", protocol == "protocol")
    check("requirement keyed by req id", requirements == {"req-parent": "requirement"})
    check("property id parsed", ids == ["p1"])
    check("parent id parsed", parents == {"p1": "req-parent"})


def test_adapter_returns_live_runner_compatible_result():
    scratch = Path(tempfile.mkdtemp(prefix="security_agent_adapter_test_"))
    build_args = {}

    def tools_factory(**kwargs):
        build_args.update(kwargs)
        return FakeTools()

    result = run_security_agent_bundle(
        codex_bin=Path("unused"), python_bin=Path("unused"), mcp_server_script=Path("unused"),
        api_key="unused", model="fake", case_id="case-1", entry_file=Path("Vault.sol"),
        repo_root=Path("."), candidate_location="Vault.withdraw",
        solc_path_dir="/opt/solc-bin", solc_remaps=None, prompt="unused",
        scratch_root=scratch, timeout_s=5,
        extra_files={".rtf/context/protocol_context.md": "protocol",
                     ".rtf/context/requirements/req-parent.md": "requirement",
                     ".rtf/plans/c1.md": PLAN},
        compile_via_foundry=False, chat_client_factory=FakeChatClient,
        tools_factory=tools_factory,
    )
    validation = validate_cluster_response(["p1"], result.final_decision)
    check("result is structurally complete for live_runner", validation.complete, validation)
    check("FAIL verdict projected", result.final_decision["properties"][0]["verdict"] == "FAIL")
    check("token cost accumulated", result.cost_usd == 0.002, result.cost_usd)
    check("tool telemetry projected", result.tool_calls == 1 and result.files_inspected == 1)
    trajectory_events = [json.loads(line) for line in Path(result.trajectory_path).read_text().splitlines()]
    check("trajectory artifact written", Path(result.trajectory_path).exists(), result.trajectory_path)
    check("trajectory has ordered start/tool/finish events",
          trajectory_events[0]["event_type"] == "cluster_started" and
          any(event["event_type"] == "tool_result" for event in trajectory_events) and
          trajectory_events[-1]["event_type"] == "cluster_finished", trajectory_events)
    check("sequence numbers are monotonic",
          [event["sequence"] for event in trajectory_events] ==
          list(range(1, len(trajectory_events) + 1)), trajectory_events)
    check("explicit solc path forwarded without mutating PATH",
          build_args["extra_compile_kwargs"] == {"solc": "/opt/solc-bin/solc"}, build_args)


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
