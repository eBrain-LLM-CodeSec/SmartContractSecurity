"""Custom security-investigation agent kernel.

See SECURITY_AGENT_KERNEL_DESIGN.md (one directory up) for the full
architecture trace and design rationale. This package is a drop-in
alternative investigator for RTF v2's existing cluster pipeline
(rtf.l11_investigation_grouping) -- it does not modify grouping, context
assembly, or predicate/generation code.
"""
