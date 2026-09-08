---
forge:
  artifact: specification
  schema: 1
change: CHG-0057
status: complete
---

# CHG-0057 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0057 |
| **Flow** | STANDARD |
| **Status** | Complete |

## Summary

The release metadata identifies CLI version `0.1.0b4`, and the changelog moves
the current Unreleased capability-exposure entry into a dated `0.1.0b4`
section. No executable or Protocol behavior changes.

## Classification

The non-behavioral scaffold is used because this Change publishes already-merged
behavior and changes release metadata only.

## User Stories

User Stories are optional behavioral context. Include this section only when a meaningful actor, concrete capability, and outcome add information; otherwise remove it. Do not invent a persona to satisfy the template.

## Functional Requirements

Each requirement is an independent, verifiable contract. A Requirement without a User Story is valid.

### FR-001 · Release metadata identifies the merged change
Priority: required

#### Requirement
The package version source is `0.1.0b4` and the changelog has a dated matching section.

#### Expected Behavior
The version uses valid PEP 440 syntax and does not alter Protocol versioning.

#### Boundary
State an explicit limit only when the requirement needs one.

#### Acceptance
AC-001
Given the merged capability-exposure commit is on `main`
When the release metadata is inspected
Then CLI version and changelog identify `0.1.0b4`.

## Non-functional Requirements

Add NFR-xxx entries only when applicable. They do not require a User Story.

## Constraints

Add CON-xxx entries only when they restrict the solution or Change.

## Traceability Matrix

Use this as an index across Discovery, User Stories, Requirements, and Acceptance; the relationships on the entities remain authoritative. Omit User Story columns when no Stories apply.

## Compatibility Statement

Describe compatibility with existing behavior, artifacts, Protocol versions, or explicitly state why it is not materially affected.

## Specification Gate

Complete: the release boundary is metadata-only and the expected version and
changelog result are directly verifiable.

## Out of Scope

No runtime, Protocol, Capability, or Adapter behavior is in scope.
