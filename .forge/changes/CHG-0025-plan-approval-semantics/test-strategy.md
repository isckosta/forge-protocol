---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0025
status: complete
---

# Test Strategy — Plan Approval Semantics

## Behavioral scope

The Plan authorization validator and Gate dependency are executable behavior,
so TDD applies. The RFC and Contract wording themselves are prose and have no
separate TDD cycle.

## Test level

Use focused unit tests for the validation function and its manifest-level
integration with the existing unresolved-Decision validation. Run the
contract/schema suite and the full pytest suite during Verification.

## Required cases

1. Active approved Plan with no Decision: one Plan authorization finding.
2. Active approved Plan with open matching Decision: invalid/fails closed.
3. Active approved Plan with autonomous human-authority resolution: C-055
   finding and no authorization pass.
4. Active approved Plan with human Decision but no recorded approval boundary:
   C-077 finding and no authorization pass.
5. Active approved Plan with resolved human Decision and recorded approval
   boundary: Plan check passes.
6. Multiple valid matching approvals or conflicting active approvals fail
   closed; a superseded historical approval does not satisfy the check.
7. Historical Changes allocated before CHG-0025 remain compatible.
8. Existing specification Gate assertions and unrelated Decision rules remain
   unchanged.

## TDD evidence boundary

The RED command and its observed expected failure MUST be recorded before the
implementation change. A pure documentation statement MUST NOT be presented
as a fabricated test cycle.
