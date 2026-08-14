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

## Compatibility conflict requiring independent review

The revised requirement that every FULL `forge/change@1` instance contain `reviewer_identity` is a breaking schema change: historical FULL manifests that were valid under the same schema identifier become invalid without retroactive mutation. That conflicts with Protocol 1 C-045/C-046, while CHG-0008's non-goals also forbid rewriting completed historical Changes.

The Resolver therefore does not fabricate reviewer evidence, rewrite historical Changes, weaken canonical contract tests, or claim this compatibility conflict is resolved. Independent Strict Review must decide whether the requirement needs a new schema/Protocol version or another explicitly governed migration boundary before CHG-0008 can complete.

## Consequences

Reviewer/Resolver separation becomes inspectable and partially machine-enforceable. FULL same-session review and inconsistent identical-session claims become deterministic C-026 validation failures once structurally valid evidence is present. Review identity becomes durable repository evidence. The change increases confidence against context contamination while leaving epistemic independence explicitly out of scope.
