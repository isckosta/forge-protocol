---
forge:
  artifact: specification
  schema: 1
change: CHG-0056
status: pending
---

# CHG-0056 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0056 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Requirements

### REQ-001 — Canonical catalog

Forge SHALL load all packaged `capabilities/*/CAPABILITY.md` definitions in stable order, reject duplicate or invalid invocation identities, and expose no Harness-specific fields in the canonical model.

### REQ-002 — Exposure contract

The generic exposure contract SHALL provide only a Capability reference and stable invocation identity. It SHALL not define slash commands, lifecycle, gates, approvals, or execution.

### REQ-003 — Native projection

Adapters SHALL derive one native skill representation per catalog entry when their packaged evidence declares skills supported. The projection SHALL include a discoverable `SKILL.md` and the exact canonical definition as a reference resource.

### REQ-004 — Semantic fallback

An adapter without a supported native skill or command surface SHALL not fail Capability loading or alter the canonical definition; consumers can still use the Capability through ordinary Harness interaction.

### REQ-005 — Distinct responsibilities

Projected Capability invocation SHALL delegate to canonical behavior and SHALL not duplicate Verification, Review, Investigate, Fix, Flow, lifecycle, or governance responsibilities.

## Summary

State the expected outcome and the contract boundary in a few sentences.

## Classification

Record the selected Flow and the semantic reason for it.

## User Stories

User Stories are optional behavioral context. Include this section only when a meaningful actor, concrete capability, and outcome add information; otherwise remove it. Do not invent a persona to satisfy the template.

## Functional Requirements

Each requirement is an independent, verifiable contract. A Requirement without a User Story is valid.

### FR-001 · <requirement title>
Stories: <US identifiers, when applicable>
Origin: <finding reference, when applicable>
Priority: <priority, when used>

#### Requirement
Write the normative behavior.

#### Expected Behavior
Describe important rules and consequences only when they add information.

#### Boundary
State an explicit limit only when the requirement needs one.

#### Acceptance
AC-001
Given <initial condition>
When <action>
Then <observable result>

## Non-functional Requirements

Add NFR-xxx entries only when applicable. They do not require a User Story.

## Constraints

Add CON-xxx entries only when they restrict the solution or Change.

## Traceability Matrix

Use this as an index across Discovery, User Stories, Requirements, and Acceptance; the relationships on the entities remain authoritative. Omit User Story columns when no Stories apply.

## Compatibility Statement

Describe compatibility with existing behavior, artifacts, Protocol versions, or explicitly state why it is not materially affected.

## Specification Gate

Record the evidence that this Specification is complete, internally consistent, and ready for the next Flow stage.

## Out of Scope

List exclusions and boundaries.
