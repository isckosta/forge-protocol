---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0002
status: approved
---

# Test Strategy — Harness Adapter Foundation

## Objective

Drive Adapter Foundation behavior through TDD while keeping Core independent from any real Harness SDK or installation.

## Test levels

### Unit
Use for Adapter manifest parsing, Protocol interval compatibility, capability vocabulary, ownership/intent enums, deterministic plan ordering, digest comparison, and conformance checks.

### Integration
Use temporary repositories for installation records, path confinement, collision detection, drift detection, and safe publication behavior.

### Contract
Use canonical fixture manifests and Effective Forge Configuration fixtures to prove Adapter semantics are independent from a specific Harness.

## First TDD sequence

1. Adapter manifest schema and validation.
2. Protocol compatibility interval.
3. Capability declaration and unsupported-required-capability reporting.
4. Adapter plan model and stable ordering.
5. Ownership and collision semantics.
6. Installation record and digest-based drift detection.
7. Conformance checks for Flow/TDD/Strict Review preservation.
8. Safe publisher only after planning and conflict semantics are proven.

## RED evidence

Every behavioral cycle records the Requirement(s), failing test identifier, expected failure, and observed reason before production implementation.

## Regression policy

Any defect discovered during CHG-0002 receives a reproducing regression test first when reasonably automatable.

## Verification beyond TDD

Completion Verification includes full suite, isolated wheel installation, bundled schema/resource availability, offline manifest validation/planning, path-security and symlink cases, deterministic repeated planning, installation-record roundtrip, and dependency audit.
