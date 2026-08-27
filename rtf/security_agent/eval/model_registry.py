"""Model/provider configuration for the multi-model evaluation harness.

Deliberately NOT an elaborate provider framework (per the task spec): every
candidate model in this registry is reached the exact same way the GLM-5.3
and GPT-5.6 Sol capability-test scripts already reached their models --
`ResponsesChatClient` posting to OpenRouter's `/responses` endpoint, model
id passed straight through as a plain string. There is no per-provider HTTP
client here; the only genuinely provider-specific knobs this project has
ever needed in practice are `reasoning_effort` (some models are not
reasoning models at all, so the field may be irrelevant) and the tool-
schema `required`-field strictness gap discovered during the GPT-5.6 Sol
test (OpenAI/Azure enforces `strict: true` literally; GLM tolerates it
loosely) -- and that gap was already fixed once and for all by making
`build_tool_schemas()` always populate `required` with every declared
parameter (a wire-contract change, not a tool-behavior change), so it is
no longer a per-model flag at all. `preflight.py` exists specifically to
catch any FUTURE provider-specific incompatibility live, before spending
money on a real investigation, rather than this registry trying to
predict every provider's quirks in advance.

Every OpenRouter model id below was confirmed LIVE against
`GET https://openrouter.ai/api/v1/models` (a free, unauthenticated-cost
call) on 2026-08-27 -- not guessed. See MODEL_EVAL_HARNESS_IMPLEMENTATION_
REPORT.md for the exact query used.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

DEFAULT_OPENROUTER_KEY_FILE = "/scratch/md5344/evmbench/run/task5_secrets/openrouter.key"
"""Same shared secrets file every prior live run in this project has read
(`key_mode=proxy_static`, chmod 600) -- all candidate models below are
OpenRouter-hosted, so this one proxy key covers all of them. Not a
hardcoded secret VALUE, just the conventional path; the actual key is only
ever read from disk or environment at call time, never embedded in code or
written into any run artifact (see test_model_registry.py's secret-leakage
test)."""


@dataclass(frozen=True)
class ModelConfig:
    key: str
    """Short CLI-facing name, e.g. "deepseek-v4-pro"."""
    openrouter_model_id: str
    """Exact OpenRouter model slug, e.g. "deepseek/deepseek-v4-pro"."""
    display_name: str
    tier: int
    """Candidate priority per the task spec: 0=control (GPT-5.6 Sol), then
    1-4 in the order candidates should be tried (economic floor last)."""
    api_key_env: str = "OPENROUTER_API_KEY"
    """Checked FIRST, ahead of the shared key file -- lets a future direct
    (non-OpenRouter) integration for this model override cleanly without
    any code change here. All current candidates go through OpenRouter, so
    this defaults to the same env var for every entry; per-model overrides
    (DEEPSEEK_API_KEY, KIMI_API_KEY, MINIMAX_API_KEY) are still honored if
    set, per the task's explicit secret-management spec."""
    fallback_api_key_env: str | None = None
    """Optional model-specific env var name checked between api_key_env
    and the shared key file (e.g. "DEEPSEEK_API_KEY")."""
    reasoning_effort: str = "low"
    """Passed as `reasoning.effort` on the Responses API request. Matches
    the kernel's own default -- overridable per model since not every
    candidate is necessarily a reasoning model in the same sense GLM/Sol
    are; preflight surfaces whether the field is accepted at all."""
    context_length: int | None = None
    """Informational only (from OpenRouter's /models listing) -- this
    harness does not enforce it, since the single-property trimmed plan
    used throughout stays far under any of these limits."""
    notes: str = ""


MODEL_REGISTRY: dict[str, ModelConfig] = {
    "gpt-5.6-sol": ModelConfig(
        key="gpt-5.6-sol", openrouter_model_id="openai/gpt-5.6-sol",
        display_name="GPT-5.6 Sol", tier=0, context_length=None,
        notes="Tier 0 control -- the model Codex used successfully, and "
              "already validated once inside this same custom kernel "
              "(rtf_canto_gpt56sol_capability_test_20260827, 1/1). Re-run "
              "sparingly per Phase 13 -- prefer reusing that existing result.",
    ),
    "deepseek-v4-pro": ModelConfig(
        key="deepseek-v4-pro", openrouter_model_id="deepseek/deepseek-v4-pro",
        display_name="DeepSeek V4 Pro", tier=1,
        fallback_api_key_env="DEEPSEEK_API_KEY", context_length=1048576,
        notes="Tier 1, first candidate tested. Unpinned slug (tracks "
              "OpenRouter's default routing for this name) -- "
              "deepseek/deepseek-v4-pro-0813 also exists as a dated pin "
              "if reproducibility against a moving default becomes a "
              "concern later.",
    ),
    "kimi-k3": ModelConfig(
        key="kimi-k3", openrouter_model_id="moonshotai/kimi-k3",
        display_name="Kimi K3", tier=2,
        fallback_api_key_env="KIMI_API_KEY", context_length=1048576,
        notes="Tier 2 -- tested only if DeepSeek fails Canto qualification.",
    ),
    "minimax-m3": ModelConfig(
        key="minimax-m3", openrouter_model_id="minimax/minimax-m3",
        display_name="MiniMax M3", tier=3,
        fallback_api_key_env="MINIMAX_API_KEY", context_length=1048576,
        notes="Tier 3 -- tested only if DeepSeek and Kimi both fail.",
    ),
    "qwen3.6-35b-a3b": ModelConfig(
        key="qwen3.6-35b-a3b", openrouter_model_id="qwen/qwen3.6-35b-a3b",
        display_name="Qwen3.6-35B-A3B", tier=4,
        context_length=262144,
        notes="Optional Tier 4 -- economic floor/control, smallest active "
              "parameter count of the candidates.",
    ),
}


def get_model_config(key: str) -> ModelConfig:
    try:
        return MODEL_REGISTRY[key]
    except KeyError:
        raise KeyError(
            f"unknown model key {key!r} -- known keys: {sorted(MODEL_REGISTRY)}"
        ) from None


def resolve_api_key(config: ModelConfig, key_file: str = DEFAULT_OPENROUTER_KEY_FILE) -> str:
    """Env var (model-specific, then generic) first, shared key file last.
    Never returns a value that was itself hardcoded in this module --
    always read from environment or disk at call time."""
    for env_name in (config.fallback_api_key_env, config.api_key_env):
        if env_name and os.environ.get(env_name):
            return os.environ[env_name]
    from pathlib import Path
    return Path(key_file).read_text().strip()
