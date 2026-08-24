---
forge:
  artifact: specification
  schema: 1
change: CHG-0037
status: complete
---

# CHG-0037 · Specification

> **Change Contract**
>
> This Specification defines the layout and authoring guidance for readable, traceable Change Specifications. Requirements remain the authoritative, verifiable contract.

## Overview

| | |
|---|---|
| **Change** | CHG-0037 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

The scaffold SHALL generate a Specification with a compact Overview, optional User Stories, self-contained Requirements, nearby Acceptance content, separate NFRs and Constraints, a Compatibility Statement, a Specification Gate, and a Traceability Matrix index.

## Classification

This is a behavioral, documentation-and-scaffolding Change. It does not alter Protocol integers, Change Schemas, Gate semantics, or historical artifacts.

## User Stories

User Stories are optional behavioral context. A Story has a stable `US-xxx` identifier and may reference zero or more Discovery findings and one or more Requirements. A Requirement may reference multiple Stories or none.

Stories use actor, capability, and outcome prose and may contain non-executable Given/When/Then Acceptance Scenarios. No external BDD framework is required.

## Functional Requirements

### FR-001 · Traceable Specification scaffold

#### Requirement
The generated `specification.md` SHALL preserve the existing `forge:` front matter and emit stable English structural headings for Overview, User Stories, Functional Requirements, Non-functional Requirements, Constraints, Traceability Matrix, Compatibility Statement, and Specification Gate.

#### Expected Behavior
The template SHALL explain that User Stories are optional and SHALL NOT emit a fictitious Story by default.

#### Acceptance
AC-001 — Given a STANDARD scaffold, When `specification.md` is generated, Then the front matter and required structural headings are present and the legacy disconnected `Acceptance Criteria` scaffold is absent.

### FR-002 · Self-contained Requirements

#### Requirement
The generated Functional Requirement guidance SHALL support visible `Stories`, optional `Origin` and `Priority`, `Requirement`, optional `Expected Behavior` and `Boundary`, and nearby `Acceptance` content.

#### Acceptance
AC-002 — A generated Requirement template contains `#### Requirement` and `#### Acceptance` and does not require a User Story.

### FR-003 · Optional behavioral traceability

#### Requirement
The guidance SHALL support stable `US-xxx`, `FR-xxx`, `NFR-xxx`, `CON-xxx`, and `AC-xxx` identifiers and SHALL describe a Traceability Matrix as an index that degrades to Discovery → Requirement → Acceptance when no Stories exist.

#### Acceptance
AC-003 — The guidance documents one Story mapped to multiple Requirements, a Requirement mapped to multiple Stories, and a technical Requirement without a Story.

### FR-004 · Guidance and compatibility boundary

#### Requirement
User Stories, Acceptance Scenarios, and the new Markdown layout SHALL remain non-binding presentation guidance. `forge validate` SHALL not parse or enforce these Markdown relationships, and historical Specifications without User Stories SHALL remain valid.

#### Acceptance
AC-004 — Existing scaffold, protocol, schema, validation, and adapter tests remain passing; no file under `protocol/schemas/` changes.

## Non-functional Requirements

### NFR-001 · Plain-text readability

The generated Markdown SHALL remain readable without renderer-specific HTML, badges, emojis, or required external tooling.

## Constraints

### CON-001 · Scope boundary

Do not create a separate user-stories artifact, backlog model, BDD dependency, lifecycle command, automatic test generation, or full Plan/Task/Test traceability implementation.

## Traceability Matrix

This matrix is an index only; entity-local references remain authoritative.

| Discovery | User Story | Requirement | Acceptance |
|---|---|---|---|
| Repository audit | — | FR-001, FR-004 | AC-001, AC-004 |
| Repository audit | — | FR-002 | AC-002 |
| Repository audit | — | FR-003 | AC-003 |

## Compatibility Statement

The existing front matter, Change Schema, Protocol integers, Flow Gates, historical Specifications, `traceability.yml`, and Harness Adapter semantics remain unchanged. The new structure applies to newly generated Specifications and guidance only.

## Specification Gate

This Specification is complete when the scaffold behavior, canonical guidance, example, documentation, and focused tests are updated without introducing Markdown semantic enforcement.

## Out of Scope

Protocol semantic changes, Schema changes, validator parsing, BDD execution, and retroactive historical artifact rewrites.
