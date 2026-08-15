---
forge:
  artifact: tasks
  schema: 1
change: CHG-0008
status: active
---
# Tasks — Verifiable Review Independence

## Historical
- [x] T-001 Preserve original CHG-0008 implementation/TDD history.
- [x] T-002 Preserve Strict Review Iterations 1 and 2 and findings R001-R005.

## Resolution 1
- [x] T-020 through T-034: Protocol 2 boundary, provenance ledger, all-Flow validation, Adapter projection, verification and distribution evidence.

## Resolution 2 — R004 remainder / R005
- [x] T-040 Record Specification Drift for concrete revision binding before implementation.
- [x] T-041 Create and observe dedicated RED: same `revision.id`, different commit.
- [x] T-042 Model logical revision separately from concrete immutable revision reference.
- [x] T-043 Enforce subject/Reviewer immutable-reference equality under C-026.
- [x] T-044 Enforce explicit Git subject existence and post-freeze subject mutation detection locally.
- [x] T-045 Preserve review-control metadata commits after freeze without allowing subject mutation.
- [x] T-046 Preserve Protocol 1 and FAST/STANDARD/FULL Protocol 2 regressions.
- [x] T-047 Update Protocol 2 Specification, Review Policy, schema, ADR, Architecture, Codex projection, evidence and knowledge capture.
- [x] T-048 Verify GREEN in Tests run 31903247493 and Distribution Verification run 31903247492.
- [x] T-049 Freeze the final Resolution 2 review subject; the following metadata commit records `resolution-002` against this immutable commit.
- [ ] T-050 Obtain independent Strict Review Iteration 3 against `resolution-002`.
- [ ] T-051 Complete CHG-0008 only after independent acceptance and all Completion Gates.
