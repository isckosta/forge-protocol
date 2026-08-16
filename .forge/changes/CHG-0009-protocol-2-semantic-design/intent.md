---
forge:
  artifact: intent
  schema: 1
change: CHG-0009
status: complete
---

# Intent — Protocol 2 Semantic Design and Compatibility Boundary

## Problem

The Forge Engineering Contract has thirteen proposed conceptual guarantees, labelled C-047 through C-059, covering evidence, subject binding, revision-bound Gates, invalidation, authority, scope, assumptions, reversibility, and engineering confidence. These proposals are not canonical.

The repository has evolved since this Change was originally framed: Protocol 2 now formally exists, introduced by CHG-0008 for verifiable Strict Review independence, revision-bound review provenance, and `forge/change@2`. Therefore this Change must not pretend that Protocol 2 is unallocated or overwrite its published meaning.

## Goal

Establish a normative compatibility framework that determines, with repository evidence, which proposed guarantees are clarifications or compatible maintenance, which already belong to Protocol 2, and which would introduce new mandatory semantics requiring a later integer Protocol boundary.

## Required outcomes

1. Preserve Protocol 1 historical meaning and previously conforming instances.
2. Preserve Protocol 2 published review-independence meaning and previously conforming Protocol 2 instances.
3. Classify each proposed C-047 through C-059 concept using explicit compatibility categories.
4. Produce an operational interpretation of C-045 and C-046 that future Changes can apply deterministically.
5. Analyze evidence, provenance, subject binding, Gate revision binding, mutation invalidation, authority precedence, scope, assumptions, unknowns, reversibility, and engineering confidence.
6. Determine whether each concept belongs in Contract, Specification, Policy, schema, template, or a future Protocol version.
7. Produce candidate architecture and migration principles without implementing new lifecycle semantics.
8. Define follow-up work using placeholder identifiers only.

## Non-goals

- No reinterpretation of Protocol 1.
- No silent expansion of Protocol 2 obligations.
- No complete Evidence Model implementation.
- No Gate invalidation engine.
- No migration CLI.
- No mass Flow or schema rewrite.
- No fabricated historical provenance.
- No provider-specific or hosted Forge dependency.
- No reservation of future Change identifiers.

## Classification

The requested `architecture` Change kind is not part of canonical Protocol 1. This Change uses `feature`, matching prior protocol-semantic evolution Changes, because the work defines future Core behavior and compatibility semantics rather than merely documenting an existing architecture.

## Flow

FULL. The Change affects compatibility reasoning, canonical Protocol boundaries, future schema and lifecycle design, Adapter compatibility, and migration safety.

## Base revision

Analysis base: `70841bd77bd0128c48deda73b24708c3e5e3c461` on `main`.
