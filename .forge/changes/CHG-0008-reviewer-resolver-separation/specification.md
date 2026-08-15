---
forge:
  artifact: specification
  schema: 1
change: CHG-0008
status: complete
---

# Specification — Verifiable Reviewer/Resolver Separation

## Functional requirements

### FR-001 — Reviewer identity schema
The Change schema MUST define `review.reviewer_identity` as a closed object containing required `actor_type`, `session_ref`, and `resolver_session_ref`. `actor_type` MUST be a string permitting only `human`, `agent_isolated_session`, and `agent_same_session`; both session references MUST be non-empty strings.

### FR-002 — FULL identity evidence
Whenever `flow.current == full`, JSON Schema MUST structurally require the entire `reviewer_identity` object, using the schema's existing `if`/`then` conditional pattern. A missing or partial object MUST fail structural validation.

### FR-003 — Per-Flow policy
Review Policy MUST define FAST minimum `agent_same_session`, STANDARD minimum `agent_isolated_session`, FULL minimum `human`, FULL fallback `agent_isolated_session` when no human reviewer is available, and FULL prohibition of `agent_same_session`.

### FR-004 — Canonical C-026
C-026 MUST require Reviewer and Resolver to remain distinct Roles backed by recorded, verifiable evidence of independent execution rather than assertion alone. Evidence strength MUST be Flow-proportional and policy-defined, and `review_passed` MUST NOT be asserted when evidence is below the active Flow minimum.

### FR-005 — Specification alignment
Protocol Specification §25 MUST describe the same role separation, verifiable evidence, Flow-proportional strength, and prohibition on asserting passed Review with insufficient evidence.

### FR-006 — CLI same-session semantic validation
For any structurally valid Change with `flow.current == full` and `review.reviewer_identity.actor_type == agent_same_session`, `forge validate` MUST fail and name C-026.

### FR-007 — CLI inconsistent-session semantic validation
For any structurally valid FULL Change whose `actor_type != agent_same_session`, `forge validate` MUST fail and name C-026 when `session_ref == resolver_session_ref`, because identical references contradict the claimed operational independence.

### FR-008 — Structural/semantic layer separation
Tests and code comments MUST state that JSON Schema owns FULL identity presence/type checks while the CLI validator owns C-026 semantic consistency checks. The exact same-session RED fixture MUST pass structural schema validation before it is exercised through `forge validate`.

### FR-009 — Codex projection
STANDARD and FULL Codex projections MUST instruct execution to open or use an isolated review session (or human review surface where policy requires), record Reviewer and Resolver session references, and ensure `session_ref` is distinct from `resolver_session_ref`.

### FR-010 — Decision documentation
An ADR MUST state that `agent_same_session` → `agent_isolated_session` → `human` represents increasing operational independence through reduced context contamination and confirmation bias, not epistemic independence. It MUST state that a fresh session of the same model does not eliminate correlated model errors and MUST list `agent_different_model` as future work only.

### FR-011 — Breaking-change record
CHANGELOG MUST record the FULL reviewer identity requirement as a breaking schema change.

### FR-012 — Historical preservation
Completed historical Changes under `.forge/changes/` MUST NOT be retroactively modified by this Change.

## Invariants

### INV-001 — No historical evidence fabrication
Completed historical Changes MUST NOT be retroactively edited to invent reviewer identity.

### INV-002 — No self-certified independence
The Resolver session MUST NOT create `review.md`, claim independent Strict Review, or set `review.status: passed`.

### INV-003 — Repository authority
All durable evidence required for handoff MUST be stored in the repository rather than relying on chat history.

## Acceptance criteria

- AC-001: the exact FULL same-session RED fixture is structurally valid against `change.schema.json`.
- AC-002: the same fixture causes `forge validate` to fail with C-026 after semantic implementation.
- AC-003: a structurally valid `agent_isolated_session` fixture with identical reviewer/resolver references causes `forge validate` to fail with C-026.
- AC-004: a FULL manifest without `reviewer_identity`, including one with Review still pending, fails structural schema validation.
- AC-005: canonical Review Policy YAML validates against its policy schema.
- AC-006: STANDARD/FULL Codex projection output requires isolated review execution and distinct session references.
- AC-007: ADR and CHANGELOG accurately state the operational-independence limits and breaking nature of the schema change.
- AC-008: no completed historical Change is modified.
- AC-009: `review.md` is absent and Strict Review remains pending for independent execution.
- AC-010: the complete canonical test suite and `forge validate` pass only if the revised schema requirement can coexist with Protocol 1 compatibility obligations without fabricated evidence or historical rewrites.

## Known contract conflict (resolved)

FR-002 and FR-012 were originally simultaneously incompatible with Protocol 1 compatibility
invariants C-045/C-046 and the canonical test that validates every historical `forge/change@1`
manifest against the current schema: the literal FR-002 wording made the requirement apply to
every FULL manifest regardless of which schema suffix it declared, which retroactively
invalidated historical FULL Changes and, self-referentially, CHG-0008's own in-progress
manifest.

This is resolved per `protocol/compatibility.md`'s existing schema-versioning mechanism, which
was already canonical and did not require a Protocol version bump: `forge/change@1` is
restored to its original shape (the `reviewer_identity` property remains defined but optional,
which is compatible per compatibility.md's "optional fields... whose absence preserves
existing meaning"). A new schema suffix, `forge/change@2`, carries the structural requirement
that FULL manifests declare a complete `reviewer_identity` object regardless of review status.
FR-002 is amended to read: *"Whenever a Change manifest declares `schema: forge/change@2` and
`flow.current == full`, JSON Schema MUST structurally require the entire `reviewer_identity`
object."* No historical manifest declares `forge/change@2`, so none are retroactively
invalidated, satisfying FR-012/INV-001/AC-008 without fabricating evidence or weakening the
canonical compatibility test.

CHG-0008's own manifest remains on `forge/change@1` while its own Strict Review is pending —
it has not claimed compliance with the discipline it introduces, and it will only be truthful
to migrate to `forge/change@2` once a genuinely independent Reviewer session has executed and
recorded real `reviewer_identity` evidence (T-014). Migrating it preemptively to satisfy its
own new rule before that Review happens would itself violate INV-002.

AC-010 is satisfied: the full canonical test suite and `forge validate` pass
(`pytest -q` → 168 passed, 0 failed) without fabricated evidence or historical rewrites.
