---
forge:
  artifact: verification
  schema: 1
change: CHG-0012
status: complete
---
# Verification — CHG-0012

## TDD
RED: `test_complete_change_is_exempt_from_post_completion_freeze_drift`
(`tests/unit/test_freeze_check_exempts_complete_changes.py`) written and run
against the unmodified validator; failed with exactly the CI's own finding
message, reproducing the causal bug rather than an environment failure.
`test_active_change_still_detects_freeze_drift` (regression guard) was
already green before the fix, proving the exemption did not yet exist.

GREEN: one-condition fix (`st.get("current")!="complete"`) added inline;
both tests pass; the causal RED reproduces and now correctly does not fire.

## Full suite and CLI
```
pytest -q            -> 374 passed (372 pre-existing + 2 new; zero regressions)
forge validate        -> exit 0, "Forge project is valid" (both CI-breaking
                          findings gone; reproduces the fix closing the exact
                          failure from GitHub Actions run 32091880352)
forge doctor          -> exit 0, all PASS
```

Passing Verification is evidence only, not Strict Review acceptance.
