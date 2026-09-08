---
forge:
  artifact: intent
  schema: 1
change: CHG-0055
status: active
---

# CHG-0055 · QA Capability

> **Change Intent**
>
> Define `/qa` as an independent, Harness-independent competency for
> exploratory evaluation of observable behavior and reproducible reporting of
> behavioral findings beyond known Requirements.

## Overview
| | |
|---|---|
| **Change** | CHG-0055 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

Forge has `investigate` for diagnosing a known problem and `fix` for repairing
an understood defect, but it lacks a canonical competency for exercising
executable software as a product to discover unknown behavioral problems.

## Goal

1. Define QA under the existing Capability Contract.
2. Require systematic exploration of normal, boundary, invalid, error,
   combinatorial, and cross-boundary behavior when applicable.
3. Require findings to separate observation, expectation, reproduction,
   evidence, and impact without assuming cause or implementing a fix.

## Scope

The Change covers the canonical QA identity, purpose, applicability, inputs,
exploratory behavior, output finding shape, evidence expectations, and
boundaries with Verification, Review, Investigate, and Fix.

## Out of Scope

It does not add a Gate, Flow, lifecycle, mandatory artifact, executor,
registry, enforcement mechanism, Harness-specific projection, or product
implementation. It does not change the existing loader or Protocol semantics.

## Success Criteria

`capabilities/qa/CAPABILITY.md` satisfies the existing contract, is reusable
in any Forge-enabled repository, guides risk-informed behavioral exploration,
and produces reproducible findings while preserving the responsibilities of
the adjacent competencies.
