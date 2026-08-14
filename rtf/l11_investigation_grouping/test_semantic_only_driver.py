"""Wiring test for rtf.l11_investigation_grouping.semantic_only_driver.
Zero real LLM/Codex calls -- fake chat_client + a mocked
run_arm_g_bundle_fn, same "mock-tested first" convention as
test_live_runner.py. Verifies the full generation -> grounding ->
clustering -> (mocked) investigation -> verdict-resolution wiring is
correct BEFORE any live run. Run with:
    .venv/bin/python3 -m rtf.l11_investigation_grouping.test_semantic_only_driver
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from rtf.l11_investigation_grouping.live_runner import prepare_cluster_investigations_with_scope_boundary
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.l11_investigation_grouping.run_metadata import GROUPING_POLICY_G2_CONTEXT_AWARE
from rtf.l11_investigation_grouping.semantic_only_driver import run_semantic_investigation
from rtf.l12_evaluation.metrics import ConformanceState
from rtf.l5_predicates.compile_helper import compile_evmbench_target

PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


class FakeChatClient:
    def __init__(self, response: dict):
        self.response = response

    def complete_json(self, messages, temperature=0.0, **kwargs):
        return self.response, None


_VAULT_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Vault {
    uint256 public totalAssetsHeld;
    uint256 public accruedFees;

    function deposit(uint256 amount) external { totalAssetsHeld += amount; }
    function accrueFee(uint256 amount) external { accruedFees += amount; }
    function totalAssets() external view returns (uint256) { return totalAssetsHeld; }
}
"""

_ONE_PROPERTY_ENTRY = {
    "statement": "Vault.totalAssets must not include amounts already owed via Vault.accruedFees.",
    "property_type": "accounting",
    "rationale": "Accrued fees are no longer shareholder-backed assets.",
    "affected_contracts": ["Vault"],
    "affected_functions": ["Vault.totalAssets"],
    "affected_state_variables": ["Vault.totalAssetsHeld", "Vault.accruedFees"],
    "source_refs": ["synthetic-fixture"],
    "confidence": 0.8,
}


class FakeArmGResult:
    def __init__(self, final_decision, cost_usd=0.01):
        self.final_decision = final_decision
        self.cost_usd = cost_usd


def _fake_run_arm_g_bundle(*, case_id, **kwargs):
    # Echo back a FAIL for every property in this cluster -- proves the
    # driver's own property_id set (not a hardcoded guess) drives the
    # response shape, and that verdicts round-trip end to end.
    prompt = kwargs.get("prompt", "")
    return FakeArmGResult(final_decision={
        "properties": [
            {
                "property_id": "semantic__accounting__PLACEHOLDER",
                "verdict": "FAIL",
                "evidence": "totalAssets() returns totalAssetsHeld without subtracting accruedFees.",
                "files_read": ["Vault.sol"],
                "counterexample_attempt": "accrueFee(100) then totalAssets() still returns full totalAssetsHeld.",
                "counterexample_result": "confirmed: accruedFees is never subtracted.",
                "reasoning": "Direct code read.",
                "vulnerable_location": "Vault.totalAssets",
                "confidence": "HIGH",
            }
        ]
    })


def test_driver_wires_generation_through_to_a_mocked_investigation():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "Vault.sol").write_text(_VAULT_SOURCE, encoding="utf-8")
        client = FakeChatClient({"properties": [_ONE_PROPERTY_ENTRY]})

        # The driver assigns a real, content-derived property_id we can't
        # predict in advance -- capture it via a closure so the fake
        # investigation function can echo the CORRECT id, exactly like a
        # real Codex response naming the property_id it was actually given.
        captured = {}

        def _run_arm_g_bundle_fn(*, case_id, prompt, extra_files, candidate_location, **kwargs):
            import re
            haystack = "\n".join(extra_files.values())
            m = re.search(r"`(semantic__[a-z_]+__[0-9a-f]+::loc0)`", haystack)
            pid = m.group(1) if m else None
            captured["property_id"] = pid
            return FakeArmGResult(final_decision={"properties": [{
                "property_id": pid, "verdict": "FAIL",
                "evidence": "totalAssets() never subtracts accruedFees.",
                "files_read": ["Vault.sol"], "counterexample_attempt": "accrueFee then totalAssets",
                "counterexample_result": "confirmed", "reasoning": "direct read",
                "vulnerable_location": "Vault.totalAssets", "confidence": "HIGH",
            }]})

        with tempfile.TemporaryDirectory() as scratch:
            result = run_semantic_investigation(
                audit_id="wiring-test", repo_root=repo, entry_sol_file=repo / "Vault.sol",
                solc_version="0.8.20", chat_client=client,
                codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
                mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
                scratch_root=Path(scratch), run_arm_g_bundle_fn=_run_arm_g_bundle_fn,
            )

        check("driver: exactly one cluster formed", len(result["clusters"]) == 1, result["clusters"])
        check("driver: exactly one property in the pool", len(result["properties_by_id"]) == 1, result["properties_by_id"])
        pid = captured["property_id"]
        check("driver: mocked investigation received the real property_id", pid is not None, captured)
        check("driver: property_verdicts resolved to FAIL",
              result["property_verdicts"][pid].conformance_state == ConformanceState.FAIL,
              result["property_verdicts"])
        check("driver: total_cost_usd reflects the mocked call's cost", result["total_cost_usd"] == 0.01, result["total_cost_usd"])
        check("driver: raw_property_entries_by_id carries the investigator's own evidence text",
              "accruedFees" in result["raw_property_entries_by_id"][pid]["evidence"], result["raw_property_entries_by_id"])
        check("driver: semantic_observability recorded zero rejections",
              result["semantic_observability"]["rejected_generation"] == [] and
              result["semantic_observability"]["rejected_grounding"] == [], result["semantic_observability"])


_HELPER_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Helper {
    uint256 public helperState;
    function bump() external { helperState += 1; }
}
"""

_VAULT_WITH_HELPER_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./Helper.sol";

contract Vault {
    uint256 public totalAssetsHeld;
    Helper public helper;

    function deposit(uint256 amount) external { totalAssetsHeld += amount; }
    function callHelper() external { helper.bump(); }
}
"""

_VAULT_IN_SCOPE_ENTRY = {
    "statement": "Vault.deposit must increase Vault.totalAssetsHeld by exactly the deposited amount.",
    "property_type": "accounting", "rationale": "Deposits must be fully reflected in accounting.",
    "affected_contracts": ["Vault"], "affected_functions": ["Vault.deposit"],
    "affected_state_variables": ["Vault.totalAssetsHeld"], "source_refs": ["fixture"], "confidence": 0.8,
}
_HELPER_OUT_OF_SCOPE_ENTRY = {
    "statement": "Helper.bump must increase Helper.helperState by exactly one.",
    "property_type": "accounting", "rationale": "bump should be a pure increment.",
    "affected_contracts": ["Helper"], "affected_functions": ["Helper.bump"],
    "affected_state_variables": ["Helper.helperState"], "source_refs": ["fixture"], "confidence": 0.8,
}


def test_scope_files_drops_properties_targeting_files_outside_declared_scope():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "Helper.sol").write_text(_HELPER_SOURCE, encoding="utf-8")
        (repo / "Vault.sol").write_text(_VAULT_WITH_HELPER_SOURCE, encoding="utf-8")
        client = FakeChatClient({"properties": [_VAULT_IN_SCOPE_ENTRY, _HELPER_OUT_OF_SCOPE_ENTRY]})

        invoked_property_ids: list[str] = []

        def _run_arm_g_bundle_fn(*, case_id, prompt, extra_files, candidate_location, **kwargs):
            import re
            haystack = "\n".join(extra_files.values())
            for m in re.finditer(r"`(semantic__[a-z_]+__[0-9a-f]+::loc0)`", haystack):
                invoked_property_ids.append(m.group(1))
            entries = [{
                "property_id": pid, "verdict": "PASS", "evidence": "e", "files_read": [],
                "counterexample_attempt": "a", "counterexample_result": "r", "reasoning": "r",
                "vulnerable_location": None, "confidence": "HIGH",
            } for pid in set(invoked_property_ids)]
            return FakeArmGResult(final_decision={"properties": entries})

        with tempfile.TemporaryDirectory() as scratch:
            result = run_semantic_investigation(
                audit_id="scope-test", repo_root=repo, entry_sol_file=repo / "Vault.sol",
                solc_version="0.8.20", chat_client=client,
                codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
                mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
                scratch_root=Path(scratch), run_arm_g_bundle_fn=_run_arm_g_bundle_fn,
                scope_files=["Vault.sol"],  # deliberately excludes Helper.sol
            )

        check("scope: exactly one property in scope", result["in_scope_count"] == 1, result["in_scope_count"])
        check("scope: exactly one property out of scope", result["out_of_scope_count"] == 1, result["out_of_scope_count"])
        check("scope: the out-of-scope property targets Helper.sol",
              result["out_of_scope_properties"][0].relevant_files == ("Helper.sol",) or
              any("Helper" in f for f in result["out_of_scope_properties"][0].relevant_files),
              result["out_of_scope_properties"])
        check("scope: only the in-scope property's id was ever sent to investigation",
              len(invoked_property_ids) == 1, invoked_property_ids)
        in_scope_pid = list(result["properties_by_id"].keys())
        check("scope: properties_by_id only contains the in-scope property (post-scope-filter pool)",
              len(in_scope_pid) == 1, in_scope_pid)


_FOUNDRY_TOML = """[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc = "0.8.20"
"""

_VAULT_ENTRY_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Vault {
    uint256 public totalAssetsHeld;
    function deposit(uint256 amount) external { totalAssetsHeld += amount; }
}
"""

# Deliberately NOT imported by Vault.sol -- a sibling scope file, same shape
# as the real 2025-04-forte Ln.sol / 2024-08-phi Cred.sol gap this fix
# targets (RTF_V2_5ENTRY_ALL_MISSES_ROOT_CAUSE.md).
_SIBLING_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Sibling {
    uint256 public siblingState;
    function bump() external { siblingState += 1; }
}
"""

_SIBLING_PROPERTY_ENTRY = {
    "statement": "Sibling.bump must increase Sibling.siblingState by exactly one per call.",
    "property_type": "accounting", "rationale": "bump is documented as a pure increment.",
    "affected_contracts": ["Sibling"], "affected_functions": ["Sibling.bump"],
    "affected_state_variables": ["Sibling.siblingState"], "source_refs": ["fixture"], "confidence": 0.8,
}


def test_compile_via_foundry_makes_a_sibling_scope_file_visible_to_generation():
    """Real end-to-end proof (mocked LLM/Codex only) of the exact gap
    RTF_V2_5ENTRY_ALL_MISSES_ROOT_CAUSE.md documents: `Sibling.sol` is a
    real scope file that `Vault.sol` (the entry) never imports. Skips
    gracefully if the container/Singularity isn't available in this
    environment, same convention as `test_compile_helper.py`'s own
    real-container test.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "foundry.toml").write_text(_FOUNDRY_TOML, encoding="utf-8")
        (repo / "src").mkdir()
        (repo / "src" / "Vault.sol").write_text(_VAULT_ENTRY_SOURCE, encoding="utf-8")
        (repo / "src" / "Sibling.sol").write_text(_SIBLING_SOURCE, encoding="utf-8")
        client = FakeChatClient({"properties": [_SIBLING_PROPERTY_ENTRY]})

        def _run_arm_g_bundle_fn(*, case_id, prompt, extra_files, candidate_location, **kwargs):
            return FakeArmGResult(final_decision={"properties": []})

        with tempfile.TemporaryDirectory() as scratch:
            try:
                result = run_semantic_investigation(
                    audit_id="foundry-compile-test", repo_root=repo, entry_sol_file=repo / "src" / "Vault.sol",
                    solc_version="0.8.20", chat_client=client,
                    codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
                    mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
                    scratch_root=Path(scratch), run_arm_g_bundle_fn=_run_arm_g_bundle_fn,
                    scope_files=["src/Vault.sol", "src/Sibling.sol"], compile_via_foundry=True,
                )
            except Exception as e:  # noqa: BLE001
                check("compile_via_foundry driver test skipped/failed (container unavailable here?)",
                      False, f"{type(e).__name__}: {e}")
                return

        check("compile_via_foundry: the sibling property was grounded (not rejected as ungrounded)",
              result["semantic_observability"]["rejected_grounding"] == [], result["semantic_observability"])
        check("compile_via_foundry: the sibling property is in the pool, proving Sibling.sol was compiled",
              any(p.target_contract == "Sibling" for p in result["properties_by_id"].values()),
              [(pid, p.target_contract) for pid, p in result["properties_by_id"].items()])
        check("compile_via_foundry: the sibling property is in scope (scope_files included it)",
              result["in_scope_count"] == 1 and result["out_of_scope_count"] == 0,
              (result["in_scope_count"], result["out_of_scope_count"]))


_SCOPE_MATRIX_FOUNDRY_TOML = """[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc = "0.8.20"
"""

_SCOPE_MATRIX_ENTRY_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Entry {
    uint256 public entryState;
    function bump() external { entryState += 1; }
}
"""

# In scope, NOT imported by Entry.sol -- same shape as the real
# 2025-04-forte Ln.sol / 2024-08-phi Cred.sol gap this fix targets.
_SCOPE_MATRIX_SIBLING_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Sibling {
    uint256 public siblingState;
    function bump() external { siblingState += 1; }
}
"""

# First-party, compiled, visible, groundable, but OUT OF SCOPE, and
# deliberately NOT imported by Entry.sol -- corrects the existing
# test_scope_files_drops_properties_targeting_files_outside_declared_scope
# fixture above, whose own Helper.sol IS imported by its entry (so it was
# already visible under the OLD entry-import-graph compile path too, and
# only proves the weaker claim). This fixture's Helper.sol is visible
# ONLY because whole-project Foundry compilation exists.
_SCOPE_MATRIX_HELPER_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Helper {
    uint256 public helperState;
    function bump() external { helperState += 1; }
}
"""

_SCOPE_MATRIX_VENDOR_SOURCE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Vendor {
    uint256 public vendorState;
    function bump() external { vendorState += 1; }
}
"""

_SCOPE_MATRIX_ENTRY_PROPERTY = {
    "statement": "Entry.bump must increase Entry.entryState by exactly one per call.",
    "property_type": "accounting", "rationale": "bump is documented as a pure increment.",
    "affected_contracts": ["Entry"], "affected_functions": ["Entry.bump"],
    "affected_state_variables": ["Entry.entryState"], "source_refs": ["fixture"], "confidence": 0.8,
}
_SCOPE_MATRIX_SIBLING_PROPERTY = {
    "statement": "Sibling.bump must increase Sibling.siblingState by exactly one per call.",
    "property_type": "accounting", "rationale": "bump is documented as a pure increment.",
    "affected_contracts": ["Sibling"], "affected_functions": ["Sibling.bump"],
    "affected_state_variables": ["Sibling.siblingState"], "source_refs": ["fixture"], "confidence": 0.8,
}
_SCOPE_MATRIX_HELPER_PROPERTY = {
    "statement": "Helper.bump must increase Helper.helperState by exactly one per call.",
    "property_type": "accounting", "rationale": "bump is documented as a pure increment.",
    "affected_contracts": ["Helper"], "affected_functions": ["Helper.bump"],
    "affected_state_variables": ["Helper.helperState"], "source_refs": ["fixture"], "confidence": 0.8,
}
_SCOPE_MATRIX_VENDOR_PROPERTY = {
    "statement": "Vendor.bump must increase Vendor.vendorState by exactly one per call.",
    "property_type": "accounting", "rationale": "bump is documented as a pure increment.",
    "affected_contracts": ["Vendor"], "affected_functions": ["Vendor.bump"],
    "affected_state_variables": ["Vendor.vendorState"], "source_refs": ["fixture"], "confidence": 0.8,
}


def test_compile_via_foundry_scope_matrix_entry_sibling_helper_vendor():
    """Goal 1 test fixture (RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md SS7):
    proves all four visibility/scope outcomes in one real whole-project
    Foundry compile. Entry/Sibling are in-scope and reportable (Sibling
    NOT imported by Entry -- the structural gap this fix targets). Helper
    is first-party, compiled, visible, and groundable, but OUT OF SCOPE
    and NOT imported by Entry -- visible only because whole-project
    compilation exists, correctly rejected as unreportable. Vendor lives
    under lib/ (a vendored path) -- ProjectManifest.from_slither's
    existing repo_root filtering (always applied by
    run_semantic_investigation) excludes it from the manifest entirely,
    so a property naming it is rejected at grounding, never even reaching
    the scope check. Skips gracefully if the container/Singularity isn't
    available here, same convention as the sibling-visibility test above.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "foundry.toml").write_text(_SCOPE_MATRIX_FOUNDRY_TOML, encoding="utf-8")
        (repo / "src").mkdir()
        (repo / "lib").mkdir()
        (repo / "src" / "Entry.sol").write_text(_SCOPE_MATRIX_ENTRY_SOURCE, encoding="utf-8")
        (repo / "src" / "Sibling.sol").write_text(_SCOPE_MATRIX_SIBLING_SOURCE, encoding="utf-8")
        (repo / "src" / "Helper.sol").write_text(_SCOPE_MATRIX_HELPER_SOURCE, encoding="utf-8")
        (repo / "lib" / "Vendor.sol").write_text(_SCOPE_MATRIX_VENDOR_SOURCE, encoding="utf-8")
        client = FakeChatClient({"properties": [
            _SCOPE_MATRIX_ENTRY_PROPERTY, _SCOPE_MATRIX_SIBLING_PROPERTY,
            _SCOPE_MATRIX_HELPER_PROPERTY, _SCOPE_MATRIX_VENDOR_PROPERTY,
        ]})

        invoked_property_ids: list[str] = []
        received_compile_via_foundry: list[bool] = []

        def _run_arm_g_bundle_fn(*, case_id, prompt, extra_files, candidate_location, **kwargs):
            import re
            haystack = "\n".join(extra_files.values())
            for m in re.finditer(r"`(semantic__[a-z_]+__[0-9a-f]+::loc0)`", haystack):
                invoked_property_ids.append(m.group(1))
            received_compile_via_foundry.append(kwargs.get("compile_via_foundry"))
            entries = [{
                "property_id": pid, "verdict": "PASS", "evidence": "e", "files_read": [],
                "counterexample_attempt": "a", "counterexample_result": "r", "reasoning": "r",
                "vulnerable_location": None, "confidence": "HIGH",
            } for pid in set(invoked_property_ids)]
            return FakeArmGResult(final_decision={"properties": entries})

        with tempfile.TemporaryDirectory() as scratch:
            try:
                result = run_semantic_investigation(
                    audit_id="scope-matrix-test", repo_root=repo, entry_sol_file=repo / "src" / "Entry.sol",
                    solc_version="0.8.20", chat_client=client,
                    codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
                    mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
                    scratch_root=Path(scratch), run_arm_g_bundle_fn=_run_arm_g_bundle_fn,
                    scope_files=["src/Entry.sol", "src/Sibling.sol"],  # Helper.sol deliberately excluded
                    compile_via_foundry=True,
                )
            except Exception as e:  # noqa: BLE001
                check("scope matrix driver test skipped/failed (container unavailable here?)",
                      False, f"{type(e).__name__}: {e}")
                return

        rejected_grounding = result["semantic_observability"]["rejected_grounding"]
        check("scope matrix: Vendor property rejected at grounding (filtered from the manifest by repo_root)",
              any("Vendor" in str(r) for r in rejected_grounding), rejected_grounding)
        check("scope matrix: exactly Entry+Sibling in scope, Helper out of scope",
              result["in_scope_count"] == 2 and result["out_of_scope_count"] == 1,
              (result["in_scope_count"], result["out_of_scope_count"]))
        in_scope_contracts = {p.target_contract for p in result["properties_by_id"].values()}
        check("scope matrix: properties_by_id (post-filter pool) contains exactly Entry and Sibling",
              in_scope_contracts == {"Entry", "Sibling"}, in_scope_contracts)
        out_of_scope_contracts = {p.target_contract for p in result["out_of_scope_properties"]}
        check("scope matrix: out_of_scope_properties contains exactly Helper",
              out_of_scope_contracts == {"Helper"}, out_of_scope_contracts)
        check("scope matrix: only Entry+Sibling property ids were ever sent to investigation (Helper never dispatched)",
              len(invoked_property_ids) == 2, invoked_property_ids)


def test_boundary_a_blocks_a_property_that_bypassed_the_primary_filter():
    """Deliberate bypass simulation (RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md
    SS10) -- NOT a re-test of the primary filter. Calls
    `prepare_cluster_investigations_with_scope_boundary` DIRECTLY with a
    pool that already includes an out-of-scope Helper property, skipping
    `run_semantic_investigation`'s own upstream `split_properties_by_scope`
    call entirely (the way a bug, or a future alternate caller, might).
    Boundary A must independently catch it: it must never appear in
    `properties_by_id` (never clustered) or in any cluster's
    `property_ids` (never dispatched to investigation).
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "Vault.sol").write_text(_VAULT_SOURCE, encoding="utf-8")
        slither = compile_evmbench_target(repo / "Vault.sol", repo, solc_version="0.8.20")

        in_scope_prop = PropertyMetadata(
            property_id="semantic__accounting__aaaaaaaaaaaa::loc0",
            requirement_id="semantic__accounting__aaaaaaaaaaaa", requirement_level="GP",
            requirement_semantic_intent=None, property_text="Vault.deposit must increase totalAssetsHeld.",
            target_contract="Vault", target_function="deposit", relevant_files=("Vault.sol",),
            source_kind="code_semantics", generation_method="semantic_derivation",
        )
        bypassed_out_of_scope_prop = PropertyMetadata(
            property_id="semantic__accounting__bbbbbbbbbbbb::loc0",
            requirement_id="semantic__accounting__bbbbbbbbbbbb", requirement_level="GP",
            requirement_semantic_intent=None, property_text="Helper.bump must increase helperState.",
            target_contract="Helper", target_function="bump", relevant_files=("Helper.sol",),
            source_kind="code_semantics", generation_method="semantic_derivation",
        )

        clusters, properties_by_id, _protocol_md, _req_ctx, violations = prepare_cluster_investigations_with_scope_boundary(
            [in_scope_prop, bypassed_out_of_scope_prop], GROUPING_POLICY_G2_CONTEXT_AWARE,
            "boundary-a-test", slither, ["Vault.sol"],
        )

        check("boundary A: violation recorded for the bypassed Helper property",
              any(v["property_id"] == bypassed_out_of_scope_prop.property_id and v["boundary"] == "boundary_a_pre_investigation"
                  for v in violations), violations)
        check("boundary A: Helper never appears in properties_by_id (never clustered)",
              bypassed_out_of_scope_prop.property_id not in properties_by_id, properties_by_id)
        all_clustered_ids = {pid for c in clusters for pid in c.property_ids}
        check("boundary A: Helper's property_id never appears in any cluster (never dispatched)",
              bypassed_out_of_scope_prop.property_id not in all_clustered_ids, all_clustered_ids)
        check("boundary A: the in-scope Vault property still made it through",
              in_scope_prop.property_id in properties_by_id, properties_by_id)


def test_boundary_b_strips_a_fabricated_property_id_from_investigator_output():
    """Deliberate bypass simulation (RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md
    SS10) -- NOT a re-test of the primary filter. The mocked investigator
    returns a real verdict for the property it was actually asked about
    PLUS a fabricated extra entry naming a property_id this run never
    dispatched (simulating an investigator that reasoned about or
    invented a reference to something out of scope). `resolve_property_
    verdicts` resolves every entry a response contains unconditionally
    (confirmed: `cluster_response_validation.py`), and
    `run_cluster_investigations_live` records every entry's raw JSON into
    `raw_property_entries_by_id` unconditionally too -- so without
    Boundary B, the fabricated entry WOULD leak into
    `raw_property_entries_by_id`. Boundary B must strip it before
    `run_semantic_investigation` returns, and record the violation.
    """
    FABRICATED_PID = "semantic__accounting__deadbeefcafe0::loc0"
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "Vault.sol").write_text(_VAULT_SOURCE, encoding="utf-8")
        client = FakeChatClient({"properties": [_ONE_PROPERTY_ENTRY]})
        captured = {}

        def _run_arm_g_bundle_fn(*, case_id, prompt, extra_files, candidate_location, **kwargs):
            import re
            haystack = "\n".join(extra_files.values())
            m = re.search(r"`(semantic__[a-z_]+__[0-9a-f]+::loc0)`", haystack)
            pid = m.group(1) if m else None
            captured["property_id"] = pid
            return FakeArmGResult(final_decision={"properties": [
                {
                    "property_id": pid, "verdict": "FAIL",
                    "evidence": "totalAssets() never subtracts accruedFees.",
                    "files_read": ["Vault.sol"], "counterexample_attempt": "accrueFee then totalAssets",
                    "counterexample_result": "confirmed", "reasoning": "direct read",
                    "vulnerable_location": "Vault.totalAssets", "confidence": "HIGH",
                },
                {
                    "property_id": FABRICATED_PID, "verdict": "FAIL",
                    "evidence": "Helper.bump has no access control.",
                    "files_read": ["Helper.sol"], "counterexample_attempt": "a",
                    "counterexample_result": "r", "reasoning": "r",
                    "vulnerable_location": "Helper.bump", "confidence": "HIGH",
                },
            ]})

        with tempfile.TemporaryDirectory() as scratch:
            result = run_semantic_investigation(
                audit_id="boundary-b-test", repo_root=repo, entry_sol_file=repo / "Vault.sol",
                solc_version="0.8.20", chat_client=client,
                codex_bin=Path("/nonexistent/codex"), python_bin=Path("/nonexistent/python3"),
                mcp_server_script=Path("/nonexistent/mcp.py"), api_key="unused", codex_model="unused",
                scratch_root=Path(scratch), run_arm_g_bundle_fn=_run_arm_g_bundle_fn,
            )

        check("boundary B: fabricated property_id NOT in raw_property_entries_by_id",
              FABRICATED_PID not in result["raw_property_entries_by_id"], result["raw_property_entries_by_id"])
        check("boundary B: fabricated property_id NOT in property_verdicts",
              FABRICATED_PID not in result["property_verdicts"], result["property_verdicts"])
        check("boundary B: violation recorded naming the fabricated property_id",
              any(v["property_id"] == FABRICATED_PID and v["boundary"] == "boundary_b_pre_return"
                  for v in result["scope_boundary_violations"]),
              result["scope_boundary_violations"])
        check("boundary B: the real property's verdict still made it through",
              captured["property_id"] in result["property_verdicts"], result["property_verdicts"])


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
