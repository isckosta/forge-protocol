---
forge:
  artifact: specification
  schema: 1
change: CHG-0008
status: complete
---

# Specification — Verifiable Review Independence

This specification incorporates the accepted drift recorded in `specification-drift.md`. The earlier session-strength hierarchy is superseded by provider-independent Execution and Execution Context evidence.

## Functional requirements

### FR-001 — Review identity schema
`review.reviewer_identity` MUST be a closed object containing required `actor_type`, `execution_id`, `context_id`, `resolver_execution_id`, and `resolver_context_id`. `actor_type` MUST permit only `human` or `agent`; all identifiers MUST be non-empty strings.

### FR-002 — FULL identity evidence
For `schema: forge/change@2` with `flow.current == full`, JSON Schema MUST require the entire `reviewer_identity` object. `forge/change@1` MUST remain backward compatible and MUST NOT retroactively require it.

### FR-003 — Execution independence
Strict Review MUST NOT share `execution_id` with the Implementation or Resolution being reviewed. `forge validate` MUST reject equality with C-026.

### FR-004 — Context independence
Strict Review MUST NOT share `context_id` with the Implementation or Resolution being reviewed. `forge validate` MUST reject equality with C-026 even when execution IDs differ.

### FR-005 — Role switching is not independence
Canonical Contract and Specification MUST state that changing Role inside the same Execution or transient conversational/reasoning context is self-review and MUST NOT satisfy Strict Review.

### FR-006 — Resolution boundary
A Resolver MUST NOT resolve blocking Findings in the Reviewer's Execution Context.

### FR-007 — Independent re-review
After blocking Findings are resolved, `review_passed` MUST require a re-review Execution and Context distinct from the Resolution Execution and Context. The same Reviewer actor MAY perform re-review in a new compliant context.

### FR-008 — Self-review semantics
Self-review MAY occur in an Implementation or Resolution context but MUST NOT satisfy the Strict Review Gate.

### FR-009 — Provider independence
The same Harness, provider, model, or agent implementation MAY perform multiple Roles when required execution/context boundaries are real and durably evidenced. Core terminology MUST be `execution_id` and `context_id`, not Harness-specific session terminology.

### FR-010 — Review Policy
Canonical Review Policy MUST require execution-context independence for FAST, STANDARD, and FULL; forbid shared execution and shared context; state that Role switching is not independence; state that self-review does not satisfy Strict Review; and require re-review independent from Resolution after blocking findings.

### FR-011 — Codex projection
STANDARD and FULL Codex projection MUST instruct the harness to use an independent Review Execution and Context, record the four execution/context identifiers, reject Role switching in the same conversation, and require independent re-review after blocking resolution.

### FR-012 — Structural/semantic separation
JSON Schema MUST own evidence shape and presence. CLI validation MUST own semantic equality checks. The structural execution-context fixture MUST become valid before semantic C-026 tests can pass.

### FR-013 — Decision documentation
ADR-0008 MUST document context contamination, the human PR analogy, provider-independent execution/context boundaries, and the limitation that isolated executions do not guarantee epistemic independence.

### FR-014 — Historical preservation
Completed historical Changes MUST NOT be retroactively modified or assigned fabricated review identity evidence.

### FR-015 — Completion safety
Protocol Completion rules MUST block Completion when required Review independence cannot be demonstrated from repository-native evidence.

## Invariants

### INV-001 — No fabricated independence
Execution/context identifiers MUST describe real review and implementation/resolution executions. They MUST NOT be invented merely to satisfy validation.

### INV-002 — No self-certification
The Resolver execution for CHG-0008 MUST NOT perform or certify the Change's final Strict Review.

### INV-003 — Repository authority
Durable review independence evidence MUST live in repository-native Change state; transient chat history is not authoritative evidence.

## Acceptance criteria

- AC-001: the execution-context fixture is structurally valid against `forge/change@2`.
- AC-002: distinct executions sharing one context fail `forge validate` with C-026.
- AC-003: one execution with superficially distinct context IDs fails `forge validate` with C-026.
- AC-004: distinct Reviewer/Resolver executions and contexts pass the semantic C-026 validator.
- AC-005: FULL `forge/change@2` without `reviewer_identity` fails structural validation; FULL `forge/change@1` without it remains valid.
- AC-006: Review Policy validates against its policy schema with execution-context independence semantics.
- AC-007: STANDARD/FULL Codex projection contains the independent execution/context and re-review rules.
- AC-008: Contract §C-026, Specification §§22/25/27, ADR-0008, and CHG-0008 artifacts agree on the invariant.
- AC-009: no historical completed Change is modified.
- AC-010: full test suite and distribution verification pass before handoff to an independent Strict Reviewer.
- AC-011: `review.md` remains absent and CHG-0008 remains incomplete until a genuinely independent Review Execution occurs.
