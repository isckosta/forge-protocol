---
forge:
  artifact: architecture
  schema: 1
change: CHG-0001
status: approved
---

# Architecture — Bootstrap Forge CLI

## Objective

Implement a small deterministic Python CLI for Forge infrastructure without creating a Forge workflow runtime.

## Initial package layout

```text
src/forge/
    cli/
    application/
    configuration/
    validation/
    workspace/
    git/
    resources/

tests/
    unit/
    integration/
    fixtures/
```

## CLI layer

Typer command definitions. Responsibilities: parse input, invoke application behavior, render results, and map failures to exit codes. Business rules do not belong in command functions.

## Application layer

Coordinates CLI use cases. Initial responsibilities: `InitializeForgeProject`, `ValidateForgeProject`, `DiagnoseForgeProject`, and `GetForgeVersion`.

## Workspace boundary

Responsible for repository location, `.forge/` location, workspace state, and project resources.

## Configuration boundary

Responsible for YAML loading, structured configuration, Protocol compatibility, and Schema validation integration. Pydantic models may support Implementation but do not replace canonical JSON Schemas.

## Protocol resolution

The installed Forge distribution provides canonical Protocol resources for Protocol versions supported by the CLI.

A project does not own a private authoritative copy of canonical Flow definitions.

Project configuration references canonical concepts by stable identifiers.

Conceptually:

```text
Installed Protocol
    ↓
Canonical Flow
    ↓
Project Flow Configuration
    ↓
Effective Flow
```

Contract resolution is:

```text
Canonical Engineering Contract
+
Project Engineering Contract
=
Effective Engineering Contract
```

Project configuration cannot weaken canonical Contract invariants.

## Validation boundary

Validation returns structured Findings independent from terminal rendering.

```text
ValidationFinding
    code
    severity
    artifact
    message
    path
    location?
```

## Git boundary

Git behavior remains isolated. Use `git` through subprocess argument arrays where needed. The Forge Project Root is resolved from Git's top-level directory.

## Testability

Architecture MUST allow application behavior to be tested without relying on terminal rendering internals. Filesystem-dependent behavior should accept explicit project paths where appropriate. Validation rules should remain independently executable. External process execution should remain isolated enough to permit deterministic tests.

## Initialization

`forge init` resolves the Git Project Root, inspects current state, rejects unsafe overwrite, creates the baseline workspace using rollback-safe behavior, creates project configuration, makes canonical Flows and Contract discoverable through Protocol resolution, validates generated state, and reports the result.

## Validation

`forge validate` locates the workspace, loads configuration, validates Schema and Protocol compatibility, validates canonical Flow references and Contract availability, aggregates Findings, and produces deterministic status.

## Doctor

Doctor is read-only and may inspect Git availability, Git repository state, Forge initialization, Schema, Protocol compatibility, canonical Flow availability, and Contract availability.

## Error model

Expected failures use structured application errors such as `ForgeAlreadyInitialized`, `ForgeNotInitialized`, `NotGitRepository`, `InvalidForgeConfiguration`, `UnsupportedProtocolVersion`, and `GitUnavailable`.

## Security

No remote requests. No secrets. Avoid shell interpretation.

## Future compatibility

Architecture may later support `configure`, `update`, `migrate`, Adapter installation, and Conformance validation. They are not part of CHG-0001.
