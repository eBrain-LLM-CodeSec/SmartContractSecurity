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
from weakref import WeakKeyDictionary

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


_NATSPEC_RE = re.compile(r"(?:^[ \t]*///[^\n]*\n?)+|/\*\*.*?\*/", re.MULTILINE | re.DOTALL)
_README_NAMES = ("README.md", "Readme.md", "readme.md", "README", "README.rst", "README.txt")
_MAX_README_CHARS = 6000
_MAX_DOC_FILE_CHARS = 3000
_MAX_NATSPEC_SNIPPET_CHARS = 800
_MAX_SOURCE_EXCERPT_CHARS = 8000


def collect_documentary_and_implementation_evidence(req_id: str, entry_sol_file: Path, repo_root: Path) -> list[dict]:
    """Generic, mechanical evidence collector for requirements whose own
    Track A design record concluded `NO_PREDICATE_POSSIBLE`/`NOT_IMPLEMENTED`
    because assessing them requires comparing DOCUMENTED claims against
    implementation behavior (the archetypal L7 Q-level shape -- see
    `rtf/track_a/l7_level_q_evidence/SCHEMA.md`) -- inherently semantic,
    but the underlying documentary evidence (README, NatSpec doc-comments,
    docs/ files) and the implementation it should be compared against are
    both 100% mechanically collectible. This predicate produces EVIDENCE
    ONLY, no verdict -- it follows the EXACT SAME "evidence collected ->
    L8 judges" pattern every other predicate in this registry already
    uses (see `run_rtf.py`'s module docstring, outcome (1)), so judgment
    reuses the existing bounded-L8 + escalation-to-Codex pipeline
    unchanged rather than a new, parallel judgment mechanism.

    Deliberately generic and standards-driven -- identical logic runs for
    every requirement that registers this predicate, regardless of
    req_id; nothing here encodes knowledge of any specific project's
    business logic, benchmark finding, or vulnerability class. The only
    per-requirement variation is which req_id evidence gets attached to;
    what a given requirement's text demands OF this evidence is decided
    downstream by L8, which already receives the requirement's own
    normative text + context bundle for exactly that purpose.

    Content is capped per item (not a whole-repo dump) to stay within the
    same evidence-budgeting machinery (`evidence_ranking.py`) every other
    requirement's evidence already flows through.
    """
    findings: list[dict] = []
    found_readme = False
    found_docs = False
    found_natspec = False

    for name in _README_NAMES:
        p = repo_root / name
        if p.exists() and p.is_file():
            text = p.read_text(encoding="utf-8", errors="replace")
            findings.append({"req_id": req_id, "location": name,
                              "detail": text[:_MAX_README_CHARS]})
            found_readme = True
            break

    docs_dir = repo_root / "docs"
    if docs_dir.is_dir():
        doc_files = sorted(
            f for f in docs_dir.rglob("*")
            if f.is_file() and f.suffix.lower() in (".md", ".txt", ".rst")
        )
        for f in doc_files[:10]:  # bounded: a docs/ dir is documentation, not a code dump
            text = f.read_text(encoding="utf-8", errors="replace")
            findings.append({"req_id": req_id, "location": str(f.relative_to(repo_root)),
                              "detail": text[:_MAX_DOC_FILE_CHARS]})
            found_docs = True

    if entry_sol_file.exists():
        source = entry_sol_file.read_text(encoding="utf-8", errors="replace")
        for m in _NATSPEC_RE.finditer(source):
            snippet = m.group(0).strip()
            if len(snippet) < 15:  # skip trivial one-line comments, not real NatSpec
                continue
            findings.append({"req_id": req_id, "location": f"{entry_sol_file.name} (NatSpec)",
                              "detail": snippet[:_MAX_NATSPEC_SNIPPET_CHARS]})
            found_natspec = True
        # The entry file's own (capped) source, so a "does implementation
        # match documentation" judgment has real implementation code to
        # compare against, not only the documentation side.
        findings.append({"req_id": req_id, "location": entry_sol_file.name,
                          "detail": source[:_MAX_SOURCE_EXCERPT_CHARS]})

    # Explicit, unambiguous absence evidence -- critical correctness fix,
    # not cosmetic. `run_rtf.py`'s "no evidence collected + unconditioned
    # subject -> automatic PASS" shortcut is correct for PROHIBITION-shaped
    # requirements ("MUST NOT contain X": no evidence = nothing bad found =
    # genuinely PASS) but would be SILENTLY WRONG for these AFFIRMATIVE-
    # OBLIGATION-shaped ones ("MUST have documentation": no evidence found
    # should never auto-resolve to PASS). Always returning at least one
    # finding keeps every requirement using this predicate in the
    # "evidence collected -> deferred to L8" branch unconditionally, and
    # stating the absence explicitly (rather than leaving L8 to infer it
    # from a shorter-than-expected evidence list) lets L8 correctly reason
    # toward FAIL/INSUFFICIENT_EVIDENCE instead of an unearned PASS.
    if not found_readme:
        findings.append({"req_id": req_id, "location": repo_root.name,
                          "detail": "No README file was found at the repository root."})
    if not found_docs:
        findings.append({"req_id": req_id, "location": repo_root.name,
                          "detail": "No docs/ directory (or no .md/.txt/.rst files within it) was found."})
    if not found_natspec:
        findings.append({"req_id": req_id, "location": entry_sol_file.name,
                          "detail": "No NatSpec (/// or /** */) doc-comments were found in this file."})

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


_REUSED_DETECTOR_RESULT_CACHE: "WeakKeyDictionary" = WeakKeyDictionary()


def run_reused_slither_detector(slither: Slither, detector_classes: list, req_id: str) -> list[dict]:
    """Generic wrapper for the EXACT_MATCH/PARTIAL_MATCH-as-evidence-
    collector components that reuse an existing Slither detector directly
    (per that requirement's own L4 record), rather than deriving a custom
    predicate -- e.g. req-1-no-assembly reuses Slither's own `assembly`
    detector as-is (a genuine mere-presence check, per that record's own
    analysis), and req-1-check-return reuses `unchecked-lowlevel` +
    `unchecked-send` together. Runs them via Slither's own public API
    (register_detector/run_detectors), not by reimplementing their logic.

    Safe to call MULTIPLE TIMES against the SAME shared `slither` object
    with DIFFERENT (possibly overlapping) `detector_classes` -- confirmed
    necessary, not a defensive guess: found via a real L12 orchestrator
    run sharing one compiled Slither object across many requirements,
    where req-1-check-return/req-2-handle-return (same detector classes)
    and req-1-no-assembly (a different class) are all registered on the
    same object in sequence.

    THREE separate problems were found by that real run, not one, and
    all three are handled here:
    (1) `register_detector` raises `SlitherError` if the exact same class
    is registered twice.
    (2) `run_detectors()` returns results for EVERY detector ever
    registered on the object, not just the ones passed to THIS call.
    (3) The deeper, non-obvious one: `run_detectors()` is NOT idempotent
    across repeated calls even for the SAME already-registered detector
    -- confirmed empirically (not merely inferred from reading Slither's
    source): calling it a second time for a detector that already
    produced a finding on the first call returns an EMPTY result for
    that finding the second time, even though nothing about the compiled
    target changed. (Slither's own detectors/analyses appear to carry
    state across `.detect()` calls on the same instance -- the exact
    internal mechanism was not tracked down further, since problem (2)'s
    fix below makes it moot: this predicate never needs to call
    `run_detectors()` twice for the same detector class at all.)

    Fix: cache each detector's raw results (keyed by the detector's own
    `ARGUMENT`) the FIRST time it is registered and run, on a
    `WeakKeyDictionary` keyed by the `slither` object itself (so the
    cache is automatically garbage-collected with the object, never a
    global leak across unrelated compiled targets). Every subsequent
    call for an already-cached detector class reuses the cached raw
    results directly and never calls `run_detectors()` again for that
    class -- entirely sidestepping problem (3) rather than trying to
    explain or work around Slither's own internal statefulness.
    """
    if slither not in _REUSED_DETECTOR_RESULT_CACHE:
        _REUSED_DETECTOR_RESULT_CACHE[slither] = {}
    cache = _REUSED_DETECTOR_RESULT_CACHE[slither]

    already_registered = {type(d) for d in slither.detectors}
    newly_needed = [cls for cls in detector_classes if cls.ARGUMENT not in cache]
    for cls in newly_needed:
        if cls not in already_registered:
            slither.register_detector(cls)
    if newly_needed:
        raw_results = slither.run_detectors()
        newly_needed_arguments = {cls.ARGUMENT for cls in newly_needed}
        for detector_results in raw_results:
            for r in detector_results:
                check = r.get("check")
                if check in newly_needed_arguments:
                    cache.setdefault(check, []).append(r)
            # Ensure every newly-needed detector gets a (possibly empty) cache
            # entry even if it produced zero results this run, so it's never
            # re-registered/re-run again on a future call.
        for cls in newly_needed:
            cache.setdefault(cls.ARGUMENT, [])

    wanted_arguments = {cls.ARGUMENT for cls in detector_classes}
    findings = []
    for check_name in wanted_arguments:
        for r in cache.get(check_name, []):
            # Prefer the first "function"-typed element's real name (matches
            # this module's other predicates' "Contract.function" location
            # convention) over the bare check name, which was a real
            # inconsistency caught by this module's own composition test
            # (find_documented_trigger_sites) failing to recognize a hit.
            func_el = next((el for el in r.get("elements", []) if el.get("type") == "function"), None)
            # `.get(key, {})`'s default only applies when `key` is MISSING --
            # if it's present with an explicit `None` value (confirmed to
            # happen for real, on a real EVMbench target: some detectors'
            # "function" elements have `type_specific_fields: None`
            # explicitly, not merely absent), `.get()` returns that `None`
            # and the next chained `.get()` call crashes. `or {}` at each
            # step guards against both "missing" and "explicitly None".
            type_specific_fields = ((func_el or {}).get("type_specific_fields") or {})
            parent = (type_specific_fields.get("parent") or {})
            contract_name = parent.get("name", "?")
            func_name = (func_el or {}).get("name", r.get("check", "?"))
            findings.append({"req_id": req_id, "location": f"{contract_name}.{func_name}", "detail": r.get("description", "").strip()})
    return findings


def check_compiler_version_exact(slither: Slither, req_id: str, exact: str) -> list[dict]:
    """req-1-compiler-sol-2021-4 (S) conformance component: 'MUST NOT use
    Solidity compiler version 0.8.8' -- a single named version, not a
    range (confirmed by re-reading the requirement's own text). Same
    `compilation_unit.solc_version` field as check_compiler_version_floor,
    exact-equality instead of a floor comparison -- checks the ACTUAL
    compiled version, not pragma text, avoiding the pragma-vs-compiled-
    version scope mismatch this requirement's own L4 record flagged
    against reusing Slither's solc-version detector as-is.
    """
    actual = slither.compilation_units[0].solc_version
    if actual == exact:
        return [{"req_id": req_id, "location": "compiler config", "detail": f"solc {actual} == prohibited exact version {exact}"}]
    return []


def check_compiler_version_in_range(slither: Slither, req_id: str, low: str, high: str) -> list[dict]:
    """Version-range component shared by the batch of individually-named
    Compiler Bug S/M requirements (req-1-compiler-SOL-2021-*,
    req-1-compiler-SOL-2022-*, req-1-compiler-SOL-2023-*,
    req-2-compiler-SOL-2021-3, req-2-compiler-SOL-2022-*,
    req-2-compiler-SOL-2023-1), each of whose own text names an explicit
    inclusive version range ('... between X and Y (inclusive)') rather
    than a single floor or exact version. Same `compilation_unit.solc_version`
    field as `check_compiler_version_floor`/`_exact`, inclusive range
    comparison instead of a floor/equality one.

    This is deliberately only the VERSION half of each of these
    requirements' PATTERN_AND_VERSION strategy -- per each requirement's
    own L5/L6 record, the pattern component (the specific named code
    shape, e.g. 'keccak(mem,length) with mismatched non-32-multiple
    lengths') is a separate, not-yet-implemented component; a version
    match alone does not by itself mean the requirement is violated,
    since the vulnerable PATTERN might not be present at all -- exactly
    the VERSION_ONLY-vs-PATTERN_AND_VERSION distinction this project's
    own architecture (see the plan's Contradiction c) requires keeping
    separate, not silently collapsed into a single verdict.
    """
    actual = tuple(int(x) for x in slither.compilation_units[0].solc_version.split("."))
    lo = tuple(int(x) for x in low.split("."))
    hi = tuple(int(x) for x in high.split("."))
    if lo <= actual <= hi:
        return [{"req_id": req_id, "location": "compiler config", "detail": f"solc {slither.compilation_units[0].solc_version} within named range [{low}, {high}] -- version component only, pattern component not evaluated here"}]
    return []


def _assembly_block_text(node) -> str:
    """Confirmed by direct inspection (not guessed): Slither's own
    `node.inline_asm` (backed by `_asm_source_code`) is only populated
    for some AST/solc-version combinations -- for a stock 0.8.20 compile
    of a plain `assembly { ... }` block, it is None even when the block
    plainly contains e.g. `create2`. The raw block text is reliably
    available via `node.source_mapping.content` instead (confirmed
    against a real ASSEMBLY-type node from a real compile). Prefer
    `inline_asm` when Slither does populate it, fall back to source text
    otherwise.
    """
    asm = node.inline_asm
    if asm:
        return str(asm)
    if node.source_mapping is not None and node.source_mapping.content:
        return node.source_mapping.content
    return ""


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
                if node.type.name == "ASSEMBLY" and "create2" in _assembly_block_text(node):
                    findings.append({"req_id": "req-1-no-create2", "location": f"{contract.name}.{func.name}", "detail": "create2 opcode in assembly"})
    return findings


def find_selfdestruct_presence(slither: Slither, req_id: str = "req-1-self-destruct", contracts: list | None = None) -> list[dict]:
    """req-1-self-destruct (S): 'MUST NOT contain selfdestruct()/suicide()'
    -- mere presence, unconditional on protection (unlike Slither's own
    `suicidal` detector, explicitly rejected as a match for this
    requirement per its L4 record: suicidal.py only flags UNPROTECTED
    public/external calls, conflating 'absent' with 'present-but-
    protected'). Reuses the same internal-call-name matching suicidal.py
    itself uses, minus its protection/visibility filters.

    `contracts`, if given, scopes the scan to a specific contract set
    (e.g. one CREATE2-deployed target plus its bases) instead of every
    contract in the compilation unit -- reused as-is by
    `find_create2_deployed_target_violations` for req-2-protect-create2,
    per that requirement's own L6 record noting this exact reuse
    opportunity. Default (None) preserves the original whole-unit scan.
    """
    findings = []
    for contract in (contracts if contracts is not None else slither.contracts):
        for func in contract.functions_declared:
            calls = [ir.function.name for ir in func.all_internal_calls() if ir.function]
            if "selfdestruct(address)" in calls or "suicide(address)" in calls:
                findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "selfdestruct/suicide present"})
    return findings


def find_delegatecall_presence(slither: Slither, req_id: str = "req-1-delegatecall", contracts: list | None = None) -> list[dict]:
    """req-1-delegatecall (S): 'MUST NOT contain the delegatecall()
    instruction' -- mere presence, unconditional on destination taint
    (unlike Slither's `controlled-delegatecall`, which only flags a
    TAINTED destination -- explicitly noted as a scope gap in this
    requirement's L4 record). Reuses `function.low_level_calls`, the same
    IR controlled_delegatecall.py reads, minus the taint filter. Also
    covers `callcode()` (the requirement's third named instruction) in
    the same pass, since Slither's own low_level_calls IR names both
    identically apart from `function_name`.

    `contracts`, if given, scopes the scan the same way as
    `find_selfdestruct_presence` above -- reused by
    `find_create2_deployed_target_violations` for req-2-protect-create2.
    """
    findings = []
    for contract in (contracts if contracts is not None else slither.contracts):
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


def find_udvt_narrower_than_32_bytes(slither: Slither, req_id: str = "req-1-compiler-sol-2021-4") -> list[dict]:
    """req-1-compiler-sol-2021-4 (S) applicability component: 'Tested Code
    that uses custom value types shorter than 32 bytes'. 'Custom value
    type' is EthTrust's own reference to Solidity's user-defined value
    type feature (`type X is Y;`); Slither exposes these directly via
    `compilation_unit.type_aliases`, each with an `underlying_type.size`
    in bits -- confirmed by direct inspection of a real compiled example,
    not guessed. 32 bytes = 256 bits.
    """
    findings = []
    for name, alias in slither.compilation_units[0].type_aliases.items():
        size_bits = getattr(alias.underlying_type, "size", None)
        if size_bits is not None and size_bits < 256:
            findings.append({"req_id": req_id, "location": f"type {name}", "detail": f"underlying type {alias.underlying_type} is {size_bits} bits (<256)"})
    return findings


def find_state_write_without_event(slither: Slither, req_id: str = "req-3-event-on-state-change") -> list[dict]:
    """req-3-event-on-state-change (Q): 'MUST emit a contract event for
    all transactions that cause state changes'. Direct trigger/outcome
    cross-reference: for each function, does it write to any state
    variable, and does it also contain an EventCall IR anywhere -- both
    confirmed by direct inspection of real compiled IR, not guessed.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_declared:
            if not func.state_variables_written:
                continue
            has_event = any(type(ir).__name__ == "EventCall" for node in func.nodes for ir in node.irs)
            if not has_event:
                findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "writes state but emits no event"})
    return findings


def find_non_exact_pragma(slither: Slither, req_id: str = "req-3-consistent-solidity-output") -> list[dict]:
    """req-3-consistent-solidity-output (Q): 'MUST specify a range of
    Solidity versions ... that produce the same Bytecode given the same
    compilation options'. Text-grounded mechanical proxy: a pragma pinned
    to a SINGLE exact version (no ^, >, <, ~, or compound range) trivially
    satisfies this by construction (one version can only ever produce one
    bytecode for fixed compilation options); a caret/range pragma does
    NOT guarantee it, since different versions in the range can differ.
    This does not verify TRUE cross-version bytecode equivalence for
    ranges that happen to be safe -- it flags every non-exact pragma as a
    candidate, which is deliberately over-inclusive rather than asserting
    a range is safe without evidence.
    """
    findings = []
    for cu in slither.compilation_units:
        for p in cu.pragma_directives:
            if not p.directive or p.directive[0] != "solidity":
                continue
            version_text = p.version.strip()
            if any(ch in version_text for ch in ("^", ">", "<", "~", " ", "||")):
                findings.append({"req_id": req_id, "location": str(p), "detail": f"pragma '{version_text}' is a range, not an exact pin"})
    return findings


BLOCK_DATA_SOLIDITY_VAR_NAMES = {"block.timestamp", "now", "block.number", "block.prevrandao", "block.difficulty"}


def find_block_data_usage(slither: Slither, req_id: str) -> list[dict]:
    """req-2-random-enough (M) and req-2-block-data-misuse (M) share this
    trigger per their L6 records. Deliberately broader than Slither's own
    `weak-prng` detector, which -- per direct inspection of bad_prng.py --
    only fires on a MODULO operation whose operand depends on
    block.timestamp/now/blockhash(), and never checks block.difficulty/
    block.prevrandao at all (arguably THE most-cited post-merge weak-
    randomness source, per that requirement's own L6 record) nor any
    non-modulo usage. This predicate flags ANY read of block.timestamp,
    now, block.number, block.prevrandao, or block.difficulty, regardless
    of how the value is subsequently used -- a text-grounded, deliberately
    over-inclusive trigger (both requirements' own applicability_rule
    notes these values are only a CONCERN, not automatically a violation
    -- the semantic condition, not built here, is where that judgment
    belongs).
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                for v in node.solidity_variables_read:
                    if v.name in BLOCK_DATA_SOLIDITY_VAR_NAMES:
                        findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": f"reads {v.name}"})
    return findings


def find_cross_boundary_block_data_argument(
    slither: Slither, req_id: str = "req-2-block-data-misuse", max_hops: int = 4,
) -> list[dict]:
    """Targeted, mechanical extension of `find_block_data_usage`. That
    predicate flags a function only at the LOCATION where it itself
    reads block.timestamp/block.number/etc -- it can never ask "is the
    CALLER passing the right kind of value into this". This predicate
    flags the CALLER's own location instead, whenever it calls (directly
    or transitively, within `max_hops` call-graph hops) into a function
    `find_block_data_usage` already flagged.

    Grounded directly in req-2-block-data-misuse's own normative text
    and explanatory guidance (never in EVMbench): the requirement's spec
    text names, as its own worked example, "using block.number / 14 as
    a proxy for elapsed seconds" -- a value computed in ONE place and
    misused according to a DIFFERENT function's assumption about what it
    represents. A property derived only at the block-data-reading
    function's own location can never pose that question; it's only
    askable from the caller's side. This predicate identifies WHERE to
    ask it -- like every predicate in this module, it does not verify
    the argument's actual semantic correctness itself (that judgment
    belongs to the investigating agent), it only locates the real
    candidate.

    Root-cased by a real audit run: LendingLedger.update_market computes
    `epoch` from block.number and passes it to GaugeController.
    gauge_relative_weight_write, which forwards it into _get_weight/
    _get_sum -- functions `find_block_data_usage` already flags via
    their own `t > block.timestamp` comparisons, two call-graph hops
    away from update_market. Without this predicate, no property is
    ever derived AT update_market asking whether `epoch`'s semantics
    match what the callee expects.

    Mechanical, not exhaustive: uses Slither's own `internal_calls`/
    `high_level_calls` per function to build a direct-callee adjacency
    map, then a breadth-first search up to `max_hops` (capped, matching
    this project's own convention elsewhere for bounding a search rather
    than letting it run unbounded) to test reachability.

    Deliberately does NOT skip a function that's already flagged by
    `find_block_data_usage` for its own direct read: real audit
    behavior showed this location can still be crowded out of the
    per-requirement evidence pool's top-`max_locations` cut by other
    functions with far more raw block-data reads (e.g. a checkpoint
    function with a dozen block.timestamp reads outranking a caller
    with four block.number reads) -- adding a second, independent
    evidence item for the SAME location, grounded in a different signal
    (call-graph reachability, not a raw read count), gives it another,
    real chance to survive that ranking rather than silently relying on
    its own direct-read evidence alone.
    """
    flagged = {
        tuple(f["location"].split(".", 1))
        for f in find_block_data_usage(slither, req_id)
    }

    adjacency: dict[tuple[str, str], set[tuple[str, str]]] = {}
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            key = (contract.name, func.name)
            callees: set[tuple[str, str]] = set()
            for call_op in func.internal_calls:
                callee = getattr(call_op, "function", None)
                callee_contract = getattr(callee, "contract", None) if callee else None
                if callee is not None and callee_contract is not None:
                    callees.add((callee_contract.name, callee.name))
            for target_contract, call_op in func.high_level_calls:
                callee = getattr(call_op, "function", None)
                if callee is not None:
                    callees.add((target_contract.name, callee.name))
            adjacency[key] = callees

    def reaches_flagged(start: tuple[str, str]) -> tuple[str, str] | None:
        visited = {start}
        frontier = [start]
        for _ in range(max_hops):
            next_frontier = []
            for node in frontier:
                for callee in adjacency.get(node, ()):
                    if callee in flagged:
                        return callee
                    if callee not in visited:
                        visited.add(callee)
                        next_frontier.append(callee)
            frontier = next_frontier
            if not frontier:
                break
        return None

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            key = (contract.name, func.name)
            target = reaches_flagged(key)
            if target is not None:
                findings.append({
                    "req_id": req_id, "location": f"{contract.name}.{func.name}",
                    "detail": f"calls (directly or transitively, within {max_hops} hops) into "
                              f"block-data-sensitive function {target[0]}.{target[1]}",
                })
    return findings


def find_unprotected_arithmetic(slither: Slither, req_id: str = "req-2-overflow-underflow") -> list[dict]:
    """req-2-overflow-underflow (M) trigger, per its own L6 record:
    arithmetic in `unchecked {}` blocks, or in code compiled <0.8.0
    (unchecked by default), or via inline assembly (bypasses checks
    entirely). Explicitly noted in that record as a COARSE, deliberately
    over-inclusive trigger -- `unchecked {}` is also used for benign gas
    optimization where overflow is provably unreachable (e.g. a bounded
    loop counter), which this predicate cannot distinguish from genuinely
    risky arithmetic; that judgment belongs to the semantic-condition
    component (L8), not here.

    Two of the three named sub-conditions are implemented (unchecked-block
    arithmetic via node.scope.is_checked, confirmed by direct inspection
    of a real compiled example -- not documented anywhere in Slither's own
    detector source, since no existing detector reads this field; and
    pre-0.8.0 arithmetic via compilation_unit.solc_version). The third
    (arithmetic specifically WITHIN inline assembly, as opposed to mere
    assembly presence) is NOT implemented -- flagged, not silently
    skipped, since distinguishing arithmetic opcodes from other assembly
    content requires parsing the raw Yul/assembly text, not yet done.
    """
    from slither.slithir.operations import Binary, BinaryType

    arithmetic_ops = {BinaryType.ADDITION, BinaryType.SUBTRACTION, BinaryType.MULTIPLICATION, BinaryType.POWER}
    pre_080 = tuple(int(x) for x in slither.compilation_units[0].solc_version.split(".")) < (0, 8, 0)

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                is_unchecked_scope = not getattr(node.scope, "is_checked", True)
                if not (is_unchecked_scope or pre_080):
                    continue
                for ir in node.irs:
                    if isinstance(ir, Binary) and ir.type in arithmetic_ops:
                        reason = "inside unchecked{} block" if is_unchecked_scope else f"solc {slither.compilation_units[0].solc_version} < 0.8.0 (unchecked by default)"
                        findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": f"{ir.type.value} operation, {reason}"})
    return findings


def find_state_write_after_external_call(slither: Slither, req_id: str) -> list[dict]:
    """req-1-use-c-e-i (S) / req-2-external-calls (M)'s CEI sub-clause /
    req-3-external-calls (Q)'s trigger, all sharing this concept per their
    respective records. Deliberately BROADER than Slither's own
    reentrancy-eth/reentrancy-no-eth/reentrancy-benign/reentrancy-events
    detectors, whose own docstring says they're heuristic-based and check
    for EXPLOITABLE reentrancy (an attacker-reachable reentrant call path)
    -- per this requirement's own L4/L6 records, EthTrust's CEI
    requirement is about the raw ORDERING itself (effects before
    interaction), regardless of whether a concrete exploit is currently
    reachable. Real CFG reachability via node.sons (not just node-ID
    ordering, which doesn't hold across branches/loops): for every node
    containing an external call, does ANY node reachable via the
    control-flow graph afterward write to a state variable.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                if not (node.high_level_calls or node.low_level_calls):
                    continue
                reachable = _reachable_nodes(node)
                writer = next((n for n in reachable if n.state_variables_written), None)
                if writer:
                    findings.append(
                        {
                            "req_id": req_id,
                            "location": f"{contract.name}.{func.name}",
                            "detail": f"external call at node {node.node_id} followed by state write at node {writer.node_id} (CFG-reachable)",
                        }
                    )
    return findings


def _reachable_nodes(start_node) -> set:
    seen = set()
    frontier = list(start_node.sons)
    while frontier:
        n = frontier.pop()
        if n in seen:
            continue
        seen.add(n)
        frontier.extend(n.sons)
    return seen


def find_external_call_presence(slither: Slither, req_id: str) -> list[dict]:
    """Simple standalone 'makes external calls' trigger, shared by several
    M/Q requirements' applicability rules (req-2-avoid-readonly-
    reentrancy, req-2-random-enough's sibling req-3-external-calls' own
    trigger reuse, etc.) -- any high_level_calls or low_level_calls at
    any node.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                if node.high_level_calls or node.low_level_calls:
                    findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "makes an external call"})
    return findings


def find_documented_trigger_sites(slither: Slither) -> list[dict]:
    """req-2-documented (M): 'MUST document the need for each instance of'
    8 named triggers -- CREATE2, assembly{}, selfdestruct()/suicide(),
    external calls, delegatecall(), overflow/underflow-prone code,
    block.number/block.timestamp, oracle/pseudo-randomness use.
    Composes 7 of the 8 already-built predicates (this requirement's own
    L6 record explicitly noted all 8 triggers are shared with other
    requirements built elsewhere in this project -- confirmed true for 7).
    Oracle usage specifically is NOT composed here: unlike the other 7,
    'oracle' isn't a language construct EthTrust's text names directly
    (the way block.timestamp or delegatecall() are) -- detecting it would
    require maintaining a list of known oracle interface signatures (e.g.
    Chainlink's latestRoundData), which is closer to an invented
    heuristic than a text-grounded derivation. Left unbuilt and flagged,
    not guessed at.
    """
    from slither.detectors.statements.assembly import Assembly

    findings = []
    findings += find_create2_usage(slither)
    findings += run_reused_slither_detector(slither, [Assembly], "req-2-documented")
    findings += find_selfdestruct_presence(slither, req_id="req-2-documented")
    findings += find_external_call_presence(slither, req_id="req-2-documented")
    findings += find_delegatecall_presence(slither, req_id="req-2-documented")
    findings += find_unprotected_arithmetic(slither, req_id="req-2-documented")
    findings += find_block_data_usage(slither, req_id="req-2-documented")
    # 8th trigger, oracle/pseudo-randomness use: pseudo-randomness is
    # already covered by find_block_data_usage above; oracle usage
    # specifically is NOT covered -- see docstring.
    return findings


def find_fuzzing_evidence(repo_root: Path, sol_test_paths: list[Path], req_id: str = "req-R-fuzzing-in-testing") -> list[dict]:
    """req-R-fuzzing-in-testing (GP): 'Fuzzing SHOULD be used to probe
    Tested Code for errors'. Presence-only check per this requirement's
    own strategy note: an Echidna/Medusa config file, OR a Foundry-
    convention test function taking one or more parameters (the standard
    way Foundry recognizes a fuzz test -- `forge test` randomizes any
    parameterized test function's inputs automatically, no special
    annotation needed).
    """
    findings = []
    for name in ("echidna.yaml", "echidna.yml", "medusa.json"):
        if (repo_root / name).exists():
            findings.append({"req_id": req_id, "location": name, "detail": "fuzzing tool config present"})
    for p in sol_test_paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"function\s+(test\w*)\s*\(([^)]+)\)", text):
            params = m.group(2).strip()
            if params:
                findings.append({"req_id": req_id, "location": f"{p}:{m.group(1)}", "detail": "Foundry-convention parameterized test function (fuzzed by forge test)"})
    return findings


def find_mutation_testing_evidence(repo_root: Path, req_id: str = "req-R-mutation-testing") -> list[dict]:
    """req-R-mutation-testing (GP): 'Mutation Testing SHOULD be used to
    evaluate and improve the quality of test suites'. Presence-only check:
    a config file for a known mutation-testing tool (gambit, universal
    mutator, vertigo).
    """
    findings = []
    for name in ("gambit.json", ".gambit.json", "universalmutator.yaml", "vertigo.toml", "vertigo.yaml"):
        if (repo_root / name).exists():
            findings.append({"req_id": req_id, "location": name, "detail": "mutation testing tool config present"})
    return findings


def find_formal_verification_evidence(repo_root: Path, sol_source_paths: list[Path], req_id: str = "req-R-formal-verification") -> list[dict]:
    """req-R-formal-verification (GP): 'The Tested Code SHOULD undergo
    formal verification'. Presence-only check: a Certora spec file
    (*.spec), a Certora conf file (*.conf mentioning certora), or
    Solidity's own SMTChecker pragma (`pragma experimental SMTChecker;`
    or the newer `// SPDX...` + `settings { "modelChecker": ...}` foundry
    config -- checked here only for the simpler in-source pragma form).
    """
    findings = []
    for p in repo_root.rglob("*.spec"):
        findings.append({"req_id": req_id, "location": str(p), "detail": "Certora spec file present"})
    for p in repo_root.rglob("*.conf"):
        if "certora" in p.read_text(encoding="utf-8", errors="replace").lower():
            findings.append({"req_id": req_id, "location": str(p), "detail": "Certora conf file present"})
    for p in sol_source_paths:
        if "SMTChecker" in p.read_text(encoding="utf-8", errors="replace"):
            findings.append({"req_id": req_id, "location": str(p), "detail": "SMTChecker pragma present"})
    return findings


def find_ecrecover_usage(slither: Slither, req_id: str) -> list[dict]:
    """req-2-signature-verification (M) / req-2-malleable-signatures-for-
    replay (M) shared trigger, per their L6 records: signature-
    verification usage. `ecrecover` is a SolidityCall IR (confirmed by
    direct inspection, not guessed), directly named in Solidity itself --
    the same mechanism as find_encode_packed_untainted_collision's
    SolidityFunction matching.
    """
    from slither.core.declarations import SolidityFunction

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for ir in func.solidity_calls:
                if ir.function == SolidityFunction("ecrecover(bytes32,uint8,bytes32,bytes32)"):
                    findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "ecrecover() used directly"})
    return findings


def find_oz_ecdsa_library_usage(slither: Slither, req_id: str = "req-2-malleable-signatures-for-replay") -> list[dict]:
    """req-2-malleable-signatures-for-replay (M)'s malleability sub-
    condition: OpenZeppelin's ECDSA.recover()/tryRecover() enforce the
    low-s-value check that blocks the classic signature-malleability
    attack; raw ecrecover() does not. This checks for a LIBRARY named
    'ECDSA' being used (the OZ convention specifically) -- NOT proof that
    malleability is unhandled if absent (a project could implement its
    own guard manually), only positive evidence that the well-known safe
    pattern IS present when found. Framed as evidence, not a full
    verdict, consistent with this requirement's own DETERMINISTIC_
    EVIDENCE_ONLY framing for its trigger components.
    """
    from slither.slithir.operations import LibraryCall

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                for ir in node.irs:
                    # `using ECDSA for bytes32; h.recover(sig)` compiles to a
                    # LibraryCall IR (confirmed by direct inspection, not
                    # internal_calls as first guessed -- library calls via
                    # `using X for Y` are their own IR operation type).
                    if isinstance(ir, LibraryCall) and ir.function.contract.name == "ECDSA" and ir.function.name in ("recover", "tryRecover"):
                        findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "uses OpenZeppelin ECDSA.recover/tryRecover (malleability-guarded)"})
    return findings


def find_division_in_value_context(slither: Slither, req_id: str = "req-2-check-rounding") -> list[dict]:
    """req-2-check-rounding (M) coarse trigger, per its own L6 record:
    'similar in character to req-2-overflow-underflow's coarse trigger'.
    Any DIVISION binary operation -- deliberately broad (division is the
    only arithmetic operator that can introduce rounding at all; whether
    a SPECIFIC division is value-affecting and whether its rounding is
    exploitable both require semantic review, not attempted here).
    """
    from slither.slithir.operations import Binary, BinaryType

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                for ir in node.irs:
                    if isinstance(ir, Binary) and ir.type == BinaryType.DIVISION:
                        findings.append({"req_id": req_id, "location": f"{contract.name}.{func.name}", "detail": "division operation (potential rounding)"})
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


def find_erc_interface_conformance(slither: Slither, req_id: str = "req-R-follow-erc-standards") -> list[dict]:
    """req-R-follow-erc-standards (GP): 'SHOULD conform to finalized [ERC]
    standards when it is reasonably capable of doing so for its use-case'.

    DETERMINISTIC_TRIGGER_SEMANTIC_CONDITION-shaped per this requirement's
    own GP record: identifying which ERC a contract's interface resembles,
    and whether its function signatures match that ERC's own declared
    return types, is a checkable signature-matching exercise; whether
    pursuing that ERC was 'reasonably' applicable to the contract's
    use-case, and whether full conformance (events, invariants, not just
    signatures) holds, are semantic judgments this predicate does not make.

    Deliberately reuses Slither's OWN ERC-resemblance heuristics
    (`Contract.is_possible_erc20`/`is_possible_erc721`) and Slither's OWN
    interface-correctness checkers
    (`IncorrectERC20InterfaceDetection`/`IncorrectERC721InterfaceDetection`,
    both of which encode ERC-20/ERC-721's own standardized function
    signatures) rather than re-deriving a signature list here -- the same
    'reuse an existing analyzer's own construct-level knowledge, don't
    reinvent it' discipline used throughout L4/L5, applied to a GP
    requirement instead of an S requirement.
    """
    from slither.detectors.erc.erc20.incorrect_erc20_interface import (
        IncorrectERC20InterfaceDetection,
    )
    from slither.detectors.erc.incorrect_erc721_interface import (
        IncorrectERC721InterfaceDetection,
    )

    findings = []
    for contract in slither.contracts_derived:
        resembles_erc20 = contract.is_possible_erc20()
        resembles_erc721 = contract.is_possible_erc721()
        if not resembles_erc20 and not resembles_erc721:
            continue

        if resembles_erc721 and resembles_erc20:
            standard = "ERC721"
            mismatches = IncorrectERC721InterfaceDetection.detect_incorrect_erc721_interface(contract)
            signature_check_performed = True
        elif resembles_erc20:
            standard = "ERC20"
            mismatches = IncorrectERC20InterfaceDetection.detect_incorrect_erc20_interface(contract)
            signature_check_performed = True
        else:
            # resembles_erc721 only: Slither's own erc721 checker requires
            # is_possible_erc20() to ALSO be true before it runs at all
            # (see incorrect_erc721_interface.py's own detect_ function
            # gate) -- so no signature check actually executes for this
            # case. Reported honestly as "not performed" rather than
            # defaulting to a misleading "conforms".
            standard = "ERC721_ONLY_RESEMBLANCE_NO_CHECK_AVAILABLE"
            mismatches = []
            signature_check_performed = False

        findings.append({
            "req_id": req_id,
            "location": contract.name,
            "detail": (
                f"resembles {standard}; signature_check_performed="
                f"{signature_check_performed}; "
                f"interface_mismatches={[f.full_name for f in mismatches]}"
            ),
        })
    return findings


def find_create2_deployed_target_violations(slither: Slither, req_id: str = "req-2-protect-create2") -> list[dict]:
    """req-2-protect-create2 (M): 'For Tested Code that uses the CREATE2
    instruction, any contract to be deployed using CREATE2 MUST be within
    the Tested Code, and MUST NOT use any selfdestruct(), delegatecall()
    nor callcode() instructions...'.

    Genuine cross-requirement reuse, per this requirement's own L6
    record: for the statically-resolvable case (high-level
    `new X{salt: ...}()`), Slither's NewContract IR exposes the deployed
    contract as a real `Contract` object (`ir.contract_created`) --
    already necessarily part of the compiled Tested Code (it couldn't
    compile otherwise), so the 'within Tested Code' clause is trivially
    satisfied for this shape. The same object plus its base contracts
    (`.inheritance`) are then fed straight into
    `find_selfdestruct_presence`/`find_delegatecall_presence` (both
    req-1-level predicates, unmodified in behavior, just scoped to the
    target's own code instead of a whole-unit scan) to check the
    selfdestruct/delegatecall/callcode clause.

    For the low-level shape (raw `create2` opcode in assembly, per
    req-1-no-create2's own two-shape derivation), the deployed contract's
    bytecode is an opaque runtime value -- its identity is NOT statically
    resolvable from Tested Code at all, so NEITHER the 'within Tested
    Code' clause NOR the selfdestruct/delegatecall/callcode clause can be
    checked. This is reported as an explicit evidence gap, not silently
    treated as passing or skipped.

    'Fully compatible with the claims of the contract author' is a
    semantic condition (L8), not attempted here.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                for ir in node.irs:
                    if type(ir).__name__ == "NewContract" and getattr(ir, "call_salt", None) is not None:
                        target = ir.contract_created
                        target_and_bases = [target] + list(target.inheritance)
                        violations = (
                            find_selfdestruct_presence(slither, req_id=req_id, contracts=target_and_bases)
                            + find_delegatecall_presence(slither, req_id=req_id, contracts=target_and_bases)
                        )
                        if violations:
                            for v in violations:
                                findings.append({
                                    "req_id": req_id,
                                    "location": f"{contract.name}.{func.name} (CREATE2-deploys {target.name})",
                                    "detail": f"deployed target violation: {v['detail']} in {v['location']}",
                                })
                        else:
                            findings.append({
                                "req_id": req_id,
                                "location": f"{contract.name}.{func.name} (CREATE2-deploys {target.name})",
                                "detail": f"deployed target {target.name} statically resolved, within Tested Code, no selfdestruct/delegatecall/callcode found",
                            })
                if node.type.name == "ASSEMBLY" and "create2" in _assembly_block_text(node):
                    findings.append({
                        "req_id": req_id,
                        "location": f"{contract.name}.{func.name}",
                        "detail": "assembly create2: deployed contract identity not statically resolvable from Tested Code -- cannot verify 'within Tested Code' or selfdestruct/delegatecall/callcode absence for this case (evidence gap, not a pass)",
                    })
    return findings


def find_unsafe_assembly_variable_write(slither: Slither, req_id: str = "req-2-safe-assembly") -> list[dict]:
    """req-2-safe-assembly (M): 'MUST NOT use the assembly {} instruction
    to change a variable unless the code cannot: create storage pointer
    collisions, nor allow arbitrary values to be assigned to variables of
    type function.' Per this requirement's own L6 record, this is
    DETERMINISTIC_TRIGGER_SEMANTIC_CONDITION: the two named attack
    surfaces are checkable triggers; whether a flagged write is genuinely
    a collision/arbitrary-value risk versus a deliberately-safe pattern
    (e.g. ERC-1967's well-known constant storage slot) needs semantic
    review, not attempted here.

    Slither exposes no variable-read/write IR for identifiers referenced
    only inside an assembly block (confirmed empirically: node.variables_written
    /node.state_variables_written are always empty for such nodes -- see
    AR-008), so all three triggers below are necessarily text-level
    matches against the raw assembly block content (via
    `_assembly_block_text`), not IR-level ones.

    Trigger 1 -- storage pointer reassignment (`<ident>.slot := <expr>`):
    directly reassigning a variable's OWN storage slot pointer is the
    literal 'storage pointer collision' shape the requirement names.
    Flagged unconditionally (evidence only) -- whether `<expr>` is
    attacker-influenced or a compile-time constant is not determined
    here.

    Trigger 2 -- computed `sstore` slot (`sstore(<expr>, ...)` where
    `<expr>` is not a bare `<ident>.slot` reference): writing to a slot
    not derived from any declared variable's own slot at all -- reached
    via `sstore` instead of a direct `.slot :=` assignment. This trigger
    is deliberately ambiguous by nature: a computed/non-.slot sstore
    target is BOTH the textbook collision-risk shape AND the shape of the
    well-known SAFE unstructured-storage pattern (e.g. ERC-1967's
    `keccak256(...) - 1` constant slot) -- this predicate cannot and does
    not attempt to distinguish the two.

    Trigger 3 -- direct value write to a function-typed variable's own
    slot (`sstore(<ident>.slot, <value>)` where `<ident>.slot` IS a bare,
    already-resolved reference to a declared `function`-typed state
    variable): unlike Trigger 2, the slot ADDRESS here is not in question
    (Solidity's own compiler already rejects unresolved identifiers, so a
    successfully-compiled `<ident>.slot` necessarily names a real
    variable) -- what's flagged is the VALUE write into that specific
    variable's slot, the requirement's own second named attack surface
    ('arbitrary values ... assigned to variables of type function').
    `sstore(<ident>.slot, ...)` for a non-function-typed `<ident>` is NOT
    flagged by either Trigger 2 or 3 -- a direct, unconditional write to a
    variable's own resolved slot is neither a collision risk nor a
    function-pointer risk.

    KNOWN GAP, not silently skipped: `.selector`/`.address` assignment on
    a LOCAL variable of EXTERNAL function-pointer type inside assembly
    (Solidity's only supported assembly accessors for that specific
    variable shape, per the compiler's own error message when `.slot` is
    attempted on it) could not be given ANY test fixture -- confirmed
    empirically that Slither's own Yul parser raises
    `SlitherException: unresolved reference to identifier <x>.address`
    and crashes analysis entirely for this shape (a genuine Slither
    limitation, not a predicate gap). This predicate therefore cannot
    detect that specific sub-case at all; logged, not glossed over.
    """
    findings = []
    for contract in slither.contracts:
        function_typed_state_var_names = {
            v.name for v in contract.state_variables if type(v.type).__name__ == "FunctionType"
        }
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                if node.type.name != "ASSEMBLY":
                    continue
                text = _assembly_block_text(node)

                for m in re.finditer(r"\b(\w+)\.slot\s*:=", text):
                    ident = m.group(1)
                    role = " (function-typed state variable)" if ident in function_typed_state_var_names else ""
                    findings.append({
                        "req_id": req_id,
                        "location": f"{contract.name}.{func.name}",
                        "detail": f"assembly reassigns storage slot pointer of '{ident}'{role} via .slot := -- storage pointer collision shape, evidence only",
                    })

                for m in re.finditer(r"sstore\s*\(\s*([^,]+?)\s*,", text):
                    slot_expr = m.group(1).strip()
                    direct_match = re.fullmatch(r"(\w+)\.slot", slot_expr)
                    if direct_match:
                        # bare <declared-var>.slot -- Solidity already resolved
                        # this to a real variable at compile time, so the SLOT
                        # ADDRESS itself is safe. Still flagged if that variable
                        # is function-typed: this is then a direct VALUE write
                        # into a function pointer's slot -- the requirement's
                        # 'arbitrary values assigned to variables of type
                        # function' shape, independent of the collision
                        # question above.
                        ident = direct_match.group(1)
                        if ident in function_typed_state_var_names:
                            findings.append({
                                "req_id": req_id,
                                "location": f"{contract.name}.{func.name}",
                                "detail": f"sstore() writes directly to '{ident}.slot' (function-typed state variable) -- evidence for the 'arbitrary values assigned to variables of type function' shape, whether the written value is attacker-influenced needs semantic review",
                            })
                        continue
                    findings.append({
                        "req_id": req_id,
                        "location": f"{contract.name}.{func.name}",
                        "detail": f"sstore() with computed/non-.slot storage slot expression '{slot_expr}' -- ambiguous: matches both the collision-risk pattern and the well-known safe unstructured-storage constant pattern, evidence only",
                    })
    return findings


def find_readonly_reentrancy_candidates(slither: Slither, req_id: str = "req-2-avoid-readonly-reentrancy") -> list[dict]:
    """req-2-avoid-readonly-reentrancy (M): 'Tested Code that makes
    external calls MUST protect itself against Read-only Re-entrancy
    Attacks' -- defined in this requirement's own context bundle: 'arises
    when a view function reads a state that will subsequently be
    changed'. Per this requirement's own L6 record, the trigger is a
    genuinely cross-function correlation (not a single-function scan):
    (1) some function writes a state variable AFTER an external call
    (the classic CEI-ordering shape, reusing the exact same CFG-
    reachability technique as `find_state_write_after_external_call` --
    that predicate's own req-1-use-c-e-i/req-2-external-calls records),
    AND (2) a SEPARATE externally-reachable `view`/`pure` function in the
    SAME contract reads that same state variable. During the reentrant
    window opened by (1)'s external call -- before its post-call write
    executes -- a caller of (2) observes a stale value, exactly the
    attack the definition names.

    DETERMINISTIC_EVIDENCE_ONLY: this predicate identifies the STRUCTURAL
    precondition (a stale-readable view function exists) -- it does not
    determine whether the stale read is actually consequential (e.g.
    whether any real external protocol integrates with this specific view
    function in a way that would be deceived), which is this
    requirement's own semantic condition per its L6 classification.
    """
    findings = []
    for contract in slither.contracts:
        stale_write_targets: dict[str, set] = {}
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                if not (node.high_level_calls or node.low_level_calls):
                    continue
                for n in _reachable_nodes(node):
                    for v in n.state_variables_written:
                        stale_write_targets.setdefault(func.name, set()).add(v)

        if not stale_write_targets:
            continue

        all_stale_vars = set()
        for vs in stale_write_targets.values():
            all_stale_vars |= vs

        for func in contract.functions_declared:
            if func.visibility not in ("public", "external"):
                continue
            if not (func.view or func.pure):
                continue
            stale_reads = set(func.all_state_variables_read()) & all_stale_vars
            if stale_reads:
                findings.append({
                    "req_id": req_id,
                    "location": f"{contract.name}.{func.name}",
                    "detail": (
                        f"view/pure function reads state variable(s) "
                        f"{sorted(v.name for v in stale_reads)}, which can be "
                        f"written AFTER an external call elsewhere in this "
                        f"contract (functions with the post-call write: "
                        f"{sorted(stale_write_targets.keys())}) -- candidate "
                        f"read-only reentrancy, structural precondition only"
                    ),
                })
    return findings


def check_compiler_version_is_latest_stable(slither: Slither, req_id: str, latest_known_stable_version: str) -> list[dict]:
    """req-R-use-latest-compiler (GP): 'SHOULD use the latest available
    stable Solidity compiler version'. Per this requirement's own GP
    record: the trigger (the compiled version, same
    `compilation_unit.solc_version` field as
    `check_compiler_version_floor`/`_exact`) is trivial, but the
    comparison target -- 'the latest available stable' version -- is a
    MOVING, externally-defined reference point as of the evaluation date,
    not something derivable from the code or the frozen EthTrust spec
    text. There is no honest way to hardcode a 'latest' version inside
    this module without it silently going stale the moment a new
    Solidity release ships.

    Resolved by making the reference an explicit, REQUIRED parameter
    (`latest_known_stable_version`) the caller must supply -- e.g. from
    the Solidity release list as of the actual evaluation date -- rather
    than a default baked into this module. This keeps the external-
    evidence dependency visible and auditable (the caller's supplied
    value is itself evidence, inspectable per-run) instead of hidden
    inside a predicate that looks self-contained but silently isn't.
    """
    actual = slither.compilation_units[0].solc_version
    if actual != latest_known_stable_version:
        return [{"req_id": req_id, "location": "compiler config", "detail": f"solc {actual} != caller-supplied latest known stable version {latest_known_stable_version} (external, time-anchored reference -- not derived from spec text)"}]
    return []


def find_keccak256_calls_chainid_dependency(slither: Slither, req_id: str = "req-1-eip155-chainid") -> list[dict]:
    """req-1-eip155-chainid (S): 'MUST create hashes for transactions
    that incorporate chainid values ... [EIP-155]'. Per this
    requirement's own L5 record: the APPLICABILITY side ('is this hash a
    transaction/signature-authorization hash at all') is an
    AMBIGUOUS_TEXT_GAP -- EthTrust's own text names no specific Solidity
    construct for recognizing signing-hash sites, so no predicate for
    that half is derivable without importing outside domain knowledge.
    This function implements ONLY the record's other, explicitly
    text-grounded component (`conformance-hash-incorporates-chainid`):
    'chainid' IS a term the requirement's own L1 enumerated_terms name
    directly, and checking whether `block.chainid` is a dependency of a
    given `keccak256()` call is mechanically checkable.

    Reports EVERY `keccak256()` call site and whether `block.chainid` is
    read in the SAME CFG node as that call (confirmed empirically: for a
    single-expression `keccak256(abi.encodePacked(..., block.chainid))`,
    Slither's `node.solidity_variables_read` correctly includes
    'block.chainid' on that node) -- NOT which of those sites are
    actually transaction/signature-authorization hashes (the blocked
    applicability half). Consuming code (or the L8 semantic reviewer this
    requirement's own record says it converges on) must independently
    determine which reported sites are relevant tx-signing hashes.

    Deliberate, documented limitation: this only detects `block.chainid`
    read in the SAME node as the `keccak256()` call, not a chainid value
    CACHED into a local/state variable earlier and referenced later
    (e.g. `uint c = block.chainid; ... keccak256(abi.encodePacked(c))`)
    -- that would require real data-dependency/taint tracking across
    statements, which this predicate does not attempt (the requirement's
    own L5 record scoped this component to the isolated,
    already-tractable case, not full interprocedural analysis).
    """
    from slither.slithir.operations import SolidityCall

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                for ir in node.irs:
                    if isinstance(ir, SolidityCall) and ir.function.name == "keccak256(bytes)":
                        has_chainid = any(v.name == "block.chainid" for v in node.solidity_variables_read)
                        findings.append({
                            "req_id": req_id,
                            "location": f"{contract.name}.{func.name}",
                            "detail": (
                                f"keccak256() call at node {node.node_id}: "
                                f"block.chainid {'IS' if has_chainid else 'is NOT'} "
                                f"read in the same expression -- whether this is a "
                                f"transaction/signature-authorization hash at all is "
                                f"NOT determined here (blocked applicability "
                                f"component, see this requirement's own L5 record)"
                            ),
                        })
    return findings


def find_selfdestruct_protection_status(slither: Slither, req_id: str = "req-2-self-destruct") -> list[dict]:
    """req-2-self-destruct (M): the Set-of-Overriding-Requirements
    exception to req-1-self-destruct -- selfdestruct()/suicide() MAY be
    present provided it 'can only be called by authorised parties'. Per
    this record's own classification_rationale: Slither's `suicidal`
    detector was explicitly REJECTED as a match for the S-level
    mere-presence check (req-1-self-destruct), because it only flags
    UNPROTECTED calls -- but that same protection heuristic
    (`Function.is_protected()`, a public method on Slither's own Function
    class, not merely internal to the suicidal.py detector) is exactly
    the right evidence for THIS M-level requirement's authorization
    condition.

    Reuses `Function.is_protected()` directly (checks for `onlyOwner` in
    modifiers, or `msg.sender` used directly in a require/assert/if
    condition -- per its own docstring) rather than reimplementing
    protection detection. Mirrors `suicidal.py`'s own scope choices
    (skips constructors -- always considered protected; only public/
    external functions are in scope, since a private/internal function
    cannot itself be called by an unauthorized external party directly).

    DETERMINISTIC_EVIDENCE_ONLY, not DETERMINISTIC_COMPLETE:
    `is_protected()`'s own docstring documents a real false-negative
    case (`address a = msg.sender; require(a == owner);` is NOT detected
    as protected) -- so an UNPROTECTED result here is evidence, not
    proof, that the function is genuinely open to anyone.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_declared:
            if func.is_constructor:
                continue
            if func.visibility not in ("public", "external"):
                continue
            calls = [ir.function.name for ir in func.all_internal_calls() if ir.function]
            if not ("selfdestruct(address)" in calls or "suicide(address)" in calls):
                continue
            protected = func.is_protected()
            findings.append({
                "req_id": req_id,
                "location": f"{contract.name}.{func.name}",
                "detail": (
                    f"selfdestruct/suicide-containing function is "
                    f"{'PROTECTED (access-controlled)' if protected else 'UNPROTECTED -- callable by anyone'} "
                    f"per Slither's own is_protected() heuristic (evidence, "
                    f"not proof -- see this function's own documented "
                    f"false-negative case)"
                ),
            })
    return findings


def find_linting_violations_via_reused_detectors(slither: Slither, req_id: str = "req-3-linted") -> list[dict]:
    """req-3-linted (Q): 'Code Linting' -- 7 named sub-clauses, per this
    requirement's own record flagged as STRUCTURALLY MISPLACED at Level
    [Q] ('the clearest example in the whole Q-level batch of the S/M/Q
    axis NOT being a verification-method axis' -- these are classic
    static-lint rules, mechanically closer to Level [S] in character).
    This function reuses 7 EXISTING Slither detectors directly (via
    `run_reused_slither_detector`, the same generic wrapper already used
    for req-1-no-assembly/req-1-check-return), covering 3 of the 7 named
    sub-clauses:

    - 'MUST NOT create unnecessary variables' -> `UnusedStateVars`. Only
      the STATE-variable subset is covered -- Slither ships no general
      unused-LOCAL-variable detector (confirmed by search); a genuinely
      unused local variable is not detected by any reused component
      here.
    - 'MUST NOT use the same name for functions, variables or other
      tokens ... within the same scope' -> all 4 of Slither's own
      shadowing detectors (`LocalShadowing`, `StateShadowing`,
      `BuiltinSymbolShadowing`, `ShadowingAbstractDetection`).
    - 'MUST NOT include code that cannot be reached in execution' ->
      `DeadCode`. NOTE this is a PARTIAL/analogous match, not exact:
      Slither's `DeadCode` detects internal FUNCTIONS never called from
      any entry point, not unreachable STATEMENTS within a function body
      (e.g. code after an unconditional `return`/`revert`) -- the
      requirement's literal 'unreachable code' phrasing is closer to the
      latter, which this reused detector does not cover.
    - 'MUST NOT contain a function that has the same name as the smart
      contract unless it is explicitly declared as a constructor' ->
      `MultipleConstructorSchemes`. NOT exercised by this module's own
      test suite: triggering it requires a pre-0.4.22 Solidity compiler
      (the old function-named-as-contract constructor scheme was removed
      entirely at 0.4.22), which is outside this project's supported
      compiler range -- included for completeness and logged as
      structurally untested here, not silently assumed working.

    The remaining 3 sub-clauses are NOT covered by this function:
    'MUST NOT include assert() statements that fail in normal operation'
    (semantic -- requires knowing what 'normal operation' is), the
    unreachable-STATEMENT half of the dead-code clause (see above), and
    the pragma/visibility clauses (see
    `find_pragma_solidity_version_specified` and this requirement's own
    updated record for the visibility clause, which turns out to need no
    predicate at all).
    """
    from slither.detectors.variables.unused_state_variables import UnusedStateVars
    from slither.detectors.functions.dead_code import DeadCode
    from slither.detectors.compiler_bugs.multiple_constructor_schemes import MultipleConstructorSchemes
    from slither.detectors.shadowing.local import LocalShadowing
    from slither.detectors.shadowing.state import StateShadowing
    from slither.detectors.shadowing.builtin_symbols import BuiltinSymbolShadowing
    from slither.detectors.shadowing.abstract import ShadowingAbstractDetection

    return run_reused_slither_detector(
        slither,
        [
            UnusedStateVars,
            DeadCode,
            MultipleConstructorSchemes,
            LocalShadowing,
            StateShadowing,
            BuiltinSymbolShadowing,
            ShadowingAbstractDetection,
        ],
        req_id,
    )


def find_pragma_solidity_version_specified(sol_source_paths: list[Path], req_id: str = "req-3-linted") -> list[dict]:
    """req-3-linted (Q) sub-clause: 'MUST specify one or more Solidity
    compiler versions in its pragma directive'. Pure text presence check
    on raw source, same style as `find_spdx_or_license_file` -- flags
    files MISSING a `pragma solidity` directive (this function reports
    violations, i.e. absence, matching the 'MUST' framing, unlike the
    license check which reports presence as evidence FOR compliance).
    """
    findings = []
    for p in sol_source_paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"pragma\s+solidity\s", text):
            findings.append({"req_id": req_id, "location": str(p), "detail": "no 'pragma solidity ...' directive found in this file"})
    return findings


def find_state_mutating_function_protection_status(slither: Slither, req_id: str = "req-3-access-control") -> list[dict]:
    """req-3-access-control (Q): 'Enforce Least Privilege' -- 'Tested
    code that enables privileged access MUST implement appropriate
    access control mechanisms'. Per this requirement's own record, the
    mechanically-checkable half is 'presence of an access-control
    modifier (onlyOwner-style, role-based)'; whether the GRANTED
    privilege is the MINIMUM necessary needs the documentation
    cross-check this layer exists for.

    Scoping judgment, made explicit rather than silent: EthTrust's own
    conditioning clause ('enables privileged access') names no concrete
    Solidity construct to detect directly. This function interprets
    STATE-MUTATING public/external functions as the defensible proxy for
    'enables ... access' (a pure view/pure function cannot itself change
    anything, so access control is not a meaningful question for it) --
    broader than 'privileged' in the strict sense, narrower than 'every
    public function'. This interpretive choice is logged here, not
    treated as self-evidently correct.

    Reuses `Function.is_protected()` (the same Slither method already
    used by `find_selfdestruct_protection_status`) rather than
    reimplementing access-control-modifier detection.
    """
    findings = []
    for contract in slither.contracts:
        for func in contract.functions_declared:
            if func.is_constructor:
                continue
            if func.visibility not in ("public", "external"):
                continue
            if not func.all_state_variables_written():
                continue
            protected = func.is_protected()
            findings.append({
                "req_id": req_id,
                "location": f"{contract.name}.{func.name}",
                "detail": (
                    f"state-mutating function is "
                    f"{'PROTECTED (access-controlled)' if protected else 'UNPROTECTED -- callable by anyone'} "
                    f"per Slither's own is_protected() heuristic -- evidence "
                    f"only, whether the granted access level is the MINIMUM "
                    f"necessary needs a documentation cross-check, not "
                    f"attempted here"
                ),
            })
    return findings


def find_unvalidated_function_parameters(slither: Slither, req_id: str = "req-3-all-valid-inputs") -> list[dict]:
    """req-3-all-valid-inputs (Q): 'Process All Inputs' -- 'MUST
    validate inputs, and function correctly whether the input is as
    designed or malformed'. Per this requirement's own record, a
    PARTIAL deterministic signal is plausible: 'presence/absence of
    require()-style bounds checks on function parameters is
    syntactically locatable'.

    For EVERY function with at least one parameter -- ALL visibilities,
    not just public/external -- checks whether ANY `require()`/`assert()`
    call anywhere in the function body reads at least one of that
    function's own parameters (confirmed empirically: a
    `require(amount > 0, ...)` call's node has the parameter variable in
    `node.variables_read`). DETERMINISTIC_EVIDENCE_ONLY, not
    DETERMINISTIC_COMPLETE: presence of SOME require() referencing SOME
    parameter does not establish that validation is CORRECT or COMPLETE
    for every parameter and every malformed-input case -- only that the
    function is not entirely unvalidated. Flags functions where NO
    parameter is referenced in any require()/assert() at all -- the
    clearer, more defensible signal.

    CORRECTION (see AR-011): an earlier version of this predicate
    restricted scanning to `public`/`external` functions only. Re-reading
    this requirement's own normative text and definitions found NO
    textual basis for that restriction anywhere -- 'Tested Code' is
    defined broadly as all of a contract's (or related contracts')
    Solidity source, and 'inputs' is never scoped to the external
    interface specifically. The public/external-only restriction was an
    unexamined convention imported from general Solidity-audit practice
    (attack-surface framing), not a derivation from this requirement's
    own text -- exactly the kind of unsupported narrowing this project's
    methodology exists to catch. Confirmed as a real, fixable gap, not a
    theoretical one: on a real EVMbench target (2023-07-pooltogether),
    the OLD scope missed `Vault._burn`/`_mint`/`_transfer` entirely --
    all three are `internal` overrides with a `uint96(_shares)` truncating
    cast and ZERO require()/assert() touching `_shares` anywhere in their
    bodies (confirmed by direct inspection of the real source) -- exactly
    the real vulnerability (EVMbench finding H-02) this predicate exists
    to help surface evidence for, and the OLD scope could never have
    found it regardless of anything else in the pipeline.
    """
    from slither.slithir.operations import SolidityCall

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_declared:
            if func.is_constructor:
                continue
            params = set(func.parameters)
            if not params:
                continue
            validated_params = set()
            for node in func.nodes:
                is_require_or_assert = any(
                    isinstance(ir, SolidityCall) and ir.function.name in ("require(bool)", "require(bool,string)", "assert(bool)")
                    for ir in node.irs
                )
                if is_require_or_assert:
                    validated_params |= set(node.variables_read) & params
            if not validated_params:
                findings.append({
                    "req_id": req_id,
                    "location": f"{contract.name}.{func.name}",
                    "detail": f"none of this function's parameters ({sorted(p.name for p in params)}) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling",
                })
    return findings


def _bound_check_covers_variable(func, variable, dest_bits: int) -> str | None:
    """Shared helper for `find_unsafe_narrowing_cast`: does ANY node in
    `func` contain a require()/assert()/SolidityCall-revert-style check
    that reads `variable` and bounds it against `dest_bits`'s max value
    (`2**dest_bits - 1`)? Checked via TWO real, confirmed-empirically
    idioms (not guessed): (1) a literal constant operand in a Binary
    comparison whose value exactly equals `2**dest_bits - 1` (confirmed:
    Slither's IR resolves a raw numeric literal like
    `79228162514264337593543950335` to a `Constant` with `.value` set);
    (2) the `type(uintN).max`/`type(intN).max` idiom, which does NOT
    constant-fold to a `Constant` at the IR level (confirmed empirically
    -- it resolves to an opaque `TemporaryVariable`), so is matched
    instead via `node.expression`'s own string form, which reliably
    contains the literal text `type()(uintN).max` for this idiom.
    Returns a human-readable description of the check found, or None.
    """
    from slither.slithir.operations import Binary

    max_value = (2 ** dest_bits) - 1
    for node in func.nodes:
        if variable not in node.variables_read:
            continue
        expr_text = str(node.expression) if node.expression else ""
        for ir in node.irs:
            if not isinstance(ir, Binary):
                continue
            if variable not in (ir.variable_left, ir.variable_right):
                continue
            other = ir.variable_right if ir.variable_left is variable else ir.variable_left
            if getattr(other, "value", None) == max_value:
                return f"{expr_text.strip()} (literal bound {max_value} == 2**{dest_bits}-1)"
        if ".max" in expr_text and (f"uint{dest_bits})" in expr_text or f"int{dest_bits})" in expr_text):
            return f"{expr_text.strip()} (type(...).max idiom)"
    return None


def find_unsafe_narrowing_cast(slither: Slither, req_id: str = "req-3-all-valid-inputs") -> list[dict]:
    """req-3-all-valid-inputs (Q): 'Tested Code MUST validate inputs,
    and function correctly whether the input is as designed or
    malformed.' A value larger than a narrower destination integer
    type's max representable value IS a malformed input for that
    specific downstream representation -- silently truncating it via an
    explicit narrowing cast, without first validating the value fits,
    is a direct failure to 'function correctly' on a malformed input;
    this is the exact mechanism EVMbench finding H-02 (2023-07-
    pooltogether) demonstrates (`uint96(_shares)` with no
    `_shares <= type(uint96).max` check), confirmed by inspecting the
    real fix diff, not assumed. General, NOT specific to that one
    codebase: fires on ANY `uintN(x)`/`intN(x)` explicit narrowing
    conversion (destination bit-width strictly less than the source's,
    both integer-kind, not `address`/`bytesN` reinterpretation casts --
    those have different semantics, not a magnitude-truncation risk)
    where no require()/assert() in the same function bounds the source
    value against the destination type's max. Does NOT flag code using
    OpenZeppelin's `SafeCast` library (e.g. `.toUint96()`) -- those are
    LibraryCall IR, not a raw TypeConversion, so they're structurally
    invisible to this check, which only looks for the raw, unchecked
    cast form; SafeCast's own internal implementation already performs
    exactly this bound check, which is the entire reason it exists.

    Produces STRUCTURED evidence (not just a one-line `detail` string),
    added in response to a real, reproduced L12 finding
    (RTF_V1_RUN2_REPORT.md): both L8 and the real upstream DetectGrader
    independently judged this predicate's OLD bare 'parameter not
    validated' phrasing too generic to support a confident verdict, even
    when it correctly named the exact vulnerable location. The
    structured fields name the specific operation, types, and the exact
    missing condition, per the plan's own evidence design.

    DETERMINISTIC_EVIDENCE_ONLY: confirms the cast is UNCHECKED by this
    specific bound-check idiom, not that truncation is exploitable in
    context (e.g. a value that can never realistically exceed the
    destination type's range from any reachable caller would still be
    flagged here, same over-inclusive-by-design tradeoff as this
    project's other DETERMINISTIC_EVIDENCE_ONLY predicates) -- that
    remains L8's semantic question.
    """
    from slither.slithir.operations import TypeConversion

    INTEGER_PREFIXES = ("uint", "int")

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_declared:
            for node in func.nodes:
                for ir in node.irs:
                    if not isinstance(ir, TypeConversion):
                        continue
                    src_var = ir.variable
                    src_type = getattr(src_var, "type", None)
                    dst_type = ir.type
                    if src_type is None or dst_type is None:
                        continue
                    # Check the type's STRING form is integer-kind ("uintN"/"intN")
                    # BEFORE ever touching `.size` -- confirmed by a real crash
                    # against real code (pooltogether's Vault.sol): Slither's
                    # `ElementaryType.size` is a property that RAISES
                    # `SlitherException` for non-numeric types (e.g. "string",
                    # "bool") rather than returning None, so `getattr(t, "size",
                    # None)` does NOT safely no-op the way it would for a merely
                    # MISSING attribute -- the property getter still executes and
                    # still raises. TypeConversion fires for every explicit cast,
                    # not just integer-narrowing ones, so this predicate must rule
                    # out non-integer conversions using the type's `str()` form
                    # first, never by probing `.size` speculatively.
                    src_str, dst_str = str(src_type), str(dst_type)
                    if not (src_str.startswith(INTEGER_PREFIXES) and dst_str.startswith(INTEGER_PREFIXES)):
                        continue
                    try:
                        src_size = src_type.size
                        dst_size = dst_type.size
                    except Exception:  # noqa: BLE001 -- .size can still raise for a type shape not anticipated by the check above; skip rather than crash the whole run
                        continue
                    if dst_size >= src_size:
                        continue

                    check_desc = _bound_check_covers_variable(func, src_var, dst_size)
                    src_name = getattr(src_var, "name", str(src_var))
                    location = f"{contract.name}.{func.name}"

                    if check_desc is not None:
                        continue  # validated -- not flagged, matching this module's "flag only the unchecked case" convention

                    findings.append({
                        "req_id": req_id,
                        "location": location,
                        "detail": f"unchecked narrowing cast: {src_name} ({src_str}) -> {dst_str}, no bound check found for this parameter against the destination type's max value",
                        "structured_evidence": {
                            "operation": f"narrowing type conversion {src_str} -> {dst_str}",
                            "input": {"name": src_name, "type": src_str},
                            "source_type": src_str,
                            "destination_type": dst_str,
                            "validation_found": "none",
                            "missing_safety_condition": f"{src_name} <= type({dst_str}).max",
                            "risk": f"values of {src_name} above {dst_str}'s maximum representable value ({(2**dst_size)-1}) are silently truncated by this cast rather than rejected",
                            "affected_functions": [location],
                        },
                    })
    return findings


def find_unchecked_ecrecover_result(slither: Slither, req_id: str = "req-2-signature-verification") -> list[dict]:
    """req-2-signature-verification (M): 'Tested Code MUST properly
    verify signatures to ensure authenticity of messages that were
    signed off-chain.' `ecrecover()` returns `address(0)` for a
    malformed/invalid signature (a documented Solidity/EVM behavior, not
    a project-specific fact) -- if the caller never checks the recovered
    address against `address(0)` before trusting it as 'the signer', an
    invalid signature is silently treated as authentically signed BY the
    zero address, which is exactly a failure to 'ensure authenticity'
    per this requirement's own text. This is the precise mechanism
    EVMbench finding H-03 (2026-01-tempo-mpp-streams) demonstrates,
    confirmed by inspecting the real finding text and fix diff, not
    assumed -- and independently, the SAME requirement's context bundle
    references [swcregistry], where this exact pattern is a named,
    externally-recognized weakness class (SWC-122), corroborating this
    isn't an invented check.

    General, NOT specific to any one codebase: fires on any raw
    `ecrecover()` call (the same `SolidityCall` trigger
    `find_ecrecover_usage()` already uses), OR a call to a LOCAL
    'signature-recovery wrapper' function -- a function with at least one
    `return` statement whose value is directly an `ecrecover()` call's
    result in the same CFG node (the common `return ecrecover(...);`
    idiom, including when it's only one of several return paths, e.g.
    an early `return address(0)` for a malformed-length guard clause).
    This second case was added after a real gap was found by running
    against actual code (2026-01-tempo-mpp-streams): its `_recoverSigner`
    helper wraps `ecrecover()` and returns its result directly, but the
    actual `address(0)` check (or its absence) belongs at the CALL SITE
    of `_recoverSigner`, not adjacent to the raw `ecrecover()` call
    itself -- a one-level-only trace is not a benchmark-specific special
    case, it is the general shape of 'a helper function wrapping a
    primitive', the same pattern OpenZeppelin's own `ECDSA.recover()`
    library function has (already covered separately by
    `find_oz_ecdsa_library_usage()` for the malleability angle; this is
    the equivalent for a hand-rolled, non-library wrapper).

    For both trigger shapes, traces the result to the real named variable
    it's assigned to (confirmed empirically: `address signer =
    ecrecover(...)` / `address signer = _recoverSigner(...)` both compile
    to a SolidityCall/InternalCall followed immediately by an Assignment
    IR in the same node) and checks whether that variable is ever
    compared against `address(0)` anywhere else in the function. A real,
    documented scope limit remains: a one-line inline use with NO
    intermediate named variable at either the ecrecover call OR the
    wrapper call (e.g. `return ecrecover(...) != address(0)`) is not
    traced and is reported as an explicit UNKNOWN, not silently treated
    as checked or unchecked either way -- only wrapper functions ONE
    level deep are traced, not arbitrarily nested call chains.

    DETERMINISTIC_EVIDENCE_ONLY: absence of a traced address(0) check is
    evidence the check is missing for this specific traced variable, not
    proof no equivalent protection exists anywhere in the call chain
    (e.g. a caller-side check two or more levels up) -- that broader
    question remains L8's.
    """
    from slither.core.declarations import SolidityFunction
    from slither.slithir.operations import Assignment, Binary, BinaryType, InternalCall, Return, SolidityCall

    ECRECOVER_SIG = SolidityFunction("ecrecover(bytes32,uint8,bytes32,bytes32)")

    def _zero_check_covers_variable(func, variable) -> bool:
        for other_node in func.nodes:
            if variable not in other_node.variables_read:
                continue
            expr_text = str(other_node.expression) if other_node.expression else ""
            for other_ir in other_node.irs:
                if isinstance(other_ir, Binary) and other_ir.type in (BinaryType.EQUAL, BinaryType.NOT_EQUAL):
                    if variable in (other_ir.variable_left, other_ir.variable_right) and "address(0)" in expr_text.replace(" ", ""):
                        return True
        return False

    def _named_var_for(node, tmp_result):
        for other_ir in node.irs:
            if isinstance(other_ir, Assignment) and other_ir.rvalue is tmp_result:
                return other_ir.lvalue
        return None

    # Pass 1: identify local "signature-recovery wrapper" functions --
    # a function with >=1 `return` node whose returned value is, in that
    # SAME node, an ecrecover() call's lvalue.
    wrapper_functions = set()
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            for node in func.nodes:
                ecrecover_lvalues = {ir.lvalue for ir in node.irs if isinstance(ir, SolidityCall) and ir.function == ECRECOVER_SIG}
                if not ecrecover_lvalues:
                    continue
                for ir in node.irs:
                    if isinstance(ir, Return) and any(v in ecrecover_lvalues for v in ir.values):
                        wrapper_functions.add(func)

    findings = []
    for contract in slither.contracts:
        for func in contract.functions_and_modifiers_declared:
            location = f"{contract.name}.{func.name}"
            for node in func.nodes:
                # Trigger shape 1: direct ecrecover() call.
                for ir in node.irs:
                    if isinstance(ir, SolidityCall) and ir.function == ECRECOVER_SIG:
                        named_var = _named_var_for(node, ir.lvalue)
                        _emit_ecrecover_finding(findings, req_id, location, named_var, _zero_check_covers_variable, func)
                # Trigger shape 2: call to a local wrapper function.
                for ir in node.irs:
                    if isinstance(ir, InternalCall) and ir.function in wrapper_functions:
                        named_var = _named_var_for(node, ir.lvalue)
                        _emit_ecrecover_finding(findings, req_id, location, named_var, _zero_check_covers_variable, func, via_wrapper=getattr(ir.function, "name", str(ir.function)))
    return findings


def _emit_ecrecover_finding(findings, req_id, location, named_var, zero_check_fn, func, via_wrapper=None):
    """Shared finding-construction logic for both trigger shapes in
    `find_unchecked_ecrecover_result` -- kept as one place so the
    structured-evidence schema can't silently drift between the two
    cases.
    """
    wrapper_note = f" (via local wrapper function '{via_wrapper}')" if via_wrapper else ""
    if named_var is None:
        findings.append({
            "req_id": req_id,
            "location": location,
            "detail": f"ecrecover() result{wrapper_note} used without an intermediate named variable -- cannot trace whether it is checked against address(0) (known predicate scope limit, not evidence either way)",
            "structured_evidence": {
                "operation": f"ecrecover(...){wrapper_note}",
                "possible_result": "address(0) for an invalid/malformed signature",
                "validation_found": "UNKNOWN -- result not assigned to a traceable named variable",
                "risk": "cannot be determined by this predicate; requires manual/semantic review",
            },
        })
        return

    if zero_check_fn(func, named_var):
        return  # validated -- not flagged

    findings.append({
        "req_id": req_id,
        "location": location,
        "detail": f"ecrecover() result{wrapper_note} (assigned to '{getattr(named_var, 'name', named_var)}') is never compared against address(0) anywhere in this function",
        "structured_evidence": {
            "operation": f"ecrecover(...){wrapper_note}",
            "input": {"name": getattr(named_var, "name", str(named_var)), "type": "address"},
            "possible_result": "address(0) for an invalid/malformed signature (documented Solidity/EVM behavior)",
            "validation_found": "none",
            "missing_safety_condition": f"{getattr(named_var, 'name', named_var)} != address(0)",
            "risk": "an invalid signature recovers to address(0) and, if address(0) is ever treated as authorized (e.g. an unset/default signer field), an invalid signature would be accepted as authentic",
            "affected_functions": [location],
        },
    })


_GROWTH_INSERT_METHOD_NAMES = ("push", "add", "set", "insert", "append", "enqueue")
"""Generic method-name signals for "something was added to a collection" --
deliberately covers both a raw dynamic array's own `.push` AND the common
member-function names OpenZeppelin-style `using X for Y` library wrappers
(EnumerableSet/EnumerableMap and hand-rolled equivalents) expose for the
same operation. Matched as a SUBSTRING of a node's own expression text
(e.g. `shareBalance.set(who, amount)` naturally contains `.set(` even
though `set` is defined in a separate library contract, confirmed against
a real compiled OZ-shaped Map-library fixture this session -- Slither
does not need to resolve the library call target for this signal to
fire, only the syntax of the call site itself)."""

_GROWTH_REMOVE_METHOD_NAMES = ("pop", "remove", "delete", "dequeue")
"""Same mechanism as `_GROWTH_INSERT_METHOD_NAMES`, for the inverse
operation. `"delete"` matches both `.delete(...)`-shaped library calls
and Solidity's own `delete x[...]` statement (checked separately below
via a literal `delete ` prefix, since that's a keyword, not a method
call, and would never match a `.delete(` substring)."""


def _is_growth_capable_container_type(t, _depth: int = 0) -> bool:
    """True for a dynamic array, a plain mapping, or a struct-typed
    variable that itself CONTAINS a dynamic array or mapping member
    (the generic structural shape of OpenZeppelin's EnumerableSet/
    EnumerableMap AND any hand-rolled equivalent -- verified against a
    real compiled fixture mirroring EnumerableMap's actual internal
    struct layout, `bytes32[] _keys` + `mapping(bytes32 => uint256)
    _values`, this session). Deliberately does NOT check the type's own
    NAME anywhere (no "EnumerableMap"/"EnumerableSet" string match) --
    req-3-enough-gas's own normative text names the general class
    ("data structures... that grow over time"), not any specific
    library, so detection is purely structural. `_depth` caps recursion
    into nested struct members at 1 level (a struct-of-structs-of-
    arrays is a real but rare pattern; unbounded recursion risks a
    pathological cycle in a self-referential type graph)."""
    from slither.core.declarations.structure_contract import StructureContract
    from slither.core.solidity_types import ArrayType, MappingType, UserDefinedType

    if isinstance(t, ArrayType) and t.length is None:
        return True
    if isinstance(t, MappingType):
        return True
    if _depth < 1 and isinstance(t, UserDefinedType):
        underlying = getattr(t, "type", None)
        if isinstance(underlying, StructureContract):
            for member in underlying.elems.values():
                if _is_growth_capable_container_type(member.type, _depth=_depth + 1):
                    return True
    return False


def find_unbounded_growth_with_downstream_iteration(
    slither: Slither, req_id: str = "req-3-enough-gas",
) -> list[dict]:
    """req-3-enough-gas (Q): "Sufficient Gas MUST be available to work
    with data structures in the Tested Code that grow over time" -- its
    own explanatory text names the exact mechanism this predicate
    detects verbatim: "Iterating over a structure whose size is not
    clear in advance... can result in significant increases in gas
    usage." Also registered under req-3-protect-gas ("MUST protect
    against malicious actors stealing or wasting gas" / Gas Griefing),
    a closely related obligation over the same code pattern.

    RTF_V3_REDESIGN_PLAN.md Phase 5: before this predicate, BOTH
    requirements had only `collect_documentary_and_implementation_
    evidence` registered -- a documentary README/NatSpec-vs-
    implementation comparison with NO code-pattern detection at all, so
    applicability silently depended on whether a target happened to
    document its own growth-management approach. This predicate adds a
    real structural signal, generalized (per the task brief's explicit
    instruction) across dynamic arrays, plain mappings, and any struct-
    typed collection wrapper (EnumerableSet/EnumerableMap and hand-
    rolled equivalents alike) -- see `_is_growth_capable_container_type`.

    Flags a function at the SITE WHERE THE RISK MATERIALIZES (the
    iterating/enumerating function, matching this module's existing
    convention of flagging the location an investigation should focus
    on, not the requirement's abstract subject) when, for some state
    variable of a growth-capable container type in the SAME contract:
    (1) some function calls an insertion-shaped method on it
    (`_GROWTH_INSERT_METHOD_NAMES`), (2) NO function in the contract
    calls a removal-shaped method on it (`_GROWTH_REMOVE_METHOD_NAMES`)
    -- i.e. no detected pruning path at all, and (3) this function
    contains a loop construct and reads the same variable somewhere
    within it (approximated as "the function has a loop AND reads the
    variable anywhere in its body" -- a deliberately generic, slightly
    over-inclusive signal; per Phase 5's own design principle this is
    ROUTING, not a verdict, so over-inclusion here trades a small
    false-positive-applicability cost for not missing a real pattern,
    while the investigating agent remains responsible for confirming an
    actual reachable gas-DoS path).

    Deliberately per-contract (not whole-project call-graph traversal
    like `find_cross_boundary_block_data_argument`) for this first
    version -- a removal method genuinely defined only in a SEPARATE
    contract this one never calls is, correctly, treated as "no removal
    path from this contract's own reachable surface," matching the real
    phi H-03 shape (a library CAN remove entries but the contract using
    it never calls that path).
    """
    from slither.core.cfg.node import NodeType

    findings: list[dict] = []
    for contract in slither.contracts:
        if contract.is_interface:
            continue
        growth_vars = [
            v for v in contract.state_variables_declared
            if _is_growth_capable_container_type(v.type)
        ]
        if not growth_vars:
            continue

        for gv in growth_vars:
            insert_funcs: set[str] = set()
            has_removal = False
            for func in contract.functions_and_modifiers_declared:
                for node in func.nodes:
                    touched = {x.name for x in node.state_variables_written} | {x.name for x in node.state_variables_read}
                    if gv.name not in touched:
                        continue
                    expr = str(node.expression or "")
                    if any(f".{name}(" in expr for name in _GROWTH_INSERT_METHOD_NAMES):
                        insert_funcs.add(func.name)
                    if any(f".{name}(" in expr for name in _GROWTH_REMOVE_METHOD_NAMES) or expr.strip().startswith("delete "):
                        has_removal = True

            if not insert_funcs or has_removal:
                continue  # no insertion path found, or a real removal/pruning path exists

            for func in contract.functions_and_modifiers_declared:
                has_loop = any(n.type == NodeType.STARTLOOP for n in func.nodes)
                if not has_loop:
                    continue
                reads_gv = any(gv.name in {x.name for x in n.state_variables_read} for n in func.nodes)
                if not reads_gv:
                    continue
                findings.append({
                    "req_id": req_id,
                    "location": f"{contract.name}.{func.name}",
                    "detail": (
                        f"iterates/enumerates {contract.name}.{gv.name}, a growth-capable "
                        f"container written to via {', '.join(sorted(insert_funcs))} with no "
                        f"detected removal/pruning path anywhere in {contract.name} -- "
                        f"potential unbounded gas cost as the structure grows over the "
                        f"contract's operational lifetime"
                    ),
                    "structured_evidence": {
                        "growth_variable": f"{contract.name}.{gv.name}",
                        "insertion_sites": sorted(f"{contract.name}.{f}" for f in insert_funcs),
                        "removal_sites_found": [],
                        "iterating_function": f"{contract.name}.{func.name}",
                    },
                })
    return findings
