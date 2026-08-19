<!-- Illustrative example, not a real Change. See README.md. -->

# Verification — CHG-EXAMPLE

<!-- protocol/artifact-structure.md §2.1/§2.3/§4 (Verification): the
     outcome comes first, before any evidence. A reader never needs to
     read past this section to learn PASS or FAIL. -->

## Result

# PASS

<!-- protocol/artifact-structure.md §2.4 Scanability: a short table
     mapping each Acceptance Criterion to its individual result reads
     well here, once Result itself is already known. -->

## Summary

| Acceptance Criterion | Result |
| --- | --- |
| AC-001 — rejects usernames shorter than 3 characters | PASS |
| AC-002 — accepts usernames of exactly 3 characters | PASS |
| AC-003 — existing valid usernames unaffected | PASS |

<!-- protocol/artifact-structure.md §2.2 Artifact Responsibility:
     Verification contains what was checked and its result — not a
     re-argument of the Specification. -->

## Test Evidence

- `pytest tests/unit/test_users.py -q` — 6 passed, 0 failed.
- `TDD-001` (RED, `test_create_username_rejects_short_names`): failed
  before the fix for the expected reason (`ValueError` not raised);
  passes after.

## Forge Evidence

- `forge validate` — "Forge project is valid" (exit 0).
- `forge doctor` — 7/7 checks PASS.

## Compatibility

No public interface changed shape; `create_username`'s existing valid
inputs are unaffected (AC-003).

## Conclusion

All Acceptance Criteria verified PASS. No Limitations to record.
