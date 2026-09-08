---
forge:
  artifact: plan
  schema: 1
change: CHG-0056
status: pending
---

# Plan — CHG-0056 Capability Exposure

1. Add deterministic packaged Capability catalog resolution and the Harness-independent exposure model.
2. Extend Adapter projection context and Codex/Claude skill renderers to derive native Capability skills and canonical references.
3. Align Codex publication evidence with the official `.agents/skills` repository skill root.
4. Add unit and integration coverage, update generated adapter artifacts and documentation, then run Forge validation, verification, and review.

## Implementation Boundary

The human maintainer explicitly confirmed “prossiga como está” after the
native skill layout decision in the active chat. This confirms the Plan
Decision for the declared scope; it does not authorize unrelated expansion.

## Approval Record

<!-- forge:plan-approval-confirmation -->
<!-- forge:plan-approval-record -->

- Decision: DEC-001
- Authority: human maintainer
- Confirmation: explicit chat confirmation to proceed with the selected
  direct-child skill layout (`.agents/skills/<capability>` and
  `.claude/skills/<capability>`)
- Observed by: operator
- Date: 2026-09-08
