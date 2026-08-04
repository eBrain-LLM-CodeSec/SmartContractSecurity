"""FPSL -- Flexible Prompt Strategy Library for the Commentator agent
(Agent4Vul S3.2). Five prompt strategies guide the LLM's reasoning during
comment generation:

  1. simple description        -- concise, line-level "what this does"
  2. detailed description      -- variable usage, function defs, actions
  3. role-playing               -- LLM plays an expert smart-contract auditor
  4. CoT                       -- chain-of-thought reasoning before commenting
  5. vulnerability-customized CoT -- CoT focused on specific vuln classes

All five strategies are asked to emit the same structured JSON contract
(see commentator.py's Comment model) so the Commentator can mix strategies
without changing its parsing. Strategy 5 is parameterized over EVMbench's
core vuln-class rule-of-thumb hints (not learned, just prompt content).
"""
from __future__ import annotations

VULN_CLASSES = [
    "access_control",
    "arithmetic_downcast",
    "reentrancy",
    "oracle_price",
    "accounting",
    "delegatecall",
]

# Core rule-of-thumb hints per EVMbench-relevant vuln class -- injected into
# strategy 5's prompt, not a learned/trained signal.
CORE_RULES: dict[str, str] = {
    "access_control": (
        "State-changing external/public functions that lack an owner/role check "
        "(no modifier, no msg.sender comparison) on privileged operations "
        "(minting, setting fee recipients, withdrawing funds, changing config)."
    ),
    "arithmetic_downcast": (
        "Narrowing type conversions (e.g. uint256 -> uint96/uint128/uint64) that can "
        "silently truncate large values, especially on share/balance/amount variables."
    ),
    "reentrancy": (
        "An external call (low-level .call/.send/.transfer, or a high-level call to "
        "another contract) that happens before a state variable it depends on is updated."
    ),
    "oracle_price": (
        "Price or exchange-rate values read directly from a single on-chain source "
        "without staleness/deviation checks, or usable within a single transaction "
        "(manipulable via flash loan / same-block trades)."
    ),
    "accounting": (
        "Share/balance/fee bookkeeping that can double-count, under/over-attribute, "
        "or diverge from actual token balances (e.g. mixing 'loose' and deposited assets)."
    ),
    "delegatecall": (
        "delegatecall to a target address that is mutable or attacker-influenced, or "
        "storage-layout mismatches between the calling and called contract."
    ),
}

_OUTPUT_CONTRACT = """\
Respond with a single fenced ```json code block containing exactly these fields:
{
  "suspicious": true|false,
  "vuln_class": "access_control"|"arithmetic_downcast"|"reentrancy"|"oracle_price"|"accounting"|"delegatecall"|"other"|null,
  "severity": "low"|"medium"|"high"|null,
  "rationale": "<concise technical explanation>",
  "lines": [<int>, ...]
}
Set "suspicious": false and null the other fields if you find nothing concerning.
Do not use vague language -- name the concrete mechanism and exact lines if suspicious.
The code below is shown with its ACTUAL file line numbers in the left margin
(e.g. " 42: someCode();") -- "lines" MUST use those exact numbers, not
line numbers counted from the start of the snippet.
"""


def _wrap(system: str, source: str, context: str | None) -> list[dict]:
    user = f"Function/context under review (left margin = absolute file line number):\n```solidity\n{source}\n```\n"
    if context:
        user += f"\nAdditional context:\n{context}\n"
    user += f"\n{_OUTPUT_CONTRACT}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def strategy_1_simple_description(source: str, context: str | None = None) -> list[dict]:
    system = (
        "You are annotating smart contract code. Give a concise, plain description of what this "
        "function does, then assess whether anything in it looks security-suspicious."
    )
    return _wrap(system, source, context)


def strategy_2_detailed_description(source: str, context: str | None = None) -> list[dict]:
    system = (
        "You are annotating smart contract code in detail. Describe variable usage, the function's "
        "signature/purpose, and every distinct action it performs (reads, writes, external calls, "
        "arithmetic, casts), then assess whether anything looks security-suspicious."
    )
    return _wrap(system, source, context)


def strategy_3_role_playing(source: str, context: str | None = None) -> list[dict]:
    system = (
        "You are a senior smart contract security auditor with years of experience finding exploitable "
        "bugs in production DeFi code. Review this function the way you would during a paid audit: "
        "note what it does, then flag anything an attacker could exploit."
    )
    return _wrap(system, source, context)


def strategy_4_cot(source: str, context: str | None = None) -> list[dict]:
    system = (
        "You are a smart contract security auditor. Think step by step: (1) what does this function do, "
        "(2) what invariants does it assume, (3) could any external actor break those invariants, "
        "(4) is there a concrete exploitable issue. Show this reasoning, then give your final assessment."
    )
    return _wrap(system, source, context)


def strategy_5_vulnerability_customized_cot(
    source: str, context: str | None = None, vuln_classes: list[str] | None = None
) -> list[dict]:
    classes = vuln_classes or VULN_CLASSES
    hints = "\n".join(f"- {c}: {CORE_RULES[c]}" for c in classes if c in CORE_RULES)
    system = (
        "You are a smart contract security auditor performing vulnerability-focused chain-of-thought "
        "review. For each of the following vulnerability classes, explicitly check whether this function "
        "exhibits it, citing the specific lines/variables involved:\n"
        f"{hints}\n"
        "Reason through each class briefly, then give your final assessment for the single most likely "
        "issue (if any)."
    )
    return _wrap(system, source, context)


def prompt_p1_authorization(source: str, context: str | None = None) -> list[dict]:
    system = (
        "You are a smart contract security auditor reviewing a function that a deterministic "
        "static-analysis router flagged as a state-changing, public/external function with no "
        "authorization control found (no protective modifier, no msg.sender check, in the function "
        "body, its applied modifiers, or bounded internal-helper calls). Confirm or refute this: "
        f"{CORE_RULES['access_control']}\n"
        "The router's flag is a coarse signal, not a verdict -- some functions are legitimately "
        "open to any caller (e.g. a user acting on their own funds/state). Assess whether THIS "
        "specific function's lack of an authorization check is actually exploitable, citing the "
        "concrete privileged operation and exact lines if so."
    )
    return _wrap(system, source, context)


def prompt_p2_reentrancy(source: str, context: str | None = None) -> list[dict]:
    system = (
        "You are a smart contract security auditor reviewing a function that a deterministic "
        "static-analysis router flagged for an external call followed by a state write on some "
        "control-flow path (call-before-write ordering). Confirm or refute this: "
        f"{CORE_RULES['reentrancy']}\n"
        "The additional context below lists the external call site, the state written "
        "before/after it, and other functions touching the same state -- use it to assess whether "
        "a reentrant callback could actually exploit the ordering, citing exact lines if so."
    )
    return _wrap(system, source, context)


def prompt_p5_arithmetic_precision(source: str, context: str | None = None) -> list[dict]:
    system = (
        "You are a smart contract security auditor reviewing a function that a deterministic "
        "static-analysis router flagged for a narrowing integer type conversion. Confirm or refute "
        f"this: {CORE_RULES['arithmetic_downcast']}\n"
        "The additional context below cites the exact cast site(s) found. Assess whether the "
        "narrowing is actually reachable with values large enough to truncate, citing exact lines "
        "if so."
    )
    return _wrap(system, source, context)


def prompt_unresolved_investigation(source: str, context: str | None = None) -> list[dict]:
    system = (
        "You are a smart contract security auditor reviewing a function that a deterministic "
        "static-analysis router could NOT fully resolve: one of its checks (e.g. authorization-"
        "control detection) hit source text it could not read (an unreadable applied modifier or "
        "internal helper), so the router cannot say whether the relevant control is present or "
        "absent for this function. This is a general, non-committal investigation request, not a "
        "specific vulnerability-class flag -- review the function (and its cited unreadable "
        "dependency, if included in the context below) for anything genuinely concerning across "
        "any vulnerability class, citing exact lines if so. Do not assume the missing information "
        "implies a vulnerability; assess only what you can actually see."
    )
    return _wrap(system, source, context)


STRATEGIES = {
    1: strategy_1_simple_description,
    2: strategy_2_detailed_description,
    3: strategy_3_role_playing,
    4: strategy_4_cot,
    5: strategy_5_vulnerability_customized_cot,
    # MGPR per-family specialist prompts (string keys, additive -- selected
    # via a4v/mgpr/router.py's Route.family -> FamilySpec.prompt_id, not by
    # config.yaml's fpsl.strategies_default). Reuses the existing CORE_RULES
    # hint text for the families that already have a current analog
    # (access_control/reentrancy/arithmetic_downcast).
    "P1_AUTHORIZATION_v1": prompt_p1_authorization,
    "P2_REENTRANCY_v1": prompt_p2_reentrancy,
    "P5_ARITHMETIC_PRECISION_v1": prompt_p5_arithmetic_precision,
    # Gap C, Workstream 2: the investigation-fallback prompt for decision-
    # blocking-unresolved units -- not tied to any single family, since a
    # unit's `families_blocked` may span more than one.
    "UNRESOLVED_INVESTIGATION_v1": prompt_unresolved_investigation,
}


def build_prompt(strategy: int | str, source: str, context: str | None = None) -> list[dict]:
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown FPSL strategy {strategy!r}; must be one of {sorted(STRATEGIES, key=str)}")
    return STRATEGIES[strategy](source, context)
