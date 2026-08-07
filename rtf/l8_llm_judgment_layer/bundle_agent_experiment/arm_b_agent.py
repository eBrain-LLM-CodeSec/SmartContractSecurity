"""Arm B: one fresh tool-using agent session per bundle -- a hand-built
ReAct-style loop over the same model as Arm A (no native function-calling
available; see CODEX_SYSTEM_PROMPT_v1.md's implementation note for why
this substitutes for the real Codex CLI, which lives only inside the
SLURM/Singularity worker stack). Each call to run_arm_b starts a brand
new `messages` list -- no cross-bundle memory, per the research-integrity
constraint (no cross-bundle agent memory).
"""
from __future__ import annotations

from pathlib import Path

from a4v.llm import ChatClient, extract_last_fenced_json

from .tools import MAX_TOOL_ACTIONS, ToolBudget, execute_action

MAX_TURNS = 14  # hard absolute cap on API calls per bundle, independent of the
                # tool-action budget -- guarantees termination/cost bound even
                # if the model never emits valid JSON or ignores instructions

FORCED_FINAL_MESSAGE = (
    "Your tool-action budget is exhausted (8/8 used). You must now return your "
    "final decision using only what you have already discovered -- no further tool "
    "calls will be executed. If a material fact remains unresolved, return "
    "INCONCLUSIVE or INSUFFICIENT_EVIDENCE with stop_reason: \"BUDGET_EXHAUSTED\". "
    "Respond with EXACTLY one fenced JSON object: {\"action\": \"final\", \"decision\": {...}}."
)

INVALID_JSON_NUDGE = (
    "Your last response was not a single valid fenced JSON object. Reply with EXACTLY "
    "one fenced ```json code block containing either a tool-call action or your final "
    "decision, per the protocol -- no other text."
)


def build_arm_b_initial_message(requirement_text: str, context_bundle_text: str,
                                 candidate_location: str, evidence_bundle_text: str,
                                 unresolved_facts: list[str], repo_root: Path) -> str:
    unresolved_block = "\n".join(f"- {f}" for f in unresolved_facts) if unresolved_facts else "(none explicitly stated)"
    return f"""EthTrust requirement:
{requirement_text}

Applicable context (definitions / parent section / related requirements):
{context_bundle_text}

Candidate location under investigation: {candidate_location}

Initial evidence bundle for this candidate (a starting hypothesis, not ground truth -- you may verify it):
{evidence_bundle_text}

Explicitly unresolved facts noted by the tool that produced this evidence:
{unresolved_block}

Repository root you may investigate: {repo_root}
Tool-action budget: {MAX_TOOL_ACTIONS} actions total for this investigation.

Begin your investigation, or return your final decision immediately if the initial
evidence already fully resolves the candidate. Respond with EXACTLY one fenced JSON
object per the protocol."""


def _fallback_result(candidate_location: str, req_id: str, budget: ToolBudget, reason: str) -> dict:
    return {
        "decision": "INSUFFICIENT_EVIDENCE",
        "candidate": {"contract": None, "function": None, "location": candidate_location},
        "requirement_id": req_id,
        "verified_initial_evidence": [],
        "new_evidence_found": [],
        "relational_facts": [],
        "protections_found": [],
        "missing_or_unresolved_facts": [f"agent loop did not produce a valid final decision ({reason})"],
        "reasoning_summary": f"Synthesized fallback: {reason}. This is NOT a model-produced judgment.",
        "confidence": "LOW",
        "files_inspected": sorted(budget.files_opened),
        "tool_actions_used": budget.actions_used,
        "stop_reason": "BUDGET_EXHAUSTED" if "budget" in reason else "GENUINE_AMBIGUITY",
    }


def run_arm_b(chat_client: ChatClient, system_prompt: str, req_id: str, requirement_text: str,
              context_bundle_text: str, candidate_location: str, evidence_bundle_text: str,
              unresolved_facts: list[str], repo_root: Path) -> dict:
    budget = ToolBudget(repo_root=repo_root)
    initial_msg = build_arm_b_initial_message(requirement_text, context_bundle_text, candidate_location,
                                               evidence_bundle_text, unresolved_facts, repo_root)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": initial_msg},
    ]
    turns = []
    final = None
    forced_final_issued = False
    invalid_json_retries = 0

    for turn_idx in range(MAX_TURNS):
        result = chat_client.complete(messages, temperature=0.0)
        messages.append({"role": "assistant", "content": result.content})
        turns.append({
            "turn": turn_idx, "raw_response": result.content,
            "prompt_tokens": result.prompt_tokens, "completion_tokens": result.completion_tokens,
            "cost_usd": result.cost_usd, "cached": result.cached,
        })

        try:
            action = extract_last_fenced_json(result.content)
        except Exception:
            invalid_json_retries += 1
            if invalid_json_retries > 2:
                final = _fallback_result(candidate_location, req_id, budget, "model repeatedly returned invalid JSON")
                break
            messages.append({"role": "user", "content": INVALID_JSON_NUDGE})
            continue

        kind = action.get("action")
        if kind == "final":
            final = action.get("decision", action)
            break
        if kind is None and "decision" in action:
            # tolerate a bare final-decision object without the {"action": "final", ...} wrapper
            final = action
            break

        if budget.actions_used >= budget.max_actions:
            if forced_final_issued:
                final = _fallback_result(candidate_location, req_id, budget,
                                          "model issued another tool call after budget exhaustion + forced-final instruction")
                break
            messages.append({"role": "user", "content": FORCED_FINAL_MESSAGE})
            forced_final_issued = True
            continue

        try:
            obs = execute_action(repo_root, budget, action)
        except Exception as e:
            obs = f"ERROR executing action: {e}"
        messages.append({
            "role": "user",
            "content": f"Tool result:\n\n{obs}\n\nRemaining tool-action budget: {budget.remaining()}. "
                       f"Continue investigating or return your final decision as instructed.",
        })

    if final is None:
        final = _fallback_result(candidate_location, req_id, budget, "max_turns exhausted without a final decision")

    return {
        "final": final,
        "trace": budget.trace,
        "turns": turns,
        "tool_actions_used": budget.actions_used,
        "files_opened": sorted(budget.files_opened),
        "expansion_hops": budget.expansion_hops(),
        "system_prompt": system_prompt,
        "initial_user_message": initial_msg,
    }
