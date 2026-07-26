"""Agentic Auditor: one investigation session per audit over a priority
queue of candidates (plan: "Agentic Auditor (ONE shared Codex agent per
audit)").

Important nuance, confirmed by reading the already-proven, already-graded
worker_runner implementation (`backend/worker_runner/common.py:run_codex_stage`):
`codex exec` has **no session-resume mechanism** -- "a retry launches a
BRAND-NEW codex session from scratch". So "one shared session per audit" is
implemented here as one FRESH `codex exec` process per candidate, whose
prompt carries accumulated on-disk working memory (already-confirmed/
rejected candidates, contracts already summarized) -- this is the same
pattern the existing SmartAuditFlow investigation loop uses (task_state.json
/ evidence/*.json fed into each fresh stage call), reimplemented
independently here with agent4vul's own state shapes, per the deliberate
choice to keep this pipeline self-contained rather than reuse that code.

`codex exec`'s own flags (build_codex_cmd) mirror the flags proven to work
in this environment (see common.py's build_codex_cmd / run_codex_detect.sh)
-- --dangerously-bypass-approvals-and-sandbox, --skip-git-repo-check, -C
<agent_dir>, -o <out_path> --json. `invoke` is an injectable seam so tests
never spawn a real codex subprocess or spend tokens (mirrors the "FakeCodex"
pattern in common.py's own test suite).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from a4v.consolidate import Finding
from a4v.graph import ProgramGraph
from a4v.llm import extract_last_fenced_json
from a4v.score import Candidate
from a4v.slice import BundleBuilder, numbered_source


@dataclass
class Verdict:
    node_id: str
    decision: str  # "confirm" | "reject"
    vuln_class: str | None
    severity: str | None
    mechanism: str
    file: str | None
    lines: list[int]
    fix: str | None
    reasoning: str


@dataclass
class Budget:
    token_ceiling: int
    tool_call_ceiling: int
    tokens_used: int = 0
    tool_calls_used: int = 0

    def exhausted(self) -> bool:
        return self.tokens_used >= self.token_ceiling or self.tool_calls_used >= self.tool_call_ceiling

    def spend(self, tokens: int, tool_calls: int = 0) -> None:
        self.tokens_used += tokens
        self.tool_calls_used += tool_calls


class CodexInvoker(Protocol):
    def __call__(self, cmd: list[str], *, cwd: str, timeout: int) -> tuple[bool, str]:
        """Returns (ok, output_text). ok=False on timeout/crash."""
        ...


def default_codex_invoke(cmd: list[str], *, cwd: str, timeout: int) -> tuple[bool, str]:
    import subprocess
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0, proc.stdout
    except subprocess.TimeoutExpired:
        return False, ""


def parse_codex_usage(stdout: str) -> tuple[int, int] | None:
    """Extracts (prompt_tokens, completion_tokens) from codex exec's --json
    event stream (a `{"type":"turn.completed","usage":{...}}` line). Returns
    None if no such event is found (e.g. a fake/test invoker's stdout)."""
    total_input = 0
    total_output = 0
    found = False
    for line in stdout.splitlines():
        line = line.strip()
        if not line or '"turn.completed"' not in line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = event.get("usage")
        if not usage:
            continue
        found = True
        total_input += usage.get("input_tokens", 0)
        total_output += usage.get("output_tokens", 0)
    return (total_input, total_output) if found else None


def build_codex_cmd(*, model: str, agent_dir: Path, out_path: Path, prompt: str,
                     reasoning_effort: str = "") -> list[str]:
    cmd = [
        "codex", "exec",
        "--model", model,
        "--dangerously-bypass-approvals-and-sandbox",
        "--skip-git-repo-check",
        # Confirmed live (2026-07-23): without --ephemeral, the container's
        # read-only filesystem outside our bind mount makes codex fail to
        # persist skills/session state, which surfaces as a nonzero exit code
        # even though the actual turn completed and -o's output was written
        # correctly. --ephemeral skips that persistence entirely.
        "--ephemeral",
        "-C", str(agent_dir),
        "-o", str(out_path), "--json",
    ]
    if reasoning_effort:
        cmd += ["-c", f"model_reasoning_effort={reasoning_effort}"]
    cmd.append(prompt)
    return cmd


@dataclass
class WorkingMemory:
    """Accumulated state across candidates in one audit. This -- not a
    persisted process -- is what makes the session 'shared'."""
    confirmed: list[Verdict] = field(default_factory=list)
    rejected: list[Verdict] = field(default_factory=list)
    contract_summaries: dict[str, str] = field(default_factory=dict)

    def summary_text(self) -> str:
        parts = []
        if self.confirmed:
            parts.append("Already CONFIRMED this audit (do not re-report the same mechanism+location):")
            for v in self.confirmed:
                parts.append(f"  - [{v.severity}] {v.vuln_class} in {v.file}:{v.lines} -- {v.mechanism[:150]}")
        if self.rejected:
            parts.append("Already REJECTED this audit (do not re-investigate without new evidence):")
            for v in self.rejected:
                parts.append(f"  - {v.node_id}: {v.reasoning[:150]}")
        if self.contract_summaries:
            parts.append("Contracts already summarized this audit:")
            for c, s in self.contract_summaries.items():
                parts.append(f"  - {c}: {s}")
        return "\n".join(parts) if parts else "(none yet -- this is the first candidate investigated)"


_VERDICT_OUTPUT_CONTRACT = """\
Investigate this candidate using the tools available in this working
directory (read files, grep, run the graph/bundle/slither tool wrappers as
needed). Iterate until you can confirm or reject it, then respond with a
final fenced ```json block with exactly these fields:
{
  "decision": "confirm"|"reject",
  "vuln_class": "<string or null>",
  "severity": "low"|"medium"|"high"|null,
  "mechanism": "<concrete technical explanation, or rejection reasoning>",
  "file": "<path or null>",
  "lines": [<int>, ...],
  "fix": "<concrete suggested fix, or null>",
  "reasoning": "<why you confirmed or rejected>"
}
A "confirm" without a concrete mechanism + exact file/line + fix will be
treated as a rejection -- the grader is strict on mechanism, code location,
and fix, and rejects vague/generic text.
"""


def build_candidate_prompt(candidate: Candidate, bundle_json: dict, memory: WorkingMemory) -> str:
    signal = candidate.comment.rationale if candidate.comment else "(no Commentator signal; static-rule seed only)"
    return (
        "You are auditing a smart contract project for a loss-of-funds vulnerability.\n\n"
        f"Candidate under investigation: {candidate.node_id}\n"
        f"Static/Commentator signal that raised this candidate: {signal}\n\n"
        f"Context bundle:\n{json.dumps(bundle_json, indent=2)[:6000]}\n\n"
        f"Working memory from prior candidates in this audit:\n{memory.summary_text()}\n\n"
        f"{_VERDICT_OUTPUT_CONTRACT}"
    )


def _bundle_json(pg: ProgramGraph, bundle_builder: BundleBuilder, node_id: str) -> tuple[dict, str]:
    bundle = bundle_builder.expand(node_id, hops=1)
    payload = {
        "seed": bundle.seed, "contract": bundle.contract,
        "contract_summary": bundle.contract_summary,
        "state_vars": bundle.state_vars,
        "write_after_external_call_vars": bundle.write_after_external_call_vars,
        "source_excerpts": {
            k: numbered_source(v, bundle.source_excerpt_start_lines.get(k, 1))
            for k, v in bundle.source_excerpts.items()
        },
    }
    return payload, bundle.contract


class AgenticAuditor:
    def __init__(self, pg: ProgramGraph, checkout_dir: Path, out_dir: Path, model: str,
                 per_audit_token_ceiling: int = 1_500_000, per_audit_tool_call_ceiling: int = 150,
                 per_candidate_soft_cap_seconds: int = 600, reasoning_effort: str = "high",
                 invoke: CodexInvoker = default_codex_invoke):
        self.pg = pg
        self.checkout_dir = Path(checkout_dir)
        self.out_dir = Path(out_dir)
        self.model = model
        self.budget = Budget(token_ceiling=per_audit_token_ceiling, tool_call_ceiling=per_audit_tool_call_ceiling)
        self.per_candidate_soft_cap_seconds = per_candidate_soft_cap_seconds
        self.reasoning_effort = reasoning_effort
        self.invoke = invoke
        self.memory = WorkingMemory()
        self.bundle_builder = BundleBuilder(pg)
        self.trace_path = self.out_dir / "investigations" / "session.jsonl"
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)

    def _log_trace(self, entry: dict) -> None:
        entry = {**entry, "ts": time.time()}
        with self.trace_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def _investigate_one(self, candidate: Candidate, bundle_json: dict) -> Verdict | None:
        prompt = build_candidate_prompt(candidate, bundle_json, self.memory)
        safe_name = candidate.node_id.replace("::", "_").replace("/", "_").replace("(", "").replace(")", "")
        out_path = self.out_dir / "investigations" / f"{safe_name}.json"
        cmd = build_codex_cmd(model=self.model, agent_dir=self.checkout_dir, out_path=out_path,
                               prompt=prompt, reasoning_effort=self.reasoning_effort)

        self._log_trace({"event": "investigate_start", "node_id": candidate.node_id})
        ok, stdout = self.invoke(cmd, cwd=str(self.checkout_dir), timeout=self.per_candidate_soft_cap_seconds)

        if not ok:
            self._log_trace({"event": "investigate_timeout", "node_id": candidate.node_id})
            return None

        raw = out_path.read_text() if out_path.exists() else stdout
        try:
            data = extract_last_fenced_json(raw)
        except Exception as e:  # noqa: BLE001
            self._log_trace({"event": "investigate_parse_error", "node_id": candidate.node_id, "error": str(e)})
            return None

        verdict = Verdict(
            node_id=candidate.node_id,
            decision=data.get("decision", "reject"),
            vuln_class=data.get("vuln_class"),
            severity=data.get("severity"),
            mechanism=data.get("mechanism", ""),
            file=data.get("file"),
            lines=[int(x) for x in (data.get("lines") or []) if isinstance(x, (int, float))],
            fix=data.get("fix"),
            reasoning=data.get("reasoning", ""),
        )
        usage = parse_codex_usage(stdout)
        if usage is not None:
            prompt_tokens, completion_tokens = usage
        else:
            # Fallback for invokers whose stdout has no --json event stream
            # (e.g. a test's fake invoker) -- a rough placeholder so the
            # ceiling still moves rather than never triggering in tests.
            prompt_tokens, completion_tokens = len(prompt) // 4, 0
        self._log_trace({
            "event": "investigate_done", "node_id": candidate.node_id,
            "decision": verdict.decision, "vuln_class": verdict.vuln_class,
            "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
        })
        self.budget.spend(tokens=prompt_tokens + completion_tokens, tool_calls=1)
        return verdict

    def run(self, candidates: list[Candidate]) -> tuple[list[Finding], list[str]]:
        """Works `candidates` strong-signal-first, then by score descending.
        Returns (findings, not_investigated_node_ids). Stops cleanly (not
        mid-candidate) once the per-audit budget is exhausted, recording the
        untouched tail honestly rather than silently dropping it.
        """
        ordered = sorted(candidates, key=lambda c: (not c.strong_signal, -c.score))
        not_investigated: list[str] = []
        findings: list[Finding] = []

        for i, candidate in enumerate(ordered):
            if self.budget.exhausted():
                not_investigated.extend(c.node_id for c in ordered[i:])
                self._log_trace({"event": "ceiling_reached", "remaining": len(ordered) - i})
                break

            bundle_json, contract = _bundle_json(self.pg, self.bundle_builder, candidate.node_id)
            self.memory.contract_summaries.setdefault(contract, bundle_json["contract_summary"])

            verdict = self._investigate_one(candidate, bundle_json)
            if verdict is None:
                not_investigated.append(candidate.node_id)
                continue

            if verdict.decision == "confirm" and verdict.mechanism and (verdict.file or verdict.lines):
                self.memory.confirmed.append(verdict)
                node_data = self.pg.graph.nodes.get(candidate.node_id, {})
                findings.append(Finding(
                    title=f"{(verdict.vuln_class or 'issue').replace('_', ' ').capitalize()} in {contract}",
                    contract=contract,
                    vuln_class=verdict.vuln_class,
                    severity=verdict.severity,
                    mechanism=verdict.mechanism,
                    file=verdict.file or node_data.get("file"),
                    lines=verdict.lines or node_data.get("lines", []),
                    fix=verdict.fix,
                    source_node_ids=[candidate.node_id],
                ))
            else:
                self.memory.rejected.append(verdict)

        return findings, not_investigated
