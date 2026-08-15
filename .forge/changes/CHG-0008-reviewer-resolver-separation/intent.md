---
forge:
  artifact: intent
  schema: 1
change: CHG-0008
status: complete
---

# Intent — Verifiable Review Independence

## Problem

Protocol 1's conceptual Reviewer/Resolver Role separation was insufficient to prevent self-review by Role switching inside one Execution Context. Strict Review Iteration 1 then established that strengthening that rule in-place under integer Protocol 1 violated C-045/C-046, while arbitrary unequal execution/context strings still did not constitute durable evidence.

## Goal

Introduce an honest compatibility boundary for verifiable review independence: preserve Protocol 1 historical meaning, define the stronger invariant in Protocol 2, capture provider-independent revision-bound execution provenance, and enforce it consistently across FAST, STANDARD, and FULL without overstating what Core can prove.

## Required outcomes

1. Preserve existing valid Protocol 1 instances and schemas.
2. Introduce integer Protocol 2 for independent Strict Review Execution and Execution Context.
3. Separate Protocol version from artifact schema version.
4. Persist Implementation/Resolution/Review provenance before it is referenced by Review.
5. Distinguish claimed, recorded, and verified provenance.
6. Bind Review Iterations to the revision and provenance they evaluate.
7. Reject forged IDs, missing/partial/wrong-revision provenance, shared Execution/Context, contaminated re-review, and active downgrade attempts.
8. Apply Protocol 2 quality invariants equally to FAST, STANDARD, and FULL.
9. Keep Core local and provider-independent.
10. Preserve Strict Review Iteration 1 and leave this Resolution awaiting a new independent Reviewer.

## Non-goals

- No retroactive fabrication of CHG-0008's original Implementation/Review provenance.
- No hosted Forge backend requirement.
- No claim that self-recorded repository provenance is cryptographic/external proof.
- No Strict Re-review, approval, merge, or Completion performed by this Resolver execution.

## Flow

FULL. This Change alters canonical Protocol versioning, review semantics, schemas, validation, diagnostics, Adapter projection, compatibility documentation, and durable Change evidence.
