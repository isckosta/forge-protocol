---
forge:
  artifact: test_design
  schema: 1
change: CHG-0050
status: complete
---

# CHG-0050 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0050 |
| **Flow** | STANDARD |
| **Status** | Complete |

## Test Strategy

Describe how this Change will be demonstrated before Implementation. Group scenarios into Layers only when that adds clarity (e.g. Domain, API, Persistence, CLI, Harness, Manual Acceptance); a single Layer is valid for a small Change.

| Layer | Scope | Method |
|---|---|---|
| Layer A | Story contract, traceability, scaffold, and Markdown evidence boundaries | Automated |

## Coverage Map

List every Requirement this Change must verify before Implementation, with the Scenario that covers it. Include a Story column only when User Stories apply; a Requirement without a User Story is valid.

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001 | Automated |
| FR-002 | TD-002 | Automated |
| FR-003 | TD-003 | Automated |
| FR-004 | TD-004 | Automated |
| FR-005 | TD-005 | Automated |

## Layer A · Story contract and traceability

### TD-001 · Behavioral Story floor
Requirements: FR-001
Stories: US-001
Type: Unit
Priority: high

#### Purpose
Behavioral Specifications require a stable User Story, while technical Changes remain exempt.

#### Scenario
Given a Change with `observable_behavior: true`, when its Specification is validated, then it declares `Behavior: behavioral` and contains a stable `US-xxx` heading.

#### Evidence
Focused unit tests pass for behavioral, technical, historical, and FAST cases.

#### Failure Condition
An absent, duplicated, mismatched, indented, or fenced Story identifier is accepted.

### TD-002 · Story traceability
Requirements: FR-002
Stories: US-001
Type: Unit

#### Purpose
Every Story traces to completed executable work and passing Verification.

#### Scenario
Given a behavioral Change in Implementation or later, when traceability is validated, then every Story links to a completed Task and passing Acceptance evidence.

#### Evidence
Focused tests cover missing links, fenced task examples, fenced verification examples, and failed result rows.

#### Failure Condition
Documentation examples, incomplete tasks, or non-PASS result rows satisfy traceability.

### TD-003 · Stable identity
Requirements: FR-003
Stories: US-001, US-003
Type: Unit

#### Purpose
Story identifiers are unique and stable.

#### Scenario
Given Story headings, when the Specification is parsed, then stable `US-xxx` identifiers are collected and duplicates are rejected.

#### Evidence
The contract suite asserts duplicate detection and many-to-many traceability fixtures.

#### Failure Condition
The same stable identifier appears more than once without a finding.

### TD-004 · Technical exemption
Requirements: FR-004
Stories: US-002
Type: Unit

#### Purpose
Technical and FAST Changes do not require synthetic Stories.

#### Scenario
Given a technical Change or a FAST Change without a Specification, when validated, then no synthetic Story is required.

#### Evidence
Technical and FAST exemption tests pass.

#### Failure Condition
The validator requires an artificial persona Story.

### TD-005 · Markdown evidence boundary
Requirements: FR-005
Stories: US-003
Type: Unit

#### Purpose
Indented and fenced examples are not treated as real Story headings.

#### Scenario
Given Story-shaped text inside indentation or a fenced Markdown example, when parsed, then only headings outside examples count.

#### Evidence
Mixed fence, tilde fence, and fence-info regression tests pass.

#### Failure Condition
An inner fence with language metadata closes an outer example and creates a false Story.

## Manual Acceptance

Use `Type: Manual Acceptance` for a property that depends on human or real-Harness interaction and cannot reasonably be checked by tooling. A Manual Acceptance scenario still needs Preconditions, explicit operator instructions, observable Evidence, and a Failure Condition; it MUST NOT be presented as an automated guarantee.

## Valid RED

When TDD applies, RED is valid only when the test fails for the expected behavioral reason. A RED caused by a syntax error, a broken import, an invalid fixture, missing configuration, or unrelated infrastructure unavailability is not valid evidence and must be fixed and re-run before it counts.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001 | — | Covered |
| FR-002 | TD-002 | — | Covered |
| FR-003 | TD-003 | — | Covered |
| FR-004 | TD-004 | — | Covered |
| FR-005 | TD-005 | — | Covered |

## Coverage Gaps

No mandatory Requirement remains without a verification strategy. The Change has no manual acceptance gap.

## Test Design Gate

Record that every mandatory Requirement has a verification strategy, critical scenarios have a clear Purpose, Failure Conditions are defined, automated and Manual Acceptance are separated, valid RED is defined when TDD applies, and no Requirement remains without known coverage.
