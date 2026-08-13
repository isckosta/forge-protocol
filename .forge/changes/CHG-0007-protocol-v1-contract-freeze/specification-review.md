---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0007
status: passed
iteration: 3
---

# Adversarial Specification Review — Protocol v1 Contract Freeze

## Review objective

Attempt to reject the proposed freeze for ambiguous compatibility promises,
incomplete schema scope, contradictory Flow semantics, or permission to rewrite
historical evidence.

## Iteration 1 findings

### SR-001 — MAJOR — “Backward compatible” lacked a rejection boundary

The initial design did not say whether changing a required field or Gate under
the same integer identifier was allowed. FR-003 through FR-005 now distinguish
compatible additions from changes that require a new integer Protocol.

Resolution: accepted.

### SR-002 — MAJOR — “Validate schemas” did not define catalog closure

Testing only the six existing JSON files would leave Flow, Policy, and TDD
identifiers unsupported. FR-007 through FR-010 now require a portable catalog,
identity agreement, schema validity, canonical instances, and the complete v1
surface.

Resolution: accepted.

### SR-003 — MAJOR — Historical cleanup could falsify evidence

An unconstrained migration could normalize inaccurate completion or TDD claims.
FR-013 and INV-002 now limit migration to mechanical shape changes and prohibit
improving historical facts.

Resolution: accepted.

### SR-004 — MINOR — FAST Requirement precondition could be over-frozen

FAST does not require formal Requirement identifiers, so copying the STANDARD
precondition would increase ceremony without quality value. FR-012 makes this
distinction explicit while preserving common behavioral RED checks.

Resolution: accepted.

## Iteration 2 decision

The revised Specification has bounded compatibility semantics, complete schema
scope, explicit historical integrity, deterministic validation, and testable
acceptance scenarios. No blocker or major finding remains.

Decision: PASS.

## Iteration 3 — Pre-implementation feasibility correction

### SR-005 — MAJOR — Standard JSON Schema cannot compare interval fields

The implementation plan incorrectly assigned `min < max_exclusive` entirely
to Draft 2020-12 JSON Schema. The standard has no portable cross-field numeric
comparison keyword. AC-004 now assigns type/bound checks to JSON Schema and
ordering to the existing deterministic Adapter manifest validator. This keeps
the acceptance behavior while avoiding a non-standard extension.

Resolution: accepted before production implementation. Decision remains PASS.
