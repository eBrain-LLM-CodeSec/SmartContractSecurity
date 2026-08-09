# Phase 5 step 1: Liquid-Ron zero-cost sanity check

Per the implementation plan's §19 ("First run Liquid-Ron as a sanity
check... Record exactly which standard detection evidence caused ERC-4626
to become applicable"). **Zero cost**: no live Codex/L8 calls anywhere in
this check -- `rtf.standards.discovery.discover_applicable_standards` and
`rtf.standards.routing.build_standards_routed_requirements` run directly
against a real compiled Slither object, nothing more.

**Target**: `2025-01-liquid-ron`'s `src/LiquidRon.sol`, compiled from a real
checkout at `/scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-01-liquid-ron`
(a full Foundry project with `lib/openzeppelin-contracts` vendored,
`solc 0.8.20`).

## Standard detection (real evidence, not asserted)

**ERC-4626: APPLICABLE, confidence 0.95.** Contract `LiquidRon` identified
via 3 independent strong signals:
- `erc4626-inherits-ierc4626`: `LiquidRon` inherits `IERC4626`
- `erc4626-inherits-erc4626-base`: `LiquidRon` inherits `ERC4626` (source:
  `contract LiquidRon is ERC4626, RonHelper, Pausable, ValidatorTracker`,
  `src/LiquidRon.sol` line 29 -- OpenZeppelin's vendored base, imported via
  `import "@openzeppelin/token/ERC20/extensions/ERC4626.sol";`)
- `erc4626-documentation-claim`: `README.md` mentions both `ERC-4626` and
  `ERC4626`

Plus supporting signals: 16/16 canonical ERC-4626 function names present,
both `Deposit`/`Withdraw` events declared.

**ERC-20: ALSO independently APPLICABLE, confidence 0.95** (a vault is
inherently a token too -- `LiquidRon` inherits both `IERC20` and OZ's
`ERC20` base, imports `IERC20` across 4 files, README mentions `ERC20`,
6/6 canonical signatures, both `Transfer`/`Approval` events). Confirms the
multi-standard mechanism generalizes to a real target, not just synthetic
fixtures.

**No LiquidRon-specific code anywhere caused this.** `discovery.py`
contains zero `if audit_id == ...` branches or ERC-4626-specific logic --
every signal above is a data-driven check against `standard.json`'s own
registered `detection_signals`, the same code that ran against the
synthetic fixtures in Phase 2.

## Requirement generation + routing

```json
{
  "standards_considered": 2,
  "standards_discovered_applicable": 2,
  "clauses_loaded": 91,
  "requirements_generated": 91,
  "requirements_applicable": 91,
  "requirements_not_applicable": 0,
  "requirements_routed_agent": 91,
  "unsupported": 0,
  "silently_missing": 0,
  "valid": true
}
```

All 91 requirements (77 ERC-4626 + 14 ERC-20) generated, all 91 applicable
to this specific contract, all 91 routed to agent investigation, zero
silently missing -- the §12 invariant holds on a real target, not just
synthetic fixtures.

## The H-01-relevant requirement, specifically

`gp-accepted-standard__erc-4626__erc4626-totalassets-must-include-fees`:

- **applicability_state: APPLICABLE**, evidence location `LiquidRon`,
  conformance_state `None` (pending agent investigation -- correctly
  un-prejudged).
- Obligation text (independently derived from the pinned EIP-4626 spec,
  see `rtf/standards/erc/ERC-4626/clauses.json`): *"totalAssets() MUST be
  inclusive of any fees that are charged against assets in the Vault --
  amounts owed to a third party (e.g. an accrued operator/management fee)
  that are still held in the Vault's asset balance are still part of
  totalAssets() until actually paid out."*
- Bundle's `parent_section_context` records the full real detector reason
  and evidence list (reproduced above) -- an agent receiving this
  requirement would see exactly why ERC-4626 was determined applicable,
  not an asserted claim.

## Honest scoping of what this proves

This confirms the **opportunity** exists: an independently-generated,
on-topic, correctly-routed requirement about `totalAssets()`'s
fee-accounting behavior reaches the point of being handed to a real Codex
investigation. It does **not** by itself prove a real agent would
correctly diagnose H-01's specific mechanism (the distinction between a
fee "charged against assets" in the generic EIP-4626 sense and
`operatorFeeAmount` specifically being a third-party claim rather than a
vault-level dilution fee -- a distinction EIP-4626's own spec text does not
explicitly draw either). That is exactly the kind of semantic reasoning
question routed to the agent, not resolved deterministically -- and
verifying it empirically requires a real (paid) Codex investigation, which
remains gated behind the plan's hard acceptance checks (§23) and explicit
user authorization, not attempted here.

Per §21's classification rubric, this is the correct zero-cost-answerable
question: **"Did an independently justified RTF requirement exist? Was it
generated? Was it applicable? Did it actually fire? Would the Codex agent
have received it?"** -- all confirmed **yes**, with real evidence above.
Whether the investigation itself would succeed is deliberately out of
scope for this preflight.

**Routing trace frozen before this comparison was written down** -- no
code in `rtf/standards/` was modified after running this check against the
real target.
