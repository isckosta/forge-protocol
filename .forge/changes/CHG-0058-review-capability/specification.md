---
forge:
  artifact: specification
  schema: 1
change: CHG-0058
status: complete
---

# CHG-0058 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0058 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

Add one canonical `review` Capability using the unchanged Capability Contract.
It must define a critical, adversarial analysis competency whose effective
review profile is supplied by Forge and whose results are findings and
evidence, not governance decisions.

## Classification

STANDARD: this adds a reusable canonical definition and focused contract tests
without changing runtime product behavior, Protocol semantics, Flow semantics,
or adapter integration.

## User Stories

User Stories are optional behavioral context. Include this section only when a meaningful actor, concrete capability, and outcome add information; otherwise remove it. Do not invent a persona to satisfy the template.

## Functional Requirements

Each requirement is an independent, verifiable contract. A Requirement without a User Story is valid.

### FR-001 · <requirement title>
Stories: <US identifiers, when applicable>
Origin: <finding reference, when applicable>
Priority: <priority, when used>

#### Requirement
`capabilities/review/CAPABILITY.md` SHALL contain valid frontmatter and all
seven required non-empty sections, and SHALL load through the unchanged
generic Capability loader with id `review`.

#### Expected Behavior
The definition remains Harness-independent and introduces no new execution or
governance mechanism.

#### Boundary
No loader, model, catalog, Protocol, or adapter-specific change is required.

#### Acceptance
AC-001 Given the real definition path, when the existing loader reads it, then
it returns a populated `Capability` with id `review` and all seven sections.

### FR-002 · Critical and adversarial analysis

#### Requirement
The competency SHALL compare the subject and its claims against applicable
obligations, requirements, context, and the effective review profile, actively
searching for defects, regressions, inconsistencies, risks, and claims whose
evidence is insufficient.

#### Acceptance
AC-002 The definition names these search targets and requires testing both
supporting and disconfirming evidence rather than accepting the subject's
claims at face value.

### FR-003 · Findings and evidence

#### Requirement
Outputs SHALL contain clear findings with location/scope, observed condition,
expected or required condition, impact, materiality/severity when applicable,
and evidence sufficient for an independent reader to verify the conclusion.
Uncertainty and evidence gaps SHALL be explicit, and absence of findings SHALL
not be represented as proof beyond the performed review scope.

#### Acceptance
AC-003 The definition specifies a reproducible finding shape, severity or
materiality guidance, and evidence expectations for both findings and clean
areas.

### FR-004 · Effective profile and governance boundaries

#### Requirement
The competency SHALL consume the effective review profile and context supplied
by Forge without resolving, changing, or weakening them. It SHALL remain
independent from the rules that determine when Review is mandatory and SHALL
not own Flow, Gates, approval, Completion, Review Mode/Profile selection,
normative independence requirements, provenance authority, human authority,
lifecycle, executor, registry, or orchestration.

#### Acceptance
AC-004 The definition explicitly assigns those responsibilities outside the
Capability and distinguishes Review from Verification, Investigate, Fix, and QA.

## Non-functional Requirements

### NFR-001 · Harness independence

The definition SHALL be reusable across Harnesses and contain no Harness name,
Harness-specific skill format, or per-Capability integration instruction.

Add NFR-xxx entries only when applicable. They do not require a User Story.

## Constraints

- No new executor, registry, lifecycle, orchestration, or mandatory artifact.
- No Protocol, Engineering Contract, Flow, Gate, or adapter-specific change.

Add CON-xxx entries only when they restrict the solution or Change.

## Traceability Matrix

| Requirement | Acceptance |
|---|---|
| FR-001 | AC-001 |
| FR-002 | AC-002 |
| FR-003 | AC-003 |
| FR-004 | AC-004 |
| NFR-001 | AC-001–AC-004 |

## Compatibility Statement

The change is additive. Existing loader, model, catalog, projections, Protocol
2 schemas, Engineering Contract, Flows, and adapters remain unchanged; the
new definition is consumed through their existing generic path.

## Specification Gate

All requested behavior maps to four acceptance criteria, and the boundaries
exclude governance and Harness integration. No unresolved design decision
expands scope.

## Out of Scope

No execution implementation, review obligation, profile resolver, lifecycle,
authority mechanism, or Harness-specific representation is in scope.
