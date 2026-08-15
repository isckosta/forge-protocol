---
forge:
  artifact: architecture
  schema: 1
change: CHG-0008
status: complete
---

# Architecture — Verifiable Review Independence

## Decision boundaries

Canonical semantics remain in the Protocol schema, Review Policy, Engineering Contract, and Specification. The CLI adds semantic C-026 guards at the existing validation boundary rather than creating a lifecycle engine. Harness Adapters project the invariant into native execution terminology but do not redefine it.

## Core model

Forge models review independence with provider-independent concepts:

- **Execution**: one concrete invocation performing work;
- **Execution Context**: transient conversational, reasoning, or equivalent non-repository state visible to that Execution.

`review.reviewer_identity` is a closed object containing:

- `actor_type`: `human | agent`;
- `execution_id`: durable Reviewer execution reference;
- `context_id`: durable Reviewer context reference;
- `resolver_execution_id`: Implementation/Resolution execution reference;
- `resolver_context_id`: Implementation/Resolution context reference.

`forge/change@2` requires the complete object for FULL Changes. `forge/change@1` keeps it optional for compatibility.

## Validation layers

1. **Structural — JSON Schema.** Owns presence, closure, actor enum, identifier type, and non-empty values.
2. **Semantic — CLI validator.** Owns C-026 independence checks. Equality of Reviewer/Resolver execution IDs is invalid. Equality of Reviewer/Resolver context IDs is independently invalid. One distinct identifier cannot compensate for equality of the other.

This makes the failure mode explicit: `review-exec-2` using the Resolver's conversation context is still contaminated, while a claimed new context inside the same concrete execution is still self-review.

## Resolution and re-review

The Resolver for blocking Findings must run outside the Reviewer's Execution Context. After resolution, acceptance requires a re-review Execution and Context independent from that Resolution. The same Reviewer actor may re-review in a fresh compliant context.

## Adapter projection

Codex STANDARD/FULL projections instruct the harness to create a real execution/context boundary, record all four identifiers, treat Role switching in the same conversation as self-review, and repeat the independence boundary for re-review after blocking Resolution.

Harnesses may call these primitives runs, threads, sessions, conversations, invocations, or workspaces. Adapters map those native references into Forge `execution_id`/`context_id`; Core never depends on the Harness term "session".

## Compatibility boundary

The artifact-shape break remains isolated to `forge/change@2`. Historical `forge/change@1` manifests remain valid and are not retroactively edited. No historical reviewer evidence is fabricated.

## Trade-offs

Execution-context isolation reduces context contamination and confirmation bias but does not guarantee epistemic independence. Same-model isolated executions may retain correlated blind spots. Different-model or human-only review can be stricter project policy, not a Core requirement.
