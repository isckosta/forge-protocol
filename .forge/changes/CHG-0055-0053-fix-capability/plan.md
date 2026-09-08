---
forge:
  artifact: plan
  schema: 1
change: CHG-0055
status: approved
---

# Plan — CHG-0055 Fix Capability

1. **[RED]** Add `tests/capabilities/test_fix_capability.py` covering the
   existing loader, accepted inputs, sufficient-understanding gate, minimal
   repair boundary, scope expansion, verification evidence, and governance
   exclusions. Confirm the expected missing-definition failure.
2. **[GREEN]** Add `capabilities/fix/CAPABILITY.md` with the seven required
   sections. Keep the definition canonical and prose-only; it must state
   when to escalate to investigation, how to preserve the repair boundary,
   how to seek the smallest cause-correcting change, and what reproducible
   evidence is required.
3. Run the focused capability tests and full test suite, then run
   `forge validate`. Evaluate documentation impact and record the result.

## Human Plan Authorization

The user's explicit implementation request on 2026-09-08 authorizes this
localized Plan to proceed to Implementation; no unresolved decision expands
the declared boundary.

<!-- forge:plan-approval-confirmation -->
## Plan Approval Confirmation

<!-- forge:plan-approval-record -->
**Approved.** The human maintainer explicitly instructed continuation in the
active chat session on 2026-09-08 with “Prossiga”, after the implementation
and verification state was reported. This confirmation authorizes the
localized Plan to proceed under C-077 and is recorded as `DEC-001` in
`manifest.yml` and `plan-approval-001` in `provenance.yml`.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.
