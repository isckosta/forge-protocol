---
forge:
  artifact: plan
  schema: 1
change: CHG-0054
status: approved
---

# Plan — CHG-0054 Forge Skill Activation Contract

1. Update the projection activation description and regenerate both
   Forge-owned Harness outputs through the Adapter update path.
2. Add cross-Harness activation/discovery tests for positive, negative, and
   ambiguous routing signals.
3. Run targeted tests, full verification, Adapter doctor, and merge-check.

## Implementation Boundary

The user's explicit request authorizes this bounded implementation. Review and
merge remain subject to the independent Forge gates.
