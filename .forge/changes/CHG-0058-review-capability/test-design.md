---
forge:
  artifact: test_design
  schema: 1
change: CHG-0058
status: complete
---

# CHG-0058 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0058 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Test Strategy

The real canonical file is loaded through the existing loader and its prose is
checked for the required review search targets, finding/evidence shape, and
governance boundaries. This verifies the additive Capability contract without
pretending that keyword assertions replace human review of prose quality.

| Layer | Scope | Method |
|---|---|---|
| Layer A | Canonical review Capability contract | Automated |

## Coverage Map

List every Requirement this Change must verify before Implementation, with the Scenario that covers it. Include a Story column only when User Stories apply; a Requirement without a User Story is valid.

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001 | Automated |
| FR-002 | TD-002 | Automated |
| FR-003 | TD-003 | Automated |
| FR-004 | TD-004 | Automated |
| NFR-001 | TD-005 | Automated |

## Layer A · Capability contract and semantic boundary

### TD-001 · Definition conforms to the existing loader contract
Requirements: FR-001
Stories: <US identifiers, when applicable>
Type: <Unit | Integration | Domain Integration | Manual Acceptance>
Priority: <priority, when used>

#### Purpose
Proves the real definition is discoverable and structurally valid without
changing the Foundation.

#### Preconditions
State only the initial state this scenario actually depends on. Omit this section when there is none.

#### Scenario
Given the definition is absent, the test fails with the expected missing-file
error (RED). Given the definition exists, the loader returns id `review`, an
integer schema, and seven non-empty sections (GREEN).

#### Evidence
Focused pytest result and the loaded `Capability` fields.

#### Failure Condition
Any loader error, missing section, wrong id, or test passing before the real
definition exists invalidates the evidence.

#### Boundary
Does not prove the qualitative adequacy of the prose by itself.

### TD-002 · Adversarial search scope is explicit
Requirements: FR-002
Type: Unit

The real behavior text must mention obligations/context/profile-aware analysis
and active search for defects, regressions, inconsistencies, risks, and
unsupported claims, including disconfirming evidence.

### TD-003 · Findings are evidence-bearing and materiality-aware
Requirements: FR-003
Type: Unit

The real outputs and evidence sections must specify reproducible findings,
location/scope, observed versus expected condition, impact, severity or
materiality, uncertainty/evidence gaps, and clean-scope limitations.

### TD-004 · Governance remains outside the competency
Requirements: FR-004
Type: Unit

The real definition must explicitly preserve the supplied effective profile
and deny ownership of obligation selection, Flow, Gates, approval,
Completion, independence rules, provenance authority, human authority,
lifecycle, executor, registry, and orchestration.

### TD-005 · Harness-independent canonical source
Requirements: NFR-001
Type: Unit

The full real definition contains no Harness names or Harness-specific
projection mechanism terms.

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
| NFR-001 | TD-005 | — | Covered |

## Coverage Gaps

No mandatory Requirement remains without a verification strategy. Qualitative
prose quality remains a review concern, not an automated keyword guarantee.

## Test Design Gate

Every mandatory Requirement has a focused automated strategy; valid RED is the
expected missing-definition failure; no Requirement remains without coverage.
