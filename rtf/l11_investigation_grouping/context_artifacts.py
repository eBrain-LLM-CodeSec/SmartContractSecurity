"""Phase 7 of the grouped-investigation architecture: reusable Markdown
context artifacts.

Three kinds, per the plan:

A. **Protocol context** (one per audit, reused across every cluster) --
   repo-wide FACTS (in-scope contracts, inheritance, interfaces,
   external entry points, state, constants), never vulnerability
   conclusions. Built from real Slither data (`generate_protocol_
   context_md`), never from EVMbench.
B. **Requirement context** (one per requirement, reused across every
   cluster derived from it) -- the requirement's own EthTrust text,
   provenance, and general investigation obligations.
   `generate_requirement_context_md`.
C. **Cluster investigation plan** (one per cluster) -- objective, why
   these properties were grouped, which files/components are involved,
   per-property detail, a fixed investigation procedure, and the
   required output schema. **Never contains an expected verdict** --
   the planner provides context and obligations; the investigator
   independently decides correctness (enforced structurally here: no
   code path in this module ever reads or writes anything resembling a
   PASS/FAIL conclusion). `generate_cluster_plan_md`.

All three generators are pure string-building functions (no filesystem
I/O) for testability; `write_context_artifacts` is the thin wrapper that
actually writes files, kept separate per this project's established
"separate I/O from generation" convention. Output is deterministic
(sorted lists, stable section ordering) so repeated generation from
identical inputs is byte-identical -- required for Phase 12's
prompt-prefix caching to have any chance of working, and already true
as of this phase, not deferred.
"""
from __future__ import annotations

from pathlib import Path

from rtf.l11_investigation_grouping.grouping_engine import Cluster
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.standards.discovery import _is_vendored_path


def _contract_is_vendored(contract, repo_root: Path) -> bool:
    """True if `contract`'s own source file resolves to a path under a
    vendored directory relative to `repo_root`. Same helper shape as
    `semantic_property_generation._contract_is_vendored` (which filters
    the GENERATOR-facing `ProjectManifest`) -- both delegate to the one
    canonical rule, `rtf.standards.discovery._is_vendored_path`, rather
    than each defining their own. This copy exists (instead of importing
    the other module's private helper) because `semantic_property_
    generation.py` is a higher layer that itself depends on things this
    module doesn't need -- see RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md
    SS16. Best-effort: a contract with no resolvable source file is never
    treated as vendored.
    """
    source_mapping = getattr(contract, "source_mapping", None)
    if source_mapping is None or getattr(source_mapping, "filename", None) is None:
        return False
    raw = getattr(source_mapping.filename, "absolute", None) or getattr(source_mapping.filename, "used", None)
    if not raw:
        return False
    return _is_vendored_path(Path(raw), repo_root)


def generate_protocol_context_md(
    audit_id: str, slither, scope_files: list[str], repo_root: "Path | None" = None,
) -> str:
    """Repo-wide, vulnerability-conclusion-free FACTS about the audited
    protocol, from a compiled Slither object. `scope_files` is the
    audit's own discovered/declared in-scope file list (see
    `scope_discovery.py`) -- used to distinguish in-scope contracts from
    incidentally-compiled dependencies.

    `repo_root`, when given, excludes vendored contracts (`lib/`,
    `node_modules/`, `vendor/`, `dependencies/`, `.deps/` -- see
    `_contract_is_vendored`) from every section below. `None` (the
    default) is byte-identical to prior behavior -- needed for existing
    callers with no `repo_root` concept and for synthetic single-file
    test fixtures. Load-bearing once compilation covers a whole project
    (`compile_helper.compile_evmbench_target_via_foundry`): this is the
    INVESTIGATOR-facing document (distinct from the generator-facing
    `ProjectManifest`, which already gets equivalent filtering) -- an
    unfiltered version would otherwise flood every cluster investigation
    with every vendored OpenZeppelin/Solady contract's own entry points
    and state variables, unconditionally, on every real audit that has a
    populated `lib/`. See RTF_V2_WHOLE_PROJECT_COMPILATION_PLAN.md SS16.

    Every section is either populated with real data or explicitly
    states "not available" -- never silently omitted or guessed.
    """
    lines = [f"# Protocol context: {audit_id}\n"]
    lines.append(
        "This document states FACTS about the repository's structure --"
        " never vulnerability conclusions. Generated once per audit,"
        " reused unchanged across every cluster investigation for it.\n"
    )

    scope_set = set(scope_files)
    lines.append("## In-scope contracts\n")
    if scope_files:
        for f in sorted(scope_files):
            lines.append(f"- `{f}`")
    else:
        lines.append("(scope file list not available for this generation)")
    lines.append("")

    contracts = sorted(
        [c for c in getattr(slither, "contracts", [])
         if repo_root is None or not _contract_is_vendored(c, repo_root)],
        key=lambda c: c.name,
    )
    lines.append("## Contracts and inheritance\n")
    if contracts:
        for c in contracts:
            kind = "interface" if c.is_interface else ("abstract contract" if getattr(c, "is_abstract", False) else "contract")
            inheritance = ", ".join(p.name for p in (c.inheritance or [])) or "(none)"
            lines.append(f"- **{c.name}** ({kind}) -- inherits from: {inheritance}")
    else:
        lines.append("(no compiled contracts available)")
    lines.append("")

    lines.append("## Externally callable entry points\n")
    any_entry_points = False
    for c in contracts:
        if c.is_interface:
            continue
        externals = sorted(
            f.name for f in getattr(c, "functions_declared", [])
            if getattr(f, "visibility", None) in ("public", "external") and not f.is_constructor
        )
        if externals:
            any_entry_points = True
            lines.append(f"- **{c.name}**: {', '.join(externals)}")
    if not any_entry_points:
        lines.append("(no public/external entry points found)")
    lines.append("")

    lines.append("## Critical state variables\n")
    any_state = False
    for c in contracts:
        state_vars = sorted(
            f"{v.name}{' (constant)' if getattr(v, 'is_constant', False) else ''}"
            f"{' (immutable)' if getattr(v, 'is_immutable', False) else ''}"
            for v in getattr(c, "state_variables_declared", [])
        )
        if state_vars:
            any_state = True
            lines.append(f"- **{c.name}**: {', '.join(state_vars)}")
    if not any_state:
        lines.append("(no state variables found)")
    lines.append("")

    lines.append("## Trust boundaries (not independently verified -- naming heuristic only)\n")
    lines.append(
        "The following functions are gated by an access-control modifier"
        " whose NAME suggests a privileged caller (e.g. `onlyOwner`) --"
        " this is a naming-convention observation, not a verified"
        " access-control guarantee; the investigating agent must still"
        " verify the actual guard logic itself.\n"
    )
    any_privileged = False
    for c in contracts:
        if c.is_interface:
            continue
        privileged = sorted(
            f.name for f in getattr(c, "functions_declared", [])
            if any(mod.name.lower().startswith(("only", "require")) or "admin" in mod.name.lower() or "owner" in mod.name.lower()
                   for mod in getattr(f, "modifiers", []))
        )
        if privileged:
            any_privileged = True
            lines.append(f"- **{c.name}**: {', '.join(privileged)}")
    if not any_privileged:
        lines.append("(no privilege-suggestive modifier names found)")
    lines.append("")

    return "\n".join(lines) + "\n"


def generate_requirement_context_md(requirement_record: dict, explanatory_text: str | None = None) -> str:
    """One requirement's own reusable context -- its exact EthTrust text,
    provenance, and the general investigation obligations every cluster
    derived from it should carry. `explanatory_text`, when given, is the
    raw spec prose surrounding the normative sentence (see
    RTF_ETHTRUST_TRANSLATION_AUDIT.md's Phase 1 finding that this is
    currently dropped before reaching the agent) -- included here so
    this artifact is a strict improvement over the prompt text
    `codex_bridge.build_codex_prompt_inputs` currently sends, not a
    lateral move.

    Also renders `exceptions_referenced`/`overriding_requirements`/
    `referenced_requirements` straight from `requirement_record` when
    present (RTF_V3_REDESIGN_PLAN.md finding 1: `l1_corpus/parse_spec.py`
    already extracts all three, but this function previously never read
    them, so an applicable EthTrust exception/override was silently
    invisible to the investigator). Every value rendered here comes
    verbatim from the parsed spec record -- nothing is invented or
    paraphrased by RTF; the "Provenance" section immediately below marks
    the boundary between official EthTrust text and RTF's own added
    framing (the "General investigation obligations" section).
    """
    req_id = requirement_record.get("req_id", "<unknown>")
    level = requirement_record.get("level", "?")
    title = requirement_record.get("requirement_semantic_intent") or requirement_record.get("title", req_id)
    normative_text = requirement_record.get("normative_text", "")
    section = requirement_record.get("section") or {}
    secno = section.get("secno", "?")
    # `exceptions_referenced`/`overriding_requirements` are structured
    # spec cross-references (req_id/relation/link_text/condition_text),
    # not prose -- and the parser deliberately puts a
    # "this_requirement_is_excepted_by" record in BOTH lists (it's both
    # an exception and, from this requirement's side, something that can
    # override it). Merge + dedupe by (req_id, relation) so the rendered
    # text says each real cross-reference once, phrased by its relation.
    _cross_refs: dict[tuple[str, str], dict] = {}
    for item in (requirement_record.get("exceptions_referenced") or []) + (
        requirement_record.get("overriding_requirements") or []
    ):
        key = (item.get("req_id", ""), item.get("relation", ""))
        _cross_refs[key] = item
    referenced = requirement_record.get("referenced_requirements") or []

    lines = [f"# Requirement context: {req_id}\n"]
    lines.append(f"**[{level}] {title}** (EthTrust spec section {secno})\n")
    lines.append("## Normative text (verbatim from the spec)\n")
    lines.append(f"> {normative_text}\n")
    if explanatory_text:
        lines.append("## Explanatory text (verbatim from the spec, surrounding context)\n")
        lines.append(f"> {explanatory_text}\n")
    if _cross_refs:
        lines.append(
            "## Exceptions / overriding requirements (from the spec's own"
            " cross-references -- check whether these apply BEFORE"
            " concluding a violation of the normative text above; a real"
            " EthTrust exception/override can change what conformance"
            " requires here)\n"
        )
        for (ref_req_id, relation), item in sorted(_cross_refs.items()):
            link_text = item.get("link_text", "")
            condition = item.get("condition_text")
            if relation == "this_requirement_is_excepted_by":
                phrase = f"This requirement is EXCEPTED BY `{ref_req_id}` ({link_text})"
            elif relation == "this_requirement_overrides":
                phrase = f"This requirement OVERRIDES `{ref_req_id}` ({link_text})"
            else:
                phrase = f"Related ({relation}): `{ref_req_id}` ({link_text})"
            if condition:
                phrase += f" -- condition: {condition}"
            lines.append(f"- {phrase}\n")
    if referenced:
        lines.append(
            "## Related EthTrust requirements referenced by this one"
            " (context only -- not themselves being investigated here)\n"
        )
        for item in referenced:
            lines.append(f"- `{item.get('req_id', '')}` ({item.get('link_text', '')})\n")
    lines.append("## Provenance\n")
    lines.append(f"- `req_id`: `{req_id}`")
    lines.append(f"- Security Level: `{level}`")
    lines.append(f"- Spec section: `{secno}`\n")
    lines.append("## General investigation obligations\n")
    lines.append(
        "- Determine what a VIOLATION of this specific requirement would"
        " concretely look like in the code you're given.\n"
        "- Actively search for that violation before concluding the"
        " requirement is satisfied -- do not rely on absence-of-notice.\n"
        "- A PASS verdict requires a genuine counterexample search"
        " (`counterexample_search` in the output schema), not just a"
        " clean read-through.\n"
        "- This context file is reused, unchanged, across every cluster"
        " investigating a property derived from this requirement -- it"
        " does not itself name any specific target contract, function,"
        " or expected outcome; those are the cluster plan's job.\n"
    )
    return "\n".join(lines) + "\n"


def generate_cluster_plan_md(
    cluster: Cluster,
    properties_by_id: dict[str, PropertyMetadata],
    protocol_context_path: str,
    requirement_context_paths: dict[str, str],
) -> str:
    """The per-cluster investigation plan. Structurally guarantees no
    expected-verdict leakage: this function never reads or writes
    anything resembling PASS/FAIL/a vulnerability conclusion -- its only
    inputs are `Cluster`/`PropertyMetadata` (which never carry a verdict
    field at all) and file-path strings.
    """
    members = [properties_by_id[pid] for pid in cluster.property_ids]

    lines = [f"# Cluster investigation plan: {cluster.cluster_id}\n"]

    lines.append("## Objective\n")
    categories = sorted({m.reasoning_category.value for m in members if m.reasoning_category})
    if categories:
        lines.append(
            f"Investigate {len(members)} distinct EthTrust-derived propert"
            f"{'y' if len(members) == 1 else 'ies'} concerning: {', '.join(categories)}.\n"
        )
    else:
        lines.append(f"Investigate {len(members)} distinct EthTrust-derived properties.\n")

    lines.append("## Why these properties are grouped\n")
    if cluster.grouping_reason:
        lines.append("Shared characteristics: " + ", ".join(cluster.grouping_reason) + "\n")
    else:
        lines.append("(single-property cluster -- no grouping rationale applies)\n")

    lines.append("## Files / components involved\n")
    files = cluster.shared_context.get("files") or []
    contracts = cluster.shared_context.get("contracts") or []
    if files:
        lines.append("Files: " + ", ".join(f"`{f}`" for f in files))
    if contracts:
        lines.append("Contracts: " + ", ".join(f"`{c}`" for c in contracts))
    if not files and not contracts:
        lines.append("(no specific files/contracts identified ahead of time -- discover them as part of the investigation)")
    lines.append("")

    lines.append("## Properties\n")
    for m in sorted(members, key=lambda p: p.property_id):
        lines.append(f"### `{m.property_id}`")
        lines.append(f"- Target: `{m.target_contract or '?'}.{m.target_function or '?'}`")
        lines.append(f"- Derived property (what to check): {m.property_text}")
        lines.append(f"- EthTrust basis: {m.source_provenance}")
        if m.candidate_locations:
            lines.append(f"- Candidate locations: {', '.join(m.candidate_locations)}")
        deps = [d for d in (m.relevant_state_variables + m.relevant_symbols) if d]
        if deps:
            lines.append(f"- Relevant dependencies: {', '.join(sorted(set(deps)))}")
        req_ctx_path = requirement_context_paths.get(m.requirement_id)
        if req_ctx_path:
            lines.append(f"- Requirement context: `{req_ctx_path}`")
        for note in m.related_out_of_scope_context:
            lines.append(f"- {note}")
        lines.append("")

    lines.append("## Investigation procedure\n")
    lines.append(f"""1. Read the protocol context: `{protocol_context_path}`.
2. Read each property's referenced requirement context file (listed above).
3. Inspect all listed candidate locations.
4. Follow relevant dependencies/calls where required.
5. Determine the intended invariant/semantics for each property independently.
6. Attempt to construct a counterexample for EACH property.
7. Verify the counterexample attempt against the actual implementation.
8. Return an independent verdict for EVERY property listed above.
""")

    lines.append("## Required output schema\n")
    lines.append("Every property listed above MUST return exactly one object:\n")
    lines.append("""```json
{
  "property_id": "...",
  "verdict": "PASS | FAIL | INCONCLUSIVE | INSUFFICIENT_EVIDENCE",
  "evidence": "...",
  "files_read": ["..."],
  "counterexample_attempt": "...",
  "counterexample_result": "...",
  "reasoning": "...",
  "vulnerable_location": "... (if applicable, else null)",
  "confidence": "HIGH | MEDIUM | LOW"
}
```
""")
    lines.append(
        "A PASS for one property is NOT evidence for another. Every"
        " property requires its own explicit counterexample search"
        " before PASS. Every property_id listed above must appear"
        " exactly once in the response -- no omissions, no duplicates,"
        " no cluster-wide verdict.\n"
    )

    lines.append("## What would constitute a violation\n")
    lines.append(
        "For each property above, a violation is a concrete, reproducible case where the"
        " property's stated invariant does NOT hold in the actual implementation -- a"
        " specific input, call sequence, or state transition under which the derived"
        " property (\"what to check\", listed per-property above) fails. A violation is"
        " NOT: a stylistic concern, a theoretical edge case with no reachable trigger, or"
        " a disagreement with the requirement's own wording (if the requirement itself"
        " seems wrong, say so in `reasoning` -- do not silently substitute a different"
        " check). Every property is independent: violating one does not imply anything"
        " about the others in this cluster.\n"
    )

    lines.append("## Evidence required before reporting a finding\n")
    lines.append(
        "A verdict of the schema's first FAIL value requires: (1) the specific code"
        " location where the violation occurs, (2) a concrete counterexample"
        " (`counterexample_attempt`) showing the property's invariant breaking, and (3)"
        " `counterexample_result` explaining why that counterexample succeeds against the"
        " real implementation, not a hypothetical. The schema's first PASS value requires"
        " an explicit, genuine attempt to construct a counterexample first"
        " (`counterexample_attempt`/`counterexample_result` showing why it did NOT"
        " succeed) -- absence of an immediately obvious violation is not sufficient"
        " evidence of correctness. When the evidence needed to decide either way isn't"
        " available from the given context/code, use one of the schema's other two"
        " values rather than guessing.\n"
    )

    return "\n".join(lines) + "\n"


def write_context_artifacts(
    root: Path,
    audit_id: str,
    protocol_context_md: str,
    requirement_context_by_id: dict[str, str],
    cluster_plans_by_id: dict[str, str],
) -> dict[str, str]:
    """Writes the three artifact kinds under `root` (`.rtf/context/`,
    `.rtf/context/requirements/`, `.rtf/plans/`), returning a dict of
    {logical_name: relative_path_written} for callers (Phase 8's prompt
    builder) to reference. Content is written EXACTLY as given -- this
    function does no generation itself, only I/O, per the module's
    stated separation.
    """
    context_dir = root / ".rtf" / "context"
    requirements_dir = context_dir / "requirements"
    plans_dir = root / ".rtf" / "plans"
    context_dir.mkdir(parents=True, exist_ok=True)
    requirements_dir.mkdir(parents=True, exist_ok=True)
    plans_dir.mkdir(parents=True, exist_ok=True)

    written: dict[str, str] = {}

    protocol_path = context_dir / "protocol_context.md"
    protocol_path.write_text(protocol_context_md, encoding="utf-8")
    written["protocol_context"] = str(protocol_path.relative_to(root))

    for req_id, content in requirement_context_by_id.items():
        path = requirements_dir / f"{req_id}.md"
        path.write_text(content, encoding="utf-8")
        written[f"requirement:{req_id}"] = str(path.relative_to(root))

    for cluster_id, content in cluster_plans_by_id.items():
        path = plans_dir / f"{cluster_id}.md"
        path.write_text(content, encoding="utf-8")
        written[f"plan:{cluster_id}"] = str(path.relative_to(root))

    return written
