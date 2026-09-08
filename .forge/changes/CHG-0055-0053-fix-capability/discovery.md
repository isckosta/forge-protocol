---
forge:
  artifact: discovery
  schema: 1
change: CHG-0055
status: complete
---

# Discovery — CHG-0055 0053 Fix Capability

## Executive Summary

The Capability Architecture is intentionally a canonical prose contract;
`investigate` already demonstrates that a concrete competency needs only a
new directory and focused contract tests. The existing loader is generic and
must remain untouched. The requested `/fix` behavior belongs in a second
definition, not in Flow or a new execution mechanism.

## Investigation

Evidence inspected:

- `capabilities/capability.md` requires exactly seven non-empty sections and
  does not define lifecycle, execution, or authority fields.
- `capabilities/investigate/CAPABILITY.md` separates diagnostic evidence and
  explicitly permits escalation when root cause is not established.
- `.forge/policies/testing.yml` requires a regression test for a reasonably
  automatable bugfix, with RED before production behavior.
- Existing capability tests load real definitions through the unchanged
  `forge_cli.capabilities.loader`.

Implication: the smallest compliant implementation is one canonical
`fix` definition, one focused test module, and Forge documentation/change
evidence. No adapter projection or new mandatory artifact is justified.
