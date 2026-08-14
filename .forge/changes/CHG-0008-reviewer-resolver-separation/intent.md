---
forge:
  artifact: intent
  schema: 1
change: CHG-0008
status: complete
---

# Intent — Verifiable Reviewer/Resolver Separation

## Problem

C-026 and Protocol Specification §25 require Reviewer and Resolver separation, but the requirement was only conceptual: Change manifests did not record Reviewer/Resolver execution identity, Review Policy stored a bare boolean, and `forge validate` could not enforce the FULL same-session prohibition.

## Goal

Make Reviewer/Resolver separation durable, policy-driven, and verifiable across schema, canonical prose, CLI validation, and the Codex projection without claiming stronger independence than isolated execution provides.

## Required outcomes

1. Record reviewer identity and reviewer/resolver session references in the Change schema.
2. Define per-Flow separation minimums and FULL fallback semantics in Review Policy.
3. Strengthen C-026 around recorded execution evidence.
4. Align Specification §25.
5. Reject FULL `agent_same_session` review in `forge validate`, with C-026, using TDD.
6. Project isolated-review instructions for STANDARD/FULL in Codex.
7. Record the architectural decision and its limitations in an ADR.
8. Record the schema evolution as breaking in CHANGELOG.

## Non-goals

- No `agent_different_model` actor type.
- No additional FAST/STANDARD ceremony outside the policy minimum and Codex projection instruction.
- No retroactive mutation of completed historical Changes.
- No self-certification of Strict Review by the Resolver session.

## Flow

FULL. The Change modifies canonical Protocol semantics, schema, policy, CLI validation behavior, and a Harness Adapter projection.

## Completion constraint

Strict Review must be performed by a genuinely separate reviewer execution. This Resolver session leaves `review.status: pending` and does not create `review.md`.
