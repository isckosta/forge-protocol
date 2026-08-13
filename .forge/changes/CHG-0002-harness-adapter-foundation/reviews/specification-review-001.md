---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0002
iteration: 1
status: failed
---

# Specification Review — CHG-0002

## Result

FAILED

- BLOCKER: 1
- MAJOR: 2
- MINOR: 0

## SPEC-001 — Protocol range grammar is undefined

Severity: BLOCKER

The specification requires an Adapter to declare a supported Protocol range but does not define a canonical range grammar. Independent implementations could interpret the same manifest differently.

Resolution required: Protocol v1 Adapter manifests will use explicit integer bounds rather than free-form semantic-version expressions:

```yaml
protocol:
  min: 1
  max_exclusive: 2
```

Compatibility is `min <= project_protocol < max_exclusive`.

## SPEC-002 — Required capability source is ambiguous

Severity: MAJOR

The specification says unsupported required capabilities must be reported but does not define what makes a capability required.

Resolution required: Adapter conformance requirements derive from Effective Forge Configuration and canonical Flow/Contract invariants. An Adapter may additionally require capabilities for its own operation, but those are implementation requirements and cannot redefine Forge semantics.

## SPEC-003 — Installation versus activation is ambiguous

Severity: MAJOR

The specification uses activation without defining an Adapter lifecycle state.

Resolution required: CHG-0002 will not introduce an activation state. The relevant operations are manifest validation, planning, installation record creation/update, drift validation, and publication. Compatibility failure blocks planning/application.

## Gate

Specification Gate: FAILED until the resolutions are incorporated and re-reviewed.
