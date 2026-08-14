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
The Change schema MUST define `review.reviewer_identity` as a closed object containing required `actor_type`, `session_ref`, and `resolver_session_ref`. `actor_type` MUST permit only `human`, `agent_isolated_session`, and `agent_same_session`.

### FR-002 — FULL identity evidence
For an active, non-completed FULL Change whose Review is no longer pending, the schema MUST require `reviewer_identity`. A pending Strict Review MUST NOT be forced to fabricate reviewer evidence. Completed historical Changes MUST remain unmodified.

### FR-003 — Per-Flow policy
Review Policy MUST define FAST minimum `agent_same_session`, STANDARD minimum `agent_isolated_session`, FULL minimum `human`, FULL fallback `agent_isolated_session`, and FULL prohibition of `agent_same_session`.

### FR-004 — Canonical C-026
C-026 MUST require recorded execution evidence meeting active policy. FULL MUST NOT assert passed Review with non-compliant identity evidence.

### FR-005 — Specification alignment
Protocol Specification §25 MUST describe the same per-Flow separation semantics and evidence requirement.

### FR-006 — CLI semantic validation
For any Change with `flow.current == full` and `review.reviewer_identity.actor_type == agent_same_session`, `forge validate` MUST fail and name C-026.

### FR-007 — Codex projection
STANDARD and FULL Codex projections MUST instruct execution to use an isolated review session (or human surface where policy requires) and record Reviewer and Resolver session references.

### FR-008 — Decision documentation
An ADR MUST state that same-model isolated sessions reduce context contamination but do not eliminate correlated model bias, and MUST list `agent_different_model` as future work only.

### FR-009 — Breaking-change record
CHANGELOG MUST record the reviewer identity schema/policy evolution as breaking.

## Invariants

### INV-001 — No historical evidence fabrication
Completed historical Changes MUST NOT be retroactively edited to invent reviewer identity.

### INV-002 — No self-certified independence
The Resolver session MUST NOT create a `review.md` claiming independent Strict Review or set `review.status: passed`.

### INV-003 — Repository authority
All durable evidence required for handoff MUST be stored in the repository rather than relying on chat history.

## Acceptance criteria

- AC-001: the dedicated FULL same-session fixture causes CLI validation to fail with C-026.
- AC-002: the RED commit fails only because the validator still accepts the prohibited review identity.
- AC-003: after implementation, the full test suite passes.
- AC-004: canonical policy YAML validates against its policy schema.
- AC-005: completed historical Change manifests remain valid and unchanged.
- AC-006: STANDARD/FULL Codex projection output contains isolated-session and session-reference instructions.
- AC-007: Strict Review remains pending for external execution.
