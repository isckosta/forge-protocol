---
forge:
  artifact: architecture
  schema: 1
change: CHG-0008
status: complete
---

# Architecture — Verifiable Reviewer/Resolver Separation

## Decision boundaries

Canonical semantics remain in Protocol schema, Review Policy, Engineering Contract, and Specification. The CLI adds a semantic guard at the existing validation boundary rather than creating a new lifecycle engine. Codex remains a projection layer and only emits instructions derived from Flow context; it does not redefine review policy.

## Data model

`review.reviewer_identity` is a closed object with:

- `actor_type`: `human | agent_isolated_session | agent_same_session`;
- `session_ref`: durable Reviewer execution reference;
- `resolver_session_ref`: durable Resolver execution reference.

Pending Review may omit the identity because no review execution exists yet. Active/failed/passed FULL Review requires it for non-completed Changes. Completed historical Changes remain untouched.

## Validation

`validate_project` scans repository-native Change manifests and emits a `ValidationFinding` with code `C-026` when FULL explicitly records `agent_same_session`. Structural identity requirements remain in JSON Schema; semantic prohibition remains in CLI validation.

## Adapter projection

The Codex projector receives `flow_id`. For STANDARD/FULL it appends reviewer/resolver instructions requiring a separate review execution and recorded session references. FAST output is not changed by this behavior.

## Trade-offs

YAML parsing failures in Change manifests remain outside this focused semantic check because generic Change-schema validation is not currently part of `forge validate`. Isolated same-model sessions improve context separation but do not provide model-bias independence.
