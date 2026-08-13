---
forge:
  artifact: plan
  schema: 1
change: CHG-0007
status: approved
---

# Plan — Protocol v1 Contract Freeze

## Phase 1 — Machine-readable contract

Drive a catalog-closure test from RED to GREEN, add schemas for Flow, Policy,
and TDD evidence, and require Adapter interval ordering at schema level.

## Phase 2 — Repository consistency

Extend the contract test to canonical instances, observe the known structural
RED, and mechanically migrate the five manifests and CHG-0004 traceability.

## Phase 3 — Stable version and compatibility

Drive the CLI label from `1-draft` to `1` through RED/GREEN. Publish explicit
compatibility, breaking-change, and deprecation rules; reconcile canonical
documentation and RFC status.

## Phase 4 — Verification and Strict Review

Run focused and full tests, schema audit, diff checks, and isolated-wheel
validation. Review all normative surfaces adversarially and remediate blocking
findings with regression-first TDD where behavioral.

## Phase 5 — Knowledge and Completion

Capture durable versioning/migration decisions, update roadmap status only
after evidence exists, reconcile active external review threads, and mark the
Change complete only when every FULL Gate passes.
