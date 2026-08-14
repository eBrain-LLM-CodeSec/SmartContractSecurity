"""RTF v2 Phase 3: protocol-context NARRATIVE extraction.

`rtf.l11_investigation_grouping.context_artifacts.generate_protocol_context_md`
already produces a real, Slither-derived `protocol_context.md` -- in-scope
contracts, inheritance, entry points, state variables, a naming-heuristic
trust-boundary section. See that module's own docstring. What it does NOT
cover (per `RTF_V2_ARCHITECTURE.md` section A.13/C.2): protocol purpose,
applicable standards + their concrete obligations, accounting-relevant
state, and lifecycle/initialization hints. This module adds exactly those
sections, as a SEPARATE, additive artifact -- `generate_protocol_context_md`
itself is left untouched (its existing callers/tests are unaffected).

Same discipline as `context_artifacts.py`: every claim is either grounded
in an identifiable, quoted source (a README paragraph, a NatSpec comment,
a standard's own clause text, a real inheritance/modifier fact) or the
section explicitly states "not available" -- never a free-form summary,
never an invented claim, never a vulnerability conclusion. No LLM is used
anywhere in this module (deliberately, this session -- see
RTF_V2_ARCHITECTURE.md section C.2): every section here is $0-cost and
byte-reproducible on identical input, which is what makes it safe to run
unconditionally on every audit, not just when budget allows.
"""
from __future__ import annotations

import re
from pathlib import Path

from rtf.standards.discovery import discover_applicable_standards
from rtf.standards.generator import generate_requirements_for_standard
from rtf.standards.models import DetectionConfidence, StandardDetectionResult
from rtf.standards.registry import StandardsRegistry

# Same NatSpec doc-comment shape `predicates.collect_documentary_and_
# implementation_evidence` already treats as "real NatSpec, not a stray
# one-line comment" -- reused verbatim rather than a second definition.
_NATSPEC_RE = re.compile(r"(?:^[ \t]*///[^\n]*\n?)+|/\*\*.*?\*/", re.MULTILINE | re.DOTALL)
_MIN_NATSPEC_SNIPPET_CHARS = 15
_MAX_NATSPEC_SNIPPET_CHARS = 500

_README_NAMES = ("README.md", "Readme.md", "readme.md", "README", "README.rst", "README.txt")
_MAX_README_EXCERPT_CHARS = 1200

# Naming-heuristic only (like `generate_protocol_context_md`'s own "Trust
# boundaries" section) -- flags a state variable as ACCOUNTING-RELEVANT by
# name, never as evidence of a bug. Kept a small, explicit, documented list
# rather than NLP: every name here is a common ERC-20/4626/fee-vault term,
# not tuned to any specific EVMbench target.
_ACCOUNTING_KEYWORDS = (
    "fee", "asset", "share", "balance", "supply", "debt", "collateral",
    "reward", "price", "rate", "reserve", "deposit", "withdraw",
)

# Same rationale: naming-heuristic lifecycle signals, not a verified claim.
_LIFECYCLE_BASE_CONTRACTS = ("Initializable", "Pausable")
_LIFECYCLE_MODIFIER_KEYWORDS = ("initializer", "onlyinitializing", "whennotpaused", "whenpaused")


def _find_readme(repo_root: Path) -> tuple[str, str] | None:
    for name in _README_NAMES:
        p = repo_root / name
        if p.exists() and p.is_file():
            return p.read_text(encoding="utf-8", errors="replace"), name
    return None


def _first_readme_paragraph(text: str) -> str | None:
    """First non-empty paragraph that isn't a bare Markdown heading/badge
    line -- a real descriptive sentence, not a title or a shields.io badge
    row. Returns None (never a guess) if no such paragraph exists in the
    first part of the file."""
    for para in text.split("\n\n"):
        stripped = para.strip()
        if not stripped:
            continue
        lines = [ln.strip() for ln in stripped.splitlines() if ln.strip()]
        if not lines:
            continue
        # Skip heading-only or badge-only paragraphs (all lines start with
        # '#' or '[![' -- Markdown heading / shields.io badge conventions).
        if all(ln.startswith("#") or ln.startswith("[![") or ln.startswith("![") for ln in lines):
            continue
        return stripped[:_MAX_README_EXCERPT_CHARS]
    return None


def _overview_paragraph(text: str) -> str | None:
    """Prefer the first prose paragraph under a Markdown Overview heading.

    Audit repositories frequently prepend contest metadata, prize tables,
    badges, or known-issue lists before the protocol's actual description.
    An explicit ``Overview`` section is stronger evidence of purpose than
    the first arbitrary non-heading paragraph.
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not re.match(r"^#{1,6}\s+(?:protocol\s+)?overview\s*$", line.strip(), re.IGNORECASE):
            continue
        tail = "\n".join(lines[index + 1:])
        return _first_readme_paragraph(tail)
    return None


def extract_protocol_purpose(repo_root: Path) -> tuple[str, str] | None:
    """Returns (verbatim_excerpt, citation) for the protocol's own
    self-description, or None if no README with a real descriptive
    paragraph exists. Never synthesizes a purpose statement -- if the repo
    doesn't say what it's for in its own words, this function says so
    (via the "not available" fallback in the caller), rather than
    guessing from contract/function names."""
    found = _find_readme(repo_root)
    if found is None:
        return None
    text, name = found
    para = _overview_paragraph(text) or _first_readme_paragraph(text)
    if para is None:
        return None
    return para, name


def extract_applicable_standards_obligations(
    repo_root: Path, entry_sol_file: Path, slither, registry: StandardsRegistry | None = None,
) -> list[dict]:
    """For every standard `discover_applicable_standards` confirms
    APPLICABLE (not merely UNCERTAIN), returns
    `{"standard_id", "contracts", "obligations": [{"clause_id", "section",
    "normative_strength", "obligation_text"}, ...]}` -- the CONCRETE,
    clause-level obligations (`rtf.standards.generator`'s own output),
    never the bare "implements ERC-4626" applicability fact alone (see
    Section 7's explicit instruction against that). Reuses
    `rtf.standards.discovery`/`generator` verbatim -- no new detection or
    translation logic here, only composition + citation.
    """
    registry = registry if registry is not None else StandardsRegistry()
    results = discover_applicable_standards(repo_root, entry_sol_file, slither, registry=registry)
    out: list[dict] = []
    for result in results:
        if result.applicable != DetectionConfidence.APPLICABLE:
            continue
        record = registry.load(result.standard_id)
        clauses = registry.load_clauses(result.standard_id)
        generated = generate_requirements_for_standard(record, clauses)
        out.append({
            "standard_id": result.standard_id,
            "contracts": list(result.contracts),
            "confidence": result.confidence,
            "detection_reason": result.reason,
            "obligations": [
                {
                    "clause_id": g.clause_id,
                    "section": g.source_section,
                    "normative_strength": g.normative_strength.value,
                    "obligation_text": g.obligation_text,
                }
                for g in generated
            ],
        })
    return out


def extract_accounting_state_variables(slither, repo_root: "Path | None" = None) -> list[tuple[str, str, str]]:
    """Returns (contract_name, state_var_name, matched_keyword) for every
    project state variable whose name suggests economic/accounting
    significance -- a naming heuristic (documented, same discipline as
    `generate_protocol_context_md`'s "Trust boundaries" section), not a
    verified accounting-correctness claim.

    `repo_root`, when given, excludes vendored contracts (see
    `context_artifacts._contract_is_vendored`) -- `None` (the default) is
    byte-identical to prior behavior. See
    RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md SS16.
    """
    from rtf.l11_investigation_grouping.context_artifacts import _contract_is_vendored

    out: list[tuple[str, str, str]] = []
    for contract in getattr(slither, "contracts_derived", []):
        if getattr(contract, "is_interface", False):
            continue
        if repo_root is not None and _contract_is_vendored(contract, repo_root):
            continue
        for v in getattr(contract, "state_variables_declared", []):
            lowered = v.name.lower()
            for kw in _ACCOUNTING_KEYWORDS:
                if kw in lowered:
                    out.append((contract.name, v.name, kw))
                    break
    return out


def extract_lifecycle_hints(slither, repo_root: "Path | None" = None) -> list[str]:
    """Returns human-readable, cited lifecycle/initialization signals:
    a contract inheriting a known lifecycle base contract, or declaring a
    function with a lifecycle-suggestive modifier name. Naming/inheritance
    heuristic only -- the investigating agent must still verify the actual
    guard logic, exactly like `generate_protocol_context_md`'s trust-
    boundary section already caveats for access control.

    `repo_root`, when given, excludes vendored contracts -- `None` (the
    default) is byte-identical to prior behavior. See
    RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md SS16.
    """
    from rtf.l11_investigation_grouping.context_artifacts import _contract_is_vendored

    hints: list[str] = []
    for contract in getattr(slither, "contracts_derived", []):
        if getattr(contract, "is_interface", False):
            continue
        if repo_root is not None and _contract_is_vendored(contract, repo_root):
            continue
        base_names = {b.name for b in getattr(contract, "inheritance", [])}
        matched_bases = base_names & set(_LIFECYCLE_BASE_CONTRACTS)
        if matched_bases:
            hints.append(f"**{contract.name}** inherits {', '.join(sorted(matched_bases))}")
        for f in getattr(contract, "functions_declared", []):
            mod_names = {m.name.lower() for m in getattr(f, "modifiers", [])}
            matched_mods = mod_names & set(_LIFECYCLE_MODIFIER_KEYWORDS)
            if matched_mods:
                hints.append(f"**{contract.name}.{f.name}** uses modifier(s) {', '.join(sorted(matched_mods))}")
    return hints


def generate_protocol_context_narrative_md(
    repo_root: Path, entry_sol_file: Path, slither, registry: StandardsRegistry | None = None,
) -> str:
    """The new sections this phase adds. Composed with the existing
    `generate_protocol_context_md` output by `generate_enriched_protocol_
    context_md` below -- kept as its own pure function (same "separate
    generation from I/O" convention as `context_artifacts.py`) so it can
    be tested and reused independently.
    """
    lines = ["## Protocol purpose (from the project's own documentation)\n"]
    purpose = extract_protocol_purpose(repo_root)
    if purpose is not None:
        excerpt, citation = purpose
        lines.append(f"> {excerpt}\n")
        lines.append(f"(verbatim excerpt from `{citation}`)\n")
    else:
        lines.append("(not available -- no README with a descriptive paragraph found)\n")

    lines.append("## Applicable external standards and their concrete obligations\n")
    obligations = extract_applicable_standards_obligations(repo_root, entry_sol_file, slither, registry=registry)
    if obligations:
        for entry in obligations:
            lines.append(
                f"### {entry['standard_id']} (confidence {entry['confidence']:.2f}) -- "
                f"contracts: {', '.join(entry['contracts']) or '(none confirmed)'}\n"
            )
            lines.append(f"Detected because: {entry['detection_reason']}\n")
            if entry["obligations"]:
                lines.append("Concrete obligations derived from this standard's own clauses "
                              "(not the bare fact of implementing it):\n")
                for ob in entry["obligations"]:
                    lines.append(
                        f"- [{ob['normative_strength']}] (`{ob['clause_id']}`, {ob['section']}): "
                        f"{ob['obligation_text']}"
                    )
            lines.append("")
    else:
        lines.append("(no external standard confirmed applicable with strong evidence)\n")

    lines.append("## Accounting-relevant state variables (naming heuristic -- not a correctness claim)\n")
    accounting_vars = extract_accounting_state_variables(slither, repo_root=repo_root)
    if accounting_vars:
        for contract_name, var_name, kw in sorted(accounting_vars):
            lines.append(f"- **{contract_name}.{var_name}** (name suggests: {kw})")
        lines.append("")
    else:
        lines.append("(no state variable names suggest accounting/economic significance)\n")

    lines.append("## Lifecycle / initialization signals (naming heuristic -- verify guard logic independently)\n")
    lifecycle_hints = extract_lifecycle_hints(slither, repo_root=repo_root)
    if lifecycle_hints:
        for hint in lifecycle_hints:
            lines.append(f"- {hint}")
        lines.append("")
    else:
        lines.append("(no lifecycle/initialization signals found)\n")

    return "\n".join(lines) + "\n"


def generate_enriched_protocol_context_md(
    audit_id: str, repo_root: Path, entry_sol_file: Path, slither, scope_files: list[str],
    registry: StandardsRegistry | None = None,
) -> str:
    """The full RTF v2 `protocol_context.md`: the existing, unchanged
    structural facts (`generate_protocol_context_md`) followed by this
    phase's narrative sections. A strict textual superset of the pre-v2
    artifact -- nothing existing is removed or altered, so any caller
    still reading the old sections keeps working."""
    from rtf.l11_investigation_grouping.context_artifacts import generate_protocol_context_md

    base = generate_protocol_context_md(audit_id, slither, scope_files, repo_root=repo_root)
    narrative = generate_protocol_context_narrative_md(repo_root, entry_sol_file, slither, registry=registry)
    return base + "\n" + narrative
