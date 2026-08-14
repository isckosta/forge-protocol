# ADR-0008 — Verifiable Reviewer/Resolver Separation

Status: Proposed pending CHG-0008 Strict Review

## Context

C-026 and Protocol Specification §25 previously described Reviewer and Resolver as distinct conceptual Roles, but Forge stored no durable evidence identifying the review actor/session versus the resolver session. The Review Policy represented separation only as a boolean, and `forge validate` could not reject an explicitly same-session FULL review.

## Decision

Forge will represent Reviewer/Resolver execution evidence in `review.reviewer_identity` with `actor_type`, `session_ref`, and `resolver_session_ref`.

The Review Policy defines minimum separation by Flow: FAST permits `agent_same_session`; STANDARD requires at least `agent_isolated_session`; FULL prefers `human` and permits `agent_isolated_session` only as an explicit fallback when no human reviewer is available. FULL forbids `agent_same_session`.

For active FULL review execution, the Change schema requires reviewer identity evidence. Pending reviews do not fabricate identity evidence, and already-completed historical Changes remain readable without retroactive mutation. `forge validate` independently rejects a FULL manifest that records `agent_same_session`, naming C-026.

Codex STANDARD/FULL projections instruct the harness not to conduct Strict Review in the Resolver session and to record Reviewer and Resolver session references.

## Limits

An isolated session of the same underlying model reduces context contamination from the Resolver transcript and implementation path. It does not eliminate correlated model bias, shared training-data blind spots, shared prompting failure modes, or systematic reasoning errors. This decision must not be presented as model independence.

`agent_different_model` is future work only and is not introduced by CHG-0008.

## Compatibility

This is a breaking schema/policy evolution for active FULL review execution. Protocol 1 C-045/C-046 also constrain revisions that invalidate previously valid Protocol 1 instances. CHG-0008 therefore preserves completed historical manifests and records the prospective enforcement boundary explicitly rather than rewriting historical evidence. Independent Strict Review must verify that this compatibility treatment is acceptable before the Change can complete.

## Consequences

Reviewer/Resolver separation becomes inspectable and partially machine-enforceable. FULL same-session review becomes a deterministic validation failure. Review identity becomes durable repository evidence. The mechanism raises confidence against context contamination but does not provide proof of epistemic independence.
