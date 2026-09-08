---
forge:
  artifact: plan
  schema: 1
change: CHG-0055
status: approved
---

# Plan — CHG-0055 QA Capability

1. [RED] Add the contract-focused QA capability test and confirm the expected
   missing-definition failure.
2. [GREEN] Add `capabilities/qa/CAPABILITY.md` with the seven required sections,
   exploratory scenario coverage, finding shape, evidence expectations, and
   responsibility boundaries.
3. Run the focused test, full suite, `forge validate`, and `git diff --check`;
   record documentation impact and verification results.

## Human Plan Authorization

The user's explicit implementation request in the active chat on 2026-09-08
authorizes this localized Plan to proceed to Implementation. No unresolved
decision expands the declared boundary.

<!-- forge:plan-approval-confirmation -->
**Approved.** The human maintainer explicitly requested implementation of the
QA capability in the active chat on 2026-09-08. This is recorded as the plan
decision for CHG-0055.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.
