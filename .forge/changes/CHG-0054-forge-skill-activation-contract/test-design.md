---
forge:
  artifact: test_design
  schema: 1
change: CHG-0054
status: complete
---

# CHG-0054 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0054 |
| **Flow** | STANDARD |
| **Status** | Complete |

## Test Strategy

Render both Adapter projections and assert the published front matter as an
observable discovery contract. Cover exact parity, positive signals, negative
exclusions, and the material/immaterial boundary.

| Layer | Scope | Method |
|---|---|---|
| Layer A | Codex and Claude Code skill projections | Automated |

## Coverage Map

List every Requirement this Change must verify before Implementation, with the Scenario that covers it. Include a Story column only when User Stories apply; a Requirement without a User Story is valid.

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001, TD-002, TD-003 | Automated |

## Layer A · <name>

### TD-001 · Projection parity
Requirements: FR-001
Stories: <US identifiers, when applicable>
Type: <Unit | Integration | Domain Integration | Manual Acceptance>
Priority: <priority, when used>

#### Purpose
Prove that compatible Harnesses receive equivalent activation criteria.

#### Preconditions
State only the initial state this scenario actually depends on. Omit this section when there is none.

#### Scenario
Given equivalent Codex and Claude Code projection inputs
When each skill is rendered
Then both descriptions contain the same activation contract.

#### Evidence
Pytest assertions over the two generated `SKILL.md` resources.

#### Failure Condition
Any adapter drift or reintroduction of the circular description invalidates it.

### TD-002 · Positive routing signals
Requirements: FR-001
Type: Unit

#### Purpose
Prove material feature/behavior work, material defect fixes, Change
continuation, and explicit Forge requests are discoverable before load.

#### Scenario
Given the rendered description
When each positive signal is inspected
Then it is present.

#### Evidence
Parametrized pytest assertions.

### TD-003 · Negative and ambiguous boundary
Requirements: FR-001
Type: Unit

#### Purpose
Prove that read-only, explanatory, investigative-without-change, trivial, and
immaterial work is not automatically promoted.

#### Scenario
Given the rendered description
When non-trigger and materiality boundary terms are inspected
Then exclusions are explicit and the circular phrase is absent.

#### Evidence
Parametrized pytest assertions.

#### Boundary
State what this scenario does not prove, only when it could reasonably be mistaken for proving more. Omit when there is no such risk.

## Manual Acceptance

Use `Type: Manual Acceptance` for a property that depends on human or real-Harness interaction and cannot reasonably be checked by tooling. A Manual Acceptance scenario still needs Preconditions, explicit operator instructions, observable Evidence, and a Failure Condition; it MUST NOT be presented as an automated guarantee.

## Valid RED

When TDD applies, RED is valid only when the test fails for the expected behavioral reason. A RED caused by a syntax error, a broken import, an invalid fixture, missing configuration, or unrelated infrastructure unavailability is not valid evidence and must be fixed and re-run before it counts.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001, TD-002, TD-003 | — | Covered |

## Coverage Gaps

No mandatory Requirement remains without automated coverage.

## Test Design Gate

Test Design Gate satisfied; valid RED is the old circular description rather
than an import, fixture, or infrastructure failure.
