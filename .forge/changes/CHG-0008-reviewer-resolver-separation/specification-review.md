# Adversarial Specification Review — CHG-0008

Status: complete

The pre-implementation review challenged two edge cases. First, requiring reviewer identity while Strict Review is still pending would force fabricated evidence; the requirement is therefore bound to actual active review execution while preserving the invariant that passed FULL Review cannot exist without identity. Second, applying the new required field retroactively would invalidate completed `forge/change@1` history and conflict with the explicit non-goal; completed historical records are preserved and the compatibility boundary is surfaced for independent Strict Review.

No requirement was weakened to permit FULL same-session Review. `agent_same_session` remains prohibited for FULL both by policy and semantic CLI validation.
