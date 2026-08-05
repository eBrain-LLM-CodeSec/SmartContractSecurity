"""Custom predicate implementations for RTF strategy components marked
'sound derivation, not yet implemented' in Track A/B's L4/L5/L6/L7
records. Each function is the literal code behind one of those records'
derivation traces -- cross-referenced by req_id in each function's
docstring, not free-standing heuristics invented here.

Every predicate takes a real, compiled `slither.Slither` object (never
raw source text alone, except where the derivation trace itself specifies
a pre-compilation textual check, e.g. license headers) and returns a list
of finding dicts: {"req_id", "location", "detail"}.
"""
from __future__ import annotations

import re
from pathlib import Path

from slither import Slither
from slither.core.declarations import FunctionContract

RTLO_9_CHAR_RE = re.compile(
    "[⁦⁧⁨ ‪‫‬‭‮]"
)


def find_spdx_or_license_file(sol_source_paths: list[Path], repo_root: Path) -> list[dict]:
    """req-R-define-license (GP): 'SHOULD define a software license'.
    Presence check: an SPDX-License-Identifier comment in any source file,
    OR a LICENSE/LICENSE.md/LICENSE.txt file at the repo root. Pure text
    check, no compilation needed -- matches the derivation trace's own
    'mechanically checkable' note.
    """
    findings = []
    for p in sol_source_paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        if "SPDX-License-Identifier" in text:
            findings.append({"req_id": "req-R-define-license", "location": str(p), "detail": "SPDX-License-Identifier found"})
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        if (repo_root / name).exists():
            findings.append({"req_id": "req-R-define-license", "location": name, "detail": "LICENSE file present at repo root"})
    return findings


def check_compiler_version_floor(slither: Slither, req_id: str, floor: str) -> list[dict]:
    """req-1-no-ancient-compilers (S, floor='0.3.0'), req-1-compiler-060
    (S, floor='0.8.0'), req-2-compiler-060 (M, floor='0.8.0'): 'MUST NOT
    use a Solidity compiler version older than X'. Direct reuse of the
    same field Slither's own solc-version detector reads
    (compilation_unit.solc_version), compared against the requirement's
    OWN stated threshold rather than the detector's hardcoded 0.8.0 --
    the fix for req-1-no-ancient-compilers's NO_MATCH finding (the
    existing detector's constant was the wrong threshold for that
    specific requirement).
    """
    actual = tuple(int(x) for x in slither.compilation_units[0].solc_version.split("."))
    floor_t = tuple(int(x) for x in floor.split("."))
    if actual < floor_t:
        return [{"req_id": req_id, "location": "compiler config", "detail": f"solc {slither.compilation_units[0].solc_version} < required floor {floor}"}]
    return []


def find_create2_usage(slither: Slither) -> list[dict]:
    """req-1-no-create2 (S): 'MUST NOT contain a CREATE2 instruction'.
    Two code shapes named in the requirement's own text: high-level
    salted `new X{salt: ...}()`, and low-level `create2` in assembly.
    Checked via Slither's NewContract IR (has a .salt attribute when
    present) and a regex over ASSEMBLY-type node source mappings for the
    literal `create2` mnemonic.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                for ir in node.irs:
                    if type(ir).__name__ == "NewContract" and getattr(ir, "call_salt", None) is not None:
                        findings.append({"req_id": "req-1-no-create2", "location": f"{contract.name}.{func.name}", "detail": "salted new{}() (CREATE2)"})
                if node.type.name == "ASSEMBLY" and node.inline_asm and "create2" in str(node.inline_asm):
                    findings.append({"req_id": "req-1-no-create2", "location": f"{contract.name}.{func.name}", "detail": "create2 opcode in assembly"})
    return findings


def find_selfdestruct_presence(slither: Slither, req_id: str = "req-1-self-destruct") -> list[dict]:
    """req-1-self-destruct (S): 'MUST NOT contain selfdestruct()/suicide()'
    -- mere presence, unconditional on protection (unlike Slither's own
    `suicidal` detector, explicitly rejected as a match for this
    requirement per its L4 record: suicidal.py only flags UNPROTECTED
    public/external calls, conflating 'absent' with 'present-but-
    protected'). Reuses the same internal-call-name matching suicidal.py
    itself uses, minus its protection/visibility filters.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_declared:
            calls = [ir.function.name for ir in func.all_internal_calls() if ir.function]
            if "selfdestruct(address)" in calls or "suicide(address)" in calls:
                findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "selfdestruct/suicide present"})
    return findings


def find_delegatecall_presence(slither: Slither, req_id: str = "req-1-delegatecall") -> list[dict]:
    """req-1-delegatecall (S): 'MUST NOT contain the delegatecall()
    instruction' -- mere presence, unconditional on destination taint
    (unlike Slither's `controlled-delegatecall`, which only flags a
    TAINTED destination -- explicitly noted as a scope gap in this
    requirement's L4 record). Reuses `function.low_level_calls`, the same
    IR controlled_delegatecall.py reads, minus the taint filter.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for ir in func.low_level_calls:
                if ir.function_name in ("delegatecall", "callcode"):
                    findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": f"{ir.function_name} present"})
    return findings


def find_tx_origin_any_usage(slither: Slither, req_id: str = "req-1-no-tx.origin") -> list[dict]:
    """req-1-no-tx.origin (S): 'MUST NOT contain a tx.origin instruction'
    -- mere presence anywhere, unconditional on conditional-node context
    (unlike Slither's `tx-origin`, which only flags tx.origin read inside
    if/require/assert AND only when msg.sender isn't also read there --
    explicitly noted as a scope gap in this requirement's L4 record: a
    non-conditional tx.origin read, e.g. logged in an event, would
    violate the S-level text but never trigger that detector).
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                if any(v.name == "tx.origin" for v in node.solidity_variables_read):
                    findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "tx.origin read (any context)"})
    return findings


def find_exact_native_balance_check(slither: Slither, req_id: str) -> list[dict]:
    """req-1-exact-balance-check (S) / req-2-verify-exact-balance-check
    (M): 'checks whether the balance of an account is exactly equal to
    (i.e. ==) a specified amount or the value of a variable'. Scope
    corrected per AR-002 in the L9 register: native ETH `.balance` only
    (matching the requirement's own wording, 'balance of an account'),
    NOT ERC20 balanceOf() -- an earlier draft over-generalized to token
    balances, which the requirement's text doesn't support.
    """
    from slither.slithir.operations import Binary, BinaryType, SolidityCall

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                for ir in node.irs:
                    if isinstance(ir, Binary) and ir.type in (BinaryType.EQUAL, BinaryType.NOT_EQUAL):
                        operands = [ir.variable_left, ir.variable_right]
                        if any(_is_native_balance_access(op, node) for op in operands):
                            findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": f"exact balance comparison ({ir.type.value})"})
    return findings


def _is_native_balance_access(operand, node) -> bool:
    # `X.balance` compiles to a SolidityCall IR: `TMP = SOLIDITY_CALL
    # balance(address)(X)` -- confirmed by direct inspection of real
    # compiled IR (not guessed): the operand being compared IS that call's
    # lvalue. Kept deliberately narrow (native ETH only, via this specific
    # solidity-call name) per AR-002's correction -- no ERC20 balanceOf()
    # matching, which the requirement's text doesn't support.
    from slither.slithir.operations import SolidityCall

    for ir in node.irs:
        if isinstance(ir, SolidityCall) and ir.function and ir.function.name == "balance(address)" and ir.lvalue == operand:
            return True
    return False


def find_encode_packed_untainted_collision(slither: Slither, req_id: str = "req-1-no-hashing-consecutive-variable-length-args") -> list[dict]:
    """req-1-no-hashing-consecutive-variable-length-args (S): 'MUST NOT
    use abi.encodePacked() with consecutive variable length arguments' --
    unconditional (no override clause on this requirement at all, per its
    L1 record), unlike Slither's `encode-packed-collision`, which only
    flags when the dynamic argument is TAINTED by external input --
    explicitly noted as a scope gap in this requirement's L4 record.
    Reuses the same dynamic-type-counting logic, minus the taint filter.
    """
    from slither.core.declarations import SolidityFunction
    from slither.core.solidity_types import ElementaryType, ArrayType

    def is_dynamic(arg) -> bool:
        t = getattr(arg, "type", None)
        if isinstance(t, ElementaryType) and t.name in ("string", "bytes"):
            return True
        if isinstance(t, ArrayType) and t.length is None:
            return True
        return False

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for ir in func.solidity_calls:
                if ir.function == SolidityFunction("abi.encodePacked()"):
                    dyn_count = 0
                    for arg in ir.arguments:
                        if is_dynamic(arg):
                            dyn_count += 1
                        else:
                            dyn_count = 0
                        if dyn_count > 1:
                            findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "abi.encodePacked() with 2+ consecutive dynamic-type args (taint-independent)"})
                            break
    return findings


def find_unicode_direction_control_chars(sol_source_paths: list[Path], req_id: str = "req-1-unicode-bdo") -> list[dict]:
    """req-1-unicode-bdo (S): 'MUST NOT contain any of the Unicode
    Direction Control Characters U+2066, U+2067, U+2068, U+2029, U+202A,
    U+202B, U+202C, U+202D, or U+202E'. Slither's own `rtlo` detector
    covers only U+202E (1 of 9) -- this predicate directly extends
    rtlo.py's own regex approach to all 9 named codepoints, exactly the
    'trivially fixable' mechanical extension noted in this requirement's
    L4 record. Operates on raw source text, same as rtlo.py itself does
    (a source-level check, not a compiled-IR one).
    """
    findings = []
    for p in sol_source_paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in RTLO_9_CHAR_RE.finditer(text):
            findings.append({"req_id": req_id, "location": f"{p}:char_offset_{m.start()}", "detail": f"U+{ord(m.group()):04X} direction-control character"})
    return findings


def find_public_interfaces_missing_natspec(slither: Slither, req_id: str = "req-3-annotate") -> list[dict]:
    """req-3-annotate (Q): 'All Public Interfaces ... MUST be annotated
    with inline comments according to the NatSpec format'. Mechanically
    checkable per this requirement's own L7 record: NatSpec presence on
    public/external functions is a direct AST property.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_declared:
            if func.visibility not in ("public", "external"):
                continue
            if func.is_constructor:
                continue
            if not _has_natspec_comment(func):
                findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "public/external function has no NatSpec annotation"})
    return findings


def _has_natspec_comment(func: FunctionContract) -> bool:
    # Confirmed by direct inspection of a real compiled Function object
    # (not guessed): Slither exposes this as the boolean
    # `has_documentation`, not a structured `natspec` object.
    return bool(getattr(func, "has_documentation", False))
