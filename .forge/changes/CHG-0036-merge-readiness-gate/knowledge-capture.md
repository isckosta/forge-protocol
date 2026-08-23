---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0036
status: complete
---

# Knowledge Capture — CHG-0036 Merge Readiness Gate

## What Changed

Merge authorization is now evaluated by a reusable, repository-native engine
from explicit BASE..HEAD revisions and canonical Change evidence.

## Durable Knowledge

`forge validate` remains structural validity. `forge change merge-check` is a
separate authorization boundary and must fail closed when provenance,
revision history, Flow configuration, or lifecycle evidence is ambiguous.

## Consequences for Future Changes

Required CI must run the check on the exact Pull Request head with complete
history. Branch protection remains an external configuration boundary, while
release provenance remains an independent post-merge control.

## References

- `docs/rfcs/0006-merge-readiness-gate.md`
- `protocol/policies/merge-readiness.yml`
