<!-- Illustrative example, not a real Change. See README.md. -->

# Strict Review — CHG-EXAMPLE

<!-- protocol/artifact-structure.md §2.1/§2.3/§4 (Review): an aggregate
     Verdict at the very top. A Change with several iterations would
     otherwise make a top-to-bottom reader scroll past every earlier
     negative verdict before reaching the one that matters for
     Completion (see CHG-0008, six iterations, cited in Discovery). -->

## Verdict

# PASS (final, Iteration 2)

<!-- protocol/artifact-structure.md §2.4 Scanability. -->

## Summary

| Severity | Count |
| --- | --- |
| BLOCKER | 0 |
| MAJOR | 0 |
| MINOR | 0 |
| OBSERVATION | 1 |

## Review Subject

`create_username` length validation, subject commit `a1b2c3d`.

<!-- protocol/artifact-structure.md §4 (Review): the existing
     per-iteration `## Iteration N — <verdict>` convention is preserved
     unchanged beneath the aggregate Verdict, not replaced by it. -->

## Iteration 1 — REQUEST CHANGES

### R001 — MINOR — Boundary case (exactly 3 characters) untested

**Problem:** `AC-002` has no direct test.

**Evidence:** `tests/unit/test_users.py` covers `len < 3` and `len > 3`
only.

**Impact:** A future off-by-one regression at the boundary would not be
caught.

**Required Resolution:** Add a test for the exact-3-characters case.

## Iteration 2 — PASS

R001 resolved: `test_create_username_accepts_minimum_length` added and
passing. One OBSERVATION recorded (naming style, non-blocking) and
accepted without a required change.

## Approved Aspects

TDD ordering (RED before GREEN), root-cause fix (not a mitigation),
Verification evidence completeness.

## Conclusion

No BLOCKER or MAJOR Findings remain. **PASS.**
