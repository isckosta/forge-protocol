---
forge:
  artifact: intent
  schema: 1
change: CHG-0058
status: complete
---

# CHG-0058 · Review Capability

> **Change Intent**
>
> Define `review` as a canonical, Harness-independent competency for critical
> and adversarial analysis of a subject under Forge's already-effective review
> context, without taking ownership of review governance.

## Overview
| | |
|---|---|
| **Change** | CHG-0058 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

Forge has canonical competencies for investigation, repair, and exploratory
QA, but it does not yet have a reusable competency that evaluates a subject
against its obligations and effective review profile. Review already has
normative obligations, profiles, independence, provenance, and lifecycle rules
outside the Capability layer; encoding those rules in an absent or ad hoc
competency would duplicate authority and make Harness projections diverge.

## Goal

1. Define a canonical `review` Capability that actively searches for defects,
   regressions, inconsistencies, risks, and unsupported claims.
2. Require clear findings with materiality/severity where applicable and
   evidence sufficient to support conclusions.
3. Preserve the effective review profile and all review governance boundaries
   as inputs and external responsibilities.

## Scope

The Change covers the identity, applicability, inputs, adversarial review
behavior, outputs, evidence expectations, and boundaries of the review
competency. It demonstrates that the existing generic Capability discovery and
Harness projection path can carry the new competency.

## Out of Scope

It does not add or redefine Flow, Gates, approval, Completion, review
obligation, Review Mode/Profile selection, independence requirements, human
authority, executor, registry, lifecycle, orchestration, Protocol, or
Engineering Contract behavior. It does not add Harness-specific integration.

## Success Criteria

`review` exists as a contract-conforming canonical Capability, is discovered
by the existing generic catalog, and is projected to supported Harnesses
without Capability-specific branches. Its definition guides evidence-based,
adversarial findings while explicitly leaving review governance to Forge.
