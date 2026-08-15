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

## Compatibility boundary (resolved via schema versioning)

The literal FULL structural requirement would have made previously valid historical FULL
`forge/change@1` manifests invalid under the updated schema, conflicting with Protocol 1
C-045/C-046 and with canonical-instance validation, since the Change forbids retroactively
editing completed records.

This is resolved by isolating the break to a new schema suffix rather than the existing one,
exactly as `protocol/compatibility.md` already prescribes ("An individual artifact shape may
instead require a new schema suffix when the break is limited to that artifact"):

- `protocol/schemas/change.schema.json` (`forge/change@1`) is restored to its pre-Change shape:
  `reviewer_identity` remains a defined, optional property; no `allOf` forces its presence.
  Every existing conforming instance — historical Changes and CHG-0008's own in-progress
  manifest — stays valid.
- `protocol/schemas/change-v2.schema.json` (`forge/change@2`) is new. It is byte-identical to
  v1 except for the `schema` const and the `allOf`/`if`/`then` requiring `reviewer_identity`
  whenever `flow.current == full`, unconditional on review status (matching AC-004 literally).
- `protocol/schemas/catalog.yml` registers `forge/change@2` alongside `forge/change@1`.
- The RED fixture (`tests/fixtures/full-change-agent-same-session.yml`) declares
  `schema: forge/change@2`, since it exists specifically to exercise the new mandatory
  behavior. A regression test (`test_forge_change_v1_does_not_require_reviewer_identity_for_full`)
  pins the opposite behavior for v1 so the two schemas cannot silently reconverge.

No Protocol version bump was needed: Protocol, Schema, CLI, and Adapter versions are
independent axes per `compatibility.md`, and this break is limited to one artifact shape.

## Trade-offs

A separate same-model session improves operational independence by reducing context contamination and confirmation bias from the Resolver's execution trail. It does not provide epistemic independence or eliminate correlated model errors. `agent_different_model` remains future work.
