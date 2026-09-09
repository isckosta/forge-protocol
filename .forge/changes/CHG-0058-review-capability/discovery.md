---
forge:
  artifact: discovery
  schema: 1
change: CHG-0058
status: complete
---

# Discovery — CHG-0058 Review Capability

## Executive Summary

The existing Capability Contract requires only seven prose sections and the
loader discovers every `*/CAPABILITY.md` deterministically. The existing
`investigate`, `fix`, and `qa` definitions demonstrate that a new competency
can be added as one canonical file. The generic adapter projection receives
the loaded catalog and derives exposure identities; no adapter code branches
on individual Capability ids.

Implication: `review` can be added as a single canonical definition plus a
focused contract test. The review profile must be described as an already
effective input, never selected or resolved by the Capability.

## Investigation

Evidence inspected: `capabilities/capability.md`,
`capabilities/README.md`, the canonical `investigate`, `fix`, and `qa`
definitions, `src/forge_cli/capabilities/{loader,exposure}.py`, the generic
adapter driver, and both Codex and Claude Code projection paths. These show
that the requested boundary is supported without Foundation, Protocol, or
Harness-specific changes.

The pre-existing `forge doctor` result also reports a Codex installation
publication-root mismatch. That is an environment installation issue, not a
limitation of canonical Capability discovery, and is not changed here.
