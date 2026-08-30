---
forge:
  artifact: test_design
  schema: 1
change: CHG-0050
status: pending
---

# CHG-0050 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0050 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Test Strategy

Describe how this Change will be demonstrated before Implementation. Group scenarios into Layers only when that adds clarity (e.g. Domain, API, Persistence, CLI, Harness, Manual Acceptance); a single Layer is valid for a small Change.

| Layer | Scope | Method |
|---|---|---|
| Layer A | <scope> | Automated |

## Coverage Map

List every Requirement this Change must verify before Implementation, with the Scenario that covers it. Include a Story column only when User Stories apply; a Requirement without a User Story is valid.

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001 | Automated |
| FR-002 | TD-002 | Automated |
| FR-003 | TD-003 | Automated |
| FR-004 | TD-004 | Automated |
| FR-005 | TD-005 | Automated |

## Layer A · <name>

### TD-001 · Behavioral Story floor
Requirements: FR-001
Stories: US-001
Type: Unit
Priority: high

#### Purpose
Behavioral Specifications require a stable User Story.

### TD-002 · Story traceability
Requirements: FR-002
Stories: US-001
Type: Unit

#### Purpose
Every Story traces to completed executable work and passing Verification.

### TD-003 · Stable identity
Requirements: FR-003
Stories: US-001, US-003
Type: Unit

#### Purpose
Story identifiers are unique and stable.

### TD-004 · Technical exemption
Requirements: FR-004
Stories: US-002
Type: Unit

#### Purpose
Technical and FAST Changes do not require synthetic Stories.

### TD-005 · Markdown evidence boundary
Requirements: FR-005
Stories: US-003
Type: Unit

#### Purpose
Indented and fenced examples are not treated as real Story headings.

#### Preconditions
State only the initial state this scenario actually depends on. Omit this section when there is none.

#### Scenario
Given <initial condition>
When <action>
Then <observable result>

#### Evidence
State what observable material will exist to support the result: exit code, persisted row, emitted event, HTTP status, log, snapshot, test result, or manual observation.

#### Failure Condition
State what invalidates this scenario as evidence, including a false positive, not only what a failing assertion looks like.

#### Boundary
State what this scenario does not prove, only when it could reasonably be mistaken for proving more. Omit when there is no such risk.

## Manual Acceptance

Use `Type: Manual Acceptance` for a property that depends on human or real-Harness interaction and cannot reasonably be checked by tooling. A Manual Acceptance scenario still needs Preconditions, explicit operator instructions, observable Evidence, and a Failure Condition; it MUST NOT be presented as an automated guarantee.

## Valid RED

When TDD applies, RED is valid only when the test fails for the expected behavioral reason. A RED caused by a syntax error, a broken import, an invalid fixture, missing configuration, or unrelated infrastructure unavailability is not valid evidence and must be fixed and re-run before it counts.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001 | — | Covered |

## Coverage Gaps

State explicitly that no mandatory Requirement remains without a verification strategy, or list each gap. A critical Requirement that cannot be verified is a Specification problem, not an Implementation problem.

## Test Design Gate

Record that every mandatory Requirement has a verification strategy, critical scenarios have a clear Purpose, Failure Conditions are defined, automated and Manual Acceptance are separated, valid RED is defined when TDD applies, and no Requirement remains without known coverage.
