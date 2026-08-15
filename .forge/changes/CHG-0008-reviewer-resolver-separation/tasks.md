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
- [x] T-002 Preserve Strict Review Iterations and findings without rewriting historical verdicts.

## Resolution 1
- [x] T-020 through T-034: Protocol 2 boundary, provenance ledger, all-Flow validation, Adapter projection, verification and distribution evidence.

## Resolution 2 — R004 remainder / R005
- [x] T-040 Record Specification Drift for concrete revision binding before implementation.
- [x] T-041 Create and observe dedicated RED: same `revision.id`, different commit.
- [x] T-042 Model logical revision separately from concrete immutable revision reference.
- [x] T-043 Enforce subject/Reviewer immutable-reference equality under C-026.
- [x] T-044 Enforce explicit Git subject existence and committed post-freeze subject mutation detection locally.
- [x] T-045 Preserve review-control metadata commits after freeze without allowing committed subject mutation.
- [x] T-046 Preserve Protocol 1 and FAST/STANDARD/FULL Protocol 2 regressions.
- [x] T-047 Update Protocol 2 Specification, Review Policy, schema, ADR, Architecture, Codex projection, evidence and knowledge capture.
- [x] T-048 Verify GREEN in Tests run 31903247493 and Distribution Verification run 31903247492.
- [x] T-049 Freeze the final Resolution 2 review subject and record `resolution-002` against it.
- [x] T-050 Obtain independent Strict Review Iteration 3 against `resolution-002`; preserve its REQUEST CHANGES verdict and R006.

## Resolution 3 — R006 / Iteration 3 CI regression
- [x] T-052 Record Specification Drift for effective reviewable workspace freeze before final Resolution 3 behavior.
- [x] T-053 Add dedicated R006 regressions for unstaged, staged, untracked, deletion, rename, metadata allowlist, ignored paths, and adversarial path bypasses.
- [x] T-054 Establish a causal RED against the pre-fix validator after repairing the unrelated malformed Iteration 3 YAML artifact.
- [x] T-055 Replace commit-only freeze detection with one local reviewable workspace delta covering committed, staged, unstaged, and untracked Git state.
- [x] T-056 Enforce exact Change-local review-control paths and reject rename/symlink/lookalike/directory/same-basename bypasses.
- [x] T-057 Preserve R001-R005, Protocol 1, and FAST/STANDARD/FULL Protocol 2 regressions.
- [x] T-058 Update Protocol 2 normative resources and Codex Adapter freeze guidance.
- [x] T-059 Diagnose the `Tests` workflow failure as malformed YAML in the Iteration 3 `evidence_gap` and repair the artifact without weakening tests/workflows.
- [x] T-060 Obtain causal GREEN: Tests run 31904623010 (`210 passed`) and Distribution Verification run 31904622991 pass on the restored R006 implementation.
- [x] T-061 Complete final pre-freeze Resolution 3 evidence and full regression checkpoint: Tests run 31904809568 (`212 passed`) and Distribution Verification run 31904809691 passed.
- [ ] T-062 After the immutable subject is created, record `resolution-003` and prepare `review-004` pending using only review-control metadata.
- [ ] T-063 Dogfood the freeze after review-control metadata and confirm final CI remains green.
- [ ] T-064 Obtain independent Strict Review Iteration 4 against `resolution-003`.
- [ ] T-051 Complete CHG-0008 only after independent acceptance and all Completion Gates.

T-062/T-063 intentionally remain unchecked in this reviewable artifact because they occur only after this reviewable Resolution state is frozen. Their authoritative post-freeze state is represented by the allowed review-control metadata and final CI, not by mutating `tasks.md` after the freeze.
