---
forge:
  artifact: specification
  schema: 1
change: CHG-0055
status: complete
---

# CHG-0055 · QA Capability Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0055 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

Add one canonical QA definition that follows the existing Capability Contract
and remains independent of any Harness or execution mechanism.

## Classification

STANDARD, because the Change adds a reusable capability definition and
contract-focused tests without changing runtime product behavior or Protocol
semantics.

## User Stories

User Stories are optional behavioral context. Include this section only when a meaningful actor, concrete capability, and outcome add information; otherwise remove it. Do not invent a persona to satisfy the template.

## Functional Requirements

Each requirement is an independent, verifiable contract. A Requirement without a User Story is valid.

### FR-001 · Contract-conforming definition

#### Requirement
`capabilities/qa/CAPABILITY.md` has the required frontmatter and seven
non-empty sections and loads through the unchanged generic loader.

#### Expected Behavior
The capability id is `qa` and schema is an integer.

#### Boundary
The definition contains no Harness-specific or new enforcement mechanism.

#### Acceptance
AC-001 Given the QA definition path, when the existing loader reads it, then
it returns a populated `Capability` with id `qa`.

### FR-002 · Exploratory behavior

#### Requirement
QA explores happy paths, edge cases, invalid states, errors, relevant
combinations, and applicable boundaries, prioritizing observable behavior.

#### Acceptance
AC-002 The definition names each applicable exploration class and requires
recording exact actions and observable results.

### FR-003 · Reproducible findings

#### Requirement
Each finding distinguishes observed behavior, expected behavior, reproduction
conditions, evidence, and impact, with uncertainty and reproduction status
explicitly labelled.

#### Acceptance
AC-003 The definition specifies the finding shape and evidence needed for
another person to retry it.

### FR-004 · Responsibility boundaries

#### Requirement
QA discovers and characterizes behavior but does not assume root cause, fix
software, or duplicate Verification, Review, Investigate, or Fix.

#### Acceptance
AC-004 The definition explicitly distinguishes all four competencies and
denies correction, unsupported causal certainty, and governance ownership.

## Non-functional Requirements

### NFR-001 · Portability

The capability remains Harness-independent and reusable in any Forge-enabled
repository.

## Constraints

No new Gate, Flow, lifecycle, mandatory artifact, executor, registry, or
enforcement mechanism may be introduced.

## Traceability Matrix

FR-001 → AC-001; FR-002 → AC-002; FR-003 → AC-003; FR-004 → AC-004;
NFR-001 is covered by AC-001 through AC-004 and the portability assertions.

## Compatibility Statement

The existing loader, model, Protocol, Flow, and adapters remain unchanged.
The new definition is additive and uses the existing Capability Contract.

## Specification Gate

Requirements and acceptance criteria are independently verifiable, bounded to
the existing Capability Contract, and contain no unresolved design decision.

## Out of Scope

No runtime implementation, registry, executor, mandatory artifact, or
Harness-specific representation is in scope.
