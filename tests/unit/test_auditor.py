"""AgenticAuditor tests using a fake codex invoker (mirrors the "FakeCodex"
seam pattern already proven in backend/worker_runner/common.py's own test
suite) -- no real subprocess is spawned, no tokens are spent.
"""
import json
from pathlib import Path

import pytest

from a4v.auditor import AgenticAuditor, parse_codex_usage
from a4v.commentator import Comment
from a4v.features import NodeFeatures
from a4v.graph import ProgramGraph
from a4v.score import Candidate

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VAULT_SOL = FIXTURES / "multi_contract" / "Vault.sol"


def _features(node_id: str, **kwargs) -> NodeFeatures:
    base = dict(node_id=node_id, cyclomatic_complexity=1.0, external_call_count=0.0,
                unsafe_cast_count=0.0, write_after_external_call_count=0.0)
    base.update(kwargs)
    return NodeFeatures(**base)


def _candidate(node_id: str, score: float, strong_signal: bool = False, vuln_class: str = "reentrancy") -> Candidate:
    comment = Comment(suspicious=True, vuln_class=vuln_class, severity="high", rationale="looks bad", lines=[1])
    return Candidate(node_id=node_id, score=score, strong_signal=strong_signal,
                      features=_features(node_id), comment=comment)


def test_parse_codex_usage_extracts_tokens_from_event_stream():
    stdout = (
        '{"type":"thread.started","thread_id":"x"}\n'
        '{"type":"turn.started"}\n'
        '{"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"OK"}}\n'
        '{"type":"turn.completed","usage":{"input_tokens":7329,"cached_input_tokens":3840,"output_tokens":38}}\n'
    )
    usage = parse_codex_usage(stdout)
    assert usage == (7329, 38)


def test_parse_codex_usage_returns_none_without_turn_completed():
    assert parse_codex_usage("not json at all\nmore garbage") is None


class FakeInvoker:
    """Writes a scripted verdict (or simulates a timeout) per node_id,
    recording call order and never spawning a real subprocess."""

    def __init__(self, scripted: dict[str, dict | None]):
        self.scripted = scripted  # node_id -> verdict dict, or None for "timeout"
        self.calls: list[str] = []

    def __call__(self, cmd: list[str], *, cwd: str, timeout: int) -> tuple[bool, str]:
        # -o <out_path> is always the element right after the "-o" flag
        out_path = Path(cmd[cmd.index("-o") + 1])
        # candidate node_id is embedded in the prompt (last cmd arg)
        prompt = cmd[-1]
        node_id = next((n for n in self.scripted if n in prompt), None)
        self.calls.append(node_id)

        verdict = self.scripted.get(node_id)
        if verdict is None:
            return False, ""  # simulated timeout
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("```json\n" + json.dumps(verdict) + "\n```")
        return True, ""


@pytest.fixture
def pg() -> ProgramGraph:
    return ProgramGraph.build(VAULT_SOL)


def test_confirmed_candidate_becomes_finding(tmp_path, pg):
    node = "fn::Vault.withdraw(uint256)"
    invoker = FakeInvoker({node: {
        "decision": "confirm", "vuln_class": "reentrancy", "severity": "high",
        "mechanism": "external call before state write", "file": str(VAULT_SOL),
        "lines": [37, 38], "fix": "use checks-effects-interactions", "reasoning": "confirmed via trace",
    }})
    auditor = AgenticAuditor(pg, checkout_dir=FIXTURES / "multi_contract", out_dir=tmp_path,
                              model="test-model", invoke=invoker)
    findings, not_investigated = auditor.run([_candidate(node, score=1.0)])

    assert len(findings) == 1
    assert findings[0].vuln_class == "reentrancy"
    assert findings[0].lines == [37, 38]
    assert not not_investigated
    assert len(auditor.memory.confirmed) == 1


def test_rejected_candidate_not_a_finding_but_recorded_in_memory(tmp_path, pg):
    node = "fn::Vault.deposit()"
    invoker = FakeInvoker({node: {
        "decision": "reject", "vuln_class": None, "severity": None,
        "mechanism": "", "file": None, "lines": [], "fix": None,
        "reasoning": "no external call here, not reentrancy",
    }})
    auditor = AgenticAuditor(pg, checkout_dir=FIXTURES / "multi_contract", out_dir=tmp_path,
                              model="test-model", invoke=invoker)
    findings, not_investigated = auditor.run([_candidate(node, score=1.0)])

    assert findings == []
    assert not not_investigated
    assert len(auditor.memory.rejected) == 1
    assert auditor.memory.rejected[0].reasoning == "no external call here, not reentrancy"


def test_vague_confirm_is_downgraded_to_rejected(tmp_path, pg):
    """A 'confirm' with no mechanism/file/lines must not become a finding --
    the grader is strict on concreteness, so vague confirms are treated as
    rejections defensively, independent of the model's own self-report."""
    node = "fn::Vault.callHelper()"
    invoker = FakeInvoker({node: {
        "decision": "confirm", "vuln_class": "other", "severity": "low",
        "mechanism": "", "file": None, "lines": [], "fix": None, "reasoning": "vague",
    }})
    auditor = AgenticAuditor(pg, checkout_dir=FIXTURES / "multi_contract", out_dir=tmp_path,
                              model="test-model", invoke=invoker)
    findings, _ = auditor.run([_candidate(node, score=1.0)])
    assert findings == []
    assert len(auditor.memory.rejected) == 1


def test_timeout_advances_queue_and_records_not_investigated(tmp_path, pg):
    node_a = "fn::Vault.withdraw(uint256)"
    node_b = "fn::Vault.deposit()"
    invoker = FakeInvoker({
        node_a: None,  # simulated timeout
        node_b: {"decision": "reject", "vuln_class": None, "severity": None,
                  "mechanism": "", "file": None, "lines": [], "fix": None, "reasoning": "fine"},
    })
    auditor = AgenticAuditor(pg, checkout_dir=FIXTURES / "multi_contract", out_dir=tmp_path,
                              model="test-model", invoke=invoker)
    candidates = [_candidate(node_a, score=2.0, strong_signal=True), _candidate(node_b, score=1.0)]
    findings, not_investigated = auditor.run(candidates)

    assert node_a in not_investigated
    assert invoker.calls == [node_a, node_b], "a per-candidate timeout must not block the rest of the queue"


def test_strong_signal_investigated_before_higher_raw_score(tmp_path, pg):
    weak_but_high_score = "fn::Vault.deposit()"
    strong_but_low_score = "fn::Vault.withdraw(uint256)"
    verdict = {"decision": "reject", "vuln_class": None, "severity": None,
                "mechanism": "", "file": None, "lines": [], "fix": None, "reasoning": "n/a"}
    invoker = FakeInvoker({weak_but_high_score: verdict, strong_but_low_score: verdict})
    auditor = AgenticAuditor(pg, checkout_dir=FIXTURES / "multi_contract", out_dir=tmp_path,
                              model="test-model", invoke=invoker)
    candidates = [
        _candidate(weak_but_high_score, score=100.0, strong_signal=False),
        _candidate(strong_but_low_score, score=0.1, strong_signal=True),
    ]
    auditor.run(candidates)
    assert invoker.calls[0] == strong_but_low_score, "strong-signal candidates must be investigated first"


def test_per_audit_ceiling_stops_cleanly_and_records_tail(tmp_path, pg):
    node_a = "fn::Vault.withdraw(uint256)"
    node_b = "fn::Vault.deposit()"
    verdict = {"decision": "reject", "vuln_class": None, "severity": None,
                "mechanism": "", "file": None, "lines": [], "fix": None, "reasoning": "n/a"}
    invoker = FakeInvoker({node_a: verdict, node_b: verdict})
    # ceiling of 1 tool call -- exhausted right after the first candidate
    auditor = AgenticAuditor(pg, checkout_dir=FIXTURES / "multi_contract", out_dir=tmp_path,
                              model="test-model", invoke=invoker, per_audit_tool_call_ceiling=1)
    candidates = [_candidate(node_a, score=2.0, strong_signal=True), _candidate(node_b, score=1.0)]
    findings, not_investigated = auditor.run(candidates)

    assert invoker.calls == [node_a]
    assert not_investigated == [node_b]

    trace_lines = auditor.trace_path.read_text().strip().splitlines()
    events = [json.loads(l)["event"] for l in trace_lines]
    assert "ceiling_reached" in events


def test_session_trace_has_start_and_done_events(tmp_path, pg):
    node = "fn::Vault.withdraw(uint256)"
    invoker = FakeInvoker({node: {
        "decision": "confirm", "vuln_class": "reentrancy", "severity": "high",
        "mechanism": "m", "file": "f.sol", "lines": [1], "fix": "x", "reasoning": "r",
    }})
    auditor = AgenticAuditor(pg, checkout_dir=FIXTURES / "multi_contract", out_dir=tmp_path,
                              model="test-model", invoke=invoker)
    auditor.run([_candidate(node, score=1.0)])

    events = [json.loads(l) for l in auditor.trace_path.read_text().strip().splitlines()]
    kinds = [e["event"] for e in events]
    assert kinds == ["investigate_start", "investigate_done"]
    assert all("ts" in e for e in events)
