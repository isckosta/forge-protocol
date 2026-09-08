---
forge:
  artifact: test_design
  schema: 1
change: CHG-0053
status: complete
---

# CHG-0053 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0053 |
| **Flow** | STANDARD |
| **Status** | Complete |

## Test Strategy

The single automated layer loads the real canonical definition through the
unchanged loader and checks contract, input, boundary, minimal-repair, and
evidence language. RED is the expected missing-file failure; GREEN is the
passing focused capability suite.

| Layer | Scope | Method |
|---|---|---|
| Layer A | Canonical fix Capability contract | Automated |

## Coverage Map

List every Requirement this Change must verify before Implementation, with the Scenario that covers it. Include a Story column only when User Stories apply; a Requirement without a User Story is valid.

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001 | Automated |
| FR-002 | TD-002 | Automated |
| FR-003 | TD-003 | Automated |
| FR-004 | TD-004 | Automated |
| FR-005 | TD-005 | Automated |
| NFR-001 | TD-001 | Automated |

## Layer A · Capability Contract

### TD-001 · Definition loads through the generic contract
Requirements: FR-001, NFR-001
Type: Unit

#### Purpose
Proves the definition is portable and satisfies the existing contract.

#### Preconditions
The canonical definition exists in the repository.

#### Scenario
Given the definition exists, when the existing loader loads it, then a
populated `Capability` with id `fix` and all seven sections is returned.

#### Evidence
Pytest result and loader return value.

#### Failure Condition
Any missing section, wrong id/schema, or loader modification invalidates it.

#### Boundary
This does not prove a product-level fix; it proves the capability contract.

### TD-002 · Insufficient understanding escalates
Requirements: FR-002
Type: Unit

#### Purpose
Proves unresolved material uncertainty is directed to investigation.

#### Scenario
Given one precondition is unknown, when Fix decides whether to implement,
then it escalates instead of claiming a confirmed cause.

#### Evidence
Focused assertions over Behavior and Outputs.

#### Failure Condition
The definition permits implementation from unsupported inference.

### TD-003 · Minimal repair preserves boundary
Requirements: FR-003
Type: Unit

#### Purpose
Proves the capability requires a smallest cause-oriented correction and
detects material expansion.

#### Scenario
Given a proposed repair would become architectural or breaking, then Fix
names escalation rather than silent expansion.

#### Evidence
Focused assertions over Purpose, Behavior, and raw definition text.

#### Failure Condition
The definition treats a symptom patch or broad redesign as a local fix.

### TD-004 · Verification is reproducible and proportional
Requirements: FR-004
Type: Unit

#### Purpose
Proves the output requires regression reproduction and restored-behavior evidence.

#### Scenario
Given an automatable defect, when the repair is reported, then regression
and verification evidence are identified.

#### Evidence
Focused assertions over Outputs and Evidence Expectations.

#### Failure Condition
Passing tests alone are presented as proof of every claim.

### TD-005 · Governance remains outside the capability
Requirements: FR-005
Type: Unit

#### Purpose
Proves the definition does not redefine Forge governance.

#### Scenario
Given the definition is loaded, then it preserves Flow, Gate, approval,
Merge Readiness, lifecycle, and Protocol authority.

#### Evidence
Focused assertions over forbidden vocabulary and boundary terms.

#### Failure Condition
The definition introduces a mandatory artifact, execution mechanism, or authority.

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
| NFR-001 | TD-001 | — | Covered |

## Coverage Gaps

No mandatory Requirement remains without a verification strategy; manual
acceptance is unnecessary for this canonical prose and loader contract.

## Test Design Gate

Every requirement has a scenario, purpose, evidence, and failure condition;
valid RED is defined and no coverage gap remains.
