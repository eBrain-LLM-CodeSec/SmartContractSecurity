"""Synthetic positive/negative snippet tests per strategy component, per
the plan's own verification requirement. Each test compiles REAL
Solidity source (not mocked) and asserts the predicate fires on the
positive fixture and does NOT fire on the negative one. Run with:
    .venv/bin/python3 -m rtf.l5_predicates.test_predicates
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from .compile_helper import compile_source
from . import predicates as P

PASSES = []
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
    else:
        FAILURES.append(f"{name}: {detail}")


def _write_and_compile(src: str, version: str = "0.8.20"):
    return compile_source(src, solc_version=version)


def test_compiler_version_floor():
    old = _write_and_compile("pragma solidity ^0.7.6;\ncontract C { function f() public pure returns (uint) { return 1; } }", version="0.7.6")
    new = _write_and_compile("pragma solidity ^0.8.20;\ncontract C { function f() public pure returns (uint) { return 1; } }", version="0.8.20")
    r_old = P.check_compiler_version_floor(old, "req-1-compiler-060", "0.8.0")
    r_new = P.check_compiler_version_floor(new, "req-1-compiler-060", "0.8.0")
    check("compiler_version_floor: flags 0.7.6 < 0.8.0", len(r_old) == 1, r_old)
    check("compiler_version_floor: does not flag 0.8.20 >= 0.8.0", len(r_new) == 0, r_new)


def test_compiler_version_exact():
    hit = _write_and_compile("pragma solidity 0.8.9;\ncontract C {}", version="0.8.9")
    miss = _write_and_compile("pragma solidity 0.8.20;\ncontract C {}", version="0.8.20")
    r_hit = P.check_compiler_version_exact(hit, "req-1-compiler-sol-2021-4", "0.8.9")
    r_miss = P.check_compiler_version_exact(miss, "req-1-compiler-sol-2021-4", "0.8.9")
    check("compiler_version_exact: flags the exact prohibited version", len(r_hit) == 1, r_hit)
    check("compiler_version_exact: does not flag a different version", len(r_miss) == 0, r_miss)


def test_compiler_version_in_range():
    inside_low_end = _write_and_compile("pragma solidity 0.8.13;\ncontract C {}", version="0.8.13")
    inside_high_end = _write_and_compile("pragma solidity 0.8.16;\ncontract C {}", version="0.8.16")
    below = _write_and_compile("pragma solidity 0.8.12;\ncontract C {}", version="0.8.12")
    above = _write_and_compile("pragma solidity 0.8.17;\ncontract C {}", version="0.8.17")
    r_low = P.check_compiler_version_in_range(inside_low_end, "req-2-compiler-SOL-2022-7", "0.8.13", "0.8.16")
    r_high = P.check_compiler_version_in_range(inside_high_end, "req-2-compiler-SOL-2022-7", "0.8.13", "0.8.16")
    r_below = P.check_compiler_version_in_range(below, "req-2-compiler-SOL-2022-7", "0.8.13", "0.8.16")
    r_above = P.check_compiler_version_in_range(above, "req-2-compiler-SOL-2022-7", "0.8.13", "0.8.16")
    check("compiler_version_in_range: flags the low (inclusive) end of the range", len(r_low) == 1, r_low)
    check("compiler_version_in_range: flags the high (inclusive) end of the range", len(r_high) == 1, r_high)
    check("compiler_version_in_range: does not flag just below the range", len(r_below) == 0, r_below)
    check("compiler_version_in_range: does not flag just above the range", len(r_above) == 0, r_above)


def test_create2():
    positive = """
    pragma solidity ^0.8.20;
    contract Target {}
    contract C {
        function deploy(bytes32 salt) public returns (address) {
            return address(new Target{salt: salt}());
        }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract Target {}
    contract C {
        function deploy() public returns (address) {
            return address(new Target());
        }
    }
    """
    assembly_positive = """
    pragma solidity ^0.8.20;
    contract C {
        function deploy(bytes memory bytecode, bytes32 salt) public returns (address addr) {
            assembly {
                addr := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
            }
        }
    }
    """
    r_pos = P.find_create2_usage(_write_and_compile(positive))
    r_neg = P.find_create2_usage(_write_and_compile(negative))
    r_asm = P.find_create2_usage(_write_and_compile(assembly_positive))
    check("create2: flags salted new{}()", len(r_pos) >= 1, r_pos)
    check("create2: does not flag plain new()", len(r_neg) == 0, r_neg)
    check("create2: flags raw create2 opcode in assembly (previously dead code -- node.inline_asm was always None)", len(r_asm) >= 1, r_asm)


def test_selfdestruct_presence_unconditional_on_protection():
    positive_unprotected = """
    pragma solidity ^0.8.20;
    contract C {
        function kill() public { selfdestruct(payable(msg.sender)); }
    }
    """
    positive_protected = """
    pragma solidity ^0.8.20;
    contract C {
        address owner;
        modifier onlyOwner() { require(msg.sender == owner); _; }
        function kill() public onlyOwner { selfdestruct(payable(msg.sender)); }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        function noop() public pure returns (uint) { return 1; }
    }
    """
    r_unprot = P.find_selfdestruct_presence(_write_and_compile(positive_unprotected))
    r_prot = P.find_selfdestruct_presence(_write_and_compile(positive_protected))
    r_neg = P.find_selfdestruct_presence(_write_and_compile(negative))
    check("selfdestruct: flags unprotected selfdestruct", len(r_unprot) == 1, r_unprot)
    check(
        "selfdestruct: ALSO flags PROTECTED selfdestruct (mere-presence, unlike Slither's own suicidal detector)",
        len(r_prot) == 1,
        r_prot,
    )
    check("selfdestruct: does not flag code with no selfdestruct", len(r_neg) == 0, r_neg)


def test_delegatecall_presence_unconditional_on_taint():
    positive_hardcoded = """
    pragma solidity ^0.8.20;
    contract C {
        address constant TARGET = address(0xdead);
        function callit() public { (bool ok, ) = TARGET.delegatecall(""); require(ok); }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        address target;
        function callit() public { (bool ok, ) = target.call(""); require(ok); }
    }
    """
    r_pos = P.find_delegatecall_presence(_write_and_compile(positive_hardcoded))
    r_neg = P.find_delegatecall_presence(_write_and_compile(negative))
    check("delegatecall: flags delegatecall to a HARDCODED (non-tainted) address", len(r_pos) == 1, r_pos)
    check("delegatecall: does not flag plain .call()", len(r_neg) == 0, r_neg)


def test_tx_origin_any_context():
    positive_nonconditional = """
    pragma solidity ^0.8.20;
    contract C {
        event Origin(address);
        function log() public { emit Origin(tx.origin); }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        function log() public view returns (address) { return msg.sender; }
    }
    """
    r_pos = P.find_tx_origin_any_usage(_write_and_compile(positive_nonconditional))
    r_neg = P.find_tx_origin_any_usage(_write_and_compile(negative))
    check(
        "tx.origin: flags NON-conditional usage (e.g. logged in event) -- the exact gap Slither's own tx-origin detector has",
        len(r_pos) == 1,
        r_pos,
    )
    check("tx.origin: does not flag code using only msg.sender", len(r_neg) == 0, r_neg)


def test_exact_native_balance_check():
    positive = """
    pragma solidity ^0.8.20;
    contract C {
        function check() public view returns (bool) {
            return address(this).balance == 1 ether;
        }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        function check() public view returns (bool) {
            return address(this).balance >= 1 ether;
        }
    }
    """
    r_pos = P.find_exact_native_balance_check(_write_and_compile(positive), "req-1-exact-balance-check")
    r_neg = P.find_exact_native_balance_check(_write_and_compile(negative), "req-1-exact-balance-check")
    check("exact_balance: flags `.balance == x`", len(r_pos) >= 1, r_pos)
    check("exact_balance: does not flag `.balance >= x`", len(r_neg) == 0, r_neg)


def test_encode_packed_untainted():
    positive = """
    pragma solidity ^0.8.20;
    contract C {
        function h() public pure returns (bytes32) {
            string memory a = "fixed-a";
            string memory b = "fixed-b";
            return keccak256(abi.encodePacked(a, b));
        }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        function h(uint a, uint b) public pure returns (bytes32) {
            return keccak256(abi.encodePacked(a, b));
        }
    }
    """
    r_pos = P.find_encode_packed_untainted_collision(_write_and_compile(positive))
    r_neg = P.find_encode_packed_untainted_collision(_write_and_compile(negative))
    check(
        "encode_packed: flags 2 consecutive dynamic-type args even with NO external taint (internal-only strings)",
        len(r_pos) >= 1,
        r_pos,
    )
    check("encode_packed: does not flag non-dynamic (uint) args", len(r_neg) == 0, r_neg)


def test_unicode_direction_control_chars():
    with tempfile.TemporaryDirectory() as tmp:
        # U+2066 (LRI) -- one of the 8 chars rtlo.py itself does NOT check
        # (it only checks U+202E).
        bad_path = Path(tmp) / "Bad.sol"
        bad_path.write_text("// comment with hidden ⁦ char\npragma solidity ^0.8.20;\ncontract C {}", encoding="utf-8")
        good_path = Path(tmp) / "Good.sol"
        good_path.write_text("pragma solidity ^0.8.20;\ncontract C {}", encoding="utf-8")

        r_pos = P.find_unicode_direction_control_chars([bad_path])
        r_neg = P.find_unicode_direction_control_chars([good_path])
        check("unicode_bdo: flags U+2066 (LRI) -- NOT covered by Slither's own rtlo detector (U+202E only)", len(r_pos) == 1, r_pos)
        check("unicode_bdo: does not flag clean source", len(r_neg) == 0, r_neg)


def test_reused_assembly_detector_for_no_assembly():
    from slither.detectors.statements.assembly import Assembly

    positive = """
    pragma solidity ^0.8.20;
    contract C {
        function f() public pure returns (uint x) {
            assembly { x := 1 }
        }
    }
    """
    negative = "pragma solidity ^0.8.20;\ncontract C { function f() public pure returns (uint) { return 1; } }"
    r_pos = P.run_reused_slither_detector(_write_and_compile(positive), [Assembly], "req-1-no-assembly")
    r_neg = P.run_reused_slither_detector(_write_and_compile(negative), [Assembly], "req-1-no-assembly")
    check("reused assembly detector: flags inline assembly (mere presence)", len(r_pos) == 1, r_pos)
    check("reused assembly detector: does not flag assembly-free code", len(r_neg) == 0, r_neg)


def test_reused_unchecked_call_detectors_for_check_return():
    from slither.detectors.operations.unchecked_low_level_return_values import UncheckedLowLevel
    from slither.detectors.operations.unchecked_send_return_value import UncheckedSend

    positive_call = """
    pragma solidity ^0.8.20;
    contract C {
        function f(address target) public {
            target.call("");
        }
    }
    """
    positive_send = """
    pragma solidity ^0.8.20;
    contract C {
        function f(address payable target) public {
            target.send(1 ether);
        }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        function f(address target) public {
            (bool ok, ) = target.call("");
            require(ok);
        }
    }
    """
    r_call = P.run_reused_slither_detector(_write_and_compile(positive_call), [UncheckedLowLevel], "req-1-check-return")
    r_send = P.run_reused_slither_detector(_write_and_compile(positive_send), [UncheckedSend], "req-1-check-return")
    r_neg = P.run_reused_slither_detector(_write_and_compile(negative), [UncheckedLowLevel], "req-1-check-return")
    check("reused unchecked-lowlevel: flags an unchecked .call() return", len(r_call) == 1, r_call)
    check("reused unchecked-send: flags an unchecked .send() return", len(r_send) == 1, r_send)
    check("reused unchecked-lowlevel: does not flag a checked .call() return", len(r_neg) == 0, r_neg)


def test_ecrecover_usage():
    positive = """
    pragma solidity ^0.8.20;
    contract C {
        function verify(bytes32 h, uint8 v, bytes32 r, bytes32 s) public pure returns (address) {
            return ecrecover(h, v, r, s);
        }
    }
    """
    negative = "pragma solidity ^0.8.20;\ncontract C { function f() public pure returns (uint) { return 1; } }"
    r_pos = P.find_ecrecover_usage(_write_and_compile(positive), "req-2-signature-verification")
    r_neg = P.find_ecrecover_usage(_write_and_compile(negative), "req-2-signature-verification")
    check("ecrecover: flags direct ecrecover() usage", len(r_pos) == 1, r_pos)
    check("ecrecover: does not flag code without signature verification", len(r_neg) == 0, r_neg)


def test_oz_ecdsa_library_usage():
    # Minimal stand-in for OpenZeppelin's ECDSA library shape (a `library
    # ECDSA` with a `recover` function) -- not the real OZ source, just
    # enough to exercise the library-name + function-name matching logic
    # against a REAL compiled `using ECDSA for bytes32` call site.
    positive = """
    pragma solidity ^0.8.20;
    library ECDSA {
        function recover(bytes32 hash, bytes memory sig) internal pure returns (address) {
            return address(0);
        }
    }
    contract C {
        using ECDSA for bytes32;
        function verify(bytes32 h, bytes memory sig) public pure returns (address) {
            return h.recover(sig);
        }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        function verify(bytes32 h, uint8 v, bytes32 r, bytes32 s) public pure returns (address) {
            return ecrecover(h, v, r, s);
        }
    }
    """
    r_pos = P.find_oz_ecdsa_library_usage(_write_and_compile(positive))
    r_neg = P.find_oz_ecdsa_library_usage(_write_and_compile(negative))
    check("oz_ecdsa: flags usage of a library named ECDSA's recover()", len(r_pos) == 1, r_pos)
    check("oz_ecdsa: does not flag raw ecrecover() with no ECDSA library involved", len(r_neg) == 0, r_neg)


def test_division_in_value_context():
    positive = """
    pragma solidity ^0.8.20;
    contract C {
        function share(uint total, uint parts) public pure returns (uint) {
            return total / parts;
        }
    }
    """
    negative = "pragma solidity ^0.8.20;\ncontract C { function f(uint a, uint b) public pure returns (uint) { return a + b; } }"
    r_pos = P.find_division_in_value_context(_write_and_compile(positive))
    r_neg = P.find_division_in_value_context(_write_and_compile(negative))
    check("division: flags a division operation", len(r_pos) == 1, r_pos)
    check("division: does not flag addition-only code", len(r_neg) == 0, r_neg)


def test_documented_trigger_sites_composition():
    src = """
    pragma solidity ^0.8.20;
    contract C {
        function useAssembly() public pure returns (uint x) { assembly { x := 1 } }
        function useDelegatecall(address t) public { (bool ok, ) = t.delegatecall(""); require(ok); }
        function useSelfdestruct() public { selfdestruct(payable(msg.sender)); }
        function useTimestamp() public view returns (uint) { return block.timestamp; }
        function boring() public pure returns (uint) { return 1; }
    }
    """
    r = P.find_documented_trigger_sites(_write_and_compile(src))
    locations_hit = {f["location"].split(".")[-1] for f in r}
    check(
        "documented_trigger_sites: composition catches assembly/delegatecall/selfdestruct/timestamp, skips boring()",
        {"useAssembly", "useDelegatecall", "useSelfdestruct", "useTimestamp"} <= locations_hit and "boring" not in locations_hit,
        locations_hit,
    )


def test_unprotected_arithmetic():
    unchecked_block = """
    pragma solidity ^0.8.20;
    contract C {
        function f(uint a, uint b) public pure returns (uint) {
            unchecked { return a + b; }
        }
    }
    """
    checked_default = """
    pragma solidity ^0.8.20;
    contract C {
        function f(uint a, uint b) public pure returns (uint) {
            return a + b;
        }
    }
    """
    pre_080 = """
    pragma solidity ^0.7.6;
    contract C {
        function f(uint a, uint b) public pure returns (uint) {
            return a + b;
        }
    }
    """
    r_unchecked = P.find_unprotected_arithmetic(_write_and_compile(unchecked_block))
    r_checked = P.find_unprotected_arithmetic(_write_and_compile(checked_default))
    r_pre080 = P.find_unprotected_arithmetic(_write_and_compile(pre_080, version="0.7.6"))
    check("unprotected_arithmetic: flags addition inside unchecked{}", len(r_unchecked) == 1, r_unchecked)
    check("unprotected_arithmetic: does NOT flag default-checked (>=0.8.0) addition", len(r_checked) == 0, r_checked)
    check("unprotected_arithmetic: flags addition in pre-0.8.0 code (unchecked by default)", len(r_pre080) == 1, r_pre080)


def test_state_write_after_external_call_ordering():
    positive = """
    pragma solidity ^0.8.20;
    contract C {
        uint public x;
        function bad(address target) public {
            (bool ok, ) = target.call("");
            require(ok);
            x = 1;
        }
    }
    """
    negative_effects_first = """
    pragma solidity ^0.8.20;
    contract C {
        uint public x;
        function good(address target) public {
            x = 1;
            (bool ok, ) = target.call("");
            require(ok);
        }
    }
    """
    negative_no_write = """
    pragma solidity ^0.8.20;
    contract C {
        function noop(address target) public {
            (bool ok, ) = target.call("");
            require(ok);
        }
    }
    """
    r_pos = P.find_state_write_after_external_call(_write_and_compile(positive), "req-1-use-c-e-i")
    r_neg_order = P.find_state_write_after_external_call(_write_and_compile(negative_effects_first), "req-1-use-c-e-i")
    r_neg_write = P.find_state_write_after_external_call(_write_and_compile(negative_no_write), "req-1-use-c-e-i")
    check("cei_ordering: flags state write AFTER external call (interaction-before-effects)", len(r_pos) == 1, r_pos)
    check("cei_ordering: does not flag effects-before-interaction (correct CEI order)", len(r_neg_order) == 0, r_neg_order)
    check("cei_ordering: does not flag a call with no subsequent state write at all", len(r_neg_write) == 0, r_neg_write)


def test_block_data_usage_covers_prevrandao_gap():
    # block.prevrandao is the exact gap found in Slither's own weak-prng
    # detector (bad_prng.py only checks timestamp/now/blockhash) -- the
    # case this predicate exists specifically to cover.
    positive_prevrandao = """
    pragma solidity ^0.8.20;
    contract C {
        function f() public view returns (uint) { return block.prevrandao; }
    }
    """
    positive_timestamp_no_modulo = """
    pragma solidity ^0.8.20;
    contract C {
        function f() public view returns (bool) { return block.timestamp > 1000; }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        function f(uint x) public pure returns (uint) { return x + 1; }
    }
    """
    r_prevrandao = P.find_block_data_usage(_write_and_compile(positive_prevrandao), "req-2-random-enough")
    r_ts_no_mod = P.find_block_data_usage(_write_and_compile(positive_timestamp_no_modulo), "req-2-random-enough")
    r_neg = P.find_block_data_usage(_write_and_compile(negative), "req-2-random-enough")
    check("block_data: flags block.prevrandao (Slither's own weak-prng detector misses this entirely)", len(r_prevrandao) == 1, r_prevrandao)
    check("block_data: flags block.timestamp even WITHOUT a modulo op (weak-prng only checks modulo usage)", len(r_ts_no_mod) == 1, r_ts_no_mod)
    check("block_data: does not flag code with no block-data reads", len(r_neg) == 0, r_neg)


def test_udvt_narrower_than_32_bytes():
    positive = "pragma solidity ^0.8.20;\ntype Foo is uint96;\ncontract C {}"
    negative = "pragma solidity ^0.8.20;\ntype Foo is uint256;\ncontract C {}"
    r_pos = P.find_udvt_narrower_than_32_bytes(_write_and_compile(positive))
    r_neg = P.find_udvt_narrower_than_32_bytes(_write_and_compile(negative))
    check("udvt: flags a uint96-backed custom value type (<32 bytes)", len(r_pos) == 1, r_pos)
    check("udvt: does not flag a uint256-backed one (exactly 32 bytes)", len(r_neg) == 0, r_neg)


def test_state_write_without_event():
    positive = """
    pragma solidity ^0.8.20;
    contract C {
        uint public x;
        function setNoEvent(uint v) public { x = v; }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        uint public x;
        event Changed(uint);
        function setWithEvent(uint v) public { x = v; emit Changed(v); }
    }
    """
    r_pos = P.find_state_write_without_event(_write_and_compile(positive))
    r_neg = P.find_state_write_without_event(_write_and_compile(negative))
    check("event_on_state_change: flags a state write with no event", len(r_pos) == 1, r_pos)
    check("event_on_state_change: does not flag a state write WITH an event", len(r_neg) == 0, r_neg)


def test_non_exact_pragma():
    positive = "pragma solidity ^0.8.20;\ncontract C {}"
    negative = "pragma solidity 0.8.20;\ncontract C {}"
    r_pos = P.find_non_exact_pragma(_write_and_compile(positive))
    r_neg = P.find_non_exact_pragma(_write_and_compile(negative))
    check("pragma: flags a caret range pragma", len(r_pos) == 1, r_pos)
    check("pragma: does not flag an exact single-version pin", len(r_neg) == 0, r_neg)


def test_fuzzing_evidence():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        test_with_params = root / "C.t.sol"
        test_with_params.write_text("contract CTest { function testDeposit(uint amount, address user) public {} }", encoding="utf-8")
        test_no_params = root / "D.t.sol"
        test_no_params.write_text("contract DTest { function testSetup() public {} }", encoding="utf-8")

        r_params = P.find_fuzzing_evidence(root, [test_with_params])
        r_no_params = P.find_fuzzing_evidence(root, [test_no_params])
        check("fuzzing: flags a parameterized Foundry test function (fuzzed by forge test)", len(r_params) == 1, r_params)
        check("fuzzing: does not flag a no-argument test function", len(r_no_params) == 0, r_no_params)

        (root / "echidna.yaml").write_text("testMode: assertion", encoding="utf-8")
        r_config = P.find_fuzzing_evidence(root, [test_no_params])
        check("fuzzing: an echidna.yaml config alone counts as evidence", any("echidna" in f["location"] for f in r_config), r_config)


def test_mutation_testing_evidence():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        check("mutation_testing: no finding without a config file", P.find_mutation_testing_evidence(root) == [], P.find_mutation_testing_evidence(root))
        (root / "gambit.json").write_text("{}", encoding="utf-8")
        r = P.find_mutation_testing_evidence(root)
        check("mutation_testing: flags gambit.json presence", len(r) == 1, r)


def test_formal_verification_evidence():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sol_with_smt = root / "C.sol"
        sol_with_smt.write_text("pragma solidity ^0.8.20;\npragma experimental SMTChecker;\ncontract C {}", encoding="utf-8")
        sol_without = root / "D.sol"
        sol_without.write_text("pragma solidity ^0.8.20;\ncontract D {}", encoding="utf-8")

        r_smt = P.find_formal_verification_evidence(root, [sol_with_smt])
        r_none = P.find_formal_verification_evidence(root, [sol_without])
        check("formal_verification: flags SMTChecker pragma", len(r_smt) == 1, r_smt)
        check("formal_verification: no finding for plain source with no FV evidence at all", len(r_none) == 0, r_none)

        (root / "Vault.spec").write_text("rule noop {}", encoding="utf-8")
        r_certora = P.find_formal_verification_evidence(root, [sol_without])
        check("formal_verification: a Certora .spec file alone counts as evidence", any(".spec" in f["location"] for f in r_certora), r_certora)


def test_spdx_or_license_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with_spdx = root / "WithSpdx.sol"
        with_spdx.write_text("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\ncontract C {}", encoding="utf-8")
        without_spdx = root / "NoSpdx.sol"
        without_spdx.write_text("pragma solidity ^0.8.20;\ncontract C {}", encoding="utf-8")

        r_with = P.find_spdx_or_license_file([with_spdx], root)
        r_without = P.find_spdx_or_license_file([without_spdx], root)
        check("license: flags presence of SPDX header", any(f["location"] == str(with_spdx) for f in r_with), r_with)
        check("license: no SPDX finding for file lacking it, and no LICENSE file present", len(r_without) == 0, r_without)

        (root / "LICENSE").write_text("MIT", encoding="utf-8")
        r_license_file = P.find_spdx_or_license_file([without_spdx], root)
        check("license: LICENSE file at repo root counts even without SPDX header", any("LICENSE" in f["location"] for f in r_license_file), r_license_file)


def test_natspec_presence():
    positive = """
    pragma solidity ^0.8.20;
    contract C {
        /// @notice does a thing
        /// @param x the input
        /// @return the output
        function f(uint x) public pure returns (uint) { return x; }
    }
    """
    negative = """
    pragma solidity ^0.8.20;
    contract C {
        function f(uint x) public pure returns (uint) { return x; }
    }
    """
    r_pos = P.find_public_interfaces_missing_natspec(_write_and_compile(positive))
    r_neg = P.find_public_interfaces_missing_natspec(_write_and_compile(negative))
    check("natspec: does NOT flag a function WITH NatSpec", len(r_pos) == 0, r_pos)
    check("natspec: DOES flag a public function with no NatSpec", len(r_neg) == 1, r_neg)


def test_erc_interface_conformance():
    conformant_erc20 = """
    pragma solidity ^0.8.20;
    contract C {
        function totalSupply() external view returns (uint256) { return 0; }
        function balanceOf(address) external view returns (uint256) { return 0; }
        function transfer(address, uint256) external returns (bool) { return true; }
        function transferFrom(address, address, uint256) external returns (bool) { return true; }
        function approve(address, uint256) external returns (bool) { return true; }
        function allowance(address, address) external view returns (uint256) { return 0; }
    }
    """
    broken_erc20 = """
    pragma solidity ^0.8.20;
    contract C {
        function totalSupply() external view returns (uint256) { return 0; }
        function balanceOf(address) external view returns (uint256) { return 0; }
        function transfer(address, uint256) external {}
        function transferFrom(address, address, uint256) external returns (bool) { return true; }
        function approve(address, uint256) external returns (bool) { return true; }
        function allowance(address, address) external view returns (uint256) { return 0; }
    }
    """
    unrelated = """
    pragma solidity ^0.8.20;
    contract C {
        uint256 public count;
        function increment() external { count += 1; }
    }
    """
    r_conformant = P.find_erc_interface_conformance(_write_and_compile(conformant_erc20))
    r_broken = P.find_erc_interface_conformance(_write_and_compile(broken_erc20))
    r_unrelated = P.find_erc_interface_conformance(_write_and_compile(unrelated))

    check("erc_conformance: resembles ERC20 and reports it conforms", len(r_conformant) == 1 and "resembles ERC20" in r_conformant[0]["detail"] and "interface_mismatches=[]" in r_conformant[0]["detail"], r_conformant)
    check("erc_conformance: resembles ERC20 and flags the broken transfer() signature", len(r_broken) == 1 and "resembles ERC20" in r_broken[0]["detail"] and "transfer" in r_broken[0]["detail"], r_broken)
    check("erc_conformance: does not fire on a contract with no ERC resemblance", len(r_unrelated) == 0, r_unrelated)


def test_create2_deployed_target_violations():
    target_has_selfdestruct = """
    pragma solidity ^0.8.20;
    contract Target {
        function kill() public { selfdestruct(payable(msg.sender)); }
    }
    contract Deployer {
        function deploy(bytes32 salt) public returns (address) {
            Target t = new Target{salt: salt}();
            return address(t);
        }
    }
    """
    target_clean = """
    pragma solidity ^0.8.20;
    contract Target {
        uint public x;
        function setX(uint v) public { x = v; }
    }
    contract Deployer {
        function deploy(bytes32 salt) public returns (address) {
            Target t = new Target{salt: salt}();
            return address(t);
        }
    }
    """
    assembly_create2 = """
    pragma solidity ^0.8.20;
    contract Deployer {
        function deploy(bytes memory bytecode, bytes32 salt) public returns (address addr) {
            assembly {
                addr := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
            }
        }
    }
    """
    no_create2_at_all = """
    pragma solidity ^0.8.20;
    contract Target {}
    contract Deployer {
        function deploy() public returns (address) {
            Target t = new Target();
            return address(t);
        }
    }
    """

    r_bad = P.find_create2_deployed_target_violations(_write_and_compile(target_has_selfdestruct))
    r_clean = P.find_create2_deployed_target_violations(_write_and_compile(target_clean))
    r_asm = P.find_create2_deployed_target_violations(_write_and_compile(assembly_create2))
    r_none = P.find_create2_deployed_target_violations(_write_and_compile(no_create2_at_all))

    check("create2_target: flags selfdestruct in the CREATE2-deployed target contract", len(r_bad) == 1 and "selfdestruct" in r_bad[0]["detail"], r_bad)
    check("create2_target: reports statically-clean target with no violation found", len(r_clean) == 1 and "no selfdestruct/delegatecall/callcode found" in r_clean[0]["detail"], r_clean)
    check("create2_target: assembly create2 reported as an evidence gap, not a pass", len(r_asm) == 1 and "evidence gap" in r_asm[0]["detail"], r_asm)
    check("create2_target: does not fire when CREATE2 is not used at all", len(r_none) == 0, r_none)


def test_unsafe_assembly_variable_write():
    slot_reassignment = """
    pragma solidity ^0.8.20;
    contract C {
        struct S { uint x; }
        S s1;
        S s2;
        function reassign(bytes32 raw) public {
            S storage p = s1;
            assembly {
                p.slot := raw
            }
            p.x = 1;
        }
    }
    """
    function_typed_slot_write = """
    pragma solidity ^0.8.20;
    contract C {
        function() external fp;
        function setFp(bytes32 raw) public {
            assembly {
                sstore(fp.slot, raw)
            }
        }
    }
    """
    computed_sstore_slot = """
    pragma solidity ^0.8.20;
    contract C {
        function write(uint val) public {
            assembly {
                sstore(add(1, 2), val)
            }
        }
    }
    """
    direct_slot_reference_only = """
    pragma solidity ^0.8.20;
    contract C {
        uint x;
        function bump() public {
            assembly {
                sstore(x.slot, 1)
            }
        }
    }
    """
    no_assembly = """
    pragma solidity ^0.8.20;
    contract C {
        uint public x;
        function bump() public { x += 1; }
    }
    """

    r_reassign = P.find_unsafe_assembly_variable_write(_write_and_compile(slot_reassignment))
    r_fp_slot = P.find_unsafe_assembly_variable_write(_write_and_compile(function_typed_slot_write))
    r_computed = P.find_unsafe_assembly_variable_write(_write_and_compile(computed_sstore_slot))
    r_direct = P.find_unsafe_assembly_variable_write(_write_and_compile(direct_slot_reference_only))
    r_none = P.find_unsafe_assembly_variable_write(_write_and_compile(no_assembly))

    check("safe_assembly: flags direct .slot := reassignment (storage pointer collision shape)", len(r_reassign) == 1 and "slot pointer" in r_reassign[0]["detail"], r_reassign)
    check("safe_assembly: flags sstore(fp.slot, ...) and tags it as a function-typed variable", len(r_fp_slot) == 1 and "function-typed state variable" in r_fp_slot[0]["detail"], r_fp_slot)
    check("safe_assembly: flags sstore() with a computed slot expression", len(r_computed) == 1 and "computed/non-.slot" in r_computed[0]["detail"], r_computed)
    check("safe_assembly: does NOT flag sstore(x.slot, ...) -- direct reference to a declared variable's own slot", len(r_direct) == 0, r_direct)
    check("safe_assembly: does not fire when there is no assembly at all", len(r_none) == 0, r_none)


def test_readonly_reentrancy_candidates():
    stale_view_reads_stale_var = """
    pragma solidity ^0.8.20;
    interface IExternal { function poke() external; }
    contract C {
        uint public price;
        IExternal ext;
        function update() public {
            ext.poke();
            price = 100;
        }
        function getPrice() public view returns (uint) {
            return price;
        }
    }
    """
    correct_cei_order = """
    pragma solidity ^0.8.20;
    interface IExternal { function poke() external; }
    contract C {
        uint public price;
        IExternal ext;
        function update() public {
            price = 100;
            ext.poke();
        }
        function getPrice() public view returns (uint) {
            return price;
        }
    }
    """
    view_reads_unrelated_var = """
    pragma solidity ^0.8.20;
    interface IExternal { function poke() external; }
    contract C {
        uint public price;
        uint public other;
        IExternal ext;
        function update() public {
            ext.poke();
            price = 100;
        }
        function getOther() public view returns (uint) {
            return other;
        }
    }
    """

    r_stale = P.find_readonly_reentrancy_candidates(_write_and_compile(stale_view_reads_stale_var))
    r_correct = P.find_readonly_reentrancy_candidates(_write_and_compile(correct_cei_order))
    r_unrelated = P.find_readonly_reentrancy_candidates(_write_and_compile(view_reads_unrelated_var))

    check("readonly_reentrancy: flags a view function reading a state var written after an external call elsewhere", len(r_stale) == 1 and "price" in r_stale[0]["detail"], r_stale)
    check("readonly_reentrancy: does not flag when the write happens BEFORE the external call (correct CEI order)", len(r_correct) == 0, r_correct)
    check("readonly_reentrancy: does not flag a view function reading an unrelated, never-post-call-written variable", len(r_unrelated) == 0, r_unrelated)


def test_compiler_version_is_latest_stable():
    matches = _write_and_compile("pragma solidity ^0.8.20;\ncontract C {}", version="0.8.20")
    behind = _write_and_compile("pragma solidity ^0.8.9;\ncontract C {}", version="0.8.9")
    r_match = P.check_compiler_version_is_latest_stable(matches, "req-R-use-latest-compiler", "0.8.20")
    r_behind = P.check_compiler_version_is_latest_stable(behind, "req-R-use-latest-compiler", "0.8.20")
    check("latest_compiler: does not flag when compiled version matches the caller-supplied latest", len(r_match) == 0, r_match)
    check("latest_compiler: flags when compiled version is behind the caller-supplied latest", len(r_behind) == 1, r_behind)


def test_keccak256_chainid_dependency():
    src = """
    pragma solidity ^0.8.20;
    contract C {
        function hashWithChainid(address a, uint256 nonce) public view returns (bytes32) {
            return keccak256(abi.encodePacked(a, nonce, block.chainid));
        }
        function hashWithoutChainid(address a, uint256 nonce) public pure returns (bytes32) {
            return keccak256(abi.encodePacked(a, nonce));
        }
    }
    """
    r = P.find_keccak256_calls_chainid_dependency(_write_and_compile(src))
    with_chainid = [f for f in r if "hashWithChainid" in f["location"]]
    without_chainid = [f for f in r if "hashWithoutChainid" in f["location"]]
    check("chainid_dependency: reports both keccak256() call sites", len(r) == 2, r)
    check("chainid_dependency: reports 'block.chainid IS read' for the site that includes it", len(with_chainid) == 1 and "IS read" in with_chainid[0]["detail"], with_chainid)
    check("chainid_dependency: reports 'is NOT read' for the site that omits it", len(without_chainid) == 1 and "is NOT read" in without_chainid[0]["detail"], without_chainid)


def test_selfdestruct_protection_status():
    unprotected = """
    pragma solidity ^0.8.20;
    contract C {
        function kill() public {
            selfdestruct(payable(msg.sender));
        }
    }
    """
    protected = """
    pragma solidity ^0.8.20;
    contract C {
        address owner;
        modifier onlyOwner() { require(msg.sender == owner); _; }
        function kill() public onlyOwner {
            selfdestruct(payable(msg.sender));
        }
    }
    """
    r_unprotected = P.find_selfdestruct_protection_status(_write_and_compile(unprotected))
    r_protected = P.find_selfdestruct_protection_status(_write_and_compile(protected))
    check("selfdestruct_protection: flags an unprotected selfdestruct-containing function", len(r_unprotected) == 1 and "UNPROTECTED" in r_unprotected[0]["detail"], r_unprotected)
    check("selfdestruct_protection: reports a PROTECTED status for an onlyOwner-guarded selfdestruct", len(r_protected) == 1 and "PROTECTED" in r_protected[0]["detail"] and "UNPROTECTED" not in r_protected[0]["detail"], r_protected)


def test_linting_violations_via_reused_detectors():
    lint_issues = """
    pragma solidity ^0.8.20;
    contract C {
        uint public counter;
        uint private neverUsed;
        function bump() public {
            uint counter = 1;
            counter += 1;
        }
        function neverCalled() internal returns (uint) { return 1; }
    }
    """
    clean = """
    pragma solidity ^0.8.20;
    contract C {
        uint public counter;
        function bump() public {
            counter += 1;
        }
    }
    """
    r_issues = P.find_linting_violations_via_reused_detectors(_write_and_compile(lint_issues))
    r_clean = P.find_linting_violations_via_reused_detectors(_write_and_compile(clean))
    check("linting: flags a contract with an unused state var, local shadowing, and a never-called internal function", len(r_issues) >= 3, r_issues)
    check("linting: does not flag a clean contract", len(r_clean) == 0, r_clean)


def test_pragma_solidity_version_specified():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with_pragma = root / "WithPragma.sol"
        with_pragma.write_text("pragma solidity ^0.8.20;\ncontract C {}", encoding="utf-8")
        without_pragma = root / "NoPragma.sol"
        without_pragma.write_text("contract C {}", encoding="utf-8")
        r = P.find_pragma_solidity_version_specified([with_pragma, without_pragma])
        check("pragma_specified: does not flag a file WITH a pragma directive", not any(f["location"] == str(with_pragma) for f in r), r)
        check("pragma_specified: flags a file with no pragma directive at all", any(f["location"] == str(without_pragma) for f in r), r)


def test_state_mutating_function_protection_status():
    src = """
    pragma solidity ^0.8.20;
    contract C {
        uint public x;
        address owner;
        modifier onlyOwner() { require(msg.sender == owner); _; }
        function setUnprotected(uint v) public { x = v; }
        function setProtected(uint v) public onlyOwner { x = v; }
        function getX() public view returns (uint) { return x; }
    }
    """
    r = P.find_state_mutating_function_protection_status(_write_and_compile(src))
    unprotected = [f for f in r if "setUnprotected" in f["location"]]
    protected = [f for f in r if "setProtected" in f["location"]]
    getters = [f for f in r if "getX" in f["location"]]
    check("access_control: flags an unprotected state-mutating function", len(unprotected) == 1 and "UNPROTECTED" in unprotected[0]["detail"], unprotected)
    check("access_control: reports PROTECTED for an onlyOwner-guarded state-mutating function", len(protected) == 1 and "PROTECTED" in protected[0]["detail"] and "UNPROTECTED" not in protected[0]["detail"], protected)
    check("access_control: does not report a pure view function at all (no state write)", len(getters) == 0, getters)


def test_unvalidated_function_parameters():
    src = """
    pragma solidity ^0.8.20;
    contract C {
        function validated(uint amount) public pure returns (uint) {
            require(amount > 0, "bad");
            return amount;
        }
        function unvalidated(uint amount) public pure returns (uint) {
            return amount + 1;
        }
        function noParams() public pure returns (uint) {
            return 1;
        }
    }
    """
    r = P.find_unvalidated_function_parameters(_write_and_compile(src))
    check("input_validation: does not flag a function whose parameter is required()", not any("validated" == f["location"].split(".")[-1] for f in r), r)
    check("input_validation: flags a function whose parameter is never validated", any("unvalidated" in f["location"] for f in r), r)
    check("input_validation: does not flag a function with no parameters at all", not any("noParams" in f["location"] for f in r), r)


def test_unvalidated_function_parameters_covers_internal_functions():
    """Regression test for AR-011: the predicate used to scan only
    public/external functions, which has no basis in this requirement's
    own text and would have missed a real EVMbench vulnerability (H-02)
    whose exact shape -- an internal function truncating a parameter via
    an unsafe cast, with zero require()/assert() touching it -- is
    reproduced directly here.
    """
    src = """
    pragma solidity ^0.8.20;
    contract C {
        function _burn(address _owner, uint256 _shares) internal virtual {
            _reallyBurn(_owner, uint96(_shares));
        }
        function _reallyBurn(address, uint96) internal virtual {}

        function _mintValidated(uint256 _shares) internal virtual returns (uint256) {
            require(_shares > 0, "bad");
            return _shares;
        }
    }
    """
    r = P.find_unvalidated_function_parameters(_write_and_compile(src))
    check("input_validation: flags an INTERNAL function with an unvalidated parameter (previously invisible to this predicate)", any("_burn" == f["location"].split(".")[-1] for f in r), r)
    check("input_validation: does not flag an internal function whose parameter IS required()", not any("_mintValidated" == f["location"].split(".")[-1] for f in r), r)


def test_reused_detector_safe_across_multiple_calls_on_shared_slither_object():
    """Regression test for a real bug found by the L12 orchestrator
    running many requirements' predicates against ONE shared, long-lived
    Slither object (unlike every other test in this file, which compiles
    a fresh object per test): calling run_reused_slither_detector twice
    on the SAME object -- once with overlapping detector classes, once
    with a different, unrelated class -- used to crash with
    `SlitherError: You can't register X twice`, and even when it didn't
    crash, results from an EARLIER unrelated call could leak into a
    LATER call's return value (since slither.run_detectors() returns
    every registered detector's results, not just the ones passed to a
    given call).
    """
    from slither.detectors.statements.assembly import Assembly
    from slither.detectors.operations.unchecked_low_level_return_values import UncheckedLowLevel
    from slither.detectors.operations.unchecked_send_return_value import UncheckedSend

    src = """
    pragma solidity ^0.8.20;
    contract C {
        function useAssembly() public pure returns (uint x) {
            assembly { x := 1 }
        }
        function unchecked_() public {
            address(this).call("");
        }
    }
    """
    shared = _write_and_compile(src)

    r1 = P.run_reused_slither_detector(shared, [UncheckedLowLevel, UncheckedSend], "req-1-check-return")
    r2 = P.run_reused_slither_detector(shared, [UncheckedLowLevel, UncheckedSend], "req-2-handle-return")  # SAME classes, second call -- must not crash
    r3 = P.run_reused_slither_detector(shared, [Assembly], "req-1-no-assembly")  # DIFFERENT class, third call

    check("reused_detector: repeated call with the SAME detector classes on a shared object does not crash", True, "")
    check("reused_detector: second call with same classes returns the same finding, not empty/duplicated", len(r1) == 1 and len(r2) == 1, (r1, r2))
    check("reused_detector: a later call with a DIFFERENT class does not leak the earlier call's unchecked-call findings into its own result", len(r3) == 1 and all("useAssembly" in f["location"] for f in r3), r3)
    check("reused_detector: req_id is correctly attributed per-call, not stale from an earlier call", r1[0]["req_id"] == "req-1-check-return" and r2[0]["req_id"] == "req-2-handle-return", (r1, r2))


def test_unsafe_narrowing_cast_no_bound_check():
    """Case 1: unsafe narrowing cast, no bound check at all."""
    src = """
    pragma solidity ^0.8.20;
    contract Ledger {
        mapping(address => uint96) internal _balances;
        function record(address _who, uint256 _amount) internal {
            _balances[_who] = uint96(_amount);
        }
    }
    """
    r = P.find_unsafe_narrowing_cast(_write_and_compile(src))
    check("narrowing_cast: flags the unchecked cast", len(r) == 1, r)
    if r:
        f = r[0]
        check("narrowing_cast: correct location", f["location"] == "Ledger.record", f)
        se = f.get("structured_evidence") or {}
        check("narrowing_cast: structured evidence names the operation", "uint256" in se.get("operation", "") and "uint96" in se.get("operation", ""), se)
        check("narrowing_cast: structured evidence names the input", se.get("input", {}).get("name") == "_amount", se)
        check("narrowing_cast: validation_found is 'none'", se.get("validation_found") == "none", se)
        check("narrowing_cast: missing_safety_condition names the bound", "type(uint96).max" in se.get("missing_safety_condition", ""), se)


def test_safe_narrowing_cast_with_bound_check():
    """Case 2: safe narrowing cast, bounded via type(uint96).max."""
    src = """
    pragma solidity ^0.8.20;
    contract Ledger {
        mapping(address => uint96) internal _balances;
        function record(address _who, uint256 _amount) internal {
            require(_amount <= type(uint96).max, "too large");
            _balances[_who] = uint96(_amount);
        }
    }
    """
    r = P.find_unsafe_narrowing_cast(_write_and_compile(src))
    check("narrowing_cast: does NOT flag a cast bounded by type(uintN).max", len(r) == 0, r)


def test_safe_narrowing_cast_with_literal_bound_check():
    """Case 2b: safe narrowing cast, bounded via the equivalent raw literal
    instead of the type(uintN).max idiom -- exercises the OTHER supported
    bound-check form."""
    src = """
    pragma solidity ^0.8.20;
    contract Ledger {
        mapping(address => uint96) internal _balances;
        function record(address _who, uint256 _amount) internal {
            require(_amount <= 79228162514264337593543950335, "too large");
            _balances[_who] = uint96(_amount);
        }
    }
    """
    r = P.find_unsafe_narrowing_cast(_write_and_compile(src))
    check("narrowing_cast: does NOT flag a cast bounded by the equivalent literal", len(r) == 0, r)


def test_narrowing_cast_ignores_safe_widening_and_non_integer_casts():
    src = """
    pragma solidity ^0.8.20;
    contract Ledger {
        function widen(uint96 _amount) internal pure returns (uint256) {
            return uint256(_amount);
        }
        function reinterpretAddress(address _who) internal pure returns (uint160) {
            return uint160(_who);
        }
    }
    """
    r = P.find_unsafe_narrowing_cast(_write_and_compile(src))
    check("narrowing_cast: does not flag a WIDENING cast", not any("widen" in f["location"] for f in r), r)
    check("narrowing_cast: does not flag an address<->uint160 reinterpretation cast (same width, different semantics)", not any("reinterpretAddress" in f["location"] for f in r), r)


def test_narrowing_cast_does_not_flag_safecast_library_usage():
    """Confirms the predicate does not (and structurally cannot) flag
    OpenZeppelin's SafeCast-style pattern -- a LibraryCall, not a raw
    TypeConversion, so it never matches this predicate's trigger at all."""
    src = """
    pragma solidity ^0.8.20;
    library SafeCastLike {
        function toUint96(uint256 value) internal pure returns (uint96) {
            require(value <= type(uint96).max, "SafeCast: overflow");
            return uint96(value);
        }
    }
    contract Ledger {
        using SafeCastLike for uint256;
        mapping(address => uint96) internal _balances;
        function record(address _who, uint256 _amount) internal {
            _balances[_who] = _amount.toUint96();
        }
    }
    """
    r = P.find_unsafe_narrowing_cast(_write_and_compile(src))
    check("narrowing_cast: does not flag Ledger.record (the cast happens inside the library, already checked there)", not any("Ledger.record" in f["location"] for f in r), r)


def test_ecrecover_result_unchecked():
    """Case 3: ecrecover result used without a zero-address check."""
    src = """
    pragma solidity ^0.8.20;
    contract Auth {
        address public authorizedSigner;
        function verify(bytes32 _digest, uint8 _v, bytes32 _r, bytes32 _s) internal view returns (bool) {
            address signer = ecrecover(_digest, _v, _r, _s);
            return signer == authorizedSigner;
        }
    }
    """
    r = P.find_unchecked_ecrecover_result(_write_and_compile(src))
    check("ecrecover_check: flags the unchecked ecrecover result", len(r) == 1, r)
    if r:
        f = r[0]
        se = f.get("structured_evidence") or {}
        check("ecrecover_check: correct location", f["location"] == "Auth.verify", f)
        check("ecrecover_check: structured evidence names the operation", se.get("operation") == "ecrecover(...)", se)
        check("ecrecover_check: validation_found is 'none'", se.get("validation_found") == "none", se)
        check("ecrecover_check: missing_safety_condition names the zero-address check", "address(0)" in se.get("missing_safety_condition", ""), se)


def test_ecrecover_result_checked():
    """Case 4: ecrecover result correctly checked against address(0)."""
    src = """
    pragma solidity ^0.8.20;
    contract Auth {
        address public authorizedSigner;
        function verify(bytes32 _digest, uint8 _v, bytes32 _r, bytes32 _s) internal view returns (bool) {
            address signer = ecrecover(_digest, _v, _r, _s);
            require(signer != address(0), "invalid signature");
            return signer == authorizedSigner;
        }
    }
    """
    r = P.find_unchecked_ecrecover_result(_write_and_compile(src))
    check("ecrecover_check: does not flag a properly-checked ecrecover result", len(r) == 0, r)


def test_ecrecover_wrapper_function_traced_one_level():
    """A local helper function that wraps ecrecover() and returns its
    result directly (the general 'signature-recovery wrapper' pattern,
    e.g. a hand-rolled equivalent of OpenZeppelin's ECDSA.recover()) --
    confirms the predicate traces ONE level through such a wrapper to
    find (or fail to find) the actual check at the CALL SITE, not just
    adjacent to the raw ecrecover() call.
    """
    unchecked_src = """
    pragma solidity ^0.8.20;
    contract Auth {
        address public authorizedSigner;
        function _recover(bytes32 _digest, uint8 _v, bytes32 _r, bytes32 _s) internal pure returns (address) {
            if (_v < 27) {
                return address(0);
            }
            return ecrecover(_digest, _v, _r, _s);
        }
        function verify(bytes32 _digest, uint8 _v, bytes32 _r, bytes32 _s) internal view returns (bool) {
            address signer = _recover(_digest, _v, _r, _s);
            return signer == authorizedSigner;
        }
    }
    """
    checked_src = """
    pragma solidity ^0.8.20;
    contract Auth {
        address public authorizedSigner;
        function _recover(bytes32 _digest, uint8 _v, bytes32 _r, bytes32 _s) internal pure returns (address) {
            if (_v < 27) {
                return address(0);
            }
            return ecrecover(_digest, _v, _r, _s);
        }
        function verify(bytes32 _digest, uint8 _v, bytes32 _r, bytes32 _s) internal view returns (bool) {
            address signer = _recover(_digest, _v, _r, _s);
            require(signer != address(0), "invalid signature");
            return signer == authorizedSigner;
        }
    }
    """
    r_unchecked = P.find_unchecked_ecrecover_result(_write_and_compile(unchecked_src))
    r_checked = P.find_unchecked_ecrecover_result(_write_and_compile(checked_src))

    verify_findings_unchecked = [f for f in r_unchecked if f["location"] == "Auth.verify"]
    verify_findings_checked = [f for f in r_checked if f["location"] == "Auth.verify"]
    check("ecrecover_check: traces through a one-level wrapper to flag the CALL SITE when unchecked", len(verify_findings_unchecked) == 1, r_unchecked)
    if verify_findings_unchecked:
        se = verify_findings_unchecked[0].get("structured_evidence") or {}
        check("ecrecover_check: wrapper-traced finding names the wrapper in its operation field", "_recover" in se.get("operation", ""), se)
    check("ecrecover_check: does not flag the call site when the wrapper's result IS checked there", len(verify_findings_checked) == 0, r_checked)


def test_ecrecover_borderline_no_intermediate_variable():
    """Case 5: borderline -- ecrecover's result is used inline with no
    intermediate named variable, so this predicate cannot trace whether
    it's checked. Per its own documented scope limit, this must be
    reported as an explicit UNKNOWN, not silently treated as either
    checked or unchecked -- exactly the 'insufficient evidence' shape
    this test set is required to cover.
    """
    src = """
    pragma solidity ^0.8.20;
    contract Auth {
        function verify(bytes32 _digest, uint8 _v, bytes32 _r, bytes32 _s, address _expected) internal pure returns (bool) {
            return ecrecover(_digest, _v, _r, _s) == _expected;
        }
    }
    """
    r = P.find_unchecked_ecrecover_result(_write_and_compile(src))
    check("ecrecover_check: borderline inline-use case produces exactly one finding", len(r) == 1, r)
    if r:
        se = r[0].get("structured_evidence") or {}
        check("ecrecover_check: borderline case is reported as UNKNOWN, not silently checked or unchecked", se.get("validation_found", "").startswith("UNKNOWN"), se)


def main() -> int:
    tests = [
        test_compiler_version_floor,
        test_compiler_version_exact,
        test_compiler_version_in_range,
        test_create2,
        test_selfdestruct_presence_unconditional_on_protection,
        test_delegatecall_presence_unconditional_on_taint,
        test_tx_origin_any_context,
        test_exact_native_balance_check,
        test_encode_packed_untainted,
        test_unicode_direction_control_chars,
        test_reused_assembly_detector_for_no_assembly,
        test_reused_unchecked_call_detectors_for_check_return,
        test_ecrecover_usage,
        test_oz_ecdsa_library_usage,
        test_division_in_value_context,
        test_documented_trigger_sites_composition,
        test_unprotected_arithmetic,
        test_state_write_after_external_call_ordering,
        test_block_data_usage_covers_prevrandao_gap,
        test_udvt_narrower_than_32_bytes,
        test_state_write_without_event,
        test_non_exact_pragma,
        test_fuzzing_evidence,
        test_mutation_testing_evidence,
        test_formal_verification_evidence,
        test_spdx_or_license_file,
        test_natspec_presence,
        test_erc_interface_conformance,
        test_create2_deployed_target_violations,
        test_unsafe_assembly_variable_write,
        test_readonly_reentrancy_candidates,
        test_compiler_version_is_latest_stable,
        test_keccak256_chainid_dependency,
        test_selfdestruct_protection_status,
        test_linting_violations_via_reused_detectors,
        test_pragma_solidity_version_specified,
        test_state_mutating_function_protection_status,
        test_unvalidated_function_parameters,
        test_unvalidated_function_parameters_covers_internal_functions,
        test_reused_detector_safe_across_multiple_calls_on_shared_slither_object,
        test_unsafe_narrowing_cast_no_bound_check,
        test_safe_narrowing_cast_with_bound_check,
        test_safe_narrowing_cast_with_literal_bound_check,
        test_narrowing_cast_ignores_safe_widening_and_non_integer_casts,
        test_narrowing_cast_does_not_flag_safecast_library_usage,
        test_ecrecover_result_unchecked,
        test_ecrecover_result_checked,
        test_ecrecover_wrapper_function_traced_one_level,
        test_ecrecover_borderline_no_intermediate_variable,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
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
