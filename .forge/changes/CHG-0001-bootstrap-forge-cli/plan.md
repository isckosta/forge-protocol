---
forge:
  artifact: plan
  schema: 1
change: CHG-0001
status: draft
---

# Plan — Bootstrap Forge CLI

## Phase 1 — Python test foundation
Create Python 3.12+ package skeleton, executable packaging configuration, Pytest infrastructure, and CLI test harness. Do not implement behavioral CLI commands yet.

## Phase 2 — First RED: `forge version`
Write the public CLI behavior test, execute it, confirm valid RED, then implement the minimum GREEN and refactor only afterward.

## Phase 3 — Git Project Root
Drive Git availability, repository detection, top-level resolution, and nested execution through focused TDD cycles.

## Phase 4 — Workspace model
Drive `.forge/` presence, non-destructive initialization, and rollback-safe behavior through tests.

## Phase 5 — Configuration and Protocol resolution
Drive Project Schema loading, Protocol compatibility, canonical Flow references, and Effective Contract discoverability through TDD.

## Phase 6 — `forge init`
Implement acceptance scenarios incrementally through RED -> GREEN -> REFACTOR.

## Phase 7 — `forge validate`
Develop validation behavior through failing fixtures and focused RED cycles.

## Phase 8 — `forge doctor`
Develop diagnostics through read-only integration tests and aggregated check behavior.

## Phase 9 — Verification
Run the full suite, installation smoke test, dependency inspection, offline checks, generated workspace validation, and configured static checks.

## Phase 10 — Strict Review
Review Specification, TDD evidence, Architecture, Implementation, tests, Verification evidence, CLI boundary, and Documentation. Resolve blocking Findings and re-review.

## Phase 11 — Documentation and Knowledge
Document installation and commands, and update durable Architecture knowledge if Implementation changes a material decision.
