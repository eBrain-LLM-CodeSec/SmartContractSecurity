"""Unit tests for rtf.l11_investigation_grouping.cluster_prompt. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_cluster_prompt
"""
from __future__ import annotations

import sys

from rtf.l11_investigation_grouping.cluster_prompt import (
    CLUSTER_PROMPT_PATH, build_cluster_investigation_prompt, load_frozen_cluster_prompt,
)

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def test_frozen_prompt_file_exists():
    check("ARM_G_CLUSTER_PROMPT_v1.md exists", CLUSTER_PROMPT_PATH.exists(), CLUSTER_PROMPT_PATH)


def test_frozen_prompt_grants_full_repository_access():
    text = load_frozen_cluster_prompt()
    check("cluster prompt grants full repository access (not restricted)",
          "full, normal access to the repository" in text, text[:200])


def test_frozen_prompt_requires_independent_verdict_per_property():
    text = load_frozen_cluster_prompt()
    check("prompt states a PASS on one property is not evidence for another",
          "not evidence for another" in text or "own independent" in text.lower(), text)


def test_frozen_prompt_requires_counterexample_search_per_property():
    import re
    text = load_frozen_cluster_prompt()
    normalized = re.sub(r"\s+", " ", text.lower())
    check("prompt requires counterexample search per property",
          "counterexample" in normalized and "per property" in normalized, text)


def test_frozen_prompt_output_schema_uses_properties_list():
    text = load_frozen_cluster_prompt()
    check("output schema names a 'properties' list", '"properties"' in text, text)
    check("output schema requires exact property_id match, no dupes/missing",
          "no more, no fewer, no duplicates" in text, text)


def test_frozen_prompt_never_contains_an_expected_verdict():
    """The frozen prompt itself is generic instructions, not tied to any
    specific investigation -- it should never contain a concrete
    verdict conclusion (only the schema's enumerated possible VALUES,
    which is a distinct, legitimate use of the words PASS/FAIL)."""
    text = load_frozen_cluster_prompt()
    check("prompt is generic (no req_id, no contract name, no specific finding)",
          "req-" not in text and ".sol" not in text, text)


def test_build_cluster_investigation_prompt_includes_all_three_paths():
    prompt = build_cluster_investigation_prompt(
        protocol_context_path=".rtf/context/protocol_context.md",
        requirement_context_paths=[".rtf/context/requirements/req-a.md", ".rtf/context/requirements/req-b.md"],
        cluster_plan_path=".rtf/plans/cluster_007.md",
    )
    check("prompt includes protocol context path", ".rtf/context/protocol_context.md" in prompt, prompt)
    check("prompt includes both requirement context paths",
          ".rtf/context/requirements/req-a.md" in prompt and ".rtf/context/requirements/req-b.md" in prompt, prompt)
    check("prompt includes cluster plan path", ".rtf/plans/cluster_007.md" in prompt, prompt)


def test_build_cluster_investigation_prompt_includes_frozen_contract_text():
    prompt = build_cluster_investigation_prompt(
        protocol_context_path="p.md", requirement_context_paths=["r.md"], cluster_plan_path="c.md",
    )
    check("built prompt includes the frozen ROLE section", "## ROLE" in prompt, prompt[:200])


def test_build_cluster_investigation_prompt_handles_empty_requirement_list():
    prompt = build_cluster_investigation_prompt(
        protocol_context_path="p.md", requirement_context_paths=[], cluster_plan_path="c.md",
    )
    check("empty requirement list: no crash, explicit '(none)' placeholder", "(none)" in prompt, prompt)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILURES.append(f"{t.__name__}: CRASHED -- {type(e).__name__}: {e}")

    print(f"PASSED: {len(PASSES)}")
    for p in PASSES:
        print(f"  ok - {p}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  FAIL - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
