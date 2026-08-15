---
forge:
  artifact: verification
  schema: 1
change: CHG-0008
status: passed
---
# Verification — CHG-0008 Resolutions

Verification evidence is Resolver evidence only; it is not Strict Review acceptance.

## Historical Resolution 3 — R006
Resolution 3 established the effective reviewable workspace freeze: committed, staged, unstaged, deletion/rename, and Git-visible untracked state are combined from the Git repository root; exact Change-local `manifest.yml`, `provenance.yml`, and `review.md` are the only review-control path exceptions and must remain regular non-symlink files. Its causal GREEN was `eaa6c481e5ea9a08c3f4e234feb6d1cbf871ee99`, Tests run `31904623010`, with Distribution Verification run `31904622991`. Final Resolution 3 regressions passed at Tests run `31904809568` and Distribution Verification run `31904809691`. Strict Review Iteration 4 subsequently accepted R006 for its original dirty-workspace defect and found R007 instead.

## Resolution 4 — R007 root cause
The R006 allowlist protected the effective filesystem delta but left the source of the baseline mutable. `_validate_protocol2_review_provenance` loaded the subject immutable Git commit from the current `provenance.yml`; `_reviewable_workspace_delta` then excluded that same `provenance.yml`. A post-freeze reviewable commit B could therefore be hidden by rewriting the allowlisted subject and Reviewer records from frozen A to B.

## TDD-010 causal RED
RED commit `73f865ff712647c24a0203c530703d69c2513ae8`, Tests run `31906413392`, job `95064855880`:

- setup and dependency installation passed;
- command: `pytest -q`;
- result: `1 failed, 212 passed in 5.49s`;
- failing regression: `test_rewriting_frozen_subject_provenance_cannot_move_baseline`;
- observed vulnerable behavior: `forge validate` returned exit code `0` after freeze A → reviewable commit B → coherent subject/Reviewer provenance rewrite to B.

## Implementation and authority boundary
Core now resolves committed history for the exact Change-local provenance and manifest paths before trusting current review-control metadata. The first committed representation of a referenced subject provenance record is the immutable repository-native authority for the full subject record. The first committed `revision`/`subject_provenance` pair for an existing Review Iteration is independently authoritative.

Current metadata may append new provenance records and update legitimate review state, but it cannot mutate or redirect those anchored records. A differing Role, Execution, Context, logical revision, immutable reference/commit, source/assurance, record identity, or historical Iteration subject binding is rejected before the immutable commit is used for effective-workspace comparison. Missing referenced records and duplicate current IDs remain rejected by existing validation.

A repository with no `HEAD` has no historical authority yet and may establish its first record prospectively. Once an anchor exists, complete local Git history is required. Shallow history and Git/history lookup failures fail closed. GitHub or a hosted Forge backend is not required.

## GREEN and regression preservation
Corrected implementation commit `80292e6acc54a59e15bf4c4919b9286cc2ba5dd6`:

- Tests run `31906638536`: PASS;
- Distribution Verification run `31906638462`: PASS.

The R007 regression suite was subsequently expanded to cover subject-field mutation, Role replacement, historical Iteration redirection, legitimate Reviewer-record append, subject-record removal, and shallow-history fail-closed behavior. Existing R006 regressions continue to cover committed/staged/unstaged/untracked mutation, deletion, rename, exact metadata boundaries, symlink/directory substitution, and metadata lookalikes. Protocol 1 and FAST/STANDARD/FULL Protocol 2 coverage remain in the suite.

CI checkouts used by repository validation now use complete Git history (`fetch-depth: 0`), because a shallow clone cannot truthfully establish the first committed provenance authority. The Tests workflow also dogfoods `forge validate` and `forge doctor` against the repository itself after the full test suite.

## Assurance
The new authority is recorded repository-native Git history. It detects semantic rewrites relative to the repository history available to Core, but it is not cryptographic/external attestation and does not claim protection against an actor who can rewrite Git history itself. `recorded` remains the correct assurance for this Resolver execution.

## Resolution 4 freeze procedure
All implementation, tests, Protocol 2 normative resources, architecture, strategy, TDD evidence, verification, traceability/knowledge changes and workflow changes belong to the Resolution 4 reviewable subject and must be finalized before freeze. After the final reviewable commit is green, that exact commit becomes `chg-0008-resolution-004`'s frozen subject. A subsequent Change-local `provenance.yml` metadata commit records `resolution-004` pointing back to it; that first committed record becomes the immutable provenance authority. Only legitimate review-control metadata may follow. No `review-005`, Strict Review PASS, Completion, or merge is produced by this Resolver.
