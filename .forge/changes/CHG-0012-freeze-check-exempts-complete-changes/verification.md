---
forge:
  artifact: verification
  schema: 1
change: CHG-0012
status: complete
---
# Verification — CHG-0012

## TDD

### Resolution 1 (initial attempt)
RED: `test_complete_change_is_exempt_from_post_completion_freeze_drift`
written and run against the unmodified validator; failed with exactly the
CI's own finding message, reproducing the causal bug rather than an
environment failure. `test_active_change_still_detects_freeze_drift`
(regression guard) was already green before the fix.

GREEN: unconditional `state.current == "complete"` exemption. Both tests
passed — but independent Strict Review Iteration 1 found this GREEN state
concealed a BLOCKER (CHG-0012-R001): the exemption also silently disabled
detection of the Change's own reviewed files being tampered with, not only
unrelated activity. Neither shipped test exercised that scenario.

### Resolution 2 (post-Review correction)
RED: `test_tampering_between_freeze_and_completion_is_still_detected`,
built directly from the Reviewer's own reproduction, written and run
against Resolution 1's code; failed (no finding produced) — reproducing
CHG-0012-R001 as a causal RED, not merely trusting the Reviewer's prose.

GREEN: `_first_commit_where_state_complete` + `_resolution_delta`-based
comparison (`src/forge_cli/validation/__init__.py`) replaces the
unconditional exemption. The new RED now correctly fires,
`test_complete_change_is_exempt_from_post_completion_freeze_drift` and
`test_active_change_still_detects_freeze_drift` remain green, and a new
`test_tampering_after_completion_is_a_disclosed_residual_limitation`
documents the accepted, disclosed trade-off (drift *after* the genuine
completion seal is a different Change's concern) as distinct from the
BLOCKER (drift *before* sealing, which must and does still fire).

## Full suite and CLI
```
pytest -q            -> 376 passed (372 pre-existing + 4 new; zero regressions)
forge validate        -> exit 0, "Forge project is valid" (both CI-breaking
                          findings gone; reproduces the fix closing the exact
                          failure from GitHub Actions run 32091880352)
forge doctor          -> exit 0, all PASS
```

Passing Verification is evidence only, not Strict Review acceptance.
