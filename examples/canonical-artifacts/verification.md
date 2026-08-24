<!-- Illustrative example, not a real Change. See README.md. -->

---
forge:
  artifact: verification
  schema: 1
change: CHG-EXAMPLE
status: passed
---
# CHG-EXAMPLE · Verification

<!-- protocol/artifact-structure.md §2.1/§2.3/§4 (Verification): the
     outcome comes first, before any evidence. A reader never needs to
     read past this section to learn PASS or FAIL. Rendered as bold
     text, not a nested heading, per §4's rendering recommendation. -->

## Result

**PASS**

<!-- §4 (Verification): Summary is a short aggregate read, not a
     restatement of individual results — those belong to Acceptance
     Coverage below. -->

## Summary

4 Acceptance Criteria verified: 4 passed, 0 failed. Automated and Forge
checks passed; one Manual Evidence check was required and passed. No
Limitations.

<!-- §2.4 Scanability: a compact table referencing ids, not the full
     Acceptance Criterion text (which already lives in specification.md,
     §2.2 Artifact Responsibility). -->

## Acceptance Coverage

| Acceptance | Requirement | Result | Evidence |
| --- | --- | --- | --- |
| AC-001 | FR-001 | PASS | TDD-001 |
| AC-002 | FR-001 | PASS | TDD-001 |
| AC-003 | FR-001 | PASS | TDD-002 |
| AC-004 | FR-002 | PASS | Manual Evidence |

<!-- §4 (Verification): Requirement Coverage is conditional — shown
     here because FR-001 aggregates two Acceptance Criteria covered by
     two different TDD-xxx cases, which Acceptance Coverage alone does
     not make obvious. A Change where every Requirement maps 1:1 to one
     Acceptance Criterion would correctly omit this section. -->

## Requirement Coverage

| Requirement | Evidence | Result |
| --- | --- | --- |
| FR-001 | TDD-001, TDD-002 | PASS |
| FR-002 | Manual Evidence | PASS |

<!-- §2.2 Artifact Responsibility: Verification contains what was
     checked and its result — not a re-argument of the Specification.
     TDD-xxx is referenced by id (tdd-evidence.yml is the authority for
     the RED/GREEN sequence itself), not renarrated. -->

## Test Evidence

- `pytest tests/unit/test_users.py -q` — 6 passed, 0 failed.
- `TDD-001` (`test_create_username_rejects_short_names`): RED failed
  before the fix for the expected reason (`ValueError` not raised);
  GREEN passes after — see `tdd-evidence.yml`.
- `TDD-002` (`test_create_username_accepts_minimum_length`): RED/GREEN
  as above.

## Forge Evidence

- `forge validate` — "Forge project is valid" (exit 0).
- `forge doctor` — 7/7 checks PASS.

<!-- §4 (Verification): Manual Evidence stays distinct from Test/Forge
     Evidence so a human observation is never presented as an
     automated guarantee. -->

## Manual Evidence

FR-002 (support-facing documentation) — the on-call runbook's username
policy section was read side-by-side with the new validation error
message by the reviewing operator; the wording matches. Covers AC-004.

## Compatibility and Limitations

No public interface changed shape; `create_username`'s existing valid
inputs are unaffected (AC-003). No Limitations to record.

## Conclusion

All Acceptance Criteria verified PASS; no regressions found. The
Change is ready for the next gate defined by its Flow.
