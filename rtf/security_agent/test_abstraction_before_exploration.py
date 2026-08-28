"""Deterministic tests (Step 6) for the abstraction-before-exploration
methodology experiment. No live model calls anywhere in this file.

Tests A/B validate the ACTUAL patched checkout that the live experiment
runs against (`glm53_baseline_checkout`, patched in place -- see
`abstraction_before_exploration_glm53_launch.py`'s docstring), not just
this worktree's own copy of prompts.py, since those two copies now
legitimately differ (this worktree's prompts.py also carries the
anti-anchoring gate content, which the experiment's checkout deliberately
does not, to keep this a single-variable comparison against the existing
GLM-5.3 0/3 baseline).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_BASELINE_CHECKOUT = Path("/scratch/md5344/.claude/jobs/c1eeff9d/tmp/glm53_baseline_checkout")
_PATCHED_PROMPTS_PATH = _BASELINE_CHECKOUT / "rtf" / "security_agent" / "prompts.py"

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ORIGINAL_LAUNCH_SCRIPT = _REPO_ROOT / "glm53_capability_test_launch.py"
_METHODOLOGY_LAUNCH_SCRIPT = _REPO_ROOT / "abstraction_before_exploration_glm53_launch.py"

pytestmark = pytest.mark.skipif(
    not _PATCHED_PROMPTS_PATH.exists(),
    reason="throwaway pinned baseline checkout not present in this environment",
)


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _patched_prompts_source() -> str:
    return _PATCHED_PROMPTS_PATH.read_text()


# --- Test A: methodology is present ---------------------------------------
#
# Checked through the real public functions a live run actually calls
# (`build_system_prompt`/`build_initial_user_message`), not a raw
# source-text grep: the source file uses backslash line-continuations
# (`\` immediately followed by a newline) throughout, exactly like every
# other paragraph in this template -- Python joins those with no space at
# import/parse time, but `Path.read_text()` reads the raw bytes, where
# that backslash-newline pair is still literally present. A raw-source
# grep for a phrase that happens to be wrapped across such a
# continuation would therefore never match even though the actual
# rendered prompt is correct -- a real gap found while writing this test,
# not a bug in the prompt itself.

def test_methodology_concepts_present_in_rendered_prompt():
    """The four concepts (PROPERTY / VARIABLES / DISCRIMINATOR / MINIMAL
    PLAN from the task spec) are expressed as natural-language instructions
    mapped onto the EXISTING Hypothesis.claim/next_evidence_needed fields,
    not as literal uppercase labels -- matching the task's own Step 2
    example wording ("State the exact behavior...", "Identify the
    input/state dimensions...", etc.), not a new schema convention."""
    module = _load_module(_PATCHED_PROMPTS_PATH, "patched_prompts_for_test")
    system_prompt = module.build_system_prompt()
    initial_message = module.build_initial_user_message(
        property_ids=["req-x::loc0"], protocol_context_md="pc", requirement_context_by_property={},
        cluster_plan_md="plan",
    )
    # PROPERTY
    assert "the exact behavior being verified" in system_prompt
    # VARIABLES
    assert "which input/state dimensions could change" in system_prompt
    # DISCRIMINATOR
    assert "a valid scenario where a correct and an incorrect" in system_prompt
    assert "behave observably differently" in system_prompt
    # MINIMAL PLAN
    assert "the minimum code/evidence needed" in system_prompt
    # Reuses existing fields, not new ones
    assert "`claim`, write" in system_prompt
    assert "`next_evidence_needed`, write" in system_prompt
    # Exploration-discipline rule (Step 4)
    assert "Prefer tool calls that directly test the current scenario" in system_prompt
    # Instruction appears BEFORE exploration begins, in both the system
    # prompt and the initial user message's closing line
    assert "Before broad exploration" in system_prompt
    assert "Before your first exploratory tool call" in initial_message


# --- Test B: no Canto/ground-truth leakage --------------------------------

_GROUND_TRUTH_MARKERS = (
    "nextepoch", "epoch boundary", "different reward rate", "500000", "600000",
    "reward misattribution", "block_epoch", "canto",
)


def test_no_canto_ground_truth_leakage_in_patched_prompt():
    source = _patched_prompts_source().lower()
    for marker in _GROUND_TRUTH_MARKERS:
        assert marker not in source, f"ground-truth marker {marker!r} found in patched prompts.py"


# --- Test C: tool surface unchanged ---------------------------------------

_EXPECTED_TOOL_NAMES = frozenset({
    "get_callees", "get_callers", "get_contract_source", "get_external_calls",
    "get_function_source", "get_inheritance", "get_modifiers", "get_related_functions",
    "get_state_reads", "get_state_writes", "read_evidence", "read_file", "search_repository",
})
_EXPECTED_ACTION_TOOL_NAMES = frozenset({"update_investigation", "conclude"})


def test_tool_surface_unchanged_in_patched_checkout():
    sys.path.insert(0, str(_BASELINE_CHECKOUT))
    try:
        from rtf.security_agent.tools import SecurityAgentTools, build_tool_schemas
        from rtf.security_agent.kernel import NATIVE_RESPONSE_MODELS
        from rtf.security_agent.response_schema import build_action_tool_schemas

        assert set(SecurityAgentTools.TOOL_NAMES) == _EXPECTED_TOOL_NAMES
        read_tool_names = {s["name"] for s in build_tool_schemas()}
        assert read_tool_names == _EXPECTED_TOOL_NAMES
        action_tool_names = {s["name"] for s in build_action_tool_schemas(NATIVE_RESPONSE_MODELS)}
        assert action_tool_names == _EXPECTED_ACTION_TOOL_NAMES
    finally:
        sys.path.remove(str(_BASELINE_CHECKOUT))
        for mod_name in list(sys.modules):
            if mod_name.startswith("rtf."):
                del sys.modules[mod_name]


# --- Test D: completion logic unchanged -----------------------------------

def test_completion_gate_behavior_unchanged_in_patched_checkout():
    """The methodology experiment touches prompts.py ONLY -- completion.py's
    PASS-gate mechanics must behave identically to the pre-experiment
    baseline: a property with status=PASS and zero counterexample_attempts
    is still rejected."""
    sys.path.insert(0, str(_BASELINE_CHECKOUT))
    try:
        from rtf.security_agent.completion import check_property_completion
        from rtf.security_agent.state import ClusterInvestigationState, RequirementResolution, RequirementState

        state = ClusterInvestigationState(cluster_id="c1", property_ids=["req-x::loc0"])
        req = RequirementState(property_id="req-x::loc0")
        req.status = RequirementResolution.PASS
        state.requirement_states["req-x::loc0"] = req
        result = check_property_completion(state, "req-x::loc0")
        assert result.ready is False
        assert "pass_without_counterexample_attempt" in result.blocking_reasons
    finally:
        sys.path.remove(str(_BASELINE_CHECKOUT))
        for mod_name in list(sys.modules):
            if mod_name.startswith("rtf."):
                del sys.modules[mod_name]


# --- Test E: baseline configuration unchanged -----------------------------

_COMPARED_CONSTANTS = ("BASELINE_CHECKOUT", "AUDIT_ID", "TARGET_PROPERTY_ID", "MODEL",
                       "MAX_STEPS", "MAX_COST_USD", "REPO_ROOT", "SCOPE_FILES", "SOLC_VERSION")


@pytest.mark.skipif(
    not (_ORIGINAL_LAUNCH_SCRIPT.exists() and _METHODOLOGY_LAUNCH_SCRIPT.exists()),
    reason="launch scripts not present in this environment (untracked, scratch-only)",
)
def test_baseline_configuration_identical_to_original_glm53_experiment():
    original = _load_module(_ORIGINAL_LAUNCH_SCRIPT, "original_glm53_launch_for_test")
    methodology = _load_module(_METHODOLOGY_LAUNCH_SCRIPT, "methodology_glm53_launch_for_test")
    for name in _COMPARED_CONSTANTS:
        assert getattr(original, name) == getattr(methodology, name), f"{name} differs between the two launch scripts"
    assert methodology.NUM_RUNS == 3
