# Specification — CHG-0006

Status: approved after adversarial Specification Review Iteration 1.

## Functional Requirements

### FR-001 — Explicit blocking-thread projection

When `before_completion.require` contains `blocking_review_threads_resolved`, generated Codex workflow instructions MUST explicitly state that Completion requires all blocking review threads on any active external review surface to be resolved.

### FR-002 — Conditional projection

When the canonical Flow omits `blocking_review_threads_resolved`, the Codex Adapter MUST NOT invent that instruction.

### FR-003 — Durable guidance alignment

The canonical Engineering Contract and project Architecture documentation MUST describe the same external-review reconciliation invariant as the Core Protocol without assigning external-review execution to the CLI or Adapter.

### FR-004 — Honest remediation evidence

CHG-0006 MUST record complete, temporally valid RED/GREEN evidence for its own behavioral change. CHG-0005 workflow evidence MAY be cited as historical context but MUST NOT be represented as a CHG-0006 TDD cycle.

## Constraints

- CON-001: CHG-0005 Git history and artifacts remain unchanged.
- CON-002: The raw canonical Flow remains authoritative and included in the projection.
- CON-003: Projection remains deterministic and explicitly non-enforcing.
- CON-004: No GitHub API, provider-specific review model, or CLI lifecycle executor is introduced.

## Acceptance Criteria

### AC-001 — Required Gate is explicit

Given a Flow whose Completion requirements include `blocking_review_threads_resolved`, when the Codex projection is generated, then the Harness instruction section explicitly requires resolution of all blocking threads on any active external review surface.

### AC-002 — Requirement is not invented

Given a Flow without `blocking_review_threads_resolved`, when the Codex projection is generated, then no blocking-review-thread Completion instruction is emitted.

### AC-003 — Contract and Architecture agree

Given the completed Change, when maintainers inspect the Core Protocol, Engineering Contract, and Architecture documentation, then each describes blocking external review threads as a Completion blocker while preserving repository and process authority boundaries.

### AC-004 — Evidence is attributable

Given final CHG-0006 TDD evidence, when a reviewer follows its commits and workflow runs, then the CHG-0006 regression is demonstrably RED before GREEN and CHG-0005 evidence is clearly identified only as prior history.
