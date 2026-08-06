"""L8 LLM Judgment Layer: structured output schema + deterministic validation.

Per the plan: LLMs are semantic reviewers, not conformance authorities.
Every judgment call must return this exact shape, and `validate_judgment`
must pass before the result is trusted anywhere else in the framework
(L6/L7 consumers, L12 evaluation). Confidence never substitutes for
evidence and never by itself changes `decision` -- `validate_judgment`
enforces that a HIGH-confidence PASS/FAIL with zero evidence entries is
rejected, not silently accepted.
"""
from __future__ import annotations

# Bump on any REQUIRED_FIELDS change or judgment_config schema change (the
# "judgment_config" block's own internal shape -- see judgment_layer.py's
# _judgment_config_metadata()). Distinct from PROMPT_VERSION (judgment_layer.py),
# which tracks the prompt TEMPLATE text.
SCHEMA_VERSION = "l8-judgment-schema-v2-with-config-metadata"

DECISIONS = {"PASS", "FAIL", "INCONCLUSIVE", "INSUFFICIENT_EVIDENCE"}
CONFIDENCES = {"HIGH", "MEDIUM", "LOW"}
AGREEMENT_VALUES = {"AGREE", "DISAGREE", "N/A"}

REQUIRED_FIELDS = {
    "decision",
    "requirement_citations",
    "evidence",
    "reasoning_summary",
    "open_questions",
    "confidence",
    "model_version",
    "prompt_version",
    "run_id",
    "second_pass_agreement",
    "schema_version",
    "judgment_config",
}


def validate_judgment(d: dict) -> list[str]:
    """Deterministic schema validation. Returns a list of error strings;
    empty list means the judgment is well-formed (NOT that it's correct --
    citation existence and second-pass agreement are separate checks)."""
    errors: list[str] = []

    missing = REQUIRED_FIELDS - d.keys()
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")
        return errors  # can't check further without the base shape

    if d["decision"] not in DECISIONS:
        errors.append(f"decision {d['decision']!r} not in {sorted(DECISIONS)}")

    if not isinstance(d["requirement_citations"], list):
        errors.append("requirement_citations must be a list")

    if not isinstance(d["evidence"], list):
        errors.append("evidence must be a list")
    else:
        for i, ev in enumerate(d["evidence"]):
            if not isinstance(ev, dict) or not {"source", "location", "claim"} <= ev.keys():
                errors.append(f"evidence[{i}] missing source/location/claim: {ev!r}")

    if not isinstance(d["reasoning_summary"], str) or not d["reasoning_summary"].strip():
        errors.append("reasoning_summary must be a non-empty string")

    if not isinstance(d["open_questions"], list):
        errors.append("open_questions must be a list")

    if d["confidence"] not in CONFIDENCES:
        errors.append(f"confidence {d['confidence']!r} not in {sorted(CONFIDENCES)}")

    if not isinstance(d["model_version"], str) or not d["model_version"]:
        errors.append("model_version must be a pinned, non-empty string")

    if not isinstance(d["prompt_version"], str) or not d["prompt_version"]:
        errors.append("prompt_version must be a pinned, non-empty string")

    if not isinstance(d["run_id"], str) or not d["run_id"]:
        errors.append("run_id must be a non-empty string")

    if d["second_pass_agreement"] not in AGREEMENT_VALUES:
        errors.append(f"second_pass_agreement {d['second_pass_agreement']!r} not in {sorted(AGREEMENT_VALUES)}")

    if not isinstance(d["schema_version"], str) or not d["schema_version"]:
        errors.append("schema_version must be a pinned, non-empty string")

    # judgment_config: the full LLM-call configuration metadata (RTF Phase H
    # item 1 -- "every future judgment artifact must automatically store this
    # metadata"). Checked for presence of its required keys, not just
    # dict-ness, so a partially-populated config can't silently pass.
    _JUDGMENT_CONFIG_REQUIRED_KEYS = {
        "provider", "model_id", "api_base_url", "temperature", "top_p", "max_tokens",
        "timeout_seconds", "retry_max_attempts", "retry_wait_multiplier", "retry_wait_min",
        "retry_wait_max", "prompt_version", "schema_version", "cache_key",
    }
    if not isinstance(d["judgment_config"], dict):
        errors.append("judgment_config must be a dict")
    else:
        missing_cfg = _JUDGMENT_CONFIG_REQUIRED_KEYS - d["judgment_config"].keys()
        if missing_cfg:
            errors.append(f"judgment_config missing required keys: {sorted(missing_cfg)}")

    # The rule that gives 'errors' below teeth: confidence never substitutes
    # for evidence. A PASS/FAIL with no evidence at all is a defect
    # regardless of how confident the model claims to be.
    if d["decision"] in ("PASS", "FAIL") and not d.get("evidence"):
        errors.append(
            f"decision={d['decision']!r} with zero evidence entries -- "
            "confidence must never substitute for evidence (plan L8 rule)"
        )

    return errors
