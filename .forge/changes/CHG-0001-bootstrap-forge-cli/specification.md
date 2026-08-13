---
forge:
  artifact: specification
  schema: 1
change: CHG-0001
status: approved
review:
  iterations: 2
  findings_resolved: 7
---

# Specification — Bootstrap Forge CLI

## 1. Objective

Provide the first deterministic Forge CLI responsible exclusively for Forge installation, initialization, validation, diagnostics, and version reporting.

The CLI is infrastructure for the Forge Protocol. It is not the Forge development workflow runtime.

## 2. Project Model

### FR-001 — Git repository requirement
Forge v1 MUST operate on Git repositories. A Forge Project MUST have a resolvable Git repository root.

### FR-002 — Project Root
The Forge Project Root MUST be the top-level directory returned by Git for the current repository. Commands executed from nested repository directories MUST resolve to the same Forge Project Root.

## 3. Version

### FR-003 — Version command
Forge MUST provide `forge version`. The command MUST report Forge CLI version and highest supported Forge Protocol version.

## 4. Initialization

### FR-004 — Init command
Forge MUST provide `forge init`.

### FR-005 — Workspace creation
Given a valid Git repository that is not Forge-enabled, `forge init` MUST create `.forge/` at the Forge Project Root.

### FR-006 — Nested execution
When `forge init` is executed from a nested directory, `.forge/` MUST be created at the Git repository root.

### FR-007 — No silent overwrite
When `.forge/` already exists, `forge init` MUST NOT silently overwrite it.

### FR-008 — Atomic initialization
A failed initialization MUST NOT leave a workspace that appears successfully initialized. The Implementation SHOULD use staging or equivalent rollback-safe behavior.

### FR-009 — Project configuration
Successful initialization MUST create `.forge/forge.yml` conforming to the supported Forge Project Schema.

## 5. Canonical Protocol Resolution

### FR-010 — Protocol reference
Project configuration MUST identify the Forge Protocol version used by the project.

### FR-011 — Canonical Flow resolution
Project Flow configuration MUST reference canonical Flows by identifier: `fast`, `standard`, `full`. Canonical Flow definitions MUST NOT be duplicated into the project as authoritative definitions.

### FR-012 — Project Flow configuration
Project-specific Flow configuration MAY strengthen or configure behavior where the canonical Protocol permits it. It MUST NOT weaken canonical Contract requirements.

## 6. Contract Resolution

### FR-013 — Canonical Contract
Every Forge Project MUST operate under the canonical Forge Engineering Contract for its configured Protocol version.

### FR-014 — Project Contract extension
A project MAY define additional engineering rules in `.forge/contract/engineering.md`.

### FR-015 — Effective Contract
The Effective Engineering Contract MUST consist of Canonical Engineering Contract plus Project Engineering Contract. Project rules MAY strengthen canonical requirements and MUST NOT weaken them.

## 7. Validation

### FR-016 — Validate command
Forge MUST provide `forge validate`.

### FR-017 — Initialization validation
When Forge is not initialized, `forge validate` MUST fail with `E_FORGE_NOT_INITIALIZED`.

### FR-018 — Project Schema validation
`forge validate` MUST validate `.forge/forge.yml` against the supported Forge Project Schema.

### FR-019 — Protocol compatibility
`forge validate` MUST reject a configured Protocol version unsupported by the installed CLI.

### FR-020 — Flow validation
Validation MUST reject unknown canonical Flow identifiers.

### FR-021 — Contract validation
Validation MUST confirm that the canonical Engineering Contract required by the configured Protocol version is available.

### FR-022 — Actionable Findings
Validation failures MUST identify error code, affected Artifact or subsystem, problem, relevant path when available, and an actionable message.

### FR-023 — Deterministic validation
Given identical repository state and Forge CLI version, validation results MUST be deterministic.

## 8. Doctor

### FR-024 — Doctor command
Forge MUST provide `forge doctor`.

### FR-025 — Doctor checks
Doctor MUST inspect at least Git availability, Git repository detection, Forge initialization, Project Schema validity, Protocol compatibility, canonical Flow availability, and canonical Contract availability.

### FR-026 — Doctor aggregation
Doctor MUST evaluate all reasonably executable diagnostic checks rather than stop after the first failure. Dependent checks MAY be marked skipped when a prerequisite prevents execution.

### FR-027 — Doctor read-only invariant
`forge doctor` MUST NOT modify repository state.

## 9. CLI Boundary

### FR-028 — No lifecycle execution commands
The Forge CLI MUST NOT expose canonical development lifecycle commands such as `change`, `specify`, `test-design`, `implement`, `verify`, `review`, `resolve`, or `complete`.

## 10. Exit Codes

### FR-029 — Success
Successful commands MUST exit with `0`.

### FR-030 — Invalid Forge state
Commands failing because the Forge project is missing or invalid SHOULD exit with `2`.

### FR-031 — Environment failure
Commands unable to operate because a required environment capability is missing SHOULD exit with `3`.

### FR-032 — Unexpected internal failure
Unexpected internal failures SHOULD exit with a non-zero code distinct from normal validation failures.

## 11. Non-Functional Requirements

- NFR-001: Forge CLI MUST support Python 3.12 or newer.
- NFR-002: Initial commands MUST operate without network access.
- NFR-003: Filesystem behavior MUST use platform-independent path handling.
- NFR-004: CLI output SHOULD be concise and actionable.
- NFR-005: Validation and diagnostic results SHOULD exist as structured application data independent from terminal rendering.
- NFR-006: Architecture MUST allow deterministic testing of CLI behavior without network access.

## 12. Constraints

- CON-001: No LLM SDK dependency.
- CON-002: No database dependency.
- CON-003: No Forge account.
- CON-004: No Forge-hosted service dependency.
- CON-005: No hidden Protocol download required for the initial Core commands.

## 13. Invariants

- INV-001: Forge Protocol remains independent from CLI Implementation.
- INV-002: CLI is not the development workflow runtime.
- INV-003: Initialization MUST preserve existing repository content.
- INV-004: Project configuration cannot weaken the canonical Engineering Contract.
- INV-005: Harness-specific behavior cannot redefine canonical Forge semantics.

## 14. Acceptance Scenarios

### AC-001 — Initialize from repository root
Given a non-Forge Git repository, when `forge init` runs, `.forge/` is created at the repository root and generated configuration is valid.

### AC-002 — Initialize from nested directory
Given a nested directory inside a non-Forge Git repository, when `forge init` runs, `.forge/` is created at the Git repository root.

### AC-003 — Reject non-Git directory
Given a directory outside a Git repository, when `forge init` runs, initialization fails and no `.forge/` workspace is created.

### AC-004 — Preserve existing Forge workspace
Given an existing `.forge/`, when `forge init` runs, initialization fails and existing files remain unchanged.

### AC-005 — Validate valid workspace
Given a valid Forge workspace, when `forge validate` runs, validation succeeds with exit code 0.

### AC-006 — Reject missing workspace
Given a Git repository without `.forge/`, when `forge validate` runs, validation reports `E_FORGE_NOT_INITIALIZED` and exits non-zero.

### AC-007 — Reject invalid project configuration
Given an invalid `.forge/forge.yml`, when `forge validate` runs, validation reports actionable structured Findings.

### AC-008 — Detect unsupported Protocol
Given a project configured with an unsupported Forge Protocol, when validation runs, validation fails explicitly.

### AC-009 — Doctor is read-only
Given any diagnosable repository state, when `forge doctor` runs, repository contents remain unchanged.

### AC-010 — Doctor aggregates failures
Given multiple Forge environment problems, when `forge doctor` runs, all reasonably executable checks are reported.

### AC-011 — CLI remains infrastructure-only
Given the installed Forge CLI, when available commands are inspected, Forge development lifecycle commands are absent.
