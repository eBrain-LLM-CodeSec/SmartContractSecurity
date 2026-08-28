import json
from pathlib import Path

RUN_DIR = Path("/scratch/md5344/evmbench/rtf_canto_full_rerun_sol_20260828")

verdicts = {}
raw_entries = {}
for line in (RUN_DIR / "checkpoint.jsonl").read_text().splitlines():
    line = line.strip()
    if not line:
        continue
    rec = json.loads(line)
    for pid, v in rec.get("verdicts", {}).items():
        verdicts[pid] = v
    for pid, e in rec.get("raw_entries", {}).items():
        raw_entries[pid] = e


def is_semantic(pid):
    return pid.startswith("semantic__")


fail_ids = [pid for pid, v in verdicts.items() if v["conformance_state"] == "FAIL"]
sem_fails = [p for p in fail_ids if is_semantic(p)]
struct_fails = [p for p in fail_ids if not is_semantic(p)]
print(f"Total resolved: {len(verdicts)}  FAIL: {len(fail_ids)} (semantic: {len(sem_fails)}, structural: {len(struct_fails)})")

lines = ["# Security Audit Report: 2024-01-canto (security-agent kernel, GPT-5.6 Sol investigator)\n"]
lines.append(
    "Findings below combine RTF's deterministic EthTrust (81-requirement "
    "corpus) + real ERC/EIP-standards-generated structural predicates "
    "with RTF v2's semantic property generation + grounding, investigated "
    "by the custom security-agent kernel (native update_investigation/"
    "conclude tools, anti-anchoring PASS gate, rank_evidence scope-filter fix, "
    "and OpenAI-strict-schema tools.py fix applied) with GPT-5.6 Sol as the "
    "investigator model, against a real whole-project Foundry compile "
    "(compile_via_foundry=True).\n"
)
for i, pid in enumerate(sorted(fail_ids), 1):
    entry = raw_entries.get(pid, {})
    source = "semantic (RTF v2 code-derived)" if is_semantic(pid) else "structural (EthTrust/ERC-derived)"
    lines.append(f"## {i}. `{pid}` [{source}]\n")
    loc = entry.get("vulnerable_location") or ", ".join(entry.get("files_read") or []) or "unknown"
    lines.append(f"**Location:** {loc}\n")
    if entry.get("claim"):
        lines.append(f"**Property tested:** {entry['claim']}\n")
    if entry.get("reasoning"):
        lines.append(f"**Reasoning:** {entry['reasoning']}\n")
    if entry.get("counterexample_result"):
        lines.append(f"**Counterexample:** {entry['counterexample_result']}\n")

audit_md = "\n".join(lines)
(RUN_DIR / "audit.md").write_text(audit_md, encoding="utf-8")
print(f"Wrote audit.md ({len(fail_ids)} FAIL findings)")
