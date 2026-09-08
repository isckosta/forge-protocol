---
forge:
  artifact: discovery
  schema: 1
change: CHG-0055
status: complete
---

# Discovery — CHG-0055 QA Capability

## Executive Summary

The Capability Contract requires only the seven canonical sections and the
generic loader already loads any conforming definition by path. Existing
`investigate` and `fix` definitions establish the repository convention for
Harness-independent, prose-only competencies. Therefore QA can be added as a
new `capabilities/qa/` definition with a focused contract test; no registry,
loader, Protocol, Flow, or adapter change is necessary.

## Investigation

Evidence: `capabilities/capability.md`, `capabilities/investigate/CAPABILITY.md`,
`capabilities/fix/CAPABILITY.md`, `src/forge_cli/capabilities/loader.py`, and
the existing capability test modules.
