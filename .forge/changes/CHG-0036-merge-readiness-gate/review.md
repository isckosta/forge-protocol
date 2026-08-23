---
forge:
  artifact: review
  schema: 1
change: CHG-0036
status: active
---

# Review — CHG-0036 Merge Readiness Gate

## Verdict

**REQUEST CHANGES**

## Iteration 1 — REQUEST CHANGES

Independent review found fail-open behavior in the initial evaluator:

- manifest-only completion claims could pass without Verification, Review,
  or provenance artifacts;
- ambiguous paths were discarded rather than blocked;
- shallow history and symlinked evidence were not rejected;
- Plan digest evidence did not validate role, assurance, observer, algorithm,
  or path; and
- Review subject and Reviewer provenance checks were incomplete.

The findings were resolved by adding RED tests and strengthening evidence,
materiality, history, symlink, Plan digest, subject, and Reviewer checks.

## Resolution

The initial review subject is superseded. A new immutable implementation
subject must be frozen and independently re-reviewed after the complete test
suite passes.
