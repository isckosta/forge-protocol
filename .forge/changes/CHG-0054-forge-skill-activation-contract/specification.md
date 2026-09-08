---
forge:
  artifact: specification
  schema: 1
change: CHG-0054
status: complete
---

# CHG-0054 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0054 |
| **Flow** | STANDARD |
| **Status** | Complete |

## Summary

The skill description is a pre-load routing contract. It names observable
material-change signals and explicit exclusions only. Lifecycle obligations,
Flow selection, and Forge authority remain in the skill body and repository
state.

## Classification

STANDARD: this is a bounded cross-Harness discovery contract change with no
Protocol schema or lifecycle semantic change.

## User Stories

User Stories are optional behavioral context. Include this section only when a meaningful actor, concrete capability, and outcome add information; otherwise remove it. Do not invent a persona to satisfy the template.

## Functional Requirements

Each requirement is an independent, verifiable contract. A Requirement without a User Story is valid.

### FR-001 · Observable activation signals
Stories: <US identifiers, when applicable>
Origin: <finding reference, when applicable>
Priority: <priority, when used>

#### Requirement
Each published Forge skill description MUST identify a Forge-enabled repository
and material behavior implementation/change, material defect correction,
existing Forge Change continuation, or explicit Forge governance request.

#### Expected Behavior
It MUST NOT require the Harness to know beforehand that the work is a
“Forge-governed Change”. It MUST also name the read-only, investigative without
change, trivial, and immaterial boundaries.

#### Boundary
State an explicit limit only when the requirement needs one.

#### Acceptance
AC-001: Codex and Claude Code publish equivalent positive signals.
AC-002: Non-change work is explicitly excluded from automatic activation.
AC-003: The description contains no lifecycle gate or Harness-specific
authority replacement.

## Non-functional Requirements

Add NFR-xxx entries only when applicable. They do not require a User Story.

## Constraints

Add CON-xxx entries only when they restrict the solution or Change.

## Traceability Matrix

| Requirement | Acceptance | Evidence |
|---|---|---|
| FR-001 | AC-001, AC-002, AC-003 | activation contract unit tests |

## Compatibility Statement

Protocol 2 and lifecycle artifacts remain compatible. Only skill discovery
metadata and generated Adapter outputs change.

## Specification Gate

Specification is complete: one bounded requirement covers the routing contract
and all acceptance conditions have automated coverage across both projections.

## Out of Scope

No Protocol/schema expansion, no Harness-specific algorithm, and no automatic
Change lifecycle for read-only or immaterial work.
