---
forge:
  artifact: architecture
  schema: 1
change: CHG-0008
status: complete
---

# Architecture — Verifiable Reviewer/Resolver Separation

## Decision boundaries

Canonical semantics remain in the Protocol schema, Review Policy, Engineering Contract, and Specification. The CLI adds semantic C-026 guards at the existing validation boundary rather than creating a new lifecycle engine. Codex remains a projection layer and emits execution instructions derived from Flow context; it does not redefine review policy.

## Data model

`review.reviewer_identity` is a closed object with three required fields:

- `actor_type`: `human | agent_isolated_session | agent_same_session`;
- `session_ref`: non-empty durable Reviewer execution reference;
- `resolver_session_ref`: non-empty durable Resolver execution reference.

For every Change where `flow.current == full`, JSON Schema requires the complete object.

## Validation layers

Validation is deliberately split into two responsibilities:

1. **Structural — JSON Schema.** `change.schema.json` owns presence, object closure, actor enum, string type, and non-empty session references. A FULL manifest with no `reviewer_identity`, or a partial identity object, fails here before semantic C-026 evaluation.
2. **Semantic — CLI validator.** `forge validate` owns claims that are structurally representable but operationally inconsistent. For FULL, `agent_same_session` fails C-026. For any other actor type, identical `session_ref` and `resolver_session_ref` also fail C-026 because the evidence contradicts the claimed separation.

The exact mandatory RED fixture is structurally valid, so its CLI failure is evidence of the semantic layer rather than malformed input.

## Adapter projection

The Codex projector receives `flow_id`. For STANDARD/FULL it appends reviewer/resolver instructions requiring a separate review execution and recorded session references, with Reviewer `session_ref` distinct from Resolver `resolver_session_ref`. FAST output is not changed by this behavior.

## Compatibility boundary

The literal FULL structural requirement makes previously valid historical FULL `forge/change@1` manifests invalid under the updated schema. The Change simultaneously forbids retroactively editing those completed records. This conflicts with Protocol 1 C-045/C-046 and with canonical-instance validation. Architecture does not hide that contradiction by weakening tests or fabricating reviewer evidence; schema/Protocol versioning or an explicit migration boundary is required before final completion.

## Trade-offs

A separate same-model session improves operational independence by reducing context contamination and confirmation bias from the Resolver's execution trail. It does not provide epistemic independence or eliminate correlated model errors. `agent_different_model` remains future work.
