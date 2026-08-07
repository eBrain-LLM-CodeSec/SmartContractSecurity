"""Arm A: one bounded LLM judgment call per bundle -- no repository tools,
no ability to search additional files, no evidence beyond what's in the
bundle. See BUNDLE_LLM_VS_CODEX_AGENT_PREREGISTRATION.md sec. "Arm A".
"""
from __future__ import annotations

from a4v.llm import ChatClient, extract_last_fenced_json

ARM_A_SYSTEM_PROMPT = (
    "You are an EthTrust-guided smart-contract evidence reviewer. You will be given "
    "exactly one EthTrust requirement and exactly one evidence bundle describing ONE "
    "candidate location. You have NO ability to search the repository, request "
    "additional files, or see any code beyond what is given to you below. Judge only "
    "whether the described behavior AT THIS SPECIFIC CANDIDATE LOCATION satisfies, "
    "violates, or cannot yet be judged against the requirement -- do not judge the "
    "codebase as a whole, and do not extrapolate a location-level judgment into a "
    "target-wide conformance claim. Base your judgment ONLY on the requirement text "
    "and evidence given; do not assume facts not stated. Return ONLY the exact JSON "
    "object requested, as a single fenced ```json code block, with no other text."
)

OUTPUT_SCHEMA_INSTRUCTIONS = """Return exactly this JSON object (fenced as ```json ... ```):
{
  "decision": "PASS | FAIL | INCONCLUSIVE | INSUFFICIENT_EVIDENCE",
  "reasoning_summary": "...",
  "supporting_facts": ["..."],
  "missing_facts": ["..."],
  "requirement_citations": ["..."],
  "code_citations": ["..."],
  "confidence": "HIGH | MEDIUM | LOW"
}"""


def build_arm_a_user_message(requirement_text: str, context_bundle_text: str,
                              candidate_location: str, evidence_bundle_text: str,
                              known_limitations: list[str]) -> str:
    limitations_block = "\n".join(f"- {l}" for l in known_limitations) if known_limitations else "(none stated)"
    return f"""EthTrust requirement:
{requirement_text}

Applicable context (definitions / parent section / related requirements):
{context_bundle_text}

Candidate location under judgment: {candidate_location}

Evidence bundle for this candidate (this is ALL the evidence you have -- you cannot request more):
{evidence_bundle_text}

Known limitations of this evidence, as stated by the tool that produced it:
{limitations_block}

Question: at this specific candidate/location ({candidate_location}), does the observed
behavior satisfy or violate the requirement above? Do not ask or answer whether the
whole Tested Code conforms -- judge only this location.

{OUTPUT_SCHEMA_INSTRUCTIONS}"""


def run_arm_a(chat_client: ChatClient, requirement_text: str, context_bundle_text: str,
              candidate_location: str, evidence_bundle_text: str,
              known_limitations: list[str]) -> dict:
    user_msg = build_arm_a_user_message(requirement_text, context_bundle_text, candidate_location,
                                         evidence_bundle_text, known_limitations)
    messages = [
        {"role": "system", "content": ARM_A_SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    result = chat_client.complete(messages, temperature=0.0)
    decision = extract_last_fenced_json(result.content)
    return {
        "decision_raw": decision,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "cost_usd": result.cost_usd,
        "cached": result.cached,
        "user_message": user_msg,
        "system_prompt": ARM_A_SYSTEM_PROMPT,
        "raw_response": result.content,
    }
