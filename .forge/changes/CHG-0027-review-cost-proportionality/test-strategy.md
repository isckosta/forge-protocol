---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0027
status: not_applicable
---
# Test Strategy — Review Cost Proportionality

## TDD applicability

`tdd: not_applicable`. This Change proposes and documents an RFC only. It
does not add executable production behavior, a schema, a Flow, a Gate, or a
Review-policy implementation. There is therefore no honest RED/GREEN cycle
to run.

## Verification strategy

Verification will instead check that the RFC is Proposed, all referenced
paths and Git ranges exist, repository schemas validate, prohibited source
and protocol directories are unchanged, and roadmap status matches the
RFC-only scope. A future implementation Change must define its own real
test strategy and TDD evidence.
