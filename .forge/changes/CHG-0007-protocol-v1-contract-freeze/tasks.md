---
forge:
  artifact: tasks
  schema: 1
change: CHG-0007
status: approved
---

# Tasks — Protocol v1 Contract Freeze

## T-001 — Establish FULL Change artifacts

Requirements: all

Record Intent, Discovery, Specification, adversarial Specification Review,
Architecture, Test Strategy, Plan, Tasks, and initial traceability/evidence.

## T-002 — TDD schema catalog closure

Requirements: FR-002, FR-007, FR-008, FR-010, NFR-001, INV-001

Create the contract test first, observe missing-catalog RED, then add the
catalog and Flow, Policy, and TDD-evidence schemas. Tighten Adapter interval
field bounds, retain semantic cross-field ordering validation, and prove
catalog identity/file closure.

## T-003 — TDD canonical-instance audit and migration

Requirements: FR-009, FR-013, NFR-001, INV-002

Extend the contract test, observe schema drift RED, then mechanically migrate
manifests and CHG-0004 traceability without changing historical facts.

## T-004 — TDD stable Protocol label

Requirements: FR-001, FR-002, INV-001

Change the CLI expectation first, observe `1-draft`, then set the display label
to `1` while preserving integer compatibility.

## T-005 — Freeze compatibility and lifecycle documentation

Requirements: FR-003..FR-006, FR-011, FR-012

Publish compatibility/deprecation policy and reconcile Specification, Contract,
Flows, README, Architecture, Changelog, and RFC-0001.

## T-006 — Verification

Requirements: all

Verify tests, schemas, requirements, historical integrity, and isolated-wheel
behavior; record exact commands and results.

## T-007 — Strict Review and remediation

Requirements: all

Review adversarially, resolve blocker/major findings, and re-review resolutions.

## T-008 — Documentation, Knowledge Capture, and Completion

Requirements: all

Capture durable decisions, update roadmap status, reconcile active external
review threads, and complete only after all Gates pass.
