"""MGPR: Metric-Gated Prompt Routing for the Commentator stage.

Deterministic, code-only router that decides, per routing unit (currently
only `function`), which vulnerability-family Commentator prompt applies and
what bounded context it gets -- replacing the fixed `fpsl.strategies_default`
config int and the fixed `BundleBuilder.expand(seed, hops=1)` context radius.
See /scratch/md5344/.claude/plans/effervescent-inventing-teapot.md for the
full design rationale; this package implements only the P1/P2/P5 slice.
"""
