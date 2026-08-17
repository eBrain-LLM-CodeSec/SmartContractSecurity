"""Deterministic Increment-6 adapter tests; no network or real model."""
from __future__ import annotations

import sys
import tempfile
import json
from pathlib import Path

from a4v.llm import ChatResult
from rtf.l11_investigation_grouping.cluster_response_validation import (
    resolve_property_verdicts, validate_cluster_response,
)
from rtf.l12_evaluation.metrics import ConformanceState
from rtf.security_agent.investigator import (
    _extract_context, _property_entries_for_legacy_harness, _property_metadata_from_plan,
    run_security_agent_bundle,
)
from rtf.security_agent.state import ClusterInvestigationState, RequirementResolution

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
    """ModelClient.decide() calls .complete() directly (not
    .complete_json()) -- see model_client.py's own docstring on why
    (content=None must be caught before extract_last_fenced_json)."""

    def __init__(self, *args, **kwargs):
        self.turn = 0

    def complete(self, messages, temperature=0.0, top_p=None, max_tokens=None):
        self.turn += 1
        if self.turn == 1:
            raw = {"action": "call_tool", "tool": "get_function_source",
                   "args": {"contract": "Vault", "function": "withdraw"},
                   "reasoning": "inspect ordering"}
        else:
            raw = {"action": "conclude", "evidence": [{
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
            }]}
        content = "```json\n" + json.dumps(raw) + "\n```"
        return ChatResult(content, 10, 5, False, 0.001)


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


# --- root cause 4: verdict-vocabulary mismatch with the legacy harness -----

def test_not_applicable_and_unresolved_verdicts_translated_for_legacy_harness():
    """Real live finding (2026-08-17 forte run, 15/147 properties):
    rtf.security_agent.state.RequirementResolution is PASS/FAIL/
    NOT_APPLICABLE/UNRESOLVED (the brief's own literal 4-state schema);
    the pre-existing pipeline's ConformanceState is PASS/FAIL/
    INCONCLUSIVE/INSUFFICIENT_EVIDENCE. NOT_APPLICABLE and UNRESOLVED
    were never recognized keys in cluster_response_validation.py's
    _DECISION_TO_CONFORMANCE -- both fell into its unknown_verdict:X
    branch and were force-downgraded to INCONCLUSIVE anyway, just
    without ever reaching the harness's own resolution logic under the
    RIGHT verdict."""
    state = ClusterInvestigationState.initial("c1", ["p1", "p2", "p3"])
    state.resolve_requirement("p1", RequirementResolution.NOT_APPLICABLE, reason="construct never used here")
    state.mark_unresolved_reason("p2", "max_steps_exhausted")
    state.resolve_requirement("p3", RequirementResolution.FAIL, reason="real finding")

    entries = {e["property_id"]: e for e in _property_entries_for_legacy_harness(state)}
    check("NOT_APPLICABLE translated to INSUFFICIENT_EVIDENCE", entries["p1"]["verdict"] == "INSUFFICIENT_EVIDENCE",
          entries["p1"])
    check("UNRESOLVED translated to INCONCLUSIVE", entries["p2"]["verdict"] == "INCONCLUSIVE", entries["p2"])
    check("PASS/FAIL/etc. pass through unchanged", entries["p3"]["verdict"] == "FAIL", entries["p3"])


def test_translated_verdicts_never_hit_unknown_verdict_in_the_real_harness():
    """Integration-style check against the REAL, unmodified
    cluster_response_validation.resolve_property_verdicts (the exact
    function that produced unknown_verdict:X live) -- proves end-to-end
    compatibility without needing a live run to observe it."""
    state = ClusterInvestigationState.initial("c1", ["p1", "p2"])
    state.resolve_requirement("p1", RequirementResolution.NOT_APPLICABLE, reason="n/a")
    state.mark_unresolved_reason("p2", "max_steps_exhausted")

    response = {"properties": _property_entries_for_legacy_harness(state)}
    resolved = resolve_property_verdicts(response)
    check("p1 resolved to a REAL ConformanceState", resolved["p1"].conformance_state == ConformanceState.INSUFFICIENT_EVIDENCE,
          resolved["p1"])
    check("p2 resolved to a REAL ConformanceState", resolved["p2"].conformance_state == ConformanceState.INCONCLUSIVE,
          resolved["p2"])
    check("p1 was NOT downgraded via the unknown_verdict path",
          not (resolved["p1"].reason or "").startswith("unknown_verdict"), resolved["p1"].reason)
    check("p2 was NOT downgraded via the unknown_verdict path",
          not (resolved["p2"].reason or "").startswith("unknown_verdict"), resolved["p2"].reason)


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
