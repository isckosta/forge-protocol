---
forge:
  artifact: plan
  schema: 1
change: CHG-0058
status: approved
---

# Plan — CHG-0058 Review Capability

1. [RED] Add `tests/capabilities/test_review_capability.py` and confirm the
   expected missing-definition failure.
2. [GREEN] Add `capabilities/review/CAPABILITY.md` with the seven required
   sections, adversarial review behavior, evidence-bearing finding shape, and
   governance boundaries.
3. Run the focused capability tests, full suite, `forge validate`, and
   `git diff --check`; record documentation impact and verification.

## Human Plan Authorization

The user's explicit implementation request in the active chat on 2026-09-08
authorizes this localized Plan to proceed to Implementation. No unresolved
decision expands the declared boundary.

<!-- forge:plan-approval-confirmation -->
<!-- forge:plan-approval-record -->
**Approved.** The human maintainer explicitly requested implementation of the
review capability in the active chat on 2026-09-08.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.
