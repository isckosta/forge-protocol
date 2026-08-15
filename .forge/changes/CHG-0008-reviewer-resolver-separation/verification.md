---
forge:
  artifact: verification
  schema: 1
change: CHG-0008
status: passed
---
# Verification — Strict Review Iteration 2 Resolution

Resolution implementation and Verification are passed; this is not Strict Review acceptance.

## Scope
This Resolution addresses the remainder of R004 and R005. R001-R003 remain preserved as resolved by the prior Resolution and were regression-protected.

## Dedicated RED
Test-only commit `b565426abc2b1c04f322667635b3267373fb17a7` introduced the case required by R005: valid subject/Reviewer Roles and assurance, distinct Execution/Context, same logical `revision.id`, but different commits. Tests run `31902858488`, job `95056158653`, reached the test step after environment/dependency setup and failed because Core still accepted commit divergence.

## Implementation
Core now normalizes a concrete immutable revision reference. `revision.commit` remains compatible Git shorthand; `revision.immutable_ref` provides the generic representation. Subject and Reviewer provenance must match on logical and concrete revision. Explicit Git subjects must exist locally. Once frozen, any committed change outside Change-local `manifest.yml`, `provenance.yml`, and `review.md` invalidates the binding and requires new subject provenance.

This makes the review subject explicit without impossible commit self-reference: reviewable evidence is frozen first; provenance metadata is committed afterwards and points to the frozen subject.

## GREEN
GREEN revision `e360685531e2a4ee76890b1c636173f02ead1d3e`:
- Tests run `31903247493`, job `95057114869`: PASS (`pytest -q`).
- Distribution Verification run `31903247492`: PASS.
- Distribution workflow covers wheel build, isolated wheel install, offline init/validate/doctor, Adapter schema/loading and dependency audit.
- Protocol 1 compatibility and Protocol 2 FAST/STANDARD/FULL regressions are included.
- Existing forged IDs, shared Execution, shared Context, wrong logical revision and downgrade regressions remain in the suite.

## Assurance boundary
`recorded` continues to mean repository-native self-recorded evidence. It is not external/cryptographic proof. `verified` remains stronger observer-backed evidence. Core now mechanically verifies concrete revision consistency in addition to the prior provenance relationships.

## Review boundary
Strict Review Iterations 1 and 2 remain historical failures. This Resolver does not create Reviewer provenance for Iteration 3, does not approve the Resolution, and does not complete or merge CHG-0008. The final review-subject freeze and `resolution-002` record are established by the subsequent review-control metadata commit.
