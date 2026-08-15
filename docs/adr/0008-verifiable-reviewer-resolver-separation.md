# ADR-0008 — Verifiable Reviewer/Resolver Separation

Status: Proposed pending CHG-0008 Strict Review

## Context

C-026 and Protocol Specification §25 previously described Reviewer and Resolver as distinct conceptual Roles, but Forge stored no durable evidence identifying the review actor/session versus the resolver session. The Review Policy represented separation only as a boolean, and `forge validate` could not reject an explicitly same-session FULL review or an inconsistent claim of isolation backed by identical session references.

## Decision

Forge will represent Reviewer/Resolver execution evidence in `review.reviewer_identity` with required `actor_type`, `session_ref`, and `resolver_session_ref` fields. For `flow.current == full`, the Change schema requires the entire object structurally.

The Review Policy defines minimum separation by Flow: FAST permits `agent_same_session`; STANDARD requires at least `agent_isolated_session`; FULL requires `human`, with `agent_isolated_session` as an explicit fallback only when no human reviewer is available. FULL never accepts `agent_same_session`.

The hierarchy `agent_same_session` → `agent_isolated_session` → `human` represents increasing strength of **operational independence**. The intended benefit is reduced context contamination from the Resolver's own execution trail and reduced confirmation bias from reusing the same reasoning context. It is not a claim of **epistemic independence**. A fresh session of the same underlying model can still reproduce correlated model errors, shared blind spots, and systematic reasoning failures.

Structural JSON Schema validation owns presence and type constraints for FULL reviewer identity evidence. Semantic CLI validation owns C-026 consistency checks: FULL rejects `agent_same_session`, and a claimed independent actor with identical `session_ref` and `resolver_session_ref` is rejected as inconsistent evidence.

Codex STANDARD/FULL projections instruct the harness not to conduct Strict Review in the Resolver session, to open or use an isolated review execution context, and to record a Reviewer `session_ref` distinct from the Resolver `resolver_session_ref`.

## Limits

This mechanism improves inspectability and operational separation. It does not prove that a review is correct, independent in the epistemic sense, or free from correlated model failure. The mechanism must not be presented as solving those stronger problems.

`agent_different_model` is future work only and is not introduced by CHG-0008.

## Compatibility conflict and its resolution

An earlier revision of this decision would have made every FULL `forge/change@1` instance
require `reviewer_identity`, a breaking schema change: historical FULL manifests valid under
that same schema identifier would become invalid without retroactive mutation, conflicting
with Protocol 1 C-045/C-046, while CHG-0008's own non-goals forbid rewriting completed
historical Changes.

This is resolved without a Protocol version bump, using the schema-versioning mechanism
`protocol/compatibility.md` already defines: the requirement lives only under a new artifact
schema suffix, `forge/change@2`. `forge/change@1` is restored to its original, backward
compatible shape. No historical Change, and no other in-flight Change, is forced onto the new
requirement; a Change adopts `forge/change@2` when it is ready to truthfully record reviewer
identity. CHG-0008's own manifest stays on `forge/change@1` until its own Strict Review
actually happens — recording identity before that would be self-certification, which INV-002
forbids regardless of how the schema is versioned.

This was resolved by a second Resolver-role pass, not by the independent Reviewer session this
Change requires. It is disclosed here as such and remains subject to that Review.

## Consequences

Reviewer/Resolver separation becomes inspectable and partially machine-enforceable. FULL same-session review and inconsistent identical-session claims become deterministic C-026 validation failures once structurally valid evidence is present. Review identity becomes durable repository evidence. The change increases confidence against context contamination while leaving epistemic independence explicitly out of scope.
