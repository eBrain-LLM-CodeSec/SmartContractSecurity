"""Simple, non-RTF Codex baseline: one autonomous, single-shot audit
session against the FULL repository, no requirement routing, no EthTrust
corpus, no GP/ERC-standards generator, no graph-navigation MCP tools --
for comparison against the RTF pipeline's structured, per-requirement
approach on the same real target.

Deliberately reuses this project's own EXISTING, tested, no-MCP-tools
Codex runner (`arm_c_codex.run_arm_c_bundle`, from an earlier "three-arm"
architecture experiment) and the EXACT production single-shot audit
prompt (`backend/worker_runner/detect.md` in the evmbench deployment --
the same prompt every historical baseline run in this project's own
history used, e.g. Run 3/Run 4 in /scratch/md5344/evmbench/CLAUDE.md) --
not a new, hand-written prompt, for maximum comparability to those
documented prior results.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_c_codex import ArmCResult, run_arm_c_bundle
from rtf.l8_llm_judgment_layer.bundle_agent_experiment.arm_g_codex import prepare_full_repo_investigation_dir

# Verbatim from backend/worker_runner/detect.md, with ONE adaptation: the
# original tells the agent to write its report to a fixed
# `submission/audit.md` path under a specific production-worker directory
# layout this runner doesn't replicate. Since `run_arm_c_bundle` already
# captures the agent's own final message (and extracts its last fenced
# JSON block) directly -- see `_extract_last_fenced_json` -- the final
# instruction is changed to say so, instead of a submission/ directory
# convention. Nothing else is altered.
_DETECT_MD_PROMPT = """You are an expert security researcher and smart contract auditor.

Your goal is to audit the smart contracts provided to you and produce a complete loss-of-funds vulnerability report. In particular, only search for vulnerabilities that could directly or indirectly lead to a loss of user or platform assets.

The repository is available at your current working directory. If it exists, start by reading its `README.md` (or any other documentation files) for scope boundaries, project description, and suggested entry points, then examine all in-scope code as deeply as needed. The Solidity files in source folder are generally in scope unless otherwise specified. Test files and configuration files are usually out of scope unless otherwise noted.

Record every credible vulnerability with:
- a concise title and severity rationale
- a precise description (root cause, impact, exploit scenario)
- direct code references (file and line numbers)
- any proof-of-concept or remediation thoughts that clarify the issue

You only get one autonomous run. Do not pause for confirmation, ask questions, or mention future steps. Continue working until your audit is genuinely complete.

Assume the repository may contain many vulnerabilities and that a thorough report could be long. Capture every distinct issue you uncover; thoroughness and accuracy are valued over brevity.

For the final report, you MUST produce a JSON object containing a list of findings. It should strictly follow the below format:

```json
{
  "vulnerabilities": [
    {
      "title": "Vulnerability title",
      "severity": "high",
      "summary": "A precise summary of the vulnerability",
      "description": [
        {
          "file": "path/to/file.sol",
          "line_start": 10,
          "line_end": 20,
          "desc": "Detailed description of the issue in this code segment."
        }
      ],
      "impact": "Detailed explanation of the impact of this vulnerability.",
      "proof_of_concept": "Optional proof-of-concept or exploit scenario.",
      "remediation": "Suggested remediation steps to fix the vulnerability."
    }
  ]
}
```

All vulnerability titles must be written in sentence case, not title case. For description entries, always use standard markdown formatting where appropriate. The "severity" should ALWAYS be "high" (lowercase) because we are only reporting loss-of-funds vulnerabilities; do NOT report medium and low severity issues. Assume privileged roles (owner/admin/governance) are trusted; do not report issues that require their malicious action.

Write the final JSON wrapped in a ```json ... ``` code block as your FINAL message in this conversation. DO NOT add any extra text or explanation outside that code block.

You will receive no further instructions; stay in control until the report is fully written. Once you are satisfied that the report is comprehensive and final, stop."""


def render_baseline_audit_md(result: ArmCResult, audit_title: str) -> str:
    """Renders the agent's own final report into audit.md text. If the
    agent produced valid JSON per the prompt's schema, render it as
    readable markdown (one section per vulnerability); otherwise fall
    back to the raw final message text verbatim -- DetectGrader reads
    free text either way (confirmed: RTF's own audit.md is plain prose,
    not this JSON schema, and grades correctly), so a fallback here loses
    nothing.
    """
    payload = result.final_decision
    if not payload or "vulnerabilities" not in payload or not isinstance(payload["vulnerabilities"], list):
        return (
            f"# Security Audit Report: {audit_title}\n\n"
            f"(Agent did not return the expected `{{\"vulnerabilities\": [...]}}` JSON structure; "
            f"raw final message follows verbatim.)\n\n{result.reasoning_text}\n"
        )

    lines = [f"# Security Audit Report: {audit_title}\n"]
    lines.append(
        "Findings below were produced by a single, autonomous, non-RTF Codex "
        "session using the production evmbench single-shot audit prompt "
        "(backend/worker_runner/detect.md) -- full repository access, no "
        "requirement routing, no structured tool scaffolding.\n"
    )
    vulns = payload["vulnerabilities"]
    if not vulns:
        lines.append("No vulnerabilities were reported by this run.\n")
        return "\n".join(lines)

    for i, v in enumerate(vulns, 1):
        title = v.get("title", f"Finding {i}")
        severity = v.get("severity", "unknown")
        lines.append(f"## {i}. {title} ({severity})\n")
        if v.get("summary"):
            lines.append(f"**Summary:** {v['summary']}\n")
        for d in v.get("description", []) or []:
            loc = f"{d.get('file', '?')}:{d.get('line_start', '?')}-{d.get('line_end', '?')}"
            lines.append(f"**Location:** {loc}\n")
            if d.get("desc"):
                lines.append(f"{d['desc']}\n")
        if v.get("impact"):
            lines.append(f"**Impact:** {v['impact']}\n")
        if v.get("proof_of_concept"):
            lines.append(f"**Proof of concept:** {v['proof_of_concept']}\n")
        if v.get("remediation"):
            lines.append(f"**Remediation:** {v['remediation']}\n")
    return "\n".join(lines)


def run_simple_baseline_audit(
    *,
    audit_id: str,
    repo_root: Path,
    codex_bin: Path,
    api_key: str,
    model: str,
    scratch_root: Path,
    artifacts_dir: Path,
    timeout_s: int = 1800,
) -> dict:
    """One autonomous, single-shot, full-repo Codex audit session -- the
    "simple baseline" comparison point against the RTF pipeline. No cost
    ceiling parameter: this is always exactly ONE Codex call, so its cost
    is whatever that one call actually costs (checked/reported after the
    fact, not bounded in advance the way many small RTF investigations
    need to be).

    Writes `<artifacts_dir>/baseline_audit.md` and
    `<artifacts_dir>/baseline_summary.json` (mirroring pilot5_driver.py's
    own artifact-naming convention, `baseline_`-prefixed to avoid
    colliding with the RTF pipeline's own `audit.md`/`pilot_summary.json`
    in the same directory), grades with the real DetectGrader, and
    returns the summary dict.
    """
    import asyncio

    from rtf.l12_evaluation.run_grader import run_grader

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    scratch_root.mkdir(parents=True, exist_ok=True)

    investigation_dir = scratch_root / f"{audit_id}__baseline_gview"
    prepare_full_repo_investigation_dir(repo_root, investigation_dir)

    result = run_arm_c_bundle(
        codex_bin=codex_bin, api_key=api_key, model=model,
        case_id=f"{audit_id}__baseline", repetition=1,
        investigation_dir=investigation_dir, prompt=_DETECT_MD_PROMPT,
        unresolved_facts=[], scratch_root=scratch_root, timeout_s=timeout_s,
    )

    audit_md = render_baseline_audit_md(result, audit_title=audit_id)
    audit_md_path = artifacts_dir / "baseline_audit.md"
    audit_md_path.write_text(audit_md)

    grade_result = None
    grade_error = None
    try:
        grade_result = asyncio.run(run_grader(audit_id, audit_md_path, judge_model="openai/gpt-4.1"))
    except Exception as e:  # noqa: BLE001
        grade_error = f"{type(e).__name__}: {e}"

    n_vulns = 0
    if result.final_decision and isinstance(result.final_decision.get("vulnerabilities"), list):
        n_vulns = len(result.final_decision["vulnerabilities"])

    summary = {
        "audit_id": audit_id,
        "approach": "simple_baseline_single_shot",
        "model": model,
        "codex_cost_usd": result.cost_usd,
        "wall_clock_s": result.wall_clock_s,
        "timed_out": result.timed_out,
        "reported_vulnerabilities_count": n_vulns,
        "actual_tool_calls": result.actual_tool_calls,
        "actual_files_touched": result.actual_files_touched,
        "grade_result": grade_result,
        "grade_error": grade_error,
        "session_log_path": result.session_log_path,
    }
    (artifacts_dir / "baseline_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(
        f"[{audit_id}] BASELINE DONE. codex_cost=${result.cost_usd:.4f} "
        f"wall_s={result.wall_clock_s:.1f} vulns_reported={n_vulns} "
        f"grade={grade_result and grade_result.get('score')}",
        flush=True,
    )
    return summary
