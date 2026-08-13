---
forge:
  artifact: strict_review
  schema: 1
change: CHG-0002
iteration: 1
status: failed
---

# Strict Review — CHG-0002

## Iteration 1

Result: FAILED

Findings:

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0
- OBSERVATION: 0

Project policy treats MAJOR findings as blocking.

### REV-001 — CREATE publication contains a no-overwrite race

Severity: MAJOR

Status: OPEN

The publisher checks that a `CREATE` target is absent during global preflight, but does not revalidate absence immediately before publication. `_replace_file` ultimately uses `os.replace`, so a file created after preflight and before the write can be silently replaced.

This violates the no-silent-overwrite contract expressed by FR-017 and INV-004. The defect is especially material because the publisher explicitly narrows the analogous TOCTOU window for `UPDATE`, making the missing `CREATE` precondition inconsistent with the intended safe-publication boundary.

Required resolution:

1. establish a regression test that creates the target after preflight but before the CREATE write;
2. reach valid RED for silent replacement;
3. change publication so CREATE revalidates target absence immediately before mutation and reports conflict instead of overwriting;
4. preserve any externally-created file during rollback/conflict handling;
5. rerun the full automated and isolated-distribution Verification;
6. perform adversarial re-review.

## Review gate

FAILED until REV-001 is resolved and re-reviewed.
