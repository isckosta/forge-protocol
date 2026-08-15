---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0008
status: approved
---

# Test Strategy — CHG-0008

## Historical cycles
TDD-001 through TDD-009 remain preserved. TDD-006 covers the Protocol 1/2 provenance boundary, TDD-007 Protocol-aware projection, TDD-008 concrete immutable revision binding, and TDD-009 the R006 effective-workspace freeze.

## TDD-010 — R007 immutable provenance authority
The causal RED exercises the real CLI boundary, not a text/helper assertion:

1. freeze reviewable subject A;
2. commit `resolution-001` provenance binding to A;
3. commit reviewable mutation B;
4. rewrite only review-control metadata so subject and Reviewer provenance coherently claim B;
5. require `forge validate` to reject the moved baseline.

The threat matrix extends that causal case with mutation of immutable_ref/commit/logical revision and execution fields, Role replacement, removal/recreation, duplicate/shadow IDs, historical Review Iteration redirection, legitimate Reviewer-record append, shallow-history fail-closed behavior, and preservation of R006 committed/staged/unstaged/untracked/rename/symlink protections.

Existing regressions remain authoritative for exact Change-local metadata paths, metadata lookalikes, another Change's metadata, tracked deletion/rename, Git-visible untracked paths, ignored paths, symlink/directory substitution, nested repository-root discovery, Protocol 1 compatibility, and FAST/STANDARD/FULL Protocol 2 behavior.

## Expected lifecycle behavior
A newly created subject record may be written prospectively after its reviewable subject commit. Once that record first appears in committed Git history, its semantic content is immutable. New Review provenance and legitimate `manifest.yml`/`review.md` state may be added without renewing the subject, provided neither the anchored subject record nor an existing Iteration's subject binding changes.

## Verification
GREEN requires the complete `pytest -q` suite, direct `forge validate` and `forge doctor` against the repository with complete Git history, and Distribution Verification. Distribution Verification continues to exercise wheel build, isolated wheel-only install, offline init/validate/doctor, Adapter schema/loading, and runtime dependency audit.

Passing Verification is Resolution evidence only. It is not Strict Review acceptance.
