---
forge:
  artifact: specification
  schema: 1
change: CHG-0059
status: pending
---

# CHG-0059 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0059 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

The Adapter projects the resolved Forge inputs into Copilot-native files under
`.github/` without changing canonical Forge state. Generic Adapter Core
continues to own publication safety and installation semantics.

## Classification

STANDARD is selected because the Change materially adds a packaged Adapter,
projection behavior, vendor capability evidence, hooks, and regression
coverage while preserving existing Protocol semantics.

## User Stories

User Stories are optional behavioral context. Include this section only when a meaningful actor, concrete capability, and outcome add information; otherwise remove it. Do not invent a persona to satisfy the template.

## Functional Requirements

Each requirement is an independent, verifiable contract. A Requirement without a User Story is valid.

### FR-001 · Package and register the Adapter
Priority: required

#### Requirement
The repository SHALL package a versioned `github-copilot` Adapter descriptor,
publication metadata, capability evidence, Driver, and registry entry.

#### Expected Behavior
The descriptor SHALL be loadable offline and compatible with Protocol 2.

#### Boundary
State an explicit limit only when the requirement needs one.

#### Acceptance
AC-001
Given the packaged registry
When the Adapter list is resolved
Then `github-copilot` is present with valid manifest and evidence.

### FR-002 · Project effective Forge workflow
Priority: required

#### Requirement
The Adapter SHALL project the effective Engineering Contract, Flows, canonical
references, and canonical Capabilities into Copilot Agent Skills under
`.github/skills/`.

#### Acceptance
AC-002
Given identical resolved Adapter inputs
When projection runs repeatedly or with reordered Flows
Then the artifacts, contents, and digests are identical and publication paths
remain within `.github/`.

### FR-003 · Provide a discovery pointer without duplicating authority
Priority: required

#### Requirement
The Adapter SHALL generate a minimal `.github/copilot-instructions.md` pointer
to the Forge skill and SHALL not copy the Contract or lifecycle rules into the
pointer.

#### Acceptance
AC-003
Given a generated Copilot repository
When `copilot-instructions.md` is inspected
Then it points to `.github/skills/forge/SKILL.md` and does not redefine Forge
workflow authority.

### FR-004 · Represent mechanical protection and limitations
Priority: required

#### Requirement
The Adapter SHALL publish a documented POSIX Copilot `preToolUse` hook for
review-control metadata and SHALL distinguish Linux/macOS CLI and cloud-agent
hook enforcement from Windows CLI, IDE/code-review surface limitations, and
Skill guidance.

#### Acceptance
AC-004
Given hook input for a protected metadata mutation
When the generated hook executes
Then it denies the mutation on the supported POSIX hook surfaces, while
read-only Git inspection remains allowed.

### FR-005 · Preserve Adapter Core semantics
Priority: required

#### Requirement
The Adapter SHALL use existing publication ownership, deterministic planning,
installation, drift, and Protocol compatibility abstractions without adding a
Copilot-specific Forge workflow model.

#### Acceptance
AC-005
Given the existing Adapter Core tests and generated projection
When targeted and distribution tests run
Then they pass without Core or Protocol changes.

## Non-functional Requirements

### NFR-001 · Offline deterministic evidence

Packaged evidence and projection generation SHALL work without fetching vendor
documentation at runtime.

## Constraints

- Do not duplicate canonical Forge state in Copilot-specific files.
- Do not claim Copilot capabilities are universal across surfaces.
- Do not add Copilot SDK dependencies to Forge Core.

## Traceability Matrix

| Requirement | Discovery | Acceptance |
|---|---|---|
| FR-001 | Existing Adapter boundary | AC-001 |
| FR-002 | Existing Adapter boundary | AC-002 |
| FR-003 | Authority and enforcement boundary | AC-003 |
| FR-004 | Copilot repository primitives | AC-004 |
| FR-005 | Existing Adapter boundary | AC-005 |

## Compatibility Statement

Protocol schemas and Forge Core semantics are unchanged. Existing Codex and
Claude Code registry behavior remains intact; the new Adapter is additive.

## Specification Gate

The requirements are independently verifiable, map to the implementation and
tests, preserve canonical authority, and state the documented Copilot surface
boundaries. The implementation predated this retrospective Change scaffold;
this record does not claim the gate authorized those earlier edits.

## Out of Scope

Separate Copilot adapters per surface, custom agents, MCP integration, Protocol
changes, and universal enforcement claims.
