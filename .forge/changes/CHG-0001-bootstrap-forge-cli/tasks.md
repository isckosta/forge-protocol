---
forge:
  artifact: tasks
  schema: 1
change: CHG-0001
status: draft
---

# Tasks — Bootstrap Forge CLI

## T-001 — Initialize Python test foundation
Requirements: NFR-001, NFR-006

Create package skeleton, Pytest configuration, CLI test harness, and packaging entrypoint configuration without behavioral production commands.

## T-002 — TDD `forge version`
Requirements: FR-003

RED: write and execute failing CLI behavior test. GREEN: implement minimum version command. REFACTOR only if justified.

## T-003 — TDD Git Project Root
Requirements: FR-001, FR-002, FR-006

Drive Git requirement, nested directory resolution, and Project Root behavior through tests.

## T-004 — TDD workspace state
Requirements: FR-004, FR-005, FR-007, FR-008

Drive Forge workspace detection, creation, overwrite protection, and rollback-safe behavior through tests.

## T-005 — TDD configuration model
Requirements: FR-009, FR-010, FR-018, FR-019, FR-023

Drive valid/invalid configuration and Protocol compatibility through tests.

## T-006 — TDD Protocol and Contract resolution
Requirements: FR-011, FR-012, FR-013, FR-014, FR-015, INV-004, INV-005

Drive canonical Flow references, project Flow configuration, canonical Contract availability, and project Contract extension behavior through tests.

## T-007 — TDD `forge init`
Requirements: FR-004..FR-015

Implement acceptance scenarios incrementally through valid TDD cycles.

## T-008 — TDD Validation Findings
Requirements: FR-016..FR-023

Create structured Validation Findings independent of terminal rendering.

## T-009 — TDD `forge validate`
Requirements: FR-016..FR-023, FR-029, FR-030

Implement public validation command and exit behavior after relevant RED evidence.

## T-010 — TDD diagnostic checks
Requirements: FR-024..FR-027

Drive each diagnostic behavior through tests.

## T-011 — TDD `forge doctor`
Requirements: FR-024..FR-027, FR-029..FR-032

Prove aggregation and read-only behavior.

## T-012 — Verify CLI scope
Requirements: FR-028, INV-002

Test that prohibited lifecycle commands are absent.

## T-013 — Add repository fixtures
Support non-Git directory, uninitialized Git repository, nested directory, valid Forge project, invalid configuration, existing workspace, and unsupported Protocol fixtures.

## T-014 — Installation smoke test
Requirements: FR-003, NFR-001

Verify package installation exposes `forge`.

## T-015 — Verify offline operation and dependencies
Requirements: NFR-002, CON-001..CON-005

Assert initial commands do not require network/account state and runtime dependencies include no LLM SDK or database.

## T-016 — Execute complete Verification
Verify all Requirements and Acceptance Scenarios.

## T-017 — Execute Strict Review
Review TDD compliance and final Implementation. Resolve blocking Findings and re-review.
