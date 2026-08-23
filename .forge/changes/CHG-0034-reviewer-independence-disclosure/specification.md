---
forge:
  artifact: specification
  schema: 1
change: CHG-0034
status: pending
---

# Specification — CHG-0034 Reviewer Independence Disclosure

## Summary

Define a durable, non-normative disclosure of the actual evidence boundary
of Protocol 2 Reviewer independence: distinct Execution and Execution Context,
not vendor/model diversity.

## Classification

STANDARD — the Change updates the canonical Contract and contributor-facing
roadmap/documentation, requiring Discovery, Specification, Plan, Verification,
Strict Review, and Documentation. It does not introduce executable behavior,
change a Gate, alter persistence, or change the normative requirements of
C-026 or C-037. It is therefore not FULL and is not a FAST copy correction.

## Functional Requirements

## FR-001 — Disclose the independence boundary

The canonical Contract MUST state that the verifiable Reviewer independence
guarantee is at the Execution and Execution Context level. It MUST state that
this does not establish independence of AI vendor, model, or provider for a
particular review.

## FR-002 — Preserve existing semantics

The Change MUST NOT change the normative requirements of C-026 or C-037,
introduce a vendor/model selection requirement, or weaken the requirement for
an adversarial Strict Review with distinct Reviewer/Resolver Roles.

## FR-003 — Keep the disclosure consistent

Harness-facing projections and contributor documentation MUST not imply a
stronger vendor/model independence guarantee than the canonical Contract.

## FR-004 — Correct remediation roadmap state

`ROADMAP-REMEDIATION.md` MUST identify items #1 through #9 as complete, item
#10 as the active next item, and CHG-0034 as its repository-native Change.

## Acceptance Criteria

## AC-001 — Contract wording is explicit

The Contract contains the execution/context guarantee and the vendor/model
limitation, and existing C-026/C-037 normative text remains unchanged in
meaning.

## AC-002 — No RFC is required for this scope

Discovery records evidence that this is a non-material clarification. If
implementation would add a new review obligation or alter Review semantics,
the Change is stopped and escalated to an RFC instead.

## AC-003 — Projections remain honest

Relevant Adapter projections and contributor docs are inspected and updated
only where their wording would otherwise overstate the guarantee.

## AC-004 — Roadmap is current

The remediation status/sequencing note points to CHG-0034 and no longer
claims item #2 or CHG-0024 is next.

## AC-005 — Repository validation passes

`forge validate` passes, Verification records the documentation-only test
exception, and an independent Strict Review passes against the frozen subject.

## Out of Scope

- Implementing hint-free review mode.
- Selecting or requiring a different vendor, model, or Harness for Review.
- Changing Protocol identifiers, Flows, Gates, provenance schema, or review
  lifecycle semantics.
- Remediation items #2 through #9.
