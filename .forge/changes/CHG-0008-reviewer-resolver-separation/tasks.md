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
- [x] T-047 Update Protocol 2 authority/resources and Change evidence required by R005.
- [x] T-048 Verify Resolution 2 GREEN and Distribution Verification.
- [x] T-049 Freeze Resolution 2 and record `resolution-002`.
- [x] T-050 Preserve independent Strict Review Iteration 3 REQUEST CHANGES and R006.

## Resolution 3 — R006
- [x] T-052 Record Specification Drift for effective reviewable workspace freeze.
- [x] T-053 Add staged, unstaged, untracked, deletion, rename and metadata-boundary regressions.
- [x] T-054 Establish causal R006 RED.
- [x] T-055 Enforce one repository-root effective reviewable workspace delta.
- [x] T-056 Preserve the exact Change-local metadata exception; reject path/symlink/lookalike bypasses.
- [x] T-057 Preserve R001-R005, Protocol 1, and FAST/STANDARD/FULL regressions.
- [x] T-058 Update architecture/guidance for the effective workspace freeze.
- [x] T-059 Diagnose and repair unrelated historical malformed YAML without weakening enforcement.
- [x] T-060 Obtain causal R006 GREEN and Distribution Verification.
- [x] T-061 Complete pre-freeze Resolution 3 evidence and regression checkpoint.
- [x] T-062 Record `resolution-003` after freeze using review-control metadata.
- [x] T-063 Confirm post-freeze dogfood/CI remains green.
- [x] T-064 Preserve independent Strict Review Iteration 4 REQUEST CHANGES and R007.

## Resolution 4 — R007
- [x] T-065 Establish causal RED for mutable allowlisted provenance moving the frozen baseline.
- [x] T-066 Anchor referenced subject provenance and Review Iteration subject selection to committed Git history.
- [x] T-067 Preserve R005/R006, exact metadata boundaries, Protocol 1 and all Protocol 2 Flow regressions.
- [x] T-068 Record TDD/verification/architecture/knowledge evidence, freeze Resolution 4 and record `resolution-004`.
- [x] T-069 Preserve independent Strict Review Iteration 5 REQUEST CHANGES and R008.

## Resolution 5 — R008
- [x] T-070 Establish tests-only RED proving failed Iteration `revision`/`subject_provenance` rewrites bypass historical authority.
- [x] T-071 Remove verdict/status coupling from Review Iteration subject-binding history enforcement.
- [x] T-072 Add adversarial coverage for revision-only, provenance-only, simultaneous rewrite, lifecycle transition, mutable review metadata, new Iteration and historical ID replacement.
- [x] T-073 Preserve committed bound Iteration IDs so remove/rename/replacement cannot evade per-ID authority.
- [x] T-074 Preserve fail-closed history behavior while allowing a later valid binding to establish authority after a historical YAML snapshot that could not itself establish one.
- [x] T-075 Verify R005/R006/R007, Protocol 1 compatibility, Protocol 2 FAST/STANDARD/FULL, `forge validate`, `forge doctor`, schemas/contract tests and distribution verification in the full suite.
- [x] T-076 Update architecture, knowledge capture, TDD evidence, verification, tasks and traceability for R008 without normative churn.
- [ ] T-077 Freeze the final Resolution 5 reviewable subject and record `resolution-005` using only truthful repository-native provenance.
- [ ] T-078 Obtain a new independent Strict Review Iteration 6 against `resolution-005`.
- [ ] T-051 Complete CHG-0008 only after independent acceptance and all Completion Gates.

T-077 is completed only by the post-freeze review-control metadata sequence. T-078 explicitly belongs to a separate Reviewer execution and is not executed by this Resolution session.
