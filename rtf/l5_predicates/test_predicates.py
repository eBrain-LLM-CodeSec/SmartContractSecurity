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
    r_pos = P.find_create2_usage(_write_and_compile(positive))
    r_neg = P.find_create2_usage(_write_and_compile(negative))
    check("create2: flags salted new{}()", len(r_pos) >= 1, r_pos)
    check("create2: does not flag plain new()", len(r_neg) == 0, r_neg)


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


def main() -> int:
    tests = [
        test_compiler_version_floor,
        test_compiler_version_exact,
        test_create2,
        test_selfdestruct_presence_unconditional_on_protection,
        test_delegatecall_presence_unconditional_on_taint,
        test_tx_origin_any_context,
        test_exact_native_balance_check,
        test_encode_packed_untainted,
        test_unicode_direction_control_chars,
        test_reused_assembly_detector_for_no_assembly,
        test_reused_unchecked_call_detectors_for_check_return,
        test_block_data_usage_covers_prevrandao_gap,
        test_udvt_narrower_than_32_bytes,
        test_state_write_without_event,
        test_non_exact_pragma,
        test_spdx_or_license_file,
        test_natspec_presence,
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
