# L7 Protocol Conformance Evidence Assessment — schema

Per the plan: this is a **protocol conformance evidence assessment scoped
to repository-visible artifacts**, never a certification claim and never
a full protocol/deployment assessment. Structurally out of scope on every
run: deployed proxy/implementation state, multisig configuration,
governance execution history, off-chain services, operational controls,
external dependency risk beyond what's vendored in-repo.

Per Q requirement, per audited repository, the assessment record is:

```json
{
  "req_id": "...",
  "audited_repo": "...",
  "evidence_expected": ["..."],
  "evidence_found": [
    {"source": "path/to/file", "excerpt": "...", "claim_summarized": "..."}
  ],
  "claims_vs_implementation": [
    {"claim": "...", "implementing_components": ["path:symbol", "..."],
     "consistent": true, "contradiction_note": null}
  ],
  "evidence_not_verifiable_from_repo": ["..."],
  "open_questions_for_owner_or_expert": ["..."],
  "conformance_state": "PASS | FAIL | INCONCLUSIVE | INSUFFICIENT_EVIDENCE",
  "reasoning_summary": "..."
}
```

**Schema justification (this schema is a framework design assumption --
EthTrust prescribes no conformance-claim format itself, logged per the
plan's requirement to justify every field against spec text):**

| Field | Justified by |
|---|---|
| `evidence_expected` | Directly derived from the requirement's own referenced Q requirements (its context bundle) -- e.g. req-3-implement-as-documented names req-3-documented and req-3-document-system explicitly. |
| `evidence_found` | Operationalizes "whether that evidence exists in the repository" -- a direct, minimal translation, not an invented criterion. |
| `claims_vs_implementation` | Operationalizes "Implement as Documented"'s own core obligation -- code MUST behave as documentation claims -- this is the literal comparison the requirement asks for. |
| `evidence_not_verifiable_from_repo` | Required by the Rev. 3 re-scoping of L7 to repository-visible evidence only -- this field is where the "we can't see this from the repo" honesty lives, rather than silently omitting it. |
| `open_questions_for_owner_or_expert` | Required by the plan's explicit instruction not to infer undocumented architecture and judge against the inference -- gaps get asked, not filled in. |
| `conformance_state` | The plan's own 4-state model (PASS/FAIL/INCONCLUSIVE/INSUFFICIENT_EVIDENCE), applied identically to L6/L8's LLM judgment schema for consistency across the framework. |

## Prototype status

No live repository was assessed against this schema in Track A -- doing
so requires the L8 shared LLM Judgment Layer (not yet built) plus a
target audit repo. What Track A produced instead, per requirement, is the
fully-specified **reviewer rubric**: exactly which evidence to look for
and where it comes from in the requirement's own text/context bundle --
see `req-3-implement-as-documented.json` in this directory. Running the
rubric against a real EVMbench audit entry is deferred to whenever L8
exists, consistent with how L4/L6 also stopped at "component specified,
not yet executed" rather than fabricating results.
