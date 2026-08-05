"""Self-test for the parts of L8 that don't require live LLM access:
schema validation, citation checking, stability aggregation, and prompt
construction. No network calls. Run with:
    python3 -m rtf.l8_llm_judgment_layer.selftest
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from .citation_check import verify_evidence_citations
from .judgment_layer import LLMJudgmentLayer, build_judgment_prompt
from .schema import validate_judgment
from .stability import compute_stability

PASSES = []
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def test_schema_valid_pass() -> None:
    good = {
        "decision": "PASS",
        "requirement_citations": ["req-2-verify-exact-balance-check"],
        "evidence": [{"source": "Vault.sol", "location": "Vault.sol:42", "claim": "balance check guarded by CEI"}],
        "reasoning_summary": "Balance check at line 42 is followed by state update before external call.",
        "open_questions": [],
        "confidence": "HIGH",
        "model_version": "test-model-v1",
        "prompt_version": "rtf-l8-v1",
        "run_id": "abc123",
        "second_pass_agreement": "N/A",
    }
    check("schema: well-formed PASS accepted", validate_judgment(good) == [], validate_judgment(good))


def test_schema_rejects_evidence_free_pass() -> None:
    bad = {
        "decision": "PASS",
        "requirement_citations": [],
        "evidence": [],
        "reasoning_summary": "Looks fine.",
        "open_questions": [],
        "confidence": "HIGH",
        "model_version": "test-model-v1",
        "prompt_version": "rtf-l8-v1",
        "run_id": "abc123",
        "second_pass_agreement": "N/A",
    }
    errors = validate_judgment(bad)
    check(
        "schema: confidence-without-evidence PASS is rejected",
        any("zero evidence" in e for e in errors),
        errors,
    )


def test_schema_rejects_bad_enum() -> None:
    bad = {
        "decision": "MAYBE",
        "requirement_citations": [],
        "evidence": [],
        "reasoning_summary": "x",
        "open_questions": [],
        "confidence": "HIGH",
        "model_version": "v1",
        "prompt_version": "p1",
        "run_id": "r1",
        "second_pass_agreement": "N/A",
    }
    errors = validate_judgment(bad)
    check("schema: invalid decision enum rejected", any("decision" in e for e in errors), errors)


def test_citation_check_real_and_fake_files() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        real_file = repo / "Vault.sol"
        real_file.write_text("\n".join(f"line {i}" for i in range(1, 51)))

        evidence = [
            {"source": "a", "location": "Vault.sol:10", "claim": "exists, in range"},
            {"source": "b", "location": "Vault.sol:1000", "claim": "exists, out of range"},
            {"source": "c", "location": "DoesNotExist.sol:5", "claim": "file missing"},
            {"source": "d", "location": "Vault.sol#line", "claim": "symbol present as literal text"},
        ]
        result = verify_evidence_citations(evidence, repo)
        check(
            "citation_check: 2 valid / 4 total, raw counts reported",
            result["valid"] == 2 and result["total"] == 4,
            result,
        )
        check(
            "citation_check: in-range real location marked ok",
            result["details"][0]["ok"] is True,
            result["details"][0],
        )
        check(
            "citation_check: out-of-range line marked invalid",
            result["details"][1]["ok"] is False and "exceeds file length" in result["details"][1]["reason"],
            result["details"][1],
        )
        check(
            "citation_check: missing file marked invalid",
            result["details"][2]["ok"] is False and "not found" in result["details"][2]["reason"],
            result["details"][2],
        )
        check(
            "citation_check: valid/invalid counts sum to total",
            result["valid"] + result["invalid"] == result["total"],
            result,
        )


def test_stability_aggregation() -> None:
    judgments = [{"decision": d} for d in ["PASS", "PASS", "PASS", "FAIL", "PASS"]]
    stability = compute_stability(judgments)
    check(
        "stability: flip rate reported as raw count, not bare percentage",
        stability["flip_rate_display"] == "1/5" and stability["flip_count"] == 1,
        stability,
    )
    check("stability: modal decision correct", stability["modal_decision"] == "PASS", stability)


def test_stability_requires_min_two_runs() -> None:
    try:
        compute_stability([{"decision": "PASS"}])
        check("stability: rejects single-run input", False, "did not raise")
    except ValueError:
        check("stability: rejects single-run input", True)


def test_prompt_uses_only_context_bundle_content() -> None:
    bundle_record = {
        "bundle": {
            "self": "Tested code MUST do X.",
            "parent_section_context": None,
            "definitions": [{"id": "dfn-tested-code", "text": "Tested Code means the source code."}],
            "overriding_requirements": [],
            "exceptions": [],
            "referenced_requirements": [],
        }
    }
    messages = build_judgment_prompt(bundle_record, "Does the code do X?")
    user_content = messages[1]["content"]
    check(
        "prompt: includes the requirement's own text",
        "Tested code MUST do X." in user_content,
        user_content,
    )
    check(
        "prompt: includes bundle definitions",
        "Tested Code means the source code." in user_content,
        user_content,
    )
    check(
        "prompt: includes the specific question",
        "Does the code do X?" in user_content,
        user_content,
    )
    system_content = messages[0]["content"]
    check(
        "prompt: system message permits INCONCLUSIVE/INSUFFICIENT_EVIDENCE",
        "INCONCLUSIVE" in system_content and "INSUFFICIENT_EVIDENCE" in system_content,
        system_content,
    )


class FakeChatClient:
    """Mimics just enough of a4v.llm.ChatClient's interface to test
    judge_once/judge_with_second_pass/judge_stability's cache-bypass logic
    without any network access. Records every call and every cache-path
    lookup so the test can assert on ordering/bypass behavior directly."""

    def __init__(self, tmp_cache_dir: Path):
        self.tmp_cache_dir = tmp_cache_dir
        self.complete_json_calls = 0
        self.cache_path_lookups: list[Path] = []

    def _cache_key(self, messages, temperature):
        return "fixed-key-since-messages-are-identical-across-repeat-calls"

    def _cache_path(self, key):
        p = self.tmp_cache_dir / f"{key}.json"
        self.cache_path_lookups.append(p)
        return p

    def complete_json(self, messages, temperature=0.0):
        self.complete_json_calls += 1
        data = {
            "decision": "PASS",
            "requirement_citations": [],
            "evidence": [{"source": "x", "location": "x.sol:1", "claim": "y"}],
            "reasoning_summary": f"call number {self.complete_json_calls}",
            "open_questions": [],
            "confidence": "HIGH",
        }

        class Result:
            prompt_tokens = 1
            completion_tokens = 1

        return data, Result()


def test_judge_once_bypass_cache_deletes_entry() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp)
        fake = FakeChatClient(cache_dir)
        layer = LLMJudgmentLayer(chat_client=fake, model_version="test-model")
        bundle_record = {"bundle": {"self": "x", "parent_section_context": None, "definitions": [],
                                     "overriding_requirements": [], "exceptions": [], "referenced_requirements": []}}
        cache_file = cache_dir / "fixed-key-since-messages-are-identical-across-repeat-calls.json"
        cache_file.write_text("{}")  # simulate a pre-existing cache entry

        layer.judge_once(bundle_record, "q?", bypass_cache=True)
        check("judge_once(bypass_cache=True) deletes the pre-existing cache file", not cache_file.exists())


def test_judge_with_second_pass_uses_fresh_second_call() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fake = FakeChatClient(Path(tmp))
        layer = LLMJudgmentLayer(chat_client=fake, model_version="test-model")
        bundle_record = {"bundle": {"self": "x", "parent_section_context": None, "definitions": [],
                                     "overriding_requirements": [], "exceptions": [], "referenced_requirements": []}}
        layer.judge_with_second_pass(bundle_record, "q?")
        check(
            "judge_with_second_pass makes exactly 2 real completion calls (not cache-shortcut to 1)",
            fake.complete_json_calls == 2,
            fake.complete_json_calls,
        )


def test_judge_stability_bypasses_cache_for_all_but_first_run() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fake = FakeChatClient(Path(tmp))
        layer = LLMJudgmentLayer(chat_client=fake, model_version="test-model")
        bundle_record = {"bundle": {"self": "x", "parent_section_context": None, "definitions": [],
                                     "overriding_requirements": [], "exceptions": [], "referenced_requirements": []}}
        layer.judge_stability(bundle_record, "q?", n_runs=4)
        check(
            "judge_stability(n_runs=4) makes exactly 4 real completion calls",
            fake.complete_json_calls == 4,
            fake.complete_json_calls,
        )


def main() -> int:
    test_schema_valid_pass()
    test_schema_rejects_evidence_free_pass()
    test_schema_rejects_bad_enum()
    test_citation_check_real_and_fake_files()
    test_stability_aggregation()
    test_stability_requires_min_two_runs()
    test_prompt_uses_only_context_bundle_content()
    test_judge_once_bypass_cache_deletes_entry()
    test_judge_with_second_pass_uses_fresh_second_call()
    test_judge_stability_bypasses_cache_for_all_but_first_run()

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
