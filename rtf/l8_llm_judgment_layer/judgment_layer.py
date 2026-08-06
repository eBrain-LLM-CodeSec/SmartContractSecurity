"""L8: the shared LLM Judgment Layer -- orchestrates a4v.llm.ChatClient
(existing, reused as-is for caching/retries/JSON-extraction, not
duplicated) into the plan's structured, validated judgment protocol.

LIVE EXECUTION IS NOT WIRED UP IN THIS PASS. This module is complete and
independently testable (schema.py, citation_check.py, stability.py all
have no live-LLM dependency and are exercised by selftest.py), but
`LLMJudgmentLayer.judge()` requires a real `ChatClient` (which itself
needs an OpenRouter API key file and a chosen model) and a real target
repository -- neither is provisioned for Track A yet. This mirrors how
L4/L6 components were left "soundly derived, not yet implemented" rather
than faked; building the plumbing now means it's ready the moment a
target repo and credentials are chosen, without inventing fake results in
the meantime.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from a4v.llm import (
    RETRY_MAX_ATTEMPTS,
    RETRY_WAIT_MAX,
    RETRY_WAIT_MIN,
    RETRY_WAIT_MULTIPLIER,
    ChatClient,
)

from .citation_check import verify_evidence_citations
from .schema import SCHEMA_VERSION, validate_judgment
from .stability import compute_stability

PROMPT_VERSION = "rtf-l8-v1"  # bump on any prompt template change; pinned per plan L8 rule

# Pinned L8 sampling defaults. Neither field was ever sent by a4v.llm.ChatClient
# before this change (see AR-014) -- provider/model defaults applied silently
# and invisibly. Pinned here, specifically for RTF's own L8 calls, rather than
# changing ChatClient's own defaults, which would also affect the Commentator/
# Auditor pipeline (a4v/auditor.py, a4v/commentator.py) that reuses the same
# shared client with no reason to change their behavior.
# top_p=1.0: no nucleus-sampling restriction beyond temperature=0.0's own
#   near-deterministic greedy selection -- an explicit no-op pin, not a new
#   behavior, chosen so the field is *recorded*, not so it changes sampling.
# max_tokens=4096: generous headroom for a JSON judgment object (reasoning_
#   summary + evidence + citations rarely exceeds a few hundred tokens) plus
#   any provider-side reasoning tokens some models (e.g. codex-max) may emit
#   before the fenced JSON. Not empirically tuned against a truncation case;
#   logged as a procedural, not measured, choice (see AR-014).
DEFAULT_TOP_P = 1.0
DEFAULT_MAX_TOKENS = 4096


def build_judgment_prompt(requirement_context_bundle: dict, question: str) -> list[dict]:
    """Builds the message list for a judgment call. The prompt is generated
    FROM the requirement's own context bundle (L2) -- self, definitions,
    overriding/exception text, parent-section context -- per the plan's
    'context bundle, not isolated sentence' rule, plus the specific,
    narrow `question` a component asks (e.g. an M requirement's exception
    condition, or a Q requirement's evidence-assessment rubric item).
    General smart-contract vulnerability knowledge is deliberately NOT
    injected here -- only what the bundle and the question state.
    """
    bundle = requirement_context_bundle["bundle"]
    context_parts = [f"Requirement: {bundle['self']}"]
    if bundle.get("parent_section_context"):
        context_parts.append(f"Section context: {bundle['parent_section_context']}")
    for d in bundle.get("definitions", []):
        context_parts.append(f"Definition ({d['id']}): {d['text']}")
    for o in bundle.get("overriding_requirements", []):
        context_parts.append(f"Related requirement ({o['req_id']}): {o['normative_text']}")
    for e in bundle.get("exceptions", []):
        context_parts.append(f"Exception ({e['req_id']}): {e['normative_text']}")
    for r in bundle.get("referenced_requirements", []):
        context_parts.append(f"Referenced requirement ({r['req_id']}): {r['normative_text']}")

    system = (
        "You are a semantic reviewer assisting a standards-conformance framework, "
        "not a conformance authority. You must return ONLY the JSON object described "
        "below, wrapped in a ```json fence. You are explicitly permitted -- and expected, "
        "when the evidence does not support a confident PASS/FAIL -- to answer "
        "INCONCLUSIVE or INSUFFICIENT_EVIDENCE instead. Every PASS or FAIL you return "
        "MUST be backed by at least one specific, checkable evidence citation "
        "(file path + line number or symbol name) -- confidence alone is never sufficient.\n\n"
        "Return exactly this JSON shape:\n"
        '{"decision": "PASS|FAIL|INCONCLUSIVE|INSUFFICIENT_EVIDENCE", '
        '"requirement_citations": [...], '
        '"evidence": [{"source": "...", "location": "path:line_or_symbol", "claim": "..."}], '
        '"reasoning_summary": "...", "open_questions": [...], "confidence": "HIGH|MEDIUM|LOW"}'
    )
    user = "\n\n".join(context_parts) + f"\n\nQuestion: {question}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


@dataclass
class LLMJudgmentLayer:
    chat_client: ChatClient
    model_version: str  # pinned model identifier, e.g. "openai/gpt-5.1-codex-max"
    top_p: float = DEFAULT_TOP_P
    max_tokens: int = DEFAULT_MAX_TOKENS

    def _judgment_config_metadata(self, messages: list[dict], temperature: float, cache_key: str) -> dict:
        """The full LLM-call configuration for ONE judge_once() call, stamped
        onto every returned judgment artifact (Phase H work item 1: "every
        future judgment artifact must automatically store this metadata").
        Every field here is read from the actual objects making the call
        (self.chat_client, the module-level retry constants re-exported from
        a4v.llm) rather than duplicated by hand, so it can't silently drift
        from what was really sent.
        """
        return {
            "provider": "openrouter",
            "model_id": self.model_version,
            "api_base_url": self.chat_client.base_url,
            "temperature": temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "timeout_seconds": self.chat_client.timeout,
            "retry_max_attempts": RETRY_MAX_ATTEMPTS,
            "retry_wait_multiplier": RETRY_WAIT_MULTIPLIER,
            "retry_wait_min": RETRY_WAIT_MIN,
            "retry_wait_max": RETRY_WAIT_MAX,
            "prompt_version": PROMPT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "cache_key": cache_key,
        }

    def judge_once(
        self,
        requirement_context_bundle: dict,
        question: str,
        repo_root: Path | None = None,
        temperature: float = 0.0,
        bypass_cache: bool = False,
    ) -> dict:
        messages = build_judgment_prompt(requirement_context_bundle, question)
        cache_key = self.chat_client._cache_key(messages, temperature, self.top_p, self.max_tokens)
        if bypass_cache:
            # ChatClient caches by exact (model, messages, temperature, top_p,
            # max_tokens) -- fine for normal single-shot use, but repeated
            # "independent" calls with identical inputs (second-pass review,
            # stability testing) would otherwise just replay the SAME cached
            # response every time, silently defeating both mechanisms
            # (disagreement can never be detected, flip rate is trivially
            # always 0). Caught live during RTF L8 validation (2026-08-06).
            # Deleting the cache entry just before the call forces a genuine
            # fresh completion; only used by judge_with_second_pass/
            # judge_stability's repeat calls, not by ordinary single
            # judge_once() use, where caching stays valuable.
            cache_path = self.chat_client._cache_path(cache_key)
            cache_path.unlink(missing_ok=True)
        data, chat_result = self.chat_client.complete_json(
            messages, temperature=temperature, top_p=self.top_p, max_tokens=self.max_tokens
        )

        # Fill in the framework-tracked fields the model isn't asked to invent itself.
        data.setdefault("second_pass_agreement", "N/A")
        data["model_version"] = self.model_version
        data["prompt_version"] = PROMPT_VERSION
        data["run_id"] = str(uuid.uuid4())
        data["schema_version"] = SCHEMA_VERSION
        data["judgment_config"] = self._judgment_config_metadata(messages, temperature, cache_key)

        errors = validate_judgment(data)
        if errors:
            raise ValueError(f"LLM judgment failed schema validation: {errors}\nRaw: {data}")

        if repo_root is not None and data["evidence"]:
            data["citation_check"] = verify_evidence_citations(data["evidence"], repo_root)

        return data

    def judge_with_second_pass(
        self, requirement_context_bundle: dict, question: str, repo_root: Path | None = None
    ) -> dict:
        """Two independent calls (temperature 0 each, but the model may still
        vary run-to-run) with explicit disagreement detection -- per plan L8
        rule, a second independent review pass is mandatory before an L6/L7
        consumer may trust a PASS/FAIL. The second call bypasses the cache
        (see judge_once's bypass_cache docstring) -- without that, this method
        would silently always report AGREE, since it would just be comparing
        the first response against itself."""
        first = self.judge_once(requirement_context_bundle, question, repo_root)
        second = self.judge_once(requirement_context_bundle, question, repo_root, bypass_cache=True)
        agree = first["decision"] == second["decision"]
        first["second_pass_agreement"] = "AGREE" if agree else "DISAGREE"
        second["second_pass_agreement"] = "AGREE" if agree else "DISAGREE"
        # Current design: both passes route through this SAME LLMJudgmentLayer
        # instance (same self.chat_client, same self.model_version) -- i.e.
        # both passes always use the same model today. Recorded explicitly
        # (Phase H work item 1) rather than left implicit, since item 8 asks
        # this project to separately investigate whether the second pass
        # should ever use a DIFFERENT model/role (independent judge vs.
        # structured verifier) -- that comparison needs this field to exist
        # first, to know what today's baseline actually is.
        same_model = first["model_version"] == second["model_version"]
        return {"first_pass": first, "second_pass": second, "agree": agree, "same_model": same_model}

    def judge_stability(
        self, requirement_context_bundle: dict, question: str, n_runs: int = 10, repo_root: Path | None = None
    ) -> dict:
        """Runs beyond the first bypass the cache (see judge_once's
        bypass_cache docstring) -- otherwise every run after the first would
        just replay the same cached response, and flip_rate would be
        meaningless-but-always-zero rather than a real measurement."""
        runs = [
            self.judge_once(requirement_context_bundle, question, repo_root, bypass_cache=(i > 0))
            for i in range(n_runs)
        ]
        return {"runs": runs, "stability": compute_stability(runs)}
