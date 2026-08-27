"""Offline counterexample-quality scorer for the frozen Canto gate case
(2024-01-canto / req-3-implement-as-documented::loc0 / LendingLedger.
update_market), Phase 7 of the model-eval harness spec.

Deliberately NOT a general RTF component: the marker phrases below are
hand-tuned to this one known bug (`update_market` computing
`nextEpoch = i + BLOCK_EPOCH` instead of `epoch + BLOCK_EPOCH`), the same
way the GPT-5.6 Sol vs. GLM-5.3 comparison in EXPERIMENT_REPORT.md was
written up by hand. This module exists so that comparison can be produced
mechanically, from the same signals, for every future model run against
this exact case, without a human re-reading each trajectory by hand every
time -- NOT as a reusable classifier for other properties or audits.

Ground truth (the bug mechanism, the correct formula, the epoch-boundary
counterexample shape) is used HERE, by design (Phase 7: "may use known
ground truth because it is outside the investigator"). It must never be
fed back into a prompt, tool, or the investigator's own context -- this
module only ever reads a FINISHED run's state.json/trajectory.jsonl after
the fact.

Levels, exactly as specified:
  0 INVALID                    -- scenario violates explicit preconditions
                                   or cannot execute.
  1 VALID_NON_DISCRIMINATING   -- legitimate scenario, cannot expose the
                                   target property failure.
  2 VALID_DISCRIMINATING       -- varies relevant state enough that the
                                   vulnerability could become observable.
  3 TARGET_BUG_TRACED          -- concretely traces execution and names
                                   the actual causal mechanism.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path


class CounterexampleLevel(IntEnum):
    INVALID = 0
    VALID_NON_DISCRIMINATING = 1
    VALID_DISCRIMINATING = 2
    TARGET_BUG_TRACED = 3


@dataclass(frozen=True)
class ScenarioScore:
    level: CounterexampleLevel
    has_counterexample_attempt: bool
    preconditions_satisfied: bool
    varies_epoch_boundary: bool
    """Level-2 signal: mentions a non-epoch-aligned start point together
    with differing configuration across two epochs."""
    names_causal_mechanism: bool
    """Level-3 signal: explicitly names nextEpoch/BLOCK_EPOCH together
    with the specific `i + BLOCK_EPOCH` vs `epoch + BLOCK_EPOCH` error."""
    matched_snippets: tuple[str, ...]
    """The literal substrings that triggered the strongest matched level
    -- kept so a human can spot-check the classification instead of
    trusting it blindly."""


# --- Level 0 --------------------------------------------------------------
# Two independent signals, checked in order of authority:
#
# 1. The anti-anchoring self-certification tag (`preconditions: valid-state`
#    / `invalid/rejected-state`), written by `record_counterexample_attempt`
#    on the CURRENT committed kernel (73bf68c onward). Authoritative when
#    present.
# 2. A live check against every state.json this scorer was built against
#    (GLM-5.3/GPT-5.6-Sol Canto runs, both on the FROZEN pre-73bf68c
#    baseline checkout this harness deliberately keeps using for fair
#    comparison) showed NO such tag exists in that record format at all --
#    just `"Hypothesis {hid} — attempt: {attempt}; result: {result}"`. For
#    that format, fall back to explicit invalid/rejected-execution language
#    in the attempt/result text itself. Calibrated against all 4 known
#    runs (3 GLM-5.3 + 1 Sol, all legitimate scenarios, zero false Level-0
#    hits) -- see test_scenario_scorer.py.
_PRECONDITION_TAG = re.compile(r"preconditions:\s*(valid-state|invalid/rejected-state)", re.IGNORECASE)
# Bare "revert" deliberately excluded (real false positive found live,
# DeepSeek qualification run_002: "Inspect claim() source for any
# require/revert that enforces..." -- a code-SEARCH plan naming the
# keyword, not a description of an actual invalid-execution outcome).
# Only inflected forms that describe something that ACTUALLY happened
# ("reverts", "reverted", "it revert(s|ed)") are trustworthy signals here.
_INVALID_LANGUAGE_MARKERS = re.compile(
    r"\b(it\s+reverts|it\s+reverted|call\s+reverts|call\s+reverted|transaction\s+reverts|"
    r"transaction\s+reverted|is invalid|cannot execute|not executable|"
    r"violat(?:es|ing|ed) (?:the |a )?precondition|"
    r"(?:is|was) disallowed|(?:is|was) rejected by|impossible (?:state|scenario|input))\b",
    re.IGNORECASE,
)

# --- Level 2: requires BOTH a non-epoch-aligned starting point AND
# heterogeneous configuration across (at least) two epochs -- either
# alone is too weak (e.g. GLM-5.3 run 1's evidence mentions "epoch
# boundary" in passing while describing the mechanism generally, with no
# actual varied-configuration scenario -- a real false positive caught
# while calibrating this scorer, see test_scenario_scorer.py). Matches
# the task spec's own description of Sol's discriminating scenario:
# "a non-epoch-aligned starting point; different configuration across
# adjacent epochs" -- both parts, not either.
_NON_ALIGNED_START_MARKERS = re.compile(
    r"non[- ]epoch[- ]aligned|whitelist(?:ed)?\s+(?:a\s+)?market\s+at\s+block\s+\d",
    re.IGNORECASE,
)
_HETEROGENEOUS_CONFIG_MARKERS = re.compile(
    r"different\s+(?:cantoperblock|rate|weight|reward|configuration)s?\s+(?:at|across|between|in)\s+"
    r"epochs?\s+\d|"
    r"epoch\s+\d+\s+and\s+epochs?\s+\d+.{0,40}different|"
    r"epoch\s+\d+\s+(?:vs\.?|versus)\s+epoch\s+\d+",
    re.IGNORECASE,
)

# --- Level 3: the actual causal mechanism, named explicitly ---------------
_MECHANISM_MARKERS = re.compile(
    r"nextepoch\s*=\s*i\s*\+\s*block_epoch|"
    r"nextepoch.{0,80}block_epoch|"
    r"(?:should be|instead of|not)\s+`?epoch\s*\+\s*block_epoch`?|"
    r"stale epoch|misattribut\w*|"
    r"charged? at the (?:old|stale|wrong) epoch",
    re.IGNORECASE | re.DOTALL,
)


def _collect_text(state: dict, target_property_id: str) -> tuple[list[str], list[str]]:
    """Returns (counterexample_records, evidence_texts) for the target
    property. Counterexample records are the plain-text strings
    `ClusterInvestigationState.record_counterexample_attempt` writes
    (state.py:294) -- already carry `preconditions: valid-state` /
    `invalid/rejected-state` verbatim. Evidence texts pull each linked
    evidence entry's `claim` (the model's OWN paraphrase/assertion) plus
    the property's `final_assessment.interpretation` -- deliberately NOT
    `raw_excerpt` (a real false positive, found live during the DeepSeek
    qualification run: run_002's ev-3 quoted update_market's loop body
    VERBATIM -- including the literal buggy line `nextEpoch = i +
    BLOCK_EPOCH` -- purely as supporting code for an unrelated claim
    about mid-epoch claiming, never asserting that formula is wrong.
    Matching against quoted source code conflates "the model read this
    line" with "the model identified this line as the bug", which is
    exactly the Level-1/Level-3 distinction this scorer exists to draw.
    Confirmed live that GPT-5.6 Sol's own `claim` text for its analogous
    ev-3 ALREADY states the mechanism explicitly in its own words
    ("computes nextEpoch as i + BLOCK_EPOCH rather than epoch +
    BLOCK_EPOCH") -- so restricting to `claim` loses no real signal for
    the one run that should score TARGET_BUG_TRACED, while correctly
    excluding the one that shouldn't. See test_scenario_scorer.py."""
    req_state = state.get("requirement_states", {}).get(target_property_id, {})
    ce_records = list(req_state.get("counterexample_attempts", []))
    # `RequirementState` links evidence via `evidence_for_ids`/
    # `evidence_against_ids` (state.py), NOT a single `evidence_ids` field
    # -- confirmed live against real state.json shapes (an earlier draft
    # of this scorer used the wrong key name, silently fell through its
    # "or not evidence_ids" fallback, and pulled in evidence from OTHER
    # properties in the same cluster, producing a real false-positive
    # Level-2 match on GLM-5.3 run 1; see test_scenario_scorer.py).
    evidence_ids = set(req_state.get("evidence_for_ids", [])) | set(req_state.get("evidence_against_ids", []))
    final_assessment = req_state.get("final_assessment") or {}
    evidence_ids |= set(final_assessment.get("evidence_ids", []))
    evidence_texts = []
    for eid in evidence_ids:
        ev = state.get("evidence", {}).get(eid)
        if ev is None:
            continue
        evidence_texts.append(ev.get("claim") or "")
    interpretation = final_assessment.get("interpretation")
    if interpretation:
        evidence_texts.append(interpretation)
    return ce_records, evidence_texts


def score_canto_gate_run(state_path: Path, target_property_id: str = "req-3-implement-as-documented::loc0"
                          ) -> ScenarioScore:
    state = json.loads(Path(state_path).read_text())
    ce_records, evidence_texts = _collect_text(state, target_property_id)
    has_attempt = bool(ce_records)

    if not has_attempt:
        return ScenarioScore(
            level=CounterexampleLevel.INVALID, has_counterexample_attempt=False,
            preconditions_satisfied=False, varies_epoch_boundary=False,
            names_causal_mechanism=False, matched_snippets=(),
        )

    tag_hits = [m.group(1).lower() for r in ce_records for m in _PRECONDITION_TAG.finditer(r)]
    if tag_hits:
        preconditions_ok = any(tag == "valid-state" for tag in tag_hits)
    else:
        # No authoritative tag in this record format (the frozen pre-
        # 73bf68c baseline checkout this harness uses) -- fall back to
        # invalid-execution language in the attempt/result text itself.
        preconditions_ok = not any(_INVALID_LANGUAGE_MARKERS.search(r) for r in ce_records)
    if not preconditions_ok:
        invalid_hits = (tuple(f"preconditions: {t}" for t in tag_hits if t != "valid-state") if tag_hits
                        else tuple(m.group(0) for r in ce_records for m in _INVALID_LANGUAGE_MARKERS.finditer(r)))
        return ScenarioScore(
            level=CounterexampleLevel.INVALID, has_counterexample_attempt=True,
            preconditions_satisfied=False, varies_epoch_boundary=False,
            names_causal_mechanism=False, matched_snippets=invalid_hits,
        )

    all_text = "\n".join(ce_records + evidence_texts)
    mechanism_hits = tuple(m.group(0) for m in _MECHANISM_MARKERS.finditer(all_text))
    if mechanism_hits:
        return ScenarioScore(
            level=CounterexampleLevel.TARGET_BUG_TRACED, has_counterexample_attempt=True,
            preconditions_satisfied=True, varies_epoch_boundary=True,
            names_causal_mechanism=True, matched_snippets=mechanism_hits,
        )

    start_hits = tuple(m.group(0) for m in _NON_ALIGNED_START_MARKERS.finditer(all_text))
    config_hits = tuple(m.group(0) for m in _HETEROGENEOUS_CONFIG_MARKERS.finditer(all_text))
    boundary_hits = start_hits + config_hits
    if start_hits and config_hits:
        return ScenarioScore(
            level=CounterexampleLevel.VALID_DISCRIMINATING, has_counterexample_attempt=True,
            preconditions_satisfied=True, varies_epoch_boundary=True,
            names_causal_mechanism=False, matched_snippets=boundary_hits,
        )

    return ScenarioScore(
        level=CounterexampleLevel.VALID_NON_DISCRIMINATING, has_counterexample_attempt=True,
        preconditions_satisfied=True, varies_epoch_boundary=False,
        names_causal_mechanism=False, matched_snippets=(),
    )
